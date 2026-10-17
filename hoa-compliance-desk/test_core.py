import pytest
from datetime import date
from core import *
from safety import SensitiveDataError
T = date(2026, 10, 17)

def test_demo_is_marked_demo():
    h = demo_hoa(); assert h["demo"] and "DEMO" in h["name"] and "DEMO ONLY" in h["rules"][0]["source"]
    s = board_summary(h, T); assert "DEMO CONTENT" in s and "Not legal advice" in s

def test_notice_send_by_from_user_rule():
    h = new_hoa("Sample HOA"); add_notice_rule(h, "Annual", 21, "Bylaws Art. 3 Sec. 2")
    r = plan_meeting_notice(h, "2026-12-10", "7 PM", "Clubhouse", ["Budget", "Election"], today=T)
    assert r["send_by"] == "2026-11-19" and "Bylaws Art. 3 Sec. 2" in r["send_by_info"] and "33 days left" in r["send_by_info"]
    d = r["draft"]; assert "Thursday, December 10, 2026" in d and "1. Budget" in d and "[DRAFT FOR BOARD REVIEW" in d
    assert "Nothing was sent" in r["note"] and r["warnings"] == []
def test_no_rule_no_send_by():
    r = plan_meeting_notice(new_hoa("S"), "2026-12-10", "7", "Hall", ["x"], today=T)
    assert r["send_by"] is None and "won't guess" in r["send_by_info"]
def test_send_by_passed_warns():
    h = new_hoa("S"); add_notice_rule(h, "A", 30, "bylaws")
    r = plan_meeting_notice(h, "2026-11-01", "7", "Hall", ["x"], today=T); assert any("already passed" in w for w in r["warnings"])
def test_two_rules_need_label():
    h = new_hoa("S"); add_notice_rule(h, "A", 10, "s"); add_notice_rule(h, "B", 20, "s")
    assert plan_meeting_notice(h, "2026-12-10", "7", "H", ["x"], today=T)["send_by"] is None
    assert plan_meeting_notice(h, "2026-12-10", "7", "H", ["x"], "B", today=T)["send_by"] == "2026-11-20"
    with pytest.raises(ValueError, match="No notice rule"): plan_meeting_notice(h, "2026-12-10", "7", "H", ["x"], "Z", today=T)
def test_rule_requires_source():
    with pytest.raises(ValueError, match="source"): add_notice_rule(new_hoa("S"), "A", 10, "")
    with pytest.raises(ValueError): add_notice_rule(new_hoa("S"), "A", 0, "s")
def test_weekend_and_past_warnings():
    r = plan_meeting_notice(new_hoa("S"), "2026-12-12", "7", "H", ["x"], today=T); assert any("weekend" in w for w in r["warnings"])
    r = plan_meeting_notice(new_hoa("S"), "2026-10-01", "7", "H", ["x"], today=T); assert any("in the past" in w for w in r["warnings"])

def test_upcoming_quarterly_and_clamp():
    h = new_hoa("S"); add_schedule(h, "Dues", "dues", "quarterly", "2026-11-30", 7, 100)
    u = upcoming(h, T, 250); assert [x["due"] for x in u] == ["2026-11-30", "2027-02-28", "2027-05-30"]
    assert u[0]["remind_on"] == "2026-11-23" and u[0]["amount"] == 100
def test_upcoming_monthly_leap_clamp():
    h = new_hoa("S"); add_schedule(h, "M", "dues", "monthly", "2027-01-31", 1)
    assert [x["due"] for x in upcoming(h, date(2027, 1, 1), 100)] == ["2027-01-31", "2027-02-28", "2027-03-31"]
def test_upcoming_empty_and_past_first_date():
    assert upcoming(new_hoa("S"), T)[0]["due"] is None
    h = new_hoa("S"); add_schedule(h, "A", "other", "annual", "2020-03-01", 5)
    assert [x["due"] for x in upcoming(h, T, 365)] == ["2027-03-01"]
def test_schedule_validation():
    h = new_hoa("S")
    with pytest.raises(ValueError, match="kind"): add_schedule(h, "A", "pizza", "monthly", "2026-01-01", 1)
    with pytest.raises(ValueError, match="frequency"): add_schedule(h, "A", "dues", "weekly", "2026-01-01", 1)
    with pytest.raises(ValueError, match="date"): add_schedule(h, "A", "dues", "monthly", "Jan 1", 1)

def test_reminder_draft():
    h = new_hoa("Sample HOA", "board@example.com"); r = reminder_draft(h, "Q4 dues", "2026-12-01", 150, "Pay at the portal")
    assert "Q4 dues is due December 1, 2026: $150.00." in r["draft"] and "board@example.com" in r["draft"] and "Nothing was sent" in r["note"]
    assert "[HOW TO PAY" in reminder_draft(h, "x", "2026-12-01")["draft"]
    for bad in ("foreclos", "lien", "penalt", "fine of"): assert bad not in r["draft"].lower()

def test_records():
    c = records_checklist(); assert len(c) == 14 and all(x["status"] == "missing" for x in c)
    mark_record(c, "minutes", "have"); assert c[1]["status"] == "have"
    with pytest.raises(ValueError): mark_record(c, "minutes", "done")
    with pytest.raises(KeyError): mark_record(c, "zzz", "have")
    assert "doesn't know retention" in [x for x in c if x["id"] == "retention"][0]["hint"]

@pytest.mark.parametrize("bad", ["123-45-6789", "123456789", "4111 1111 1111 1111", "password: abc", "1 2 3 4 5 6 7 8 9"])
def test_refuses_sensitive(bad):
    with pytest.raises(SensitiveDataError): new_hoa(bad)
    with pytest.raises(SensitiveDataError): new_hoa("S", bad)
    h = new_hoa("S"); add_notice_rule(h, "A", 5, "s")
    with pytest.raises(SensitiveDataError): plan_meeting_notice(h, "2026-12-10", "7", "H", [bad], today=T)
    with pytest.raises(SensitiveDataError): reminder_draft(h, "x", "2026-12-01", pay_instructions=bad)
    with pytest.raises(SensitiveDataError): add_schedule(h, bad, "dues", "monthly", "2026-01-01", 1)

@pytest.mark.parametrize("q", ["is it legal to skip the annual meeting?", "what is the quorum", "can the board foreclose", "do we have to send notice", "how many days notice do we need"])
def test_legal_refused(q): assert scope_check(q)["is_advice_request"]
def test_paperwork_ok(): assert not scope_check("where do I store the minutes")["is_advice_request"]

def test_bad_inputs():
    with pytest.raises(ValueError): upcoming({})
    with pytest.raises(ValueError): plan_meeting_notice(new_hoa("S"), "2026-12-10", "7", "H", [], today=T)
    with pytest.raises(ValueError): plan_meeting_notice(new_hoa("S"), "12/10/2026", "7", "H", ["x"], today=T)
    with pytest.raises(ValueError): new_hoa("  ")
