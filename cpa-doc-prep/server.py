from mcp.server.fastmcp import FastMCP
import core
mcp = FastMCP("cpa-doc-prep")

@mcp.tool()
def make_checklist(profiles: list[str]) -> list[dict]:
    """Build a tax-document checklist. profiles: employee, investor, self_employed, parent, homeowner."""
    return core.build_checklist(profiles)

@mcp.tool()
def mark_item(checklist: list[dict], item_id: str, status: str) -> list[dict]:
    """Set an item's status: missing, received, sent_to_preparer, not_applicable."""
    return core.update_status(checklist, item_id, status)

@mcp.tool()
def checklist_summary(checklist: list[dict]) -> dict:
    """Group checklist items by status."""
    return core.summary(checklist)

@mcp.tool()
def check_sensitive(text: str) -> dict:
    """Detect full SSN or card numbers in text before sharing."""
    return core.sensitive_check(text)

@mcp.tool()
def scope_check(text: str) -> dict:
    """Check whether a question asks for tax advice or an amount owed (this tool never answers those)."""
    return core.scope_check(text)

@mcp.tool()
def draft_preparer_message(checklist: list[dict], preparer: str = "your preparer", sender: str = "me", channel: str = "email", note: str = "") -> dict:
    """Draft (never send) an email or text to a tax preparer listing what is ready and missing. No tax advice."""
    return core.draft_message(checklist, preparer, sender, channel, note)

if __name__ == "__main__":
    mcp.run()
