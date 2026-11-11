---
name: wahr-falsch-quiz
description: >
  Erstellt Wahr-Falsch-Quizze als Text-Lösungsdatei (.txt) für IT-Auszubildende
  (Fachinformatiker und Informationstechnische Assistenten). Word-Dokument (.docx) im
  Microsoft Forms Import-Format nur auf ausdrückliche Nachfrage.
disable-model-invocation: true
---

# Wahr-Falsch-Quiz Skill

## Zweck
Dieser Skill erstellt Wahr-Falsch-Quizze für IT-Auszubildende (Fachinformatiker und Informationstechnische Assistenten). Standardausgabe ist **nur eine Text-Datei (.txt)** mit `[w]`/`[f]`-Präfix pro Aussage. Ein Word-Dokument (.docx), das direkt in Microsoft Forms importiert werden kann, wird **nur erzeugt, wenn der Nutzer ausdrücklich danach fragt** (Word, docx, Forms-Import).

## Punktesystem
- Richtige Antwort (Wahr/Falsch korrekt eingeschätzt): **+1 Punkt**
- Falsche Antwort: **-1 Punkt**
- Nicht oder nicht eindeutig gekennzeichnete Aussage: **0 Punkte** (Minimum: 0 Punkte gesamt)

## Antwortoptionen (fest, für jede Aussage gleich)
Jede Aussage hat genau zwei Antwortmöglichkeiten:
1. **Wahr**
2. **Falsch**

(Keine dritte Option – 0 Punkte entsteht durch Nicht-Ankreuzen)

---

## Vorgehen

### Schritt 1: Thema und Parameter klären
Falls nicht vollständig angegeben, frage nach:
- **Fachgebiet** (z. B. Netzwerktechnik, IT-Sicherheit, Programmierung, Betriebssysteme, Datenbanken)
- **Schwierigkeitsgrad**: Grundlagen / Fortgeschritten / Prüfungsvorbereitung
- **Anzahl der Aussagen** (Standard: 15, Bereich: 10–20)

### Schritt 2: Aussagen entwickeln

Erstelle 10–20 Aussagen nach diesen Regeln:

**Inhaltliche Qualität:**
- Fachlich korrekt und dem Ausbildungsstand von IT-Azubis angemessen
- Deckt verschiedene Aspekte des Themas ab (keine Wiederholungen)
- Falsche Aussagen sind plausibel falsch – nicht offensichtlich unsinnig
- Wahre Aussagen sind eindeutig richtig – keine Graubereiche

**Formulierung:**
- Klare, präzise Sprache ohne Doppeldeutigkeiten
- Keine Verneinungen in Aussagen (z. B. nicht: „TCP ist kein verbindungsorientiertes Protokoll")
- Keine Trivialfragen
- Aussagen als vollständige Sätze formulieren
- Sonderzeichen in Aussagen (wie `<`, `>`, `&`) als XML-Entities escapen: `&lt;`, `&gt;`, `&amp;`

**Verteilung:**
- Ca. 55–65 % wahre Aussagen, 35–45 % falsche Aussagen
- Keine erkennbare Reihenfolge (nicht alle wahren zuerst)

**Qualitätsprüfung vor der Ausgabe:**
- ✅ Jede Aussage eindeutig wahr ODER falsch?
- ✅ Keine Doppeldeutigkeiten?
- ✅ Verschiedene Themenaspekte abgedeckt?
- ✅ Dem Ausbildungsstand angemessen?

### Schritt 3: Datei erstellen

Standard: nur `.txt` (`--variante text`, Default des Skripts). Das Docx-Format unten ist nur
relevant, wenn der Nutzer ausdrücklich ein Word-Dokument möchte.

#### Docx-Format (Microsoft Forms-kompatibel, nur auf Nachfrage)

Microsoft Forms erkennt beim Import nur bestimmte Aufzählungsformate. Das Dokument muss **Plain-Text-Nummerierungen** verwenden — keine automatischen Word-Listen, sondern hartcodierte Präfixe im Text:

- Fragen: `1.`, `2.`, `3.`, ...
- Antwortoptionen: `a)`, `b)`, ...

Jede Frage und jede Antwortoption steht in einem eigenen Absatz (`<w:p>`).

Das ergibt pro Aussage dieses Muster im Dokument:
```
1. [AUSSAGE]
a) Wahr
b) Falsch
```

#### Ansatz: Skript [`scripts/generate.py`](scripts/generate.py)

Das Skript liest die Aussagen (Text + Wahr/Falsch + optionale Erklärung) aus einer
JSON-Konfigurationsdatei nach dem Schema von [`example_config.json`](example_config.json)
– der Python-Code selbst muss dafür nicht verändert werden.

Vorgehen:
1. JSON-Konfiguration nach dem Schema unten schreiben (siehe Abschnitt "Konfigurationsschema").
2. Skript mit `pipx run` ausführen. Die Abhängigkeit (`python-docx`) steht als PEP-723-Header
   im Skript, `pipx run` installiert sie automatisch:
   ```bash
   pipx run scripts/generate.py --config config.json
   ```
   - `--output pfad` überschreibt optional das `output`-Feld aus der Config.
   - `--variante text|schueler|lehrer|beide` steuert, welche Version(en) erzeugt werden
     (Standard: `text` = nur `.txt`, siehe Abschnitt "Varianten" unten).

**Wichtig:**
- Den Ausgabepfad (`output` in der Config, z. B. `quiz_THEMA_NNfragen.txt`) mit dem
  tatsächlichen Thema und der Anzahl der Fragen befüllen.
- Standardmäßig im aktuellen Arbeitsverzeichnis speichern. Falls der Nutzer einen anderen
  Speicherort nennt oder im aktuellen Verzeichnis kein sinnvoller Ablageort ist, vorher nachfragen.

### Konfigurationsschema

Die Config ist ein JSON-Objekt mit folgenden Feldern:

| Feld | Pflicht | Beschreibung |
|---|---|---|
| `output` | ja | Ausgabepfad; Endung wird bei `text` durch `.txt` ersetzt, bei Docx-Varianten `.docx` verwenden |
| `aussagen` | ja | Liste von `{"text": str, "antwort": "wahr"\|"falsch", "erklaerung": str}` |

`erklaerung` ist pro Aussage optional, aber empfohlen – sie wird für die Lösungstabelle im
Chat (Schritt 4) verwendet und fließt nicht in die Dateien ein.

Referenz-Config mit vollständigem Beispiel: [`example_config.json`](example_config.json).

### Schritt 4: Lösungsblatt im Chat ausgeben

Nach der Datei-Erstellung: Gib eine übersichtliche Lösungstabelle im Chat aus:

| Nr. | Aussage (gekürzt) | Antwort | Erklärung |
|-----|-------------------|---------|-----------|
| 1   | ...               | Wahr    | ...       |

### Varianten

Die `.txt`-Lösungsdatei enthält pro Zeile nur Präfix und Aussagetext (keine Nummerierung,
keine Erklärung), in der Reihenfolge der Config. Präfix aus dem `antwort`-Wert:
`[w]` = wahr, `[f]` = falsch.

```
[w] Aussagetext eins
[f] Aussagetext zwei
```

| `--variante` | Docx | `.txt` |
|---|---|---|
| `text` (Standard) | – | `output` mit `.txt`-Endung |
| `lehrer` | `output` mit `[w]`/`[f]`-Präfix | `output` mit `.txt` statt `.docx` |
| `schueler` | `output` ohne Präfix (Forms-Import) | `output` mit `_LOESUNG.txt`-Suffix |
| `beide` | `output` (Schüler) + `output` mit `_LOESUNG`-Suffix (Lehrer) | `output` mit `_LOESUNG.txt`-Suffix |

Wichtig:
- **Standard ist immer `--variante text`.** Docx-Varianten nur verwenden, wenn der Nutzer ausdrücklich ein Word-Dokument / docx / Forms-Import verlangt. Ohne Angabe, welche Docx-Version: `schueler` für Forms-Import, `lehrer` für eigene Übersicht, `beide` auf Wunsch.
- Die Lehrerversion ist **nicht** für den direkten Microsoft-Forms-Import geeignet, da die Präfixe sonst als Teil der Frage übernommen würden.

### Schritt 5: Ausgabe

- Dateiname: `quiz_[thema]_[anzahl]fragen.txt` (bei Docx-Wunsch zusätzlich `.docx`, siehe Tabelle oben)
- Speicherpfad: aktuelles Arbeitsverzeichnis (siehe Hinweis in Schritt 3)
- Dem Nutzer mitteilen:
  - Anzahl der Aussagen und Wahr/Falsch-Verteilung
  - Nur bei Docx-Ausgabe: Hinweis, dass das Dokument direkt in Microsoft Forms importierbar ist

---

## Microsoft Forms Import-Anleitung (nur bei Docx-Ausgabe)

1. Microsoft Forms öffnen → **Neues Quiz**
2. Oben rechts **„…"** → **„Fragen importieren"**
3. Die `.docx`-Datei hochladen
4. Nach Import: Punkte prüfen und ggf. anpassen (+1 / -1)
