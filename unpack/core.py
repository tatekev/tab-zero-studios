"""Unpack core: turn the text of a confusing letter/bill into What / Do / By when.
Rule-based, offline, no network, no data stored. Not legal, tax or financial advice."""
import re
from datetime import date, datetime

MONTHS = {m: i for i, m in enumerate(
    ["january","february","march","april","may","june","july","august","september","october","november","december"], 1)}
KINDS = [
    ("bill", ["amount due","balance due","please pay","statement balance","minimum payment","invoice","past due","pay by"]),
    ("tax notice", ["internal revenue","irs","notice cp","tax year","department of revenue","estimated tax"]),
    ("hoa notice", ["homeowners association","hoa","assessment","architectural","covenants"]),
    ("insurance", ["policy number","premium","claim number","coverage","deductible"]),
    ("medical", ["explanation of benefits","patient responsibility","this is not a bill","provider"]),
    ("legal or court", ["court","summons","hearing","plaintiff","defendant","attorney"]),
    ("school", ["student","school","teacher","parent","classroom"]),
]
ACTION_WORDS = ["pay","call","respond","reply","sign","return","submit","send","provide","contact","schedule","attend","file","review","confirm","verify","update"]
URGENT = ["final notice","past due","immediately","urgent","shutoff","shut-off","disconnect","penalty","late fee","overdue","failure to"]
MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d{2})?")
DATE_PATTERNS = [
    re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b"),
    re.compile(r"\b(" + "|".join(m.capitalize() for m in MONTHS) + r")\s+(\d{1,2})(?:st|nd|rd|th)?(?:,\s*(\d{4}))?", re.I),
]

def _to_date(m, today, kind):
    try:
        if kind == 0:
            mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            y += 2000 if y < 100 else 0
        else:
            mo, d = MONTHS[m.group(1).lower()], int(m.group(2))
            y = int(m.group(3)) if m.group(3) else today.year
        return date(y, mo, d)
    except ValueError:
        return None

def find_dates(text, today=None):
    today = today or date.today()
    found = []
    for s in re.split(r"(?<=[.!?\n])\s+", text):
        for k, p in enumerate(DATE_PATTERNS):
            for m in p.finditer(s):
                d = _to_date(m, today, k)
                if d:
                    found.append((d, s.strip()))
    return found

def classify(text):
    low = text.lower()
    best, score = "general letter", 0
    for name, keys in KINDS:
        n = sum(low.count(k) for k in keys)
        if n > score:
            best, score = name, n
    return best

def unpack(text, today=None):
    today = today or date.today()
    low = text.lower()
    kind = classify(text)
    amounts = list(dict.fromkeys(MONEY.findall(text)))[:5]
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
    actions = [s for s in sentences if any(re.search(r"\b" + w + r"\b", s.lower()) for w in ACTION_WORDS)][:5]
    dates = find_dates(text, today)
    future = sorted([d for d in dates if d[0] >= today], key=lambda x: x[0])
    deadline = None
    for d, s in future:
        if re.search(r"due|by|before|no later|deadline|on or before|respond|within", s.lower()):
            deadline = (d, s); break
    if not deadline and future:
        deadline = future[0]
    past = [d for d in dates if d[0] < today]
    urgent = [u for u in URGENT if u in low]
    days_left = (deadline[0] - today).days if deadline else None
    if urgent and (days_left is None or days_left <= 7):
        urgency = "high"
    elif days_left is not None and days_left <= 14:
        urgency = "medium"
    else:
        urgency = "low"
    what = f"This looks like a {kind}." + (f" Amounts mentioned: {', '.join(amounts)}." if amounts else "")
    return {
        "what_is_this": what,
        "what_to_do": actions or ["No clear action found. Read it once, then ask the sender or a person you trust."],
        "by_when": (deadline[0].isoformat() + f" ({days_left} days from today)") if deadline else "No clear date found. Check the letter for a deadline.",
        "urgency": urgency,
        "warning_words": urgent,
        "dates_in_the_past": [d[0].isoformat() for d in past][:3],
        "first_tiny_step": (actions[0] if actions else "Put the letter in one spot and set a 5 minute timer to re-read it."),
        "disclaimer": "General reading help only. Not legal, tax, or financial advice. Check the original document.",
    }

def to_markdown(r):
    lines = ["## What is this?", r["what_is_this"], "", "## What do I do?"]
    lines += [f"{i}. {a}" for i, a in enumerate(r["what_to_do"], 1)]
    lines += ["", "## By when?", r["by_when"], f"Urgency: **{r['urgency']}**", "",
              "## First tiny step", r["first_tiny_step"], "", f"_{r['disclaimer']}_"]
    return "\n".join(lines)
