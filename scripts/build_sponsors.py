#!/usr/bin/env python3
"""
Génère data/sponsors.js à partir de data/lots.js.

Usage :
    python3 scripts/build_sponsors.py

Le script agrège la valeur cumulée donnée par chaque sponsor (les lots étant
des paniers multi-cadeaux, on ne compte pas le nombre de lots — ce n'est pas
un concours), puis associe à chaque sponsor un nom d'affichage propre et son
logo via la table SPONSOR_MAP ci-dessous. Les sponsors sont triés par la valeur
de leur lot unique le plus cher (décroissant), puis, à égalité, par la valeur
totale donnée (décroissant), puis par nom.

➜ POUR AJOUTER / CORRIGER UN LOGO :
   1. Dépose l'image dans le dossier sponsors/ (ex. sponsors/rialto.png).
   2. Ajoute (ou complète) une ligne dans SPONSOR_MAP :
        ("Le Rialto", "Le Rialto", "sponsors/rialto.png"),
      → 1er champ = nom tel qu'il apparaît dans les lots (sert à la corres-
        pondance, insensible aux accents/articles/casse) ;
        2e = nom affiché sur le site ; 3e = chemin du logo (ou None).
   3. Relance : python3 scripts/build_sponsors.py
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOTS_PATH = ROOT / "data" / "lots.js"
OUT_PATH = ROOT / "data" / "sponsors.js"


def clean_name(s: str) -> str:
    """Retire l'article initial, la queue « - valeur … » et les guillemets parasites."""
    if not s:
        return ""
    x = re.sub(r"\s+", " ", s).strip()
    x = re.sub(r"\s*[-–]\s*valeur.*$", "", x, flags=re.IGNORECASE)
    x = x.strip("\"“”'")
    x = re.sub(r"^l['’‘]", "", x, flags=re.IGNORECASE)
    return x.strip()


def norm(s: str) -> str:
    """Clé de correspondance : minuscules, sans accent, alphanum uniquement."""
    x = clean_name(s).lower()
    x = unicodedata.normalize("NFD", x)
    x = "".join(c for c in x if unicodedata.category(c) != "Mn")
    x = re.sub(r"[^a-z0-9]+", " ", x).strip()
    # Neutralise un article de tête (le/la/les/l) pour que « le Son de Gaston »
    # et « Son de Gaston » donnent la même clé de correspondance.
    x = re.sub(r"^(le|la|les|l)\s+", "", x)
    return x


# (correspondance dans les lots, nom affiché, logo|None) — trié par habitude visuelle.
SPONSOR_MAP: list[tuple[str, str, str | None]] = [
    ("APEEGG", "APEEGG", "assets/logos/apeegg.jpg"),
    ("APE GG", "L'APE GG", "assets/logos/apeegg.jpg"),
    ("Crossfit Valkyrie", "Crossfit Valkyrie", "sponsors/Crossfil valkyrie.jpg"),
    ("Leclerc Culturel Saint Grégoire", "Leclerc Culturel Saint Grégoire", "sponsors/leclerc culturel.jpg"),
    ("Carrefour Pacé", "Carrefour Pacé", "sponsors/Carrefour.png"),
    ("Chloé de Gaïa", "Chloé de Gaïa", "sponsors/chloé de gaia.png"),
    ("Forêt Adrénaline", "Forêt Adrénaline", "sponsors/Foret adrenaline.png"),
    ("Get Out", "Get Out", "sponsors/get out.jpg"),
    ("Aqua Ouest", "Aqua Ouest", "sponsors/aqua ouest.png"),
    ("La Crêpe Enchan'thé", "La Crêpe Enchan'thé", "sponsors/crepe enchathe.jpeg"),
    ("Sandrine Julou", "Sandrine Julou (massage Renaissance)", "sponsors/Renaissance.png"),
    ("Frank Provost (Grand Quartier)", "Frank Provost (Grand Quartier)", "sponsors/Frank provost.png"),
    ("R de fête", "R de fête", "sponsors/r de fete.png"),
    ("The Roof Rennes", "The Roof Rennes", "sponsors/The roof.png"),
    ("Les Paillettes de Marinette", "Les Paillettes de Marinette", "sponsors/paillettes marinette.png"),
    ("ostréiculteur Lomet de la baie de Cancale et la Rôtisserie du dimanche",
     "L'ostréiculteur Lomet de la baie de Cancale et la Rôtisserie du dimanche", "sponsors/ostréiculteur.png"),
    ("Son de Gaston", "Le Son de Gaston", "sponsors/son gaston.jpg"),
    ("Parc de Branféré", "Le Parc de Branféré", "sponsors/Parc de Branféré.png"),
    ("Mat l'Eau", "Mat l'Eau", "sponsors/Math l_eau.png"),
    ("institut Grand Large de Montgermont", "L'institut Grand Large de Montgermont", "sponsors/inst grand large.jpg"),
    ("association Regards de Mômes", "L'association Regards de Mômes", "sponsors/Pestaculaire.png"),
    ("coiffeur Lucie Saint Lyse", "Le coiffeur Lucie Saint Lyse", "sponsors/lucie st lise.jpg"),
    ("Planète Sauvage", "Planète Sauvage", "sponsors/planete sauvage.jpg"),
    ("Gardenoo", "Gardenoo", "sponsors/gardenoo.jpg"),
    ("récrée des 3 Curés", "La récrée des 3 Curés", "sponsors/récrée curés.jpg"),
    ("Escape Your Family", "Escape Your Family", "sponsors/escape family.jpg"),
    ("Level 3", "Level 3", "sponsors/Level 3.png"),
    ("Chaudrons Ambulant", "Le Chaudrons Ambulant", "sponsors/chaudron ambulant.jpg"),
    ("Zoo de la Bourbansais", "Le Zoo de la Bourbansais", "sponsors/zoo bourbansais.png"),
    ("parc des Naudières", "Le parc des Naudières", "sponsors/Parc des Naudières.png"),
    ("volailler La Haie du Val", "Le volailler La Haie du Val", "sponsors/la haie du val.png"),
    ("volailler La Rotisserie Pacéenne", "Le volailler La Rotisserie Pacéenne", "sponsors/rotisserie paceenne.png"),
    ("Cobac Parc", "Cobac Parc", "sponsors/cobac parc.png"),
    ("Florus", "Florus", "sponsors/florus.jpg"),
    ("Saint Mélaine à Pacé", "Le Saint Mélaine à Pacé", "sponsors/St melaine.png"),
    ("Office de Tourisme de Rennes", "Office de Tourisme de Rennes", "sponsors/tourisme rennes.jpg"),
    ("Primeur & Saveurs", "Primeur & Saveurs", "sponsors/primeur saveur.jpg"),
    ("librairie Et Cetera", "La librairie Et Cetera", "sponsors/etcetera.jpg"),
    ("Chez Marina", "Chez Marina", "sponsors/chez marina.jpg"),
    ("Fromagerie Guillaume à Pacé", "La Fromagerie Guillaume à Pacé", "sponsors/fromagerie guillaume.png"),
    ("Carbasson à Pacé", "Le Carbasson à Pacé", "sponsors/carbasson.png"),
    ("Jardines de Brocéliande", "Les Jardins de Brocéliande", "sponsors/Jardins brocéliande.png"),
    ("Upper Avenue", "Upper Avenue", "sponsors/Upper Avenue.png"),
    ("Au Paciflore", "Au Paciflore", "sponsors/paciflore.jpg"),
    ("Loisirs et Couture", "Loisirs et Couture", "sponsors/couture loisirs.jpg"),
    ("Rialto", "Le Rialto", "sponsors/Le rialto.png"),
    ("boulangerie OPI", "La boulangerie OPI", "sponsors/OPI.png"),
    ("ferme du Monde à Carentoir", "La ferme du Monde à Carentoir", "sponsors/ferme bout monde.jpg"),
    ("Super U l'Hermitage", "Super U l'Hermitage", "sponsors/super u.png"),
    ("traiteur de Spécialités haïtiennes et antillaises",
     "Le traiteur de Spécialités haïtiennes et antillaises", "sponsors/Spe antillaises.png"),
    ("champs Libres", "Les Champs Libres", "sponsors/les champs libres.png"),
    ("Noue Café à Pacé", "Le Noue Café à Pacé", "sponsors/Noue cafe.png"),
    ("parc Terre Nataé", "Le parc Terre Nataé", "sponsors/terre natae.png"),
]


# Donateurs co-contributeurs d'un même lot (lots multi-cadeaux garnis par
# plusieurs enseignes). Chacun est crédité de la VALEUR PLEINE du lot, et
# apparaît dans son propre encart — jamais fusionnés (ce sont des concurrents).
SPLIT: dict[str, list[str]] = {
    norm("Leclerc Culturel Saint Grégoire & Super U L'Hermitage"): [
        "Leclerc Culturel Saint Grégoire",
        "Super U l'Hermitage",
    ],
}


def donors_for(sponsor: str) -> list[tuple[str, str]]:
    """(clé de correspondance, nom brut) pour chaque donateur d'un champ."""
    key = norm(sponsor)
    if key in SPLIT:
        return [(norm(p), clean_name(p)) for p in SPLIT[key]]
    return [(key, clean_name(sponsor))]


def load_lots() -> list[dict]:
    text = LOTS_PATH.read_text(encoding="utf-8")
    m = re.search(r"window\.LOTS\s*=\s*(\[.*\]);", text, flags=re.S)
    if not m:
        raise SystemExit(f"Impossible de lire les lots dans {LOTS_PATH}")
    return json.loads(m.group(1))


def main() -> None:
    lots = load_lots()
    mapping = {norm(match): (name, logo) for match, name, logo in SPONSOR_MAP}

    agg: dict[str, dict] = {}
    for lot in lots:
        if not clean_name(lot.get("sponsor", "")):
            continue
        value = lot.get("value") or 0.0
        for key, raw in donors_for(lot["sponsor"]):
            entry = agg.setdefault(key, {"raw": raw, "total": 0.0, "max": 0.0})
            entry["total"] += value          # valeur cumulée (départage les égalités)
            entry["max"] = max(entry["max"], value)  # lot unique le plus cher (tri principal)

    sponsors = []
    unmapped = []
    for key, e in agg.items():
        if key in mapping:
            name, logo = mapping[key]
        else:
            name, logo = e["raw"], None
            unmapped.append(e["raw"])
        sponsors.append({
            "name": name,
            "logo": logo,
            "_max": round(e["max"], 2),
            "_total": round(e["total"], 2),
        })

    # Tri : lot le plus cher décroissant, puis valeur totale donnée décroissante,
    # puis nom (pour un ordre stable et reproductible).
    sponsors.sort(key=lambda s: (-s["_max"], -s["_total"], s["name"]))

    # On ne publie que nom + logo (les montants ne servent qu'au tri, non affichés).
    sponsors = [{"name": s["name"], "logo": s["logo"]} for s in sponsors]

    # Vérifie que les logos référencés existent réellement.
    missing_files = [s["logo"] for s in sponsors
                     if s["logo"] and not (ROOT / s["logo"]).exists()]

    body = json.dumps(sponsors, ensure_ascii=False, indent=2)
    js = "// Sponsors avec logos — généré par scripts/build_sponsors.py depuis data/lots.js.\n" \
         f"window.SPONSORS = {body};\n"
    OUT_PATH.write_text(js, encoding="utf-8")

    with_logo = sum(1 for s in sponsors if s["logo"])
    print(f"OK : {len(sponsors)} sponsors écrits ({with_logo} avec logo, "
          f"{len(sponsors) - with_logo} sans).")
    if unmapped:
        print(f"⚠ {len(unmapped)} sponsor(s) hors table (logo: null par défaut) : "
              + ", ".join(unmapped))
    if missing_files:
        print("⚠ Logos référencés mais fichiers introuvables : " + ", ".join(missing_files))


if __name__ == "__main__":
    main()
