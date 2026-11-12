"""Certificat par boîte, en forme corrigée : couverture complète, arithmétique exacte.

Ce que ce fichier établit, et sur quoi
--------------------------------------
Pour une région close du domaine des modules, il produit une couverture FINIE en boîtes telles
que, sur chacune, le moteur `obligations.certifie_boite` prouve :

  (i)   le diamètre de la cellule est < T   (hypothèse ε = D/T < 1 de `Pont.lemmeB`) ;
  (ii)  pour les 21 paires d'une clique de sept décalages, un couple de sommets u, v de la
        cellule avec |u − (v + d)|² ≤ T²   (témoins proches, `Boites.clique_de_temoins`) ;
  (iii) pour les 21 paires, un couple avec |u − (v + d)|² ≥ T²   (témoins lointains).

Le seuil T est celui de la boîte (un par boîte, comme le quantificateur ∀(g,h) ∃s l'exige),
et non le seuil figé de `omega_exact` — c'est la correction du geste 39. Les sommets sont
prouvés dans la cellule sur toute la boîte par `Boites.cell_of_fini` (contrainte automatique
au-delà de 2r, puis liste finie de contraintes), ce qui rend les témoins valides partout.

Aucun flottant dans une décision : tout est en fractions, les encadrements sont des formes de
la moyenne sur des polynômes exacts, et l'on n'encadre jamais deux quantités pour les comparer
(règle du dossier : une seule fonction différence).

Reproduire
----------
    cd dossiers/note && python3 obligations_boites.py

Sortie : `obligations_boites.json` (boîtes, seuils, cliques, marges) et la même chose en clair.
"""
import json
import sys
from fractions import Fraction as F

sys.path.insert(0, "/home/user/Recherches-maths/dossiers/note")
import obligations as O

# Les deux boîtes de l'export initial (h ∈ [433/500, 9/10]), celles du point bloquant.
REGIONS = [
    ("boite 0 (g < 0)", F(-1, 2), F(-1, 4), F(433, 500), F(9, 10)),
    ("boite 1 (g > 0)", F(1, 4), F(1, 2), F(433, 500), F(9, 10)),
]
PROF_MAX = 9


def main():
    rapport = {"regions": [], "profondeur_max": PROF_MAX}
    total_ok = True
    for (nom, g0, g1, h0, h1) in REGIONS:
        feuilles, echecs, essais = O.couvre(g0, g1, h0, h1, prof_max=PROF_MAX)
        aire = sum((b[1] - b[0]) * (b[3] - b[2]) for b in feuilles)
        tot = (g1 - g0) * (h1 - h0)
        ok = (not echecs) and aire == tot
        total_ok = total_ok and ok
        print(f"{nom} : g ∈ [{g0}, {g1}], h ∈ [{h0}, {h1}]")
        print(f"  {len(feuilles)} feuilles certifiées, {len(echecs)} échec(s), {essais} essais")
        print(f"  aire couverte = {aire} / {tot} = {float(aire / tot):.6f}  "
              f"{'COMPLET' if ok else 'INCOMPLET'}")
        detail = []
        for (a, b_, c, d, r) in feuilles:
            detail.append({"g": [str(a), str(b_)], "h": [str(c), str(d)], "T2": r["T2"],
                           "clique": r["clique"], "sommets_prouves": r["sommets_prouves"],
                           "diam2_sup": r["diam2_sup"],
                           "marge_proche": r["marge_proche"], "marge_loin": r["marge_loin"]})
        rapport["regions"].append({
            "nom": nom, "g": [str(g0), str(g1)], "h": [str(h0), str(h1)],
            "feuilles": len(feuilles), "echecs": len(echecs), "essais": essais,
            "aire": str(aire), "aire_totale": str(tot), "complet": ok, "detail": detail,
        })
        if echecs:
            for e in echecs[:5]:
                print(f"    reste : g ∈ [{e[0]}, {e[1]}], h ∈ [{e[2]}, {e[3]}] — "
                      f"{e[4].get('raison')}")
        print()

    rapport["tout_complet"] = total_ok
    with open("obligations_boites.json", "w") as fh:
        json.dump(rapport, fh, ensure_ascii=False, indent=1)
    print("écrit obligations_boites.json —", "COUVERTURE COMPLÈTE" if total_ok else "INCOMPLET")
    return 0 if total_ok else 1


if __name__ == "__main__":
    sys.exit(main())
