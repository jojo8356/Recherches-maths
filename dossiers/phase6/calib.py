import math,sys; sys.path.insert(0,'.')
from partition2 import *
print("CALIBRATION : la machinerie retrouve-t-elle les valeurs de la phase 5 ?")
# pavage CARRE (periode 12x12, 144 cellules) -> attendu omega=9
P=12; seeds=[(i+0.5,j+0.5) for i in range(P) for j in range(P)]
cells=voronoi_tore(seeds,(P,0),(0,P)); cells,k=normaliser(cells,1e-4)
adj,m=graphe(cells,(k*P,0),(0,k*P))
w,cl=clique_max(adj); print(f"  carre 12x12 : n={len(cells)} aretes={sum(len(a) for a in adj)//2} omega={w} (attendu 9)")
col,_=k_color(adj,6); print(f"    6-coloriage possible ? {bool(col)}   (attendu : non, omega=9)")
# pavage HEXAGONAL (tore rhombique 12x12 cellules) -> attendu omega=7
b1=(1,0); b2=(0.5,math.sqrt(3)/2); m_=12
seeds=[(i*b1[0]+j*b2[0]+b1[0]/3+b2[0]/3, i*b1[1]+j*b2[1]+b1[1]/3+b2[1]/3) for i in range(m_) for j in range(m_)]
U1=(m_*b1[0],m_*b1[1]); U2=(m_*b2[0],m_*b2[1])
cells=voronoi_tore(seeds,U1,U2); cells,k=normaliser(cells,1e-4)
adj,m=graphe(cells,(k*U1[0],k*U1[1]),(k*U2[0],k*U2[1]))
w,cl=clique_max(adj); print(f"  hexagonal 12x12 : n={len(cells)} aretes={sum(len(a) for a in adj)//2} omega={w} (attendu 7)")
col,_=k_color(adj,7); print(f"    7-coloriage possible ? {bool(col)}  (attendu : oui)")
col6,_=k_color(adj,6); print(f"    6-coloriage possible ? {bool(col6)}  (attendu : non)")
