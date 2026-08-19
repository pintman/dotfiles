#!/usr/bin/env python3
"""Kapselt die AppleScript/osascript-Aufrufe gegen Mail.app als parametrisierte Subcommands.

Reines Python-Stdlib, kein pip install nötig. Übergibt das AppleScript-Skript über stdin an
osascript statt über einen Shell-String — Account-/Mailbox-/Suchbegriff-Parameter brauchen
daher nur AppleScript-Escaping (Anführungszeichen/Backslash), kein Shell-Escaping.
"""

import argparse
import subprocess
import sys
import time


def escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def run_applescript(script: str) -> str:
    result = subprocess.run(
        ["osascript"], input=script, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(1)
    return result.stdout


def cmd_list_accounts(args: argparse.Namespace) -> None:
    script = """
tell application "Mail"
    set output to ""
    repeat with acc in accounts
        set output to output & (name of acc) & " | " & (email addresses of acc) & linefeed
    end repeat
    return output
end tell
"""
    sys.stdout.write(run_applescript(script))


def cmd_list_mailboxes(args: argparse.Namespace) -> None:
    script = f"""
tell application "Mail"
    set theAccount to account "{escape(args.account)}"
    set output to ""
    repeat with mb in mailboxes of theAccount
        set output to output & (name of mb) & linefeed
    end repeat
    return output
end tell
"""
    sys.stdout.write(run_applescript(script))


def _found_messages_block(args: argparse.Namespace) -> str:
    return f"""
    set theAccount to account "{escape(args.account)}"
    set theBox to mailbox "{escape(args.mailbox)}" of theAccount
    set foundMsgs to (messages of theBox whose subject contains "{escape(args.query)}")
"""


def cmd_search(args: argparse.Namespace) -> None:
    script = f"""
tell application "Mail"
{_found_messages_block(args)}
    if (count of foundMsgs) = 0 then return "Keine Treffer."
    set output to ""
    set n to 0
    repeat with m in foundMsgs
        set n to n + 1
        set output to output & n & ". Von: " & (sender of m) & linefeed
        set output to output & "   Betreff: " & (subject of m) & linefeed
        set output to output & "   Datum: " & (date received of m) & linefeed
    end repeat
    return output
end tell
"""
    sys.stdout.write(run_applescript(script))


def cmd_read(args: argparse.Namespace) -> None:
    script = f"""
tell application "Mail"
{_found_messages_block(args)}
    if (count of foundMsgs) < {args.index} then return "Kein Treffer mit Index {args.index}."
    set m to item {args.index} of foundMsgs
    return (content of m)
end tell
"""
    sys.stdout.write(run_applescript(script))


def cmd_reply(args: argparse.Namespace) -> None:
    # `content` einer Antwort NICHT per AppleScript-Property setzen: Mail.app füllt den
    # zitierten Text im WebView-Editor asynchron nach und überschreibt dabei gesetzten
    # Inhalt wieder (bekannte, nicht per delay behebbare Einschränkung). Deshalb wird das
    # Fenster nur geöffnet (Cursor steht bereits richtig) und optional per System
    # Events/keystroke getippt.
    open_script = f"""
tell application "Mail"
{_found_messages_block(args)}
    if (count of foundMsgs) < {args.index} then return "Kein Treffer mit Index {args.index}."
    set m to item {args.index} of foundMsgs
    reply m with opening window
    return "Antwortfenster geöffnet."
end tell
"""
    sys.stdout.write(run_applescript(open_script))

    if args.text:
        # Erfordert Bedienungshilfen-Berechtigung für den Prozess, der osascript ausführt.
        time.sleep(1.5)
        run_applescript('tell application "Mail" to activate')
        time.sleep(0.5)
        # Zeilenumbrüche im Text als eigene "key code 36" (Return) senden statt sie roh in
        # den AppleScript-String-Literal einzubetten (dort syntaktisch nicht zulässig).
        statements = []
        for i, line in enumerate(args.text.split("\n")):
            if i > 0:
                statements.append("key code 36")
            statements.append(f'keystroke "{escape(line)}"')
        type_script = 'tell application "System Events"\n    ' + "\n    ".join(statements) + "\nend tell"
        run_applescript(type_script)
        print("Text eingetippt (falls Bedienungshilfen-Berechtigung erteilt ist).")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-accounts", help="Accounts mit Name und E-Mail-Adresse auflisten")

    p = sub.add_parser("list-mailboxes", help="Mailbox-Namen eines Accounts auflisten")
    p.add_argument("--account", required=True, help="Account-Name (aus list-accounts)")

    p = sub.add_parser("search", help="Mails mit Betreff-Treffer in einer Mailbox suchen")
    p.add_argument("--account", required=True)
    p.add_argument("--mailbox", required=True, help="Mailbox-Name (aus list-mailboxes)")
    p.add_argument("--query", required=True, help="Suchbegriff (Teilstring im Betreff)")

    p = sub.add_parser("read", help="Inhalt einer per search gefundenen Mail ausgeben")
    p.add_argument("--account", required=True)
    p.add_argument("--mailbox", required=True)
    p.add_argument("--query", required=True)
    p.add_argument("--index", type=int, default=1, help="1-basierter Treffer-Index (Default: 1)")

    p = sub.add_parser(
        "reply", help="Antwort-Entwurf öffnen (nie senden), optional Text eintippen"
    )
    p.add_argument("--account", required=True)
    p.add_argument("--mailbox", required=True)
    p.add_argument("--query", required=True)
    p.add_argument("--index", type=int, default=1, help="1-basierter Treffer-Index (Default: 1)")
    p.add_argument(
        "--text",
        help="Optional: Antworttext per System Events eintippen (Bedienungshilfen-Berechtigung nötig)",
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()
    commands = {
        "list-accounts": cmd_list_accounts,
        "list-mailboxes": cmd_list_mailboxes,
        "search": cmd_search,
        "read": cmd_read,
        "reply": cmd_reply,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
