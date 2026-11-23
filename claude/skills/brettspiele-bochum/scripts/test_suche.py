#!/usr/bin/env python3
"""Tests für suche.py (offline, kein Netzwerkzugriff).

Aufruf:
    python3 -m unittest scripts/test_suche.py
"""

import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).parent))
import suche  # noqa: E402


def solr_query(url: str) -> str:
    params = parse_qs(urlparse(url).query)
    return params["p_r_p_arena_urn:arena_search_query"][0]


class BuildUrlTest(unittest.TestCase):
    def test_einzelbegriff_wird_an_spielfilter_gehaengt(self):
        url = suche.build_url("Catan")
        self.assertEqual(
            solr_query(url),
            r"organisationId_index:ADEBOCHUM\|012d1f3e\-bc90\-4f78\-9bda\-02b2736c9d36"
            " AND mediaClass_index:game AND (Catan)",
        )

    def test_solr_suche_und_suchseite(self):
        url = suche.build_url("Catan")
        params = parse_qs(urlparse(url).query)
        self.assertTrue(url.startswith("https://stadtbuecherei.bochum.de/suche?"))
        self.assertEqual(params["p_r_p_arena_urn:arena_search_type"], ["solr"])

    def test_mehrere_woerter_in_klammern(self):
        self.assertTrue(solr_query(suche.build_url("Siedler von Catan")).endswith(
            "AND (Siedler von Catan)"))

    def test_solr_sonderzeichen_werden_escaped(self):
        self.assertTrue(solr_query(suche.build_url("Ich: Spiel!")).endswith(
            r"AND (Ich\: Spiel\!)"))

    def test_ohne_begriff_alle_spiele(self):
        self.assertTrue(solr_query(suche.build_url("")).endswith("mediaClass_index:game"))


FIXTURE = Path(__file__).parent / "fixtures" / "catan.html"


class ParseResultsTest(unittest.TestCase):
    def setUp(self):
        self.total, self.spiele = suche.parse_results(FIXTURE.read_text(encoding="utf-8"))

    def test_trefferzahl(self):
        self.assertEqual(self.total, 6)
        self.assertEqual(len(self.spiele), 6)

    def test_erster_treffer_vollstaendig(self):
        self.assertEqual(self.spiele[0], {
            "id": "f0383d94-db0e-43fa-ab0c-07f2d8b9b347",
            "titel": "Die Siedler von Catan - das Würfelspiel : für 1-4 Spieler ab 7 Jahren",
            "mitwirkende": "Teuber, Klaus",
            "jahr": "2009",
            "reihe": "",
        })

    def test_reihe_und_fehlende_mitwirkende(self):
        self.assertEqual(self.spiele[1]["reihe"], "Spiel des Jahres 1995")
        self.assertEqual(self.spiele[1]["mitwirkende"], "")

    def test_keine_treffer(self):
        self.assertEqual(suche.parse_results("<html><body>keine Treffer</body></html>"), (0, []))


class DetailUrlTest(unittest.TestCase):
    def test_detail_url_enthaelt_id_und_bibliothek(self):
        params = parse_qs(urlparse(suche.detail_url("abc-123")).query)
        self.assertEqual(params["p_r_p_arena_urn:arena_search_item_id"], ["abc-123"])
        self.assertEqual(params["p_r_p_arena_urn:arena_agency_name"], ["ADEBOCHUM"])


if __name__ == "__main__":
    unittest.main()
