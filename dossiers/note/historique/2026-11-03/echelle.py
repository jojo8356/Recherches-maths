"""omega en fonction de l'echelle, calcul EXACT.

A l'echelle delta (cellules de diametre delta), deux cellules ne peuvent etre en
conflit que si la distance de leurs centres verifie |D - 1| <= delta. Le graphe de
conflit est donc un graphe de Cayley : il ne depend que de la difference des indices.
Comme il est sommet-transitif, toute clique est la translatee d'une clique contenant 0 :
il suffit donc de chercher la plus grande clique contenant la cellule 0 dans l'anneau
des differences candidates. Aucune fenetre arbitraire, donc aucune troncature.

(C'est ce qui manquait a la table L5 du journal : a delta = 0,5 et plus petit, la
fenetre 5x5 de balayage.py tronquait le graphe et sous-estimait omega.)
"""
import math

import numpy as np


def cellule_voronoi(b1, b2, rmax=6.0, nmax=8):
    poly = [(-rmax, -rmax), (rmax, -rmax), (rmax, rmax), (-rmax, rmax)]
    V = []
    for i in range(-nmax, nmax + 1):
        for j in range(-nmax, nmax + 1):
            if i == 0 and j == 0:
                continue
            v = (i * b1[0] + j * b2[0], i * b1[1] + j * b2[1])
            if math.hypot(*v) <= 5.5:
                V.append(v)
    for v in V:
        c = (v[0] ** 2 + v[1] ** 2) / 2
        out, m = [], len(poly)
        for k in range(m):
            a, b = poly[k], poly[(k + 1) % m]
            da = v[0] * a[0] + v[1] * a[1] - c
            db = v[0] * b[0] + v[1] * b[1] - c
            if da <= 0:
                out.append(a)
            if (da < 0 < db) or (db < 0 < da):
                t = da / (da - db)
                out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
        poly = out
        if len(poly) < 3:
            return None
    P = []
    for p in poly:
        if not P or math.hypot(p[0] - P[-1][0], p[1] - P[-1][1]) > 1e-9:
            P.append(p)
    if len(P) > 1 and math.hypot(P[0][0] - P[-1][0], P[0][1] - P[-1][1]) < 1e-9:
        P.pop()
    return P


def reseau_unite(rho, thd):
    """Cellule de Voronoi normalisee a un diametre de 1, et base correspondante."""
    th = math.radians(thd)
    b1 = (1.0, 0.0)
    b2 = (rho * math.cos(th), rho * math.sin(th))
    P = cellule_voronoi(b1, b2)
    D = max(math.dist(p, q) for p in P for q in P)
    k = 1.0 / D
    return ([(k * x, k * y) for (x, y) in P],
            (k * b1[0], k * b1[1]), (k * b2[0], k * b2[1]))


def _dm(P, Q):
    """(min, max) des distances entre deux polygones convexes, en flottants."""
    def pt_seg(X, Y):
        A = np.asarray(Y)[None, :, :]
        B = np.roll(np.asarray(Y), -1, axis=0)[None, :, :]
        AB = B - A
        L = np.maximum((AB ** 2).sum(-1), 1e-30)
        t = np.clip(((X[:, None, :] - A) * AB).sum(-1) / L, 0, 1)
        pr = A + t[..., None] * AB
        return np.sqrt(((X[:, None, :] - pr) ** 2).sum(-1)).min()

    X, Y = np.asarray(P), np.asarray(Q)
    dmin = min(pt_seg(X, Y), pt_seg(Y, X))
    dmax = np.sqrt(((X[:, None, :] - Y[None, :, :]) ** 2).sum(-1)).max()
    return float(dmin), float(dmax)


def graphe_echelle(P, b1, b2, delta, tol=1e-12):
    """Graphe de conflit de l'anneau, entierement (sans fenetre arbitraire).

    Sommets : differences (i,j) dont la cellule peut etre en conflit avec (0,0),
    plus l'origine. Renvoie (liste des offsets, adjacence, dict des (dmin,dmax)).
    """
    # Bornes d'enumeration EXACTES : (i,j) = M^{-1} v, donc |i| <= |B2|.|v|/|det| et
    # |j| <= |B1|.|v|/|det|. Les prendre en indices (comme le premier jet) oubliait des
    # conflits des que |B1| depassait delta (bug attrape par la verification directe).
    det = abs(b1[0] * b2[1] - b1[1] * b2[0])
    Rmax = 1.0 / delta + 1.2
    Ri = int(math.ceil(math.hypot(*b2) * Rmax / det)) + 1
    Rj = int(math.ceil(math.hypot(*b1) * Rmax / det)) + 1
    cand = []
    for i in range(-Ri, Ri + 1):
        for j in range(-Rj, Rj + 1):
            if i == 0 and j == 0:
                continue
            D = math.hypot(delta * (i * b1[0] + j * b2[0]), delta * (i * b1[1] + j * b2[1]))
            if abs(D - 1) <= delta * 1.05:          # condition necessaire
                cand.append((i, j))
    Pd = [(delta * x, delta * y) for (x, y) in P]
    offsets = [(0, 0)] + cand
    n = len(offsets)
    nv = len(Pd)
    cen = np.array([(delta * (i * b1[0] + j * b2[0]), delta * (i * b1[1] + j * b2[1]))
                    for (i, j) in offsets])
    Vp = (np.asarray(Pd)[None, :, :] + cen[:, None, :]).reshape(-1, 2)
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
    conflit = (lo <= 1 + tol) & (vv >= 1 - tol)
    np.fill_diagonal(conflit, False)
    adj = [set(np.nonzero(conflit[r])[0]) for r in range(n)]
    return offsets, adj


def clique_max_avec0(adj):
    """Plus grande clique contenant le sommet 0 (graphe sommet-transitif)."""
    V = adj[0] | {0}
    sous = [sorted(adj[v] & V) for v in range(len(adj))]
    best = [0, None]

    def bk(Rr, P, X):
        if not P and not X:
            if len(Rr) > best[0]:
                best[0], best[1] = len(Rr), set(Rr)
            return
        if len(Rr) + len(P) <= best[0]:
            return
        u = max(P | X, key=lambda v: len(set(sous[v]) & P))
        for v in list(P - set(sous[u])):
            bk(Rr | {v}, P & set(sous[v]), X & set(sous[v]))
            P.discard(v)
            X.add(v)

    bk({0}, set(sous[0]) - {0}, set())
    return best[0], best[1]


def omega_echelle(rho, thd, delta, retour_clique=False):
    P, b1, b2 = reseau_unite(rho, thd)
    offsets, adj = graphe_echelle(P, b1, b2, delta)
    w, cl = clique_max_avec0(adj)
    if retour_clique:
        return w, [offsets[i] for i in sorted(cl)]
    return w


if __name__ == "__main__":
    import time
    t0 = time.time()
    print("validation contre le balayage (delta = 0,999) :")
    for (rho, th, attendu) in [(1.0, 60, 7), (1.0, 90, 9), (1.9, 70, 7), (1.7, 120, 7)]:
        w = omega_echelle(rho, th, 0.999)
        print(f"  rho={rho} theta={th} : omega={w} (balayage {attendu}) "
              f"{'ok' if w == attendu else 'DESACCORD'}")
    print(f"\ncourbe exacte omega(delta) :")
    for (rho, th, nom) in [(1.0, 60, "hexagonal"), (1.0, 90, "carre"), (1.9, 70, "anisotrope")]:
        ligne = []
        for d in (0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.999):
            ligne.append(f"{d:.2f}:{omega_echelle(rho, th, d)}")
        print(f"  {nom:12s} " + "  ".join(ligne))
    print(f"({time.time()-t0:.1f}s)")
