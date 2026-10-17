# Testing HOA Compliance Desk (plain English)

## Fastest check (2 commands)
1. `cd tab-zero-studios/hoa-compliance-desk`
2. `../.venv/bin/python try_it.py`  **Pass:** five `PASS` lines and `5/5 samples passed`. **Broken:** any `FAIL`.
3. `../.venv/bin/python -m pytest -q`  **Pass:** `25 passed`. **Broken:** any `FAILED`.
4. Server check from the top folder: `.venv/bin/python mcp_smoke_new.py`. **Pass:** `20/20 checks passed` (covers all six new tools).

## The 5 samples by hand (tool name, what to send, expected)
**Sample 1: demo.** `lake_crest_demo`, then `board_summary`
Expected: Name "Lake Crest HOA (DEMO)", demo true, summary starts with "DEMO CONTENT. Numbers are made up for practice."

**Sample 2: notice.** `start_hoa` Sample Oaks HOA. `save_notice_rule` label `Annual`, days_before `21`, source `Bylaws Art. 3 Sec. 2`. `plan_meeting_notice` date `2026-12-10`, time `7 PM`, place `Clubhouse`, agenda [`Budget`,`Election`].
Expected: send_by 2026-11-19, text says "21 days before the meeting, per Bylaws Art. 3 Sec. 2, as your board typed". Draft starts "NOTICE OF ANNUAL MEETING OF MEMBERS: Sample Oaks HOA", has the agenda, and ends "[DRAFT FOR BOARD REVIEW...]".

**Sample 3: no rule.** Make a new HOA with no rule and call `plan_meeting_notice` the same way
Expected: send_by is empty and the text says no notice rule was saved and it won't guess.

**Sample 4: schedule.** `save_schedule` label `Quarterly dues`, kind `dues`, frequency `quarterly`, first_date `2026-11-30`, remind_days_before 7, amount 100. `upcoming_dates` within 250 days.
Expected: Dues on 2026-11-30, 2027-02-28 (month end handled), 2027-05-30, each with a reminder date 7 days earlier (2026-11-23 first). The date list depends on today's date.

**Sample 5: refusals.** `plan_meeting_notice` with agenda item `card 4111 1111 1111 1111`. `scope_check` with `is it legal to skip the annual meeting?`
Expected: Card refused. scope_check says it can't say what the law or your documents require.

## Red flags
A send-by date with no rule saved; legal claims; threats of liens or fines in reminders; Lake Crest data that looks real; SSN/card accepted.

## What "pass" means
All 5 samples match, `try_it.py` says 5/5, and the automatic tests pass.
