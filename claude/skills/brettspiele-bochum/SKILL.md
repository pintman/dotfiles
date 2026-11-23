---
name: brettspiele-bochum
description: >
  Sucht Brettspiele/Gesellschaftsspiele im Katalog der Stadtbücherei Bochum und in der
  Spieliothek Herne (Spielezentrum Herne). Nutze diesen Skill, wenn der Benutzer wissen will, ob
  die Stadtbücherei Bochum oder die Spieliothek/das Spielezentrum Herne ein bestimmtes Spiel hat,
  oder nach ausleihbaren Spielen dort sucht ("hat die Bücherei Catan", "Brettspiele in der
  Stadtbücherei suchen", "gibt es das in der Spieliothek").
disable-model-invocation: true
---

# Brettspiele in Bochum (Stadtbücherei) und Herne (Spieliothek) suchen

## Ablauf

1. Suchbegriff aus der Frage ableiten (Spieltitel, Verlag, Stichwort).
2. Skript aufrufen (durchsucht standardmäßig beide Bibliotheken, Ausgabe in zwei Abschnitten):
   ```
   scripts/suche.py "<Suchbegriff>"
   ```
   - `--nur bochum|herne`: nur eine Bibliothek.
   - `--open`: Suche (Bochum) bzw. PDF-Liste (Herne) nur im Browser öffnen (z. B. bei HTTP 429).
   - `--url`: nur URL(s) ausgeben.
   - `-v`/`--verfuegbar` (nur Bochum): zusätzlich je Treffer (max. 10) Standort, Signatur, Status
     (Verfügbar/Nicht verfügbar), Rückgabedatum und Vormerkungen abrufen. Langsam: 2 Abrufe
     pro Spiel, Katalog drosselt → Skript wartet bei HTTP 429 einmal (≤ 60 s), sonst Hinweis.
     Nutzen, wenn nach Verfügbarkeit/Ausleihbarkeit gefragt wird; bei vielen Treffern erst
     ohne `-v` suchen und den Begriff eingrenzen. Bash-Timeout großzügig setzen (≥ 5 min).
   - `--update`: Herne-Liste neu herunterladen.
3. Ausgabe kurz zusammenfassen, nach Bibliothek gruppiert (passende Spiele hervorheben, mit `-v`
   verfügbare zuerst). Bochum ohne `-v` → Detail-Link für Verfügbarkeit nennen.
4. Bei HTTP 429 der Bochum-Suche: Wartezeit nennen bzw. `--open` vorschlagen, nicht wiederholt
   anstoßen. Mehr Treffer als eine Seite → das Skript nennt die Such-URL für den Rest.

## Bochum

Axiell-Arena-Katalog. Mehrere Wörter werden als ein Klammerausdruck gesucht, Solr-Sonderzeichen
werden escaped. Ohne Begriff → alle Spiele.

## Herne (Spieliothek)

- Kein Online-Katalog, nur eine PDF-Gesamtliste (**Stand 03/2018**). Neuere Spiele fehlen, es gibt
  **keine Verfügbarkeit**. Darauf beim Zusammenfassen hinweisen; aktuellen Bestand/Verfügbarkeit
  vor Ort oder telefonisch erfragen. Ausleihe nur mit Mitgliedschaft (ab 1 €/Monat).
- Das Skript lädt die PDF beim ersten Lauf (TLS-Zertifikat der Website ist fehlerhaft und wird
  bewusst ignoriert), wandelt sie mit `pdftotext` (poppler, `brew install poppler`) um und cacht
  sie in `~/.cache/brettspiele/herne.txt`.
- Suche: alle Wörter müssen in Titel oder Verlag vorkommen (Groß-/Kleinschreibung egal), max. 30
  Treffer. Titel sind teils abgekürzt („Siedler v. Catan“) → bei 0 Treffern kürzeren Begriff
  probieren. Ohne Begriff wird nur der PDF-Link genannt.
