"""Reprise de T8 sous les deux conventions de tangence, plus la carte delta* stricte."""
import json, time
import coloriage as K
import tangence

t0 = time.time()
RES = {"coloriage": [], "coloriage_strict": [], "delta_etoile_strict": {}, "delta_etoile_large": {}}

RESEAUX = [(1.0, 60, "hexagonal"), (1.0, 90, "carre"), (2.0, 90, "rectangulaire"),
           (1.9, 70, "anisotrope"), (1.4, 100, "divers")]
DELTAS = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.98]

for (rho, th, nom) in RESEAUX:
    for d in DELTAS:
        ws, wl = tangence.omega_deux(rho, th, d)
        ok_l, n_l, _, _ = K.chercher(rho, th, d, mmax=24, verbose=False, convention="large")
        ok_s, n_s, abc_s, _ = K.chercher(rho, th, d, mmax=24, verbose=False, convention="strict")
        RES["coloriage"].append(dict(reseau=nom, rho=rho, theta=th, delta=d, omega_strict=ws,
                                     omega_large=wl, six=ok_l, sous_reseaux=n_l))
        RES["coloriage_strict"].append(dict(reseau=nom, rho=rho, theta=th, delta=d,
                                            six=ok_s, sous_reseaux=n_s,
                                            sous_reseau=abc_s if ok_s else None))
        print(f"{nom:12s} d={d:.2f} omega {ws}/{wl} | 6-coloriage large={ok_l} strict={ok_s} "
              f"({n_l}/{n_s} sous-reseaux sans boucle) [{time.time()-t0:.0f}s]", flush=True)

# carte delta* : plus grande echelle ou omega <= 6, sous chaque convention
pay = json.load(open("paysage.json"))
for th in pay["theta"]:
    for rho in pay["rho"]:
        ds_l = ds_s = None
        for d in pay["delta"]:
            ws, wl = tangence.omega_deux(th and rho, th, d)
            if wl <= 6: ds_l = d
            if ws <= 6: ds_s = d
        RES["delta_etoile_large"][f"{th},{rho:.4f}"] = ds_l
        RES["delta_etoile_strict"][f"{th},{rho:.4f}"] = ds_s
    print(f"  carte : theta={th} fait [{time.time()-t0:.0f}s]", flush=True)

json.dump(RES, open("conventions.json", "w"), ensure_ascii=False)
print("ecrit conventions.json")
