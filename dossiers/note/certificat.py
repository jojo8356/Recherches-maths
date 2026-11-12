"""Certificat rigoureux du theoreme A : omega >= 7 pour TOUT reseau du domaine reduit.

Principe
--------
Pour prouver qu'une clique de 7 cellules existe pour tout (rho,theta) d'une boite,
il suffit d'exhiber pour chaque paire deux couples de points TEMOINS
  - un couple proche   (distance <= seuil T)   prouve  dmin <= T
  - un couple eloigne  (distance >= seuil T)   prouve  dmax >= T
et de prouver que ces points appartiennent aux cellules pour tout (rho,theta) de la
boite. L'appartenance a une cellule de Voronoi est une conjonction d'inegalites
lineaires, donc verifiable par arithmetique d'intervalles. Aucune structure
combinatoire n'a besoin d'etre constante sur la boite.

Encadrement du diametre
-----------------------
P_sup = intersection des contraintes actives en 5 points de la boite. Comme c'est
l'intersection d'un SOUS-ENSEMBLE des contraintes, P_sup contient la cellule ; son
diametre majore donc celui de toutes les cellules de la boite. Tout sommet de P_sup
est l'intersection d'une paire de contraintes : on enumere toutes les paires et on
n'ecarte que celles demontrees infaisables, donc le majorant est sur.

Arithmetique
------------
mpmath.iv (30 chiffres) pour les objets geometriques ; numpy pour les verifications
en masse, avec elargissement explicite de 1e-12 (les valeurs sont d'ordre 1 et
l'erreur d'arrondi relative est de l'ordre de 1e-16).
"""
import math
import numpy as np
from mpmath import iv

iv.dps = 30

EPS = 1e-3          # cellules de diametre <= 1 - EPS
SEUIL_R2 = 25.0     # contraintes avec |v|^2 >= 25 : automatiques (cellule dans B(0,2.5))
NIVEAUX = (1.0, 0.9995, 0.998, 0.995, 0.99, 0.98, 0.96, 0.94, 0.9)   # retractions
GONFLE = 1e-12      # elargissement des intervalles vectorises


# ------------------------------------------------------------------ flottants
def bvec(rho, th):
    return (1.0, 0.0), (rho * math.cos(th), rho * math.sin(th))


def cellule(b1, b2, rmax=6.0, nmax=8):
    """Sommets de la cellule de Voronoi de l'origine."""
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


def contraintes_actives(b1, b2, P, nmax=8, tol=1e-9):
    A = []
    for i in range(-nmax, nmax + 1):
        for j in range(-nmax, nmax + 1):
            if i == 0 and j == 0:
                continue
            v = (i * b1[0] + j * b2[0], i * b1[1] + j * b2[1])
            if math.hypot(*v) > 5.5:
                continue
            c = (v[0] ** 2 + v[1] ** 2) / 2
            sl = [v[0] * p[0] + v[1] * p[1] - c for p in P]
            if min(abs(x) for x in sl) < tol and max(sl) < tol:
                A.append((i, j))
    return A


def graphe_rapide(P, b1, b2, T, R=3):
    """Matrice de conflit (seuil T) pour les (2R+1)^2 cellules, vectorise."""
    P = np.asarray(P)
    nv = len(P)
    idx = [(i, j) for i in range(-R, R + 1) for j in range(-R, R + 1)]
    n = len(idx)
    cen = np.array([(i * b1[0] + j * b2[0], i * b1[1] + j * b2[1]) for i, j in idx])
    Vp = (P[None, :, :] + cen[:, None, :]).reshape(-1, 2)
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
    return lo, vv, idx


def clique_max(adj, taille_max=12):
    best = [0, None]

    def bk(Rr, P, X):
        if not P and not X:
            if len(Rr) > best[0]:
                best[0], best[1] = len(Rr), set(Rr)
            return
        if len(Rr) + len(P) <= best[0]:
            return
        u = max(P | X, key=lambda v: len(adj[v] & P))
        for v in list(P - adj[u]):
            bk(Rr | {v}, P & adj[v], X & adj[v])
            P.discard(v)
            X.add(v)

    bk(set(), set(range(len(adj))), set())
    return best[0], best[1]


# ------------------------------------------------------------------ intervalles
def norm2_min(i, j, rho0, rho1, th0, th1):
    """Minorant demontre de |i b1 + j b2|^2 sur la boite (theta en degres)."""
    c0, c1 = math.cos(math.radians(th0)), math.cos(math.radians(th1))   # c0 >= c1
    mixed = 2 * rho0 * c1 * i * j if i * j >= 0 else 2 * rho1 * c0 * i * j
    return i * i + mixed + rho0 * rho0 * j * j


def iv_bvect(rho, th):
    return (iv.mpf(1), iv.mpf(0)), (rho * iv.cos(th), rho * iv.sin(th))


def iv_vec(b1, b2, ij):
    i, j = ij
    return (i * b1[0] + j * b2[0], i * b1[1] + j * b2[1])


def iv_norm2(v):
    return v[0] * v[0] + v[1] * v[1]


def iv_solve(v, w, det=None):
    if det is None:
        det = v[0] * w[1] - v[1] * w[0]
    if det.a <= 0 <= det.b:
        return None
    cv, cw = iv_norm2(v) / 2, iv_norm2(w) / 2
    return (cv * w[1] - v[1] * cw) / det, (v[0] * cw - cv * w[0]) / det


def iv_dist2(P, Q):
    dx, dy = P[0] - Q[0], P[1] - Q[1]
    return dx * dx + dy * dy


def masse(ivects):
    """Transforme des listes de vecteurs-intervalles en tableaux numpy (lo,hi)."""
    vx = np.array([[float(v[0].a) - GONFLE, float(v[0].b) + GONFLE] for v in ivects])
    vy = np.array([[float(v[1].a) - GONFLE, float(v[1].b) + GONFLE] for v in ivects])
    return vx, vy


def prod_iv(a, b):
    """Produit d'intervalles : a (n,2), b (m,2) -> (n,m,2)."""
    c = np.stack([a[:, None, 0] * b[None, :, 0], a[:, None, 0] * b[None, :, 1],
                  a[:, None, 1] * b[None, :, 0], a[:, None, 1] * b[None, :, 1]], axis=2)
    return np.stack([c.min(axis=2), c.max(axis=2)], axis=2)


def somme_iv(a, b):
    return np.stack([a[..., 0] + b[..., 0], a[..., 1] + b[..., 1]], axis=-1)


def carre_iv(a):
    """Carre d'un intervalle (a de forme (n,2)) : gere le changement de signe."""
    lo = np.where((a[:, 0] <= 0) & (a[:, 1] >= 0), 0.0,
                  np.minimum(a[:, 0] ** 2, a[:, 1] ** 2))
    hi = np.maximum(a[:, 0] ** 2, a[:, 1] ** 2)
    return np.stack([lo, hi], axis=1)


# ------------------------------------------------------------------ certification
def certifie(rho0, rho1, th0, th1, k=7, export=False):
    rhoc, thc = (rho0 + rho1) / 2, (th0 + th1) / 2
    thr = math.radians(thc)
    b1, b2 = bvec(rhoc, thr)
    P = cellule(b1, b2)
    if P is None:
        return False, {"raison": "cellule vide"}

    # contraintes actives en 5 points -> P_sup (sur-ensemble de la cellule)
    A = set()
    for (rr, tt) in ((rhoc, thr), (rho0, math.radians(th0)), (rho0, math.radians(th1)),
                     (rho1, math.radians(th0)), (rho1, math.radians(th1))):
        bb1, bb2 = bvec(rr, tt)
        PP = cellule(bb1, bb2)
        if PP is None:
            return False, {"raison": "cellule vide (coin)"}
        A |= set(contraintes_actives(bb1, bb2, PP))
    A = sorted(A)
    if len(A) < 4:
        return False, {"raison": "contraintes actives < 4"}

    rib = iv.mpf([rho0, rho1])
    tib = iv.mpf([math.radians(th0), math.radians(th1)])
    ib1, ib2 = iv_bvect(rib, tib)
    ivA = [iv_vec(ib1, ib2, ij) for ij in A]
    cA = [iv_norm2(v) / 2 for v in ivA]

    sommets = []
    for a1 in range(len(A)):
        for a2 in range(a1 + 1, len(A)):
            if A[a1][0] * A[a2][1] - A[a1][1] * A[a2][0] == 0:
                continue                                  # paralleles : aucun sommet
            detB = ib1[0] * ib2[1] - ib1[1] * ib2[0]
            det = detB * (A[a1][0] * A[a2][1] - A[a1][1] * A[a2][0])
            sol = iv_solve(ivA[a1], ivA[a2], det)
            if sol is None:
                return False, {"raison": "determinant indetermine"}
            faisable = True
            for qq in range(len(A)):
                if (ivA[qq][0] * sol[0] + ivA[qq][1] * sol[1] - cA[qq]).a > 0:
                    faisable = False
                    break
            if faisable:
                sommets.append(sol)
    if len(sommets) < 3:
        return False, {"raison": "P_sup degenere"}

    zero = (iv.mpf(0), iv.mpf(0))
    rmax2 = max(float(iv_dist2(s, zero).b) for s in sommets)
    if rmax2 > 2.5 ** 2:
        return False, {"raison": "P_sup hors boule 2.5"}
    diam_max = math.sqrt(max(float(iv_dist2(sommets[i], sommets[j]).b)
                             for i in range(len(sommets)) for j in range(i + 1, len(sommets))))
    # echelle maximalement admissible : diametre de cellule = 1 - EPS pour CHAQUE t.
    # Le seuil est donc T(t) = diam(t)/(1-EPS), encadre par [T_min, T_max].
    Tc = (max(math.dist(p, q) for p in P for q in P)) / (1 - EPS)   # au centre
    T_max = diam_max / (1 - EPS)
    T_min = None                                                     # apres les temoins

    # ------------------------------------------------------------------
    # TEMOINS
    #  - generiques : sommets et points d'aretes a plusieurs retractions (pour dmax)
    #  - par paire  : point d'approche minimale, tire vers l'interieur (pour dmin)
    # Tous sont verifies appartenir a la cellule pour tout t de la boite ; ceux
    # qui ne se certifient pas sont ecartes.
    # ------------------------------------------------------------------
    nv = len(P)
    cen = (sum(p[0] for p in P) / nv, sum(p[1] for p in P) / nv)
    echelle = max(math.dist(p, cen) for p in P)

    def points_cellule(lam):
        """Sommets de la cellule retractes vers le centroide : servent a dmax et a diam_min."""
        return [(cen[0] + lam * (q[0] - cen[0]), cen[1] + lam * (q[1] - cen[1])) for q in P]

    gen = []                                     # temoins generiques
    for lam in NIVEAUX:
        gen += points_cellule(lam)

    # graphe de conflit au centre ; clique ROBUSTE si possible
    diam_c = max(math.dist(p, q) for p in P for q in P)
    Tc = diam_c / (1 - EPS)
    T_max = diam_max / (1 - EPS)
    lo, vv, idx = graphe_rapide(P, b1, b2, Tc, R=3)
    best_cl = None
    for delta in (0.15, 0.08, 0.03, 0.01, 0.0):
        conflit = (lo < Tc * (1 - delta)) & (vv > Tc * (1 + delta))
        np.fill_diagonal(conflit, False)
        adj = [set(np.nonzero(conflit[r])[0]) for r in range(len(idx))]
        w, cl0 = clique_max(adj)
        if w >= k:
            best_cl = sorted(idx[i] for i in cl0)[:k]
            break
    if best_cl is None:
        return False, {"raison": f"pas de clique {k}"}
    cl = best_cl

    def centre(ij):
        return (ij[0] * b1[0] + ij[1] * b2[0], ij[0] * b1[1] + ij[1] * b2[1])

    def proj_seg(p, a, b):
        ax, ay = b[0] - a[0], b[1] - a[1]
        L = ax * ax + ay * ay
        t = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / L))
        return (a[0] + t * ax, a[1] + t * ay)

    def plus_proches(Pa, Pb):
        """Point d'approche minimale entre deux polygones convexes (flottants)."""
        best = (1e30, Pa[0], Pb[0])
        for A, B, sens in ((Pa, Pb, 1), (Pb, Pa, -1)):
            for j in range(len(B)):
                a, b = B[j], B[(j + 1) % len(B)]
                for p in A:
                    q = proj_seg(p, a, b)
                    d = math.dist(p, q)
                    if d < best[0]:
                        best = (d, p, q) if sens == 1 else (d, q, p)
        return best[1], best[2]

    PAIRES = [(cl[a], cl[b]) for a in range(k) for b in range(a + 1, k)]
    par_paire = []
    for (oa, ob) in PAIRES:
        ca, cb = centre(oa), centre(ob)
        Pa = [(p[0] + ca[0], p[1] + ca[1]) for p in P]
        Pb = [(p[0] + cb[0], p[1] + cb[1]) for p in P]
        p, q = plus_proches(Pa, Pb)
        locaux = []
        for delta in (0.0, 1e-3, 4e-3, 1.5e-2, 4e-2):
            la = (cen[0] + (1 - delta) * (p[0] - ca[0] - cen[0]) + ca[0],
                  cen[1] + (1 - delta) * (p[1] - ca[1] - cen[1]) + ca[1])
            lb = (cen[0] + (1 - delta) * (q[0] - cb[0] - cen[0]) + cb[0],
                  cen[1] + (1 - delta) * (q[1] - cb[1] - cen[1]) + cb[1])
            locaux.append(((la[0] - ca[0], la[1] - ca[1]), (lb[0] - cb[0], lb[1] - cb[1])))
        par_paire.append(locaux)

    # liste complete des points a certifier (reperes dans la cellule de l'origine)
    tous = list(gen)
    for locaux in par_paire:
        for (la, lb) in locaux:
            tous.append(la)
            tous.append(lb)
    tous = np.array(tous)

    # verification d'appartenance, vectorisee
    vv_lat = [(i, j) for i in range(-9, 10) for j in range(-9, 10)
              if not (i == 0 and j == 0) and norm2_min(i, j, rho0, rho1, th0, th1) < SEUIL_R2]
    ivv = [iv_vec(ib1, ib2, ij) for ij in vv_lat]
    vx, vy = masse(ivv)
    sx, sy = carre_iv(vx), carre_iv(vy)
    n2 = np.stack([sx[:, 0] + sy[:, 0], sx[:, 1] + sy[:, 1]], axis=1)
    cx = np.stack([(n2[:, 0] - GONFLE) / 2, (n2[:, 1] + GONFLE) / 2], axis=1)
    px = np.stack([tous[:, 0] - GONFLE, tous[:, 0] + GONFLE], axis=1)
    py = np.stack([tous[:, 1] - GONFLE, tous[:, 1] + GONFLE], axis=1)
    val = somme_iv(prod_iv(vx, px), prod_iv(vy, py))
    val[:, :, 0] -= cx[:, None, 0]
    val[:, :, 1] -= cx[:, None, 1]
    mx = val[:, :, 1].max(axis=0)
    garde = mx < 0
    if garde.sum() < 4:
        return False, {"raison": "trop peu de temoins certifies", "n": int(garde.sum())}
    marge_app = float(-mx[garde].max())
    tous_c = tous[garde]
    ngen = len(gen)
    gen_c = tous_c[:int(garde[:ngen].sum())] if garde[:ngen].any() else tous_c[:0]
    # index des points de paire certifies
    idxp = {}
    pos = ngen
    for ip, locaux in enumerate(par_paire):
        l = []
        for j in range(len(locaux)):
            if garde[pos] and garde[pos + 1]:
                l.append(((tous[pos][0], tous[pos][1]), (tous[pos + 1][0], tous[pos + 1][1])))
            pos += 2
        idxp[ip] = l

    if len(gen_c) < 3:
        return False, {"raison": "temoins generiques insuffisants"}
    diam_min = max(math.dist(gen_c[i], gen_c[j]) for i in range(len(gen_c))
                   for j in range(i + 1, len(gen_c)))
    T_min = diam_min / (1 - EPS)

    # --- verification des paires
    gx = np.stack([gen_c[:, 0] - GONFLE, gen_c[:, 0] + GONFLE], axis=1)
    gy = np.stack([gen_c[:, 1] - GONFLE, gen_c[:, 1] + GONFLE], axis=1)
    marge_min = 1e30
    for ip, (oa, ob) in enumerate(PAIRES):
        vaS = iv_vec(ib1, ib2, oa)
        vbS = iv_vec(ib1, ib2, ob)
        vxa = (float(vaS[0].a) - GONFLE, float(vaS[0].b) + GONFLE)
        vya = (float(vaS[1].a) - GONFLE, float(vaS[1].b) + GONFLE)
        vxb = (float(vbS[0].a) - GONFLE, float(vbS[0].b) + GONFLE)
        vyb = (float(vbS[1].a) - GONFLE, float(vbS[1].b) + GONFLE)
        # proche : couples dedies a la paire
        mn = -1e30
        for (pa, pb) in idxp[ip]:
            sup = _sup_dist(pa, pb, vxa, vya, vxb, vyb)
            mn = max(mn, (T_min * T_min - sup) / (T_min * T_min))
            if mn > 0:
                break
        # eloigne : temoins generiques
        fa = (oa[0] * b1[0] + oa[1] * b2[0], oa[0] * b1[1] + oa[1] * b2[1])
        fb = (ob[0] * b1[0] + ob[1] * b2[0], ob[0] * b1[1] + ob[1] * b2[1])
        d0 = np.hypot(gen_c[:, None, 0] + fa[0] - gen_c[None, :, 0] - fb[0],
                      gen_c[:, None, 1] + fa[1] - gen_c[None, :, 1] - fb[1])
        ordre = np.argsort(-d0, axis=None)[:4]
        mf = -1e30
        for kk in list(ordre):
            u, w2 = np.unravel_index(kk, d0.shape)
            inf = _inf_dist(gen_c[u], gen_c[w2], vxa, vya, vxb, vyb)
            mf = max(mf, (inf - T_max * T_max) / (T_max * T_max))
            if mf > 0:
                break
        if mn <= 0 or mf <= 0:
            return False, {"raison": "paire non certifiee", "paire": (oa, ob),
                           "marge_proche": mn, "marge_eloignee": mf,
                           "nmoyens_proches": len(idxp[ip])}
        marge_min = min(marge_min, mn, mf)

    info = {"Tc": Tc, "T_min": T_min, "T_max": T_max,
            "diam_min": diam_min, "diam_max": diam_max,
            "marge": marge_min, "marge_appartenance": marge_app, "clique": cl}
    if export:
        # TEMOINS exportes : la verification independante (verif_exacte.py) ne doit
        # dependre que de ces donnees, pas du code qui les a trouvees.
        # Coordonnees locales (repere de la cellule de l'origine), en flottants :
        # json les ecrit avec repr, donc l'aller-retour est exact (dyadiques).
        paires = []
        for ip, (oa, ob) in enumerate(PAIRES):
            paires.append({"a": [int(oa[0]), int(oa[1])], "b": [int(ob[0]), int(ob[1])],
                           "temoins": [[[float(pa[0]), float(pa[1])],
                                        [float(pb[0]), float(pb[1])]]
                                       for (pa, pb) in idxp[ip]]})
        info["_tem"] = {"A": [[int(i), int(j)] for (i, j) in A],
                        "clique": [[int(i), int(j)] for (i, j) in cl],
                        "gen": gen_c.tolist(),
                        "paires": paires,
                        "T_min": float(T_min), "T_max": float(T_max),
                        "diam_min": float(diam_min), "diam_max": float(diam_max)}
    return True, info



def _box_pt(q, vx, vy):
    """Enveloppe du point q (deja dans le repere de la cellule) translate de (vx,vy)."""
    return (np.array([q[0] + vx[0], q[0] + vx[1]]),
            np.array([q[1] + vy[0], q[1] + vy[1]]))


def _sup_dist(qa, qb, vxa, vya, vxb, vyb):
    """Majorant sur de la distance au carre entre les deux points temoins translates."""
    A = _box_pt(qa, vxa, vya)
    B = _box_pt(qb, vxb, vyb)
    dx = np.array([A[0][0] - B[0][1], A[0][1] - B[0][0]])
    dy = np.array([A[1][0] - B[1][1], A[1][1] - B[1][0]])
    return (max(dx[0] ** 2, dx[1] ** 2) + max(dy[0] ** 2, dy[1] ** 2)) * (1 + 1e-12) + GONFLE


def _inf_dist(qa, qb, vxa, vya, vxb, vyb):
    """Minorant sur de la distance au carre entre les deux points temoins translates."""
    A = _box_pt(qa, vxa, vya)
    B = _box_pt(qb, vxb, vyb)
    dx = 0.0 if (A[0][0] <= B[0][1] and B[0][0] <= A[0][1]) else min(abs(A[0][0] - B[0][1]), abs(B[0][0] - A[0][1]))
    dy = 0.0 if (A[1][0] <= B[1][1] and B[1][0] <= A[1][1]) else min(abs(A[1][0] - B[1][1]), abs(B[1][0] - A[1][1]))
    return (dx * dx + dy * dy) * (1 - 1e-12) - GONFLE


if __name__ == "__main__":
    import time
    t0 = time.time()
    for t in [(1.0, 1.02, 60, 61), (1.9, 1.92, 69, 70), (1.0, 1.005, 90, 90.5)]:
        ok, info = certifie(*t)
        print(t, "->", ok, {k: (round(v, 5) if isinstance(v, float) else v)
                            for k, v in info.items() if k in ('marge', 'raison', 'T')})
    print(f"{(time.time()-t0)/3*1000:.0f} ms/boite")
