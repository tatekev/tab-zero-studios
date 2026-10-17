# HOA Board Desk

Turns outdated HOA info into a clean site, FAQ, and newsletter for board review.

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
cd hoa-board-desk
../.venv/bin/python server.py     # starts the MCP server over stdio; your MCP client launches this for you
../.venv/bin/python -m pytest -q  # optional: automatic tests
```
MCP client config: `{"command":"<repo>/.venv/bin/python","args":["server.py"],"cwd":"<repo>/hoa-board-desk"}`

Quick check that everything works: `./run_all_checks.sh` from the top folder (sets itself up on first run; the last line should say `ALL GOOD`).

## Tools
- `audit_outdated(text)`: flags stale dates/placeholders
- `make_faq(facts)`, `make_newsletter(...)`
- `make_site(...)`: writes a 3-page accessible static site

## Privacy and limits
Runs fully offline and sends nothing. The only thing it writes is the 3 site files in the folder you choose with `make_site`. Audit flags past dates, impossible dates, dates with no year that may have passed, and placeholder text (TBD, coming soon, fake phone numbers). `make_faq` and `make_newsletter` add a visible "Board check" line when their own text has such items. Audit flags are prompts to check, not verdicts. FAQ answers show the sources you provide; answers without one are labeled for the board to confirm. Not legal, tax, or financial advice.
