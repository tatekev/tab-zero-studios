#!/usr/bin/env bash
# One command self-check. Prints ALL GOOD or PROBLEM at the end.
cd "$(dirname "$0")" || exit 1
PY=".venv/bin/python"; [ -x "$PY" ] || PY="python3"
fail=0
for d in unpack cpa-doc-prep hoa-board-desk; do
  echo "== $d"; (cd "$d" && "../$PY" -m pytest -q 2>&1 | tail -2) || true
  (cd "$d" && "../$PY" -m pytest -q >/dev/null 2>&1) || fail=1
done
echo "== MCP over stdio"; "$PY" mcp_smoke.py 2>&1 | grep -E "^(PASS|FAIL)|checks passed"
"$PY" mcp_smoke.py >/dev/null 2>&1 || fail=1
[ $fail = 0 ] && echo "ALL GOOD" || echo "PROBLEM: something failed. Do not submit. Send this screen to Cornelius."
exit $fail
