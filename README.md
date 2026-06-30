# Tombola de la Fête des Écoles — Guy Gérard, Pacé

Site statique pour la tombola de la fête de l'école Guy Gérard. Conçu pour être hébergé gratuitement sur **GitHub Pages** et maintenu d'une année sur l'autre en quelques minutes.

## Structure du projet

```
.
├── index.html               ← page unique du site
├── styles/main.css          ← feuille de style
├── scripts/main.js          ← rendu des lots, recherche, gagnants
├── data/
│   ├── lots.js              ← 115 lots de la tombola (édité chaque année)
│   └── winners.js           ← numéros gagnants (rempli après le tirage)
└── assets/
    └── logos/               ← logos à fournir (apeegg.svg, ecole.svg, …)
```

## Mise en route locale

Comme le site charge `data/lots.js` et `data/winners.js` en `<script>`, il fonctionne directement par **double-clic sur `index.html`**.

Pour servir avec un mini-serveur (recommandé pour vérifier les chemins comme sur GitHub Pages) :

```bash
python3 -m http.server 8000
# puis ouvrir http://localhost:8000
```

## Mettre à jour les lots

Le fichier `data/lots.js` exporte `window.LOTS`, un tableau d'objets :

```js
{
  num: 1,                              // numéro original (CSV)
  rank: 1,                             // classement par valeur (auto-trié)
  title: "Switch 2",                   // titre principal
  description: "…",                    // détail (optionnel)
  sponsor: "APEEGG",                   // sponsor extrait automatiquement
  value: 419,                          // valeur en €
  category: "famille"                  // catégorie auto
}
```

Pour régénérer ce fichier depuis un nouveau CSV, garder à disposition le script Python utilisé pour la première génération (cf. l'historique du dépôt). Pour des **petites retouches**, il est plus rapide d'éditer directement `data/lots.js` à la main.

⚠️ Le script JS **trie les lots par valeur décroissante** automatiquement et met en avant les 3 premiers (podium) puis les 4 à 10 (coups de cœur). Pas besoin de gérer l'ordre soi-même.

## Saisir les numéros gagnants après le tirage

Une fois le tirage fait et les colonnes gagnants du Sheet remplies, on régénère
`data/winners.js` automatiquement depuis le CSV — **pas de saisie à la main** :

```bash
python3 scripts/csv_to_winners.py
```

Le script lit, dans le même CSV que les lots :

- **colonne A** — le n° du lot (même logique que `csv_to_lots.py`),
- **colonne E** — `N° du ticket gagnant`,
- **colonne F** — `NOM Prénom` du gagnant, **nom de famille en premier** (convention du Sheet).

Il écrit `window.WINNERS` et passe `window.DRAW_DONE = true;`. Chaque entrée :

```js
{ num: 1, ticket: "771", name: "Rock B." }
```

- `num` correspond au **numéro original** du lot (colonne `num` dans `lots.js`, pas le `rank`) ; les lots « bis » gardent leur libellé string (`"1 bis"`) pour matcher.
- `name` est **anonymisé pour l'affichage public** : prénom + initiale du nom de famille (`BAMENDU Rock` → `Rock B.`, `LE DU VICTOR` → `Victor L.`). Les noms de famille composés et les prénoms à trait d'union sont gérés.
- Les lots sans ticket renseigné (invendu, réservé) sont ignorés.

> ⚠️ Le script normalise la casse (`DESMARES BENJAMIN` → `Benjamin D.`) mais **ne peut pas réinventer les accents manquants** dans la source (`AGNES` → `Agnes`). Pour des accents corrects, les saisir dans le Sheet avant de relancer.

Une fois `data/winners.js` régénéré et committé, la section *« Les numéros gagnants »* affiche la liste, et chaque lot concerné porte la mention « Ticket gagnant n°XXXX ».

## Remplacer les logos

Déposer dans `assets/logos/` :

- `apeegg.svg` — logo de l'association des parents d'élèves.
- `ecole.svg` — logo de l'école Guy Gérard.

Formats acceptés : SVG (recommandé pour la netteté) ou PNG transparent.
Si les noms diffèrent, ajuster les `<img>` en haut de `index.html`.

## Déploiement sur GitHub Pages

1. Créer un dépôt GitHub et y pousser tout le dossier.
2. *Settings → Pages → Source* : choisir la branche `main` et le dossier `/ (root)`.
3. Le site est servi sur `https://<utilisateur>.github.io/<dépôt>/` quelques secondes après.

Aucun build, aucune dépendance — c'est juste du HTML + CSS + JS.

## Mettre à jour le contenu rédactionnel

- Date, lieu, heures : éditer la section `<section class="hero">` et `<section class="programme">` dans `index.html`.
- Texte de remerciements : section `<section class="thanks">`.
- Règlement : section `<section class="reglement">`. Le texte legal peut être totalement réécrit, la mise en page suit.

## Crédits techniques

- Typographie : [Fraunces](https://fonts.google.com/specimen/Fraunces) + [DM Sans](https://fonts.google.com/specimen/DM+Sans) (Google Fonts).
- Aucun framework, aucune librairie, ~30 ko de code.
