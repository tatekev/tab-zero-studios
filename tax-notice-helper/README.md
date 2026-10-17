# Tax Notice Helper

Turns an IRS or state tax letter into a plain answer, what to do, a reply-by date, and a reply checklist. Extends Unpack.

Part of **Tab Zero Studios**: *Tools for Atypical Thinkers, Everywhere.*

## What it does
Paste the text of a tax letter. It names the agency and notice number (like CP14 or CP2000), gives a one-line plain meaning for common notices, lists what to do, and gives a tick-box reply checklist. It shows a reply-by date **only if a date is written in the letter**. If the letter says "90 days" it quotes that and does not turn it into a date. It flags scam signs (gift cards, arrest threats, links) and strict-deadline words (levy, tax court, appeal).

## What it does not do
English letters only. Its meanings list covers only 17 common notice codes; for others it says so. It reads text you paste; it cannot read photos or PDFs. It never says whether you should pay, disagree, or ignore.

## Run
```
pip install -r ../requirements.txt
python server.py        # MCP server over stdio
python -m pytest -q     # 19 tests
python try_it.py        # runs the 5 samples in TESTING.md
```
MCP client config: `{"command":"python","args":["server.py"],"cwd":"tax-notice-helper"}`

## Tools
- `explain_tax_notice(text)`: plain answer, what it means, what to do, reply-by date, red flags, reply checklist
- `explain_tax_notice_markdown(text)`: same as a short card with tick boxes
- `reply_checklist()`: the general 11-step reply checklist
- `scope_check(text)`: says so when a question asks whether to pay, dispute, or ignore (never answers)

## Privacy and limits
Runs fully offline. Stores nothing and sends nothing; your client app keeps the record between calls. It refuses SSN and card numbers in every field (and, where it matters, passwords and long account numbers). Dates must be typed as year-month-day (2026-11-05); it never guesses a date. Not legal, tax, medical, or financial advice.
