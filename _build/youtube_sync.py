"""Put new videos from the David Park PhD YouTube channel on the website.

Reads the channel's public feed (no key needed) and sorts every new full video (Shorts are skipped):
  1. a Merit Test episode, matched by its title to build.py's EPISODES, goes into _build/youtube.json;
  2. a show episode goes into _build/videos.json under its show, found by the show's YouTube playlist
     ("Business Now", "Business Story", the names in build.py's SHOWS) or by the show name in the title or description;
  3. any other full video goes into _build/videos.json as "other" (More videos on the Shows page).
A video that mentions The Merit Test but matches no planned title is left out, so it never lands in a show by mistake.
Prints what it found. Exit code 0 always, so a quiet run is not an error.

Usage
    python3 _build/youtube_sync.py            update youtube.json and videos.json
    python3 _build/youtube_sync.py --dry-run  only print what it would do

Run by .github/workflows/youtube-sync.yml every 15 minutes (GitHub often runs it later), which then runs build.py and publishes.
"""
import difflib
import json
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CHANNEL_ID = "UC-N6X4gJtGrTDSAuOea8nEA"  # David Park PhD, the English channel (@DavidPark_PhD until the handle switch, WD-60)
FEED = "https://www.youtube.com/feeds/videos.xml?channel_id=" + CHANNEL_ID
HERE = Path(__file__).resolve().parent
IDS = HERE / "youtube.json"
VIDEOS = HERE / "videos.json"
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015", "m": "http://search.yahoo.com/mrss/"}
UA = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en"}


def slugify(t):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t.lower())).strip("-")


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t.lower())).strip()


def episodes():
    """Merit Test episode numbers and titles straight from build.py's EPISODES list, without running the build."""
    src = (HERE / "build.py").read_text()
    return [(int(n), t) for n, t in re.findall(r'dict\(n=(\d+),.*?title="([^"]+)"', src, re.S)]


def shows():
    """(key, name) of each show in build.py's SHOWS."""
    return re.findall(r'dict\(key="(\w+)", tag="\w+", name="([^"]+)"', (HERE / "build.py").read_text())


def fetch(url, tries=3):
    for attempt in range(tries):  # YouTube sometimes answers 404 or 5xx for a few minutes
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"fetch attempt {attempt + 1} {url}: {e}")
            time.sleep(15)
    return None


def entries(xml_bytes):
    root = ET.fromstring(xml_bytes)
    out = []
    for e in root.findall("a:entry", NS):
        out.append(dict(id=e.findtext("yt:videoId", namespaces=NS), title=e.findtext("a:title", namespaces=NS) or "",
                        published=(e.findtext("a:published", namespaces=NS) or "")[:10],
                        description=e.findtext("m:group/m:description", namespaces=NS) or ""))
    return out


def page_ids(url):
    """Video ids in the order a channel or playlist page lists them (used when YouTube's feeds are down)."""
    raw = fetch(url, tries=2)
    if not raw:
        return None
    html = raw.decode("utf8", "ignore")
    return list(dict.fromkeys(re.findall(r'"videoId":"([\w-]{11})"', html)))


def watch_details(vid):
    """Title, publish date and description from a video's own page."""
    raw = fetch(f"https://www.youtube.com/watch?v={vid}&hl=en", tries=2)
    if not raw:
        return None
    html = raw.decode("utf8", "ignore")
    def js(key):
        m = re.search(r'"' + key + r'":"((?:[^"\\]|\\.)*)"', html)
        return json.loads('"' + m.group(1) + '"') if m else ""
    title = js("title") or ""
    if not title:
        return None
    return dict(id=vid, title=title, published=(js("publishDate") or js("uploadDate"))[:10], description=js("shortDescription"))


def channel_page_entries(known):
    """Fallback for a dead feed: the channel's Videos tab lists full videos only (Shorts have their own tab)."""
    ids = page_ids(f"https://www.youtube.com/channel/{CHANNEL_ID}/videos?hl=en")
    if ids is None:
        return None
    out = []
    for vid in ids[:15]:
        if vid in known:
            out.append(dict(id=vid, title=None, published="", description=None))   # already on the site: no page fetch needed
            continue
        d = watch_details(vid)
        if d:
            out.append(d)
    return out


def find_playlists(names):
    """Playlist ids by name, read from the channel's playlists page (best effort; a playlist id set by hand always wins)."""
    page = fetch(f"https://www.youtube.com/channel/{CHANNEL_ID}/playlists?hl=en", tries=1)
    if not page:
        return {}
    html = page.decode("utf8", "ignore")
    ids = [(m.start(), m.group(1)) for m in re.finditer(r'"(?:playlistId|contentId)":"(PL[\w-]{10,})"', html)]
    found = {}
    for name in names:
        spots = [m.start() for m in re.finditer(re.escape(json.dumps(name)), html)]
        best = min(((abs(s - p), pid) for s in spots for p, pid in ids), default=None)
        if best and best[0] < 4000:
            found[name] = best[1]
    return found


def is_short(vid):
    """YouTube answers /shorts/<id> with 200 for a Short and redirects a normal video to /watch."""
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    opener = urllib.request.build_opener(NoRedirect)
    try:
        return opener.open(urllib.request.Request(f"https://www.youtube.com/shorts/{vid}", headers=UA), timeout=20).status == 200
    except urllib.error.HTTPError as e:
        return False if 300 <= e.code < 400 else True  # on an unexpected error, treat it as a Short and skip it
    except (urllib.error.URLError, TimeoutError):
        return True


def main():
    dry = "--dry-run" in sys.argv
    ids = json.loads(IDS.read_text()) if IDS.exists() else {}
    store = json.loads(VIDEOS.read_text()) if VIDEOS.exists() else {}
    store.setdefault("items", []); store.setdefault("playlists", {}); store.setdefault("shorts", [])
    known = set(ids.values()) | {v["id"] for v in store["items"]} | set(store["shorts"])
    raw = fetch(FEED)
    from_page = raw is None
    if from_page:
        print("YouTube feed unavailable, reading the channel's Videos page instead")
        feed = channel_page_entries(known)
        if feed is None:
            print("::warning::YouTube feed and channel page unavailable, will try again on the next run")
            return
    else:
        feed = entries(raw)
    new = [v for v in feed if v["id"] and v["id"] not in known]
    show_list = shows()
    if new:
        missing = [n for k, n in show_list if k not in store["playlists"]]
        for name, pid in find_playlists(missing).items():
            key = next(k for k, n in show_list if n == name); store["playlists"][key] = pid
            print(f"playlist {name}: {pid}")
    members = {}
    for key, pid in store["playlists"].items():
        pl = fetch("https://www.youtube.com/feeds/videos.xml?playlist_id=" + pid, tries=1) if new else None
        if pl:
            members[key] = {v["id"] for v in entries(pl)}
        else:
            members[key] = set(page_ids("https://www.youtube.com/playlist?list=" + pid + "&hl=en") or []) if new else set()
    open_eps = [(n, t) for n, t in episodes() if str(n) not in ids]
    changed = []
    for v in new:
        if not from_page and is_short(v["id"]):
            print(f"skip Short {v['id']} {v['title']!r}"); store["shorts"] = (store["shorts"] + [v["id"]])[-300:]; changed.append("short")
            continue
        best = max(open_eps, key=lambda x: difflib.SequenceMatcher(None, norm(x[1]), norm(v["title"])).ratio(), default=None)
        score = difflib.SequenceMatcher(None, norm(best[1]), norm(v["title"])).ratio() if best else 0
        if score >= 0.9:
            print(f"Merit Test episode {best[0]}: {v['id']} {v['title']!r} (title match {score:.2f})")
            ids[str(best[0])] = v["id"]; open_eps.remove(best); changed.append(f"ep{best[0]}")
            continue
        text = (v["title"] + " " + v["description"]).lower()
        if "merit test" in text and not any(n.lower() in text for k, n in show_list):
            print(f"::warning::{v['id']} {v['title']!r} mentions The Merit Test but matches no planned title; add it to EPISODES in build.py")
            continue
        show = next((k for k, n in show_list if v["id"] in members.get(k, set())), None) \
            or next((k for k, n in show_list if n.lower() in text), None) or "other"
        print(f"{show}: {v['id']} {v['title']!r} ({v['published']})")
        store["items"].append(dict(id=v["id"], title=v["title"], published=v["published"], show=show,
                                   slug=slugify(v["title"]), description=v["description"])); changed.append(show)
    by_id = {v["id"]: v for v in feed}
    for it in store["items"]:                      # keep each page in step with its YouTube description and title
        f = by_id.get(it["id"])
        if f and f.get("title") and (it.get("description") != f["description"] or it["title"] != f["title"]):
            it["description"], it["title"] = f["description"], f["title"]; changed.append("updated " + it["id"])
        it.setdefault("slug", slugify(it["title"]))  # the address stays the same even if the title changes later
    if changed and not dry:
        IDS.write_text(json.dumps(dict(sorted(ids.items(), key=lambda x: int(x[0]))), indent=1) + "\n")
        # newest first; on the same day the one added later (uploaded later) comes first
        order = {id(v): i for i, v in enumerate(store["items"])}
        new_ids = [v["id"] for v in new]
        store["items"].sort(key=lambda x: (x["published"], -new_ids.index(x["id"]) if x["id"] in new_ids else -99, order[id(x)]), reverse=True)
        VIDEOS.write_text(json.dumps(store, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(feed)} videos in the feed, new: {changed or 'none'}{' (dry run)' if dry else ''}")


if __name__ == "__main__":
    main()
