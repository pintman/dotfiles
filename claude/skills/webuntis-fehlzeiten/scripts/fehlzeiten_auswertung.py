#!/usr/bin/env python3
"""Wertet einen WebUntis-Export 'AbsencePerStudent_*.csv' aus und gibt
pro Schüler*in eine übersichtliche Textzusammenfassung aus.

Aufruf: python3 fehlzeiten_auswertung.py AbsencePerStudent_YYYYMMDD_HHMM.csv
"""
import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime

# Spaltenindizes (Header enthält doppelte Spalte "Text", daher per Index)
NAME, KLASSE, DATUM, WOCHENTAG = 0, 3, 4, 5
FEHLSTD, FEHLMIN, LEHRKRAFT, FACH, GRUND = 6, 7, 8, 9, 10
STUNDE, STATUS, FEHLTAGE = 16, 17, 18

BREITE = 64


def lese_csv(pfad):
    for enc in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            with open(pfad, encoding=enc, newline="") as f:
                zeilen = list(csv.reader(f, delimiter="\t"))
            if zeilen and "Klasse" in zeilen[0]:
                return zeilen[1:]
        except (UnicodeError, UnicodeDecodeError):
            continue
    raise SystemExit(f"Datei {pfad} konnte nicht gelesen werden.")


def zahl(s):
    try:
        return int(s)
    except ValueError:
        return 0


def bereiche(nummern):
    """[1,2,3,5,7,8] -> '1–3, 5, 7–8'"""
    nummern = sorted(set(nummern))
    teile, start = [], None
    for i, n in enumerate(nummern):
        if start is None:
            start = n
        if i == len(nummern) - 1 or nummern[i + 1] != n + 1:
            teile.append(str(start) if start == n else f"{start}–{n}")
            start = None
    return ", ".join(teile)


def auswerten(zeilen):
    schueler = {}
    for z in zeilen:
        if len(z) <= FEHLTAGE or not z[NAME].strip():
            continue
        s = schueler.setdefault(z[NAME], {"klasse": z[KLASSE], "eintraege": []})
        if z[DATUM].strip():
            s["eintraege"].append(z)
    return schueler


def bericht(name, daten):
    e = daten["eintraege"]
    out = ["=" * BREITE, f"{name} ({daten['klasse']})", "-" * BREITE]
    if not e:
        out.append("keine Fehlzeiten")
        return out, (name, 0, 0, 0)

    verspaetet = [z for z in e if z[GRUND] == "verspätet"]
    fehl = [z for z in e if z[GRUND] != "verspätet"]
    std = sum(zahl(z[FEHLSTD]) for z in fehl)
    std_ne = sum(zahl(z[FEHLSTD]) for z in fehl if z[STATUS] != "entsch.")
    tage = {z[DATUM] for z in fehl}
    fehltage = sum(zahl(z[FEHLTAGE]) for z in e)
    gruende = Counter()
    for z in fehl:
        gruende[z[GRUND]] += zahl(z[FEHLSTD])

    out.append(f"Fehlstunden:  {std}  (entsch. {std - std_ne} | nicht entsch. {std_ne})")
    out.append(f"Fehltage:     {fehltage} (an {len(tage)} Tagen abwesend)")
    if verspaetet:
        minuten = sum(zahl(z[FEHLMIN]) for z in verspaetet)
        out.append(f"Verspätungen: {len(verspaetet)}× ({minuten} Min.)")
    else:
        out.append("Verspätungen: –")
    if gruende:
        out.append("Gründe:       " + ", ".join(f"{g} {n}" for g, n in gruende.most_common()))

    # Gruppieren nach Tag + Grund + Status
    gruppen = defaultdict(list)
    for z in e:
        gruppen[(z[DATUM], z[WOCHENTAG], z[GRUND], z[STATUS])].append(z)

    def sortkey(k):
        return datetime.strptime(k[0], "%d.%m.%y")

    out.append("Tage:")
    for key in sorted(gruppen, key=sortkey):
        datum, wtag, grund, status = key
        zs = gruppen[key]
        stunden = bereiche(zahl(z[STUNDE]) for z in zs)
        faecher = ", ".join(sorted({z[FACH] for z in zs}))
        status_txt = "entsch." if status == "entsch." else "NICHT entsch."
        if grund == "verspätet":
            umfang = f"{sum(zahl(z[FEHLMIN]) for z in zs)} Min (Std {stunden})"
        else:
            umfang = f"{sum(zahl(z[FEHLSTD]) for z in zs)} Std ({stunden})"
        out.append(f"  {wtag:<3} {datum}  {umfang:<14} {grund:<24} {status_txt:<14} {faecher}")

    return out, (name, std, std_ne, len(verspaetet))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("csv", help="WebUntis-Export AbsencePerStudent_*.csv")
    args = p.parse_args()

    schueler = auswerten(lese_csv(args.csv))
    uebersicht = []
    for name in sorted(schueler):
        zeilen, summe = bericht(name, schueler[name])
        print("\n".join(zeilen))
        print()
        uebersicht.append(summe)

    print("=" * BREITE)
    print("KLASSENÜBERSICHT (sortiert nach nicht entschuldigten Stunden)")
    print("-" * BREITE)
    print(f"{'Name':<28} {'Fehlstd.':>8} {'n. entsch.':>10} {'Verspät.':>9}")
    for name, std, ne, vs in sorted(uebersicht, key=lambda x: (-x[2], -x[1], x[0])):
        print(f"{name:<28} {std:>8} {ne:>10} {vs:>9}")


if __name__ == "__main__":
    main()
