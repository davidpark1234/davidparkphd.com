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
    dict(n=1, slug="is-your-business-idea-a-good-opportunity", title="Is Your Business Idea a Good Opportunity?",
         youtube=None, chips=["MERIT"],
         card="How to tell an idea you like from an opportunity worth pursuing, by asking what would have to be true for it to work.",
         lede="Liking an idea and knowing it's a good opportunity are two different things. Here's how to tell them apart, before you've bet too much on it.",
         about=["Through Maya, who wants to cook dinners for families with a new baby, this episode shows a different question to ask about any idea. What would have to be true for it to work? Then, for each of those claims, how good does it look, and how do you know?",
                "It ends with MERIT, five plain questions you can use on any business, and a short exercise. You don't need any other episode to use them."],
         merit=[("M", "Market", "Do enough people want it, badly enough?"),
                ("E", "Edge", "Why would they pick yours over what they do now?"),
                ("R", "Returns", "Will it make enough money to be worth it?"),
                ("I", "Implementation", "Can you build it and deliver it?"),
                ("T", "Team", "Are you the right people to do it?")],
         chapters=[("0:00", "Should you go for it?"), ("0:29", "Maya's idea"), ("1:08", "An idea or an opportunity?"),
                   ("1:41", "What would have to be true"), ("2:44", "Two questions, how good and how do you know"),
                   ("3:14", "Weak spots are not an exam"), ("4:46", "Found or made"), ("5:08", "Quibi"),
                   ("5:58", "MERIT"), ("6:49", "Try it yourself")],
         worksheet="what-has-to-be-true",
         sources_title="Sources for the Quibi story",
         sources=[('Anthony Ha, TechCrunch, April 5, 2020, "Quibi launches its mobile streaming service in the middle of the quarantine era"', "https://techcrunch.com/2020/04/05/quibi-launches-its-mobile-streaming-service-in-the-middle-of-the-quarantine-era"),
                  ("Fortune, April 6, 2020", "https://fortune.com/2020/04/06/quibi-launch-coronavirus-pandemic"),
                  ('Associated Press, October 21, 2020, "Short-video app Quibi shutting down just months after launch"', "https://www.ksat.com/business/2020/10/21/short-video-app-quibi-shutting-down-just-months-after-launch/"),
                  ('Quibi, October 21, 2020, "An open letter from Quibi" (archived copy)', "http://web.archive.org/web/20201022230831/https://quibi-hq.medium.com/an-open-letter-from-quibi-8af6b415377f")],
         note="Maya and the corner café are illustrative examples."),
    dict(n=2, slug=None, title="Where Do Good Opportunities Come From?", youtube=None, chips=["Market"],
         card="Why some people spot opportunities everyone else misses, and where to look for your own."),
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
}

# Kit (kit.com) form. Set form_id from the form's embed code (Kit > Grow > Landing pages and forms > the form > Embed > HTML).
SIGNUP = dict(form_id="10049880")
SIGNUP_LIVE = bool(SIGNUP["form_id"])
SIGNUP_SHOWN = SIGNUP_LIVE or os.environ.get("PREVIEW") == "1"

NAV = [("Episodes", "/episodes/"), ("Resources", "/resources/"), ("Topics", "/#topics"), ("Book", "/#book"), ("About", "/about.html")]
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">'
FOOTER = """<footer>
 <div class="wrap">
  <a class="logo" href="/">David Park <span>PhD</span></a>
 </div>
</footer>"""
e = html.escape


def nav(active=None):
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{h}"{cur if t == active else ""}>{t}</a>' for t, h in NAV)
    return f' <nav>\n  <a class="logo" href="/">David Park <span>PhD</span></a>\n  <div class="menu">{links}</div>\n </nav>'


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
<meta property="og:image" content="{BASE}/images/{image}">
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
  <div class="crumb"><a href="/episodes/">Episodes</a> / Part {k}. {e(PARTS[k - 1][0])}</div>
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
    <p>The five questions and the exercise from this episode, on one page.</p>
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
    return page("resources/index.html", "Resources | David Park PhD", "Free worksheets for the Evidence-Based Entrepreneurship series from David Park PhD.", body, "Resources")



def home_latest():
    """The homepage banner and its two episode cards: the newest episode that is out (or episode 1) and the one after it."""
    out = [x for x in EPISODES if x["youtube"] and ep_href(x)]
    latest = out[-1] if out else EPISODES[0]
    i = EPISODES.index(latest)
    cards = "\n".join(card(x) for x in EPISODES[i:i + 2])
    if out:
        strip = f'<div class="strip">New episode. <a href="{ep_href(latest)}"><b>{e(latest["title"])}</b></a> Watch it now, with its free worksheet.</div>'
    else:
        strip = '<div class="strip">New series. <b>Evidence-Based Entrepreneurship</b>. Episode 1 is coming soon, and its free worksheet is ready now.</div>'
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
  <p style="margin-top:28px"><a class="btn coral" href="/resources/">Get the free worksheets</a><a class="btn ghost" href="/episodes/">Browse the episodes</a></p>
 </section>"""
    urls = [page("privacy.html", "Privacy note | David Park PhD", "What happens to your email address when you sign up for David Park PhD emails.", privacy)]
    page("thanks.html", "Thanks for signing up | David Park PhD", "Check your inbox to confirm your sign-up.", thanks)
    return urls


def main():
    urls = [BASE + "/", BASE + "/about.html", episodes_index(), resources_index()]
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
