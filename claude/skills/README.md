# Claude Code Skills

Diese Skills liegen im dotfiles-Repo und werden per Symlink unter
`~/.claude/skills` eingebunden:

```
ln -s ~/proj/dotfiles/claude/skills ~/.claude/skills
```

Jeder Unterordner ist ein eigenständiger Skill (`SKILL.md` + ggf.
weitere Ressourcen), der von Claude Code automatisch erkannt und über
den Namen des Ordners aufgerufen werden kann.
