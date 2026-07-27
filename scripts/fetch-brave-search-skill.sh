#!/bin/bash
# Holt den brave-search-Skill frisch von https://github.com/badlogic/pi-skills
# und legt ihn unter ~/.agents/skills/brave-search ab. Klont dafür flach in ein
# Temp-Verzeichnis und kopiert den Unterordner rüber, statt Dateien einzeln
# aufzuzählen – erfasst so auch künftige Unterordner im Skill.
#
# Aufruf: scripts/fetch-brave-search-skill.sh

set -euo pipefail

SKILL_DIR="$HOME/.agents/skills/brave-search"
REPO_URL="https://github.com/badlogic/pi-skills.git"

TMP_DIR="$(mktemp -d)"
# Räumt TMP_DIR auch bei Fehlern/Abbruch auf, nicht nur beim regulären Ende.
trap 'rm -rf "$TMP_DIR"' EXIT

git clone --depth 1 --quiet "$REPO_URL" "$TMP_DIR"

rm -rf "$SKILL_DIR"
mkdir -p "$(dirname "$SKILL_DIR")"
cp -R "$TMP_DIR/brave-search" "$SKILL_DIR"

echo "brave-search-Skill aktualisiert in $SKILL_DIR"
