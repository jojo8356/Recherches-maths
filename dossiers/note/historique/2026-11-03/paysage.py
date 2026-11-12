"""Paysage omega(rho, theta, delta) et grandeur delta* : la plus grande echelle ou
le pavage n'a plus de clique de 7.

Enjeu : la contrainte polygonale exige seulement « diametre < 1 », pas « = 1 ».
Si un reseau et une echelle donnaient omega <= 6 avec delta grand, l'obstruction par
clique disparaitrait et un 6-coloriage pourrait s'y loger. delta* mesure ou cela
commence.
"""
import json
import math

import echelle

THE = [60 + 3 * i for i in range(21)]          # 60 .. 120
RHO = [1.0 + 0.0625 * j for j in range(17)]    # 1 .. 2
DEL = [round(0.30 + 0.02 * k, 3) for k in range(35)]   # 0.30 .. 0.98


def main():
    import time
    t0 = time.time()
    res = {}
    for rho in RHO:
        for th in THE:
            courbe = []
            for d in DEL:
                courbe.append(echelle.omega_echelle(rho, th, d))
            res[f"{th},{rho:.4f}"] = courbe
        print(f"  rho={rho:.3f} fait  ({time.time()-t0:.0f}s)", flush=True)

    # delta* = plus grande echelle ou omega <= 6 (recherche lineaire sur la grille)
    etoiles = {}
    for k, courbe in res.items():
        dstar = None
        for d, w in zip(DEL, courbe):
            if w <= 6:
                dstar = d
        etoiles[k] = dstar
    json.dump({"theta": THE, "rho": RHO, "delta": DEL, "omega": res,
               "delta_etoile": etoiles, "temps_s": round(time.time() - t0, 1)},
              open("paysage.json", "w"))

    vals = [v for v in etoiles.values() if v is not None]
    print(f"\n{len(res)} reseaux x {len(DEL)} echelles, {time.time()-t0:.0f}s")
    if vals:
        print(f"reseau(x) avec omega <= 6 a une echelle : {len(vals)} / {len(res)}")
        mx = max(vals)
        print(f"delta* maximal : {mx}  pour", [k for k, v in etoiles.items() if v == mx][:8])
        import collections
        print("distribution de delta* :", dict(sorted(collections.Counter(vals).items())))
    borne = min(min(c) for c in res.values())
    print(f"minimum de omega sur toute la grille : {borne}")
    print("reseaux ou omega <= 6 pour TOUTE la plage 0,30-0,98 :",
          sum(1 for c in res.values() if max(c) <= 6))


if __name__ == "__main__":
    main()
