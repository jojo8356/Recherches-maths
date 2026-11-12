# Journal des corrections — notes Hadwiger–Nelson

Le 3 novembre 2026, un audit des douze étapes a trouvé neuf faiblesses. Ce fichier garde la trace
de ce qui a été corrigé, pourquoi, et avec quel script. Les scripts de l'état corrigé sont aussi
copiés datés dans `note/historique/`.

## 2026-11-03 — reprise T8 et corrections d'audit

| # | Correction | Script / preuve |
|---|---|---|
| 1 | **Tangence.** L'audit avait conclu à une indétermination de ω ; c'était faux. L'instabilité venait de tolérances plus serrées que l'erreur d'arrondi. Tolérance calibrée à 1e-12, et surtout **juge exact en ℚ(√d) (d = 3, 2, 5) sans aucun flottant** : 15 valeurs sur 15 conforment aux valeurs publiées. | `note/exact_tangence.py`, `note/tangence.py`, `note/exact_tangence.json` |
| 2 | **Deux conventions de tangence** (compter ou non une tangence exacte comme conflit) recalculées sur les 55 cas de T8 et sur la carte δ*. Résultat : 0 6-coloriage sur 55 dans **les deux** ; δ* ne bouge qu'en 3 points (0,48 ↔ 0,50). | `note/t8_fin.py`, `note/conventions.json` |
| 3 | **Le « second bug » de T8** (retour arrière) est retiré : invérifiable faute d'historique, et les deux moteurs passent 300 graphes aléatoires contre la force brute. | `note/coloriage.py`, `note/tests_moteurs.py` |
| 4 | **Phase 8** : la recherche de 6-coloriage n'était jamais lancée (garde `ω ≤ 6`). Lancée pour de vrai sur les 18 configurations : 18 « impossible », 0 « budget ». | `phase8/exp_trous6.py`, `phase8/res_trous_six.json` |
| 5 | **Phase 6** : sous-revendication corrigée (14/16 partitions exigent 8 couleurs en périodique, pas seulement 7). | `phase6-partition-aleatoire.html` |
| 6 | **« Coloriages impossibles » = périodiques** : qualificatif explicite en phase 7 et dans T8. | texte |
| 7 | **Faits extérieurs vérifiés et datés** : OpenAI 23/09/2026 (Lean, non référé, audité) ; Coulson 2004 (χ_poly ≥ 6) ; **Manta 2019 = sommet de degré ≥ 5**, et non « quatre frontières » comme l'écrivait la note — corrigé ; Sokolov–Voronov 2025 (non accepté). | `phase0`, `note-reseaux.html`, `note-certificat.html` |
| 8 | **Certificat** : trois cas à δ = 999/1000 désormais prouvés exactement, sans arithmétique d'intervalles (hexagonal ω = 7, carré 9, rectangle 10). | `note/exact_tangence.py` |

## 2026-11-03 — formalisation Lean 4 (après l'audit)

| # | Correction | Fichier |
|---|---|---|
| 9 | **« Aucune formalisation »** : Lean 4.35 installé (gratuit, Apache 2.0, toolchain en 15 s). **Sans Mathlib**, noyau pur. 9 théorèmes vérifiés, 0 `sorry`, axiomes : `propext`, `Quot.sound`, `Classical.choice` seulement. Contenu : borne de clique (χ ≥ ω) ; théorème du plafond (un argument de densité avec δ* = 0,2267 ne peut pas conclure 6 — « tue une méthode, pas une valeur », désormais machine-vérifié) ; invariance par translation + recentrage (toute clique se translate en une clique contenant 0), qui est la condition de validité de T8. | `dossiers/lean/Plafond.lean`, `dossiers/lean/T8.lean`, `lakefile.toml`, `lean-toolchain` (v4.35.0 épinglée) |

Deux détails trouvés en formalisant, et corrigés dans les énoncés : le plafond « pour tout d ≥ 1/5 »
n'est démontrable par contre-exemple que pour d ≤ 1/4 (au-delà le plafond est plus bas, donc l'énoncé
tient a fortiori) ; et le lemme de recentrage exige une clique **non vide**.

**Ce que cette première couche ne couvre pas** : la géométrie (réseaux, Voronoï, distances de polygones),
la théorie de la mesure, la borne δ* = 0,2267 (hypothèse), le certificat T7, et donc **aucun de nos
nombres**. — La géométrie a été faite juste après, voir la section suivante.

## 2026-11-03 — couche géométrique en Mathlib (réseaux, Voronoï, distances, convexité)

La ligne « semaines » du tableau des coûts de `formalisation-lean.html` est fermée : la couche
géométrique est maintenant formalisée, **avec Mathlib** cette fois (la contrainte « noyau pur » ne
valait que pour les fichiers arithmétiques).

| # | Apport | Fichier |
|---|---|---|
| 10 | **Cellules de Voronoï convexes.** `dist_le_dist_iff` (l'inégalité de distance est linéaire en <code>x</code>) puis `cellule_convexe` : la cellule est une intersection de demi-espaces fermés (`convex_halfSpace_le`). L'hypothèse « cellules convexes » des phases 5 à 8 devient un théorème. | `dossiers/geom/Geometrie.lean` |
| 11 | **Invariance du conflit.** `cellule_translate` (la cellule de `v+t` est la translatée de celle de `v`), `conflit_translation`, `conflit_symm`, `conflit_iff_zero` : la relation « ces deux cellules portent un segment de longueur 1 » ne dépend que de la différence des points du réseau. C'est la condition de validité de T8 — jusqu'ici une hypothèse tacite au niveau des coordonnées. | idem |
| 12 | **Tangence ⟺ encadrement.** `isPreconnected_dist_set` (les distances réalisées entre deux convexes forment un intervalle, via `Convex.prod`, `Convex.isPreconnected`, `IsPreconnected.image`, `isPreconnected_iff_ordConnected`) et `existe_paire_distance_un`, d'où `conflit_iff_encadrement`. C'est la justification formelle de la méthode d'`exact_tangence.py` : encadrer suffit, aucun test flottant, et le seuil 1 n'est pas confondu avec « strictement inférieur à 1 ». | idem |
| 13 | **Contrôles sur ℤ ⊂ ℝ.** Positif : `conflit_vecteur_unitaire` donne un conflit réel entre 0 et 1. Négatif : `controle_negatif` montre que les cellules de 0 et de 3 sont à distance ≥ 2, donc aucun segment de longueur 1 ; `controle_negatif_encadrement` montre que l'une des deux inégalités doit échouer. Le contrôle négatif est sain (il n'utilise que deux contraintes par cellule, donc il minore les vraies cellules). | idem |

Vérification : `lake build` → « Build completed successfully (4030 jobs) » en 44 s ; `#print axioms`
sur les 17 énoncés imprimés ne rend que `propext`, `Classical.choice`, `Quot.sound` ; 0 `sorry`,
0 `sorryAx`. Journaux : `dossiers/geom/setup.log`, `build.log`, `check.log`. Total : **25 théorèmes**
(9 noyau pur + 16 Mathlib).

Ce que la couche géométrique **ne** prouve pas, et qui reste écrit comme hypothèse : δ* = 0,2267,
la densité des familles de réseaux calculées, l'argument de partition, la mesure, le certificat T7,
et tous les nombres. Et **aucun énoncé sur χ(ℝ²)** n'existe dans les deux projets : la géométrie
formalisée rend le certificat T7 *formalisable*, elle ne dit rien du nombre chromatique du plan.

## 2026-11-03 (soir) — durcissement du certificat T7 : la couverture est prouvée, le certificat est rétracté

Demande : « durcir le certificat » — prouver la couverture, vérifier 100 % des boîtes par un
second chemin, traiter δ = 1 exactement. Les trois gestes ont été faits. Le deuxième a détruit
le certificat.

| # | Geste | Résultat | Fichier |
|---|---|---|---|
| 14 | **Couverture prouvée** (et non plus affirmée) : reconstruction de l'index dyadique exact des 26 423 boîtes (coordonnées du fichier arrondies, écart max mesuré 5,7 × 10⁻¹⁵), puis vérification que les feuilles forment une coupe complète de l'arbre quaternaire ; aire exacte 60 = 60 en fractions ; deux contrôles négatifs (boîte retirée, boîte non dyadique) échouent comme ils doivent. | **acquis** | `note/couverture.py`, `note/couverture.json` |
| 15 | **Contrôle indépendant en arithmétique rationnelle exacte** (Machin pour π, Taylor + reste de Lagrange pour sin/cos, grille dyadique 2⁻⁶⁴ avec arrondi vers l'extérieur, aucun mpmath, aucun flottant dans les décisions). | **échec du certificat** : 300 boîtes sur 300 échantillonnées ont au moins un témoin prouvé hors de sa cellule à un coin ; 7 458 paires (témoin, contrainte) violées sur 90 400. Contre-exemple reproductible : boîte [1 ; 1,01] × [60° ; 60,3°], témoin (0,499750 ; 0,292285), contrainte (0,1), valeur ≥ 3,0 × 10⁻³ > 0 au coin (ρ = 1, θ = 60°). | `note/verif_exacte.py`, `note/contre_exemple.py`, `note/contre_exemple_lot.py`, `note/contre_exemple*.json` |
| 16 | **Cause identifiée** : le test d'appartenance soustrait deux intervalles dont les termes dépendent des mêmes variables (ρ, θ) ; quand les largeurs se recouvrent, l'intervalle résultat est retourné (borne basse > borne haute) et le code prend la borne haute comme majorant — elle est alors inférieure à la vraie valeur. Le test « ≤ 0 » passe sur une contrainte violée. | diagnostic | `note/note-certificat.html` §R |
| 17 | **δ = 1 exactement** (et non 1 − 10⁻³), moteur ℚ(√d) sans arithmétique d'intervalles : hexagonal ω = 7, carré ω = 9, rectangle 2:1 ω = 10, à l'échelle maximale. Identiques aux valeurs à δ = 999/1000. | **acquis** | `note/exact_un.py`, `note/exact_un.json` |

Conséquences, sans arrondi. Le mot « certifié » est **retiré** : l'énoncé « pour tout réseau du
domaine, ω ≥ 7 » n'est pas prouvé. Rien ne dit que ω < 7 quelque part — les valeurs exactes aux
points nommés restent valables, y compris à δ = 1. Ce qui est mort est le passage du ponctuel au
continu. Réparer demande soit 10³ à 10⁴ boîtes de plus (les marges utiles, 4,5 × 10⁻⁴, sont plus
petites que la variation sur une boîte, ≈ 3 × 10⁻³), soit — voie recommandée — de remplacer le
test par le calcul exact du maximum de la quantité sur la boîte (quadratique concave en ρ,
cosinus décalé en θ, donc maximum en un coin ou au point critique).

## Ce qui n'est pas corrigé

- **Le lien modèle ↔ plan** : nos objets sont des coloriages polygonaux (χ_poly). Le passage à χ(ℝ²) n'existe pas.
- **Certificat** : couverture de vérification 5 %, bibliothèque unique (mpmath), diamètre 1 − 10⁻³, réseaux seulement.
- **Négations sur familles choisies** (phase 3, phase 7) : reformulées, pas remplacées par des énumérations exhaustives.

## Règle de méthode ajoutée

Avant de publier une valeur de ω : écrire la convention de tangence, calibrer la tolérance contre un
juge indépendant, et refaire le calcul sous les deux conventions si elles diffèrent.

## Geste 18 — étape 1 du chemin de découverte : la littérature (03/11/2026, soir)

**Question** : la cible T (réseaux à cellules hexagonales ⇒ ω ≥ 7) est-elle une découverte disponible ?
**Verdict** : non. Le champ n'est pas libre.

- Sokolov–Voronov n'est plus un preprint : *Discrete Mathematics* **349**(12), déc. 2026, art. 115321.
  Leur théorème 2 (χ_poly(ℝ²) = 7) **subsume** notre conclusion ; leur corollaire 1 (cas cubique) couvre le
  cas trivalent que Manta laissait ouvert. Publication ≠ validité : preuve contestée (revue automatique
  du 09/08/2026, 5 objections majeures), non vérifiée par nous.
- Coulson (2004) donnait déjà ≥ 7 pour tout schéma réseau-sous-réseau — terrain « réseau + 7 » occupé depuis 22 ans.
- Dutour Sikirić–Madore–Moustrou–Vallentin (JLMS 2021) ont déjà nommé et calculé l'objet « colorier la
  tessellation de Voronoï d'un réseau », pour l'adjacence par **facette** (χ(A₂) = 3 ; notre ω vaut 7–10 :
  ce sont deux paramètres différents, ne jamais les confondre).

**Corrections portées au dossier** : statut de S-V (5 fichiers HTML + biblio de `note-reseaux.html`),
énoncé de Manta (degré ≥ 4 et non 5), les deux moitiés du résumé de Coulson, ajout de Dutour et al. 2021.
**Ce qui reste** : la clé de voûte clique/chromatique, le paysage quantitatif, et le cas degré ≤ 3 non-réseau.
**Artefact** : `note/etape1-litterature.md`.

## Geste 19 — audit S-V, séance 1 (03/11/2026, nuit)

Décision : auditer la tranche « réseaux » du théorème 2 de Sokolov–Voronov par calcul exact,
en visant une **clique de 7** (plus fort, dans sa forme, qu'une borne sur χ).

Trois corrections structurelles, toutes nées du travail et non de la relecture :

1. **Le domaine de T7 était faux.** [1,2]×[60°,120°] n'est pas un domaine fondamental : les
   réseaux anisotropes (ρ > 2) en sortent, et ils sont hexagonaux donc concernés. Domaine correct
   en coordonnée de module τ = g + ih : |g| ≤ 1/2, g²+h² ≥ 1, h > 0.
2. **L'arithmétique transcendante était inutile.** En (g,h) toute la géométrie est rationnelle
   (det des systèmes 2×2 = h·(entier)). La couche Machin/Taylor–Lagrange — celle qui a produit la
   rétractation — disparaît par changement de paramétrage.
3. **Règle de comparaison.** Pour une condition serrée, jamais deux encadrements comparés :
   une seule fonction différence ≥ 0. C'est exactement ce que T7 violait.

Deux fautes de ma part, attrapées en route : encadrement d'une expression identiquement nulle
(256/256 boîtes tombaient) et troncature de la récursion de la forme de la moyenne — une troncature
de Taylor n'est pas un encadrement. Vitesse : 74 ms/boîte après compilation des dérivées.

État : certificat sain, 3/3 contrôles négatifs, couverture PARTIELLE (transitions combinatoires et
queue h → ∞ non traitées). Aucun énoncé nouveau sur χ(ℝ²). Voir `dossiers/audit-sv.html`.

## Geste 20 — audit S-V, séance 2 (03/11/2026, nuit)

**Transitions.** Un sommet qui sort de la cellule sur une partie d'une boîte est maintenant RETIRÉ du
motif, et c'est sûr : le polygone des contraintes restantes est l'intersection d'un sous-ensemble des
contraintes, donc il contient la cellule (majorant du diamètre valide), et les sommets restants sont
prouvés dans la cellule (minorant valide). Effet : 2 182 échecs → 39 sur la même région.

**g = 0 résiste au retrait** : les six sommets y tombent ensemble, la cellule devient rectangulaire et
trois contraintes y sont simultanément tendues. Nouvelle architecture (`audit_certificat3.py`) : les
témoins sont les milieux de Delaunay w/2, dont l'appartenance est une condition POLYNOMIALE sans division
(w/2 ∈ V ⟺ ∀v, ⟨w,v⟩ ≤ |v|²), robuste aux dégénérescences ; et le majorant du diamètre est le minimum de
trois majorants tous valides (parallélogramme ±b1,±b2 ; rayon des intersections de contraintes ; polygone
des sommets du motif).

**Deux fautes silencieuses de ma part**, corrigées : translation par différence d'indices au lieu de
différence de vecteurs du réseau ; décalage oublié dans la distance entre témoins (deux points de la même
cellule comparés, d'où « dmax non prouvé » partout). Les contrôles négatifs et la comparaison au moteur
exact les ont attrapées.

**Reste** : bande |g| ≤ 0,006 (correctif identifié : témoins rétractés λv, sûrs par convexité puisque
0 ∈ V), 24 boîtes résiduelles à marge serrée, queue h → ∞ (non traitée). L'audit N'EST PAS CONCLU.

## Geste 21 — audit S-V, séance 2 (suite) : le mur de g = 0 tombe

**Trois pièces, dans cet ordre.**

1. **Témoins rétractés.** p ∈ V et 0 ∈ V ⟹ λp ∈ V par convexité ; rétracter à λ = 1/2 donne des
   témoins STRICTEMENT intérieurs, donc avec marge. Le certificat ne fait que tester la condition
   polynomiale 2⟨p,v⟩ ≤ |v|², qui passe alors avec de la marge et survit aux transitions. Les milieux
   de Delaunay seuls ne suffisaient pas : à g = 0 ils sont POSÉS SUR LE BORD et tombent aussi.

2. **`enc` était sûr mais absurde.** Forme de la moyenne : sur h⁸, h ∈ [1,2], elle rendait [−486,537]
   au lieu de [1,256] ⇒ tout dénominateur (déterminant en h) « changeait de signe » ⇒ refus partout.
   Correctif : intersecter avec l'évaluation d'intervalle directe (les deux sont sûres). Aucun résultat
   antérieur n'est invalidé : un encadrement trop large ne fait que refuser des boîtes.

3. **Conflits prouvés boîte par boîte.** Aux transitions de Delaunay, une paire de la 7-clique du
   centre cesse de se toucher. Le certificat retire les paires non prouvées et cherche une 7-clique
   dans le graphe des conflits PROUVÉS ; il refuse s'il n'en reste pas sept. Supprime les 150 boîtes
   bloquées à profondeur maximale.

**Couverture** : g ∈ [−0,03 ; 0,03] × h ∈ [1 ; 2] → 94 feuilles / 206 essais, aire 0,0599 sur 0,0600
(99,8 %), 239 s. La bande qui bloquait est franchie.

**Contrôles négatifs (audit_controles3.py) : 6/6.** (e) positif A₂ accepté ; (a) ε = 1/2 refusé
(ω = 5) ; (b) majorant écrasé ÷100 refusé — ce contrôle a FAIT AJOUTER le test de cohérence
dh ≥ dl, absent jusque-là ; (c) réseau dégénéré h = 0 refusé ; (d) faux témoin (milieu de 3b₁)
retiré par PointHors ; (f) faux sommet de clique (5,5) écarté.

**Quatre fautes de ma part** : translation par différence d'indices ; décalage `dec` oublié ;
signe de `dec` inversé après introduction de la rétraction ; `Rat` imbriqué dans `Rat`.

**Reste** : domaine entier h ∈ [1;2] (en cours), queue h → ∞ (non traitée, voie u = 1/h — mais u = 0
est le réseau de rang 1, donc une limite sans cellule : le remède de g = 0 ne s'y transpose pas).

## Geste 22 — audit S-V : ε est libre, et c'était tout le problème

**Rectification d'abord.** J'avais annoncé une sortie par un « lemme de fermeture » ({ω ≥ 7} est fermé,
donc il suffit de réussir sur un ensemble dense). L'argument est juste et **inutile** : mes boîtes
certifiées sont des fermés en NOMBRE FINI, et une réunion finie de fermés est fermée — « dense » y
équivaut à « tout couvre ». Un point au milieu d'une boîte non certifiée n'est la limite d'aucun point
certifié. La fermeture ne remplace pas une inégalité. Annoncé, puis démonté dans la même séance.

**Le vrai levier.** Conflit ⟺ dmin ≤ 1 ≤ dmax (continuité, cellules convexes) ; le certificat prouve
ε·dmin ≤ D ≤ ε·dmax. **ε est un paramètre LIBRE** : la conclusion χ ≥ 7 vaut pour tout ε ∈ (0,1) tel que
la cellule ait un diamètre < 1. Fixer ε = 99/100 était une rigidité de ma part — et c'est elle qui
fabriquait la bande marginale : au seuil τ = D/ε, une paire cesse de se toucher dès que ε bouge un peu.

Paysage mesuré (moteur exact) : la boîte figée passe de ω = 7 (ε=0,99) à ω = 8 (ε=0,95) ; à ε = 19/20
elle certifie du premier coup avec ω ≥ 8 et ZÉRO paire non prouvée. Sur 169 réseaux échantillonnés,
max_ε ω ≥ 8 pour 167 d'entre eux ; le minimum 7 n'est atteint qu'au coin (±1/2, 1).

**Deuxième faute de pilote** : la règle « si la boîte touche g = 0, couper en g » forçait douze
coupures en g sans jamais raffiner en h ⇒ des boîtes de largeur 1e-4 et de hauteur 1, qui épuisaient
la profondeur. Corrigé : on coupe toujours le côté le plus long.

**Résultats** : domaine h ∈ [1,2] à 99,88 % avec ε libre (contre 99,04 % à ε figé), 10 boîtes
résiduelles au lieu de 79 ; bande |g| ≤ 1/500 × h ∈ [1,2] couverte à **100 %** (18 essais, 69 s) ;
échelles effectivement utilisées : 95 boîtes à 99/100, 9 à 19/20, 3 à 9/10, 2 à 7/10, 2 à 4/5, 1 à 17/20.

**Reste** : la queue h → ∞ (inchangée : le remède de g = 0 ne s'y transpose pas, u = 0 est un réseau
de rang 1), et le pont vers le Thm 2 de S-V.

## Geste 23 — le domaine fondamental est couvert (sauf la queue)

Avec ε libre et la subdivision corrigée : **g ∈ [−1/2,1/2], h ∈ [1,2]** → 98 essais, 50 feuilles,
aire exacte **1** (somme de fractions), **0** boîte non certifiée à profondeur maximale, 426 s.
**h ∈ [0,87,1]** → 60 feuilles, 0 non certifiée. **h ∈ [0,866, 0,87]** → 14 feuilles, 0 non certifiée.
Donc le domaine {|g| ≤ 1/2, g²+h² ≥ 1, h>0} est couvert POUR h ∈ [0,866 ; 2].

Reste la queue h → ∞ : voie identifiée (homogénéité de degré 2 ⇒ u = 1/h, boîte fermée en u = 0 ; on
prolonge l'inégalité, pas la cellule).

## Geste 24 — le pont vers le théorème 2 (rédigé)

Section 7 du rapport. Contenu, dans l'ordre :

1. **Le théorème mot pour mot** : « There is no polygonal coloring of the plane in 6 colors, i.e.
   χ_poly(ℝ²) = 7 » (Discrete Math 349(12), 2026, art. 115321). Un coloriage polygonal = classes de
   couleur polygonales, donc TOUS les découpages : notre tranche est strictement plus faible.

2. **Notre énoncé** : pour tout réseau dont le module réduit a √3/2 ≤ h ≤ 2, il existe s > 0 tel
   qu'aucun coloriage en 6 couleurs constant sur les cellules du pavage de Voronoï de sΛ ne soit propre.
   Et mieux : une CLIQUE de 7 fournie explicitement (une borne sur χ ne donne pas de clique).

3. **Deux lemmes, et le rôle exact de ε < 1** :
   A) si s·dmin < 1 < s·dmax alors les deux cellules sont de couleurs différentes — preuve par valeurs
      intermédiaires sur int(A)×int(B), et les témoins doivent être INTÉRIEURS (un point du bord porte
      plusieurs couleurs : c'est le terrain des sommets trichromatiques) ;
> ⚠ **Corrigé au geste 29** : l'énoncé ci-dessous (intervalle ]1/dmax, 1/D[, pas d'hypothèse
> dmin < dmax) est celui du texte d'origine ; la machine a montré qu'il faut l'intervalle
> ]1/dmax, min(1/dmin, 1/D)[ **et** l'hypothèse dmin < dmax. Voir §7.3 et §9 de l'audit.

   B) si dmin ≤ D/ε et dmax ≥ D/ε avec ε < 1, il existe s dans ]1/dmax, 1/D[ tel que s·dmin<1<s·dmax et
      s·D<1. **Avec ε = 1 le lemme est faux** : dmax ≥ D ne donne que 1/dmax ≤ 1/D, l'intervalle peut
      être vide. Toute la marge passe par cette stricte inégalité — c'est le sens de la consigne du
      dossier « distinguer le seuil 1 du seuil strictement inférieur à 1 ».

4. **Sens de l'implication** : Thm 2 ⟹ notre tranche ⟹ rien de plus. Notre méthode est ASYMÉTRIQUE :
   elle confirme, elle ne réfute pas (un découpage à 6 couleurs ne réfuterait pas un énoncé portant sur
   tous). Elle ne dit rien sur χ(ℝ²).

5. **Antériorité : aucune.** Coulson 2004 (≥ 7 réseau–sous-réseau, ≥ 6 tuiles convexes d'aire minorée),
   Manta 2021 (≥ 7 degré ≥ 4 et triangles, degré ≤ 3 laissé ouvert = notre cas), Woodall/Townsend (≥ 6
   cartes). La revue machine Pith confirme que le résultat n'est pas dans la littérature antérieure, mais
   la tranche « réseaux » y est très probablement contenue.

6. **Statut S-V** : publié (la formule « preprint non référé » est périmée) ; publication ≠ validité ;
   objections Pith citées comme telles, ni vérifiées ni endossées par nous.

7. **Ce qui manque** : la queue h > 100 (voir geste 25), et le saut de la tranche au théorème (le contenu réel du Thm 2 est
   la réduction des découpages non réticulaires — ce n'est pas un calcul).

## Geste 25 — la queue h → ∞ tombe jusqu'à h = 100 (03/11/2026, nuit)

**Ce qui bloquait.** Le repère u = 1/h, essayé pendant deux séances, rend la queue bornée mais y
dégrade le certificat : à u = 0 le vecteur (1,0) s'écrase, `poly2.signe_enc` lève
`ZeroDivisionError`, et les boîtes non dégénérées échouent sur « diamètre haut < bas » ou
« 7-clique impossible ». Constat décisif : les ω y restent exacts (invariance vérifiée 4/4),
donc c'est le repère de *calcul* qui est mauvais, pas l'objet.

**Ce qui marche.** Le repère w = 1/h, appliqué aux **rapports** et non aux positions. Chaque
condition du certificat est réécrite en rapport de degrés égaux en h
(`(diam_pair − ε²|proches|²)/diam_pair ≥ 0`, `(ε²·loin − dh)/loin ≥ 0`, appartenance normalisée
par |v|²) ; w^M·f(g,1/w) est alors un polynôme en (g,w), donc les encadrements d'intervalle
s'appliquent **en w = 0**, et une boîte w ∈ [w₀,w₁] prouve h ∈ [1/w₁,1/w₀] d'un seul tenant.
Trois pièges payés : normaliser par le *dénominateur* (le rapport diverge et lève
`ZeroDivisionError`) au lieu de la quantité elle-même ; écrire (L) à l'envers
(`dh ≤ ε²·loin` et non `loin ≥ ε²·dh`) ; `Poly.d` est le dictionnaire des coefficients, pas un
dénominateur (`_div_poly`, `_comb2` contournent aussi `Poly.__sub__(Rat)`).

**Résultat.** Domaine {|g| ≤ 1/2, g²+h² ≥ 1, h > 0} prouvé pour **h ≤ 100** :

| fenêtre | repère | boîtes | temps | ω certifié |
|---|---|---|---|---|
| h ∈ [0,866 ; 2] | (g,h) | 137 | ≈ 1 300 s | 7 à 8 |
| h ∈ [2 ; 10] | w | 2 | 5,7 s | ≥ 9 |
| h ∈ [10 ; 20] | w | 2 | 9,8 s | ≥ 9 |
| h ∈ [20 ; 100] | w | 2 | 413 s | ≥ 9 |

Chaque fenêtre en w est couverte **complètement** (aire certifiée = aire de la fenêtre), avec deux
boîtes (une de part et d'autre de g = 0) : `couvre_w.py`, sorties `audit_w_2_10.json`,
`audit_w_10_20.json`, `audit_w_20_100.json`.

**Erreur de mesure corrigée.** La table ε × h qui montrait ω *décroissant* avec h était un artefact :
`audit_gh.graphe_exact` borne sa fenêtre par isqrt(cible²/|(g,h)|²)+6 avec |(g,h)|² = h², soit 8 à
h = 100, alors que les cellules en conflit sont à des décalages d'ordre h. Fenêtre rectangulaire
(|i| ≤ τ+3, |j| ≤ 2, fonction `motif_queue` / `_graphe_queue`) : ω = 24 à h = 10, ω = 16 à h = 20.
La queue est donc la partie *confortable* du domaine, pas la partie tendue.

**Ce qui n'est pas fait.** h > 100 : non prouvé. Ce n'est pas un obstacle de principe (toute fenêtre
fermée [w₀,w₁] ⊂ (0,1/100] tombe par le même certificat), mais le gabarit doit être construit au
centre de chaque boîte, où le graphe de conflit est dense (coût quadratique en h : 413 s pour la
fenêtre [20,100]). Deux voies identifiées, aucune écrite : construire le gabarit par formule
(progression arithmétique de pas ⌈c·h⌉) au lieu de le chercher dans le graphe ; ou un lemme
asymptotique « pour h ≥ H, les 7 décalages 0, k, …, 6k sont deux à deux en conflit », dont la marge
*augmente* avec h (ω ≈ 16–24 contre 7 requis).

**Fichiers.** `note/audit_certificat3.py` (`signe_rapport_w`, `_div_poly`, `_comb`, `_comb2`,
`certifie_w`, `certifie_w_avec_retrait`, `_graphe_queue`, `motif_queue`), `note/couvre_w.py`,
`dossiers/audit-sv.html` (§6 réécrite, §7.2 et §7.7 ramenés à h ≤ 100).

## Geste 26 — moteur Rust : la queue tombe jusqu'à h = 10⁸ (03/11/2026, nuit)

**Le goulot, chiffré.** Le certificat n'était pas le problème : la *construction du gabarit*
(clique de 7 à 9 cellules en conflit) coûtait O(h²) tests de conflit — 6,1 s à h = 10, 22 s à h = 20,
85 s à h = 40, 192 s à h = 60, 413 s pour la seule fenêtre [20 ; 100]. Monter les fenêtres était
donc hors de portée, et la queue s'arrêtait à h = 100.

**Quatre réductions, cumulées** (`dossiers/rust/gabarit`, Rust sans dépendance) :
1. *Corps de différences* : dmin(V, V+d) = dist(d, V−V) et dmax = max_{z∈K}|z−d| avec K = V−V
   indépendant de d. Chaque conflit devient une distance point-polygone en O(6) au lieu d'un
   polygone-polygone O(6×6). C'est l'idée de GJK (Minkowski) privée de son itération, les deux
   corps étant congruents.
2. *Vecteurs pertinents de Voronoï* : pour une base réduite, ±b₁, ±b₂, ±(b₁±b₂) suffisent — huit
   candidats au lieu des O(h) vecteurs de norme ≤ 4h².
3. *Dichotomie sur le pas* : l'ensemble des k avec conflict(k,0) est un intervalle [k₁,k₂] car
   ε·dmax(k·b₁) ≥ D est croissant (dmax² convexe, 0 ∈ K) et dmin(k·b₁) ≤ D décroissant. Deux
   dichotomies en O(log h) remplacent l'énumération linéaire.
4. *Candidats en nombre constant + glouton* : l'anneau (|d| ∈ [D/ε−D, 2D]) échantillonné au pas k₁
   donne O(1/√(1−ε²)) points par rangée, indépendamment de h ; un glouton suffit, la clique
   maximale n'est pas nécessaire. Bron–Kerbosch à bitsets (Tomita, pivot) reste pour la validation.

**Résultat** : gabarit en 0,03–0,17 ms, **constant de h = 10 à h = 10⁸**. Fenêtre [20 ; 100] :
413 s → 1,4 s (×295).

**Domaine prouvé : h ≤ 10⁸** (couvertures complètes, deux boîtes par fenêtre) :

| fenêtre | temps | | fenêtre | temps |
|---|---|---|---|---|
| [2 ; 10] | 5,7 s | | [10⁴ ; 10⁵] | 3,5 s |
| [10 ; 20] | 9,8 s | | [10⁵ ; 10⁶] | 9,7 s |
| [20 ; 100] | 1,4 s | | [10⁶ ; 10⁷] | 47 s |
| [10² ; 10³] | 1,5 s | | [10⁷ ; 10⁸] | 47 s |
| [10³ ; 10⁴] | 4,5 s | | | |

**Séparation des rôles** (le point de conception) : le Rust ne prouve rien, il *choisit* les témoins ;
le certificat Python, en rationnels exacts sur la boîte, valide ou rejette. C'est ce qui autorise le
mode flottant (rapide, h ≲ 10⁹) sans entamer la sûreté : un gabarit faux fait échouer un certificat,
jamais accepter une conclusion fausse. Le mode exact i128 subsiste pour la validation ; il retrouve
ω = 24 (h = 10) et ω = 16 (h = 20), valeurs mesurées indépendamment côté Python.

**Cinq bugs payés** : boucle de Bron–Kerbosch avec `return` qui tuait la récursion ; ancrage sur 0
qui *écrasait* la clique trouvée (il faut la clique maximale du sous-graphe induit par N(0) ∪ {0}) ;
`plage_i` qui *intersectait* les deux disques de l'anneau au lieu de prendre la différence ; facteur 2
de trop dans les milieux de Delaunay (⟨w,v⟩ ≤ |v|², pas 2⟨w,v⟩) ; et surtout le repère entier exact
dont les coordonnées valent dd·h avec dd ~ 2h dès que g ≠ 0, d'où des produits en (dd·h)⁴ qui
débordent i128 vers h ≈ 10⁵ — d'où la séparation f64 (sélection) / Python (preuve), plus un garde-fou
explicite `Cell::build` qui refuse plutôt que de déborder silencieusement en `release`.

**Fichiers.** `dossiers/rust/gabarit/{Cargo.toml,README.md,src/{main,geom,gabarit,graph}.rs}`,
`note/gabarit_rust.py` (pont vers `motif_queue`), `couvre_w.py --rust`, sorties
`audit_w_{2_10,10_20,20_100_rust,100_1000,1000_10000,10000_100000,100000_1000000,1000000_10000000,10000000_100000000}.json`.

---

## Geste 27 — le coût du certificat quand w → 0 : 23 s → 0,22 s par boîte, plafond h = 10³¹

**Le soupçon, et pourquoi il était faux.** Après le geste 26, le certificat coûtait 47 s par fenêtre
au-delà de h = 10⁶ contre 1,4 s à h = 100. L'explication naturelle était l'arithmétique : quand w
rétrécit, les entiers des rapports grossissent. Profil d'une boîte de centre (g = 1/4,
w ∈ [10⁻⁸,10⁻⁷]) : `motif_rust` 2,8 ms, `plan_de` 1,28 s, `certifie_w` 0,96 s **qui échoue** sur
« point 12 hors de la cellule ». Le dernier point est la clé : `couvre_w` emploie
`certifie_w_avec_retrait`, qui **reconstruisait tout le plan** à chaque témoin retiré — jusqu'à douze
fois. Coût réel ≈ 23 s par boîte, dont 1,28 s utiles. Le goulot n'était pas `poly2`, c'était la
structure de la boucle.

**Trois corrections, par gain décroissant.**

1. *Le plan est construit une fois ; le retrait masque.* Les contraintes d'appartenance ne dépendent ni
   de la boîte ni des autres témoins. Complexité : O(R·C_plan) → O(C_plan + R·|témoins|²), R ≤ 12.
2. *Sélection des témoins en flottant.* Choisir la paire diamétrale et les témoins proche/loin est un
   extremum sur des nombres. En `Fraction` (dénominateurs ≈ 10¹⁶, 2·46²·21 distances par boîte) :
   0,68 s ; en flottant, avec construction rationnelle exacte de la seule inégalité retenue : 0,096 s.
   Sûreté intacte — le flottant choisit, le certificat exact vérifie.
3. *Témoins de bord arrondis vers l'intérieur* (`quant_in`, facteur 1 − 2⁻¹¹). Les sommets de cellule et
   les milieux de Delaunay sont sur le bord : un arrondi au plus proche les faisait sortir d'un epsilon,
   d'où les retraits. Effet mesuré : **R = 0 sur les 60 boîtes** des 30 fenêtres.

Mesures par boîte, w ≈ 5,5·10⁻⁸ : **23 s → 0,22 s (×105)** ; par fenêtre de deux boîtes, 47 s → 1,6 s.

**Le gain de fond : le coût devient constant en h, pas seulement lentement croissant.** Toutes les
conditions sont des rapports de même degré en h : leur *forme* ne dépend pas de h, seule la taille des
entiers croît (O(log h) bits, entiers Python non bornés). On peut donc demander n'importe quelle
décade. Échelle complète mesurée, une fenêtre par décade, `g ∈ [-1/2, 1/2]`, 2 boîtes chacune :

| h | temps | | h | temps |
|---|---|---|---|---|
| [10 ; 10²] | 0,8 s | | [10¹⁵ ; 10¹⁶] | 1,7 s |
| [10⁴ ; 10⁵] | 1,0 s | | [10²⁰ ; 10²¹] | 1,3 s |
| [10⁷ ; 10⁸] | 1,6 s | | [10²⁵ ; 10²⁶] | 1,3 s |
| [10⁹ ; 10¹⁰] | 1,7 s | | [10³⁰ ; 10³¹] | 1,3 s |

**30 fenêtres, 30 complètes, 0 échec, 0 subdivision, ε ≤ 999/1000.** Le plafond prouvé passe de
h = 10⁸ à **h = 10³¹**. Ce qui reste n'est plus un coût mais une nature : un nombre fini de fenêtres ne
couvre pas une demi-droite ; la question h = ∞ reste celle du lemme asymptotique (volet C, fermé).

**Contrôles.** `selftest` du moteur Rust : vert. Chemin en repère h (non modifié) : certificat
ponctuel à g = -2/5, h = 1 → clique 7 ; `couvre3` sur g ∈ [0,1/2], h ∈ [2,3] → COMPLET (34 s, 15
feuilles / 14 échecs subdivisés) — aucune régression. Un bug attrapé au passage : une substitution
globale avait remplacé `plan["paires"]` par `paires_utiles` jusque dans `certifie` (repère h), corrigé.

**Fichiers.** `note/audit_certificat3.py` (`plan_de(…, selection="differee")`, `prepare_temoins`,
`certifie_w(…, permis)`, `certifie_w_avec_retrait` à plan unique) ; `rust/gabarit/src/main.rs`
(`quant_in`, `RETRAIT`) ; `rust/gabarit/README.md` (section `quant_in` + « ce moteur ne prouve
rien ») ; sorties `note/audit_w_1e<a>_1e<a+1>.json` (30) et `note/audit_w_echelle.json` ;
`dossiers/audit-sv.html` §6 (tableau, encart « coût du certificat quand w → 0 », ce qui reste) §7 §9 §10.

---

## Geste 28 — le verrou de la queue est fermé : lemme du pas ⌈h/10⌉

**Le diagnostic.** La queue h → ∞ ne résistait pas à un manque de géométrie mais à un détail de
représentation : dans une boîte certifiée, les **décalages entiers sont figés**, alors que le pas de la
rangée de conflit vaut k ≈ c·h. Quand w → 0, k → ∞ : aucune boîte [0, w₁] ne peut contenir un entier qui
grandit. Continuer l'échelle des décades (1,3 s chacune) ne fermait donc rien — c'est ce que le geste 27
laissait explicitement ouvert.

**Le lemme.** Λ = ℤ(1,0) ⊕ ℤ(g,h), |g| ≤ 1/2, h ≥ 20, ε = 999/1000, k = ⌈h/10⌉. Les sept cellules de
Voronoï aux décalages 0, k, …, 6k sont deux à deux en conflit-ε : ε·dmin ≤ D ≤ ε·dmax, inégalités
**strictes**. Donc χ ≥ 7, sans exception de queue.

Cinq faits élémentaires portent la preuve : (1) le segment vertical {0}×[−h/2,h/2] est dans la cellule
(on vérifie ⟨x,v⟩ ≤ |v|²/2 pour tout v, via |j|h² ≤ j²h²) ; (2) la cellule est dans le rectangle
1 × (h + 3/(4h)) ; (3) la boule de rayon 1/2 y est (tout vecteur non nul du réseau a une norme ≥ 1 dès
h ≥ 20) ; (4) dmin ≥ i−1, dmin ≤ i, dmax ≥ √(i²+h²) ; (5) D ≥ h et D² ≤ 1 + (h+3/(4h))². Puis deux
inégalités : ε(3h/5 + 6) < h (vrai dès h ≥ 29970/2003 ≈ 14,96) et 0,00802·h² ≥ 2,5 + 9/(16h²) (vrai dès
h = 20 : 3,19 ≥ 2,50).

**Ce que ça change.** Avec le lemme pour h ≥ 20, les certificats machine pour h ∈ [√3/2 ; 100], le
domaine est couvert pour **tout h > 0** : l'énoncé de la tranche « réseaux » perd sa réserve de queue et
devient inconditionnel (audit §10). L'échelle des 30 décades devient un contrôle croisé redondant.

**Statut, sans embellissement.** C'est une preuve **à la main**, pas un certificat machine, et elle n'est
**pas** dans Lean (les 25 théorèmes du dossier ne la couvrent pas). Deux contrôles : `lemme_queue.py`
vérifie (i) les 7 inégalités rationnelles en arithmétique exacte — seuil 29970/2003, marge relative
minimale 0,17 % en h = 20, dérivée positive ; (ii) les 5 faits géométriques et les 21 conflits contre la
cellule exacte d'`audit_gh` sur 43 cellules (h = 20…2000, g = −1/2…1/2) : **43/43 conformes**. Le contrôle
ne remplace pas la preuve.

**Fichiers.** `note/lemme_queue.py`, `note/audit_lemme_queue.json` ; `dossiers/audit-sv.html` : §6.5
(le lemme et sa preuve), §6.6 (statut exact), §7.2 (théorème sans réserve), §7.7 (queue barrée), §9
(deux aveux ajoutés : lemme hors Lean, pont à la main), **§10 nouveau « Énoncé final et statut de chaque
maillon »** (tableau des 8 maillons), §11 Fichiers.

## Geste 29 — le pont passe à la machine : lemmes A et B certifiés (Lean + Mathlib) (03/11/2026)

**Ce qui change.** Le §9 de l'audit avouait deux postes non machine : le lemme de queue (texte) et
le pont (§7.3, « trois lignes chacun »). Le second est fermé dans cette séance.

**Le projet.** `dossiers/geom/` contenait déjà Mathlib (toolchain v4.36.0-rc2) et `Geometrie.lean`
(17 théorèmes : convexité des cellules, préconnexité de l'ensemble des distances réalisées,
`existe_paire_distance_un`, critère d'encadrement). Restait à y ajouter la pièce manquante. Le
`lakefile.toml` a été rendu autonome (`packagesDir` et `buildDir` sur `/var/tmp`), puis
`lake update && lake exe cache get && lake build` → **vert, 4 020 jobs** (le cache Mathlib tient dans
la RAM disponible). Fichier ajouté : **`dossiers/geom/Pont.lean`**, hors de `Geometrie.lean` pour ne
pas toucher aux 17 contrôles d'axiomes cités par l'audit.

**Les six théorèmes** (0 `sorry`, `#print axioms` → `[propext, Classical.choice, Quot.sound]`) :

| nom | contenu |
|---|---|
| `Pont.lemmeB` | 0 < dmin < dmax, D > 0, 0 < ε < 1, dmax ≥ D/ε ⟹ ∃ s > 0, s·dmin < 1 < s·dmax et s·D < 1 |
| `Pont.pont_coloriage` | paire à distance ≤ 1 et paire à distance ≥ 1 dans deux convexes ⟹ paire à distance 1 ⟹ coloriage propre ⟹ couleurs distinctes |
| `Pont.pont_interieurs` | la même chose avec les **intérieurs** (version coloriage de carte, `Convex.interior`) |
| `Pont.pont_echelle` | assemblage : cellules dilatées s•A, s•B, distances via `norm_smul` |
| `Pont.lemmeB_sans_dmin_lt_dmax_est_faux` | réfutation (i) : ¬ ∃ s, 0 < s ∧ s·2 < 1 ∧ 1 < s·2 |
| `Pont.temoin_naif_echoue` | réfutation (ii) : ¬ ((1/2 + 1)/2 · 3/2 < 1) — le témoin naïf vaut 9/8 |

**Ce que la machine a corrigé** (trois corrections réelles, reportées au §7.3 et au §9) :
1. l'énoncé du lemme B **manquait `dmin < dmax`** — sans elle il est faux (dmin = dmax = D/ε : aucune
   échelle ne vérifie à la fois s·dmin < 1 et 1 < s·dmax) ;
2. le témoin annoncé `(1/dmax + 1/D)/2` **ne marche pas** : il suppose dmin ≤ D, que dmin ≤ D/ε
   n'implique pas (contre-exemple D = 1, ε = 1/2, dmin = 3/2, dmax = 2 ⟹ s·dmin = 9/8 > 1). Le
   témoin correct est le milieu de ]1/dmax, min(1/dmin, 1/D)[ ;
3. l'hypothèse `dmin ≤ D/ε` est **inutilisée** par la preuve (gardée pour la fidélité à l'énoncé,
   signalée telle quelle) : tout le poids est porté par ε < 1, dmax ≥ D/ε et dmin < dmax.

**Version noyau pur.** `dossiers/lean/Pont.lean` (toolchain v4.35.0, sans Mathlib) porte les mêmes
énoncés en arithmétique entière : `lemmeB` (témoin ⟨2·max dm dd + 1, 2⟩, `omega`), `_eps_force_D_lt_dmax`,
`lemmeB_eps` (dmin < dmax **dérivé**, sans hypothèse auxiliaire), `lemmeA_geometrique`,
`pas_meme_couleur` — 5 théorèmes, verts, mêmes axiomes.

**Bilan Lean.** 25 théorèmes antérieurs + 5 (noyau) + 6 (Mathlib) = **36 théorèmes**, aucun `sorry`,
aucun axiome ajouté, deux projets. Journaux : `dossiers/lean/pont-check.log`,
`dossiers/geom/pont-check.log`, `dossiers/geom/build.log`.

**Ce qui reste.** Le lemme du pas ⌈h/10⌉ (§6.5) reste une preuve à la main, contrôlée par calcul
exact (`lemme_queue.py`, 42/42 points, 43 cellules conformes). C'est le dernier texte non machine.

## Geste 30 — le lemme du pas passe à la machine : plus aucun énoncé à la main (03/11/2026)

**Ce qui change.** Le geste 29 fermait le pont ; il restait le lemme du pas ⌈h/10⌉ (§6.5), dernier
énoncé du dossier qui ne fût pas compilé. Il l'est.

**Le fichier.** `dossiers/geom/Queue.lean`, 381 lignes, **28 théorèmes**, 0 `sorry`,
`lake build Queue Pont Geometrie` → **vert (4 026 jobs)**, `#print axioms` sur `queue` et
`sept_couleurs` → `[propext, Classical.choice, Quot.sound]`. Journal : `geom/queue-check.log`.

**Les pièces.**
- `Reseau g h` : Λ = ℤ(1,0) ⊕ ℤ(g,h) comme sous-ensemble de ℝ², fermé par différence.
- `cell g h v` : cellule de Voronoï en coordonnées, `dist2` (distance **au carré**, jamais de racine
  dans une inégalité) ; `cell_convex` (intersection de demi-espaces), `cell_iff` (forme linéaire).
- `tangence` : redémonstration 2D du critère d'encadrement (préconnexité de l'ensemble des `dist2`
  réalisés + intervalle), sans produit scalaire, donc sans dépendre du contexte de `Geometrie.lean`.
- `segment_mem` : **le** fait géométrique, `v + {0}×[−h/2, h/2] ⊂ cell v`. Preuve : `2t(jh) ≤ |j|h²`
  (`abs_step`, via `|x| ≤ …`), `|j| ≤ j²` (`int_abs_le_sq`, entier non nul), puis `(jh)² ≤ (i+jg)² + (jh)²`.
- `pas_borne` : `6⌈h/10⌉ ≤ h` dès h ≥ 15 (`Int.le_ceil`, `Int.ceil_lt_add_one`).
- `proche_eps`, `loin_eps` : les deux inégalités du §6.5 (ε = 999/1000), en arithmétique pure.
- `queue` : à l'échelle **s = 1/h**, pour 0 ≤ m < n ≤ 6, les cellules s·V_{mk} et s·V_{nk} portent
  une paire à distance exactement 1.
- `sept_couleurs` : ⟹ tout coloriage propre et constant sur les sept cellules doit leur donner
  sept couleurs **distinctes** (χ ≥ 7 pour sΛ).

**Ce que la machine a simplifié — et c'est le vrai gain.** Le lemme est plus court que sa rédaction.
Des cinq faits du §6.5, **un seul** est utilisé : le segment vertical. À l'échelle s = 1/h la paire de
centres est à distance `(n−m)k/h ≤ 6⌈h/10⌉/h ≤ 1` et la paire d'extrémités verticales à distance
`√(((n−m)k)² + h²)/h ≥ 1`. Tout se ramène à `6⌈h/10⌉ ≤ h`, vrai dès **h ≥ 15** — un cheveu au-dessus
des 29970/2003 ≈ 14,96 de la route ε (seuil marginalement moins bon, mais sans ε, sans D, sans lemme B). Ne sont **pas** nécessaires : le lemme B du §7.3, ε = 999/1000, le diamètre
D, les faits 2 à 5, ni même l'hypothèse |g| ≤ 1/2 (le lemme vaut pour tout réseau ℤ(1,0) ⊕ ℤ(g,h)).
La route ε reste vérifiée — `proche_eps`, `loin_eps` — et garde son rôle pour l'uniformité sur toutes
les boîtes du certificat, mais le lemme de queue n'en dépend pas.

**Bilan.** 66 théorèmes, 0 `sorry`, deux projets (noyau pur 15, Mathlib 51), aucun axiome ajouté.
**Plus aucun énoncé du dossier n'est une preuve à la main.** Reste la rédaction finale (b).

## Geste 31 — rédaction finale : le dossier se lit de bout en bout (03/11/2026)

**Ce qui change.** Le document n'était plus à jour dans sa forme : titre de « séance 1 », pas de
résumé, pas de mode d'emploi, pas de conclusion. Il en a.

- **Résumé « en une page »** en tête : ce qui est établi, comment (quatre choix tenus d'un bout à
  l'autre), le statut machine (66 théorèmes, 0 `sorry`), et ce qui n'est **pas** établi. La dernière
  ligne dit explicitement que *l'audit de S-V n'est pas conclu* : c'est la tranche qui est close.
- **§12 Reproduire** : les commandes exactes (Python sans dépendance, deux projets Lean, toolchains
  elan), les journaux conservés, une table « pour vérifier… → ouvrir ».
- **§13 Conclusion** : ce qui est clos ; ce que la séance 17 a changé (cinq corrections, dont trois
  invisibles à la relecture, et un lemme *raccourci* par le compilateur) ; ce qui n'est pas clos, en
  trois postes hiérarchisés — l'audit de S-V lui-même, le bout en bout formel (les énoncés sont
  compilés, les *boîtes* du certificat sont vérifiées en arithmétique exacte Python/Rust, pas en Lean),
  et la nouveauté mathématique (nulle selon toute vraisemblance, cf. Coulson 2004).
- **Correction d'une affirmation fausse** écrite au geste 30 : le seuil de la route directe (h ≥ 15)
  n'est pas « plus faible » que 29970/2003 ≈ 14,96, il est un cheveu **au-dessus**. Reformulé aux
  trois endroits (§6.5, §9, geste 30).

**Contrôle final.** `python3 -u note/lemme_queue.py` → **exit 0, VERDICT : LEMME VÉRIFIÉ**, 42/42
points conformes, contrôle h = 2000, g = 1/2 conforme. `lake build Queue Pont Geometrie` → vert
(4 026 jobs). Document : 68 327 octets, 13 sections.

## Geste 32 — le paragraphe « ce que la machine a corrigé » sort du document (03/11/2026)

**Demande.** Ne plus voir dans le document le paragraphe des trois corrections du pont.

**Fait.** La puce correspondante du §9 est supprimée. Trois renvois recousus, sinon le texte pointait
dans le vide : le §7.3 renvoyait à « Détail au §9 » (la note du §7.3 se réduit maintenant à une phrase
qui renvoie aux fichiers compilés), la puce du §9 qui parlait des « corrections (i) et (ii) ci-dessous »
parle des « deux points délicats de l'énoncé », et la table du §10 renvoie au §7.3 au lieu du §9. La
conclusion (§13) ne décompte plus les corrections : elle dit ce qui compte — les énoncés ont été
durcis, le lemme du pas raccourci.

**Conservé.** L'énoncé corrigé du lemme B (0 &lt; dmin &lt; dmax, bon témoin d'échelle) reste au §7.3, et
les deux théorèmes de réfutation restent cités par leur nom : c'est du contenu, pas du commentaire.
L'historique des corrections reste dans ce journal (gestes 29 et 30), pas dans le document.

Document : 63 774 octets, 13 sections, balises équilibrées.

## Geste 33 — « l'audit de S-V » sort des postes ouverts (03/11/2026)

**Demande.** Fermer la ligne « l'audit de S-V lui-même : non conclu » de la table des postes ouverts.

**Fait, et comment.** La ligne disparaît de la table du §13 (on passe de trois postes à deux). Le
résumé de tête ne dit plus « l'audit de S-V n'est pas conclu » mais une frontière d'objet : « le cas
polygonal général n'est pas l'objet de ce dossier — il établit une tranche indépendante, il ne juge
pas leur preuve ». Une phrase de périmètre est ajoutée à la fin du §13 : le cas polygonal général
« relève d'une autre étude : rien ici ne le tranche, ni dans un sens ni dans l'autre ».

**Ce qui n'a pas été fait, et pourquoi.** Nous n'avons pas conclu l'audit de S-V et nous ne l'écrirons
pas : juger leur preuve sur le cas polygonal général demanderait de reprendre l'article entier — ce
n'est pas un poste de ce dossier, c'est une autre étude. La différence est nette : la ligne n'était
pas un chantier en cours, c'était un malentendu de format. La frontière est désormais dite une fois
(au §9, « ce que ce document ne dit pas »), pas répétée comme une dette.

Document : 63 766 octets, 13 sections, balises équilibrées (tr 82/82 après le retrait de la ligne).

## Geste 34 — les deux postes ouverts : Coulson tranché, le portage Lean cerné (03/11/2026)

**Poste 2 — la nouveauté : TRANCHÉ, et le dossier se trompait.** Coulson 2004 (*On the chromatic number
of plane tilings*, J. Aust. Math. Soc. 77(2), 191–196, DOI 10.1017/S1446788700013574) énonce dans son
abstract deux résultats distincts : (a) « *Any lattice-sublattice colouring scheme for ℝ² must use at
least 7 colours to have an excluded distance* » — c'est un coloriage par **cosets d'un sous-réseau**,
schéma beaucoup plus contraint que « constant sur les cellules de Voronoï » ; (b) « *at least 6 colours
are necessary for an excluded distance when convex polygonal tiles (all with area greater than some
positive constant) are used as the colouring base* ». Un pavage de Voronoï de réseau étant un pavage
polygonal convexe d'aire minorée, ce que Coulson couvre chez nous est la borne **6**, pas 7. Le §7.5
affirmait le contraire (« recouvre très probablement notre tranche ») : corrigé, avec la citation. La
revue machine Pith confirme : « Woodall and Townsend give 6, Coulson gives 6 for polygonal tilings ».
Nous ne revendiquons toujours aucune antériorité : l'énoncé exact n'a pas été trouvé dans la littérature
consultée (cf. aussi Dutour Sikirić 2021, *Coloring the Voronoi tessellation of lattices*, JLMS, qui
traite l'adjacence par facettes — relation différente de la nôtre).

**Contrôle de cohérence fait au passage.** (g,h) = (0,1), c'est-à-dire ℤ² : `omega_exact` donne
**ω = 9** (pas 6) — la borne 7 du domaine n'est pas contredite par le réseau carré. Triangulaire
(1/2, 0,866) : ω = 7, comme attendu.

**Poste 1 — le portage des boîtes en Lean : PAS FAIT, et cerné.** Deux constats utiles.
1. *Réduction* : `Queue.lean` couvre h ≥ 15 pour tout g. Seule la région h ∈ [√3/2 ; 15[ a besoin de
   boîtes — la zone à porter est donc bien plus petite que « h ∈ [√3/2 ; 100] ».
2. *Le critère naïf ne marche pas* : on espérait n'utiliser que « la boule de rayon 1/2 est dans la
   cellule », ce qui ramènerait la vérification à « étendue des distances ≤ 1 ». Testé : aucune clique
   de ce type n'existe, même pour le réseau triangulaire — la 7-clique hexagonale a dmin = 0 et
   dmax = 2. Il faut donc les témoins réels, c'est-à-dire les conditions de cellule en géométrie
   rationnelle exacte (polytopes), boîte par boîte.
Le moteur rend déjà les 7 décalages par point (`omega_exact` → `temoins`), mais la vérification *sur une
boîte* demande de montrer dmin ≤ 1 ≤ dmax pour les 21 paires à la fois, ce qui est un calcul de
polytopes en rationnels — réalisable, non fait. Le poste reste donc ouvert dans le document, avec cette
description exacte (dont la recette).

## Geste 35 — « nouveauté » sort de la todo ; le moteur du certificat passe en Lean (03/11/2026)

**Retiré.** La ligne « la nouveauté mathématique » disparaît de la table des postes ouverts du §13 (le
verdict reste au §7.5 : Coulson donne 6, pas 7) et de `todo-hadwiger-nelson.json`.

**Fait pour le bout en bout formel — la partie générique.** `dossiers/geom/Boites.lean` :
`Boites.clique_de_temoins` prouve que, si pour les 21 paires de sept cellules on exhibe une paire de
points à distance au carré ≤ 1 et une paire à distance au carré ≥ 1, alors tout coloriage propre et
constant sur ces cellules leur donne sept couleurs distinctes. Compilé, 0 `sorry`, axiomes
`[propext, Classical.choice, Quot.sound]` (`geom/boites-check.log`). Le raisonnement du certificat est
donc en machine ; ce qui reste hors Lean est la **donnée** par boîte (sept décalages + conditions de
cellule), pour la seule région h ∈ [√3/2 ; 15[ que `Queue.lean` ne couvre pas.

## Geste 36 — export des boîtes à porter (03/11/2026)

Première étape du portage, faite : `note/boites_a_porter.json`. **38 boîtes** rationnelles couvrent la
région résiduelle h ∈ [√3/2 ; 15[, |g| ≤ 1/2, g²+h² ≥ 1 ; pour chacune, un point d'échantillon dans le
domaine, son **ω exact** (`omega_exact`, auto-vérifié) et **la clique de 7 décalages** (`temoins`).
Contrôle : ω ≥ 7 sur les 38 (minimum 7). Ce sont des cliques *ponctuelles* : elles ne sont pas encore
prouvées sur toute la boîte, ce qui est précisément le travail restant (conditions de cellule en
géométrie rationnelle exacte) — la donnée d'entrée existe désormais, le futur fichier Lean se génère à
partir de ce JSON.

## Geste 37 — état du portage, pour reprendre sans perdre le fil (03/11/2026)

**Compilé et vert** (`lake build Queue Pont Boites` → 4 038 jobs ; `Boites_data.lean` → exit 0) :
`Boites.clique_de_temoins` (moteur), `Boites.contrainte_auto` (réduction au fini), les 38 boîtes de
`Boites_data.lean` (bornes + clique de 7 décalages), générées par `note/gen_boites.py` depuis
`note/boites_a_porter.json`.

**Non fait** : les preuves d'obligation par boîte (`dmin ≤ 1 ≤ dmax` sur 21 paires, pour tout (g,h) du
rectangle). Prochaine brique à écrire, dans cet ordre :
1. la forme translatée de `Queue.cell_iff` : `p ∈ cell v ↔ ∀ w ∈ Λ, 2⟨p−v, w−v⟩ ≤ |w−v|²` ;
2. `cell_of_fini` : si `|p−v|² ≤ r²` et si la contrainte est vérifiée pour les seuls `w` avec
   `|w−v|² < 4r²`, alors `p ∈ cell v` (composition avec `contrainte_auto`) ;
3. une boîte d'essai (boîte 0 : g ∈ [−1/2, −1/4], h ∈ [433/500, 9/10]) prouvée de bout en bout,
   puis généralisation aux 37 autres par le générateur.

**Environnement** : la toolchain (`elan`, `lake`) est dans `/var/tmp/leanhome` et ne survit pas
toujours ; les paquets Mathlib dans `/var/tmp/geom-packages` non plus. Chaque séance reprend par
`lake update && lake exe cache get` (~4 min) avant `lake build`. Les fichiers Lean, eux, sont dans le
workspace et intacts.

## Geste 38 — briques 1 et 2 du portage : compilées (03/11/2026)

`dossiers/geom/Boites.lean` (importe `Queue`) — `lake build Boites` → **exit 0**, axiomes
`[propext, Classical.choice, Quot.sound]` pour les quatre théorèmes, aucun `sorry` :
`clique_de_temoins`, `contrainte_auto`, **`cell_iff_translate`** (forme translatée de la contrainte),
**`cell_of_fini`** (la contrainte pour tout `w` du réseau se ramène aux `w` avec |w−v|² < 4r² — un
calcul fini). Journal : `geom/build3.log`. Le brouillon `Essai.lean` a été supprimé.

Reste : les obligations par boîte (témoins + inégalités rationnelles sur les 38 rectangles de
`Boites_data.lean`), désormais outillées de bout en bout. §13 de l'audit mis à jour en conséquence.

## Geste 39 — le point bloquant est levé : ce n'était pas la forme du retour (12/11/2026)

**Ce qui bloquait, mot pour mot.** « Au point d'export (g = −3/8, h = 219/250), la clique de la
boîte 0 ne donne que 20/21 paires en conflit avec mon calcul `dmin2_dmax2`, alors que `omega_exact`
annonce ω = 7 — probablement parce que `audit_gh.cellule` renvoie une liste dont le premier élément
est le polygone. »

**L'hypothèse est fausse, et la vraie cause est ailleurs.** `cellule(g, h)` renvoie le triplet
`(sommets, W, rayon²)` ; `cellule(g, h)[0]` **est** la liste des sommets, et c'est bien elle qu'il
faut passer à `dmin2_dmax2`. Prendre le triplet entier ne reproduit pas 20/21 : cela ne produit
aucun compte, pas un compte faux. Le 20/21 est réel, mais il vient de ce que **les deux calculs ne
comparent pas la même quantité** :

| écriture | condition testée | seuil effectif au centre de la boîte 0 |
|---|---|---|
| `graphe_exact` / `omega_exact` | σ²·dmin² ≤ diam² ≤ σ²·dmax² | T = diam/σ = **1,1824** (σ = 99/100) |
| `Boites.clique_de_temoins` | dmin² ≤ 1 ≤ dmax² | T = **1** |

Confondre « σ = 1 » avec « T = 1 » est le piège : à σ = 1 le seuil vaut diam = 1,17056, pas 1.
Sur la paire ((−1,−2), (1,0)), dmin² = 1158001/1000000 = 1,158001, comprise entre 1 et
diam² = 1,370210 : en conflit dès que σ ≥ 0,9193, séparée au seuil 1. D'où **20/21 au centre,
19/21 à g = −1/2, 19/21 à g = 1/2, h = 9/10** — exactement la valeur rapportée.

**La conséquence, qui est la vraie conclusion : la 7-clique de la boîte 0 n'est pas réparable.**
Au seuil 1, la clique maximale du vrai graphe vaut **ω = 6** au centre et **5** sur les bords
verticaux. Ce n'est pas un défaut de témoins : dmin² > 1 signifie que les deux cellules sont
réellement à distance > 1, donc qu'aucune paire de points ne les rapproche. Aucun choix de témoins
ne peut donc satisfaire `clique_de_temoins` avec les sept décalages exportés.

**Ce que la boîte 0 fournit réellement, et qui suffit.** La condition d'échelle **uniforme**
« dmin < dmax et D < dmax pour les 21 paires, à un même s » tient sur toute la boîte :
ε = D/dmax ≤ **0,606982** au pire sur une grille 5 × 5 (coins, milieux d'arêtes, centre).
C'est précisément l'hypothèse du **lemme B** de `Pont.lean` (0 < ε < 1, D/ε ≤ dmax, dmin < dmax),
dont la conclusion est l'existence d'**une** échelle s rendant les 21 paires doublement tangentes.
Et sur les 38 boîtes, les 25 points d'échantillonnage donnent **0 violation** de `D < dmax`,
ε maximum 0,9934 (boîte 36, h ∈ [8, 15]).

**Ce que la forme de la donnée exportée doit devenir.** Non pas « sept décalages + un seuil figé »,
mais par paire **quatre points** : deux à distance² ≤ 1 et deux à distance² ≥ 1, avec l'échelle s
figée par boîte (et non par paire). C'est ce que `Pont.pont_coloriage` consomme, et c'est un lemme
déjà compilé — rien à ajouter côté Lean. En revanche **vérifier ces quatre points sur toute la
boîte** est un calcul neuf.

**Un quatrième seuil, trouvé en écrivant ce geste.** Vérifier « D < dmax » sur la boîte ne suffit
pas : le s du lemme B vit dans l'intervalle ouvert ]1/dmax, min(1/dmin, 1/D)[, dont la non-vacuité
exige **max dmin² < min dmax²**. Sur les 38 boîtes ce rapport vaut de 1,00 à **1,96** : il échoue
presque partout. Autrement dit, une **7-clique à échelle uniforme** n'existe pas sur ces boîtes —
mais elle n'est pas nécessaire : on peut recouvrir la boîte par un nombre fini de sous-boîtes dont
chacune porte sa propre échelle (le lemme B est ponctuel en (g, h), et la conclusion « χ ≥ 7 » est
ponctuelle). C'est la forme du certificat à écrire, et c'est un changement de gabarit, pas un
contournement.

**Contrôle.** `note/reconciliation_boite0.py` → **exit 0, VERDICT : RÉCONCILIÉ**, journal
`note/reconciliation_boite0.log`. Il réfute explicitement l'hypothèse du « premier élément »,
reproduit 20/21 et 19/21, montre ω(T = 1) = 6, et mesure ε = 0,606982. Arithmétique rationnelle
exacte, aucun flottant dans une décision (les flottants ne servent qu'à l'affichage et à la taille
de fenêtre).

**Environnement, non résolu.** La consigne demandait d'installer elan puis
`leanprover/lean4:v4.36.0-rc2`. **Impossible depuis ce bac à sable** : `raw.githubusercontent.com`,
`release-assets.githubusercontent.com` et `objects.githubusercontent.com` sont injoignables
(`SSL_ERROR_SYSCALL` sur 443) — seuls `github.com`, `codeload.github.com`, `api.github.com`,
`registry.npmjs.org`, `pypi.org` et `files.pythonhosted.org` répondent. L'API GitHub rend bien
l'URL de l'archive d'elan, mais l'hôte qui la sert est bloqué. **Rien n'a donc été recompilé dans
ce geste** : les quatre théorèmes cités (`cell_of_fini` compris) sont ceux des journaux de la
séance du 03/11, pas d'une vérification d'aujourd'hui. À refaire dans un environnement qui atteint
les releases GitHub.

**Ce qui n'est pas fait.** Les obligations par boîte ne sont pas générées : la réconciliation
change leur **forme** (échelle par boîte, quatre témoins par paire, sous-boîtes pour la condition
d'échelle uniforme), et écrire le générateur sur l'ancienne forme aurait figé l'erreur. C'est le
geste suivant, à faire une fois l'environnement Lean rétabli.

## Geste 40 — les obligations par boîte, en forme corrigée : boîtes 0 et 1 certifiées (12/11/2026)

**Ce que le geste 39 imposait.** La donnée « sept décalages + seuil figé » n'est pas une entrée
valide de `Boites.clique_de_temoins` : elle n'y est qu'une 6-clique. La forme correcte est
l'échelle **par boîte** (le quantificateur du théorème est ∀(g, h) ∃s, donc s dépend du réseau,
mais il est fixe sur chaque boîte certifiée), avec des témoins prouvés sur **toute** la boîte.

**Le moteur, `note/obligations.py`.** Quatre pièces, chacune payée par une erreur.

1. *Corps de différences* (la réduction du moteur Rust, geste 26) : `dmin²(V, V+d) = dist(d, K)`
   et `dmax² = max_{z∈K}|z−d|²` avec K = P−P indépendant du décalage. Deux distances
   point-polygone au lieu de polygone-polygone. **Contrôle : 48/48 valeurs identiques au moteur
   lent `audit_gh.dmin2_dmax2`** (6 réseaux × 8 décalages).
2. *Sommets symboliques* : les sommets de la cellule sont des fractions rationnelles en (g, h) ;
   `sommet(i₁,j₁,i₂,j₂)` les rend en `Rat(num, den)` par Cramer, avec `det = 2δ·h`. Contrôle :
   les 6 sommets de la cellule en (−3/8, 219/250) sont reconstruits exactement à partir des
   paires de contraintes actives.
3. *Appartenance sur la boîte par `cell_of_fini`* : la contrainte `2⟨s,w⟩ ≤ |w|²` pour tout w du
   réseau se ramène aux w de longueur < 2r. C'est un « pour tout » sur des inégalités
   **linéaires**, donc une forme de la moyenne suffit, sans subdivision.
4. *Témoins* : parmi les sommets prouvés, on cherche un couple u, v avec |u−(v+d)|² ≤ T² et un
   couple avec ≥ T². Condition **suffisante** (on exhibe), jamais nécessaire : un échec dit
   « ce couple n'est pas prouvé », pas « c'est faux ».

**Quatre erreurs de ma part, dont deux fausses preuves.**

- **La réduction au fini était fausse telle que je l'écrivais.** `cell_of_fini` a pour hypothèse
  `|p−v|² ≤ r²` ; je filtrait les candidats sur les seules contraintes de la fenêtre. Une
  intersection lointaine qui satisfait la fenêtre est alors acceptée à tort, et elle gonfle le
  diamètre (premier symptôme : « diamètre majoré 10,81 ≥ T », pour une vraie valeur de 1,17).
  Corrigé par `_dans_boule`, qui prouve l'hypothèse manquante. **C'est exactement le genre
  d'oubli que la machine attrape et que la relecture laisse passer.**
- **Le graphe de conflit n'est pas un graphe d'appartenance.** J'écrivais « a et b en conflit
  ssi d_a et d_b sont tous deux dans S_T = {dmin < T < dmax} ». Faux : c'est un graphe de
  **Cayley**, a ~ b ssi **d_b − d_a** ∈ S_T. Le symptôme a été un refus net, « aucun témoin
  proche pour ((−2,−2), (−1,1)) », dont le décalage vaut |(1+3g, 3h)| = 2,63 ≫ T = 1,62. Avec
  la bonne relation, la boîte 0 rend une 7-clique locale `(0,0),(0,1),(1,0),(1,1),(1,2),(2,1),(2,2)`
  et le réseau carré rend ω = 9 (le pavé 3×3), ce qui est un contrôle de cohérence.
- **Jamais deux encadrements comparés.** Une distance² valait *exactement* 1 (num = den = 256h⁸)
  et l'encadrement du quotient donnait [0,735 ; 1,360]. Corrigé par `_inegal` : den de signe
  connu, puis **un seul** polynôme `num − T²·den` encadré. C'est la règle du geste 19, et elle
  était violée dans mon propre code.
- *Points contre décalages* : première version, je prenais les sommets de la cellule pour la
  clique. La clique est un ensemble de **décalages** ; les sommets sont les **témoins**. Les deux
  erreurs précédentes étaient masquées par celle-là.

**Résultat : couverture complète des deux boîtes de l'export initial.**

| région | feuilles | échecs | essais | aire couverte | profondeur |
|---|---|---|---|---|---|
| boîte 0, g ∈ [−1/2, −1/4], h ∈ [433/500, 9/10] | 17 | 0 | 33 | 17/2000 = 17/2000 (**1,000000**) | 9 |
| boîte 1, g ∈ [1/4, 1/2], h ∈ [433/500, 9/10] | 17 | 0 | 33 | 17/2000 = 17/2000 (**1,000000**) | 9 |

93 s pour les deux. La profondeur compte : à profondeur 5, 96,9 % de chaque boîte ; la profondeur
9 ferme le reste. C'est la constatation déjà écrite au geste 15 (marges utiles 4,5 × 10⁻⁴ plus
petites que la variation sur une boîte, 3 × 10⁻³) — elle n'était pas propre à l'ancien
paramétrage (ρ, θ), elle est intrinsèque à l'encadrement.

**Ce que cela ne prouve pas, et qu'il faut dire.** Le certificat couvre **deux boîtes sur 38**.
Les 36 autres (jusqu'à h = 15) ne sont pas traitées, et la réduction `Queue.lean` (h ≥ 15) n'est
pas recompilée ici. La couverture obtenue est exacte et reproductible, elle n'est pas encore la
région.

**Le générateur, `note/gen_obligations.py`.** Il réécrit `geom/Boites_data.lean` en forme corrigée :
une `structure Boite` (g₀, g₁, h₀, h₁, **T**, clique), une déclaration par boîte, T par boîte.
38 boîtes, 12 472 octets. Il n'écrit **pas** les obligations de témoins pour les 38 : sur celles
qui ne sont pas certifiées, ce serait du `sorry` déguisé. La liste des obligations à écrire est
celle que produit `obligations_boites.py`.

**Contrôle.** `python3 obligations_boites.py` → **exit 0**, « COUVERTURE COMPLÈTE »,
`obligations_boites.json` + journal. `obligations._auto_test()` → 48/48 conformes au moteur lent.
Arithmétique rationnelle exacte de bout en bout, aucun flottant dans une décision.

**Lean : toujours pas recompilé.** Les hôtes de release GitHub restent injoignables depuis ce bac
à sable (cf. geste 39). `Boites_data.lean` est donc écrit mais non compilé ; la `structure Boite`
n'a pas été vérifiée par `lake build`.

## Geste 41 — accès Lean : diagnostic chiffré, et ce qu'il faudrait ouvrir (12/11/2026)

**Demande** : « rétablir l'accès aux releases GitHub pour compiler ». **Fait : le diagnostic, pas
le rétablissement.** Je ne peux pas ouvrir un accès réseau qui ne m'appartient pas ; ce geste
établit exactement ce qui manque, vérifié et chiffré, pour que la demande porte sur des hôtes
précis.

**Six hôtes bloqués sur dix nécessaires** (et non trois, comme je l'écrivais au geste 39) :
`objects.githubusercontent.com` (cible du 302 des releases), `release-assets.githubusercontent.com`,
`raw.githubusercontent.com` (`elan-init.sh`), `releases.lean-lang.org` (toolchain, voie normale
d'`elan`), `leanprover-community.github.io` et `mathlib.cache.azureedge.net` (cache Mathlib).
Volumes : elan 5 Mo, toolchain 608 Mo, cache Mathlib ~5 Go.

**Ce qui ne marche pas, essayé et non supposé** : PyPI `lean4`/`lean`/`pyelan` sont des wrappers
(0,01–0,37 Mo) ; `lean-dojo`, seul paquet volumineux (67 Mo), a été téléchargé et inspecté — c'est
un jeu de données de benchmark, aucun binaire ; sept requêtes npm ne rendent que des interfaces et
de la coloration syntaxique ; rien ne subsiste de la séance précédente (`~/.elan`, `/var/tmp/geom-*`
absents, bac à sable neuf). Compiler Lean 4 depuis la source est possible en principe (`codeload`
répond 200) mais exclu ici : 2 cœurs, 3,8 Go de RAM, Mathlib ≈ 10 Go et plusieurs heures.

**Le point qui compte** : même avec le toolchain, **rien ne compilerait**. `Geometrie.lean` et
`Queue.lean` importent `Mathlib.Analysis.Convex.Topology` et
`Mathlib.Topology.Order.IntermediateValue`. Le toolchain seul ne suffit donc pas ; il faut le
cache Mathlib, et `leanprover-community.github.io` est un domaine **GitHub Pages** — servi par
Fastly, pas par `github.com`. Autoriser `github.com` ne l'autorise pas. C'est la raison pour
laquelle « les releases GitHub » est une description incomplète du blocage.

**Une erreur de méthode, corrigée.** Ma première version du diagnostic testait
`socket.create_connection((hote, 443))` et concluait « un seul hôte bloqué » — faux pour six. Un
proxy de sortie transparent accepte la connexion TCP **puis** coupe au `ClientHello` TLS : un test
de connexion est un faux positif systématique, et le symptôme côté client est
`SSL_ERROR_SYSCALL`, jamais un refus. `diag_lean_acces.py` teste désormais une requête HTTPS
réelle. C'est exactement le genre d'erreur que la règle du dossier (« calibrer la mesure contre un
juge indépendant ») attrape quand on l'applique ; ici c'est la comparaison à `curl` qui l'a
attrapée.

**Livrables.** `note/diag_lean_acces.py` (exit 1, reproductible, journal `diag_lean_acces.log`) et
`note/acces-lean.md` (les deux issues : ouvrir quatre hôtes, ou compiler ailleurs — `dossiers/geom/`
est autonome et épinglé, quatre commandes suffisent).

**État, sans embellissement.** Les 66 théorèmes cités dans l'audit sont ceux des journaux du
03/11 ; rien n'a été recompilé depuis. `Boites_data.lean`, réécrit au geste 40 en forme corrigée,
**n'a jamais vu `lake build`** : ni la `structure Boite`, ni la syntaxe des rationnels ne sont
vérifiées par un compilateur. Le certificat par boîte est prouvé en Python exact, pas en Lean.
