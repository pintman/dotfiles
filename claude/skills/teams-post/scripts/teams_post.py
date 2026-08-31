#!/usr/bin/env python3
"""Bereitet einen Beitrag (Betreff + Nachricht) in einem Microsoft-Teams-Kanal vor, per chrome-agent (CDP).

Füllt Betreff- und Nachrichtenfeld aus und stoppt dann bewusst — den
"Veröffentlichen"-Klick löst immer der Mensch selbst im geöffneten
Chrome-Fenster aus. Login übernimmt ebenfalls immer der Mensch; das Skript
gibt niemals Zugangsdaten ein.

Voraussetzung: `chrome-agent` (https://github.com/captivus/chrome-agent) auf dem PATH.
Ist es nicht installiert, meldet das Skript das über Exit-Code 2 — dann laut
SKILL.md den Skill `setup-chrome-agent` verwenden.

Kalibriert gegen teams.cloud.microsoft (Fluent-UI-Seitenleiste, CKEditor-
Nachrichtenfeld); andere Teams-Frontend-Versionen können abweichende
Texte/Strukturen haben.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_BASE_URL = "https://teams.cloud.microsoft/"
DEFAULT_PROFILE_DIR = Path.home() / ".claude" / "teams-post" / "chrome-profile"
DEFAULT_CHANNEL = "Allgemein"

CHROME_AGENT_MISSING_EXIT = 2


class StepError(Exception):
    """Ein Ablaufschritt konnte nicht ausgeführt werden (Element nicht gefunden o. Ä.)."""


def require_chrome_agent() -> str:
    path = shutil.which("chrome-agent")
    if path is None:
        print(
            "chrome-agent nicht gefunden. Bitte den setup-chrome-agent-Skill "
            "ausführen und danach erneut versuchen.",
            file=sys.stderr,
        )
        sys.exit(CHROME_AGENT_MISSING_EXIT)
    return path


def ca(*args: str, timeout: float = 30) -> str:
    result = subprocess.run(
        ["chrome-agent", *args], capture_output=True, text=True, timeout=timeout
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"chrome-agent {' '.join(args)} fehlgeschlagen: {result.stderr.strip()}"
        )
    return result.stdout


def ca_json(*args: str, timeout: float = 30) -> dict:
    out = ca(*args, timeout=timeout)
    return json.loads(out)


def find_running_teams_instance() -> str | None:
    try:
        data = ca_json("status", timeout=10)
    except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None
    for inst in data:
        for target in inst.get("targets", []):
            url = target.get("url", "")
            if "teams.microsoft.com" in url or "teams.cloud.microsoft" in url:
                return inst["name"]
    return None


def launch(profile_dir: Path, port: int | None) -> str:
    profile_dir.mkdir(parents=True, exist_ok=True)
    args = ["launch"]
    if port is not None:
        args += ["--port", str(port)]
    args += ["--", f"--user-data-dir={profile_dir}"]
    info = ca_json(*args, timeout=40)
    return info["name"]


def evaluate(instance: str, expression: str):
    out = ca_json(instance, "Runtime.evaluate", json.dumps({
        "expression": expression,
        "returnByValue": True,
        "awaitPromise": True,
    }))
    if "exceptionDetails" in out:
        raise StepError(f"JS-Fehler: {out['exceptionDetails']}")
    result = out.get("result", {})
    return result.get("value")


def click(instance: str, x: int, y: int) -> None:
    ca(instance, "Input.dispatchMouseEvent", json.dumps({
        "type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1,
    }))
    time.sleep(0.05)
    ca(instance, "Input.dispatchMouseEvent", json.dumps({
        "type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1,
    }))


def insert_text(instance: str, text: str) -> None:
    ca(instance, "Input.insertText", json.dumps({"text": text}))


def screenshot(instance: str, debug_dir: Path | None, name: str) -> None:
    if debug_dir is None:
        return
    debug_dir.mkdir(parents=True, exist_ok=True)
    out = ca_json(instance, "Page.captureScreenshot", '{"format":"png"}', timeout=20)
    import base64
    (debug_dir / f"{name}.png").write_bytes(base64.b64decode(out["data"]))


def wait_for(fn, timeout: float = 15, interval: float = 0.5, what: str = "Element"):
    deadline = time.time() + timeout
    last_err = None
    while time.time() < deadline:
        try:
            value = fn()
            if value:
                return value
        except StepError as exc:
            last_err = exc
        time.sleep(interval)
    raise StepError(f"{what} nicht gefunden (Timeout nach {timeout}s). {last_err or ''}")


def js_str(s: str) -> str:
    return json.dumps(s)


def find_leaf_by_text(instance: str, text: str, exact: bool = True):
    cmp = f"t === {js_str(text)}" if exact else f"t.includes({js_str(text)})"
    expr = f"""
    (() => {{
      const all = [...document.querySelectorAll('*')];
      const els = all.filter(e => e.children.length === 0 && (() => {{ const t = e.textContent.trim(); return {cmp}; }})());
      if (els.length === 0) return null;
      const e = els[0];
      const r = e.getBoundingClientRect();
      return {{x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)}};
    }})()
    """
    return evaluate(instance, expr)


def click_text(instance: str, text: str, what: str | None = None, timeout: float = 15):
    what = what or f"Element mit Text '{text}'"
    pos = wait_for(lambda: find_leaf_by_text(instance, text), timeout=timeout, what=what)
    click(instance, pos["x"], pos["y"])
    return pos


def find_by_selector(instance: str, selector: str):
    expr = f"""
    (() => {{
      const el = document.querySelector({js_str(selector)});
      if (!el) return null;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) return null;
      return {{x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)}};
    }})()
    """
    return evaluate(instance, expr)


def click_selector(instance: str, selector: str, what: str, timeout: float = 15):
    pos = wait_for(lambda: find_by_selector(instance, selector), timeout=timeout, what=what)
    click(instance, pos["x"], pos["y"])
    return pos


def wait_ready(instance: str, timeout: float = 20) -> None:
    wait_for(
        lambda: evaluate(instance, "document.readyState") == "complete",
        timeout=timeout,
        what="Seite (readyState complete)",
    )


def wait_for_login(instance: str, timeout: float) -> None:
    print("Warte auf manuellen Login im geöffneten Chrome-Fenster ...")
    deadline = time.time() + timeout
    last_reminder = time.time()
    while time.time() < deadline:
        try:
            pos = find_leaf_by_text(instance, "Aktivität")
        except StepError:
            pos = None
        if pos:
            print("Login erkannt.")
            return
        if time.time() - last_reminder > 30:
            print("... warte weiter auf Login ...")
            last_reminder = time.time()
        time.sleep(1.5)
    raise StepError(f"Kein Login innerhalb von {timeout}s erkannt.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--team", required=True, help="Teamname exakt wie in der Teams-Seitenleiste")
    parser.add_argument("--title", required=True, help="Text fürs Betreff-Feld")
    parser.add_argument("--content", required=True, help="Text fürs Nachrichtenfeld")
    parser.add_argument("--channel", default=DEFAULT_CHANNEL, help="Kanalname (Default: Allgemein)")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--login-timeout", type=float, default=300)
    parser.add_argument("--debug", action="store_true", help="Screenshots nach jedem Schritt speichern")
    parser.add_argument("--debug-dir", type=Path, default=Path("teams-post-debug"))
    args = parser.parse_args()

    debug_dir = args.debug_dir if args.debug else None

    require_chrome_agent()

    instance = find_running_teams_instance()
    fresh_launch = instance is None
    if instance:
        print(f"Nutze bereits laufende chrome-agent-Instanz '{instance}'.")
    else:
        print("Starte Chrome über chrome-agent ...")
        instance = launch(args.profile_dir, args.port)
        print(f"Instanz '{instance}' gestartet.")

    if fresh_launch:
        ca(instance, "Page.navigate", json.dumps({"url": args.base_url}))
        wait_ready(instance)
        wait_for_login(instance, args.login_timeout)

    screenshot(instance, debug_dir, "00_start")

    print("Wechsle zur Team-Liste ...")
    try:
        click_text(instance, "Alle Teams", what="Link 'Alle Teams'", timeout=5)
        time.sleep(0.5)
    except StepError:
        pass  # ggf. schon auf der Team-Liste
    screenshot(instance, debug_dir, "01_alle_teams")

    print(f"Öffne Team '{args.team}' ...")
    click_text(instance, args.team, what=f"Team '{args.team}'")
    time.sleep(0.6)
    screenshot(instance, debug_dir, "02_team_geoeffnet")

    print(f"Öffne Kanal '{args.channel}' ...")
    click_text(instance, args.channel, what=f"Kanal '{args.channel}'")
    time.sleep(0.6)
    screenshot(instance, debug_dir, "03_kanal_geoeffnet")

    print("Öffne Compose-Bereich ('In Kanal posten') ...")
    click_selector(
        instance, 'button[data-tid="compose-start-post"]', what="Button 'In Kanal posten'"
    )
    time.sleep(0.6)
    screenshot(instance, debug_dir, "04_compose_geoeffnet")

    print("Fülle Betreff-Feld ...")
    click_selector(
        instance, 'input[placeholder="Betreff hinzufügen"]', what="Betreff-Feld"
    )
    insert_text(instance, args.title)

    print("Fülle Nachrichtenfeld ...")
    click_selector(
        instance,
        'div[role="textbox"][aria-label="Nachricht eingeben"]',
        what="Nachrichtenfeld",
    )
    insert_text(instance, args.content)

    screenshot(instance, debug_dir, "05_entwurf_ausgefuellt")

    print()
    print("Entwurf ist ausgefüllt. Bitte im Chrome-Fenster prüfen und selbst auf")
    print("'Veröffentlichen' klicken — das übernimmt dieses Skript bewusst nicht.")
    print(f"(chrome-agent-Instanz: {instance}; schließen mit: chrome-agent stop {instance})")


if __name__ == "__main__":
    try:
        main()
    except StepError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        sys.exit(1)
