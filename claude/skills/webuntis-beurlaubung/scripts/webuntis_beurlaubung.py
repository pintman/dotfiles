#!/usr/bin/env python3
"""Bereitet eine Beurlaubung (Abwesenheitseintrag) für einen oder mehrere Schüler in
WebUntis vor, per chrome-agent (CDP). Füllt das Formular bis kurz vor dem Speichern
aus und stoppt dann bewusst — den "Speichern"-Klick löst immer der Mensch selbst im
geöffneten Chrome-Fenster aus. Login übernimmt ebenfalls immer der Mensch; das
Skript gibt niemals Zugangsdaten ein.

Voraussetzung: `chrome-agent` (https://github.com/captivus/chrome-agent) auf dem PATH.
Ist es nicht installiert, meldet das Skript das über Exit-Code 2 — dann greift laut
SKILL.md der alte claude-in-chrome-Ablauf.

Kalibriert gegen tbs1.webuntis.com: Klassenbuch → Abwesenheiten. Anders als der
Stundenplan-/Prüfungsbereich (Ant-Design, moderne SPA) läuft dieses Modul als
Legacy-Dojo/dijit-Anwendung innerhalb eines <iframe> (embedded.do) — die
Formularfelder sind daher größtenteils echte <select>/<input>-Elemente, aber die
Datumsfelder (dijit.form.DateTextBox) verlangen simuliertes Tippen statt direktem
Value-Setzen, da sonst das Hidden-Feld mit dem ISO-Datum nicht synchron bleibt.
Andere WebUntis-Instanzen können abweichende Texte/Strukturen haben.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

DEFAULT_BASE_URL = "https://tbs1.webuntis.com"
DEFAULT_PROFILE_DIR = Path.home() / ".claude" / "webuntis-beurlaubung" / "chrome-profile"
DEFAULT_TEXT = "Beurlaubung durch Ausbildungsbetrieb"
ABWESENHEITSGRUND = "Beurlaubung"  # exakte Option im Abwesenheitsgrund-Dropdown

CHROME_AGENT_MISSING_EXIT = 2

IFRAME_DOC = "document.querySelector('iframe').contentDocument"


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


def click(instance: str, x: int, y: int, count: int = 1) -> None:
    ca(instance, "Input.dispatchMouseEvent", json.dumps({
        "type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": count,
    }))
    time.sleep(0.05)
    ca(instance, "Input.dispatchMouseEvent", json.dumps({
        "type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": count,
    }))


def key(instance: str, key_name: str) -> None:
    ca(instance, "Input.dispatchKeyEvent", json.dumps({"type": "keyDown", "key": key_name, "code": key_name}))
    ca(instance, "Input.dispatchKeyEvent", json.dumps({"type": "keyUp", "key": key_name, "code": key_name}))


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


def find_leaf_by_text(instance: str, text: str, exact: bool = True, in_iframe: bool = False):
    doc = IFRAME_DOC if in_iframe else "document"
    offset = (
        "(() => { const r = document.querySelector('iframe').getBoundingClientRect(); "
        "return {x: r.left, y: r.top}; })()"
        if in_iframe else "({x: 0, y: 0})"
    )
    cmp = f"t === {js_str(text)}" if exact else f"t.includes({js_str(text)})"
    expr = f"""
    (() => {{
      const doc = {doc};
      const off = {offset};
      const all = [...doc.querySelectorAll('*')];
      const els = all.filter(e => e.children.length === 0 && (() => {{ const t = e.textContent.trim(); return {cmp}; }})());
      if (els.length === 0) return null;
      const e = els[0];
      const r = e.getBoundingClientRect();
      return {{x: Math.round(off.x + r.left + r.width/2), y: Math.round(off.y + r.top + r.height/2)}};
    }})()
    """
    return evaluate(instance, expr)


def click_text(instance: str, text: str, what: str | None = None, timeout: float = 15,
                exact: bool = True, in_iframe: bool = False):
    what = what or f"Element mit Text '{text}'"
    pos = wait_for(
        lambda: find_leaf_by_text(instance, text, exact=exact, in_iframe=in_iframe),
        timeout=timeout, what=what,
    )
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
            pos = find_leaf_by_text(instance, "Klassenbuch")
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


def field_rect_in_iframe(instance: str, element_id: str):
    expr = f"""
    (() => {{
      const doc = {IFRAME_DOC};
      const off = (() => {{ const r = document.querySelector('iframe').getBoundingClientRect(); return {{x: r.left, y: r.top}}; }})();
      const el = doc.getElementById({js_str(element_id)});
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return {{
        x: Math.round(off.x + r.left + r.width/2), y: Math.round(off.y + r.top + r.height/2),
        rightArrowX: Math.round(off.x + r.right + 12),
        left: r.left, top: r.top, width: r.width, height: r.height,
      }};
    }})()
    """
    return evaluate(instance, expr)


def select_option_by_text(instance: str, element_id: str, option_text: str) -> None:
    expr = f"""
    (() => {{
      const doc = {IFRAME_DOC};
      const sel = doc.getElementById({js_str(element_id)});
      if (!sel) return {{found: false}};
      const idx = [...sel.options].findIndex(o => o.text.trim() === {js_str(option_text)});
      if (idx === -1) return {{found: false, options: [...sel.options].map(o => o.text)}};
      sel.selectedIndex = idx;
      sel.dispatchEvent(new Event('change', {{bubbles: true}}));
      return {{found: true}};
    }})()
    """
    result = evaluate(instance, expr)
    if not result or not result.get("found"):
        options = result.get("options") if result else None
        raise StepError(
            f"Option '{option_text}' in Feld '{element_id}' nicht gefunden. "
            f"Verfügbare Optionen: {options}"
        )


def set_input_by_id(instance: str, element_id: str, value: str) -> bool:
    expr = f"""
    (() => {{
      const doc = {IFRAME_DOC};
      const el = doc.getElementById({js_str(element_id)});
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


def set_date_field(instance: str, element_id: str, value_ddmmyyyy: str,
                    blur_field_id: str, debug_dir: Path | None, debug_name: str) -> None:
    """Dojo DateTextBox: natives Value-Setzen synchronisiert das Hidden-ISO-Feld nicht.
    Stattdessen: Dreifachklick (Alles markieren) -> Delete -> Input.insertText -> auf ein
    anderes Feld klicken (Blur löst die interne Validierung/Formatierung aus)."""
    rect = wait_for(lambda: field_rect_in_iframe(instance, element_id), what=f"Feld '{element_id}'")
    click(instance, rect["x"], rect["y"], count=3)
    time.sleep(0.15)
    key(instance, "Delete")
    time.sleep(0.1)
    insert_text(instance, value_ddmmyyyy)
    time.sleep(0.2)
    blur_rect = wait_for(lambda: field_rect_in_iframe(instance, blur_field_id), what=f"Feld '{blur_field_id}'")
    click(instance, blur_rect["x"], blur_rect["y"])
    time.sleep(0.3)
    screenshot(instance, debug_dir, debug_name)

    check_expr = f"""
    (() => {{
      const doc = {IFRAME_DOC};
      const el = doc.getElementById({js_str(element_id)});
      return el ? el.value : null;
    }})()
    """
    current = evaluate(instance, check_expr)
    if current != value_ddmmyyyy:
        raise StepError(
            f"Datumsfeld '{element_id}' zeigt '{current}' statt '{value_ddmmyyyy}' — "
            "bitte manuell prüfen/korrigieren."
        )


def find_students_field_id(instance: str) -> str:
    """Sucht das 'Schüler*innen'-Feld über die Label-Nähe statt über eine feste
    dojo-Auto-ID (die ist pro Seitenaufruf nicht stabil). Das Label 'Schüler*innen' kommt
    auch im Listen-Filter oberhalb des Dialogs vor -- deshalb zusätzlich auf das Label
    innerhalb des offenen Dialogs (.dijitDialog) einschränken."""
    expr = f"""
    (() => {{
      const doc = {IFRAME_DOC};
      const all = [...doc.querySelectorAll('*')];
      const label = all.find(e => e.children.length === 0 && e.textContent.trim() === 'Schüler*innen' && e.closest('.dijitDialog'));
      if (!label) return null;
      const dialog = label.closest('.dijitDialog');
      const lr = label.getBoundingClientRect();
      // Nur die eigentlichen Text-Input-Elemente der dijit-Widgets (nicht Pfeil-Buttons/
      // Validierungs-Icons, die dieselbe Klasse 'dijitReset dijitInputField...' tragen aber
      // keine eigene ID haben) -- und unter denen das mit leerem Wert (Klasse-Feld ist zu
      // diesem Zeitpunkt bereits vorbefüllt, Schüler*innen-Feld noch leer).
      const candidates = all.filter(e => {{
        if (e.tagName !== 'INPUT' || !e.id) return false;
        if (!dialog.contains(e)) return false;
        if (!e.className.includes('dijitInputInner')) return false;
        const r = e.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return false;
        return Math.abs(r.top - lr.top) < 40 && e.value === '';
      }});
      candidates.sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
      const best = candidates[0];
      return best ? best.id : null;
    }})()
    """
    field_id = wait_for(lambda: evaluate(instance, expr), what="Schüler*innen-Feld")
    return field_id


def select_students(instance: str, klasse: str, names: list[str], debug_dir: Path | None) -> None:
    field_id = find_students_field_id(instance)
    for name in names:
        rect = wait_for(
            lambda: field_rect_in_iframe(instance, field_id),
            what=f"Schüler*innen-Feld (für '{name}')",
        )
        click(instance, rect["rightArrowX"], rect["y"])
        option_text = f"{name} ({klasse})"
        try:
            click_text(instance, option_text, what=f"Schüler*in '{option_text}'", in_iframe=True)
        except StepError as exc:
            raise StepError(
                f"Schüler*in '{name}' nicht im Auswahlfeld für Klasse '{klasse}' gefunden "
                f"(erwarteter Eintrag: '{option_text}'). Name/Klasse prüfen. ({exc})"
            ) from exc
        time.sleep(0.4)
    screenshot(instance, debug_dir, "schueler_ausgewaehlt")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--klasse", required=True, help="Klassenkürzel wie in WebUntis, z. B. ITF24a")
    parser.add_argument("--schueler", action="append", required=True,
                         help="Schülername wie in WebUntis (Nachname Vorname). Mehrfach angeben für mehrere Schüler.")
    parser.add_argument("--von", required=True, help="Beurlaubung ab YYYY-MM-DD")
    parser.add_argument("--bis", default=None, help="Beurlaubung bis YYYY-MM-DD (Default: --von)")
    parser.add_argument("--text", default=DEFAULT_TEXT, help="Text/Bemerkung im Abwesenheitsformular")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--login-timeout", type=float, default=300)
    parser.add_argument("--debug", action="store_true", help="Screenshots nach jedem Schritt speichern")
    parser.add_argument("--debug-dir", type=Path, default=Path("webuntis-beurlaubung-debug"))
    args = parser.parse_args()

    von = date.fromisoformat(args.von)
    bis = date.fromisoformat(args.bis) if args.bis else von
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

    print("Öffne Klassenbuch → Abwesenheiten ...")
    click_text(instance, "Klassenbuch", what="Menüpunkt 'Klassenbuch'")
    time.sleep(0.6)
    click_text(instance, "Abwesenheiten", what="Untermenüpunkt 'Abwesenheiten'")
    time.sleep(1.0)
    wait_for(lambda: find_leaf_by_text(instance, "Neu", in_iframe=True), what="Abwesenheiten-Seite (Button 'Neu')")
    screenshot(instance, debug_dir, "01_abwesenheiten")

    print(f"Setze Klassenfilter auf '{args.klasse}' ...")
    select_option_by_text(instance, "absenceListForm.idklasseId", args.klasse)
    time.sleep(1.0)
    screenshot(instance, debug_dir, "02_klassenfilter")

    print("Öffne 'Neue Abwesenheit' ...")
    click_text(instance, "Neu", what="Button 'Neu'", in_iframe=True)
    time.sleep(0.8)
    wait_for(lambda: find_leaf_by_text(instance, "Neue Abwesenheit", exact=False, in_iframe=True),
             what="Dialog 'Neue Abwesenheit'")
    screenshot(instance, debug_dir, "03_dialog_offen")

    print(f"Wähle Schüler*innen: {', '.join(args.schueler)} ...")
    select_students(instance, args.klasse, args.schueler, debug_dir)

    print(f"Setze Zeitraum {von.isoformat()} – {bis.isoformat()} ...")
    set_date_field(instance, "absenceForm.idstartDate", von.strftime("%d.%m.%Y"),
                   blur_field_id="absenceForm.idendDate", debug_dir=debug_dir, debug_name="04_von_gesetzt")
    set_date_field(instance, "absenceForm.idendDate", bis.strftime("%d.%m.%Y"),
                   blur_field_id="absenceForm.idtext", debug_dir=debug_dir, debug_name="05_bis_gesetzt")

    print(f"Setze Abwesenheitsgrund auf '{ABWESENHEITSGRUND}' ...")
    select_option_by_text(instance, "absenceForm.idabsenceReason", ABWESENHEITSGRUND)

    print(f"Setze Text auf '{args.text}' ...")
    if not set_input_by_id(instance, "absenceForm.idtext", args.text):
        raise StepError("Textfeld 'absenceForm.idtext' nicht gefunden — bitte Text manuell eintragen.")

    screenshot(instance, debug_dir, "06_formular_ausgefuellt")

    print()
    print("Formular ist ausgefüllt. Bitte im Chrome-Fenster prüfen (insbesondere die")
    print("Schülerauswahl und den Zeitraum) und selbst auf 'Speichern' klicken — das")
    print("übernimmt dieses Skript bewusst nicht.")
    print(f"(chrome-agent-Instanz: {instance}; schließen mit: chrome-agent stop {instance})")

    print()
    print("Vorlagentext für den Ausbildungsbetrieb:")
    print(build_betriebstext(args.schueler, von, bis))


def build_betriebstext(names: list[str], von: date, bis: date) -> str:
    if len(names) == 1:
        subjekt = f"den Azubi {names[0]}"
        verb = "wurde"
    else:
        if len(names) == 2:
            namen_text = " und ".join(names)
        else:
            namen_text = ", ".join(names[:-1]) + " und " + names[-1]
        subjekt = f"die Azubis {namen_text}"
        verb = "wurden"

    if von == bis:
        zeitraum = f"am {von.strftime('%d.%m.%Y')}"
    else:
        zeitraum = f"vom {von.strftime('%d.%m.%Y')} bis {bis.strftime('%d.%m.%Y')}"

    return (
        f"Die Beurlaubung für {subjekt} {verb} {zeitraum} genehmigt, sofern keine "
        "angekündigten Leistungsüberprüfungen für den Tag vorliegen."
    )


if __name__ == "__main__":
    try:
        main()
    except StepError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        sys.exit(1)
