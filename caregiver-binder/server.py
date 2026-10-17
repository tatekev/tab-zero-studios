from mcp.server.fastmcp import FastMCP
import core
mcp = FastMCP("caregiver-binder")

@mcp.tool()
def start_binder(person_name: str, prepared_by: str = "", note: str = "") -> dict:
    """Start a binder. Your app keeps it between calls. It stores locations and contacts only, never passwords."""
    return core.new_binder(person_name, prepared_by, note)

@mcp.tool()
def add_account(binder: dict, name: str, account_type: str, kept_where: str, last4: str = "", contact_phone: str = "", note: str = "") -> dict:
    """Add an account. kept_where = WHERE the login is kept (like 'password manager'), never the login. Types: bank, credit_card, loan_mortgage, insurance, utility, phone_internet, email, subscription, social_media, government, retirement_investment, other."""
    return core.add_account(binder, name, account_type, kept_where, last4, contact_phone, note)

@mcp.tool()
def add_document(binder: dict, name: str, doc_type: str, location: str, held_by: str = "", note: str = "") -> dict:
    """Add a document and where it is. Types: will, power_of_attorney, healthcare_directive, insurance_policy, deed_title, birth_marriage_certificate, tax_returns, medication_list, id_card, vehicle_title, other."""
    return core.add_document(binder, name, doc_type, location, held_by, note)

@mcp.tool()
def add_contact(binder: dict, name: str, role: str, phone: str = "", email: str = "", call_first: bool = False, note: str = "") -> dict:
    """Add a person to call. Mark call_first for the first people to call."""
    return core.add_contact(binder, name, role, phone, email, call_first, note)

@mcp.tool()
def add_checklist_step(binder: dict, text: str, when: str = "First 72 hours") -> dict:
    """Add your own step to the first-72-hours checklist."""
    return core.add_step(binder, text, when)

@mcp.tool()
def tick_step(binder: dict, step_id: str, done: bool = True) -> dict:
    """Tick a checklist step."""
    return core.tick(binder, step_id, done)

@mcp.tool()
def find_gaps(binder: dict) -> list[str]:
    """What is still missing from the binder."""
    return core.gaps(binder)

@mcp.tool()
def print_binder(binder: dict) -> str:
    """The whole binder as printable Markdown."""
    return core.to_markdown(binder)

@mcp.tool()
def scope_check(text: str) -> dict:
    """Say so when a question asks for legal, medical or financial advice (this tool never answers that)."""
    return core.scope_check(text)

if __name__ == "__main__":
    mcp.run()
