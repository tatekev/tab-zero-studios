# Medical Bill & Appeal Kit

A checklist for medical bills, an itemized-bill request letter, an appeal letter template, and a deadline tracker.

Part of **Tab Zero Studios**: *Tools for Atypical Thinkers, Everywhere.*

## What it does
Walks you through checking a bill against the EOB, drafts a letter asking the billing office for an itemized bill, drafts an appeal letter using only the reason you copy from the denial letter and your own words, and tracks deadlines. A deadline is saved only if you give an exact date or a start date plus a number of days, **and** say where on your letter you read it.

## What it does not do
Drafts only; nothing is sent. It adds no medical or legal claims and never says whether you will win. It never guesses a deadline. Account and claim numbers: last 4 digits only (longer ones are refused). Type phone numbers with dashes.

## Run
```
pip install -r ../requirements.txt
python server.py        # MCP server over stdio
python -m pytest -q     # 29 tests
python try_it.py        # runs the 5 samples in TESTING.md
```
MCP client config: `{"command":"python","args":["server.py"],"cwd":"medical-bill-appeal-kit"}`

## Tools
- `bill_checklist()`, `tick_checklist_item`: 12 steps for checking a bill and EOB
- `start_case`
- `add_deadline`, `finish_deadline`, `deadline_tracker`: deadlines YOU read on your letters (source required)
- `log_contact`: call and letter log
- `draft_itemized_bill_request`: letter asking for an itemized bill (draft only)
- `draft_appeal_letter`: appeal template from your own words (draft only)
- `case_summary`
- `scope_check(text)`

## Privacy and limits
Runs fully offline. Stores nothing and sends nothing; your client app keeps the record between calls. It refuses SSN and card numbers in every field (and, where it matters, passwords and long account numbers). Dates must be typed as year-month-day (2026-11-05); it never guesses a date. Not legal, tax, medical, or financial advice.
