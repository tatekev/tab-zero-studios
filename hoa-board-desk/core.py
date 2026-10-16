"""HOA Board Desk core: audit stale HOA info, build FAQ, newsletter, and a clean static site.
Offline, no network. Not legal advice; boards should check governing documents."""
import html, re, unicodedata
from datetime import date

YEAR = re.compile(r"(?<![\d/-])(20\d{2})(?![\d/-])")
MONTHS = {m: i for i, m in enumerate(["january","february","march","april","may","june","july","august","september","october","november","december"], 1)}
for _m, _i in list(MONTHS.items()):
    MONTHS[_m[:3]] = _i
MONTHS["sept"] = 9
MON = "|".join(sorted(MONTHS, key=len, reverse=True))
DATE_PATTERNS = [
    (re.compile(r"(?<![\d/-])(\d{4})-(\d{1,2})-(\d{1,2})(?![\d/-])"), "iso"),
    (re.compile(r"(?<![\d/-])(\d{1,2})/(\d{1,2})/(\d{4}|\d{2})(?![\d/])"), "us"),
    (re.compile(r"\b(" + MON + r")\.?\s+(\d{1,2})(?:st|nd|rd|th)?\s*,?\s+(\d{4})\b", re.I), "mdy"),
    (re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(" + MON + r")\.?,?\s+(\d{4})\b", re.I), "dmy"),
]
PLACEHOLDERS = re.compile(
    r"\b(?:tbd|tba|tbc|coming soon|under construction|to be (?:announced|determined|decided)|check back|stay tuned|lorem ipsum|insert [\w ]{1,20} here|your name here|n/a)\b"
    r"|x{3,}[-\s.]?x{3,}|\(?xxx\)?[-\s.]?xxx[-\s.]?xxxx|xxx-xxxx|\[(?:insert|date|name|phone|email|tbd)[^\]]*\]|\b555-01\d\d\b|\bxx/xx(?:/xx(?:xx)?)?\b|\b(?:mm/dd/yyyy|month dd)\b", re.I)
PLACEHOLDER_EXPLAIN = "placeholder wording (like TBD, coming soon, or a fake phone number)"

def _mk(y, mo, d):
    try:
        return date(y, mo, d)
    except ValueError:
        return None

def _dates_in(line):
    out, taken = [], []
    for p, kind in DATE_PATTERNS:
        for m in p.finditer(line):
            if any(not (m.end() <= x or m.start() >= y) for x, y in taken):
                continue
            g = m.groups()
            if kind == "iso": d = _mk(int(g[0]), int(g[1]), int(g[2]))
            elif kind == "us":
                y = int(g[2]); y += 2000 if y < 100 else 0
                d = _mk(y, int(g[0]), int(g[1])) or (_mk(y, int(g[1]), int(g[0])) if int(g[0]) > 12 else None)
            elif kind == "mdy": d = _mk(int(g[2]), MONTHS[g[0].lower()], int(g[1]))
            else: d = _mk(int(g[2]), MONTHS[g[1].lower()], int(g[0]))
            taken.append((m.start(), m.end()))
            if d: out.append((m.group(0), d, m.start(), m.end()))
    return out

def audit(text, today=None):
    """Flag lines that MAY be out of date: past dates, years before this year, placeholder wording.
    A flag is a prompt for the board to check, not a verdict (a past date can be correct history)."""
    today = today or date.today()
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    text = unicodedata.normalize("NFKC", text)
    flags = []
    for n, line in enumerate(text.splitlines(), 1):
        why = []
        dates = _dates_in(line)
        spans = [(a, b) for _, _, a, b in dates]
        for raw, d, _, _ in dates:
            if d < today:
                why.append(f"date {raw} has passed")
        years = [int(m.group(1)) for m in YEAR.finditer(line) if not any(a <= m.start() < b for a, b in spans)]
        if years and max(years) < today.year:
            why.append(f"mentions {max(years)}, before this year")
        if PLACEHOLDERS.search(line):
            why.append(PLACEHOLDER_EXPLAIN)
        if why:
            flags.append({"line": n, "text": line.strip(), "why": why})
    return flags

NO_SOURCE = " _(Source: not provided. Board to confirm before publishing.)_"

def build_faq(facts):
    """facts: list of {"q":..., "a":...,"source":...}. Every answer shows its source if you gave one;
    answers without a source are labeled so the board checks them. Entries missing a question or answer are skipped and counted."""
    out = ["# Frequently Asked Questions", ""]
    skipped = 0
    for f in facts or []:
        if not isinstance(f, dict) or not str(f.get("q", "")).strip() or not str(f.get("a", "")).strip():
            skipped += 1; continue
        src = f" _(Source: {str(f['source']).strip()})_" if str(f.get("source", "")).strip() else NO_SOURCE
        out += [f"## {str(f['q']).strip()}", f"{str(f['a']).strip()}{src}", ""]
    if skipped:
        out += [f"_Board note: {skipped} entr{'y was' if skipped == 1 else 'ies were'} skipped because the question or answer was blank._", ""]
    return "\n".join(out)

def build_newsletter(name, month, news, dates, reminders=()):
    out = [f"# {name} Newsletter: {month}", "", "## What's new"]
    out += [f"- {n}" for n in (news or [])] or ["- No news this month."]
    out += ["", "## Dates to remember"]
    good = [d for d in (dates or []) if isinstance(d, dict) and str(d.get("date", "")).strip() and str(d.get("what", "")).strip()]
    out += [f"- **{d['date']}**: {d['what']}" for d in good] or ["- No dates to remember this month."]
    if reminders:
        out += ["", "## Friendly reminders"] + [f"- {r}" for r in reminders]
    out += ["", "_Questions? Contact the board using the details on the community site. Draft for board review before sending._"]
    return "\n".join(out)

def _inline(e):
    def img(m):
        alt, src = m.group(1).strip(), m.group(2).strip()
        if not alt:
            raise ValueError("Every image needs alt text, like ![Pool in summer](pool.jpg).")
        if not re.match(r"^(https?://|[\w./-]+$)", src) or src.lower().startswith("javascript"):
            return html.escape(alt)
        return f'<img src="{src}" alt="{alt}">'
    def link(m):
        txt, url = m.group(1), m.group(2).strip()
        if not re.match(r"^(https?://|mailto:|[\w./#-]+$)", url):
            return txt
        return f'<a href="{url}">{txt}</a>'
    e = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", img, e)
    e = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)", link, e)
    e = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", e)
    e = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<em>\1</em>", e)
    return e

def md_to_html(md):
    out, lst = [], None
    for line in (md or "").splitlines():
        e = _inline(html.escape(line))
        li = e.startswith("- "); ol = re.match(r"^\d+\. ", e)
        want = "ul" if li else ("ol" if ol else None)
        if lst and lst != want:
            out.append(f"</{lst}>"); lst = None
        if want:
            if not lst: out.append(f"<{want}>"); lst = want
            out.append(f"<li>{e[2:] if li else e[ol.end():]}</li>")
        elif e.startswith("### "): out.append(f"<h3>{e[4:]}</h3>")
        elif e.startswith("## "): out.append(f"<h2>{e[3:]}</h2>")
        elif e.startswith("# "): out.append(f"<h1>{e[2:]}</h1>")
        elif e.strip(): out.append(f"<p>{e}</p>")
    if lst: out.append(f"</{lst}>")
    return "\n".join(out)

PAGE = """<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>body{{font:18px/1.6 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem;color:#1b2430;background:#fff}}
nav a{{margin-right:1rem;padding:.25rem}}a{{color:#0b5cad}}a:focus,a:hover{{outline:3px solid #0b5cad;outline-offset:2px}}h1{{color:#0b3d6b}}img{{max-width:100%;height:auto}}
.skip{{position:absolute;left:-999px}}.skip:focus{{position:static}}[aria-current=page]{{font-weight:700}}</style></head><body>
<a class="skip" href="#main">Skip to main content</a>
<nav aria-label="Main">{nav}</nav><main id="main">{body}</main></body></html>"""

def build_site(name, intro, faq_md, newsletter_md, out_dir, lang="en"):
    """Write exactly 3 files (index.html, faq.html, newsletter.html) into out_dir. Accessible: lang, one h1 per page,
    skip link, labeled nav, main landmark, alt text required for images."""
    import os
    if not str(name).strip():
        raise ValueError("Give the community a name.")
    if not re.match(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*$", str(lang)):
        raise ValueError("lang must look like 'en' or 'es'.")
    pages = {"index.html": ("Home", f"# {name}\n\n{intro}"), "faq.html": ("FAQ", faq_md), "newsletter.html": ("Newsletter", newsletter_md)}
    rendered = {}
    for fn, (label, md) in pages.items():
        body = md_to_html(md)
        if "<h1>" not in body:
            body = f"<h1>{html.escape(label)}</h1>\n" + body
        nav = "".join(f'<a href="{f}"' + (' aria-current="page"' if f == fn else "") + f">{l}</a>" for f, (l, _) in pages.items())
        rendered[fn] = PAGE.format(lang=html.escape(str(lang)), title=html.escape(f"{label} - {name}"), nav=nav, body=body)
    os.makedirs(out_dir, exist_ok=True)
    for fn, doc in rendered.items():
        with open(os.path.join(out_dir, fn), "w", encoding="utf-8") as f:
            f.write(doc)
    return sorted(pages)
