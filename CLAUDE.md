# Globale Anweisungen für Claude Code

Diese Datei gilt projektübergreifend für alle Repositories und Arbeitsverzeichnisse.

## Sprache

Antworte standardmäßig auf Deutsch, sofern der Nutzer nicht explizit Englisch verwendet oder danach fragt.

## Arbeitsweise

- Kurze, direkte Antworten bevorzugen – keine langen Zusammenfassungen am Ende, wenn der Nutzer den Diff/die Änderung selbst lesen kann.
- Bei git: niemals force-push, `reset --hard` oder andere destruktive Befehle ohne ausdrückliche Bestätigung.
- Vor größeren Änderungen an unbekannten Repositories erst kurz Kontext erfragen (Art des Projekts, ob Git-Repo, ob produktiv genutzt).

## Editor

- Der Nutzer verwendet Emacs. Emacs legt Backup-Dateien mit `~`-Suffix an (z. B. `Datei.md~`).
- Bei Bitten um „aufräumen“ dürfen `*~`-Dateien ohne Rückfrage gelöscht werden.
