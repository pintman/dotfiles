# Dotfiles

Configfiles for my setup

## Inhalt

- `claude/` – Konfiguration von Claude Code, s. [claude/README.md](claude/README.md).
- `pi/` – Konfiguration von [pi](https://pi.dev) (Coding Agent bzw. agent harness), s. [pi/README.md](pi/README.md).
- `scripts/fetch-brave-search-skill.sh` – lädt den brave-search-Skill für pi herunter nach `~/.agents/skills/brave-search`.
- `git-hooks/pre-commit` – Git-Hook, prüft Python-Dateien vor jedem Commit mit ruff. Aktivieren mit `git config core.hooksPath git-hooks`.
