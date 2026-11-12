# gabarit — cliques de conflit exactes, en temps constant en h

Programme Rust (sans aucune dépendance externe) qui produit les **témoins** du certificat
χ ≥ 7 de l'audit Sokolov–Voronov : une clique de 7 à 9 cellules deux à deux en conflit, les
paires de contraintes tendues à chaque sommet, et les milieux de Delaunay.

Il ne prouve rien. Il choisit. La preuve est le certificat Python (`audit_certificat3.py`,
repère w = 1/h, encadrements d'intervalles en arithmétique rationnelle exacte). Un gabarit est
donc une **conjecture** : s'il est faux, le certificat échoue — jamais l'inverse. C'est cette
séparation des rôles qui autorise la voie rapide en flottants sans compromettre la sûreté.

## Ce que ça change

| | avant (Python) | après (Rust) |
|---|---|---|
| construction du gabarit à h = 10 | 6,1 s | 0,08 ms |
| à h = 20 | 22 s | 0,06 ms |
| à h = 40 | 85 s | 0,06 ms |
| à h = 60 | 192 s | 0,06 ms |
| complexité en h | O(h²) tests de conflit | **O(log h)**, constant mesuré jusqu'à 10⁸ |
| fenêtre [20 ; 100] de la couverture | 413 s | **1,4 s** |

Mesures (`gabarit bench --eps 99/100`) : 0,03 à 0,17 ms pour h = 10, 10², 10³, 10⁴, 10⁵, 10⁶, 10⁸.
Le temps ne dépend plus de h.

## Les quatre réductions de complexité

**1. Corps de différences (mémoïsation structurelle).** Pour deux cellules translatées V et V + d,

    dmin(V, V+d) = dist(d, V − V),      dmax(V, V+d) = max_{z ∈ V−V} |z − d|.

Le polygone K = V − V ne dépend que du réseau. Calculé une fois (4 à 6 sommets), il ramène
chaque test de conflit à O(#K) = O(6) au lieu d'un calcul polygone-polygone en O(6 × 6).
C'est l'idée de l'algorithme GJK (Minkowski difference + support function) dépouillée de son
côté itératif : ici les deux corps sont *congruents*, donc K est fixe.

**2. Vecteurs pertinents de Voronoï.** Pour une base réduite (|g| ≤ 1/2, h ≥ √3/2), les facettes
de la cellule sont portées par ±b₁, ±b₂, ±(b₁ ± b₂) — huit candidats au plus (théorème de
Voronoï). Le code Python énumérait |v|² ≤ 4h², soit O(h) vecteurs, pour retrouver au plus six
facettes. Ici : O(1).

**3. Dichotomie sur le pas.** Dans une rangée j, deux cellules séparées de k se testent par
`conflict(k, 0)` — invariance par translation. L'ensemble des k en conflit est exactement un
intervalle [k₁, k₂] parce que deux prédicats sont monotones :

* `ε·dmax(k·b₁) ≥ D` est croissant (dmax² est convexe et 0 ∈ K, donc son minimum est en k = 0) ;
* `dmin(k·b₁) ≤ D` est décroissant (distance à un convexe contenant 0, le long d'un rayon).

Deux dichotomies en O(log D) donnent k₁ (le pas de la rangée) et k₂ (la portée). Plus
d'énumération linéaire.

**4. Candidats en nombre constant, glouton plutôt que clique maximale.** L'anneau des offsets
possibles (dmin ≤ D ⟹ |d| ≤ 2D ; dmax ≥ D/ε ⟹ |d| ≥ D/ε − D) est échantillonné au pas k₁ :
O(k₂/k₁) = O(1/√(1−ε²)) points par rangée — soit ~7 à 10 à ε = 99/100, **indépendamment de h**.
Il ne reste qu'à prendre 9 sommets deux à deux en conflit : un glouton en O(|c|·9) suffit.
Bron–Kerbosch à bitsets (Tomita, pivot + ordre de dégénérescence d'Eppstein) reste disponible
pour la validation et les cas marginaux.

**Total : O(log h) tests de conflit, O(1) candidats, aucun calcul de clique maximale.**

## Deux moteurs, et pourquoi

| | `--exact` (i128) | défaut (f64) |
|---|---|---|
| arithmétique | rationnelle entière, repère mis à l'échelle | flottante |
| rôle | **validation** : retrouve ω = 24 à h = 10 et ω = 16 à h = 20 (valeurs mesurées côté Python) | production : sélection des témoins |
| portée | h ≲ 10⁴ (au-delà, dd·h explose et les produits dépassent i128) | h ≲ 10⁹ |

Le repère entier exact coûte cher : ses coordonnées valent dd·h avec dd ~ 2h dès que g ≠ 0,
d'où des produits en (dd·h)⁴. En f64, aucun débordement dans la plage utile. La contrepartie
est assumée et bornée : en mode flottant, les conflits sont testés avec une marge relative de
1e-9, et le gabarit n'est qu'une conjecture soumise au certificat.

## Ce que le programme produit

`gabarit run --g 1/4 --h 20 --eps 99/100 --json` émet exactement le format attendu par
`audit_certificat3.motif_queue` (pont : `note/gabarit_rust.py`) :

```json
{ "centre": ["1/4","20"],
  "clique": [[0,0],[-1,-2],[2,-2],[-1,-1],...],
  "paires": [[[-1,0],[0,-1]],...],
  "mids":   [[0,0],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0]],
  "pts_mid": {...}, "pts_centre": [...], "omega": 9 }
```

Les points sont rationalisés au dénominateur 2²⁰ (le certificat vérifie ensuite, exactement,
que chaque témoin est bien dans sa cellule sur toute la boîte, et retire ceux qui n'y sont pas).

## Construire et tester

```sh
cargo build --release          # aucune dépendance
./target/release/gabarit selftest
./target/release/gabarit bench --eps 99/100 --hs 10,1000,1000000
./target/release/gabarit run --g 0 --h 1000000 --eps 99/100 --check
```

`selftest` vérifie : Bron–Kerbosch sur un K₅ ; ω exact à h = 10 et h = 20 contre les valeurs
Python ; que chaque paire des gabarits est un conflit **exact** (arithmétique i128, calcul
polygone-polygone indépendant du corps de différences) ; des coins anisotropes g ≠ 0.

## Ce que le moteur doit au certificat : `quant_in` (rétraction avant arrondi)

Les témoins transmis au certificat Python passent par une rationalisation au dénominateur
2²⁰ (`quant`, sortie JSON `motif_queue`). Or les sommets de cellule et les milieux de Delaunay
sont **sur le bord** de la cellule : arrondis au plus proche, ils sortent d'un epsilon, le
certificat les rejette (`PointHors`) et le Python les retire un à un. Ce détail de sortie a
coûté cher — voir plus bas.

`quant_in` rétracte donc le point d'un facteur `1 − 2⁻¹¹` **avant** d'arrondir : marge relative
de 5·10⁻⁴, très au-delà de la variation des contraintes d'appartenance sur une boîte de
certification. Ce n'est pas une hypothèse de preuve : `1 − 2⁻¹¹ < 1` et la cellule est convexe
et contient 0, donc le point rétracté est dans la cellule ; le certificat, lui, revérifie
l'appartenance exactement.

Effet mesuré sur les 60 boîtes des 30 fenêtres h ∈ [10, 10³¹] : **zéro retrait**, alors que
chaque boîte en déclenchait jusqu'à douze auparavant.

## Ce que ce moteur ne fait pas

Il ne prouve rien, et ne doit rien prouver : il **suggère** une clique et des témoins. Toute la
preuve est le certificat rationnel exact côté Python (`audit_certificat3.certifie_w`), qui
vérifie l'appartenance et les conflits sur toute la boîte. C'est ce qui autorise le flottant ici,
et c'est aussi pourquoi `--check` (mode exact i128) n'est qu'un contrôle de cohérence à petite
échelle : au-delà de h ≈ 5·10⁵ il ne s'applique plus (garde-fou), sans que la preuve en souffre.

## Limites connues

* **h < 3** : le motif n'est plus une rangée mais l'arrangement hexagonal ; la voie rapide ne le
  trouve pas. C'est le domaine du code Python, rapide à ces tailles (et déjà couvert).
* **Coin exactement hexagonal** (g = ±1/2, h = √3/2 ou h = 1) : la clique est marginale (ω = 7
  sans marge) et la tolérance relative de 1e-9 écarte les paires tangentes.
* **Garde-fou i128** : `Cell::build` refuse dd·h > 10¹² plutôt que de déborder silencieusement
  (le mode `release` enveloppe les dépassements sans paniquer).
* Les valeurs de ω de la littérature Python restent la référence ; celles du mode exact ont été
  retrouvées à l'identique (24 et 16), ce qui valide la géométrie, pas la preuve.

## Références utiles

* G. van den Bergen / E. Gilbert, D. Johnson, S. Keerthi — *GJK*, distance entre convexes via la
  différence de Minkowski et la fonction d'appui.
* G. Voronoï — vecteurs pertinents et facettes de la cellule : pour une base réduite,
  ±b₁, ±b₂, ±(b₁±b₂) suffisent.
* C. Bron, J. Kerbosch (1973), E. Tomita *et al.* (2006, pivot), D. Eppstein *et al.* (2010,
  ordre de dégénérescence, O(dn·3^{d/3})).
