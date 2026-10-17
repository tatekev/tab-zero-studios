"""Real MCP-over-stdio check for the 6 new servers. Run: .venv/bin/python mcp_smoke_new.py (exit 0 = all pass)."""
import asyncio, sys, json, os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
HERE = os.path.dirname(os.path.abspath(__file__))
results = []
def check(name, ok, detail=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + ((" -- " + detail[:200]) if (detail and not ok) else ""))
def data(res):
    if res.structuredContent is not None:
        sc = res.structuredContent
        return sc.get("result", sc) if isinstance(sc, dict) and list(sc) == ["result"] else sc
    t = res.content[0].text
    return json.loads(t) if t[:1] in "[{" else t
async def run(d, fn):
    p = StdioServerParameters(command=sys.executable, args=["server.py"], cwd=os.path.join(HERE, d))
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize(); await fn(s)
async def refused(s, tool, args):
    res = await s.call_tool(tool, args)
    txt = res.content[0].text if res.content else ""
    return bool(res.isError) and "123-45-6789" not in txt
async def tax(s):
    n = {t.name for t in (await s.list_tools()).tools}
    check("tax-notice-helper: tools", n == {"explain_tax_notice", "explain_tax_notice_markdown", "reply_checklist", "scope_check"}, str(n))
    x = data(await s.call_tool("explain_tax_notice", {"text": "Internal Revenue Service Notice CP14. You owe $50. Pay by 2099-12-01. SSN 123-45-6789"}))
    check("tax-notice-helper: answer + deadline + SSN hidden", x["reply_by"].startswith("2099-12-01") and "123-45-6789" not in json.dumps(x))
    x = data(await s.call_tool("explain_tax_notice", {"text": "Notice CP2000 from the IRS. Please review."}))
    check("tax-notice-helper: no date invented", x["reply_by_found"] is False)
async def gig(s):
    n = {t.name for t in (await s.list_tools()).tools}
    check("gig-tax-organizer: tools", len(n) == 14 and "preparer_packet" in n, str(n))
    b = data(await s.call_tool("start_book", {"tax_year": 2026}))
    b = data(await s.call_tool("log_trip", {"book": b, "date": "2026-03-02", "miles": 12.5, "purpose": "Airport"}))
    b = data(await s.call_tool("log_receipt", {"book": b, "date": "2026-03-03", "vendor": "Shop", "amount": 20, "category": "supplies"}))
    t = data(await s.call_tool("entry_totals", {"book": b}))
    check("gig-tax-organizer: totals", t["miles_logged"] == 12.5 and t["receipts_total_entered"] == 20)
    p = data(await s.call_tool("preparer_packet", {"book": b}))
    check("gig-tax-organizer: packet", "No tax has been calculated" in p)
    check("gig-tax-organizer: refuses SSN", await refused(s, "log_trip", {"book": b, "date": "2026-03-02", "miles": 1, "purpose": "123-45-6789"}))
async def med(s):
    n = {t.name for t in (await s.list_tools()).tools}
    check("medical-bill-appeal-kit: tools", len(n) == 11 and "draft_appeal_letter" in n, str(n))
    c = data(await s.call_tool("start_case", {"patient_name": "Sample Patient", "provider": "Sample Hospital"}))
    c = data(await s.call_tool("add_deadline", {"case": c, "label": "Appeal", "source": "letter p2", "start_date": "2099-01-01", "days": 30}))
    t = data(await s.call_tool("deadline_tracker", {"case": c}))
    check("medical-bill-appeal-kit: tracker", t[0]["due"] == "2099-01-31")
    d = data(await s.call_tool("draft_itemized_bill_request", {"case": c, "date_of_service": "2026-09-03"}))
    check("medical-bill-appeal-kit: draft only", "Nothing was sent" in d["note"])
    check("medical-bill-appeal-kit: refuses SSN", await refused(s, "start_case", {"patient_name": "123-45-6789", "provider": "x"}))
async def lease(s):
    n = {t.name for t in (await s.list_tools()).tools}
    check("lease-end-deposit-packet: tools", len(n) == 11 and "draft_demand_letter" in n, str(n))
    p = data(await s.call_tool("start_packet", {"tenant": "T", "landlord": "L", "property_address": "1 Sample St", "move_in_date": "2024-01-01", "move_out_date": "2099-01-01"}))
    p = data(await s.call_tool("add_deadline_rule", {"packet": p, "label": "Return", "days": 30, "starts": "move_out_date", "source": "lease s.4"}))
    t = data(await s.call_tool("deadline_tracker", {"packet": p}))
    check("lease-end-deposit-packet: user rule tracked", t[0]["due"] == "2099-01-31")
    check("lease-end-deposit-packet: rule without source refused", await refused(s, "add_deadline_rule", {"packet": p, "label": "x", "days": 5, "starts": "other", "source": ""}))
async def hoa(s):
    n = {t.name for t in (await s.list_tools()).tools}
    check("hoa-compliance-desk: tools", len(n) == 11 and "lake_crest_demo" in n, str(n))
    h = data(await s.call_tool("lake_crest_demo", {}))
    check("hoa-compliance-desk: demo marked", h["demo"] is True)
    r = data(await s.call_tool("plan_meeting_notice", {"hoa": h, "meeting_date": "2099-12-10", "time": "7 PM", "place": "Clubhouse", "agenda": ["Budget"]}))
    check("hoa-compliance-desk: send-by", r["send_by"] == "2099-11-19", str(r)[:150])
async def care(s):
    n = {t.name for t in (await s.list_tools()).tools}
    check("caregiver-binder: tools", len(n) == 9 and "print_binder" in n, str(n))
    b = data(await s.call_tool("start_binder", {"person_name": "Sample Person"}))
    b = data(await s.call_tool("add_contact", {"binder": b, "name": "Pat", "role": "Sister", "phone": "555-123-4567", "call_first": True}))
    m = data(await s.call_tool("print_binder", {"binder": b}))
    check("caregiver-binder: prints", "CALL FIRST" in m and "First 72 hours" in m)
    check("caregiver-binder: refuses password", await refused(s, "add_account", {"binder": b, "name": "Bank", "account_type": "bank", "kept_where": "password: hunter2"}))
async def main():
    for d, f in (("tax-notice-helper", tax), ("gig-tax-organizer", gig), ("medical-bill-appeal-kit", med), ("lease-end-deposit-packet", lease), ("hoa-compliance-desk", hoa), ("caregiver-binder", care)):
        try: await run(d, f)
        except Exception as e: check(d + ": ran", False, repr(e))
    print(f"{sum(results)}/{len(results)} checks passed"); sys.exit(0 if all(results) else 1)
asyncio.run(main())
