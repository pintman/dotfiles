---
name: teams-post
description: >
  Bereitet einen Beitrag (Titel + Inhalt) in einem Microsoft-Teams-Kanal vor,
  per Chrome-Browserautomatisierung über chrome-agent. Login übernimmt der
  Benutzer selbst, niemals Zugangsdaten eingeben oder danach fragen. Der Post
  wird nur bis zum ausgefüllten Entwurf vorbereitet — "Veröffentlichen"
  klickt immer der Benutzer selbst, nie automatisch. Trigger: "Post in Teams
  vorbereiten", "Teams-Beitrag erstellen", "in Teams-Kanal X posten",
  "Beitrag in Microsoft Teams".
disable-model-invocation: true
---

# Beitrag in Microsoft Teams vorbereiten

Füllt einen neuen Kanal-Beitrag (Betreff + Nachricht) in Microsoft Teams
Web aus, per `chrome-agent` (CDP). **Sendet nie automatisch** — der Klick auf
"Veröffentlichen" bleibt immer beim Benutzer.

## Voraussetzung

`chrome-agent` (https://github.com/captivus/chrome-agent) muss auf dem PATH
sein. Fehlt es, meldet das Skript das über Exit-Code 2 — dann den Skill
`setup-chrome-agent` nutzen, um es einzurichten.

## Aufruf

```
python3 scripts/teams_post.py \
  --team "<Teamname>" --title "<Titel>" --content "<Inhalt>" \
  [--channel "<Kanalname>"]
```

| Parameter | Pflicht | Bedeutung |
|---|---|---|
| `--team` | ja | Teamname exakt wie in der Teams-Seitenleiste angezeigt |
| `--title` | ja | Text fürs Betreff-Feld |
| `--content` | ja | Text fürs Nachrichtenfeld |
| `--channel` | nein | Kanalname, Default `Allgemein` |

Login übernimmt der Benutzer selbst — das Skript gibt niemals Zugangsdaten
ein. Ist beim ersten Start kein Login vorhanden, wartet das Skript bis zu
`--login-timeout` Sekunden (Default 300) darauf.

Das Skript navigiert zum passenden Team/Kanal, klickt "In Kanal posten",
füllt Betreff- und Nachrichtenfeld aus — und **stoppt dann bewusst vor dem
Klick auf "Veröffentlichen"**. Es meldet am Ende die chrome-agent-Instanz;
der Benutzer prüft im Fenster und veröffentlicht selbst (oder verwirft den
Entwurf über das Papierkorb-Icon oben rechts im Compose-Bereich).

Läuft bereits eine chrome-agent-Instanz mit offenem Teams-Tab, wird diese
wiederverwendet (kein erneuter Login nötig).

## Team-/Kanalnamen ermitteln

`--team`/`--channel` müssen exakt wie in Teams angezeigt geschrieben sein.
Bei Unsicherheit oder wenn `teams_post.py` mit `Team '<Name>' nicht gefunden`
oder `Kanal '<Name>' nicht gefunden` abbricht: **nicht raten**, sondern
`scripts/teams_list.py` nutzen, um die exakten Namen aufzulisten (reine
Leseoperation, ändert nichts):

```
python3 scripts/teams_list.py                 # alle Teams auflisten
python3 scripts/teams_list.py --team "<Teamname>"   # Kanäle dieses Teams auflisten
```

Gibt eine Namensliste (einer pro Zeile) auf stdout aus; Statusmeldungen
gehen nach stderr. Nutzt dieselbe chrome-agent-Instanz/-Session wie
`teams_post.py`.

## Fehlerbehandlung

| Problem | Lösung |
|---|---|
| Exit-Code 2 / `chrome-agent nicht gefunden` | Skill `setup-chrome-agent` ausführen, danach erneut versuchen |
| `Fehler: Team '<Name>' nicht gefunden` | `scripts/teams_list.py` (ohne `--team`) ausführen, um die exakte Schreibweise zu ermitteln — nicht raten |
| `Fehler: Kanal '<Name>' nicht gefunden` | `scripts/teams_list.py --team "<Teamname>"` ausführen, um die exakten Kanalnamen zu ermitteln, oder `--channel` weglassen für den Standardkanal "Allgemein" |
| Skript hängt bei "Warte auf manuellen Login" | Benutzer muss sich im geöffneten Chrome-Fenster einloggen; danach erkennt das Skript den Login automatisch am Nav-Eintrag "Aktivität" |
| Nachrichtenfeld enthält den Inhalt nicht wie erwartet (z. B. bei mehrzeiligem `--content`) | Bekannte Einschränkung: Text wird per CDP `Input.insertText` als ein Block eingefügt; ob eingebettete Zeilenumbrüche als Absätze ankommen, ist nicht in jedem Fall verlässlich. Ergebnis im Chrome-Fenster prüfen und bei Bedarf manuell nachbessern, bevor veröffentlicht wird |
| Bricht das Skript mit `Fehler: ... nicht gefunden` ab (z. B. weil sich die Teams-Oberfläche geändert hat) | Nicht blind wiederholen — Hinweis an den Benutzer geben |
