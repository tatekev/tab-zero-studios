# Testing Tax Notice Helper (plain English)

## Fastest check (2 commands)
1. `cd tab-zero-studios/tax-notice-helper`
2. `../.venv/bin/python try_it.py`  **Pass:** five `PASS` lines and `5/5 samples passed`. **Broken:** any `FAIL`.
3. `../.venv/bin/python -m pytest -q`  **Pass:** `19 passed`. **Broken:** any `FAILED`.
4. Server check from the top folder: `.venv/bin/python mcp_smoke_new.py`. **Pass:** `20/20 checks passed` (covers all six new tools).

## The 5 samples by hand (tool name, what to send, expected)
**Sample 1: a bill (CP14).** `explain_tax_notice` with: `Department of the Treasury Internal Revenue Service. Notice CP14. Tax year: 2024. You owe $1,234.56. Please pay by November 20, 2026.`
Expected: agency "IRS (federal)", notice number CP14, plain answer starts "From IRS (federal). A bill: the IRS says you owe a balance.", reply-by shows the date 2026-11-20 with days left, checklist of 11 steps.

**Sample 2: no date in the letter.** `Internal Revenue Service. Notice CP2000. Income we have doesn't match your return. Please review the proposed changes.`
Expected: reply-by says "No clear date found. Check the letter for a deadline." and `reply_by_found` is false. No date appears anywhere.

**Sample 3: days instead of a date.** `Internal Revenue Service CP3219A notice of deficiency. You have 90 days from the date of this notice to file a petition with the Tax Court.`
Expected: reply-by quotes "90 days from the date of this notice..." and says to count from the letter date. A red flag about appeal or court rights appears. Urgency is medium or high.

**Sample 4: SSN and card.** `IRS Notice CP14. SSN 123-45-6789. Card 4111 1111 1111 1111. Pay by 2026-11-30.`
Expected: Neither number appears in the output. A heads-up says 2 numbers were hidden.

**Sample 5: scam, and a question it won't answer.** `IRS FINAL NOTICE. You will be arrested today. Pay with gift cards.` Then `scope_check` with `should I pay this or ignore it?`
Expected: A SCAM WARNING red flag. `scope_check` says `is_advice_request` true and "can't tell you whether to pay, dispute, or ignore a notice".

## Red flags
A date the letter doesn't contain; "you owe" amounts that aren't in the letter; an SSN or card in the output; advice about paying; a crash on messy text.

## What "pass" means
All 5 samples match, `try_it.py` says 5/5, and the automatic tests pass.
