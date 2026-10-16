# CPA Doc Prep

Tax-document checklist and tracker, plus a draft email or text to your preparer. Organizes paperwork only; never gives tax advice.

Part of **Tab Zero Studio** — *Tools for Atypical Thinkers, Everywhere.*

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
- `draft_preparer_message(...)`: draft only; you press send

## Privacy and limits
Runs fully offline. Stores nothing and sends nothing. Use sample or pasted text only; never full SSNs or card numbers. Not legal, tax, or financial advice.
