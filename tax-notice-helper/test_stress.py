import random, string
from datetime import date
from core import explain_notice, to_markdown
def test_fuzz_never_crashes():
    random.seed(7)
    pool = string.printable + "éß漢字🙂\u200b\u202e"
    for _ in range(300):
        s = "".join(random.choice(pool) for _ in range(random.randint(0, 400)))
        r = explain_notice(s, date(2026, 10, 17)); to_markdown(r)
        assert r["disclaimer"] and r["reply_checklist"]
def test_never_invents_dates_fuzz():
    for s in ["IRS CP14 pay soon", "Department of Revenue notice, respond promptly", "IRS notice. Within 30 days of this letter."]:
        r = explain_notice(s, date(2026, 10, 17))
        assert r["reply_by_found"] is False
