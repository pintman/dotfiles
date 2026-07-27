#!/bin/bash
# Holt den brave-search-Skill frisch von https://github.com/badlogic/pi-skills
# und legt ihn unter ~/.agents/skills/brave-search ab. Überschreibt bestehende
# Dateien vollständig (curl statt Copy-Paste, vermeidet Encoding-Korruption).
#
# Aufruf: scripts/fetch-brave-search-skill.sh

set -euo pipefail

SKILL_DIR="$HOME/.agents/skills/brave-search"
API_URL="https://api.github.com/repos/badlogic/pi-skills/contents/brave-search"

mkdir -p "$SKILL_DIR"

curl -sf "$API_URL" | jq -r '.[] | select(.type == "file") | "\(.name)\t\(.download_url)"' |
while IFS=$'\t' read -r name url; do
  echo "Hole $name ..."
  curl -sf "$url" -o "$SKILL_DIR/$name"
done

echo "brave-search-Skill aktualisiert in $SKILL_DIR"
