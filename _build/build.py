"""Build the generated pages of davidparkphd.com from the data below.

Writes episodes/index.html, one page per episode, resources/index.html and sitemap.xml, and keeps the nav and
footer of every page (homepage and About included) the same. Hand-written pages keep their own body.

Release day for an episode (Release procedure step 4). Set its "youtube" id, run this, check, commit, push.

Email sign-up. The form posts to the email service in SIGNUP. Until its form id is set, the sign-up stays off the
live pages, so no form goes up that doesn't work. PREVIEW=1 python3 website/build.py shows it for a local check.

Usage: python3 website/build.py (or python3 website/site/_build/build.py, the same script)

This file lives in the site repo under _build/ (GitHub Pages does not publish folders that start with _), so the
GitHub job in .github/workflows/youtube-sync.yml can run it. YouTube ids live in _build/youtube.json, which that
job fills in when an episode goes public (_build/youtube_sync.py).
"""
import html, os, re
from datetime import date
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
BASE = "https://www.davidparkphd.com"
# The stylesheet link carries a hash of styles.css, so browsers load a changed stylesheet instead of a cached one.
import hashlib
CSS_V = hashlib.sha1((SITE / "styles.css").read_bytes()).hexdigest()[:8]

PARTS = [
    ("Is there anything here?", 1, 4),
    ("Can it work, and is it worth it for you?", 5, 10),
    ("How do you find out before you bet too much?", 11, 14),
    ("Can you build it and get the resources?", 15, 17),
    ("Can you make the case, and should you go ahead?", 18, 20),
]

# Episodes with a decided upload title (Series plan/Episode titles.md). Later ones appear as they are decided.
EPISODES = [
    dict(n=1, slug="is-your-business-idea-a-good-opportunity", title="Why a Good Idea Isn't Enough",
         youtube=None, chips=["MERIT"],
         card="Quibi had $1.75 billion and still missed one question. How to tell an idea you like from an opportunity worth pursuing.",
         lede="A good idea and a good opportunity are two different things. Here's how to tell them apart, before you've bet too much on it.",
         about=["In 2020, Quibi launched with $1.75 billion and leaders from the top of Hollywood and Silicon Valley, and about six months later it announced it was shutting down. Before the money went in, nobody had answered the one question it all rested on.",
                "This episode asks what would have to be true for an idea to work, and how sure you really are of each part. It runs Quibi through five questions, MERIT, then does the same for Maya, who wants to cook dinners for families with a new baby, and ends with a short exercise for your own idea."],
         merit=[("M", "Market", "Do enough people want it, badly enough?"),
                ("E", "Edge", "Why would they pick yours over what they do now?"),
                ("R", "Returns", "Will it make enough money to be worth it?"),
                ("I", "Implementation", "Can you build it and deliver it?"),
                ("T", "Team", "Are you the right people to do it?")],
         chapters=[("0:00", "Quibi's $1.75 billion question"), ("0:57", "A good idea or a good opportunity?"),
                   ("1:30", "Quibi, part by part"), ("3:02", "Maya's idea, at your own scale"), ("5:15", "Back to Quibi"),
                   ("5:53", "The MERIT test"), ("6:20", "Recap"), ("6:38", "Try this"), ("7:04", "The worksheet, and what's next")],
         worksheet="what-has-to-be-true",
         sources_title="Sources for the Quibi story",
         sources=[('Anthony Ha, TechCrunch, April 5, 2020, "Quibi launches its mobile streaming service in the middle of the quarantine era"', "https://techcrunch.com/2020/04/05/quibi-launches-its-mobile-streaming-service-in-the-middle-of-the-quarantine-era"),
                  ('Associated Press, October 21, 2020, "Short-video app Quibi shutting down just months after launch"', "https://www.ksat.com/business/2020/10/21/short-video-app-quibi-shutting-down-just-months-after-launch/"),
                  ('Quibi, October 21, 2020, "An open letter from Quibi" (archived copy)', "http://web.archive.org/web/20201022230831/https://quibi-hq.medium.com/an-open-letter-from-quibi-8af6b415377f"),
                  ('NBC News, October 22, 2020, "A look at why Quibi failed so soon after launching" (subscriber figures as reported, and the Katzenberg quote)', "https://www.nbcnews.com/business/business-news/look-why-quibi-failed-so-soon-after-launching-n1244312")],
         note="Maya is an illustrative example."),
    dict(n=2, slug="where-do-good-opportunities-come-from", title="Where Do Good Opportunities Come From?",
         youtube=None, chips=["Market", "MERIT"],
         card="Why some people spot opportunities everyone else misses, and where to look for your own.",
         lede="Good opportunities rarely come from trying to think one up. Here's where they usually start, and how to tell whether one is any good.",
         about=["Before Gymshark, Ben Francis tried apps and a website. What worked was a problem he had himself: he couldn't find gym clothes that fit, so he started sewing his own in his family's garage.",
                "This episode shows where good opportunities usually start: a real problem people already pay for, wait for or work around, in a place you know better than most, at a moment when something has changed. It looks at research on user entrepreneurs, then introduces MERIT, the five questions this series uses to judge an idea, and runs the Gymshark garage through it."],
         merit=[("M", "Market", "Who is the customer, how many are there, and will they pay?"),
                ("E", "Edge", "Why you, and what stops others copying you once it works?"),
                ("R", "Returns", "Does the price cover the cost, and is it worth it for you?"),
                ("I", "Implementation", "Can you build it, reach the people who want it and deliver?"),
                ("T", "Team", "Do you have the skills it takes, and who do you need to bring in?")],
         chapters=[("0:00", "Two people, one question"), ("0:55", "Where Gymshark came from"), ("1:57", "How you know a problem is real"),
                   ("2:24", "The person with the problem"), ("3:20", "From a fix to a business"), ("3:52", "What MERIT is"),
                   ("4:55", "The garage, letter by letter"), ("5:57", "What happened next"), ("6:49", "Finding yours"), ("7:50", "Next time")],
         worksheet="problem-journal-page",
         sources_title="Sources",
         sources=[("Shah, S. K., & Tripsas, M. (2007). The accidental entrepreneur: The emergent and collective process of user entrepreneurship. Strategic Entrepreneurship Journal, 1(1-2), 123-140", "https://doi.org/10.1002/sej.15"),
                  ("Park, Rha, Shah and Chattopadhyay (2024), Industrial and Corporate Change, 33(1), 64-89", "https://doi.org/10.1093/icc/dtad072"),
                  ('Gymshark, "The Official Gymshark Story" (the company\'s own account)', "https://www.gymshark.com/blog/article/the-official-gymshark-story"),
                  ("Forbes Australia, April 7, 2023, on Ben Francis and Gymshark", "https://www.forbes.com.au/news/billionaires/forbes-rich-list-gymshark-founder-ben-francis-rise-to-success/"),
                  ("Mark Sweney, The Guardian, July 3, 2026 (the 2020 valuation of 1.25 billion pounds)", "https://www.theguardian.com/business/2026/jul/03/gymshark-founder-ben-francis-stake-us-private-equity-firm")],
         note="The nurse is an illustrative example. Money is given in US dollars, converted from pounds at about $1.50 to the pound."),
    dict(n=3, slug=None, title="Who Should Be Your First Customer?", youtube=None, chips=["Market"],
         card="Why the first customer you pick matters more than the size of the market, and how to choose the one to start with."),
]

# YouTube ids, set by hand or by _build/youtube_sync.py when the episode goes public. Keys are episode numbers.
import json
_YT = json.loads((SITE / "_build" / "youtube.json").read_text()) if (SITE / "_build" / "youtube.json").exists() else {}
for _ep in EPISODES:
    _ep["youtube"] = _YT.get(str(_ep["n"])) or _ep["youtube"]

WORKSHEETS = {
    "what-has-to-be-true": dict(name="What Has to Be True? Worksheet", ep=1, pdf="what-has-to-be-true-worksheet.pdf",
                                img="worksheet-01-preview.jpg",
                                text="Write down what a business depends on, and see which parts you know and which you only believe. The five MERIT questions and the exercise from episode 1, on one page."),
    "problem-journal-page": dict(name="Problem Journal Page", ep=2, pdf="problem-journal-page.pdf",
                                 img="worksheet-02-preview.jpg",
                                 panel="Five problems from a place you know, and the one MERIT question to answer next, on one page.",
                                 text="Write down five problems people pay for, wait for or work around in a place you know, star your favorite, and note the one MERIT question you can't answer about it yet. From episode 2, on one page."),
}

# Kit (kit.com) form. Set form_id from the form's embed code (Kit > Grow > Landing pages and forms > the form > Embed > HTML).
SIGNUP = dict(form_id="10049880")
SIGNUP_LIVE = bool(SIGNUP["form_id"])
SIGNUP_SHOWN = SIGNUP_LIVE or os.environ.get("PREVIEW") == "1"

NAV = [("Shows", "/shows/"), ("Courses", "/courses/"), ("Resources", "/resources/"), ("Book", "/#book"), ("About", "/about.html")]
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@112,600;112,800&family=Oswald:wght@500;600;700&family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">'
FOOTER = """<footer>
 <div class="wrap">
  <a class="logo" href="/"><img src="/images/logo-dark.png" width="400" height="44" alt="David Park PhD"></a>
 </div>
</footer>"""
e = html.escape


def nav(active=None):
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{h}"{cur if t == active else ""}>{t}</a>' for t, h in NAV)
    return f' <nav>\n  <a class="logo" href="/"><img src="/images/logo.png" width="400" height="44" alt="David Park PhD"></a>\n  <div class="menu">{links}</div>\n </nav>'


def signup():
    if not SIGNUP_SHOWN:
        return "<!-- signup --><!-- /signup -->"
    action = f"https://app.kit.com/forms/{SIGNUP['form_id']}/subscriptions" if SIGNUP_LIVE else "#"
    return f"""<!-- signup -->
<section class="join" id="signup">
 <div class="wrap">
  <div>
   <div class="kicker">Free email</div>
   <h2>Get each new episode and its <span class="mark">worksheet</span></h2>
   <p>One short email when a new episode comes out, with the worksheet that goes with it. No spam, and you can unsubscribe at any time.</p>
  </div>
  <form class="signup" action="{action}" method="post">
   <label class="sr" for="signup-email">Email address</label>
   <input id="signup-email" type="email" name="email_address" placeholder="Your email address" autocomplete="email" required>
   <button class="btn coral" type="submit">Sign up</button>
  </form>
  <div class="fine">By signing up you agree to receive these emails. See the <a href="/privacy.html">privacy note</a>.</div>
 </div>
</section>
<!-- /signup -->"""


def page(path, title, desc, body, active=None, image="og-image.jpg"):
    url = BASE + "/" + path.replace("index.html", "")
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{image if image.startswith("http") else BASE + "/images/" + image}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-32.png">
<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="/styles.css?v={CSS_V}">
</head>
<body>
<div class="wrap">
{nav(active)}
{body}
</div>

{signup()}
{FOOTER}
</body>
</html>
"""
    out = SITE / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    return url


def part_of(n):
    return next(i for i, p in enumerate(PARTS, 1) if p[1] <= n <= p[2])


def chips(ep):
    k = part_of(ep["n"])
    return "".join(f'<span class="chip c">{e(c)}</span>' for c in ep["chips"]) + f'<span class="chip">Part {k}. {e(PARTS[k - 1][0])}</span>'


def ep_href(ep):
    return f"/episodes/{ep['slug']}.html" if ep.get("slug") else None


def card(ep):
    href = ep_href(ep)
    top = f'<img src="/images/ep{ep["n"]:02d}-thumbnail.jpg" alt="Episode {ep["n"]} thumbnail">' if href else '<div class="ph grid">Coming next</div>'
    inner = f"""
    {top}
    <div class="body">
     <div class="kicker">EP. {ep["n"]}</div>
     <h3>{e(ep["title"])}</h3>
     <p>{e(ep["card"])}</p>
     <div class="chips">{chips(ep)}</div>
    </div>
   """
    return f'   <a class="card" href="{href}">{inner}</a>' if href else f'   <div class="card">{inner}</div>'


def worksheet_offer(key, link_episode=True):
    w = WORKSHEETS[key]
    ep = next(x for x in EPISODES if x["n"] == w["ep"])
    kb = round((SITE / "resources" / w["pdf"]).stat().st_size / 1024)
    goes = f'<a href="{ep_href(ep)}">Episode {ep["n"]}. {e(ep["title"])}</a>' if link_episode else f'Episode {ep["n"]}'
    return f"""  <div class="offer">
   <img src="/images/{w["img"]}" alt="The {e(w["name"])}">
   <div>
    <div class="kicker">Worksheet for episode {ep["n"]}</div>
    <h2>{e(w["name"])}</h2>
    <p>{e(w["text"])}</p>
    <a class="btn coral" href="/resources/{w["pdf"]}" download>Download the worksheet (PDF, {kb} KB)</a>
    <div class="fine">Goes with {goes}. Free to use and share with credit.</div>
   </div>
  </div>"""


def episode_page(ep, nxt):
    k = part_of(ep["n"])
    if ep["youtube"]:
        player = f'<iframe src="https://www.youtube-nocookie.com/embed/{ep["youtube"]}" title="{e(ep["title"])}" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>'
        stamp = lambda t, s: f'<a href="https://www.youtube.com/watch?v={ep["youtube"]}&amp;t={sum(int(x) * 60 ** i for i, x in enumerate(reversed(t.split(":"))))}s"><time>{t}</time>{e(s)}</a>'
    else:
        player = f'<img src="/images/ep{ep["n"]:02d}-thumbnail.jpg" alt="Episode {ep["n"]} thumbnail"><span class="soon">Coming to YouTube soon</span>'
        stamp = lambda t, s: f"<time>{t}</time>{e(s)}"
    merit = "".join(f'<li><b>{l}</b><div><strong>{e(w)}</strong>{e(q)}</div></li>' for l, w, q in ep["merit"])
    chapters = "".join(f"<li>{stamp(t, s)}</li>" for t, s in ep["chapters"])
    sources = "".join(f'<li>{e(t)}, <a href="{u}">{e(u.split("//")[1].split("/")[0].replace("www.", ""))}</a></li>' for t, u in ep["sources"])
    w = WORKSHEETS[ep["worksheet"]]
    nhref = ep_href(nxt) if nxt else None
    ntitle = f'<a href="{nhref}">{e(nxt["title"])}</a>' if nhref else e(nxt["title"])
    body = f""" <section class="pagehead">
  <div class="crumb"><a href="/courses/">Evidence-Based Entrepreneurship</a> / Part {k}. {e(PARTS[k - 1][0])}</div>
  <div class="kicker">Episode {ep["n"]}</div>
  <h1 class="ph1">{e(ep["title"])}</h1>
  <p class="lede">{e(ep["lede"])}</p>
 </section>

 <div class="ep">
  <div>
   <div class="player">{player}</div>
   <div class="prose">
    <h2>About this episode</h2>
    {"".join(f"<p>{e(p)}</p>" for p in ep["about"])}
    <h2>The five MERIT questions</h2>
    <p>For each one, write down what would have to be true, how good it looks, and how you know.</p>
    <ol class="qlist">{merit}</ol>
    <h2>Chapters</h2>
    <ol class="chapters">{chapters}</ol>
    <h2>{e(ep["sources_title"])}</h2>
    <ul class="sources">{sources}</ul>
    <p class="note">{e(ep["note"])}</p>
   </div>
  </div>
  <aside class="side">
   <div class="panel">
    <img src="/images/{w["img"]}" alt="The {e(w["name"])}">
    <div class="kicker">Free worksheet</div>
    <h3>{e(w["name"])}</h3>
    <p>{e(w.get("panel", "The five questions and the exercise from this episode, on one page."))}</p>
    <a class="btn coral" href="/resources/{w["pdf"]}" download>Download (PDF)</a>
   </div>
   <div class="panel">
    <div class="kicker">Next episode</div>
    <h3>{ntitle}</h3>
    <p>{e(nxt["card"])}{"" if nhref else " Coming soon."}</p>
   </div>
  </aside>
 </div>"""
    return page(f"episodes/{ep['slug']}.html", f"{ep['title']} | David Park PhD", ep["card"], body, "Episodes", image=f"ep{ep['n']:02d}-thumbnail.jpg")


def episodes_index():
    parts = []
    for i, (name, a, b) in enumerate(PARTS, 1):
        out = [x for x in EPISODES if a <= x["n"] <= b and ep_href(x)]
        status = ", ".join(f'<a href="{ep_href(x)}">Episode {x["n"]} {"is out" if x["youtube"] else "coming soon"}</a>' for x in out) or "Coming soon"
        rng = f"Episodes {a} and {b}" if b == a + 1 else f"Episodes {a} to {b}"
        parts.append(f'<div class="part"><b>{i}</b><div><h3>{e(name)}</h3><small>{rng}. {status}</small></div></div>')
    body = f""" <section class="pagehead">
  <div class="kicker">Evidence-Based Entrepreneurship Series</div>
  <h1 class="ph1">Episodes</h1>
  <p class="lede">Twenty episodes on one question. You have a business idea. Is it worth pursuing? Each one comes with a free worksheet.</p>
 </section>
 <section class="tight">
  <div class="cards">
{chr(10).join(card(x) for x in EPISODES)}
  </div>
 </section>
 <section>
  <div class="head"><h2>The series in five parts</h2></div>
  <div class="parts">{"".join(parts)}</div>
 </section>"""
    return page("episodes/index.html", "Episodes | David Park PhD", "All episodes of the Evidence-Based Entrepreneurship series from David Park PhD, with a free worksheet for each.", body, "Episodes")


# The Merit Test course stays "coming soon" until episode 1 is public on the David Park PhD channel (WD-61): youtube_sync.py
# then records its id and the banner, the course page and the homepage course row switch to the episodes by themselves.
COURSE_SOON = not _YT.get("1")

# Show episodes and other full videos from the channel, written by youtube_sync.py (newest first).
_VID = json.loads((SITE / "_build" / "videos.json").read_text()) if (SITE / "_build" / "videos.json").exists() else {}
VIDEOS = _VID.get("items", [])
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

# Shows (WD-55, WD-59, WD-62, WD-63). Add a show here when it launches; "first" stays None until its first episode is out.
SHOWS = [
    dict(key="now", tag="NOW", name="Business Now", line="Business news, checked against the evidence.",
         about="One story in the news, what the research says about it, and what it means for founders.", first=None),
    dict(key="story", tag="STORY", name="Business Story", line="One company's story, and the research that explains it.",
         about="A well-known company, why it worked or failed, and the lesson founders can use.", first=None),
]


def show_cover(s):
    # the approved stacked lockup, as in the videos (WD-59; Business Story's is provisional, WD-62)
    return f"""<div class="scover"><img src="/images/shows/business-{s["key"]}-lockup.png" alt="{e(s["name"])} with David Park PhD"></div>"""


def merit_cover():
    tiles = "".join('<b class="o">R</b>' if c == "R" else f"<b>{c}</b>" for c in "MERIT")
    return f'<div class="mcover"><div class="the">THE</div><div class="mtiles">{tiles}</div><div class="the">TEST</div></div>'


def show_videos(key):
    return [v for v in VIDEOS if v["show"] == key]


def when(v):
    y, m = v["published"][:4], v["published"][5:7]
    return f"{MONTHS[int(m) - 1]} {y}" if y and m else ""


def video_href(v):
    return f"/episodes/{v.get('slug') or re.sub('[^a-z0-9]+', '-', v['title'].lower()).strip('-')}.html"


def linkify(text):
    out, last = [], 0
    for m in re.finditer(r"https?://[^\s<>()]+[^\s<>().,;]", text):
        out.append(e(text[last:m.start()])); u = m.group(0)
        out.append(f'<a href="{e(u)}">{e(u.split("//", 1)[1].split("/")[0].replace("www.", ""))}</a>'); last = m.end()
    return "".join(out) + e(text[last:])


SOCIAL_LINE = re.compile(r"^(instagram|youtube|website|linkedin|tiktok|x|twitter)\b.*https?://", re.I)


def show_episode_page(v):
    """A page for one show episode, built from its YouTube description: summary, chapters, sources and notes."""
    show = next((s for s in SHOWS if s["key"] == v["show"]), None)
    name = show["name"] if show else "Video"
    blocks = [bl.strip() for bl in re.split(r"\n\s*\n", v.get("description", "")) if bl.strip()]
    about, notes, chapters, sources, seen_chapters = [], [], [], [], False
    for bl in blocks:
        lines = [l.strip() for l in bl.split("\n") if l.strip()]
        head = lines[0].rstrip(":").lower()
        if head == "chapters":
            seen_chapters = True
            for l in lines[1:]:
                m = re.match(r"(\d+(?::\d+)+)\s+(.*)", l)
                if m:
                    secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(m.group(1).split(":"))))
                    chapters.append(f'<li><a href="https://www.youtube.com/watch?v={v["id"]}&amp;t={secs}s"><time>{m.group(1)}</time>{e(m.group(2))}</a></li>')
        elif head in ("sources", "references"):
            sources += [f"<li>{linkify(l)}</li>" for l in lines[1:]]
        elif all(SOCIAL_LINE.match(l) for l in lines) or all(l.startswith("#") for l in lines):
            continue                                    # account links and hashtags stay on YouTube
        else:
            (notes if seen_chapters else about).append("<p>" + "<br>".join(linkify(l) for l in lines) + "</p>")
    player = f'<iframe src="https://www.youtube-nocookie.com/embed/{v["id"]}" title="{e(v["title"])}" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>'
    sec = lambda title, inner: f"<h2>{title}</h2>{inner}" if inner else ""
    others = [x for x in show_videos(v["show"]) if x["id"] != v["id"]][:3]
    more = "".join(f'<li><a href="{video_href(x)}">{e(x["title"])}</a></li>' for x in others)
    body = f""" <section class="pagehead">
  <div class="crumb"><a href="/shows/">Shows</a> / <a href="/shows/#{v["show"]}">{e(name)}</a></div>
  <div class="kicker">{e(name)} · {when(v)}</div>
  <h1 class="ph1">{e(v["title"])}</h1>
 </section>

 <div class="ep">
  <div>
   <div class="player">{player}</div>
   <div class="prose">
    {sec("About this episode", "".join(about))}
    {sec("Chapters", '<ol class="chapters">' + "".join(chapters) + "</ol>" if chapters else "")}
    {sec("Sources", '<ul class="sources">' + "".join(sources) + "</ul>" if sources else "")}
    {"".join(n.replace("<p>", '<p class="note">', 1) for n in notes)}
   </div>
  </div>
  <aside class="side">
   <div class="panel">
    {show_cover(show) if show else ""}
    <div class="kicker">Show</div>
    <h3>{e(name)}</h3>
    <p>{e(show["line"]) if show else ""}</p>
    <a class="btn coral" href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener">Watch on YouTube</a>
   </div>
   {f'<div class="panel"><div class="kicker">More from {e(name)}</div><ul class="morelist">{more}</ul></div>' if more else ""}
  </aside>
 </div>"""
    desc = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", about[0]))[:200] if about else v["title"]
    return page(video_href(v).lstrip("/"), f"{v['title']} | {name} | David Park PhD", desc, body, "Shows",
                image=f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg")


def video_card(v, label):
    return f"""   <a class="card" href="{video_href(v)}">
    <img src="https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg" alt="" loading="lazy">
    <div class="body">
     <div class="kicker">{e(label)} · {when(v)}</div>
     <h3>{e(v["title"])}</h3>
    </div>
   </a>"""


def home_show_cards():
    out = []
    for s in SHOWS:
        vids = show_videos(s["key"])
        latest = (f'<p class="latest-ep"><span>Latest episode</span><a href="{video_href(vids[0])}">{e(vids[0]["title"])}</a></p>' if vids
                  else '<div class="chips"><span class="chip">First episodes coming soon</span></div>')
        out.append(f"""   <div class="card showcard">
    <a href="/shows/#{s["key"]}" aria-label="{e(s["name"])}">{show_cover(s)}</a>
    <div class="body">
     <div class="kicker">Show</div>
     <h3><a href="/shows/#{s["key"]}">{e(s["name"])}</a></h3>
     <p>{e(s["line"])}</p>
     {latest}
    </div>
   </div>""")
    return "<!-- shows -->\n" + "\n".join(out) + "\n   <!-- /shows -->"

def course_card(wide):
    chips = ('<span class="chip c">Coming soon</span><span class="chip">20 episodes</span><span class="chip">Free worksheets</span>' if COURSE_SOON
             else '<span class="chip c">MERIT</span><span class="chip">Free worksheets</span>')
    return f"""   <a class="card coursecard{" wide" if wide else ""}" href="/courses/">
    {merit_cover()}
    <div class="body">
     <div class="kicker">Free course</div>
     <h3>The Merit Test</h3>
     <p>You have a business idea. Is it worth pursuing? Short episodes in order, each with a one-page worksheet.</p>
     <div class="chips">{chips}</div>
    </div>
   </a>"""


def course_hero(tag, where):
    """The course card: David's original grid-paper hero, with his photo and credentials (as on the site before WD-63)."""
    first = next((x for x in EPISODES if ep_href(x)), EPISODES[0])
    label = "Evidence-Based Entrepreneurship · Free course" + (", coming soon" if COURSE_SOON else "")
    if COURSE_SOON:
        btns = ('<a class="btn coral" href="/courses/">About the course</a>' if where == "home" else "") + '<a class="btn ghost" href="/resources/">Free worksheets</a>'
        soon = '<p class="soon-note">The course starts soon. Sign up below to hear when episode 1 is out.</p>' if where == "courses" else ""
    else:
        btns = f'<a class="btn coral" href="{ep_href(first)}">Start with episode 1</a><a class="btn ghost" href="/resources/">Free worksheets</a>'
        soon = ""
    creds = ('<div class="creds"><span>David Park <b class="phd">PhD</b>, professor of entrepreneurship at Syracuse University</span><span>Poets&amp;Quants Best 40 Under 40 MBA Professor</span><span>Poets&amp;Quants Top 50 Undergrad Business Professor</span><span>SBA Instructor of the Year</span></div>'
             if where == "courses" else "")   # the homepage card leaves out the name and awards (David, 2026-11-05)
    return f""" <div class="hero grid course-hero on-{where}">
  <div class="copy">
   <div class="series">{label}</div>
   <{tag} class="hh">Evidence-based tools<br> <span class="nw">for <em>starting a business.</em></span></{tag}>
   <p>Before you bet your savings or your career on a business idea, find out what has to be true for it to work. Short episodes built on research, and a free worksheet to test your own idea.</p>
   {soon}{btns}
  </div>
  <div class="photo"><img src="/images/david-park-headshot.webp" alt="David Park"></div>
  {creds}
 </div>"""


def shows_index():
    blocks = []
    for s in SHOWS:
        vids = show_videos(s["key"])
        status = (f'<a class="btn coral" href="{video_href(vids[0])}">Watch the latest episode</a>' if vids
                  else '<p class="soon-note">The first episodes are coming soon. Sign up below to hear when they are out.</p>')
        grid = (f'\n  <div class="cards showeps">\n' + "\n".join(video_card(v, s["name"]) for v in vids) + "\n  </div>") if vids else ""
        blocks.append(f""" <section class="tight show" id="{s["key"]}">
  <div class="showrow">
   {show_cover(s)}
   <div>
    <div class="kicker">Show</div>
    <h2>{e(s["name"])}</h2>
    <p class="lede">{e(s["line"])}</p>
    <p>{e(s["about"])}</p>
    {status}
   </div>
  </div>{grid}
 </section>""")
    body = """ <section class="pagehead">
  <div class="kicker">Shows</div>
  <h1 class="ph1">Shows</h1>
  <p class="lede">Short shows on business, each one checked against the research.</p>
 </section>
""" + "\n".join(blocks)
    other = show_videos("other")
    if other:
        body += '\n <section class="tight show" id="more">\n  <div class="head"><h2>More videos</h2></div>\n  <div class="cards">\n' + "\n".join(video_card(v, "Video") for v in other) + "\n  </div>\n </section>"
    return page("shows/index.html", "Shows | David Park PhD", "Business Now and Business Story with David Park PhD: business news and company stories, checked against the research.", body, "Shows")


def courses_index():
    parts = []
    for i, (name, a, bb) in enumerate(PARTS, 1):
        out = [x for x in EPISODES if a <= x["n"] <= bb and ep_href(x)]
        status = "Coming soon" if COURSE_SOON else (", ".join(f'<a href="{ep_href(x)}">Episode {x["n"]} {"is out" if x["youtube"] else "coming soon"}</a>' for x in out) or "Coming soon")
        rng = f"Episodes {a} and {bb}" if bb == a + 1 else f"Episodes {a} to {bb}"
        parts.append(f'<div class="part"><b>{i}</b><div><h3>{e(name)}</h3><small>{rng}. {status}</small></div></div>')
    merit = "".join(f"<span><b>{l}</b>{w}</span>" for l, w in [("M", "Market"), ("E", "Edge"), ("R", "Returns"), ("I", "Implementation"), ("T", "Team")])
    first = next((x for x in EPISODES if ep_href(x)), EPISODES[0])
    body = f""" <section class="pagehead tight-top">
{course_hero("h1", "courses")}
 </section>
 {"" if COURSE_SOON else chr(10).join([' <section class="tight">', '  <div class="cards">', chr(10).join(card(x) for x in EPISODES), '  </div>', ' </section>'])}
 <section>
  <div class="topics">
   <div class="tbox">
    <h3>The Merit Test</h3>
    <p>The framework David Park developed and uses throughout the course: five plain questions to ask about any business.</p>
    <div class="merit">{merit}</div>
   </div>
   <div class="tbox">
    <h3>The course in five parts</h3>
    <p>From a first idea to the decision to go ahead.</p>
    <div class="parts">{"".join(parts)}</div>
   </div>
  </div>
 </section>"""
    return page("courses/index.html", "Evidence-Based Entrepreneurship | Free course | David Park PhD",
                ("Coming soon. " if COURSE_SOON else "") + "Evidence-Based Entrepreneurship, a free course from David Park PhD: 20 short episodes on whether a business idea is worth pursuing, built on his Merit Test framework, with a free worksheet for each.", body, "Courses")


def episodes_redirect():
    """/episodes/ moved to /courses/ (WD-63). Episode pages keep their own addresses."""
    (SITE / "episodes/index.html").write_text("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>The Merit Test | David Park PhD</title>
<meta http-equiv="refresh" content="0; url=/courses/"><link rel="canonical" href="https://www.davidparkphd.com/courses/">
<meta name="robots" content="noindex"></head>
<body><p>The episodes are now in <a href="/courses/">The Merit Test course</a>.</p></body></html>
""")


def resources_index():
    body = f""" <section class="pagehead">
  <div class="kicker">Free resources</div>
  <h1 class="ph1">Resources</h1>
  <p class="lede">One-page worksheets that go with the episodes, for working through your own idea. Free to use and share with credit.</p>
 </section>
 <section class="tight">
  <div class="head"><h2>Worksheets</h2></div>
{chr(10).join(worksheet_offer(k) for k in WORKSHEETS)}
 </section>
 <section>
  <div class="tbox soonbox">
   <h3>More on the way</h3>
   <p>A new worksheet comes with each episode, and short guides for hands-on steps will follow. New ones appear here first.</p>
  </div>
 </section>"""
    return page("resources/index.html", "Resources | David Park PhD", "Free one-page worksheets for Evidence-Based Entrepreneurship, the free course from David Park PhD.", body, "Resources")



def home_latest():
    """The homepage banner and its two episode cards: the newest episode that is out (or episode 1) and the one after it."""
    from datetime import date as _d
    fresh = [v for v in VIDEOS if v["show"] != "other" and v["published"] and (_d.today() - _d.fromisoformat(v["published"])).days <= 14]
    show_strip = None
    if fresh:
        v = fresh[0]; name = next(s["name"] for s in SHOWS if s["key"] == v["show"])
        show_strip = f'<div class="strip">New on {e(name)}. <a href="{video_href(v)}"><b>{e(v["title"])}</b></a> Watch it now.</div>'
    if COURSE_SOON:
        return (show_strip or '<div class="strip">Coming soon. <b>Evidence-Based Entrepreneurship</b>, a free course in 20 short episodes, each with a free worksheet.</div>',
                "<!-- latest -->\n" + course_hero("h2", "home") + "\n   <!-- /latest -->")
    out = [x for x in EPISODES if x["youtube"] and ep_href(x)]
    latest = out[-1] if out else EPISODES[0]
    i = EPISODES.index(latest)
    cards = course_hero("h2", "home") + '\n  <div class="cards course-latest">\n' + "\n".join(card(x) for x in EPISODES[i:i + 2]) + "\n  </div>"
    if out:
        strip = show_strip or f'<div class="strip">New episode. <a href="{ep_href(latest)}"><b>{e(latest["title"])}</b></a> Watch it now, with its free worksheet.</div>'
    else:
        strip = '<div class="strip">New free course. <b>Evidence-Based Entrepreneurship</b>. Episode 1 is coming soon, and its free worksheet is ready now.</div>'
    return strip, "<!-- latest -->\n" + cards + "\n   <!-- /latest -->"


def sync_shared(path, active=None):
    """Give a hand-written page the shared nav and footer."""
    p = SITE / path
    s = p.read_text()
    s = re.sub(r" <nav>.*?</nav>", lambda m: nav(active), s, count=1, flags=re.S)
    s = re.sub(r"<footer>.*?</footer>", lambda m: FOOTER, s, count=1, flags=re.S)
    s = re.sub(r'href="/styles\.css(\?v=\w+)?"', f'href="/styles.css?v={CSS_V}"', s)
    s = re.sub(r"\n?<!-- signup -->.*?<!-- /signup -->\n?", "\n", s, flags=re.S)
    s = s.replace("\n<footer>", "\n" + signup() + "\n<footer>", 1)
    if path == "index.html":
        strip, latest = home_latest()
        s = re.sub(r'<div class="strip">.*?</div>', lambda m: strip, s, count=1, flags=re.S)
        s = re.sub(r"<!-- latest -->.*?<!-- /latest -->", lambda m: latest, s, count=1, flags=re.S)
        s = re.sub(r"<!-- shows -->.*?<!-- /shows -->", lambda m: home_show_cards(), s, count=1, flags=re.S)
    p.write_text(s)


def signup_pages():
    """The privacy note and the thank-you page the email service sends people to after they sign up."""
    if not SIGNUP_SHOWN:
        return []
    privacy = """ <section class="pagehead prose">
  <div class="kicker">Privacy</div>
  <h1 class="ph1">Privacy note</h1>
  <p class="lede">What happens to your email address when you sign up.</p>
  <h2>What is collected</h2>
  <p>Only the email address you type into the sign-up form.</p>
  <h2>What it is used for</h2>
  <p>To send you an email when a new episode and its worksheet come out. It is never sold or shared for anyone else's marketing.</p>
  <h2>Who handles it</h2>
  <p>The list is kept by Kit (kit.com), the email service that sends the emails. Kit may record whether an email was opened, to help keep the list healthy.</p>
  <h2>Leaving the list</h2>
  <p>Every email has an unsubscribe link. One click removes you, and you can also reply to any email to ask for your address to be deleted.</p>
  <p class="note">This site itself sets no cookies and runs no tracking.</p>
 </section>"""
    thanks = """ <section class="pagehead">
  <div class="kicker">Almost done</div>
  <h1 class="ph1">Check your inbox</h1>
  <p class="lede">An email is on its way to confirm your address. Click the button in it, and you're on the list.</p>
  <p style="margin-top:28px"><a class="btn coral" href="/resources/">Get the free worksheets</a><a class="btn ghost" href="/courses/">Start the free course</a></p>
 </section>"""
    urls = [page("privacy.html", "Privacy note | David Park PhD", "What happens to your email address when you sign up for David Park PhD emails.", privacy)]
    page("thanks.html", "Thanks for signing up | David Park PhD", "Check your inbox to confirm your sign-up.", thanks)
    return urls


def main():
    urls = [BASE + "/", BASE + "/about.html", shows_index(), courses_index(), resources_index()]
    urls += [show_episode_page(v) for v in VIDEOS]
    episodes_redirect()
    eps = [x for x in EPISODES]
    for i, ep in enumerate(eps):
        if ep_href(ep):
            urls.append(episode_page(ep, eps[i + 1] if i + 1 < len(eps) else None))
    urls += signup_pages() if SIGNUP_LIVE else []
    if SIGNUP_SHOWN and not SIGNUP_LIVE:
        signup_pages()
    for k, w in WORKSHEETS.items():
        urls.append(f"{BASE}/resources/{w['pdf']}")
    sync_shared("index.html")
    sync_shared("about.html", "About")
    today = date.today().isoformat()
    (SITE / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    print("\n".join(urls))


if __name__ == "__main__":
    main()
