# Test results (Oct 16, 2026, CT)

| Check | Pass | Fail |
|---|---|---|
| Unpack automated tests (31; 26 stress inputs + 5 originals) | 31 | 0 |
| CPA Doc Prep automated tests (54; 40+ parametrized adversarial inputs) | 54 | 0 |
| HOA Board Desk automated tests (29; incl. accessibility) | 29 | 0 |
| Real MCP over stdio (`mcp_smoke.py`, all 3 servers) | 18 | 0 |
| **Total** | **132** | **0** |

Re-run any time: `./run_all_checks.sh` (ends with `ALL GOOD`).

## Inputs stress-tested
Utility shutoff, IRS-style notice, medical EOB, HOA violation letter; empty / whitespace / None; 100,000+ char input (under 5s); Spanish; 7 date formats (slash, ISO, "Oct. 30, 2026", "30 October 2026", 2-digit year, full-width digits); no year; past dates; invalid dates (02/30); multiple deadlines; "within 30 days"; SSN as dashes / spaces / dots / no separators / full-width; 16-digit and Amex cards; four date strings that must NOT look like a card; prompt injection inside a letter; RTL and zero-width characters; emoji and accents; "how much tax will I owe" and four similar questions; script tags and javascript: links in HOA text; images without alt text.

## Bugs fixed (found by reading the code and probing; old code was not re-run on every input, so treat "before" as reviewed, not measured)
Unpack
- Keywords matched inside words (for example "irs" in "first"), causing wrong letter types. Now whole-word matching.
- Only 2 date formats read. Now 5 families; "Oct. 25" no longer splits the sentence.
- Dates without a year were silently assumed this year even when already past. Now flagged, never used as a deadline if past.
- Any date in a letter could become the deadline. Now only a date near a deadline word counts; other dates are listed separately ("Hearing" is not a deadline).
- "Within N days" is quoted, never turned into a date.
- Empty input and non-English text had no handling. Added messages and a warning.
- SSN/card numbers in a letter were echoed back. Now hidden everywhere.
- Prompt-injection sentences could appear as "what to do". Now ignored with a warning.
- Urgency was "medium" for deadlines decades away. Fixed. Overdue letters now say so.
- Added weak-guess wording ("might be") and "an HOA notice".
CPA Doc Prep
- SSN check missed spaces and dots; card check was loose and could match strings of dates. Rewritten.
- Only the note was scanned. Now preparer, sender, and every checklist item are scanned too.
- Unknown profile names were silently ignored. Now a clear error. Names like "Self-Employed" now work.
- Added `scope_check` so "how much tax will I owe" gets a plain refusal, and drafts warn if the note asks a tax question.
- Text-message drafts were mangled ("Still waiting on:; item"). Fixed. Bad channel is refused.
- Summary now always shows all four statuses plus counts.
HOA Board Desk
- Audit only read US dates and year-only text. Now 4 date formats; more placeholders (TBA, "to be announced", "[insert date]", fake 555-01xx phone numbers). A past date next to a future date is still flagged.
- FAQ entries without sources looked sourced. Now labeled "Source: not provided"; skipped entries are counted.
- FAQ used skipped heading levels (h1 to h3), an accessibility problem. Now h2.
- Site had no skip link, nav label, or main area; no way to require alt text; files written without UTF-8 (crash risk on accents); page language fixed to English. All fixed. Images now require alt text.
- Newsletter crashed on malformed date entries. Now skipped.

## Claims softened in SUBMISSION.md / READMEs
- Unpack: added "English only" and "never invents a deadline"; "flags urgency" is now "rates urgency".
- CPA Doc Prep: "Warns before full SSNs or card numbers get pasted" is now "checks text for ... and refuses to put them in a draft" (it cannot stop typing elsewhere). Checklist is called a general starting list. "Stores nothing" clarified: the client app holds the checklist.
- HOA Board Desk: "accessible" is now "follows basic accessibility practices" (automated checks only, no screen-reader audit). "Stale dates" is now "past dates ... for the board to check". "Cites sources" is now "shows the sources you give". README no longer says "stores nothing" without noting `make_site` writes 3 files.

## Not covered
No real-browser or screen-reader audit. Unpack covers English only. Date wording the rules don't know (for example "the fifteenth of next month") is reported as "No clear date found", never guessed.
