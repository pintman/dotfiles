---
name: setup-chrome-agent
description: >
  Prüft, ob chrome-agent (CLI zur Chrome-Ansteuerung, u. a. für den
  webuntis-klausur-Skill) installiert ist, und installiert es andernfalls
  passend zum vorhandenen Browser (Vivaldi-Fork oder Standard-chrome-agent
  via pipx). Nutze diesen Skill, wenn chrome-agent eingerichtet oder
  geprüft werden soll — Trigger: "chrome-agent installieren",
  "chrome-agent einrichten", "setup-chrome-agent".
disable-model-invocation: true
---

# chrome-agent einrichten

Richtet [chrome-agent](https://github.com/captivus/chrome-agent) ein, die
CLI zur Chrome-Ansteuerung über CDP.

## Ablauf

Alle Schritte (Erkennung, pipx-Check, Browser-Erkennung, Installation,
Verifikation) stecken in einem Script. Einfach ausführen:

```
scripts/setup.sh
```

Exit-Codes und wie darauf zu reagieren ist:

| Exit | Bedeutung | Reaktion |
|------|-----------|----------|
| 0 | Erfolg — bereits installiert (`ALREADY_INSTALLED ...`) oder frisch installiert (`INSTALLED variant=... ...`) | Pfad/Version bzw. installierte Variante (chrome/vivaldi) kurz melden. Fertig. |
| 2 | `pipx` fehlt (stderr: `ERROR_NO_PIPX ...`) | Nutzer informieren, dass `pipx` Voraussetzung ist (z. B. `brew install pipx` oder `apt install pipx`), dort abbrechen. Nicht eigenmächtig `pipx` installieren. |
| 3 | Weder Vivaldi noch Chrome gefunden (stderr: `ERROR_NO_BROWSER ...`) | Nutzer informieren, dass chrome-agent einen der beiden Browser voraussetzt. Keine Installation versuchen, keinen Browser nachinstallieren. |
| 4 | `pipx install` fehlgeschlagen (stderr: `ERROR_INSTALL_FAILED variant=...` + Fehlerausgabe) | Fehlerausgabe an den Nutzer weitergeben, nicht erneut versuchen. |
| 5 | Verifikation nach Installation fehlgeschlagen (stderr: `ERROR_VERIFY_FAILED variant=...` + Installationsausgabe) | Ausgabe an den Nutzer weitergeben, nicht erneut versuchen. |

Bei jedem Fehler-Exit (2/3/4/5): nicht eigenmächtig nachinstallieren oder
reparieren, sondern dem Nutzer die konkrete Ursache melden.
