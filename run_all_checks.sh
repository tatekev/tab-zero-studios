#!/usr/bin/env bash
# One command self-check. Prints ALL GOOD or PROBLEM at the end.
cd "$(dirname "$0")" || exit 1
PY="$PWD/.venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "First run: setting up a private Python environment (about 30 seconds)..."
  python3 -m venv .venv && "$PY" -m pip install -q -r requirements.txt || { echo "PROBLEM: install failed. Python 3.10 or newer is required."; exit 1; }
fi
fail=0
for d in unpack cpa-doc-prep hoa-board-desk tax-notice-helper gig-tax-organizer medical-bill-appeal-kit lease-end-deposit-packet hoa-compliance-desk caregiver-binder; do
  echo "== $d"; (cd "$d" && "$PY" -m pytest -q 2>&1 | tail -2) || true
  (cd "$d" && "$PY" -m pytest -q >/dev/null 2>&1) || fail=1
done
echo "== MCP over stdio"; "$PY" mcp_smoke.py 2>&1 | grep -E "^(PASS|FAIL)|checks passed"
"$PY" mcp_smoke.py >/dev/null 2>&1 || fail=1
echo "== MCP new tools"; "$PY" mcp_smoke_new.py 2>&1 | grep -E "^(PASS|FAIL)|checks passed"
"$PY" mcp_smoke_new.py >/dev/null 2>&1 || fail=1
echo "== End-user walk-through over MCP"; "$PY" mcp_end_user.py 2>&1 | grep -E "^(FAIL)|checks passed"
"$PY" mcp_end_user.py >/dev/null 2>&1 || fail=1
[ $fail = 0 ] && echo "ALL GOOD" || echo "PROBLEM: something failed. Do not submit. Send this screen to Cornelius."
exit $fail
