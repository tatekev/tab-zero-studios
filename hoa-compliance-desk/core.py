"""HOA Compliance Desk core: annual-meeting notice planner, dues/reserve reminder schedule, records checklist.
Drafts only; nothing is sent. Offline, stores nothing (your app keeps the 'hoa'). Never states what a state law or your
documents require: notice periods are typed in by the board with where they found them. Not legal advice.
'Lake Crest' content here is DEMO sample content (clearly marked), not real HOA data."""
import re, calendar
from datetime import date
from safety import (norm, field, parse_date, add_days, positive_int, money, refuse_sensitive, status_for, md_escape, SensitiveDataError)

DISCLAIMER = "Board paperwork help only. Not legal advice. This tool doesn't know your state's rules or your governing documents; every notice period here is one your board typed in from them. Check with your HOA attorney or manager."
LEGAL_Q = re.compile(r"\b(?:is (?:it|this|that) (?:legal|required|allowed|valid)|do we (?:have to|need to)|are we (?:required|allowed|liable)|can (?:the board|we|an owner|a homeowner) (?:fine|foreclose|lien|evict|sue|ignore|skip|waive)|what(?:'s| is| are) the (?:law|statute|rule|quorum|notice period)|how (?:many|long) days (?:notice|do)|quorum|proxy rules?|foreclos\w+|\bsue\b|lawsuit|liab\w+)\b", re.I)
ADVICE_MSG = "This desk organizes notices, reminders, and records from rules your board types in. It can't say what the law or your documents require. Ask your HOA attorney, manager, or read your bylaws."
FREQ = {"monthly": 1, "quarterly": 3, "semiannual": 6, "annual": 12}
KINDS = ("dues", "reserve", "insurance", "tax_filing", "other")

RECORDS = [
    {"id": "governing", "item": "Governing documents: declaration/CC&Rs, bylaws, articles, rules and amendments", "hint": "Keep the current version and the amendment history."},
    {"id": "minutes", "item": "Board and member meeting minutes, with date and who attended", "hint": "Approved minutes in one folder, by year."},
    {"id": "notices", "item": "Copies of every meeting notice sent, with the date and how it was sent", "hint": "Proof that notice went out."},
    {"id": "financials", "item": "Budget, year-end financial statements, bank statements", "hint": "Treasurer keeps; board reviews."},
    {"id": "reserve", "item": "Reserve study or reserve plan, and reserve account statements", "hint": "Note the date of the last study."},
    {"id": "dues", "item": "Dues and assessment ledger by unit", "hint": "Who paid, who is late, and the date of each reminder sent."},
    {"id": "insurance", "item": "Insurance policies and certificates, with renewal dates", "hint": "Put the renewal date on the reminder schedule."},
    {"id": "contracts", "item": "Vendor contracts and invoices (landscaping, management, repairs)", "hint": "Note each end or renewal date."},
    {"id": "violations", "item": "Violation notices, owner replies, and outcomes", "hint": "One folder per unit."},
    {"id": "arc", "item": "Architectural/modification requests and decisions", "hint": "Date received, decision, date told."},
    {"id": "elections", "item": "Election materials: candidate list, ballots procedure, results", "hint": "Keep per your governing documents."},
    {"id": "tax", "item": "Tax filings and registrations (federal/state, annual report)", "hint": "Ask your accountant which apply. Put due dates on the schedule."},
    {"id": "owner_list", "item": "Current owner and contact list", "hint": "Keep private; share only with the board."},
    {"id": "retention", "item": "I checked my governing documents and state page for how long to keep each record", "hint": "This tool doesn't know retention periods. Write down your source."},
]

def scope_check(text):
    q = bool(LEGAL_Q.search(norm(text)))
    return {"is_advice_request": q, "message": ADVICE_MSG if q else "OK. This is a paperwork question."}

def new_hoa(name, contact=""):
    refuse_sensitive(name, contact, secrets=True)
    return {"name": field(name, "name", 120, required=True), "contact": field(contact, "contact", 200), "demo": False, "rules": [], "schedules": []}

def demo_hoa():
    """Lake Crest DEMO: made-up sample numbers for trying the tool. Replace with your board's real facts."""
    h = new_hoa("Lake Crest HOA (DEMO)", "board@example.com (demo)"); h["demo"] = True
    add_notice_rule(h, "Annual meeting notice", 21, "DEMO ONLY: example number, not Lake Crest's real rule. Board must replace from its bylaws.")
    add_schedule(h, "Quarterly dues reminder", "dues", "quarterly", "2026-12-01", 7, 150)
    add_schedule(h, "Reserve contribution reminder", "reserve", "annual", "2027-01-15", 14, 5000)
    add_schedule(h, "Insurance renewal check", "insurance", "annual", "2027-03-01", 30, None)
    return h

def _h(h):
    if not isinstance(h, dict) or "name" not in h: raise ValueError("Pass the hoa that new_hoa() or demo_hoa() gave you.")
    h.setdefault("rules", []); h.setdefault("schedules", []); return h

def add_notice_rule(hoa, label, days_before, source):
    h = _h(hoa); refuse_sensitive(label, source, secrets=True)
    src = field(source, "source", 300)
    if not src: raise ValueError("source is required: say which bylaw or document says this (article, section). This tool never supplies notice periods.")
    h["rules"].append({"label": field(label, "label", 100, required=True), "days_before": positive_int(days_before, "days_before", 365), "source": src}); return h

def plan_meeting_notice(hoa, meeting_date, time, place, agenda, rule_label="", today=None):
    h = _h(hoa); today = today or date.today(); refuse_sensitive(time, place, agenda, rule_label, secrets=True)
    md = parse_date(meeting_date, "meeting_date")
    items = [field(a, "agenda item", 200) for a in (agenda or []) if field(a, "agenda item", 200)]
    if not items: raise ValueError("Add at least one agenda item.")
    rule = None
    if rule_label:
        rule = next((r for r in h["rules"] if r["label"] == rule_label), None)
        if not rule: raise ValueError(f"No notice rule named '{rule_label}'. Add it first with add_notice_rule (with its source).")
    elif len(h["rules"]) == 1: rule = h["rules"][0]
    warnings = []; send_by = None
    if rule:
        sb = add_days(md, -rule["days_before"]); send_by = sb.isoformat(); n = (sb - today).days
        info = f"Send by {send_by} ({rule['days_before']} days before the meeting, per \"{rule['source']}\", as your board typed). {status_for(n)}."
        if n < 0: warnings.append(f"The send-by date ({send_by}) has already passed. Talk to your HOA attorney or manager before you send, and consider moving the meeting date.")
    else:
        info = "No send-by date: no notice rule was saved. Check your bylaws and add the rule. This tool won't guess."
    if md < today: warnings.append("The meeting date is in the past.")
    if md.weekday() >= 5: warnings.append("The meeting falls on a weekend. Fine if intended; check it is the right day.")
    L = [f"NOTICE OF ANNUAL MEETING OF MEMBERS: {h['name']}", "", f"Date: {md.strftime('%A, %B %d, %Y').replace(' 0', ' ')}", f"Time: {field(time, 'time', 60) or '[TIME]'}",
         f"Place: {field(place, 'place', 200) or '[PLACE]'}", "", "Agenda:"] + [f"{i}. {a}" for i, a in enumerate(items, 1)] + ["",
         "All owners are invited. Please contact the board with questions" + (f": {h['contact']}." if h["contact"] else "."), "",
         "By order of the Board of Directors.", "", "[DRAFT FOR BOARD REVIEW: check the wording against your bylaws before sending. Keep a record of the date and how it was sent.]"]
    return {"send_by": send_by, "send_by_info": info, "warnings": warnings, "draft": "\n".join(L), "note": "Draft only. Nothing was sent. " + DISCLAIMER}

def add_schedule(hoa, label, kind, frequency, first_date, remind_days_before, amount=None):
    h = _h(hoa); refuse_sensitive(label, secrets=True)
    k = re.sub(r"[\s-]+", "_", norm(kind).strip().lower()); f = norm(frequency).strip().lower()
    if k not in KINDS: raise ValueError("kind must be one of: " + ", ".join(KINDS))
    if f not in FREQ: raise ValueError("frequency must be one of: " + ", ".join(FREQ))
    h["schedules"].append({"label": field(label, "label", 100, required=True), "kind": k, "frequency": f, "first_date": parse_date(first_date, "first_date").isoformat(),
                           "remind_days_before": positive_int(remind_days_before, "remind_days_before", 365) if remind_days_before not in (None, 0) else 0,
                           "amount": None if amount in (None, "") else money(amount, "amount")}); return h

def _occurrences(first, months, start, end):
    out = []; i = 0
    while True:
        total = first.month - 1 + months * i; y = first.year + total // 12; m = total % 12 + 1
        d = date(y, m, min(first.day, calendar.monthrange(y, m)[1]))
        if d > end: break
        if d >= start: out.append(d)
        i += 1
        if i > 2000: break
        if months == 0: break
    return out

def upcoming(hoa, today=None, within_days=120):
    """Every due date in the window from schedules your board saved, with the reminder-send date."""
    h = _h(hoa); today = today or date.today(); end = add_days(today, positive_int(within_days, "within_days", 1830)); out = []
    for s in h["schedules"]:
        for d in _occurrences(parse_date(s["first_date"]), FREQ[s["frequency"]], today, end):
            rem = add_days(d, -s["remind_days_before"]); out.append({"label": s["label"], "kind": s["kind"], "due": d.isoformat(), "remind_on": rem.isoformat(),
                "amount": s["amount"], "status": status_for((d - today).days), "reminder_status": status_for((rem - today).days)})
    out.sort(key=lambda x: x["due"])
    if not h["schedules"]: return [{"label": "No schedules saved", "due": None, "tip": "Add dues or reserve dates with add_schedule."}]
    return out

def reminder_draft(hoa, label, due_date, amount=None, pay_instructions=""):
    h = _h(hoa); refuse_sensitive(label, pay_instructions, secrets=True)
    d = parse_date(due_date, "due_date"); a = None if amount in (None, "") else money(amount, "amount")
    L = [f"Friendly reminder from {h['name']}", "", f"{field(label, 'label', 100, required=True)} is due {d.strftime('%B %d, %Y').replace(' 0', ' ')}" + (f": ${a:,.2f}." if a is not None else "."), "",
         field(pay_instructions, "pay_instructions", 500) or "[HOW TO PAY: add your board's payment instructions]", "",
         "If you have already paid, thank you. If you have questions, please contact the board" + (f" at {h['contact']}." if h["contact"] else "."), "", "[DRAFT FOR BOARD REVIEW. Nothing was sent. Check it against your documents before sending.]"]
    return {"draft": "\n".join(L), "note": "Draft only. Nothing was sent. " + DISCLAIMER}

def records_checklist():
    return [dict(r, status="missing") for r in RECORDS]

def mark_record(items, record_id, status):
    s = norm(status).strip().lower()
    if s not in ("missing", "have", "needs_update", "not_applicable"): raise ValueError("status must be one of: missing, have, needs_update, not_applicable")
    for r in items:
        if r["id"] == record_id: r["status"] = s; return items
    raise KeyError(f"No record '{record_id}'. Valid ids: " + ", ".join(r["id"] for r in items))

def board_summary(hoa, today=None):
    h = _h(hoa); today = today or date.today()
    L = [f"# Compliance desk: {md_escape(h['name'])}", ""]
    if h["demo"]: L += ["**DEMO CONTENT. Numbers are made up for practice.**", ""]
    L += ["## Notice rules your board saved"] + ([f"- {md_escape(r['label'])}: {r['days_before']} days before. Source: {md_escape(r['source'])}" for r in h["rules"]] or ["- None yet."])
    L += ["", "## Coming up (next 120 days)"]
    for u in upcoming(h, today):
        L.append(f"- {u['due']}: {md_escape(u['label'])}" + (f" (${u['amount']:,.2f})" if u.get("amount") else "") + f", {u['status']}; remind on {u['remind_on']}" if u.get("due") else f"- {u['label']}")
    L += ["", f"_{DISCLAIMER}_"]
    return "\n".join(L)
