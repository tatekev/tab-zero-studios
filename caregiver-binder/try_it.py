"""Run the 5 samples from TESTING.md. Run: ../.venv/bin/python try_it.py"""
import sys
from datetime import date
from core import *
from safety import SensitiveDataError
T = date(2026, 10, 17); ok = []
def chk(n, c): ok.append(c); print(("PASS " if c else "FAIL ") + n)
b = new_binder("Sample Person", "Sample Helper")
chk("Sample 1: checklist has 14 steps in 3 time blocks", len(b["checklist"]) == 14 and {c["when"] for c in b["checklist"]} == {"First hour", "First 24 hours", "First 72 hours"})
add_contact(b, "Pat Sample", "Sister", "555-123-4567", call_first=True); add_contact(b, "Lee Sample", "Neighbor", "555-987-6543", "lee@example.com", True)
add_document(b, "Will", "will", "Fire safe in hall closet", "Sample Law Office"); add_account(b, "First Bank checking", "bank", "password manager", "1234")
m = to_markdown(b, T)
chk("Sample 2: printed binder shows CALL FIRST, location, and 'ends in 1234'", "**CALL FIRST**" in m and "Fire safe in hall closet" in m and "| bank | 1234 | password manager |" in m)
g = " ".join(gaps(b))
chk("Sample 3: gaps names missing power of attorney, directive, email", "power of attorney" in g and "health care directive" in g and "No email account" in g)
bad = 0
for s in ("password: hunter2", "my PIN is 4321", "123-45-6789", "4111 1111 1111 1111"):
    try: add_account(b, "Bank", "bank", s)
    except SensitiveDataError: bad += 1
chk("Sample 4: password, PIN, SSN, card all refused (4/4), nothing saved", bad == 4 and len(b["accounts"]) == 1)
chk("Sample 5: 'is the will valid' refused", scope_check("is the will valid?")["is_advice_request"])
print(f"{sum(ok)}/{len(ok)} samples passed"); sys.exit(0 if all(ok) else 1)
