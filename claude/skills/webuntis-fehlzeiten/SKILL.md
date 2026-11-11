---
name: webuntis-fehlzeiten
description: >
  Lädt den WebUntis-Bericht "Fehlzeiten pro Schüler*in" (CSV) einer Klasse für das
  aktuelle Schuljahr per Chrome-Browserautomatisierung herunter und/oder wertet eine
  solche CSV pro Schüler*in übersichtlich als Text aus. Zwei unabhängige Skripte.
  Login übernimmt Benutzer selbst — niemals Zugangsdaten eingeben oder danach fragen.
  Download benötigt `chrome-agent`.
disable-model-invocation: true
---

# Fehlzeiten aus WebUntis holen und auswerten

Zwei voneinander unabhängige Skripte unter `scripts/`:

| Skript | Zweck |
|---|---|
| `webuntis_fehlzeiten_download.py` | holt die CSV aus WebUntis |
| `fehlzeiten_auswertung.py` | wertet eine CSV aus (auch manuell exportierte) |

## 1. Download

```
python3 scripts/webuntis_fehlzeiten_download.py --klasse ITF24a [--ziel ~/Downloads] [--debug]
```

- Voraussetzung: `chrome-agent` (`command -v chrome-agent`). Exit-Code 2 → Skill
  `setup-chrome-agent` ausführen, danach erneut versuchen.
- Startet Chrome (Profil `~/.claude/webuntis-fehlzeiten/chrome-profile`) oder nutzt eine
  laufende chrome-agent-Instanz mit WebUntis-Tab. Ohne Session: Benutzer loggt sich im
  Chrome-Fenster selbst ein, das Skript wartet (`--login-timeout`, Default 300 s).
- Auf `https://tbs1.webuntis.com/class-register-reports`: Klasse wählen, Zeitraum
  „Aktuelles Schuljahr“, Haken Fehlzeiten / Verspätungen / Nur zählende Abwesenheiten /
  Alle Schüler*innen, CSV-Export „Fehlzeiten pro Schüler*in“ (Gruppierung „pro Stunde“).
- Der Bericht wird asynchron erzeugt; das Skript wartet auf den Download-Link und speichert
  die Datei unverändert als `<ziel>/AbsencePerStudent_YYYYMMDD_HHMM.csv`.
- Fortschritt geht nach stderr, **stdout enthält nur den CSV-Pfad**.
- `--debug` speichert Screenshots je Schritt (`--debug-dir`).
- Bei `Fehler: ... nicht gefunden` nicht blind wiederholen: Klassenkürzel prüfen, ggf. hat
  sich die WebUntis-Oberfläche geändert (Legacy-Dojo-Seite im iframe `embedded.do`).

## 2. Auswertung

```
python3 scripts/fehlzeiten_auswertung.py <AbsencePerStudent_*.csv>
```

Pro Schüler*in: Fehlstunden (entsch./nicht entsch.), Fehltage, Verspätungen, Gründe,
chronologische Tagesliste. Am Ende Klassenübersicht sortiert nach nicht entschuldigten
Stunden.

## Kombiniert

```
python3 scripts/fehlzeiten_auswertung.py "$(python3 scripts/webuntis_fehlzeiten_download.py --klasse ITF24a)"
```
