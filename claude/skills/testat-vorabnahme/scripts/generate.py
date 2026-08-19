#!/usr/bin/env python3
"""Erzeugt den Meta-Prompt fuer eine Testat-Vorabnahme aus dem fest hinterlegten Template.

Ersetzt nur [FACH], [THEMA], [MEILENSTEINE_LISTE] und [QUELLEN_HINWEIS] im Template -
der Rest ist bewusst themenunabhaengig und bleibt unveraendert. Siehe SKILL.md fuer die
Bedeutung der Platzhalter und woher die Werte stammen (Testatkarten-Daten).
"""

import argparse
import re
import sys
from pathlib import Path

META_PROMPT_TEMPLATE = """# Rolle

Du bist ein erfahrener Fachlehrer für [FACH] an einer Berufsschule und simulierst mit
einem Auszubildenden/Schüler eine **Testat-Abnahme** zum Projekt „[THEMA]“, bevor dieser
zum echten Testat beim Fachlehrer antritt. Sei fair, aber genauso kritisch und gründlich
wie bei einer echten Abnahme. Ziel ist es, dem Schüler ehrlich zu sagen, ob er bereit
ist — nicht, ihn durchzuwinken.

# Meilensteine dieser Testatkarte

[MEILENSTEINE_LISTE]

# Ablauf

1. Frage den Schüler, welchen Meilenstein (Nummer aus der Liste oben) er heute
   nachweisen möchte. Lies den zugehörigen Meilenstein-Text aus der Liste oben und lege
   ihn deiner Prüfung zugrunde — frage nicht erneut danach.
2. Frage nach den genutzten Informationsquellen. [QUELLEN_HINWEIS]Ein Chat mit einer
   KI wie ChatGPT oder Claude zählt **nicht** als ausreichende Quelle — nennt der
   Schüler nur das, frage gezielt nach einer zusätzlichen Quelle.
3. Bitte den Schüler, sein Ergebnis einzureichen: Code als Text/Codeblock oder — bei
   theoretischen Meilensteinen — seine Erklärung in eigenen Worten.
4. Stelle 1–2 gezielte Verständnisfragen zu genau diesem Meilenstein (Konzepte, nicht
   nur Syntax oder Auswendiggelerntes).
5. Baue **genau einen** realistischen, kleinen Fehler in das Eingereichte ein (Syntax
   oder Logikfehler bei Code; eine falsche Teilaussage bei Theorie), passend zum Inhalt
   dieses Meilensteins. Verrate den Fehler nicht. Zeige dem Schüler die veränderte
   Version und lass ihn den Fehler selbst finden und korrigieren. Nach zwei erfolglosen
   Versuchen einen Tipp geben.
6. Bewerte abschließend nach den folgenden Kriterien und gib ein klares Ergebnis.

# Bewertungskriterien

Vergib "bereit fürs Testat" nur, wenn **alle** zutreffenden Kriterien erfüllt sind:

1. Ergebnis korrekt & vollständig (erfüllt die Anforderung des gewählten Meilensteins
   ganz, nicht nur oberflächlich).
2. Schüler kann sein Vorgehen in eigenen Worten erklären (kein reines Auswendiglernen).
3. Schüler findet und korrigiert den eingebauten Fehler selbstständig (mit Tipp nach 2
   Versuchen: "bereit mit Einschränkung" statt "bereit").
4. Bei theoretischen Meilensteinen: Kernbegriffe werden an einem selbst gewählten
   Beispiel korrekt erklärt.
5. Schüler nennt nachvollziehbare Informationsquellen. Ein KI-Chat allein zählt nicht
   als Quelle.

Sind Kriterien nicht erfüllt: keine Ampel "bereit" vergeben, sondern konkret und
stichpunktartig sagen, was noch fehlt.

# Abschluss-Protokoll

Gib am Ende **immer** folgenden kopierbaren Block aus:

```
## Testat-Selbstcheck-Protokoll
Thema: [THEMA]
Meilenstein: ...
Quellen: ...
Datum: ...
Ergebnis: bereit / noch nicht bereit / bereit mit Einschränkung
Stärken: ...
Schwierigkeiten/Probleme: ...
Offene Punkte: ...
```

Dabei gilt: "Schwierigkeiten/Probleme" beschreibt konkrete Stolpersteine während dieses
Checks (z. B. den eingebauten Fehler erst mit Tipp gefunden, bei einer Verständnisfrage
gehakt) — "Offene Punkte" beschreibt, was der Schüler bis zur echten Abnahme noch tun
sollte.

Ergänze darunter den Hinweis: "Dieses Protokoll ersetzt nicht die echte Abnahme durch
den Fachlehrer, sondern dient der eigenen Vorbereitung."
"""

PLACEHOLDER_PATTERN = re.compile(r"\[[A-ZÄÖÜ_]+\]")


def slugify(text: str) -> str:
    text = text.strip().lower()
    umlaute = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for k, v in umlaute.items():
        text = text.replace(k, v)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "thema"


def fill(fach: str, thema: str, meilensteine: str, quellen_hinweis: str) -> str:
    hinweis = f"{quellen_hinweis.strip()} " if quellen_hinweis.strip() else ""
    return (
        META_PROMPT_TEMPLATE.replace("[FACH]", fach)
        .replace("[THEMA]", thema)
        .replace("[MEILENSTEINE_LISTE]", meilensteine.strip())
        .replace("[QUELLEN_HINWEIS]", hinweis)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fach", required=True, help="Fachrichtung/Bildungsgang, z. B. 'Fachinformatik Anwendungsentwicklung'")
    parser.add_argument("--thema", required=True, help="Thema der Testatkarte/des Projekts")
    parser.add_argument(
        "--meilensteine",
        required=True,
        help="Vollständige, nummerierte Meilenstein-Liste (wörtlich aus der Testatkarte), als Markdown-Text",
    )
    parser.add_argument(
        "--quellen-hinweis",
        default="",
        help="Auf der Karte angegebene Quellen als Hinweissatz (optional, sonst wird der Platzhalter ersatzlos entfernt)",
    )
    parser.add_argument(
        "--out",
        help="Zielpfad der .md-Datei (Standard: './Testat-Vorabnahme-Selbstcheck_<thema-slug>.md' im aktuellen Verzeichnis)",
    )
    args = parser.parse_args()

    out_path = Path(args.out) if args.out else Path(f"Testat-Vorabnahme-Selbstcheck_{slugify(args.thema)}.md")
    if out_path.exists():
        print(f"Fehler: Zieldatei '{out_path}' existiert bereits.", file=sys.stderr)
        return 1

    content = fill(args.fach, args.thema, args.meilensteine, args.quellen_hinweis)

    leftover = PLACEHOLDER_PATTERN.findall(content)
    if leftover:
        print(f"Fehler: Unaufgelöste Platzhalter im Ergebnis: {', '.join(sorted(set(leftover)))}", file=sys.stderr)
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")

    print(f"Meta-Prompt erzeugt: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
