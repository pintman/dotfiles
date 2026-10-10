---
name: discord-post
description: >
  Sendet eine Nachricht per Webhook in einen Discord-Kanal — einfacher Text
  oder Embed mit Titel, Text, Autor, Farbe, Feldern, Bildern, Fußzeile sowie
  optional Dateianhängen. Zeigt immer erst eine Vorschau und sendet nur nach
  Bestätigung.
disable-model-invocation: true
---

# Nachricht in Discord senden

Sendet per Discord-Webhook über `scripts/discord_post.py` (Python 3, nur
Standardbibliothek).

## Ablauf

1. Payload mit `--dry-run` erzeugen und dem Benutzer als Vorschau zeigen.
2. **Erst nach ausdrücklicher Bestätigung** denselben Aufruf ohne `--dry-run`
   ausführen. Nie ungefragt senden.
3. Ausgabe (`message_id`, `channel_id`) kurz melden.

## Einrichtung

Webhook anlegen: Discord-Kanal → Einstellungen → Integrationen → Webhooks →
Neuer Webhook → URL kopieren. Dann im Shell-Profil:

```
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/<ID>/<TOKEN>"
```

Die URL ist ein Geheimnis: niemals in Repo-Dateien, Notizen oder Chat-Ausgaben
schreiben. Für einen anderen Kanal `--webhook <URL>` übergeben (vom Benutzer
bereitgestellt).

## Aufruf

```
python3 scripts/discord_post.py [Optionen] [--dry-run]
```

| Parameter | Bedeutung |
|---|---|
| `--content` | Text außerhalb des Embeds (max. 2000) |
| `--username` | Anzeigename nur für diese Nachricht (max. 80) |
| `--avatar-url` | Profilbild-URL nur für diese Nachricht |
| `--title` | Embed-Titel (max. 256) |
| `--description` / `--text` | Embed-Text, Markdown (max. 4096) |
| `--url` | Link hinter dem Titel |
| `--color` | `#RRGGBB` oder Dezimalzahl |
| `--author`, `--author-url`, `--author-icon` | Autorzeile oben im Embed |
| `--footer`, `--footer-icon` | Fußzeile |
| `--image` / `--thumbnail` | Bild-URL groß unten / klein oben rechts |
| `--field "Name=Wert"` | Feld, mehrfach (max. 25) |
| `--inline-fields` | Felder nebeneinander |
| `--timestamp` | aktuelle Zeit in der Fußzeile |
| `--file PFAD` | Datei anhängen, mehrfach |
| `--allow-mentions` | @-Erwähnungen pingen (Default: aus) |
| `--webhook URL` | statt `$DISCORD_WEBHOOK_URL` |
| `--dry-run` | Payload ausgeben, nicht senden |

Ein Embed entsteht nur, wenn mindestens ein Embed-Parameter gesetzt ist.
Mehrzeiliger Text in Bash: `--text $'Zeile 1\nZeile 2'`.

## Beispiel

```
python3 scripts/discord_post.py \
  --username "Schul-Bot" --title "Klausurtermin FI23" \
  --text "Die Klausur findet **Dienstag** statt." \
  --color "#5865F2" --author "M. Bakera" \
  --field "Raum=A1.23" --field "Zeit=08:00–09:30" --inline-fields \
  --footer "Berufskolleg Bochum" --timestamp --dry-run
```

## Fehlerbehandlung

| Problem | Lösung |
|---|---|
| Exit 2 / `Keine Webhook-URL` | Benutzer bitten, `DISCORD_WEBHOOK_URL` zu setzen (siehe Einrichtung) |
| `Fehler: ... zu lang` | Text kürzen oder auf mehrere Nachrichten aufteilen |
| `HTTP 401/404` | Webhook gelöscht oder URL falsch — Benutzer neue URL besorgen lassen |
| `HTTP 400` mit Fehlertext | Discord-Meldung lesen (meist ungültige Bild-URL oder Format), Parameter korrigieren |
| `HTTP 429` | Rate-Limit — kurz warten, nicht in Schleife wiederholen |
