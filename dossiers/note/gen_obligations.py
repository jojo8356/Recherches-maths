"""Générateur des obligations par boîte, en forme CORRIGÉE (geste 40).

Ce que le geste 39 a établi
---------------------------
La donnée « sept décalages + un seuil figé » est une mauvaise entrée de
`Boites.clique_de_temoins`, qui demande des témoins à distance² ≤ 1 et ≥ 1 (seuil absolu
T = 1). La forme correcte est l'échelle par boîte, issue de `Pont.lemmeB` :

    ∃T > D  tel que pour les 21 paires de la clique, dmin < T < dmax,

et les témoins doivent être prouvés sur TOUTE la boîte. Ce générateur écrit donc, par boîte :

  * les bornes rationnelles et le seuil T (un seul par boîte, tiré de `obligations.meilleur_T`) ;
  * la clique (7 décalages, normalisée pour contenir (0,0)) ;
  * pour chaque paire, le décalage d = d_b − d_a.

Ce qu'il n'écrit pas, et pourquoi
---------------------------------
Il n'écrit PAS les 21 obligations de témoins. Sur les boîtes testées, celles-ci demandent une
subdivision : la largeur d'encadrement de la forme de la moyenne sur un rectangle
|g| = 1/4, h ≈ 1/2 est du même ordre que la variation réelle (constat du certificat T7,
geste 15 : « les marges utiles, 4,5 × 10⁻⁴, sont plus petites que la variation sur une
boîte, ≈ 3 × 10⁻³ »). Écrire des obligations que le certificat ne passe pas reviendrait à
produire du texte Lean faux ou `sorry` — ce que le dossier s'interdit. La subdivision est
calculée par `obligations.couvre`, et c'est elle qui doit fournir les boîtes.

Usage :  python3 gen_obligations.py            (écrit ../geom/Boites_data.lean)
"""
import json
import sys

sys.path.insert(0, "/home/user/Recherches-maths/dossiers/note")
from fractions import Fraction as F

import obligations as O


def _q(x):
    x = F(x)
    return f"({x.numerator} : ℚ) / {x.denominator}"


def rendu(boites, chemin):
    out = ["""import Queue

/- Fichier GÉNÉRÉ par note/gen_obligations.py — ne pas éditer à la main.

   Une déclaration par boîte : bornes rationnelles, seuil d'échelle T, et clique de sept
   décalages. Le seuil T est CELUI DE LA BOÎTE (un seul par boîte), conformément au
   quantificateur réel du théorème  ∀(g, h) ∃s, et non un seuil figé global : c'est la
   correction du geste 39. Les obligations de témoins (distance² ≤ T² et ≥ T², sommets
   prouvés dans la cellule) dépendent de la subdivision et sont produites à part. -/

open Set

namespace BoitesData

/-- Une boîte à certifier : g ∈ [g₀, g₁], h ∈ [h₀, h₁], seuil T, et sept décalages. -/
structure Boite where
  g0 : ℚ
  g1 : ℚ
  h0 : ℚ
  h1 : ℚ
  T  : ℚ
  clique : List (ℤ × ℤ)

"""]
    for n, b in enumerate(boites):
        cl = ", ".join(f"({i}, {j})" for (i, j) in b["clique"])
        out.append(f"/-- Boîte {n} : h ∈ [{F(b['h'][0])}, {F(b['h'][1])}], "
                   f"ω = {b.get('omega', len(b['clique']))}, T = {F(b['T2'])}^½. -/\n")
        out.append(f"def boite{n} : Boite :=\n"
                   f"  {{ g0 := {_q(b['g'][0])}, g1 := {_q(b['g'][1])},\n"
                   f"    h0 := {_q(b['h'][0])}, h1 := {_q(b['h'][1])},\n"
                   f"    T := {_q(b['T2'])},\n"
                   f"    clique := [{cl}] }}\n\n")
    out.append("end BoitesData\n")
    open(chemin, "w").write("".join(out))
    return len("".join(out))


def main():
    """Exporte les boîtes déjà certifiées sous forme abrégée, sans obligation de témoin."""
    d = json.load(open("/home/user/Recherches-maths/dossiers/note/boites_a_porter.json"))
    boites = []
    for b in d["detail"]:
        g = [F(x) for x in b["g"]]
        h = [F(x) for x in b["h"]]
        gc, hc = (g[0] + g[1]) / 2, (h[0] + h[1]) / 2
        try:
            om, T2, cl = O.meilleur_T(O.Cellule(gc, hc))
        except Exception as e:  # noqa: BLE001
            print(f"  boîte {b['point']} : échec ({e})")
            continue
        boites.append({"g": [str(g[0]), str(g[1])], "h": [str(h[0]), str(h[1])],
                       "T2": str(T2), "clique": [list(c) for c in cl], "omega": om})
    n = rendu(boites, "/home/user/Recherches-maths/dossiers/geom/Boites_data.lean")
    print(f"écrit geom/Boites_data.lean : {len(boites)} boîtes, {n} octets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
