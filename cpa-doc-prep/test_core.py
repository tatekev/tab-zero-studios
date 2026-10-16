import pytest
from core import *
def test_checklist_dedupes():
    c = build_checklist(["employee", "homeowner"])
    ids = [x["id"] for x in c]
    assert ids.count("1098") == 1 and "w2" in ids
def test_status_and_summary():
    c = build_checklist(["investor"])
    update_status(c, "k1", "received")
    assert summary(c)["received"] == ["Schedule K-1 (partnership, S-corp, trust)"]
    with pytest.raises(ValueError): update_status(c, "k1", "bogus")
    with pytest.raises(KeyError): update_status(c, "nope", "missing")
def test_sensitive():
    assert sensitive_check("ssn 123-45-6789")["has_ssn"]
    assert sensitive_check("card 4111 1111 1111 1111")["has_card"]
    assert not sensitive_check("last 4 is 6789")["has_ssn"]
def test_draft_blocks_ssn():
    with pytest.raises(ValueError): draft_message([], note="my ssn 123-45-6789")
def test_draft_content():
    c = build_checklist(["investor"]); update_status(c, "1099_b", "received")
    d = draft_message(c, "Sample CPA", "Sample Client")
    assert "I have these ready" in d["draft"] and "Still waiting on" in d["draft"] and "not tax advice" in d["note"]
    assert "\n- " not in draft_message(c, channel="text")["draft"]
