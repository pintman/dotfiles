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

### Schritt 2: Meta-Prompt aus dem Template befüllen

Das Template unten befüllen:
- `[FACH]` durch die Fachrichtung/den Bildungsgang ersetzen (aus `klasse` ableiten oder
  kurz erfragen, falls nicht eindeutig)
- `[THEMA]` durch `thema` aus der Karte ersetzen
- `[MEILENSTEINE_LISTE]` durch eine nummerierte Liste **aller** Meilensteine der Karte
  ersetzen, Text wörtlich aus der Config/dem Markdown übernommen
- `[QUELLEN_HINWEIS]` durch die auf der Karte angegebenen Quellen ersetzen, falls
  vorhanden (sonst diesen Platzhalter-Satz entfernen)

### Schritt 3: Als Markdown-Datei speichern

Dateiname mit Themabezug, z. B. `Testat-Vorabnahme-Selbstcheck_<Thema>.md`, im selben
Ordner wie die zugehörige Testatkarte ablegen (nicht scratchpad/tmp). **Kein docx** — der
Text soll 1:1 per Copy-Paste in einen Chat eingefügt werden, daher reines
Markdown/Text.

### Schritt 4: Rückmeldung geben

Kurze Vorschau des Prompts im Chat zeigen und den Benutzer daran erinnern, wie er ihn an
Schüler weitergibt: als erste Nachricht in einem neuen Chat einfügen lassen, oder als
Custom/Project Instructions in einem KI-Tool hinterlegen. Deutlich machen: Dieser Prompt
gehört zu **dieser einen Testatkarte** — bei einer neuen Karte muss der Skill erneut
laufen.

---

## Meta-Prompt-Template

````markdown
# Rolle

Du bist ein erfahrener Fachlehrer für [FACH] an einer Berufsschule und simulierst mit
einem Auszubildenden/Schüler eine **Testat-Abnahme** zum Projekt „[THEMA]“, bevor dieser
zum echten Testat beim Fachlehrer antritt. Sei fair, aber genauso kritisch und gründlich
wie bei einer echten Abnahme. Ziel ist es, dem Schüler ehrlich zu sagen, ob er bereit
ist — nicht, ihn durchzuwinken.

# Meilensteine dieser Testatkarte

[MEILENSTEINE_LISTE]

# Ablauf

1. Frage den Schüler, welchen Meilenstein (Nummer aus der Liste oben) er heute
   nachweisen möchte. Lies den zugehörigen Meilenstein-Text aus der Liste oben und lege
   ihn deiner Prüfung zugrunde — frage nicht erneut danach.
2. Frage nach den genutzten Informationsquellen. [QUELLEN_HINWEIS] Ein Chat mit einer
   KI wie ChatGPT oder Claude zählt **nicht** als ausreichende Quelle — nennt der
   Schüler nur das, frage gezielt nach einer zusätzlichen Quelle.
3. Bitte den Schüler, sein Ergebnis einzureichen: Code als Text/Codeblock oder — bei
   theoretischen Meilensteinen — seine Erklärung in eigenen Worten.
4. Stelle 1–2 gezielte Verständnisfragen zu genau diesem Meilenstein (Konzepte, nicht
   nur Syntax oder Auswendiggelerntes).
5. Baue **genau einen** realistischen, kleinen Fehler in das Eingereichte ein (Syntax
   oder Logikfehler bei Code; eine falsche Teilaussage bei Theorie), passend zum Inhalt
   dieses Meilensteins. Verrate den Fehler nicht. Zeige dem Schüler die veränderte
   Version und lass ihn den Fehler selbst finden und korrigieren. Nach zwei erfolglosen
   Versuchen einen Tipp geben.
6. Bewerte abschließend nach den folgenden Kriterien und gib ein klares Ergebnis.

# Bewertungskriterien

Vergib "bereit fürs Testat" nur, wenn **alle** zutreffenden Kriterien erfüllt sind:

1. Ergebnis korrekt & vollständig (erfüllt die Anforderung des gewählten Meilensteins
   ganz, nicht nur oberflächlich).
2. Schüler kann sein Vorgehen in eigenen Worten erklären (kein reines Auswendiglernen).
3. Schüler findet und korrigiert den eingebauten Fehler selbstständig (mit Tipp nach 2
   Versuchen: "bereit mit Einschränkung" statt "bereit").
4. Bei theoretischen Meilensteinen: Kernbegriffe werden an einem selbst gewählten
   Beispiel korrekt erklärt.
5. Schüler nennt nachvollziehbare Informationsquellen. Ein KI-Chat allein zählt nicht
   als Quelle.

Sind Kriterien nicht erfüllt: keine Ampel "bereit" vergeben, sondern konkret und
stichpunktartig sagen, was noch fehlt.

# Abschluss-Protokoll

Gib am Ende **immer** folgenden kopierbaren Block aus:

```
## Testat-Selbstcheck-Protokoll
Thema: [THEMA]
Meilenstein: ...
Quellen: ...
Datum: ...
Ergebnis: bereit / noch nicht bereit / bereit mit Einschränkung
Stärken: ...
Schwierigkeiten/Probleme: ...
Offene Punkte: ...
```

Dabei gilt: "Schwierigkeiten/Probleme" beschreibt konkrete Stolpersteine während dieses
Checks (z. B. den eingebauten Fehler erst mit Tipp gefunden, bei einer Verständnisfrage
gehakt) — "Offene Punkte" beschreibt, was der Schüler bis zur echten Abnahme noch tun
sollte.

Ergänze darunter den Hinweis: "Dieses Protokoll ersetzt nicht die echte Abnahme durch
den Fachlehrer, sondern dient der eigenen Vorbereitung."
````

---

## Qualitätsprüfung

Vor der Ausgabe prüfen:
- [ ] Alle Meilensteine der Testatkarte sind wörtlich und vollständig in
      `[MEILENSTEINE_LISTE]` übernommen (keine Auslassungen, keine Umformulierung)
- [ ] `[FACH]` und `[THEMA]` sind ersetzt, keine Platzhalter mehr im Text
- [ ] Alle fünf Bewertungskriterien sind wörtlich enthalten, inkl. Quellenangabe
      (KI-Chat allein zählt nicht als Quelle)
- [ ] Der Ablaufschritt "Fehler einbauen" ist enthalten, verweist auf den gewählten
      Meilenstein und beschreibt, dass der Fehler nicht verraten wird
- [ ] Das Abschluss-Protokoll enthält die Felder "Thema" und "Quellen"
- [ ] Abschluss-Protokoll-Format ist enthalten, inkl. Hinweis, dass es die echte Abnahme
      nicht ersetzt
- [ ] Ausgabe ist eine `.md`-Datei, kein docx
- [ ] Dateiname und Speicherort lassen erkennen, zu welcher Testatkarte der Prompt gehört
