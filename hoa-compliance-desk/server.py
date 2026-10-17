from mcp.server.fastmcp import FastMCP
import core
mcp = FastMCP("hoa-compliance-desk")

@mcp.tool()
def start_hoa(name: str, contact: str = "") -> dict:
    """Start an HOA record. Your app keeps it between calls."""
    return core.new_hoa(name, contact)

@mcp.tool()
def lake_crest_demo() -> dict:
    """DEMO: a sample 'Lake Crest HOA' with made-up numbers for practice. Not real HOA data."""
    return core.demo_hoa()

@mcp.tool()
def save_notice_rule(hoa: dict, label: str, days_before: int, source: str) -> dict:
    """Save a notice period your board found in its bylaws (days before the meeting). 'source' is required."""
    return core.add_notice_rule(hoa, label, days_before, source)

@mcp.tool()
def plan_meeting_notice(hoa: dict, meeting_date: str, time: str, place: str, agenda: list[str], rule_label: str = "") -> dict:
    """Compute the send-by date from YOUR saved rule and draft an annual meeting notice. Draft only."""
    return core.plan_meeting_notice(hoa, meeting_date, time, place, agenda, rule_label)

@mcp.tool()
def save_schedule(hoa: dict, label: str, kind: str, frequency: str, first_date: str, remind_days_before: int = 7, amount: float = 0) -> dict:
    """Save a recurring date (dues, reserve, insurance, tax_filing, other). frequency: monthly, quarterly, semiannual, annual."""
    return core.add_schedule(hoa, label, kind, frequency, first_date, remind_days_before, amount or None)

@mcp.tool()
def upcoming_dates(hoa: dict, within_days: int = 120) -> list[dict]:
    """Due dates and reminder-send dates in the next N days."""
    return core.upcoming(hoa, within_days=within_days)

@mcp.tool()
def draft_payment_reminder(hoa: dict, label: str, due_date: str, amount: float = 0, pay_instructions: str = "") -> dict:
    """Draft (never send) a friendly dues or reserve reminder."""
    return core.reminder_draft(hoa, label, due_date, amount or None, pay_instructions)

@mcp.tool()
def records_checklist() -> list[dict]:
    """A 14-item HOA records checklist."""
    return core.records_checklist()

@mcp.tool()
def mark_record(items: list[dict], record_id: str, status: str) -> list[dict]:
    """Set a record's status: missing, have, needs_update, not_applicable."""
    return core.mark_record(items, record_id, status)

@mcp.tool()
def board_summary(hoa: dict) -> str:
    """One-page Markdown summary of saved rules and upcoming dates."""
    return core.board_summary(hoa)

@mcp.tool()
def scope_check(text: str) -> dict:
    """Say so when a question asks what the law or bylaws require (this tool never answers that)."""
    return core.scope_check(text)

if __name__ == "__main__":
    mcp.run()
