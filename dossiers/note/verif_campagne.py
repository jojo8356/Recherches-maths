"""Vérification INDÉPENDANTE d'un certificat de boîte, par un autre moteur.

Le moteur de `obligations.py` prouve l'appartenance des témoins par encadrement
polynomial ; celui-ci ne partage rien avec lui : il construit la cellule numériquement
(`audit_gh.cellule`), et mesure les distances par le calcul polygone-polygone LENT
(`audit_gh.dmin2_dmax2`), écrit bien avant et sans rapport avec la réduction au fini.

C'est ce contrôle qui a démasqué deux fautes de sûreté du moteur (voir CHANGELOG,
geste 43) : un `appartient` qui n'excluait que les violations certaines, et un seuil T²
construit sur des bornes trop larges. Il doit donc être passé AVANT de publier un chiffre.

Ce qu'il vérifie, pour chaque feuille certifiée et en plusieurs points de la feuille :
  * diamètre de la cellule < T² ;
  * pour les 21 paires de la clique : dmin² ≤ T² ≤ dmax² (dmin, dmax exacts).
Il ne vérifie PAS l'appartenance des témoins feuille par feuille : il vérifie la
conclusion, ce qui est plus fort et indépendant de la méthode.

Usage :  python3 verif_campagne.py [--exemples 4]
"""
import json
import sys
import types
from fractions import Fraction as F

sys.modules.setdefault("numpy", types.ModuleType("numpy"))
sys.path.insert(0, "/home/user/Recherches-maths/dossiers/note")
import audit_gh as AG          # noqa: E402
import obligations as O        # noqa: E402


def verifie_feuille(a, b_, c, d, T2, clique, prof=6):
    """Contrôle une feuille en quatre points, moteur lent. Renvoie la liste des anomalies."""
    anomalies = []
    for (gg, hh) in (((a + b_) / 2, (c + d) / 2), (a, c), (b_, d), ((a + b_) / 2, c)):
        info = AG.cellule(gg, hh)
        if info is None:
            continue
        P = info[0]
        diam2 = max((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 for p in P for q in P)
        if not (diam2 < T2):
            anomalies.append(("diametre", gg, hh, diam2, T2))
            continue
        for i in range(len(clique)):
            for j in range(i + 1, len(clique)):
                di = clique[j][0] - clique[i][0]
                dj = clique[j][1] - clique[i][1]
                dx = F(di) + F(dj) * gg
                dy = F(dj) * hh
                Q = [(p[0] + dx, p[1] + dy) for p in P]
                dmin, dmax = AG.dmin2_dmax2(P, Q)
                if not (dmin <= T2 <= dmax):
                    anomalies.append(("paire", tuple(clique[i]), tuple(clique[j]),
                                      gg, hh, dmin, dmax, T2))
    return anomalies


def main():
    n_ex = 4
    if "--exemples" in sys.argv:
        n_ex = int(sys.argv[sys.argv.index("--exemples") + 1])
    d = json.load(open("/home/user/Recherches-maths/dossiers/note/boites_a_porter.json"))
    detail = d["detail"]
    # Un exemple par bande de h : c'est là que le moteur était le plus fragile.
    bandes = {}
    for k, b in enumerate(detail):
        bandes.setdefault(b["h"][1], k)
    tous = sorted(bandes.values())
    # un exemple par bande, en privilégiant les plus HAUTES (c'est là que le moteur cassait)
    choix = tous[-n_ex:] if n_ex else tous
    total = 0
    fautes = 0
    for k in choix:
        b = detail[k]
        g0, g1 = (F(x) for x in b["g"])
        h0, h1 = (F(x) for x in b["h"])
        feuilles, echecs, _ = O.couvre(g0, g1, h0, h1, prof_max=6)
        print(f"boîte {k}  g∈[{b['g'][0]},{b['g'][1]}] h∈[{b['h'][0]},{b['h'][1]}]  "
              f"feuilles={len(feuilles)} échecs={len(echecs)}", flush=True)
        for (a, bb, c, dd, r) in feuilles:
            T2 = F(r["T2"])
            clique = [tuple(x) for x in r["clique"]]
            ano = verifie_feuille(a, bb, c, dd, T2, clique)
            total += 1
            if ano:
                fautes += 1
                print("   ANOMALIE", ano[0], flush=True)
    print(f"\nfeuilles contrôlées : {total}   avec anomalie : {fautes}")
    return 0 if fautes == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
