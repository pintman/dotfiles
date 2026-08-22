#!/usr/bin/env python3
"""Prueft alle .yaml/.yml- und .json-Dateien im Repo auf gueltige Syntax."""
import glob
import json
import sys

import yaml


def check(files: list[str], loader) -> bool:
    failed = False
    for path in sorted(files):
        try:
            with open(path, encoding="utf-8") as fh:
                loader(fh)
            print(f"OK {path}")
        except Exception as e:
            print(f"FEHLER {path}: {e}")
            failed = True
    return failed


def main() -> int:
    yaml_files = glob.glob("**/*.yaml", recursive=True) + glob.glob("**/*.yml", recursive=True)
    json_files = glob.glob("**/*.json", recursive=True)

    failed = False
    failed |= check(yaml_files, yaml.safe_load)
    failed |= check(json_files, json.load)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
