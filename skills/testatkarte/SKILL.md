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

Verwende das docx-Skill. Installiere falls nötig: `npm install -g docx`

**Seitenaufbau:**
- **A4** (11906 × 16838 DXA), Ränder 1440 DXA (1 Zoll) rundherum
- **Seite 1**: Namenszeile + Titel + Einleitungstext + Meilensteintabelle
- **Seiten 2–4**: Zusatzinformationen mit Abschnitten

**Farbschema** (schwarz-weiß, druckfreundlich):
- Tabellenheader-Hintergrund: `000000` (schwarz)
- Tabellenheader-Schrift: `FFFFFF` (weiß)
- Ungerade Zeilen: `EEEEEE` (hellgrau)
- Gerade Zeilen: `FFFFFF` (weiß)
- Überschriften-Farbe: `000000` (schwarz)

**Schriftgrößen**: Mindestens 11pt (= `size: 22` in docx). Fließtext 11pt, Überschriften 12–16pt.

---

## Code-Template

```javascript
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  VerticalAlign, PageBreak, LevelFormat
} = require('docx');
const fs = require('fs');

// ── Konstanten ──────────────────────────────────────────────
const PAGE_W = 11906;   // A4 Breite in DXA
const PAGE_H = 16838;   // A4 Höhe in DXA
const MARGIN  = 1440;   // 1 Zoll Rand
const CONTENT_W = PAGE_W - 2 * MARGIN;  // 9026 DXA

const COLOR_HEADER_BG   = '000000'; // schwarz
const COLOR_HEADER_TEXT = 'FFFFFF'; // weiß
const COLOR_ROW_ODD     = 'EEEEEE'; // hellgrau
const COLOR_ROW_EVEN    = 'FFFFFF'; // weiß
const COLOR_BORDER      = '000000'; // schwarz
const COLOR_TITLE       = '000000'; // schwarz

const border = { style: BorderStyle.SINGLE, size: 1, color: COLOR_BORDER };
const borders = { top: border, bottom: border, left: border, right: border };

// ── Hilfsfunktionen ─────────────────────────────────────────
function headerCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: COLOR_HEADER_BG, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, bold: true, color: COLOR_HEADER_TEXT, size: 22, font: 'Arial' })]
    })]
  });
}

function dataCell(text, width, isOdd, bold = false, wrap = true) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: isOdd ? COLOR_ROW_ODD : COLOR_ROW_EVEN, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      children: [new TextRun({ text, bold, size: 22, font: 'Arial' })]
    })]
  });
}

function heading(text, level = HeadingLevel.HEADING_1) {
  return new Paragraph({
    heading: level,
    children: [new TextRun({ text, font: 'Arial' })]
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
    spacing: { before: opts.spaceBefore || 0, after: opts.spaceAfter || 120 },
    children: [new TextRun({ text, font: 'Arial', size: opts.size || 22, bold: opts.bold || false, italics: opts.italic || false })]
  });
}

// ── MEILENSTEINE (anpassen!) ─────────────────────────────────
const THEMA = 'THEMA';
const KLASSE = 'KLASSE';  // z.B. ITA, FIA
const EINLEITUNG = 'Bearbeite nacheinander die folgenden Meilensteine. Lasse jeden Meilenstein von einem Fachlehrer abzeichnen, sobald du ihn erfolgreich absolviert hast. Während der Abnahme werden ggf. kleine Fehler eingebaut, die korrigiert werden müssen. Letzter Abnahmezeitpunkt: 20 Minuten vor Stundenende. Es sind maximal 2 Meilensteine pro Sitzung möglich.';

const MEILENSTEINE = [
  // { nr: 1, text: "Aufgabenbeschreibung..." },
  // ... weitere Meilensteine
];

// ── SPALTENBREITEN ───────────────────────────────────────────
const COL_NR     = 600;
const COL_TESTAT = 1800;
const COL_TEXT   = CONTENT_W - COL_NR - COL_TESTAT;  // Rest

// ── SEITE 1: Meilensteintabelle ──────────────────────────────
const meilensteinRows = MEILENSTEINE.map((m, i) => {
  const isOdd = i % 2 === 0;
  return new TableRow({
    children: [
      dataCell(String(m.nr), COL_NR, isOdd, true),
      dataCell(m.text, COL_TEXT, isOdd),
      dataCell('', COL_TESTAT, isOdd),
    ]
  });
});

const meilensteinTable = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA },
  columnWidths: [COL_NR, COL_TEXT, COL_TESTAT],
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        headerCell('Nr.', COL_NR),
        headerCell('Meilenstein', COL_TEXT),
        headerCell('Testat, Datum', COL_TESTAT),
      ]
    }),
    ...meilensteinRows
  ]
});

// ── NAMEZEILE ────────────────────────────────────────────────
const nameBorder = { style: BorderStyle.SINGLE, size: 1, color: COLOR_BORDER };
const nameBorders = { top: nameBorder, bottom: nameBorder, left: nameBorder, right: nameBorder };

const nameTable = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA },
  columnWidths: [1800, CONTENT_W - 1800],
  rows: [new TableRow({
    children: [
      new TableCell({
        borders: nameBorders,
        width: { size: 2200, type: WidthType.DXA },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text: 'Name:', bold: true, font: 'Arial', size: 22 })] })]
      }),
      new TableCell({
        borders: nameBorders,
        width: { size: CONTENT_W - 1800, type: WidthType.DXA },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text: '', font: 'Arial', size: 22 })] })]
      }),
    ]
  })]
});

// ── SEITEN 2-4: Zusatzinformationen ──────────────────────────
// Hier kommt das themenspezifische Referenzmaterial rein.
// Beispiel-Struktur (anpassen!):
const zusatzSeiten = [
  new Paragraph({ children: [new PageBreak()] }),
  heading('Zusatzinformationen'),
  // ... Abschnitte mit para(), heading(), Tabellen, Codeblöcken etc.
];

// ── DOKUMENT ZUSAMMENBAUEN ───────────────────────────────────
const doc = new Document({
  styles: {
    default: { document: { run: { font: 'Arial', size: 22 } } },
    paragraphStyles: [
      {
        id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 28, bold: true, font: 'Arial', color: COLOR_TITLE },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 }
      },
      {
        id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 24, bold: true, font: 'Arial', color: COLOR_TITLE },
        paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 1 }
      },
      {
        id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 22, bold: true, font: 'Arial' },
        paragraph: { spacing: { before: 120, after: 60 }, outlineLevel: 2 }
      },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_W, height: PAGE_H },
        margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN }
      }
    },
    children: [
      nameTable,
      para(''),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 120 },
        children: [new TextRun({ text: `Testatkarte – ${THEMA} – ${KLASSE}`, bold: true, size: 32, font: 'Arial', color: COLOR_TITLE })]
      }),
      para(''),
      para(EINLEITUNG, { size: 22, spaceAfter: 200 }),
      meilensteinTable,
      ...zusatzSeiten,
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('/mnt/user-data/outputs/testatkarte.docx', buf);
  console.log('Testatkarte erstellt!');
});
```

---

## Zusatzinformationen gestalten (Seiten 2–4)

Die Zusatzinformationen sollen Schülern helfen, die Meilensteine zu lösen. Typische Abschnitte:

### Klassendiagramme / Strukturdiagramme
Verwende Tabellen, um UML-Klassendiagramme nachzubilden:
```
| KlassenName       |
|-------------------|
| + attribut: Typ   |
| + methode(): void |
```

### Codebeispiele
Verwende `Courier New`-Schrift (Monospace) für Code-Abschnitte:
```javascript
new TextRun({ text: 'code hier', font: 'Courier New', size: 22 })
```
Füge jede Code-Zeile als separaten Paragraph mit grauem Hintergrund ein:
```javascript
new Paragraph({
  shading: { fill: 'F0F0F0', type: ShadingType.CLEAR },
  children: [new TextRun({ text: 'from gpiozero import LED', font: 'Courier New', size: 22 })]
})
```

### Hilfreiche LLM-Prompts
Kursiv formatierte Prompts, die Schüler bei einer KI eingeben können:
```javascript
new TextRun({ text: 'Prompt-Text', italics: true, size: 22, font: 'Arial' })
```

### Konzepterklärungen / Tabellen
Erklärungen zu Begriffen, Operatoren, Konzepten als beschriftete Tabellen oder Fließtext.

---

## Qualitätsprüfung

Vor der Ausgabe prüfen:
- [ ] Alle Meilensteine umfassen in Summe genug Arbeit für die geplante Projektdauer
- [ ] Jeder Meilenstein ist klar formuliert und eindeutig prüfbar
- [ ] Dokument hat maximal 4 Seiten
- [ ] Meilensteintabelle passt auf Seite 1 (ggf. Schriftgröße auf 16 reduzieren)
- [ ] Zusatzinfos auf Seiten 2–4 sind themenspezifisch und hilfreich
- [ ] Dokument mit `python scripts/office/validate.py` validiert

---

## Nach der Erstellung

Sobald die Testatkarte fertig erstellt und ausgegeben wurde, frage den Nutzer, ob mit dem
Skill `testat-vorabnahme` (gleicher Ordner) ein passender Selbstcheck-Prompt zu dieser
Testatkarte erstellt werden soll (Meta-Prompt, mit dem Schüler/Auszubildende in einem
beliebigen KI-Chat selbst prüfen können, ob sie testat-reif sind).

---

## Abhängigkeiten

- `docx` npm-Paket: `npm install -g docx`
- Validierung: `python scripts/office/validate.py` (aus dem docx-Skill)
