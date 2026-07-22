#!/usr/bin/env python3
"""Rendert eine PlantUML-Datei ueber den oeffentlichen PlantUML-Server zu SVG und PNG.

Nutzt ausschliesslich urllib (Stdlib) - kein pip-Install, keine venv noetig.
"""
import argparse
import sys
import time
import zlib
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Austauschbar, falls spaeter ein selbstgehosteter PlantUML-Server verwendet werden soll.
PLANTUML_SERVER = "https://www.plantuml.com/plantuml"

USER_AGENT = "Mozilla/5.0 (compatible; klassendiagramm-skill)"
TIMEOUT_SECONDS = 20
RETRY_DELAY_SECONDS = 3


def _encode6bit(b: int) -> str:
    if b < 10:
        return chr(48 + b)
    b -= 10
    if b < 26:
        return chr(65 + b)
    b -= 26
    if b < 26:
        return chr(97 + b)
    b -= 26
    if b == 0:
        return "-"
    if b == 1:
        return "_"
    return "?"


def _append3bytes(b1: int, b2: int, b3: int, length: int) -> str:
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    res = _encode6bit(c1 & 0x3F) + _encode6bit(c2 & 0x3F)
    if length > 1:
        res += _encode6bit(c3 & 0x3F)
    if length > 2:
        res += _encode6bit(c4 & 0x3F)
    return res


def encode_plantuml(text: str) -> str:
    """PlantUMLs eigenes Deflate+Base64-Encoding fuer die Server-URL."""
    compressed = zlib.compress(text.encode("utf-8"), 9)[2:-4]  # raw deflate, ohne zlib-Header/Checksum
    out = []
    for i in range(0, len(compressed), 3):
        chunk = compressed[i:i + 3]
        b1 = chunk[0]
        b2 = chunk[1] if len(chunk) > 1 else 0
        b3 = chunk[2] if len(chunk) > 2 else 0
        out.append(_append3bytes(b1, b2, b3, len(chunk)))
    return "".join(out)


def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        return resp.read()


def render_format(encoded: str, fmt: str, out_path: Path):
    url = f"{PLANTUML_SERVER}/{fmt}/{encoded}"
    attempts = 0
    while True:
        attempts += 1
        try:
            data = fetch(url)
            out_path.write_bytes(data)
            return
        except HTTPError as e:
            # HTTP 400 vom PlantUML-Server bedeutet Syntaxfehler im .puml, kein Netzwerkproblem -> kein Retry.
            error_body = e.read()
            error_path = out_path.with_suffix(f".error.{fmt}")
            error_path.write_bytes(error_body)
            print(
                f"Fehler: PlantUML-Server meldet Syntaxfehler (HTTP {e.code}) fuer Format {fmt}.\n"
                f"Fehlerbild gespeichert unter {error_path} - .puml-Quelltext pruefen.",
                file=sys.stderr,
            )
            sys.exit(2)
        except (URLError, TimeoutError) as e:
            if attempts >= 2:
                print(
                    f"Fehler: PlantUML-Server nicht erreichbar ({e}). "
                    f".puml-Quelltext bleibt erhalten, spaeter erneut versuchen.",
                    file=sys.stderr,
                )
                sys.exit(1)
            time.sleep(RETRY_DELAY_SECONDS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("puml_file", type=Path, help="Pfad zur .puml-Quelldatei")
    parser.add_argument("-o", "--output-stem", type=Path, required=True,
                         help="Zielpfad ohne Endung, z.B. out/diagramm (erzeugt diagramm.svg und diagramm.png)")
    args = parser.parse_args()

    if not args.puml_file.is_file():
        print(f"Fehler: Datei nicht gefunden: {args.puml_file}", file=sys.stderr)
        sys.exit(1)

    text = args.puml_file.read_text(encoding="utf-8")
    encoded = encode_plantuml(text)

    args.output_stem.parent.mkdir(parents=True, exist_ok=True)

    for fmt, suffix in (("svg", ".svg"), ("png", ".png")):
        out_path = args.output_stem.with_suffix(suffix)
        render_format(encoded, fmt, out_path)
        print(f"{fmt.upper()} gespeichert -> {out_path}")


if __name__ == "__main__":
    main()
