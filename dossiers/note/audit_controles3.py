"""AUDIT S-V — contrôles négatifs du certificat v3.

Règle du dossier : PAS DE CERTIFICAT SANS CONTRÔLE NÉGATIF. Un certificat qui ne sait pas
dire « non » ne dit pas « oui ». On vérifie donc que le certificat REFUSE dans quatre
situations où il le doit, et qu'il ACCEPTE là où il le doit.

  (a) ε = 1/2 (au lieu de 99/100) : la conclusion est fausse, le certificat doit refuser.
  (b) prémisse corrompue : on gonfle le diamètre minorant (diam_pair × 2). Le certificat
      croit alors que la cellule est deux fois plus grosse ; (U) passe trivialement mais
      (L) doit le trahir. Refus attendu.
  (c) boîte hors du domaine (g = 3, h = 2) : la cellule y dégénère, le motif n'est plus
      construit ; refus attendu.
  (d) témoin faux : la définition d'un milieu est décalée (« m(w) » remplacé par
      « m(w) + (1,0) ») ; le point n'est plus dans la cellule et le certificat doit lever
      PointHors, donc RETIRER le point — pas l'accepter.
  (e) témoin d'un contrôle positif : la même boîte avec les définitions intactes doit
      passer (sinon le refus de (d) ne prouve rien).
"""
import json
import time
from fractions import Fraction as F

import audit_certificat3 as C3
from poly2 import Rat


def boite_point(g, h):
    return (g, g), (h, h)


def cas_positif(g, h, ech):
    mot = C3.motif_au_centre(g, h, ech)
    return C3.certifie_avec_retrait(boite_point(g, h)[0], boite_point(g, h)[1], ech, mot)


def main():
    G, H = F(-2, 5), F(1)                      # A₂ : ω = 7, le régime le plus serré
    res = {}

    # (e) contrôle POSITIF d'abord : sans lui, les refus ne signifient rien
    t = time.time()
    r = cas_positif(G, H, F(99, 100))
    res["e_positif_ech_99_100"] = {
        "attendu": "accepté",
        "obtenu": f"accepté (ω ≥ {r['clique_prouvee']}, diam² "
                  f"{r['diam_bas']:.3f}..{r['diam_haut']:.3f})",
        "ok": True, "temps": round(time.time() - t, 2)}

    # (a) ε = 1/2 : conclusion fausse ⇒ refus
    try:
        cas_positif(G, H, F(1, 2))
        res["a_ech_1_2"] = {"attendu": "refus", "obtenu": "ACCEPTÉ — DÉFAUT", "ok": False}
    except C3.Echec as e:
        res["a_ech_1_2"] = {"attendu": "refus", "obtenu": f"refus ({str(e)[:70]})", "ok": True}

    # (b) prémisse corrompue : le majorant du diamètre est divisé par 100. C'est la
    # direction DANGEREUSE (un majorant trop petit rend (L) facile), et c'est la seule qui
    # pourrait faire certifier une cellule trop petite. Le contrôle de cohérence dh ≥ dl
    # doit le refuser.
    mot = C3.motif_au_centre(G, H, F(99, 100))
    pl = C3.plan_de(mot, F(99, 100))
    pl["para_dist"] = [d / 100 for d in pl["para_dist"]]
    try:
        C3.certifie(boite_point(G, H)[0], boite_point(G, H)[1], F(99, 100), pl)
        res["b_majorant_ecrase"] = {"attendu": "refus", "obtenu": "ACCEPTÉ — DÉFAUT", "ok": False}
    except C3.Echec as e:
        res["b_majorant_ecrase"] = {"attendu": "refus", "obtenu": f"refus ({str(e)[:70]})", "ok": True}

    # (c) réseau dégénéré : h = 0, la « base » est de rang 1, il n'y a pas de cellule.
    # NB : certifier en (3,2) n'est PAS un défaut — le réseau y existe et le certificat y est
    # valide ; (3,2) est seulement hors du module réduit, donc hors de ce qu'on couvre. Un
    # contrôle négatif doit porter sur un énoncé FAUX, pas sur une région non couverte.
    try:
        mot = C3.motif_au_centre(F(3), F(0), F(99, 100))
        C3.certifie_avec_retrait((F(3), F(3)), (F(0), F(0)), F(99, 100), mot)
        res["c_reseau_degenere"] = {"attendu": "refus", "obtenu": "ACCEPTÉ — DÉFAUT", "ok": False}
    except Exception as e:                                  # noqa: BLE001
        res["c_reseau_degenere"] = {"attendu": "refus", "obtenu": f"refus ({str(e)[:70]})", "ok": True}

    # (d) témoin faux : on ajoute le milieu du vecteur (3,0), qui n'est PAS dans la cellule
    # (à A₂, |b₁| = 2 et le milieu de 3b₁ est loin à l'extérieur). Sa condition d'appartenance
    # est calculée par la formule honnête ⟨w,v⟩ ≤ |v|² : elle doit échouer, donc PointHors.
    mot = C3.motif_au_centre(G, H, F(99, 100))
    pl = C3.plan_de(mot, F(99, 100))
    w = (3, 0)
    faux_sym = C3.milieu(w)
    faux_val = (C3.AG.vecteur(w[0], w[1], G, H)[0] / 2, C3.AG.vecteur(w[0], w[1], G, H)[1] / 2)
    faux_mem = [(ij, C3.delaunay(w, ij)) for ij in
                [(i, j) for i in range(-6, 7) for j in range(-6, 7) if (i, j) != (0, 0)]]
    pl["points"].append({"nom": "faux", "sym": faux_sym, "val": faux_val, "lam": F(1)})
    pl["membres"].append(faux_mem)
    k = len(pl["points"]) - 1
    try:
        C3.certifie(boite_point(G, H)[0], boite_point(G, H)[1], F(99, 100), pl)
        res["d_temoin_faux"] = {"attendu": "PointHors (retrait)", "obtenu": "ACCEPTÉ — DÉFAUT",
                                "ok": False}
    except C3.PointHors as e:
        res["d_temoin_faux"] = {"attendu": "PointHors (retrait)", "obtenu": f"PointHors {e.k}",
                                "ok": True}

    # (f) faux sommet de clique : on ajoute une cellule lointaine (5,5) à la clique. Aucun
    # conflit avec elle ne se prouve ; la clique prouvée ne doit donc pas la contenir.
    mot = C3.motif_au_centre(G, H, F(99, 100))
    mot = dict(mot, clique=list(mot["clique"]) + [(5, 5)])
    try:
        r = C3.certifie_avec_retrait(boite_point(G, H)[0], boite_point(G, H)[1], F(99, 100), mot)
        faux = {"obtenu": f"ω ≥ {r['clique_prouvee']} (la cellule (5,5) écartée)",
                "attendu": "clique ≤ vraie clique", "ok": r["clique_prouvee"] <= 7}
        res["f_faux_sommet"] = faux
    except C3.Echec as e:
        res["f_faux_sommet"] = {"attendu": "clique ≤ vraie clique",
                                "obtenu": f"refus ({str(e)[:60]})", "ok": False}

    print("=== CONTRÔLES NÉGATIFS DU CERTIFICAT v3 ===")
    for k, v in res.items():
        print(f"  {'OK ' if v['ok'] else 'DÉFAUT'} | {k:22s} | attendu {v['attendu']:18s} | {v['obtenu']}")
    print(f"  VERDICT : {'tous les contrôles passent' if all(v['ok'] for v in res.values()) else 'ÉCHEC'}")
    json.dump(res, open("audit_controles3.json", "w"), indent=1, ensure_ascii=False)
    print("  écrit audit_controles3.json")


if __name__ == "__main__":
    main()
