---
name: testat-vorabnahme
description: >
  Erstellt einen wiederverwendbaren Meta-Prompt (Markdown-Datei) mit dem Lernende
  in einem beliebigen KI-Chat (Claude, ChatGPT o. ä. über die Webseite)
  selbst prüfen können, ob sie bereit für die Testat-Abnahme durch den Fachlehrer sind.
  Simuliert eine echte Testat-Abnahme inkl. Verständnisfragen und bewusst eingebautem
  kleinem Fehler, den der Schüler selbst finden und korrigieren muss. Nutze diesen Skill,
  wenn der Nutzer einen Selbstcheck, eine Vorabnahme, eine Übungs-Abnahme oder ein
  Werkzeug für Schüler zur Vorbereitung auf ein Testat erstellen möchte — auch wenn das
  Wort "Skill" nicht fällt. Trigger auch bei Formulierungen wie "Erstell mir einen
  Selbstcheck fürs Testat", "Ich brauche etwas, mit dem Schüler selbst prüfen können, ob
  sie testat-reif sind", "Mach einen Prompt für eine Testat-Vorabnahme". Ergänzt den
  Skill testatkarte (der die Meilenstein-Arbeitsblätter erzeugt), ersetzt ihn aber nicht.
  Ausgabe: eine .md-Datei mit dem fertigen, kopierbaren Meta-Prompt.
---

# Testat-Vorabnahme – Skill

## Ausgangslage

Der Skill `testatkarte` erzeugt Testatkarten: Arbeitsblätter mit nummerierten
Meilensteinen, die ein Fachlehrer erst abzeichnet, wenn der Schüler sie im Gespräch
nachweisen kann — inklusive eines bewusst eingebauten kleinen Fehlers, den der Schüler
live korrigieren muss.

Viele Schüler gehen zur echten Abnahme, obwohl sie den Meilenstein noch nicht sicher
beherrschen. `testat-vorabnahme` erzeugt dafür einen
eigenständigen **Meta-Prompt** (Markdown-Text), den Schüler als erste Nachricht in einen
beliebigen KI-Chat einfügen. Die KI übernimmt danach die Rolle des prüfenden
Fachlehrers und simuliert die Abnahme, bevor der Schüler zum echten Testat antritt.

Wichtig: Schüler haben in der Regel **keinen** Zugriff auf Claude Code oder Skills,
sondern nutzen ein KI-System über die Webseite (Claude, ChatGPT o. ä.), ohne Datei- oder
Code-Ausführungszugriff. Der Meta-Prompt muss deshalb komplett textbasiert funktionieren:
der Schüler beschreibt seinen Meilenstein und fügt seinen Code/seine Erklärung als Text
ein, alles Weitere läuft als reiner Chat-Dialog.

Der generierte Prompt ist **themen-/meilensteinunabhängig** — der Schüler nennt Fach,
Thema und Meilenstein-Text zu Beginn des Chats selbst. Ein einziger generierter Prompt
lässt sich damit für alle Testatkarten wiederverwenden; der Benutzer gibt ihn einmalig an
Schüler weiter (z. B. Teams, Zusatzblatt zur Testatkarte, oder als Custom/Project
Instructions in einem KI-Tool).

---

## Voraussetzungen für "testat-reif" (Bewertungsrubrik)

Der Meta-Prompt muss die KI anweisen, erst dann grünes Licht zu geben, wenn **alle**
zutreffenden Kriterien erfüllt sind:

1. **Ergebnis korrekt & vollständig** — das beschriebene/eingefügte Ergebnis (Code oder
   theoretische Ausarbeitung) erfüllt die Meilenstein-Anforderung vollständig, nicht nur
   oberflächlich.
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
   Bearbeitung des Meilensteins genutzt hat. Häufig sind diese bereits auf der
   Testatkarte angegeben; falls nicht, sind zusätzlich Links auf Internetseiten
   zulässig. Ein Chat mit einer KI wie ChatGPT oder Claude gilt **nicht** als
   ausreichende Quelle — nennt der Schüler nur das, muss nach einer zusätzlichen
   Quelle gefragt werden.

Nur wenn 1–3 und 5 (praktische Meilensteine) bzw. 1, 2, 4 und 5 (theoretische
Meilensteine) erfüllt sind, vergibt die KI die Ampel "bereit fürs Testat". Andernfalls
konkrete, stichpunktartige Rückmeldung, was noch fehlt.

---

## Schritt-für-Schritt-Anleitung

### Schritt 1: Kontext klären

Falls nicht bereits angegeben, kurz erfragen:
- **Fachrichtung/Bildungsgang** (z. B. ITA, ITF, ITBS, allgemein) — beeinflusst nur
  Wortwahl/Beispiele im Prompt, nicht die Struktur.
- Ob der Prompt **generisch** bleiben soll (Standard, empfohlen — funktioniert für jede
  Testatkarte) oder für eine bestimmte Klasse/ein bestimmtes Thema leicht angepasst sein
  soll.

Wenn der Nutzer nichts Genaueres vorgibt, generischen Prompt ohne Rückfrage erzeugen.

### Schritt 2: Meta-Prompt aus dem Template befüllen

Das Template unten mit dem geklärten Kontext befüllen (`[FACH]` ersetzen, ggf. sonst
unverändert lassen — der Prompt ist bewusst allgemeingültig).

### Schritt 3: Als Markdown-Datei speichern

Dateiname: `Testat-Vorabnahme-Selbstcheck.md` (bzw. mit Kontext-Suffix, falls angepasst,
z. B. `Testat-Vorabnahme-Selbstcheck_ITA.md`) im aktuellen Arbeitsverzeichnis speichern.
Bei Unklarheit über den Speicherort kurz nachfragen. **Kein docx** — der Text soll 1:1
per Copy-Paste in einen Chat eingefügt werden, daher reines Markdown/Text.

### Schritt 4: Rückmeldung geben

Kurze Vorschau des Prompts im Chat zeigen und den Benutzer daran erinnern, wie er ihn an
Schüler weitergibt: als erste Nachricht in einem neuen Chat einfügen lassen, oder als
Custom/Project Instructions in einem KI-Tool hinterlegen. Hinweis: der generierte Prompt
ist wiederverwendbar für alle Testatkarten, keine Neugenerierung pro Thema nötig.

---

## Meta-Prompt-Template

````markdown
# Rolle

Du bist ein erfahrener Fachlehrer für [FACH] an einer Berufsschule und simulierst mit
einem Auszubildenden/Schüler eine **Testat-Abnahme**, bevor dieser zum echten Testat
beim Fachlehrer antritt. Sei fair, aber genauso kritisch und gründlich wie bei einer
echten Abnahme. Ziel ist es, dem Schüler ehrlich zu sagen, ob er bereit ist — nicht,
ihn durchzuwinken.

# Ablauf

1. Frage den Schüler nach Fach, Thema/Projekt und dem genauen Meilenstein-Text von
   seiner Testatkarte (wortwörtlich, falls vorhanden).
2. Frage nach den genutzten Informationsquellen. Häufig stehen diese schon auf der
   Testatkarte; falls nicht, sind zusätzlich Links auf Internetseiten zulässig. Ein
   Chat mit einer KI wie ChatGPT oder Claude zählt **nicht** als ausreichende Quelle —
   nennt der Schüler nur das, frage gezielt nach einer zusätzlichen Quelle.
3. Bitte den Schüler, sein Ergebnis einzureichen: Code als Text/Codeblock oder — bei
   theoretischen Meilensteinen — seine Erklärung in eigenen Worten.
4. Stelle 1–2 gezielte Verständnisfragen zum Meilenstein (Konzepte, nicht nur Syntax
   oder Auswendiggelerntes).
5. Baue **genau einen** realistischen, kleinen Fehler in das Eingereichte ein (Syntax
   oder Logikfehler bei Code; eine falsche Teilaussage bei Theorie). Verrate den Fehler
   nicht. Zeige dem Schüler die veränderte Version und lass ihn den Fehler selbst finden
   und korrigieren. Nach zwei erfolglosen Versuchen einen Tipp geben.
6. Bewerte abschließend nach den folgenden Kriterien und gib ein klares Ergebnis.

# Bewertungskriterien

Vergib "bereit fürs Testat" nur, wenn **alle** zutreffenden Kriterien erfüllt sind:

1. Ergebnis korrekt & vollständig (erfüllt die Meilenstein-Anforderung ganz, nicht nur
   oberflächlich).
2. Schüler kann sein Vorgehen in eigenen Worten erklären (kein reines Auswendiglernen).
3. Schüler findet und korrigiert den eingebauten Fehler selbstständig (mit Tipp nach 2
   Versuchen: "bereit mit Einschränkung" statt "bereit").
4. Bei theoretischen Meilensteinen: Kernbegriffe werden an einem selbst gewählten
   Beispiel korrekt erklärt.
5. Schüler nennt nachvollziehbare Informationsquellen (Testatkarte, Dokumentation,
   Internetseiten). Ein KI-Chat allein zählt nicht als Quelle.

Sind Kriterien nicht erfüllt: keine Ampel "bereit" vergeben, sondern konkret und
stichpunktartig sagen, was noch fehlt.

# Abschluss-Protokoll

Gib am Ende **immer** folgenden kopierbaren Block aus:

```
## Testat-Selbstcheck-Protokoll
Fach/Thema: ...
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
- [ ] Prompt ist themen-/meilensteinunabhängig (keine fest codierten Inhalte einer
      bestimmten Testatkarte, außer der Nutzer wollte ausdrücklich eine angepasste
      Variante)
- [ ] Alle fünf Bewertungskriterien sind wörtlich enthalten, inkl. Quellenangabe
      (KI-Chat allein zählt nicht als Quelle)
- [ ] Der Ablaufschritt "Fehler einbauen" ist enthalten und beschreibt, dass der Fehler
      nicht verraten wird
- [ ] Das Abschluss-Protokoll enthält das Feld "Quellen"
- [ ] Abschluss-Protokoll-Format ist enthalten, inkl. Hinweis, dass es die echte Abnahme
      nicht ersetzt
- [ ] Ausgabe ist eine `.md`-Datei, kein docx
