import pytest
from datetime import date
from core import *
from safety import SensitiveDataError
T = date(2026, 10, 17)

def full_book():
    b = new_book(2026, "Sample Driver")
    add_income(b, "2026-03-01", "Sample Rides", 1200.50)
    add_income(b, "2026-04-01", "Sample Eats", 800)
    add_trip(b, "2026-03-02", 12.5, "Airport run", "Home", "Airport")
    add_trip(b, "2026-03-03", 7, "", "", "")
    add_receipt(b, "2026-03-04", "Sample Auto Parts", 45.10, "vehicle_costs", has_photo=True)
    add_receipt(b, "2026-03-05", "Mystery Shop", 10, "other")
    add_payment(b, "2026-04-14", "Q1 estimated", 300, "A1B2")
    return b

def test_usual_dates_flag_weekend_and_unconfirmed():
    u = usual_dates(2026)
    assert [x["usual_date"] for x in u] == ["2026-04-15", "2026-06-15", "2026-09-15", "2027-01-15"]
    assert all(not x["confirmed"] and "Confirm" in x["note"] for x in u)
    assert any(x["weekend"] for x in usual_dates(2027))  # 2027-06-15 is Tue; Apr 15 2028 is Sat
    assert any(x["weekend"] for x in usual_dates(2028))

def test_reminders_user_dates_only():
    b = new_book(2026)
    assert reminders(b, T)[0]["date"] is None
    set_due_dates(b, [{"label": "Q4", "date": "2027-01-15"}, {"label": "Q3", "date": "2026-09-15"}])
    r = reminders(b, T)
    assert r[0]["label"] == "Q3" and r[0]["status"].startswith("PAST") and r[1]["days"] == 90

def test_totals_only_add_entries():
    t = totals(full_book())
    assert t["miles_logged"] == 19.5 and t["income_total_entered"] == 2000.5 and t["receipts_total_entered"] == 55.1
    assert t["receipts_by_category"]["vehicle_costs"] == 45.1
    assert "deduct" not in " ".join(k for k in t if k != "note")
    assert "Not deductions" in t["note"]

def test_gaps():
    g = " ".join(gaps(full_book()))
    assert "no purpose" in g and "no photo" in g and "'other'" in g

def test_double_entry_and_outside_year():
    b = new_book(2026)
    add_receipt(b, "2026-05-01", "A", 10, "supplies", has_photo=True); add_receipt(b, "2026-05-01", "a", 10, "supplies", has_photo=True)
    add_trip(b, "2024-01-01", 5, "x", "a", "b")
    g = " ".join(gaps(b))
    assert "same as receipt 1" in g and "outside 2026" in g

def test_packet_content_no_tax_math():
    p = handoff_packet(full_book(), "Sample CPA", T)
    assert "Year-end packet for Sample CPA: tax year 2026" in p and "No tax has been calculated" in p
    assert "$2,000.50" in p and "19.5 miles" in p and "A1B2" in p
    low = p.lower().replace(DISCLAIMER.lower(), "")
    for bad in ("you owe", "deduction of", "tax due", "per mile rate", "refund of"):
        assert bad not in low

def test_csv_roundtrip():
    b = full_book(); c = to_csv(b, "receipts")
    b2 = new_book(2026); from_csv(b2, "receipts", c)
    assert totals(b2)["receipts_total_entered"] == 55.1 and b2["receipts"][0]["has_photo"] is True

def test_csv_formula_injection_neutralized():
    b = new_book(2026); add_receipt(b, "2026-01-01", "=HYPERLINK(\"x\")", 5, "supplies")
    assert "'=HYPERLINK" in to_csv(b, "receipts")

def test_csv_bad_row_message():
    b = new_book(2026)
    with pytest.raises(ValueError, match="CSV row 2"): from_csv(b, "trips", "date,miles,purpose\nnot-a-date,5,x\n")

@pytest.mark.parametrize("bad", ["123-45-6789", "123456789", "123 45 6789", "4111 1111 1111 1111", "4111111111111111", "1 2 3 - 4 5 - 6 7 8 9"])
def test_refuses_ssn_and_cards_everywhere(bad):
    b = new_book(2026)
    with pytest.raises(SensitiveDataError): add_trip(b, "2026-01-01", 5, bad)
    with pytest.raises(SensitiveDataError): add_receipt(b, "2026-01-01", bad, 5)
    with pytest.raises(SensitiveDataError): add_income(b, "2026-01-01", "x", 5, bad)
    with pytest.raises(SensitiveDataError): add_payment(b, "2026-01-01", "q", 5, bad)
    with pytest.raises(SensitiveDataError): new_book(2026, bad)
    with pytest.raises(SensitiveDataError): handoff_packet(b, bad)
    with pytest.raises(SensitiveDataError): from_csv(b, "trips", "date,miles,purpose\n2026-01-01,5," + bad)
    assert b["trips"] == [] and b["receipts"] == []

def test_last4_ok():
    add_trip(new_book(2026), "2026-01-01", 5, "client at acct ending 6789")

@pytest.mark.parametrize("q", ["how much tax will I owe", "can I deduct my phone?", "what is my mileage rate", "should I pay quarterly", "is this deductible", "calculate my tax"])
def test_tax_questions_refused(q):
    r = scope_check(q); assert r["is_tax_advice_request"] and "organizes records" in r["message"]
def test_records_question_ok():
    assert not scope_check("where do I put my receipts")["is_tax_advice_request"]

@pytest.mark.parametrize("d", ["2026-02-30", "02/03/2026", "tomorrow", "", None, "2026-13-01", "20260101"])
def test_bad_dates_clear_errors(d):
    with pytest.raises(ValueError, match="date"): add_trip(new_book(2026), d, 5, "x")

@pytest.mark.parametrize("m", [0, -3, "abc", 5000, float("nan"), None, True])
def test_bad_miles(m):
    with pytest.raises(ValueError): add_trip(new_book(2026), "2026-01-01", m, "x")

@pytest.mark.parametrize("a", [-1, "abc", "1e999", "", float("inf")])
def test_bad_amounts(a):
    with pytest.raises(ValueError): add_receipt(new_book(2026), "2026-01-01", "v", a)

def test_messy_amounts_ok():
    b = new_book(2026); add_receipt(b, "2026-01-01", "V", " $1,234.50 ", "Phone-Internet")
    assert b["receipts"][0]["amount"] == 1234.5 and b["receipts"][0]["category"] == "phone_internet"

def test_bad_category_and_book():
    with pytest.raises(ValueError, match="category"): add_receipt(new_book(2026), "2026-01-01", "v", 1, "yachts")
    with pytest.raises(ValueError): add_trip({}, "2026-01-01", 1, "x")
    with pytest.raises(ValueError): new_book("twenty")

def test_unicode_and_control_chars():
    b = new_book(2026); add_trip(b, "2026-01-01", 5, "caf\u00e9 \u202e run\x00", "A", "B")
    assert "\x00" not in b["trips"][0]["purpose"] and "\u202e" not in b["trips"][0]["purpose"]
