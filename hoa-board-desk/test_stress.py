"""Stress / regression / accessibility tests for HOA Board Desk. Sample data only."""
import builtins, re, time
from datetime import date
from html.parser import HTMLParser
import pytest
import core

T = date(2026, 10, 16)
def lines(text): return [f["line"] for f in core.audit(text, T)]

def test_flags_past_dates_all_formats():
    for t in ("Meeting 3/4/2023", "Meeting 2023-03-04", "Meeting March 4, 2023", "Meeting 4 March 2023", "Meeting Mar. 4 2023", "Meeting 3/4/23", "Dues due 12/01/2025"):
        assert lines(t) == [1], t
def test_future_dates_not_flagged():
    for t in ("Dues due 12/01/2026", "Meeting 2027-01-05", "Meeting January 5, 2027", "Annual meeting 2027", "Today is 10/16/2026 meeting"):
        assert lines(t) == [], t
def test_past_date_next_to_future_date_still_flagged():
    f = core.audit("Dues due 12/01/2026 (old date 3/4/2023)", T); assert f and "3/4/2023" in f[0]["why"][0]
def test_placeholders():
    for t in ("Pool: coming soon", "Clubhouse hours TBD", "Phone: XXX-XXXX", "Call (xxx) xxx-xxxx", "Date to be announced", "Lorem ipsum dolor", "[insert date here]", "COMING SOON!", "Call 205-555-0142 or 555-0123", "Under Construction", "Contact: [phone]", "Meeting TBA"):
        assert lines(t) == [1], t
def test_clean_text_has_no_flags():
    assert core.audit("Gate code is current.\nOffice open Monday to Friday.\nFounded in 1998.", T) == []
def test_empty_none_long_unicode():
    assert core.audit("", T) == [] and core.audit(None, T) == []
    t0 = time.time(); f = core.audit("Annual meeting 3/4/2023\n" * 20000, T); assert len(f) == 20000 and time.time() - t0 < 10
    assert lines("Réunion 🏠 le 3/4/2023 café") == [1]
def test_line_numbers_multi_line():
    assert lines("ok\nPool TBD\nok\nMeeting 1/2/2020\n") == [2, 4]
def test_invalid_dates_do_not_crash():
    assert lines("Date 13/45/2026 and 02/30/2026") == [1]  # impossible dates are flagged as not real, never crash
def test_flag_wording_is_a_prompt_not_verdict():
    assert "may" in core.audit.__doc__.lower()

def test_faq_sources_cited_and_missing_labeled():
    md = core.build_faq([{"q": "When are dues due?", "a": "Quarterly.", "source": "Sample Bylaws Art. 4"}, {"q": "Pets?", "a": "Allowed.", "source": ""}])
    assert "(Source: Sample Bylaws Art. 4)" in md and "Source: not provided" in md
def test_faq_skips_and_counts_blank():
    md = core.build_faq([{"q": "", "a": "x"}, {"q": "q", "a": " "}, "junk", None, {"q": "Real?", "a": "Yes", "source": "S"}])
    assert "3 entries were skipped" not in md and "4 entries were skipped" in md and "Real?" in md
def test_faq_empty():
    assert core.build_faq([]).startswith("# Frequently Asked Questions") and core.build_faq(None)
def test_newsletter_sections_and_review_note():
    nl = core.build_newsletter("Sample Oaks HOA", "November 2026", ["New mailbox"], [{"date": "Nov 5", "what": "Board meeting"}], ["Trim hedges"])
    for h in ("# Sample Oaks HOA Newsletter: November 2026", "## What's new", "## Dates to remember", "## Friendly reminders", "**Nov 5**: Board meeting", "Draft for board review"): assert h in nl
def test_newsletter_bad_or_empty_inputs():
    nl = core.build_newsletter("X HOA", "Nov", [], [{"date": "Nov 5"}, {}, "bad"]); assert "No news this month" in nl and "No dates to remember" in nl
def test_html_escapes_everything():
    h = core.md_to_html("# <script>alert(1)</script>\n- <img src=x onerror=alert(1)>\n[click](javascript:alert(1))\n[ok](https://example.org)")
    assert "<script>" not in h and "<img src=x" not in h and 'href="javascript' not in h and 'href="https://example.org"' in h
def test_image_requires_alt_text():
    with pytest.raises(ValueError): core.md_to_html("![](pool.jpg)")
    assert 'alt="Pool in summer"' in core.md_to_html("![Pool in summer](pool.jpg)")
def test_lists_ordered_and_bold():
    h = core.md_to_html("1. one\n2. two\n\n- **bold**"); assert "<ol>" in h and "</ol>" in h and "<strong>bold</strong>" in h

class P(HTMLParser):
    def __init__(s): super().__init__(); s.tags = []; s.h = []; s.imgs = []; s.attrs = {}
    def handle_starttag(s, t, a):
        a = dict(a); s.tags.append(t)
        if t[0] == "h" and t[1:].isdigit(): s.h.append(int(t[1:]))
        if t == "img": s.imgs.append(a)
        if t == "html": s.attrs["lang"] = a.get("lang")
        if t == "nav": s.attrs["navlabel"] = a.get("aria-label")
def lum(hexc):
    r, g, b = [int(hexc[i:i+2], 16) / 255 for i in (1, 3, 5)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
def ratio(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True); return (x + 0.05) / (y + 0.05)

def test_site_three_pages_accessible(tmp_path):
    faq = core.build_faq([{"q": "Dues?", "a": "Quarterly.", "source": "Sample Bylaws"}])
    nl = core.build_newsletter("Sample Oaks HOA", "November 2026", ["New mailbox"], [{"date": "Nov 5", "what": "Meeting"}])
    files = core.build_site("Sample Oaks HOA", "Welcome ![Entrance sign](sign.jpg)", faq, nl, str(tmp_path))
    assert files == ["faq.html", "index.html", "newsletter.html"] and sorted(p.name for p in tmp_path.iterdir()) == files
    for fn in files:
        src = (tmp_path / fn).read_text(encoding="utf-8"); p = P(); p.feed(src)
        assert p.attrs["lang"] == "en" and p.attrs["navlabel"] and "main" in p.tags and "<title>" in src
        assert p.h.count(1) == 1, fn
        assert all(b - a <= 1 for a, b in zip(p.h, p.h[1:])) and p.h[0] == 1, (fn, p.h)   # no skipped heading levels
        assert all(i.get("alt") for i in p.imgs)
        assert 'class="skip"' in src and "<script" not in src
def test_site_missing_h1_gets_one(tmp_path):
    core.build_site("X HOA", "Hi", "No heading faq", "No heading news", str(tmp_path))
    assert "<h1>FAQ</h1>" in (tmp_path / "faq.html").read_text(encoding="utf-8")
def test_site_unicode_and_lang(tmp_path):
    core.build_site("Comunidad Ñandú 🏠", "Bienvenidos, café", "# Preguntas", "# Boletín", str(tmp_path), lang="es")
    s = (tmp_path / "index.html").read_text(encoding="utf-8"); assert 'lang="es"' in s and "Ñandú" in s
def test_site_rejects_bad_input(tmp_path):
    with pytest.raises(ValueError): core.build_site("  ", "x", "", "", str(tmp_path))
    with pytest.raises(ValueError): core.build_site("X", "x", "", "", str(tmp_path), lang='"><script>')
def test_site_title_escaped(tmp_path):
    core.build_site('A <b>HOA</b>', "x", "# F", "# N", str(tmp_path)); assert "<b>HOA" not in (tmp_path / "index.html").read_text(encoding="utf-8")
def test_contrast_meets_wcag_aa():
    css = core.PAGE
    for fg, bg in (("#1b2430", "#ffffff"), ("#0b5cad", "#ffffff"), ("#0b3d6b", "#ffffff")):
        assert fg in css and ratio(fg, bg) >= 4.5, (fg, ratio(fg, bg))
def test_site_only_writes_where_asked(tmp_path, monkeypatch):
    seen = []; real = builtins.open
    monkeypatch.setattr(builtins, "open", lambda p, *a, **k: (seen.append(str(p)), real(p, *a, **k))[1])
    core.build_site("X", "x", "# F", "# N", str(tmp_path)); assert seen and all(s.startswith(str(tmp_path)) for s in seen)


# --- added in 2026-10-17 end-user test pass ---
T0 = date(2026, 10, 17)
def test_yearless_past_date_flagged():
    assert core.audit("Next meeting: Oct 1", T0) and not core.audit("See you Dec 1", T0)
def test_may_the_word_is_not_a_date():
    assert core.audit("May is nice", T0) == []
def test_newsletter_flags_past_and_placeholder_dates():
    nl = core.build_newsletter("H", "Nov", [], [{"date": "3/4/2023", "what": "Meeting TBD"}])
    assert "Board check" in nl and nl.splitlines()[-1].endswith("Draft for board review before sending._")
def test_faq_placeholder_answer_gets_board_check():
    assert "Board check" in core.build_faq([{"q": "Pool hours?", "a": "TBD"}])
def test_newsletter_blank_name_refused():
    import pytest
    with pytest.raises(ValueError): core.build_newsletter("", "", [], [])
def test_markup_in_text_is_escaped(tmp_path):
    core.build_site("H", "<img src=x onerror=alert(1)>", "", "", str(tmp_path))
    h = (tmp_path / "index.html").read_text()
    assert "<img src=x" not in h and "&lt;img" in h
