# Tab Zero Studios (TZS)
*Tools for Atypical Thinkers, Everywhere.* — Systems for Pretty Chaotic You.

Nine small, offline MCP servers. Each folder has its own README and tests. Sample data only. None gives legal, tax or medical advice.

- `unpack/` – turns a confusing letter or message into a plain breakdown
- `cpa-doc-prep/` – organizes documents for a tax preparer (no tax math)
- `hoa-board-desk/` – notices, minutes and FAQs for small HOA boards
- `tax-notice-helper/` – plain-English breakdown of IRS/state notices
- `gig-tax-organizer/` – mileage, receipt and income logs plus a preparer packet
- `medical-bill-appeal-kit/` – bill checklist, itemized-bill request, appeal draft, deadlines
- `lease-end-deposit-packet/` – photo log, demand-letter draft, deadline tracker
- `hoa-compliance-desk/` – notice send-by dates, dues/insurance dates, records checklist
- `caregiver-binder/` – where things are and who to call, 72-hour checklist

Install: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` (Python 3.10+, no accounts or keys). Self-check: `./run_all_checks.sh` (includes `mcp_end_user.py`, which runs every TESTING.md sample plus messy inputs over real MCP). Testing guide: `TESTING.md`. Latest results: `TEST-RESULTS.md`.
