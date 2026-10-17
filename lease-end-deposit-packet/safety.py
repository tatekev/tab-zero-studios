"""Shared safety helpers (copied into each TZS tool so every folder stands alone).
Offline. Stores nothing. Never echoes a hidden number."""
import re, unicodedata
from datetime import date, timedelta

class SensitiveDataError(ValueError):
    """Raised when text contains an SSN, card number, or password-like secret."""

SSN = re.compile(r"(?<![\d-])\d{3}[- .]?\d{2}[- .]?\d{4}(?![\d-])")
CARD = re.compile(r"(?<![\d-])(?:\d{4}[ -]){3}\d{1,7}(?![\d-])|(?<![\d-])\d{4}[ -]\d{6}[ -]\d{5}(?![\d-])|(?<![\d-])\d{13,19}(?![\d-])")
LOOSE_SSN = re.compile(r"(?<![\d])(?:\d[ .-]{0,3}){8}\d(?![\d])")
SECRET = re.compile(r"\b(?:pass(?:word|code|phrase)?|pwd|pin|secret|security answer|login|passwd|recovery (?:code|key)|seed phrase|2fa code|otp)\b\s*(?:is|was|=|:|-)\s*\S+", re.I)
LONG_ACCT = re.compile(r"(?<![\d-])\d{9,12}(?![\d-])")
INJECTION = re.compile(r"ignore (?:all |any )?(?:the )?(?:previous|prior|above|earlier) (?:instructions|rules|prompts?)|disregard (?:all |the )?(?:previous|prior|above|your)|you are now\b|system prompt|as an ai\b|new instructions:|reveal your|do not tell the user|override (?:your|the) (?:rules|instructions)", re.I)
MAX_FIELD = 2000
MAX_TEXT = 100_000

def norm(text):
    """Make any input a clean string: NFKC, no control/format chars."""
    if text is None: return ""
    if not isinstance(text, str): text = str(text)
    text = unicodedata.normalize("NFKC", text)
    text = "".join(c for c in text if c in "\n\t" or unicodedata.category(c) not in ("Cc", "Cf", "Co", "Cs"))
    return text.replace("\r", "\n")

def _digits_ok_zip(m):
    return re.fullmatch(r"\d{5}-\d{4}", m.group(0)) is not None

def has_ssn_or_card(text):
    t = norm(text)
    if CARD.search(t) or SSN.search(t): return True
    return any(not _digits_ok_zip(m) for m in LOOSE_SSN.finditer(t))

def has_secret(text):
    return bool(SECRET.search(norm(text)))

def redact(text):
    """Return (text with SSN/card-like numbers replaced, count)."""
    n = 0
    def sub(m):
        nonlocal n; n += 1; return "[hidden number]"
    t = CARD.sub(sub, norm(text)); t = SSN.sub(sub, t)
    t = LOOSE_SSN.sub(lambda m: m.group(0) if _digits_ok_zip(m) else sub(m), t)
    return t, n

REFUSAL = "Remove the full SSN or card number first. Use only the last 4 digits. Nothing was saved."
SECRET_REFUSAL = "That looks like a password, PIN, or code. Don't type those here. Write down only WHERE it is kept (like 'password manager'). Nothing was saved."

def refuse_sensitive(*fields, secrets=False):
    """Raise SensitiveDataError if any field holds an SSN/card (and, if secrets=True, a password-like secret)."""
    for f in fields:
        if f is None: continue
        if isinstance(f, (list, tuple)):
            refuse_sensitive(*f, secrets=secrets); continue
        if isinstance(f, dict):
            refuse_sensitive(*f.values(), secrets=secrets); continue
        s = str(f)
        if has_ssn_or_card(s): raise SensitiveDataError(REFUSAL)
        if secrets and (has_secret(s) or LONG_ACCT.search(norm(s))): raise SensitiveDataError(SECRET_REFUSAL)

def field(value, name="field", maxlen=MAX_FIELD, required=False):
    v = norm(value).strip()
    if required and not v: raise ValueError(f"{name} is required.")
    if len(v) > maxlen: v = v[:maxlen]
    return v

def parse_date(value, name="date"):
    """Strict YYYY-MM-DD only (also accepts a date object). Raises a clear error otherwise. Never guesses."""
    if isinstance(value, date): return value
    s = norm(value).strip()
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if not m: raise ValueError(f"{name} must look like 2026-11-05 (year-month-day). Got: {s[:30]!r}")
    try: return date(int(m[1]), int(m[2]), int(m[3]))
    except ValueError: raise ValueError(f"{name} is not a real calendar date: {s[:30]!r}")

def add_days(d, n):
    return d + timedelta(days=int(n))

def days_from(today, d):
    return (d - today).days

def status_for(days):
    if days is None: return "no date"
    if days < 0: return f"PAST (was {-days} day{'s' if days != -1 else ''} ago)"
    if days == 0: return "TODAY"
    return f"{days} day{'s' if days != 1 else ''} left"

def positive_int(value, name, maxv=3650):
    try:
        if isinstance(value, bool): raise ValueError
        n = int(str(value).strip())
    except (ValueError, TypeError):
        raise ValueError(f"{name} must be a whole number, like 30.")
    if n <= 0 or n > maxv: raise ValueError(f"{name} must be between 1 and {maxv}.")
    return n

def money(value, name="amount"):
    """Parse user-entered dollars to cents-safe float; reject negatives/garbage. Returns float."""
    s = norm(value).replace("$", "").replace(",", "").strip()
    try:
        x = float(s)
    except ValueError:
        raise ValueError(f"{name} must be a number like 12.50.")
    if x != x or x in (float("inf"), float("-inf")) or x < 0 or x > 10_000_000:
        raise ValueError(f"{name} must be between 0 and 10,000,000.")
    return round(x, 2)

def md_escape(s):
    return norm(s).replace("|", "\\|").replace("\n", " ")

def csv_safe(s):
    """Stop spreadsheet formula injection."""
    s = norm(s)
    return ("'" + s) if s[:1] in "=+-@" and not re.fullmatch(r"-?\d+(\.\d+)?", s) else s
