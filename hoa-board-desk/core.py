"""HOA Board Desk core: audit stale HOA info, build FAQ, newsletter, and a clean static site.
Offline, no network. Not legal advice; boards should check governing documents."""
import html, re
from datetime import date

YEAR = re.compile(r"\b(20\d{2})\b")
DATE_US = re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b")

def audit(text, today=None):
    """Flag likely out-of-date lines: past years, past dates, 'TBD', 'coming soon', old contact placeholders."""
    today = today or date.today()
    flags = []
    for n, line in enumerate(text.splitlines(), 1):
        why = []
        years = [int(y) for y in YEAR.findall(line)]
        if years and max(years) < today.year:
            why.append(f"mentions {max(years)}, before this year")
        for m in DATE_US.finditer(line):
            try:
                if date(int(m.group(3)), int(m.group(1)), int(m.group(2))) < today:
                    why.append(f"date {m.group(0)} has passed")
            except ValueError:
                pass
        if re.search(r"\b(tbd|coming soon|under construction|xxx-xxxx)\b", line, re.I):
            why.append("placeholder wording")
        if why:
            flags.append({"line": n, "text": line.strip(), "why": why})
    return flags

def build_faq(facts):
    """facts: list of {"q":..., "a":...,"source":...}. Returns markdown; drops entries without answers; keeps source citations."""
    out = ["# Frequently Asked Questions", ""]
    for f in facts:
        if not f.get("q") or not f.get("a"):
            continue
        src = f" _(Source: {f['source']})_" if f.get("source") else ""
        out += [f"### {f['q'].strip()}", f"{f['a'].strip()}{src}", ""]
    return "\n".join(out)

def build_newsletter(name, month, news, dates, reminders=()):
    out = [f"# {name} Newsletter: {month}", "", "## What's new"]
    out += [f"- {n}" for n in news] or ["- No news this month."]
    out += ["", "## Dates to remember"] + [f"- **{d['date']}**: {d['what']}" for d in dates]
    if reminders:
        out += ["", "## Friendly reminders"] + [f"- {r}" for r in reminders]
    out += ["", "_Questions? Contact the board using the details on the community site. Draft for board review before sending._"]
    return "\n".join(out)

def md_to_html(md):
    out, in_ul = [], False
    for line in md.splitlines():
        e = html.escape(line)
        e = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", e)
        e = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<em>\1</em>", e)
        li = e.startswith("- ")
        if in_ul and not li:
            out.append("</ul>"); in_ul = False
        if li:
            if not in_ul: out.append("<ul>"); in_ul = True
            out.append(f"<li>{e[2:]}</li>")
        elif e.startswith("### "): out.append(f"<h3>{e[4:]}</h3>")
        elif e.startswith("## "): out.append(f"<h2>{e[3:]}</h2>")
        elif e.startswith("# "): out.append(f"<h1>{e[2:]}</h1>")
        elif e.strip(): out.append(f"<p>{e}</p>")
    if in_ul: out.append("</ul>")
    return "\n".join(out)

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>body{{font:18px/1.6 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem;color:#1b2430}}
nav a{{margin-right:1rem}}a{{color:#0b5cad}}h1{{color:#0b3d6b}}</style></head><body>
<nav><a href="index.html">Home</a><a href="faq.html">FAQ</a><a href="newsletter.html">Newsletter</a></nav>{body}</body></html>"""

def build_site(name, intro, faq_md, newsletter_md, out_dir):
    import os
    os.makedirs(out_dir, exist_ok=True)
    pages = {"index.html": f"# {name}\n\n{intro}", "faq.html": faq_md, "newsletter.html": newsletter_md}
    for fn, md in pages.items():
        with open(os.path.join(out_dir, fn), "w") as f:
            f.write(PAGE.format(title=html.escape(name), body=md_to_html(md)))
    return sorted(pages)
