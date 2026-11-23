#!/usr/bin/env python3
"""Sucht Brettspiele in der Stadtbücherei Bochum (Axiell Arena) und der Spieliothek Herne.

Python-Stdlib; für Herne zusätzlich `pdftotext` (poppler).
Bochum: eine Anfrage, Trefferliste; -v/--verfuegbar ruft pro Treffer Detailseite + Standorte ab.
Herne: kein Online-Katalog, nur PDF-Gesamtliste (Stand 03/2018) → wird geladen, nach
~/.cache/brettspiele/herne.txt konvertiert und lokal durchsucht (--update lädt neu).
--open öffnet die Suche nur im Browser, --url gibt nur die URL(s) aus.
"""

import argparse
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import webbrowser
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.parse import urlencode

BASE_URL = "https://stadtbuecherei.bochum.de/suche"
DETAIL_URL = "https://stadtbuecherei.bochum.de/results"
AGENCY = "ADEBOCHUM"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko)"
MAX_VERFUEGBAR = 10  # Detail-Abrufe pro Suche (-v)
PAUSE_S = 1.0  # Pause vor jedem Detail-Abruf
MAX_WARTEN_S = 60  # längste Wartezeit bei HTTP 429 (-v)

HERNE_PDF_URL = "https://spielezentrum.de/media/uploads/2018/03/SPO-Spiele-web.pdf"
HERNE_CACHE = Path.home() / ".cache" / "brettspiele" / "herne.txt"
HERNE_STAND = "03/2018"
MAX_HERNE = 30  # ausgegebene Herne-Treffer

# Aus einer echten Browser-Suche übernommen: Bibliothek Bochum + Medienklasse "game".
SPIEL_FILTER = (
    r"organisationId_index:ADEBOCHUM\|012d1f3e\-bc90\-4f78\-9bda\-02b2736c9d36"
    " AND mediaClass_index:game"
)

# Solr-Sonderzeichen (Leerzeichen bleiben, damit mehrere Wörter funktionieren).
SOLR_SPECIAL = re.compile(r'([+\-&|!(){}\[\]^"~*?:\\/])')


def solr_escape(term: str) -> str:
    return SOLR_SPECIAL.sub(r"\\\1", term)


def build_url(begriff: str) -> str:
    query = SPIEL_FILTER
    begriff = begriff.strip()
    if begriff:
        query += f" AND ({solr_escape(begriff)})"
    params = {
        "p_p_id": "searchResult_WAR_arenaportlet",
        "p_p_lifecycle": "1",
        "p_p_state": "normal",
        "p_r_p_arena_urn:arena_facet_queries": "",
        "p_r_p_arena_urn:arena_search_query": query,
        "p_r_p_arena_urn:arena_search_type": "solr",
        "p_r_p_arena_urn:arena_sort_advice": "field=Relevance&direction=Descending",
    }
    return f"{BASE_URL}?{urlencode(params)}"


def detail_url(record_id: str) -> str:
    params = {
        "p_p_id": "crDetailWicket_WAR_arenaportlet",
        "p_p_lifecycle": "1",
        "p_p_state": "normal",
        "p_r_p_arena_urn:arena_search_item_id": record_id,
        "p_r_p_arena_urn:arena_agency_name": AGENCY,
    }
    return f"{DETAIL_URL}?{urlencode(params)}"


# Klasse des umschließenden Elements → Feldname im Ergebnis.
FELDER = {
    "arena-record-title": "titel",
    "arena-detail-contributor": "mitwirkende",
    "arena-record-year": "jahr",
    "arena-record-series": "reihe",
}
VOID_TAGS = {"img", "br", "hr", "input", "meta", "link", "source", "wbr"}


class _ResultParser(HTMLParser):
    """Sammelt Treffer aus einer Arena-Trefferliste (div.arena-record)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[set[str]] = []
        self.spiele: list[dict[str, str]] = []

    def handle_starttag(self, tag, attrs):
        classes = set((dict(attrs).get("class") or "").split())
        if "arena-record" in classes:
            self.spiele.append({"id": "", "titel": "", "mitwirkende": "", "jahr": "", "reihe": ""})
        if tag not in VOID_TAGS:
            self.stack.append(classes)

    def handle_endtag(self, tag):
        if tag not in VOID_TAGS and self.stack:
            self.stack.pop()

    def handle_data(self, data):
        text = data.strip()
        if not text or not self.spiele:
            return
        aktuell = self.spiele[-1]
        offen = set().union(*self.stack) if self.stack else set()
        if "arena-record-id" in offen:
            aktuell["id"] += text
            return
        if "arena-field" in offen:  # Beschriftung wie "Erscheinungsjahr:"
            return
        for klasse, feld in FELDER.items():
            if klasse in offen:
                aktuell[feld] = f"{aktuell[feld]} {text}".strip()
                return


def parse_results(html: str) -> tuple[int, list[dict[str, str]]]:
    parser = _ResultParser()
    parser.feed(html)
    match = re.search(r"hat (\d+) Treffer", html)
    total = int(match.group(1)) if match else len(parser.spiele)
    return total, parser.spiele


class _HoldingsParser(HTMLParser):
    """Sammelt Standorte aus dem Wicket-AJAX-Fragment der Detailseite."""

    FELDER = {
        "arena-holding-link": "standort",
        "arena-holding-shelf-mark": "signatur",
        "arena-holding-nof-total": "gesamt",
        "arena-holding-first-loan-due-date": "rueckgabe",
        "arena-availability-right": "status",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[set[str]] = []
        self.standorte: list[dict[str, str]] = []

    def handle_starttag(self, tag, attrs):
        classes = set((dict(attrs).get("class") or "").split())
        if "arena-holding-container" in classes:
            self.standorte.append({feld: "" for feld in self.FELDER.values()})
        if tag not in VOID_TAGS:
            self.stack.append(classes)

    def handle_endtag(self, tag):
        if tag not in VOID_TAGS and self.stack:
            self.stack.pop()

    def handle_data(self, data):
        text = data.strip()
        if not text or not self.standorte:
            return
        offen = set().union(*self.stack) if self.stack else set()
        if "arena-field" in offen:
            return
        for klasse, feld in self.FELDER.items():
            if klasse in offen:
                eintrag = self.standorte[-1]
                eintrag[feld] = f"{eintrag[feld]} {text}".strip()
                return


def parse_summary(html: str) -> dict[str, str]:
    """Zusammenfassung der Detailseite: Anzahl verfügbar und Vormerkungen."""
    ergebnis = {}
    for klasse, feld in (("arena-availsummary-loans", "verfuegbar"),
                         ("arena-availsummary-reservations", "vormerkungen")):
        match = re.search(rf'class="{klasse}">.*?class="arena-value">([^<]*)<', html, re.S)
        ergebnis[feld] = match.group(1).strip() if match else ""
    return ergebnis


def holdings_url(html: str) -> str | None:
    """AJAX-URL des Standort-Panels (wird im Browser per JavaScript nachgeladen)."""
    match = re.search(r'wicketAjaxGet\("([^"]*holdingsPanel[^"]*)"', html)
    if not match:
        return None
    return re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), match.group(1))


def parse_holdings(xml: str) -> list[dict[str, str]]:
    parser = _HoldingsParser()
    for teil in re.findall(r"<!\[CDATA\[(.*?)\]\]>", xml, re.S):
        parser.feed(teil)
    return parser.standorte


_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
AJAX_HEADERS = {"Wicket-Ajax": "true", "X-Requested-With": "XMLHttpRequest"}


class Gedrosselt(Exception):
    """HTTP 429; wait = Retry-After in Sekunden (oder None)."""

    def __init__(self, wait: int | None) -> None:
        super().__init__(wait)
        self.wait = wait


def fetch(url: str, headers: dict[str, str] | None = None) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
        with _OPENER.open(request, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as err:
        if err.code == 429:
            wait = err.headers.get("Retry-After", "")
            raise Gedrosselt(int(wait) if wait.isdigit() else None) from None
        sys.exit(f"HTTP-Fehler {err.code} beim Abruf von {url}")
    except urllib.error.URLError as err:
        sys.exit(f"Netzwerkfehler: {err.reason}")


def format_spiel(spiel: dict[str, str]) -> str:
    zeile = f"- {spiel['titel']}"
    if spiel["jahr"]:
        zeile += f" ({spiel['jahr']})"
    if spiel["mitwirkende"]:
        zeile += f" – {spiel['mitwirkende']}"
    if spiel["reihe"]:
        zeile += f" [{spiel['reihe']}]"
    if spiel["id"]:
        zeile += f"\n  {detail_url(spiel['id'])}"
    return zeile


def verfuegbarkeit(record_id: str) -> dict:
    """Detailseite + Standort-Panel abrufen (gleiche Session wegen Wicket)."""
    html = fetch(detail_url(record_id))
    info = {**parse_summary(html), "standorte": []}
    url = holdings_url(html)
    if url:
        info["standorte"] = parse_holdings(fetch(url, AJAX_HEADERS))
    return info


def verfuegbarkeit_mit_retry(record_id: str) -> dict | None:
    """Bei HTTP 429 einmal Retry-After abwarten (max. MAX_WARTEN_S), sonst None."""
    try:
        return verfuegbarkeit(record_id)
    except Gedrosselt as err:
        wait = err.wait if err.wait is not None else MAX_WARTEN_S
        if wait > MAX_WARTEN_S:
            return None
        print(f"  (Katalog drosselt, warte {wait} s …)", file=sys.stderr, flush=True)
        time.sleep(wait)
        try:
            return verfuegbarkeit(record_id)
        except Gedrosselt:
            return None


def format_verfuegbarkeit(info: dict) -> str:
    zeilen = []
    for ort in info["standorte"]:
        zeile = f"  {ort['standort'] or '?'}"
        if ort["signatur"]:
            zeile += f", {ort['signatur']}"
        zeile += f": {ort['status'] or '?'}"
        if ort["rueckgabe"]:
            zeile += f" (Rückgabe {ort['rueckgabe']})"
        zeilen.append(zeile)
    if not zeilen:  # Fallback: nur Zusammenfassung
        zeilen.append(f"  Verfügbar: {info['verfuegbar'] or '?'}")
    zeilen[-1] += f" · Vormerkungen: {info['vormerkungen'] or '?'}"
    return "\n".join(zeilen)


# --- Spieliothek Herne (PDF-Gesamtliste) ---------------------------------------------------

_JAHR = re.compile(r"^\d{4}$")
_ALTER = re.compile(r"^\d{2}")
_SPIELER = re.compile(r"^[\d.+\-]+$")


def _herne_felder(eintrag: dict[str, str], werte: list[str]) -> None:
    """Spalten nach Alter/Spieltyp/Spieler/Jahr zuordnen (Spalten können fehlen)."""
    werte = list(werte)
    if werte and _JAHR.match(werte[-1]):
        eintrag["jahr"] = werte.pop()
    if werte and _ALTER.match(werte[0]):
        eintrag["alter"] = werte.pop(0)
    if werte and _SPIELER.match(werte[-1]):
        eintrag["spieler"] = werte.pop()
    if werte:
        eintrag["spieltyp"] = " ".join(werte)


def parse_herne(text: str) -> list[dict[str, str]]:
    """pdftotext-Ausgabe (-layout) der Herne-Liste in Einträge zerlegen.

    Spaltenbreiten variieren je Seite → Trennung an ≥ 2 Leerzeichen. Stark eingerückte Zeilen
    sind Fortsetzungen (umgebrochene Spalten) des vorherigen Eintrags.
    """
    spiele: list[dict[str, str]] = []
    for roh in text.splitlines():
        roh = roh.replace("\f", "")
        zeile = roh.strip()
        if not zeile or zeile == "Spieliothek" or zeile.startswith("Titel "):
            continue
        felder = re.split(r"\s{2,}", zeile)
        if len(roh) - len(roh.lstrip()) >= 10 and spiele:
            _herne_felder(spiele[-1], felder)
            continue
        eintrag = {"titel": felder[0], "verlag": "", "alter": "", "spieltyp": "",
                   "spieler": "", "jahr": ""}
        if len(felder) > 1:
            eintrag["verlag"] = felder[1]
        _herne_felder(eintrag, felder[2:])
        spiele.append(eintrag)
    return spiele


def suche_herne(spiele: list[dict[str, str]], begriff: str) -> list[dict[str, str]]:
    """Alle Wörter müssen (ohne Groß-/Kleinschreibung) in Titel oder Verlag vorkommen."""
    woerter = begriff.casefold().split()
    return [s for s in spiele
            if all(w in f"{s['titel']} {s['verlag']}".casefold() for w in woerter)]


def format_herne(spiel: dict[str, str]) -> str:
    zeile = f"- {spiel['titel']}"
    if spiel["jahr"]:
        zeile += f" ({spiel['jahr']})"
    if spiel["verlag"]:
        zeile += f" – {spiel['verlag']}"
    details = [spiel["spieltyp"]]
    if spiel["alter"]:
        details.append(f"ab {spiel['alter']}")
    if spiel["spieler"]:
        details.append(f"{spiel['spieler']} Sp.")
    details = [d for d in details if d]
    if details:
        zeile += " · " + ", ".join(details)
    return zeile


def herne_text(update: bool = False) -> str:
    """Herne-Liste als Text (Cache, sonst PDF laden + pdftotext). Fehler → RuntimeError."""
    if HERNE_CACHE.exists() and not update:
        return HERNE_CACHE.read_text(encoding="utf-8")
    if not shutil.which("pdftotext"):
        raise RuntimeError("pdftotext fehlt (brew install poppler)")
    # spielezentrum.de liefert ein Zertifikat für einen anderen Host (7wonders-turnier.de).
    # Bewusst nur für diesen Abruf ohne Prüfung; es wird nur eine öffentliche PDF gelesen.
    kontext = ssl.create_default_context()
    kontext.check_hostname = False
    kontext.verify_mode = ssl.CERT_NONE
    request = urllib.request.Request(HERNE_PDF_URL, headers={"User-Agent": USER_AGENT})
    print("(Lade Herne-Liste …)", file=sys.stderr, flush=True)
    try:
        with urllib.request.urlopen(request, timeout=120, context=kontext) as response:
            pdf = response.read()
    except (urllib.error.URLError, TimeoutError) as err:
        raise RuntimeError(f"Abruf der Herne-Liste fehlgeschlagen: {err}") from None
    with tempfile.TemporaryDirectory() as tmp:
        pfad = Path(tmp) / "herne.pdf"
        pfad.write_bytes(pdf)
        ergebnis = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(pfad), "-"],
                                  capture_output=True, text=True, encoding="utf-8")
    if ergebnis.returncode != 0:
        raise RuntimeError(f"pdftotext fehlgeschlagen: {ergebnis.stderr.strip()}")
    HERNE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    HERNE_CACHE.write_text(ergebnis.stdout, encoding="utf-8")
    return ergebnis.stdout


def ausgabe_herne(begriff: str, update: bool) -> None:
    print(f"## Spieliothek Herne (Liste Stand {HERNE_STAND}, ohne Verfügbarkeit)")
    if not begriff.strip():
        print(f"Bestand zu groß für eine Liste ohne Suchbegriff – Gesamtliste: {HERNE_PDF_URL}")
        return
    try:
        spiele = parse_herne(herne_text(update))
    except RuntimeError as err:
        print(f"Nicht durchsuchbar: {err}\nGesamtliste: {HERNE_PDF_URL}")
        return
    treffer = suche_herne(spiele, begriff)
    if not treffer:
        print("Keine Spiele gefunden (neuere Spiele fehlen in der Liste).")
        return
    print(f"{len(treffer)} Treffer:")
    for spiel in treffer[:MAX_HERNE]:
        print(format_herne(spiel))
    if len(treffer) > MAX_HERNE:
        print(f"… {len(treffer) - MAX_HERNE} weitere – Begriff eingrenzen.")


# --- Stadtbücherei Bochum ------------------------------------------------------------------

def ausgabe_bochum(begriff: str, verfuegbar: bool) -> None:
    print("## Stadtbücherei Bochum")
    url = build_url(begriff)
    try:
        total, spiele = parse_results(fetch(url))
    except Gedrosselt as err:
        print(f"Katalog drosselt Anfragen (HTTP 429). Bitte in {err.wait or '?'} s erneut "
              f"versuchen oder im Browser öffnen:\n{url}")
        return
    except SystemExit as err:  # Netzwerk-/HTTP-Fehler aus fetch
        print(err.code)
        return
    if not spiele:
        print("Keine Spiele gefunden.")
        return
    print(f"{total} Treffer:")
    abfragen = verfuegbar
    for nr, spiel in enumerate(spiele):
        print(format_spiel(spiel))
        if abfragen and spiel["id"] and nr < MAX_VERFUEGBAR:
            time.sleep(PAUSE_S)  # Katalog drosselt schnelle Folgeanfragen
            try:
                info = verfuegbarkeit_mit_retry(spiel["id"])
            except SystemExit as err:
                abfragen = False
                print(f"  Verfügbarkeit: {err.code}")
                continue
            if info is None:
                abfragen = False
                print("  Verfügbarkeit: Katalog drosselt (HTTP 429) – ab hier Detail-Link nutzen.")
            else:
                print(format_verfuegbarkeit(info))
    if total > len(spiele):
        print(f"\n… {total - len(spiele)} weitere auf der Website:\n{url}")
    if not verfuegbar:
        print("\nVerfügbarkeit: siehe Detail-Link (oder -v).")
    elif abfragen and len(spiele) > MAX_VERFUEGBAR:
        print(f"\nVerfügbarkeit nur für die ersten {MAX_VERFUEGBAR} Treffer abgerufen.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Brettspiele in der Stadtbücherei Bochum und der Spieliothek Herne suchen.")
    parser.add_argument("begriff", nargs="*", help="Suchbegriff, z. B. Catan (leer = alle Spiele)")
    parser.add_argument("--nur", choices=["bochum", "herne"], help="nur eine Bibliothek durchsuchen")
    parser.add_argument("--open", action="store_true",
                        help="Suche nur im Browser öffnen, nichts abrufen")
    parser.add_argument("--url", action="store_true", help="Nur die Such-URL(s) ausgeben")
    parser.add_argument("-v", "--verfuegbar", action="store_true",
                        help=f"Bochum: Verfügbarkeit/Standort je Treffer abrufen "
                             f"(max. {MAX_VERFUEGBAR})")
    parser.add_argument("--update", action="store_true", help="Herne-Liste neu herunterladen")
    args = parser.parse_args()

    begriff = " ".join(args.begriff)
    bochum = args.nur in (None, "bochum")
    herne = args.nur in (None, "herne")

    if args.url or args.open:
        urls = ([build_url(begriff)] if bochum else []) + ([HERNE_PDF_URL] if herne else [])
        for url in urls:
            print(url)
            if args.open:
                webbrowser.open(url)
        return

    if bochum:
        ausgabe_bochum(begriff, args.verfuegbar)
    if bochum and herne:
        print()
    if herne:
        ausgabe_herne(begriff, args.update)


if __name__ == "__main__":
    main()
