"""Certificat de omega >= 8 : la region obtenue doit coincider avec celle du balayage."""
import json, time
from certificat import certifie

RHO0, RHO1, TH0, TH1 = 1.0, 2.0, 60.0, 120.0
NR, NT = 40, 80
t0 = time.time()
out = []
dr, dt = (RHO1 - RHO0) / NR, (TH1 - TH0) / NT
for i in range(NR):
    for j in range(NT):
        a, b = RHO0 + i * dr, RHO0 + (i + 1) * dr
        c, d = TH0 + j * dt, TH0 + (j + 1) * dt
        ok, info = certifie(a, b, c, d, k=8)
        out.append([a, b, c, d, bool(ok), round(info.get('marge', -1), 6) if ok else None])
aire = sum((b - a) * (d - c) for (a, b, c, d, ok, m) in out if ok) / (1.0 * 60.0)
print(f"boites {NR*NT}, certifiees {sum(1 for o in out if o[4])}, aire {100*aire:.2f} %, {time.time()-t0:.0f}s")
json.dump({"grille": [NR, NT], "boites": out, "aire_pct": 100 * aire,
           "temps_s": round(time.time() - t0, 1)},
          open("certificat_k8.json", "w"))
