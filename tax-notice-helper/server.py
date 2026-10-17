from mcp.server.fastmcp import FastMCP
import core
mcp = FastMCP("tax-notice-helper")

@mcp.tool()
def explain_tax_notice(text: str) -> dict:
    """Turn the text of an IRS or state tax letter into a plain answer, what to do, a reply-by date (only if it is in the text), and a reply checklist. Pass pasted text only. Not tax or legal advice."""
    return core.explain_notice(text)

@mcp.tool()
def explain_tax_notice_markdown(text: str) -> str:
    """Same as explain_tax_notice but as a short brain-friendly Markdown card with a tick-box reply checklist."""
    return core.to_markdown(core.explain_notice(text))

@mcp.tool()
def reply_checklist() -> list[str]:
    """The general reply checklist for any tax notice."""
    return core.REPLY_CHECKLIST

@mcp.tool()
def scope_check(text: str) -> dict:
    """Say so when a question asks whether to pay, dispute or ignore a notice (this tool never answers that)."""
    return core.scope_check(text)

if __name__ == "__main__":
    mcp.run()
