# CPA Doc Prep

Tax-document checklist and tracker, plus a draft email or text to your preparer. Organizes paperwork only; never gives tax advice.

Part of **Tab Zero Studios** — *Tools for Atypical Thinkers, Everywhere.*

## Run
```
pip install -r ../requirements.txt
python server.py        # MCP server over stdio
python -m pytest -q     # tests
```
MCP client config: `{"command":"python","args":["server.py"],"cwd":"cpa-doc-prep"}`

## Tools
- `make_checklist(profiles)`: employee, investor, self_employed, parent, homeowner
- `mark_item`, `checklist_summary`
- `check_sensitive(text)`: flags full SSN/card numbers
- `scope_check(text)`: says so when a question asks for tax advice or an amount owed
- `draft_preparer_message(...)`: draft only; you press send

## Privacy and limits
Runs fully offline. Stores nothing and sends nothing; your client app keeps the checklist between calls. It checks only text passed to its tools (it can't stop you typing a number elsewhere). It refuses to put SSN/card-like numbers in a draft, and never computes tax or gives advice. Not legal, tax, or financial advice.
