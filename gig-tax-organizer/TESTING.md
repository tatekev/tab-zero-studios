# Testing Gig Tax Organizer (plain English)

## Fastest check (2 commands)
1. `cd tab-zero-studios/gig-tax-organizer`
2. `../.venv/bin/python try_it.py`  **Pass:** five `PASS` lines and `5/5 samples passed`. **Broken:** any `FAIL`.
3. `../.venv/bin/python -m pytest -q`  **Pass:** `45 passed`. **Broken:** any `FAILED`.
4. Server check from the top folder: `.venv/bin/python mcp_smoke_new.py`. **Pass:** `20/20 checks passed` (covers all six new tools).

## The 5 samples by hand (tool name, what to send, expected)
**Sample 1: usual dates.** `usual_payment_dates` with 2026
Expected: 4 dates: 2026-04-15, 2026-06-15, 2026-09-15, 2027-01-15. Each says to confirm on IRS.gov or with your preparer, and `confirmed` is false.

**Sample 2: reminders.** `start_book` 2026, then `save_due_dates` with `[{"label":"Q4","date":"2027-01-15"}]`, then `upcoming_reminders`
Expected: Q4, 2027-01-15, days = days from today (90 on Oct 17, 2026). With no saved dates it says "No dates saved yet".

**Sample 3: totals.** Log trips 12.5 mi ("Airport run") and 7 mi ("Client visit"); receipts 45.10 (vehicle_costs, photo yes) and 10 (other); income 1200.50. Then `entry_totals`.
Expected: miles_logged 19.5, receipts total 55.1, income total 1200.5. The note says "Not deductions, not tax".

**Sample 4: packet.** `preparer_packet` with preparer `Sample CPA`
Expected: Starts "Year-end packet for Sample CPA: tax year 2026", says "No tax has been calculated", lists tables, and under gaps mentions the receipt with no photo and the 'other' category.

**Sample 5: refusals.** `log_trip` with purpose `ssn 123-45-6789`. Then `scope_check` with `how much tax will I owe`.
Expected: The trip is refused ("Remove the full SSN or card number first...") and not saved. scope_check: is_tax_advice_request true. Dates must look like 2026-03-02; `March 2` gives a clear error.

## Red flags
Any tax amount, deduction, or mileage-rate dollar value; a due date you didn't enter shown as confirmed; an SSN/card saved; a crash instead of a clear message.

## What "pass" means
All 5 samples match, `try_it.py` says 5/5, and the automatic tests pass.
