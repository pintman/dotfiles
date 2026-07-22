---
name: youtube
description: "Ermittelt Titel und Beschreibung von YouTube-Videos oder findet ein bestimmtes Video innerhalb einer YouTube-Playlist. Trigger: ein YouTube-Link kommt vor, \"YouTube-Link\", \"Video zusammenfassen\", \"was ist in dem Video\", \"in der Playlist suchen\", \"welches Video ist gemeint\"."
---

# YouTube-Skill

Ruft Titel und Beschreibung eines YouTube-Videos ab bzw. findet ein Video innerhalb einer
Playlist - ohne API-Key, nur mit `curl` und Python-Stdlib (`json`, `re`).

**Wichtig:** `WebFetch` allein liefert bei YouTube-Videoseiten meist nicht das echte
Beschreibungsfeld, sondern nur Footer-Boilerplate. Deshalb immer die Seite per `curl` direkt
holen und das eingebettete JSON auswerten - nicht aus Titel/Thumbnail raten.

## Fall 1: Direkter Video-Link vorhanden

1. Video-ID aus der URL extrahieren (Parameter `v=` bzw. Teil nach `youtu.be/`).
2. Seite holen und Beschreibung extrahieren:
   ```bash
   curl -s "https://www.youtube.com/watch?v=<ID>" -A "Mozilla/5.0" | grep -o '"shortDescription":"[^"]*"'
   ```
3. Titel und Beschreibung (JSON-escaped, also `\n` etc. beim Lesen beachten) als Basis für eine
   kurze Zusammenfassung (1-2 Sätze) verwenden - nicht aus dem Titel/Thumbnail geraten, sondern
   auf Basis des tatsächlichen Beschreibungstexts.

## Fall 2: Nur ein Verweis auf eine Playlist (Video muss erst gefunden werden)

Wenn eine Notiz/Anfrage nur auf eine Playlist verweist statt auf einen direkten Video-Link,
zuerst das passende Video darin identifizieren:

1. Playlist-HTML holen. Ohne Consent-Cookie liefert YouTube nur einen Redirect auf
   `consent.youtube.com` mit leerem Body - deshalb Cookie mitschicken:
   ```bash
   curl -s "https://www.youtube.com/playlist?list=<PLAYLIST_ID>" -A "Mozilla/5.0" \
     -H "Cookie: CONSENT=YES+cb; SOCS=CAI" -o playlist.html
   ```
2. Die Playlist-Items stecken im HTML in `var ytInitialData = {...};`. Ein Regex bis zum ersten
   `;` schlägt fehl, weil das JSON selbst `;` in Strings enthalten kann - stattdessen ab der
   Fundstelle mit Pythons `json.JSONDecoder().raw_decode(html, start)` parsen. Die früher
   verwendete Struktur `playlistVideoRenderer` existiert in aktuellen YouTube-Ausgaben nicht
   mehr; Playlist-Einträge stecken jetzt unter dem Schlüssel `lockupViewModel` - rekursiv
   einsammeln. Je Eintrag:
   - Video-ID: `lockupViewModel['contentId']`
   - Titel: `lockupViewModel['metadata']['lockupMetadataViewModel']['title']['content']`

   Beispiel-Snippet:
   ```python
   import json, re

   html = open("playlist.html", encoding="utf-8").read()
   start = html.index("var ytInitialData = ") + len("var ytInitialData = ")
   data, _ = json.JSONDecoder().raw_decode(html, start)

   def find_lockups(obj, out):
       if isinstance(obj, dict):
           if "lockupViewModel" in obj:
               lvm = obj["lockupViewModel"]
               try:
                   title = lvm["metadata"]["lockupMetadataViewModel"]["title"]["content"]
                   out.append((lvm["contentId"], title))
               except (KeyError, TypeError):
                   pass
           for v in obj.values():
               find_lockups(v, out)
       elif isinstance(obj, list):
           for v in obj:
               find_lockups(v, out)

   videos = []
   find_lockups(data, videos)
   ```
3. Anhand des Titels/Stichworts aus der ursprünglichen Anfrage das passende Video identifizieren.
4. Für dieses Video wie in Fall 1 die Beschreibung per `shortDescription`-Regex holen.

## Hinweise

- Beide Fälle funktionieren komplett ohne YouTube-API-Key.
- Nur `curl` + Python-Stdlib (`json`, `re`) nötig, keine externen Pakete.
- Wird das gefundene Ergebnis in eine Notiz/Datei übernommen: Titel und kurze Zusammenfassung
  (nicht nur den nackten Link) eintragen, damit der Kontext auch ohne erneutes Nachschlagen
  verständlich bleibt.
