# Unpack

Turns a confusing letter or bill into: what it is, what to do, and by when.

Part of **Tab Zero Studios** — *Tools for Atypical Thinkers, Everywhere.*

## Install (no accounts, no keys, no credentials)
Needs Python 3.10 or newer. From the repo's top folder:
```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```
(Windows: `.venv\Scripts\pip` and `.venv\Scripts\python`.)

## Run
```
cd unpack
../.venv/bin/python server.py     # starts the MCP server over stdio; your MCP client launches this for you
../.venv/bin/python -m pytest -q  # optional: automatic tests
```
MCP client config: `{"command":"<repo>/.venv/bin/python","args":["server.py"],"cwd":"<repo>/unpack"}`

Quick check that everything works: `./run_all_checks.sh` from the top folder (sets itself up on first run; the last line should say `ALL GOOD`).

## Tools
- `unpack_letter(text)`: structured result (what, actions, deadline, urgency, first tiny step)
- `unpack_letter_markdown(text)`: short brain-friendly card

## Privacy and limits
Runs fully offline. Stores nothing and sends nothing. English only. Never invents a deadline: if none is found it says so, and "within N days" is quoted, not calculated. Hides SSN-like and card-like numbers (including ones typed with odd spacing), replacing them with `[hidden number]`. If a date is misspelled or impossible it says so instead of guessing. Text that looks like instructions to an AI is ignored and flagged. Paste only the letter text. Not guaranteed to catch every date format. Not legal, tax, or financial advice.
