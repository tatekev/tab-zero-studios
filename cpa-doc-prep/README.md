# CPA Doc Prep

Tax-document checklist and tracker, plus a draft email or text to your preparer. Organizes paperwork only; never gives tax advice.

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
cd cpa-doc-prep
../.venv/bin/python server.py     # starts the MCP server over stdio; your MCP client launches this for you
../.venv/bin/python -m pytest -q  # optional: automatic tests
```
MCP client config: `{"command":"<repo>/.venv/bin/python","args":["server.py"],"cwd":"<repo>/cpa-doc-prep"}`

Quick check that everything works: `./run_all_checks.sh` from the top folder (sets itself up on first run; the last line should say `ALL GOOD`).

## Tools
- `make_checklist(profiles)`: employee, investor, self_employed, parent, homeowner
- `mark_item`, `checklist_summary`
- `check_sensitive(text)`: flags full SSN/card numbers
- `scope_check(text)`: says so when a question asks for tax advice or an amount owed
- `draft_preparer_message(...)`: draft only; you press send

## Privacy and limits
Runs fully offline. Stores nothing and sends nothing; your client app keeps the checklist between calls. It checks only text passed to its tools (it can't stop you typing a number elsewhere). It refuses to put SSN/card-like numbers in a draft (including numbers disguised with odd spacing, dashes or zero-width characters), declines questions that ask what you owe or what to deduct (it recognizes common English phrasings only, so it can miss unusual ones), and never computes tax or gives advice. Not legal, tax, or financial advice.
