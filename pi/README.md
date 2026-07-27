# Pi Coding Agent Konfiguration

Dieser Ordner liegt im dotfiles-Repo und wird per Symlink unter
`~/.pi` eingebunden:

```
ln -s ~/proj/dotfiles/pi/extensions ~/.pi/extensions
```

## Inhalt

- `extensions/smart-footer.ts` – zeigt Cwd, Tokenzahl und Status kompakt in der Fußzeile an.
