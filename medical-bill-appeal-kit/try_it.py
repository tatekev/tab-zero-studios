"""Run the 5 samples from TESTING.md. Run: ../.venv/bin/python try_it.py"""
import sys
from datetime import date
from core import *
from safety import SensitiveDataError
T = date(2026, 10, 17); ok = []
def chk(n, c): ok.append(c); print(("PASS " if c else "FAIL ") + n)
chk("Sample 1: checklist has 12 steps, none done", len(checklist()) == 12 and not any(x["done"] for x in checklist()))
c = new_case("Sample Patient", "Sample Hospital", "Sample Insurance")
add_deadline(c, "Appeal", "denial letter, page 2", start_date="2026-10-01", days=180)
t = tracker(c, T)[0]
chk("Sample 2: 180 days from 2026-10-01 = 2027-03-30 (164 days left), source shown", t["due"] == "2027-03-30" and t["status"] == "164 days left" and t["source"] == "denial letter, page 2")
try: add_deadline(c, "Pay", "", exact_date="2026-12-01"); nosrc = False
except ValueError: nosrc = True
chk("Sample 3: a deadline with no source is refused", nosrc and len(c["deadlines"]) == 1)
d = itemized_request_letter(c, "2026-09-03", "1 Sample St", "1234", today=T)["draft"]
a = appeal_letter(c, "9876", "2026-10-05", "Service not medically necessary", "My doctor ordered it.", ["Denial letter"], today=T)["draft"]
chk("Sample 4: both letters are drafts, use only your words", "itemized bill" in d and "ending 1234" in d and "My doctor ordered it." in a and "[DRAFT" in a)
try: new_case("123-45-6789", "x"); ref = False
except SensitiveDataError: ref = True
chk("Sample 5: SSN refused; 'should I take this medication' refused", ref and scope_check("should I take this medication?")["is_advice_request"])
print(f"{sum(ok)}/{len(ok)} samples passed"); sys.exit(0 if all(ok) else 1)
