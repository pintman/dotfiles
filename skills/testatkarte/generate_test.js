const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  VerticalAlign, PageBreak
} = require('docx');
const fs = require('fs');

// ── Konstanten ──────────────────────────────────────────────
const PAGE_W    = 11906;
const PAGE_H    = 16838;
const MARGIN    = 1080;  // ~1.9 cm – etwas enger für mehr Platz
const CONTENT_W = PAGE_W - 2 * MARGIN; // 9746

const BK = '000000';  // Schwarz
const WH = 'FFFFFF';  // Weiß
const GR = 'EEEEEE';  // Hellgrau für Code

const thinB  = { style: BorderStyle.SINGLE, size: 2,  color: BK };
const thickB = { style: BorderStyle.SINGLE, size: 8,  color: BK };
const cellBorders = { top: thinB, bottom: thinB, left: thinB, right: thinB };
// Header-Zeile: dickere obere/untere Linie
const headBorders = {
  top: thickB, bottom: thickB,
  left: thinB, right: thinB
};

// ── Hilfsfunktionen ─────────────────────────────────────────
function headerCell(text, width, align = AlignmentType.CENTER) {
  return new TableCell({
    borders: headBorders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: WH, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: align,
      children: [new TextRun({ text, bold: true, size: 18, font: 'Arial' })]
    })]
  });
}

function dataCell(text, width, bold = false, align = AlignmentType.LEFT) {
  return new TableCell({
    borders: cellBorders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: WH, type: ShadingType.CLEAR },
    margins: { top: 60, bottom: 60, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: align,
      children: [new TextRun({ text, bold, size: 17, font: 'Arial' })]
    })]
  });
}

function h(text, level = HeadingLevel.HEADING_1) {
  return new Paragraph({ heading: level, children: [new TextRun({ text, font: 'Arial' })] });
}

function p(text, opts = {}) {
  return new Paragraph({
    alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
    spacing: { before: opts.before || 0, after: opts.after || 100 },
    shading: opts.code ? { fill: GR, type: ShadingType.CLEAR } : undefined,
    children: [new TextRun({
      text,
      font: opts.code ? 'Courier New' : 'Arial',
      size: opts.size || (opts.code ? 16 : 18),
      bold: opts.bold || false,
      italics: opts.italic || false,
    })]
  });
}

const codeLine = (text) => p(text, { code: true, after: 0 });
const promptText = (text) => p(text, { italic: true, size: 17, after: 60 });

// ── Inhalte ──────────────────────────────────────────────────
const THEMA  = 'LEDs';
const KLASSE = 'ITA';

const EINLEITUNG =
  'Bearbeite nacheinander die folgenden Meilensteine. Lasse jeden Meilenstein von einem Fachlehrer abzeichnen, ' +
  'sobald du ihn erfolgreich absolviert hast. Während der Abnahme werden ggf. kleine Fehler eingebaut, ' +
  'die korrigiert werden müssen. Letzter Abnahmezeitpunkt: 20 Minuten vor Stundenende. ' +
  'Es sind maximal 2 Meilensteine pro Sitzung möglich.';

const MEILENSTEINE = [
  { nr: 1,  text: 'Stelle eine SSH-Verbindung vom Laptop zum Raspberry Pi her und navigiere per Konsole in ein Verzeichnis deiner Wahl.' },
  { nr: 2,  text: 'Übertrage einen Ordner mit mindestens einem Unterordner und mehreren Dateien per SCP auf den Raspberry Pi. Übertrage die Dateien danach zurück auf den Laptop.' },
  { nr: 3,  text: 'Erstelle ein Python-Programm hallo.py auf dem Pi. Das Programm fragt nach dem Namen und gibt "Hallo NAME" aus. Führe es in der Konsole aus.' },
  { nr: 4,  text: 'Erstelle eine virtuelle Python-Umgebung mit venv, aktiviere sie und führe hallo.py darin aus.' },
  { nr: 5,  text: 'Importiere die LED-Klasse aus gpiozero. Erstelle drei LED-Objekte an korrekten GPIO-Pins. Das Programm liest eine Zahl (1–3) und danach "an" oder "aus" ein und schaltet die zugehörige LED entsprechend.' },
  { nr: 6,  text: 'Erkläre handschriftlich die OOP-Begriffe Objekt, Klasse, Attribut und Methode jeweils an einem selbst gewählten Beispiel.' },
  { nr: 7,  text: 'Schreibe ein Programm, das drei LEDs binär von 0 bis 7 hochzählt (000 → 001 → 010 …). Jeder Druck auf Enter zeigt den nächsten Wert als leuchtende LEDs.' },
  { nr: 8,  text: 'Schreibe ein Python-Programm, das eine vollständige Ampelschaltung (Rot → Rot-Gelb → Grün → Gelb → Rot) mit time.sleep() durchläuft.' },
  { nr: 9,  text: 'Erstelle ein Reaktionsspiel: Nach einer zufälligen Wartezeit leuchtet eine LED auf; der Schüler drückt eine Taste. Die Reaktionszeit wird gemessen und ausgegeben.' },
  { nr: 10, text: 'Beschreibe auf Papier zwei Attribute und zwei Methoden der Klasse LED aus gpiozero mit kurzen Beispielen.' },
  { nr: 11, text: 'Dokumentiere einen erfolgreichen Testlauf eines deiner Programme mit einem kurzen Video (max. 60 Sekunden).' },
  { nr: 12, text: 'Erweitere das Projekt um eine kreative eigene Funktion (z. B. Morse-Code, Musikrhythmus, PWM-Dimmer) und präsentiere sie.' },
];

// ── Spaltenbreiten ────────────────────────────────────────────
const COL_NR     = 480;
const COL_TESTAT = 1800;
const COL_TEXT   = CONTENT_W - COL_NR - COL_TESTAT;

// ── Meilensteintabelle ────────────────────────────────────────
const mRows = MEILENSTEINE.map((m) =>
  new TableRow({ children: [
    dataCell(String(m.nr), COL_NR, true, AlignmentType.CENTER),
    dataCell(m.text, COL_TEXT),
    dataCell('', COL_TESTAT),
  ]})
);

const mTable = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA },
  columnWidths: [COL_NR, COL_TEXT, COL_TESTAT],
  rows: [
    new TableRow({ tableHeader: true, children: [
      headerCell('Nr.', COL_NR, AlignmentType.CENTER),
      headerCell('Meilenstein', COL_TEXT, AlignmentType.LEFT),
      headerCell('Testat, Datum', COL_TESTAT, AlignmentType.CENTER),
    ]}),
    ...mRows
  ]
});

// ── Namenszeile ───────────────────────────────────────────────
const nameBorders = {
  top: thickB, bottom: thickB, left: thickB, right: thickB
};
const nameTable = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA },
  columnWidths: [1600, CONTENT_W - 1600],
  rows: [new TableRow({ children: [
    new TableCell({
      borders: nameBorders,
      width: { size: 1600, type: WidthType.DXA },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({ children: [new TextRun({ text: 'Name:', bold: true, font: 'Arial', size: 20 })] })]
    }),
    new TableCell({
      borders: nameBorders,
      width: { size: CONTENT_W - 1600, type: WidthType.DXA },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({ children: [new TextRun({ text: '', font: 'Arial', size: 20 })] })]
    }),
  ]})]
});

// ── Klassendiagramm-Tabelle ───────────────────────────────────
const KD_W = 4000;
const kdBorderH = { top: thickB, bottom: thickB, left: thickB, right: thickB };
const kdBorderD = { top: thinB, bottom: thinB, left: thickB, right: thickB };

const kdTable = new Table({
  width: { size: KD_W, type: WidthType.DXA },
  columnWidths: [KD_W],
  rows: [
    new TableRow({ children: [new TableCell({
      borders: kdBorderH,
      margins: { top: 60, bottom: 60, left: 120, right: 120 },
      children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: 'LED', bold: true, size: 20, font: 'Arial' })] })]
    })]}),
    new TableRow({ children: [new TableCell({
      borders: kdBorderD,
      margins: { top: 60, bottom: 60, left: 120, right: 120 },
      children: [
        new Paragraph({ children: [new TextRun({ text: '+ is_lit: bool', font: 'Courier New', size: 18 })] }),
        new Paragraph({ children: [new TextRun({ text: '+ pin: int',     font: 'Courier New', size: 18 })] }),
        new Paragraph({ children: [new TextRun({ text: '+ value: int',   font: 'Courier New', size: 18 })] }),
      ]
    })]}),
    new TableRow({ children: [new TableCell({
      borders: kdBorderD,
      margins: { top: 60, bottom: 60, left: 120, right: 120 },
      children: [
        new Paragraph({ children: [new TextRun({ text: '+ LED(pin: int | str)', font: 'Courier New', size: 18 })] }),
        new Paragraph({ children: [new TextRun({ text: '+ on(): void',          font: 'Courier New', size: 18 })] }),
        new Paragraph({ children: [new TextRun({ text: '+ off(): void',         font: 'Courier New', size: 18 })] }),
        new Paragraph({ children: [new TextRun({ text: '+ toggle(): void',      font: 'Courier New', size: 18 })] }),
      ]
    })]}),
  ]
});

// ── Seiten 2–4: Zusatzinformationen ──────────────────────────
const zusatz = [
  new Paragraph({ children: [new PageBreak()] }),
  h('Zusatzinformationen'),

  h('Die Klasse LED', HeadingLevel.HEADING_2),
  h('Klassendiagramm', HeadingLevel.HEADING_3),
  p('Attribute: is_lit, pin, value', { after: 80 }),
  p('Methoden: on(), off(), toggle(), blink(), …', { after: 120 }),
  kdTable,
  p(''),

  h('Beispielverwendung', HeadingLevel.HEADING_3),
  codeLine('from gpiozero import LED'),
  codeLine('from time import sleep'),
  codeLine(''),
  codeLine('red = LED(17)  # LED-Objekt an GPIO-Pin 17'),
  codeLine(''),
  codeLine('while True:'),
  codeLine('    red.on()'),
  codeLine('    sleep(1)'),
  codeLine('    red.off()'),
  codeLine('    sleep(1)'),
  p(''),

  h('Hilfreiche Prompts', HeadingLevel.HEADING_2),
  p('Solltest du bei einem Meilenstein nicht weiterkommen, nutze folgende Prompts bei einem LLM (z. B. Claude).', { after: 120 }),

  h('Verbindungsprobleme mit dem Raspberry Pi', HeadingLevel.HEADING_3),
  promptText('# Das Problem'),
  promptText('Ich kann mich nicht von meinem Laptop aus mit meinem Raspberry Pi verbinden.'),
  promptText('# Rahmenbedingungen'),
  promptText('Ich bin im Schulraum. Es gibt ein lokales WLAN. Die Clients sehen sich gegenseitig.'),
  promptText('# Auftrag'),
  promptText('Welche Schritte kann ich unternehmen, um die Ursache zu finden und das Problem zu lösen?'),
  p(''),

  h('Dateien übertragen', HeadingLevel.HEADING_3),
  promptText('Ich habe einen Raspberry Pi und einen Laptop. Wie kann ich Dateien und ganze Ordner per SCP übertragen? Zeige mir den Prozess Schritt für Schritt und erkläre mögliche Probleme.'),
  p(''),

  h('Virtuelle Python-Umgebung', HeadingLevel.HEADING_3),
  promptText('Ich bin per SSH mit meinem Raspberry Pi verbunden und möchte eine virtuelle Python-Umgebung mit venv erstellen. Erkläre mir jeden Schritt und mögliche Fehlerquellen.'),

  new Paragraph({ children: [new PageBreak()] }),
  h('Bit-Operationen'),

  h('Shift-Operator (>>)', HeadingLevel.HEADING_2),
  p('Verschiebt die Bits einer Zahl x-mal nach rechts. Das letzte Bit wird verworfen.', { after: 80 }),
  codeLine('# 6 in binär: 110'),
  codeLine('6 >> 1  # 110 -> 011 = 3'),
  codeLine('6 >> 2  # 110 ->  01 = 1'),
  p(''),

  h('Bitweise UND-Verknüpfung (&)', HeadingLevel.HEADING_2),
  p('Ergibt 1, wenn beide Bits 1 sind, sonst 0. Nützlich zum Prüfen einzelner Bits.', { after: 80 }),
  codeLine('  5 in binär:  101'),
  codeLine('& 1 in binär:  001'),
  codeLine('─────────────────'),
  codeLine('Ergebnis: 5 & 1 = 001 = 1'),
  p(''),
  p('& 1 prüft, ob eine Zahl ungerade (Bit = 1) oder gerade (Bit = 0) ist.', { after: 80 }),

  h('Bit prüfen – Beispiel', HeadingLevel.HEADING_2),
  codeLine('x = 0b101  # = 5 dezimal'),
  codeLine(''),
  codeLine('if x & 0b100 != 0: print("Bit 2 gesetzt")  # -> ausgegeben'),
  codeLine('if x & 0b010 != 0: print("Bit 1 gesetzt")  # -> nicht ausgegeben'),
  codeLine('if x & 0b001 != 0: print("Bit 0 gesetzt")  # -> ausgegeben'),
  p(''),
  p('Binärformat angeben: Präfix 0b verwenden, z. B. 0b101 = 5.', { italic: true }),
];

// ── Dokument ──────────────────────────────────────────────────
const doc = new Document({
  styles: {
    default: { document: { run: { font: 'Arial', size: 20 } } },
    paragraphStyles: [
      {
        id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 28, bold: true, font: 'Arial' },
        paragraph: {
          spacing: { before: 240, after: 120 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BK, space: 1 } },
          outlineLevel: 0
        }
      },
      {
        id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 24, bold: true, font: 'Arial' },
        paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 1 }
      },
      {
        id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 20, bold: true, font: 'Arial' },
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
      p(''),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 160 },
        children: [new TextRun({ text: `Testatkarte – ${THEMA} – ${KLASSE}`, bold: true, size: 36, font: 'Arial' })]
      }),
      new Paragraph({
        spacing: { before: 0, after: 180 },
        children: [new TextRun({ text: EINLEITUNG, size: 17, font: 'Arial' })]
      }),
      mTable,
      ...zusatz,
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('/tmp/testatkarte/testatkarte_LEDs_ITA.docx', buf);
  console.log('Fertig!');
});
