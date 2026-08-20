#!/bin/bash
# Verifiziert nur das externe Verhalten von block-commit-session-url.sh (Exit-Code + stderr),
# nicht die interne Regex-Implementierung. Seam: JSON-Payload via stdin, wie Claude Code ihn liefert.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/block-commit-session-url.sh"

FAILURES=0

run_case() {
  local desc="$1" cmd="$2" expected_exit="$3"
  local payload actual_exit stderr_out
  payload=$(printf '{"tool_input":{"command":%s}}' "$(jq -Rs '.' <<<"$cmd")")
  stderr_out=$(echo "$payload" | "$HOOK" 2>&1 >/dev/null)
  actual_exit=$?
  if [ "$actual_exit" -ne "$expected_exit" ]; then
    echo "FAIL: $desc -- expected exit $expected_exit, got $actual_exit"
    FAILURES=$((FAILURES + 1))
    return
  fi
  if [ "$expected_exit" -eq 2 ] && [ -z "$stderr_out" ]; then
    echo "FAIL: $desc -- expected stderr message on block, got none"
    FAILURES=$((FAILURES + 1))
    return
  fi
  echo "PASS: $desc"
}

# Blockiert werden soll:
run_case "git commit mit Session-URL" 'git commit -m "fix: x

Claude-Session: https://claude.ai/code/session_01Abc"' 2
run_case "git -C /pfad commit mit Session-URL" 'git -C /pfad commit -m "Claude-Session: https://claude.ai/code/session_01Abc"' 2
run_case "compound mit add und commit" 'git add . && git commit -m "Claude-Session: https://claude.ai/code/session_01Abc"' 2

# Nicht blockiert werden soll:
run_case "git commit ohne Session-URL" 'git commit -m "fix: x"' 0
run_case "git status" "git status" 0
run_case "git push mit Session-URL im Nachrichtentext (kein commit)" 'git log --grep=session_01Abc' 0
run_case "Session-URL ausserhalb eines commit-Aufrufs" 'echo "https://claude.ai/code/session_01Abc"' 0

if [ "$FAILURES" -gt 0 ]; then
  echo "$FAILURES Test(s) fehlgeschlagen."
  exit 1
fi

echo "Alle Tests bestanden."
exit 0
