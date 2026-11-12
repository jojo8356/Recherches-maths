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

## Ce qui n'est pas corrigé

- **Le lien modèle ↔ plan** : nos objets sont des coloriages polygonaux (χ_poly). Le passage à χ(ℝ²) n'existe pas.
- **Aucune formalisation** (Lean ou autre).
- **Certificat** : couverture de vérification 5 %, bibliothèque unique (mpmath), diamètre 1 − 10⁻³, réseaux seulement.
- **Négations sur familles choisies** (phase 3, phase 7) : reformulées, pas remplacées par des énumérations exhaustives.

## Règle de méthode ajoutée

Avant de publier une valeur de ω : écrire la convention de tangence, calibrer la tolérance contre un
juge indépendant, et refaire le calcul sous les deux conventions si elles diffèrent.
