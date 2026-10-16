"""CPA Doc Prep core: checklist + tracker + draft message to a preparer.
Organizes paperwork only. Never computes tax or gives tax advice. Sample data only; never store full SSNs/card numbers."""
import re

CATALOG = {
    "w2": ("W-2 from each employer", "Employer, by Jan 31"),
    "1099_int": ("1099-INT (bank interest)", "Bank"),
    "1099_div": ("1099-DIV (dividends)", "Brokerage"),
    "1099_b": ("1099-B / consolidated 1099 (brokerage sales)", "Brokerage, often late Feb to March"),
    "1099_nec": ("1099-NEC / 1099-K (self-employed or side income)", "Payer or platform"),
    "k1": ("Schedule K-1 (partnership, S-corp, trust)", "Entity or its preparer, often March to September"),
    "1098": ("Form 1098 (mortgage interest)", "Lender"),
    "property_tax": ("Property tax statement", "County"),
    "1095": ("Form 1095 (health coverage)", "Insurer or employer"),
    "childcare": ("Childcare provider name, address and total paid", "Provider"),
    "estimated": ("Estimated tax payments made (dates and amounts)", "Your bank records"),
    "last_return": ("Last year's return", "Your files"),
    "id": ("Photo ID and dependents' info (last 4 of SSN only in chat)", "Your files"),
}
PROFILES = {
    "employee": ["w2", "1099_int", "1098", "property_tax", "1095", "last_return", "id"],
    "investor": ["1099_int", "1099_div", "1099_b", "k1", "last_return"],
    "self_employed": ["1099_nec", "estimated", "last_return", "id"],
    "parent": ["childcare", "1095", "id"],
    "homeowner": ["1098", "property_tax"],
}
SSN = re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b")
CARD = re.compile(r"\b(?:\d[ -]?){13,16}\b")

def build_checklist(profiles):
    keys = []
    for p in profiles:
        for k in PROFILES.get(p.lower(), []):
            if k not in keys:
                keys.append(k)
    return [{"id": k, "item": CATALOG[k][0], "usually_from": CATALOG[k][1], "status": "missing"} for k in keys]

def update_status(checklist, item_id, status):
    if status not in ("missing", "received", "sent_to_preparer", "not_applicable"):
        raise ValueError("bad status")
    for c in checklist:
        if c["id"] == item_id:
            c["status"] = status
            return checklist
    raise KeyError(item_id)

def summary(checklist):
    out = {}
    for c in checklist:
        out.setdefault(c["status"], []).append(c["item"])
    return out

def sensitive_check(text):
    """Flag full SSN / card numbers so they are never put in a draft."""
    return {"has_ssn": bool(SSN.search(text)), "has_card": bool(CARD.search(text))}

def draft_message(checklist, preparer="your preparer", sender="me", channel="email", note=""):
    if sensitive_check(note)["has_ssn"] or sensitive_check(note)["has_card"]:
        raise ValueError("Remove SSN or card numbers from the note. Send those by a secure portal.")
    sent = [c["item"] for c in checklist if c["status"] in ("received", "sent_to_preparer")]
    missing = [c["item"] for c in checklist if c["status"] == "missing"]
    lines = [f"Hi {preparer},", ""]
    if sent:
        lines += ["I have these ready for you:"] + [f"- {i}" for i in sent] + [""]
    if missing:
        lines += ["Still waiting on:"] + [f"- {i}" for i in missing] + [""]
    if note:
        lines += [note, ""]
    lines += ["Please tell me if anything else is needed, and how you want me to send it securely.", "", f"Thanks, {sender}"]
    body = "\n".join(lines)
    if channel == "text":
        body = body.replace("\n- ", "; ").replace("\n\n", " ")
    return {"channel": channel, "draft": body, "note": "Draft only. You review and press send. This is not tax advice."}
