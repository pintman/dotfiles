---
name: brettspiele-bochum
description: >
  Sucht Brettspiele/Gesellschaftsspiele im Katalog der Stadtbücherei Bochum. Nutze diesen Skill,
  wenn der Benutzer wissen will, ob die Stadtbücherei Bochum ein bestimmtes Spiel hat, oder
  nach ausleihbaren Spielen dort sucht ("hat die Bücherei Catan", "Brettspiele in der
  Stadtbücherei suchen").
disable-model-invocation: true
---

# Brettspiele in der Stadtbücherei Bochum suchen

## Ablauf

1. Suchbegriff aus der Frage ableiten (Spieltitel, Verlag, Stichwort). Ohne Begriff wird nach allen
   Spielen gesucht.
2. Skript aufrufen:
   ```
   scripts/suche.py "<Suchbegriff>"
   ```
   Ausgabe: Trefferzahl, pro Spiel Titel (Jahr) – Mitwirkende [Reihe] + Detail-Link.
   - `--open`: Suche stattdessen nur im Browser öffnen (z. B. bei HTTP 429).
   - `--url`: nur die Such-URL ausgeben.
   - `-v`/`--verfuegbar`: zusätzlich je Treffer (max. 10) Standort, Signatur, Status
     (Verfügbar/Nicht verfügbar), Rückgabedatum und Vormerkungen abrufen. Langsam: 2 Abrufe
     pro Spiel, Katalog drosselt → Skript wartet bei HTTP 429 einmal (≤ 60 s), sonst Hinweis.
     Nutzen, wenn nach Verfügbarkeit/Ausleihbarkeit gefragt wird; bei vielen Treffern erst
     ohne `-v` suchen und den Begriff eingrenzen. Bash-Timeout großzügig setzen (≥ 5 min).
3. Ausgabe kurz zusammenfassen (passende Spiele hervorheben, mit `-v` verfügbare zuerst).
   Ohne `-v` → Detail-Link für Verfügbarkeit nennen.
4. Bei HTTP 429 der Suche selbst: Wartezeit nennen bzw. `--open` vorschlagen, nicht wiederholt anstoßen.
   Mehr Treffer als eine Seite → das Skript nennt die Such-URL für den Rest.

Mehrere Wörter werden als ein Klammerausdruck gesucht, Solr-Sonderzeichen werden escaped.
