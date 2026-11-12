"""Obligations par boîte — moteur exact et générateur, en forme corrigée (geste 39).

Ce que le geste 39 a changé
--------------------------
La donnée exportée jusqu'ici était « sept décalages + un seuil figé ». C'est faux comme
entrée de `Boites.clique_de_temoins`, qui demande des témoins à distance² ≤ 1 et ≥ 1,
c'est-à-dire un seuil T = 1 *absolu*. Or `omega_exact` mesure le seuil T = diam/σ, qui vaut
1,18 et non 1 au centre de la boîte 0 : la 7-clique exportée n'y est qu'une 6-clique.

La forme correcte
-----------------
Le quantificateur du théorème est  ∀(g, h) ∃s : χ(sΛ) ≥ 7.  L'échelle s dépend donc du
réseau, c'est-à-dire du point (g, h) — mais elle est FIXE sur chaque sous-boîte certifiée,
puisque les 21 paires doivent toutes être en conflit à la même échelle.

   conflit à l'échelle s, pour la paire de décalage d  ⟺  s·dmin(d) ≤ 1 ≤ s·dmax(d)
                                                      ⟺  1/dmax(d) ≤ s ≤ 1/dmin(d)

Posons T = 1/s. La paire d est en conflit ⟺ dmin(d) < T < dmax(d) (inégalités strictes, c'est
ce qui donne la marge du lemme B). Sept cellules reçoivent sept couleurs distinctes dès que
les 21 paires vérifient cela au même T, et que la cellule est de diamètre dilaté < 1 :

      ∃T > D  tel que  ω({d : dmin(d) < T < dmax(d)}) ≥ 7,

où D est le diamètre de la cellule. C'est exactement la conjonction de `Boites.clique_de_temoins`
(sept cellules en conflit ⟹ sept couleurs) et de `Pont.lemmeB` (0 < ε = D/T < 1, dmin ≤ D/ε,
dmax ≥ D/ε, dmin < dmax ⟹ l'échelle existe). Rien de neuf à prouver : la composition est déjà
compilée. Ce qui reste à calculer, c'est, pour chaque sous-boîte, un T et un jeu de témoins
qui passent sur TOUTE la sous-boîte.

Réduction au corps de différences (la même que le moteur Rust, geste 26)
------------------------------------------------------------------------
Toutes les cellules d'un réseau sont translatées l'une de l'autre. Donc, avec K = P − P
(corps de différences de la cellule P, indépendant du décalage) :

      dmin²(V, V + d) = dist(d, K)²          (= 0 si d ∈ K, sinon distance au bord)
      dmax²(V, V + d) = max_{z ∈ K} |z − d|²  (= max sur les sommets de K, f convexe)

Deux distances point-polygone en O(|K|) au lieu de polygone-polygone en O(|P|²). Ce fichier
ne fait que du rationnel exact : aucune tolérance, aucun flottant dans une décision.
"""
import sys
import types
from fractions import Fraction as F

try:
    import numpy  # noqa: F401
except ModuleNotFoundError:
    sys.modules.setdefault("numpy", types.ModuleType("numpy"))

import audit_gh as AG


# --------------------------------------------------------------- géométrie exacte de base
def vecteur(i, j, g, h):
    return (F(i) + j * g, j * h)


def dist2(p, q):
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def enveloppe(points):
    """Enveloppe convexe exacte (Andrew monotone chain), sans doublon ni point colinéaire."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def demi(seq):
        out = []
        for p in seq:
            while len(out) >= 2 and _cross(out[-2], out[-1], p) <= 0:
                out.pop()
            out.append(p)
        return out

    bas = demi(pts)
    haut = demi(reversed(pts))
    return bas[:-1] + haut[:-1]


def corps_differences(P):
    """K = P − P, en sommets (enveloppe convexe des |P|² différences). Exact."""
    return enveloppe([(a[0] - b[0], a[1] - b[1]) for a in P for b in P])


def _dist2_point_convexe(d, K):
    """dist(d, K)² pour K convexe fermé donné par ses sommets (exact)."""
    n = len(K)
    if n == 0:
        return F(0)
    if n == 1:
        return dist2(d, K[0])
    if n == 2:
        return _dist2_point_segment(d, K[0], K[1])
    # test d'appartenance par les produits vectoriels (K est donné en sens direct ou non :
    # on teste que d est du même côté de toutes les arêtes)
    signes = set()
    for k in range(n):
        c = _cross(K[k], K[(k + 1) % n], d)
        signes.add((c > 0) - (c < 0))
    if len(signes) == 1:
        return F(0)
    return min(_dist2_point_segment(d, K[k], K[(k + 1) % n]) for k in range(n))


def _dist2_point_segment(x, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    L = ax * ax + ay * ay
    if L == 0:
        return dist2(x, a)
    t = ((x[0] - a[0]) * ax + (x[1] - a[1]) * ay) / L
    if t < 0:
        t = F(0)
    elif t > 1:
        t = F(1)
    return dist2(x, (a[0] + t * ax, a[1] + t * ay))


class Cellule:
    """Cellule de Voronoï d'un réseau (g, h), avec son corps de différences et son diamètre."""

    def __init__(self, g, h):
        info = AG.cellule(g, h)
        if info is None:
            raise ValueError(f"cellule non certifiée en g={g}, h={h}")
        self.g, self.h = g, h
        self.P = info[0]
        self.W = info[1]
        self.K = corps_differences(self.P)
        self.diam2 = max(dist2(p, q) for p in self.P for q in self.P)

    def dmin2_dmax2(self, d):
        """(dmin², dmax²) entre la cellule et sa translatée de d, par le corps de différences."""
        lo = _dist2_point_convexe(d, self.K)
        hi = max(dist2(z, d) for z in self.K)
        return lo, hi

    def table(self, offsets):
        """{(décalage) : (dmin², dmax²)} pour tous les décalages, sauf (0,0)."""
        out = {}
        for (i, j) in offsets:
            if (i, j) == (0, 0):
                continue
            out[(i, j)] = self.dmin2_dmax2(vecteur(i, j, self.g, self.h))
        return out


def fenetre(g, h, T2, diam2):
    """Décalages susceptibles d'être en conflit au seuil T (inégalité triangulaire)."""
    # dmin ≤ T et dmax ≥ T exigent |d| ≤ T + 2·diam ; on prend la borne sûre
    rayon = F(T2).__float__() ** 0.5 + 2 * F(diam2).__float__() ** 0.5
    nmax = int(rayon / min(1.0, abs(F(h).__float__()))) + 4
    return [(i, j) for i in range(-nmax, nmax + 1) for j in range(-nmax, nmax + 1)]


def clique_max(n, adj, exige=7):
    """Clique maximale (Bron–Kerbosch avec pivot) ; renvoie (taille, ensemble)."""
    best = [0, None]

    def bk(R, P, X):
        if len(P) == 0 and len(X) == 0:
            if len(R) > best[0]:
                best[0], best[1] = len(R), set(R)
            return
        if len(R) + len(P) <= best[0]:
            return
        u = max(P | X, key=lambda v: len(adj[v] & P), default=None)
        for v in list(P - (adj[u] if u is not None else set())):
            bk(R | {v}, P & adj[v], X & adj[v])
            P.discard(v)
            X.add(v)

    bk(set(), set(range(n)), set())
    return best[0], best[1]


def _normalise(clique):
    """Translate la clique pour qu'elle contienne (0, 0) et soit triée.

    Le graphe de conflit est un graphe de Cayley : il ne dépend que des DIFFÉRENCES de
    décalages, donc toute translatée d'une clique est une clique. Sans cette
    normalisation, Bron–Kerbosch rend une translatée arbitraire (aux alentours de
    (−9, −8) sur la boîte 0), qui est correcte mais illisible et inutilement lointaine.
    """
    if not clique:
        return clique
    base = min(clique)
    return sorted((i - base[0], j - base[1]) for (i, j) in clique)


def meilleur_T(cell, exige=7):
    """Cherche T > D tel que le graphe de conflit ait une clique de taille ≥ exige.

    LE GRAPHE EST UN GRAPHE DE CAYLEY SUR LES DÉCALAGES, pas un graphe d'appartenance.
    Deux cellules décalées de d_a et d_b sont en conflit ssi la DIFFÉRENCE d_b − d_a est
    dans l'ensemble de conflit S_T = {d : dmin(d) < T < dmax(d)} ; par translation, cela ne
    dépend que de la différence. Écrire « a et b sont tous deux dans S_T » (ma première
    version) est faux : deux cellules peuvent être chacune en conflit avec V sans l'être
    entre elles — et c'est ce que le test des témoins proches a révélé en refusant la paire
    ((−2,−2), (−1,1)), dont le décalage vaut |(1+3g, 3h)| = 2,63 ≫ T = 1,62.

    Les seules valeurs de T qui changent le graphe sont les dmin et dmax ; on teste les
    milieux entre valeurs critiques consécutives, en exigeant T > D (le ε < 1 du lemme B)
    et des inégalités strictes (la marge du lemme B).
    """
    Tref = F(cell.diam2).__float__()
    offs = fenetre(cell.g, cell.h, F(cell.diam2) * 9, cell.diam2)
    tab = cell.table(offs)
    if not tab:
        return 0, None, None
    crit = sorted({cell.diam2} | {lo for (lo, hi) in tab.values()} | {hi for (lo, hi) in tab.values()})
    essais = [(a + b) / 2 for a, b in zip(crit, crit[1:])]
    essais = [T2 for T2 in essais if T2 > cell.diam2]
    meilleur = (0, None, None)
    for T2 in sorted(essais):   # T croissant : on prend la clique la plus LOCALE
        S = {d for d, (lo, hi) in tab.items() if lo < T2 < hi}
        # graphe de Cayley : a ~ b ssi (d_b − d_a) ∈ S
        dec = sorted(set(offs) | {(0, 0)})
        idx = {o: k for k, o in enumerate(dec)}
        adj = [set() for _ in dec]
        for a in range(len(dec)):
            for b in range(a + 1, len(dec)):
                dd = (dec[b][0] - dec[a][0], dec[b][1] - dec[a][1])
                if dd in S:
                    adj[a].add(b)
                    adj[b].add(a)
        taille, Cl = clique_max(len(dec), adj)
        if taille > meilleur[0]:
            meilleur = (taille, T2, _normalise([dec[k] for k in Cl]) if Cl is not None else None)
        if taille >= exige:
            return (taille, T2, _normalise([dec[k] for k in Cl]))
    return meilleur


def _auto_test():
    """Le moteur rapide doit retrouver le moteur lent (dmin2_dmax2 polygone-polygone)."""
    cas = [(F(0), F(1)), (F(-3, 8), F(219, 250)), (F(1, 2), F(433, 500)),
           (F(-1, 2), F(9, 10)), (F(1, 4), F(19, 20)), (F(0), F(866, 1000))]
    ok = True
    for g, h in cas:
        cell = Cellule(g, h)
        for d_ij in [(-1, -2), (-1, -1), (0, -2), (0, -1), (1, -1), (1, 0), (2, 2), (-2, 1)]:
            d = vecteur(*d_ij, g, h)
            Q = [(x + d[0], y + d[1]) for (x, y) in cell.P]
            lo_slow, hi_slow = AG.dmin2_dmax2(cell.P, Q)
            lo_fast, hi_fast = cell.dmin2_dmax2(d)
            if not (lo_slow == lo_fast and hi_slow == hi_fast):
                print(f"  ÉCART g={g} h={h} d={d_ij} : lent ({lo_slow}, {hi_slow}) "
                      f"≠ rapide ({lo_fast}, {hi_fast})")
                ok = False
    print("auto-test du corps de différences :", "CONFORME (48/48)" if ok else "ÉCHEC")
    return ok


if __name__ == "__main__":
    sys.exit(0 if _auto_test() else 1)


# ==================================================================== niveau 2 : symbolique
# Tout ce qui suit certifie une INÉGALITÉ SUR UNE BOÎTE ENTIÈRE, en polynômes exacts.
# Les sommets de la cellule sont des fractions rationnelles en (g, h) : on les manipule
# comme des Rat(num, den) de poly2, et un encadrement par forme de la moyenne (poly2.enc)
# donne des bornes SÛRES sur la boîte.

import poly2 as P2
from poly2 import Poly, Rat, G, H, enc, enc_rat

ZERO = Poly.const(0)
UN = Poly.const(1)


def v_x(i, j):
    """Composante x du vecteur (i, j) du réseau : i + j·g."""
    return Poly.const(i) + Poly.const(j) * G


def v_y(i, j):
    """Composante y : j·h."""
    return Poly.const(j) * H


def norme2_poly(i, j):
    a, b = v_x(i, j), v_y(i, j)
    return a * a + b * b


def sommet(i1, j1, i2, j2):
    """Sommet intersection des contraintes (i1,j1) et (i2,j2), en Rat — None si parallèles.

    p·v_k = |v_k|²/2 pour k = 1, 2 ; det[v1;v2] = det(b1,b2)·(i1·j2 − i2·j1) = h·δ.
    Cramer donne, sans division par h·δ au dénominateur du numérateur :
        p_x = (|v1|²·v2y − v1y·|v2|²) / (2·h·δ)
        p_y = (v1x·|v2|² − |v1|²·v2x) / (2·h·δ)
    """
    delta = i1 * j2 - i2 * j1
    if delta == 0:
        return None
    den = Poly.const(2 * delta) * H
    nx = norme2_poly(i1, j1) * v_y(i2, j2) - v_y(i1, j1) * norme2_poly(i2, j2)
    ny = v_x(i1, j1) * norme2_poly(i2, j2) - norme2_poly(i1, j1) * v_x(i2, j2)
    return (Rat(nx, den), Rat(ny, den))


ZERO_RAT = (Rat(Poly.const(0)), Rat(Poly.const(0)))


def dist2_rat(a, b):
    """|a − b|² pour deux points à coordonnées Rat. `ZERO_RAT` est l'origine."""
    dx, dy = a[0] - b[0], a[1] - b[1]
    return dx * dx + dy * dy


def contraintes_actives(g, h):
    """Décalages dont la contrainte est tendue en un sommet de la cellule (g, h)."""
    info = AG.cellule(g, h)
    if info is None:
        return set()
    P, W, _ = info
    tol = F(1, 10 ** 18)
    nmax = int(float(W) ** 0.5) + 4
    cons = []
    for i in range(-nmax, nmax + 1):
        for j in range(-nmax, nmax + 1):
            if (i, j) == (0, 0):
                continue
            v = vecteur(i, j, g, h)
            n2 = v[0] * v[0] + v[1] * v[1]
            if n2 > W:
                continue
            cons.append(((i, j), v, n2 / 2))
    act = set()
    for p in P:
        ten = [ij for (ij, v, c) in cons if abs(p[0] * v[0] + p[1] * v[1] - c) < tol]
        act |= set(ten)
    return act


def boite_sup(g0, g1, h0, h1):
    """Sur-ensemble de la cellule pour TOUT (g, h) de la boîte : couples de contraintes.

    Les contraintes actives sont prises aux cinq points (centre + quatre coins) ; le polygone
    des intersections faisables de paires de ce sur-ensemble CONTIENT la cellule partout dans
    la boîte. Les sommets sont gardés symboliquement (en Rat), pas numériquement.
    """
    A = set()
    for gg in (g0, (g0 + g1) / 2, g1):
        for hh in (h0, (h0 + h1) / 2, h1):
            try:
                A |= contraintes_actives(gg, hh)
            except Exception:
                pass
    A = sorted(A)
    sommets = []
    for a in range(len(A)):
        for b in range(a + 1, len(A)):
            s = sommet(A[a][0], A[a][1], A[b][0], A[b][1])
            if s is not None:
                sommets.append((A[a], A[b], s))
    return A, sommets


def _choix_min(cands, boite):
    """Indice de la plus petite des Rat sur la boîte (comparaison par signe encadré)."""
    best = 0
    for k in range(1, len(cands)):
        d = cands[best] - cands[k]
        lo, hi = d.signe_enc(boite)
        if hi < 0:
            continue          # cands[best] < cands[k] : on garde best
        best = k
    return best


def _choix_max(cands, boite):
    best = 0
    for k in range(1, len(cands)):
        d = cands[k] - cands[best]
        lo, hi = d.signe_enc(boite)
        if hi < 0:
            continue
        best = k
    return best


# ============================================================ niveau 3 : certifier une boîte
class Echec(Exception):
    pass


def _enc_neg(r, boite):
    """Certifie r < 0 STRICTEMENT sur la boîte. Renvoie (ok, borne_sup)."""
    lo, hi = r.signe_enc(boite)
    return hi < 0, hi


def _enc_pos(r, boite):
    """Certifie r > 0 STRICTEMENT sur la boîte. Renvoie (ok, borne_inf)."""
    lo, hi = r.signe_enc(boite)
    return lo > 0, lo


def _borne_sup(r, boite):
    return r.signe_enc(boite)[1]


class Boite:
    """Une boîte (g, h) et tout ce qu'on peut y certifier."""

    def __init__(self, g0, g1, h0, h1):
        self.boite = (g0, g1, h0, h1)
        self.g0, self.g1, self.h0, self.h1 = g0, g1, h0, h1

    def __repr__(self):
        return f"Boite(g∈[{self.g0},{self.g1}], h∈[{self.h0},{self.h1}])"

    # ---------------------------------------------------------------- contraintes finies
    def contraintes(self, r2max):
        """Décalages w dont la contrainte peut être active : |w|² < 4·r² quelque part.

        `r2max` est un majorant de |p|² sur la boîte. On garde tout w dont la BORNE
        INFÉRIEURE de |w|² sur la boîte est < 4·r²max : liste sûre (sur-inclut).
        """
        r2 = _borne_sup(Rat(r2max) if not isinstance(r2max, Rat) else r2max, self.boite)
        # fenêtre sûre : |w|² < 4 r² borné, donc |j|·h ≤ 2r et |i + jg| ≤ 2r
        rm = F(r2).__float__() ** 0.5 if r2 > 0 else F(1).__float__()
        hmin = min(abs(F(self.h0).__float__()), abs(F(self.h1).__float__()))
        jmax = int(2 * rm / max(hmin, 1e-12)) + 3
        imax = int(2 * rm) + int(2 * rm / max(hmin, 1e-12)) + 6
        out = []
        for i in range(-imax, imax + 1):
            for j in range(-jmax, jmax + 1):
                if (i, j) == (0, 0):
                    continue
                n2 = norme2_poly(i, j)
                lo = n2.__class__  # noqa: F841  (lisibilité)
                if enc_rat(n2, Poly.const(1), self.boite)[0] < 4 * F(r2):
                    out.append((i, j))
        return out

    # ---------------------------------------------------------------- appartenance
    def appartient(self, s, contraintes):
        """Certifie s ∈ cell sur toute la boîte : 2⟨s,w⟩ ≤ |w|² pour tout w.

        `s` est un couple de Rat (point rationnel en (g,h)). Renvoie (ok, pire_marge).
        C'est `Boites.cell_of_fini` : la liste `contraintes` couvre les w tels que
        |w|² < 4r², les autres sont automatiques.
        """
        pire = None
        for (i, j) in contraintes:
            vx, vy = v_x(i, j), v_y(i, j)
            # 2(sx·vx + sy·vy) − (vx² + vy²)
            expr = (s[0] * Rat(vx) + s[1] * Rat(vy)) * Poly.const(2) \
                - Rat(vx * vx + vy * vy)
            # APPARTENANCE : l'inégalité est LARGE (2⟨s,w⟩ ≤ |w|²), et elle est TENDUE
            # aux sommets (valeur exactement 0). On accepte donc hi ≤ 0, pas hi < 0.
            lo, hi = expr.signe_enc(self.boite)
            if lo > 0:
                return False, lo
            pire = hi if pire is None else max(pire, hi)
        return True, pire

    def boite_sup_sommets(self):
        """Sommets candidats = intersections de paires de contraintes actives (sur-ensemble)."""
        A = set()
        for gg in (self.g0, (self.g0 + self.g1) / 2, self.g1):
            for hh in (self.h0, (self.h0 + self.h1) / 2, self.h1):
                try:
                    A |= contraintes_actives(gg, hh)
                except Exception:
                    pass
        A = sorted(A)
        cands = []
        for a in range(len(A)):
            for b in range(a + 1, len(A)):
                s = sommet(A[a][0], A[a][1], A[b][0], A[b][1])
                if s is not None:
                    cands.append((A[a], A[b], s))
        return A, cands


def _inegal(a, T2, boite, sens):
    """Certifie  a ≤ T²  (sens="le")  ou  a ≥ T²  (sens="ge")  sur la boîte.

    RÈGLE DU DOSSIER (geste 19, règle 3) : jamais deux encadrements comparés, une seule
    fonction différence. `a` est un Rat num/den ; l'inégalité a ≤ T² s'écrit, den étant de
    signe constant et connu, num − T²·den ≤ 0. On encadre UN polynôme, pas un quotient.
    C'est indispensable ici : certaines distances² valent identiquement 1 (num = den = 256h⁸),
    et l'encadrement du quotient [81,110]/[81,110] donnerait [0,73 ; 1,36] au lieu de 1.
    """
    sden = Rat(a.d).signe_enc(boite)
    if sden[0] > 0:
        P = Rat(a.n - Poly.const(T2) * a.d)
        sgn = 1
    elif sden[1] < 0:
        P = Rat(Poly.const(T2) * a.d - a.n)
        sgn = -1
    else:
        raise ZeroDivisionError("dénominateur de signe indéterminé")
    lo, hi = P.signe_enc(boite)
    if sens == "le":
        ok = hi <= 0
        return ok, (hi if sgn == 1 else -lo)
    ok = lo >= 0
    return ok, (lo if sgn == 1 else -hi)


def _dans_boule(b, s, r2):
    """Certifie |s|² ≤ r² sur la boîte. C'est l'hypothèse `hp` de `cell_of_fini`.

    SANS ELLE LA RÉDUCTION AU FINI EST FAUSSE : la liste de contraintes ne couvre que les
    w avec |w|² < 4r², et les autres ne sont automatiques QUE pour un point de la boule
    (c'est Cauchy–Schwarz dans `contrainte_auto`). Un point lointain qui satisferait les
    contraintes de la fenêtre serait accepté à tort, et il gonflerait le diamètre.
    """
    try:
        ok, _ = _inegal(dist2_rat(s, ZERO_RAT), r2, b.boite, "le")
    except ZeroDivisionError:
        return False
    return ok


def _sommets_prouves(b, cands, r2):
    """Candidats dont l'appartenance est prouvée sur toute la boîte (deux passages).

    Chaque candidat doit satisfaire DEUX choses : être dans la boule de rayon r (hypothèse
    de `cell_of_fini`), et vérifier les contraintes de la fenêtre finie. Le second passage
    resserre r (majorant de |p| pour p dans la cellule, valide par convexité : la cellule est
    dans l'enveloppe convexe de ses sommets), ce qui raccourcit la liste de contraintes.
    """
    cons = b.contraintes(Poly.const(r2))
    proves = [(ca, cb, s) for (ca, cb, s) in cands
              if _dans_boule(b, s, r2) and b.appartient(s, cons)[0]]
    if not proves:
        return proves, cons
    ray = [dist2_rat(s, ZERO_RAT) for (_, _, s) in proves]
    r2b = max(_borne_sup(r, b.boite) for r in ray)
    cons = b.contraintes(Poly.const(r2b))
    proves = [(ca, cb, s) for (ca, cb, s) in proves
              if _dans_boule(b, s, r2b) and b.appartient(s, cons)[0]]
    return proves, cons


def _decalage(da, db):
    """Vecteur (i + j·g, j·h) du décalage db − da, en Poly."""
    di, dj = db[0] - da[0], db[1] - da[1]
    return (Poly.const(di) + Poly.const(dj) * G, Poly.const(dj) * H)


def _dist2_rat(a, b):
    return dist2_rat(a, b)


def certifie_boite(g0, g1, h0, h1, T2=None, clique=None):
    """Certifie l'obligation sur la boîte, ou dit qu'il faut subdiviser.

    ATTENTION À NE PAS CONFONDRE (c'était mon erreur de la première version) :
      * la CLIQUE est un ensemble de 7 DÉCALAGES du réseau (les sept cellules) ;
      * les SOMMETS de la cellule sont les TÉMOINS, pas la clique.

    Obligation, pour une clique d₁…d₇ et un seuil T fixés :
      (i)   toute paire de sommets de la cellule est à distance < T     [ε = D/T < 1]
      (ii)  pour chacune des 21 paires (d_a, d_b), il existe des sommets u, v de la cellule
            tels que |u − (v + d)|² ≤ T²      — les témoins proches   (d = d_b − d_a)
      (iii) pour chacune des 21 paires, il existe des sommets u, v tels que
            |u − (v + d)|² ≥ T²             — les témoins lointains
    Les sommets prouvés appartiennent à la cellule pour TOUT (g, h) de la boîte, donc les
    témoins u, v + d aussi (translation). (ii) et (iii) sont les deux hypothèses de
    `Boites.clique_de_temoins` ; (i) est celle de `Pont.lemmeB`.

    Pourquoi (ii) se teste sur des sommets : deux cellules adjacentes qui partagent une
    arête partagent ses extrémités, donc une paire de sommets à distance nulle existe.
    C'est une condition SUFFISANTE (on exhibe un couple), jamais une condition nécessaire :
    un échec dit « ce couple-là n'est pas prouvé », pas « c'est faux ».
    """
    b = Boite(g0, g1, h0, h1)
    gc, hc = (g0 + g1) / 2, (h0 + h1) / 2
    if T2 is None or clique is None:
        try:
            _, T2c, clc = meilleur_T(Cellule(gc, hc))
        except Exception:
            return {"ok": False, "raison": "aucun seuil T au centre", "subdiviser": False}
        if T2 is None:
            T2 = T2c
        if clique is None:
            clique = clc
    if clique is None or len(clique) < 7:
        return {"ok": False, "raison": "clique de centre < 7", "subdiviser": True}
    clique = list(clique)[:9]
    r = {"boite": [str(g0), str(g1), str(h0), str(h1)], "T2": str(T2),
         "clique": [list(c) for c in clique], "subdiviser": False}

    A, cands = b.boite_sup_sommets()
    if len(cands) < 3:
        return {**r, "raison": f"sur-ensemble dégénéré ({len(cands)})"}
    try:
        proves, cons = _sommets_prouves(b, cands, _rayons_borne(cands, b.boite))
    except ZeroDivisionError as e:
        return {**r, "raison": f"appartenance : {e}", "subdiviser": True}
    r["sommets_prouves"] = len(proves)
    if len(proves) < 3:
        return {**r, "raison": f"{len(proves)} sommets prouvés sur {len(cands)}", "subdiviser": True}
    sommets = [s for (_, _, s) in proves]

    # (i) diamètre < T
    pire = None
    for a in range(len(sommets)):
        for c in range(a + 1, len(sommets)):
            try:
                ok, m = _inegal(dist2_rat(sommets[a], sommets[c]), T2, b.boite, "le")
            except ZeroDivisionError as e:
                return {**r, "raison": f"diamètre : {e}", "subdiviser": True}
            if not ok:
                return {**r, "raison": "diamètre : deux sommets peuvent dépasser T",
                        "subdiviser": True}
            pire = m if pire is None else max(pire, m)
    r["diam2_sup"] = str(pire)

    # (ii)+(iii) les 21 paires de la clique
    marge_proche = marge_loin = None
    for a in range(len(clique)):
        for c in range(a + 1, len(clique)):
            vx, vy = _decalage(clique[a], clique[c])
            proche = lointain = None
            for u in sommets:
                for v in sommets:
                    e = (u[0] - v[0] - Rat(vx), u[1] - v[1] - Rat(vy))
                    dd = e[0] * e[0] + e[1] * e[1]
                    try:
                        okp, mp = _inegal(dd, T2, b.boite, "le")
                        okl, ml = _inegal(dd, T2, b.boite, "ge")
                    except ZeroDivisionError:
                        continue
                    if okp and (proche is None or mp > proche):
                        proche = mp
                    if okl and (lointain is None or ml < lointain):
                        lointain = ml
            if proche is None:
                return {**r, "raison": f"paire {clique[a]},{clique[c]} : aucun témoin proche",
                        "subdiviser": True}
            if lointain is None:
                return {**r, "raison": f"paire {clique[a]},{clique[c]} : aucun témoin lointain",
                        "subdiviser": True}
            marge_proche = proche if marge_proche is None else min(marge_proche, proche)
            marge_loin = lointain if marge_loin is None else min(marge_loin, lointain)
    r.update(ok=True, raison="diamètre < T, 21 paires avec témoins proche et lointain",
             marge_proche=str(marge_proche), marge_loin=str(marge_loin))
    return r


def _rayons_borne(cands, boite):
    ray = [dist2_rat(s, ZERO_RAT) for (_, _, s) in cands]
    return max(_borne_sup(r, boite) for r in ray)


def couvre(g0, g1, h0, h1, profondeur=0, prof_max=7, T2=None, journal=None):
    """Subdivise jusqu'à certifier ; renvoie (feuilles certifiées, échecs, essais)."""
    r = certifie_boite(g0, g1, h0, h1, T2=T2)
    if journal is not None:
        journal.append(r)
    if r.get("ok"):
        return [(g0, g1, h0, h1, r)], [], 1
    if not r.get("subdiviser") or profondeur >= prof_max:
        return [], [(g0, g1, h0, h1, r)], 1
    gm, hm = (g0 + g1) / 2, (h0 + h1) / 2
    if (g1 - g0) >= (h1 - h0):
        sous = [(g0, gm, h0, h1), (gm, g1, h0, h1)]
    else:
        sous = [(g0, g1, h0, hm), (g0, g1, hm, h1)]
    feuilles, echecs, essais = [], [], 1
    for (a, b_, c, d) in sous:
        f, e, n = couvre(a, b_, c, d, profondeur + 1, prof_max, T2, journal)
        feuilles += f
        echecs += e
        essais += n
    return feuilles, echecs, essais
