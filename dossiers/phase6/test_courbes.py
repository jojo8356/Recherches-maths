import math,sys; sys.path.insert(0,'.')
from courbes import *
from partition2 import *
b1=(1,0); b2=(0.5,math.sqrt(3)/2); m=7
seeds=[(i*b1[0]+j*b2[0]+(b1[0]+b2[0])/3, i*b1[1]+j*b2[1]+(b1[1]+b2[1])/3) for i in range(m) for j in range(m)]
U1=(m*b1[0],m*b1[1]); U2=(m*b2[0],m*b2[1])
# validation : aire totale, puis reconstruction du cas droit (R=None)
for R in (None,1.0):
    res=pavage_courbe(seeds,U1,U2,R,M=6,sign_seed=1)
    if res is None: print("echec"); continue
    cells,aretes=res
    tot=sum(abs(aire(c)) for c in cells)
    aire_tore=abs(U1[0]*U2[1]-U1[1]*U2[0])
    dm=[diam(c) for c in cells]
    print(f"R={R!s:5s} : {len(cells)} cellules, {max(len(c) for c in cells)} sommets max, "
          f"aire totale={tot:.6f} (tore {aire_tore:.6f}) | diam {min(dm):.4f}-{max(dm):.4f}")
