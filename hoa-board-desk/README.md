# HOA Board Desk

Turns outdated HOA info into a clean site, FAQ, and newsletter for board review.

Part of **Tab Zero Studios** — *Tools for Atypical Thinkers, Everywhere.*

## Run
```
pip install -r ../requirements.txt
python server.py        # MCP server over stdio
python -m pytest -q     # tests
```
MCP client config: `{"command":"python","args":["server.py"],"cwd":"hoa-board-desk"}`

## Tools
- `audit_outdated(text)`: flags stale dates/placeholders
- `make_faq(facts)`, `make_newsletter(...)`
- `make_site(...)`: writes a 3-page accessible static site

## Privacy and limits
Runs fully offline. Stores nothing and sends nothing. Use sample or pasted text only; never full SSNs or card numbers. Not legal, tax, or financial advice.
