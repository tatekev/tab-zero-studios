# Testing Medical Bill & Appeal Kit (plain English)

## Fastest check (2 commands)
1. `cd tab-zero-studios/medical-bill-appeal-kit`
2. `../.venv/bin/python try_it.py`  **Pass:** five `PASS` lines and `5/5 samples passed`. **Broken:** any `FAIL`.
3. `../.venv/bin/python -m pytest -q`  **Pass:** `29 passed`. **Broken:** any `FAILED`.
4. Server check from the top folder: `.venv/bin/python mcp_smoke_new.py`. **Pass:** `20/20 checks passed` (covers all six new tools).

## The 5 samples by hand (tool name, what to send, expected)
**Sample 1: checklist.** `bill_checklist`
Expected: 12 items, none done. First is "I have an ITEMIZED bill...". `tick_checklist_item` with id `itemized` marks it done.

**Sample 2: deadline from days.** `start_case` (Sample Patient, Sample Hospital, insurer Sample Insurance). `add_deadline` label `Appeal`, source `denial letter, page 2`, start_date `2026-10-01`, days `180`. `deadline_tracker`.
Expected: Due 2027-03-30, "as you typed", source shown (164 days left on Oct 17, 2026).

**Sample 3: no source, no deadline.** `add_deadline` with an empty source
Expected: Clear error: "source is required...never guesses deadlines." Nothing saved.

**Sample 4: letters.** `draft_itemized_bill_request` (date `2026-09-03`, account_last4 `1234`). `draft_appeal_letter` (claim `9876`, denial_date `2026-10-05`, reason `Service not medically necessary`, why `My doctor ordered it.`)
Expected: Both end with "[DRAFT...]" and say "Nothing was sent". The first says "Account reference: ending 1234". The second quotes your reason and why, and has no legal claims.

**Sample 5: refusals.** `start_case` with patient name `123-45-6789`. `add_deadline` ... `itemized_bill_request` with account_last4 `12345678`. `scope_check` with `should I take this medication?`
Expected: SSN and the long number are refused. scope_check says it can't give medical or legal advice.

## Red flags
A deadline with no source; legal threats or promises in a letter; an SSN/card/long account number accepted; anything that looks sent.

## What "pass" means
All 5 samples match, `try_it.py` says 5/5, and the automatic tests pass.
