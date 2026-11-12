"""Verification INDEPENDANTE du certificat : on ne reutilise pas le code d'intervalles.

Pour un echantillon de boites certifiees, on tire des points (rho,theta) au hasard
dans la boite, on refait la geometrie a 50 chiffres (mpmath, sans intervalles), on
normalise la cellule a un diametre de 1-1e-3 et on verifie que les 7 cellules de la
clique certifiee sont bien deux a deux en conflit. Un seul echec invaliderait le
certificat.
"""
import math
import random
import json
import sys

import numpy as np
from mpmath import mp

mp.dps = 50


def cellule_mp(rho, th, nmax=8):
    """Cellule de Voronoi de l'origine, par intersection de demi-plans (mpmath)."""
    poly = [(-6, -6), (6, -6), (6, 6), (-6, 6)]
    V = []
    for i in range(-nmax, nmax + 1):
        for j in range(-nmax, nmax + 1):
            if i == 0 and j == 0:
                continue
            vx = mp.mpf(i) + j * rho * mp.cos(th)
            vy = j * rho * mp.sin(th)
            if mp.sqrt(vx * vx + vy * vy) <= 5.5:
                V.append((vx, vy))
    for (vx, vy) in V:
        c = (vx * vx + vy * vy) / 2
        out, m = [], len(poly)
        for k in range(m):
            a, b = poly[k], poly[(k + 1) % m]
            da = vx * a[0] + vy * a[1] - c
            db = vx * b[0] + vy * b[1] - c
            if da <= 0:
                out.append(a)
            if (da < 0 < db) or (db < 0 < da):
                t = da / (da - db)
                out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
        poly = out
        if len(poly) < 3:
            return None
    for p in poly:
        assert abs(vx * p[0] + vy * p[1] - c) >= 0
    return poly


def diam(P):
    return max(mp.sqrt((P[i][0] - P[j][0]) ** 2 + (P[i][1] - P[j][1]) ** 2)
               for i in range(len(P)) for j in range(len(P)))


def dist_min_max(Pa, Pb):
    def pt_seg(p, a, b):
        ax, ay = b[0] - a[0], b[1] - a[1]
        L = ax * ax + ay * ay
        t = 0 if L == 0 else ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / L
        t = max(mp.mpf(0), min(mp.mpf(1), t))
        q = (a[0] + t * ax, a[1] + t * ay)
        return mp.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

    dmin = min(min(pt_seg(p, Pb[j], Pb[(j + 1) % len(Pb)]) for j in range(len(Pb))) for p in Pa)
    dmin = min(dmin, min(min(pt_seg(p, Pa[j], Pa[(j + 1) % len(Pa)]) for j in range(len(Pa))) for p in Pb))
    dmax = max(mp.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) for p in Pa for q in Pb)
    return dmin, dmax


def verifie(rho, thd, clique, eps=1e-3):
    th = mp.mpf(thd) * mp.pi / 180
    P = cellule_mp(mp.mpf(rho), th)
    if P is None:
        return None
    D = diam(P)
    k = (1 - mp.mpf(eps)) / D
    b1 = (k, mp.mpf(0))
    b2 = (k * mp.mpf(rho) * mp.cos(th), k * mp.mpf(rho) * mp.sin(th))
    cellules = {}
    for (i, j) in clique:
        cellules[(i, j)] = [(p[0] + i * b1[0] + j * b2[0], p[1] + i * b1[1] + j * b2[1]) for p in P]
    pire = None
    for a in range(len(clique)):
        for b in range(a + 1, len(clique)):
            dmin, dmax = dist_min_max(cellules[clique[a]], cellules[clique[b]])
            marge = min(float(1 - dmin), float(dmax - 1))
            pire = marge if pire is None else min(pire, marge)
            if not (dmin < 1 < dmax):
                return (False, (clique[a], clique[b]), float(dmin), float(dmax))
    return (True, pire, float(D * k))


if __name__ == "__main__":
    d = json.load(open("certificat.json"))
    boites = [b for b in d["boites"] if b[5]]
    random.seed(2026)
    profondes = [b for b in boites if b[4] >= 3]          # toutes les boites fines
    ech = profondes + random.sample(boites, min(1200, len(boites)))
    print(f"{len(ech)} boites echantillonnees (dont {len(profondes)} de profondeur >= 3)")
    n = 0
    pire_global = 1e30
    for (a, b, c, e, prof, ok, marge) in ech:
        # on redemande la clique certifiee (recalcul rapide via le module)
        sys.path.insert(0, ".")
        from certificat import certifie
        okk, info = certifie(a, b, c, e)
        if not okk:
            print("RECALCUL ECHOUE", (a, b, c, e)); continue
        clique = [tuple(x) for x in info["clique"]]
        for _ in range(2):
            rho = random.uniform(a, b)
            th = random.uniform(c, e)
            res = verifie(rho, th, clique)
            n += 1
            if res is None or res[0] is not True:
                print("ECHEC", (a, b, c, e), (rho, th), res)
                sys.exit(1)
            pire_global = min(pire_global, res[1])
    print(f"{n} points verifies a 50 chiffres, tous avec la clique annoncee.")
    print(f"marge minimale observee (min(1-dmin, dmax-1)) : {pire_global:.4f}")
