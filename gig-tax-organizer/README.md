# Gig Tax Organizer

Quarterly date reminders, a mileage log, a receipt log, and a year-end packet for your tax preparer. Organizes only.

Part of **Tab Zero Studios**: *Tools for Atypical Thinkers, Everywhere.*

## What it does
Keeps a year's records for gig or side-hustle work: mileage trips, receipts by category, income received, and estimated payments you made. Shows days left to the due dates you confirm (it also lists the usual calendar dates as suggestions, flagged to confirm). Finds gaps (no trip purpose, no receipt photo, same receipt twice, date outside the year). Exports and imports CSV, and builds a one-page packet to hand a preparer.

## What it does not do
It adds up what you typed and nothing more. It never computes tax, deductions, mileage-rate values, or what you owe, and refuses to. Usual dates are federal and may move for weekends and holidays; state dates differ. The 'book' lives in your app; the tool stores nothing.

## Run
```
pip install -r ../requirements.txt
python server.py        # MCP server over stdio
python -m pytest -q     # 45 tests
python try_it.py        # runs the 5 samples in TESTING.md
```
MCP client config: `{"command":"python","args":["server.py"],"cwd":"gig-tax-organizer"}`

## Tools
- `start_book(tax_year)`
- `usual_payment_dates(tax_year)`: the usual 4 dates, marked as suggestions to confirm
- `save_due_dates`, `upcoming_reminders`: days left to dates YOU confirmed
- `log_trip`, `log_receipt`, `log_income`, `log_estimated_payment`
- `entry_totals`: adds up what you typed (not deductions)
- `find_gaps`: missing purposes, photos, odd dates, double entries
- `export_csv`, `import_csv`: fillable spreadsheet files
- `preparer_packet`: one-page Markdown for your preparer
- `scope_check(text)`

## Privacy and limits
Runs fully offline. Stores nothing and sends nothing; your client app keeps the record between calls. It refuses SSN and card numbers in every field (and, where it matters, passwords and long account numbers). Dates must be typed as year-month-day (2026-11-05); it never guesses a date. Not legal, tax, medical, or financial advice.
