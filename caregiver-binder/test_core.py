import pytest
from datetime import date
from core import *
from safety import SensitiveDataError
T = date(2026, 10, 17)
def full():
    b = new_binder("Sample Person", "Sample Helper")
    add_contact(b, "Pat Sample", "Sister", "555-123-4567", call_first=True)
    add_contact(b, "Lee Sample", "Neighbor", "(555) 987 6543", "lee@example.com", True)
    add_document(b, "Will", "will", "Fire safe in hall closet", "Sample Law Office")
    add_document(b, "Med list", "Medication list", "Fridge door")
    add_account(b, "First Bank checking", "bank", "password manager", "1234", "555-000-1111")
    add_account(b, "Main email", "Email", "paper in safe")
    return b

def test_checklist_default_and_tick():
    b = new_binder("P"); assert len(b["checklist"]) == 14 and {c["when"] for c in b["checklist"]} == {"First hour", "First 24 hours", "First 72 hours"}
    tick(b, "safe"); assert b["checklist"][0]["done"]
    with pytest.raises(KeyError): tick(b, "zzz")
def test_checklist_has_no_advice_on_paying():
    t = " ".join(c["item"] for c in new_binder("P")["checklist"]).lower()
    assert "don't pay or cancel anything yet" in t and "emergency number" in t
def test_markdown_binder():
    m = to_markdown(full(), T)
    assert "# Caregiver binder: Sample Person" in m and "**CALL FIRST** Lee Sample" in m and "Fire safe in hall closet" in m
    assert "| First Bank checking | bank | 1234 | password manager |" in m and "- [ ] Make sure everyone is safe" in m and "Not legal, medical" in m
    assert "No document listed for a power of attorney" in m
def test_gaps():
    g = " ".join(gaps(full())); assert "power of attorney" in g and "health care directive" in g and "phone account" in g
    assert "a will" not in g and "email account listed" not in g
    assert "Mark at least two" in " ".join(gaps(new_binder("P")))
def test_custom_step():
    b = new_binder("P"); add_step(b, "Feed the cat", "First 24 hours"); assert b["checklist"][-1]["item"] == "Feed the cat"
    with pytest.raises(ValueError): add_step(b, "x", "Tomorrow")

SECRETS = ["123-45-6789", "123456789", "4111 1111 1111 1111", "password: hunter2", "my PIN is 4321", "passcode=998877", "recovery code: abcd-efgh", "1 2 3 - 4 5 - 6 7 8 9", "account number 123456789012", "seed phrase is apple"]
@pytest.mark.parametrize("bad", SECRETS)
def test_refuses_secrets_everywhere(bad):
    with pytest.raises(SensitiveDataError): new_binder(bad)
    b = new_binder("P")
    with pytest.raises(SensitiveDataError): add_account(b, "Bank", "bank", bad)
    with pytest.raises(SensitiveDataError): add_account(b, bad, "bank", "safe")
    with pytest.raises(SensitiveDataError): add_account(b, "Bank", "bank", "safe", note=bad)
    with pytest.raises(SensitiveDataError): add_document(b, "Will", "will", bad)
    with pytest.raises(SensitiveDataError): add_contact(b, "A", "B", "555-111-2222", note=bad)
    with pytest.raises(SensitiveDataError): add_step(b, bad)
    assert b["accounts"] == [] and b["documents"] == [] and b["contacts"] == []
def test_last4_only():
    b = new_binder("P")
    with pytest.raises(ValueError): add_account(b, "Bank", "bank", "safe", "12345678")
    with pytest.raises(ValueError): add_account(b, "Bank", "bank", "safe", "12-34")
def test_refusal_message_never_echoes():
    try: add_account(new_binder("P"), "Bank", "bank", "password: hunter2")
    except SensitiveDataError as e: assert "hunter2" not in str(e) and "WHERE" in str(e)
def test_phone_formats_ok_and_bad():
    b = new_binder("P")
    for p in ("5551234567", "555-123-4567", "+1 (555) 123-4567"): add_contact(b, "A", "B", p)
    for p in ("call me maybe", "1234567890123456789"):
        with pytest.raises((ValueError, SensitiveDataError)): add_contact(b, "A", "B", p)
def test_contact_needs_way_to_reach():
    with pytest.raises(ValueError, match="phone number or an email"): add_contact(new_binder("P"), "A", "B")
    with pytest.raises(ValueError, match="email"): add_contact(new_binder("P"), "A", "B", email="nope")
def test_bad_types():
    b = new_binder("P")
    with pytest.raises(ValueError, match="account_type"): add_account(b, "x", "crypto", "safe")
    with pytest.raises(ValueError, match="doc_type"): add_document(b, "x", "diary", "safe")
    with pytest.raises(ValueError): tick({}, "safe")
@pytest.mark.parametrize("q", ["should I sell the house?", "what medication dose", "is the will valid", "will Medicare cover this", "probate steps"])
def test_advice_refused(q): assert scope_check(q)["is_advice_request"]
def test_ok_question(): assert not scope_check("where do I put the spare key info")["is_advice_request"]
def test_markdown_escapes_and_unicode():
    b = new_binder("Zo\u00eb \u202e"); add_contact(b, "A|B", "x\x00", "555-111-2222"); m = to_markdown(b, T)
    assert "A\\|B" in m and "\x00" not in m and "\u202e" not in m
