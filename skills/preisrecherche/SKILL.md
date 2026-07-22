---
name: preisrecherche
description: "Recherchiert Preise für Elektronikartikel bei verschiedenen Händlern – insbesondere für öffentliche Beschaffungen, bei denen mindestens drei Angebote benötigt werden. Typische Trigger: \"Preisvergleich\", \"Angebote einholen\", \"Beschaffung\", \"Preise recherchieren\", \"günstigsten Anbieter finden\", oder wenn eine Liste von Artikeln angegeben wird, die bei Händlern wie Conrad, Reichelt, Alternate, AZ Delivery, Berrybase oder Voelkner gesucht werden sollen. Ergebnis ist immer eine Excel-Datei (.xlsx). Trigger auch, wenn der Nutzer sagt \"such mir Preise für...\" oder \"vergleich die Preise für...\" – selbst ohne explizite Erwähnung von Excel oder Händlern."
---

# Preisrecherche-Skill

Dieser Skill recherchiert Preise für Elektronikartikel bei verschiedenen Händlern und erstellt daraus eine strukturierte Excel-Tabelle für die öffentliche Beschaffung (mind. 3 Angebote je Artikel).

---

## Schritt 1: Eingabe parsen

Die Artikelliste kann auf zwei Arten kommen:

**a) Als Text im Chat:**
Extrahiere jeden Artikel als einzelnen Suchbegriff. Beispiel:
```
- Raspberry Pi 4 Model B 4GB
- USB-C Netzteil 5V 3A
- HDMI Kabel 1m
```

**b) Als hochgeladene Datei (Excel oder Textdatei):**
Lese die Datei aus `/mnt/user-data/uploads/`. 
- `.xlsx` / `.csv`: Erste Spalte enthält die Artikelnamen
- `.txt`: Eine Zeile = ein Artikel

---

## Schritt 2: Händler festlegen

Standardmäßig werden **mindestens 3 Händler** gesucht. Bevorzugte Händler (je nach Verfügbarkeit):

| Händler | Such-URL (Beispiel) |
|---|---|
| Conrad | `https://www.conrad.de/search?search=ARTIKEL` |
| Reichelt | `https://www.reichelt.de/index.html?ACTION=446&LA=0&nbc=1&q=ARTIKEL` |
| Alternate | `https://www.alternate.de/search?query=ARTIKEL` |
| AZ Delivery | `https://www.az-delivery.de/search?type=product&q=ARTIKEL` |
| Berrybase | `https://www.berrybase.de/search?q=ARTIKEL` |
| Voelkner | `https://www.voelkner.de/search/search.html?query=ARTIKEL` |

Wenn ein Händler keinen passenden Treffer liefert, versuche den nächsten aus der Liste. Das Ziel sind **immer mindestens 3 Angebote** für eine Bestellung.

---

## Schritt 3: Websuche pro Artikel und Händler

Für jeden Artikel und jeden Händler:

1. Führe eine gezielte Websuche durch, z. B.:
   ```
   web_search: "Raspberry Pi 4 4GB site:conrad.de"
   ```
   oder alternativ direkt auf die Shop-Suche:
   ```
   web_fetch: https://www.conrad.de/search?search=Raspberry+Pi+4+4GB
   ```

2. Extrahiere aus dem Ergebnis:
   - **Artikelbezeichnung** (wie der Händler den Artikel nennt)
   - **Preis brutto** (inkl. 19% MwSt. – wie im Shop angezeigt)
   - **Preis netto** = Preis brutto / 1.19, gerundet auf 2 Dezimalstellen
   - **Link** zur Produktseite (direkte URL zum Artikel)

3. Falls kein eindeutiges Ergebnis gefunden wird:
   - Trage `"Nicht gefunden"` in die Felder ein
   - Versuche einen alternativen Händler

### Wichtige Hinweise zur Preisextraktion:
- Deutsche Shops zeigen Preise **immer brutto (inkl. MwSt.)** an
- MwSt.-Satz für Elektronik in Deutschland: **19%**
- Netto = Brutto ÷ 1,19
- Bei Staffelpreisen: den **Einzelpreis (Menge 1)** verwenden
- Bei Preisbereichen (z. B. Varianten): den günstigsten relevanten Preis nehmen

---

## Schritt 4: Excel-Tabelle erstellen

Nutze `openpyxl` um die Tabelle zu erstellen. Lies dazu den xlsx-Skill:
`/mnt/skills/public/xlsx/SKILL.md`

### Tabellenstruktur

**Erste Zeile (Überschriften-Gruppe):** Händlernamen als verbundene Spalten
**Zweite Zeile (Spaltenüberschriften):** Fixe Spalten

```
Spalte A: Gesuchter Artikel
Spalte B: Händler 1 – Artikelbezeichnung
Spalte C: Händler 1 – Preis netto (€)
Spalte D: Händler 1 – Preis brutto (€)
Spalte E: Händler 1 – Link
Spalte F: Händler 2 – Artikelbezeichnung
... (Wiederholung für jeden Händler)
Letzte Spalten: Günstigster Anbieter (netto), Günstigster Preis netto (€)
```

### Formatierungsvorgaben

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HAENDLER_FARBEN = {
    "Conrad":    "FFD700",  # Gold
    "Reichelt":  "4472C4",  # Blau
    "Alternate": "ED7D31",  # Orange
    "AZ Delivery": "70AD47", # Grün
    "Berrybase": "9B59B6",  # Lila
    "Voelkner":  "E74C3C",  # Rot
}

HEADER_FONT = Font(name="Arial", bold=True, color="FFFFFF", size=11)
DATA_FONT   = Font(name="Arial", size=10)
WRAP        = Alignment(wrap_text=True, vertical="top")
```

- **Zeilenhöhe:** Kopfzeilen 30px, Datenzeilen 40px
- **Spaltenbreiten:** Artikel 35, Bezeichnung 30, Preis 14, Link 12 (gekürzt mit Hyperlink)
- **Links:** Als Excel-Hyperlink einfügen (`ws.cell().hyperlink = url`), Text = "Link"
- **Wechselnde Zeilenfärbung:** Gerade Zeilen leicht grau (`F2F2F2`)
- **Händler-Gruppenheader:** Zellen verbinden, Händlerfarbe als Hintergrund
- **Preisspalten:** Zahlenformat `#.##0,00 €` (deutsches Format)
- **"Günstigster Anbieter":** Letzte Spaltengruppe, grüner Header (`70AD47`)

### Günstigster Anbieter (Formel)
Verwende Excel-Formeln (nicht Python-Berechnungen):
- Günstigster Preis: `=MIN(C3, G3, K3, ...)` (alle Nettospalten)
- Günstigster Anbieter: `=INDEX({"Conrad","Reichelt","Alternate",...}, MATCH(MIN(C3,G3,K3,...), (C3,G3,K3,...),0))`

---

## Schritt 5: Datei speichern und ausgeben

```python
wb.save("/mnt/user-data/outputs/preisrecherche.xlsx")
```

Dann `present_files` aufrufen mit dem Pfad zur Datei.

Abschließend im Chat kurz zusammenfassen:
- Wie viele Artikel wurden recherchiert
- Bei welchen Händlern
- Wie viele Artikel nicht gefunden wurden (falls zutreffend)

---

## Fehlerbehandlung

| Problem | Lösung |
|---|---|
| Händler-Seite nicht erreichbar | Anderen Händler verwenden |
| Preis nicht eindeutig | Günstigsten Einzelpreis nehmen, im Kommentar vermerken |
| Artikel nicht gefunden | "Nicht gefunden" eintragen, anderen Suchbegriff versuchen |
| Weniger als 3 Angebote | Nutzer informieren und weitere Händler vorschlagen |
| Datei leer / nicht lesbar | Nutzer um erneutes Hochladen bitten |
