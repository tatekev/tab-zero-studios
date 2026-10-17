# Testing Caregiver Binder (plain English)

## Fastest check (2 commands)
1. `cd tab-zero-studios/caregiver-binder`
2. `../.venv/bin/python try_it.py`  **Pass:** five `PASS` lines and `5/5 samples passed`. **Broken:** any `FAIL`.
3. `../.venv/bin/python -m pytest -q`  **Pass:** `27 passed`. **Broken:** any `FAILED`.
4. Server check from the top folder: `.venv/bin/python mcp_smoke_new.py`. **Pass:** `20/20 checks passed` (covers all six new tools).

## The 5 samples by hand (tool name, what to send, expected)
**Sample 1: checklist.** `start_binder` person `Sample Person`, prepared_by `Sample Helper`
Expected: Checklist of 14 steps in three blocks: First hour, First 24 hours, First 72 hours. First step: "Make sure everyone is safe...".

**Sample 2: fill and print.** `add_contact` Pat Sample, Sister, 555-123-4567, call_first true. `add_contact` Lee Sample, Neighbor, 555-987-6543, lee@example.com, call_first true. `add_document` `Will`, type `will`, location `Fire safe in hall closet`, held_by `Sample Law Office`. `add_account` `First Bank checking`, type `bank`, kept_where `password manager`, last4 `1234`. `print_binder`.
Expected: Markdown with "CALL FIRST" on both contacts, the safe location, and a row "| First Bank checking | bank | 1234 | password manager |". Ends with the disclaimer.

**Sample 3: gaps.** `find_gaps`
Expected: Mentions no power of attorney, no health care directive, no email account, no phone account. Does not mention the will.

**Sample 4: secrets refused.** `add_account` with kept_where `password: hunter2`; again with `my PIN is 4321`; `123-45-6789`; `4111 1111 1111 1111`
Expected: All four refused with a message about writing WHERE it is kept. The message never repeats the secret. Nothing saved.

**Sample 5: advice refused.** `scope_check` with `is the will valid?`
Expected: is_advice_request true; says to ask an elder-law attorney, doctor, or financial professional.

## Red flags
Any password, PIN, or full number saved or echoed; advice about paying or cancelling; a crash on odd characters.

## What "pass" means
All 5 samples match, `try_it.py` says 5/5, and the automatic tests pass.
