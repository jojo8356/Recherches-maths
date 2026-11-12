"""Phase 8 / T1 - cellules non simplement connexes.
Une cellule convexe P est remplacee par un ANNEAU (P prive de son homothetique c+rho(P-c))
plus la cellule interieure (l'homothetique). L'anneau est connexe, non simplement connexe,
de meme diametre que P ; la cellule interieure est logee dans le trou.
Chaque cellule = liste de polygones simples (pour que les distances restent exactes)."""
import math, sys
import numpy as np
sys.path.insert(0, '../phase6')
from partition2 import voronoi_tore, wrap, normaliser, clique_max, k_color


def _edges(polys):
    E = []
    for P in polys:
        n = len(P)
        for k in range(n):
            E.append((P[k], P[(k + 1) % n]))
    return np.array(E, dtype=float)


def _verts(polys):
    return np.array([p for P in polys for p in P], dtype=float)


def _pt_seg(P, S):
    A = S[None, :, 0, :]; B = S[None, :, 1, :]
    AB = B - A; L = (AB ** 2).sum(-1); L = np.where(L < 1e-30, 1e-30, L)
    t = np.clip(((P[:, None, :] - A) * AB).sum(-1) / L, 0, 1)
    proj = A + t[..., None] * AB
    return np.sqrt(((P[:, None, :] - proj) ** 2).sum(-1))


def dmin_cells(A, B):
    EA, EB = _edges(A), _edges(B)
    d1 = _pt_seg(EA[:, 0, :], EB).min()
    d2 = _pt_seg(EB[:, 0, :], EA).min()
    return float(min(d1, d2))


def dmax_cells(A, B):
    VA, VB = _verts(A), _verts(B)
    return float(np.sqrt(((VA[:, None, :] - VB[None, :, :]) ** 2).sum(-1)).max())


def diam_cell(A):
    return dmax_cells(A, A)


def aire_cell(A):
    s = 0.0
    for P in A:
        for k in range(len(P)):
            x1, y1 = P[k]; x2, y2 = P[(k + 1) % len(P)]
            s += x1 * y2 - x2 * y1
    return s / 2


def partage(P, rho):
    """P convexe -> (anneau = liste de quadrilateres, interieur = polygone)"""
    n = len(P)
    c = (sum(p[0] for p in P) / n, sum(p[1] for p in P) / n)
    inner = [(c[0] + rho * (p[0] - c[0]), c[1] + rho * (p[1] - c[1])) for p in P]
    anneau = []
    for k in range(n):
        a = P[k]; b = P[(k + 1) % n]; ia = inner[k]; ib = inner[(k + 1) % n]
        anneau.append([a, b, ib, ia])
    return anneau, inner


def construit(seeds, U1, U2, choix, rho, verbose=False):
    cells0 = voronoi_tore(seeds, U1, U2)
    if cells0 is None:
        return None
    cells = []
    for i, P in enumerate(cells0):
        if choix(i):
            anneau, inner = partage(P, rho)
            cells.append(anneau); cells.append([inner])
        else:
            cells.append([P])
    if verbose:
        print(f"    {len(cells0)} cellules -> {len(cells)} ; dont "
              f"{sum(1 for c in cells if len(c) > 1)} anneaux")
    return cells


def graphe(cells, U1, U2, margin=0.01):
    n = len(cells)
    cx = [_verts(c).mean(0) for c in cells]
    rad = [max(math.dist(tuple(q), tuple(cc)) for q in _verts(c)) for c, cc in zip(cells, cx)]
    adj = [set() for _ in range(n)]
    mm = []
    for i in range(n):
        for j in range(i + 1, n):
            dv = wrap((cx[j][0] - cx[i][0], cx[j][1] - cx[i][1]), U1, U2)
            if math.hypot(*dv) > 1.0 + rad[i] + rad[j] + 0.05:
                continue
            B = [[(x - cx[j][0] + cx[i][0] + dv[0], y - cx[j][1] + cx[i][1] + dv[1])
                  for x, y in P] for P in cells[j]]
            lo = dmin_cells(cells[i], B); hi = dmax_cells(cells[i], B)
            if lo <= 1 + margin and hi >= 1 - margin:
                adj[i].add(j); adj[j].add(i); mm.append(min(hi - 1, 1 - lo))
    return adj, mm
