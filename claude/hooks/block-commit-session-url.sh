#!/bin/bash
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

if echo "$CMD" | grep -qE '(^|&&|;|\|)\s*git\b(\s+(-C\s+\S+|-c\s+\S+|--no-pager))*\s+commit\b' \
  && echo "$CMD" | grep -qE 'claude\.ai/code/session_'; then
  echo "Guardrail: Commit-Message enthält eine Claude-Session-URL. Bitte entfernen." >&2
  exit 2
fi

exit 0
