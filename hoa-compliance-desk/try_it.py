"""Run the 5 samples from TESTING.md. Run: ../.venv/bin/python try_it.py"""
import sys
from datetime import date
from core import *
from safety import SensitiveDataError
T = date(2026, 10, 17); ok = []
def chk(n, c): ok.append(c); print(("PASS " if c else "FAIL ") + n)
h = demo_hoa()
chk("Sample 1: Lake Crest is clearly marked DEMO", h["demo"] and "DEMO" in h["name"] and "DEMO CONTENT" in board_summary(h, T))
h2 = new_hoa("Sample Oaks HOA"); add_notice_rule(h2, "Annual", 21, "Bylaws Art. 3 Sec. 2")
r = plan_meeting_notice(h2, "2026-12-10", "7 PM", "Clubhouse", ["Budget", "Election"], today=T)
chk("Sample 2: send-by = 2026-11-19 from YOUR rule; notice drafted", r["send_by"] == "2026-11-19" and "NOTICE OF ANNUAL MEETING" in r["draft"] and "[DRAFT FOR BOARD REVIEW" in r["draft"])
chk("Sample 3: no rule -> no send-by date", plan_meeting_notice(new_hoa("S"), "2026-12-10", "7", "Hall", ["x"], today=T)["send_by"] is None)
add_schedule(h2, "Quarterly dues", "dues", "quarterly", "2026-11-30", 7, 100)
u = upcoming(h2, T, 250)
chk("Sample 4: quarterly dues 2026-11-30, 2027-02-28, 2027-05-30; reminders 7 days earlier", [x["due"] for x in u] == ["2026-11-30", "2027-02-28", "2027-05-30"] and u[0]["remind_on"] == "2026-11-23")
try: plan_meeting_notice(h2, "2026-12-10", "7", "Hall", ["card 4111 1111 1111 1111"], today=T); ref = False
except SensitiveDataError: ref = True
chk("Sample 5: card refused; 'is it legal to skip the meeting' refused", ref and scope_check("is it legal to skip the annual meeting?")["is_advice_request"])
print(f"{sum(ok)}/{len(ok)} samples passed"); sys.exit(0 if all(ok) else 1)
