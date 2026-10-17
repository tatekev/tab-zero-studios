# HOA Compliance Desk

Annual meeting notice planner, dues and reserve reminder schedule, and a records checklist for HOA boards. Lake Crest demo included.

Part of **Tab Zero Studios**: *Tools for Atypical Thinkers, Everywhere.*

## What it does
A board saves its notice rule (days before a meeting, plus which bylaw says so). Give a meeting date, time, place and agenda and it computes the send-by date and drafts the notice for board review. A schedule feature lists upcoming dues, reserve, insurance, and filing dates with a reminder date before each, and drafts friendly payment reminders. A 14-item records checklist helps keep records in order. The Lake Crest demo has made-up numbers and is labeled DEMO everywhere.

## What it does not do
It doesn't know your state's law or your governing documents; no rule saved means no send-by date. The records checklist has no retention periods; it tells you to look them up. Drafts only; nothing is sent. Demo content is not real HOA data.

## Run
```
pip install -r ../requirements.txt
python server.py        # MCP server over stdio
python -m pytest -q     # 25 tests
python try_it.py        # runs the 5 samples in TESTING.md
```
MCP client config: `{"command":"python","args":["server.py"],"cwd":"hoa-compliance-desk"}`

## Tools
- `start_hoa`, `lake_crest_demo`: demo content, clearly marked
- `save_notice_rule`: a notice period your board found in its bylaws (source required)
- `plan_meeting_notice`: send-by date from YOUR rule, plus a draft notice
- `save_schedule`, `upcoming_dates`: dues, reserve, insurance, and filing reminder dates
- `draft_payment_reminder`: friendly reminder (draft only)
- `records_checklist`, `mark_record`: 14 records to keep
- `board_summary`
- `scope_check(text)`

## Privacy and limits
Runs fully offline. Stores nothing and sends nothing; your client app keeps the record between calls. It refuses SSN and card numbers in every field (and, where it matters, passwords and long account numbers). Dates must be typed as year-month-day (2026-11-05); it never guesses a date. Not legal, tax, medical, or financial advice.
