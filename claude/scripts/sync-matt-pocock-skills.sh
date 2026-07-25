#!/bin/bash
# Vergleicht die importierten Matt-Pocock-Skills gegen den aktuellen Stand von
# https://github.com/mattpocock/skills und zeigt Abweichungen als Diff an.
# Überschreibt nichts – Übernahme erfolgt manuell nach Prüfung des Diffs.
#
# Aufruf: claude/scripts/sync-matt-pocock-skills.sh

set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../skills" && pwd)"
BASE_URL="https://raw.githubusercontent.com/mattpocock/skills/main/skills"

locals=(
  "to-tickets/SKILL.md"
  "to-spec/SKILL.md"
  "teach/SKILL.md"
  "teach/GLOSSARY-FORMAT.md"
  "teach/LEARNING-RECORD-FORMAT.md"
  "teach/MISSION-FORMAT.md"
  "teach/RESOURCES-FORMAT.md"
  "teach/agents/openai.yaml"
  "implement/SKILL.md"
  "tdd/SKILL.md"
  "tdd/mocking.md"
  "tdd/tests.md"
  "grilling/SKILL.md"
  "grilling/agents/openai.yaml"
  "grill-me/SKILL.md"
  "grill-me/agents/openai.yaml"
  "setup-matt-pocock-skills/SKILL.md"
  "setup-matt-pocock-skills/domain.md"
  "setup-matt-pocock-skills/issue-tracker-github.md"
  "setup-matt-pocock-skills/issue-tracker-gitlab.md"
  "setup-matt-pocock-skills/issue-tracker-local.md"
  "setup-matt-pocock-skills/triage-labels.md"
  "mp-code-review/SKILL.md"
  "mp-code-review/agents/openai.yaml"
)
ups=(
  "engineering/to-tickets/SKILL.md"
  "engineering/to-spec/SKILL.md"
  "productivity/teach/SKILL.md"
  "productivity/teach/GLOSSARY-FORMAT.md"
  "productivity/teach/LEARNING-RECORD-FORMAT.md"
  "productivity/teach/MISSION-FORMAT.md"
  "productivity/teach/RESOURCES-FORMAT.md"
  "productivity/teach/agents/openai.yaml"
  "engineering/implement/SKILL.md"
  "engineering/tdd/SKILL.md"
  "engineering/tdd/mocking.md"
  "engineering/tdd/tests.md"
  "productivity/grilling/SKILL.md"
  "productivity/grilling/agents/openai.yaml"
  "productivity/grill-me/SKILL.md"
  "productivity/grill-me/agents/openai.yaml"
  "engineering/setup-matt-pocock-skills/SKILL.md"
  "engineering/setup-matt-pocock-skills/domain.md"
  "engineering/setup-matt-pocock-skills/issue-tracker-github.md"
  "engineering/setup-matt-pocock-skills/issue-tracker-gitlab.md"
  "engineering/setup-matt-pocock-skills/issue-tracker-local.md"
  "engineering/setup-matt-pocock-skills/triage-labels.md"
  "engineering/code-review/SKILL.md"
  "engineering/code-review/agents/openai.yaml"
)
# lokal: mp-code-review, entspricht upstream engineering/code-review – umbenannt
# wegen Namenskollision mit dem eingebauten /code-review-Befehl (siehe ADR).

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

drift=0
for i in "${!locals[@]}"; do
  local="${locals[$i]}"
  up="${ups[$i]}"
  local_path="$SKILLS_DIR/$local"
  curl -sf "$BASE_URL/$up" -o "$tmp" || {
    echo "FEHLER beim Abruf: $up"
    continue
  }
  if [ ! -f "$local_path" ]; then
    echo "NEU UPSTREAM (lokal fehlt): $local"
    drift=1
    continue
  fi
  if diff -q "$tmp" "$local_path" >/dev/null 2>&1; then
    continue
  fi
  drift=1
  echo "=== $local ==="
  diff "$local_path" "$tmp" || true
  echo
done

if [ "$drift" -eq 0 ]; then
  echo "Keine Abweichungen von mattpocock/skills."
fi
