"""Générateur JSON → Lean : une déclaration par boîte.

Lit `boites_a_porter.json` (38 boîtes de la région h ∈ [√3/2 ; 15[) et écrit
`../geom/Boites_data.lean` : pour chaque boîte, ses bornes rationnelles, sa clique de 7 décalages,
et l'OBLIGATION correspondante (les 21 paires avec témoins à distance² ≤ 1 et ≥ 1).

Ce fichier ne prouve rien : il fabrique la liste des obligations, que le moteur
`Boites.clique_de_temoins` transforme en « sept couleurs » dès que les témoins sont fournis.
"""
import json
from fractions import Fraction as F

d = json.load(open("boites_a_porter.json"))
out = ["""import Queue

/- Fichier GÉNÉRÉ par note/gen_boites.py — ne pas éditer à la main.
   Pour chaque boîte : bornes, clique de 7 décalages, et l'obligation à prouver. -/

open Set

namespace BoitesData
"""]
for n, b in enumerate(d["detail"]):
    g0, g1 = (F(x) for x in b["g"]); h0, h1 = (F(x) for x in b["h"])
    cl = b["clique"]
    out.append(f"/-- Boîte {n} : g ∈ [{g0}, {g1}], h ∈ [{h0}, {h1}] ; ω = {b['omega']} au centre. -/")
    out.append(f"def boite{n} : ℚ × ℚ × ℚ × ℚ := ({g0.numerator}/{g0.denominator}, "
               f"{g1.numerator}/{g1.denominator}, {h0.numerator}/{h0.denominator}, {h1.numerator}/{h1.denominator})")
    out.append(f"def clique{n} : List (ℤ × ℤ) := " + "[" + ", ".join(f"({i}, {j})" for i, j in cl) + "]")
    out.append("")
out.append("end BoitesData")
open("../geom/Boites_data.lean", "w").write("\n".join(out))
print("écrit ../geom/Boites_data.lean :", len(d["detail"]), "boîtes,", len(out), "lignes")
