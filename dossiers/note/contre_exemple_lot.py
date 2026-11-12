"""Quantification : sur un echantillon de boites, combien ont au moins un temoin PROUVE
hors de sa cellule a un coin ? (evaluation exacte, independante du certificat)"""
import gzip
import json, sys
from fractions import Fraction as F
import verif_exacte as V
from contre_exemple import f_corner

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
n_box = n_box_vio = n_paires = n_paires_vio = 0
exemples = []
for ligne in gzip.open("certificat_temoins_echantillon.jsonl.gz","rt"):
    if n_box >= N:
        break
    rec = json.loads(ligne)
    n_box += 1
    (rho0, rho1), (th0, th1) = rec["r"], rec["t"]
    coins = [(rho0, th0), (rho0, th1), (rho1, th0), (rho1, th1)]
    gen = [(F(p[0]), F(p[1])) for p in rec["tem"]["gen"]]
    A = [tuple(o) for o in rec["tem"]["A"]]
    vio = 0
    for p in gen:
        for ij in A:
            n_paires += 1
            lb = max(f_corner(p, ij, r, t, "lo") for (r, t) in coins)
            if lb > 0:
                vio += 1
                n_paires_vio += 1
    if vio:
        n_box_vio += 1
        if len(exemples) < 5:
            exemples.append({"boite": rec["r"] + rec["t"], "n_violations": vio, "n_temoins": len(gen)})
print(f"boites examinees : {n_box}")
print(f"boites avec au moins un temoin prouve hors cellule : {n_box_vio} ({100*n_box_vio/n_box:.1f} %)")
print(f"paires (temoin, contrainte) violees : {n_paires_vio} / {n_paires} ({100*n_paires_vio/max(1,n_paires):.2f} %)")
for e in exemples: print("  ", e)
json.dump({"boites": n_box, "boites_violees": n_box_vio, "paires": n_paires,
           "paires_violees": n_paires_vio, "exemples": exemples},
          open("contre_exemple_lot.json","w"), ensure_ascii=False, indent=1)
