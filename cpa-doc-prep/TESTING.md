# Testing CPA Doc Prep (plain English)

## Run the automatic tests
1. `cd tab-zero-studios/cpa-doc-prep && ../.venv/bin/python -m pytest -q`.
2. **Pass:** `54 passed`. **Broken:** any `FAILED`.
3. Server check from the top folder: `.venv/bin/python mcp_smoke.py`. **Pass:** all `PASS`, `18/18`.

## 5 samples (tool name, what to send, expected)
**Sample 1: checklist.** `make_checklist` with profiles `["employee","homeowner"]`.
Expected: 7 items, all "missing": W-2 from each employer; 1099-INT; Form 1098; Property tax statement; Form 1095; Last year's return; Photo ID and dependents' info. Form 1098 and property tax appear only once even though both profiles list them. Profile names like `Self-Employed` also work. `astronaut` gives a clear error listing valid profiles.

**Sample 2: tracking.** From sample 1, `mark_item` id `w2` status `received`, then `checklist_summary`.
Expected counts: missing 6, received 1, sent_to_preparer 0, not_applicable 0. Statuses allowed: missing, received, sent_to_preparer, not_applicable. Anything else gives a clear error.

**Sample 3: email draft.** `draft_preparer_message` with that checklist, preparer `Sample CPA`, sender `Sample Client`.
Expected: starts "Hi Sample CPA,", "I have these ready for you:" lists the W-2, "Still waiting on:" lists the other 6, ends "Thanks, Sample Client". The result says "Draft only. Nothing was sent." Channel `text` gives one short paragraph: "Hi Sample CPA. Ready for you: W-2 from each employer. Still waiting on: ...".

**Sample 4: SSN refusal.** `check_sensitive` with `my ssn is 123 45 6789`.
Expected: has_ssn true, safe false, redacted text `my ssn is [removed]`; the number is never echoed back. Also try `123456789`, `123-45-6789`, `4111 1111 1111 1111`: all flagged. Then `draft_preparer_message` with note `my ssn is 123-45-6789`: it must **refuse** with "Remove SSN or card numbers first..." and not produce a draft. `last 4 is 6789` is allowed.

**Sample 5: no tax advice.** `scope_check` with `how much tax will I owe`.
Expected: is_tax_advice_request true; message "This tool only organizes tax paperwork. It can't work out what you owe or give tax advice. Ask your tax preparer." No dollar figure anywhere.

## Red flags
A number for what you owe; a full SSN/card in any draft; "sent" wording; a checklist missing for a profile; a crash instead of a clear message.

## What "pass" means
All 5 samples match and all automatic tests pass.
