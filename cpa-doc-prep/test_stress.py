"""Stress / regression tests for CPA Doc Prep. Sample data only."""
import pytest, builtins, re
import core
from core import *

SSN_FORMS = ["123-45-6789", "123 45 6789", "123456789", "123.45.6789", "123 - 45 - 6789", "ssn: 123456789.", "１２３-４５-６７８９"]
CARD_FORMS = ["4111111111111111", "4111 1111 1111 1111", "4111-1111-1111-1111", "3782 822463 10005", "378282246310005", "4111.1111.1111.1111"]

@pytest.mark.parametrize("t", SSN_FORMS)
def test_ssn_detected_all_formats(t):
    r = sensitive_check("my number is " + t); assert r["has_ssn"] and not r["safe"]
    assert not re.search(r"\d{4}", r["redacted_text"].replace("my number is", "")) or "removed" in r["redacted_text"]
@pytest.mark.parametrize("t", CARD_FORMS)
def test_card_detected_all_formats(t):
    assert sensitive_check("card " + t)["has_card"]
@pytest.mark.parametrize("t", ["last 4 is 6789", "Tax year 2025, filed 10/15/2026", "dates 2026-10-25 2026-11-05 2026-12-01", "call 205-555-0142", "$1,234,567.89 of income", "ZIP 35004"])
def test_no_false_alarms(t):
    r = sensitive_check(t); assert r["safe"], t
@pytest.mark.parametrize("t", SSN_FORMS + CARD_FORMS)
def test_draft_refuses_in_every_field(t):
    for kw in ({"note": "see " + t}, {"preparer": t}, {"sender": t}):
        with pytest.raises(ValueError) as e: draft_message([], **kw)
        assert t not in str(e.value)
    c = build_checklist(["employee"]); c[0]["item"] = "W-2 " + t
    with pytest.raises(ValueError): draft_message(c)
def test_redacted_output_never_contains_number():
    r = sensitive_check("ssn 123-45-6789 card 4111 1111 1111 1111"); assert "123-45" not in str(r) and "4111" not in str(r)
def test_each_profile_has_checklist_and_expected_items():
    exp = {"employee": "w2", "investor": "1099_b", "self_employed": "1099_nec", "parent": "childcare", "homeowner": "1098"}
    for p, i in exp.items():
        c = build_checklist([p]); assert c and all(x["status"] == "missing" for x in c) and i in [x["id"] for x in c]
def test_profile_name_variants_and_unknown():
    assert build_checklist(["Self-Employed"]) == build_checklist(["self employed"]) == build_checklist("self_employed")
    with pytest.raises(ValueError) as e: build_checklist(["employee", "astronaut"])
    assert "astronaut" in str(e.value) and "homeowner" in str(e.value)
    with pytest.raises(ValueError): build_checklist([])
def test_all_profiles_dedupe():
    ids = [x["id"] for x in build_checklist(list(PROFILES))]; assert len(ids) == len(set(ids))
def test_tracking_all_statuses_and_counts():
    c = build_checklist(["employee"])
    update_status(c, "w2", "received"); update_status(c, "1098", "sent_to_preparer"); update_status(c, "id", "not_applicable")
    s = summary(c); assert s["counts"]["received"] == 1 and s["counts"]["sent_to_preparer"] == 1 and s["counts"]["not_applicable"] == 1
    assert s["counts"]["missing"] == len(c) - 3
    update_status(c, "w2", "RECEIVED"); update_status(c, "w2", "missing"); assert summary(c)["counts"]["received"] == 0
def test_bad_status_and_id_errors_are_helpful():
    c = build_checklist(["employee"])
    with pytest.raises(ValueError) as e: update_status(c, "w2", "done"); assert "missing" in str(e.value)
    with pytest.raises(KeyError) as e: update_status(c, "zzz", "missing")
    assert "w2" in str(e.value)
def test_draft_email_lists_ready_and_missing_and_hides_not_applicable():
    c = build_checklist(["employee"]); update_status(c, "w2", "received"); update_status(c, "id", "not_applicable")
    d = draft_message(c, "Sample CPA", "Sample Client")["draft"]
    assert d.startswith("Hi Sample CPA,") and "I have these ready" in d and "Still waiting on" in d and "Photo ID" not in d and d.rstrip().endswith("Thanks, Sample Client")
def test_draft_text_is_one_line_and_short_form():
    c = build_checklist(["investor"]); update_status(c, "k1", "received")
    d = draft_message(c, channel="text")
    assert "\n" not in d["draft"] and ":;" not in d["draft"] and "Ready for you:" in d["draft"] and d["channel"] == "text"
def test_draft_bad_channel():
    with pytest.raises(ValueError): draft_message([], channel="fax")
def test_draft_is_draft_only_and_says_so():
    d = draft_message(build_checklist(["parent"])); assert "Nothing was sent" in d["note"] and "not tax advice" in d["note"]
def test_draft_empty_checklist_ok():
    assert "Hi," in draft_message([])["draft"]
def test_never_computes_tax_user_asks():
    for q in ("how much tax will I owe", "How much will I owe this year?", "What is my refund going to be", "Should I itemize or take the standard deduction?", "can I deduct my home office"):
        r = scope_check(q); assert r["is_tax_advice_request"] and "can't" in r["message"] and not re.search(r"\$\s?\d", r["message"]), q
        assert sensitive_check(q)["looks_like_tax_question"]
    assert not scope_check("Where do I find my W-2?")["is_tax_advice_request"]
def test_tax_question_in_note_warns_and_adds_no_numbers():
    d = draft_message(build_checklist(["employee"]), note="How much tax will I owe?")
    assert d["warnings"] and "Ask your tax preparer" in d["warnings"][0]
def test_no_dollar_amounts_or_advice_words_in_any_output():
    c = build_checklist(list(PROFILES)); d = draft_message(c)["draft"] + str(summary(c)) + str(c)
    assert not re.search(r"\$\s?\d", d) and "you should deduct" not in d.lower()
def test_unicode_and_long_note():
    d = draft_message([], note="Résumé 🏠 " + "x" * 5000)["draft"]; assert "🏠" in d and len(d) < 2600
def test_stores_nothing(monkeypatch):
    monkeypatch.setattr(builtins, "open", lambda *a, **k: (_ for _ in ()).throw(AssertionError("open")))
    c = build_checklist(["employee"]); draft_message(c); summary(c); sensitive_check("x")
def test_sample_text_with_ssn_last4_ok_in_draft():
    draft_message([], note="Dependent SSN ends in 6789.")


# --- added in 2026-10-17 end-user test pass ---
import pytest
@pytest.mark.parametrize("n", ["1 2 3 - 4 5 - 6 7 8 9", "123/45/6789", "123_45_6789", "123\u200b-45-6789", "123\u201345\u20136789", "\uff11\uff12\uff13-45-6789", "4 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1"])
def test_disguised_numbers_flagged_and_refused(n):
    assert not sensitive_check("x " + n)["safe"]
    assert "6789" not in sensitive_check("x " + n)["redacted_text"] or "6789" not in n
    with pytest.raises(ValueError):
        draft_message(build_checklist(["employee"]), note=n)

@pytest.mark.parametrize("q", ["do I need to file?", "is my mortgage interest deductible", "calculate my taxes", "Do I qualify for the child tax credit", "what is my tax bracket"])
def test_more_tax_advice_requests_declined(q):
    assert scope_check(q)["is_tax_advice_request"]

def test_long_note_cut_is_disclosed():
    r = draft_message(build_checklist(["employee"]), note="x" * 5000)
    assert any("cut off" in w for w in r["warnings"])
