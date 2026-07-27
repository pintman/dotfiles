#!/bin/bash
# Holt den brave-search-Skill frisch von https://github.com/badlogic/pi-skills
# und legt ihn unter ~/.agents/skills/brave-search ab. Überschreibt bestehende
# Dateien vollständig (curl statt Copy-Paste, vermeidet Encoding-Korruption).
#
# Aufruf: scripts/fetch-brave-search-skill.sh

set -euo pipefail

SKILL_DIR="$HOME/.agents/skills/brave-search"
BASE_URL="https://raw.githubusercontent.com/badlogic/pi-skills/main/brave-search"

files=(
  "SKILL.md"
  "content.js"
  "search.js"
  "package.json"
  "package-lock.json"
)

mkdir -p "$SKILL_DIR"

for f in "${files[@]}"; do
  echo "Hole $f ..."
  curl -sf "$BASE_URL/$f" -o "$SKILL_DIR/$f"
done

echo "brave-search-Skill aktualisiert in $SKILL_DIR"
