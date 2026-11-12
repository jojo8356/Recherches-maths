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


def iadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def imul(a, b):
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (min(p), max(p))


class Arbre:
    """Polynôme + ses dérivées premières, calculées UNE fois (pas d'arbre récursif :
    un arbre complet coûterait 2^degré nœuds)."""
    __slots__ = ("f", "dg", "dh")

    def __init__(self, f):
        self.f = f
        dg, dh = f.dg(), f.dh()
        self.dg = dg if not dg.zero() else None
        self.dh = dh if not dh.zero() else None


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
    return (lo, hi) if lo <= hi else out


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
        return enc_rat(self.n, self.d, boite)

    def signe_enc(self, boite):
        """(min, max) du signe : on multiplie par le signe du dénominateur, supposé constant."""
        a = enc(self.n, boite)
        b = enc(self.d, boite)
        if b[0] > 0:
            return a
        if b[1] < 0:
            return (-a[1], -a[0])
        raise ZeroDivisionError(f"dénominateur non défini en signe : {b}")


def carre(r):
    return r * r


def point(x, y):
    return (x, y)


def dist2(p, q):
    dx, dy = p[0] - q[0], p[1] - q[1]
    return carre(dx) + carre(dy)
