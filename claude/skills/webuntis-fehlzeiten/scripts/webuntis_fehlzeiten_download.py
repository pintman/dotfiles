#!/usr/bin/env python3
"""Lädt den WebUntis-Bericht "Fehlzeiten pro Schüler*in" als CSV herunter, per
chrome-agent (CDP). Login übernimmt immer der Mensch; das Skript gibt niemals
Zugangsdaten ein.

Ablauf auf https://tbs1.webuntis.com/class-register-reports (Legacy-Dojo-Seite in
einem <iframe>, embedded.do):
  Klasse wählen -> Zeitraum "Aktuelles Schuljahr" -> Haken Fehlzeiten, Verspätungen,
  Nur zählende Abwesenheiten, Alle Schüler*innen -> CSV-Button in der Zeile
  "Fehlzeiten pro Schüler*in". WebUntis erzeugt den Bericht asynchron und zeigt dann
  eine Meldung mit Download-Link (a.un-report__message-button). Diese Datei wird per
  fetch() im Seitenkontext (Session-Cookies) geholt und byte-genau gespeichert.

Die letzte Zeile auf stdout ist der Pfad der gespeicherten CSV-Datei.

Voraussetzung: `chrome-agent` auf dem PATH, sonst Exit-Code 2.
"""

import argparse
import base64
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_BASE_URL = "https://tbs1.webuntis.com"
REPORT_PATH = "/class-register-reports"
DEFAULT_PROFILE_DIR = Path.home() / ".claude" / "webuntis-fehlzeiten" / "chrome-profile"
DEFAULT_ZIEL = Path.home() / "Downloads"

CHROME_AGENT_MISSING_EXIT = 2

ZEITRAUM = "CURRENT_SCHOOLYEAR"  # Option "Aktuelles Schuljahr"
CHECKBOXEN = {
    "withAbsences1": "Fehlzeiten",
    "withLateness1": "Verspätungen",
    "excludeNotCountingAbsences1": "Nur zählende Abwesenheiten",
    "allStudents1": "Alle Schüler*innen",
}
BERICHT_ZEILE = "Fehlzeiten pro Schüler"
DATEI_PRAEFIX = "AbsencePerStudent_"

IFRAME_DOC = "document.querySelector('iframe').contentDocument"
IFRAME_WIN = "document.querySelector('iframe').contentWindow"


class StepError(Exception):
    """Ein Ablaufschritt konnte nicht ausgeführt werden (Element nicht gefunden o. Ä.)."""


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def require_chrome_agent() -> None:
    if shutil.which("chrome-agent") is None:
        log("chrome-agent nicht gefunden. Bitte Skill 'setup-chrome-agent' ausführen.")
        sys.exit(CHROME_AGENT_MISSING_EXIT)


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
    return json.loads(ca(*args, timeout=timeout))


def find_running_webuntis_instance() -> str | None:
    try:
        data = ca_json("status", timeout=10)
    except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None
    for inst in data:
        if not inst.get("alive", True):
            continue
        for target in inst.get("targets", []):
            if "webuntis.com" in target.get("url", ""):
                return inst["name"]
    return None


def launch(profile_dir: Path) -> str:
    profile_dir.mkdir(parents=True, exist_ok=True)
    info = ca_json("launch", "--", f"--user-data-dir={profile_dir}", timeout=40)
    return info["name"]


def evaluate(instance: str, expression: str, timeout: float = 30):
    out = ca_json(instance, "Runtime.evaluate", json.dumps({
        "expression": expression,
        "returnByValue": True,
        "awaitPromise": True,
    }), timeout=timeout)
    if "exceptionDetails" in out:
        raise StepError(f"JS-Fehler: {out['exceptionDetails']}")
    return out.get("result", {}).get("value")


def screenshot(instance: str, debug_dir: Path | None, name: str) -> None:
    if debug_dir is None:
        return
    debug_dir.mkdir(parents=True, exist_ok=True)
    out = ca_json(instance, "Page.captureScreenshot", '{"format":"png"}', timeout=20)
    (debug_dir / f"{name}.png").write_bytes(base64.b64decode(out["data"]))


def wait_for(fn, timeout: float = 20, interval: float = 0.5, what: str = "Element"):
    deadline = time.time() + timeout
    last_err = None
    while time.time() < deadline:
        try:
            value = fn()
            if value:
                return value
        except (StepError, RuntimeError, json.JSONDecodeError) as exc:
            last_err = exc  # z. B. iframe lädt gerade neu
        time.sleep(interval)
    raise StepError(f"{what} nicht gefunden (Timeout nach {timeout}s). {last_err or ''}")


def js_str(s: str) -> str:
    return json.dumps(s)


def form_state(instance: str):
    """Zustand des Berichtsformulars im iframe, oder None solange es nicht geladen ist."""
    ids = js_str(list(CHECKBOXEN))
    return evaluate(instance, f"""
    (() => {{
      const f = document.querySelector('iframe');
      if (!f || !f.contentDocument) return null;
      const d = f.contentDocument;
      const sel = d.getElementById('classregReportForm.idklasseId');
      if (!sel || d.readyState !== 'complete' || !f.contentWindow.dijit) return null;
      return {{
        klasse: sel.selectedOptions[0] ? sel.selectedOptions[0].text.trim() : '',
        start: d.getElementById('classregReportForm.idstartDate').value,
        end: d.getElementById('classregReportForm.idendDate').value,
        checks: Object.fromEntries({ids}.map(id => [id, !!(d.getElementById(id) || {{}}).checked])),
      }};
    }})()
    """)


def wait_for_report_page(instance: str, base_url: str, login_timeout: float) -> None:
    """Navigiert zur Berichtsseite. Nach dem Login leitet WebUntis auf /today um —
    dann erneut navigieren."""
    report_url = base_url + REPORT_PATH
    ca(instance, "Page.navigate", json.dumps({"url": report_url}))
    deadline = time.time() + login_timeout
    last_nav = time.time()
    hinweis = False
    while time.time() < deadline:
        try:
            if form_state(instance):
                return
            url = evaluate(instance, "location.href") or ""
        except (StepError, RuntimeError, json.JSONDecodeError):
            url = ""
        logged_in_elsewhere = "webuntis.com/" in url and REPORT_PATH not in url and "login" not in url.lower()
        if logged_in_elsewhere and time.time() - last_nav > 3:
            ca(instance, "Page.navigate", json.dumps({"url": report_url}))
            last_nav = time.time()
        elif not hinweis and time.time() - last_nav > 8:
            log("Bitte im geöffneten Chrome-Fenster bei WebUntis einloggen ...")
            hinweis = True
        time.sleep(1.5)
    raise StepError(f"Berichtsseite nicht erreicht (Login innerhalb von {login_timeout}s?).")


def select_klasse(instance: str, klasse: str) -> None:
    state = wait_for(lambda: form_state(instance), what="Berichtsformular")
    if state["klasse"] == klasse:
        return
    result = evaluate(instance, f"""
    (() => {{
      const sel = {IFRAME_DOC}.getElementById('classregReportForm.idklasseId');
      const idx = [...sel.options].findIndex(o => o.text.trim() === {js_str(klasse)});
      if (idx === -1) return {{found: false, options: [...sel.options].map(o => o.text.trim())}};
      sel.selectedIndex = idx;
      sel.dispatchEvent(new Event('change', {{bubbles: true}}));
      return {{found: true}};
    }})()
    """)
    if not result or not result.get("found"):
        options = result.get("options") if result else None
        raise StepError(f"Klasse '{klasse}' nicht in der Auswahl. Verfügbar: {options}")
    # Klassenwechsel lädt den iframe neu
    time.sleep(1.0)
    wait_for(lambda: (s := form_state(instance)) and s["klasse"] == klasse,
             what=f"Formular mit Klasse '{klasse}'")


def zeitraum_js(setzen: bool) -> str:
    """Findet das Zeitraum-Widget (dijit-ID ist nach iframe-Reload nicht stabil) und
    liefert dessen Wert; setzt ihn optional auf ZEITRAUM."""
    return f"""
    (() => {{
      const w = {IFRAME_WIN};
      if (!w || !w.dijit) return null;
      const fs = w.dijit.registry.toArray().filter(x =>
        x.declaredClass === 'dijit.form.FilteringSelect' && x.store && x.store.get && x.store.get({js_str(ZEITRAUM)}));
      if (!fs.length) return null;
      if ({'true' if setzen else 'false'} && fs[0].get('value') !== {js_str(ZEITRAUM)}) fs[0].set('value', {js_str(ZEITRAUM)});
      return fs[0].get('value');
    }})()
    """


def select_zeitraum(instance: str) -> dict:
    wait_for(lambda: evaluate(instance, zeitraum_js(setzen=True)),
             what="Zeitraum-Auswahl (Option 'Aktuelles Schuljahr')")
    time.sleep(1.0)  # Zeitraumwechsel kann den iframe neu laden

    def gesetzt():
        if evaluate(instance, zeitraum_js(setzen=False)) != ZEITRAUM:
            return None
        return form_state(instance)

    return wait_for(gesetzt, what="Zeitraum 'Aktuelles Schuljahr'")


def set_checkboxen(instance: str) -> None:
    result = evaluate(instance, f"""
    (() => {{
      const d = {IFRAME_DOC};
      const out = {{}};
      for (const id of {js_str(list(CHECKBOXEN))}) {{
        const cb = d.getElementById(id);
        if (!cb) {{ out[id] = null; continue; }}
        if (!cb.checked) cb.click();
        out[id] = cb.checked;
      }}
      return out;
    }})()
    """)
    fehlend = [CHECKBOXEN[i] for i, v in (result or {}).items() if not v]
    if not result or fehlend:
        raise StepError(f"Haken konnten nicht gesetzt werden: {fehlend or list(CHECKBOXEN.values())}")


def vorhandene_links(instance: str) -> list[str]:
    return evaluate(instance, f"""
    [...{IFRAME_DOC}.querySelectorAll('a.un-report__message-button')]
      .map(a => a.href).filter(h => h.includes({js_str(DATEI_PRAEFIX)}))
    """) or []


def csv_export_starten(instance: str) -> None:
    ok = evaluate(instance, f"""
    (() => {{
      const d = {IFRAME_DOC};
      const rows = [...d.querySelectorAll('tr')].filter(tr =>
        tr.querySelector('button.icon-report-csv') && tr.innerText.trim().startsWith({js_str(BERICHT_ZEILE)}));
      if (!rows.length) return false;
      // innerste passende Zeile (äußere Layout-Tabellen enthalten die Zeile ebenfalls)
      rows[rows.length - 1].querySelector('button.icon-report-csv').click();
      return true;
    }})()
    """)
    if not ok:
        raise StepError(f"CSV-Button in Zeile '{BERICHT_ZEILE}' nicht gefunden.")


def download(instance: str, href: str, ziel: Path) -> Path:
    data = evaluate(instance, f"""
    (async () => {{
      const r = await fetch({js_str(href)}, {{credentials: 'include'}});
      const buf = new Uint8Array(await r.arrayBuffer());
      let s = '';
      for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode(...buf.subarray(i, i + 0x8000));
      return {{status: r.status, name: new URL(r.url).searchParams.get('name') || new URL({js_str(href)}, location.href).searchParams.get('name'), b64: btoa(s)}};
    }})()
    """, timeout=90)
    if not data or data.get("status") != 200:
        raise StepError(f"Download fehlgeschlagen (HTTP {data.get('status') if data else '?'}).")
    name = data.get("name") or f"{DATEI_PRAEFIX}{time.strftime('%Y%m%d_%H%M')}"
    ziel.mkdir(parents=True, exist_ok=True)
    pfad = ziel / f"{name}.csv"
    pfad.write_bytes(base64.b64decode(data["b64"]))
    return pfad


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--klasse", required=True, help="Klassenkürzel wie in WebUntis, z. B. ITF24a")
    parser.add_argument("--ziel", type=Path, default=DEFAULT_ZIEL, help="Zielordner (Default: ~/Downloads)")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR)
    parser.add_argument("--login-timeout", type=float, default=300)
    parser.add_argument("--bericht-timeout", type=float, default=120,
                        help="Wartezeit auf die Fertigstellung des Berichts in Sekunden")
    parser.add_argument("--debug", action="store_true", help="Screenshots nach jedem Schritt speichern")
    parser.add_argument("--debug-dir", type=Path, default=Path("webuntis-fehlzeiten-debug"))
    args = parser.parse_args()
    debug_dir = args.debug_dir if args.debug else None

    require_chrome_agent()

    instance = find_running_webuntis_instance()
    if instance:
        log(f"Nutze laufende chrome-agent-Instanz '{instance}'.")
    else:
        log("Starte Chrome über chrome-agent ...")
        instance = launch(args.profile_dir)

    log("Öffne Klassenbuch → Berichte ...")
    wait_for_report_page(instance, args.base_url, args.login_timeout)
    screenshot(instance, debug_dir, "01_berichte")

    log(f"Wähle Klasse '{args.klasse}' ...")
    select_klasse(instance, args.klasse)

    log("Setze Zeitraum 'Aktuelles Schuljahr' ...")
    state = select_zeitraum(instance)
    log(f"  Zeitraum: {state['start']} – {state['end']}")

    log("Setze Haken: " + ", ".join(CHECKBOXEN.values()) + " ...")
    set_checkboxen(instance)
    screenshot(instance, debug_dir, "02_formular")

    vorher = set(vorhandene_links(instance))
    log("Starte CSV-Export 'Fehlzeiten pro Schüler*in' ...")
    csv_export_starten(instance)
    href = wait_for(
        lambda: next((h for h in vorhandene_links(instance) if h not in vorher), None),
        timeout=args.bericht_timeout, interval=1.0, what="Fertiger Bericht (Download-Link)",
    )
    screenshot(instance, debug_dir, "03_bericht_fertig")

    pfad = download(instance, href, args.ziel.expanduser())
    log(f"Gespeichert. (chrome-agent-Instanz: {instance}; schließen mit: chrome-agent stop {instance})")
    print(pfad)


if __name__ == "__main__":
    try:
        main()
    except StepError as exc:
        log(f"Fehler: {exc}")
        sys.exit(1)
