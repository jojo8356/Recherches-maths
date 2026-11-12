"""AUDIT S-V — le moteur EXACT, en coordonnées de module (g, h).

Pourquoi ce changement de paramétrage
-------------------------------------
L'ancien certificat T7 travaillait en (rho, theta) : la géométrie y fait intervenir
cos theta et sin theta, donc des irrationnels, donc de l'arithmétique d'intervalles
trigonométrique (Machin, Taylor+Lagrange). C'est cette couche qui a produit l'intervalle
retourné et la rétractation.

Le réseau b1 = (1,0), b2 = (g, h) est décrit par DEUX RATIONNELS. Tout est alors rationnel :
  - vecteurs du réseau  v_ij = (i + j g, j h)                       (rationnel)
  - contrainte de Voronoï  2<p, v> <= |v|^2                          (rationnel)
  - sommets de la cellule = intersection de deux contraintes        (rationnel)
  - distances^2 entre sommets                                       (rationnel)
Aucune fonction transcendante n'apparaît. Le domaine des modules est l'ensemble
{|g| <= 1/2, g^2 + h^2 >= 1, h > 0} — le domaine fondamental de SL(2,Z) agissant sur H,
et non plus le rectangle [1,2] x [60,120] de T7 (qui ratait tous les réseaux anisotropes).

Ce fichier ne certifie rien : il CALCULE omega exactement, et il se vérifie lui-même
(voir `controle_fenetre`). Le certificat est l'affaire du fichier suivant.
"""
import math
from fractions import Fraction as F

import numpy as np


# --------------------------------------------------------------- géométrie exacte
def vecteur(i, j, g, h):
    return (F(i) + j * g, j * h)


def norme2(v):
    return v[0] * v[0] + v[1] * v[1]


def cellule(g, h, fenetre2=None):
    """Cellule de Voronoï de 0, en rationnel exact, avec auto-vérification de la fenêtre.

    On découpe un grand carré par les demi-plans 2<p,v> <= |v|^2 pour tous les v du réseau
    tels que |v|^2 <= W. Les contraintes omises (|v|^2 > W) sont PROUVÉES redondantes :
    si le polygone obtenu est dans la boule de rayon sqrt(W)/2, alors pour |p| <= sqrt(W)/2
    et |v|^2 >= W on a 2<p,v> <= 2|p||v| <= sqrt(W)|v| <= |v|^2.
    Renvoie (sommets, W, rayon2_max) ou None.
    """
    if fenetre2 is None:
        fenetre2 = 4 * max(F(1), norme2((g, h)))
    W = F(fenetre2)
    R = math.sqrt(float(W)) / 2 + 1.0
    poly = [(-F(R), -F(R)), (F(R), -F(R)), (F(R), F(R)), (-F(R), F(R))]
    i_max = int(math.isqrt(int(W))) + 4
    for i in range(-i_max, i_max + 1):
        for j in range(-i_max, i_max + 1):
            if i == 0 and j == 0:
                continue
            v = vecteur(i, j, g, h)
            n2 = norme2(v)
            if n2 > W:
                continue
            c = n2 / 2                                   # 2<p,v> <= n2  <=>  <p,v> <= n2/2
            out = []
            m = len(poly)
            for k in range(m):
                a, b = poly[k], poly[(k + 1) % m]
                da = a[0] * v[0] + a[1] * v[1] - c
                db = b[0] * v[0] + b[1] * v[1] - c
                if da <= 0:
                    out.append(a)
                if (da < 0 < db) or (db < 0 < da):
                    t = da / (da - db)
                    out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
            poly = out
            if len(poly) < 3:
                return None
    ded = []
    for p in poly:
        if not ded or (p[0] - ded[-1][0]) ** 2 + (p[1] - ded[-1][1]) ** 2 > F(1, 10 ** 24):
            ded.append(p)
    if len(ded) > 2 and (ded[0][0] - ded[-1][0]) ** 2 + (ded[0][1] - ded[-1][1]) ** 2 < F(1, 10 ** 24):
        ded.pop()
    rayon2 = max(norme2(p) for p in ded)
    # auto-vérification : le rayon doit rester sous sqrt(W)/2, sinon la fenêtre ne prouve rien
    if 4 * rayon2 > W:
        return None
    return ded, W, rayon2


def controle_fenetre(g, h):
    """Contrôle négatif structurel : doubler la fenêtre ne doit RIEN changer.

    Si la cellule changeait en doublant W, c'est que la fenêtre précédente omettait une
    contrainte active : la cellule calculée n'était pas la bonne.
    """
    a = cellule(g, h)
    if a is None:
        return False, "fenêtre 1 non certifiée"
    W2 = a[1] * 4
    b = cellule(g, h, W2)
    if b is None:
        return False, "fenêtre 2 non certifiée"
    A = sorted((str(p[0]), str(p[1])) for p in a[0])
    B = sorted((str(p[0]), str(p[1])) for p in b[0])
    return (A == B), ("identique" if A == B else f"différent : {len(A)} vs {len(B)} sommets")


def dist2(p, q):
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def _dist2_pt_seg2(x, a, b):
    """Distance^2 exacte d'un point à un segment (rationnel)."""
    abx, aby = b[0] - a[0], b[1] - a[1]
    L = abx * abx + aby * aby
    if L == 0:
        return dist2(x, a)
    t = ((x[0] - a[0]) * abx + (x[1] - a[1]) * aby) / L
    if t < 0:
        t = F(0)
    elif t > 1:
        t = F(1)
    pr = (a[0] + t * abx, a[1] + t * aby)
    return dist2(x, pr)


def dmin2_dmax2(P, Q):
    """(dmin^2, dmax^2) exactes entre deux polygones convexes."""
    dmin2 = min(min(_dist2_pt_seg2(p, Q[k], Q[(k + 1) % len(Q)]) for k in range(len(Q))) for p in P)
    dmin2 = min(dmin2, min(min(_dist2_pt_seg2(q, P[k], P[(k + 1) % len(P)]) for k in range(len(P)))
                           for q in Q))
    dmax2 = max(dist2(p, q) for p in P for q in Q)
    return dmin2, dmax2


# --------------------------------------------------------------- omega exact
def graphe_exact(g, h, ech):
    """Graphe de conflit exact. ech = diamètre voulu des cellules (Fraction < 1).

    Conflit <=> dmin <= T <= dmax avec T = diam/ech, donc en élevant au carré :
      ech^2 * dmin^2 <= diam^2   et   diam^2 <= ech^2 * dmax^2.
    Tout est rationnel : aucune tolérance, aucun epsilon.
    """
    info = cellule(g, h)
    if info is None:
        return None
    P, W, _ = info
    diam2 = max(dist2(p, q) for p in P for q in P)
    ech2 = ech * ech
    # Fenêtre d'indices. Tout est en unités RÉSEAU (non normalisées) :
    #   seuil T = diam/ech ; condition nécessaire au conflit : |c| <= T + diam = diam*(1/ech + 1).
    # (Première version fausse : fenêtre en unités normalisées, d'où omega = 1 pour h = 20.)
    cible2 = (diam2 ** 0.5 * (float(1 / ech) + 1.0)) ** 2 if False else None
    _T = None
    cible2 = diam2 * (1 / ech + 1) ** 2
    n_max = int(math.isqrt(int(cible2 / max(norme2((g, h)), F(1, 1000))))) + 6
    offs, adj = [], []
    cand = [(0, 0)]
    for i in range(-n_max, n_max + 1):
        for j in range(-n_max, n_max + 1):
            if (i, j) == (0, 0):
                continue
            c = vecteur(i, j, g, h)
            if norme2(c) <= cible2:
                cand.append((i, j))
    idx = {o: t for t, o in enumerate(cand)}
    n = len(cand)
    adj = [set() for _ in range(n)]
    for a in range(n):
        for b in range(a + 1, n):
            ca = vecteur(*cand[a], g, h)
            cb = vecteur(*cand[b], g, h)
            d = (cb[0] - ca[0], cb[1] - ca[1])
            if norme2(d) > cible2:
                continue
            Q = [(x + d[0], y + d[1]) for (x, y) in P]
            lo2, hi2 = dmin2_dmax2(P, Q)
            if ech2 * lo2 <= diam2 <= ech2 * hi2:
                adj[a].add(b)
                adj[b].add(a)
    return {"sommets": P, "diam2": diam2, "adj": adj, "idx": idx, "cand": cand}


def clique_max_avec0(adj):
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

    bk(set(), adj[0] | {0}, set())
    return best[0], best[1]


def omega_exact(g, h, ech=F(99, 100)):
    Gr = graphe_exact(g, h, ech)
    if Gr is None:
        return None
    k, S = clique_max_avec0(Gr["adj"])
    inv = {t: o for o, t in Gr["idx"].items()}
    return {"omega": k, "nv": len(Gr["sommets"]),
            "temoins": sorted(inv[i] for i in S) if S else None,
            "deg0": len(Gr["adj"][0]), "n": len(Gr["cand"])}


def main():
    ech = F(99, 100)
    print("=== contrôles de la fenêtre (contrôle négatif structurel) ===")
    for (g, h) in [(F(0), F(1)), (F(1, 2), F(9, 10)), (F(0), F(3)), (F(-1, 3), F(7, 5)),
                   (F(1, 2), F(1)), (F(0), F(20))]:
        ok, msg = controle_fenetre(g, h)
        print(f"  g={g} h={h}: {ok} ({msg})")

    print("\n=== omega exact sur quelques points rationnels connus ===")
    for (g, h, nom) in [(F(0), F(1), "carré (τ=i)"),
                        (F(1, 2), F(9, 10), "proche A2"),
                        (F(0), F(20), "très anisotrope"),
                        (F(-1, 2), F(9, 10), "proche A2 (réflexion)")]:
        r = omega_exact(g, h, ech)
        print(f"  {nom:38s} g={g:>5} h={h:>4} -> omega={r['omega']}, {r['nv']} sommets, "
              f"degré(0)={r['deg0']}, {r['n']} candidats")
        print(f"      témoins {r['temoins']}")

    # A2 exact : tau = exp(i*pi/3) n'est pas rationnel ; on vise le point rationnel
    # le plus proche et on note l'écart. Le minimum exact de omega est attendu à A2.
    print("\n=== le minimum 7 est-il atteint ? (quadrillage rationnel du domaine) ===")
    best = (99, None)
    for hnum in range(10, 41):           # h = 1.0 .. 4.0 par pas de 0.1
        h = F(hnum, 10)
        for gnum in range(-10, 11):      # g = -0.5 .. 0.5 par pas de 0.05
            g = F(gnum, 20)
            if g * g + h * h < 1:
                continue
            r = omega_exact(g, h, ech)
            if r is None:
                continue
            if r["omega"] < best[0]:
                best = (r["omega"], (g, h, r))
    print("  minimum sur le quadrillage :", best[0], "en", best[1][0], best[1][1])
    print("  ", {k: v for k, v in best[1][2].items()})


if __name__ == "__main__":
    main()
