---
name: teach-web
description: >
  Erzeugt ein portables Starter-Kit (vier separate Dateien in einem Ordner) für einen
  geführten Fernlern-Workspace über die normale Claude.ai-Weboberfläche (Projects,
  Knowledge, Artifacts) — ganz ohne Claude-Code-Subscription. Gedacht für den
  Bildungsbereich: Schüler und Auszubildende richten sich damit selbst einen geführten
  Fernlern-Workspace zu einem Thema ein, mit Mission, Lernprotokollen und
  HTML-Lektionen als Artifacts, ganz ohne Dateisystemzugriff. Berücksichtigt, dass
  Claude.ai-Accounts laut Anthropics Nutzungsbedingungen erst ab 18 Jahren zulässig
  sind — minderjährige Lernende tun sich dafür mit einer volljährigen Person zusammen
  und lernen als Team. Nutze diesen Skill, wenn der Nutzer ein geführtes Lernsetting
  "im Web", "über die Weboberfläche", "für Schüler ohne Claude Code" oder "für Schüler
  ohne Subscription" verfügbar machen möchte, oder ein Selbstlern-/Fernlern-Kit für ein
  bestimmtes Thema für Azubis/Schüler erstellen will — auch ohne das Wort "Skill".
  Ausgabe: vier Dateien in einem Ordner (Custom-Instructions-Kurzanleitung, vollständige
  Rollen-/Philosophie-Datei, leerer Startzustand samt Stylesheet, Einrichtungs-Anleitung
  für Schüler) — jede Datei bereits unter dem Namen, den Claude.ai später erwartet.
disable-model-invocation: true
argument-hint: "Thema/Mission + Zielgruppe, z. B. 'Netzwerktechnik-Grundlagen, Azubis 1. Lehrjahr Fachinformatiker'"
---

# Teach-Web – Skill

## Ausgangslage

Ein geführtes Fernlern-Setting braucht normalerweise ein Arbeitsverzeichnis, das autonom
gelesen und beschrieben wird: Mission, Ressourcenliste, Lernprotokolle, HTML-Lektionen,
Assets. Das setzt Claude Code (oder eine vergleichbare Coding-Umgebung mit Datei-/
Bash-Zugriff) voraus.

Viele Schüler und Auszubildende haben das nicht — sie nutzen KI ausschließlich über die
Weboberfläche. `teach-web` überträgt diese Philosophie so, dass sie in einem normalen
Claude.ai-Project funktioniert:

- Statt eines Verzeichnisses gibt es **eine einzige Zustandsdatei** (`ZUSTAND.md`), die
  der/die Lernende in die Project-Knowledge hochlädt und nach jeder Sitzung durch eine
  aktualisierte Fassung ersetzt (Claude kann in einer Web-Session keine Dateien
  autonom schreiben, nur Artifacts zum Download erzeugen).
- Statt `./lessons/*.html` + `./assets/*` ist **jede Lektion ein eigenständiges
  Artifact** mit komplett inline eingebettetem Stylesheet (kein Verzeichnis zum
  gemeinsamen Verlinken vorhanden).
- Statt aktiver Fremd-Community-Empfehlungen (Foren, Subreddits) verweist die
  Weisheits-Säule zurückhaltender auf bereits vorhandene, beaufsichtigte Strukturen —
  angemessen für eine teils minderjährige Zielgruppe.
- Claude.ai-Accounts sind laut Anthropics Consumer-Nutzungsbedingungen erst ab 18
  zulässig. Minderjährige Lernende bilden deshalb ein Team mit einer volljährigen
  Person (Mitauszubildende:r, Familienmitglied), die den Account hält; der Fortschritt
  wird dann fürs Team gemeinsam geführt, nicht individuell getrennt.
- Custom Instructions in Claude Projects sind praktisch auf ca. 8.000 Zeichen begrenzt.
  Die volle Rollen-/Philosophie-Beschreibung ist daher **keine** Custom Instruction,
  sondern eine hochgeladene Knowledge-Datei (`ANLEITUNG.md`, kein Zeichenlimit); das
  Custom-Instructions-Feld enthält nur einen kurzen, robusten Verweis darauf.
- Das Kit selbst wird als **vier separate Dateien** erzeugt, nicht als eine Datei zum
  manuellen Aufteilen — jede Datei trägt bereits den Namen, unter dem sie später in
  Claude.ai landet (`ANLEITUNG.md`, `ZUSTAND.md`). Das spart Schülern und Azubis den
  Copy-Paste-Split-Schritt komplett.

## Schritt-für-Schritt-Anleitung

### Schritt 1: Kontext klären

Falls nicht schon angegeben, kurz erfragen:

- **Thema/Mission-Stichpunkt** (z. B. "Netzwerktechnik-Grundlagen", "Python-Basics").
  Ohne Thema kein sinnvoller Rollen-Text — hier nachfragen, nicht raten.
- **Zielgruppe** (Alter, Ausbildungsjahr/Schulform). Falls nichts Genaueres angegeben
  wird: Standardannahme "gemischt 16–19, Azubis und Schüler, Berufsschulkontext"
  verwenden, ohne extra nachzufragen.

Das Kit ist bewusst **wiederverwendbar für die ganze Klasse/Gruppe zu diesem einen
Thema** — jedes Team/jede Einzelperson erhält denselben Ordner und pflegt danach im
eigenen Project einen eigenen `ZUSTAND.md`-Stand. Keine Einzelanfertigung pro Person
nötig.

### Schritt 2: Kit per Skript erzeugen

Die vier Templates (Platzhalter-Befüllung, Ordnerstruktur, Dateinamen) sind fest und
themenunabhängig — dafür kein manuelles Abschreiben/Befüllen mehr, sondern:

```bash
python3 scripts/generate_kit.py --thema "<Thema>" --zielgruppe "<Zielgruppe>"
```

- `--zielgruppe` ist optional; ohne Angabe wird die Standardannahme aus Schritt 1
  verwendet (`gemischt 16–19, Azubis und Schüler, Berufsschulkontext`).
- `--out <pfad>` überschreibt optional den Zielordner (Standard:
  `Teach-Web-Kit_<thema-slug>/` im aktuellen Arbeitsverzeichnis, Slug automatisch aus
  `--thema` abgeleitet). Bei Unklarheit über den Speicherort vorher kurz nachfragen.

Das Skript legt den Ordner an und schreibt **vier einzelne Dateien** hinein (bricht mit
Fehlermeldung ab, falls der Zielordner bereits existiert und nicht leer ist):

- `custom-instructions.md`
- `ANLEITUNG.md`
- `ZUSTAND.md`
- `EINRICHTUNG.md`

Die Namen `ANLEITUNG.md` und `ZUSTAND.md` sind absichtlich exakt die Namen, die auch in
der Project-Knowledge verwendet werden — dadurch entfällt beim Einrichten jedes
Umbenennen oder Aufteilen. Der restliche Template-Inhalt (Philosophie, Mission-Interview,
ZPD, Lernprotokolle, Stylesheet-Pflege) ist im Skript fest hinterlegt und bewusst
themenunabhängig formuliert.

### Schritt 3: Rückmeldung geben

Kurz auflisten, welche vier Dateien im Ordner liegen, und erklären, wie sie
weitergegeben werden: den ganzen Ordner an Schüler/Azubis aushändigen (Teams, Moodle,
Zip), mit dem Hinweis, `EINRICHTUNG.md` zuerst zu lesen. Daran erinnern, dass das Kit
pro Thema einmalig generiert wird, nicht pro Schüler.

## Template-Inhalte

Der vollständige Text aller vier Dateien (Rolle/Philosophie, Mission-Interview, ZPD,
Lernprotokoll-Regeln, Stylesheet, Einrichtungs-Anleitung für beide Altersfälle) ist in
[`scripts/generate_kit.py`](scripts/generate_kit.py) hinterlegt — dort ist er die
einzige Quelle der Wahrheit. Inhaltliche Änderungen an den Templates (nicht nur an
Thema/Zielgruppe) direkt im Skript vornehmen, nicht hier im SKILL.md duplizieren.

## Qualitätsprüfung

Vor der Ausgabe prüfen:
- [ ] `--thema` wurde übergeben und taucht in `EINRICHTUNG.md`/`ZUSTAND.md` korrekt
      auf, keine `[THEMA]`-Platzhalter mehr übrig (Skript ersetzt automatisch)
- [ ] Zielordner enthält wirklich **vier separate Dateien**: `custom-instructions.md`,
      `ANLEITUNG.md`, `ZUSTAND.md`, `EINRICHTUNG.md`
- [ ] Skript ist ohne Fehler durchgelaufen (kein Abbruch wegen nicht-leerem
      Zielordner)
- [ ] Alle vier Dateien sind reines Markdown (kein docx) und einzeln lesbar/hochladbar
