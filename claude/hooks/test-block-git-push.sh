#!/bin/bash
# Verifiziert nur das externe Verhalten von block-git-push.sh (Exit-Code + stderr),
# nicht die interne Regex-Implementierung. Seam: JSON-Payload via stdin, wie Claude Code ihn liefert.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/block-git-push.sh"

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
run_case "git push" "git push" 2
run_case "git push origin main" "git push origin main" 2
run_case "git push --force" "git push --force" 2
run_case "git -C /pfad push" "git -C /pfad push" 2
run_case "compound mit vorangestelltem commit" 'git add . && git commit -m "x" && git push' 2
run_case "git -c key=value push" "git -c user.name=x push" 2
run_case "git --no-pager push" "git --no-pager push" 2

# Nicht blockiert werden soll:
run_case "git commit" 'git commit -m "x"' 0
run_case "git status" "git status" 0
run_case "git log" "git log" 0
run_case "git add mit push im Dateinamen" "git add claude/hooks/block-git-push.sh" 0
run_case "git commit-message erwaehnt push" 'git commit -m "implement push button"' 0

if [ "$FAILURES" -gt 0 ]; then
  echo "$FAILURES Test(s) fehlgeschlagen."
  exit 1
fi

echo "Alle Tests bestanden."
exit 0
