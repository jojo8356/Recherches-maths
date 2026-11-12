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
            # APPARTENANCE : il faut que l'inégalité 2⟨s,w⟩ ≤ |w|² soit vraie pour TOUT
            # (g, h) de la boîte, donc que le MAJORANT de l'expression soit ≤ 0. Elle est
            # large et tendue aux sommets (valeur exactement 0), d'où hi ≤ 0 et non hi < 0.
            #
            # C'ÉTAIT LE DÉFAUT DE SÛRETÉ LE PLUS GRAVE DU MOTEUR : la version d'avant
            # testait `lo > 0`, c'est-à-dire « l'inégalité est-elle PROUVÉE FAUSSE quelque
            # part ». Elle n'écartait donc que les points dont la violation était certaine,
            # et acceptait tous les autres — y compris des points franchement hors de la
            # cellule, comme (−0,625 ; 0,848) sur g ∈ [−1/4,0], h ∈ [17/10, 37/20], où la
            # contrainte w = (−1,0) exige pourtant p_x ≥ −1/2. Ces faux sommets entraient
            # ensuite comme témoins, et le certificat « prouvait » des choses fausses : la
            # vérification indépendante par `audit_gh.dmin2_dmax2` (moteur polygone-polygone
            # lent, écrit bien avant) a trouvé 202 anomalies sur 738 paires.
            lo, hi = expr.signe_enc(self.boite)
            if hi > 0:
                return False, hi
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

    ATTENTION AUX UNITÉS : le nombre rendu est une borne de num − T²·den (à un signe près),
    PAS une valeur de a. Il sert à décider, jamais à construire un seuil — voir
    `_choisit_T`, où cette confusion a produit des seuils à 67 000.

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


def _filtre_numerique(b, ca, cb, s):
    """Ce candidat est-il dans la cellule aux neuf points d'échantillonnage de la boîte ?

    Aucune valeur de preuve : c'est un filtre de coût. Les contraintes testées sont les
    DEUX qui définissent le sommet, ce qui suffit à écarter les intersections lointaines.
    """
    for gg in (b.g0, (b.g0 + b.g1) / 2, b.g1):
        for hh in (b.h0, (b.h0 + b.h1) / 2, b.h1):
            for (i, j) in (ca, cb):
                try:
                    px = s[0].n.eval(gg, hh) / s[0].d.eval(gg, hh)
                    py = s[1].n.eval(gg, hh) / s[1].d.eval(gg, hh)
                except ZeroDivisionError:
                    return False
                vx = i + j * gg
                vy = j * hh
                if 2 * (px * vx + py * vy) > vx * vx + vy * vy + F(1, 10 ** 9) * max(1, vx * vx + vy * vy):
                    return False
    return True


def _sommets_prouves(b, cands, r2):
    """Candidats dont l'appartenance est prouvée sur toute la boîte (deux passages).

    Chaque candidat doit satisfaire DEUX choses : être dans la boule de rayon r (hypothèse
    de `cell_of_fini`), et vérifier les contraintes de la fenêtre finie. Le second passage
    resserre r (majorant de |p| pour p dans la cellule, valide par convexité : la cellule est
    dans l'enveloppe convexe de ses sommets), ce qui raccourcit la liste de contraintes.
    """
    # PRÉ-FILTRE NUMÉRIQUE, sans valeur de preuve. Les candidats sont les intersections de
    # paires de contraintes ; beaucoup sont très loin de la cellule et l'encadrement exact de
    # leur appartenance coûte cher (ce sont justement les coordonnées les plus sensibles à
    # (g, h)). On écarte d'abord ceux qui ne sont pas dans la cellule NUMÉRIQUEMENT, aux neuf
    # points d'échantillonnage. Comme le test exact qui suit est refait sur tout survivant,
    # ce filtre ne peut que faire PERDRE des sommets, jamais en accepter un de faux.
    garde = [_filtre_numerique(b, ca, cb, s) for (ca, cb, s) in cands]
    if not any(garde):
        garde = [True] * len(cands)
    cons = b.contraintes(Poly.const(r2))
    proves = [(ca, cb, s) for k, (ca, cb, s) in enumerate(cands) if garde[k]
              and _dans_boule(b, s, r2) and b.appartient(s, cons)[0]]
    if not proves:
        return proves, cons
    ray = [dist2_rat(s, ZERO_RAT) for (_, _, s) in proves]
    r2b = max(_borne_sup(r, b.boite) for r in ray)
    # Le second passage ne doit que RESSERRER. Il arrivait qu'il élargisse : si le
    # dénominateur d'une coordonnée encadre 0, le quotient explose et `_borne_sup` rend une
    # valeur énorme — sur h ∈ [2, 3] cela donnait r² ≈ 300 et 6528 contraintes au lieu de 20,
    # d'où 90 s par nœud. On garde donc le plus petit des deux rayons : les sommets sont de
    # toute façon revérifiés un par un par `_dans_boule` et `appartient`.
    r2b = min(r2, r2b)
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


class Trop_Long(Exception):
    """Budget de temps épuisé : la boîte n'est ni certifiée ni réfutée."""


def _verifie_echeance(echeance):
    import time as _t
    if echeance is not None and _t.time() > echeance:
        raise Trop_Long("budget de temps épuisé")


GARDES = 3          # couples témoins gardés par côté et par paire (voir l'élagage)


def points_temoins(sommets, gc, hc):
    """Sommets prouvés + milieux des arêtes de leur enveloppe convexe.

    POURQUOI DES MILIEUX : les témoins de `Boites.clique_de_temoins` sont deux points
    QUELCONQUES des cellules, pas deux sommets. Se limiter aux sommets perd des paires
    entières — deux cellules voisines qui partagent une arête peuvent n'avoir aucun couple
    de sommets à distance < T alors que leurs arêtes se touchent. Sur la boîte h ∈ [2, 3]
    cela se voyait : pour une des 21 paires, le meilleur couple de sommets était à
    distance² 10,6 pour un seuil de 2,2, donc aucun T n'existait.

    POURQUOI C'EST SÛR : la cellule est CONVEXE (`Queue.cell_convex`) et chaque sommet est
    prouvé dans la cellule pour tout (g, h) de la boîte. Donc tout barycentre à coefficients
    FIXÉS de sommets prouvés est dans la cellule pour tout (g, h) de la boîte : c'est une
    combinaison convexe, et les coefficients (1/2, 1/2) ne dépendent pas de (g, h). Les
    milieux sont donc des témoins admissibles, exactement comme les sommets.

    L'ordre cyclique n'est calculé qu'à un point (le centre) et n'a AUCUNE valeur de preuve :
    si l'ordre change dans la boîte, on inclut seulement d'autres milieux, qui sont tous
    dans la cellule par le même argument. Un milieu inutile ne peut rien fausser.
    """
    pts = list(sommets)
    if len(pts) > 2:
        num = [(p[0].n.eval(gc, hc) / p[0].d.eval(gc, hc),
                p[1].n.eval(gc, hc) / p[1].d.eval(gc, hc), k) for k, p in enumerate(pts)]
        cyc = enveloppe([(a, b) for (a, b, _) in num])
        pos = {(a, b): k for (a, b, k) in num}
        ordre = [pos[(a, b)] for (a, b) in cyc]
        for k in range(len(ordre)):
            i, j = pts[ordre[k]], pts[ordre[(k + 1) % len(ordre)]]
            pts.append(((i[0] + j[0]) / 2, (i[1] + j[1]) / 2))
    return pts



def _couples_temoins(b, temoins, clique, echeance=None):
    """Les distances² |u − (v + d)|² (en Rat) des couples de témoins, par paire de la clique.

    Structure rendue : {(d_a, d_b) : [(valeur au centre, u, v, Rat)]}, la même liste servant
    aux deux côtés (témoins proches et lointains) : c'est un seul jeu de polynômes, et
    `_inegal` en fait une inégalité à la fois.

    On peut ÉLAGUER sans risque : ne garder que les couples les plus petits au centre pour
    le côté « proche » et les plus grands pour le côté « lointain » ne peut que rendre la
    condition plus difficile à satisfaire — la preuve reste « il existe un couple de CET
    ensemble qui passe », revérifié exactement. Sans élagage, chaque nœud encadrait
    21 × |témoins|² distances, et la campagne dépassait le budget dès h ≳ 1.
    """
    gc, hc = (b.g0 + b.g1) / 2, (b.h0 + b.h1) / 2
    out = {}
    for a in range(len(clique)):
        for c in range(a + 1, len(clique)):
            _verifie_echeance(echeance)
            vx, vy = _decalage(clique[a], clique[c])
            lst = []
            for u in temoins:
                for v in temoins:
                    e = (u[0] - v[0] - Rat(vx), u[1] - v[1] - Rat(vy))
                    dd = e[0] * e[0] + e[1] * e[1]
                    try:
                        if dd.d.eval(gc, hc) <= 0:
                            continue
                        val = dd.n.eval(gc, hc) / dd.d.eval(gc, hc)
                    except ZeroDivisionError:
                        continue
                    lst.append((val, u, v, dd))
            if not lst:
                return None
            lst.sort(key=lambda z: z[0])
            # union des deux extrémités triées, chaque élément étiqueté par son côté
            choisis = [(True, z) for z in lst[:GARDES]] + [(False, z) for z in lst[-GARDES:]]
            out[(a, c)] = (choisis, lst)
    return out


def _bornes_paire(b, choisis):
    """Les quatre bornes utiles des d² des témoins d'une paire, sur la boîte entière.

    Renvoie (min_w lo_w, max_w hi_w, min_w hi_w, max_w lo_w).

    Les deux premières servent à DIAGNOSTIQUER et à la vérification finale (« existe-t-il
    un témoin dont le minorant dépasse T² ? ») ; les deux dernières servent à CONSTRUIRE
    le seuil, parce que les conditions du théorème portent sur le pire cas de chaque côté
    (voir `_choisit_T`).
    """
    los, his = [], []
    for (_, (val, u, v, dd)) in choisis:
        try:
            lo, hi = dd.enc(b.boite)
        except ZeroDivisionError:
            continue
        los.append(lo)
        his.append(hi)
    if not los:
        return None, None, None, None
    return min(los), max(his), min(his), max(los)


def _choisit_T(b, couples, diam2, echeance=None):
    """Un seuil T² admissible sur CETTE boîte, ou None.

    ATTENTION AU SENS DES BORNES, c'est le piège de cette fonction (je m'y suis pris deux
    fois). Sur la boîte, d_w² est encadré par [lo_w, hi_w] pour chaque témoin w. Les deux
    conditions du théorème, valables pour TOUT (g, h) de la boîte, demandent :

        (ii)  « ∃w : d_w² ≤ T² »  ⟹  il faut T² ≥ hi_w pour un w  ⟹  T² ≥ min_w hi_w
                                         (le pire cas de d_w² est son MAJORANT)
        (iii) « ∃w : d_w² ≥ T² »  ⟹  il faut T² ≤ lo_w pour un w  ⟹  T² ≤ max_w lo_w
                                         (le pire cas est son MINORANT)

    Utiliser max_w lo et min_w hi (ce que fait la vérification paire par paire ci-dessous
    pour constater un échec) n'est PAS suffisant pour construire T : c'est nécessaire, pas
    suffisant, et un T² choisi ainsi au-dessus du vrai maximum ne prouve rien. La
    vérification indépendante l'a montré : sur g ∈ [−1/4,0], h ∈ [9/10,1], T² = 4,7927 avait
    été retenu alors que la vraie distance² maximale entre les cellules (2,1) et (2,2) vaut
    4,4514 au bord de la boîte. D'où :

        bas  = max(diam², max_p min_w hi_w)      haut = min_p max_w lo_w
        admissible ⟺ bas < haut                  T² = (bas + haut)/2

    `bas < haut` est la condition stricte du lemme B (`dmin < dmax`). Le milieu maximise la
    marge, ce qui est le but : voir `certifie_boite` sur la marge du centre (0,03 au lieu
    de 0,25) qui bloquait 18 feuilles par boîte dans la campagne précédente.

    L'enchaînement est cohérent parce que la MÊME primitive sert au calcul des bornes et à
    la vérification finale : `Rat.enc`, forme centrée, dont la sûreté a été contrôlée sur
    7200 points échantillonnés (0 violation). C'est `_inegal` qui NE convient pas ici : elle
    encadre le polynôme num − T²·den d'un bloc, et sur les boîtes hautes les coefficients en
    h¹⁴ font perdre toute la compensation (un d² de 326 était déclaré < 81).
    """
    bas = diam2
    haut = None
    for (paire, (choisis, _)) in couples.items():
        _verifie_echeance(echeance)
        lo_min, hi_max, hi_min, lo_max = _bornes_paire(b, choisis)
        if hi_min is None or lo_max is None:
            return None
        bas = max(bas, hi_min)          # pire cas du côté « proche »
        haut = lo_max if haut is None else min(haut, lo_max)
    if not (bas < haut):
        return None
    return (bas + haut) / 2


def _premier_echec(b, couples, diam2=None):
    """Diagnostic : où le calcul du seuil s'est arrêté, et de quel type d'échec il s'agit.

    Deux causes très différentes, qu'il ne faut pas confondre :
      * « bas ≥ haut » avec des valeurs FRANCHEMENT incompatibles : les témoins retenus ne
        suffisent pas sur cette boîte (il faut subdiviser, ou prendre plus de témoins) ;
      * une incompatibilité de faible largeur : c'est l'encadrement qui manque de finesse.

    Un échec ici n'est jamais une réfutation.
    """
    bas = diam2
    haut = None
    ou = None
    for (paire, (choisis, _)) in couples.items():
        lo_min, hi_max, hi_min, lo_max = _bornes_paire(b, choisis)
        if hi_min is None:
            return f"paire {paire} sans témoin exploitable"
        if haut is not None and hi_min >= haut:
            ou = paire
        bas = max(bas, hi_min)
        haut = lo_max if haut is None else min(haut, lo_max)
    txt = f"bas = {float(bas):.4f} ≥ haut = {float(haut):.4f}"
    if diam2 is not None:
        txt += f" (diamètre² = {float(diam2):.4f})"
    if ou is not None:
        txt += f", bloqué par la paire {ou}"
    return txt


def certifie_boite(g0, g1, h0, h1, T2=None, clique=None, echeance=None):
    """Certifie l'obligation sur la boîte, ou dit qu'il faut subdiviser.

    ATTENTION À NE PAS CONFONDRE (c'était mon erreur de la première version) :
      * la CLIQUE est un ensemble de 7 DÉCALAGES du réseau (les sept cellules) ;
      * les TÉMOINS sont des points des cellules, pas la clique.

    Obligation à prouver, pour une clique d₁…d₇ et un seuil T :
      (i)   le diamètre de la cellule est < T                        [ε = D/T < 1]
      (ii)  pour chacune des 21 paires, il existe des points u, v de la cellule tels que
            |u − (v + d)|² ≤ T²                      — les témoins proches
      (iii) pour chacune des 21 paires, il existe u, v tels que |u − (v + d)|² ≥ T²
                                                     — les témoins lointains
    (ii) et (iii) sont les deux hypothèses de `Boites.clique_de_temoins` ; (i) est celle de
    `Pont.lemmeB` (0 < ε = D/T < 1, dmin ≤ D/ε ≤ dmax, dmin < dmax ⟹ l'échelle existe).
    Les sommets prouvés appartiennent à la cellule pour TOUT (g, h) de la boîte, donc les
    témoins aussi (translation) ; les milieux d'arêtes sont sûrs par convexité.

    QUATRE DÉFAUTS CORRIGÉS ICI, tous découverts en instrumentant la campagne :

    1. LE SEUIL T ÉTAIT CELUI DU CENTRE DE LA BOÎTE RACINE, propagé à toutes les feuilles.
       La marge restante était celle du centre (0,03 au lieu de 0,25), et la subdivision ne
       pouvait rien y changer. T est maintenant choisi pour la boîte : voir `_choisit_T`.

    2. LES TÉMOINS ÉTAIENT RESTREINTS AUX SOMMETS. Or ce sont deux points quelconques des
       cellules. Voir `points_temoins` : milieux d'arêtes ajoutés, sûrs par convexité.

    3. LA MEMBRURE ENCADRÉE COMPARAIT DEUX QUOTIENTS. `a ≤ T²` s'écrit num − T²·den ≤ 0
       avec den > 0 : UN seul polynôme, jamais deux encadrements comparés (règle du dossier,
       geste 19). C'est `_inegal`, et elle seule décide.

    4. LE RAYON r DE LA RÉDUCTION AU FINI ÉTAIT DÉMESURÉ, et son second passage pouvait
       l'ÉLARGIR (jusqu'à 6528 contraintes sur h ∈ [2,3], 90 s par nœud). Voir
       `rayon_numerique` et `_sommets_prouves`.
    """
    b = Boite(g0, g1, h0, h1)
    gc, hc = (g0 + g1) / 2, (h0 + h1) / 2
    if clique is None:
        try:
            _, _, clique = meilleur_T(Cellule(gc, hc))
        except Exception:
            return {"ok": False, "raison": "aucune clique au centre", "subdiviser": False}
    if clique is None or len(clique) < 7:
        return {"ok": False, "raison": "clique de centre < 7", "subdiviser": True}
    clique = list(clique)[:9]
    r = {"boite": [str(g0), str(g1), str(h0), str(h1)],
         "clique": [list(c) for c in clique], "subdiviser": False}

    A, cands = b.boite_sup_sommets()
    if len(cands) < 3:
        return {**r, "raison": f"sur-ensemble dégénéré ({len(cands)})"}
    _verifie_echeance(echeance)
    r2 = rayon_numerique(g0, g1, h0, h1, cands)
    if r2 is None:
        r2 = rayon_geometrique(g0, g1, h0, h1)
    try:
        proves, cons = _sommets_prouves(b, cands, r2)
    except ZeroDivisionError as e:
        return {**r, "raison": f"appartenance : {e}", "subdiviser": True}
    r["sommets_prouves"] = len(proves)
    if len(proves) < 3:
        return {**r, "raison": f"{len(proves)} sommets prouvés sur {len(cands)}",
                "subdiviser": True}
    sommets = [s for (_, _, s) in proves]
    temoins = points_temoins(sommets, gc, hc)

    # (i) diamètre de l'enveloppe des sommets : ne dépend pas de T
    diam2 = None
    for a in range(len(sommets)):
        for c in range(a + 1, len(sommets)):
            try:
                hi = dist2_rat(sommets[a], sommets[c]).enc(b.boite)[1]
            except ZeroDivisionError as e:
                return {**r, "raison": f"diamètre : {e}", "subdiviser": True}
            diam2 = hi if diam2 is None else max(diam2, hi)
    r["diam2_sup"] = str(diam2)

    _verifie_echeance(echeance)
    couples = _couples_temoins(b, temoins, clique, echeance)
    if couples is None:
        return {**r, "raison": "témoins : dénominateur de signe indéterminé",
                "subdiviser": True}

    if T2 is None:
        T2 = _choisit_T(b, couples, diam2, echeance)
        if T2 is None:
            return {**r, "raison": "pas de seuil : " + _premier_echec(b, couples, diam2),
                    "subdiviser": True}
    r["T2"] = str(T2)

    # VÉRIFICATION FINALE, paire par paire et côté par côté
    for (paire, (choisis, _)) in couples.items():
        _verifie_echeance(echeance)
        lo_min, hi_max, hi_min, lo_max = _bornes_paire(b, choisis)
        if hi_min is None:
            return {**r, "raison": f"paire {paire} : aucun témoin exploitable",
                    "subdiviser": True}
        # (ii) « ∃w : d_w² ≤ T² » : il suffit que le MAJORANT d'un témoin soit ≤ T²,
        #      donc que min_w hi_w ≤ T².
        if not (hi_min <= T2):
            return {**r, "raison": f"paire {paire} : aucun témoin proche "
                                   f"(min des majorants = {float(hi_min):.4f} > T² = "
                                   f"{float(T2):.4f})", "subdiviser": True}
        # (iii) « ∃w : d_w² ≥ T² » : il suffit que le MINORANT d'un témoin soit ≥ T²,
        #       donc que max_w lo_w ≥ T².
        if not (T2 <= lo_max):
            return {**r, "raison": f"paire {paire} : aucun témoin lointain "
                                   f"(max des minorants = {float(lo_max):.4f} < T² = "
                                   f"{float(T2):.4f})", "subdiviser": True}
    if not (diam2 < T2):
        return {**r, "raison": "diamètre : l'enveloppe dépasse le seuil", "subdiviser": True}
    r.update(ok=True, raison="diamètre < T, 21 paires avec témoins proche et lointain")
    return r


def rayon_geometrique(g0, g1, h0, h1):
    """Majorant de |p|² pour p dans la cellule, valable pour TOUT (g, h) de la boîte.

    POURQUOI PAS « le max des |s|² des candidats » : parmi les intersections de paires de
    contraintes figurent des points arbitrairement loin, qui ne sont pas dans la cellule
    mais que rien n'écarte a priori. Sur la boîte h ∈ [8, 15] l'un d'eux donne
    r² ≈ 4,1·10¹⁰, et la liste de contraintes explose (la boucle porte sur ≈ 2r × 2r/h
    décalages) : le calcul ne termine pas. Un rayon tiré des DONNÉES ne vaut que si les
    données sont dans la cellule — ce qu'on est justement en train de prouver.

    LE PIÈGE À ÉVITER (il m'a coûté une version fausse) : dans la base b₁ = (1, 0),
    b₂ = (g, h), les vecteurs du réseau sont i·b₁ + j·b₂ = (i + j·g, j·h). Le vecteur
    d'indices (0, 1) est donc (g, h) et NON (0, h) : écrire « |p_y| ≤ h/2 grâce à la
    contrainte (0,±1) » est faux dès que g ≠ 0. Le majorant doit se déduire des seuls
    vecteurs dont on connaît vraiment les coordonnées, c'est-à-dire de b₁, b₂ et b₂ − b₁.

    Majorant retenu, et il est SÛR : la cellule est contenue dans l'intersection des
    demi-plans associés à ces trois vecteurs, qui sont tous dans le réseau,

        T = { p : ⟨p, b₁⟩ ≤ |b₁|²/2,  ⟨p, b₂⟩ ≤ |b₂|²/2,  ⟨p, b₂−b₁⟩ ≤ |b₂−b₁|²/2 }.

    Ces trois normales engendrent positivement ℝ² (b₁ et b₂ sont une base, et
    b₁ − b₂ + (b₂−b₁) = 0), donc T est un TRIANGLE borné, et la cellule y est incluse.
    On prend r² = (6/5)·max des |sommet|² de ce triangle : le facteur n'est qu'une marge,
    car la sûreté est de toute façon revérifiée sommet par sommet par `_dans_boule`.

    Gain : sur h ∈ [8, 15] l'ancienne formule donnait r² = 2(1+16²)+1 = 515, celle-ci
    donne ≈ (6/5)·(1 + h²)/4 ≈ 68. La longueur de la liste de contraintes varie comme r²/h,
    d'où un gain d'un ordre de grandeur sur les grandes boîtes.
    """
    pts = []
    for (a, c) in (((1, 0), (0, 1)), ((1, 0), (-1, 1)), ((0, 1), (-1, 1))):
        s = sommet(a[0], a[1], c[0], c[1])
        if s is None:
            continue
        pts.append(s)
    if not pts:
        return 2 * (1 + (max(abs(F(h0)), abs(F(h1))) + 1) ** 2) + 1
    boite = (g0, g1, h0, h1)
    r2 = None
    for p in pts:
        hi = dist2_rat(p, ZERO_RAT).enc(boite)[1]
        r2 = hi if r2 is None else max(r2, hi)
    return F(6, 5) * r2


def rayon_numerique(g0, g1, h0, h1, cands):
    """Majorant de |p|² estimé NUMÉRIQUEMENT, pour raccourcir la liste de contraintes.

    Ce rayon n'est PAS un ingrédient de sûreté — et c'est ce qui autorise à l'estimer.
    La réduction au fini (`Boites.contrainte_auto`) dit : si |p|² ≤ r² et |w|² ≥ 4r², alors
    la contrainte de w est automatique. Le seul usage de r est donc là, et `_dans_boule`
    revérifie |s|² ≤ r² EXACTEMENT, sommet par sommet, avant d'accepter quoi que ce soit.
    Un r trop petit fait seulement perdre des sommets (preuve incomplète) ; il ne peut pas
    faire accepter un point hors de la cellule. C'est pourquoi on peut se permettre de
    l'estimer sur cinq points échantillonnés au lieu de l'encadrer sur la boîte.

    Méthode : aux cinq points (quatre coins + centre), on construit la cellule numériquement
    (`audit_gh.cellule`), on garde les candidats qui y sont, et on prend le plus grand |p|²
    observé, majoré de 30 %. Le facteur absorbe le déplacement de la cellule entre le point
    d'échantillonnage et l'intérieur de la boîte.

    Gain mesuré sur h ∈ [2, 3] : le triangle majorant donnait r² = 29 (194 contraintes,
    90 s par nœud) ; ici r² ≈ 3 (une vingtaine de contraintes).
    """
    best = None
    for gg in (g0, (g0 + g1) / 2, g1):
        for hh in (h0, (h0 + h1) / 2, h1):
            try:
                info = AG.cellule(gg, hh)
            except Exception:
                info = None
            if info is None:
                continue
            Pd = info[0]
            for (_, _, spt) in cands:
                try:
                    x = spt[0].n.eval(gg, hh) / spt[0].d.eval(gg, hh)
                    y = spt[1].n.eval(gg, hh) / spt[1].d.eval(gg, hh)
                except ZeroDivisionError:
                    continue
                if _dist2_point_convexe((x, y), Pd) != 0:
                    continue
                d2 = x * x + y * y
                best = d2 if best is None else max(best, d2)
    if best is None:
        return None
    return F(13, 10) * best + F(1, 100)


def _rayons_borne(cands, boite):
    """Ancien calcul, conservé pour comparaison — voir `rayon_geometrique`."""
    ray = [dist2_rat(s, ZERO_RAT) for (_, _, s) in cands]
    return max(_borne_sup(r, boite) for r in ray)


def couvre(g0, g1, h0, h1, profondeur=0, prof_max=7, T2=None, journal=None, echeance=None,
           clique=None):
    """Subdivise jusqu'à certifier ; renvoie (feuilles certifiées, échecs, essais).

    La CLIQUE est calculée une seule fois, à la racine, puis RÉUTILISÉE telle quelle par
    tous les descendants. C'est licite et c'est le point important : la clique n'est qu'un
    jeu de sept décalages CANDIDATS ; ce qui la rend légitime sur une boîte, ce sont les
    témoins proches et lointains, revérifiés exactement sur chaque nœud. Recalculer
    `meilleur_T` au centre de chaque nœud ne changeait jamais la réponse et coûtait, sur
    les boîtes à grand h, plus cher que la preuve elle-même (énumération des décalages
    dans une fenêtre de rayon 5·D pour chaque centre).
    """
    if clique is None:
        try:
            _, _, clique = meilleur_T(Cellule((g0 + g1) / 2, (h0 + h1) / 2))
        except Exception:
            clique = None
    try:
        r = certifie_boite(g0, g1, h0, h1, T2=T2, clique=clique, echeance=echeance)
    except Trop_Long as e:
        r = {"ok": False, "subdiviser": False, "raison": f"trop long : {e}"}
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
        f, e, n = couvre(a, b_, c, d, profondeur + 1, prof_max, T2, journal, echeance,
                         clique)
        feuilles += f
        echecs += e
        essais += n
    return feuilles, echecs, essais
