#!/usr/bin/env python3
"""
Convertit le CSV de la tombola en data/lots.js.

Usage :
    python3 scripts/csv_to_lots.py

Le CSV attendu est à la racine du projet (le fichier exporté depuis le
Google Sheet « 2026TOMBOLA lots_sponsors »). Format des colonnes utiles :
    A = N° du lot
    B = cellule multi-lignes contenant titre, description, ligne « Offert par … »
        et ligne « Valeur … »
    C = valeur formatée « 419,00 € »

Le script déduit aussi une catégorie via mots-clés. Tu peux ajuster
CATEGORY_KEYWORDS si une catégorie te semble fausse.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "2026TOMBOLA lots_sponsors.xlsx - 2026 trame site & gagnants.csv"
OUT_PATH = ROOT / "data" / "lots.js"

# Mots-clés -> catégorie. Le premier match gagne (l'ordre = priorité).
# La famille est testée AVANT le sport pour que les enveloppes type
# « escape game + breizh arena pour enfants » tombent en famille plutôt qu'en sport.
CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("gastro", [
        "fromag", "boulanger", "panier garni", "poulet", "huitre", "huître",
        "bourriche", "repas", "saint mélaine", "saint melaine", "primeur",
        "pasta", "crêpe", "crepe", "galette", "rôtisserie", "rotisserie",
        "fallafel", "haïtien", "haitien", "antillais", "tarte", "saveurs",
        "jus de pommes", "épicerie", "epicerie", "poissonnerie", "mat l'eau",
        "chez marina", "papilles", "le verger", "ferme du verger", "demay",
        "auguin", "gaïa", "gaia", "délices", "delices", "fabio",
        "chaudrons", "opi", "ostréiculteur", "ostreiculteur", "florus",
        "paciflore", "fleurist",
    ]),
    ("beaute", [
        "massage", "coiffur", "coupe + ", "shampoing", "shampooing",
        "salon de coif", "soin", "parfum", "vernis", "beauté", "ongle",
        "manucure", "embryolisse", "roger gallet", "renaissance",
        "frank provost", "lucie saint", "atelier des coiffeurs",
        "gautier", "klorane", "hei poa", "solinote", "savon", "hygiène",
        "hygiene", "girly", "lot corps", "piscine", "aqua ouest",
        "détente", "detente", "svr", "vichy", "avène", "avene",
    ]),
    ("mode", [
        "boucles d'oreilles", "bijou", "paillettes de marinette",
        "demi-sel", "doudou", "p'tit loup", "tilouloup", "mini loup",
        "baroudeurs", "tablier", "vacances", "tricheur", "alphab",
    ]),
    ("famille", [
        "parc", "zoo", "ferme", "kingoland", "branféré", "branfere",
        "planète sauvage", "planete sauvage", "gardenoo", "récrée",
        "recree", "naudières", "naudieres", "cobac", "manège", "manege",
        "champs libres", "espace des sciences", "terre nataé",
        "terre natae", "breizh arena", "regards de mômes",
        "regards de momes", "jardins", "ferme du monde", "harry potter",
        "sorciers", "switch", "nintendo", "lego", "loopiland",
        "rocher portail",
    ]),
    ("sport", [
        "escalade", "accobranche", "accrobranche", "crossfit", "escape",
        "ciné", "cine", "festival", "level 3", "rialto", "trampoline",
        "upper avenue", "the roof", "valkyrie", "son de gaston",
        "get out",
    ]),
    ("maison", [
        "déco", "deco", "affiche", "cadréa", "cadrea",
        "loisirs et couture", "decatlon", "décathlon", "decathlon",
        "chèque cadeau", "oxalys", "fromagerie guillaume",
    ]),
]


def parse_value(raw: str) -> float | None:
    """Transforme '419,00 €' en 419.0."""
    if not raw:
        return None
    cleaned = (
        raw.replace("\xa0", " ")
        .replace("€", "")
        .replace(" ", "")
        .replace(",", ".")
        .strip()
    )
    try:
        return float(cleaned)
    except ValueError:
        return None


def squash(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# On ne capture QUE les formes masculines (« offert » / « offerts ») — c'est la
# convention du Sheet pour signaler un partenaire principal. Les formes
# féminines (« offerte » / « offertes ») restent dans la description.
_OFFERT_PAR = re.compile(
    r"\s*[-–]?\s*offerts?\s+par\s+(.+)$",
    flags=re.IGNORECASE,
)


def parse_cell(num: int, raw: str, value_cell: str) -> dict:
    """Extrait title / description / sponsor / value depuis la cellule multi-lignes."""
    lines = [squash(line) for line in (raw or "").splitlines() if squash(line)]

    # Retire la ligne « Valeur … » : la valeur vient de la colonne dédiée.
    lines = [l for l in lines if not re.match(r"^Valeur\b", l, flags=re.IGNORECASE)]

    sponsor = ""
    # On cherche la PREMIÈRE occurrence de « offert par X » (peu importe la ligne)
    # et on coupe la ligne à cet endroit. Les occurrences suivantes restent en place
    # dans la description (utile quand un lot agrège plusieurs partenaires).
    for i, line in enumerate(lines):
        m = _OFFERT_PAR.search(line)
        if not m:
            continue
        sponsor = m.group(1).strip()
        prefix = line[: m.start()].strip()
        if prefix:
            lines[i] = prefix
        else:
            lines.pop(i)
        break

    title = lines[0] if lines else ""
    description = " · ".join(lines[1:]) if len(lines) > 1 else ""

    return {
        "num": num,
        "title": title,
        "description": description,
        "sponsor": sponsor,
        "value": parse_value(value_cell),
    }


def infer_category(lot: dict) -> str:
    haystack = " ".join([lot["title"], lot["description"], lot["sponsor"]]).lower()
    for category, keywords in CATEGORY_KEYWORDS:
        if any(k in haystack for k in keywords):
            return category
    return "famille"


def main() -> None:
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV introuvable : {CSV_PATH}")

    rows: list[tuple[int, str, str]] = []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0].strip().isdigit():
                continue
            num = int(row[0].strip())
            cell = row[1] if len(row) > 1 else ""
            value_cell = row[2] if len(row) > 2 else ""
            # Lignes réservées (numéro présent mais cellule vide) : on saute.
            if not cell.strip() and not value_cell.strip():
                continue
            rows.append((num, cell, value_cell))

    rows.sort(key=lambda r: r[0])

    lots: list[dict] = []
    for num, cell, value_cell in rows:
        lot = parse_cell(num, cell, value_cell)
        lot["category"] = infer_category(lot)
        lots.append(lot)

    # Classement par valeur décroissante (lots sans valeur en dernier).
    # Le n° de lot départage les ex æquo pour un ordre stable et reproductible.
    lots.sort(key=lambda l: (-(l["value"] or 0), l["num"]))
    for rank, lot in enumerate(lots, start=1):
        lot["rank"] = rank

    body = json.dumps(lots, ensure_ascii=False, indent=2)
    js = (
        "// Données des lots de la tombola — généré depuis le CSV.\n"
        "// Édite ce fichier pour mettre à jour la liste.\n"
        f"window.LOTS = {body};\n"
    )
    OUT_PATH.write_text(js, encoding="utf-8")
    print(f"OK : {len(lots)} lots écrits dans {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
