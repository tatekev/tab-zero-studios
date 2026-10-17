"""Lease-End Deposit Packet core: move-in/move-out photo log, comparison, deadline tracker with YOUR state rules, demand-letter draft.
Drafts only; nothing is sent. Offline, stores nothing (your app keeps the 'packet'). Never states what any state's law says:
every deadline rule is typed in by you, with where you found it. Not legal advice."""
import re
from datetime import date
from safety import (norm, field, parse_date, add_days, positive_int, money, refuse_sensitive, status_for, md_escape, SensitiveDataError)

PHASES = ("move_in", "move_out")
CONDITIONS = ("good", "fair", "worn", "dirty", "damaged", "missing")
RANK = {c: i for i, c in enumerate(CONDITIONS)}
STARTS = {"move_out_date": "move-out date", "lease_end_date": "lease end date", "forwarding_address_date": "date you gave your forwarding address", "other": "another date you typed"}
DISCLAIMER = "Paperwork help only. Not legal advice. This tool does not know or state your state's or city's rules; every rule here is one you typed in. Check them against the official source or ask a tenant organization or lawyer."
LEGAL_Q = re.compile(r"\b(?:can (?:they|my landlord|the landlord|he|she)|is (?:it|this|that|my landlord) (?:legal|illegal|allowed|required|ok)|do (?:they|i|landlords?) (?:have to|need to)|how (?:many|long) days|what(?:'s| is| are) the (?:law|deadline|rule|limit)|(?:am i|are they) (?:entitled|required|liable)|should i (?:sue|withhold|stop paying)|can i (?:sue|withhold)|small claims|\bsue\b|lawsuit|double damages|treble|penalt(?:y|ies) (?:for|under)|normal wear)\b", re.I)
ADVICE_MSG = "This tool organizes your records and drafts a letter from rules you type in. It can't tell you what the law is or what you're allowed to do. Look at your state's official tenant page, a tenant union, legal aid, or a lawyer."

def scope_check(text):
    q = bool(LEGAL_Q.search(norm(text)))
    return {"is_advice_request": q, "message": ADVICE_MSG if q else "OK. This is a records question."}

def new_packet(tenant, landlord, property_address, move_in_date, move_out_date=None, deposit_amount=None, forwarding_address=""):
    refuse_sensitive(tenant, landlord, property_address, forwarding_address, secrets=True)
    p = {"tenant": field(tenant, "tenant", 100, required=True), "landlord": field(landlord, "landlord", 150, required=True),
         "property": field(property_address, "property_address", 300, required=True), "forwarding_address": field(forwarding_address, "forwarding_address", 300),
         "move_in": parse_date(move_in_date, "move_in_date").isoformat(), "move_out": None, "deposit": None, "photos": [], "rules": [], "deductions": [], "events": []}
    if move_out_date: p["move_out"] = parse_date(move_out_date, "move_out_date").isoformat()
    if p["move_out"] and p["move_out"] < p["move_in"]: raise ValueError("move_out_date is before move_in_date. Check both.")
    if deposit_amount not in (None, ""): p["deposit"] = money(deposit_amount, "deposit_amount")
    return p

def _p(p):
    if not isinstance(p, dict) or "tenant" not in p: raise ValueError("Pass the packet that new_packet() gave you.")
    for k in ("photos", "rules", "deductions", "events"): p.setdefault(k, [])
    return p

def set_move_out(packet, move_out_date):
    p = _p(packet); d = parse_date(move_out_date, "move_out_date")
    if d.isoformat() < p["move_in"]: raise ValueError("move_out_date is before move_in_date. Check both.")
    p["move_out"] = d.isoformat(); return p

def add_photo(packet, phase, room, item, condition, filename, taken_date, note=""):
    p = _p(packet); phase = re.sub(r"[\s-]+", "_", norm(phase).strip().lower()); cond = norm(condition).strip().lower()
    if phase not in PHASES: raise ValueError("phase must be move_in or move_out.")
    if cond not in CONDITIONS: raise ValueError("condition must be one of: " + ", ".join(CONDITIONS))
    refuse_sensitive(room, item, filename, note, secrets=True)
    fn = field(filename, "filename", 200)
    if "/" in fn or "\\" in fn: fn = re.split(r"[\\/]", fn)[-1]
    p["photos"].append({"phase": phase, "room": field(room, "room", 80, required=True).title(), "item": field(item, "item", 120, required=True).lower(),
                        "condition": cond, "filename": fn, "taken": parse_date(taken_date, "taken_date").isoformat(), "note": field(note, "note", 300)})
    return p

def compare(packet):
    """Match move-in and move-out photos by room+item. Says what changed; never says who is responsible or what is 'normal wear'."""
    p = _p(packet); idx = {"move_in": {}, "move_out": {}}
    for ph in p["photos"]: idx[ph["phase"]][(ph["room"], ph["item"])] = ph
    same, changed, only_in, only_out = [], [], [], []
    for k, a in sorted(idx["move_in"].items()):
        b = idx["move_out"].get(k)
        if not b: only_in.append({"room": k[0], "item": k[1], "tip": "No move-out photo yet."}); continue
        if RANK[b["condition"]] > RANK[a["condition"]]:
            changed.append({"room": k[0], "item": k[1], "move_in": a["condition"], "move_out": b["condition"], "move_in_photo": a["filename"], "move_out_photo": b["filename"], "move_out_note": b["note"]})
        else: same.append({"room": k[0], "item": k[1], "move_in": a["condition"], "move_out": b["condition"]})
    for k, b in sorted(idx["move_out"].items()):
        if k not in idx["move_in"]: only_out.append({"room": k[0], "item": k[1], "tip": "No move-in photo for this. Your records can't show the starting condition."})
    return {"same_or_better": same, "looks_worse_at_move_out": changed, "only_move_in_photo": only_in, "only_move_out_photo": only_out,
            "note": "'Looks worse' only compares the conditions you picked. It does not say who is responsible or what counts as normal wear. " + DISCLAIMER}

def add_rule(packet, label, days, starts, source, source_text=""):
    """YOU type the rule from an official source or your lease. source is REQUIRED (e.g. 'lease section 12' or 'my state's tenant page, URL').
    starts: move_out_date, lease_end_date, forwarding_address_date, or other."""
    p = _p(packet); refuse_sensitive(label, source, source_text, secrets=True)
    src = field(source, "source", 300)
    if not src: raise ValueError("source is required: say where you read this rule (lease section, official web page). This tool never supplies rules.")
    st = re.sub(r"[\s-]+", "_", norm(starts).strip().lower())
    if st not in STARTS: raise ValueError("starts must be one of: " + ", ".join(STARTS))
    p["rules"].append({"label": field(label, "label", 100, required=True), "days": positive_int(days, "days", 365), "starts": st, "source": src,
                       "source_text": field(source_text, "source_text", 500), "start_date": None}); return p

def set_event_date(packet, starts, when):
    p = _p(packet); st = re.sub(r"[\s-]+", "_", norm(starts).strip().lower())
    if st not in STARTS: raise ValueError("starts must be one of: " + ", ".join(STARTS))
    p["events"] = [e for e in p["events"] if e["key"] != st] + [{"key": st, "date": parse_date(when, "when").isoformat()}]; return p

def _start_for(p, st):
    if st == "move_out_date": return p["move_out"]
    for e in p["events"]:
        if e["key"] == st: return e["date"]
    return None

def tracker(packet, today=None):
    p = _p(packet); today = today or date.today()
    if not p["rules"]:
        return [{"label": "No rules saved", "due": None, "status": "no date", "tip": "Add the rule you found with add_rule (days + where you found it). This tool doesn't know your state's rules and won't guess."}]
    out = []
    for r in p["rules"]:
        s = _start_for(p, r["starts"])
        if not s:
            out.append({"label": r["label"], "due": None, "status": "no start date", "source": r["source"], "tip": f"Add the {STARTS[r['starts']]} (set_event_date, or set the move-out date) to see this deadline."}); continue
        due = add_days(parse_date(s), r["days"]); n = (due - today).days
        out.append({"label": r["label"], "due": due.isoformat(), "status": status_for(n), "how": f"{r['days']} days after the {STARTS[r['starts']]} ({s}), as you typed", "source": r["source"], "confirm": "Double-check against your source."})
    return out

def add_deduction(packet, description, amount, photo_filename=""):
    """A charge the landlord listed (or that you dispute). Just records it."""
    p = _p(packet); refuse_sensitive(description, photo_filename, secrets=True)
    p["deductions"].append({"description": field(description, "description", 200, required=True), "amount": money(amount, "amount"), "photo": field(photo_filename, "photo_filename", 200)}); return p

def demand_letter(packet, amount_requested, reasons, forwarding_address="", rule_text_you_found="", today=None):
    """Template from YOUR facts. Cites a rule only if you typed it (quoted back, with your source). Never says what the law is."""
    p = _p(packet); today = today or date.today()
    refuse_sensitive(reasons, forwarding_address, rule_text_you_found, secrets=True)
    amt = money(amount_requested, "amount_requested")
    rs = [field(r, "reason", 400) for r in (reasons or []) if field(r, "reason", 400)]
    if not rs: raise ValueError("Give at least one reason, in your own words (for example 'The carpet was already stained at move-in; see photos dated ...').")
    fwd = field(forwarding_address, "forwarding_address", 300) or p["forwarding_address"] or "[YOUR FORWARDING ADDRESS]"
    ch = compare(p)["looks_worse_at_move_out"]
    L = [fwd, "", today.strftime("%B %d, %Y").replace(" 0", " "), "", f"To: {p['landlord']}", "", "Re: Request to return my security deposit", f"Rental address: {p['property']}",
         f"Tenant: {p['tenant']}", f"Move-in: {p['move_in']}" + (f"; Move-out: {p['move_out']}" if p["move_out"] else ""), "", "Hello,", ""]
    L += [f"I am asking for the return of ${amt:,.2f} of my security deposit" + (f" (the deposit I paid was ${p['deposit']:,.2f})." if p["deposit"] is not None else "."), ""]
    if p["deductions"]:
        L += ["I received or expect these charges and I am asking you to review them:"] + [f"- {d['description']}: ${d['amount']:,.2f}" for d in p["deductions"]] + [""]
    L += ["My reasons:"] + [f"{i}. {r}" for i, r in enumerate(rs, 1)] + [""]
    photos = [ph for ph in p["photos"]]
    if photos: L += [f"I have {len([x for x in photos if x['phase']=='move_in'])} move-in photos and {len([x for x in photos if x['phase']=='move_out'])} move-out photos, with dates, and can send copies on request.", ""]
    if rule_text_you_found.strip():
        L += [f"I read the following in my lease or an official source: \"{field(rule_text_you_found, 'rule', 500)}\" [CHECK THIS QUOTE AND ITS SOURCE BEFORE SENDING]", ""]
    L += ["Please send the amount above and an itemized written list of any amount you keep. My forwarding address is above.", "", "Thank you,", p["tenant"], "",
          "[DRAFT: review every line, add your signature, and send it yourself by a method you can prove, like certified mail. Keep a copy and your photos. Check your deadline first.]"]
    return {"draft": "\n".join(L), "note": "Draft only. Nothing was sent. This template does not say what the law is. " + DISCLAIMER,
            "photos_that_look_worse": len(ch)}

def photo_log_markdown(packet):
    p = _p(packet)
    L = [f"# Photo log: {md_escape(p['property'])}", f"Tenant: {md_escape(p['tenant'])}. Landlord: {md_escape(p['landlord'])}", "", "| Phase | Room | Item | Condition | File | Date taken | Note |", "|---|---|---|---|---|---|---|"]
    for x in sorted(p["photos"], key=lambda x: (x["phase"] != "move_in", x["room"], x["item"])):
        L.append(f"| {x['phase'].replace('_','-')} | {md_escape(x['room'])} | {md_escape(x['item'])} | {x['condition']} | {md_escape(x['filename'])} | {x['taken']} | {md_escape(x['note'])} |")
    L += ["", f"_{DISCLAIMER}_"]
    return "\n".join(L)
