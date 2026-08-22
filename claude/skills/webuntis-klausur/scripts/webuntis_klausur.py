#!/usr/bin/env python3
"""Legt eine Prüfung (Klassenarbeit/Sonstige Leistung) in WebUntis an, per chrome-agent (CDP).

Füllt das Prüfungsformular bis kurz vor dem Speichern aus und stoppt dann bewusst —
den "Speichern"-Klick löst immer der Mensch selbst im geöffneten Chrome-Fenster aus.
Login übernimmt ebenfalls immer der Mensch; das Skript gibt niemals Zugangsdaten ein.

Voraussetzung: `chrome-agent` (https://github.com/captivus/chrome-agent) auf dem PATH.
Ist es nicht installiert, meldet das Skript das über Exit-Code 2 — dann greift laut
SKILL.md der alte claude-in-chrome-Ablauf.

Kalibriert gegen tbs1.webuntis.com (Ant-Design-Frontend); andere WebUntis-Instanzen
können abweichende Texte/Strukturen haben.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

DEFAULT_BASE_URL = "https://tbs1.webuntis.com"
DEFAULT_PROFILE_DIR = Path.home() / ".claude" / "webuntis-klausur" / "chrome-profile"
EXAM_TYPES = ["Klassenarbeit", "Sonstige Leistung"]

CHROME_AGENT_MISSING_EXIT = 2


class StepError(Exception):
    """Ein Ablaufschritt konnte nicht ausgeführt werden (Element nicht gefunden o. Ä.)."""


def require_chrome_agent() -> str:
    path = shutil.which("chrome-agent")
    if path is None:
        print(
            "chrome-agent nicht gefunden. Bitte den claude-in-chrome-Ablauf aus "
            "SKILL.md verwenden.",
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


def find_running_webuntis_instance() -> str | None:
    try:
        data = ca_json("status", timeout=10)
    except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None
    for inst in data:
        for target in inst.get("targets", []):
            if "webuntis.com" in target.get("url", ""):
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


def find_row_field(instance: str, label_text: str):
    expr = f"""
    (() => {{
      const LABEL = {js_str(label_text)};
      const all = [...document.querySelectorAll('*')];
      const labelEl = all.find(e => e.children.length === 0 && e.textContent.trim() === LABEL);
      if (!labelEl) return null;
      const lr = labelEl.getBoundingClientRect();
      const candidates = all.filter(e => {{
        if (e === labelEl) return false;
        const tag = e.tagName;
        const cls = (e.className && e.className.toString) ? e.className.toString() : '';
        const isField = tag === 'INPUT' || tag === 'TEXTAREA' || cls.includes('ant-select-selector') || cls.includes('ant-picker') || tag === 'BUTTON';
        if (!isField) return false;
        const r = e.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return false;
        return Math.abs((r.top + r.height/2) - (lr.top + lr.height/2)) < 20 && r.left > lr.right;
      }});
      candidates.sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left);
      const best = candidates[0];
      if (!best) return null;
      const r = best.getBoundingClientRect();
      return {{x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)}};
    }})()
    """
    return evaluate(instance, expr)


def set_input_by_id(instance: str, element_id: str, value: str) -> bool:
    expr = f"""
    (() => {{
      const el = document.getElementById({js_str(element_id)});
      if (!el) return false;
      const proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
      const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
      setter.call(el, {js_str(value)});
      el.dispatchEvent(new Event('input', {{bubbles: true}}));
      el.dispatchEvent(new Event('change', {{bubbles: true}}));
      return true;
    }})()
    """
    return bool(evaluate(instance, expr))


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
            pos = find_leaf_by_text(instance, "Stundenplan")
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


def school_year_label(d: date) -> str:
    start_year = d.year if d.month >= 8 else d.year - 1
    return f"{start_year}/{start_year + 1}"


def ensure_school_year(instance: str, target: date, debug_dir: Path | None) -> None:
    desired = school_year_label(target)
    expr = """
    (() => {
      const all = [...document.querySelectorAll('*')];
      const el = all.find(e => e.children.length === 0 && /^(Schuljahr N\\/A|\\d{4}\\/\\d{4})$/.test(e.textContent.trim()));
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return {text: el.textContent.trim(), x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)};
    })()
    """
    current = wait_for(lambda: evaluate(instance, expr), what="Schuljahr-Dropdown")
    if current["text"] == desired:
        return
    print(f"Stelle Schuljahr auf {desired} um (aktuell: {current['text']}) ...")
    click(instance, current["x"], current["y"])
    screenshot(instance, debug_dir, "schuljahr_dropdown")
    click_text(instance, desired, what=f"Schuljahr-Option '{desired}'")
    time.sleep(0.8)


def read_week_range(instance: str):
    expr = """
    (() => {
      const wrap = document.querySelector('.date-picker-with-arrows');
      if (!wrap) return null;
      const span = wrap.querySelector('.date-text');
      const buttons = [...wrap.querySelectorAll('button')];
      if (!span || buttons.length < 2) return null;
      const pr = buttons[0].getBoundingClientRect();
      const nr = buttons[buttons.length - 1].getBoundingClientRect();
      return {
        text: span.textContent.trim(),
        prev: {x: Math.round(pr.left + pr.width/2), y: Math.round(pr.top + pr.height/2)},
        next: {x: Math.round(nr.left + nr.width/2), y: Math.round(nr.top + nr.height/2)},
      };
    })()
    """
    return wait_for(lambda: evaluate(instance, expr), what="Wochen-Datumsanzeige")


def parse_week_start(range_text: str) -> date:
    # Format: "07. 09. - 13. 09. 2026" (WebUntis rendert mit Leerzeichen nach den Punkten).
    start_part, end_part = [p.strip() for p in range_text.split("-")]
    end_nums = [int(n) for n in end_part.replace(".", " ").split()]
    start_nums = [int(n) for n in start_part.replace(".", " ").split()]
    end_day, end_month, end_year = end_nums
    start_day, start_month = start_nums
    start_year = end_year if start_month <= end_month else end_year - 1
    return date(start_year, start_month, start_day)


def navigate_to_week(instance: str, target: date, debug_dir: Path | None) -> None:
    target_monday = target - timedelta(days=target.weekday())
    for _ in range(60):
        info = read_week_range(instance)
        current_monday = parse_week_start(info["text"])
        diff_weeks = (target_monday - current_monday).days // 7
        if diff_weeks == 0:
            return
        pos = info["next"] if diff_weeks > 0 else info["prev"]
        click(instance, pos["x"], pos["y"])
        time.sleep(0.6)
    screenshot(instance, debug_dir, "week_nav_failed")
    raise StepError(f"Zielwoche für {target.isoformat()} nach 60 Klicks nicht erreicht.")


def find_lesson_block(instance: str, target: date, klasse: str, fach: str):
    day_text = target.strftime("%d.%m.")
    expr = f"""
    (() => {{
      const DAY = {js_str(day_text)};
      const KLASSE = {js_str(klasse)};
      const FACH = {js_str(fach)};
      const all = [...document.querySelectorAll('*')];
      const headers = all.filter(e => e.children.length === 0 && /^\\w{{2}}\\s\\d{{2}}\\.\\d{{2}}\\.$/.test(e.textContent.trim()));
      const header = headers.find(e => e.textContent.trim().endsWith(DAY));
      if (!header) return {{error: 'header-not-found', headers: headers.map(h => h.textContent.trim())}};
      const hr = header.getBoundingClientRect();
      const xMin = hr.left - 20, xMax = hr.right + 20;
      const blocks = all.filter(e => {{
        const r = e.getBoundingClientRect();
        if (r.width < 30 || r.height < 20) return false;
        if (r.left < xMin || r.left > xMax) return false;
        const t = e.textContent;
        return t.includes(KLASSE) && t.includes(FACH);
      }});
      if (blocks.length === 0) return {{error: 'block-not-found'}};
      // textContent wird an Vorfahren vererbt -- Container, die einen anderen Treffer
      // umschließen, sind kein eigener Block, sondern Verschachtelungsrauschen.
      const leafBlocks = blocks.filter(b => !blocks.some(other => other !== b && b.contains(other)));
      leafBlocks.sort((a, b) => {{
        const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        return (ra.width * ra.height) - (rb.width * rb.height);
      }});
      const best = leafBlocks[0];
      const r = best.getBoundingClientRect();
      return {{
        x: Math.round(r.left + r.width / 2),
        y: Math.round(r.top + r.height / 2),
        text: best.textContent.trim(),
        matchCount: leafBlocks.length,
      }};
    }})()
    """
    return evaluate(instance, expr)


def select_pruefungsart(instance: str, exam_type: str, debug_dir: Path | None) -> None:
    trigger = wait_for(
        lambda: find_row_field(instance, "Prüfungsart"),
        what="Prüfungsart-Feld",
    )
    click(instance, trigger["x"], trigger["y"])
    screenshot(instance, debug_dir, "pruefungsart_dropdown")
    click_text(instance, exam_type, what=f"Prüfungsart-Option '{exam_type}'")
    time.sleep(0.3)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="Klausurdatum YYYY-MM-DD")
    parser.add_argument("--klasse", required=True, help="Klassenkürzel wie im Stundenplan, z. B. ITF25a")
    parser.add_argument("--fach", required=True, help="Fachkürzel wie im Stundenplan, z. B. IT_LF08")
    parser.add_argument("--type", choices=EXAM_TYPES, default="Klassenarbeit", help="Prüfungsart")
    parser.add_argument("--title", default=None, help="Optionaler Titel fürs Name-Feld")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--login-timeout", type=float, default=300)
    parser.add_argument("--debug", action="store_true", help="Screenshots nach jedem Schritt speichern")
    parser.add_argument("--debug-dir", type=Path, default=Path("webuntis-klausur-debug"))
    args = parser.parse_args()

    target = date.fromisoformat(args.date)
    debug_dir = args.debug_dir if args.debug else None

    require_chrome_agent()

    instance = find_running_webuntis_instance()
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

    print("Öffne Stundenplan → Mein Stundenplan ...")
    click_text(instance, "Stundenplan", what="Menüpunkt 'Stundenplan'")
    time.sleep(0.6)
    click_text(instance, "Mein Stundenplan", what="Menüpunkt 'Mein Stundenplan'")
    time.sleep(0.6)
    screenshot(instance, debug_dir, "01_mein_stundenplan")

    ensure_school_year(instance, target, debug_dir)
    screenshot(instance, debug_dir, "02_schuljahr")

    print(f"Navigiere zur Woche von {target.isoformat()} ...")
    navigate_to_week(instance, target, debug_dir)
    screenshot(instance, debug_dir, "03_zielwoche")

    print(f"Suche Stunde {args.klasse} / {args.fach} am {target.isoformat()} ...")
    block = wait_for(
        lambda: find_lesson_block(instance, target, args.klasse, args.fach) or None,
        what="Stundenblock",
    )
    if block.get("error"):
        screenshot(instance, debug_dir, "block_not_found")
        raise StepError(
            f"Stundenblock nicht gefunden ({block['error']}). "
            f"Verfügbare Tagesköpfe: {block.get('headers')}"
        )
    if block.get("matchCount", 1) > 1:
        print(
            f"Achtung: {block['matchCount']} passende Blöcke gefunden, nehme den kleinsten "
            f"('{block['text']}'). Bitte vor dem Speichern prüfen."
        )
    click(instance, block["x"], block["y"])
    time.sleep(0.8)
    screenshot(instance, debug_dir, "04_stunde_geoeffnet")

    print("Wechsle zu Tab 'Details' ...")
    click_text(instance, "Details", what="Tab 'Details'")
    time.sleep(0.5)
    screenshot(instance, debug_dir, "05_details_tab")

    print("Klicke 'Prüfung erstellen' ...")
    click_text(instance, "Prüfung erstellen", what="Button 'Prüfung erstellen'")
    time.sleep(0.8)
    wait_for(lambda: find_leaf_by_text(instance, "Prüfungsart"), what="Prüfungsformular")
    screenshot(instance, debug_dir, "06_pruefungsformular")

    print(f"Setze Prüfungsart auf '{args.type}' ...")
    select_pruefungsart(instance, args.type, debug_dir)

    if args.title:
        print(f"Setze Name-Feld auf '{args.title}' ...")
        if not set_input_by_id(instance, "name", args.title):
            field = wait_for(lambda: find_row_field(instance, "Name"), what="Name-Feld")
            click(instance, field["x"], field["y"])
            raise StepError(
                "input#name nicht gefunden — Feld wurde fokussiert, bitte Titel manuell eintragen."
            )

    screenshot(instance, debug_dir, "07_formular_ausgefuellt")

    print()
    print("Formular ist ausgefüllt. Bitte im Chrome-Fenster prüfen und selbst auf")
    print("'Speichern' klicken — das übernimmt dieses Skript bewusst nicht.")
    print(f"(chrome-agent-Instanz: {instance}; schließen mit: chrome-agent stop {instance})")


if __name__ == "__main__":
    try:
        main()
    except StepError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        sys.exit(1)
