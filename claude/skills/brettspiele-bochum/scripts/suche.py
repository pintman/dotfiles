#!/usr/bin/env python3
"""Baut eine Brettspiel-Suche im Katalog der Stadtbücherei Bochum (Axiell Arena).

Reines Python-Stdlib. Standard: eine Anfrage, Trefferliste ausgeben.
--open öffnet die Suche nur im Browser, --url gibt nur die URL aus.
"""

import argparse
import re
import sys
import urllib.error
import urllib.request
import webbrowser
from html.parser import HTMLParser
from urllib.parse import urlencode

BASE_URL = "https://stadtbuecherei.bochum.de/suche"
DETAIL_URL = "https://stadtbuecherei.bochum.de/results"
AGENCY = "ADEBOCHUM"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko)"

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


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as err:
        if err.code == 429:
            wait = err.headers.get("Retry-After", "?")
            sys.exit(f"Katalog drosselt Anfragen (HTTP 429). Bitte in {wait} s erneut versuchen "
                     f"oder im Browser öffnen:\n{url}")
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Brettspiele im Katalog der Stadtbücherei Bochum suchen.")
    parser.add_argument("begriff", nargs="*", help="Suchbegriff, z. B. Catan (leer = alle Spiele)")
    parser.add_argument("--open", action="store_true",
                        help="Suche nur im Browser öffnen, nichts abrufen")
    parser.add_argument("--url", action="store_true", help="Nur die Such-URL ausgeben")
    args = parser.parse_args()

    url = build_url(" ".join(args.begriff))
    if args.url:
        print(url)
        return
    if args.open:
        print(url)
        webbrowser.open(url)
        return

    total, spiele = parse_results(fetch(url))
    if not spiele:
        print("Keine Spiele gefunden.")
        return
    print(f"{total} Treffer:")
    for spiel in spiele:
        print(format_spiel(spiel))
    if total > len(spiele):
        print(f"\n… {total - len(spiele)} weitere auf der Website:\n{url}")
    print("\nVerfügbarkeit: siehe Detail-Link.")


if __name__ == "__main__":
    main()
