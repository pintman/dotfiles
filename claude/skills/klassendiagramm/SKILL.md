---
name: klassendiagramm
description: >
  Erstellt UML-Klassendiagramme mit PlantUML, gerendert über den öffentlichen
  PlantUML-Server (www.plantuml.com) - ohne lokale Installation von PlantUML,
  Java oder Graphviz. Unterstützt zwei Eingabequellen: (a) Reverse-Engineering
  aus bestehendem Python-Quellcode via ast-Modul, (b) Freitext-Beschreibung
  einer Klassenstruktur. Diagramme orientieren sich bewusst nah am UML-Standard
  (Sichtbarkeit +/-/#, {static}/{abstract}, Vererbung vs. Interface-Realisierung,
  Multiplizität, Enums) statt am PlantUML-Hausstil.
  Nutze diesen Skill, wenn der Nutzer ein Klassendiagramm, UML-Diagramm,
  Strukturdiagramm zu Python-Code erstellen möchte, oder Formulierungen wie
  "erstell ein Klassendiagramm für...", "visualisiere die Klassenstruktur von...",
  "mach mir ein UML-Diagramm zu..." verwendet.
---

# Klassendiagramm-Skill

Erstellt UML-Klassendiagramme via [PlantUML](https://plantuml.com), gerendert über
den öffentlichen Server `https://www.plantuml.com/plantuml`. Kein lokales PlantUML,
kein Java, kein Graphviz, kein pip-Install nötig - alle Skripte nutzen ausschließlich
die Python-Standardbibliothek.

## Zwei Eingabemodi

### Modus A: Aus Python-Quellcode

Wenn der Nutzer ein Diagramm zu **bestehendem Code** möchte:

1. Kläre, welche `.py`-Dateien einbezogen werden sollen (keine automatische
   rekursive Verzeichniserfassung, keine Import-Auflösung - siehe
   "Umfang der Code-Analyse" unten). Bei offensichtlichem Kontext
   (z. B. "für dieses Modul") die naheliegenden Dateien direkt verwenden,
   sonst kurz nachfragen.
2. Extraktion ausführen:
   ```bash
   python3 scripts/extract_classes.py datei1.py datei2.py -o ziel.puml
   ```
   Das Skript nutzt `ast`, um pro Klasse Sichtbarkeit, Attribute (aus
   Typannotationen und typisierten Konstruktor-Parametern), Methoden,
   Vererbung, Interfaces (`ABC`/`Protocol`), Enums und einfache Assoziationen
   zu extrahieren. Details siehe Abschnitt "Was der Extraktor erkennt".
3. Weiter mit "Rendern" unten.

### Modus B: Aus Freitext-Beschreibung

Wenn der Nutzer die Struktur **beschreibt statt Code zu liefern**:

1. Erarbeite im Gespräch die Klassen, Attribute, Methoden und Beziehungen.
   Bei Unklarheiten (fehlende Typen, unklare Beziehungsrichtung) nachfragen
   statt zu raten.
2. Schreibe den `.puml`-Quelltext **von Hand**, aber nach denselben Regeln
   wie der Extraktor (siehe "Was der Extraktor erkennt" - insb. Sichtbarkeit,
   `{abstract}`/`{static}`, `..|>` für Interface-Realisierung vs. `--|>` für
   Vererbung, `"*"` für Mehrfachbeziehungen).
3. Kopfzeilen aus [`scripts/skinparams.puml`](scripts/skinparams.puml) direkt
   nach `@startuml` einfügen, damit das Ergebnis optisch identisch zu
   Modus A ist.
4. Weiter mit "Rendern" unten.

## Rendern (beide Modi)

```bash
python3 scripts/render.py ziel.puml -o ausgabeordner/diagrammname
```

Erzeugt `diagrammname.svg` und `diagrammname.png` per Aufruf des öffentlichen
PlantUML-Servers (Basis-URL ist `PLANTUML_SERVER` in `render.py` - dort
austauschbar, falls später ein selbstgehosteter Server verwendet werden soll).

**Encoding**: PlantUML-Quelltext wird mit dem PlantUML-eigenen Deflate+Base64-
Verfahren kodiert (in `render.py` selbst implementiert, nur `zlib`, kein
externes Paket).

**Fehlerbehandlung**:
- Der Server antwortet bei **Syntaxfehlern im `.puml`** mit HTTP 400 und einem
  Fehlerbild. `render.py` speichert dieses Fehlerbild als
  `<name>.error.<format>`, bricht mit Exitcode 2 ab und meldet, dass der
  `.puml`-Text geprüft werden muss - kein Retry, da es kein Netzwerkproblem ist.
- Bei **Netzwerkproblemen/Timeouts** wird einmal automatisch erneut versucht
  (kurze Pause), danach Abbruch mit Exitcode 1 und klarer Meldung. Der
  `.puml`-Quelltext bleibt in jedem Fall als Datei erhalten.
- Kein Fallback auf alternative/Mirror-Server - nur der offizielle
  PlantUML-Server wird angesprochen.

## Was der Extraktor erkennt (Modus A) bzw. worauf Modus B sich ausrichtet

| UML-Element | Herkunft/Regel |
|---|---|
| Sichtbarkeit | `_x` → `#` (protected), `__x` → `-` (private), sonst `+` (public) |
| `{static}` | `@staticmethod`/`@classmethod` |
| `{abstract}` | `@abstractmethod`; Klasse wird `abstract class`, wenn sie mind. eine abstrakte Methode hat, aber keine reine Schnittstelle ist |
| Interface | `class X(Protocol)` oder `class X(ABC)` mit ausschließlich abstrakten Methoden → `interface`-Block statt `class` |
| Vererbung | `class B(A)` → `B --|> A` (durchgezogen) |
| Interface-Realisierung | Basisklasse ist ein erkanntes Interface → `..|>` (gestrichelt) statt `--|>` |
| Enum | `class X(Enum)` (auch `IntEnum`/`StrEnum`/`Flag`/`IntFlag`) → `enum`-Block mit den Werten als Einträgen |
| Attributtypen | Aus Klassenebene-Annotationen, `self.x: T = ...` im Konstruktor, oder `self.x = param`, wobei `param` ein typisierter Konstruktor-Parameter ist (strukturell abgeleitet, nicht geraten) |
| Assoziationen | Attributtyp verweist auf eine andere im selben Lauf erfasste Klasse → `Owner --> Ziel : attributname`. **Nur einfache Assoziation** - keine Heuristik für Aggregation/Komposition |
| Multiplizität | `List[X]`/`list[X]`/`Set[X]`/`Sequence[X]` etc. mit `X` als bekannter Klasse → `"*"` an der Zielseite |
| Rückgabetyp `None` | wird als `void` dargestellt (UML-Konvention statt Pythons `None`) |

Basisklassen, die nicht unter den übergebenen Dateien sind, werden nicht als
Box gezeichnet (keine Import-Auflösung, siehe unten) - `ABC`/`Protocol`/
`Enum`-Familie werden als reine Marker ohnehin nie als eigene Klasse gezeichnet.

## Umfang der Code-Analyse

Es wird **keine** automatische rekursive Verzeichniserfassung und **keine**
Python-Import-Auflösung vorgenommen. Stattdessen: Der Nutzer (oder ich im
Gespräch) legt die Liste der einzubeziehenden `.py`-Dateien fest. Klassen
werden über alle übergebenen Dateien hinweg per **Namensabgleich** verknüpft
(keine `sys.path`-/Package-Mechanik). Das deckt die meisten Ad-hoc-Anfragen ab,
ohne sich in relativen Importen, `__init__.py`-Reexports oder dynamischen
Importen zu verheddern.

## Visueller Stil

Alle Diagramme nutzen feste Skinparams ([`scripts/skinparams.puml`](scripts/skinparams.puml)),
um näher an klassischer UML-Notation zu sein als PlantUMLs Hausstil:
keine Attribut-/Klassen-Icons (`classAttributeIconSize 0`, `hide circle`),
monochrom, rechteckige Boxen ohne Schatten. Bei Modus B diese Datei immer
mit einbeziehen, nicht neu erfinden.

## Speicherort und Benennung

- `.puml`, `.svg`, `.png` bekommen denselben Dateinamen-Stamm, nur die Endung
  unterscheidet sich.
- Sprechender Name aus dem Kontext ableiten: bei Code-Analyse der Modul-/
  Package-Name, bei Freitext ein Begriff aus dem Thema.
- Ablage im aktuellen Arbeitsverzeichnis bzw. kontextnah (z. B. neben dem
  analysierten Code). Ist der Zielort nicht klar (insbesondere bei Modus B
  ohne bestehenden Code-Kontext), kurz nachfragen. Nicht im scratchpad-/
  tmp-Ordner ablegen.
- Bei Namenskollision mit vorhandenen Dateien nachfragen (überschreiben oder
  anderer Name), nicht automatisch einen Zeitstempel anhängen.

## Abgrenzung zu `testatkarte`

Der Skill `testatkarte` hat einen eigenen `classdiagram`-Block-Typ für
Arbeitsblätter - das ist eine einfache **Tabellendarstellung** (Attribute/
Methoden als Text), kein echtes UML mit Pfeilen/Notation. Dieser Skill hier
ist unabhängig davon und ersetzt ihn nicht.
