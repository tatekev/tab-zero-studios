"""CPA Doc Prep core: checklist + tracker + draft message to a preparer.
Organizes paperwork only. Never computes tax or gives tax advice. Sample data only; never store full SSNs/card numbers."""
import re, unicodedata

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
SSN = re.compile(r"(?<![\d-])\d{3}[-.\s]{0,3}\d{2}[-.\s]{0,3}\d{4}(?![\d-])")
CARD = re.compile(r"(?<![\d-])(?:\d{4}[ .-]){3}\d{1,7}(?![\d-])|(?<![\d-])\d{4}[ .-]\d{6}[ .-]\d{5}(?![\d-])|(?<![\d-])\d{13,19}(?![\d-])")
STATUSES = ("missing", "received", "sent_to_preparer", "not_applicable")
CHANNELS = ("email", "text")
MAX_NOTE = 2000
TAX_QUESTION = re.compile(r"\b(?:calculate|compute|estimate|figure out|work out)\b[^.?!]{0,30}\b(?:tax(?:es)?|refund|owe|deduction)\b|\bwhat (?:do|did|would|will) i owe\b|\b(?:tax bracket|deductible|tax credit)\b|\bdo i (?:qualify|need to file|have to file|need to pay)\b|\bam i (?:allowed|supposed) to\b|\bcan i (?:file|claim)\b|\b(?:how much|what(?:'s| is| will)?)\b[^.?!]{0,40}\b(?:tax(?:es)?|refund|owe|deduct\w*)\b|\bwill i (?:owe|get a refund)\b|\bshould i (?:itemi[sz]e|deduct|claim|file)\b|\bcan i (?:deduct|write off|claim)\b|\bam i (?:eligible|required)\b|\bhow much (?:do|will) i owe\b", re.I)
ADVICE_MSG = "This tool only organizes tax paperwork. It can't work out what you owe or give tax advice. Ask your tax preparer."

def _norm(text):
    t = unicodedata.normalize("NFKC", text if isinstance(text, str) else ("" if text is None else str(text)))
    return "".join(c for c in t if c in "\n\t" or unicodedata.category(c) not in ("Cc", "Cf", "Co", "Cs"))

_DASHES = dict.fromkeys(map(ord, "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\ufe58\ufe63\uff0d"), "-")
# Loose patterns catch disguised numbers: "1 2 3 - 4 5 - 6 7 8 9", "123/45/6789", "123_45_6789"
_SEP = r"[\s\-./_]{0,3}"
_LB = r"(?<!\d)(?<!\d[\s\-./_])(?<!\d[\s\-./_]{2})(?<!\d[\s\-./_]{3})"
_LA = r"(?![\s\-./_]{0,3}\d)"   # not part of a longer digit run, so lists of dates are left alone
LOOSE_SSN = re.compile(_LB + r"(?:\d" + _SEP + r"){8}\d" + _LA)
LOOSE_CARD = re.compile(_LB + r"(?:\d" + _SEP + r"){12,18}\d" + _LA)

def _hide_numbers(t):
    t = t.translate(_DASHES)
    return t

def _profile_key(p):
    return re.sub(r"[\s-]+", "_", _norm(p).strip().lower())

def build_checklist(profiles):
    if isinstance(profiles, str):
        profiles = [profiles]
    if not profiles:
        raise ValueError("Pick at least one profile: " + ", ".join(PROFILES))
    keys, bad = [], []
    for p in profiles:
        pk = _profile_key(p)
        if pk not in PROFILES:
            bad.append(str(p)); continue
        for k in PROFILES[pk]:
            if k not in keys:
                keys.append(k)
    if bad:
        raise ValueError("Unknown profile: " + ", ".join(bad) + ". Valid profiles: " + ", ".join(PROFILES))
    return [{"id": k, "item": CATALOG[k][0], "usually_from": CATALOG[k][1], "status": "missing"} for k in keys]

def update_status(checklist, item_id, status):
    status = _profile_key(status)
    if status not in STATUSES:
        raise ValueError("Status must be one of: " + ", ".join(STATUSES))
    for c in checklist:
        if c["id"] == item_id:
            c["status"] = status
            return checklist
    raise KeyError(f"No checklist item '{item_id}'. Valid ids: " + ", ".join(c["id"] for c in checklist))

def summary(checklist):
    out = {s: [] for s in STATUSES}
    for c in checklist:
        out.setdefault(c["status"], []).append(c["item"])
    out["counts"] = {s: len(out[s]) for s in STATUSES}
    return out

def sensitive_check(text):
    """Flag full SSN / card numbers so they are never put in a draft. Never echoes the number."""
    t = _hide_numbers(_norm(text))
    has_card = bool(CARD.search(t) or LOOSE_CARD.search(t))
    has_ssn = bool(SSN.search(t) or LOOSE_SSN.search(t))
    red = t
    if has_ssn or has_card:
        for rx in (CARD, LOOSE_CARD, SSN, LOOSE_SSN):
            red = rx.sub("[removed]", red)
    msg = ("Looks like a full SSN or card number. Don't paste it here. Share it only by your preparer's secure portal, or use the last 4 digits." if (has_ssn or has_card) else "No full SSN or card number found.")
    return {"has_ssn": has_ssn, "has_card": has_card, "safe": not (has_ssn or has_card), "message": msg, "redacted_text": red,
            "looks_like_tax_question": bool(TAX_QUESTION.search(t))}

def scope_check(text):
    """Tell the user when they ask for tax advice / amounts; this tool never answers those."""
    q = bool(TAX_QUESTION.search(_norm(text)))
    return {"is_tax_advice_request": q, "message": ADVICE_MSG if q else "OK. This is a paperwork question."}

def draft_message(checklist, preparer="your preparer", sender="me", channel="email", note=""):
    channel = _profile_key(channel)
    if channel not in CHANNELS:
        raise ValueError("channel must be 'email' or 'text'")
    fields = [preparer, sender, note] + [str(c.get(k, "")) for c in checklist for k in ("item", "usually_from", "id")]
    for f in fields:
        r = sensitive_check(f)
        if not r["safe"]:
            raise ValueError("Remove SSN or card numbers first. Send those only by a secure portal, or use the last 4 digits.")
    preparer, sender, note = _norm(preparer).strip() or "your preparer", _norm(sender).strip() or "me", _norm(note).strip()
    long_note = len(note) > MAX_NOTE
    note = note[:MAX_NOTE]
    sent = [c["item"] for c in checklist if c.get("status") in ("received", "sent_to_preparer")]
    missing = [c["item"] for c in checklist if c.get("status") == "missing"]
    warnings = []
    if long_note:
        warnings.append(f"Your note was longer than {MAX_NOTE} characters, so it was cut off. Send the rest to your preparer yourself.")
    if TAX_QUESTION.search(note):
        warnings.append(ADVICE_MSG + " Your note is included only as a question for your preparer.")
    if channel == "email":
        lines = [(f"Hi {preparer}," if preparer != "your preparer" else "Hi,"), ""]
        if sent: lines += ["I have these ready for you:"] + [f"- {i}" for i in sent] + [""]
        if missing: lines += ["Still waiting on:"] + [f"- {i}" for i in missing] + [""]
        if note: lines += [note, ""]
        lines += ["Please tell me if anything else is needed, and how you want me to send it securely.", "", f"Thanks, {sender}"]
        body = "\n".join(lines)
    else:
        parts = [f"Hi {preparer}."]
        if sent: parts.append("Ready for you: " + "; ".join(sent) + ".")
        if missing: parts.append("Still waiting on: " + "; ".join(missing) + ".")
        if note: parts.append(note)
        parts.append(f"How should I send these securely? Thanks, {sender}")
        body = " ".join(parts)
    return {"channel": channel, "draft": body, "warnings": warnings,
            "note": "Draft only. Nothing was sent. You review and press send. This is not tax advice."}
