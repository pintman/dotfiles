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

## sync-matt-pocock-skills.sh

Vergleicht die importierten Skills aus [mattpocock/skills](https://github.com/mattpocock/skills)
(`to-tickets`, `to-spec`, `teach`, `implement`, `tdd`, `grilling`, `grill-me`,
`setup-matt-pocock-skills`, `mp-code-review`) gegen den aktuellen Upstream-Stand
und zeigt Abweichungen als Diff. Überschreibt nichts – die Übernahme einzelner
Änderungen erfolgt manuell nach Prüfung. On-Demand-Aufruf, kein Scheduling; siehe
`docs/adr/0002-matt-pocock-skills-kein-plugin.md`.

```
claude/scripts/sync-matt-pocock-skills.sh
```
