"""Verification EXACTE de omega aux echelles de tangence : corps Q(sqrt d), aucun flottant.

Le treillis hexagonal normalise (d=3), le carre (d=2) et le rectangle 2:1 (d=5) ont toutes
leurs coordonnees dans un corps quadratique reel. Les distances carrees y vivent aussi, donc
« dmin <= 1 <= dmax » est une decision de signe exacte. Sert de juge pour la tolerance du
calcul flottant (voir tangence.py).
"""
from fractions import Fraction as F
import time, sys

D = 3                                   # corps courant : Q(sqrt D)

def e(a, b=0): return (F(a), F(b))
def add(x, y): return (x[0]+y[0], x[1]+y[1])
def sub(x, y): return (x[0]-y[0], x[1]-y[1])
def mul(x, y): return (x[0]*y[0] + D*x[1]*y[1], x[0]*y[1] + x[1]*y[0])
def div(x, y):
    den = y[0]*y[0] - D*y[1]*y[1]
    assert den != 0
    return ((x[0]*y[0] - D*x[1]*y[1])/den, (x[1]*y[0]-x[0]*y[1])/den)
def sgn(x):
    a, b = x
    if b == 0: return (a > 0) - (a < 0)
    if a == 0: return (b > 0) - (b < 0)
    if a > 0 and b > 0: return 1
    if a < 0 and b < 0: return -1
    lhs, rhs = a*a, D*b*b
    if a > 0: return (lhs > rhs) - (lhs < rhs)
    return (rhs > lhs) - (rhs < lhs)

Z = e(0); UN = e(1)
def lt(x, y): return sgn(sub(x, y)) < 0
def le(x, y): return sgn(sub(x, y)) <= 0

class Pt:
    __slots__ = ('x', 'y')
    def __init__(self, x, y): self.x, self.y = x, y
    def __sub__(self, o): return Pt(sub(self.x, o.x), sub(self.y, o.y))
def norm2(v): return add(mul(v.x, v.x), mul(v.y, v.y))

def d2_pt_seg(p, a, b):
    ab = b - a
    L = norm2(ab)
    if sgn(L) == 0: return norm2(p - a)
    ap = p - a
    t = div(add(mul(ap.x, ab.x), mul(ap.y, ab.y)), L)
    if lt(t, Z): t = Z
    if lt(UN, t): t = UN
    proj = Pt(add(a.x, mul(t, ab.x)), add(a.y, mul(t, ab.y)))
    return norm2(p - proj)

def d2_min(A, B):
    n = len(B); best = None
    for X, Y in ((A, B), (B, A)):
        for p in X:
            for k in range(n):
                d = d2_pt_seg(p, Y[k], Y[(k+1) % n])
                if best is None or lt(d, best): best = d
    return best

def d2_max(A, B):
    best = None
    for p in A:
        for q in B:
            d = norm2(p - q)
            if best is None or lt(best, d): best = d
    return best

def conflict(A, B):
    return le(d2_min(A, B), UN) and le(UN, d2_max(A, B))

# ---------------------------------------------------------------- les trois reseaux
def cellules_hexa(delta):
    d = e(F(delta).limit_denominator(10**7))
    r34, q, h = e(0, F(1, 4)), e(F(1, 4)), e(F(1, 2))
    neg = lambda v: (-v[0], -v[1])
    base = [Pt(r34, q), Pt(Z, h), Pt(neg(r34), q), Pt(neg(r34), neg(q)), Pt(Z, neg(h)), Pt(r34, neg(q))]
    P = [Pt(mul(p.x, d), mul(p.y, d)) for p in base]
    b1 = Pt(mul(e(0, F(1, 2)), d), Z)
    b2 = Pt(mul(e(0, F(1, 4)), d), mul(e(F(3, 4)), d))
    return P, b1, b2

def cellules_carre(delta):
    # cote = sqrt2/2, diametre 1 ; Q(sqrt2)
    d = e(F(delta).limit_denominator(10**7))
    s = e(0, F(1, 4))                    # sqrt2/4 = 1/(2 sqrt2)
    ns = (-s[0], -s[1])
    base = [Pt(s, s), Pt(ns, s), Pt(ns, ns), Pt(s, ns)]
    P = [Pt(mul(p.x, d), mul(p.y, d)) for p in base]
    b1 = Pt(mul(e(0, F(1, 2)), d), Z)
    b2 = Pt(Z, mul(e(0, F(1, 2)), d))
    return P, b1, b2

def cellules_rect2(delta):
    # rectangle 1 x 2 de diametre sqrt5, normalise a 1 : cotes sqrt5/5 et 2sqrt5/5 ; Q(sqrt5)
    d = e(F(delta).limit_denominator(10**7))
    a = e(0, F(1, 10))                   # demi-cote : 1/(2 sqrt5)
    b = e(0, F(1, 5))                    # demi-cote : 1/sqrt5
    na, nb = (-a[0], -a[1]), (-b[0], -b[1])
    base = [Pt(a, b), Pt(na, b), Pt(na, nb), Pt(a, nb)]
    P = [Pt(mul(p.x, d), mul(p.y, d)) for p in base]
    b1 = Pt(mul(e(0, F(1, 5)), d), Z)     # espacement 1/sqrt5
    b2 = Pt(Z, mul(e(0, F(2, 5)), d))     # espacement 2/sqrt5
    return P, b1, b2

def cell(P, b1, b2, i, j):
    sx = add(mul(e(i), b1.x), mul(e(j), b2.x))
    sy = add(mul(e(i), b1.y), mul(e(j), b2.y))
    return [Pt(add(p.x, sx), add(p.y, sy)) for p in P]

def omega_exact(P, b1, b2, R=8):
    C0 = cell(P, b1, b2, 0, 0)
    ring = [(i, j) for i in range(-R, R+1) for j in range(-R, R+1)
            if (i, j) != (0, 0) and conflict(C0, cell(P, b1, b2, i, j))]
    S = set(ring)
    adj = [set() for _ in ring]
    for a, o in enumerate(ring):
        for b, o2 in enumerate(ring):
            if a != b and (o2[0]-o[0], o2[1]-o[1]) in S:
                adj[a].add(b)
    best = [0]
    def bk(cand, k):
        if k + len(cand) <= best[0]: return
        if not cand:
            best[0] = max(best[0], k); return
        for v in sorted(cand):
            bk(cand & adj[v], k+1)
            cand = cand - {v}
    for v in range(len(ring)):
        bk(set(adj[v]), 1)
    return best[0] + 1, len(ring)

if __name__ == "__main__":
    PLANS = [("hexagonal (60 deg)", 3, cellules_hexa, ["3/10", "1/2", "7/10", "9/10", "999/1000"]),
             ("carre (90 deg)", 2, cellules_carre, ["3/10", "1/2", "7/10", "9/10", "999/1000"]),
             ("rectangle 2:1 (90 deg)", 5, cellules_rect2, ["4/10", "1/2", "7/10", "49/50", "999/1000"])]
    out = {}
    for nom, champ, fabrique, deltas in PLANS:
        D = champ
        for ds in deltas:
            t0 = time.time()
            P, b1, b2 = fabrique(F(ds))
            w, nr = omega_exact(P, b1, b2)
            out[(nom, ds)] = w
            print(f"{nom:24s} delta={float(F(ds)):.3f} : omega = {w}  (exact, anneau {nr}, {time.time()-t0:.0f}s)", flush=True)
    import json
    json.dump({f"{k[0]}|{k[1]}": v for k, v in out.items()}, open("exact_tangence.json", "w"), ensure_ascii=False, indent=1)
