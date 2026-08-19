---
name: kalendertermin
description: "Sucht nach Terminen oder legt Termine im Apple Kalender (macOS Calendar.app) per AppleScript/osascript an — auch aus einem Screenshot, PDF oder Text heraus."
disable-model-invocation: true
---

# Kalendertermin-Skill

Legt Termine direkt im lokalen Apple Kalender (Calendar.app) an bzw. fragt sie ab, per `scripts/kalendertermin.py` (kapselt die AppleScript/osascript-Aufrufe). Kein Google Calendar, keine anderen Kalender-Tools verwenden — der Benutzer nutzt Apple Kalender als einzige Quelle.

Alle Aufrufe laufen über `python3 scripts/kalendertermin.py <subcommand> ...` (reines Stdlib, kein pip install nötig). Bekannte Fallstricke (kein `id`/`uid` bei Kalendern, `location` liefert `missing value`, locale-abhängige Datums-Strings) sind im Skript selbst umgesetzt, nicht nur dokumentiert.

## Relevante Kalender

Wenn nicht angegeben, wähle den persönlichen Kalender.

Bei Unklarheit, welcher Kalender gemeint ist (z. B. bei einem Termin, der sowohl privat als auch beruflich relevant sein könnte), kurz nachfragen statt zu raten.

## Ablauf: Termin anlegen

### 1. Termindaten extrahieren

Termindaten können aus Text, Screenshots (Buchungsbestätigungen, Flugtickets, Einladungen) oder PDFs kommen. Bei Bildern/PDFs immer zuerst lesen (Read-Tool) und daraus extrahieren:
- Titel/Beschreibung des Termins
- Datum(en) und Uhrzeit(en) (Start und Ende; bei fehlender Enduhrzeit sinnvolle Dauer annehmen oder nachfragen)
- Ort (falls vorhanden)
- Referenznummern (Flugnummer, Buchungsnummer o. ä.) — gehören in die Beschreibung/Notizen des Termins

Bei mehrteiligen Buchungen (z. B. Hin- und Rückflug) für jeden Teil einen eigenen Termin anlegen.

### 2. Zielkalender festlegen

Kalender erfragen.

### 3. Termin per Skript anlegen

Kalender werden vom Skript ausschließlich per Namen referenziert (nie per `id`/`uid` — das AppleEvent dafür schlägt auf diesem System für alle Kalender fehl, bekannter Calendar.app-Bug).

```bash
python3 scripts/kalendertermin.py add-event \
  --calendar "Persönlich" --title "Titel des Termins" \
  --start 2026-08-11T14:00 --end 2026-08-11T16:30 \
  [--location "Ort"] [--description "Zusatzinfos, z. B. Flugnummer/Buchungsnummer"]
```

- `--start`/`--end` als `YYYY-MM-DD` (ganztägig) oder `YYYY-MM-DDTHH:MM` (zeitgebunden).
- Fehlt `--end`: Default ist `--start` + 1h (zeitgebunden) bzw. `--start` + 1 Tag bei `--allday`.
- Für ganztägige Termine (z. B. Urlaub, Geburtstage, Deadlines) zusätzlich `--allday` setzen und Daten ohne Uhrzeit angeben; `--end` ist dabei exklusiv (ein eintägiger Termin endet am Folgetag).
- Bei mehreren Terminen (z. B. Hin- und Rückflug) das Skript mehrfach aufrufen — für jeden Teil ein eigener `add-event`-Aufruf.

### 4. Rückmeldung

Kurz bestätigen, welche Termine mit welchen Eckdaten (Datum, Uhrzeit, Kalender) angelegt wurden. Keine ausführliche Zusammenfassung, wenn die Angaben oben im Verlauf bereits sichtbar sind.

## Ablauf: Termine abfragen

### 1. Suchkriterium klären

Aus der Anfrage ableiten:
- Zeitraum (z. B. "heute", "diese Woche", "im August", ein konkretes Datum) — bei völlig fehlendem Zeitraum sinnvoll eingrenzen (z. B. nächste 30 Tage) statt den gesamten Kalender zu durchsuchen
- Stichwort im Titel (falls die Anfrage nach einem bestimmten Termin sucht, z. B. "wann ist der Zahnarzttermin")
- Zielkalender, falls genannt

Da Abfragen lesend und damit risikoarm sind, im Zweifel **nicht** nach dem Kalender fragen — aber wenn der Zielkalender aus dem Kontext ableitbar ist (z. B. nur ein relevanter Kalender), diesen trotzdem setzen: Suche über alle Kalender ist auf diesem System sehr langsam und fehleranfällig (siehe unten).

### 2. Abfrage per Skript

```bash
python3 scripts/kalendertermin.py query-events --from 2026-08-01 --to 2026-08-07 [--calendar "Name"] [--keyword "Stichwort"]
```

- `--to` ist inklusiv; ohne `--to` ist der Default `--from` + 7 Tage.
- Ist der Zielkalender bekannt, `--calendar` setzen — deutlich schneller und zuverlässiger als über alle Kalender zu suchen.
- **Ohne `--calendar` (Suche über alle Kalender) ist die Abfrage auf diesem System sehr langsam und nicht zuverlässig**: Calendar.apps `whose`-Filterung über `every event of cal` ist selbst bei engem Zeitraum (z. B. 10 Tage) im Test mehrere Minuten (>6 Minuten) gelaufen und dann mit einem AppleScript-Fehler (`-609`, ungültige Verbindung) fehlgeschlagen, statt Ergebnisse zu liefern. Immer als Hintergrund-Task starten (nicht blockierend auf den Abschluss warten). Schlägt die Abfrage fehl oder dauert sehr lange: falls der Kalender aus dem Kontext ableitbar ist (z. B. einziger relevanter Kalender des Nutzers), erneut gezielt mit `--calendar` versuchen statt zu wiederholen.
- Auch mit `--calendar` kann eine Abfrage >120s dauern (abhängig von Anzahl/Wiederholungen der Termine im Kalender) — das ist normal, kein Fehler.
- `location` liefert bei Terminen ohne Ort `missing value` — das Skript wandelt das bereits in "kein Ort" um.

### 3. Rückmeldung

Treffer knapp auflisten (Titel, Datum/Uhrzeit, Ort, ggf. Kalender). Bei keinem Treffer das klar sagen statt zu vermuten. Bei sehr vielen Treffern zuerst eingrenzen (z. B. nach Zeitraum) statt alles aufzulisten.

## Fehlerbehandlung

| Problem | Lösung |
|---|---|
| `execution error ... AppleEvent-Routine (-10000)` | Kalender existiert nicht unter diesem Namen — `--calendar` prüfen (Groß-/Kleinschreibung, exakter Name) |
| Kalendername nicht eindeutig (mehrere `Kalender`-Einträge) | Im Zweifel nachfragen statt zu raten |
| Enduhrzeit fehlt in der Quelle | Sinnvolle Standarddauer annehmen (z. B. 1h) oder kurz nachfragen |
| Datum/Zeit aus Screenshot nicht eindeutig lesbar | Nutzer um Bestätigung bitten, nicht raten |
| `query-events` dauert sehr lange oder wirkt hängend | Erwartet, v. a. ohne `--calendar` (siehe oben) — als Hintergrund-Task laufen lassen, nicht abbrechen und blind wiederholen |
| `execution error ... hat einen Fehler erhalten: Die Verbindung ist ungültig. (-609)` bei `query-events` | Bekannte Instabilität bei sehr langen `whose`-Abfragen (v. a. ohne `--calendar`) — mit `--calendar` und/oder kleinerem Zeitraum erneut versuchen statt zu wiederholen |
| Keine Treffer bei Stichwortsuche | Groß-/Kleinschreibung und Teilstrings prüfen, ggf. Zeitraum erweitern oder ohne Stichwort erneut suchen |
