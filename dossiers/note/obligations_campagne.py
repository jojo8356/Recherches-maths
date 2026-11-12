"""Certificat par boîte sur les 36 boîtes restantes (geste 43).

Où l'on en est
--------------
Le geste 40 a certifié les boîtes 0 et 1 (h ∈ [433/500, 9/10], g ∈ [−1/2,−1/4] et [1/4,1/2]),
couverture 100 %, 17 feuilles chacune, en arithmétique rationnelle exacte. La région résiduelle
que `Queue.lean` ne couvre pas est h ∈ [√3/2 ; 15[ ; elle est découpée en 38 boîtes
(`boites_a_porter.json`). Ce fichier traite les 36 autres.

Ce qui a été corrigé pour y arriver
-----------------------------------
Sur la boîte h ∈ [8, 15], le certificat ne terminait pas. Cause : le rayon r de
`cell_of_fini` était tiré des CANDIDATS (intersections de paires de contraintes), et l'un de ces
candidats est à |s|² ≈ 4,1·10¹⁰ alors qu'il n'est pas dans la cellule. La liste de contraintes
explosait. Deux corrections :

  * majorant GÉOMÉTRIQUE du rayon (la cellule est dans |x| ≤ 1 et |y| ≤ h+1) ;
  * échelle de rayons croissants : chaque preuve est complète à son propre rayon, donc on
    commence petit et on double seulement si moins de trois sommets passent.

Ce que le script produit
------------------------
Par boîte : statut (certifiée / partielle / trop longue), nombre de feuilles, aire couverte en
fraction exacte, et si tout est allé jusqu'au bout. Un budget de temps par boîte évite qu'une
boîte récalcitrante bloque la campagne — et le statut « trop long » est distingué de « faux »,
parce que ce n'est pas la même chose et qu'il ne faut pas les confondre.

Usage :  python3 obligations_campagne.py [--budget SECONDES]
"""
import json
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, "/home/user/Recherches-maths/dossiers/note")
import obligations as O

PROF_MAX = 6
BUDGET = 600          # secondes par boîte ; au-delà, statut « trop long » (pas « faux »)


def traite(n, b, budget):
    g0, g1 = (F(x) for x in b["g"])
    h0, h1 = (F(x) for x in b["h"])
    t0 = time.time()
    feuilles, echecs, essais = O.couvre(g0, g1, h0, h1, prof_max=PROF_MAX,
                                        echeance=t0 + budget)
    aire = sum((f[1] - f[0]) * (f[3] - f[2]) for f in feuilles)
    tot = (g1 - g0) * (h1 - h0)
    longues = [e for e in echecs if "trop long" in str(e[4].get("raison", ""))]
    profonds = [e for e in echecs if "trop long" not in str(e[4].get("raison", ""))]
    if profonds:
        statut = "incomplete"
    elif longues:
        statut = "trop_longue"
    else:
        statut = "certifiee"
    return {
        "boite": n, "g": [str(g0), str(g1)], "h": [str(h0), str(h1)],
        "statut": statut, "feuilles": len(feuilles), "echecs": len(echecs),
        "essais": essais, "aire": str(aire), "aire_totale": str(tot),
        "fraction": float(aire / tot) if tot else 0.0,
        "secondes": round(time.time() - t0, 1),
        "reste": [{"g": [str(e[0]), str(e[1])], "h": [str(e[2]), str(e[3])],
                   "raison": str(e[4].get("raison", ""))[:90]} for e in echecs[:4]],
    }


def main():
    budget = BUDGET
    if "--budget" in sys.argv:
        budget = int(sys.argv[sys.argv.index("--budget") + 1])
    d = json.load(open("/home/user/Recherches-maths/dossiers/note/boites_a_porter.json"))

    # Les boîtes 0 et 1 sont déjà certifiées (geste 40) ; on reprend les 36 autres.
    deja = {0, 1}
    a_faire = [(n, b) for (n, b) in enumerate(d["detail"]) if n not in deja]

    # Les plus douces d'abord : petit h, donc cellule petite et encadrement plus serré.
    a_faire.sort(key=lambda t: F(t[1]["h"][1]))

    resultats = []
    print(f"{len(a_faire)} boîtes à traiter, budget {budget} s chacune\n", flush=True)
    print(f"{'boîte':>5} {'h':>16} {'statut':>11} {'feuilles':>8} {'aire':>8} {'s':>6}",
          flush=True)
    for (n, b) in a_faire:
        r = traite(n, b, budget)
        resultats.append(r)
        print(f"{n:5d} {b['h'][0] + '..' + b['h'][1]:>16} {r['statut']:>11} "
              f"{r['feuilles']:8d} {r['fraction']:8.4f} {r['secondes']:6.0f}", flush=True)

    cert = [r for r in resultats if r["statut"] == "certifiee"]
    inc = [r for r in resultats if r["statut"] == "incomplete"]
    lon = [r for r in resultats if r["statut"] == "trop_longue"]
    print(f"\ncertifiées : {len(cert)} / {len(resultats)}"
          f"   incomplètes : {len(inc)}   trop longues : {len(lon)}")
    with open("/home/user/Recherches-maths/dossiers/note/obligations_campagne.json", "w") as fh:
        json.dump({"budget_s": budget, "profondeur_max": PROF_MAX, "boites": resultats,
                   "certifiees": len(cert), "incompletes": len(inc),
                   "trop_longues": len(lon)}, fh, ensure_ascii=False, indent=1)
    print("écrit obligations_campagne.json")
    return 0 if not inc and not lon else 1


if __name__ == "__main__":
    sys.exit(main())
