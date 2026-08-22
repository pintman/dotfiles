#!/usr/bin/env python3
"""Ruft Titel und Beschreibung eines YouTube-Videos ab, ohne API-Key."""
import argparse
import json
import re
import sys
import urllib.request

USER_AGENT = "Mozilla/5.0"


def extract_video_id(value: str) -> str:
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", value):
        return value
    match = re.search(r"(?:v=|youtu\.be/|/shorts/)([0-9A-Za-z_-]{11})", value)
    if not match:
        raise ValueError(f"Keine Video-ID in '{value}' gefunden")
    return match.group(1)


def fetch_html(video_id: str) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_title(html: str) -> str | None:
    match = re.search(r'<meta name="title" content="([^"]*)"', html)
    return match.group(1) if match else None


def extract_description(html: str) -> str | None:
    match = re.search(r'"shortDescription":"((?:[^"\\]|\\.)*)"', html)
    if not match:
        return None
    return json.loads(f'"{match.group(1)}"')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", help="YouTube-URL oder Video-ID")
    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.video)
        html = fetch_html(video_id)
    except (ValueError, OSError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        sys.exit(1)

    title = extract_title(html)
    description = extract_description(html)

    if description is None:
        print(
            f"Fehler: Konnte Beschreibung für Video {video_id} nicht extrahieren",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        json.dumps(
            {"video_id": video_id, "title": title, "description": description},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
