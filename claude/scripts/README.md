# Claude Code Scripts

Diese Skripte liegen im dotfiles-Repo und werden per Symlink unter
`~/.claude/scripts` eingebunden:

```
ln -s ~/proj/dotfiles/claude/scripts ~/.claude/scripts
```

## statusline-command.sh

Status line abgeleitet aus der PS1-Konfiguration in `~/.bashrc`
(farbiger user@host + aktuelles Verzeichnis + Kontextauslastung).

Einbindung in `~/.claude/settings.json` (Symlink vorausgesetzt, daher
`$HOME`-Pfad statt absolutem dotfiles-Pfad):

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash \"$HOME/.claude/scripts/statusline-command.sh\""
  }
}
```

Voraussetzung: `jq` muss installiert sein (`brew install jq`).
