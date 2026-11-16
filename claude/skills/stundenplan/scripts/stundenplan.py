#!/usr/bin/env python3
"""Lädt einen WebUntis-iCal-Feed und listet Termine in einem Datumsbereich auf.

Reines Python-Stdlib, kein pip install nötig.
"""

import argparse
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

WEEKDAYS_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

def find_env_file(start: Path) -> Path | None:
    """Sucht eine .env-Datei ausgehend vom Skript-Ordner aufwärts bis zum Filesystem-Root.

    Macht den Skill portabel: unabhängig davon, wie tief er in einem Projekt liegt, wird
    die nächstgelegene .env im Projektbaum gefunden statt einen festen Pfad anzunehmen.
    """
    for candidate_dir in [start, *start.parents]:
        candidate = candidate_dir / ".env"
        if candidate.is_file():
            return candidate
    return None


def load_env_file(path: Path | None) -> dict[str, str]:
    values: dict[str, str] = {}
    if path is None or not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def fetch_ics(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.URLError as exc:
        print(f"Fehler beim Abruf des Stundenplan-Feeds: {exc}", file=sys.stderr)
        sys.exit(1)


def unfold_lines(raw: str) -> list[str]:
    # iCal-Zeilenfaltung: Fortsetzungszeilen beginnen mit Leerzeichen/Tab.
    lines = raw.replace("\r\n", "\n").split("\n")
    unfolded: list[str] = []
    for line in lines:
        if line.startswith((" ", "\t")) and unfolded:
            unfolded[-1] += line[1:]
        else:
            unfolded.append(line)
    return unfolded


def unescape_ical(value: str) -> str:
    return (
        value.replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\n", " ")
        .replace("\\\\", "\\")
    )


def parse_events(lines: list[str]) -> list[dict]:
    events: list[dict] = []
    current: dict | None = None
    for line in lines:
        if line == "BEGIN:VEVENT":
            current = {}
        elif line == "END:VEVENT":
            if current is not None and "dtstart" in current:
                events.append(current)
            current = None
        elif current is not None:
            if line.startswith("DTSTART"):
                current["dtstart"] = parse_dt(line)
            elif line.startswith("DTEND"):
                current["dtend"] = parse_dt(line)
            elif line.startswith("SUMMARY:"):
                current["summary"] = unescape_ical(line[len("SUMMARY:"):])
            elif line.startswith("LOCATION:"):
                current["location"] = unescape_ical(line[len("LOCATION:"):])
            elif line.startswith("DESCRIPTION:"):
                current["description"] = unescape_ical(line[len("DESCRIPTION:"):])
            elif line.startswith("STATUS:"):
                current["status"] = line[len("STATUS:"):]
    return events


def parse_dt(line: str) -> datetime:
    # Beispiel: DTSTART;TZID=Europe/Berlin:20260717T073000
    value = line.split(":", 1)[1]
    return datetime.strptime(value, "%Y%m%dT%H%M%S")


def is_klausur(ev: dict) -> bool:
    return "[KA]" in ev.get("summary", "") or "[KA]" in ev.get("description", "")


def is_aufsicht(ev: dict) -> bool:
    # Gleiche Bedingung wie in format_event: Termine ohne SUMMARY sind Aufsichten.
    return not ev.get("summary")


def has_klasse(ev: dict, klassen: list[str]) -> bool:
    # Exakter Token-Vergleich, damit "ITA24a" nicht auf "ITA24ab" passt.
    tokens = {t.lower() for t in re.findall(r"[A-Za-z0-9]+", ev.get("summary", ""))}
    return any(k.lower() in tokens for k in klassen)


def format_event(ev: dict) -> str:
    start = ev["dtstart"].strftime("%H:%M")
    end = ev["dtend"].strftime("%H:%M") if "dtend" in ev else "?"
    summary = ev.get("summary")
    location = ev.get("location")
    if summary:
        label = summary
        if location:
            label += f" (Raum {location})"
    else:
        label = f"Aufsicht ({location})" if location else "Aufsicht"
    return f"  {start}–{end}  {label}"


def main() -> None:
    env_path = find_env_file(Path(__file__).resolve().parent)
    env_values = load_env_file(env_path)
    default_url = os.environ.get("WEBUNTIS_ICAL_URL") or env_values.get("WEBUNTIS_ICAL_URL")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        default=default_url,
        required=default_url is None,
        help="WebUntis iCal-Export-URL (Default: WEBUNTIS_ICAL_URL aus einer .env, die "
        "ausgehend vom Skript-Ordner nach oben gesucht wird)",
    )
    parser.add_argument("--from", dest="date_from", help="Startdatum YYYY-MM-DD")
    parser.add_argument("--to", dest="date_to", help="Enddatum YYYY-MM-DD")
    parser.add_argument("--days", type=int, help="Anzahl Tage ab heute (Alternative zu --from/--to)")
    parser.add_argument("--klausuren", action="store_true", help="Nur Klausuren ([KA]) anzeigen")
    parser.add_argument("--aufsichten", action="store_true", help="Nur Aufsichten anzeigen")
    parser.add_argument(
        "--klasse",
        action="append",
        help="Nur Termine dieser Klasse (z. B. ITA24a); mehrfach angebbar",
    )
    args = parser.parse_args()

    today = date.today()
    if args.date_from or args.date_to:
        start = date.fromisoformat(args.date_from) if args.date_from else today
        end = date.fromisoformat(args.date_to) if args.date_to else start
    else:
        days = args.days if args.days is not None else 7
        start = today
        end = today + timedelta(days=days)

    raw = fetch_ics(args.url)
    lines = unfold_lines(raw)
    events = parse_events(lines)

    by_day: dict[date, list[dict]] = {}
    for ev in events:
        d = ev["dtstart"].date()
        if not (start <= d <= end):
            continue
        if (args.klausuren or args.aufsichten) and not (
            (args.klausuren and is_klausur(ev)) or (args.aufsichten and is_aufsicht(ev))
        ):
            continue
        if args.klasse and not has_klasse(ev, args.klasse):
            continue
        by_day.setdefault(d, []).append(ev)

    if not by_day:
        if args.klausuren and args.aufsichten:
            what = "Klausuren oder Aufsichten"
        elif args.klausuren:
            what = "Klausuren"
        elif args.aufsichten:
            what = "Aufsichten"
        else:
            what = "Termine"
        if args.klasse:
            what += " für " + ", ".join(args.klasse)
        print(f"Keine {what} zwischen {start.isoformat()} und {end.isoformat()}.")
        return

    for d in sorted(by_day):
        day_events = sorted(by_day[d], key=lambda e: e["dtstart"])
        weekday = WEEKDAYS_DE[d.weekday()]
        print(f"{weekday} {d.strftime('%d.%m.%Y')}")
        for ev in day_events:
            print(format_event(ev))
        print()


if __name__ == "__main__":
    main()
