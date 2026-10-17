from mcp.server.fastmcp import FastMCP
import core
mcp = FastMCP("lease-end-deposit-packet")

@mcp.tool()
def start_packet(tenant: str, landlord: str, property_address: str, move_in_date: str, move_out_date: str = "", deposit_amount: str = "", forwarding_address: str = "") -> dict:
    """Start a packet. Dates are YYYY-MM-DD. Your app keeps the packet between calls."""
    return core.new_packet(tenant, landlord, property_address, move_in_date, move_out_date or None, deposit_amount or None, forwarding_address)

@mcp.tool()
def set_move_out(packet: dict, move_out_date: str) -> dict:
    """Set or change the move-out date."""
    return core.set_move_out(packet, move_out_date)

@mcp.tool()
def log_photo(packet: dict, phase: str, room: str, item: str, condition: str, filename: str, taken_date: str, note: str = "") -> dict:
    """Log one photo. phase: move_in or move_out. condition: good, fair, worn, dirty, damaged, missing. Stores only the file NAME, not the photo."""
    return core.add_photo(packet, phase, room, item, condition, filename, taken_date, note)

@mcp.tool()
def compare_photos(packet: dict) -> dict:
    """Match move-in and move-out photos and list what changed. Does not say who is responsible."""
    return core.compare(packet)

@mcp.tool()
def add_deadline_rule(packet: dict, label: str, days: int, starts: str, source: str, source_text: str = "") -> dict:
    """Save a rule YOU found (for example 'return deposit within N days after move-out'). 'source' is required. starts: move_out_date, lease_end_date, forwarding_address_date, other."""
    return core.add_rule(packet, label, days, starts, source, source_text)

@mcp.tool()
def set_event_date(packet: dict, starts: str, when: str) -> dict:
    """Set a start date a rule counts from (lease_end_date, forwarding_address_date, other)."""
    return core.set_event_date(packet, starts, when)

@mcp.tool()
def deadline_tracker(packet: dict) -> list[dict]:
    """Days left on each rule you saved."""
    return core.tracker(packet)

@mcp.tool()
def log_charge(packet: dict, description: str, amount: float, photo_filename: str = "") -> dict:
    """Record a charge the landlord listed."""
    return core.add_deduction(packet, description, amount, photo_filename)

@mcp.tool()
def draft_demand_letter(packet: dict, amount_requested: float, reasons: list[str], forwarding_address: str = "", rule_text_you_found: str = "") -> dict:
    """Draft (never send) a deposit demand letter from your facts. Cites a rule only if you typed it."""
    return core.demand_letter(packet, amount_requested, reasons, forwarding_address, rule_text_you_found)

@mcp.tool()
def photo_log(packet: dict) -> str:
    """Markdown table of every photo logged."""
    return core.photo_log_markdown(packet)

@mcp.tool()
def scope_check(text: str) -> dict:
    """Say so when a question asks what the law is or whether something is legal (this tool never answers that)."""
    return core.scope_check(text)

if __name__ == "__main__":
    mcp.run()
