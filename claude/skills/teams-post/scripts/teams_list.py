#!/usr/bin/env python3
"""Listet Teams bzw. Kanäle eines Teams in Microsoft Teams auf, per chrome-agent (CDP).

Dient dazu, den exakten Team-/Kanalnamen zu ermitteln, wenn `teams_post.py` einen
ungenau angegebenen Namen nicht findet — reine Leseoperation, ändert nichts.

Voraussetzung: `chrome-agent` (https://github.com/captivus/chrome-agent) auf dem PATH.
Ist es nicht installiert, meldet das Skript das über Exit-Code 2 — dann laut
SKILL.md den Skill `setup-chrome-agent` verwenden.

Kalibriert gegen teams.cloud.microsoft (Fluent-UI-Team-Kacheln, ARIA-Baum für
Kanäle); andere Teams-Frontend-Versionen können abweichende Texte/Strukturen haben.
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


def wait_ready(instance: str, timeout: float = 20) -> None:
    wait_for(
        lambda: evaluate(instance, "document.readyState") == "complete",
        timeout=timeout,
        what="Seite (readyState complete)",
    )


def wait_for_login(instance: str, timeout: float) -> None:
    print("Warte auf manuellen Login im geöffneten Chrome-Fenster ...", file=sys.stderr)
    deadline = time.time() + timeout
    last_reminder = time.time()
    while time.time() < deadline:
        try:
            pos = find_leaf_by_text(instance, "Aktivität")
        except StepError:
            pos = None
        if pos:
            print("Login erkannt.", file=sys.stderr)
            return
        if time.time() - last_reminder > 30:
            print("... warte weiter auf Login ...", file=sys.stderr)
            last_reminder = time.time()
        time.sleep(1.5)
    raise StepError(f"Kein Login innerhalb von {timeout}s erkannt.")


def list_teams(instance: str) -> list[str]:
    expr = """
    (() => {
      const grid = document.querySelector('[data-tid="teams-grid-view"]');
      if (!grid) return null;
      const cards = [...grid.querySelectorAll('[role="group"][data-tid$="-team-card"]')];
      const names = cards.map(e => e.textContent.trim()).filter(Boolean);
      return names.length ? names : null;
    })()
    """
    return wait_for(lambda: evaluate(instance, expr), what="Team-Kacheln")


def list_channels(instance: str) -> list[str]:
    expr = """
    (() => {
      const items = [...document.querySelectorAll('[role="treeitem"][aria-level="2"]')];
      const names = items.map(e => e.textContent.trim()).filter(Boolean);
      return names.length ? names : null;
    })()
    """
    return wait_for(lambda: evaluate(instance, expr), what="Kanal-Liste")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--team", default=None,
        help="Team, dessen Kanäle aufgelistet werden. Ohne Angabe: listet alle Teams.",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--login-timeout", type=float, default=300)
    args = parser.parse_args()

    require_chrome_agent()

    instance = find_running_teams_instance()
    fresh_launch = instance is None
    if instance:
        print(f"Nutze bereits laufende chrome-agent-Instanz '{instance}'.", file=sys.stderr)
    else:
        print("Starte Chrome über chrome-agent ...", file=sys.stderr)
        instance = launch(args.profile_dir, args.port)
        print(f"Instanz '{instance}' gestartet.", file=sys.stderr)

    if fresh_launch:
        ca(instance, "Page.navigate", json.dumps({"url": args.base_url}))
        wait_ready(instance)
        wait_for_login(instance, args.login_timeout)

    print("Wechsle zur Team-Liste ...", file=sys.stderr)
    try:
        click_text(instance, "Alle Teams", what="Link 'Alle Teams'", timeout=5)
        time.sleep(0.5)
    except StepError:
        pass  # ggf. schon auf der Team-Liste

    if args.team:
        print(f"Öffne Team '{args.team}' ...", file=sys.stderr)
        click_text(instance, args.team, what=f"Team '{args.team}'")
        time.sleep(0.6)
        for name in list_channels(instance):
            print(name)
    else:
        for name in list_teams(instance):
            print(name)


if __name__ == "__main__":
    try:
        main()
    except StepError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        sys.exit(1)
