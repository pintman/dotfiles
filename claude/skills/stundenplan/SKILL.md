---
name: stundenplan
description: >
  Ruft den aktuellen Stundenplan aus WebUntis (iCal-Feed) ab und beantwortet Ad-hoc-Fragen
  wie "was habe ich heute/morgen", "wann ist meine nächste Stunde", "was steht diese Woche an"
  oder "was habe ich am 15.9.". Nutze diesen Skill IMMER, wenn der Benutzer nach seinem konkreten
  Unterrichtsplan/Stundenplan fragt — auch bei Formulierungen wie "Stundenplan bitte", "welche
  Klasse habe ich als Nächstes". Nicht verwechseln mit dem `briefing`-Skill (behandelt Aufgaben/
  Termine aus `status.md`, nicht den Live-Stundenplan aus WebUntis) und nicht mit
  `webuntis-klausur` (trägt Klausuren in WebUntis ein statt sie abzurufen).
---

# Stundenplan abrufen

Lädt den WebUntis-iCal-Feed des Benutzers live (kein Caching) und listet die Termine im gefragten
Zeitraum kompakt auf.

## Feed-URL

Liegt als `WEBUNTIS_ICAL_URL` in einer `.env`-Datei.

Das Skript sucht die `.env` selbst — ausgehend vom Skript-Ordner aufwärts — und braucht daher
normalerweise kein `--url`.

Enthält ein persönliches Zugriffs-Token — nicht an Dritte weitergeben oder außerhalb dieses
Skills verwenden.

## Ablauf

1. Zeitraum aus der Frage des Benutzers ableiten:
   - "heute" → `--from HEUTE --to HEUTE`
   - "morgen" → `--from MORGEN --to MORGEN`
   - "diese Woche" → Montag bis Freitag der laufenden Woche
   - konkretes Datum (z. B. "am 15.9.") → `--from 2026-09-15 --to 2026-09-15`
   - keine Angabe → kein `--from`/`--to`/`--days` nötig, Skript nutzt Default (heute bis +7 Tage)
2. Skript ausführen:
   ```
   python3 scripts/stundenplan.py --url "<Feed-URL oben>" [--from YYYY-MM-DD --to YYYY-MM-DD | --days N]
   ```
3. Ausgabe direkt als Antwort übernehmen (bereits nach Datum gruppiert, eine Zeile pro
   Termin: Uhrzeit, Kurs/Bezeichnung, Raum). Tage ohne Termine erscheinen nicht in der
   Ausgabe.

## Wichtige Details

- **"Aufsicht (T1)"/"Aufsicht (T2)"**: Termine ohne Kursbezeichnung im Feed (Pausen-/
  Aufsichtsdienste). Werden generisch beschriftet angezeigt, nicht herausgefiltert.
- **Kombi-Klassen** (z. B. "ITA24a; ITA24b PROJ") sind gemeinsamer Unterricht mehrerer
  Klassen — kein Fehler.
- Der Feed deckt nur das laufende + kommende Schulhalbjahr ab (aktuell ca. Juli–Dezember
  2026). Anfragen weit außerhalb dieses Zeitraums liefern keine Termine.
- **Immer frisch abrufen**, nie zwischenspeichern — Vertretungen/Ausfälle sollen aktuell
  sein.
- Schlägt der Abruf fehl (Netzwerkfehler, HTTP-Fehler): Fehlermeldung des Skripts an den
  Benutzer weitergeben, nicht wiederholt versuchen (z. B. Token könnte abgelaufen sein).
