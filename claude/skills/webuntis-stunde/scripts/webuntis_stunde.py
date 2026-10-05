#!/usr/bin/env python3
"""Öffnet eine Unterrichtsstunde im WebUntis-Stundenplan und liest die Schülerliste aus dem
Klassenbuch-Tab aus, per chrome-agent (CDP). Rein lesend: es wird nichts gespeichert oder
geändert. Login übernimmt immer der Mensch; das Skript gibt niemals Zugangsdaten ein.

Klickpfad: Heute → Stundenplan → Mein Stundenplan → Zielwoche → Stundenblock →
Tab "Klassenbuch" → "Schüler*innen im Unterricht". Der Weg über Klassenbuch → Abwesenheiten
taugt dafür nicht, weil dessen Klassenfilter nur die eigenen Klassen anbietet.

Voraussetzung: `chrome-agent` (https://github.com/captivus/chrome-agent) auf dem PATH
(sonst Exit-Code 2).

Kalibriert gegen tbs1.webuntis.com; die Schülerkacheln liegen in einem <iframe>.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

DEFAULT_BASE_URL = "https://tbs1.webuntis.com"
DEFAULT_PROFILE_DIR = Path.home() / ".claude" / "webuntis-stunde" / "chrome-profile"

CHROME_AGENT_MISSING_EXIT = 2


class StepError(Exception):
    """Ein Ablaufschritt konnte nicht ausgeführt werden (Element nicht gefunden o. Ä.)."""


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def require_chrome_agent() -> str:
    path = shutil.which("chrome-agent")
    if path is None:
        print("chrome-agent nicht gefunden. Skill `setup-chrome-agent` verwenden.", file=sys.stderr)
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
            pos = find_leaf_by_text(instance, "Stundenplan")
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
    print(f"Stelle Schuljahr auf {desired} um (aktuell: {current['text']}) ...", file=sys.stderr)
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


def pick_lesson_block(instance: str, target: date, klasse: str, fach: str | None, index: int):
    """Sucht alle Stundenblöcke der Klasse (und ggf. des Fachs) in der Tagesspalte, sortiert
    sie chronologisch (nach vertikaler Position), markiert den gewünschten, scrollt ihn ins
    Bild und liefert seine Klickkoordinaten. Ohne Scrollen liegen frühe Blöcke ggf. außerhalb
    des sichtbaren Bereichs."""
    day_text = target.strftime("%d.%m.")
    expr = f"""
    (() => {{
      const DAY = {js_str(day_text)};
      const KLASSE = {js_str(klasse)};
      const FACH = {js_str(fach or "")};
      const INDEX = {index};
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
        return t.includes(KLASSE) && (!FACH || t.includes(FACH));
      }});
      // textContent wird an Vorfahren vererbt -- Container, die einen anderen Treffer
      // umschließen, sind kein eigener Block, sondern Verschachtelungsrauschen.
      let leafBlocks = blocks.filter(b => !blocks.some(other => other !== b && b.contains(other)));
      if (leafBlocks.length === 0) return {{error: 'block-not-found'}};
      // Entfallene Stunden sind durchgestrichen und haben keinen Klassenbuch-Tab -- überspringen.
      const cancelled = b => [b, ...b.querySelectorAll('*')].some(e => getComputedStyle(e).textDecorationLine.includes('line-through'));
      const active = leafBlocks.filter(b => !cancelled(b));
      const skipped = leafBlocks.length - active.length;
      if (active.length === 0) return {{error: 'nur-entfallene-stunden', matchCount: leafBlocks.length}};
      leafBlocks = active;
      leafBlocks.sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
      if (INDEX >= leafBlocks.length) return {{error: 'index-out-of-range', matchCount: leafBlocks.length}};
      const best = leafBlocks[INDEX];
      best.scrollIntoView({{block: 'center'}});
      const r = best.getBoundingClientRect();
      return {{
        x: Math.round(r.left + r.width / 2),
        y: Math.round(r.top + r.height / 2),
        text: best.innerText.trim().replace(/\\s+/g, ' '),
        matchCount: leafBlocks.length,
        skipped,
      }};
    }})()
    """
    return evaluate(instance, expr)


READ_LESSON_JS = """
(() => {
  const main = document.body.innerText.split('\\n').map(s => s.trim()).filter(Boolean);
  // Kopf: Klassen, Gruppe, Fach, [Banner wie "ZUSÄTZLICHER UNTERRICHT"], Wochentag, Datum,
  // Zeit, Raum, Lehrkraft, dann Tab "Klassenbuch". Verankert am Datum, Banner (Großbuchstaben
  // mit Leerzeichen) werden übersprungen.
  let header = null;
  for (let i = main.length - 2; i >= 8; i--) {
    if (main[i] === 'Klassenbuch' && main[i + 1].startsWith('Detail')) {
      const d = i - 4;
      if (!/^\\d{1,2}\\.\\d{1,2}\\.\\d{4}$/.test(main[d])) break;
      let j = d - 2;
      const banner = [];
      while (j > 0 && /^[A-ZÄÖÜ]+( [A-ZÄÖÜ]+)+$/.test(main[j])) banner.unshift(main[j--]);
      header = {
        klassen: main[j - 2], gruppe: main[j - 1], fach: main[j],
        hinweis: banner.join(' '), wochentag: main[d - 1], datum: main[d],
        zeit: main[d + 1], raum: main[d + 2], lehrkraft: main[d + 3],
      };
      break;
    }
  }
  for (const f of document.querySelectorAll('iframe')) {
    let text;
    try { text = f.contentDocument.body.innerText; } catch (e) { continue; }
    const lines = text.split('\\n').map(s => s.trim()).filter(Boolean);
    const s = lines.indexOf('Auswahl löschen');
    if (s < 0) continue;
    const e = lines.indexOf('abwesend', s);
    const ci = lines.findIndex(l => l.startsWith('Schüler*innen im Unterricht'));
    let count = null;
    if (ci >= 0) {
      const m = (lines[ci] + ' ' + (lines[ci + 1] || '')).match(/Unterricht\\s*(\\d+)/);
      if (m) count = parseInt(m[1], 10);
    }
    return {header, count, tiles: lines.slice(s + 1, e < 0 ? undefined : e)};
  }
  return {header, count: null, tiles: null};
})()
"""


def read_lesson(instance: str) -> dict:
    data = wait_for(
        lambda: (lambda d: d if d and d.get("tiles") is not None else None)(evaluate(instance, READ_LESSON_JS)),
        timeout=20,
        what="Schülerliste im Klassenbuch-Tab",
    )
    tiles = data["tiles"]
    if len(tiles) % 2 != 0:
        raise StepError(
            f"Unerwartetes Kachelformat (ungerade Zeilenzahl {len(tiles)}): {tiles[:6]} ..."
        )
    students = [f"{tiles[i]}, {tiles[i + 1]}" for i in range(0, len(tiles), 2)]
    header = data.get("header")
    if header:
        # Mehrere Klassen kommen ohne Trenner an ("ITA24aITA24b").
        header["klassen"] = re.sub(r"(?<=[a-z0-9])(?=[A-Z]{2,})", ", ", header.get("klassen", ""))
    if data.get("count") is not None and data["count"] != len(students):
        print(
            f"Achtung: WebUntis meldet {data['count']} Schüler*innen, ausgelesen wurden "
            f"{len(students)}.",
            file=sys.stderr,
        )
    return {"header": header, "count": data.get("count"), "students": students}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="Datum der Stunde YYYY-MM-DD")
    parser.add_argument("--klasse", required=True, help="Klassenkürzel wie im Stundenplan, z. B. ITA24a")
    parser.add_argument("--fach", default=None, help="Optionales Fachkürzel, z. B. ITA_PROJ")
    parser.add_argument("--index", type=int, default=0,
                        help="Bei mehreren passenden Blöcken am Tag: 0 = frühester (Default), 1 = zweiter ...")
    parser.add_argument("--json", action="store_true", help="Ergebnis als JSON ausgeben")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--login-timeout", type=float, default=300)
    parser.add_argument("--debug", action="store_true", help="Screenshots nach jedem Schritt speichern")
    parser.add_argument("--debug-dir", type=Path, default=Path("webuntis-stunde-debug"))
    args = parser.parse_args()

    target = date.fromisoformat(args.date)
    debug_dir = args.debug_dir if args.debug else None

    require_chrome_agent()

    instance = find_running_webuntis_instance()
    if instance:
        log(f"Nutze bereits laufende chrome-agent-Instanz '{instance}'.")
    else:
        log("Starte Chrome über chrome-agent ...")
        instance = launch(args.profile_dir, args.port)
        log(f"Instanz '{instance}' gestartet.")

    # Immer über die Startseite einsteigen: aus Untermenüs (z. B. Klassenbuch) heraus ist
    # "Stundenplan" sonst nicht direkt anklickbar.
    ca(instance, "Page.navigate", json.dumps({"url": f"{args.base_url}/today"}))
    wait_ready(instance)
    wait_for_login(instance, args.login_timeout)
    screenshot(instance, debug_dir, "00_start")

    log("Öffne Stundenplan → Mein Stundenplan ...")
    click_text(instance, "Stundenplan", what="Menüpunkt 'Stundenplan'")
    time.sleep(0.6)
    click_text(instance, "Mein Stundenplan", what="Menüpunkt 'Mein Stundenplan'")
    time.sleep(0.8)
    screenshot(instance, debug_dir, "01_mein_stundenplan")

    ensure_school_year(instance, target, debug_dir)

    log(f"Navigiere zur Woche von {target.isoformat()} ...")
    navigate_to_week(instance, target, debug_dir)
    time.sleep(0.5)
    screenshot(instance, debug_dir, "02_zielwoche")

    what = args.klasse + (f" / {args.fach}" if args.fach else "")
    log(f"Suche Stunde {what} am {target.isoformat()} ...")
    block = wait_for(
        lambda: pick_lesson_block(instance, target, args.klasse, args.fach, args.index) or None,
        what="Stundenblock",
    )
    if block.get("error"):
        screenshot(instance, debug_dir, "block_not_found")
        raise StepError(
            f"Stundenblock nicht gefunden ({block['error']}, Treffer: {block.get('matchCount', 0)}). "
            f"Verfügbare Tagesköpfe: {block.get('headers')}"
        )
    if block.get("skipped"):
        log(f"Hinweis: {block['skipped']} entfallene Stunde(n) übersprungen.")
    if block["matchCount"] > 1:
        log(
            f"Hinweis: {block['matchCount']} passende Blöcke am Tag, öffne Nr. {args.index} "
            f"(0 = frühester). Andere per --index wählen."
        )
    time.sleep(0.4)
    # Nach scrollIntoView Position neu bestimmen.
    block = pick_lesson_block(instance, target, args.klasse, args.fach, args.index)
    click(instance, block["x"], block["y"])
    time.sleep(1.5)
    screenshot(instance, debug_dir, "03_stunde_geoeffnet")

    lesson = read_lesson(instance)
    lesson["url"] = evaluate(instance, "location.href")

    if args.json:
        print(json.dumps(lesson, ensure_ascii=False, indent=2))
        return

    h = lesson["header"]
    if h:
        print(f"{h.get('klassen')} | {h.get('fach')} | {h.get('wochentag')} {h.get('datum')} "
              f"{h.get('zeit')} | Raum {h.get('raum')} | {h.get('lehrkraft')}"
              + (f" | {h['hinweis']}" if h.get("hinweis") else ""))
    print(f"Schüler*innen: {len(lesson['students'])}")
    for i, name in enumerate(lesson["students"], 1):
        print(f"{i:2}. {name}")
    log(f"(Stunde bleibt geöffnet; Instanz: {instance})")


if __name__ == "__main__":
    try:
        main()
    except StepError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        sys.exit(1)
