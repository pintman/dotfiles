---
name: conventional-commits
description: Schreibt Commit-Messages im Conventional-Commits-Stil.
  Nutze diesen Skill, wenn ein Git-Commit erstellt werden soll.
---

# Conventional Commits

Wenn du einen Commit erstellst, halte dich an dieses Format:

<type>(<scope>): <kurze Beschreibung>

## Erlaubte Types
- feat: neue Funktion
- fix: Bugfix
- docs: nur Dokumentation
- refactor: Code-Umbau ohne Verhaltensänderung
- test: Tests hinzufügen oder anpassen

## Regeln
- Beschreibung im Imperativ, klein, ohne Punkt am Ende.
- Maximal 72 Zeichen in der ersten Zeile.
- Body nur bei nicht-trivialen Änderungen.
- Erwähne Claude als Co-Author wenn angebracht.
- Keine Session-URL in den Commit-Kommentar.
