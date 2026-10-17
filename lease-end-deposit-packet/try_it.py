"""Run the 5 samples from TESTING.md. Run: ../.venv/bin/python try_it.py"""
import sys
from datetime import date
from core import *
from safety import SensitiveDataError
T = date(2026, 10, 17); ok = []
def chk(n, c): ok.append(c); print(("PASS " if c else "FAIL ") + n)
p = new_packet("Sample Tenant", "Sample Landlord LLC", "1 Sample Ave, Apt 2", "2024-08-01", "2026-09-30", 1200, "9 New St")
add_photo(p, "move_in", "Kitchen", "Counter", "good", "k1.jpg", "2024-08-01"); add_photo(p, "move_out", "Kitchen", "Counter", "damaged", "k2.jpg", "2026-09-30")
add_photo(p, "move_in", "Bedroom", "Carpet", "worn", "b1.jpg", "2024-08-01"); add_photo(p, "move_out", "Bedroom", "Carpet", "worn", "b2.jpg", "2026-09-30")
c = compare(p)
chk("Sample 1: counter 'looks worse', carpet unchanged", [x["item"] for x in c["looks_worse_at_move_out"]] == ["counter"] and [x["item"] for x in c["same_or_better"]] == ["carpet"])
chk("Sample 2: no rule saved -> no deadline, says it won't guess", tracker(p, T)[0]["due"] is None and "won't guess" in tracker(p, T)[0]["tip"])
add_rule(p, "Landlord returns deposit", 30, "move_out_date", "Lease section 12")
t = tracker(p, T)[0]
chk("Sample 3: YOUR rule (30 days) -> 2026-10-30, 13 days left", t["due"] == "2026-10-30" and t["status"] == "13 days left")
d = demand_letter(p, 600, ["The counter chip was there at move-in, see k1.jpg."], today=T)["draft"]
chk("Sample 4: letter uses your reason, cites no law", "$600.00" in d and "k1.jpg" in d and "statute" not in d.lower() and "[DRAFT" in d)
try: add_rule(p, "x", 5, "other", ""); nosrc = False
except ValueError: nosrc = True
chk("Sample 5: rule with no source refused; 'what is the law' refused", nosrc and scope_check("what is the law on deposits")["is_advice_request"])
print(f"{sum(ok)}/{len(ok)} samples passed"); sys.exit(0 if all(ok) else 1)
