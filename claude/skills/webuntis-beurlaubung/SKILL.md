---
name: webuntis-beurlaubung
description: >
  Bereitet eine Beurlaubung (genehmigte Abwesenheit, ganztägig) für einen oder
  mehrere Schüler/Azubis in WebUntis vor, per Chrome-Browserautomatisierung —
  trägt sie aber NICHT final ein. Login übernimmt Benutzer selbst, niemals
  Zugangsdaten eingeben oder danach fragen. Den abschließenden "Speichern"-Klick
  löst immer der Benutzer selbst aus, nie das Skript. Gibt am Ende einen
  Vorlagentext für den Ausbildungsbetrieb auf der Konsole aus. Benötigt
  `chrome-agent` — es gibt keinen claude-in-chrome-Fallback.
disable-model-invocation: true
---

# Beurlaubung in WebUntis vorbereiten

Legt einen Abwesenheitseintrag mit Grund "Beurlaubung" für einen oder mehrere Schüler
einer Klasse an, für einen Tag oder Zeitraum. Füllt das Formular vollständig aus,
speichert aber bewusst nicht. Am Ende wird ein fertiger Vorlagentext für den
Ausbildungsbetrieb ausgegeben.

## Voraussetzungen

- `chrome-agent` muss installiert sein (`command -v chrome-agent` prüfen). Falls nicht:
  Skill `setup-chrome-agent` verwenden, um es zu installieren. 
- WebUntis läuft unter `https://tbs1.webuntis.com`.
- Login übernimmt Benutzer selbst — keine Zugangsdaten eingeben oder erfragen. Falls die
  Seite einen Login-Screen zeigt, Benutzer bitten, sich selbst einzuloggen, und danach
  fortfahren.
- Den "Speichern"-Klick am Ende löst immer der Benutzer selbst aus — niemals automatisch
  auslösen, auch nicht auf ausdrückliche Bitte.
- Alle genannten Schüler müssen in derselben Klasse sein (das WebUntis-Abwesenheitsformular
  ist klassenbezogen — ein Auftrag über mehrere Klassen hinweg braucht mehrere Durchläufe).

## Ablauf

```
python3 scripts/webuntis_beurlaubung.py \
  --klasse <Klassenkürzel> \
  --schueler "<Nachname Vorname>" [--schueler "<Nachname Vorname>" ...] \
  --von YYYY-MM-DD [--bis YYYY-MM-DD] \
  [--text "Beurlaubung durch Ausbildungsbetrieb"]
```

- `--klasse` muss exakt wie in WebUntis lauten (z. B. `ITF24a`) — im Zweifel vorher mit dem
  Benutzer klären.
- `--schueler` in der Form "Nachname Vorname" (so wie WebUntis die Namen in der Liste
  anzeigt), mehrfach angeben für mehrere Schüler. Bei Unsicherheit über die Schreibweise
  lieber vorher fragen statt zu raten — das Skript bricht mit klarer Fehlermeldung ab, wenn
  ein Name im Auswahlfeld nicht gefunden wird.
- `--bis` ist optional und defaultet auf `--von` (Beurlaubung für einen einzelnen Tag).
- `--text` ist optional, Default: "Beurlaubung durch Ausbildungsbetrieb". Der
  "Abwesenheitsgrund" wird immer fest auf die WebUntis-Option "Beurlaubung" gesetzt (dafür
  ist dieser Skill da) — dieser Wert ist nicht per Parameter änderbar.
- Das Skript startet Chrome selbst (persistentes Profil unter
  `~/.claude/webuntis-beurlaubung/`), wartet auf manuellen Login, navigiert zu
  Klassenbuch → Abwesenheiten, setzt den Klassenfilter, öffnet "Neue Abwesenheit", wählt die
  Schüler, setzt Zeitraum/Grund/Text — und **stoppt dann bewusst vor dem Speichern**. Danach
  gibt es den Vorlagentext für den Betrieb auf der Konsole aus.
- Läuft bereits eine chrome-agent-Instanz mit offenem WebUntis-Tab, wird diese wiederverwendet
  (kein erneuter Login nötig).
- Bricht das Skript mit einem `Fehler: ... nicht gefunden`-Hinweis ab (z. B. weil sich die
  WebUntis-Oberfläche geändert hat, oder weil ein Schülername/Klassenkürzel nicht passt),
  nicht blind wiederholen — Hinweis an den Nutzer geben, Ursache klären (Schreibweise,
  Klassenkürzel, ggf. geänderte WebUntis-Oberfläche).
- Exit-Code 2 bedeutet: `chrome-agent` fehlt. Dann `setup-chrome-agent` ausführen und
  danach erneut versuchen.

## Abschließender Vorlagentext

Das Skript gibt automatisch folgenden Vorlagentext für den Ausbildungsbetrieb aus:

- Ein Schüler: „Die Beurlaubung für den Azubi \<Name\> wurde am \<Datum\> genehmigt, sofern
  keine angekündigten Leistungsüberprüfungen für den Tag vorliegen."
- Mehrere Schüler: „Die Beurlaubung für die Azubis \<Name1\> und \<Name2\> wurde am \<Datum\>
  genehmigt, sofern keine angekündigten Leistungsüberprüfungen für den Tag vorliegen."
- Zeitraum statt Einzeltag: „... wurde vom \<Von\> bis \<Bis\> genehmigt, ..."
