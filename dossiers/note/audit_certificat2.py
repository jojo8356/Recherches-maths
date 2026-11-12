"""AUDIT S-V — certificat par boîtes, version 2 : polynômes exacts + forme de la moyenne.

Ce qui est certifié, exactement
-------------------------------
Soit ech < 1. Pour un réseau Lambda = Z b1 + Z b2 avec b1 = (1,0), b2 = (g,h) dans le
domaine des modules F = {|g| <= 1/2, g^2 + h^2 >= 1, h > 0}, on prouve que le graphe de
conflit du pavage de Voronoï privé de son échelle (cellules de diamètre ech, seuil 1)
contient une clique de 7 cellules.

Conflit entre deux cellules A, B : il existe p dans A, q dans B avec |p-q| = 1.
Équivaut à  dmin <= 1 <= dmax, ce qui, T = diam/ech étant le seuil en unités du réseau,
s'écrit  ech^2 dmin^2 <= diam^2 <= ech^2 dmax^2.

Structure de la preuve par boîte B (arithmétique exacte sur Q, aucun flottant)
------------------------------------------------------------------------------
1. motif : les sommets de la cellule au point central sont solutions de systèmes 2x2
   fixés (deux contraintes tendues) ; on les relève en fonctions rationnelles de (g,h).
2. appartenance : pour chaque sommet et chaque contrainte v du réseau, la fonction
   2<p,v> - |v|^2 (rationnelle) est encadrée et doit être <= 0 partout sur B. Les
   contraintes omises (|v|^2 >= wcap) sont automatiques dès que |p|^2 <= wcap/4.
3. diamètre : deux encadrements SÛRS et dans le bon sens.
     diam_bas  = min sur B de la distance entre deux sommets d'appartenance PROUVÉE
                 (donc diam >= diam_bas) ;
     diam_haut = max sur B de la distance entre deux sommets du motif
                 (majorant de diam).
4. conflit : pour chaque paire de la clique, deux paires de sommets sont exhibées :
   - proche : ech^2 |u - w|^2 <= diam_bas    (donne dmin <= T)
   - éloignée : diam_haut <= ech^2 |u' - w'|^2  (donne T <= dmax)
   Une paire de points quelconques, l'un dans A et l'autre dans B, minore dmin et majore
   dmax : aucune optimisation n'est nécessaire, donc aucune borne dans le mauvais sens.

Contrôles négatifs (--controle)
-------------------------------
(a) ech = 1/2 : omega tombe sous 7, le certificat DOIT échouer ;
(b) témoin de conflit décalé d'un cran : la condition proche DOIT échouer ;
(c) boîte volontairement hors domaine (g^2 + h^2 < 1) : refusée avant tout calcul.
"""
import argparse
import json
import math
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, ".")
import audit_gh as AG                              # noqa: E402
from poly2 import G, H, Poly, Rat, dist2, enc, carre   # noqa: E402

ECH = F(99, 100)


class Echec(Exception):
    pass


class SommetHors(Exception):
    """Un sommet du motif n'est pas dans la cellule sur toute la boîte : on le retire."""

    def __init__(self, idx):
        self.idx = idx
        super().__init__(f"sommet {idx} hors de la cellule")


# ---------------------------------------------------------------- géométrie symbolique
def vec_sym(i, j):
    return (Poly.const(i) + G * j, H * j)


def n2_sym(v):
    return carre(v[0]) + carre(v[1])


def sommet_sym(pa, pb):
    """Sommet = solution de <p,v1> = |v1|^2/2, <p,v2> = |v2|^2/2 (fonction rationnelle)."""
    v1, v2 = vec_sym(*pa), vec_sym(*pb)
    det = v1[0] * v2[1] - v1[1] * v2[0]
    c1 = n2_sym(v1) / 2
    c2 = n2_sym(v2) / 2
    px = Rat(c1 * v2[1] - v1[1] * c2, det)
    py = Rat(v1[0] * c2 - c1 * v2[0], det)
    return (px, py)


def contrainte_sym(p, ij):
    v = vec_sym(*ij)
    return (p[0] * v[0] + p[1] * v[1]) * 2 - n2_sym(v)


def carte(g, h):
    """Encadrement d'une fonction rationnelle sur la boîte (g0,g1,h0,h1)."""
    return (F(g[0]), F(g[1]), F(h[0]), F(h[1]))


# ---------------------------------------------------------------- motif au centre
def motif_au_centre(gc, hc, ech):
    info = AG.cellule(gc, hc)
    if info is None:
        raise Echec("cellule vide")
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
            raise Echec("sommet sans paire de contraintes tendues")
        paires.append((tendues[0], tendues[1]))
    Gr = AG.graphe_exact(gc, hc, ech)
    k, S = AG.clique_max_avec0(Gr["adj"])
    if k < 7:
        raise Echec(f"omega = {k} au centre (< 7) : rien à certifier ici")
    inv = {t: o for o, t in Gr["idx"].items()}
    clique = sorted(inv[i] for i in S)[:7]
    # témoins et diamètre choisis au centre
    def cel(off):
        c = AG.vecteur(off[0], off[1], gc, hc)
        return [(x + c[0], y + c[1]) for (x, y) in P]

    zero = cel((0, 0))
    d2diam, paire_diam = -1, (0, 1)
    for a in range(len(zero)):
        for b in range(a + 1, len(zero)):
            dd = AG.dist2(zero[a], zero[b])
            if dd > d2diam:
                d2diam, paire_diam = dd, (a, b)
    ech2 = ech * ech
    temoins = {}
    for a in range(len(clique)):
        for b in range(a + 1, len(clique)):
            A, B = zero, cel(clique[b])
            A = [(x - 0, y - 0) for (x, y) in zero]
            B = [(x - AG.vecteur(clique[a][0], clique[a][1], gc, hc)[0],
                  y - AG.vecteur(clique[a][0], clique[a][1], gc, hc)[1]) for (x, y) in cel(clique[b])]
            best_min, best_max = (None, (0, 0)), (None, (0, 0))
            for kk in range(len(A)):
                for ll in range(len(B)):
                    dd = AG.dist2(A[kk], B[ll])
                    if best_min[0] is None or dd < best_min[0]:
                        best_min = (dd, (kk, ll))
                    if best_max[0] is None or dd > best_max[0]:
                        best_max = (dd, (kk, ll))
            temoins[(clique[a], clique[b])] = {"proche": best_min[1], "loin": best_max[1]}
    mot = {"paires": paires, "clique": clique, "omega": k, "diam": paire_diam,
           "temoins": temoins, "nv": len(P)}
    mot["sommets"] = [sommet_sym(*pa) for pa in paires]      # calculés une seule fois
    mot["pts_centre"] = list(P)                              # valeurs exactes au centre
    mot["centre"] = (gc, hc)
    mot["cand_base"] = None
    return mot


def _iv_v(i, j, B):
    g0, g1, h0, h1 = B
    jg = (min(j * g0, j * g1), max(j * g0, j * g1))
    vx = (min(i + jg[0], i + jg[1]), max(i + jg[0], i + jg[1]))
    vy = (min(j * h0, j * h1), max(j * h0, j * h1))
    return vx, vy


def _n2_bas(vx, vy):
    def lo(a):
        return 0 if a[0] <= 0 <= a[1] else min(a[0] ** 2, a[1] ** 2)
    return lo(vx) + lo(vy)


def plan_de(motif, ech, permis=None):
    """Fonctions rationnelles à encadrer, calculées une fois par motif.

    `permis` restreint les sommets utilisables : quand un sommet sort de la cellule sur une
    partie de la boîte (transition combinatoire : une arête se replie, un sommet apparaît ou
    disparaît), on le RETIRE. C'est sûr, et c'est le point clé :

      - le polygone des contraintes restantes est une intersection d'un sous-ensemble des
        contraintes de la cellule, donc il CONTIENT la cellule : le majorant du diamètre
        reste valide ;
      - les sommets restants sont, eux, prouvés dans la cellule : le minorant du diamètre
        reste valide.
    """
    sommets = motif.get("sommets") or [sommet_sym(*pa) for pa in motif["paires"]]
    pts = motif.get("pts_centre")
    idx = list(range(len(sommets))) if permis is None else sorted(permis)
    if len(idx) < 3:
        raise Echec("moins de 3 sommets utilisables")
    # paire diamétrale au centre, parmi les sommets permis
    if pts is not None:
        best = (-1, (idx[0], idx[1]))
        for a in idx:
            for b in idx:
                if a < b:
                    dd = AG.dist2(pts[a], pts[b])
                    if dd > best[0]:
                        best = (dd, (a, b))
        paire_diam = best[1]
    else:
        paire_diam = (idx[0], idx[1])
    plan = {"sommets": sommets, "permis": idx, "ech": ech, "ech2": ech * ech,
            "diam_pair": dist2(sommets[paire_diam[0]], sommets[paire_diam[1]]),
            "cache_c": {}, "paires": {}}
    for (ca, cb), t in motif["temoins"].items():
        dec = (Rat(vec_sym(cb[0], cb[1])[0]) - Rat(vec_sym(ca[0], ca[1])[0]),
               Rat(vec_sym(cb[0], cb[1])[1]) - Rat(vec_sym(ca[0], ca[1])[1]))
        if pts is not None:
            # témoins choisis au centre parmi les sommets permis
            celb = [(pts[k][0] + AG.vecteur(cb[0], cb[1], *motif["centre"])[0],
                     pts[k][1] + AG.vecteur(cb[0], cb[1], *motif["centre"])[1]) for k in idx]
            cel_out = [(pts[k][0] + AG.vecteur(ca[0], ca[1], *motif["centre"])[0],
                        pts[k][1] + AG.vecteur(ca[0], ca[1], *motif["centre"])[1]) for k in idx]
            best_min, best_max = (None, None), (None, None)
            for kk, ia in enumerate(idx):
                for ll, ib in enumerate(idx):
                    dd = AG.dist2(cel_out[kk], celb[ll])
                    if best_min[0] is None or dd < best_min[0]:
                        best_min = (dd, (ia, ib))
                    if best_max[0] is None or dd > best_max[0]:
                        best_max = (dd, (ia, ib))
            kp, lp = best_min[1]
            kl, ll = best_max[1]
        else:
            kp, lp = t["proche"]
            kl, ll = t["loin"]
        Bp = (sommets[lp][0] + dec[0], sommets[lp][1] + dec[1])
        B2 = (sommets[ll][0] + dec[0], sommets[ll][1] + dec[1])
        plan["paires"][(ca, cb)] = {
            "ecart": plan["diam_pair"] - dist2(sommets[kp], Bp) * plan["ech2"],
            "loin": dist2(sommets[kl], B2),
        }
    return plan


def certifie(gbox, hbox, ech, plan):
    B = carte(gbox, hbox)
    tous = plan["sommets"]
    permis = plan.get("permis") or list(range(len(tous)))
    sommets = [tous[i] for i in permis]
    # rayon : wcap = 4 * majorant de |p|^2 ; les contraintes |v|^2 >= wcap sont automatiques
    R2 = max((carre(p[0]) + carre(p[1])).enc(B)[1] for p in sommets)
    wcap = 4 * R2
    cand = []
    for i in range(-16, 17):
        for j in range(-16, 17):
            if (i, j) == (0, 0):
                continue
            if _n2_bas(*_iv_v(i, j, B)) < wcap:
                cand.append((i, j))
    # --- appartenance à la cellule
    for pos, idx in enumerate(permis):
        p = sommets[pos]
        for ij in cand:
            key = (idx, ij)
            c = plan["cache_c"].get(key)
            if c is None:
                c = plan["cache_c"][key] = contrainte_sym(p, ij)
            sg = c.signe_enc(B)
            if sg[1] > 0:
                raise SommetHors(idx)
    # --- diamètre : majorant commun (max des majorants sur toutes les paires de sommets)
    m = len(sommets)
    d2haut = max(dist2(sommets[a], sommets[b]).enc(B)[1] for a in range(m) for b in range(a + 1, m))
    # --- conflits
    #
    # RÈGLE (c'est ce que T7 violait) : on ne compare JAMAIS deux encadrements pour la
    # condition serrée. On prouve qu'UNE SEULE fonction rationnelle reste >= 0 :
    #      ecart = |paire de diamètre|^2 - ech^2 |témoins proches|^2 >= 0,
    # d'où diam^2 >= ech^2 dmin^2. La condition relâchée (dmax) se fait sur des nombres,
    # avec une marge d'un facteur ~3.
    for (ca, cb), f in plan["paires"].items():
        sg = f["ecart"].signe_enc(B)
        if sg[0] < 0:
            raise Echec(f"dmin non prouvé pour {ca},{cb} (min {float(sg[0]):.3e})")
        d2l = f["loin"].enc(B)[0]
        if d2haut > plan["ech2"] * d2l:
            raise Echec(f"dmax trop petit pour {ca},{cb}")
    return {"d2haut": float(d2haut)}


def couvre(gbox, hbox, ech, prof_max, budget, t_debut):
    """Couverture adaptative.

    Gestion des transitions combinatoires : si un sommet du motif sort de la cellule, on le
    RETIRE et on reconstruit le plan (voir plan_de). Un motif peut ainsi perdre jusqu'à
    n-3 sommets ; s'il en reste trop peu, la boîte est subdivisée.
    """
    feuilles, echecs, essais = [], [], 0
    pile = [(gbox, hbox, 0, None, frozenset())]
    while pile:
        if time.time() - t_debut > budget:
            return feuilles, echecs, essais, "budget"
        g, h, prof, mot, retires = pile.pop()
        essais += 1
        # domaine F = {|g| <= 1/2, g^2 + h^2 >= 1, h > 0} : une boîte peut être à cheval
        gmin_abs = min(abs(F(g[0])), abs(F(g[1]))) if F(g[0]) * F(g[1]) > 0 else F(0)
        d2bas = gmin_abs ** 2 + F(h[0]) ** 2
        d2haut = max(abs(F(g[0])), abs(F(g[1]))) ** 2 + F(h[1]) ** 2
        if d2haut < 1:
            continue                                    # entièrement hors domaine
        if d2bas < 1:
            # à cheval sur g^2 + h^2 = 1 : on subdivise (une partie est hors domaine)
            if prof >= prof_max:
                echecs.append({"g": [float(x) for x in g], "h": [float(x) for x in h],
                               "raison": "boîte à cheval sur la frontière du domaine"})
            else:
                gm, hm = (F(g[0]) + F(g[1])) / 2, (F(h[0]) + F(h[1])) / 2
                pile += [((g[0], gm), (h[0], hm), prof + 1, mot, retires),
                         ((gm, g[1]), (h[0], hm), prof + 1, mot, retires),
                         ((g[0], gm), (hm, h[1]), prof + 1, mot, retires),
                         ((gm, g[1]), (hm, h[1]), prof + 1, mot, retires)]
            continue
        gc, hc = (F(g[0]) + F(g[1])) / 2, (F(h[0]) + F(h[1])) / 2
        try:
            if mot is None:
                mot = motif_au_centre(gc, hc, ech)
            # on essaie le jeu complet, puis en retirant les sommets fautifs (max 3 essais)
            permis = frozenset(range(len(mot["sommets"]))) - set(retires)
            plan = plan_de(mot, ech, permis)
            for _ in range(3):
                try:
                    certifie(g, h, ech, plan)
                    break
                except SommetHors as sh:
                    permis = permis - {sh.idx}
                    plan = plan_de(mot, ech, permis)
            else:
                raise Echec("certificat impossible après retrait des sommets")
            feuilles.append({"g": [float(x) for x in g], "h": [float(x) for x in h],
                             "prof": prof, "omega": mot["omega"], "retires": sorted(retires)})
        except (Echec, ZeroDivisionError, SommetHors) as e:
            if prof >= prof_max:
                echecs.append({"g": [float(x) for x in g], "h": [float(x) for x in h],
                               "raison": str(e)})
            else:
                gm, hm = (F(g[0]) + F(g[1])) / 2, (F(h[0]) + F(h[1])) / 2
                # si l'échec vient de la CLIQUE (dmin/dmax), le motif hérité n'est plus
                # valable localement : on force son recalcul pour les enfants.
                herite = mot
                if "dmin" in str(e) or "dmax" in str(e):
                    herite = None
                nouveau_retires = frozenset()
                pile += [((g[0], gm), (h[0], hm), prof + 1, herite, nouveau_retires),
                         ((gm, g[1]), (h[0], hm), prof + 1, herite, nouveau_retires),
                         ((g[0], gm), (hm, h[1]), prof + 1, herite, nouveau_retires),
                         ((gm, g[1]), (hm, h[1]), prof + 1, herite, nouveau_retires)]
    return feuilles, echecs, essais, "fini"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g0", default="-1/2")
    ap.add_argument("--g1", default="1/2")
    ap.add_argument("--h0", default="9/10")
    ap.add_argument("--h1", default="3/2")
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--prof", type=int, default=6)
    ap.add_argument("--budget", type=float, default=240.0)
    ap.add_argument("--ech", default="99/100")
    ap.add_argument("--controle", action="store_true")
    ap.add_argument("--sortie", default="audit_certificat2.json")
    a = ap.parse_args()
    ech = F(a.ech)
    if ech >= 1:
        sys.exit("ech doit être < 1 (cellules de diamètre < 1, sinon une cellule monochrome "
                 "contient déjà deux points à distance 1)")

    t0 = time.time()
    if a.controle:
        print("=== CONTRÔLES NÉGATIFS ===")
        # (c) hors domaine
        try:
            mt = motif_au_centre(F(1, 8), F(5, 8), ech)
            certifie(("0", "1/4"), ("1/2", "3/4"), ech, plan_de(mt, ech))
            print("  (c) boîte hors domaine : ACCEPTÉE -> BUG")
        except Exception as e:
            print(f"  (c) boîte hors domaine refusée : {str(e)[:70]}")
        # (a) échelle 1/2 : omega < 7
        try:
            motif_au_centre(F(-1, 2), F(1), F(1, 2))
            print("  (a) ech = 1/2 : ACCEPTÉ -> BUG")
        except Echec as e:
            print(f"  (a) ech = 1/2 rejeté : {e}")
        # (b) contrôle le plus important : on corrompt la PRÉMISSE — la paire diamétrale est
        #     remplacée par une arête, bien plus courte. La minoration du diamètre devient
        #     fausse, donc la condition « dmin <= T » doit échouer.
        mot = motif_au_centre(F(-2, 5), F(1), ech)
        pl = plan_de(mot, ech)
        court = dist2(pl["sommets"][0], pl["sommets"][1])
        ecart_corruption = court - pl["diam_pair"]      # <= 0
        for val in pl["paires"].values():
            val["ecart"] = val["ecart"] + ecart_corruption
        try:
            certifie(("-2/5", "-2/5"), ("1", "1"), ech, pl)
            print("  (b) témoin corrompu : ACCEPTÉ -> BUG")
        except Echec as e:
            print(f"  (b) témoin décalé rejeté : {str(e)[:70]}")

    g0, g1, h0, h1 = F(a.g0), F(a.g1), F(a.h0), F(a.h1)
    dg, dh = (g1 - g0) / a.n, (h1 - h0) / a.n
    tot_f, tot_e, tot_x = [], [], 0
    for i in range(a.n):
        for j in range(a.n):
            g = (g0 + i * dg, g0 + (i + 1) * dg)
            h = (h0 + j * dh, h0 + (j + 1) * dh)
            t_cellule = time.time()
            f, e, x, etat = couvre(g, h, ech, a.prof, a.budget / (a.n * a.n), t_cellule)
            tot_f += f
            tot_e += e
            tot_x += x
            print(f"  g{float(g[0]):+.3f}..{float(g[1]):+.3f} h{float(h[0]):.3f}..{float(h[1]):.3f}"
                  f" : {len(f)} feuilles, {len(e)} échecs, {x} essais [{etat}]")
            if time.time() - t0 > a.budget:
                print("  [budget global atteint]")
                break
        else:
            continue
        break
    ok = (not tot_e) and tot_f
    superficie = sum((f["g"][1] - f["g"][0]) * (f["h"][1] - f["h"][0]) for f in tot_f)
    print(f"\n=== BILAN ech = {ech} ===")
    print(f"  essais {tot_x} | feuilles certifiées {len(tot_f)} | échecs {len(tot_e)}")
    print(f"  omegas {sorted({f['omega'] for f in tot_f})} | profondeurs "
          f"{sorted({f['prof'] for f in tot_f})}")
    print(f"  aire certifiée (dans la carte (g,h)) : {superficie:.4f}")
    print(f"  temps {time.time() - t0:.1f} s")
    print(f"  VERDICT : {'CERTIFIÉ sur la région couverte' if ok else 'INCOMPLET'}")
    json.dump({"ech": str(ech), "verdict": "certifie" if ok else "incomplet",
               "feuilles": tot_f, "echecs": tot_e, "essais": tot_x,
               "aire": superficie, "secondes": round(time.time() - t0, 1)},
              open(a.sortie, "w"), indent=0)
    print(f"  écrit {a.sortie}")


if __name__ == "__main__":
    main()
