import math,sys; sys.path.insert(0,'.')
from courbes import *
b1=(1,0); b2=(0.5,math.sqrt(3)/2); m=7
seeds=[(i*b1[0]+j*b2[0]+(b1[0]+b2[0])/3, i*b1[1]+j*b2[1]+(b1[1]+b2[1])/3) for i in range(m) for j in range(m)]
U1=(m*b1[0],m*b1[1]); U2=(m*b2[0],m*b2[1])
c0,_=pavage_courbe(seeds,U1,U2,None,M=6,sign_seed=1)
c1,_=pavage_courbe(seeds,U1,U2,1.0,M=6,sign_seed=1)
a0=[aire(c) for c in c0]; a1=[aire(c) for c in c1]
print("aire min/max des cellules, droite :",round(min(a0),4),round(max(a0),4))
print("aire min/max des cellules, courbe :",round(min(a1),4),round(max(a1),4))
print("cellules dont l'aire change :",sum(1 for x,y in zip(a0,a1) if abs(x-y)>1e-9),"/",len(a0))
# ecart max a la corde
import numpy as np
def ecart(c0,c1):
    d=[]
    for P,Q in zip(c0,c1):
        for q in Q:
            d.append(min(math.dist(q,p) for p in P))
    return max(d)
print("ecart max entre polygone courbe et polygone droit :",round(ecart(c0,c1),4))
