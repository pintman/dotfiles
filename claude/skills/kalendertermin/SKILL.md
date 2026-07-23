---
name: kalendertermin
description: "Legt Termine im Apple Kalender (macOS Calendar.app) per AppleScript/osascript an. Nutze diesen Skill, wenn ein Kalendereintrag, Termin, eine Buchungsbestätigung, einen Flug, eine Reise oder ein Ereignis in den Kalender eingetragen werden soll — auch aus einem Screenshot, PDF oder Text heraus. Trigger: \"Kalendereintrag\", \"Termin erstellen\", \"trag das im Kalender ein\", \"mache dafür einen Termin\", \"in den Kalender\"."
---

# Kalendertermin-Skill

Legt Termine direkt im lokalen Apple Kalender (Calendar.app) per `osascript`/AppleScript an. Kein Google Calendar, keine anderen Kalender-Tools verwenden — Marco nutzt Apple Kalender als einzige Quelle.

## Relevante Kalender

Wenn nicht angegeben, wähle den persönlichen Kalender.

Bei Unklarheit, welcher Kalender gemeint ist (z. B. bei einem Termin, der sowohl privat als auch beruflich relevant sein könnte), kurz nachfragen statt zu raten.

## Ablauf

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

## Fehlerbehandlung

| Problem | Lösung |
|---|---|
| `execution error ... AppleEvent-Routine (-10000)` bei `id`/`uid`/`properties` | Diese Properties meiden, nur `name`, `summary`, `start date`, `end date`, `location`, `description`, `allday event` verwenden |
| Kalendername nicht eindeutig (mehrere `Kalender`-Einträge) | Im Zweifel nachfragen statt zu raten |
| Enduhrzeit fehlt in der Quelle | Sinnvolle Standarddauer annehmen (z. B. 1h) oder kurz nachfragen |
| Datum/Zeit aus Screenshot nicht eindeutig lesbar | Nutzer um Bestätigung bitten, nicht raten |
