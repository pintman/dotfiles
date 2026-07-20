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

#### Ansatz: python-docx

Falls `python-docx` noch nicht installiert ist:
```bash
pip install python-docx --quiet
```
(Falls das System eine "externally-managed-environment"-Fehlermeldung zeigt, zusätzlich `--break-system-packages` anhängen oder eine virtuelle Umgebung nutzen.)

#### Python-Skript

```python
from docx import Document
from docx.shared import Pt

aussagen = ["Aussage 1...", "Aussage 2...", ...]  # Liste der generierten Aussagen

intro = (
    "Beurteile die Korrektheit der folgenden Aussagen. "
    "Für jede korrekte Antwort gibt es einen Punkt, für jede falsche Antwort gibt es einen Minuspunkt. "
    "Durch den Abzug können nicht weniger als 0 Punkte in dieser Aufgabe erzielt werden. "
    "Jede nicht oder nicht eindeutig gekennzeichnete Aussage ergibt 0 Punkte. "
    "Rate nicht."
)

doc = Document()

# Standardschriftart setzen
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)

# Einleitungstext
doc.add_paragraph(intro)
doc.add_paragraph("")  # Leerzeile

# Fragen mit Antwortoptionen
for i, aussage in enumerate(aussagen, start=1):
    doc.add_paragraph(f"{i}. {aussage}")
    doc.add_paragraph("a) Wahr")
    doc.add_paragraph("b) Falsch")
    doc.add_paragraph("")  # Leerzeile zwischen den Fragen

output_path = "quiz_THEMA_NNfragen.docx"
doc.save(output_path)
print(f"Gespeichert: {output_path}")
```

**Wichtig:**
- Den Dateinamen (`quiz_THEMA_NNfragen.docx`) mit dem tatsächlichen Thema und der Anzahl der Fragen befüllen.
- Standardmäßig im aktuellen Arbeitsverzeichnis speichern. Falls der Nutzer einen anderen Speicherort nennt oder im aktuellen Verzeichnis kein sinnvoller Ablageort ist, vorher nachfragen.

### Schritt 4: Lösungsblatt im Chat ausgeben

Nach der Docx-Erstellung: Gib eine übersichtliche Lösungstabelle im Chat aus:

| Nr. | Aussage (gekürzt) | Antwort | Erklärung |
|-----|-------------------|---------|-----------|
| 1   | ...               | Wahr    | ...       |

### Lehrerversion mit Lösungs-Präfix (auf Wunsch)

Der Nutzer bevorzugt für die eigene Kontrolle/Vorbereitung eine **Lehrer-Lösungsversion** des Dokuments: Statt (oder zusätzlich zur) Lösungstabelle im Chat wird jeder Aussage im Docx-Text selbst ein Präfix vorangestellt:
- `[w]` für wahre Aussagen
- `[f]` für falsche Aussagen

Format je Aussage: `{i}. [w] {Aussage}` bzw. `{i}. [f] {Aussage}` (Präfix direkt nach der Nummerierung, vor dem Aussagetext).

Wichtig:
- Diese Version ist **nicht** für den direkten Microsoft-Forms-Import an Schüler geeignet, da die Präfixe sonst als Teil der Frage übernommen würden. Sie dient nur der eigenen Übersicht des Lehrers, der die Präfixe vor der Verteilung selbst entfernt.
- Dateiname entsprechend kennzeichnen, z. B. `quiz_[thema]_[anzahl]fragen_LOESUNG.docx`.
- Wenn der Nutzer nicht explizit angibt, ob er die reine Schülerversion oder die Lehrerversion mit Präfix möchte: Standardmäßig die Lehrerversion mit `[w]`/`[f]`-Präfix erstellen, da dies die vom Nutzer bevorzugte Arbeitsweise ist. Auf Wunsch zusätzlich die präfixfreie Schülerversion parallel bereitstellen.

### Schritt 5: Ausgabe

- Dateiname: `quiz_[thema]_[anzahl]fragen.docx`
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
