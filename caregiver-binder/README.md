# Caregiver Binder

A fill-in binder of accounts, documents, contacts, and a first-72-hours checklist. It never stores passwords or secrets.

Part of **Tab Zero Studios**: *Tools for Atypical Thinkers, Everywhere.*

## What it does
You record WHERE things are: which accounts exist and where the login is kept (like "password manager"), which documents exist and where, who to call, and who to call first. A built-in 14-step first-72-hours checklist walks a helper through the first hour, day, and three days. It finds gaps (no backup contact, no power-of-attorney entry, no email account listed) and prints the whole binder.

## What it does not do
It refuses passwords, PINs, codes, recovery phrases, SSNs, card numbers, and any 9+ digit run (account numbers); only the last 4 digits are kept. It doesn't give legal, medical, or financial advice, and the checklist deliberately says not to pay or cancel anything until the lawyer or advisor is asked. Print the binder and keep it somewhere safe; it stores nothing.

## Run
```
pip install -r ../requirements.txt
python server.py        # MCP server over stdio
python -m pytest -q     # 27 tests
python try_it.py        # runs the 5 samples in TESTING.md
```
MCP client config: `{"command":"python","args":["server.py"],"cwd":"caregiver-binder"}`

## Tools
- `start_binder`
- `add_account`: where the login is kept, never the login
- `add_document`: what and where
- `add_contact`: who to call (mark call first)
- `add_checklist_step`, `tick_step`: the first-72-hours checklist (14 steps built in)
- `find_gaps`
- `print_binder`: the whole binder as printable Markdown
- `scope_check(text)`

## Privacy and limits
Runs fully offline. Stores nothing and sends nothing; your client app keeps the record between calls. It refuses SSN and card numbers in every field (and, where it matters, passwords and long account numbers). Dates must be typed as year-month-day (2026-11-05); it never guesses a date. Not legal, tax, medical, or financial advice.
