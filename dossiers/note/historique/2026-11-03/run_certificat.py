"""Balayage adaptatif du certificat : couvre [1,2] x [60,120] par des boites
certifiees, en subdivisant celles qui resistent."""
import json
import sys
import time

from certificat import certifie

RHO0, RHO1 = 1.0, 2.0
TH0, TH1 = 60.0, 120.0


def run(nr0=5, nt0=10, prof_max=12, budget=3000.0, verbose=True):
    t0 = time.time()
    out = []           # (rho0,rho1,th0,th1,depth,ok,info)
    dr = (RHO1 - RHO0) / nr0
    dt = (TH1 - TH0) / nt0
    niveau = [(RHO0 + i * dr, RHO0 + (i + 1) * dr, TH0 + j * dt, TH0 + (j + 1) * dt, 0)
              for i in range(nr0) for j in range(nt0)]
    n_ok = n_ko = 0
    stop = False
    prof = 0
    while niveau and not stop:
        suivant = []
        for (a, b, c, d, p) in niveau:
            ok, info = certifie(a, b, c, d)
            if ok:
                n_ok += 1
                out.append((a, b, c, d, p, True, info))
            elif p >= prof_max:
                n_ko += 1
                out.append((a, b, c, d, p, False, info))
            else:
                am, cm = (a + b) / 2, (c + d) / 2
                suivant += [(a, am, c, cm, p + 1), (a, am, cm, d, p + 1),
                            (am, b, c, cm, p + 1), (am, b, cm, d, p + 1)]
        if verbose:
            print(f"profondeur {prof} : {len(niveau)} boites -> {n_ok} certifiees, "
                  f"{n_ko} echecs, {len(suivant)} a subdiviser, {time.time()-t0:.0f}s",
                  flush=True)
        niveau = suivant
        prof += 1
        if time.time() - t0 > budget:
            print("  budget de temps atteint", flush=True)
            stop = True
    return out, niveau, time.time() - t0


if __name__ == "__main__":
    nr0 = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    nt0 = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    prof_max = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    out, reste, dt_ = run(nr0, nt0, prof_max)
    tot = sum((b - a) * (d - c) for (a, b, c, d, p, ok, _i) in out) + \
          sum((b - a) * (d - c) for (a, b, c, d, p) in reste)
    aire_ok = sum((b - a) * (d - c) for (a, b, c, d, p, ok, _i) in out if ok)
    print(f"\nboites: {len(out)} (certifiees {sum(1 for o in out if o[5])}, "
          f"echecs {sum(1 for o in out if not o[5])}), reste {len(reste)}")
    print(f"aire certifiee : {100*aire_ok/tot:.4f} %  ({dt_:.0f}s)")
    marg = [o[6]['marge'] for o in out if o[5]]
    if marg:
        print(f"marge minimale : {min(marg):.4f}  (mediane {sorted(marg)[len(marg)//2]:.4f})")
    # sauvegarde
    res = {"date": "2026-11-03",
           "domaine": {"rho": [RHO0, RHO1], "theta": [TH0, TH1]},
           "grille_initiale": [nr0, nt0], "profondeur_max": prof_max,
           "boites": [[round(o[0], 8), round(o[1], 8), round(o[2], 6), round(o[3], 6),
                       o[4], bool(o[5]),
                       (round(o[6].get('marge', -1), 6) if o[5] else o[6].get('raison'))
                       ] for o in out],
           "aire_certifiee_pct": 100 * aire_ok / tot,
           "aire_totale": tot,
           "nb_boites": len(out),
           "nb_certifiees": sum(1 for o in out if o[5]),
           "nb_echecs": sum(1 for o in out if not o[5]),
           "temps_s": round(dt_, 1)}
    with open("certificat.json", "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("certificat.json ecrit :", len(open("certificat.json").read()), "octets")
