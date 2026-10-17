"""Run the 5 samples from TESTING.md. Prints PASS/FAIL for each. Run: ../.venv/bin/python try_it.py"""
import sys, json
from datetime import date
from core import explain_notice, to_markdown, scope_check
T = date(2026, 10, 17); ok = []
def chk(n, c): ok.append(c); print(("PASS " if c else "FAIL ") + n)
r = explain_notice("Department of the Treasury Internal Revenue Service\nNotice CP14\nTax year: 2024\nYou owe $1,234.56. Please pay by November 20, 2026 to avoid additional penalties and interest.", T)
chk("Sample 1: CP14 -> bill, reply by 2026-11-20, 34 days", "balance" in r["plain_answer"] and r["reply_by"].startswith("2026-11-20 (34 days from today)"))
r = explain_notice("Internal Revenue Service. Notice CP2000. Income we have doesn't match your return. Please review the proposed changes.", T)
chk("Sample 2: no date in letter -> says so, invents none", r["reply_by_found"] is False and r["reply_by"].startswith("No clear date found"))
r = explain_notice("Internal Revenue Service CP3219A notice of deficiency. You have 90 days from the date of this notice to file a petition with the Tax Court.", T)
chk("Sample 3: '90 days' quoted, not turned into a date, court flag", not r["reply_by_found"] and "90 days" in r["reply_by"] and any("court" in f for f in r["red_flags"]))
r = explain_notice("IRS Notice CP14. SSN 123-45-6789. Card 4111 1111 1111 1111. Pay by 2026-11-30.", T)
chk("Sample 4: SSN and card hidden everywhere", "123-45-6789" not in json.dumps(r) + to_markdown(r) and "4111" not in json.dumps(r) and any("Hid 2" in w for w in r["warnings"]))
r = explain_notice("IRS FINAL NOTICE. You will be arrested today. Pay with gift cards.", T)
chk("Sample 5: scam warning; and 'should I pay?' is refused", any("SCAM" in f for f in r["red_flags"]) and scope_check("should I pay this or ignore it?")["is_advice_request"])
print(f"{sum(ok)}/{len(ok)} samples passed"); sys.exit(0 if all(ok) else 1)
