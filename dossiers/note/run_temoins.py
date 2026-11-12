"""Re-emission du certificat AVEC ses temoins.

Le certificat de 2026-11-03 ne conservait que la conclusion par boite (« ok », marge).
Un certificat verifiable doit porter ses temoins : sans eux, un controle independant ne
peut que rejouer le meme code. Ce balayage reprend exactement la grille et la strategie
de `run_certificat.py` (100 x 200 sur [1,2] x [60,120], subdivision adaptative,
profondeur <= 8) et ecrit une ligne JSON par boite, au fil de l'eau (si le processus est
tue, ce qui est deja ecrit est valide).

Sortie : certificat_temoins.jsonl (puis .json.gz a la fin)
"""
import gzip
import json
import shutil
import time

from certificat import certifie

RHO0, RHO1 = 1.0, 2.0
TH0, TH1 = 60.0, 120.0
NR0, NT0 = 100, 200          # meme grille que certificat.json
PROF_MAX = 8
EPS = 1e-3

OUT = "certificat_temoins.jsonl"


def run():
    t0 = time.time()
    dr = (RHO1 - RHO0) / NR0
    dt = (TH1 - TH0) / NT0
    niveau = [(RHO0 + i * dr, RHO0 + (i + 1) * dr, TH0 + j * dt, TH0 + (j + 1) * dt, 0)
              for i in range(NR0) for j in range(NT0)]
    n_ok = n_ko = 0
    prof = 0
    f = open(OUT, "w")
    while niveau:
        suivant = []
        for (a, b, c, d, p) in niveau:
            ok, info = certifie(a, b, c, d, export=True)
            if ok:
                n_ok += 1
                f.write(json.dumps({"r": [a, b], "t": [c, d], "prof": p, "ok": True,
                                    "tem": info["_tem"]}) + "\n")
            elif p >= PROF_MAX:
                n_ko += 1
                f.write(json.dumps({"r": [a, b], "t": [c, d], "prof": p, "ok": False,
                                    "raison": info.get("raison")}) + "\n")
            else:
                am, cm = (a + b) / 2, (c + d) / 2
                suivant += [(a, am, c, cm, p + 1), (a, am, cm, d, p + 1),
                            (am, b, c, cm, p + 1), (am, b, cm, d, p + 1)]
        f.flush()
        print(f"profondeur {prof} : {len(niveau)} boites traitees | total ok {n_ok}, "
              f"echecs {n_ko}, a subdiviser {len(suivant)}, {time.time() - t0:.0f}s", flush=True)
        niveau = suivant
        prof += 1
    f.close()
    # compression (le fichier brut fait plusieurs centaines de Mo)
    with open(OUT, "rb") as fi, gzip.open("certificat_temoins.json.gz", "wb", compresslevel=6) as fo:
        shutil.copyfileobj(fi, fo)
    meta = {"date": "2026-11-03", "domaine": {"rho": [RHO0, RHO1], "theta": [TH0, TH1]},
            "grille_initiale": [NR0, NT0], "profondeur_max": PROF_MAX, "eps": EPS,
            "nb_ok": n_ok, "nb_echecs": n_ko, "temps_s": round(time.time() - t0, 1),
            "format": "jsonl, une ligne par boite ; 'tem' = temoins a verifier"}
    json.dump(meta, open("certificat_temoins_meta.json", "w"), ensure_ascii=False, indent=1)
    print("termine :", meta, flush=True)


if __name__ == "__main__":
    run()
