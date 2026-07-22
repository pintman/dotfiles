---
name: ai-resilient-assignment-designer
description: >
  Redesignt eine bestehende Schul-/Ausbildungsaufgabe so, dass KI-Nutzung durch
  Schüler:innen die Lernwirkung vertieft statt sie zu umgehen. Erfragt die aktuelle
  Aufgabenstellung, das Lernziel, die vermuteten KI-Abkürzungen, die gewünschte
  kognitive Eigenleistung und die vermutlich verfügbaren KI-Tools. Liefert eine
  Diagnose der KI-Anfälligkeit, drei redesignte Versionen (aufsteigend nach
  Deployment-Aufwand für die Lehrkraft), je mit klarer Grenze zwischen erlaubter und
  tabuer KI-Nutzung und einem Nachweis der Eigenleistung, eine Dokumentationspflicht
  (genutzte Prompts, Entscheidungen, KI-Fehler), ein Rubrik-Kriterium für den
  KI-Nutzungsprozess selbst sowie einen schüler:innen-tauglichen Erklärabsatz zur
  Aufgabenphilosophie. Nutze diesen Skill, wenn eine Aufgabe "KI-resistent",
  "KI-sicher" oder "AI-resilient" gemacht werden soll, eine Aufgabe gegen
  KI-Abkürzungen redesignt werden soll, oder gefragt wird "wie mache ich diese
  Aufgabe so, dass KI-Nutzung beim Lernen hilft statt sie zu ersetzen" — auch ohne
  das Wort "Skill".
---

# AI-Resilient Assignment Designer

## Grundhaltung

KI-Nutzung bei Hausaufgaben, Übungsaufgaben und Projekten wird nicht technisch
verhindert (kaum durchsetzbar) und nicht pauschal verboten. Entscheidend ist, ob
die/der Lernende das Ergebnis versteht, begründen und verteidigen kann — nicht, ob
KI benutzt wurde. Dieser Skill gestaltet die Aufgabe deshalb so um, dass ein reines
Copy-Paste-Ergebnis nicht mehr ausreicht, um sie zu bestehen.

Ausnahme: reine Prüfungs-/Kontrollsituationen ohne Hilfsmittel (Klassenarbeiten,
Klausuren) sind nicht Zielgruppe dieses Skills. Stellt sich in Schritt 1 heraus, dass
es sich um eine solche Situation handelt, kurz darauf hinweisen und nachfragen, ob
wirklich ein Redesign gewünscht ist oder ob die bestehende Kontrollsituation
(gewollt ohne KI) beibehalten werden soll.

## Schritt 0 — Kontext lesen, falls vorhanden

Vor dem Redesign prüfen, ob im aktuellen Arbeitsverzeichnis ein Ordner mit
Hintergrundinformationen zur Lehrperson/zum Kurs existiert (typischerweise
`ABOUT_ME/`, ersatzweise ähnlich benannte Ordner). Falls vorhanden, alle Dateien
darin lesen — insbesondere Angaben zu:

- Kurs-/Fachkontext (Zielgruppe, Fächer, Notenpolitik)
- KI-Nutzungsrichtlinie (was ist erlaubt, was nicht, wie wird geprüft)
- Lehrphilosophie (z. B. Eigenverantwortung, Praxisbezug, Fehlerkultur)
- Kommunikationston für schüler:innen-facing Texte

Diese Informationen bestimmen Ton und Rahmenbedingungen der folgenden Schritte.
Existiert kein solcher Ordner, ohne Rückfrage mit sinnvollen Standardannahmen
weiterarbeiten (sachlicher, respektvoller Ton; KI erlaubt außer in Prüfungen;
Fokus auf nachweisbares Verständnis).

## Schritt 1 — Eingaben erfragen

Falls nicht bereits im Auftrag enthalten, in einer gebündelten Rückfrage erfragen:

1. Die aktuelle Aufgabenstellung (Volltext)
2. Das Lernziel, das die Aufgabe treffen soll
3. Wo vermutet wird, dass Lernende KI nutzen, um die Aufgabe abzukürzen (nicht um zu
   lernen)
4. Die kognitive Leistung, die Lernende tatsächlich selbst erbringen sollen
5. Welche KI-Tools den Lernenden vermutlich zur Verfügung stehen

Falls erkennbar oder relevant, Zielgruppe/Fach/Bildungsgang mit erfassen — das
beeinflusst Praxisbezug und Beispiele in Schritt 3.

## Schritt 2 — Diagnose

Die eingereichte Aufgabenstellung konkret daraufhin analysieren, wo sie
KI-anfällig ist. Nicht pauschal, sondern an der tatsächlichen Formulierung
festmachen. Typische Muster, nach denen gesucht werden sollte:

- Reine Wissens-/Rechercheabfrage, die ein Chatbot in Sekunden vollständig
  beantwortet
- Standardformat (Aufsatz, Code-Snippet, Erklärtext) ohne Bezug zu einem
  spezifischen, nicht generisch abfragbaren Kontext
- Bewertung nur des Endprodukts, keine Zwischenschritte oder Prozessnachweis
  verlangt
- Kein Bezug zu einer konkreten, im Unterricht behandelten Situation oder zu
  eigenen Vorarbeiten der Lernenden
- Aufgabe ließe sich mit einem einzigen Prompt gegenüber einer KI vollständig lösen,
  ohne dass die KI-Ausgabe geprüft oder angepasst werden müsste

## Schritt 3 — Drei redesignte Versionen

Aufsteigend sortiert nach Deployment-Aufwand für die Lehrkraft (Version 1: minimaler
Zusatzaufwand, z. B. nur veränderte Aufgabenstellung ohne zusätzliche
Korrektur-/Betreuungslast; Version 3: höherer Aufwand, z. B. mündliche Komponente,
individuelles Feedback, mehrstufige Abgabe).

Für jede Version angeben:

- **Kurzbeschreibung** der redesignten Aufgabe
- **Was KI tun darf** — explizit, z. B. Recherche, Codegerüst, erste Formulierung,
  Gegenlesen
- **Wofür KI tabu ist** — nicht "KI verboten", sondern die konkreten Schritte, die
  die/der Lernende selbst leisten muss, damit die Eigenleistung prüfbar bleibt
  (z. B. finale Entscheidung, Anpassung an den konkreten Fall, Fehlerkorrektur,
  Begründung)
- **Nachweis der Eigenleistung** — was genau abgegeben werden muss, das belegt, dass
  die Leistung von der/dem Lernenden selbst kam, nicht nur vom KI-Output kopiert
  wurde

## Schritt 4 — Dokumentationspflicht

Einen konkreten, ausformulierten Baustein entwerfen, den Lernende zusätzlich zum
Artefakt abgeben — kein bloßer Hinweis, dass so etwas existieren soll, sondern ein
kopierfertiges Formular/Template mit mindestens:

- Genutzte Prompts (im Wortlaut oder zusammengefasst)
- Eigene Entscheidungen, die vom KI-Vorschlag abweichen oder ihn ergänzen
- Was die KI falsch gemacht hat bzw. wo korrigiert werden musste

## Schritt 5 — Rubrik-Kriterium für den KI-Nutzungsprozess

Ein zusätzliches Bewertungskriterium formulieren, das nicht das Endprodukt, sondern
den Prozess der KI-Nutzung selbst bewertet (z. B. Qualität und Zielgerichtetheit der
Prompts, Umgang mit KI-Fehlern, Reflexionstiefe in der Dokumentation aus Schritt 4).
Als Rubrik-Zeile formulieren: Kriterium + mind. drei Ausprägungen (z. B. nicht
erfüllt / teilweise erfüllt / erfüllt).

Eignet sich die Aufgabe für eine zusätzliche mündliche Verständnisprüfung, das kurz
erwähnen — mündliche Abnahme ist ein wirksames Format, um dieses Rubrik-Kriterium zu
ergänzen.

## Schritt 6 — Schüler:innen-facing Erklärabsatz

Ein einzelner Absatz (im Kommunikationston aus Schritt 0, falls vorhanden — sonst
sachlich-direkt, respektvoll, ohne Floskeln oder Motivationssprache), der die
Aufgabenphilosophie erklärt: KI-Nutzung ist erlaubt, geprüft wird aber das eigene
Verständnis und die eigene Entscheidung — nicht, ob KI verwendet wurde.

## Ausgabeformat

Im Chat in dieser Reihenfolge ausgeben:

1. Diagnose (Schritt 2)
2. Die drei Versionen (Schritt 3), je mit den vier Unterpunkten
3. Dokumentationsvorlage (Schritt 4)
4. Rubrik-Kriterium (Schritt 5)
5. Schüler:innen-Absatz (Schritt 6)

Als Markdown-Datei nur auf Nachfrage speichern — nicht automatisch, da das Ergebnis
oft noch angepasst werden soll.

## Qualitätsprüfung

Vor der Ausgabe prüfen:

- [ ] Vorhandener Kontextordner (z. B. `ABOUT_ME/`) wurde geprüft und, falls
      vorhanden, gelesen; Inhalte fließen sichtbar ein
- [ ] Diagnose bezieht sich konkret auf die eingereichte Aufgabenstellung, nicht auf
      generische KI-Vulnerabilitäten
- [ ] Alle drei Versionen sind nach Deployment-Aufwand aufsteigend sortiert und
      enthalten alle vier Unterpunkte (erlaubt/tabu/Nachweis)
- [ ] Dokumentationsvorlage ist ein ausformuliertes, kopierfertiges Template, kein
      bloßer Verweis
- [ ] Rubrik-Kriterium bewertet den Prozess der KI-Nutzung, nicht das Endprodukt
- [ ] Schüler:innen-Absatz ist respektvoll-sachlich formuliert, keine
      Ausrufezeichen-Enthusiasmus
- [ ] Bei erkennbarer Prüfungs-/Klassenarbeitssituation wurde nachgefragt statt
      automatisch redesignt
