import sys,time,json; sys.path.insert(0,'.')
from balayage import omega_reseau
import collections
thetas=[60+0.25*k for k in range(241)]          # 60 -> 120 deg
rhos=[1.0+0.005*k for k in range(201)]           # 1 -> 2
t0=time.time(); res={}; mini=99; arg=[]
for th in thetas:
    for rho in rhos:
        w=omega_reseau(rho,th,R=2)
        res[(round(th,2),round(rho,3))]=w
        if w is not None and w<mini: mini=w; arg=[(th,rho)]
        elif w==mini: arg.append((th,rho))
print(f"balayage {len(res)} reseaux en {time.time()-t0:.0f}s")
print("omega minimal =",mini," atteint en",len(arg),"points")
vals=collections.Counter(res.values())
print("repartition :",dict(sorted(vals.items())))
if mini<=6:
    print("!!! points a omega <= 6 :",arg[:20])
# carte : lignes = theta, colonnes = rho (echantillon)
print("\ncarte (lignes theta, colonnes rho de 1.0 a 2.0 par pas de 0.1) :")
hdr="      "+"".join(f"{r:4.1f}" for r in [1.0+0.1*k for k in range(11)])
print(hdr)
for th in [60+2.5*k for k in range(25)]:
    row=f"{th:5.1f} "
    for r in [1.0+0.1*k for k in range(11)]:
        w=res[(round(th,2),round(r,3))]; row+=f"{w:4d}"
    print(row)
json.dump({f"{k[0]},{k[1]}":v for k,v in res.items()},open('scan_fin.json','w'))
