---
name: webuntis-klausur
description: >
  Trägt eine Klausur/Klassenarbeit in WebUntis (`https://tbs1.webuntis.com`)
  ein, per Chrome-Browserautomatisierung. Nutze diesen Skill IMMER, wenn ein
  Klausurtermin/Klassenarbeit in Untis/WebUntis eingetragen, angelegt oder erfasst werden soll — auch
  bei Formulierungen wie "trag die Klausur in Untis ein", "leg die Klassenarbeit in WebUntis an".
  Login übernimmt Benutzer selbst, niemals Zugangsdaten eingeben oder danach fragen. Folgt einem
  verifizierten Klickpfad — nicht davon abweichende Wege (z. B. direkte URL-Navigation mit
  `?date=`) versuchen, diese funktionieren nachweislich nicht zuverlässig.
---

# Klausurtermin in WebUntis eintragen

Legt eine Prüfung (Klassenarbeit) für einen bestimmten Termin in WebUntis an, über den
Chrome-Browser (claude-in-chrome-Tools).

## Voraussetzungen

- WebUntis läuft unter `https://tbs1.webuntis.com`.
- Login übernimmt Benutzer selbst — keine Zugangsdaten eingeben oder erfragen. Falls die Seite
  einen Login-Screen zeigt, Benutzer bitten, sich selbst einzuloggen, und danach fortfahren.
- Vor dem ersten Klick die claude-in-chrome-Tools laden (`tabs_context_mcp`, `navigate`,
  `computer`, `read_page`, `tabs_create_mcp`), falls noch nicht geschehen.

## Ablauf (verifizierter Weg)

1. Links im Menü "Stundenplan" → "Mein Stundenplan" öffnen.
2. Falls das Prüfungsdatum in einem anderen Schuljahr liegt als aktuell ausgewählt: oben
   links das Schuljahr-Dropdown umstellen.
3. Auf die Datumsanzeige oben (z. B. "31.08. - 06.09.2026") klicken → öffnet einen
   Mini-Kalender mit Monats-Pfeilen. Zum richtigen Monat blättern, Tag anklicken.
4. In der Wochenansicht ggf. scrollen, um die passende Stunde zu finden, dann den
   Stundenblock anklicken.
5. Im Seitenpanel auf den Tab "Details" klicken.
6. Unten auf "Prüfung erstellen" klicken.
7. Im Formular "Prüfungsart" auf "Klassenarbeit" setzen (Alternative: "Sonstige Leistung");
   Datum/Zeit/Lehrkraft/Raum sind vorbefüllt. "Name"-Feld optional mit sprechendem Titel
   überschreiben (z. B. "Klassenarbeit ITF25a IT_LF08").
8. "Speichern" klicken. Erfolg erkennbar am "PRÜFUNG"-Badge im Detail-Panel.

## Wichtige Regeln

- **Direkte URL-Navigation mit `?date=YYYY-MM-DD` funktioniert nicht zuverlässig** (die SPA
  springt beim Neuladen zurück) — nur der Kalender-Picker in der App verwenden.
- **Nicht funktionierende Wege, nicht erneut versuchen**:
  - "Unterricht → Prüfungen" (Listenansicht ohne sichtbaren "Neu"-Button).
  - Das Stift/Edit-Icon in "Mein Unterricht" (Dialog bleibt dauerhaft bei "Wird geladen"
    hängen).
- Nach dem Speichern kurz prüfen (Screenshot/`read_page`), ob das "PRÜFUNG"-Badge im
  Detail-Panel erscheint, statt Erfolg blind anzunehmen.
- Bricht der Ablauf unerwartet ab oder reagiert ein Element nicht (siehe allgemeine
  claude-in-chrome-Hinweise zu Rabbit Holes/Loops): nicht denselben Schritt wiederholt
  versuchen, sondern Benutzer kurz Bescheid geben und nachfragen.
