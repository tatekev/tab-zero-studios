from mcp.server.fastmcp import FastMCP
import core
mcp = FastMCP("gig-tax-organizer")

@mcp.tool()
def start_book(tax_year: int, name: str = "", note: str = "") -> dict:
    """Start an empty record book for a tax year. Your app keeps the book between calls."""
    return core.new_book(tax_year, name, note)

@mcp.tool()
def usual_payment_dates(tax_year: int) -> list[dict]:
    """The usual calendar dates for quarterly estimated payments. Suggestions only; confirm on IRS.gov or with your preparer."""
    return core.usual_dates(tax_year)

@mcp.tool()
def save_due_dates(book: dict, items: list[dict]) -> dict:
    """Save the due dates YOU confirmed. items: [{"label": "Q1", "date": "2026-04-15"}]."""
    return core.set_due_dates(book, items)

@mcp.tool()
def upcoming_reminders(book: dict) -> list[dict]:
    """Days left to each saved due date."""
    return core.reminders(book)

@mcp.tool()
def log_trip(book: dict, date: str, miles: float, purpose: str, start: str = "", end: str = "", note: str = "") -> dict:
    """Add one mileage log entry (date as YYYY-MM-DD). Does not value the miles."""
    return core.add_trip(book, date, miles, purpose, start, end, note)

@mcp.tool()
def log_receipt(book: dict, date: str, vendor: str, amount: float, category: str = "other", note: str = "", has_photo: bool = False) -> dict:
    """Add one receipt entry. Categories: supplies, phone_internet, software_subscriptions, vehicle_costs, parking_tolls, equipment, advertising, fees_platform, meals, travel, education, professional_services, other."""
    return core.add_receipt(book, date, vendor, amount, category, note, has_photo)

@mcp.tool()
def log_income(book: dict, date: str, source: str, amount: float, note: str = "") -> dict:
    """Add one payment you were paid."""
    return core.add_income(book, date, source, amount, note)

@mcp.tool()
def log_estimated_payment(book: dict, date: str, label: str, amount: float, confirmation_last4: str = "") -> dict:
    """Log an estimated tax payment you already made (last digits of the confirmation only)."""
    return core.add_payment(book, date, label, amount, confirmation_last4)

@mcp.tool()
def entry_totals(book: dict) -> dict:
    """Totals of what you typed (not deductions, not tax)."""
    return core.totals(book)

@mcp.tool()
def find_gaps(book: dict) -> list[str]:
    """List missing purposes, photos, odd dates, and possible double entries."""
    return core.gaps(book)

@mcp.tool()
def export_csv(book: dict, which: str) -> str:
    """CSV text for trips, receipts, income, or payments."""
    return core.to_csv(book, which)

@mcp.tool()
def import_csv(book: dict, which: str, text: str) -> dict:
    """Load rows from a filled-in CSV (same headers as export_csv)."""
    return core.from_csv(book, which, text)

@mcp.tool()
def preparer_packet(book: dict, preparer: str = "your preparer") -> str:
    """One-page Markdown year-end packet for a tax preparer. No tax math."""
    return core.handoff_packet(book, preparer)

@mcp.tool()
def scope_check(text: str) -> dict:
    """Say so when a question asks for tax, deductions, or an amount owed (this tool never answers that)."""
    return core.scope_check(text)

if __name__ == "__main__":
    mcp.run()
