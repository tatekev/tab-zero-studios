# Testing HOA Board Desk (plain English)

## Run the automatic tests
1. `cd tab-zero-studios/hoa-board-desk && ../.venv/bin/python -m pytest -q`
2. **Pass:** `29 passed`. **Broken:** any `FAILED`. They include the accessibility checks.
3. Server check from the top folder: `.venv/bin/python mcp_smoke.py`. **Pass:** all `PASS`, `18/18`.

## 5 samples
**Sample 1: audit (`audit_outdated`).** Text (4 lines): `Annual meeting 3/4/2023` / `Pool opens soon - coming soon!` / `Gate code is current` / `Dues due 12/01/2099`
Expected: exactly 2 flags: line 1 "date 3/4/2023 has passed", line 2 "placeholder wording". Lines 3 and 4 are NOT flagged. Also flagged: `TBD`, `TBA`, `XXX-XXXX`, `[insert date here]`, `Lorem ipsum`, "to be announced". Dates like `2023-03-04`, `March 4, 2023`, `4 March 2023` are caught.

**Sample 2: FAQ (`make_faq`).** Facts: question "When are dues due?", answer "Quarterly.", source "Sample Bylaws, Article 4"; question "Can I have a dog?", answer "Yes, up to two." (no source).
Expected: a title "Frequently Asked Questions"; first answer ends "(Source: Sample Bylaws, Article 4)"; second ends "(Source: not provided. Board to confirm before publishing.)". Entries with a blank question or answer are skipped and counted in a board note.

**Sample 3: newsletter (`make_newsletter`).** name `Sample Oaks HOA`, month `November 2099`, news `["New mailboxes installed"]`, dates `[{"date":"Nov 5","what":"Board meeting"}]`, reminders `["Trim hedges"]`.
Expected: title "Sample Oaks HOA Newsletter: November 2099"; sections What's new, Dates to remember (**Nov 5**: Board meeting), Friendly reminders; last line "Draft for board review before sending."

**Sample 4: 3-page site (`make_site`).** Use the FAQ and newsletter above, name `Sample Oaks HOA`, intro `Welcome`, out_dir a new empty folder.
Expected: exactly 3 files: index.html, faq.html, newsletter.html. Open each in a browser: readable text, links at the top to the other two pages, one big heading per page, a "Skip to main content" link appears when you press Tab.

**Sample 5: bad input handled.** In `make_site` use intro `![](pool.jpg)` (picture without a description).
Expected: a clear error "Every image needs alt text". With `![Pool in summer](pool.jpg)` it works and the image has that alt text. A name that is blank is refused.

## Accessibility basics (checked automatically)
Page language set (`lang="en"`, or `es` etc.), one h1 per page and no skipped heading levels, nav is labeled, main area marked, alt text required, skip link, text contrast above 4.5 to 1 (WCAG AA) on all three text colors.

## Red flags
A past date not flagged; a made-up source in the FAQ; a page that opens blank; more or fewer than 3 files; a crash on accented letters.
## What "pass" means
All 5 samples match and all automatic tests pass.
