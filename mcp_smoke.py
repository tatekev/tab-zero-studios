import asyncio, sys, json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
async def go(d, tool, args):
    p = StdioServerParameters(command=sys.executable, args=["server.py"], cwd=d)
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = [t.name for t in (await s.list_tools()).tools]
            res = await s.call_tool(tool, args)
            print(d, tools, "->", res.content[0].text[:90].replace("\n"," "))
asyncio.run(go("unpack","unpack_letter_markdown",{"text":"Amount due $50 by 12/01/2026. Please pay online."}))
asyncio.run(go("cpa-doc-prep","make_checklist",{"profiles":["employee"]}))
asyncio.run(go("hoa-board-desk","audit_outdated",{"text":"Meeting 1/2/2020"}))
