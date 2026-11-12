import math,sys,json; sys.path.insert(0,'.')
from courbes import *
from partition2 import clique_max, k_color, normaliser
b1=(1,0); b2=(0.5,math.sqrt(3)/2)
def build(m,jit,R,sd,sign_seed,M=6):
    import random
    rnd=random.Random(sd); seeds=[]
    for i in range(m):
        for j in range(m):
            x=i*b1[0]+j*b2[0]+(b1[0]+b2[0])/3; y=i*b1[1]+j*b2[1]+(b1[1]+b2[1])/3
            if jit>0:
                a=rnd.uniform(0,2*math.pi); r=jit*math.sqrt(rnd.uniform(0,1))
                x+=r*math.cos(a); y+=r*math.sin(a)
            seeds.append((x,y))
    U1=(m*b1[0],m*b1[1]); U2=(m*b2[0],m*b2[1])
    res=pavage_courbe(seeds,U1,U2,R,M=M,sign_seed=sign_seed)
    if res is None: return None
    return res[0],U1,U2
def run(tag,cells,U1,U2,eps=1e-4,margin=0.01,essai6=True):
    cells,k=normaliser(cells,eps); U1=(k*U1[0],k*U1[1]); U2=(k*U2[0],k*U2[1])
    dm=[diam(c) for c in cells]
    adj,mm=graphe_np(cells,U1,U2,margin=margin)
    w,cl=clique_max(adj)
    r6,_=k_color(adj,6) if essai6 else (False,None)
    deg=sum(len(a) for a in adj)/len(adj)
    print(f"  {tag:34s} n={len(cells):3d} D={min(dm):.3f}-{max(dm):.3f} deg={deg:5.1f} "
          f"m={sum(len(a) for a in adj)//2:5d} | omega={w}  6 couleurs -> "
          f"{'IMPOSSIBLE' if r6 is False else 'trouve!' if isinstance(r6,list) else 'budget'}",flush=True)
    return dict(tag=tag,n=len(cells),omega=w,deg=round(deg,1),
                six=("impossible" if r6 is False else "trouve" if isinstance(r6,list) else "budget"),
                dmin=round(min(dm),4),dmax=round(max(dm),4),margin=margin)
print("PAVIAGE HEXAGONAL A BORDS COURBES — arcs de rayon R (R=1 : hypothese interdite par le preprint)")
print("marge de securite 0,01 (l'approximation polygonale des arcs vaut mieux que 0,004)\n")
RES=[]
for R,tag in ((None,"droit (R=infini)"),(3.0,"R = 3,0"),(1.5,"R = 1,5"),(1.0,"R = 1,0  <-- hypothese"),
              (0.7,"R = 0,7"),(0.45,"R = 0,45"),(0.35,"R = 0,35")):
    for ss in (1,2):
        r=build(14,0.0,R,1,ss)
        if r is None: print(f"  {tag} signe={ss} : construction impossible"); continue
        cells,U1,U2=r
        RES.append(run(f"{tag} (signes {ss})",cells,U1,U2))
json.dump(RES,open('res_courbes.json','w'),ensure_ascii=False)
print("\nomega observe :", sorted({r['omega'] for r in RES}))
print("6-coloriages trouves :", sum(1 for r in RES if r['six']=='trouve'))
