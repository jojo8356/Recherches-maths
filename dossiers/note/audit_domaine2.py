"""AUDIT S-V — séance 1, étape A (corrigée) : géométrie propre, sans le moteur historique.

Le bug attrapé en écrivant ce fichier
-------------------------------------
`echelle.py::graphe_echelle` filtre les paires candidates par |D - 1| <= delta*1.05, où
`delta` est le FACTEUR D'ÉCHELLE. Ce filtre n'est correct que si la cellule non normalisée
a un diamètre exactement 1. Pour un réseau anisotrope, le diamètre après mise à l'échelle
vaut 0.99 alors que le facteur vaut 0.082 : le filtre ne garde que 8 % de la fenêtre
nécessaire, et omega est sous-estimé (3 au lieu de la vérité). Ici le filtre utilise le
DIAMÈTRE des cellules mises à l'échelle, qui est la constante ECH.

Modèle (énoncé une fois, sans héritage)
---------------------------------------
- Réseau Lambda = Z b1 + Z b2, b1 = (1,0), b2 = rho (cos theta, sin theta), rho >= 1,
  theta in [60,120] degrés. Cellules de Voronoï V_lambda.
- Échelle admissible : cellules de diamètre ECH < 1 dans le plan métrique où la distance
  interdite vaut 1. (Il FAUT diamètre < 1 : sinon une cellule monochrome contient déjà
  deux points à distance 1.)
- Conflit : deux cellules distinctes A, B contiennent p, q avec |p - q| = 1.
  Équivalent : dmin(A,B) <= 1 <= dmax(A,B).
- omega = nombre de clique du graphe de conflit (sommet-transitif : on ancre en 0).

Sortie : audit_domaine2.json
"""
import json
import math

import numpy as np

ECH = 0.99        # diamètre des cellules à l'échelle considérée (strictement < 1)
TOL = 1e-12


def cellule(rho, th_deg):
    """Sommets de la cellule de Voronoï de 0, réseau b1=(1,0), b2=rho(cos,sin)."""
    th = math.radians(th_deg)
    b1 = (1.0, 0.0)
    b2 = (rho * math.cos(th), rho * math.sin(th))
    poly = [(-6.0, -6.0), (6.0, -6.0), (6.0, 6.0), (-6.0, 6.0)]
    for i in range(-8, 9):
        for j in range(-8, 9):
            if i == 0 and j == 0:
                continue
            vx, vy = i * b1[0] + j * b2[0], i * b1[1] + j * b2[1]
            if math.hypot(vx, vy) > 5.5:
                continue
            c = (vx * vx + vy * vy) / 2
            out = []
            m = len(poly)
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
                return None, (b1, b2)
    ded = []
    for p in poly:
        if not ded or math.dist(p, ded[-1]) > 1e-10:
            ded.append(p)
    if len(ded) > 2 and math.dist(ded[0], ded[-1]) < 1e-10:
        ded.pop()
    return ded, (b1, b2)


def diam(P):
    return max(math.dist(p, q) for p in P for q in P)


def _pt_seg(X, Q):
    """Distances de chaque point de X au polygone Q (bords), minimum."""
    best = float("inf")
    m = len(Q)
    for i in range(m):
        a, b = Q[i], Q[(i + 1) % m]
        abx, aby = b[0] - a[0], b[1] - a[1]
        L = abx * abx + aby * aby
        ax, ay = a
        x, y = X
        t = 0.0 if L == 0 else max(0.0, min(1.0, ((x - ax) * abx + (y - ay) * aby) / L))
        px, py = ax + t * abx, ay + t * aby
        best = min(best, math.hypot(x - px, y - py))
    return best


def dmin_dmax(A, B):
    """(dmin, dmax) entre deux polygones convexes."""
    dmin = min(min(_pt_seg(p, B) for p in A), min(_pt_seg(q, A) for q in B))
    dmax = max(math.dist(p, q) for p in A for q in B)
    return dmin, dmax


def graphe(rho, th_deg, ech=ECH):
    P, (b1, b2) = cellule(rho, th_deg)
    if P is None:
        return None
    d = diam(P)
    s = ech / d                      # facteur d'échelle : diamètre des cellules = ech
    Q = [(s * x, s * y) for (x, y) in P]
    c1 = (s * b1[0], s * b1[1])
    c2 = (s * b2[0], s * b2[1])
    # condition nécessaire : |D - 1| <= ech (car dmin <= D <= dmax et dmin <= 1 <= dmax)
    R = 1.0 + ech
    Ri = int(math.ceil(R / abs(c1[0] * c2[1] - c1[1] * c2[0]) * max(math.hypot(*c2), 1e-9))) + 2
    Rj = int(math.ceil(R / abs(c1[0] * c2[1] - c1[1] * c2[0]) * max(math.hypot(*c1), 1e-9))) + 2
    offs, adjs, infos = [], [], []
    for i in range(-Ri, Ri + 1):
        for j in range(-Rj, Rj + 1):
            offs.append((i, j))
    cen = [(i * c1[0] + j * c2[0], i * c1[1] + j * c2[1]) for (i, j) in offs]
    for k, (i, j) in enumerate(offs):
        if (i, j) == (0, 0):
            continue
        if abs(math.hypot(*cen[k]) - 1.0) > ech + TOL:
            continue
        A = Q
        B = [(x + cen[k][0], y + cen[k][1]) for (x, y) in Q]
        lo, hi = dmin_dmax(A, B)
        if lo <= 1.0 + TOL and hi >= 1.0 - TOL:
            infos.append(((i, j), lo, hi))
    # --- matrice COMPLÈTE des conflits sur le voisinage (et non plus une étoile)
    offs2 = [(0, 0)] + [o for o, _, _ in infos]
    n = len(offs2)
    nv = len(Q)
    cen2 = np.array([(i * c1[0] + j * c2[0], i * c1[1] + j * c2[1]) for (i, j) in offs2])
    Vp = (np.asarray(Q)[None, :, :] + cen2[:, None, :]).reshape(-1, 2)      # (n*nv, 2)
    Vn = np.roll(Vp.reshape(n, nv, 2), -1, axis=1).reshape(-1, 2)
    A = Vp[None, :, :]
    B = Vn[None, :, :]
    AB = B - A
    L = np.maximum((AB ** 2).sum(-1), 1e-30)
    t = np.clip(((Vp[:, None, :] - A) * AB).sum(-1) / L, 0, 1)
    pr = A + t[..., None] * AB
    Dm = np.sqrt(((Vp[:, None, :] - pr) ** 2).sum(-1)).reshape(n, nv, n, nv)
    lo = Dm.min(axis=(1, 3))
    vv = np.sqrt(((Vp[:, None, :] - Vp[None, :, :]) ** 2).sum(-1)).reshape(n, nv, n, nv).max(axis=(1, 3))
    conf = (lo <= 1.0 + TOL) & (vv >= 1.0 - TOL)
    np.fill_diagonal(conf, False)
    adj = [set(np.nonzero(conf[r])[0].tolist()) for r in range(n)]
    idx = {o: k for k, o in enumerate(offs2)}
    return {"P": P, "diam": d, "s": s, "nv": nv, "adj": adj, "idx": idx,
            "infos": infos, "lo": lo, "vv": vv, "offs": offs2}


def clique_max_avec0(adj):
    V = adj[0] | {0}
    best = [0, None]

    def bk(R, P, X):
        if not P and not X:
            if len(R) > best[0]:
                best[0], best[1] = len(R), set(R)
            return
        if len(R) + len(P) <= best[0]:
            return
        u = max(P | X, key=lambda v: len(adj[v] & P))
        for v in list(P - adj[u]):
            bk(R | {v}, P & adj[v], X & adj[v])
            P.discard(v)
            X.add(v)

    bk(set(), set(V), set())
    return best[0], best[1]


def omega(rho, th, ech=ECH):
    g = graphe(rho, th, ech)
    if g is None:
        return None
    k, S = clique_max_avec0(g["adj"])
    inv = {t: o for o, t in g["idx"].items()}
    return {"omega": k, "nv": g["nv"], "diam": g["diam"],
            "temoins": sorted(inv[i] for i in S) if S else None,
            "deg0": len(g["adj"][0])}


def main():
    rhos = [round(1.0 + 0.05 * k, 4) for k in range(0, 61)]
    rhos += [4.5, 5.0, 6.0, 8.0, 12.0, 20.0, 50.0, 200.0]
    thetas = [60 + 0.5 * k for k in range(0, 121)]
    res, histo, mini = {}, {}, (99, None)
    for rho in rhos:
        for th in thetas:
            r = omega(rho, th)
            if r is None or r["omega"] == 0:
                continue
            res[f"{rho:.4g},{th:g}"] = r
            histo[r["omega"]] = histo.get(r["omega"], 0) + 1
            if r["omega"] < mini[0]:
                mini = (r["omega"], (rho, th, r))
    print(f"{len(res)} réseaux évalués")
    print("histogramme de omega :", dict(sorted(histo.items())))
    print("minimum :", mini[0], "en rho =", mini[1][0], "theta =", mini[1][1])
    print("   ", {k: v for k, v in mini[1][2].items()})
    bas = [(k, v["omega"], v["nv"]) for k, v in res.items() if v["omega"] < 7]
    print(f"{len(bas)} réseaux sous 7 :", bas[:15])
    parrho = {}
    for rho in rhos:
        v = [x["omega"] for k, x in res.items() if k.startswith(f"{rho:.4g},")]
        if v:
            parrho[rho] = min(v)
    print("min de omega par rho :", parrho)
    hexa = [(k, v["omega"]) for k, v in res.items() if v["nv"] == 6]
    print(f"réseaux à cellules HEXAGONALES (nv=6) : {len(hexa)}, minimum de omega :"
          f" {min(x[1] for x in hexa) if hexa else None}")
    json.dump({"ech": ECH, "tol": TOL, "n": len(res), "histo": histo,
               "min_par_rho": parrho,
               "minimum": {"omega": mini[0], "rho": mini[1][0], "theta": mini[1][1],
                           "detail": mini[1][2]} if mini[1] else None,
               "sous_7": bas, "resultats": res},
              open("audit_domaine2.json", "w"), indent=0)
    print("écrit audit_domaine2.json")


if __name__ == "__main__":
    main()
