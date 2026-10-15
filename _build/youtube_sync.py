"""Find newly public episodes on the YouTube channel and record their video ids for the website.

Reads the channel's public feed (no key needed), matches each full video to an episode in build.py by its title,
and writes the id to _build/youtube.json. Shorts, other videos (such as the Korean series) and episodes that
already have an id are left alone. Prints what it found. Exit code 0 always, so a quiet run is not an error.

Usage
    python3 _build/youtube_sync.py            update youtube.json
    python3 _build/youtube_sync.py --dry-run  only print what it would do

Run by .github/workflows/youtube-sync.yml every 15 minutes, which then runs build.py and publishes.
"""
import difflib
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CHANNEL_ID = "UCZlZS_ah1zGoWDMqqwSMScg"  # youtube.com/@davidparkphd
FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
HERE = Path(__file__).resolve().parent
IDS = HERE / "youtube.json"
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t.lower())).strip()


def episodes():
    """Episode numbers and titles straight from build.py's EPISODES list, without running the build."""
    src = (HERE / "build.py").read_text()
    return [(int(n), t) for n, t in re.findall(r'dict\(n=(\d+),.*?title="([^"]+)"', src, re.S)]


def is_short(vid):
    """YouTube answers /shorts/<id> with 200 for a Short and redirects a normal video to /watch."""
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    opener = urllib.request.build_opener(NoRedirect)
    try:
        return opener.open(urllib.request.Request(f"https://www.youtube.com/shorts/{vid}", headers={"User-Agent": "Mozilla/5.0"}), timeout=20).status == 200
    except urllib.error.HTTPError as e:
        return False if 300 <= e.code < 400 else True  # on an unexpected error, treat it as a Short and skip it


def main():
    dry = "--dry-run" in sys.argv
    ids = json.loads(IDS.read_text()) if IDS.exists() else {}
    feed = ET.fromstring(urllib.request.urlopen(urllib.request.Request(FEED, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read())
    videos = [(e.findtext("yt:videoId", namespaces=NS), e.findtext("a:title", namespaces=NS) or "") for e in feed.findall("a:entry", NS)]
    open_eps = [(n, t) for n, t in episodes() if str(n) not in ids]
    known = set(ids.values())
    changed = []
    for vid, title in videos:
        if vid in known:
            continue
        best = max(open_eps, key=lambda x: difflib.SequenceMatcher(None, norm(x[1]), norm(title)).ratio(), default=None)
        if not best:
            break
        score = difflib.SequenceMatcher(None, norm(best[1]), norm(title)).ratio()
        if score < 0.9:
            continue
        if is_short(vid):
            print(f"skip Short {vid} {title!r}")
            continue
        print(f"episode {best[0]}: {vid} {title!r} (title match {score:.2f})")
        ids[str(best[0])] = vid
        known.add(vid)
        open_eps.remove(best)
        changed.append(best[0])
    if changed and not dry:
        IDS.write_text(json.dumps(dict(sorted(ids.items(), key=lambda x: int(x[0]))), indent=1) + "\n")
    print(f"{len(videos)} videos in the feed, new episodes: {changed or 'none'}{' (dry run)' if dry else ''}")


if __name__ == "__main__":
    main()
