---
name: testatkarte
description: >
  Erstellt Testatkarten als Word-Dokument (.docx) für Ausbildungs- und Schulprojekte.
  Eine Testatkarte ist ein strukturiertes Arbeitsblatt mit nummerierten Meilensteinen,
  die Schüler sequenziell bearbeiten und von einem Fachlehrer abzeichnen lassen.
  Nutze diesen Skill immer wenn der Nutzer eine Testatkarte, ein Attestierungsblatt,
  ein Meilenstein-Arbeitsblatt, eine Projektprüfungskarte oder ein ähnliches Dokument
  für Schüler oder Auszubildende erstellen möchte — auch wenn das Wort "Skill" nicht fällt.
  Trigger auch bei Formulierungen wie "Erstell mir eine Testatkarte zu...",
  "Ich brauche Meilensteine für ein Projekt über...",
  "Mach ein Arbeitsblatt mit Abnahme-Checkliste für...",
  "Erstelle ein Projekt-Testat für...".
  Ausgabe: eine .docx-Datei, maximal 4 Seiten, Seite 1 mit Meilensteintabelle,
  Seiten 2–4 mit Zusatzinformationen (Referenz, Codebeispiele, hilfreiche Prompts).
---

# Testatkarte – Skill

## Was ist eine Testatkarte?

Eine Testatkarte ist ein strukturiertes Projektarbeitsblatt für Schüler/Auszubildende.
Sie enthält:

1. **Seite 1**: Meilensteintabelle mit nummerierten Arbeitsaufträgen + Testat-Spalte
2. **Seiten 2–4**: Zusatzinformationen (Referenzmaterial, Codebeispiele, Diagramme, hilfreiche LLM-Prompts)

---

## Anforderungen an die Meilensteine

- **Komplexität**: Jeder Meilenstein soll mindestens 90 Minuten Arbeitszeit umfassen
- **Sequenziell**: Werden der Reihe nach bearbeitet und einzeln abgezeichnet
- **Abnahme**: Letzter Abnahmezeitpunkt: 20 Minuten vor Stundenende; max. 2 Meilensteine pro Sitzung
- **Anzahl**: In der Regel 8–14 Meilensteine; alle auf Seite 1
- **Vielfalt**: Mix aus praktischen (Programmier-/Bau-/Konfigurationsaufgaben) und theoretischen Meilensteinen (handschriftliche Erklärungen, Beschreibungen)

---

## Schritt-für-Schritt-Anleitung

### Schritt 1: Anforderungen klären

Falls nicht angegeben, frage nach:
- **Thema/Projekt** (z. B. "LEDs mit Raspberry Pi", "Netzwerkkonfiguration", "Datenbankprojekt")
- **Zielgruppe** (z. B. ITA, FIA, Klasse, Ausbildungsjahr)
- **Meilensteine**: Wenn der Nutzer keine vorgibt, generiere selbst passende (8–14 Stück)
- **Zusatzinfos**: Welche Referenzmaterialien sollen auf Seiten 2–4 stehen?

### Schritt 2: Meilensteine entwerfen

Gestalte jeden Meilenstein so, dass er klar, prüfbar und ca. 90 Minuten Arbeit umfasst.
Typische Kategorien:

- **Praktisch/technisch**: Aufbauen, Programmieren, Konfigurieren, Testen
- **Theoretisch/dokumentierend**: Handschriftlich erklären, Diagramm zeichnen, beschreiben
- **Kreativ/erweiternd**: Eigene Erweiterung, Dokumentation, Präsentation

### Schritt 3: Dokument erstellen

Nutze das Python-Skript [`generate.py`](generate.py). Es liest seinen kompletten Inhalt
(Meilensteine + Zusatzinformationen) aus einer JSON-Konfigurationsdatei – der Python-Code
selbst muss dafür nicht verändert werden.

Vorgehen:
1. JSON-Konfiguration nach dem Schema von [`example_config.json`](example_config.json) schreiben
   (siehe Abschnitt "Konfigurationsschema" unten).
2. Skript ausführen (falls `python-docx` fehlt, in einer temporären virtuellen Umgebung installieren):
   ```bash
   python3 -m venv /tmp/testatkarte_venv
   /tmp/testatkarte_venv/bin/pip install --quiet python-docx
   /tmp/testatkarte_venv/bin/python generate.py --config config.json
   ```
   `--output pfad.docx` überschreibt optional das `output`-Feld aus der Config.

**Seitenaufbau:**
- **A4** (11906 × 16838 DXA), Ränder 1440 DXA (1 Zoll) rundherum
- **Seite 1**: Namenszeile + Titel + Einleitungstext + Meilensteintabelle
- **Seiten 2–4**: Zusatzinformationen mit Abschnitten

**Farbschema** (schwarz-weiß, druckfreundlich):
- Tabellenheader-Hintergrund: `FFFFFF` (weiß)
- Tabellenheader-Schrift: `000000` (schwarz)
- Ungerade Zeilen: `EEEEEE` (hellgrau)
- Gerade Zeilen: `FFFFFF` (weiß)
- Überschriften-Farbe: `000000` (schwarz)

**Schriftgrößen**: Mindestens 11pt (= `size: 22` in docx). Fließtext 11pt, Überschriften 12–16pt.

---

## Konfigurationsschema

Die Config ist ein JSON-Objekt mit folgenden Feldern:

| Feld | Pflicht | Beschreibung |
|---|---|---|
| `thema` | ja | Thema, erscheint im Titel |
| `klasse` | ja | Zielgruppe/Klasse, erscheint im Titel |
| `einleitung` | ja | Einleitungstext auf Seite 1 |
| `meilensteine` | ja | Liste von `{"nr": int, "text": str}` |
| `output` | ja | Ausgabepfad der .docx-Datei |
| `zusatzinfos` | nein | Liste von Blocks für Seiten 2–4 (siehe unten) |

**Block-Typen für `zusatzinfos`** (jeder Block ist ein Objekt mit `"type"`):

- `{"type": "heading", "level": 1|2|3, "text": "..."}` – Überschrift
- `{"type": "paragraph", "text": "...", "center": bool, "bold": bool, "italic": bool, "size": int, "before": int, "after": int}` – Fließtext (nur `text` ist Pflicht)
- `{"type": "code", "lines": ["zeile1", "zeile2", ...]}` – Codeblock, jede Zeile eigener Paragraph mit grauem Hintergrund (Courier New)
- `{"type": "prompt", "lines": ["...", ...]}` – kursive LLM-Prompt-Zeilen
- `{"type": "classdiagram", "title": "...", "attributes": ["+ attr: Typ", ...], "methods": ["+ methode(): void", ...]}` – UML-artiges Klassendiagramm als Tabelle
- `{"type": "spacer"}` – Leerzeile
- `{"type": "pagebreak"}` – Seitenumbruch

Referenz-Config mit vollständigem Beispiel ("LEDs – ITA"): [`example_config.json`](example_config.json).
Für eine neue Testatkarte diese Datei als Vorlage kopieren und Felder/Blocks anpassen.

---

## Zusatzinformationen gestalten (Seiten 2–4)

Die Zusatzinformationen sollen Schülern helfen, die Meilensteine zu lösen. Typische Abschnitte,
jeweils als Blocks in `zusatzinfos` (siehe Konfigurationsschema oben):

- **Klassendiagramme/Strukturdiagramme**: `classdiagram`-Block (Titel, Attribute, Methoden)
- **Codebeispiele**: `code`-Block, jede Zeile als eigenes Listenelement (Courier New, grauer Hintergrund)
- **Hilfreiche LLM-Prompts**: `prompt`-Block, kursive Zeilen
- **Konzepterklärungen**: `heading`- und `paragraph`-Blocks, oder ein `classdiagram`-Block
  für tabellarische Begriffserklärungen

---

## Qualitätsprüfung

Vor der Ausgabe prüfen:
- [ ] Alle Meilensteine umfassen in Summe genug Arbeit für die geplante Projektdauer
- [ ] Jeder Meilenstein ist klar formuliert und eindeutig prüfbar
- [ ] Dokument hat maximal 4 Seiten
- [ ] Meilensteintabelle passt auf Seite 1 (ggf. Schriftgröße auf 16 reduzieren)
- [ ] Zusatzinfos auf Seiten 2–4 sind themenspezifisch und hilfreich

---

## Nach der Erstellung

Sobald die Testatkarte fertig erstellt und ausgegeben wurde, frage den Nutzer, ob mit dem
Skill `testat-vorabnahme` (gleicher Ordner) ein passender Selbstcheck-Prompt zu dieser
Testatkarte erstellt werden soll (Meta-Prompt, mit dem Schüler/Auszubildende in einem
beliebigen KI-Chat selbst prüfen können, ob sie testat-reif sind).

---

## Abhängigkeiten

- `python-docx`: `pip install python-docx`

