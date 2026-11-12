"""AUDIT S-V — certificat v3 : points témoins robustes aux transitions.

Le problème que la v2 ne savait pas traiter
-------------------------------------------
À g = 0 le réseau est rectangulaire : sa cellule n'a que 4 sommets, et au voisinage aucun
sommet du motif hexagonal n'appartient à la cellule sur toute la boîte (trois contraintes y
deviennent simultanément tendues). Retirer les sommets fautifs ne suffit pas : les six
tombent ensemble. Or g = 0 est une droite du domaine, pas un point isolé.

La sortie : ne pas dépendre des sommets
---------------------------------------
Pour tout vecteur w du réseau tel que  w/2 ∈ V,  le point w/2 est dans la cellule, et sa
condition d'appartenance est POLYNOMIALE, sans division :

    w/2 ∈ V  ⟺  ∀v ∈ Λ,  ⟨w, v⟩ ≤ |v|².

Ces points « milieux de Delaunay » existent pour tout (g,h), y compris dans les cas
dégénérés, et ne disparaissent pas aux transitions. Ils servent de :

  - témoins de conflit (un point dans A, un point dans B, leur distance minore dmin et
    majore... non : minore dmax — voir plus bas) ;
  - minoration du diamètre : diam ≥ distance entre deux points prouvés dans la cellule.

Pour le MAJORANT du diamètre, on n'a besoin de rien de délicat : l'intersection d'un
SOUS-ENSEMBLE des contraintes contient la cellule, donc le parallélogramme
{|⟨p,b₁⟩| ≤ 1/2, |⟨p,b₂⟩| ≤ |b₂|²/2} la contient aussi, et son diamètre est un majorant.
Il est grossier (facteur ~1,4) mais la condition correspondante a une marge d'un facteur 3.

Conditions certifiées
---------------------
  (U)  diam_pair − ε² · |témoins proches|²  ≥ 0     (une seule fonction rationnelle)
  (L)  diam_haut ≤ ε² · |témoins éloignés|²          (nombres, marge ×3)
"""
import argparse
import json
import math
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, ".")
import audit_gh as AG                                        # noqa: E402
from poly2 import G, H, Poly, Rat, carre, dist2, enc           # noqa: E402


def R(x):
    """Ramène un Poly / Rat / Fraction à un Rat (Poly.__sub__ n'accepte pas un Rat)."""
    return x if isinstance(x, Rat) else Rat(x)


def signe_iv(f, B):
    """Encadrement du signe d'une contrainte, qu'elle soit polynôme ou rationnelle."""
    return enc(f, B) if isinstance(f, Poly) else f.signe_enc(B)

ECH = F(99, 100)
FEN = 6          # fenêtre d'indices pour les contraintes


class Echec(Exception):
    pass


class PointHors(Exception):
    """Un point témoin n'est pas dans la cellule sur toute la boîte : on le retire."""

    def __init__(self, k):
        self.k = k
        super().__init__(f"point {k} hors de la cellule")


# ---------------------------------------------------------------- points génériques
# --- repère de travail
# "orig" : base (1,0), (g,h)            — le domaine fondamental, h non borné
# "u"    : base (u,0), (gu,1)           — même réseau divisé par h, avec u = 1/h
# Les critères du certificat sont des RAPPORTS (dmin/D, dmax/D) : un changement d'unité
# uniforme ne les change pas. Le repère "u" a l'avantage d'être BORNÉ : h ≥ 2 devient
# u ∈ (0,1/2], et la queue h → ∞ devient le point u = 0 — une limite fermée, donc
# certifiable, alors qu'une demi-droite ne l'est pas.
MODE = "orig"


def vec_sym(i, j):
    if MODE == "u":
        return (H * (Poly.const(i) + G * j), Poly.const(j))
    return (Poly.const(i) + G * j, H * j)


def n2_sym(v):
    return carre(v[0]) + carre(v[1])


def sommet_sym(pa, pb):
    v1, v2 = vec_sym(*pa), vec_sym(*pb)
    det = v1[0] * v2[1] - v1[1] * v2[0]
    c1, c2 = n2_sym(v1) / 2, n2_sym(v2) / 2
    return (Rat(c1 * v2[1] - v1[1] * c2, det), Rat(v1[0] * c2 - c1 * v2[0], det))


def contrainte(p, ij):
    """2<p,v> − |v|² : ≤ 0 ⟺ p dans le demi-plan de Voronoï de v."""
    v = vec_sym(*ij)
    return (p[0] * v[0] + p[1] * v[1]) * 2 - n2_sym(v)


def milieu(w):
    v = vec_sym(*w)
    return (Rat(v[0] / 2), Rat(v[1] / 2))


def delaunay(w, ij):
    """⟨w,v⟩ − |v|² : ≤ 0 ⟺ w/2 dans le demi-plan de v (condition sans division)."""
    v = vec_sym(*ij)
    u = vec_sym(*w)
    return (u[0] * v[0] + u[1] * v[1]) - n2_sym(v)


# ---------------------------------------------------------------- motif
def _graphe_queue(g, h, ech, nj=2):
    """Graphe de conflit à fenêtre RECTANGULAIRE, pour la queue.

    AG.graphe_exact borne sa fenêtre par isqrt(cible2/norme2(g,h)) + 6, or norme2(g,h) = h² :
    à h = 100 la fenêtre vaut 8 quand les cellules en conflit sont à des décalages d'ordre h.
    Ici la fenêtre suit le seuil : |i| ≤ tau + 2, |j| ≤ nj. Le test de norme, fait avant le
    calcul des distances, élimine presque tout (il ne reste que ~6h paires).

    Les sommets sont indexés par des ENTIERS, comme dans AG.graphe_exact (adj est indexé par
    entier, et "idx" donne l'application décalage -> indice).
    """
    P, W, _ = AG.cellule(g, h)
    diam2 = max(AG.dist2(p, q) for p in P for q in P)
    ech2 = ech * ech
    cible2 = diam2 * (1 / ech + 1) ** 2
    ni = int(math.sqrt(float(cible2))) + 3
    offs = [(i, j) for i in range(-ni, ni + 1) for j in range(-nj, nj + 1)]
    vs = [AG.vecteur(i, j, g, h) for (i, j) in offs]
    adj = {k: set() for k in range(len(offs))}
    for a in range(len(offs)):
        xa, ya = vs[a]
        for b in range(a + 1, len(offs)):
            dx, dy = vs[b][0] - xa, vs[b][1] - ya
            if dx * dx + dy * dy > cible2:
                continue
            Q = [(x + dx, y + dy) for (x, y) in P]
            lo2, hi2 = AG.dmin2_dmax2(P, Q)
            if ech2 * lo2 <= diam2 <= ech2 * hi2:
                adj[a].add(b)
                adj[b].add(a)
    return {"adj": adj, "idx": {o: k for k, o in enumerate(offs)}}


def motif_queue(gc, hc, ech):
    """Comme motif_au_centre, mais avec la fenêtre rectangulaire — utilisable pour h ≫ 1."""
    info = AG.cellule(gc, hc)
    if info is None:
        raise Echec("cellule vide au centre")
    P, W, _ = info
    # |v|² ≤ W = 4h² force |j| ≤ 2 (car |v| ≥ h|j|) et |i| ≤ 2h + 2 : énumération rectangulaire
    ni = int(2 * hc) + 3
    cons = []
    for i in range(-ni, ni + 1):
        for j in range(-2, 3):
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
        ten = [ij for (ij, v, c) in cons if abs(p[0] * v[0] + p[1] * v[1] - c) < tol]
        if len(ten) < 2:
            raise Echec("sommet sans paire tendue")
        paires.append((ten[0], ten[1]))
    Gr = _graphe_queue(gc, hc, ech)
    k, S = AG.clique_max_avec0(Gr["adj"])
    if k < 7:
        raise Echec(f"omega = {k} < 7 au centre (fenêtre large)")
    inv = {t: o for o, t in Gr["idx"].items()}
    clique = sorted(inv[i] for i in S)[:9]
    mids = [(0, 0)]
    for i in range(-3, 4):
        for j in range(-3, 4):
            if (i, j) == (0, 0):
                continue
            wv = AG.vecteur(i, j, gc, hc)
            nw2 = AG.norme2(wv)
            if nw2 == 0:
                continue
            lim = 4 * nw2 + 4
            ci = int(math.isqrt(int(lim))) + 2
            cj = int(math.isqrt(int(lim / (hc * hc)))) + 2 if hc > 0 else 0
            ok = True
            for i2 in range(-ci, ci + 1):
                for j2 in range(-cj, cj + 1):
                    if (i2, j2) == (0, 0):
                        continue
                    vv = AG.vecteur(i2, j2, gc, hc)
                    nv2 = AG.norme2(vv)
                    if nv2 > lim or nv2 == 0:
                        continue
                    if wv[0] * vv[0] + wv[1] * vv[1] - nv2 > 0:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                mids.append((i, j))
    pts_mid = {w: (AG.vecteur(w[0], w[1], gc, hc)[0] / 2,
                   AG.vecteur(w[0], w[1], gc, hc)[1] / 2) for w in mids}
    if len(mids) < 3:
        raise Echec("moins de 3 milieux de Delaunay")
    return {"paires": paires, "clique": clique, "omega": k, "mids": mids,
            "pts_mid": pts_mid, "pts_centre": list(P), "centre": (gc, hc),
            "n_sommets": len(P)}


def motif_au_centre(gc, hc, ech):
    """Points prouvés au centre + clique. Renvoie aussi les paires de contraintes des sommets."""
    # en mode "u", hc est u = 1/h : le moteur exact travaille sur h = 1/u (même réseau à
    # l'échelle 1/h près), et les valeurs numériques sont ramenées à l'unité du repère.
    if MODE == "u":
        if hc <= 0:
            raise Echec("u = 0 : réseau de rang 1, pas de cellule")
        g_ag, h_ag, fact = gc, 1 / hc, hc
    else:
        g_ag, h_ag, fact = gc, hc, F(1)
    info = AG.cellule(g_ag, h_ag)
    if info is None:
        raise Echec("cellule vide au centre")
    P, W, _ = info
    nmax = int(math.isqrt(int(W))) + 6
    cons = []
    for i in range(-nmax, nmax + 1):
        for j in range(-nmax, nmax + 1):
            if (i, j) == (0, 0):
                continue
            v = AG.vecteur(i, j, g_ag, h_ag)
            n2 = AG.norme2(v)
            if n2 > W:
                continue
            cons.append(((i, j), v, n2 / 2))
    tol = F(1, 10 ** 18)
    paires = []
    for p in P:
        ten = [ij for (ij, v, c) in cons if abs(p[0] * v[0] + p[1] * v[1] - c) < tol]
        if len(ten) < 2:
            raise Echec("sommet sans paire tendue")
        paires.append((ten[0], ten[1]))
    Gr = AG.graphe_exact(g_ag, h_ag, ech)
    k, S = AG.clique_max_avec0(Gr["adj"])
    if k < 7:
        raise Echec(f"omega = {k} < 7 au centre")
    inv = {t: o for o, t in Gr["idx"].items()}
    clique = sorted(inv[i] for i in S)[:9]        # on garde la marge : 7 suffit, 9 se défend

    # --- milieux de Delaunay vérifiés au centre
    mids = [(0, 0)]
    for w in [(i, j) for i in range(-FEN, FEN + 1) for j in range(-FEN, FEN + 1) if (i, j) != (0, 0)]:
        wv = AG.vecteur(w[0], w[1], gc, hc)
        nw2 = AG.norme2(wv)
        ok = True
        for v in [(i, j) for i in range(-nmax, nmax + 1) for j in range(-nmax, nmax + 1)
                  if (i, j) != (0, 0)]:
            vv = AG.vecteur(v[0], v[1], gc, hc)
            nv2 = AG.norme2(vv)
            if nv2 > 4 * nw2 + 4:
                continue
            if wv[0] * vv[0] + wv[1] * vv[1] - nv2 > 0:
                ok = False
                break
        if ok:
            mids.append(w)
    pts_mid = {w: (AG.vecteur(w[0], w[1], g_ag, h_ag)[0] / 2 * fact,
                   AG.vecteur(w[0], w[1], g_ag, h_ag)[1] / 2 * fact) for w in mids}
    if len(mids) < 3:
        raise Echec("moins de 3 milieux de Delaunay")
    return {"paires": paires, "clique": clique, "omega": k, "mids": mids,
            "pts_mid": pts_mid, "pts_centre": [(x * fact, y * fact) for (x, y) in P],
            "centre": (gc, hc),
            "n_sommets": len(P)}


# ---------------------------------------------------------------- candidats
def candidats(mot):
    """Points témoins : milieux de Delaunay et sommets, chacun rétracté à λ = 1 et λ = 1/2.

    Rétracter p en λp (λ < 1) est SÛR par convexité : 0 ∈ V et p ∈ V ⟹ λp ∈ V. Ce n'est pas
    une hypothèse du certificat : c'est une information de CONCEPTION. Le certificat, lui,
    teste les conditions polynomiales, qui passent pour λ < 1 avec de la MARGE. C'est cette
    marge qui survit aux transitions, là où un point du bord tombe — exactement le cas de
    g = 0, où les quatre coins de la cellule rectangulaire et tous les milieux non nuls sont
    sur le bord, donc sans marge.
    """
    base = []
    for w in mot["mids"]:
        p = milieu(w)
        base.append((f"m{w}", (R(p[0]), R(p[1])), mot["pts_mid"][w]))
    for k, pa in enumerate(mot["paires"]):
        base.append((f"s{k}", sommet_sym(*pa), mot["pts_centre"][k]))
    out = []
    for lam in (F(1), F(1, 2)):
        for nom, p, val in base:
            out.append((nom + ("" if lam == 1 else "r"), (p[0] * lam, p[1] * lam),
                        (val[0] * lam, val[1] * lam), lam))
    return out


# ---------------------------------------------------------------- plan
def plan_de(mot, ech, permis=None, selection="exacte"):
    """Fonctions à encadrer : toutes calculées une fois (elles ne dépendent pas de la boîte)."""
    gc, hc = mot["centre"]
    ech2 = ech * ech

    cand = candidats(mot)

    # --- membre de chaque candidat : contraintes à tester, en forme POLYNOMIALE (sans division)
    #     point p dans V  ⟺  ∀v ≠ 0,  2⟨p,v⟩ − |v|²  ≤ 0.
    #     Seuls les v de norme < 2|p| peuvent mordre : au-delà, l'inégalité est automatique.
    # Les vecteurs v et |v|² ne dépendent que de (i, j) : on les calcule une fois pour toutes
    # au lieu de |candidats| fois (724 contraintes = 46 témoins × ~16 vecteurs utiles).
    global _VECTEURS, _NORME, _VSYM, _N2SYM
    _VECTEURS = [(i, j) for i in range(-FEN - 3, FEN + 4) for j in range(-FEN - 3, FEN + 4)
                 if (i, j) != (0, 0)]
    _NORME = {ij: math.hypot(*AG.vecteur(ij[0], ij[1], gc, hc)) for ij in _VECTEURS}
    _VSYM = {ij: vec_sym(*ij) for ij in _VECTEURS}
    _N2SYM = {ij: n2_sym(_VSYM[ij]) for ij in _VECTEURS}
    plan = {"points": [], "membres": [], "ech": ech, "ech2": ech2, "_differe": False}
    for nom, p, val, lam in cand:
        rayon = 2 * math.hypot(float(val[0]), float(val[1])) + 0.5
        m = []
        for ij in _VECTEURS:
            if _NORME[ij] > rayon:
                continue
            vs = _VSYM[ij]
            m.append((ij, (p[0] * vs[0] + p[1] * vs[1]) * 2 - _N2SYM[ij]))
        plan["points"].append({"nom": nom, "sym": p, "val": val, "lam": lam})
        plan["membres"].append(m)

    # --- majorant 1 du diamètre : parallélogramme ±b1, ±b2 (sur-ensemble robuste)
    par = [sommet_sym(*pa) for pa in [((1, 0), (0, 1)), ((0, 1), (-1, 0)),
                                      ((-1, 0), (0, -1)), ((0, -1), (1, 0))]]
    plan["para_dist"] = [dist2(par[a], par[b]) for a in range(4) for b in range(a + 1, 4)]

    # --- majorant 2 : diam ≤ 2·max|x| sur les intersections des contraintes du motif
    cons = sorted({ij for pa in mot["paires"] for ij in pa})
    inter = []
    for a in range(len(cons)):
        for b in range(a + 1, len(cons)):
            v1, v2 = vec_sym(*cons[a]), vec_sym(*cons[b])
            if (v1[0] * v2[1] - v1[1] * v2[0]).zero():
                continue                       # contraintes parallèles : pas d'intersection
            inter.append(sommet_sym(cons[a], cons[b]))
    plan["rayon2"] = [carre(q[0]) + carre(q[1]) for q in inter]

    # --- majorant 3 (serré quand le motif est valide) : diamètre du polygone des sommets du motif.
    # C'est un majorant de diam(cellule) parce que ce polygone est l'intersection d'un
    # sous-ensemble des contraintes ; s'il est dégénéré (contraintes redondantes), ses
    # « sommets » sont à l'extérieur, donc le maximum est encore plus grand : toujours sûr.
    som_mot = [sommet_sym(*pa) for pa in mot["paires"]]
    plan["som_dist"] = [dist2(som_mot[a], som_mot[b])
                        for a in range(len(som_mot)) for b in range(a + 1, len(som_mot))]

    # --- retrait des points dont l'appartenance échoue sur la boîte
    # --- géométrie mémorisée : permet de REFAIRE la sélection des témoins sans reconstruire
    #     le plan (le retrait d'un témoin change le choix de la paire diamétrale et des témoins
    #     proche/loin, mais ni les contraintes d'appartenance, ni les majorants de diamètre).
    plan["cand_sym"] = [(c[1], c[3]) for c in cand]
    plan["cand_valf"] = [(float(c[2][0]), float(c[2][1])) for c in cand]

    plan["origine"] = list(range(len(cand)))
    if permis is not None:
        garde = [k for k in range(len(cand)) if k in permis]
        if len(garde) < 3:
            raise Echec("moins de 3 points témoins utilisables")
        for cle in ("points", "membres"):
            plan[cle] = [plan[cle][k] for k in garde]
        plan["origine"] = garde
        cand = [cand[k] for k in garde]

    # --- géométrie des paires de la clique : décalage dec = c_b − c_a (indépendant des témoins)
    plan["geo_paires"] = []
    for a in range(len(mot["clique"])):
        for b in range(a + 1, len(mot["clique"])):
            ca, cb = mot["clique"][a], mot["clique"][b]
            vca = AG.vecteur(ca[0], ca[1], gc, hc)
            vcb = AG.vecteur(cb[0], cb[1], gc, hc)
            dec = (vcb[0] - vca[0], vcb[1] - vca[1])
            sdec = (Rat(vec_sym(cb[0], cb[1])[0]) - Rat(vec_sym(ca[0], ca[1])[0]),
                    Rat(vec_sym(cb[0], cb[1])[1]) - Rat(vec_sym(ca[0], ca[1])[1]))
            plan["geo_paires"].append((ca, cb, sdec, (float(dec[0]), float(dec[1]))))

    # --- sélection différée : la paire diamétrale et les témoins proche/loin sont choisis en
    #     FLOTTANT par prepare_temoins(), au moment de la certification. Cela évite
    #     2·|cand|²·|paires| distances en Fraction (dénominateurs ~10^16).
    if selection == "differee":
        plan["_differe"] = True
        plan["diam_pair"] = None
        plan["paires"] = {}
        return plan

    # --- paire diamétrale : la plus longue distance entre points témoins (minoration du diamètre)
    best, paire = F(-1), (0, 1)
    for a in range(len(cand)):                     # argmax sur les VALEURS (nombres), pas sur les
        for b in range(a + 1, len(cand)):          # Rat symboliques : Rat n'est pas ordonné
            dd = AG.dist2(cand[a][2], cand[b][2])
            if dd > best:
                best, paire = dd, (a, b)
    plan["diam_pair"] = dist2(cand[paire[0]][1], cand[paire[1]][1])

    # --- conflits : pour chaque paire de cellules de la clique, un témoin proche et un éloigné.
    #     Le point λ_a·p + c_a est dans la cellule a (convexité), donc la distance vaut
    #         |λ_a·p_a − λ_b·p_b − dec|,   dec = c_b − c_a .
    plan["paires"] = {}
    ech2 = plan["ech2"]
    for ca, cb, sdec, dec in plan["geo_paires"]:
        best_min, best_max = None, None
        for ia, (_, _, va, la) in enumerate(cand):
            for ib, (_, _, vb, lb) in enumerate(cand):
                dd = AG.dist2((va[0] * la, va[1] * la),
                              (vb[0] * lb + dec[0], vb[1] * lb + dec[1]))
                if best_min is None or dd < best_min[0]:
                    best_min = (dd, ia, ib)
                if best_max is None or dd > best_max[0]:
                    best_max = (dd, ia, ib)
        pa = (cand[best_min[1]][1][0] * cand[best_min[1]][3],
              cand[best_min[1]][1][1] * cand[best_min[1]][3])
        pb = (cand[best_min[2]][1][0] * cand[best_min[2]][3] + sdec[0],
              cand[best_min[2]][1][1] * cand[best_min[2]][3] + sdec[1])
        ecart = R(plan["diam_pair"]) - R(dist2(pa, pb)) * R(ech2)
        qa = (cand[best_max[1]][1][0] * cand[best_max[1]][3],
              cand[best_max[1]][1][1] * cand[best_max[1]][3])
        qb = (cand[best_max[2]][1][0] * cand[best_max[2]][3] + sdec[0],
              cand[best_max[2]][1][1] * cand[best_max[2]][3] + sdec[1])
        plan["paires"][(ca, cb)] = {"ecart": ecart, "proche": R(dist2(pa, pb)),
                                    "loin": R(dist2(qa, qb))}
    return plan


def certifie(gbox, hbox, ech, plan):
    B = (F(gbox[0]), F(gbox[1]), F(hbox[0]), F(hbox[1]))
    # --- appartenance de chaque point témoin à la cellule
    for k, mem in enumerate(plan["membres"]):
        for ij, f in mem:
            if signe_iv(f, B)[1] > 0:
                raise PointHors(k)
    # --- majorant du diamètre (parallélogramme) : encadrement
    # majorant du diamètre : MINIMUM de deux sur-ensembles, tous deux valides
    #  (a) le parallélogramme ±b1, ±b2 (grossier mais robuste aux transitions) ;
    #  (b) le polygone des contraintes des sommets survivants (serré).
    dh = max(d.enc(B)[1] for d in plan["para_dist"])          # majorant 1 (parallélogramme)
    # Les majorants 2 et 3 valent par des intersections de contraintes, donc des Rat à
    # DÉNOMINATEUR det(v1,v2) : si ce déterminant s'annule sur la boîte (dégénérescence,
    # par exemple en g = 0), le signe n'est pas défini et on ne peut pas l'encadrer. Un
    # majorant qu'on ne sait pas encadrer n'est pas faux : on le laisse tomber, le
    # parallélogramme reste valide. (C'était la cause du dernier « dénominateur non défini
    # en signe » : rien à voir avec les témoins, tout avec les MAJORANTS.)
    if plan.get("som_dist"):
        try:
            dh = min(dh, max(d.enc(B)[1] for d in plan["som_dist"]))
        except ZeroDivisionError:
            pass
    if plan.get("rayon2"):
        # majorant 2 : diam ≤ 2·max|x| sur les intersections des contraintes du motif
        try:
            dh = min(dh, 4 * max(signe_iv(r, B)[1] for r in plan["rayon2"]))
        except ZeroDivisionError:
            pass
    # --- minorant du diamètre : la paire la plus longue
    dl = plan["diam_pair"].enc(B)[0]
    if dl <= 0:
        raise Echec("diamètre minoré par 0")
    # cohérence : on refuse de certifier un majorant inférieur au minorant. Sans ce test, un
    # majorant corrompu (trop petit) passerait (L) sans difficulté et le certificat
    # affirmerait une cellule plus petite que ce qu'il a lui-même mesuré.
    if dh < dl:
        raise Echec(f"incohérence : diamètre haut {float(dh):.4f} < bas {float(dl):.4f}")
    # --- conflits : seuls ceux PROUVÉS sur toute la boîte comptent
    # Aux transitions du diagramme de Delaunay, une paire de la clique du centre cesse de se
    # toucher : le conflit est faux là, et le certificat le dit (il refuse) au lieu de le
    # supposer. On retire donc les paires non prouvées, puis on cherche une 7-clique dans le
    # graphe des conflits prouvés.
    prouves, non_prouves = [], 0
    for (ca, cb), f in plan["paires"].items():
        try:
            ok = (signe_iv(f["ecart"], B)[0] >= 0
                  and dh <= plan["ech2"] * signe_iv(f["loin"], B)[0])
        except ZeroDivisionError:
            ok = False
        if ok:
            prouves.append((ca, cb))
        else:
            non_prouves += 1
    som = set()
    for ca, cb in prouves:
        som.add(ca)
        som.add(cb)
    if len(som) < 7:
        raise Echec(f"7-clique impossible : {len(som)} cellules en conflit prouvé "
                    f"({non_prouves} paires non prouvées)")
    adj = {s: set() for s in som}
    for ca, cb in prouves:
        adj[ca].add(cb)
        adj[cb].add(ca)
    best = []
    for s in sorted(som, key=lambda z: -len(adj[z])):
        cand = {s} | adj[s]
        k = [t for t in sorted(cand) if all(t == u or u in adj[t] for u in cand)]
        if len(k) > len(best):
            best = k
    if len(best) < 7:
        raise Echec(f"7-clique impossible : la plus grande clique prouvée a {len(best)} sommets "
                    f"({non_prouves} paires non prouvées sur {len(plan['paires'])})")
    return {"diam_bas": float(dl), "diam_haut": float(dh), "clique_prouvee": len(best),
            "paires_non_prouvees": non_prouves}



# ==================================================================== certificat dans le repère w = 1/h
#
# La queue h → ∞ n'est pas une région qu'une boîte fermée peut couvrir : c'est une demi-droite.
# Le repère u = 1/h la rend bornée, mais y dégénère (le vecteur (1,0) s'écrase). Ce qui NE
# dégénère pas, ce sont les RAPPORTS : dmin/D et dmax/D ont des limites finies quand h → ∞
# (mesuré : à g = 0, dmax/D → 1,0000 pour les voisins horizontaux, 2,0000 pour les verticaux).
# Un rapport num/den dont num et den ont le MÊME degré en h est continu en w = 1/h :
#     num(1/w)/den(1/w) = [w^M·num(1/w)] / [w^M·den(1/w)],
# et le membre de droite est une fonction rationnelle POLYNOMIALE en (g,w), définie en w = 0.
# On peut donc certifier la boîte FERMÉE w ∈ [0, w0], c'est-à-dire h ∈ [1/w0, ∞].

def deg_h(f):
    """Degré en h d'un Poly (0 s'il est nul)."""
    return max((j for (i, j) in f.d), default=0)


def en_w(f, M):
    """Poly(g,h)  ↦  w^M · f(g, 1/w), polynôme en (g,w) (le second indice porte w)."""
    out = {}
    for (i, j), c in f.d.items():
        if j > M:
            raise Echec(f"degré en h {j} > M = {M} : transformation impossible")
        out[(i, M - j)] = out.get((i, M - j), 0) + c
    return Poly(out)


def en_w_rat(r, M):
    """Rat  ↦  même fonction de (g,w) = w^M·r(g,1/w), écrite comme Rat de (g,w)."""
    return Rat(en_w(r.n, M), en_w(r.d, M))


def _M(*fs):
    """Le plus grand degré en h parmi les numérateurs et dénominateurs fournis."""
    m = 0
    for f in fs:
        if isinstance(f, Rat):
            m = max(m, deg_h(f.n), deg_h(f.d))
        else:
            m = max(m, deg_h(f))
    return m


def signe_rapport_w(r, B):
    """Signe d'un RAPPORT en repère w = 1/h.

    Une quantité qui diverge (le diamètre², ~ h²) ne peut pas être encadrée sur une boîte en w.
    Un *rapport* de deux quantités de même degré en h, lui, a une limite finie : c'est sous
    cette forme que les conditions doivent être écrites. On multiplie numérateur et
    dénominateur par w^M avec M = deg_h max ; si le dénominateur n'atteint pas ce degré, le
    rapport diverge en h = ∞ et la boîte n'est pas certifiable — on le signale par
    ZeroDivisionError, que l'appelant traite comme un échec ordinaire.
    """
    n, d = r.n, r.d
    M = max(deg_h(n), deg_h(d))
    if deg_h(d) < M:
        raise ZeroDivisionError("rapport divergent en h = ∞")
    return signe_iv(Rat(en_w(n, M), en_w(d, M)), B)


def _comb(a, b, c):
    """a − c·b pour a, b des Poly et c un nombre : contourne Poly.__sub__(Rat)."""
    d = dict(a.d)
    for k, v in b.d.items():
        d[k] = d.get(k, 0) - c * v
    return Poly({k: v for k, v in d.items() if v})


def _comb2(a, ca, b, cb):
    """ca·a + cb·b pour a, b des Poly : contourne Poly.__sub__(Rat)."""
    d = {}
    for k, v in a.d.items():
        d[k] = d.get(k, 0) + ca * v
    for k, v in b.d.items():
        d[k] = d.get(k, 0) + cb * v
    return Poly({k: v for k, v in d.items() if v})


def _div_poly(f, den):
    """f / den, pour f Poly ou Rat et den un Poly non nul sur la boîte : un Rat."""
    return Rat(f.n, f.d * den) if isinstance(f, Rat) else Rat(f, den)


def prepare_temoins(plan, permis):
    """Re-sélectionne les témoins SOUS CONTRAINTE de `permis`, en FLOTTANT.

    Le retrait d'un témoin change deux choses seulement : quelle paire est la plus longue
    (minorant du diamètre) et quels témoins sont proche/loin pour chaque paire de cellules.
    Ces deux choix sont des EXTREMUMS sur des nombres : les faire en flottant coûte
    O(|permis|²) opérations machine, là où la version symbolique coûtait O(|permis|²) Rat à
    gros dénominateurs — et où l'ancienne boucle RECONSTRUISAIT tout le plan (1 488
    contraintes d'appartenance) à chaque retrait.

    Le flottant ne sert QU'À CHOISIR : l'inégalité finalement retenue est toujours construite
    en rationnel exact et vérifiée sur toute la boîte. Un mauvais choix fait échouer le
    certificat, il ne le fausse pas.
    """
    idx = sorted(permis)
    vf, cs = plan["cand_valf"], plan["cand_sym"]
    lf = [float(cs[k][1]) for k in range(len(vf))]
    px = [vf[k][0] * lf[k] for k in range(len(vf))]
    py = [vf[k][1] * lf[k] for k in range(len(vf))]

    best, paire = -1.0, None
    for ii, a in enumerate(idx):
        for b in idx[ii + 1:]:
            dx, dy = px[a] - px[b], py[a] - py[b]
            dd = dx * dx + dy * dy
            if dd > best:
                best, paire = dd, (a, b)
    if paire is None:
        raise Echec("moins de 2 témoins utilisables")
    (pa, la), (pb, lb) = cs[paire[0]], cs[paire[1]]
    diam = dist2((pa[0] * la, pa[1] * la), (pb[0] * lb, pb[1] * lb))

    paires = {}
    for ca, cb, sdec, decf in plan["geo_paires"]:
        bmin = bmax = None
        for a in idx:
            xa, ya = px[a], py[a]
            for b in idx:
                dx, dy = xa - px[b] - decf[0], ya - py[b] - decf[1]
                dd = dx * dx + dy * dy
                if bmin is None or dd < bmin[0]:
                    bmin = (dd, a, b)
                if bmax is None or dd > bmax[0]:
                    bmax = (dd, a, b)

        def expr(k, dec):
            q, l = cs[k]
            return (q[0] * l + dec[0], q[1] * l + dec[1])

        paires[(ca, cb)] = {"proche": R(dist2(expr(bmin[1], (0, 0)), expr(bmin[2], sdec))),
                            "loin": R(dist2(expr(bmax[1], (0, 0)), expr(bmax[2], sdec)))}
    return {"diam": diam, "paires": paires}


def certifie_w(plan, gbox, wbox, ech, permis=None):
    """certifie() dans le repère w = 1/h, sur une boîte FERMÉE en w (donc h ≥ 1/w1).

    Toutes les conditions sont écrites en RAPPORTS de degrés égaux en h : seuls les rapports
    ont une limite quand h = ∞, et c'est elle qu'on encadre.
    """
    B = (F(gbox[0]), F(gbox[1]), F(wbox[0]), F(wbox[1]))
    ech2 = plan["ech2"]

    # Les témoins retirés sont simplement MASQUÉS : plan["membres"] n'est plus reconstruit.
    if permis is None and plan.get("_differe"):
        permis = set(range(len(plan["points"])))
    if permis is not None:
        prep = prepare_temoins(plan, permis)
        diam_rat, paires_utiles = prep["diam"], prep["paires"]
    else:
        diam_rat, paires_utiles = plan["diam_pair"], plan["paires"]

    # (1) appartenance des témoins : condition normalisée par |v|² (qui est > 0)
    for k, mem in enumerate(plan["membres"]):
        if permis is not None and k not in permis:
            continue
        for ij, f in mem:
            if signe_rapport_w(_div_poly(f, n2_sym(vec_sym(*ij))), B)[1] > 0:
                raise PointHors(k)

    # (2) majorants candidats du diamètre au carré (chacun est légitime à lui seul)
    bornes = []
    for cle in ("para_dist", "som_dist"):
        for d in plan.get(cle) or []:
            bornes.append(R(d))
    for r in plan.get("rayon2") or []:
        bornes.append(R(r) * R(4))

    # (3) minorant du diamètre (facultatif : il peut légitimement diverger)
    try:
        dl = signe_rapport_w(R(diam_rat), B)[0]
        if dl <= 0:
            raise Echec("diamètre minoré par 0")
    except ZeroDivisionError:
        dl = 0.0

    # (4) conflits, en rapports bornés
    def conflit(f):
        proche, loin = R(f["proche"]), R(f["loin"])
        # (U)  diam_pair − ε²·proche ≥ 0,  normalisée par diam_pair
        a = R(diam_rat)
        num = _comb2(a.n * proche.d, 1, proche.n * a.d, -ech2)
        if signe_rapport_w(Rat(num, a.n * proche.d), B)[0] < 0:
            return False
        # (L)  loin − ε²·dh ≥ 0, normalisée par loin, pour AU MOINS un majorant candidat
        for d in bornes:
            num = _comb2(loin.n * d.d, ech2, d.n * loin.d, -1)
            if signe_rapport_w(Rat(num, loin.n * d.d), B)[0] >= 0:
                return True
        return False

    prouves, non_prouves = [], 0
    for (ca, cb), f in paires_utiles.items():
        try:
            ok = conflit(f)
        except (ZeroDivisionError, Echec):
            ok = False
        if ok:
            prouves.append((ca, cb))
        else:
            non_prouves += 1

    som = set()
    for ca, cb in prouves:
        som.add(ca)
        som.add(cb)
    if len(som) < 7:
        raise Echec(f"7-clique impossible : {len(som)} cellules en conflit prouvé "
                    f"({non_prouves} paires non prouvées)")
    adj = {s: set() for s in som}
    for ca, cb in prouves:
        adj[ca].add(cb)
        adj[cb].add(ca)
    best = []
    for s in sorted(som, key=lambda z: -len(adj[z])):
        cand = {s} | adj[s]
        if all(t == u or u in adj[t] for t in cand for u in cand) and len(cand) > len(best):
            best = sorted(cand)
    if len(best) < 7:
        raise Echec(f"7-clique impossible : la plus grande clique prouvée a {len(best)} sommets "
                    f"({non_prouves} paires non prouvées sur {len(paires_utiles)})")
    return {"diam_bas": float(dl), "clique_prouvee": len(best),
            "paires_non_prouvees": non_prouves, "clique": best}


def certifie_w_avec_retrait(gbox, wbox, ech, mot, max_essais=12, plan=None):
    """Le pendant en repère w = 1/h de certifie_avec_retrait.

    Le plan est construit UNE fois ; les retraits ne font que masquer des témoins. Coût du
    retrait : O(|permis|²) flottant au lieu de O(plan) rationnel (1,28 s mesuré). Les indices
    sont ceux du plan complet (aucune renumérotation), donc PointHors.k est directement
    l'indice à masquer.
    """
    if plan is None:
        plan = plan_de(mot, ech, selection="differee")
    permis = set(range(len(plan["points"])))
    for _ in range(max_essais):
        try:
            return certifie_w(plan, gbox, wbox, ech, permis)
        except PointHors as ph:
            permis.discard(ph.k)
    raise Echec("certificat impossible après retrait des points")


def certifie_avec_retrait(gbox, hbox, ech, mot, max_essais=12):
    """Retrait des points témoins dont l'appartenance échoue sur la boîte.

    Attention : plan_de RENUMÉROTE les points après filtrage ; PointHors donne donc un indice
    dans le plan filtré, qu'il faut reconvertir par plan["origine"] pour mettre à jour permis.
    (Bogue attrapé ici : sans cette conversion, on retirait un point déjà retiré et la boucle
    tournait dix fois sur le même échec.)
    """
    n = len(candidats(mot))
    permis = set(range(n))
    for _ in range(max_essais):
        plan = plan_de(mot, ech, permis)
        try:
            return certifie(gbox, hbox, ech, plan)
        except PointHors as ph:
            permis.discard(plan["origine"][ph.k])
    raise Echec("certificat impossible après retrait des points")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g", default="-2/5")
    ap.add_argument("--h", default="1")
    ap.add_argument("--ech", default="99/100")
    a = ap.parse_args()
    ech = F(a.ech)
    mot = motif_au_centre(F(a.g), F(a.h), ech)
    print("omega", mot["omega"], "| sommets", mot["n_sommets"], "| milieux vérifiés", mot["mids"])
    pl = plan_de(mot, ech)
    print("points témoins :", [p["nom"] for p in pl["points"]])
    try:
        print("boîte-point :", certifie((a.g, a.g), (a.h, a.h), ech, pl))
    except Echec as e:
        print("échec boîte-point :", e)


if __name__ == "__main__":
    main()
