"""Polynômes exacts en (g, h) et encadrement par forme de la moyenne.

Idée
----
Toute la géométrie d'un réseau b1 = (1,0), b2 = (g, h) est une FONCTION RATIONNELLE de
(g, h) : contraintes 2<p,v> <= |v|^2, sommets = solutions de systèmes 2x2, distances^2.
On représente numérateur et dénominateur comme des polynômes exacts à coefficients
rationnels, et on encadre un polynôme f sur une boîte par

    f(x) in f(x_c) + somme_i  enc(df/dx_i) * (X_i - x_c_i),

qui est exact (forme de la moyenne) et dont le reste est d'ordre 2 en la taille de la
boîte. L'encadrement des dérivées est calculé par la MÊME règle, récursivement, ce qui
donne un ordre élevé sans effort.

Pourquoi cela règle le problème de T7
-------------------------------------
L'arithmétique d'intervalles naïve gonfle les expressions à dépendance : det = g*h - h*(1+g)
vaut exactement -h, mais son encadrement naïf a une largeur double de celle de h, et cette
largeur se propage dans toutes les coordonnées. Ici le point central est évalué EXACTEMENT
et la largeur ne dépend que des dérivées, pas des compensations. Conséquence pratique :
det = -h, et les contraintes qui définissent un sommet donnent un numérateur IDENTIQUEMENT
nul, donc encadré par [0, 0] — le faux positif catastrophique de T7 (majorant > 0 sur une
expression identiquement nulle) disparaît par construction.
"""
from fractions import Fraction as F


class Poly:
    __slots__ = ("d", "_ct")

    def __init__(self, d=None):
        self.d = {k: F(v) for k, v in (d or {}).items() if v}
        self._ct = None

    # ---- construction
    @staticmethod
    def monome(i, j, c=1):
        return Poly({(i, j): c})

    @staticmethod
    def const(c):
        return Poly({(0, 0): c}) if c else Poly()

    g = None
    h = None

    # ---- arithmétique
    def __add__(self, o):
        if isinstance(o, (int, F)):
            o = Poly.const(o)
        r = dict(self.d)
        for k, v in o.d.items():
            r[k] = r.get(k, F(0)) + v
            if r[k] == 0:
                del r[k]
        return Poly(r)

    __radd__ = __add__

    def __neg__(self):
        return Poly({k: -v for k, v in self.d.items()})

    def __sub__(self, o):
        if isinstance(o, (int, F)):
            o = Poly.const(o)
        return self + (-o)

    def __mul__(self, o):
        if isinstance(o, (int, F)):
            return Poly({k: v * o for k, v in self.d.items()})
        r = {}
        for k1, v1 in self.d.items():
            for k2, v2 in o.d.items():
                k = (k1[0] + k2[0], k1[1] + k2[1])
                r[k] = r.get(k, F(0)) + v1 * v2
        return Poly({k: v for k, v in r.items() if v})

    __rmul__ = __mul__

    def __truediv__(self, c):
        return Poly({k: v / F(c) for k, v in self.d.items()})

    def zero(self):
        return not self.d

    # ---- évaluation et dérivées
    def eval(self, g, h):
        s = F(0)
        for (i, j), v in self.d.items():
            s += v * (g ** i) * (h ** j)
        return s

    def dg(self):
        return Poly({(i - 1, j): v * i for (i, j), v in self.d.items() if i})

    def dh(self):
        return Poly({(i, j - 1): v * j for (i, j), v in self.d.items() if j})

    def __repr__(self):
        return " + ".join(f"{v}*g^{i}*h^{j}" for (i, j), v in sorted(self.d.items()))


Poly.g = Poly.monome(1, 0, 1)
Poly.h = Poly.monome(0, 1, 1)
G, H = Poly.g, Poly.h


def _max_abs(iv):
    """Plus grande valeur absolue d'un intervalle [lo, hi]."""
    return max(abs(iv[0]), abs(iv[1]))


def iadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def imul(a, b):
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (min(p), max(p))


class Arbre:
    """Polynôme, ses dérivées premières et secondes, calculées UNE fois.

    Les dérivées secondes servent à la forme de la moyenne d'ORDRE 2 (`enc`), sans quoi
    l'encadrement d'une coordonnée de sommet reste much trop large sur les boîtes hautes :
    sur g ∈ [−1/2,−1/4], h ∈ [9/10, 1] la vraie valeur de |s|² vaut 0,373 et l'encadrement
    d'ordre 1 donnait [0,165 ; 3,418] — un facteur 20, qui rendait toute preuve impossible.
    """
    __slots__ = ("f", "dg", "dh", "dgg", "dgh", "dhh")

    def __init__(self, f):
        self.f = f
        dg, dh = f.dg(), f.dh()
        self.dg = dg if not dg.zero() else None
        self.dh = dh if not dh.zero() else None
        dgg = dg.dg() if self.dg is not None else Poly()
        dgh = dg.dh() if self.dg is not None else Poly()
        dhh = dh.dh() if self.dh is not None else Poly()
        self.dgg = dgg if not dgg.zero() else None
        self.dgh = dgh if not dgh.zero() else None
        self.dhh = dhh if not dhh.zero() else None


def comp(f):
    if isinstance(f, Arbre):
        return f
    if f._ct is None:
        f._ct = Arbre(f)
    return f._ct


NIVEAU_PLEIN = 1      # un niveau de forme de la moyenne, fond de récursion par ieval


def _puissances(a, dmax):
    out = [(F(1), F(1))]
    for _ in range(dmax):
        out.append(imul(out[-1], a))
    return out


def ieval(f, boite):
    """Évaluation d'intervalle SÛRE d'un polynôme (Horner par variable, coût linéaire)."""
    g0, g1, h0, h1 = boite
    a = comp(f).f
    if not a.d:
        return (F(0), F(0))
    gmax = max(i for (i, j) in a.d)
    hmax = max(j for (i, j) in a.d)
    hp = _puissances((h0, h1), hmax)
    par_j = {}
    for (i, j), c in a.d.items():
        par_j.setdefault(j, []).append((i, c))
    total = None
    for j, termes in par_j.items():
        deg = max(i for i, _ in termes)
        coef = {i: c for i, c in termes}
        acc = (F(0), F(0))
        for i in range(deg, -1, -1):
            acc = imul(acc, (g0, g1))
            c = coef.get(i)
            if c:
                acc = (acc[0] + c, acc[1] + c)
        term = imul(acc, hp[j])
        total = term if total is None else (total[0] + term[0], total[1] + term[1])
    return total


def enc(f, boite, prof=0):
    """Encadrement de f sur la boîte.

    Forme de la moyenne (théorème des accroissements finis) :
        f(x) = f(x_c) + somme_i df/dx_i(xi) (x_i - x_c_i),  xi dans la boîte,
    donc f(x) appartient à  f(x_c) + somme_i [df/dx_i](boîte) * [-r_i, r_i], où [.] est une
    évaluation d'intervalle SÛRE. Ce n'est pas une troncature de Taylor : c'est exact, avec
    un reste encadré.
    """
    a = comp(f)
    if a.dg is None and a.dh is None:
        c = a.f.d.get((0, 0), F(0))
        return (c, c)
    g0, g1, h0, h1 = boite
    gc, hc = (g0 + g1) / 2, (h0 + h1) / 2
    rg, rh = (g1 - g0) / 2, (h1 - h0) / 2
    val = a.f.eval(gc, hc)
    out = (val, val)
    if a.dg is not None:
        out = iadd(out, imul(ieval(a.dg, boite), (-rg, rg)))
    if a.dh is not None:
        out = iadd(out, imul(ieval(a.dh, boite), (-rh, rh)))
    # INTERSECTION avec l'évaluation d'intervalle directe (Horner).
    # Les deux encadrements sont sûrs, donc leur intersection l'est aussi ; et ils sont
    # complémentaires : la forme de la moyenne gère les compensations près du centre mais
    # est catastrophique sur les monômes de degré élevé (h^8 sur [1,2] donnait [-486,537]
    # au lieu de [1,256], ce qui faisait échouer tout dénominateur en h^8), l'évaluation
    # directe est exacte sur un monôme mais perd les compensations.
    d = ieval(a.f, boite)
    lo, hi = max(out[0], d[0]), min(out[1], d[1])
    ordre1 = (lo, hi) if lo <= hi else out

    # ---- ordre 2, en CINQ CENTRES : f(x) = f(c) + df(c)·δ + ½ δᵀ H(ξ) δ.
    #
    # Un seul centre (le milieu) ne suffit pas : la forme centrée en c est excellente près
    # de c et s'élargit comme |f'|·|x − c|. Sur g ∈ [−1/2,−1/4], h ∈ [8 ; 10,33] le
    # diamètre² VRAI de l'enveloppe des sommets vaut 78, et l'encadrement au centre donnait
    # 574 : la largeur n'était pas de la précision, c'était tout le problème.
    #
    # On encadre donc aussi depuis les quatre coins, et on intersecte : chaque encadrement
    # est sûr, donc leur intersection l'est, et près de chaque point de la boîte c'est le
    # centre le plus proche qui est le plus fin. C'est l'astuce qui fait passer le certificat
    # des boîtes h ≲ 2 aux boîtes h ∈ [8, 15].
    if a.dgg is not None or a.dgh is not None or a.dhh is not None:
        # Bornes des dérivées secondes, calculées UNE fois.
        Mgg = _max_abs(ieval(a.dgg, boite)) if a.dgg is not None else F(0)
        Mgh = _max_abs(ieval(a.dgh, boite)) if a.dgh is not None else F(0)
        Mhh = _max_abs(ieval(a.dhh, boite)) if a.dhh is not None else F(0)
        for (cg, ch, dg, dh) in ((gc, hc, rg, rh), (g0, h0, g1 - g0, h1 - h0),
                                (g1, h0, g1 - g0, h1 - h0), (g0, h1, g1 - g0, h1 - h0),
                                (g1, h1, g1 - g0, h1 - h0)):
            valc = a.f.eval(cg, ch)
            l_lo = l_hi = F(0)
            if a.dg is not None:
                c1 = a.dg.eval(cg, ch)
                l_lo += min(c1 * dg, c1 * (-dg))
                l_hi += max(c1 * dg, c1 * (-dg))
            if a.dh is not None:
                c1 = a.dh.eval(cg, ch)
                l_lo += min(c1 * dh, c1 * (-dh))
                l_hi += max(c1 * dh, c1 * (-dh))
            # Reste d'ordre 2 : ½ δᵀ H δ avec |δ_g| ≤ dg et |δ_h| ≤ dh — LES MÊMES
            # amplitudes que le terme linéaire. Utiliser les demi-largeurs rg, rh pour un
            # centre qui est un COIN était la faute : là, |δ| va jusqu'à 2·r, donc le
            # reste est jusqu'à 4 fois plus grand, et l'encadrement devenait FAUX
            # (350 violations sur 7200 points échantillonnés, avant correction).
            rem = (Mgg * dg * dg + 2 * Mgh * dg * dh + Mhh * dh * dh) / 2
            lo2, hi2 = max(ordre1[0], valc + l_lo - rem), min(ordre1[1], valc + l_hi + rem)
            if lo2 <= hi2:
                ordre1 = (lo2, hi2)
    return ordre1


def enc_rat(num, den, boite):
    """Encadrement de num/den ; exige que den ne change pas de signe sur la boîte."""
    a = enc(num, boite)
    b = enc(den, boite)
    if b[0] > 0:
        return imul(a, (1 / b[1], 1 / b[0]))
    if b[1] < 0:
        return imul(a, (1 / b[1], 1 / b[0]))
    raise ZeroDivisionError(f"dénominateur non défini en signe : {b}")


class Rat:
    """Fonction rationnelle num/den en (g, h)."""
    __slots__ = ("n", "d")

    def __init__(self, n, d=None):
        self.n = n
        self.d = d if d is not None else Poly.const(1)

    def __add__(self, o):
        o = o if isinstance(o, Rat) else Rat(o if isinstance(o, Poly) else Poly.const(o))
        return Rat(self.n * o.d + o.n * self.d, self.d * o.d)

    __radd__ = __add__

    def __neg__(self):
        return Rat(-self.n, self.d)

    def __sub__(self, o):
        o = o if isinstance(o, Rat) else Rat(o if isinstance(o, Poly) else Poly.const(o))
        return self + (-o)

    def __mul__(self, o):
        o = o if isinstance(o, Rat) else Rat(o if isinstance(o, Poly) else Poly.const(o))
        return Rat(self.n * o.n, self.d * o.d)

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = o if isinstance(o, Rat) else Rat(o if isinstance(o, Poly) else Poly.const(o))
        return Rat(self.n * o.d, self.d * o.n)

    def enc(self, boite):
        """Encadrement de num/den, par FORME CENTRÉE, intersecté avec la forme naïve.

        POURQUOI CE N'EST PAS `enc_rat(num, den)` TOUT SEUL : encadrer le numérateur puis le
        dénominateur et diviser les deux largeurs est correct mais catastrophique dès que
        les deux dépendent de (g, h). Sur g ∈ [−1/2,−1/4], h ∈ [9/10,1], une coordonnée de
        sommet qui vaut 0,374 au centre s'encadrait dans [0,185 ; 3,418] — un facteur 20,
        qui rendait toute obligation impossible à prouver.

        Forme centrée : soit c la valeur exacte au centre et d = num − c·den, qui S'ANNULE
        exactement au centre. Alors

            num/den − c = d / den ,

        et d s'encadre en O(largeur²) puisqu'il est nul au centre (c'est exactement le
        phénomène que la forme de la moyenne exploite). La largeur du résultat ne contient
        plus le terme c × largeur(den), qui était le coupable.

        Sûreté : les deux encadrements (centré, naïf) sont corrects, donc leur intersection
        l'est aussi ; en cas d'intersection vide — impossible si les deux sont sûrs, mais on
        ne parie pas là-dessus — on garde le naïf. `den` doit être de signe constant.
        """
        naif = enc_rat(self.n, self.d, boite)
        g0, g1, h0, h1 = boite
        gc, hc = (g0 + g1) / 2, (h0 + h1) / 2
        dc = self.d.eval(gc, hc)
        if dc == 0:
            return naif
        c = self.n.eval(gc, hc) / dc
        d = self.n - Poly.const(c) * self.d
        idd = enc(d, boite)
        ivd = enc(self.d, boite)
        if ivd[0] > 0:
            inv = (1 / ivd[1], 1 / ivd[0])
        elif ivd[1] < 0:
            inv = (1 / ivd[1], 1 / ivd[0])
        else:
            return naif
        prod = imul(idd, inv)
        lo = c + prod[0]
        hi = c + prod[1]
        lo, hi = max(lo, naif[0]), min(hi, naif[1])
        return (lo, hi) if lo <= hi else naif

    def signe_enc(self, boite):
        """(min, max) de la valeur de num/den sur la boîte ; den doit être de signe constant.

        ATTENTION : ce n'est PAS « encadrer num, encadrer den, diviser ». Cette version-là
        (celle d'avant) était correcte mais très large, parce que la largeur de den se
        multipliait par la valeur de num/den. Sur les boîtes hautes elle rendait impossibles
        des inégalités vraies. On passe par `enc`, qui utilise la forme centrée
        num/den − c = (num − c·den)/den et converge en O(largeur²) au centre.
        """
        b = enc(self.d, boite)
        if b[0] > 0 or b[1] < 0:
            return self.enc(boite)
        raise ZeroDivisionError(f"dénominateur non défini en signe : {b}")


def carre(r):
    return r * r


def point(x, y):
    return (x, y)


def dist2(p, q):
    dx, dy = p[0] - q[0], p[1] - q[1]
    return carre(dx) + carre(dy)
