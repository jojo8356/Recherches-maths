"""AUDIT S-V — séance 1, étape A : le domaine est-il vraiment [1,2] x [60,120] ?

Question
--------
Le certificat T7 (rétracté) prétendait couvrir "tout réseau" avec rho in [1,2], theta in [60,120].
Or le domaine fondamental de SL(2,Z)\\H en coordonnées (rho, theta) n'est PAS ce rectangle :
|Re tau| <= 1/2 exige rho*|cos theta| <= 1/2, et rien ne borne Im tau vers le haut.
Les réseaux très anisotropes (rho > 2) ne sont donc pas couverts. S'ils sont hexagonaux,
l'audit de la tranche "degré 3" les concerne directement.

Ce script mesure omega à l'échelle delta = 0.99 (cellules de diamètre 0.99 < 1 : échelle
ADMISSIBLE, donc un coloriage de cellules y est un coloriage du plan par polygones)
sur un domaine beaucoup plus large que [1,2] x [60,120], et cherche le minimum.

Convention
----------
delta = 0.99 / diam(cellule) : les cellules du réseau normalisé ont le diamètre 0.99,
le seuil de conflit est 1 (distances euclidiennes). Conflit <=> dmin <= 1 <= dmax.
Sortie : audit_domaine.json
"""
import json
import math
import sys

import numpy as np

sys.path.insert(0, ".")
from echelle import cellule_voronoi, graphe_echelle, clique_max_avec0   # noqa: E402

ECH = 0.99          # diamètre des cellules : strictement < 1, donc admissible
TOL = 1e-12


def omega(rho, th_deg, ech=ECH):
    th = math.radians(th_deg)
    b1, b2 = (1.0, 0.0), (rho * math.cos(th), rho * math.sin(th))
    P = cellule_voronoi(b1, b2)
    if P is None or len(P) < 3:
        return None
    diam = max(math.dist(p, q) for p in P for q in P)
    delta = ech / diam
    offsets, adj = graphe_echelle(P, b1, b2, delta, tol=TOL)
    k, S = clique_max_avec0(adj)
    return {"omega": k, "nv": len(P), "diam": diam, "delta": delta,
            "temoins": sorted(offsets[i] for i in S) if S else None,
            "n_noeuds": len(offsets)}


def main():
    rhos = [round(1.0 + 0.05 * k, 4) for k in range(0, 61)]          # 1.00 .. 4.00
    rhos += [4.5, 5.0, 6.0, 8.0, 12.0, 20.0, 50.0]
    thetas = [60 + 0.5 * k for k in range(0, 121)]                   # 60 .. 120
    res = {}
    mini = (99, None)
    histo = {}
    for rho in rhos:
        for th in thetas:
            r = omega(rho, th)
            if r is None or r["omega"] == 0:
                continue
            key = f"{rho:.4g},{th:g}"
            res[key] = r
            histo[r["omega"]] = histo.get(r["omega"], 0) + 1
            if r["omega"] < mini[0]:
                mini = (r["omega"], (rho, th, r))
    print(f"{len(res)} réseaux évalués")
    print("histogramme de omega :", dict(sorted(histo.items())))
    print("minimum :", mini[0], "atteint en rho =", mini[1][0], "theta =", mini[1][1])
    print("  ->", {k: v for k, v in mini[1][2].items() if k != "temoins"},
          "témoins", mini[1][2]["temoins"])

    # où omega < 7 ?
    bas = [(k, v["omega"], v["nv"]) for k, v in res.items() if v["omega"] < 7]
    print(f"{len(bas)} réseaux sous 7 :", bas[:12])

    # le minimum par bande de rho : la question "le domaine [1,2] suffit-il ?"
    parrho = {}
    for rho in rhos:
        vals = [v["omega"] for k, v in res.items() if k.startswith(f"{rho:.4g},")]
        if vals:
            parrho[rho] = min(vals)
    print("min de omega par rho :", parrho)

    json.dump({"ech": ECH, "tol": TOL, "n": len(res), "histo": histo,
               "min_par_rho": parrho, "minimum": {"omega": mini[0],
                                                  "rho": mini[1][0], "theta": mini[1][1]} if mini[1] else None,
               "resultats": res},
              open("audit_domaine.json", "w"), indent=0)
    print("écrit audit_domaine.json")


if __name__ == "__main__":
    main()
