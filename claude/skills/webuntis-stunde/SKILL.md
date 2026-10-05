---
name: webuntis-stunde
description: >
  Öffnet eine Unterrichtsstunde im WebUntis-Stundenplan (Datum + Klasse, optional Fach) und
  liest Kopfdaten und Schülerliste aus dem Klassenbuch-Tab aus. Rein lesend.
disable-model-invocation: true
---

# Stunde in WebUntis öffnen und Schülerliste auslesen

## Voraussetzungen

- `chrome-agent` muss installiert sein (`command -v chrome-agent`). Falls nicht: Skill
  `setup-chrome-agent` verwenden. Exit-Code 2 des Skripts bedeutet ebenfalls: fehlt.
- WebUntis läuft unter `https://tbs1.webuntis.com`.
- Login übernimmt Benutzer selbst — keine Zugangsdaten eingeben oder erfragen. Das Skript
  wartet auf den manuellen Login.
- Rein lesend: nichts speichern, keine Abwesenheiten/Einträge anlegen.

## Ablauf

```
python3 scripts/webuntis_stunde.py --date YYYY-MM-DD --klasse <Kürzel> \
  [--fach <Kürzel>] [--index N] [--json] [--debug]
```

- `--klasse` wird als Teilstring im Stundenblock gesucht (`ITA24a` trifft auch den Block
  „ITA24a, ITA24b“).
- `--fach` optional, ebenfalls Teilstring (z. B. `IT_LF08`, `ITA_PROJ`).
- Mehrere passende Blöcke am Tag: Default ist der früheste; `--index 1`, `2`, … wählt
  spätere (Hinweis auf stderr nennt die Anzahl). Entfallene (durchgestrichene) Stunden werden
  übersprungen — sie haben keinen Klassenbuch-Tab.
- `--json` liefert `header` (klassen, gruppe, fach, hinweis, wochentag, datum, zeit, raum,
  lehrkraft), `count`, `students` („Nachname, Vorname“) und `url`.
- `--debug` speichert Screenshots je Schritt (`--debug-dir`, Default
  `webuntis-stunde-debug`) — dafür das Scratchpad verwenden.
- Läuft bereits eine chrome-agent-Instanz mit WebUntis-Tab, wird sie wiederverwendet; sonst
  startet das Skript Chrome mit Profil `~/.claude/webuntis-stunde/chrome-profile`.
- Die Stunde bleibt am Ende im Browser geöffnet.

## Klickpfad (verifiziert)

`/today` → Stundenplan → Mein Stundenplan → Schuljahr prüfen → Wochenpfeile bis Zielwoche →
Stundenblock in der Tagesspalte → Tab „Klassenbuch“ → „Schüler*innen im Unterricht“. Die
Schülerkacheln liegen in einem `<iframe>`.

Bekannte Sackgassen — nicht verwenden:
- Klassenbuch → Abwesenheiten: Klassenfilter bietet nur eigene Klassen (Klassenleitung) an.
- Direkte URL-Navigation mit `?date=`: unzuverlässig (siehe `webuntis-klausur`).
- Aus Untermenüs (z. B. Klassenbuch) ist „Stundenplan“ nicht direkt klickbar — daher
  steigt das Skript immer über `/today` ein.

## Fehler

`Fehler: … nicht gefunden` nicht blind wiederholen: Datum/Klasse/Fach prüfen, ggf. mit
`--debug` Screenshots ansehen (WebUntis-Oberfläche geändert?).
