"""Gig Tax Organizer core: quarterly date reminders, mileage log, receipt log, estimated-payment log, year-end handoff packet.
ORGANIZES ONLY. Never computes tax, deductions, mileage-rate values, or what you owe. Offline, stores nothing:
your app keeps the 'book' between calls (or use the CSV export). Sample data only; no SSNs or card numbers."""
import csv, io, re
from datetime import date, timedelta
from safety import (norm, field, parse_date, refuse_sensitive, money, status_for, md_escape, csv_safe, SensitiveDataError)

CATEGORIES = ["supplies", "phone_internet", "software_subscriptions", "vehicle_costs", "parking_tolls", "equipment",
              "advertising", "fees_platform", "meals", "travel", "education", "professional_services", "other"]
INCOME_SOURCES_NOTE = "Enter each payment you were paid, as shown on the platform's statement. This tool only adds up what you type."
DISCLAIMER = "Organizing only. This tool does not work out tax, deductions, or what you owe, and it is not tax advice. Your preparer decides what counts."
TAX_Q = re.compile(r"\b(?:how much|what(?:'s| is| will)?)\b[^.?!]{0,40}\b(?:tax(?:es)?|refund|owe|deduct\w*|write[- ]?off|mileage rate|per mile)\b|\bwill i (?:owe|get a refund)\b|\bshould i (?:itemi[sz]e|deduct|claim|file|pay)\b|\bcan i (?:deduct|write off|claim)\b|\bis (?:this|it|my \w+) (?:deductible|tax[- ]deductible)\b|\bdo i (?:owe|need to pay|have to pay)\b|\bhow much (?:do|will) i owe\b|\bcalculate\b[^.?!]{0,30}\btax", re.I)
ADVICE_MSG = "This tool only organizes records. It can't work out tax, deductions, or what you owe. Ask your tax preparer."

def scope_check(text):
    q = bool(TAX_Q.search(norm(text)))
    return {"is_tax_advice_request": q, "message": ADVICE_MSG if q else "OK. This is a records question."}

def new_book(tax_year, name="", note=""):
    y = int(str(tax_year).strip()) if re.fullmatch(r"\s*\d{4}\s*", str(tax_year)) else None
    if y is None or not (2000 <= y <= 2100): raise ValueError("tax_year must be a 4-digit year like 2026.")
    refuse_sensitive(name, note)
    return {"tax_year": y, "name": field(name, "name", 100), "note": field(note, "note", 500), "trips": [], "receipts": [], "income": [], "payments": [], "due_dates": []}

def _book(book):
    if not isinstance(book, dict) or "tax_year" not in book:
        raise ValueError("Pass the book that new_book() gave you.")
    for k in ("trips", "receipts", "income", "payments", "due_dates"): book.setdefault(k, [])
    return book

def usual_dates(tax_year):
    """The widely published usual calendar dates for U.S. federal estimated payments. SUGGESTION ONLY:
    they move for weekends/holidays and differ by state. Always confirm on IRS.gov or with your preparer."""
    y = int(tax_year)
    raw = [(f"Q1 (Jan-Mar income)", date(y, 4, 15)), ("Q2 (Apr-May income)", date(y, 6, 15)), ("Q3 (Jun-Aug income)", date(y, 9, 15)), ("Q4 (Sep-Dec income)", date(y + 1, 1, 15))]
    out = []
    for label, d in raw:
        wk = d.weekday() >= 5
        out.append({"label": label, "usual_date": d.isoformat(), "weekend": wk,
                    "note": "Falls on a weekend; the real due date is usually the next business day. Confirm." if wk else "Usual date. Confirm on IRS.gov or with your preparer.",
                    "confirmed": False})
    return out

def set_due_dates(book, items):
    """items: list of {label, date}. You type the dates you confirmed with IRS.gov or your preparer."""
    b = _book(book)
    if not items: raise ValueError("Give at least one {label, date}.")
    new = []
    for it in items:
        label = field(it.get("label"), "label", 80, required=True); refuse_sensitive(label)
        new.append({"label": label, "date": parse_date(it.get("date"), "date").isoformat()})
    b["due_dates"] = new
    return b

def reminders(book, today=None):
    b = _book(book); today = today or date.today()
    if not b["due_dates"]:
        return [{"label": "No dates saved yet", "date": None, "status": "no date",
                 "tip": "Call set_due_dates with dates you confirmed. Tip: usual_dates() lists the usual ones to check."}]
    out = []
    for d in sorted(b["due_dates"], key=lambda x: x["date"]):
        dd = parse_date(d["date"]); n = (dd - today).days
        out.append({"label": d["label"], "date": d["date"], "days": n, "status": status_for(n)})
    return out

def add_trip(book, trip_date, miles, purpose, start="", end="", note=""):
    b = _book(book); refuse_sensitive(purpose, start, end, note)
    m = money(miles, "miles")
    if m <= 0 or m > 3000: raise ValueError("miles must be more than 0 and at most 3000 for one trip.")
    t = {"date": parse_date(trip_date, "date").isoformat(), "miles": m, "purpose": field(purpose, "purpose", 200),
         "start": field(start, "start", 200), "end": field(end, "end", 200), "note": field(note, "note", 300)}
    b["trips"].append(t); return b

def add_receipt(book, receipt_date, vendor, amount, category="other", note="", has_photo=False):
    b = _book(book); refuse_sensitive(vendor, note)
    cat = re.sub(r"[\s-]+", "_", norm(category).strip().lower())
    if cat not in CATEGORIES: raise ValueError("category must be one of: " + ", ".join(CATEGORIES))
    r = {"date": parse_date(receipt_date, "date").isoformat(), "vendor": field(vendor, "vendor", 120, required=True),
         "amount": money(amount, "amount"), "category": cat, "note": field(note, "note", 300), "has_photo": bool(has_photo)}
    b["receipts"].append(r); return b

def add_income(book, pay_date, source, amount, note=""):
    b = _book(book); refuse_sensitive(source, note)
    b["income"].append({"date": parse_date(pay_date, "date").isoformat(), "source": field(source, "source", 120, required=True),
                        "amount": money(amount, "amount"), "note": field(note, "note", 300)})
    return b

def add_payment(book, pay_date, label, amount, confirmation_last4=""):
    """Log an estimated payment you already made."""
    b = _book(book); refuse_sensitive(label, confirmation_last4)
    c = field(confirmation_last4, "confirmation_last4", 10)
    if c and not re.fullmatch(r"[A-Za-z0-9]{1,6}", c): raise ValueError("confirmation_last4 must be up to 6 letters/digits (last digits only).")
    b["payments"].append({"date": parse_date(pay_date, "date").isoformat(), "label": field(label, "label", 80, required=True),
                          "amount": money(amount, "amount"), "confirmation_last4": c})
    return b

def totals(book):
    """Adds up what YOU typed. These are entry totals, not deductions or tax."""
    b = _book(book)
    by_cat = {}
    for r in b["receipts"]: by_cat[r["category"]] = round(by_cat.get(r["category"], 0) + r["amount"], 2)
    return {"trip_count": len(b["trips"]), "miles_logged": round(sum(t["miles"] for t in b["trips"]), 1),
            "receipt_count": len(b["receipts"]), "receipts_by_category": by_cat,
            "receipts_total_entered": round(sum(r["amount"] for r in b["receipts"]), 2),
            "income_entries": len(b["income"]), "income_total_entered": round(sum(i["amount"] for i in b["income"]), 2),
            "payments_logged": len(b["payments"]), "payments_total_entered": round(sum(p["amount"] for p in b["payments"]), 2),
            "note": "Totals of what you entered. Not deductions, not tax. " + DISCLAIMER}

def gaps(book):
    """Things a preparer will ask about. Nothing here judges deductibility."""
    b = _book(book); g = []
    y = b["tax_year"]
    for i, t in enumerate(b["trips"], 1):
        if not t["purpose"]: g.append(f"Trip {i} ({t['date']}): no purpose written.")
        if not t["start"] or not t["end"]: g.append(f"Trip {i} ({t['date']}): start or end place missing.")
    for i, r in enumerate(b["receipts"], 1):
        if not r["has_photo"]: g.append(f"Receipt {i} ({r['vendor']}, {r['date']}): no photo or copy marked.")
        if r["category"] == "other": g.append(f"Receipt {i} ({r['vendor']}): category is 'other'. Ask your preparer where it goes.")
    for coll, nm in (("trips", "Trip"), ("receipts", "Receipt"), ("income", "Income"), ("payments", "Payment")):
        for i, x in enumerate(b[coll], 1):
            if parse_date(x["date"]).year not in (y, y + 1 if coll == "payments" else y):
                g.append(f"{nm} {i} ({x['date']}): date is outside {y}. Check it.")
    seen = {}
    for i, r in enumerate(b["receipts"], 1):
        k = (r["date"], r["vendor"].lower(), r["amount"])
        if k in seen: g.append(f"Receipt {i} looks the same as receipt {seen[k]} (same date, vendor, amount). Possible double entry.")
        seen.setdefault(k, i)
    if not b["income"]: g.append("No income entries yet.")
    return g

def to_csv(book, which):
    b = _book(book)
    cols = {"trips": ["date", "miles", "purpose", "start", "end", "note"], "receipts": ["date", "vendor", "amount", "category", "note", "has_photo"],
            "income": ["date", "source", "amount", "note"], "payments": ["date", "label", "amount", "confirmation_last4"]}
    if which not in cols: raise ValueError("which must be one of: " + ", ".join(cols))
    s = io.StringIO(); w = csv.writer(s, lineterminator="\n"); w.writerow(cols[which])
    for r in b[which]: w.writerow([csv_safe(r.get(c, "")) if isinstance(r.get(c, ""), str) else r.get(c, "") for c in cols[which]])
    return s.getvalue()

def from_csv(book, which, text):
    """Load rows from a CSV you filled in (same headers as to_csv). Every row is checked like a typed entry."""
    b = _book(book); refuse_sensitive(text)
    rows = list(csv.DictReader(io.StringIO(norm(text))))
    if len(rows) > 5000: raise ValueError("Too many rows (max 5000).")
    for n, r in enumerate(rows, 2):
        try:
            if which == "trips": add_trip(b, r.get("date"), r.get("miles"), r.get("purpose", ""), r.get("start", ""), r.get("end", ""), r.get("note", ""))
            elif which == "receipts": add_receipt(b, r.get("date"), r.get("vendor"), r.get("amount"), r.get("category") or "other", r.get("note", ""), str(r.get("has_photo", "")).strip().lower() in ("true", "yes", "1", "y"))
            elif which == "income": add_income(b, r.get("date"), r.get("source"), r.get("amount"), r.get("note", ""))
            elif which == "payments": add_payment(b, r.get("date"), r.get("label"), r.get("amount"), r.get("confirmation_last4", ""))
            else: raise ValueError("which must be trips, receipts, income, or payments")
        except SensitiveDataError: raise
        except ValueError as e: raise ValueError(f"CSV row {n}: {e}")
    return b

def handoff_packet(book, preparer="your preparer", today=None):
    """A one-page Markdown packet to give a tax preparer. Facts you entered only. No tax math."""
    b = _book(book); t = totals(b); today = today or date.today()
    refuse_sensitive(preparer); preparer = field(preparer, "preparer", 100) or "your preparer"
    L = [f"# Year-end packet for {md_escape(preparer)}: tax year {b['tax_year']}", f"Prepared {today.isoformat()}" + (f" for {md_escape(b['name'])}" if b["name"] else ""), "",
         "_Organized records only. No tax has been calculated. Please tell me what else you need and how to send it securely._", "",
         "## Income entered", f"{t['income_entries']} entries, total entered: ${t['income_total_entered']:,.2f}"]
    if b["income"]:
        L += ["", "| Date | Source | Amount |", "|---|---|---|"] + [f"| {i['date']} | {md_escape(i['source'])} | ${i['amount']:,.2f} |" for i in sorted(b["income"], key=lambda x: x["date"])]
    L += ["", "## Mileage log", f"{t['trip_count']} trips, {t['miles_logged']} miles logged"]
    if b["trips"]:
        L += ["", "| Date | Miles | Purpose | From | To |", "|---|---|---|---|---|"] + [f"| {x['date']} | {x['miles']} | {md_escape(x['purpose'])} | {md_escape(x['start'])} | {md_escape(x['end'])} |" for x in sorted(b["trips"], key=lambda x: x["date"])]
    L += ["", "## Receipts", f"{t['receipt_count']} receipts, total entered: ${t['receipts_total_entered']:,.2f}"]
    if t["receipts_by_category"]:
        L += ["", "| Category | Total entered |", "|---|---|"] + [f"| {c.replace('_',' ')} | ${v:,.2f} |" for c, v in sorted(t["receipts_by_category"].items())]
        L += ["", "| Date | Vendor | Amount | Category | Photo |", "|---|---|---|---|---|"] + [f"| {r['date']} | {md_escape(r['vendor'])} | ${r['amount']:,.2f} | {r['category'].replace('_',' ')} | {'yes' if r['has_photo'] else 'no'} |" for r in sorted(b["receipts"], key=lambda x: x["date"])]
    L += ["", "## Estimated payments I logged", f"{t['payments_logged']} payments, total entered: ${t['payments_total_entered']:,.2f}"]
    if b["payments"]:
        L += ["", "| Date | Label | Amount | Confirmation (last digits) |", "|---|---|---|---|"] + [f"| {p['date']} | {md_escape(p['label'])} | ${p['amount']:,.2f} | {md_escape(p['confirmation_last4']) or '-'} |" for p in sorted(b["payments"], key=lambda x: x["date"])]
    g = gaps(b)
    L += ["", "## Questions for you / gaps I noticed"] + ([f"- {x}" for x in g] if g else ["- None found by the checker."])
    L += ["", "## Also bringing", "- Platform year-end statements and any 1099-NEC / 1099-K forms", "- Last year's return", "", f"_{DISCLAIMER}_"]
    return "\n".join(L)
