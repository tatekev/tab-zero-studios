from datetime import date
import core
T = date(2026, 10, 16)
def test_audit():
    f = core.audit("Annual meeting 3/4/2023\nPool opens May 2026 coming soon\nGate code is current\nDues due 12/01/2026", T)
    assert [x["line"] for x in f] == [1, 2]
def test_faq_skips_blank():
    md = core.build_faq([{"q": "When are dues due?", "a": "Quarterly.", "source": "Sample Bylaws"}, {"q": "No answer", "a": ""}])
    assert "When are dues due?" in md and "No answer" not in md and "Sample Bylaws" in md
def test_newsletter_and_html():
    nl = core.build_newsletter("Sample Oaks HOA", "November 2026", ["New mailbox"], [{"date": "Nov 5", "what": "Board meeting"}])
    assert "**Nov 5**" in nl and "<strong>Nov 5</strong>" in core.md_to_html(nl)
def test_html_escapes():
    assert "<script>" not in core.md_to_html("<script>x</script>")
def test_site(tmp_path):
    files = core.build_site("Sample Oaks HOA", "Welcome.", "# FAQ", "# News", str(tmp_path))
    assert files == ["faq.html", "index.html", "newsletter.html"] and (tmp_path / "index.html").exists()
