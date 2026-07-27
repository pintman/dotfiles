---
name: preisrecherche
description: "Recherchiert Preise für Elektronikartikel bei verschiedenen Händlern (z. B. Conrad, Reichelt, Alternate, AZ Delivery, Berrybase, Voelkner) – insbesondere für öffentliche Beschaffungen, bei denen mindestens drei Angebote benötigt werden. Ergebnis ist immer eine Excel-Datei (.xlsx)."
disable-model-invocation: true
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
Lese die vom Nutzer angegebene Datei (lokaler Pfad). 
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

Die komplette Formatierung (Farben, Spaltenbreiten, verbundene Header, Hyperlinks,
MIN/INDEX-Formeln) sowie die Netto-Berechnung (Brutto ÷ 1,19) übernimmt
[`scripts/generate.py`](scripts/generate.py). 

Die recherchierten **Rohdaten** (Bezeichnung, Preis **brutto**, Link
je Artikel und Händler) kommen als JSON-Konfiguration rein; die Netto-
Preise, Formeln und das Layout erzeugt das Skript deterministisch.

### Vorgehen

1. JSON-Konfiguration nach dem Schema von
   [`scripts/example_config.json`](scripts/example_config.json) schreiben (siehe
   Abschnitt "Konfigurationsschema" unten). Preis **immer als Bruttopreis** (Zahl, Punkt
   als Dezimaltrennzeichen) eintragen — die Nettoumrechnung übernimmt das Skript.
2. Skript ausführen:
   ```bash
   python3 scripts/generate.py --config config.json
   ```
   `--output pfad.xlsx` überschreibt optional das `output`-Feld aus der Config.
3. Die Ausgabe des Skripts (Pfad, Anzahl Artikel, Händler, Anzahl "Nicht gefunden")
   direkt für die Rückmeldung in Schritt 5 verwenden.

### Konfigurationsschema

Die Config ist ein JSON-Objekt mit folgenden Feldern:

| Feld | Pflicht | Beschreibung |
|---|---|---|
| `output` | ja | Ausgabepfad der .xlsx-Datei |
| `haendler` | ja | Liste der Händlernamen, bestimmt Spaltenreihenfolge (mind. 3 empfohlen) |
| `artikel` | ja | Liste von `{"name": str, "angebote": {"<Händler>": {"bezeichnung": str\|null, "preis_brutto": float\|null, "link": str\|null}}}` |

Ein Angebot, bei dem sowohl `bezeichnung` als auch `preis_brutto` `null` sind, gilt als
nicht gefunden und erscheint als `"Nicht gefunden"` in der Tabelle sowie in der
Nicht-gefunden-Zählung. Bekannte Händlerfarben (Conrad Gold, Reichelt Blau, Alternate
Orange, AZ Delivery Grün, Berrybase Lila, Voelkner Rot) sind im Skript hinterlegt;
unbekannte Händlernamen erhalten automatisch eine Fallback-Farbe.

Referenz-Config mit vollständigem Beispiel:
[`scripts/example_config.json`](scripts/example_config.json).

---

## Schritt 5: Rückmeldung

Pfad der erzeugten Datei im Chat mitteilen. Anschließend kurz zusammenfassen (aus der
Skript-Ausgabe von Schritt 4):
- Wie viele Artikel wurden recherchiert
- Bei welchen Händlern
- Wie viele Artikel nicht gefunden wurden (falls zutreffend) — bei weniger als 3
  Angeboten für einen Artikel den Nutzer aktiv darauf hinweisen und weitere Händler
  vorschlagen

---

## Fehlerbehandlung

| Problem | Lösung |
|---|---|
| Händler-Seite nicht erreichbar | Anderen Händler verwenden |
| Preis nicht eindeutig | Günstigsten Einzelpreis nehmen, im Kommentar vermerken |
| Artikel nicht gefunden | "Nicht gefunden" eintragen, anderen Suchbegriff versuchen |
| Weniger als 3 Angebote | Nutzer informieren und weitere Händler vorschlagen |
| Datei leer / nicht lesbar | Nutzer um erneutes Hochladen bitten |
