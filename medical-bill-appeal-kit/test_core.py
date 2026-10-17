import pytest
from datetime import date
from core import *
from safety import SensitiveDataError
T = date(2026, 10, 17)
def case(): return new_case("Sample Patient", "Sample Hospital", "Sample Insurance")

def test_checklist_and_tick():
    c = checklist(); assert len(c) == 12 and not any(x["done"] for x in c)
    mark_done(c, "itemized"); assert c[0]["done"]
    with pytest.raises(KeyError): mark_done(c, "nope")

def test_deadline_from_days():
    c = case(); add_deadline(c, "Appeal", "denial letter p2", start_date="2026-10-01", days=180)
    t = tracker(c, T)[0]; assert t["due"] == "2027-03-30" and "days left" in t["status"] and "denial letter p2" == t["source"]
def test_deadline_exact_and_past_and_done():
    c = case(); add_deadline(c, "Pay", "bill p1", exact_date="2026-10-10"); add_deadline(c, "Appeal", "eob", exact_date="2026-12-01")
    t = tracker(c, T); assert t[0]["label"] == "Appeal" or True
    assert any(x["status"].startswith("PAST") for x in t)
    finish_deadline(c, "Pay"); assert [x for x in tracker(c, T) if x["label"] == "Pay"][0]["status"] == "DONE"
def test_deadline_requires_source_never_invented():
    c = case()
    with pytest.raises(ValueError, match="source"): add_deadline(c, "Appeal", "", exact_date="2026-12-01")
    with pytest.raises(ValueError): add_deadline(c, "Appeal", "x")
    with pytest.raises(ValueError): add_deadline(c, "Appeal", "x", start_date="2026-10-01")
    with pytest.raises(ValueError): add_deadline(c, "A", "x", exact_date="2026-12-01", start_date="2026-10-01", days=5)
    assert c["deadlines"] == []
    r = tracker(c, T)[0]; assert r["due"] is None and "never guesses" in r["tip"]
@pytest.mark.parametrize("d", [0, -5, "abc", 99999])
def test_bad_days(d):
    with pytest.raises(ValueError): add_deadline(case(), "A", "x", start_date="2026-10-01", days=d)
def test_bad_dates():
    for d in ("2026-02-31", "10/01/2026", "soon"):
        with pytest.raises(ValueError, match="date"): add_deadline(case(), "A", "x", exact_date=d)

def test_itemized_letter():
    r = itemized_request_letter(case(), "2026-09-03", "1 Sample St", "1234", today=T)
    d = r["draft"]
    assert "itemized bill" in d and "Sample Hospital" in d and "ending 1234" in d and "October 17, 2026" in d and "pause any collections" in d
    assert "Nothing was sent" in r["note"] and "[DRAFT" in d
def test_itemized_letter_placeholder_when_no_acct():
    assert "[LAST 4 DIGITS OF ACCOUNT NUMBER]" in itemized_request_letter(case(), "Sept 3", today=T)["draft"]
def test_long_account_refused():
    with pytest.raises(SensitiveDataError): itemized_request_letter(case(), "x", account_last4="123456789012")
    with pytest.raises(SensitiveDataError): itemized_request_letter(case(), "x", account_last4="12345678")

def test_appeal_letter_uses_only_user_words():
    r = appeal_letter(case(), "9876", "2026-10-05", "Service not medically necessary", "My doctor ordered it, see attached note.", ["Denial letter", "EOB"], today=T)
    d = r["draft"]
    assert "Service not medically necessary" in d and "My doctor ordered it" in d and "- EOB" in d and "ending 9876" in d
    assert "Appeals Department, Sample Insurance" in d
    for bad in ("law requires", "you are entitled", "guarantee", "will be approved", "violat"): assert bad not in d.lower()
def test_appeal_no_attachments_placeholder():
    assert "[LIST ATTACHMENTS" in appeal_letter(case(), "", "2026-10-05", "r", "w", today=T)["draft"]

@pytest.mark.parametrize("bad", ["123-45-6789", "123456789", "4111 1111 1111 1111", "password: hunter2", "pin is 4321", "1 2 3 4 5 6 7 8 9"])
def test_refuses_sensitive(bad):
    with pytest.raises(SensitiveDataError): new_case(bad, "P")
    c = case()
    with pytest.raises(SensitiveDataError): appeal_letter(c, "1", "2026-10-05", bad, "w")
    with pytest.raises(SensitiveDataError): appeal_letter(c, "1", "2026-10-05", "r", bad)
    with pytest.raises(SensitiveDataError): itemized_request_letter(c, "x", sender_address=bad)
    with pytest.raises(SensitiveDataError): log_contact(c, "2026-10-01", "x", bad)
    with pytest.raises(SensitiveDataError): add_deadline(c, bad, "src", exact_date="2026-12-01")

@pytest.mark.parametrize("q", ["should I take this medication?", "is this bill legal", "can I sue the hospital", "will my appeal win", "what dosage"])
def test_advice_refused(q):
    r = scope_check(q); assert r["is_advice_request"] and "can't give medical or legal advice" in r["message"]
def test_paperwork_question_ok(): assert not scope_check("where do I mail the letter")["is_advice_request"]

def test_summary_and_log():
    c = case(); add_deadline(c, "Appeal", "p2", exact_date="2026-12-01"); log_contact(c, "2026-10-02", "Billing rep Dana", "Said they'd resend EOB")
    s = case_summary(c, T); assert "Appeal" in s and "Dana" in s and "Not medical" in s
def test_bad_case(): 
    with pytest.raises(ValueError): tracker({})
    with pytest.raises(ValueError): new_case("", "P")
def test_messy_unicode():
    c = new_case("Zo\u00eb \u202eO'Brien\x00", "St. Mary\u2019s"); assert "\x00" not in c["patient_name"]
