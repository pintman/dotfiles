---
name: apple-mail
description: "Liest und durchsucht E-Mails in Apple Mail (macOS Mail.app) per AppleScript/osascript und kann Antwort-Entwürfe öffnen. Nutze diesen Skill, wenn eine Mail in AppleMail/Mail.app gesucht, gelesen oder eine Antwort vorbereitet werden soll. Trigger: \"Mail in AppleMail\", \"zeig mir die Mail zu...\", \"suche die E-Mail von...\", \"erstelle eine Antwort für diese Mail\". Kein Versand — Mails werden nur gelesen bzw. Entwürfe nur geöffnet, nie automatisch abgeschickt."
---

# Apple-Mail-Skill

Liest E-Mails aus Mail.app per `scripts/apple_mail.py` (kapselt die AppleScript/osascript-Aufrufe). Kein IMAP/API-Zugriff, keine anderen Mail-Clients.

**Mails werden nie automatisch versendet.** Antwort-Entwürfe nur öffnen (`reply`-Subcommand), niemals senden.

Alle Aufrufe laufen über `python3 scripts/apple_mail.py <subcommand> ...` (reines Stdlib, kein pip install nötig). Bekannte Fallstricke (asynchrones Überschreiben von `content` bei Antwort-Fenstern, Account-Referenzierung per Name) sind im Skript selbst umgesetzt, nicht nur dokumentiert.

## Accounts finden

Accounts sind in Mail.app per Name identifiziert, nicht per E-Mail-Adresse — beide können aber unterschiedlich sein. Vor dem ersten Zugriff auf einen Account per Namen prüfen, ob Name und E-Mail-Adresse übereinstimmen:

```bash
python3 scripts/apple_mail.py list-accounts
```

## Mailbox-Namen

Die Inbox heißt **nicht** `"INBOX"` — je nach Account-Sprache/Typ z. B. `"Posteingang"` (deutsches iCloud/IMAP-Konto) oder `"INBOX"` (manche Provider). Bei Unsicherheit zuerst alle Mailbox-Namen des Accounts auflisten, bevor eine Mailbox referenziert wird:

```bash
python3 scripts/apple_mail.py list-mailboxes --account "<Account-Name>"
```

## Mails suchen und lesen

Erst gezielt in einer bekannten Mailbox suchen (schnell), nicht pauschal über alle Mailboxen eines Accounts iterieren — das kann bei vielen/großen Mailboxen sehr lange dauern oder Mail.app zum Hängen bringen (siehe Fehlerbehandlung). Das Skript bietet dafür bewusst keinen "alle Mailboxen"-Modus an.

```bash
python3 scripts/apple_mail.py search --account "<Account-Name>" --mailbox "Posteingang" --query "Suchbegriff"
```

Listet Treffer nummeriert auf (Von/Betreff/Datum). Inhalt eines konkreten Treffers (1-basierter Index, Default 1):

```bash
python3 scripts/apple_mail.py read --account "<Account-Name>" --mailbox "Posteingang" --query "Suchbegriff" [--index N]
```

## Antwort-Entwurf öffnen (nicht senden)

```bash
python3 scripts/apple_mail.py reply --account "<Account-Name>" --mailbox "Posteingang" --query "Suchbegriff" [--index N] [--text "Antworttext"]
```

Öffnet das Antwortfenster (`reply ... with opening window`) — der Cursor steht bereits oberhalb des zitierten Originaltexts. Ohne `--text` bleibt das Fenster offen und der Nutzer tippt selbst. Mit `--text` tippt das Skript den Text per `System Events`/`keystroke` ein (erfordert Bedienungshilfen-Berechtigung, siehe Fehlerbehandlung) — **nicht** versuchen, den Text stattdessen über das `content`-Property zu setzen, das übernimmt das Skript bewusst nicht (siehe Fehlerbehandlung).

## Fehlerbehandlung

| Problem | Lösung |
|---|---|
| `search`/`read`/`reply` über eine sehr große Mailbox dauert >120s oder Mail.app wird unresponsive | Task abbrechen (`TaskStop`), Mail.app ggf. neu starten lassen, danach mit engerem Suchbegriff oder einer kleineren Mailbox erneut versuchen |
| `mailbox "..." of account id ...` kann nicht gelesen werden (-1728) | Mailbox-Namen falsch geraten — erst `list-mailboxes` aufrufen, dann den tatsächlichen Namen verwenden (z. B. `"Posteingang"`) |
| Antworttext taucht kurz auf und verschwindet wieder / ist am Ende leer | Bekannte Einschränkung: Mail.app füllt den zitierten Text im WebView-Editor asynchron nach dem Öffnen des Fensters und überschreibt dabei per AppleScript gesetzten Inhalt — auch mit `delay` vor dem Setzen nicht zuverlässig behebbar. Deshalb setzt `reply` den Text nie über die `content`-Property, sondern per `keystroke` (mit `--text`) oder lässt das Fenster offen |
| `System Events hat einen Fehler erhalten: osascript ist nicht berechtigt, Tastatureingaben zu senden (1002)` | Bedienungshilfen-Berechtigung fehlt. Benutzer muss sie manuell erteilen: Systemeinstellungen → Datenschutz & Sicherheit → Bedienungshilfen → den Prozess aktivieren, der `osascript` ausführt (z. B. Terminal). Bis dahin: `reply` ohne `--text` aufrufen, Fenster öffnet trotzdem, Benutzer tippt selbst |
