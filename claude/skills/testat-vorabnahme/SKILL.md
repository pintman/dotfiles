---
name: testat-vorabnahme
description: >
  Erstellt zu einer konkreten Testatkarte einen maßgeschneiderten Meta-Prompt
  (Markdown-Datei), mit dem Lernende in einem beliebigen KI-Chat (Claude, ChatGPT o. ä.
  über die Webseite) selbst prüfen können, ob sie bereit für die Testat-Abnahme durch den
  Fachlehrer sind. Der Prompt enthält die Meilensteine der Karte bereits wörtlich
  eingebettet und simuliert eine echte Testat-Abnahme inkl. Verständnisfragen und bewusst
  eingebautem kleinem Fehler, den der Schüler selbst finden und korrigieren muss. Nutze
  diesen Skill, wenn der Nutzer einen Selbstcheck, eine Vorabnahme, eine Übungs-Abnahme
  oder ein Werkzeug für Schüler zur Vorbereitung auf ein Testat erstellen möchte — auch
  wenn das Wort "Skill" nicht fällt. Trigger auch bei Formulierungen wie "Erstell mir
  einen Selbstcheck fürs Testat", "Ich brauche etwas, mit dem Schüler selbst prüfen
  können, ob sie testat-reif sind", "Mach einen Prompt für eine Testat-Vorabnahme".
  Benötigt als Input eine bestehende Testatkarte (Config oder Markdown des Skills
  `testatkarte`) — ohne diese kann kein spezifischer Prompt erzeugt werden. Ausgabe: eine
  .md-Datei mit dem fertigen, kopierbaren Meta-Prompt für genau diese eine Testatkarte.
---

# Testat-Vorabnahme – Skill

## Ausgangslage

Der Skill `testatkarte` erzeugt Testatkarten: Arbeitsblätter mit nummerierten
Meilensteinen, die ein Fachlehrer erst abzeichnet, wenn der Schüler sie im Gespräch
nachweisen kann — inklusive eines bewusst eingebauten kleinen Fehlers, den der Schüler
live korrigieren muss.

Viele Schüler gehen zur echten Abnahme, obwohl sie den Meilenstein noch nicht sicher
beherrschen. `testat-vorabnahme` erzeugt dafür einen zu **genau einer Testatkarte**
passenden **Meta-Prompt** (Markdown-Text), den Schüler als erste Nachricht in einen
beliebigen KI-Chat einfügen. Die KI übernimmt danach die Rolle des prüfenden
Fachlehrers und simuliert die Abnahme, bevor der Schüler zum echten Testat antritt.

Dieser Skill ist **nicht eigenständig nutzbar** — er setzt eine bereits existierende
Testatkarte voraus (Config im Schema von `testatkarte` oder deren Markdown-Zwischenstand,
siehe `testatkarte/SKILL.md` Schritt 4). Die Meilensteine der Karte werden wörtlich in
den generierten Prompt übernommen; der Schüler muss sie nicht mehr abtippen, sondern
nennt zu Beginn nur noch seine Meilenstein-Nummer.

Wichtig: Schüler haben in der Regel **keinen** Zugriff auf Claude Code oder Skills,
sondern nutzen ein KI-System über die Webseite (Claude, ChatGPT o. ä.), ohne Datei- oder
Code-Ausführungszugriff. Der Meta-Prompt muss deshalb komplett textbasiert funktionieren:
der Schüler wählt seine Meilenstein-Nummer und fügt seinen Code/seine Erklärung als Text
ein, alles Weitere läuft als reiner Chat-Dialog.

Der generierte Prompt gilt **nur für die Testatkarte, aus der er erzeugt wurde**. Bei
einer neuen Testatkarte (neues Thema, neue Meilensteine) muss der Skill erneut
durchlaufen werden.

---

## Voraussetzungen für "testat-reif" (Bewertungsrubrik)

Der Meta-Prompt muss die KI anweisen, erst dann grünes Licht zu geben, wenn **alle**
zutreffenden Kriterien erfüllt sind:

1. **Ergebnis korrekt & vollständig** — das beschriebene/eingefügte Ergebnis (Code oder
   theoretische Ausarbeitung) erfüllt die Anforderung des gewählten Meilensteins
   vollständig, nicht nur oberflächlich.
2. **Verständnis, kein Copy-Paste** — der Schüler kann sein Vorgehen in eigenen Worten
   erklären (mind. 1–2 gezielte Verständnisfragen zum Meilenstein, nicht nur Syntax).
3. **Fehlerkorrektur unter Live-Bedingungen** — die KI baut genau einen realistischen,
   kleinen Fehler (Syntax/Logik, bei theoretischen Meilensteinen eine falsche
   Teilaussage) in das Eingereichte ein, ohne ihn zu verraten. Der Schüler muss ihn
   selbst finden und korrigieren. Gelingt das erst nach einem Tipp, gilt das als
   "bereit mit Einschränkung", nicht als voll bereit.
4. **Bei theoretischen Meilensteinen**: Kernbegriffe müssen an einem selbst gewählten
   Beispiel erklärt werden können (entspricht Kriterium 2, aber explizit für
   nicht-Code-Meilensteine).
5. **Quellenangabe** — der Schüler nennt, welche Informationsquellen er für die
   Bearbeitung des Meilensteins genutzt hat. Sind auf der Testatkarte selbst Quellen
   angegeben (Zusatzinfos-Seiten), sind diese im Prompt hinterlegt und gelten als
   naheliegende, aber nicht zwingende Antwort; zusätzlich sind Links auf Internetseiten
   zulässig. Ein Chat mit einer KI wie ChatGPT oder Claude gilt **nicht** als
   ausreichende Quelle — nennt der Schüler nur das, muss nach einer zusätzlichen
   Quelle gefragt werden.

Nur wenn 1–3 und 5 (praktische Meilensteine) bzw. 1, 2, 4 und 5 (theoretische
Meilensteine) erfüllt sind, vergibt die KI die Ampel "bereit fürs Testat". Andernfalls
konkrete, stichpunktartige Rückmeldung, was noch fehlt.

---

## Schritt-für-Schritt-Anleitung

### Schritt 1: Testatkarten-Daten beschaffen

Ohne die konkrete Testatkarte kann kein Prompt erzeugt werden. Vorgehen:

- **Direkt im Anschluss an `testatkarte`**: Die Config (JSON nach dem Schema aus
  `testatkarte/SKILL.md`) bzw. das in dessen Schritt 4 erzeugte Markdown liegt bereits
  im aktuellen Kontext vor — direkt weiterverwenden, nicht erneut erfragen.
- **Eigenständiger Aufruf**: Nach dem Pfad zur Testatkarten-Config (JSON) oder
  ersatzweise zur Markdown-/Word-Fassung der Karte fragen und einlesen.

Aus den Daten extrahieren:
- `thema`, `klasse` (für Titel/Kontext des Prompts)
- alle Meilensteine (`nr` + `text`), wörtlich
- aus `zusatzinfos`, soweit vorhanden: Quellenangaben, die einzelnen Meilensteinen
  zuordenbar sind (best effort — sonst als allgemeine Quellenliste übernehmen)

### Schritt 2: Meta-Prompt per Skript erzeugen

Das Template (fester Text, Platzhalter-Befüllung) ist themenunabhängig und liegt fest im
Skript — dafür kein manuelles Abschreiben/Befüllen mehr, sondern:

```bash
python3 scripts/generate.py \
  --fach "<Fachrichtung/Bildungsgang>" \
  --thema "<Thema aus der Karte>" \
  --meilensteine "<nummerierte Liste aller Meilensteine, wörtlich aus der Karte>" \
  --quellen-hinweis "<auf der Karte angegebene Quellen, falls vorhanden>" \
  --out "<Zielordner>/Testat-Vorabnahme-Selbstcheck_<Thema>.md"
```

- `--fach`: aus `klasse` ableiten oder kurz erfragen, falls nicht eindeutig
- `--thema`: wörtlich `thema` aus der Karte
- `--meilensteine`: **alle** Meilensteine der Karte als nummerierte Liste, Text wörtlich
  aus der Config/dem Markdown übernommen (mehrzeiliger String)
- `--quellen-hinweis`: optional; weglassen, wenn die Karte keine zuordenbaren Quellen
  angibt — das Skript entfernt den Platzhalter dann sauber
- `--out`: Zielpfad **im selben Ordner wie die zugehörige Testatkarte** (nicht
  scratchpad/tmp), Dateiname mit Themabezug. Ohne `--out` legt das Skript die Datei im
  aktuellen Verzeichnis unter `Testat-Vorabnahme-Selbstcheck_<thema-slug>.md` an — bei
  Unklarheit über den Speicherort vorher kurz nachfragen.

Das Skript bricht mit Fehlermeldung ab, falls die Zieldatei bereits existiert oder nach
der Befüllung noch unaufgelöste Platzhalter übrig sind. Ausgabe ist immer reines
Markdown (kein docx) — der Text soll 1:1 per Copy-Paste in einen Chat eingefügt werden.

### Schritt 3: Rückmeldung geben

Kurze Vorschau des Prompts im Chat zeigen und den Benutzer daran erinnern, wie er ihn an
Schüler weitergibt: als erste Nachricht in einem neuen Chat einfügen lassen, oder als
Custom/Project Instructions in einem KI-Tool hinterlegen. Deutlich machen: Dieser Prompt
gehört zu **dieser einen Testatkarte** — bei einer neuen Karte muss der Skill erneut
laufen.

---

## Meta-Prompt-Template

Der vollständige Text des Meta-Prompts (Rolle, Ablauf, Bewertungskriterien,
Abschluss-Protokoll) ist in [`scripts/generate.py`](scripts/generate.py) hinterlegt —
dort ist er die einzige Quelle der Wahrheit. Inhaltliche Änderungen am Template (nicht
nur an Fach/Thema/Meilensteinen) direkt im Skript vornehmen, nicht hier im SKILL.md
duplizieren.

---

## Qualitätsprüfung

Vor der Ausgabe prüfen:
- [ ] `--meilensteine` enthält alle Meilensteine der Testatkarte wörtlich und
      vollständig (keine Auslassungen, keine Umformulierung)
- [ ] Skript ist ohne Fehler durchgelaufen (kein Abbruch wegen bestehender Zieldatei
      oder unaufgelöster Platzhalter — das Skript prüft Platzhalter automatisch)
- [ ] Ausgabe ist eine `.md`-Datei, kein docx
- [ ] Dateiname und Speicherort (`--out`) lassen erkennen, zu welcher Testatkarte der
      Prompt gehört, und liegen im selben Ordner wie die Testatkarte
