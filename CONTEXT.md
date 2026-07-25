# Context

Persönliches dotfiles-Repo. Keine Anwendung mit Nutzern –
enthält Konfigurationsdateien, die per Symlink ins Home-Verzeichnis
eingebunden werden.

## Struktur

- `.bash_aliases`, `.emacs`, `.sqliterc`, `.wslconfig` – Shell-/Editor-/Tool-Configs,
  direkt per Symlink nach `~/`.
- `claude/` – Claude-Code-Konfiguration, per Symlink nach `~/.claude` eingebunden:
  - `CLAUDE.md` – globale Instruktionen für alle Projekte, die nach `~/.claude/CLAUDE.md` gelinkt wird.
  - `hooks/` – Claude-Code-Hooks (nicht Git-Hooks – siehe Glossar unten).
  - `scripts/` – Statusline u. Ä.
  - `skills/` – Custom Skills, je ein Unterordner mit `SKILL.md`.
- `.github/workflows/` – CI-Syntaxcheck für YAML/JSON/Frontmatter der Configs.

## Glossar

- **Hook** – meint in diesem Repo standardmäßig einen *Claude-Code-Hook*
  (`claude/hooks/`), nicht einen Git-Hook, sofern nicht anders gesagt.

## Konventionen

- Änderungen an `claude/*` wirken sich unmittelbar auf die eigene
  Claude-Code-Umgebung aus (Symlinks, kein Kopiervorgang).
- Commit-Messages folgen Conventional Commits.
- Keine Session-URL in Commits.

## ADRs

Architekturentscheidungen werden bei Bedarf unter `docs/adr/` abgelegt.

- [0001](docs/adr/0001-ci-syntax-check.md) – CI-Syntaxprüfung der Configs
