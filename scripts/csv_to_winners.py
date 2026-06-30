#!/usr/bin/env python3
"""
Génère data/winners.js depuis le CSV de la tombola, APRÈS le tirage.

Usage :
    python3 scripts/csv_to_winners.py

Pendant de csv_to_lots.py (qui, lui, génère la liste des LOTS). Celui-ci se
lance une fois le tirage effectué et les colonnes gagnants du Sheet remplies.

Le CSV attendu est à la racine du projet (le même export que pour les lots).
Colonnes utilisées :
    A = N° du lot (même logique que csv_to_lots.py : entier, ou « 1 bis »)
    E = N° du ticket gagnant
    F = Nom & Prénom du gagnant, au format « NOM Prénom » (nom de famille
        EN PREMIER — convention du Sheet, cf. l'en-tête « Nom & Prénom »)

Anonymisation pour l'affichage public : on ne publie que le prénom et la
première lettre du nom de famille (ex. « BAMENDU Rock » -> « Rock B. »,
« LE DU VICTOR » -> « Victor L. »).
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "2026TOMBOLA lots_sponsors.xlsx - 2026 trame site & gagnants.csv"
OUT_PATH = ROOT / "data" / "winners.js"

# Index des colonnes (0-based) dans le CSV.
COL_TICKET = 4  # E : N° du ticket gagnant
COL_NAME = 5    # F : « NOM Prénom » du gagnant

# Numéro de lot : identique à csv_to_lots.py pour que les `num` soient du même
# type des deux côtés (le site matche gagnant <-> lot avec un `===` strict).
_LOT_NUM = re.compile(r"^(\d+)\s*(bis|ter)?$", flags=re.IGNORECASE)


def lot_num(raw: str):
    """Renvoie l'identifiant du lot : entier, ou libellé string pour « 1 bis »."""
    m = _LOT_NUM.match(raw.strip())
    if not m:
        return None
    return raw.strip() if m.group(2) else int(m.group(1))


def anonymize(raw: str) -> str:
    """« NOM Prénom » -> « Prénom I. » (prénom = dernier token, nom = 1er token).

    On garde le dernier token comme prénom (supporte les noms de famille
    composés type « LE DU »). Les prénoms composés à trait d'union restent
    entiers (« Marie-Helene »). Cas limite — un prénom composé séparé par une
    espace ne conserverait que son dernier mot ; absent des données 2026.
    """
    tokens = re.sub(r"\s+", " ", (raw or "")).strip().split(" ")
    tokens = [t for t in tokens if t]
    if not tokens:
        return ""
    if len(tokens) == 1:
        return tokens[0].title()
    first_name = tokens[-1].title()
    last_initial = tokens[0][0].upper()
    return f"{first_name} {last_initial}."


def main() -> None:
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV introuvable : {CSV_PATH}")

    winners: list[dict] = []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if not row:
                continue
            num = lot_num(row[0]) if row[0] else None
            if num is None:
                continue
            ticket = (row[COL_TICKET] if len(row) > COL_TICKET else "").strip()
            name_raw = (row[COL_NAME] if len(row) > COL_NAME else "").strip()
            # Pas de ticket = lot non tiré (invendu / réservé) : on saute.
            if not ticket:
                continue
            entry = {"num": num, "ticket": ticket}
            name = anonymize(name_raw)
            if name:
                entry["name"] = name
            winners.append(entry)

    body = json.dumps(winners, ensure_ascii=False, indent=2)
    js = (
        "// Numéros gagnants de la tombola — généré depuis le CSV.\n"
        "// Régénérer avec : python3 scripts/csv_to_winners.py\n"
        "// `num` = numéro du lot dans data/lots.js ; `name` = prénom + initiale du nom.\n"
        f"window.WINNERS = {body};\n"
        "window.DRAW_DONE = true;\n"
    )
    OUT_PATH.write_text(js, encoding="utf-8")
    print(f"OK : {len(winners)} gagnants écrits dans {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
