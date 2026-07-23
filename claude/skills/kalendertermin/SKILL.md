---
name: kalendertermin
description: "Sucht nach Terminen oder legt Termine im Apple Kalender (macOS Calendar.app) per AppleScript/osascript an. Nutze diesen Skill, wenn ein Kalendereintrag, Termin, eine Buchungsbestätigung, einen Flug, eine Reise oder ein Ereignis in den Kalender eingetragen oder abgefragt werden soll — auch aus einem Screenshot, PDF oder Text heraus. Trigger: \"Kalendereintrag\", \"Termin erstellen\", \"trag das im Kalender ein\", \"mache dafür einen Termin\", \"in den Kalender\", \"schau in Kalender\"."
---

# Kalendertermin-Skill

Legt Termine direkt im lokalen Apple Kalender (Calendar.app) per `osascript`/AppleScript an. Kein Google Calendar, keine anderen Kalender-Tools verwenden — Marco nutzt Apple Kalender als einzige Quelle.

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

### 3. Termin per osascript anlegen

Vor dem Schreibzugriff **niemals** `id` oder `uid` einer Calendar-Referenz abfragen — das AppleEvent dafür schlägt auf diesem System für alle Kalender fehl (bekannter Calendar.app-Bug). Kalender ausschließlich per Namen referenzieren (`calendar "Name"`), das funktioniert zuverlässig für Lese- und Schreibzugriffe.

Vorlage für einen zeitgebundenen Termin:

```bash
osascript <<'EOF'
tell application "Calendar"
    set targetCal to calendar "Persönlich"

    set startDate to current date
    set year of startDate to 2026
    set month of startDate to 8
    set day of startDate to 11
    set hours of startDate to 14
    set minutes of startDate to 0
    set seconds of startDate to 0

    set endDate to startDate
    set endDate to startDate + (2 * hours) + (30 * minutes)

    make new event at end of events of targetCal with properties {summary:"Titel des Termins", start date:startDate, end date:endDate, location:"Ort", description:"Zusatzinfos, z. B. Flugnummer/Buchungsnummer"}
end tell
EOF
```

Für ganztägige Termine (z. B. Urlaub, Geburtstage, Deadlines) zusätzlich `allday event:true` setzen und `start date`/`end date` auf Mitternacht der jeweiligen Tage legen; `end date` bei ganztägigen Terminen ist exklusiv (ein eintägiger Termin endet am Folgetag 00:00).

Bei mehreren Terminen (z. B. Hin- und Rückflug) mehrere `make new event ...`-Blöcke in einem `tell`-Block bündeln, um nur einen osascript-Aufruf zu brauchen.

### 4. Rückmeldung

Kurz bestätigen, welche Termine mit welchen Eckdaten (Datum, Uhrzeit, Kalender) angelegt wurden. Keine ausführliche Zusammenfassung, wenn die Angaben oben im Verlauf bereits sichtbar sind.

## Ablauf: Termine abfragen

### 1. Suchkriterium klären

Aus der Anfrage ableiten:
- Zeitraum (z. B. "heute", "diese Woche", "im August", ein konkretes Datum) — bei völlig fehlendem Zeitraum sinnvoll eingrenzen (z. B. nächste 30 Tage) statt den gesamten Kalender zu durchsuchen
- Stichwort im Titel (falls die Anfrage nach einem bestimmten Termin sucht, z. B. "wann ist der Zahnarzttermin")
- Zielkalender, falls genannt

Da Abfragen lesend und damit risikoarm sind, im Zweifel **nicht** nach dem Kalender fragen, sondern über alle Kalender suchen — anders als beim Anlegen.

### 2. Abfrage per osascript

Auch hier gilt: Kalender ausschließlich per Namen referenzieren, nie per `id`/`uid` (siehe Hinweis oben). Datumsgrenzen wie beim Anlegen über `current date` + einzelne Felder aufbauen, nicht über `date "..."`-Strings (locale-abhängig, fehleranfällig).

Vorlage für eine Suche über einen Zeitraum, optional mit Stichwort, über alle Kalender:

```bash
osascript <<'EOF'
tell application "Calendar"
    set rangeStart to current date
    set year of rangeStart to 2026
    set month of rangeStart to 8
    set day of rangeStart to 1
    set hours of rangeStart to 0
    set minutes of rangeStart to 0
    set seconds of rangeStart to 0

    set rangeEnd to rangeStart + (7 * days)

    set ausgabe to ""
    repeat with cal in calendars
        set treffer to (every event of cal whose start date ≥ rangeStart and start date < rangeEnd)
        repeat with e in treffer
            set ausgabe to ausgabe & (name of cal) & ": " & (summary of e) & " | " & (start date of e as string) & " – " & (end date of e as string) & " | " & (location of e) & linefeed
        end repeat
    end repeat
    ausgabe
end tell
EOF
```

Für eine Stichwortsuche zusätzlich `and summary contains "Stichwort"` an die `whose`-Bedingung anhängen. Ist der Zielkalender bekannt, `calendars` durch `calendar "Name"` ersetzen und die äußere `repeat`-Schleife weglassen (deutlich schneller).

Bei sehr weiten Zeiträumen (z. B. "nächstes Jahr") oder Suche über alle Kalender kann die Abfrage spürbar dauern — Zeitraum wenn möglich eingrenzen.

`location of e` liefert bei Terminen ohne Ort `missing value` (kein leerer String) — in der Rückmeldung als "kein Ort" behandeln, nicht wörtlich ausgeben.

### 3. Rückmeldung

Treffer knapp auflisten (Titel, Datum/Uhrzeit, Ort, ggf. Kalender). Bei keinem Treffer das klar sagen statt zu vermuten. Bei sehr vielen Treffern zuerst eingrenzen (z. B. nach Zeitraum) statt alles aufzulisten.

## Fehlerbehandlung

| Problem | Lösung |
|---|---|
| `execution error ... AppleEvent-Routine (-10000)` bei `id`/`uid`/`properties` | Diese Properties meiden, nur `name`, `summary`, `start date`, `end date`, `location`, `description`, `allday event` verwenden |
| Kalendername nicht eindeutig (mehrere `Kalender`-Einträge) | Im Zweifel nachfragen statt zu raten |
| Enduhrzeit fehlt in der Quelle | Sinnvolle Standarddauer annehmen (z. B. 1h) oder kurz nachfragen |
| Datum/Zeit aus Screenshot nicht eindeutig lesbar | Nutzer um Bestätigung bitten, nicht raten |
| Abfrage über `calendars` sehr langsam | Auf einen konkreten Kalender einschränken oder Zeitraum verkleinern |
| Keine Treffer bei Stichwortsuche | Groß-/Kleinschreibung und Teilstrings prüfen, ggf. Zeitraum erweitern oder ohne Stichwort erneut suchen |
