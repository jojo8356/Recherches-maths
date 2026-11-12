import math,sys; sys.path.insert(0,'.')
from partition2 import *
def statut(r):
    if r is None: return("budget depasse",None)
    if r is False: return("IMPOSSIBLE (prouve)",None)
    return(f"coloriage trouve",r)
print("CALIBRATION 2 (tore compatible avec la periode 7)")
P=12; seeds=[(i+0.5,j+0.5) for i in range(P) for j in range(P)]
cells=voronoi_tore(seeds,(P,0),(0,P)); cells,k=normaliser(cells,1e-4)
adj,_=graphe(cells,(k*P,0),(0,k*P)); w,_=clique_max(adj)
s,_=statut(k_color(adj,6))
print(f"  carre 12x12      : n={len(cells)} omega={w}  6-couleurs -> {s}   (attendu omega=9, impossible)")
b1=(1,0); b2=(0.5,math.sqrt(3)/2)
for m_ in (7,14):
    seeds=[(i*b1[0]+j*b2[0]+(b1[0]+b2[0])/3, i*b1[1]+j*b2[1]+(b1[1]+b2[1])/3) for i in range(m_) for j in range(m_)]
    U1=(m_*b1[0],m_*b1[1]); U2=(m_*b2[0],m_*b2[1])
    cells=voronoi_tore(seeds,U1,U2); cells,k=normaliser(cells,1e-4)
    adj,_=graphe(cells,(k*U1[0],k*U1[1]),(k*U2[0],k*U2[1])); w,_=clique_max(adj)
    s7,c7=statut(k_color(adj,7)); s6,_=statut(k_color(adj,6))
    print(f"  hexagonal {m_:2d}x{m_:2d} : n={len(cells)} omega={w}  7-couleurs -> {s7}   6-couleurs -> {s6}")
    if c7:
        # verification independante : aucune paire de meme couleur a distance unite
        import itertools
        cen=[(sum(p[0] for p in c)/len(c),sum(p[1] for p in c)/len(c)) for c in cells]
        bad=0
        for i,j in itertools.combinations(range(len(cells)),2):
            if c7[i]!=c7[j]: continue
            dv=wrap((cen[j][0]-cen[i][0],cen[j][1]-cen[i][1]),(k*U1[0],k*U1[1]),(k*U2[0],k*U2[1]))
            B=[(x-cen[j][0]+cen[i][0]+dv[0], y-cen[j][1]+cen[i][1]+dv[1]) for x,y in cells[j]]
            lo=dmin(cells[i],B); hi=dmax(cells[i],B)
            if lo<=1<=hi: bad+=1
        print(f"     verification independante : {bad} paire(s) de meme couleur a distance unite")
