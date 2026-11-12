"""GESTE 3 — omega a l'echelle delta = 1 EXACTEMENT (et non 1 - 1e-3).

Meme moteur exact que `exact_tangence.py` (corps Q(sqrt d), aucune arithmetique
d'intervalles, aucun flottant dans les decisions), mais on pousse delta jusqu'a 1 : les
cellules ont alors un diametre EXACTEMENT egal au seuil. Ce que le certificat ne faisait
qu'a 1 - 10^-3.
"""
import json, time
import sys
sys.argv = ["x"]
import exact_tangence as E

PLANS = [("hexagonal (60 deg)", 3, "cellules_hexa", ["9/10", "99/100", "999/1000", "1"]),
         ("carre (90 deg)", 2, "cellules_carre", ["9/10", "999/1000", "1"]),
         ("rectangle 2:1 (90 deg)", 5, "cellules_rect2", ["49/50", "999/1000", "1"])]

out = {}
for nom, champ, fab, deltas in PLANS:
    E.D = champ
    for ds in deltas:
        t0 = time.time()
        P, b1, b2 = getattr(E, fab)(E.F(ds))
        w, nr = E.omega_exact(P, b1, b2)
        out[f"{nom}|{ds}"] = w
        print(f"{nom:24s} delta={ds:>9s} (= {float(E.F(ds)):.3f}) : omega = {w}  "
              f"(exact, anneau {nr}, {time.time()-t0:.0f}s)", flush=True)
json.dump(out, open("exact_un.json", "w"), ensure_ascii=False, indent=1)
print("exact_un.json ecrit")
