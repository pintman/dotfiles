# Claude Code Konfiguration

Diese Ordner liegen im dotfiles-Repo und werden per Symlink unter
`~/.claude` eingebunden:

```
ln -s ~/proj/dotfiles/claude/CLAUDE.md ~/.claude/CLAUDE.md
ln -s ~/proj/dotfiles/claude/hooks ~/.claude/hooks
ln -s ~/proj/dotfiles/claude/scripts ~/.claude/scripts
ln -s ~/proj/dotfiles/claude/skills ~/.claude/skills
ln -s ~/proj/dotfiles/claude/settings.json ~/.claude/settings.json
```

## Inhalt

- `CLAUDE.md` – globale Instruktionen für alle Projekte.
- `hooks/` – siehe [hooks/README.md](hooks/README.md).
- `scripts/` – siehe [scripts/README.md](scripts/README.md).
- `skills/` – siehe [skills/README.md](skills/README.md).
- `settings.json` – globale Claude-Code-Settings (u. a. `permissions.deny`, hooks, voice, statusLine).
