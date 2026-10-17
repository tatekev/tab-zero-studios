# Lease-End Deposit Packet

A move-in/move-out photo log, a deposit demand-letter template, and a deadline tracker that uses the rules you type in.

Part of **Tab Zero Studios**: *Tools for Atypical Thinkers, Everywhere.*

## What it does
Logs photos by room and item with a condition for move-in and move-out, then compares them and lists what looks worse. You type in a deadline rule (like "deposit returned within N days after move-out") along with where you found it, and it counts the date. It drafts a demand letter from your reasons; it cites a rule only if you typed one, and it quotes it back marked for you to check.

## What it does not do
It does not know any state's or city's law and will not say what it is. No rule saved means no deadline. It logs photo file names, not the photos. 'Looks worse' only compares conditions you picked; it does not decide who is responsible or what is normal wear. Draft only; nothing is sent.

## Run
```
pip install -r ../requirements.txt
python server.py        # MCP server over stdio
python -m pytest -q     # 23 tests
python try_it.py        # runs the 5 samples in TESTING.md
```
MCP client config: `{"command":"python","args":["server.py"],"cwd":"lease-end-deposit-packet"}`

## Tools
- `start_packet`, `set_move_out`
- `log_photo`: move-in/move-out photo log (file NAME only)
- `compare_photos`: what looks worse at move-out
- `add_deadline_rule`, `set_event_date`, `deadline_tracker`: rules YOU type, with a source
- `log_charge`
- `draft_demand_letter`: draft only
- `photo_log`: Markdown table
- `scope_check(text)`

## Privacy and limits
Runs fully offline. Stores nothing and sends nothing; your client app keeps the record between calls. It refuses SSN and card numbers in every field (and, where it matters, passwords and long account numbers). Dates must be typed as year-month-day (2026-11-05); it never guesses a date. Not legal, tax, medical, or financial advice.
