"""AUDIT S-V — couverture de la QUEUE h -> infini, dans le repère w = 1/h.

Idée
----
Le repère u = 1/h rend la queue bornée mais y dégénère (le vecteur (1,0) s'écrase) : écarté.
Ce qui ne dégénère pas, ce sont les RAPPORTS dmin/D et dmax/D, qui ont des limites finies.
On change donc de repère sur les rapports : w = 1/h, et toutes les conditions du certificat
sont écrites sous forme de rapports de degrés égaux en h (voir signe_rapport_w).

Une boîte en w est FERMÉE : w ∈ [w0, w1] représente h ∈ [1/w1, 1/w0]. Contrairement à une
boîte en h, elle est bornée dans le repère de certification même quand h -> ∞.

Ce que ce script prouve, et ce qu'il ne prouve pas
-------------------------------------------------
Il prouve : pour chaque feuille certifiée, χ ≥ 7 pour TOUS les réseaux (g, h) de la boîte,
donc uniformément en h sur la plage couverte. Si la couverture d'une fenêtre [w0, w1] avec
w0 > 0 est complète, la queue est prouvée sur h ∈ [1/w1, 1/w0].

Il ne prouve pas le point w = 0 (h = ∞) : le motif de conflit est une rangée horizontale dont
le PAS croît linéairement en h (pas ≈ h·sqrt(1/eps² − 1)), donc les décalages entiers à
prouver changent avec h. Aucune boîte de la forme [0, w1] ne peut donc être certifiée : il
faut un argument asymptotique séparé, puis un recouvrement fini [w0, w1] raccordé à lui.
"""
import argparse
import json
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, ".")
import audit_certificat3 as C3                       # noqa: E402

try:                                                 # pont Rust (facultatif)
    import gabarit_rust as GR
    RUST_DISPO = GR.disponible()
except Exception:                                    # noqa: BLE001
    GR, RUST_DISPO = None, False

UTILISE_RUST = False

PROFMAX = 14
ECHS = [F(99, 100), F(199, 200), F(999, 1000), F(9999, 10000), F(99999, 100000)]


MOTIF = None


def couvre(g, w, n, prof, budget, stats, t0):
    if time.time() - t0 > budget:
        stats["budget"] = True
        return
    if w[1] <= 0:
        stats["hors"] += 1
        return
    # g = 0 est une droite de transition (réseau rectangulaire) : on ne la traverse pas
    if g[0] < 0 < g[1]:
        couvre((g[0], F(0)), w, n, prof, budget, stats, t0)
        couvre((F(0), g[1]), w, n, prof, budget, stats, t0)
        return
    stats["essais"] += 1
    derniere = None
    wc = (w[0] + w[1]) / 2
    if wc <= 0:                       # boîte collée à w = 0 : prendre un point intérieur
        wc = w[1] / 2
    hc = 1 / wc
    for ech in ECHS:
        try:
            mot = MOTIF((g[0] + g[1]) / 2, hc, ech)
            r = C3.certifie_w_avec_retrait(g, w, ech, mot)
            stats["feuilles"] += 1
            stats["par_ech"][str(ech)] = stats["par_ech"].get(str(ech), 0) + 1
            stats["boites"].append({"g": [str(g[0]), str(g[1])], "w": [str(w[0]), str(w[1])],
                                    "h_min": str(1 / w[1]) if w[1] else None,
                                    "ech": str(ech), **r})
            return
        except Exception as e:                                # noqa: BLE001
            derniere = e
            stats["par_raison"][str(e)[:40]] = stats["par_raison"].get(str(e)[:40], 0) + 1
    stats["echecs"].append({"g": [str(g[0]), str(g[1])], "w": [str(w[0]), str(w[1])],
                            "raison": str(derniere)[:120], "prof": prof})
    if prof >= PROFMAX:
        stats["limite_prof"] += 1
        return
    lg, lw = g[1] - g[0], w[1] - w[0]
    if lg >= lw:
        m = (g[0] + g[1]) / 2
        if m == 0 or m in g:
            m = (w[0] + w[1]) / 2
            couvre(g, (w[0], m), n + 1, prof + 1, budget, stats, t0)
            couvre(g, (m, w[1]), n + 1, prof + 1, budget, stats, t0)
        else:
            couvre((g[0], m), w, n + 1, prof + 1, budget, stats, t0)
            couvre((m, g[1]), w, n + 1, prof + 1, budget, stats, t0)
    else:
        m = (w[0] + w[1]) / 2
        couvre(g, (w[0], m), n + 1, prof + 1, budget, stats, t0)
        couvre(g, (m, w[1]), n + 1, prof + 1, budget, stats, t0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g0", default="-1/2")
    ap.add_argument("--g1", default="1/2")
    ap.add_argument("--w0", default="1/20")
    ap.add_argument("--w1", default="1/10")
    ap.add_argument("--budget", type=float, default=240)
    ap.add_argument("--profmax", type=int, default=14)
    ap.add_argument("--echs", default="")
    ap.add_argument("--rust", action="store_true",
                    help="gabarits par le moteur Rust (temps constant en h)")
    ap.add_argument("--queue", action="store_true",
                    help="motif à fenêtre large (indispensable dès que h dépasse ~30)")
    ap.add_argument("--sortie", default="audit_w.json")
    a = ap.parse_args()
    global PROFMAX, ECHS, MOTIF
    PROFMAX = a.profmax
    global UTILISE_RUST
    UTILISE_RUST = bool(a.rust and RUST_DISPO)
    if a.rust and not RUST_DISPO:
        print("  [rust indisponible : repli sur le Python]")
    if UTILISE_RUST:
        def MOTIF(gc, hc, ech):                      # noqa: N802
            try:
                return GR.motif_rust(gc, hc, ech)
            except Exception:                        # noqa: BLE001
                # Le repli Python coûte O(h) et devient inutilisable au-delà de h ≈ 50 :
                # au-delà, on échoue franchement (la boîte sera subdivisée) plutôt que
                # de relancer le chemin lent.
                if hc > 50:
                    raise
                return C3.motif_queue(gc, hc, ech)
    else:
        MOTIF = C3.motif_queue if a.queue else C3.motif_au_centre
    if a.echs:
        ECHS = [F(x) for x in a.echs.split(",")]
    t0 = time.time()
    stats = {"feuilles": 0, "essais": 0, "hors": 0, "limite_prof": 0, "budget": False,
             "boites": [], "echecs": [], "par_ech": {}, "par_raison": {}}
    couvre((F(a.g0), F(a.g1)), (F(a.w0), F(a.w1)), 0, 0, a.budget, stats, t0)
    aire = sum(float(F(b["g"][1]) - F(b["g"][0])) * float(F(b["w"][1]) - F(b["w"][0]))
               for b in stats["boites"])
    attendu = float((F(a.g1) - F(a.g0)) * (F(a.w1) - F(a.w0)))
    gmin = min((F(b["g"][0]) for b in stats["boites"]), default=None)
    gmax = max((F(b["g"][1]) for b in stats["boites"]), default=None)
    hmin = min((F(b["h_min"]) for b in stats["boites"] if b["h_min"]), default=None)
    print(f"\n=== QUEUE en w  g ∈ [{a.g0}, {a.g1}]  w ∈ [{a.w0}, {a.w1}]  "
          f"(h ≥ {float(1/F(a.w1)):.3g}) ===")
    print(f"  essais {stats['essais']} | feuilles {stats['feuilles']} | "
          f"échecs {len(stats['echecs'])} | profondeur limite {stats['limite_prof']} | "
          f"{time.time() - t0:.1f} s")
    print(f"  aire certifiée {aire:.6f} / {attendu:.6f}  (manque {attendu - aire:.2e})")
    if stats["par_ech"]:
        print("  échelles :", ", ".join(f"{k} ×{v}" for k, v in
                                        sorted(stats["par_ech"].items(), key=lambda z: -z[1])))
    if stats["par_raison"]:
        print("  motifs d'échec :", "; ".join(f"{k} ×{v}" for k, v in
                                              sorted(stats["par_raison"].items(),
                                                     key=lambda z: -z[1])[:4]))
    if stats["boites"]:
        print(f"  g couvert [{float(gmin):.5f}, {float(gmax):.5f}] | h ≥ {float(hmin):.6g}")
    ok = attendu - aire < 1e-12 and not stats["budget"]
    print(f"  VERDICT : {'COMPLET sur la fenêtre' if ok else 'INCOMPLET'}")
    json.dump(stats, open(a.sortie, "w"), indent=1)
    print(f"  écrit {a.sortie}")


if __name__ == "__main__":
    main()
