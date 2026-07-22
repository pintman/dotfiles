---
name: wahr-falsch-quiz
description: >
  Erstellt Wahr-Falsch-Quizze als Word-Dokument (.docx) im Microsoft Forms Import-Format,
  speziell für IT-Auszubildende (Fachinformatiker und Informationstechnische Assistenten).
  Nutze diesen Skill immer wenn der Nutzer ein Quiz, eine Wissensüberprüfung, Aussagen zum
  Einschätzen, True/False-Fragen oder ein Wahr-Falsch-Quiz zu einem IT-Thema erstellen möchte
  - auch wenn das Wort Skill nicht fällt. Trigger auch bei Formulierungen wie
  Erstell mir Fragen zu, Ich brauche ein Quiz über, Mach eine Wissensüberprüfung zu.
---

# Wahr-Falsch-Quiz Skill

## Zweck
Dieser Skill erstellt Wahr-Falsch-Quizze für IT-Auszubildende (Fachinformatiker und Informationstechnische Assistenten). Die Ausgabe ist ein Word-Dokument (.docx), das direkt in Microsoft Forms importiert werden kann.

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

### Schritt 3: Word-Dokument erstellen

#### Format (Microsoft Forms-kompatibel)

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
2. Skript ausführen (falls `python-docx` fehlt, in einer temporären virtuellen Umgebung installieren):
   ```bash
   python3 -m venv /tmp/wahr_falsch_quiz_venv
   /tmp/wahr_falsch_quiz_venv/bin/pip install --quiet python-docx
   /tmp/wahr_falsch_quiz_venv/bin/python scripts/generate.py --config config.json
   ```
   - `--output pfad.docx` überschreibt optional das `output`-Feld aus der Config.
   - `--variante schueler|lehrer|beide` steuert, welche Version(en) erzeugt werden
     (Standard: `lehrer`, siehe Abschnitt "Lehrerversion" unten).

**Wichtig:**
- Den Ausgabepfad (`output` in der Config bzw. `quiz_THEMA_NNfragen.docx`) mit dem
  tatsächlichen Thema und der Anzahl der Fragen befüllen.
- Standardmäßig im aktuellen Arbeitsverzeichnis speichern. Falls der Nutzer einen anderen
  Speicherort nennt oder im aktuellen Verzeichnis kein sinnvoller Ablageort ist, vorher nachfragen.

### Konfigurationsschema

Die Config ist ein JSON-Objekt mit folgenden Feldern:

| Feld | Pflicht | Beschreibung |
|---|---|---|
| `output` | ja | Ausgabepfad der .docx-Datei |
| `aussagen` | ja | Liste von `{"text": str, "antwort": "wahr"\|"falsch", "erklaerung": str}` |

`erklaerung` ist pro Aussage optional, aber empfohlen – sie wird für die Lösungstabelle im
Chat (Schritt 4) verwendet und fließt nicht in das Docx selbst ein.

Referenz-Config mit vollständigem Beispiel: [`example_config.json`](example_config.json).

### Schritt 4: Lösungsblatt im Chat ausgeben

Nach der Docx-Erstellung: Gib eine übersichtliche Lösungstabelle im Chat aus:

| Nr. | Aussage (gekürzt) | Antwort | Erklärung |
|-----|-------------------|---------|-----------|
| 1   | ...               | Wahr    | ...       |

### Lehrerversion mit Lösungs-Präfix (auf Wunsch)

Der Nutzer bevorzugt für die eigene Kontrolle/Vorbereitung eine **Lehrer-Lösungsversion** des Dokuments: Statt (oder zusätzlich zur) Lösungstabelle im Chat wird jeder Aussage im Docx-Text selbst ein Präfix vorangestellt:
- `[w]` für wahre Aussagen
- `[f]` für falsche Aussagen

Das Skript übernimmt das automatisch über den `antwort`-Wert jeder Aussage in der Config
(kein manuelles Einfügen der Präfixe nötig). Gesteuert wird das über `--variante`:

| `--variante` | Erzeugt | Präfix im Text |
|---|---|---|
| `lehrer` (Standard) | eine Datei unter `output` | ja, `[w]`/`[f]` |
| `schueler` | eine Datei unter `output` | nein |
| `beide` | `output` (Schülerversion) + `output` mit `_LOESUNG`-Suffix (Lehrerversion) | nur bei der `_LOESUNG`-Datei |

Wichtig:
- Die Lehrerversion ist **nicht** für den direkten Microsoft-Forms-Import an Schüler geeignet, da die Präfixe sonst als Teil der Frage übernommen würden. Sie dient nur der eigenen Übersicht des Lehrers, der die Präfixe vor der Verteilung selbst entfernt.
- Wenn der Nutzer nicht explizit angibt, ob er die reine Schülerversion oder die Lehrerversion mit Präfix möchte: Standardmäßig `--variante lehrer` verwenden, da dies die vom Nutzer bevorzugte Arbeitsweise ist. Auf Wunsch `--variante beide` für beide Dateien parallel.

### Schritt 5: Ausgabe

- Dateiname: `quiz_[thema]_[anzahl]fragen.docx` (siehe `output` in der Config)
- Speicherpfad: aktuelles Arbeitsverzeichnis (siehe Hinweis in Schritt 3)
- Dem Nutzer mitteilen:
  - Anzahl der Aussagen und Wahr/Falsch-Verteilung
  - Hinweis: Dokument direkt in Microsoft Forms importierbar

---

## Microsoft Forms Import-Anleitung

1. Microsoft Forms öffnen → **Neues Quiz**
2. Oben rechts **„…"** → **„Fragen importieren"**
3. Die `.docx`-Datei hochladen
4. Nach Import: Punkte prüfen und ggf. anpassen (+1 / -1)
