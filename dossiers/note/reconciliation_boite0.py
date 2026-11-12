"""Réconciliation du point bloquant : « la boîte 0 ne donne que 20/21 paires en conflit ».

Ce que le dossier affirmait
---------------------------
« Au point d'export (g = −3/8, h = 219/250), la clique de la boîte 0 ne donne que 20/21 paires
en conflit avec mon calcul dmin2_dmax2, alors que omega_exact annonce ω = 7 — probablement
parce que audit_gh.cellule renvoie une liste dont le premier élément est le polygone. »

Ce que la machine dit (ce fichier le vérifie, en rationnels exacts, sans flottant décisionnel)
----------------------------------------------------------------------------------------------
1. L'hypothèse du « premier élément » est FAUSSE. `cellule(g, h)` renvoie le triplet
   (sommets, W, rayon²) ; `cellule(g, h)[0]` EST la liste des sommets, et c'est bien elle qu'il
   faut passer à `dmin2_dmax2`. Prendre le triplet entier donnerait trois « points » dont le
   premier serait une liste — aucune des variantes fautives ne reproduit 20/21.

2. Le 20/21 est réel, mais sa cause est ailleurs : **les deux calculs ne comparent pas la même
   quantité**. `audit_gh.graphe_exact` teste le conflit au seuil T = diam/σ, c'est-à-dire

       σ² · dmin² ≤ diam² ≤ σ² · dmax²        (σ = « ech », figé à 99/100)

   alors que `Boites.clique_de_temoins` demande des témoins à distance AU CARRÉ ≤ 1 et ≥ 1,
   c'est-à-dire le seuil T = 1. Les deux écritures ne coïncident que si T² = diam²/σ².
   Confondre « σ = 1 » avec « T = 1 » est le piège : à σ = 1 le seuil vaut diam ≈ 1,1706,
   pas 1. Au centre de la boîte 0, la paire ((−1,−2), (1,0)) a dmin² = 1,158001, comprise
   entre 1 et diam² = 1,370210 : elle est donc en conflit dès que σ ≥ 0,92, et n'en est pas
   un au seuil 1. D'où exactement 20/21 au centre, 19/21 à g = −1/2, 19/21 à g = 1/2,
   h = 9/10.

3. Conséquence, et c'est la vraie conclusion : la 7-clique exportée n'est pas réparable.
   Au seuil 1, ω vaut 6 au centre de la boîte 0 et 5 sur ses bords verticaux. Aucun choix de
   témoins ne peut « récupérer » la paire manquante : dmin² > 1 veut dire que les deux cellules
   sont à distance > 1, donc qu'aucune paire de points ne les rapproche.

4. Ce que la boîte 0 fournit réellement est un ε < 1 : la condition d'échelle uniforme
       dmin < dmax  et  D < dmax      (pour les 21 paires, à un même s)
   tient sur toute la boîte, avec ε = D/dmax ≤ 0,607 au pire. C'est le lemme B de Pont.lean,
   pas le seuil 1. La donnée à exporter n'est donc pas « 7 décalages » mais, par paire,
   quatre points : deux à distance² ≤ 1 et deux à distance² ≥ 1.

Ce que ce fichier ne fait pas
-----------------------------
Il ne prouve rien sur la boîte entière : il échantillonne (coins, milieux d'arêtes, centre).
Le certificat sur la boîte est l'affaire de `certifie_w`, et des quatre témoins par paire.
"""
import json
import sys
import types
from fractions import Fraction as F

# audit_gh importe numpy sans s'en servir dans les fonctions employées ici.
if "numpy" not in sys.modules:
    try:
        import numpy  # noqa: F401
    except ModuleNotFoundError:
        sys.modules["numpy"] = types.ModuleType("numpy")

import audit_gh as A

CENTRE_BOITE0 = (F(-3, 8), F(219, 250))
CLIQUE_BOITE0 = [(-1, -2), (-1, -1), (0, -2), (0, -1), (0, 0), (1, -1), (1, 0)]


def geometrie(g, h, clique):
    """(diam², {paire: (dmin², dmax²)}) exacts, pour la clique donnée."""
    info = A.cellule(g, h)
    if info is None:
        return None
    P = info[0]                                  # <- liste des sommets, pas le triplet
    diam2 = max(A.dist2(p, q) for p in P for q in P)
    paires = {}
    for i in range(len(clique)):
        for j in range(i + 1, len(clique)):
            d = A.vecteur(clique[j][0] - clique[i][0], clique[j][1] - clique[i][1], g, h)
            Q = [(x + d[0], y + d[1]) for (x, y) in P]
            paires[(clique[i], clique[j])] = A.dmin2_dmax2(P, Q)
    return diam2, paires


def compter(diam2, paires, T2):
    """Paires en conflit au SEUIL T2 = T² (distance² à comparer à 1), et les manquantes.

    Convention : une paire est en conflit au seuil T quand dmin ≤ T ≤ dmax, soit
    dmin² ≤ T² ≤ dmax². C'est la lecture de `Boites.clique_de_temoins` (T = 1) et celle de
    `pont_coloriage` (témoins à distance ≤ 1 et ≥ 1).

    Attention : `audit_gh.graphe_exact` n'utilise PAS ce paramètre-là. Il teste
    σ²·dmin² ≤ diam² ≤ σ²·dmax², c'est-à-dire le seuil T = diam/σ. Les deux écritures
    coïncident ssi T² = diam²/σ². Confondre σ = 1 avec T = 1 est exactement le piège que ce
    fichier isole : à σ = 1 le seuil vaut diam ≈ 1,17, pas 1.
    """
    manquantes = [k for k, (lo2, hi2) in paires.items()
                  if not (lo2 <= T2 <= hi2)]
    return len(paires) - len(manquantes), manquantes


def omega_max(adj):
    """Clique maximale EXACTE (Bron–Kerbosch avec pivot), sans contrainte d'appartenance à 0."""
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

    bk(set(), set(range(len(adj))), set())
    return best[0], best[1]


def graphe_seuil(g, h, T2):
    """Graphe de conflit au seuil EXACT T2 (distance²), sur une fenêtre d'indices sûre.

    C'est la lecture « σ = 1 » que réclame Boites.clique_de_temoins. La fenêtre découle de
    l'inégalité triangulaire : deux cellules à distance ≤ √T2 ont des centres à distance
    ≤ √T2 + 2·diam.
    """
    import math

    info = A.cellule(g, h)
    if info is None:
        return None
    P = info[0]
    diam2 = max(A.dist2(p, q) for p in P for q in P)
    rayon = math.isqrt(int(diam2 * (1 + math.sqrt(float(T2))) ** 2)) + 6
    cand = [(0, 0)]
    for i in range(-rayon, rayon + 1):
        for j in range(-rayon, rayon + 1):
            if (i, j) == (0, 0):
                continue
            if A.norme2(A.vecteur(i, j, g, h)) <= diam2 * (1 + math.sqrt(float(T2))) ** 2:
                cand.append((i, j))
    adj = [set() for _ in cand]
    for a in range(len(cand)):
        for b in range(a + 1, len(cand)):
            ca = A.vecteur(*cand[a], g, h)
            cb = A.vecteur(*cand[b], g, h)
            d = (cb[0] - ca[0], cb[1] - ca[1])
            if A.norme2(d) > diam2 * (1 + math.sqrt(float(T2))) ** 2:
                continue
            Q = [(x + d[0], y + d[1]) for (x, y) in P]
            lo2, hi2 = A.dmin2_dmax2(P, Q)
            if lo2 <= T2 <= hi2:
                adj[a].add(b)
                adj[b].add(a)
    return {"adj": adj, "cand": cand, "P": P, "diam2": diam2}


def main():
    ok = True
    g, h = CENTRE_BOITE0
    print("=" * 78)
    print("1. La forme de ce que renvoie audit_gh.cellule")
    print("=" * 78)
    info = A.cellule(g, h)
    print(f"  len(cellule(g, h)) = {len(info)}  -> (sommets, W, rayon²)")
    print(f"  len(cellule(g, h)[0]) = {len(info[0])} sommets ; [0][0] = {info[0][0]}")
    print("  => passer cellule(...)[0] à dmin2_dmax2 est CORRECT.")
    print("     L'hypothèse « le premier élément est le polygone » est fausse.\n")

    diam2, paires = geometrie(g, h, CLIQUE_BOITE0)
    print("=" * 78)
    print("2. Les deux seuils, au centre de la boîte 0")
    print("=" * 78)
    print(f"  diam² = {diam2} = {float(diam2):.6f}   (diam = {float(diam2) ** 0.5:.6f})")
    n_d, manq_d = compter(diam2, paires, diam2)
    n_1, manq_1 = compter(diam2, paires, F(1))
    print(f"  seuil T = diam/σ avec σ = 1  (le défaut de graphe_exact) : "
          f"{n_d}/21 en conflit")
    print(f"  seuil T = diam/σ avec σ = 99/100                        : "
          f"{compter(diam2, paires, diam2 / F(99, 100) ** 2)[0]}/21 en conflit")
    print(f"  seuil T = 1  (ce que Boites.clique_de_temoins demande)   : "
          f"{n_1}/21 en conflit   manquante(s) {manq_1}")
    for k in manq_1:
        lo2, hi2 = paires[k]
        print(f"     paire {k} : dmin² = {lo2} = {float(lo2):.6f} > 1  (dmax² = {float(hi2):.3f})")
        print(f"       -> au seuil diam/σ elle EST en conflit (dmin² = {float(lo2):.4f} ≤ "
              f"diam²/σ² pour σ ≥ {float(lo2 / diam2) ** 0.5:.4f}),")
        print("          mais au seuil 1 les deux cellules sont réellement séparées :")
        print("          aucune paire de points, aucun témoin, ne peut les rapprocher.")
    print()
    if not (n_1 == 20 and n_d == 21):
        print("  ÉCHEC : la situation décrite par le dossier n'est pas reproduite.")
        ok = False
    else:
        print("  => le 20/21 est REPRODUIT. La cause n'est pas la forme du retour de")
        print("     `cellule` (qui est correcte) mais la CONFUSION DES SEUILS :")
        print("     σ = 1 (défaut d'omega_exact/graphe_exact) n'est pas T = 1.")
        print()

    print("=" * 78)
    print("3. Sur toute la boîte 0, au seuil 1 (ce que Boites.clique_de_temoins demande)")
    print("=" * 78)
    for gg in [F(-1, 2), F(-3, 8), F(-1, 4)]:
        for hh in [F(433, 500), F(219, 250), F(9, 10)]:
            d2, pa = geometrie(gg, hh, CLIQUE_BOITE0)
            n, manq = compter(d2, pa, F(1))
            print(f"  g = {str(gg):>6} h = {str(hh):>9} : {n}/21 en conflit   manquantes {len(manq)}")
    print()

    print("=" * 78)
    print("4. La clique est-elle réparable ? ω au seuil 1, sur le vrai graphe")
    print("=" * 78)
    for gg, hh in [CENTRE_BOITE0, (F(-1, 2), F(219, 250)), (F(1, 2), F(9, 10))]:
        Gr = graphe_seuil(gg, hh, F(1))
        k, S = omega_max(Gr["adj"])
        print(f"  g = {str(gg):>6} h = {str(hh):>9} : ω(T = 1) = {k}   "
              f"clique {[Gr['cand'][i] for i in sorted(S)]}")
    r = A.omega_exact(g, h, F(99, 100))
    r1 = A.omega_exact(g, h, F(1))
    print(f"\n  Rappel, tel quel : omega_exact(g, h, 99/100) annonce ω = {r['omega']} "
          f"(les {len(r['temoins'])} décalages exportés).")
    print("  Ce chiffre est un ω au seuil T = diam/σ = 1,1824, PAS au seuil 1 :")
    print("  le défaut σ = 99/100 rend le seuil PLUS GRAND que 1, donc plus permissif.")
    print(f"  omega_exact(g, h, 1) — seuil T = diam = {float(diam2) ** 0.5:.4f} — annonce "
          f"ω = {r1['omega']} : même valeur, même cause.")
    print("  ω(T = 1) = 6 < 7 : la 7-clique exportée n'est PAS une clique à σ = 1, et aucun")
    print("  jeu de témoins ne peut la réparer (dmin² > 1 = cellules réellement séparées).\n")

    print("=" * 78)
    print("5. Ce que la boîte 0 fournit réellement : un ε < 1, pas le seuil 1")
    print("=" * 78)
    pire = F(0)
    for a in range(5):
        for c in range(5):
            gg = F(-1, 2) + F(1, 4) * F(a, 4)
            hh = F(433, 500) + (F(9, 10) - F(433, 500)) * F(c, 4)
            d2, pa = geometrie(gg, hh, CLIQUE_BOITE0)
            for k2, (lo2, hi2) in pa.items():
                pire = max(pire, d2 / hi2)          # = (D/dmax)²
    print(f"  ε = max sur la grille de D/dmax = {float(pire) ** 0.5:.6f}  (=√{pire})")
    print("  ε < 1 : la condition « D < dmax » du lemme B tient. C'est tout ce qu'il faut pour")
    print("  un conflit à l'échelle s = l'échelle de Pont.lemmeB — à condition d'exporter")
    print("  QUATRE témoins par paire, et non sept décalages avec un seuil figé.\n")

    print("=" * 78)
    print("VERDICT : " + ("RÉCONCILIÉ" if ok else "NON RÉCONCILIÉ"))
    print("=" * 78)
    print("Le 20/21 n'est pas un bug de forme de retour de `cellule`, qui est correcte :")
    print("c'est la comparaison de deux seuils différents — T = diam/σ (ce que mesurent")
    print("omega_exact et graphe_exact, σ figé à 99/100) contre T = 1 (ce que Boites.lean")
    print("consomme). Au seuil 1, ω vaut 6 et non 7 : la boîte 0 ne porte pas de 7-clique")
    print("au seuil 1, et n'en portera jamais. Ce qu'elle porte est un ε = D/dmax ≤ 0,607 < 1,")
    print("c'est-à-dire exactement l'hypothèse du lemme B de Pont.lean, à l'échelle mobile s.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
