# Claude Code Hooks

Diese Skripte liegen im dotfiles-Repo und werden per Symlink unter
`~/.claude/hooks` eingebunden:

```
ln -s ~/proj/dotfiles/claude/hooks ~/.claude/hooks
```

## require-venv-pip.sh

Blockiert `pip install` außerhalb eines aktivierten venv/virtualenv.

Einbindung in `~/.claude/settings.json` (Symlink vorausgesetzt, daher
`$HOME`-Pfad statt absolutem dotfiles-Pfad):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "$HOME/.claude/hooks/require-venv-pip.sh" }
        ]
      }
    ]
  }
}
```

Voraussetzung: `jq` muss installiert sein (`brew install jq`).
