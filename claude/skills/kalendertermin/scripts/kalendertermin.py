#!/usr/bin/env python3
"""Kapselt die AppleScript/osascript-Aufrufe gegen Calendar.app als parametrisierte Subcommands.

Reines Python-Stdlib, kein pip install nötig. Führt osascript ohne Shell-Interpolation aus
(subprocess mit Skript-Text über stdin statt Shell-String) — Parameter brauchen daher nur
AppleScript-Escaping (Anführungszeichen/Backslash), kein Shell-Escaping.

Kalender werden ausschließlich per Namen referenziert (nie per `id`/`uid`) — das AppleEvent
für id/uid schlägt für alle Kalender fehl (bekannter Calendar.app-Bug). Datumsfelder werden
über einzelne `set year/month/day/hours/minutes/seconds of ...`-Zuweisungen gesetzt statt über
locale-abhängige `date "..."`-Strings.
"""

import argparse
import subprocess
import sys
from datetime import date, datetime, timedelta


def escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def run_applescript(script: str) -> str:
    result = subprocess.run(["osascript"], input=script, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(1)
    return result.stdout


def date_field_lines(varname: str, dt: datetime) -> list[str]:
    return [
        f"set {varname} to current date",
        f"set year of {varname} to {dt.year}",
        f"set month of {varname} to {dt.month}",
        f"set day of {varname} to {dt.day}",
        f"set hours of {varname} to {dt.hour}",
        f"set minutes of {varname} to {dt.minute}",
        f"set seconds of {varname} to 0",
    ]


def parse_datetime(value: str) -> datetime:
    try:
        if "T" in value:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M")
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        print(
            f"Ungültiges Datum/Uhrzeit-Format: {value!r} (erwartet YYYY-MM-DD oder YYYY-MM-DDTHH:MM)",
            file=sys.stderr,
        )
        sys.exit(1)


def cmd_add_event(args: argparse.Namespace) -> None:
    if args.allday and ("T" in args.start or (args.end and "T" in args.end)):
        print(
            "Bei --allday dürfen --start/--end keine Uhrzeit enthalten (nur YYYY-MM-DD).",
            file=sys.stderr,
        )
        sys.exit(1)

    start_dt = parse_datetime(args.start)
    if args.end:
        end_dt = parse_datetime(args.end)
    elif args.allday:
        end_dt = start_dt + timedelta(days=1)
    else:
        end_dt = start_dt + timedelta(hours=1)

    props = [f'summary:"{escape(args.title)}"', "start date:startDate", "end date:endDate"]
    if args.location:
        props.append(f'location:"{escape(args.location)}"')
    if args.description:
        props.append(f'description:"{escape(args.description)}"')
    if args.allday:
        props.append("allday event:true")

    lines = ['tell application "Calendar"', f'set targetCal to calendar "{escape(args.calendar)}"']
    lines += date_field_lines("startDate", start_dt)
    lines += date_field_lines("endDate", end_dt)
    lines.append(
        f"make new event at end of events of targetCal with properties {{{', '.join(props)}}}"
    )
    lines.append("end tell")
    script = "\n".join(lines)

    run_applescript(script)
    kind = "ganztägig" if args.allday else f"{start_dt.strftime('%H:%M')}–{end_dt.strftime('%H:%M')}"
    print(
        f"Termin angelegt: \"{args.title}\" im Kalender \"{args.calendar}\", "
        f"{start_dt.strftime('%d.%m.%Y')} ({kind})"
        + (f", Ort: {args.location}" if args.location else "")
    )


def cmd_query_events(args: argparse.Namespace) -> None:
    start = date.fromisoformat(args.date_from)
    end = date.fromisoformat(args.date_to) if args.date_to else start + timedelta(days=7)
    range_start = datetime.combine(start, datetime.min.time())
    range_end = datetime.combine(end, datetime.min.time()) + timedelta(days=1)

    whose = "start date ≥ rangeStart and start date < rangeEnd"
    if args.keyword:
        whose += f' and summary contains "{escape(args.keyword)}"'

    lines = ['tell application "Calendar"']
    lines += date_field_lines("rangeStart", range_start)
    lines += date_field_lines("rangeEnd", range_end)
    lines.append('set ausgabe to ""')

    entry_line = (
        'set ausgabe to ausgabe & (name of cal) & ": " & (summary of e) & " | " & '
        '(start date of e as string) & " – " & (end date of e as string) & " | " & '
        "(my locOrNone(location of e)) & linefeed"
    )
    if args.calendar:
        lines.append(f'set cal to calendar "{escape(args.calendar)}"')
        lines.append(f"repeat with e in (every event of cal whose {whose})")
        lines.append(entry_line)
        lines.append("end repeat")
    else:
        lines.append("repeat with cal in calendars")
        lines.append(f"repeat with e in (every event of cal whose {whose})")
        lines.append(entry_line)
        lines.append("end repeat")
        lines.append("end repeat")

    lines.append("return ausgabe")
    lines.append("end tell")
    lines.append("")
    lines.append("on locOrNone(loc)")
    lines.append("if loc is missing value then")
    lines.append('return "kein Ort"')
    lines.append("else")
    lines.append("return loc")
    lines.append("end if")
    lines.append("end locOrNone")
    script = "\n".join(lines)

    output = run_applescript(script).strip()
    if not output:
        print(f"Keine Termine zwischen {start.isoformat()} und {end.isoformat()}.")
        return
    print(output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add-event", help="Termin im Apple Kalender anlegen")
    p.add_argument("--calendar", required=True, help="Kalendername (exakt, per Namen referenziert)")
    p.add_argument("--title", required=True)
    p.add_argument("--start", required=True, help="YYYY-MM-DD oder YYYY-MM-DDTHH:MM")
    p.add_argument(
        "--end",
        help="YYYY-MM-DD oder YYYY-MM-DDTHH:MM (Default: +1h, bei --allday +1 Tag; "
        "bei --allday ist das Enddatum exklusiv)",
    )
    p.add_argument("--location")
    p.add_argument("--description")
    p.add_argument("--allday", action="store_true")

    p = sub.add_parser("query-events", help="Termine in einem Zeitraum abfragen")
    p.add_argument("--from", dest="date_from", required=True, help="YYYY-MM-DD")
    p.add_argument("--to", dest="date_to", help="YYYY-MM-DD, inklusiv (Default: --from + 7 Tage)")
    p.add_argument("--calendar", help="Nur diesen Kalender durchsuchen (Default: alle Kalender)")
    p.add_argument("--keyword", help="Nur Termine, deren Titel dieses Stichwort enthält")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    commands = {"add-event": cmd_add_event, "query-events": cmd_query_events}
    commands[args.command](args)


if __name__ == "__main__":
    main()
