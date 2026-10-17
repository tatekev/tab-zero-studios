import pytest
from datetime import date
from core import *
from safety import SensitiveDataError
T = date(2026, 10, 17)
def pk():
    p = new_packet("Sample Tenant", "Sample Landlord LLC", "1 Sample Ave, Apt 2", "2024-08-01", "2026-09-30", 1200, "9 New St")
    add_photo(p, "move_in", "Kitchen", "Counter", "good", "C:\\pics\\k1.jpg", "2024-08-01")
    add_photo(p, "move_out", "kitchen", "counter", "damaged", "k2.jpg", "2026-09-30", "chip near sink")
    add_photo(p, "move_in", "Bedroom", "Carpet", "worn", "b1.jpg", "2024-08-01", "stain by window")
    add_photo(p, "move_out", "Bedroom", "Carpet", "worn", "b2.jpg", "2026-09-30")
    add_photo(p, "move_in", "Hall", "Door", "good", "h1.jpg", "2024-08-01")
    add_photo(p, "move_out", "Bath", "Tub", "dirty", "t2.jpg", "2026-09-30")
    return p

def test_compare_buckets():
    c = compare(pk())
    assert [x["item"] for x in c["looks_worse_at_move_out"]] == ["counter"]
    assert c["looks_worse_at_move_out"][0]["move_in_photo"] == "k1.jpg"  # path stripped
    assert [x["item"] for x in c["same_or_better"]] == ["carpet"]
    assert [x["item"] for x in c["only_move_in_photo"]] == ["door"] and [x["item"] for x in c["only_move_out_photo"]] == ["tub"]
    assert "does not say who is responsible" in c["note"]

def test_no_rules_no_deadline_never_state_law():
    t = tracker(pk(), T)[0]
    assert t["due"] is None and "won't guess" in t["tip"]

def test_rule_requires_source():
    p = pk()
    with pytest.raises(ValueError, match="source"): add_rule(p, "Return deposit", 30, "move_out_date", "")
    with pytest.raises(ValueError, match="starts"): add_rule(p, "x", 30, "whenever", "lease s.4")
    with pytest.raises(ValueError): add_rule(p, "x", 0, "move_out_date", "lease")
    assert p["rules"] == []

def test_tracker_with_user_rule():
    p = pk(); add_rule(p, "Landlord returns deposit", 30, "move_out_date", "Lease section 12", "within 30 days")
    t = tracker(p, T)[0]; assert t["due"] == "2026-10-30" and t["status"] == "13 days left" and t["source"] == "Lease section 12"
def test_tracker_missing_start_and_event():
    p = pk(); add_rule(p, "Tenant gives notice", 14, "forwarding_address_date", "state page url")
    assert tracker(p, T)[0]["status"] == "no start date"
    set_event_date(p, "forwarding_address_date", "2026-10-01"); assert tracker(p, T)[0]["due"] == "2026-10-15"
def test_tracker_no_moveout():
    p = new_packet("T", "L", "A", "2024-01-01"); add_rule(p, "r", 10, "move_out_date", "s")
    assert tracker(p, T)[0]["status"] == "no start date"
    set_move_out(p, "2026-10-10"); assert tracker(p, T)[0]["due"] == "2026-10-20"

def test_demand_letter():
    p = pk(); add_deduction(p, "Counter repair", 150, "k2.jpg")
    r = demand_letter(p, 600, ["The counter chip was there at move-in, see k1.jpg."], rule_text_you_found="within 30 days", today=T)
    d = r["draft"]
    assert "$600.00" in d and "$1,200.00" in d and "Counter repair: $150.00" in d and "k1.jpg" in d and "9 New St" in d
    assert "within 30 days\" [CHECK THIS QUOTE" in d and "Nothing was sent" in r["note"] and "[DRAFT" in d
def test_demand_letter_cites_nothing_unless_typed():
    d = demand_letter(pk(), 100, ["reason"], today=T)["draft"].lower()
    for bad in ("statute", "state law", "the law requires", "under section", "double", "penalt", "entitled"): assert bad not in d
def test_demand_needs_reason():
    with pytest.raises(ValueError): demand_letter(pk(), 100, [], today=T)
    with pytest.raises(ValueError): demand_letter(pk(), 100, ["  "], today=T)

@pytest.mark.parametrize("bad", ["123-45-6789", "123456789", "4111 1111 1111 1111", "password: x1", "1 2 3 4 5 6 7 8 9"])
def test_refuses_sensitive(bad):
    with pytest.raises(SensitiveDataError): new_packet(bad, "L", "A", "2024-01-01")
    with pytest.raises(SensitiveDataError): new_packet("T", "L", "A", "2024-01-01", forwarding_address=bad)
    p = pk()
    with pytest.raises(SensitiveDataError): add_photo(p, "move_in", "r", "i", "good", "f.jpg", "2024-01-01", bad)
    with pytest.raises(SensitiveDataError): demand_letter(p, 5, [bad], today=T)
    with pytest.raises(SensitiveDataError): demand_letter(p, 5, ["ok"], rule_text_you_found=bad, today=T)
    with pytest.raises(SensitiveDataError): add_rule(p, "l", 5, "other", bad)
    with pytest.raises(SensitiveDataError): add_deduction(p, bad, 5)

@pytest.mark.parametrize("q", ["can my landlord keep my deposit?", "how many days do they have", "what is the law on deposits", "should I sue", "is this legal", "what counts as normal wear"])
def test_legal_questions_refused(q): assert scope_check(q)["is_advice_request"]
def test_records_question_ok(): assert not scope_check("how do I name my photo files")["is_advice_request"]

def test_bad_inputs():
    with pytest.raises(ValueError): new_packet("T", "L", "A", "2024-13-01")
    with pytest.raises(ValueError, match="before"): new_packet("T", "L", "A", "2024-05-01", "2024-01-01")
    p = pk()
    with pytest.raises(ValueError, match="phase"): add_photo(p, "during", "r", "i", "good", "f", "2024-01-01")
    with pytest.raises(ValueError, match="condition"): add_photo(p, "move_in", "r", "i", "pristine", "f", "2024-01-01")
    with pytest.raises(ValueError, match="date"): add_photo(p, "move_in", "r", "i", "good", "f", "last Tuesday")
    with pytest.raises(ValueError): tracker({})
    with pytest.raises(ValueError): new_packet("", "L", "A", "2024-01-01")
def test_photo_log_md_pipes_escaped():
    p = pk(); add_photo(p, "move_in", "A|B", "x", "good", "f.jpg", "2024-01-01", "a|b")
    assert "A\\|B" in photo_log_markdown(p)
