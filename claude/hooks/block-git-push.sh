#!/bin/bash
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

if echo "$CMD" | grep -qE '(^|&&|;|\|)\s*git\b(\s+(-C\s+\S+|-c\s+\S+|--no-pager))*\s+push\b'; then
  echo "Guardrail: git push ist für Claude Code gesperrt. Bitte selbst im Terminal pushen." >&2
  exit 2
fi

exit 0
