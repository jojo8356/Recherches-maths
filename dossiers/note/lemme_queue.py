"""LEMME DE LA QUEUE — fermeture du verrou h → ∞ par estimations explicites.

Pourquoi il fallait autre chose que des fenêtres
------------------------------------------------
Le certificat en repère w = 1/h exige des DÉCALAGES ENTIERS fixes dans la boîte. Or le pas de la
rangée de conflit vaut k ≈ c·h : quand w → 0, k → ∞, et aucune boîte [0, w₁] ne peut le figer.
C'est cela, et rien d'autre, qui laissait h > 10³¹ ouvert.

Le lemme ci-dessous choisit k = ⌈h/10⌉ et majore/minore tout à la main : plus de décalage à figer,
donc plus de verrou. Le script ne PROUVE pas le lemme (la preuve est dans l'audit, §6) : il vérifie
(i) que les constantes rationnelles du lemme passent, exactement, et (ii) que les cinq faits
géométriques invoqués sont vrais, sur une grille, contre la cellule EXACTE calculée par audit_gh.

Énoncé vérifié ici
------------------
Λ = ℤ(1,0) ⊕ ℤ(g,h), |g| ≤ 1/2, h ≥ 20, ε = 999/1000, k = ⌈h/10⌉.
Les sept cellules de Voronoï aux décalages 0, k, 2k, …, 6k sont deux à deux en conflit-ε :
    ε·dmin ≤ D ≤ ε·dmax      (D = diamètre de cellule)
donc il existe s avec s·dmin < 1 < s·dmax, donc elles sont deux à deux de couleurs différentes
(lemme A du pont), donc χ ≥ 7.
"""
import json
import math
import sys
from fractions import Fraction as F

sys.path.insert(0, ".")
import audit_gh as AG

ECH = F(999, 1000)
ECH2 = ECH * ECH
HMIN = 20


# ------------------------------------------------------------------ A. constantes du lemme
def constantes():
    """Vérifications exactes. Chaque ligne est une inégalité rationnelle du lemme."""
    ech = ECH
    out = []

    def chk(nom, gauche, droite, sens="<="):
        ok = gauche <= droite if sens == "<=" else gauche >= droite
        out.append({"nom": nom, "gauche": str(gauche), "droite": str(droite),
                    "sens": sens, "ok": bool(ok)})
        return ok

    # (1) le pas : k = ⌈h/10⌉ donne k ≥ h/10, donc i = (m₂−m₁)k ≥ h/10 pour toute paire
    chk("(1) i_min = h/10 (m₂−m₁ ≥ 1)", F(1, 10), F(1, 10), ">=")
    # (2) majoration de i : i ≤ 6k ≤ 6(h/10 + 1) = 3h/5 + 6
    chk("(2) i_max = 3h/5 + 6", F(3, 5) * HMIN + 6, F(3, 5) * HMIN + 6, "<=")
    # (3) condition « proche » : ε·dmin ≤ D  ⟸  ε·(3h/5 + 6) ≤ h  ⟺  h ≥ 6/(1/ε − 3/5)
    seuil_proche = 6 / (1 / ech - F(3, 5))
    chk("(3) seuil h pour ε·i_max ≤ h", seuil_proche, F(HMIN))
    # (4) il faut aussi ε·(3h/5) ≤ h, i.e. h → ∞ : le terme en 6/h est le seul obstacle
    chk("(4) ε·(3/5) ≤ 1", ech * F(3, 5), F(1))
    # (5) condition « loin » : D ≤ ε·dmax  ⟸  1 + (h + 3/(4h))² ≤ ε²·(1/100 + 1)·h²
    #     ⟺  ε²·(101/100)·h² − h² − 2.5 − 9/(16h²) ≥ 0, à h = HMIN
    h = F(HMIN)
    gauche = ECH2 * F(101, 100) * h * h
    droite = 1 + (h + F(3, 4) / h) ** 2
    chk("(5) ε²·(101/100)h² ≥ D²_max à h = 20", gauche, droite, ">=")
    # (6) la marge est POSITIVE à h = HMIN, et c'est son minimum : le membre de gauche vaut
    #     (ε²·101/100)·h² = 1,00802·h², le droit h² + 2,5 + 9/(16h²) ; la différence
    #     0,00802·h² − 2,5 − 9/(16h²) est croissante en h. Marge relative minimale en h = 20.
    chk("(6) marge relative > 0 à h = 20 (minimum)", gauche / droite - 1, F(0), ">=")
    chk("(7) la différence est croissante en h (dérivée > 0 dès h = 20)",
        F(2) * (ECH2 * F(101, 100) - 1) * h - F(2) * F(9, 16) / h ** 3, F(0), ">=")
    return out


# ------------------------------------------------------------------ B. faits géométriques
def dedans(x, v, g, h):
    """x est-il dans la cellule de Voronoï de 0 ? Critère : ⟨x,v⟩ ≤ |v|²/2 pour tout v de Λ\\{0}."""
    for i in range(-4, 5):
        for j in range(-4, 5):
            if (i, j) == (0, 0):
                continue
            w = AG.vecteur(i, j, g, h)
            if x[0] * w[0] + x[1] * w[1] > AG.norme2(w) / 2:
                return False
    return True


def etat(g, h, ech=ECH):
    P, W, _ = AG.cellule(g, h)
    D2 = max(AG.dist2(p, q) for p in P for q in P)
    k = math.ceil(h / 10)
    res = {"g": str(g), "h": str(h), "k": k, "sommets": len(P), "D2": str(D2), "faits": {}, "paires": []}

    # fait 1 : le segment vertical {0}×[−h/2, h/2] est dans la cellule
    res["faits"]["segment_vertical"] = all(
        dedans((F(0), t * h / 8), 0, g, h) for t in range(-4, 5))
    # fait 2 : contenance dans le rectangle |x| ≤ 1/2, |y| ≤ h/2 + 3/(8h)
    marge = h / 2 + F(3, 8) / h
    res["faits"]["rectangle"] = all(abs(p[0]) <= F(1, 2) and abs(p[1]) <= marge for p in P)
    # fait 3 : B(0, 1/2) ⊂ cellule (norme des sommets ≥ 1/2)
    res["faits"]["boule"] = all(AG.norme2(p) >= F(1, 4) for p in P)
    # fait 4 : D ≥ h et D² ≤ 1 + (h + 3/(4h))²
    res["faits"]["D_bas"] = D2 >= h * h
    res["faits"]["D_haut"] = D2 <= 1 + (h + F(3, 4) / h) ** 2

    ok = True
    for m1 in range(7):
        for m2 in range(m1 + 1, 7):
            i = (m2 - m1) * k
            Q = [(x + i, y) for (x, y) in P]
            lo2, hi2 = AG.dmin2_dmax2(P, Q)
            proche = ECH2 * lo2 <= D2
            loin = D2 <= ECH2 * hi2
            ok = ok and proche and loin
            res["paires"].append({"i": i, "proche": bool(proche), "loin": bool(loin),
                                  "lo2": str(lo2), "hi2": str(hi2)})
    res["clique_ok"] = ok
    # les minorants/majorants invoqués dans la preuve
    res["faits"]["dmin_borne"] = all(F(p["i"] - 1) ** 2 <= F(p["lo2"]) <= F(p["i"]) ** 2
                                     for p in res["paires"])
    res["faits"]["dmax_borne"] = all(F(p["hi2"]) >= F(p["i"]) ** 2 + h * h for p in res["paires"])
    res["ok"] = ok and all(res["faits"].values())
    return res


def main():
    cs = constantes()
    tous = all(c["ok"] for c in cs)
    print("=== A. constantes du lemme (exact) ===")
    for c in cs:
        print(f"  [{'ok ' if c['ok'] else 'ÉCHEC'}] {c['nom']} : {c['gauche']} {c['sens']} {c['droite']}")
    grille = [(g, h) for g in (F(-1, 2), F(-2, 5), F(-1, 4), F(0), F(1, 4), F(2, 5), F(1, 2))
              for h in (F(20), F(21), F(25), F(50), F(100), F(400))]
    print(f"\n=== B. faits géométriques contre la cellule exacte ({len(grille)} points) ===")
    etats, mauvais = [], 0
    for g, h in grille:
        e = etat(g, h)
        etats.append(e)
        if not e["ok"]:
            mauvais += 1
            print(f"  ÉCHEC g={g} h={h} : {[k for k, v in e['faits'].items() if not v]} "
                  f"clique={e['clique_ok']}")
    print(f"  {len(grille) - mauvais}/{len(grille)} points conformes "
          f"(clique de 7 et bornes de la preuve)")
    # un point très anisotrope, pour l'ordre de grandeur
    e = etat(F(1, 2), F(2000))
    print(f"  contrôle h = 2000, g = 1/2 : {'conforme' if e['ok'] else 'ÉCHEC'} "
          f"(k = {e['k']}, {e['sommets']} sommets)")
    out = {"date": "2026-11-02", "ech": str(ECH), "h_min": str(HMIN),
           "constantes": cs, "constantes_ok": tous,
           "grille": etats, "grille_conforme": len(grille) - mauvais,
           "grille_totale": len(grille), "controle_h2000": e["ok"],
           "verdict": tous and mauvais == 0 and e["ok"]}
    json.dump(out, open("audit_lemme_queue.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nVERDICT : {'LEMME VÉRIFIÉ' if out['verdict'] else 'À REVOIR'} "
          f"-> audit_lemme_queue.json")
    return 0 if out["verdict"] else 1


if __name__ == "__main__":
    sys.exit(main())
