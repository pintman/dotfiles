#!/usr/bin/env python3
"""Findet Videos in einer YouTube-Playlist per Titel-Stichwort, ohne API-Key."""
import argparse
import json
import re
import sys
import urllib.request

USER_AGENT = "Mozilla/5.0"
CONSENT_COOKIE = "CONSENT=YES+cb; SOCS=CAI"
DATA_MARKER = "var ytInitialData = "


def extract_playlist_id(value: str) -> str:
    match = re.search(r"[?&]list=([0-9A-Za-z_-]+)", value)
    return match.group(1) if match else value


def fetch_html(playlist_id: str) -> str:
    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Cookie": CONSENT_COOKIE},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_videos(html: str) -> list:
    start = html.index(DATA_MARKER) + len(DATA_MARKER)
    data, _ = json.JSONDecoder().raw_decode(html, start)

    videos: list = []

    def walk(obj) -> None:
        if isinstance(obj, dict):
            if "lockupViewModel" in obj:
                lvm = obj["lockupViewModel"]
                try:
                    title = lvm["metadata"]["lockupMetadataViewModel"]["title"]["content"]
                    videos.append({"video_id": lvm["contentId"], "title": title})
                except (KeyError, TypeError):
                    pass
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)
    return videos


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("playlist", help="Playlist-URL oder Playlist-ID")
    parser.add_argument(
        "keyword",
        nargs="?",
        help="Stichwort zum Filtern der Titel (case-insensitive); ohne Angabe werden alle Videos gelistet",
    )
    args = parser.parse_args()

    playlist_id = extract_playlist_id(args.playlist)

    try:
        html = fetch_html(playlist_id)
        videos = parse_videos(html)
    except ValueError:
        print(
            "Fehler: 'ytInitialData' nicht in der Playlist-Seite gefunden "
            "(Consent-Cookie? Playlist-ID korrekt?)",
            file=sys.stderr,
        )
        sys.exit(1)
    except OSError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        sys.exit(1)

    if not videos:
        print("Fehler: Keine Videos in der Playlist gefunden", file=sys.stderr)
        sys.exit(1)

    if args.keyword:
        keyword = args.keyword.lower()
        videos = [v for v in videos if keyword in v["title"].lower()]

    print(json.dumps(videos, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
