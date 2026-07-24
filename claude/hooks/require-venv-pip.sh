#!/bin/bash
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

IS_PIP_INSTALL=$(echo "$CMD" | grep -qE '(^|&&|;|\|)\s*(pip[3]?\s+install|python[3]?\s+-m\s+pip\s+install)' && echo yes)
HAS_ACTIVATE=$(echo "$CMD" | grep -qE '\bactivate\b' && echo yes)
HAS_VENV_WORD=$(echo "$CMD" | grep -qE '(venv|virtualenv)' && echo yes)
if [ "$HAS_ACTIVATE" = "yes" ] && [ "$HAS_VENV_WORD" = "yes" ]; then
  HAS_VENV=yes
else
  HAS_VENV=no
fi

if [ "$IS_PIP_INSTALL" = "yes" ] && [ "$HAS_VENV" != "yes" ]; then
  echo "Guardrail: pip install nur in einem temporaeren venv. Beispiel: python3 -m venv /tmp/venv-demo && source /tmp/venv-demo/bin/activate && pip install <paket>" >&2
  exit 2
fi

exit 0
