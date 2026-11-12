import sys,math; sys.path.insert(0,'.'); sys.path.insert(0,'../phase6')
from trous import *
from partition2 import voronoi_tore
b1=(1,0); b2=(0.5,math.sqrt(3)/2); m=7
seeds=[(i*b1[0]+j*b2[0]+(b1[0]+b2[0])/3, i*b1[1]+j*b2[1]+(b1[1]+b2[1])/3) for i in range(m) for j in range(m)]
U1=(m*b1[0],m*b1[1]); U2=(m*b2[0],m*b2[1])
at=abs(U1[0]*U2[1]-U1[1]*U2[0])
print("controle de la partition apres decoupage (renormalisee a diametre max 1-1e-4)")
for rho in (0.0,0.3,0.5,0.7):
    cells=construit(seeds,U1,U2,lambda i:rho>0,rho,verbose=True)
    # renormalisation
    D=max(diam_cell(c) for c in cells); k=(1-1e-4)/D
    cells=[[[(k*x,k*y) for x,y in P] for P in c] for c in cells]
    tot=sum(aire_cell(c) for c in cells); at2=at*k*k
    dm=[diam_cell(c) for c in cells]
    print(f"  rho={rho}: aire={tot:.6f} tore={at2:.6f} ecart={tot-at2:+.2e} diam {min(dm):.4f}-{max(dm):.4f}")
