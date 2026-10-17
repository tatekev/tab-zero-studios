"""Run the 5 samples from TESTING.md. Run: ../.venv/bin/python try_it.py"""
import sys
from datetime import date
from core import *
from safety import SensitiveDataError
T = date(2026, 10, 17); ok = []
def chk(n, c): ok.append(c); print(("PASS " if c else "FAIL ") + n)
u = usual_dates(2026)
chk("Sample 1: usual dates are suggestions, not confirmed", [x["usual_date"] for x in u] == ["2026-04-15", "2026-06-15", "2026-09-15", "2027-01-15"] and not any(x["confirmed"] for x in u))
b = new_book(2026, "Sample Driver"); set_due_dates(b, [{"label": "Q4", "date": "2027-01-15"}])
chk("Sample 2: reminder counts days from YOUR saved date (90)", reminders(b, T)[0]["days"] == 90)
add_trip(b, "2026-03-02", 12.5, "Airport run", "Home", "Airport"); add_trip(b, "2026-03-03", 7, "Client visit", "Home", "Office")
add_receipt(b, "2026-03-04", "Sample Auto Parts", 45.10, "vehicle_costs", has_photo=True); add_receipt(b, "2026-03-05", "Mystery Shop", 10, "other")
add_income(b, "2026-03-01", "Sample Rides", 1200.50)
t = totals(b)
chk("Sample 3: totals add only what you typed (19.5 miles, $55.10, $1200.50)", t["miles_logged"] == 19.5 and t["receipts_total_entered"] == 55.1 and t["income_total_entered"] == 1200.5)
p = handoff_packet(b, "Sample CPA", T)
chk("Sample 4: packet says no tax calculated + flags gaps", "No tax has been calculated" in p and "no photo" in p and "'other'" in p)
try: add_trip(b, "2026-03-06", 5, "ssn 123-45-6789"); refused = False
except SensitiveDataError: refused = True
chk("Sample 5: SSN refused; 'how much tax will I owe' refused", refused and scope_check("how much tax will I owe")["is_tax_advice_request"])
print(f"{sum(ok)}/{len(ok)} samples passed"); sys.exit(0 if all(ok) else 1)
