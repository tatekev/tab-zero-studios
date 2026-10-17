"""Tax Notice Helper core: an IRS or state tax letter in -> plain answer, what to do, reply deadline, reply checklist.
Extends Unpack (unpack_core.py). Offline, stores nothing. Never gives tax/legal advice. Never invents a deadline:
the reply-by date is shown only if it is written in the letter's text."""
import re
from datetime import date
import unpack_core
from safety import norm, redact, INJECTION, SensitiveDataError, MAX_TEXT, status_for

DISCLAIMER = "General reading help only. Not legal or tax advice. Check the original letter, and ask a tax professional before you pay, disagree, or reply."

# Plain-language meanings for common notice codes. Deliberately general. The letter itself is the authority.
NOTICES = {
    "CP14": "A bill: the IRS says you owe a balance.",
    "CP501": "A reminder: the IRS says a balance is still unpaid.",
    "CP503": "A second reminder: the IRS says a balance is still unpaid.",
    "CP504": "A serious notice: the IRS says it may take property or money if a balance stays unpaid.",
    "CP2000": "A mismatch letter: the IRS says income it has on file doesn't match your return and proposes changes. It is not a bill yet.",
    "CP11": "The IRS changed your return and says the change makes you owe a balance.",
    "CP12": "The IRS changed your return and says the change affects your refund or balance.",
    "CP22A": "The IRS changed your return after you filed (an amended return or a correction).",
    "CP24": "The IRS changed your estimated tax payments on your return.",
    "CP71": "A yearly reminder about an unpaid balance.",
    "CP75": "The IRS is asking for documents to back up something on your return.",
    "CP90": "A final notice of intent to take (levy) money or property. Time-limited.",
    "CP3219A": "A statutory notice of deficiency: the IRS proposes changes. It has a strict date to respond. Read it today.",
    "LT11": "A final notice of intent to levy, with appeal rights. Time-limited.",
    "5071C": "The IRS wants to confirm your identity before processing a return.",
    "CP01": "The IRS flagged possible identity theft on your account.",
    "1058": "A final notice of intent to levy, with appeal rights. Time-limited.",
}
NOTICE_RE = re.compile(r"\b(?:notice|letter|form)?\s*(CP\s?-?\d{2,4}[A-Z]?|LT\s?-?\d{2,3}[A-Z]?|5071C|Letter\s+\d{3,4}[A-Z]?)\b", re.I)
IRS_RE = re.compile(r"\binternal revenue service\b|\birs\b|department of the treasury", re.I)
STATE_RE = re.compile(r"\b(?:department|dept\.?|division) of (?:revenue|taxation|taxes|finance)\b|\bstate (?:tax|revenue)\b|\btax commission\b|\bfranchise tax board\b|\bcomptroller\b", re.I)
TAX_ADVICE_Q = re.compile(r"\b(?:should i|do i have to|do i need to|can i|must i|am i required|is it legal|will they|am i in trouble|how much (?:do|will|should) i)\b[^.?!]{0,60}\b(?:pay|owe|ignore|dispute|appeal|settle|negotiate|respond|file|amend|worry|go to jail|arrest\w*)\b|\bwhat should i do about (?:my )?taxes\b|\bwill i (?:owe|go to jail|get arrested)\b|\bis (?:this|it) (?:legal|legit|valid)\b", re.I)
SCAM_RE = re.compile(r"gift cards?|wire transfer|bitcoin|crypto|western union|moneygram|arrest(?:ed)? (?:you|today)|police (?:will|are)|pay (?:today|now) or|call this number immediately|zelle|cash ?app|venmo|text message|click (?:the|this) link|\bbit\.ly\b|tinyurl", re.I)
REL_DAYS = re.compile(r"\b\d{1,3}\s+(?:calendar\s+|business\s+)?days\b[^.\n]{0,80}", re.I)
LEVY_RE = re.compile(r"\bintent to levy\b|\blevy\b|\blien\b|\bgarnish", re.I)
PETITION_RE = re.compile(r"tax court|petition|notice of deficiency|right to appeal|appeal rights|request a hearing|collection due process", re.I)
ID_RE = re.compile(r"identity (?:theft|verification|verify)|verify your identity|5071C|CP01", re.I)

REPLY_CHECKLIST = [
    "Put the letter, the envelope, and a copy of the tax return it is about in one spot.",
    "Write down the notice number, the letter date, and the tax year from the top of the letter.",
    "Find the reply-by date printed on the letter. Write it on your calendar. (This tool shows one only if it is in the text.)",
    "Read what the letter says it wants: pay, send documents, agree, or disagree. Underline that one thing.",
    "Compare the letter's numbers with your own copy of the return. Mark any that look different.",
    "Gather only the papers the letter asks for. Make copies; keep the originals.",
    "Ask your tax preparer or a tax professional what to do before you pay, disagree, or reply.",
    "Use only the phone number, address, or website printed on the letter, or on IRS.gov or your state's official site. Do not use links from texts or emails.",
    "Reply in writing by a method you can prove (certified mail with receipt, or the official online account). Keep copies of everything you send.",
    "Write down who you spoke to, the date, and what they said.",
    "Never pay with gift cards, wire transfers, or crypto. Real tax agencies don't ask for those.",
]

def _agency(text):
    irs = bool(IRS_RE.search(text)); st = bool(STATE_RE.search(text))
    if irs and not st: return "IRS (federal)"
    if st and not irs: return "state tax agency"
    if irs and st: return "IRS and a state agency are both mentioned"
    return "not clear from the text"

def _notice_codes(text):
    out = []
    for m in NOTICE_RE.finditer(text):
        code = re.sub(r"[\s-]", "", m.group(1)).upper()
        code = re.sub(r"^LETTER", "", code) if code.startswith("LETTER") else code
        if code not in out: out.append(code)
    return out[:3]

def scope_check(text):
    q = bool(TAX_ADVICE_Q.search(norm(text)))
    return {"is_advice_request": q,
            "message": ("This tool reads letters. It can't tell you whether to pay, dispute, or ignore a notice. Ask a tax professional." if q
                        else "OK. This is a reading question.")}

def explain_notice(text, today=None):
    today = today or date.today()
    raw = norm(text if isinstance(text, str) or text is None else str(text))
    warnings = []
    if len(raw) > MAX_TEXT:
        raw = raw[:MAX_TEXT]; warnings.append(f"Letter was very long. Only the first {MAX_TEXT:,} characters were read.")
    base = unpack_core.unpack(raw, today)
    safe, hidden = redact(raw)
    warnings += [w for w in base["warnings"] if w not in warnings]
    if not safe.strip():
        return {"plain_answer": "Nothing to read. No text was provided.", "agency": "unknown", "notice_numbers": [], "what_it_means": [],
                "what_to_do": ["Paste the text of the letter and try again."], "reply_by": "No text was provided. No deadline found.",
                "reply_by_found": False, "urgency": "unknown", "red_flags": [], "reply_checklist": REPLY_CHECKLIST, "warnings": warnings,
                "advice_request": False, "disclaimer": DISCLAIMER}
    sentences_ok = "\n".join(s for s in re.split(r"\n+|(?<=[.!?])\s+", safe) if s.strip() and not INJECTION.search(s))
    codes = _notice_codes(sentences_ok)
    known = [(c, NOTICES[c]) for c in codes if c in NOTICES]
    unknown = [c for c in codes if c not in NOTICES]
    agency = _agency(sentences_ok)
    is_tax = base["what_is_this"].find("tax notice") != -1 or bool(codes) or agency not in ("not clear from the text",)
    flags = []
    if SCAM_RE.search(sentences_ok):
        flags.append("SCAM WARNING: this text mentions gift cards, wire/crypto/payment apps, threats of arrest, or links. Real tax agencies don't demand those. Do not pay or click. Look up the agency's number yourself and call it.")
    if LEVY_RE.search(sentences_ok):
        flags.append("This letter mentions a levy, lien, or garnishment. These can have short, strict response windows. Find the date on the letter today.")
    if PETITION_RE.search(sentences_ok):
        flags.append("This letter mentions appeal or court rights. Those rights usually have a strict last day, printed in the letter. Find it and tell a tax professional right away.")
    if ID_RE.search(sentences_ok):
        flags.append("This is about identity. Only use the official number or website printed on the letter, or IRS.gov.")
    if not is_tax:
        warnings.append("This doesn't clearly look like a tax notice. The reading below is general. Check the letter.")
    means = [f"{c}: {m}" for c, m in known]
    if unknown: means.append("Notice number(s) not in this tool's short list: " + ", ".join(unknown) + ". Read the letter's own explanation.")
    if not codes: means.append("No notice number (like CP14 or CP2000) was found in the text.")
    if known:
        plain = f"From {agency}. " + known[0][1]
    elif is_tax:
        plain = f"From {agency}. It looks like a tax letter, but this tool doesn't know the exact kind. " + base["what_is_this"]
    else:
        plain = base["what_is_this"]
    by = base["by_when"]
    found = bool(re.match(r"\d{4}-\d{2}-\d{2}", by))
    if not found and by.startswith("No clear date found"):
        rel = REL_DAYS.search(sentences_ok)
        if rel:
            by = f'No calendar date found. The letter says: "{rel.group(0).strip()}". Count from the date on the letter. No date was invented'
    urgency = base["urgency"]
    if (flags and urgency == "low" and any(f.startswith("This letter mentions a levy") or f.startswith("This letter mentions appeal") for f in flags)):
        urgency = "medium"
    actions = list(base["what_to_do"])
    if base["what_to_do"][0].startswith("No clear action"):
        actions = ["Read the whole letter once. Underline what it asks you to do.", "Call or write your tax preparer."]
    adv = bool(TAX_ADVICE_Q.search(safe))
    if adv: warnings.append("Part of your text asks what you should do or owe. This tool can't answer that. Ask a tax professional.")
    return {"plain_answer": plain, "agency": agency, "notice_numbers": codes, "what_it_means": means, "what_to_do": actions,
            "reply_by": by, "reply_by_found": found, "urgency": urgency, "red_flags": flags, "reply_checklist": REPLY_CHECKLIST,
            "amounts_mentioned": list(dict.fromkeys(unpack_core.MONEY.findall(sentences_ok)))[:5],
            "warnings": warnings, "advice_request": adv, "disclaimer": DISCLAIMER}

def to_markdown(r):
    L = ["## Plain answer", r["plain_answer"], "", "## What it means"] + [f"- {x}" for x in r["what_it_means"] or ["Nothing specific found."]]
    L += ["", "## What to do"] + [f"{i}. {a}" for i, a in enumerate(r["what_to_do"], 1)]
    L += ["", "## Reply by", r["reply_by"] + ("" if r["reply_by_found"] else " (No date was invented.)"), f"Urgency: **{r['urgency']}**"]
    if r["red_flags"]: L += ["", "## Red flags"] + [f"- {x}" for x in r["red_flags"]]
    L += ["", "## Reply checklist"] + [f"- [ ] {x}" for x in r["reply_checklist"]]
    if r["warnings"]: L += ["", "## Heads up"] + [f"- {w}" for w in r["warnings"]]
    L += ["", f"_{r['disclaimer']}_"]
    return "\n".join(L)
