# 0001: GitHub-Actions-Workflow für Syntaxprüfung der Configs

## Status
Angenommen (2026-07-24)

## Kontext
Configdateien (YAML/JSON, Skill-Frontmatter) werden per Symlink direkt
wirksam – ein Syntaxfehler bricht sofort die reale Umgebung, nicht erst
einen Build. Es gab keine automatische Prüfung vor dem Merge.

## Entscheidung
Ein CI-Workflow (`.github/workflows/syntax-check.yml`) prüft bei jedem
Push/PR YAML, JSON und Skill-Frontmatter auf Syntaxfehler. `tidy` im
HTML-Job schlägt nur bei echten Errors fehl, nicht bei Warnings.

## Konsequenzen
- Fehler werden vor dem Merge sichtbar statt erst live in `~/.claude`.
- Zusätzlicher CI-Lauf bei jedem Push.
- Erfordert `actions/checkout` und `setup-python` aktuell zu halten.
