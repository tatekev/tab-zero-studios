"""Real MCP-over-stdio check for all 3 servers. Run: .venv/bin/python mcp_smoke.py  (exit 0 = all pass)."""
import asyncio, sys, json, os, tempfile
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
HERE = os.path.dirname(os.path.abspath(__file__))
results = []
def check(name, ok, detail=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + ((" -- " + detail) if (detail and not ok) else ""))
def data(res):
    if res.structuredContent is not None:
        sc = res.structuredContent
        return sc.get("result", sc) if isinstance(sc, dict) and list(sc) == ["result"] else sc
    return json.loads(res.content[0].text) if res.content[0].text[:1] in "[{" else res.content[0].text
async def session(d):
    p = StdioServerParameters(command=sys.executable, args=["server.py"], cwd=os.path.join(HERE, d))
    return stdio_client(p)
async def unpack():
    async with await session("unpack") as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            names = sorted(t.name for t in (await s.list_tools()).tools)
            check("unpack: tools listed", names == ["unpack_letter", "unpack_letter_markdown"], str(names))
            x = data(await s.call_tool("unpack_letter", {"text": "FINAL NOTICE. Amount due $50. Pay by 12/01/2099 or service will be disconnected."}))
            check("unpack: 3 answers + disclaimer", all(k in x for k in ("what_is_this", "what_to_do", "by_when", "urgency", "first_tiny_step", "disclaimer")) and x["by_when"].startswith("2099-12-01"), str(x)[:200])
            x = data(await s.call_tool("unpack_letter", {"text": "Thanks for being a member."}))
            check("unpack: no deadline says so", x["by_when"].startswith("No clear date found"), x["by_when"])
            m = data(await s.call_tool("unpack_letter_markdown", {"text": "Pay by 12/01/2099. SSN 123-45-6789"}))
            check("unpack: markdown card hides SSN", "## By when?" in m and "123-45-6789" not in m, m)
            x = data(await s.call_tool("unpack_letter", {"text": ""}))
            check("unpack: empty input handled", x["urgency"] == "unknown")
async def cpa():
    async with await session("cpa-doc-prep") as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            names = sorted(t.name for t in (await s.list_tools()).tools)
            check("cpa: tools listed", names == ["check_sensitive", "checklist_summary", "draft_preparer_message", "make_checklist", "mark_item", "scope_check"], str(names))
            c = data(await s.call_tool("make_checklist", {"profiles": ["employee", "homeowner"]}))
            check("cpa: checklist built", len(c) >= 6 and all(i["status"] == "missing" for i in c))
            c = data(await s.call_tool("mark_item", {"checklist": c, "item_id": "w2", "status": "received"}))
            sm = data(await s.call_tool("checklist_summary", {"checklist": c}))
            check("cpa: tracking works", sm["counts"]["received"] == 1, str(sm["counts"]))
            ss = data(await s.call_tool("check_sensitive", {"text": "ssn 123 45 6789"}))
            check("cpa: SSN flagged, not echoed", ss["has_ssn"] and "6789" not in json.dumps(ss), str(ss))
            d = data(await s.call_tool("draft_preparer_message", {"checklist": c, "preparer": "Sample CPA", "sender": "Sample Client", "channel": "text"}))
            check("cpa: text draft", d["channel"] == "text" and "Ready for you" in d["draft"] and "Nothing was sent" in d["note"], str(d)[:200])
            bad = await s.call_tool("draft_preparer_message", {"checklist": c, "note": "my ssn 123-45-6789"})
            check("cpa: draft refuses SSN (tool error)", bad.isError and "123-45-6789" not in bad.content[0].text, str(bad)[:200])
            q = data(await s.call_tool("scope_check", {"text": "how much tax will I owe"}))
            check("cpa: refuses tax advice", q["is_tax_advice_request"])
            bad = await s.call_tool("make_checklist", {"profiles": ["astronaut"]})
            check("cpa: unknown profile is a clear error", bad.isError and "Valid profiles" in bad.content[0].text)
async def hoa():
    async with await session("hoa-board-desk") as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            names = sorted(t.name for t in (await s.list_tools()).tools)
            check("hoa: tools listed", names == ["audit_outdated", "make_faq", "make_newsletter", "make_site"], str(names))
            a = data(await s.call_tool("audit_outdated", {"text": "Meeting 1/2/2020\nPool coming soon\nAll good"}))
            a = a if isinstance(a, list) else a.get("result", a)
            check("hoa: audit flags 2 lines", [f["line"] for f in a] == [1, 2], str(a))
            faq = data(await s.call_tool("make_faq", {"facts": [{"q": "Dues?", "a": "Quarterly.", "source": "Sample Bylaws"}]}))
            check("hoa: faq cites source", "Source: Sample Bylaws" in faq)
            nl = data(await s.call_tool("make_newsletter", {"name": "Sample Oaks HOA", "month": "Nov 2026", "news": ["Hi"], "dates": [{"date": "Nov 5", "what": "Meeting"}]}))
            check("hoa: newsletter", "Nov 5" in nl and "board review" in nl)
            with tempfile.TemporaryDirectory() as td:
                f = data(await s.call_tool("make_site", {"name": "Sample Oaks HOA", "intro": "Welcome", "faq_md": faq, "newsletter_md": nl, "out_dir": td}))
                check("hoa: 3-page site written", sorted(os.listdir(td)) == ["faq.html", "index.html", "newsletter.html"] and 'lang="en"' in open(os.path.join(td, "index.html"), encoding="utf-8").read(), str(f))
for fn in (unpack, cpa, hoa):
    asyncio.run(fn())
print(f"\n{sum(results)}/{len(results)} MCP checks passed"); sys.exit(0 if all(results) else 1)
