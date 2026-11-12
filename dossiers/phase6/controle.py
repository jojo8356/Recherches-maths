import math,sys,json,itertools; sys.path.insert(0,'.')
from partition2 import *
from experience import germes_hex, germes_poisson
b1=(1,0); b2=(0.5,math.sqrt(3)/2)
def run(tag,seeds,U1,U2,mode="max",eps=1e-4):
    cells=voronoi_tore(seeds,U1,U2)
    if cells is None: return None
    dm0=[diam(c) for c in cells]
    ref=max(dm0) if mode=="max" else sum(dm0)/len(dm0)   # <- seule difference
    k=(1-eps)/ref
    cells=[[(k*x,k*y) for x,y in c] for c in cells]
    U1=(k*U1[0],k*U1[1]); U2=(k*U2[0],k*U2[1])
    dm=[diam(c) for c in cells]
    adj,_=graphe(cells,U1,U2); w,_=clique_max(adj)
    r6,_=k_color(adj,6)
    print(f"  {tag:34s} norme={mode:4s} D={max(dm):.3f} moy={sum(dm)/len(dm):.3f} "
          f"deg={sum(len(a) for a in adj)/len(adj):.1f} | omega={w} 6->{'impossible' if r6 is False else 'trouve' if isinstance(r6,list) else 'budget'}",flush=True)
    return dict(tag=tag,mode=mode,omega=w,dmax=round(max(dm),4),dmoy=round(sum(dm)/len(dm),4),
                deg=round(sum(len(a) for a in adj)/len(adj),1))
print("CONTROLE : meme jeu de germes, deux normalisations")
print("(max = partition valide, toutes cellules de diametre < 1 ; moyenne = invalide, mais comparable geometriquement)")
OUT=[]
for jit in (0.0,0.10,0.20,0.30,0.40):
    for mode in ("max","moy"):
        r=run(f"hex jit={jit} s=1",germes_hex(14,1.0,jit,1),(14*b1[0],14*b1[1]),(14*b2[0],14*b2[1]),mode)
        if r: OUT.append(r)
print()
for n in (300,):
    for mode in ("max","moy"):
        r=run(f"poisson n={n} s=1",germes_poisson(n,21,1),(21,0),(0,21),mode)
        if r: OUT.append(r)
json.dump(OUT,open('res_controle.json','w'))
print("\nBALAYAGE FIN de la transition (3 germes aleatoires par valeur)")
for jit in (0.0,0.02,0.05,0.08,0.10,0.12,0.15,0.18,0.20):
    ws=[]
    for sd in (1,2,3):
        cells=voronoi_tore(germes_hex(14,1.0,jit,sd),(14*b1[0],14*b1[1]),(14*b2[0],14*b2[1]))
        if cells is None: continue
        cells,k=normaliser(cells,1e-4)
        U1=(k*14*b1[0],k*14*b1[1]); U2=(k*14*b2[0],k*14*b2[1])
        adj,_=graphe(cells,U1,U2); w,_=clique_max(adj); ws.append(w)
    print(f"  jit={jit:4.2f} : omega = {ws}")
