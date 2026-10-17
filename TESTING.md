# Tab Zero Studios: How to test everything (plain English)

Sample data only. Never paste a real SSN, card number, or real letter while testing.

## The 60-second check (all three tools at once)
1. Open a terminal on the computer or box that holds this folder (or ask Cornelius: "Run the Tab Zero Studios self-check and show me the last 3 lines").
2. Copy and paste: `cd tab-zero-studios && ./run_all_checks.sh`
3. Wait about 10 seconds.
4. **Pass looks like:** the last line says `ALL GOOD`, and you see `35 passed`, `67 passed`, `35 passed`, `18/18 MCP checks passed`, and `90/90 end-user checks passed` (numbers may grow, never shrink).
5. **Broken looks like:** the last line says `PROBLEM`, any line says `FAILED` or `FAIL`, or a Python error shows up. Don't submit. Screenshot it and send it to Cornelius.

## Test each tool by hand (5 samples each)
Open the folder for each tool and follow its own `TESTING.md`:
1. `unpack/TESTING.md`
2. `cpa-doc-prep/TESTING.md`
3. `hoa-board-desk/TESTING.md`

If you test inside Grok Bot after listing, paste the sample into the chat and say the tool name, for example "Use Unpack on this letter: ...". The answers should match the "Expected" parts.

## What every tool must always do (the promises)
- Unpack: gives What is it / What to do / By when, an urgency, one tiny first step, and the disclaimer. If there is no deadline it says "No clear ... date". It never makes up a date.
- CPA Doc Prep: builds a checklist, tracks received / missing / sent, drafts an email or text, refuses SSN or card numbers in drafts, and refuses to say what you owe.
- HOA Board Desk: flags past dates and placeholder text, builds an FAQ with sources, a newsletter, and a 3-page site.

## Red flags that mean something is broken
- A date appears that is not in the letter.
- A full SSN or card number shows up in any output.
- The tool says how much tax you owe or what to deduct.
- A draft says it was sent. (Nothing is ever sent.)
- The tool crashes on empty text instead of giving a polite message.
- The HOA site opens with unreadable text, a missing page, or no headings.

## Known limits (honest list)
- Unpack reads English only and may miss unusual date wording. If it says "No clear date found", read the letter yourself.
- "Within 30 days" is quoted back, never counted for you.
- Dates like 03/04/2027 could be March 4 or April 3. Unpack assumes month/day (US) and tells you to double-check.
- The CPA checklist is a general starting list, not a complete or personalized one.
- HOA audit flags are prompts to check, not verdicts. A past date can be correct history.
- Accessibility is checked automatically (language, headings, alt text, contrast, skip link). It is not a full audit with screen readers.
