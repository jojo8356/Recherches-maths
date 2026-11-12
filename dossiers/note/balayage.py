"""Balayage de l'espace des reseaux (2 dimensions apres similitude).
Base reduite de Minkowski : |b1|=1, |b2|=rho>=1, angle theta in [60,120].
Pour chaque reseau : cellule de Voronoi, diametre normalise a 1-eps, graphe de conflit, omega.
Tout vectorise (numpy) pour tenir la resolution."""
import math
import numpy as np


def cellule_voronoi(b1, b2, rmax=6.0):
    poly = [(-rmax, -rmax), (rmax, -rmax), (rmax, rmax), (-rmax, rmax)]
    V = []
    for i in range(-6, 7):
        for j in range(-6, 7):
            if i == 0 and j == 0:
                continue
            v = (i * b1[0] + j * b2[0], i * b1[1] + j * b2[1])
            if math.hypot(*v) <= 5.5:
                V.append(v)
    for v in V:
        c = (v[0] ** 2 + v[1] ** 2) / 2
        out = []
        m = len(poly)
        for k in range(m):
            a = poly[k]
            b = poly[(k + 1) % m]
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
    return poly


def graphe_reseau(rho, theta_deg, eps=1e-3, R=3):
    th = math.radians(theta_deg)
    b1 = (1.0, 0.0)
    b2 = (rho * math.cos(th), rho * math.sin(th))
    C = cellule_voronoi(b1, b2)
    if C is None:
        return None, None
    Ca = np.array(C)
    D = np.sqrt(((Ca[:, None, :] - Ca[None, :, :]) ** 2).sum(-1)).max()
    k = (1 - eps) / D
    Ca = Ca * k
    b1 = (k * b1[0], k * b1[1])
    b2 = (k * b2[0], k * b2[1])
    idx = [(i, j) for i in range(-R, R + 1) for j in range(-R, R + 1)]
    n = len(idx)
    cen = np.array([(i * b1[0] + j * b2[0], i * b1[1] + j * b2[1]) for i, j in idx])
    nv = Ca.shape[0]
    V = (Ca[None, :, :] + cen[:, None, :]).reshape(-1, 2)
    Vnext = np.roll(V.reshape(n, nv, 2), -1, axis=1).reshape(-1, 2)
    S = np.stack([V, Vnext], axis=1)
    A = S[None, :, 0, :]
    B = S[None, :, 1, :]
    AB = B - A
    L = (AB ** 2).sum(-1)
    L = np.where(L < 1e-30, 1e-30, L)
    t = np.clip(((V[:, None, :] - A) * AB).sum(-1) / L, 0, 1)
    proj = A + t[..., None] * AB
    Dm = np.sqrt(((V[:, None, :] - proj) ** 2).sum(-1)).reshape(n, nv, n, nv)
    lo = Dm.min(axis=(1, 3))
    VV = np.sqrt(((V[:, None, :] - V[None, :, :]) ** 2).sum(-1)).reshape(n, nv, n, nv).max(axis=(1, 3))
    conflit = (lo < 1) & (VV > 1)
    np.fill_diagonal(conflit, False)
    adj = [set(np.nonzero(conflit[i])[0]) for i in range(n)]
    return adj, n


def clique_max(adj):
    best = [0, None]

    def bk(Rr, P, X):
        if not P and not X:
            if len(Rr) > best[0]:
                best[0] = len(Rr)
                best[1] = set(Rr)
            return
        u = max(P | X, key=lambda v: len(adj[v] & P)) if (P | X) else None
        for v in list(P - adj[u]):
            bk(Rr | {v}, P & adj[v], X & adj[v])
            P.discard(v)
            X.add(v)

    bk(set(), set(range(len(adj))), set())
    return best[0], best[1]


def omega_reseau(rho, theta_deg, eps=1e-3, R=3, verbose=False):
    adj, n = graphe_reseau(rho, theta_deg, eps, R)
    if adj is None:
        return None
    w, cl = clique_max(adj)
    if verbose:
        print(f"  rho={rho:.3f} theta={theta_deg:.2f} n={n} omega={w}")
    return w


if __name__ == "__main__":
    import time
    t0 = time.time()
    for rho, th in ((1.0, 60), (1.0, 90), (1.0, 30)):
        print(f"calibration rho={rho} theta={th} : omega = {omega_reseau(rho, th)}  ({time.time()-t0:.1f}s)")
