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

### 1. Bereits installiert?

```
command -v chrome-agent
```

Falls vorhanden: Version/Pfad kurz melden, fertig — nichts weiter tun.

### 2. pipx verfügbar?

```
command -v pipx
```

Falls `pipx` fehlt: Nutzer informieren, dass `pipx` Voraussetzung für die
Installation ist (z. B. `brew install pipx` oder `apt install pipx`), und dort
abbrechen. Nicht eigenmächtig `pipx` installieren.

### 3. Vivaldi installiert?

```
[[ -d "/Applications/Vivaldi.app" ]] || command -v vivaldi
```

Falls ja: den Vivaldi-Fork installieren, der zusätzlich Vivaldi
unterstützt:

```
pipx install git+https://github.com/pintman/vivaldi-agent.git
```

Danach mit Schritt 5 (Verifikation) fortfahren.

### 4. Sonst: Chrome installiert?

```
[[ -d "/Applications/Google Chrome.app" ]] || command -v google-chrome
```

Falls ja: Standard-chrome-agent installieren:

```
pipx install chrome-agent
```

Danach mit Schritt 5 (Verifikation) fortfahren.

Falls weder Vivaldi noch Chrome gefunden wurden: dem Nutzer mitteilen,
dass chrome-agent einen dieser Browser voraussetzt und keiner der beiden
gefunden wurde. Keine Installation versuchen, keinen Browser
nachinstallieren.

### 5. Verifikation

Nach der Installation:

```
command -v chrome-agent
```

Erfolg kurz bestätigen (installierte Variante: Standard oder
Vivaldi-Fork). Schlägt die Verifikation fehl, Fehlerausgabe von `pipx
install` an den Nutzer weitergeben statt erneut zu versuchen.
