---
name: apple-mail
description: "Liest und durchsucht E-Mails in Apple Mail (macOS Mail.app) per AppleScript/osascript und kann Antwort-Entwürfe öffnen. Nutze diesen Skill, wenn eine Mail in AppleMail/Mail.app gesucht, gelesen oder eine Antwort vorbereitet werden soll. Trigger: \"Mail in AppleMail\", \"zeig mir die Mail zu...\", \"suche die E-Mail von...\", \"erstelle eine Antwort für diese Mail\". Kein Versand — Mails werden nur gelesen bzw. Entwürfe nur geöffnet, nie automatisch abgeschickt."
---

# Apple-Mail-Skill

Liest E-Mails aus Mail.app per `osascript`/AppleScript. Kein IMAP/API-Zugriff, keine anderen Mail-Clients.

**Mails werden nie automatisch versendet.** Antwort-Entwürfe nur öffnen (`reply ... with opening window`), niemals `send`.

## Accounts finden

Accounts sind in Mail.app per Name identifiziert, nicht per E-Mail-Adresse — beide können aber unterschiedlich sein. Vor dem ersten Zugriff auf einen Account per Namen prüfen, ob Name und E-Mail-Adresse übereinstimmen:

```bash
osascript -e '
tell application "Mail"
	set output to ""
	repeat with acc in accounts
		set output to output & (name of acc) & " | " & (email addresses of acc) & linefeed
	end repeat
	return output
end tell
'
```

## Mailbox-Namen

Die Inbox heißt **nicht** `"INBOX"` — je nach Account-Sprache/Typ z. B. `"Posteingang"` (deutsches iCloud/IMAP-Konto) oder `"INBOX"` (manche Provider). Bei Unsicherheit zuerst alle Mailbox-Namen des Accounts auflisten, bevor eine Mailbox referenziert wird:

```bash
osascript -e '
tell application "Mail"
	set theAccount to account "marco@bakera.de"
	set output to ""
	repeat with mb in mailboxes of theAccount
		set output to output & (name of mb) & linefeed
	end repeat
	return output
end tell
'
```

## Mails suchen und lesen

Erst gezielt in einer bekannten Mailbox suchen (schnell), nicht pauschal über `mailboxes of theAccount` iterieren — das kann bei vielen/großen Mailboxen sehr lange dauern oder Mail.app zum Hängen bringen (siehe Fehlerbehandlung).

```bash
osascript -e '
tell application "Mail"
	set theAccount to account "marco@bakera.de"
	set theInbox to mailbox "Posteingang" of theAccount
	set foundMsgs to (messages of theInbox whose subject contains "Suchbegriff")
	set output to ""
	repeat with m in foundMsgs
		set output to output & "Von: " & (sender of m) & linefeed
		set output to output & "Betreff: " & (subject of m) & linefeed
		set output to output & "Datum: " & (date received of m) & linefeed
		set output to output & "---" & linefeed
	end repeat
	return output
end tell
'
```

Inhalt einer konkreten Treffer-Mail:

```bash
osascript -e '
tell application "Mail"
	set theAccount to account "marco@bakera.de"
	set theInbox to mailbox "Posteingang" of theAccount
	set foundMsgs to (messages of theInbox whose subject contains "Suchbegriff")
	set m to item 1 of foundMsgs
	return (content of m)
end tell
'
```

## Antwort-Entwurf öffnen (nicht senden)

`reply m with opening window` öffnet das Antwortfenster und platziert den Cursor bereits oberhalb des zitierten Originaltexts — genau da, wo eigener Text hin soll. **Nicht** versuchen, den Text über das `content`-Property der Antwort zu setzen (siehe Fehlerbehandlung) — stattdessen das Fenster einfach offen lassen und Nutzer selbst tippen lassen, oder bei erteilter Bedienungshilfen-Berechtigung per `System Events`/`keystroke` eintippen.

```bash
osascript -e '
tell application "Mail"
	set theAccount to account "marco@bakera.de"
	set theInbox to mailbox "Posteingang" of theAccount
	set foundMsgs to (messages of theInbox whose subject contains "Suchbegriff")
	set m to item 1 of foundMsgs
	reply m with opening window
end tell
'
```

Falls Text automatisiert eingefügt werden soll, per `System Events` tippen (erfordert Bedienungshilfen-Berechtigung für den Prozess, der `osascript` ausführt — siehe Fehlerbehandlung):

```bash
delay 1.5
tell application "Mail" to activate
delay 0.5
tell application "System Events"
	keystroke "Antworttext"
end tell
```

## Fehlerbehandlung

| Problem | Lösung |
|---|---|
| Suche über `repeat with mb in mailboxes of theAccount` (alle Mailboxen) dauert >120s oder Mail.app wird unresponsive | Task abbrechen (`TaskStop`), Mail.app ggf. neu starten lassen, danach gezielt nur in einer bekannten Mailbox (z. B. `"Posteingang"`) suchen statt über alle Mailboxen zu iterieren |
| `mailbox "INBOX" of account id ...` kann nicht gelesen werden (-1728) | Mailbox-Namen falsch geraten — erst Mailbox-Namen des Accounts auflisten (siehe oben), dann den tatsächlichen Namen verwenden (z. B. `"Posteingang"`) |
| Text, der per `set content of theReply to "..."` gesetzt wurde, taucht kurz auf und verschwindet wieder / ist am Ende leer | Bekannte Einschränkung: Mail.app füllt den zitierten Text im WebView-Editor asynchron nach dem Öffnen des Fensters und überschreibt dabei per AppleScript gesetzten Inhalt — auch mit `delay` vor dem Setzen nicht zuverlässig behebbar. Property-basiertes Setzen von `content` bei Antwort-Fenstern vermeiden; stattdessen Fenster offen lassen (Cursor steht schon richtig) oder per `System Events`/`keystroke` tippen |
| `System Events hat einen Fehler erhalten: osascript ist nicht berechtigt, Tastatureingaben zu senden (1002)` | Bedienungshilfen-Berechtigung fehlt. Benutzer muss sie manuell erteilen: Systemeinstellungen → Datenschutz & Sicherheit → Bedienungshilfen → den Prozess aktivieren, der `osascript` ausführt (z. B. Terminal). Bis dahin: Fenster nur öffnen, Marco tippt selbst |
