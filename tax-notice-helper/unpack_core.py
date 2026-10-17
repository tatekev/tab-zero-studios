"""Unpack core: turn the text of a confusing letter/bill into What / Do / By when.
Rule-based, offline, no network, no data stored. Not legal, tax or financial advice.
Honesty rules: never invent a deadline; say so when none is found; hide SSN/card numbers."""
import re, unicodedata
from datetime import date

MAX_CHARS = 100_000
MONTHS = {m: i for i, m in enumerate(
    ["january","february","march","april","may","june","july","august","september","october","november","december"], 1)}
for _m, _i in list(MONTHS.items()):
    MONTHS[_m[:3]] = _i
MONTHS["sept"] = 9
MON = "|".join(sorted(MONTHS, key=len, reverse=True))

def _kw(words):
    return re.compile(r"\b(?:" + "|".join(re.escape(w) for w in words) + r")", re.I)

KINDS = [
    ("utility bill", ["shutoff", "shut-off", "shut off", "kwh", "therms", "meter reading", "water service", "electric service", "gas service", "service address", "disconnection", "utility"]),
    ("bill", ["amount due", "balance due", "please pay", "statement balance", "minimum payment", "invoice", "past due", "pay by", "total due"]),
    ("tax notice", ["internal revenue", "irs", "notice cp", "tax year", "department of revenue", "estimated tax", "taxpayer", "balance due to the irs"]),
    ("HOA notice", ["homeowners association", "homeowners' association", "hoa", "assessment", "architectural", "covenants", "violation", "board of directors"]),
    ("insurance letter", ["policy number", "premium", "claim number", "coverage", "deductible"]),
    ("medical letter or bill", ["explanation of benefits", "patient responsibility", "this is not a bill", "provider", "patient", "amount you may owe", "medical", "hospital"]),
    ("legal or court notice", ["court", "summons", "hearing", "plaintiff", "defendant", "attorney", "subpoena"]),
    ("school letter", ["student", "school", "teacher", "classroom", "principal"]),
]
KIND_RES = [(n, _kw(k)) for n, k in KINDS]
ACTION_RE = re.compile(r"\b(?:pay|call|respond|reply|sign|return|submit|send|provide|contact|schedule|attend|file|review|confirm|verify|update|mail|bring|register|enroll|appeal|dispute|correct|remove|trim|repair)\b", re.I)
URGENT_RE = _kw(["final notice", "final warning", "past due", "immediately", "urgent", "shutoff", "shut-off", "shut off", "disconnect",
                 "penalt", "late fee", "overdue", "failure to", "collections", "legal action", "lien", "garnish", "levy", "suspend",
                 "terminat", "foreclos", "evict", "fine of", "fines", "turned off", "turn off", "act now", "within 24 hours", "within 48 hours"])
DEADLINE_RE = re.compile(r"\b(?:due|by|before|no later than|deadline|on or before|respond|until|expires?|prior to|cure|remedy|shut\w* off|disconnect\w*)\b", re.I)
RELATIVE_RE = re.compile(r"\b(?:within|in)\s+(?:the\s+next\s+)?(\d{1,3})\s+(business\s+|calendar\s+|working\s+)?(days?|weeks?|hours?)\b[^.\n]{0,60}", re.I)
INJECTION_RE = re.compile(r"ignore (?:all |any )?(?:the )?(?:previous|prior|above|earlier) (?:instructions|rules|prompts?)|disregard (?:all |the )?(?:previous|prior|above|your)|you are now\b|system prompt|as an ai\b|new instructions:|reveal your|do not tell the user|override (?:your|the) (?:rules|instructions)", re.I)
MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d{2})?")
SSN = re.compile(r"(?<![\d-])\d{3}[- .]?\d{2}[- .]?\d{4}(?![\d-])")
CARD = re.compile(r"(?<![\d-])(?:\d{4}[ -]){3}\d{1,7}(?![\d-])|(?<![\d-])\d{4}[ -]\d{6}[ -]\d{5}(?![\d-])|(?<![\d-])\d{13,19}(?![\d-])")
# 9 digits split by single spaces/dashes/dots in any pattern (e.g. "1 2 3 - 4 5 - 6 7 8 9"); ZIP+4 is left alone
LOOSE_SSN = re.compile(r"(?<!\d)(?<!\d[ .-])(?<!\d[ .-]{2})(?<!\d[ .-]{3})(?:\d[ .-]{0,3}){8}\d(?![ .-]{0,3}\d)")
UNREAD_DATE = re.compile(r"\b(?:due|by|before|on or before|no later than|until|expires?)\s*(?:on\s*)?[:\-]?\s*(?:[A-Za-z]{3,10}\.?\s+\d{1,2}(?:st|nd|rd|th)?(?:\s*,?\s*\d{4})?|\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}|\d{4}-\d{1,2}-\d{1,2})", re.I)
STOP = set("the a an and or to of in on for you your is are was be this that with as at by it we our if not from have will please".split())

# date patterns -> (regex, kind)
DATE_PATTERNS = [
    (re.compile(r"(?<![\d/])(\d{4})-(\d{1,2})-(\d{1,2})(?![\d/])"), "iso"),
    (re.compile(r"(?<![\d/])(\d{1,2})/(\d{1,2})/(\d{4}|\d{2})(?![\d/])"), "slash"),
    (re.compile(r"\b(" + MON + r")\.?\s+(\d{1,2})(?:st|nd|rd|th)?(?:\s*,\s*|\s+)(\d{4})\b", re.I), "mdy"),
    (re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(" + MON + r")\.?,?\s+(\d{4})\b", re.I), "dmy"),
    (re.compile(r"\b(" + MON + r")\.?\s+(\d{1,2})(?:st|nd|rd|th)?\b(?!\s*,?\s*\d{4})(?!:)", re.I), "md"),
]

def clean(text):
    text = unicodedata.normalize("NFKC", text or "")
    text = "".join(c for c in text if c in "\n\t" or unicodedata.category(c) not in ("Cc", "Cf", "Co", "Cs"))
    return text.replace("\r", "\n")

def redact(text):
    n = 0
    def sub(m):
        nonlocal n; n += 1; return "[hidden number]"
    text = CARD.sub(sub, text)
    text = SSN.sub(sub, text)
    text = LOOSE_SSN.sub(lambda m: m.group(0) if re.fullmatch(r"\d{5}-\d{4}", m.group(0)) else sub(m), text)
    return text, n

def _mk(y, mo, d):
    try:
        return date(y, mo, d)
    except ValueError:
        return None

def find_dates(text, today=None):
    """Return list of dicts: date (or None), year_stated, ambiguous, sentence."""
    today = today or date.today()
    found, taken = [], []
    sentences = [s.strip() for s in re.split(r"\n+|(?<=[.!?])\s+(?=[A-Z\[])", text) if s.strip()]
    for s in sentences:
        taken = []
        for p, kind in DATE_PATTERNS:
            for m in p.finditer(s):
                if any(not (m.end() <= a or m.start() >= b) for a, b in taken):
                    continue
                g = m.groups(); amb = False; ys = True
                if kind == "iso": d = _mk(int(g[0]), int(g[1]), int(g[2]))
                elif kind == "slash":
                    a, b, y = int(g[0]), int(g[1]), int(g[2]); y += 2000 if y < 100 else 0
                    if a > 12 and b <= 12: d = _mk(y, b, a)   # clearly day/month
                    else:
                        d = _mk(y, a, b); amb = a <= 12 and b <= 12 and a != b
                elif kind == "mdy": d = _mk(int(g[2]), MONTHS[g[0].lower()], int(g[1]))
                elif kind == "dmy": d = _mk(int(g[2]), MONTHS[g[1].lower()], int(g[0]))
                else:
                    ys = False
                    if g[0].lower() == "may" and not re.search(r"\bmay\s+\d", s[m.start():m.end()].lower()): continue
                    d = _mk(today.year, MONTHS[g[0].lower()], int(g[1]))
                taken.append((m.start(), m.end()))
                if d: found.append({"date": d, "year_stated": ys, "ambiguous": amb, "sentence": s})
    return found

def classify(text):
    best, score = "general letter", 0
    for name, rx in KIND_RES:
        n = len(rx.findall(text))
        if n > score:
            best, score = name, n
    return best, score

def _looks_non_english(text):
    words = re.findall(r"[^\W\d_]+", text.lower())
    if len(words) < 8: return False
    return sum(w in STOP for w in words) / len(words) < 0.08

def _plural(n, w): return f"{n} {w}" + ("" if n == 1 else "s")

def unpack(text, today=None):
    today = today or date.today()
    warnings = []
    text = clean(text if isinstance(text, str) else ("" if text is None else str(text)))
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
        warnings.append(f"Letter was very long. Only the first {MAX_CHARS:,} characters were read.")
    text, hidden = redact(text)
    if hidden:
        warnings.append(f"Hid {hidden} number(s) that look like an SSN or card number. Don't paste those; they are not stored or shown.")
    if not text.strip():
        return {
            "what_is_this": "Nothing to read. No text was provided.",
            "what_to_do": ["Paste the text of the letter or bill and try again."],
            "by_when": "No clear date found. No text was provided.",
            "urgency": "unknown", "warning_words": [], "dates_in_the_past": [], "other_dates": [],
            "first_tiny_step": "Paste the letter text.", "warnings": warnings,
            "disclaimer": DISCLAIMER}
    nonen = _looks_non_english(text)
    if nonen:
        warnings.append("This does not look like English. Unpack only reads English well, so the summary may be wrong. Dates and dollar amounts are still shown; check the original or ask a translator.")
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\[])|\n+", text) if s.strip()]
    injected = [s for s in sentences if INJECTION_RE.search(s)]
    if injected:
        warnings.append("Part of this text looks like instructions aimed at an AI assistant. Unpack ignored it. Treat that part of the letter with suspicion.")
    safe_text = "\n".join(s for s in sentences if s not in injected)
    sentences = [s for s in sentences if s not in injected]

    kind, score = classify(safe_text)
    amounts = list(dict.fromkeys(MONEY.findall(safe_text)))[:5]
    actions = []
    for s in sentences:
        if ACTION_RE.search(s) and not re.match(r"\s*thank", s, re.I) and s not in actions:
            actions.append(s if len(s) <= 300 else s[:297] + "...")
        if len(actions) == 5: break

    dates = find_dates(safe_text, today)
    for x in dates:
        x["kw"] = bool(DEADLINE_RE.search(x["sentence"]))
    usable = [x for x in dates if x["year_stated"] or x["date"] >= today]
    unclear = [x for x in dates if not x["year_stated"] and x["date"] < today]
    future = sorted([x for x in usable if x["date"] >= today], key=lambda x: x["date"])
    past = [x for x in usable if x["date"] < today]
    with_kw = [x for x in future if x["kw"]]
    deadline = with_kw[0] if with_kw else None
    relative = [m.group(0).strip() for m in RELATIVE_RE.finditer(safe_text)][:3]
    past_deadline = [x for x in past if x["kw"]]
    urgent = list(dict.fromkeys(m.group(0).lower() for m in URGENT_RE.finditer(safe_text)))
    days_left = (deadline["date"] - today).days if deadline else None

    if deadline:
        dl = deadline["date"].isoformat()
        by_when = dl + (" (today)" if days_left == 0 else f" ({_plural(days_left, 'day')} from today)")
        if deadline["ambiguous"]: by_when += ". Read as month/day/year; double-check on the letter"
        if not deadline["year_stated"]: by_when += ". The letter gives no year, so this year is assumed; double-check"
    elif future:
        d0 = future[0]
        by_when = (f"No clear deadline found. The next date mentioned is {d0['date'].isoformat()}, but the letter doesn't say it is a deadline. Check the letter")
    elif relative:
        by_when = "No calendar date found. The letter says: \"" + relative[0] + "\". Count from the date on the letter"
    elif past_deadline:
        by_when = f"The date(s) in this letter have passed ({', '.join(x['date'].isoformat() for x in past_deadline[:3])}). It may be overdue. Contact the sender soon"
    else:
        by_when = "No clear date found. Check the letter for a deadline"
        if nonen: by_when += ". This isn't English, so dates may have been missed"
    if (deadline or (future and not deadline)) and relative:
        by_when += f". Also: \"{relative[0]}\""
    if not (deadline or future) and not past_deadline:
        unread = [m.group(0) for m in UNREAD_DATE.finditer(safe_text) if not any(m.group(0).lower() in x["sentence"].lower() and x["date"] for x in dates)]
        if unread and not relative:
            by_when = "No clear date found. The letter seems to mention: \"" + unread[0][:60] + "\" but it is misspelled, impossible, or in a format Unpack does not know. Check the letter. Nothing was guessed"
    if unclear:
        by_when += ". Some dates had no year and look earlier than today; check: " + ", ".join(x["sentence"][:60] for x in unclear[:2])

    if days_left is not None and days_left <= 3:
        urgency = "high"
    elif (urgent and (days_left is None or days_left <= 7)) or (past_deadline and not deadline) or (urgent and any("hour" in r.lower() for r in relative)):
        urgency = "high"
    elif days_left is not None and (days_left <= 14 or (urgent and days_left <= 30)):
        urgency = "medium"
    else:
        urgency = "low"

    guess = "This looks like" if score >= 2 else ("This might be" if score == 1 else "I can't tell for sure what this is; it reads like")
    what = f"{guess} {'an' if kind[0] in 'AEIOaeio' or kind.startswith('HOA') else 'a'} {kind}." + (f" Amounts mentioned: {', '.join(amounts)}." if amounts else "")
    others = [f"{x['date'].isoformat()}: {x['sentence'][:100]}" for x in future if x is not deadline][:5]
    by_when = by_when.rstrip(".") + "."
    return {
        "what_is_this": what,
        "what_to_do": actions or ["No clear action found. Read it once, then ask the sender or a person you trust."],
        "by_when": by_when,
        "urgency": urgency,
        "warning_words": urgent,
        "dates_in_the_past": [x["date"].isoformat() for x in past][:3],
        "other_dates": others,
        "first_tiny_step": (actions[0] if actions else "Put the letter in one spot and set a 5 minute timer to re-read it."),
        "warnings": warnings,
        "disclaimer": DISCLAIMER,
    }

DISCLAIMER = "General reading help only. Not legal, tax, or financial advice. Check the original document."

def to_markdown(r):
    lines = ["## What is this?", r["what_is_this"], "", "## What do I do?"]
    lines += [f"{i}. {a}" for i, a in enumerate(r["what_to_do"], 1)]
    lines += ["", "## By when?", r["by_when"], f"Urgency: **{r['urgency']}**"]
    if r.get("other_dates"):
        lines += ["", "Other dates: " + "; ".join(r["other_dates"])]
    lines += ["", "## First tiny step", r["first_tiny_step"]]
    if r.get("warnings"):
        lines += ["", "## Heads up"] + [f"- {w}" for w in r["warnings"]]
    lines += ["", f"_{r['disclaimer']}_"]
    return "\n".join(lines)
