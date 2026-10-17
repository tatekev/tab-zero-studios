from mcp.server.fastmcp import FastMCP
import core
mcp = FastMCP("medical-bill-appeal-kit")

@mcp.tool()
def bill_checklist() -> list[dict]:
    """A 12-step checklist for reviewing a medical bill and EOB."""
    return core.checklist()

@mcp.tool()
def tick_checklist_item(items: list[dict], item_id: str, done: bool = True) -> list[dict]:
    """Mark a checklist item done or not done."""
    return core.mark_done(items, item_id, done)

@mcp.tool()
def start_case(patient_name: str, provider: str, insurer: str = "", note: str = "") -> dict:
    """Start a case. Your app keeps it between calls. Refuses SSNs, cards, passwords."""
    return core.new_case(patient_name, provider, insurer, note)

@mcp.tool()
def add_deadline(case: dict, label: str, source: str, start_date: str = "", days: int = 0, exact_date: str = "") -> dict:
    """Add a deadline you read on your letter. Give exact_date, OR start_date + days. 'source' (where you read it) is required. Dates are YYYY-MM-DD."""
    return core.add_deadline(case, label, source, start_date or None, days or None, exact_date or None)

@mcp.tool()
def finish_deadline(case: dict, label: str) -> dict:
    """Mark a deadline as done."""
    return core.finish_deadline(case, label)

@mcp.tool()
def deadline_tracker(case: dict) -> list[dict]:
    """Days left for each saved deadline."""
    return core.tracker(case)

@mcp.tool()
def log_contact(case: dict, when: str, who: str, what: str) -> dict:
    """Log a call or letter (date YYYY-MM-DD)."""
    return core.log_contact(case, when, who, what)

@mcp.tool()
def draft_itemized_bill_request(case: dict, date_of_service: str, sender_address: str = "[YOUR ADDRESS]", account_last4: str = "") -> dict:
    """Draft (never send) a letter asking for an itemized bill."""
    return core.itemized_request_letter(case, date_of_service, sender_address, account_last4)

@mcp.tool()
def draft_appeal_letter(case: dict, claim_ref_last4: str, denial_date: str, denial_reason: str, why_wrong: str, attachments: list[str] = [], sender_address: str = "[YOUR ADDRESS]") -> dict:
    """Draft (never send) an appeal letter from your own words. Adds no facts or legal claims."""
    return core.appeal_letter(case, claim_ref_last4, denial_date, denial_reason, why_wrong, attachments, sender_address)

@mcp.tool()
def case_summary(case: dict) -> str:
    """One-page Markdown summary of deadlines and the contact log."""
    return core.case_summary(case)

@mcp.tool()
def scope_check(text: str) -> dict:
    """Say so when a question asks for medical or legal advice (this kit never answers that)."""
    return core.scope_check(text)

if __name__ == "__main__":
    mcp.run()
