---
name: youtube
description: "Ermittelt Titel und Beschreibung von YouTube-Videos oder findet ein bestimmtes Video innerhalb einer YouTube-Playlist. Trigger: ein YouTube-Link kommt vor, \"YouTube-Link\", \"Video zusammenfassen\", \"was ist in dem Video\", \"in der Playlist suchen\", \"welches Video ist gemeint\"."
---

# YouTube-Skill

Ruft Titel und Beschreibung eines YouTube-Videos ab bzw. findet ein Video innerhalb einer
Playlist - ohne API-Key, nur mit Python-Stdlib (`urllib`, `json`, `re`).

**Wichtig:** `WebFetch` allein liefert bei YouTube-Videoseiten meist nicht das echte
Beschreibungsfeld, sondern nur Footer-Boilerplate. Deshalb immer die Skripte unten verwenden,
die die Seite direkt holen und das eingebettete JSON auswerten - nicht aus Titel/Thumbnail raten.

## Fall 1: Direkter Video-Link vorhanden

```bash
python3 scripts/video_info.py "<Video-URL-oder-ID>"
```

Gibt JSON mit `video_id`, `title`, `description` aus (Beschreibung bereits JSON-dekodiert,
keine `\n`-Escapes mehr). Auf Basis des tatsächlichen Beschreibungstexts eine kurze
Zusammenfassung (1-2 Sätze) formulieren - nicht aus Titel/Thumbnail raten.

## Fall 2: Nur ein Verweis auf eine Playlist (Video muss erst gefunden werden)

Wenn eine Notiz/Anfrage nur auf eine Playlist verweist statt auf einen direkten Video-Link:

```bash
python3 scripts/playlist_search.py "<Playlist-URL-oder-ID>" "<Stichwort>"
```

Gibt eine JSON-Liste aller Treffer (`video_id`, `title`) aus, deren Titel das Stichwort
enthalten (case-insensitive). Ohne Stichwort-Argument werden alle Videos der Playlist gelistet -
nützlich, wenn aus der Anfrage nicht klar hervorgeht, wonach gesucht werden soll.

Anhand des Titels/Stichworts aus der ursprünglichen Anfrage das passende Video identifizieren,
dann für dieses Video `video_info.py` wie in Fall 1 aufrufen.

## Hinweise

- Beide Skripte funktionieren komplett ohne YouTube-API-Key, nur mit Python-Stdlib - keine
  externen Pakete nötig.
- `playlist_search.py` schickt ein Consent-Cookie mit (`CONSENT=YES+cb; SOCS=CAI`) - ohne das
  liefert YouTube nur einen Redirect auf `consent.youtube.com` mit leerem Body.
- Playlist-Einträge stecken im HTML unter `var ytInitialData = {...};`, unter dem Schlüssel
  `lockupViewModel` (die frühere Struktur `playlistVideoRenderer` existiert in aktuellen
  YouTube-Ausgaben nicht mehr) - das Skript parst per `json.JSONDecoder().raw_decode` statt
  per Regex bis zum ersten `;`, da das JSON selbst `;` in Strings enthalten kann.
- Wird das gefundene Ergebnis in eine Notiz/Datei übernommen: Titel und kurze Zusammenfassung
  (nicht nur den nackten Link) eintragen, damit der Kontext auch ohne erneutes Nachschlagen
  verständlich bleibt.
