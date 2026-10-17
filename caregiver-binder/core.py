"""Caregiver Binder core: accounts (where to find them), documents (where they are), contacts, first-72-hours checklist.
Builds a printable binder in Markdown. Offline, stores nothing (your app keeps the 'binder').
NEVER stores secrets: it refuses passwords, PINs, codes, SSNs, card numbers and long account numbers. You record WHERE things are, not the things.
Not legal, medical, or financial advice."""
import re
from datetime import date
from safety import (norm, field, refuse_sensitive, md_escape, SensitiveDataError)

DISCLAIMER = "Organizing help only. Not legal, medical, or financial advice. This binder holds locations and contacts, never passwords or full account numbers. Keep the printed copy somewhere safe and tell your helper where it is."
ADVICE_Q = re.compile(r"\b(?:should (?:i|we|he|she)|is it (?:legal|ok|safe)|do i (?:need|have) to|can (?:i|we|they) (?:legally|sue)|what (?:medication|dose|dosage|treatment)|diagnos\w+|will (?:medicare|medicaid|insurance) (?:pay|cover)|how (?:do|should) i (?:invest|file taxes|probate)|power of attorney (?:rules|laws?)|probate|will and testament (?:rules|valid)|is (?:the|this) (?:will|poa|document) valid)\b", re.I)
ADVICE_MSG = "This binder organizes where things are and who to call. It can't give legal, medical, or financial advice. Ask the person's doctor, an elder-law attorney, or a financial professional."
ACCOUNT_TYPES = ("bank", "credit_card", "loan_mortgage", "insurance", "utility", "phone_internet", "email", "subscription", "social_media", "government", "retirement_investment", "other")
DOC_TYPES = ("will", "power_of_attorney", "healthcare_directive", "insurance_policy", "deed_title", "birth_marriage_certificate", "tax_returns", "medication_list", "id_card", "vehicle_title", "other")
KEPT = ("password manager", "paper in safe", "paper in file cabinet", "lawyer", "bank safe deposit box", "someone I trust", "other")

FIRST_72 = [
    {"when": "First hour", "id": "safe", "item": "Make sure everyone is safe. For an emergency, call your local emergency number first."},
    {"when": "First hour", "id": "breathe", "item": "Sit down, drink water. Write on paper: today's date, what happened, who you've called."},
    {"when": "First hour", "id": "contacts_call", "item": "Call the first 2 people on the Contacts list (the people to call first)."},
    {"when": "First 24 hours", "id": "docs_find", "item": "Find the binder, then the documents listed in it (will, health directive, power of attorney, policies)."},
    {"when": "First 24 hours", "id": "pets_kids", "item": "Arrange care for children, pets, and anyone else who depends on the person today."},
    {"when": "First 24 hours", "id": "meds", "item": "Find the medication list and give it to the doctor or hospital if needed."},
    {"when": "First 24 hours", "id": "work", "item": "Tell the person's employer or school (or yours) that you need time."},
    {"when": "First 24 hours", "id": "home", "item": "Secure the home: lock up, stop mail if needed, check food and the stove."},
    {"when": "First 72 hours", "id": "lawyer", "item": "Call the lawyer or advisor listed in the binder, if one is listed. Ask what they need from you."},
    {"when": "First 72 hours", "id": "bills", "item": "List bills due in the next 30 days from the Accounts list. Don't pay or cancel anything yet. Ask the lawyer or advisor first."},
    {"when": "First 72 hours", "id": "insurance", "item": "Call the insurance companies on the list to find out what steps they need."},
    {"when": "First 72 hours", "id": "log", "item": "Start a call log: date, who, what they said, what's next."},
    {"when": "First 72 hours", "id": "help", "item": "Ask one person to be your helper for errands and calls. Hand them this binder."},
    {"when": "First 72 hours", "id": "rest", "item": "Sleep and eat. The rest can wait for the next week."},
]

def scope_check(text):
    q = bool(ADVICE_Q.search(norm(text)))
    return {"is_advice_request": q, "message": ADVICE_MSG if q else "OK. This is an organizing question."}

def new_binder(person_name, prepared_by="", note=""):
    refuse_sensitive(person_name, prepared_by, note, secrets=True)
    return {"person": field(person_name, "person_name", 100, required=True), "prepared_by": field(prepared_by, "prepared_by", 100), "note": field(note, "note", 500),
            "accounts": [], "documents": [], "contacts": [], "checklist": [dict(c, done=False) for c in FIRST_72], "extra_steps": []}

def _b(b):
    if not isinstance(b, dict) or "person" not in b: raise ValueError("Pass the binder that new_binder() gave you.")
    for k in ("accounts", "documents", "contacts", "extra_steps"): b.setdefault(k, [])
    b.setdefault("checklist", [dict(c, done=False) for c in FIRST_72]); return b

def _choice(v, allowed, name):
    s = re.sub(r"[\s/&-]+", "_", norm(v).strip().lower())
    if s not in allowed: raise ValueError(f"{name} must be one of: " + ", ".join(allowed))
    return s

def add_account(binder, name, account_type, kept_where, last4="", contact_phone="", note=""):
    """name = 'First Bank checking'. kept_where = where the login is kept (NOT the login). last4 = last 4 digits only."""
    b = _b(binder); refuse_sensitive(name, kept_where, last4, note, secrets=True); refuse_phone(contact_phone)
    l4 = field(last4, "last4", 10)
    if l4 and not re.fullmatch(r"[A-Za-z0-9]{1,6}", l4): raise ValueError("last4 must be only the last few characters (up to 6), like 1234.")
    b["accounts"].append({"name": field(name, "name", 120, required=True), "type": _choice(account_type, ACCOUNT_TYPES, "account_type"), "last4": l4,
                          "login_kept": field(kept_where, "kept_where", 150, required=True), "phone": field(contact_phone, "contact_phone", 30), "note": field(note, "note", 300)}); return b

def refuse_phone(p):
    p = norm(p).strip()
    if not p: return
    if len(re.sub(r"\D", "", p)) > 15 or re.search(r"[A-Za-z]{4,}", p): raise ValueError("contact_phone should look like 555-123-4567.")
    refuse_sensitive(p)

def add_document(binder, name, doc_type, location, held_by="", note=""):
    b = _b(binder); refuse_sensitive(name, location, held_by, note, secrets=True)
    b["documents"].append({"name": field(name, "name", 120, required=True), "type": _choice(doc_type, DOC_TYPES, "doc_type"), "location": field(location, "location", 200, required=True),
                           "held_by": field(held_by, "held_by", 120), "note": field(note, "note", 300)}); return b

def add_contact(binder, name, role, phone="", email="", call_first=False, note=""):
    b = _b(binder); refuse_sensitive(name, role, email, note, secrets=True); refuse_phone(phone)
    em = field(email, "email", 120)
    if em and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", em): raise ValueError("email doesn't look right (like name@example.com).")
    ph = field(phone, "phone", 30)
    if not ph and not em: raise ValueError("Give a phone number or an email so there is a way to reach them.")
    b["contacts"].append({"name": field(name, "name", 100, required=True), "role": field(role, "role", 100, required=True), "phone": ph, "email": em, "call_first": bool(call_first), "note": field(note, "note", 300)}); return b

def add_step(binder, text, when="First 72 hours"):
    b = _b(binder); refuse_sensitive(text, secrets=True)
    w = norm(when).strip()
    if w not in ("First hour", "First 24 hours", "First 72 hours"): raise ValueError("when must be: First hour, First 24 hours, or First 72 hours")
    b["checklist"].append({"when": w, "id": f"custom{len(b['extra_steps'])+1}", "item": field(text, "text", 300, required=True), "done": False}); b["extra_steps"].append(text); return b

def tick(binder, step_id, done=True):
    for c in _b(binder)["checklist"]:
        if c["id"] == step_id: c["done"] = bool(done); return binder
    raise KeyError(f"No step '{step_id}'. Valid ids: " + ", ".join(c["id"] for c in binder["checklist"]))

def gaps(binder):
    b = _b(binder); g = []
    if not any(c["call_first"] for c in b["contacts"]): g.append("No 'call first' contact is marked. Mark at least two people.")
    elif sum(c["call_first"] for c in b["contacts"]) < 2: g.append("Only one 'call first' contact. Add a backup.")
    have = {d["type"] for d in b["documents"]}
    for t, label in (("will", "a will"), ("power_of_attorney", "a power of attorney"), ("healthcare_directive", "a health care directive"), ("medication_list", "a medication list")):
        if t not in have: g.append(f"No document listed for {label}. If none exists, that's useful to know too. Write 'none yet' in a note.")
    if not b["accounts"]: g.append("No accounts listed yet.")
    if not any(a["type"] == "email" for a in b["accounts"]): g.append("No email account listed. Many other accounts reset through email.")
    if not any(a["type"] == "phone_internet" for a in b["accounts"]): g.append("No phone account listed.")
    for a in b["accounts"]:
        if a["login_kept"].lower() == "other": g.append(f"'{a['name']}': 'other' for where the login is kept. Be more specific.")
    return g

def to_markdown(binder, today=None):
    b = _b(binder); today = today or date.today()
    L = [f"# Caregiver binder: {md_escape(b['person'])}", f"Prepared {today.isoformat()}" + (f" by {md_escape(b['prepared_by'])}" if b["prepared_by"] else ""), ""]
    if b["note"]: L += [md_escape(b["note"]), ""]
    L += ["> This binder shows WHERE things are. It holds no passwords, PINs, or full account numbers.", "", "## Who to call", ""]
    cs = sorted(b["contacts"], key=lambda c: (not c["call_first"], c["name"].lower()))
    L += (["| Name | Role | Phone | Email | Note |", "|---|---|---|---|---|"] + [f"| {'**CALL FIRST** ' if c['call_first'] else ''}{md_escape(c['name'])} | {md_escape(c['role'])} | {md_escape(c['phone']) or '-'} | {md_escape(c['email']) or '-'} | {md_escape(c['note'])} |" for c in cs]) if cs else ["None listed yet."]
    L += ["", "## Documents (where they are)", ""]
    L += (["| Document | Type | Where | Held by |", "|---|---|---|---|"] + [f"| {md_escape(d['name'])} | {d['type'].replace('_',' ')} | {md_escape(d['location'])} | {md_escape(d['held_by']) or '-'} |" for d in b["documents"]]) if b["documents"] else ["None listed yet."]
    L += ["", "## Accounts (where the login is kept)", ""]
    L += (["| Account | Type | Ends in | Login kept | Phone |", "|---|---|---|---|---|"] + [f"| {md_escape(a['name'])} | {a['type'].replace('_',' ')} | {md_escape(a['last4']) or '-'} | {md_escape(a['login_kept'])} | {md_escape(a['phone']) or '-'} |" for a in b["accounts"]]) if b["accounts"] else ["None listed yet."]
    L += ["", "## First 72 hours"]
    cur = None
    for c in b["checklist"]:
        if c["when"] != cur: cur = c["when"]; L += ["", f"**{cur}**"]
        L.append(f"- [{'x' if c['done'] else ' '}] {md_escape(c['item'])}")
    g = gaps(b); L += ["", "## Still to fill in"] + ([f"- {x}" for x in g] if g else ["- Nothing flagged."]) + ["", f"_{DISCLAIMER}_"]
    return "\n".join(L)
