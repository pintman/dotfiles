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

## block-git-push.sh

Blockiert jeden `git push`-Aufruf, den Claude Code über das Bash-Tool
ausführen will — hart und ohne Umgehungsmöglichkeit. `git commit` bleibt
uneingeschränkt. Der Nutzer pusht in diesem Fall selbst im Terminal.

Einbindung in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "$HOME/.claude/hooks/block-git-push.sh" }
        ]
      }
    ]
  }
}
```

Voraussetzung: `jq` muss installiert sein (`brew install jq`).

Test: `claude/hooks/test-block-git-push.sh` prüft nur das externe Verhalten
(Exit-Code + `stderr`), nicht die interne Regex.
