# Testing Lease-End Deposit Packet (plain English)

## Fastest check (2 commands)
1. `cd tab-zero-studios/lease-end-deposit-packet`
2. `../.venv/bin/python try_it.py`  **Pass:** five `PASS` lines and `5/5 samples passed`. **Broken:** any `FAIL`.
3. `../.venv/bin/python -m pytest -q`  **Pass:** `23 passed`. **Broken:** any `FAILED`.
4. Server check from the top folder: `.venv/bin/python mcp_smoke_new.py`. **Pass:** `20/20 checks passed` (covers all six new tools).

## The 5 samples by hand (tool name, what to send, expected)
**Sample 1: compare photos.** `start_packet` (Sample Tenant, Sample Landlord LLC, 1 Sample Ave, move_in 2024-08-01, move_out 2026-09-30, deposit 1200). `log_photo` move_in Kitchen Counter good k1.jpg 2024-08-01; move_out Kitchen Counter damaged k2.jpg 2026-09-30; move_in Bedroom Carpet worn b1.jpg; move_out Bedroom Carpet worn b2.jpg. `compare_photos`.
Expected: looks_worse_at_move_out: the counter (good to damaged). same_or_better: the carpet. The note says it does not decide who is responsible.

**Sample 2: no rule, no deadline.** `deadline_tracker` right away
Expected: due is empty; tip says it doesn't know your state's rules and won't guess.

**Sample 3: your rule.** `add_deadline_rule` label `Landlord returns deposit`, days `30`, starts `move_out_date`, source `Lease section 12`. `deadline_tracker`.
Expected: Due 2026-10-30, "30 days after the move-out date (2026-09-30), as you typed", source shown. (13 days left on Oct 17, 2026.)

**Sample 4: letter.** `draft_demand_letter` amount 600, reasons [`The counter chip was there at move-in, see k1.jpg.`]
Expected: Letter asks for $600.00 (deposit $1,200.00), numbered reasons, ends "[DRAFT...]". No law or statute is cited. "Nothing was sent".

**Sample 5: refusals.** `add_deadline_rule` with an empty source. `scope_check` with `what is the law on deposits`. `start_packet` with tenant `123-45-6789`.
Expected: Rule refused ("source is required"). scope_check: can't tell you what the law is. SSN refused.

## Red flags
A deadline when no rule was typed; any statement of what the law says; an SSN/card accepted; a letter that threatens or cites law you didn't give.

## What "pass" means
All 5 samples match, `try_it.py` says 5/5, and the automatic tests pass.
