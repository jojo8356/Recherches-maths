"""AUDIT S-V — couverture par le certificat v3 (témoins rétractés).

Différences avec le pilote v2
-----------------------------
1. On certifie avec `certifie_avec_retrait` (v3) : les points témoins dont l'appartenance
   échoue sont retirés un à un ; les témoins rétractés λp (λ = 1/2) survivent aux
   transitions, ce qui est le cas de la bande |g| ≤ 0,006 qui arrêtait la v2.
2. Une boîte à cheval sur g = 0 n'est JAMAIS certifiée d'un bloc : on la coupe en g = 0.
   À g = 0 le réseau est rectangulaire et le motif hexagonal dégénère ; c'est une droite
   de transition, pas un point. (La v3 sait certifier des boîtes de largeur 0,01 posées
   SUR g = 0 ; ce sont les boîtes symétriques autour qui coincent.)
3. Une boîte entièrement hors du domaine (g² + h² < 1 partout) est ignorée ; une boîte
   partiellement dehors est certifiée en entier, ce qui est plus fort que nécessaire.

Domaine : {|g| ≤ 1/2, g² + h² ≥ 1, h > 0}.
"""
import argparse
import json
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, ".")
import audit_certificat3 as C3                       # noqa: E402


def hors_domaine(g, h):
    """Vrai si la boîte est entièrement hors du domaine g²+h² ≥ 1 (test aux quatre coins)."""
    if max(abs(x) for x in g) > F(1, 2):
        return True
    if h[1] <= 0:
        return True
    m = max(x * x + y * y for x in g for y in h)      # coin le plus proche de l'origine
    return m < 1


PROFMAX = 12


ECHS = [F(99, 100)]          # échelles essayées, dans l'ordre


def couvre(g, h, n, prof, ech, budget, stats, t0):
    if time.time() - t0 > budget:
        stats["budget"] = True
        return
    if hors_domaine(g, h):
        stats["hors"] += 1
        return
    # couper à g = 0 : c'est une droite de transition, on ne la traverse pas d'un bloc
    if g[0] < 0 < g[1]:
        couvre((g[0], F(0)), h, n, prof, ech, budget, stats, t0)
        couvre((F(0), g[1]), h, n, prof, ech, budget, stats, t0)
        return
    stats["essais"] += 1
    derniere = None
    # L'échelle eps est LIBRE : la conclusion χ ≥ 7 vaut pour tout eps ∈ (0,1) tel que les
    # cellules aient un diamètre < 1. On prend donc la première échelle qui certifie — fixer
    # eps = 99/100 était une rigidité qui créait une bande marginale artificielle (au seuil
    # τ = D/eps, une paire cesse de se toucher dès que eps augmente un peu).
    for ech_essai in ECHS:
        try:
            mot = C3.motif_au_centre((g[0] + g[1]) / 2, (h[0] + h[1]) / 2, ech_essai)
            r = C3.certifie_avec_retrait(g, h, ech_essai, mot)
            stats["feuilles"] += 1
            stats["par_ech"][str(ech_essai)] = stats["par_ech"].get(str(ech_essai), 0) + 1
            stats["boites"].append({"g": [str(g[0]), str(g[1])], "h": [str(h[0]), str(h[1])],
                                    "ech": str(ech_essai), **r})
            return
        except Exception as e:                                # noqa: BLE001
            derniere = e
    stats["echecs"].append({"g": [str(g[0]), str(g[1])], "h": [str(h[0]), str(h[1])],
                            "raison": str(derniere)[:120], "prof": prof, "n": n})
    if prof >= PROFMAX:
        stats["limite_prof"] += 1
        return
    # subdivision : le plus long côté, sauf si la boîte touche g = 0 ou la frontière g²+h² = 1
    lg, lh = g[1] - g[0], h[1] - h[0]
    # On coupe TOUJOURS le côté le plus long. (Une version précédente coupait en g dès que la
    # boîte touchait g = 0 : elle produisait des boîtes de largeur 1e-4 et de hauteur 1, qui
    # épuisaient la profondeur sans jamais raffiner en h.)
    if lg >= lh:
        # on coupe en g (et jamais au milieu de g = 0 : voir le test plus haut)
        m = (g[0] + g[1]) / 2
        if m == 0 or m == g[0] or m == g[1]:
            m = (h[0] + h[1]) / 2
            couvre(g, (h[0], m), n + 1, prof + 1, ech, budget, stats, t0)
            couvre(g, (m, h[1]), n + 1, prof + 1, ech, budget, stats, t0)
        else:
            couvre((g[0], m), h, n + 1, prof + 1, ech, budget, stats, t0)
            couvre((m, g[1]), h, n + 1, prof + 1, ech, budget, stats, t0)
    else:
        m = (h[0] + h[1]) / 2
        couvre(g, (h[0], m), n + 1, prof + 1, ech, budget, stats, t0)
        couvre(g, (m, h[1]), n + 1, prof + 1, ech, budget, stats, t0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g0", default="-1/2")
    ap.add_argument("--g1", default="1/2")
    ap.add_argument("--h0", default="1")
    ap.add_argument("--h1", default="2")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--budget", type=float, default=300)
    ap.add_argument("--ech", default="99/100")
    ap.add_argument("--sortie", default="audit_v3.json")
    ap.add_argument("--profmax", type=int, default=12)
    ap.add_argument("--echs", default="99/100")
    a = ap.parse_args()
    global PROFMAX
    PROFMAX = a.profmax
    ech = F(a.ech)
    global ECHS
    ECHS = [F(x) for x in a.echs.split(",")]
    t0 = time.time()
    stats = {"feuilles": 0, "essais": 0, "hors": 0, "limite_prof": 0, "budget": False,
             "boites": [], "echecs": [], "par_ech": {}}
    couvre((F(a.g0), F(a.g1)), (F(a.h0), F(a.h1)), a.n, 0, ech, a.budget, stats, t0)
    aire = sum(float(F(b["g"][1]) - F(b["g"][0])) * float(F(b["h"][1]) - F(b["h"][0]))
               for b in stats["boites"])
    print(f"\n=== BILAN v3  g ∈ [{a.g0}, {a.g1}]  h ∈ [{a.h0}, {a.h1}]  ech = {ech} ===")
    print(f"  essais {stats['essais']} | feuilles certifiées {stats['feuilles']} | "
          f"échecs {len(stats['echecs'])} | hors domaine {stats['hors']} | "
          f"profondeur limite {stats['limite_prof']}")
    print(f"  aire certifiée {aire:.4f} en (g,h) | temps {time.time() - t0:.1f} s")
    if stats["budget"]:
        print("  [budget global atteint : couverture PARTIELLE]")
    # Le verdict porte sur l'AIRE NON COUVERTE, pas sur le nombre d'échecs intermédiaires :
    # une boîte qui échoue puis est subdivisée en boîtes certifiées est un succès.
    attendu = float((F(a.g1) - F(a.g0)) * (F(a.h1) - F(a.h0)))
    manque = attendu - aire
    print(f"  aire non couverte : {manque:.2e}")
    print(f"  VERDICT : {'COMPLET sur la fenêtre' if manque < 1e-12 and not stats['budget'] else 'INCOMPLET'}")
    json.dump(stats, open(a.sortie, "w"), indent=1)
    print(f"  écrit {a.sortie}")


if __name__ == "__main__":
    main()
