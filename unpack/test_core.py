from datetime import date
from core import unpack, classify, to_markdown
T = date(2026, 10, 16)
BILL = "Acme Power. Statement balance $142.50. Amount due $142.50 by 10/25/2026. Please pay online or call us. Late fee applies after that date."
def test_bill():
    r = unpack(BILL, T)
    assert "bill" in r["what_is_this"] and "$142.50" in r["what_is_this"]
    assert r["by_when"].startswith("2026-10-25") and "9 days" in r["by_when"]
    assert r["urgency"] == "medium" or r["urgency"] == "high"
def test_urgent():
    r = unpack("FINAL NOTICE. Your account is past due. Pay immediately. Due October 18, 2026.", T)
    assert r["urgency"] == "high"
def test_no_date():
    r = unpack("Thanks for being a member. Newsletter inside.", T)
    assert "No clear date" in r["by_when"] and r["urgency"] == "low"
def test_hoa_and_markdown():
    assert classify("The Homeowners Association annual assessment is due") == "hoa notice"
    assert "## By when?" in to_markdown(unpack(BILL, T))
def test_past_date_ignored():
    r = unpack("Please respond by 01/05/2026.", T)
    assert r["dates_in_the_past"] == ["2026-01-05"] and "No clear date" in r["by_when"]
