"""Medical Bill & Appeal Kit core: bill checklist, itemized-bill request letter, appeal letter template, deadline tracker.
Drafts only; nothing is sent. Offline, stores nothing (your app keeps the 'case'). No medical or legal advice.
Deadlines come ONLY from what you type from your own letters (with where you found it). Never invented."""
import re
from datetime import date
from safety import (norm, field, parse_date, add_days, positive_int, refuse_sensitive, status_for, md_escape, SensitiveDataError, LONG_ACCT)

DISCLAIMER = "Paperwork help only. Not medical, legal, or insurance advice, and not a promise of any result. Check every date and number against your own letters."
SCOPE_Q = re.compile(r"\b(?:should i|do i need to|can i|is it safe to|is it ok to|will it|can they|do they have to|is (?:this|it|that) (?:bill |charge |denial )?(?:legal|illegal|allowed|covered|a scam|fraud|medically)|am i (?:covered|liable|required|entitled)|will (?:my|the) (?:insurance|claim|appeal) (?:pay|win|work|be approved)|can i sue|should i sue)\b[^.?!]{0,80}|\b(?:diagnos\w+|dosage|medication|treatment|symptom\w*|prescri\w+|sue|lawsuit|lawyer|attorney)\b", re.I)
ADVICE_MSG = "This kit organizes bill and appeal paperwork. It can't give medical or legal advice or say whether you'll win. For that, ask your provider's billing office, your insurer, a patient advocate, or a lawyer."

BILL_CHECKLIST = [
    {"id": "itemized", "item": "I have an ITEMIZED bill (every charge listed with a code), not just a total.", "why": "A total tells you nothing. Line items let you spot errors."},
    {"id": "eob", "item": "I have the Explanation of Benefits (EOB) from my insurer for the same visit.", "why": "The EOB says what the insurer paid and what it says you owe. The bill should match it."},
    {"id": "match_dates", "item": "The dates of service on the bill match the dates I actually had care.", "why": "Wrong dates are a common mix-up."},
    {"id": "match_provider", "item": "Every provider and facility listed is one I actually saw.", "why": "Check for charges from a place or person you don't recognize."},
    {"id": "duplicates", "item": "I checked for the same charge listed twice.", "why": "Duplicate lines happen."},
    {"id": "amounts_vs_eob", "item": "The 'you owe' amount on the bill matches the 'patient responsibility' on the EOB.", "why": "If they differ, ask which one is right, in writing."},
    {"id": "insurance_info", "item": "The insurance name and member info on the bill are correct (last 4 only).", "why": "Wrong insurance info can cause a denial."},
    {"id": "denial_reason", "item": "If a claim was denied, I wrote down the denial reason and any code printed in the letter.", "why": "The appeal needs to answer that exact reason."},
    {"id": "deadlines", "item": "I wrote down every deadline printed on the bill, EOB, or denial letter (and where I found it).", "why": "Appeal and payment windows are short. This kit never guesses them."},
    {"id": "financial_help", "item": "I asked the billing office whether they have a financial assistance or payment plan option.", "why": "You can ask. They may or may not offer one."},
    {"id": "hold", "item": "I asked the billing office to pause collections while I review (and wrote down who I asked and when).", "why": "Asking in writing leaves a record."},
    {"id": "records", "item": "I keep copies of everything I send and receive, plus a log of calls (date, name, what was said).", "why": "A paper trail helps in any later conversation."},
]

def checklist():
    return [dict(c, done=False) for c in BILL_CHECKLIST]

def mark_done(items, item_id, done=True):
    for c in items:
        if c["id"] == item_id: c["done"] = bool(done); return items
    raise KeyError(f"No checklist item '{item_id}'. Valid ids: " + ", ".join(c["id"] for c in items))

def scope_check(text):
    q = bool(SCOPE_Q.search(norm(text)))
    return {"is_advice_request": q, "message": ADVICE_MSG if q else "OK. This is a paperwork question."}

def new_case(patient_name, provider, insurer="", note=""):
    refuse_sensitive(patient_name, provider, insurer, note, secrets=True)
    return {"patient_name": field(patient_name, "patient_name", 100, required=True), "provider": field(provider, "provider", 150, required=True),
            "insurer": field(insurer, "insurer", 150), "note": field(note, "note", 500), "deadlines": [], "log": []}

def _case(c):
    if not isinstance(c, dict) or "provider" not in c: raise ValueError("Pass the case that new_case() gave you.")
    c.setdefault("deadlines", []); c.setdefault("log", []); return c

def add_deadline(case, label, source, start_date=None, days=None, exact_date=None):
    """Two ways: exact_date (a date printed on your letter) OR start_date + days (e.g. 'within 180 days of this letter').
    'source' is REQUIRED: where you read it (e.g. 'denial letter, page 2'). No source, no deadline."""
    c = _case(case); refuse_sensitive(label, source, secrets=True)
    label = field(label, "label", 100, required=True); source = field(source, "source", 200)
    if not source: raise ValueError("source is required: say where on your letter you read this deadline. This kit never guesses deadlines.")
    if exact_date and (start_date or days): raise ValueError("Give either exact_date, or start_date plus days. Not both.")
    if exact_date:
        due = parse_date(exact_date, "exact_date"); how = "date printed on letter"
    else:
        if not start_date or not days: raise ValueError("Give exact_date, or both start_date and days.")
        sd = parse_date(start_date, "start_date"); n = positive_int(days, "days")
        due = add_days(sd, n); how = f"{n} days from {sd.isoformat()} (as you typed)"
    c["deadlines"].append({"label": label, "due": due.isoformat(), "how": how, "source": source, "done": False}); return c

def finish_deadline(case, label):
    for d in _case(case)["deadlines"]:
        if d["label"] == label: d["done"] = True; return case
    raise KeyError(f"No deadline named '{label}'.")

def tracker(case, today=None):
    c = _case(case); today = today or date.today()
    if not c["deadlines"]:
        return [{"label": "No deadlines saved", "due": None, "status": "no date", "tip": "Find the dates on your bill, EOB, or denial letter and add them. This kit never guesses."}]
    out = []
    for d in sorted(c["deadlines"], key=lambda x: (x["done"], x["due"])):
        n = (parse_date(d["due"]) - today).days
        out.append({"label": d["label"], "due": d["due"], "status": "DONE" if d["done"] else status_for(n), "how": d["how"], "source": d["source"],
                    "confirm": "Double-check this against the letter." if not d["done"] else ""})
    return out

def log_contact(case, when, who, what):
    c = _case(case); refuse_sensitive(who, what, secrets=True)
    c["log"].append({"date": parse_date(when, "when").isoformat(), "who": field(who, "who", 120, required=True), "what": field(what, "what", 500, required=True)}); return c

def _id(v, name):
    v = field(v, name, 40)
    if v and re.search(r"\d{6,}", v): raise SensitiveDataError(f"{name}: use only the last 4 digits (like 'ending 1234'). Nothing was saved.")
    return v

def itemized_request_letter(case, date_of_service, sender_address="[YOUR ADDRESS]", account_last4="", today=None):
    c = _case(case); today = today or date.today()
    refuse_sensitive(sender_address, account_last4, secrets=True)
    dos = field(date_of_service, "date_of_service", 60, required=True)
    acct = _id(account_last4, "account_last4")
    ref = f"\nAccount reference: ending {re.sub(r'[^0-9A-Za-z]', '', acct)[-4:]}" if acct else "\nAccount reference: [LAST 4 DIGITS OF ACCOUNT NUMBER]"
    body = f"""{field(sender_address, 'sender_address', 300) or '[YOUR ADDRESS]'}

{today.strftime('%B %d, %Y').replace(' 0', ' ')}

To: Billing Department, {c['provider']}

Re: Request for an itemized bill
Patient: {c['patient_name']}
Date(s) of service: {dos}{ref}

Hello,

I am writing to ask for a complete itemized bill for the care listed above. Please include each charge on its own line with the date of service, the billing or procedure code, a description, and the amount.

Please also send:
- the name of each provider or facility that is billing for this visit, and
- a record of what has been paid, adjusted, or sent to insurance so far.

While I review the itemized bill, I ask that you pause any collections activity on this account, and please confirm in writing that you have done so.

Please send these records to the address above. If you need anything else from me, please let me know.

Thank you,
{c['patient_name']}

[DRAFT: review every line, add your signature, and send it yourself by a method you can prove, like certified mail. Keep a copy.]"""
    return {"draft": body, "note": "Draft only. Nothing was sent. " + DISCLAIMER}

def appeal_letter(case, claim_ref_last4, denial_date, denial_reason, why_wrong, attachments=None, sender_address="[YOUR ADDRESS]", today=None):
    """A template. denial_reason: copy it from your letter. why_wrong: YOUR words. The kit adds no facts or law."""
    c = _case(case); today = today or date.today()
    refuse_sensitive(claim_ref_last4, denial_reason, why_wrong, attachments or [], sender_address, secrets=True)
    ref = _id(claim_ref_last4, "claim_ref_last4")
    dd = parse_date(denial_date, "denial_date")
    reason = field(denial_reason, "denial_reason", 1000, required=True); why = field(why_wrong, "why_wrong", 2000, required=True)
    att = [field(a, "attachment", 120) for a in (attachments or []) if field(a, "attachment", 120)]
    to = c["insurer"] or c["provider"]
    L = [field(sender_address, "sender_address", 300) or "[YOUR ADDRESS]", "", today.strftime("%B %d, %Y").replace(" 0", " "), "",
         f"To: Appeals Department, {to}", "", "Re: Appeal of a denied or disputed claim", f"Patient: {c['patient_name']}",
         f"Provider: {c['provider']}", f"Claim reference: ending {ref[-4:]}" if ref else "Claim reference: [LAST 4 OF CLAIM NUMBER]",
         f"Date of the letter I am appealing: {dd.strftime('%B %d, %Y').replace(' 0', ' ')}", "", "Hello,", "",
         "I am writing to appeal the decision described in the letter above. I am asking for a full review.", "",
         f"The reason given in the letter was: \"{reason}\"", "", "I disagree because:", why, ""]
    L += (["I have attached:"] + [f"- {a}" for a in att]) if att else ["[LIST ATTACHMENTS: for example the denial letter, the EOB, and the itemized bill.]"]
    L += ["", "Please send me your written decision, and tell me the next steps if the decision stays the same.", "", "Thank you,", c["patient_name"], "",
          "[DRAFT: review it, add your signature, and send it yourself by a method you can prove. Keep a copy. Check the appeal deadline on your letter.]"]
    return {"draft": "\n".join(L), "note": "Draft only. Nothing was sent. This template adds no facts or legal claims; the reasons are your own words. " + DISCLAIMER}

def case_summary(case, today=None):
    c = _case(case); t = tracker(c, today)
    L = [f"# Bill case: {md_escape(c['provider'])}", f"Patient: {md_escape(c['patient_name'])}" + (f" | Insurer: {md_escape(c['insurer'])}" if c["insurer"] else ""), "", "## Deadlines"]
    L += [f"- **{md_escape(x['label'])}**: {x['due'] or 'none saved'} ({x['status']})" + (f", source: {md_escape(x['source'])}" if x.get("source") else "") for x in t]
    L += ["", "## Contact log"] + ([f"- {x['date']}: {md_escape(x['who'])}: {md_escape(x['what'])}" for x in c["log"]] or ["- Nothing logged yet."])
    L += ["", f"_{DISCLAIMER}_"]
    return "\n".join(L)
