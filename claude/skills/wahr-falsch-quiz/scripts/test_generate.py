#!/usr/bin/env python3
"""Schwarzkasten-Tests für generate.py: Config rein, Dateien raus.

Aufruf (python-docx muss installiert sein):
    python3 -m unittest scripts/test_generate.py
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent / 'generate.py'

TEST_AUSSAGEN = [
    {'text': 'Aussage eins ist wahr.', 'antwort': 'wahr'},
    {'text': 'Aussage zwei ist falsch.', 'antwort': 'falsch'},
    {'text': 'Aussage drei ist wahr.', 'antwort': 'wahr'},
]

ERWARTETER_LOESUNG_TEXT = (
    '[w] Aussage eins ist wahr.\n'
    '[f] Aussage zwei ist falsch.\n'
    '[w] Aussage drei ist wahr.\n'
)


def run_generate(tmp_dir, output_name, variante=None):
    config_path = Path(tmp_dir) / 'config.json'
    output_path = Path(tmp_dir) / output_name
    config = {'output': str(output_path), 'aussagen': TEST_AUSSAGEN}
    config_path.write_text(json.dumps(config), encoding='utf-8')

    cmd = [sys.executable, str(SCRIPT), '--config', str(config_path)]
    if variante:
        cmd += ['--variante', variante]
    subprocess.run(cmd, check=True, capture_output=True, text=True)

    return output_path


class GenerateLoesungTxtTest(unittest.TestCase):
    def test_variante_lehrer_erzeugt_txt_mit_gleichem_basisnamen(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = run_generate(tmp_dir, 'output.docx', variante='lehrer')

            self.assertTrue(output_path.exists())
            txt_path = output_path.with_suffix('.txt')
            self.assertTrue(txt_path.exists())
            self.assertEqual(txt_path.read_text(encoding='utf-8'), ERWARTETER_LOESUNG_TEXT)

    def test_variante_schueler_erzeugt_zusaetzlich_loesung_txt(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = run_generate(tmp_dir, 'output.docx', variante='schueler')

            self.assertTrue(output_path.exists())
            txt_path = output_path.parent / 'output_LOESUNG.txt'
            self.assertTrue(txt_path.exists())
            self.assertEqual(txt_path.read_text(encoding='utf-8'), ERWARTETER_LOESUNG_TEXT)

    def test_variante_beide_erzeugt_beide_docx_und_eine_txt(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = run_generate(tmp_dir, 'output.docx', variante='beide')
            loesung_docx = output_path.parent / 'output_LOESUNG.docx'
            loesung_txt = output_path.parent / 'output_LOESUNG.txt'

            self.assertTrue(output_path.exists())
            self.assertTrue(loesung_docx.exists())
            self.assertTrue(loesung_txt.exists())
            self.assertEqual(loesung_txt.read_text(encoding='utf-8'), ERWARTETER_LOESUNG_TEXT)


if __name__ == '__main__':
    unittest.main()
