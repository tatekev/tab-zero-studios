from mcp.server.fastmcp import FastMCP
from core import unpack, to_markdown
mcp = FastMCP("unpack")

@mcp.tool()
def unpack_letter(text: str) -> dict:
    """Break a confusing letter or bill into what it is, what to do, and by when. Pass pasted text only (no SSNs or card numbers)."""
    return unpack(text)

@mcp.tool()
def unpack_letter_markdown(text: str) -> str:
    """Same as unpack_letter, but a short, brain-friendly Markdown card."""
    return to_markdown(unpack(text))

if __name__ == "__main__":
    mcp.run()
