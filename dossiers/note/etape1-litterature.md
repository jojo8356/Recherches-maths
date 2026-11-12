# Étape 1 — La littérature : le champ est-il libre ?

**Date** : 3 novembre 2026 (soir) · **Question posée** : la cible T est-elle nouvelle ?

> **Cible T** : pour tout réseau du plan dont le pavage de Voronoï n'a que des sommets de
> degré 3 (cellules hexagonales), le graphe de conflit du pavage, à l'échelle maximale
> admissible, contient une 7-clique — donc χ ≥ 7 pour ce pavage.

**Verdict : non. Le champ n'est pas libre.** La *conclusion* de T est impliquée par un
théorème publié, et l'ingrédient « réseaux » était déjà connu en 2004. Ce qui reste
éventuellement nouveau est plus étroit que T et n'est plus une découverte, c'est une mesure.

---

## 1. Ce que dit chaque source, précisément

| Source | Énoncé exact | Statut | Conséquence pour T |
|---|---|---|---|
| **Coulson 2004**, *J. Austral. Math. Soc.* **77**, 191–196 | « **Any lattice-sublattice colouring scheme for ℝ² must use at least 7 colours to have an excluded distance.** » Puis : ≥ **6** couleurs pour des tuiles polygonales convexes d'aire minorée. | publié, revu | Le **7 sur les réseaux** est déjà là — mais pour la sous-classe des coloriages par classes d'une **sous-treillis** (couleur = classe modulo un sous-réseau), plus restrictive que la nôtre. Donc : n'implique pas notre énoncé, mais occupe le terrain « réseau + 7 ». |
| **Manta 2021**, *Discrete Math.* **344**, 112411 (arXiv 1909.02708) | Théorème 2.2 : *si un coloriage polygonal a un sommet de **degré ≥ 4**, il faut ≥ 7 couleurs.* Théorème 2.3 : tout coloriage triangulaire exige 7. Cas laissé ouvert : **tous les sommets de degré ≤ 3**. | publié, revu | Notre cible est exactement dans le trou laissé ouvert — pour la sous-classe « réseaux ». **Attention** : la preuve de Manta discute d'abord un sommet de degré 5, alors que le théorème énonce 4 ; notre dossier disait « ≥ 5 », c'est l'énoncé du théorème qui fait foi, la preuve est signalée comme fragile sur ce point. |
| **Sokolov–Voronov**, *Discrete Math.* **349**(12), déc. 2026, art. 115321 (DOI 10.1016/j.disc.2026.115321, arXiv 2502.01958) | Théorème 1 : ≥ 7 couleurs pour un coloriage de type carte si les bords ne contiennent pas d'arc de cercle unité et que trois bords se rencontrent en chaque sommet. **Théorème 2 : « There is no polygonal coloring of the plane in 6 colors, i.e. χ_poly(ℝ²) = 7. »** | **publié** (Elsevier, Discrete Math. 349(12), 2026) — notre dossier le disait « préprint non référé » : **c'est faux depuis cette référence** | **Il subsume T.** Si aucun coloriage polygonal à 6 couleurs du plan n'existe, alors en particulier aucun coloriage à 6 couleurs des cellules de notre pavage — donc χ ≥ 7, ce que T annonce. Réserve honnête : une revue automatique (pith.science, 09/08/2026) liste 5 objections majeures, et publication ≠ correction. |
| **Dutour Sikirić–Madore–Moustrou–Vallentin 2021**, *J. London Math. Soc.* (arXiv 1907.09751) | Définit **le nombre chromatique d'un réseau** χ(Λ) = coloriage des cellules de Voronoï tel que deux cellules **partageant une facette** diffèrent. Calcule χ(ℤⁿ) = 2, χ(A₂) = 3, χ(E₈) = 16, χ(Λ₂₄) = 4096. | publié, revu | L'**objet** « colorier la tessellation de Voronoï d'un réseau » est déjà nommé et étudié. Mais leur adjacence est la **facette partagée**, pas « distance ≤ 1 » : nos graphes sont différents (le nôtre contient le leur). Le mot « nouveau » est donc déjà pris pour l'objet, pas pour l'adjacence. |

## 2. Ce que cela laisse, exactement

Deux choses seulement, et aucune n'est une découverte au sens fort.

**(a) La clé de voûte : clique ≠ chromatique.** T annonce une **7-clique**, c'est-à-dire une
borne sur ω. Sokolov–Voronov prouvent une borne sur χ. Or χ ≥ 7 n'entraîne pas ω ≥ 7 : un
graphe 7-chromatique peut n'avoir que des triangles. Un témoin explicite de taille 7 reste donc
non couvert par la littérature. Mais un tel témoin, pour une famille de réseaux, est un
**calcul**, pas un théorème — et « il existe une 7-clique dans ce pavage-là » n'intéresse personne
en soi. Sa seule valeur est instrumentale : c'est ce qui rend le calcul vérifiable.

**(b) La mesure, pas le théorème : le paysage.** Notre moteur exact donne ω comme fonction de
deux paramètres (ρ, θ) et de l'échelle δ, et le seuil δ\*(Λ) = plus grande échelle où ω reste ≥ 7.
Le paysage déjà calculé (δ\* ∈ [0,48 ; 0,78], ω ∈ {4,…,12} selon le réseau) n'est tabulé nulle
part à ma connaissance. C'est un résultat **quantitatif** sur un objet connu — publiable comme
note de calcul, pas comme avancée.

## 3. Trois suites possibles

| Option | Contenu | Ce que ça vaut | Coût |
|---|---|---|---|
| **A. Auditer la preuve publiée sur la tranche réseaux** | Puisque S-V est publié mais contesté (5 objections), décider *par calcul exact* le cas « réseaux à cellules hexagonales » : si leur théorème tombe, cette tranche reste établie. C'est notre machine exacte + le certificat réparé. | un rôle de **vérificateur** crédible sur un cas ouvert contesté — c'est exactement ce que nos outils savent faire, et ça n'exige aucune antériorité | 2–3 séances |
| **B. Publier la mesure** | Le paysage ω(ρ,θ,δ) et les seuils δ\*(Λ), en note de calcul avec moteur exact et contrôles négatifs. | une table de référence, utile à ceux qui travaillent sur χ_poly ; honnête, modeste | 1–2 séances |
| **C. Sortir des réseaux** | Le vrai trou restant est le cas **degré ≤ 3 des pavages non-réseaux** (Manta), ou le cas « bords = arcs de cercle unité » (Question 2 de S-V). Nos outils n'y vont pas : sans translation, pas de graphe de Cayley, donc pas d'espace de paramètres à deux dimensions. | une découverte possible, mais il faudrait **changer de méthode**, pas prolonger celle-ci | semaines à mois, incertain |

## 4. Corrections à porter au dossier

1. **Sokolov–Voronov n'est plus un préprint non référé** : *Discrete Mathematics* **349**(12),
   2026, article 115321. Toute phrase du dossier qui le présente comme « non validé, non référé »
   doit être corrigée — avec la nuance que le contenu reste une preuve contestée (revue
   automatique du 09/08/2026 : 5 objections majeures) et que nous ne certifions pas leur preuve.
2. **Manta : degré ≥ 4** dans l'énoncé du théorème 2.2 (la preuve discute un moment le degré 5 ;
   c'est une incohérence interne de l'article, pas une lecture de travers de notre part).
3. **Coulson** : l'énoncé « ≥ 7 pour tout schéma de coloriage réseau-sous-réseau » est dans
   l'article, et il ne doit pas être confondu avec le « ≥ 6 pour les tuiles convexes » qui est
   l'autre moitié du même résumé.
4. **Dutour Sikirić et al. 2021** doit entrer dans les sources : c'est l'article qui nomme
   l'objet « coloriage de la tessellation de Voronoï d'un réseau » (adjacence par facette).

## 5. Conclusion en une phrase

La cible T n'était pas une découverte disponible : sa conclusion est publiée depuis cette année
(et son ingrédient « réseau » depuis 2004). Ce qui reste est un **rôle** — vérifier par calcul
exact une tranche d'un théorème contesté — et une **mesure** — le paysage des nombres de clique.
Ni l'un ni l'autre ne justifie de reparler de χ(ℝ²).
