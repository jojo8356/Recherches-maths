import math,sys,itertools; sys.path.insert(0,'.')
from partition2 import *
def rapport(res):
    return "IMPOSSIBLE" if res is False else ("budget" if res is None else "trouve")
def verifier(cells,adj,col,U1,U2):
    """verification independante, sans reutiliser le graphe : toute paire de meme couleur
       doit avoir une plage de distances qui evite exactement 1."""
    cen=[(sum(p[0] for p in c)/len(c),sum(p[1] for p in c)/len(c)) for c in cells]
    bad=[]
    for i,j in itertools.combinations(range(len(cells)),2):
        if col[i]!=col[j]: continue
        dv=wrap((cen[j][0]-cen[i][0],cen[j][1]-cen[i][1]),U1,U2)
        B=[(x-cen[j][0]+cen[i][0]+dv[0], y-cen[j][1]+cen[i][1]+dv[1]) for x,y in cells[j]]
        lo=dmin(cells[i],B); hi=dmax(cells[i],B)
        if lo<=1<=hi: bad.append((i,j,lo,hi))
    return bad
print("CALIBRATION 3")
# --- carre ---
P=12; seeds=[(i+0.5,j+0.5) for i in range(P) for j in range(P)]
cells=voronoi_tore(seeds,(P,0),(0,P)); cells,k=normaliser(cells,1e-4)
U1=(k*P,0); U2=(0,k*P); adj,_=graphe(cells,U1,U2); w,_=clique_max(adj)
r6,_=k_color(adj,6)
print(f"  carre 12x12  : n={len(cells)} aretes={sum(len(a) for a in adj)//2} omega={w}  6 couleurs -> {rapport(r6)}")
# --- hexagonal, periodes compatibles avec 7 ---
b1=(1,0); b2=(0.5,math.sqrt(3)/2)
for m_ in (7,14):
    seeds=[(i*b1[0]+j*b2[0]+(b1[0]+b2[0])/3, i*b1[1]+j*b2[1]+(b1[1]+b2[1])/3) for i in range(m_) for j in range(m_)]
    U1=(m_*b1[0],m_*b1[1]); U2=(m_*b2[0],m_*b2[1])
    cells=voronoi_tore(seeds,U1,U2); cells,k=normaliser(cells,1e-4)
    U1=(k*U1[0],k*U1[1]); U2=(k*U2[0],k*U2[1]); adj,_=graphe(cells,U1,U2); w,_=clique_max(adj)
    r7,c7=k_color(adj,7); r6,_=k_color(adj,6)
    print(f"  hexagonal {m_:2d}x{m_:2d}: n={len(cells)} aretes={sum(len(a) for a in adj)//2} omega={w}  7 -> {rapport(r7)}   6 -> {rapport(r6)}")
    if isinstance(r7,list):
        bad=verifier(cells,adj,r7,U1,U2)
        print(f"     verification independante du 7-coloriage : {len(bad)} paire(s) fautive(s)")
