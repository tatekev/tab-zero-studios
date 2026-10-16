from mcp.server.fastmcp import FastMCP
import core
mcp = FastMCP("hoa-board-desk")

@mcp.tool()
def audit_outdated(text: str) -> list[dict]:
    """Flag lines in old HOA text that look out of date (past years or dates, placeholders)."""
    return core.audit(text)

@mcp.tool()
def make_faq(facts: list[dict]) -> str:
    """Build a Markdown FAQ from facts: [{q, a, source}]."""
    return core.build_faq(facts)

@mcp.tool()
def make_newsletter(name: str, month: str, news: list[str], dates: list[dict], reminders: list[str] = []) -> str:
    """Draft a monthly newsletter in Markdown. dates: [{date, what}]. Board reviews before sending."""
    return core.build_newsletter(name, month, news, dates, reminders)

@mcp.tool()
def make_site(name: str, intro: str, faq_md: str, newsletter_md: str, out_dir: str) -> list[str]:
    """Write a clean 3-page static site (home, FAQ, newsletter) into out_dir."""
    return core.build_site(name, intro, faq_md, newsletter_md, out_dir)

if __name__ == "__main__":
    mcp.run()
