# TZS end-user test report, Sat Oct 17, 2026 (CT)
Tested locally on the box as an end user: fresh venv, README install, real MCP-over-stdio servers, every step of each TESTING.md, plus messy inputs. Sample data only. Nothing pushed, published, or sent.

## Final result: ALL GOOD
`./run_all_checks.sh`: unpack 35 passed, cpa-doc-prep 67 passed, hoa-board-desk 35 passed, MCP smoke 18/18, new end-user walk-through (`mcp_end_user.py`) 90/90.

## Install (as the README says)
- `./run_all_checks.sh` failed on a clean checkout (it pointed at a python path that did not exist and needed a hand-made venv). FIXED: it now builds its own `.venv` and installs `requirements.txt`. After that, install works with no accounts or keys.
- READMEs now give explicit install steps (Python 3.10+, venv, pip, MCP client config), what each tool really does, and its limits.

## Unpack: PASS after fixes
Steps run: all 5 TESTING.md samples (shutoff with tomorrow's date = "1 day from today", IRS CP14 = 2099-11-30, EOB no date, HOA "14 days" not turned into a date, injection + SSN), plus empty, blank, Spanish, 03/04/2027, "Jan 5".
Messy: misspelled month, impossible date 02/30, "TBD / [date]", 100k+ chars, accents/CJK, SSN/card as `123-45-6789`, `123 45 6789`, 9 digits, `1 2 3 - 4 5 - 6 7 8 9`, 16 digits, dashed, spaced, full-width, zero-width.
Promises: three answers, disclaimer, no invented deadline, SSN/card never shown.
Failures found and fixed (in the code, then tests, then docs):
1. SSN typed with odd spacing (`1 2 3 - 4 5 - 6 7 8 9`) was NOT hidden. Now hidden.
2. A misspelled or impossible deadline date (`by Decmber 31, 2099`, `02/30/2099`) said only "No clear date found", with no hint a date was in the letter. Now says the letter seems to mention it, and nothing was guessed.
3. Grammar: "an utility bill" fixed.
+5 new regression tests.

## CPA Doc Prep: PASS after fixes
Steps run: all 5 TESTING.md samples (7-item checklist with dedupe, tracking 6/1/0/0, email + text drafts, SSN refusal incl. `last 4` allowed, tax-advice decline), bad profile/status/id/channel, blank input.
Promises: never computes tax (verified: no dollar figure in any output); refuses SSN/card in drafts.
Failures found and fixed:
1. Disguised SSN/card numbers got through into drafts: spaced digits, `123/45/6789`, `123_45_6789`, en-dashes, zero-width characters. Now detected, redacted, and drafts refuse them.
2. Tax-advice questions missed: "do I need to file?", "is my mortgage interest deductible", "calculate my taxes", "do I qualify for the child tax credit", "what is my tax bracket". Now declined with the "ask your preparer" message.
3. Notes over 2000 chars were silently cut. Now the draft warns.
4. Empty-preparer draft opened "Hi your preparer," Now "Hi,".
+13 new tests (no date lists falsely flagged as numbers).
Known limit (documented): tax-question detection is English-only and phrase-based; e.g. Spanish "cuánto impuesto debo" is not caught. It still never computes anything.

## HOA Board Desk: PASS after fixes
Steps run: all 5 TESTING.md samples (audit = exactly lines 1 and 2, FAQ with sources and unsourced label, newsletter, 3-file site with a11y, alt-text refusal), blank name, bad lang, accents/es site, script tag and javascript: link, 100k+ char intro, 5000-line audit.
Failures found and fixed:
1. `02/30/2023` (impossible date) was not flagged. Now flagged.
2. `Next meeting: Oct 1` (no year, already past this year) was not flagged. Now flagged (the word "May" alone is not treated as a date).
3. Newsletter and FAQ would happily publish past dates or "TBD" with no warning. Now they add a visible "Board check" line (newsletter still ends with the "Draft for board review" line).
4. Newsletter accepted a blank community/month ("#  Newsletter: "). Now refused.
+6 new tests. One old test was updated: impossible dates are now flagged rather than ignored.
Note: sample 3's "Nov 5" has no year, so after Nov 5 it will also show a "Board check" line. That is correct and documented.

## Docs updated
Each README and TESTING.md (new counts, messy-input section), top-level README/TESTING.md, `.gitignore` (.venv).

## Needs Kevin / parent
- No git repo exists at /workspace/kevin-portfolio (not a repo), so I could not commit; files are changed in place. The pushed GitHub repo needs these changes copied or pushed by whoever owns that clone, with Kevin's okay.
- The marketplace entries said TESTING.md steps; the TESTING.md in the repo is now updated but the GitHub copy is stale until pushed.
- Not tested: running inside the actual Grok Bot app (no access here). MCP over stdio was tested with the official MCP client instead.
- Old TEST-RESULTS.md (Oct 16) is superseded by this report; counts there are out of date.
