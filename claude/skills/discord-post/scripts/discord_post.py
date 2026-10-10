#!/usr/bin/env python3
"""Sendet eine Nachricht (optional mit Embed und Dateianhängen) per Webhook in einen Discord-Kanal.

Webhook-URL kommt aus der Umgebungsvariable DISCORD_WEBHOOK_URL oder aus
--webhook. Mit --dry-run wird nur der JSON-Payload ausgegeben, nichts gesendet.

Nur Standardbibliothek, keine weiteren Abhängigkeiten.
"""

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

ENV_VAR = "DISCORD_WEBHOOK_URL"
USER_AGENT = "discord-post/1.0"

WEBHOOK_MISSING_EXIT = 2

LIMITS = {
    "content": 2000,
    "username": 80,
    "title": 256,
    "description": 4096,
    "author": 256,
    "footer": 2048,
    "field_name": 256,
    "field_value": 1024,
    "fields": 25,
    "embed_total": 6000,
}


class InputError(Exception):
    """Ungültige Eingabe, z. B. Limit überschritten."""


def check_len(name: str, value: str | None, limit_key: str | None = None) -> None:
    limit = LIMITS[limit_key or name]
    if value is not None and len(value) > limit:
        raise InputError(f"{name} ist zu lang ({len(value)} > {limit} Zeichen)")


def parse_color(value: str) -> int:
    v = value.strip()
    try:
        if v.startswith("#"):
            return int(v[1:], 16)
        if v.lower().startswith("0x"):
            return int(v, 16)
        return int(v)
    except ValueError:
        raise InputError(f"Ungültige Farbe '{value}' (erwartet #RRGGBB oder Dezimalzahl)") from None


def parse_field(raw: str, inline: bool) -> dict:
    if "=" not in raw:
        raise InputError(f"Feld '{raw}' hat nicht das Format Name=Wert")
    name, value = raw.split("=", 1)
    name, value = name.strip(), value.strip()
    if not name or not value:
        raise InputError(f"Feld '{raw}': Name und Wert dürfen nicht leer sein")
    check_len("Feldname", name, "field_name")
    check_len("Feldwert", value, "field_value")
    return {"name": name, "value": value, "inline": inline}


def build_embed(args: argparse.Namespace) -> dict | None:
    embed: dict = {}
    if args.title:
        check_len("title", args.title)
        embed["title"] = args.title
    if args.description:
        check_len("description", args.description)
        embed["description"] = args.description
    if args.url:
        embed["url"] = args.url
    if args.color:
        embed["color"] = parse_color(args.color)
    if args.author:
        check_len("author", args.author)
        embed["author"] = {"name": args.author}
        if args.author_url:
            embed["author"]["url"] = args.author_url
        if args.author_icon:
            embed["author"]["icon_url"] = args.author_icon
    if args.footer:
        check_len("footer", args.footer)
        embed["footer"] = {"text": args.footer}
        if args.footer_icon:
            embed["footer"]["icon_url"] = args.footer_icon
    if args.image:
        embed["image"] = {"url": args.image}
    if args.thumbnail:
        embed["thumbnail"] = {"url": args.thumbnail}
    if args.field:
        if len(args.field) > LIMITS["fields"]:
            raise InputError(f"Zu viele Felder ({len(args.field)} > {LIMITS['fields']})")
        embed["fields"] = [parse_field(f, args.inline_fields) for f in args.field]
    if not embed:
        return None
    if args.timestamp:
        embed["timestamp"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    total = sum(
        len(s)
        for s in [
            embed.get("title", ""),
            embed.get("description", ""),
            embed.get("author", {}).get("name", ""),
            embed.get("footer", {}).get("text", ""),
            *(f["name"] + f["value"] for f in embed.get("fields", [])),
        ]
    )
    if total > LIMITS["embed_total"]:
        raise InputError(f"Embed insgesamt zu lang ({total} > {LIMITS['embed_total']} Zeichen)")
    return embed


def build_payload(args: argparse.Namespace) -> dict:
    payload: dict = {}
    if args.content:
        check_len("content", args.content)
        payload["content"] = args.content
    if args.username:
        check_len("username", args.username)
        payload["username"] = args.username
    if args.avatar_url:
        payload["avatar_url"] = args.avatar_url
    embed = build_embed(args)
    if embed:
        payload["embeds"] = [embed]
    if not args.allow_mentions:
        payload["allowed_mentions"] = {"parse": []}
    if not (payload.get("content") or embed or args.file):
        raise InputError("Nichts zu senden: mindestens --content, ein Embed-Feld oder --file angeben")
    return payload


def build_multipart(payload: dict, files: list[Path]) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    parts: list[bytes] = []
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="payload_json"\r\n'
        f"Content-Type: application/json\r\n\r\n".encode()
        + json.dumps(payload).encode()
        + b"\r\n"
    )
    for i, path in enumerate(files):
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="files[{i}]"; '
            f'filename="{path.name}"\r\nContent-Type: {ctype}\r\n\r\n'.encode()
            + path.read_bytes()
            + b"\r\n"
        )
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def send(webhook: str, payload: dict, files: list[Path]) -> dict:
    sep = "&" if urllib.parse.urlparse(webhook).query else "?"
    url = f"{webhook}{sep}wait=true"
    if files:
        body, ctype = build_multipart(payload, files)
    else:
        body, ctype = json.dumps(payload).encode(), "application/json"
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": ctype, "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read() or b"{}")


def main() -> int:
    p = argparse.ArgumentParser(description="Nachricht per Webhook in einen Discord-Kanal senden.")
    p.add_argument("--webhook", help=f"Webhook-URL (Default: ${ENV_VAR})")
    p.add_argument("--content", help="Nachrichtentext außerhalb des Embeds (max. 2000)")
    p.add_argument("--username", help="Anzeigename für diese Nachricht")
    p.add_argument("--avatar-url", help="Profilbild-URL für diese Nachricht")

    e = p.add_argument_group("Embed")
    e.add_argument("--title", help="Embed-Titel (max. 256)")
    e.add_argument("--description", "--text", dest="description", help="Embed-Text, Markdown (max. 4096)")
    e.add_argument("--url", help="Link hinter dem Titel")
    e.add_argument("--color", help="Farbe als #RRGGBB oder Dezimalzahl")
    e.add_argument("--author", help="Autorname")
    e.add_argument("--author-url", help="Link hinter dem Autornamen")
    e.add_argument("--author-icon", help="Icon-URL neben dem Autornamen")
    e.add_argument("--footer", help="Fußzeilentext")
    e.add_argument("--footer-icon", help="Icon-URL in der Fußzeile")
    e.add_argument("--image", help="URL großes Bild")
    e.add_argument("--thumbnail", help="URL kleines Bild oben rechts")
    e.add_argument("--field", action="append", metavar="NAME=WERT", help="Feld (mehrfach möglich)")
    e.add_argument("--inline-fields", action="store_true", help="Felder nebeneinander anzeigen")
    e.add_argument("--timestamp", action="store_true", help="aktuelle Zeit als Zeitstempel setzen")

    p.add_argument("--file", action="append", type=Path, metavar="PFAD", help="Datei anhängen (mehrfach möglich)")
    p.add_argument("--allow-mentions", action="store_true", help="@-Erwähnungen pingen lassen (Default: aus)")
    p.add_argument("--dry-run", action="store_true", help="nur Payload ausgeben, nicht senden")
    args = p.parse_args()

    files = args.file or []
    try:
        for f in files:
            if not f.is_file():
                raise InputError(f"Datei nicht gefunden: {f}")
        payload = build_payload(args)
    except InputError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        for f in files:
            print(f"Anhang: {f}", file=sys.stderr)
        return 0

    webhook = args.webhook or os.environ.get(ENV_VAR)
    if not webhook:
        print(f"Keine Webhook-URL: ${ENV_VAR} setzen oder --webhook angeben.", file=sys.stderr)
        return WEBHOOK_MISSING_EXIT

    try:
        msg = send(webhook, payload, files)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        print(f"Fehler: HTTP {exc.code} – {detail}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Fehler: Verbindung fehlgeschlagen – {exc.reason}", file=sys.stderr)
        return 1

    print(f"Gesendet: message_id={msg.get('id')} channel_id={msg.get('channel_id')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
