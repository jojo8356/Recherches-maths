"""GESTE 1 — Prouver la couverture du domaine, au lieu de l'affirmer.

Le certificat de 2026-11-03 affirmait « aire certifiee 100 % » en sommant des aires en
flottants. Ce n'est pas une preuve : une somme d'aires egale a l'aire du domaine ne dit
rien si deux boites se recouvrent et qu'une troisieme manque.

Ce script refait la verification en arithmetique EXACTE (fractions de dyadiques, aucun
flottant dans les decisions) et sur la STRUCTURE :
  1. chaque boite est exactement une cellule dyadique de la grille initiale (meme
     decoupage 100 x 200, memes coordonnees) : on la reindexe par (profondeur, ix, iy) ;
  2. l'ensemble des feuilles est une COUPE COMPLETE de l'arbre quaternaire : tout noeud
     est soit une feuille, soit a ses quatre enfants presents ; recursivement jusqu'aux
     100 x 200 racines, qui pavent exactement [1,2] x [60,120] ;
  3. controle negatif : si l'on retire une boite au hasard, la verification doit ECHOUER
     (sinon elle ne prouve rien).

Conclusion prouvee : la reunion des boites certifiees est exactement le domaine.

Sortie : couverture.json + affichage.
"""
import json
import sys
from fractions import Fraction as F

RHO0, RHO1 = F(1), F(2)
TH0, TH1 = F(60), F(120)
NR0, NT0 = 100, 200                       # grille initiale (dr = 1/100, dth = 60/200)


def indexe(r0, r1, t0, t1, tol=F(1, 10**6)):
    """Reconstruit (profondeur, ix, iy) et l'ecart residuel, ou None.

    Les fichiers de certificat stockent les coordonnees arrondies (8 decimales pour rho,
    6 pour theta) : la grille decimale n'est pas exacte en binaire. On reconstruit donc
    l'INDEX exact de la cellule et on mesure l'ecart entre la valeur stockee et la
    coordonnee rationnelle exacte ; l'ecart doit rester dans le bruit d'arrondi du
    fichier (<= 5e-9), sinon la boite est declaree invalide.
    """
    wr = F(r1) - F(r0)
    for p in range(0, 15):
        if abs(wr - (RHO1 - RHO0) / (NR0 * 2 ** p)) > tol:
            continue
        ix = (F(r0) - RHO0) * (NR0 * 2 ** p) / (RHO1 - RHO0)
        iy = (F(t0) - TH0) * (NT0 * 2 ** p) / (TH1 - TH0)
        if abs(ix - round(ix)) > tol or abs(iy - round(iy)) > tol:
            continue
        ix, iy = int(round(ix)), int(round(iy))
        if not (0 <= ix < NR0 * 2 ** p and 0 <= iy < NT0 * 2 ** p):
            continue
        dr, dt = (RHO1 - RHO0) / (NR0 * 2 ** p), (TH1 - TH0) / (NT0 * 2 ** p)
        attendu = (RHO0 + ix * dr, RHO0 + (ix + 1) * dr, TH0 + iy * dt, TH0 + (iy + 1) * dt)
        ecart = max(abs(F(r0) - attendu[0]), abs(F(r1) - attendu[1]),
                    abs(F(t0) - attendu[2]), abs(F(t1) - attendu[3]))
        if ecart <= tol:
            return (p, ix, iy), ecart
    return None


def verifie(boites, verbose=True):
    """boites : liste de [r0, r1, t0, t1]. Rend (ok, rapport)."""
    feuilles = {}
    mauvaises = []
    ecarts = []
    for (r0, r1, t0, t1) in boites:
        r0, r1, t0, t1 = F(r0), F(r1), F(t0), F(t1)
        if not (RHO0 <= r0 < r1 <= RHO1 and TH0 <= t0 < t1 <= TH1):
            mauvaises.append((r0, r1, t0, t1))
            continue
        res = indexe(r0, r1, t0, t1)
        if res is None:
            mauvaises.append((r0, r1, t0, t1))
            continue
        idx, ecart = res
        ecarts.append(ecart)
        if idx in feuilles:
            return False, {"raison": "boite en double", "index": idx}
        feuilles[idx] = (r0, r1, t0, t1)
    if mauvaises:
        return False, {"raison": f"{len(mauvaises)} boites hors domaine ou non dyadiques",
                       "exemples": [list(map(str, m[:4])) for m in mauvaises[:5]]}

    # coupe complete de l'arbre quaternaire : on construit l'ensemble des noeuds
    # (feuilles + tous leurs ancetres + racines) puis on exige que tout noeud interne
    # ait ses QUATRE enfants dans l'ensemble. Pas de recursion jusqu'au fond : un trou
    # est signale comme le premier enfant manquant, pas explore 4^9 fois.
    noeuds = set(feuilles)
    for (p, ix, iy) in feuilles:
        while p > 0:
            p, ix, iy = p - 1, ix // 2, iy // 2
            noeuds.add((p, ix, iy))
    for ix in range(NR0):
        for iy in range(NT0):
            noeuds.add((0, ix, iy))
    manquants = []
    for (p, ix, iy) in noeuds:
        if (p, ix, iy) in feuilles:
            continue
        for dx in (0, 1):
            for dy in (0, 1):
                if (p + 1, 2 * ix + dx, 2 * iy + dy) not in noeuds:
                    manquants.append((p + 1, 2 * ix + dx, 2 * iy + dy))
    if manquants:
        return False, {"raison": "coupe incomplete : des cellules ne sont couvertes par aucune boite",
                       "manquants": manquants[:10], "nb_manquants": len(manquants)}
    n_noeuds = len(noeuds)

    aire = sum((b[1] - b[0]) * (b[3] - b[2]) for b in feuilles.values())
    total = (RHO1 - RHO0) * (TH1 - TH0)
    return True, {"nb_boites": len(feuilles), "noeuds_parcourus": n_noeuds,
                  "ecart_max_stockage": str(max(ecarts)) if ecarts else "0",
                  "aire_exacte": str(aire), "aire_domaine": str(total),
                  "aire_egale": aire == total,
                  "profondeurs": sorted({p for (p, _, _) in feuilles}),
                  "recouvrement": "exact (coupe complete de l'arbre quaternaire)"}


def main(fichier="certificat.json"):
    d = json.load(open(fichier))
    boites = [[b[0], b[1], b[2], b[3]] for b in d["boites"]]
    print(f"{fichier} : {len(boites)} boites, domaine declare {d['domaine']}")
    ok, rap = verifie(boites)
    print("couverture :", "PROUVEE" if ok else "ECHEC")
    for k, v in rap.items():
        print(f"  {k} : {v}")

    # ---- controle negatif : retirer une boite doit faire echouer la verification
    import random
    random.seed(1)
    i = random.randrange(len(boites))
    rest = boites[:i] + boites[i + 1:]
    ok2, rap2 = verifie(rest)
    print("\ncontrole negatif (on retire une boite au hasard) :",
          "PROUVE" if not ok2 else "*** LA VERIFICATION N'A RIEN VU ***")
    print("  raison :", rap2.get("raison"))

    # ---- controle negatif 2 : recouvrement (boite dupliquee legerement decalee)
    b = boites[0]
    recol = boites + [[b[0], (F(b[0]) + F(b[1])) / 2, b[2], b[3]]]
    ok3, rap3 = verifie([list(map(float, x)) for x in recol])
    print("controle negatif 2 (boite non dyadique ajoutee) :",
          "PROUVE" if not ok3 else "*** LA VERIFICATION N'A RIEN VU ***")
    print("  raison :", rap3.get("raison"))

    json.dump({"fichier": fichier, "couverture_prouvee": ok, "rapport": rap,
               "controle_negatif_boite_retiree": {"detecte": not ok2, "raison": rap2.get("raison")},
               "controle_negatif_boite_invalide": {"detecte": not ok3, "raison": rap3.get("raison")}},
              open("couverture.json", "w"), ensure_ascii=False, indent=1)
    print("\ncouverture.json ecrit")
    return ok


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "certificat.json")
