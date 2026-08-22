#!/usr/bin/env python3
"""Validiert das YAML-Frontmatter aller SKILL.md-Dateien.

Prueft: Frontmatter ist vorhanden und als YAML parsebar, und die
Pflichtfelder 'name' und 'description' sind nicht-leer gesetzt.
"""
import glob
import sys

import yaml


def extract_frontmatter(text: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:i])
    return None


def main() -> int:
    files = sorted(glob.glob("claude/skills/*/SKILL.md"))
    if not files:
        print("FEHLER: keine SKILL.md-Dateien gefunden.", file=sys.stderr)
        return 1

    failed = False
    for path in files:
        text = open(path, encoding="utf-8").read()
        raw = extract_frontmatter(text)
        if raw is None:
            print(f"FEHLER {path}: kein YAML-Frontmatter gefunden (fehlende '---'-Marker)")
            failed = True
            continue
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as e:
            print(f"FEHLER {path}: ungueltiges YAML im Frontmatter: {e}")
            failed = True
            continue
        if not isinstance(data, dict):
            print(f"FEHLER {path}: Frontmatter ist kein Mapping")
            failed = True
            continue
        file_ok = True
        for field in ("name", "description"):
            if not str(data.get(field, "")).strip():
                print(f"FEHLER {path}: Pflichtfeld '{field}' fehlt oder ist leer")
                failed = True
                file_ok = False
        if file_ok:
            print(f"OK {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
