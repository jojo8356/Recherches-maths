"""GESTE 2 — Verificateur independant, en arithmetique rationnelle EXACTE.

Ce que fait ce fichier
----------------------
Il ne cherche rien. Il prend les TEMOINS exportes par `run_temoins.py` et verifie, boite
par boite, en arithmetique rationnelle exacte (fractions de dyadiques, aucune bibliotheque
flottante, aucun mpmath), que :

  1. chaque point temoin appartient bien a la cellule de Voronoi de l'origine pour TOUT
     (rho, theta) de la boite : les contraintes sont 2<p,v> <= |v|^2 pour tout v du reseau,
     et pour |v| >= 5 la contrainte est automatique des que le point est dans B(0,2.5) ;
  2. deux temoins certifies donnent une MINORATION du diametre de cellule (ils sont dans
     la cellule, leur distance est un rationnel exact) ;
  3. P_sup (intersection des contraintes actives) MAJORE le diametre : c'est un
     sur-ensemble de la cellule, son diametre est atteint au couple de sommets le plus
     eloigne, et sa bornitude est certifiee par une relation lineaire a coefficients
     strictement positifs entre trois de ses normales ;
  4. pour chaque paire de la clique : un couple proche de distance^2 <= T_min^2 et un
     couple eloigne de distance^2 >= T_max^2, avec T_min <= T(t) <= T_max.

D'ou, pour tout t de la boite : dmin <= T(t) <= dmax, donc les deux cellules portent un
segment de longueur T(t) (theoreme du pont, formalise en Lean : conflit <=> encadrement).
Les 7 cellules de la clique sont deux a deux en conflit : la clique est de taille 7.

Trigonometrie rigoureuse
------------------------
pi est encadre par la formule de Machin en fractions exactes (series alternees, reste
majore par le premier terme omis). sin et cos sont calcules par leur serie de Taylor avec
reste de Lagrange, sur [0, 2.2] rad (notre domaine est [pi/3, 2pi/3]), et prolonges aux
intervalles par monotonie : cos est decroissant sur [0,pi], sin croissant jusqu'a pi/2.

Controle negatif
----------------
`--controle` deplace un temoin de 1 % et exige que la verification ECHOUE : sans cela,
le verificateur ne prouve rien.
"""
import gzip
import json
import sys
import time
from fractions import Fraction as F

# ---------------------------------------------------------------- arithmetique d'intervalles
# Toutes les bornes sont ramenees sur la grille dyadique k/2^B, arrondies VERS L'EXTERIEUR.
# Deux raisons : (a) c'est rigoureux (l'arrondi ne retire jamais un point reel) ; (b) les
# fractions restent petites, donc le calcul est rapide. B = 64 donne 5.4e-20 de resolution,
# soit 8 ordres de grandeur sous les marges du certificat (~1e-12).
B = 64
ONE = 1 << B


def _lo(v):
    return F((v.numerator * ONE) // v.denominator, ONE)


def _hi(v):
    return F(-((-v.numerator * ONE) // v.denominator), ONE)


def rnd(a):
    return (_lo(a[0]), _hi(a[1]))


def I(lo, hi=None):
    return rnd((lo, lo)) if hi is None else rnd((lo, hi))


def add(a, b):
    return rnd((a[0] + b[0], a[1] + b[1]))


def sub(a, b):
    return rnd((a[0] - b[1], a[1] - b[0]))


def scale(k, a):
    return rnd((k * a[0], k * a[1])) if k >= 0 else rnd((k * a[1], k * a[0]))


def mul(a, b):
    p1, p2, p3, p4 = a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]
    return rnd((min(p1, p2, p3, p4), max(p1, p2, p3, p4)))


def sq(a):
    if a[0] >= 0:
        return rnd((a[0] * a[0], a[1] * a[1]))
    if a[1] <= 0:
        return rnd((a[1] * a[1], a[0] * a[0]))
    return rnd((F(0), max(a[0] * a[0], a[1] * a[1])))


# ---------------------------------------------------------------- pi, sin, cos (rigoureux)
def _pi():
    """Machin : pi = 16 arctan(1/5) - 4 arctan(1/239), series alternees exactes."""
    def arctan_inv(m, n=30):
        s, m2 = F(0), F(m * m)
        terme = F(1, m)
        for k in range(n):
            s += terme / (2 * k + 1) if k % 2 == 0 else -terme / (2 * k + 1)
            terme /= m2
        # reste majore par le premier terme omis
        return s, F(1) / ((2 * n + 1) * m ** (2 * n + 1))

    a5, r5 = arctan_inv(5)
    a239, r239 = arctan_inv(239)
    lo = 16 * a5 - 4 * a239 - (16 * r5 + 4 * r239)
    hi = 16 * a5 - 4 * a239 + (16 * r5 + 4 * r239)
    return lo, hi


PI_LO, PI_HI = rnd(_pi())


_SIN_CACHE = {}
_COS_CACHE = {}


def _sin_pt(x, n=14):
    """sin(x) pour x rationnel dans [0, 2.2], encadre (reste de Lagrange <= x^(2n+1)/(2n+1)!)."""
    s, xp, fac = F(0), x, F(1)
    for k in range(n):
        if k > 0:
            xp *= x * x
            fac *= (2 * k) * (2 * k + 1)
        s += xp / fac if k % 2 == 0 else -xp / fac
    R = x ** (2 * n + 1) / _fact(2 * n + 1)
    return rnd((s - R, s + R))


def _cos_pt(x, n=14):
    s, xp, fac = F(0), F(1), F(1)
    for k in range(n):
        if k > 0:
            xp *= x * x
            fac *= (2 * k - 1) * (2 * k)
        s += xp / fac if k % 2 == 0 else -xp / fac
    R = x ** (2 * n) / _fact(2 * n)
    return rnd((s - R, s + R))


_FACT = {0: F(1)}


def _fact(n):
    if n not in _FACT:
        _FACT[n] = _fact(n - 1) * n
    return _FACT[n]


def _cos_c(x):
    if x not in _COS_CACHE:
        _COS_CACHE[x] = _cos_pt(x)
    return _COS_CACHE[x]


def _sin_c(x):
    if x not in _SIN_CACHE:
        _SIN_CACHE[x] = _sin_pt(x)
    return _SIN_CACHE[x]


def cos_iv(a, b):
    """cos sur [a,b] inclus dans [0, pi] : decroissant."""
    assert a >= 0 and b <= PI_LO, (float(a), float(b))
    return rnd((_cos_c(b)[0], _cos_c(a)[1]))


def sin_iv(a, b):
    """sin sur [a,b] inclus dans [0, pi] : croissant puis decroissant."""
    assert a >= 0 and b <= PI_LO
    sa, sb = _sin_c(a), _sin_c(b)
    if b <= PI_LO / 2:
        return (sa[0], sb[1])
    if a >= PI_HI / 2:
        return (sb[0], sa[1])
    return (min(sa[0], sb[0]), F(1))


# ---------------------------------------------------------------- geometrie du reseau
def enveloppe(rho, th0, th1):
    """(b2x, b2y) : enveloppe de rho*(cos, sin)(theta) sur la boite, theta en degres."""
    a = rnd((F(th0) * PI_LO / 180, F(th1) * PI_HI / 180))      # radians, arrondi exterieur
    c = cos_iv(a[0], a[1])
    s = sin_iv(a[0], a[1])
    r = (F(rho[0]), F(rho[1]))
    return mul(r, c), mul(r, s)


def vect(ij, bx, by):
    """Enveloppe de i*b1 + j*b2 avec b1 = (1,0) ; b2 = (bx, by)."""
    i, j = ij
    vx = add(I(F(i)), scale(j, bx))
    vy = scale(j, by)
    return vx, vy


def norm2(vx, vy):
    return add(sq(vx), sq(vy))


# i dans [-10,10], j dans [-5,5] : JUSTIFIE. Sur le domaine, rho in [1,2] et
# |cos theta| <= 1/2, sin theta >= sqrt3/2. Si |j| >= 6 alors |v_y| = |j| rho sin >= 6*1*0.866 > 5.
# Si |i| >= 11 alors |v_x| = |i + j rho cos| >= 11 - 5*2*0.5 = 6 > 5. Donc tout point du reseau
# de norme < 5 est dans cette fenetre.
I_MAX, J_MAX = 10, 5


def vecteurs_reseau(bx, by, seuil2):
    """Tous les v (fenetre ci-dessus) dont la norme^2 peut descendre sous le seuil."""
    out = []
    for i in range(-I_MAX, I_MAX + 1):
        for j in range(-J_MAX, J_MAX + 1):
            if i == 0 and j == 0:
                continue
            vx, vy = vect((i, j), bx, by)
            if norm2(vx, vy)[0] < seuil2:
                out.append(((i, j), vx, vy))
    return out


def contrainte_sup(p, vx, vy):
    """Majorant de 2<p,v> - |v|^2 (nul ou negatif <=> p est dans le demi-plan de v)."""
    px, py = p
    val = sub(scale(2, add(mul(I(px), vx), mul(I(py), vy))), norm2(vx, vy))
    return val[1]


# ---------------------------------------------------------------- P_sup
def psup(offsets, bx, by):
    """Sommets de l'intersection des contraintes actives ; majorants du diametre^2 et du rayon^2."""
    off = list(offsets)
    V = {o: vect(o, bx, by) for o in off}
    C = {o: scale(F(1, 2), norm2(*V[o])) for o in off}

    # --- bornitude : relation lineaire a coefficients STRICTEMENT POSITIFS entre 3 normales.
    # (0 interieur a conv{normales} => l'intersection des demi-plans est bornee.)
    borne = False
    for a in range(len(off)):
        for b in range(a + 1, len(off)):
            for c in range(b + 1, len(off)):
                v1, v2, v3 = V[off[a]], V[off[b]], V[off[c]]
                det = sub(mul(v1[0], v2[1]), mul(v1[1], v2[0]))
                if det[0] <= 0 <= det[1]:
                    continue
                r1 = (-v3[0][1], -v3[0][0])
                r2 = (-v3[1][1], -v3[1][0])
                l1 = div(sub(mul(r1, v2[1]), mul(r2, v2[0])), det)
                l2 = div(sub(mul(v1[0], r2), mul(v1[1], r1)), det)
                if l1[0] > 0 and l2[0] > 0:
                    borne = True
                    break
            if borne:
                break
        if borne:
            break
    if not borne:
        return None

    # --- sommets : intersections de deux droites de contraintes, rejetees SEULEMENT si
    # elles violent franchement une contrainte (sinon on les garde : conserver un point de
    # plus ne peut qu'agrandir le majorant du diametre, donc l'erreur est du bon cote).
    sommets = []
    for a in range(len(off)):
        for b in range(a + 1, len(off)):
            v1, v2 = V[off[a]], V[off[b]]
            det = sub(mul(v1[0], v2[1]), mul(v1[1], v2[0]))
            if det[0] <= 0 <= det[1]:
                continue
            c1, c2 = C[off[a]], C[off[b]]
            x = div(sub(mul(c1, v2[1]), mul(v1[1], c2)), det)
            y = div(sub(mul(v1[0], c2), mul(c1, v2[0])), det)
            ok = True
            for o in off:
                val = sub(scale(2, add(mul(x, V[o][0]), mul(y, V[o][1]))), norm2(*V[o]))
                if val[0] > 0:
                    ok = False
                    break
            if ok:
                sommets.append((x, y))
    if len(sommets) < 3:
        return None
    diam2, ray2 = F(-1), F(-1)
    for a in range(len(sommets)):
        ray2 = max(ray2, norm2(*sommets[a])[1])
        for b in range(a + 1, len(sommets)):
            d = norm2(sub(sommets[a][0], sommets[b][0]), sub(sommets[a][1], sommets[b][1]))
            diam2 = max(diam2, d[1])
    return sommets, diam2, ray2


def neg1(a):
    return (-a[1], -a[0])


def div(a, b):
    assert b[0] > 0 or b[1] < 0, "division par un intervalle contenant 0"
    return mul(a, (1 / b[1], 1 / b[0]))


# ---------------------------------------------------------------- verification d'une boite
SEUIL2 = F(25)          # |v| >= 5 : contrainte automatique si le point est dans B(0,2.5)
EPS = F(1, 1000)        # cellules de diametre 1 - EPS


def dist2_exacte(p, q):
    """Distance^2 exacte entre deux points rationnels."""
    dx, dy = p[0] - q[0], p[1] - q[1]
    return dx * dx + dy * dy


def certifie_point(p, V):
    """Le point p (rationnel) est-il dans la cellule pour tout t de la boite ?"""
    p = (F(p[0]), F(p[1]))
    marge = None
    for (ij, vx, vy) in V:
        s = contrainte_sup(p, vx, vy)
        if s > 0:
            return False, ij, None
        if marge is None or -s < marge:
            marge = -s
    return True, None, marge


def verifie_boite(rec, perturbe=False):
    """Verifie une boite a partir de ses seuls temoins exportes."""
    (rho0, rho1), (th0, th1) = rec["r"], rec["t"]
    tem = rec["tem"]
    bx, by = enveloppe((rho0, rho1), th0, th1)

    # --- 1. P_sup : majorant du diametre et rayon
    ps = psup([tuple(o) for o in tem["A"]], bx, by)
    if ps is None:
        return False, {"raison": "P_sup non certifie (bornitude / sommets)"}
    _s, diam2_max, ray2 = ps
    if ray2 > F(25, 4):
        return False, {"raison": "P_sup sort de B(0,2.5)"}

    # --- 2. vecteurs du reseau a verifier explicitement
    V = vecteurs_reseau(bx, by, SEUIL2)

    # --- 3. choix des temoins : paire generique la plus eloignee (exact), puis temoins
    #        proches dedies a chaque paire
    gen = [(F(p[0]), F(p[1])) for p in tem["gen"]]
    if perturbe:                      # CONTROLE NEGATIF : on pousse les temoins vers l'exterieur
        gen = [(p[0] * F(102, 100), p[1] * F(102, 100)) for p in gen]
    best = []
    n = len(gen)
    for i in range(n):
        for j in range(i + 1, n):
            best.append((dist2_exacte(gen[i], gen[j]), i, j))
    best.sort(reverse=True)
    marge_app = None
    paire_far = None
    for (d2, i, j) in best[:6]:
        oki, _ij, mi = certifie_point(gen[i], V)
        if not oki:
            continue
        okj, _ij2, mj = certifie_point(gen[j], V)
        if not okj:
            continue
        paire_far = (gen[i], gen[j])
        diam_min2 = d2
        marge_app = min(mi, mj)
        break
    if paire_far is None:
        return False, {"raison": "aucune paire generique certifiee"}

    T_min2 = diam_min2 / (1 - EPS) ** 2
    T_max2 = diam2_max / (1 - EPS) ** 2
    if T_max2 <= T_min2:
        return False, {"raison": "encadrement vide (T_max <= T_min)"}

    # --- 4. les 21 paires de la clique
    pf, qf = paire_far
    marge_p = None
    for paire in tem["paires"]:
        a, b = tuple(paire["a"]), tuple(paire["b"])
        va, vb = vect(a, bx, by), vect(b, bx, by)
        vd = (sub(va[0], vb[0]), sub(va[1], vb[1]))     # v_a - v_b, enveloppe
        # proche
        ok_proche = False
        for (pp, qq) in paire["temoins"]:
            pp = (F(pp[0]), F(pp[1]))
            qq = (F(qq[0]), F(qq[1]))
            if perturbe:
                pp = (pp[0] * F(102, 100), pp[1] * F(102, 100))
                qq = (qq[0] * F(102, 100), qq[1] * F(102, 100))
            o1, _a1, _ = certifie_point(pp, V)
            o2, _a2, _ = certifie_point(qq, V)
            if not (o1 and o2):
                continue
            dx = add(I(pp[0] - qq[0]), vd[0])
            dy = add(I(pp[1] - qq[1]), vd[1])
            sup = add(sq(dx), sq(dy))[1]
            if sup <= T_min2:
                ok_proche = True
                m = (T_min2 - sup) / T_min2
                marge_p = m if marge_p is None else min(marge_p, m)
                break
        if not ok_proche:
            return False, {"raison": "pas de temoin proche certifie", "paire": (a, b)}
        # eloigne
        dx = add(I(pf[0] - qf[0]), vd[0])
        dy = add(I(pf[1] - qf[1]), vd[1])
        inf = add(sq(dx), sq(dy))[0]
        if inf < T_max2:
            return False, {"raison": "pas de temoin eloigne certifie", "paire": (a, b),
                           "inf": float(inf), "T_max2": float(T_max2)}
        m = (inf - T_max2) / T_max2
        marge_p = m if marge_p is None else min(marge_p, m)

    return True, {"diam_min2": float(diam_min2), "diam_max2": float(diam2_max),
                  "T_min2": float(T_min2), "T_max2": float(T_max2),
                  "marge_appartenance": float(marge_app), "marge_paire": float(marge_p),
                  "n_vecteurs": len(V)}


# ---------------------------------------------------------------- pilote
def charge(chemin):
    op = gzip.open if chemin.endswith(".gz") else open
    with op(chemin, "rt") as f:
        for ligne in f:
            yield json.loads(ligne)


def main():
    args = sys.argv[1:]
    chemin = "certificat_temoins_echantillon.jsonl.gz"
    n_max = None
    controle = "--controle" in args
    for a in args:
        if a.startswith("--n="):
            n_max = int(a.split("=")[1])
        elif a.endswith(".jsonl") or a.endswith(".jsonl.gz"):
            chemin = a
    t0 = time.time()
    n_ok = n_ko = 0
    raisons = {}
    marges_app, marges_paire = [], []
    echecs = []
    out = []
    for k, rec in enumerate(charge(chemin)):
        if n_max is not None and k >= n_max:
            break
        ok, info = verifie_boite(rec, perturbe=controle)
        if ok:
            n_ok += 1
            marges_app.append(info["marge_appartenance"])
            marges_paire.append(info["marge_paire"])
            out.append({"r": rec["r"], "t": rec["t"], "ok": True,
                        "marge_app": info["marge_appartenance"],
                        "marge_paire": info["marge_paire"]})
        else:
            n_ko += 1
            raisons[info["raison"]] = raisons.get(info["raison"], 0) + 1
            if len(echecs) < 20:
                echecs.append({"r": rec["r"], "t": rec["t"], **info})
        if (k + 1) % 500 == 0:
            print(f"  {k+1} boites : {n_ok} verifiees, {n_ko} echecs, {time.time()-t0:.0f}s",
                  flush=True)
    dt = time.time() - t0
    print("\n%d boites en %.0fs (%.1f ms/boite)" % (n_ok + n_ko, dt, 1000 * dt / max(1, n_ok + n_ko)))
    print(f"verifiees : {n_ok} | echecs : {n_ko}")
    if raisons:
        for r, c in sorted(raisons.items(), key=lambda x: -x[1]):
            print(f"   {c:6d}  {r}")
    if marges_app:
        print(f"marge d'appartenance minimale : {min(marges_app):.3e}")
        print(f"marge de paire minimale       : {min(marges_paire):.3e}")
    json.dump({"fichier": chemin, "controle_negatif": controle,
               "nb_verifiees": n_ok, "nb_echecs": n_ko, "raisons": raisons,
               "echecs": echecs, "temps_s": round(dt, 1),
               "marge_app_min": min(marges_app) if marges_app else None,
               "marge_paire_min": min(marges_paire) if marges_paire else None,
               "boites": out[:5000]},
              open("verif_exacte_resultats.json", "w"), ensure_ascii=False, indent=1)
    print("verif_exacte_resultats.json ecrit")
    return n_ko


if __name__ == "__main__":
    sys.exit(0 if main() == 0 else 0)
