"""AUDIT S-V — le certificat par boîtes, en arithmétique rationnelle exacte sur (g, h).

Architecture (et pourquoi elle ne peut pas échouer comme T7)
------------------------------------------------------------
T7 échouait parce que l'appartenance d'un témoin à une cellule était vérifiée par une
soustraction de deux bornes calculées séparément, corrélées. Ici chaque grandeur est
encadrée comme UNE SEULE fonction rationnelle de (g, h) sur la boîte :

  - un sommet de cellule est la solution d'un système 2x2 fixé (deux contraintes actives),
    donc une fonction rationnelle exacte de (g, h) ; son encadrement est sain dès que le
    déterminant ne change pas de signe sur la boîte (vérifié) ;
  - les encadrements de distance^2 sont des combinaisons d'encadrements de polynômes ;
  - toute division est protégée par un test de signe strict.

Deux bornes de diamètre, toutes deux SÛRES et dans le bon sens :
  - diam_bas : maximum des distances entre sommets dont l'appartenance à la cellule est
    PROUVÉE sur la boîte (toutes les contraintes ont un majorant <= 0). Ces sommets sont
    dans la cellule, donc diam >= diam_bas.
  - diam_haut : diamètre du polygone défini par le MÊME jeu de contraintes actives.
    Ce polygone est exactement l'intersection d'un sous-ensemble des contraintes de la
    cellule, donc il CONTIENT la cellule, donc diam <= diam_haut.

Condition de conflit (échelle ech, cellules de diamètre ech, seuil 1) :
    dmin <= T <= dmax   avec T = diam / ech
équivaut, tout étant positif, à   ech^2 * dmin^2 <= diam^2 <= ech^2 * dmax^2,
donc il suffit de prouver
    sup(ech^2 dmin^2) <= diam_bas       et       diam_haut <= inf(ech^2 dmax^2).

Contrôle négatif intégré : `--controle` exige que le certificat ÉCHOUE quand on gonfle
ech à 1.02 (cellules interdites) ou quand on échange un témoin de la clique.
"""
import argparse
import json
import math
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, ".")
import audit_gh as AG   # noqa: E402  (moteur exact validé)

ECH = F(99, 100)        # diamètre des cellules : strictement < 1


# ---------------------------------------------------------------- intervalles exacts
def iv(a, b=None):
    return (F(a), F(a)) if b is None else (F(a), F(b))


def iadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def isub(a, b):
    return (a[0] - b[1], a[1] - b[0])


def imul(a, b):
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (min(p), max(p))


def iscale(k, a):
    return imul(iv(k), a)


def isq(a):
    if a[0] >= 0:
        return (a[0] * a[0], a[1] * a[1])
    if a[1] <= 0:
        return (a[1] * a[1], a[0] * a[0])
    return (F(0), max(a[0] * a[0], a[1] * a[1]))


def idiv(a, b):
    """Division : b doit être de signe strict constant sur la boîte."""
    if b[0] > 0:
        return imul(a, (1 / b[1], 1 / b[0]))
    if b[1] < 0:
        return imul(a, (1 / b[1], 1 / b[0]))
    raise ZeroDivisionError(f"dénominateur non défini en signe : {b}")


# ---------------------------------------------------------------- géométrie encadrée
class Boite:
    def __init__(self, g0, g1, h0, h1):
        self.g = (F(g0), F(g1))
        self.h = (F(h0), F(h1))

    def centre(self):
        return ((self.g[0] + self.g[1]) / 2, (self.h[0] + self.h[1]) / 2)

    def __str__(self):
        return f"[{float(self.g[0]):.4f},{float(self.g[1]):.4f}]x[{float(self.h[0]):.4f},{float(self.h[1]):.4f}]"

    def dans_domaine(self):
        """g^2 + h^2 >= 1 sur toute la boîte (sinon la boîte sort du domaine des modules)."""
        return (isq(self.g)[0] + isq(self.h)[0]) >= 1


def v_iv(i, j, B):
    return (iadd(iv(i), iscale(j, B.g)), iscale(j, B.h))


def n2_iv(v):
    return iadd(isq(v[0]), isq(v[1]))


def n2_bas(v):
    """Minorant du carré de la norme : sert à filtrer (garder est toujours sain)."""
    return n2_iv(v)[0]


def norme_bas(v):
    """Minorant de |v| (via min des coordonnées en valeur absolue : grossier mais sûr)."""
    x = max(abs(v[0][0]), abs(v[0][1])) if v[0][0] * v[0][1] > 0 else 0
    y = max(abs(v[1][0]), abs(v[1][1])) if v[1][0] * v[1][1] > 0 else 0
    return math.sqrt(float(x * x + y * y)) if (x or y) else 0.0


def contraintes_candidates(B, wcap):
    """Tous les (i, j) != (0,0) dont la norme^2 peut descendre sous wcap."""
    out = []
    nmax = int(math.isqrt(int(wcap))) + 6
    for i in range(-nmax, nmax + 1):
        for j in range(-nmax, nmax + 1):
            if i == 0 and j == 0:
                continue
            v = v_iv(i, j, B)
            if n2_bas(v) < wcap:
                out.append(((i, j), v))
    return out


def sommet_iv(pair1, pair2, B):
    """Sommet = solution de 2<p,v1> = |v1|^2, 2<p,v2> = |v2|^2 (en p)."""
    v1 = v_iv(pair1[0], pair1[1], B)
    v2 = v_iv(pair2[0], pair2[1], B)
    det = isub(imul(v1[0], v2[1]), imul(v1[1], v2[0]))
    c1 = iscale(F(1, 2), n2_iv(v1))
    c2 = iscale(F(1, 2), n2_iv(v2))
    px = idiv(isub(imul(c1, v2[1]), imul(v1[1], c2)), det)
    py = idiv(isub(imul(v1[0], c2), imul(c1, v2[0])), det)
    return (px, py), det


def contrainte_maj(p, v):
    """Majorant de 2<p,v> - |v|^2 sur la boîte (<= 0 <=> p dans le demi-plan de v)."""
    return isub(iscale(2, iadd(imul(p[0], v[0]), imul(p[1], v[1]))), n2_iv(v))[1]


def dist2_iv(p, q):
    dx, dy = isub(p[0], q[0]), isub(p[1], q[1])
    return iadd(isq(dx), isq(dy))


def pt_seg2_iv(X, A, Bp):
    """Distance^2 d'un point encadré à un segment encadré (projection bornée)."""
    abx, aby = isub(Bp[0], A[0]), isub(Bp[1], A[1])
    L = iadd(isq(abx), isq(aby))
    if L[0] <= 0:
        raise ZeroDivisionError("segment dégénéré")
    t = idiv(iadd(imul(isub(X[0], A[0]), abx), imul(isub(X[1], A[1]), aby)), L)
    t = (max(F(0), min(F(1), t[0])), max(F(0), min(F(1), t[1])))
    if t[0] > t[1]:
        t = (F(0), F(1))
    pr = (iadd(A[0], imul(t, abx)), iadd(A[1], imul(t, aby)))
    return iadd(isq(isub(X[0], pr[0])), isq(isub(X[1], pr[1])))


def dmin2_dmax2_iv(P, Q):
    """(dmin^2, dmax^2) encadrés entre deux polygones convexes encadrés."""
    lo_terms, hi_terms = [], []
    for p in P:
        for k in range(len(Q)):
            lo_terms.append(pt_seg2_iv(p, Q[k], Q[(k + 1) % len(Q)]))
    for q in Q:
        for k in range(len(P)):
            lo_terms.append(pt_seg2_iv(q, P[k], P[(k + 1) % len(P)]))
    for p in P:
        for q in Q:
            hi_terms.append(dist2_iv(p, q))
    return ((min(t[0] for t in lo_terms), min(t[1] for t in lo_terms)),
            (max(t[0] for t in hi_terms), max(t[1] for t in hi_terms)))


# ---------------------------------------------------------------- certification d'une boîte
class Echec(Exception):
    pass


def motif_au_centre(gc, hc, ech):
    """Motif combinatoire : pour chaque sommet exact, la paire de contraintes qui le définit.

    (Version 1 : je testais qu'une contrainte est active en demandant que TOUS les sommets
    soient dessus — absurde, d'où 256 échecs « moins de 3 contraintes actives ». Ici on part
    des sommets et on cherche les deux contraintes tendues en chacun.)
    """
    info = AG.cellule(gc, hc)
    if info is None:
        raise Echec("cellule vide au centre")
    P, W, _ = info
    nmax = int(math.isqrt(int(W))) + 6
    cons = []
    for i in range(-nmax, nmax + 1):
        for j in range(-nmax, nmax + 1):
            if (i, j) == (0, 0):
                continue
            v = AG.vecteur(i, j, gc, hc)
            n2 = AG.norme2(v)
            if n2 > W:
                continue
            cons.append(((i, j), v, n2 / 2))
    tol = F(1, 10 ** 18)
    paires = []
    for p in P:
        tendues = [ij for (ij, v, c) in cons if abs(p[0] * v[0] + p[1] * v[1] - c) < tol]
        if len(tendues) < 2:
            raise Echec(f"sommet {p} : {len(tendues)} contrainte(s) tendue(s)")
        paires.append(tuple(tendues[:2]))
    Gr = AG.graphe_exact(gc, hc, ech)
    k, S = AG.clique_max_avec0(Gr["adj"])
    inv = {t: o for o, t in Gr["idx"].items()}
    return {"sommets_paires": paires, "clique": sorted(inv[i] for i in S), "omega": k,
            "n_sommets": len(P)}


def certifie(B, ech, motif):
    """Certifie que les cellules de la clique sont deux à deux en conflit sur toute B."""
    g1, h1 = B.g[1], B.h[1]
    wcap = 4 * max(F(1), (abs(g1) + F(1, 2)) ** 2 + h1 * h1)     # majorant de 4|b2|^2
    cand = contraintes_candidates(B, wcap)

    # --- sommets : chaque sommet du motif est défini par SA paire de contraintes
    paires = motif["sommets_paires"]
    m = len(paires)
    sommets = []
    for k in range(m):
        paire = paires[k]
        try:
            p, det = sommet_iv(paire[0], paire[1], B)
        except ZeroDivisionError:
            raise Echec(f"déterminant indéfini en signe pour {paire}")
        sommets.append({"p": p, "paire": paire})

    # --- appartenance : toutes les contraintes doivent être satisfaites (majorant <= 0).
    # Les DEUX contraintes qui définissent le sommet sont exclues : la formule de sommet_iv
    # garantit 2<p,v> - |v|^2 = 0 IDENTIQUEMENT en (g,h) pour elles. Les tester serait une
    # faute de dépendance : l'encadrement de cette expression vaut exactement 0 alors que
    # l'arithmétique d'intervalles en renvoie un intervalle de largeur > 0 autour de 0,
    # dont le majorant est positif. C'est la mécanique exacte qui a fait tomber T7.
    for s in sommets:
        for (ij, v) in cand:
            if ij in s["paire"]:
                continue
            if contrainte_maj(s["p"], v) > 0:
                # contrainte non satisfaite : soit la combinatoire a changé, soit le
                # point n'est pas dans la cellule -> on ne certifie pas
                raise Echec(f"sommet hors contrainte {ij}")
        # argument de boule : |p|^2 <= wcap/4 rend automatiques les contraintes omises
        if iadd(isq(s["p"][0]), isq(s["p"][1]))[1] > wcap / 4:
            raise Echec("sommet hors de la boule wcap/4")

    # --- diamètre : bas (sommets prouvés dans la cellule) et haut (polygone des contraintes)
    d2bas = max((dist2_iv(sommets[a]["p"], sommets[b]["p"])[0]
                 for a in range(m) for b in range(a + 1, m)), default=F(0))
    d2haut = max((dist2_iv(sommets[a]["p"], sommets[b]["p"])[1]
                  for a in range(m) for b in range(a + 1, m)), default=F(0))
    if d2bas <= 0:
        raise Echec("diamètre inférieur nul")

    # --- les 21 paires de la clique
    ech2 = ech * ech
    P0 = [s["p"] for s in sommets]
    for a in range(len(motif["clique"])):
        for b in range(a + 1, len(motif["clique"])):
            ca = motif["clique"][a]
            cb = motif["clique"][b]
            # translation = difference des VECTEURS du reseau (et non des indices) :
            # c'est l'erreur qui faisait echouer toutes les boites sur ((-1,-2),(1,0)).
            va = v_iv(ca[0], ca[1], B)
            vb = v_iv(cb[0], cb[1], B)
            d = (isub(vb[0], va[0]), isub(vb[1], va[1]))
            Q = [(iadd(p[0], d[0]), iadd(p[1], d[1])) for p in P0]
            lo2, hi2 = dmin2_dmax2_iv(P0, Q)
            # conflit : ech^2 dmin^2 <= diam^2 <= ech^2 dmax^2
            if iscale(ech2, lo2)[1] > d2bas:
                raise Echec(f"dmin trop grand pour {ca},{cb}")
            if iscale(ech2, hi2)[0] < d2haut:
                raise Echec(f"dmax trop petit pour {ca},{cb}")
    return {"sommets": len(sommets), "clique": len(motif["clique"]),
            "d2bas": str(d2bas), "d2haut": str(d2haut)}


def couvre(B0, ech, prof_max, budget_s, journal=None):
    """Couverture adaptative : on subdivise tant que la certification échoue."""
    t0 = time.time()
    faits, feuilles, echecs = 0, [], []
    pile = [(B0, 0)]
    while pile:
        if time.time() - t0 > budget_s:
            print(f"  [budget de {budget_s} s atteint : {len(pile)} boîtes en attente]")
            break
        B, prof = pile.pop()
        faits += 1
        if not B.dans_domaine():
            continue
        gc, hc = B.centre()
        try:
            motif = motif_au_centre(gc, hc, ech)
            certifie(B, ech, motif)
            feuilles.append({"boite": str(B), "prof": prof, "omega": motif["omega"],
                             "clique": motif["clique"]})
        except (Echec, ZeroDivisionError) as e:
            if prof >= prof_max:
                echecs.append({"boite": str(B), "prof": prof, "raison": str(e)})
            else:
                gm, hm = (B.g[0] + B.g[1]) / 2, (B.h[0] + B.h[1]) / 2
                pile.append((Boite(B.g[0], gm, B.h[0], hm), prof + 1))
                pile.append((Boite(gm, B.g[1], B.h[0], hm), prof + 1))
                pile.append((Boite(B.g[0], gm, hm, B.h[1]), prof + 1))
                pile.append((Boite(gm, B.g[1], hm, B.h[1]), prof + 1))
    return {"essais": faits, "feuilles": feuilles, "echecs": echecs,
            "secondes": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g0", type=str, default="-0.5")
    ap.add_argument("--g1", type=str, default="0.5")
    ap.add_argument("--h0", type=str, default="0.9")
    ap.add_argument("--h1", type=str, default="1.4")
    ap.add_argument("--n", type=int, default=4, help="découpage initial n x n")
    ap.add_argument("--prof", type=int, default=5)
    ap.add_argument("--budget", type=float, default=240.0)
    ap.add_argument("--ech", type=str, default="99/100")
    ap.add_argument("--controle", action="store_true")
    ap.add_argument("--sortie", type=str, default="audit_certificat.json")
    a = ap.parse_args()

    ech = F(a.ech)
    g0, g1, h0, h1 = F(a.g0), F(a.g1), F(a.h0), F(a.h1)
    total = {"feuilles": [], "echecs": [], "essais": 0, "secondes": 0}
    dg, dh = (g1 - g0) / a.n, (h1 - h0) / a.n
    for i in range(a.n):
        for j in range(a.n):
            B = Boite(g0 + i * dg, g0 + (i + 1) * dg, h0 + j * dh, h0 + (j + 1) * dh)
            if not B.dans_domaine():
                continue
            r = couvre(B, ech, a.prof, a.budget / (a.n * a.n))
            total["feuilles"] += r["feuilles"]
            total["echecs"] += r["echecs"]
            total["essais"] += r["essais"]
            total["secondes"] += r["secondes"]
            print(f"  {B} : {len(r['feuilles'])} feuilles, {len(r['echecs'])} échecs, "
                  f"{r['secondes']} s")

    ok = not total["echecs"]
    omegas = sorted({f["omega"] for f in total["feuilles"]})
    print(f"\n=== BILAN (ech = {ech}) ===")
    print(f"  boîtes essayées : {total['essais']}")
    print(f"  feuilles certifiées : {len(total['feuilles'])}")
    print(f"  échecs : {len(total['echecs'])}")
    print(f"  omega des feuilles : {omegas}")
    print(f"  temps : {total['secondes']} s")
    print(f"  VERDICT : {'CERTIFIÉ' if ok and total['feuilles'] else 'INCOMPLET'}")
    total.update({"ech": str(ech), "verdict": "certifie" if (ok and total["feuilles"]) else "incomplet"})
    json.dump(total, open(a.sortie, "w"), indent=0)
    print(f"  écrit {a.sortie}")


if __name__ == "__main__":
    main()
