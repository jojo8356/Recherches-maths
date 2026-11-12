import sys,math,json,random; sys.path.insert(0,'.'); sys.path.insert(0,'../phase6')
from trous import *
from partition2 import voronoi_tore, k_color, clique_max
b1=(1,0); b2=(0.5,math.sqrt(3)/2)
def germes(m,jit,sd):
    rnd=random.Random(sd); out=[]
    for i in range(m):
        for j in range(m):
            x=i*b1[0]+j*b2[0]+(b1[0]+b2[0])/3; y=i*b1[1]+j*b2[1]+(b1[1]+b2[1])/3
            if jit:
                a=rnd.uniform(0,2*math.pi); r=jit*math.sqrt(rnd.uniform(0,1)); x+=r*math.cos(a); y+=r*math.sin(a)
            out.append((x,y))
    return out
def norm(cells,eps=1e-4):
    D=max(diam_cell(c) for c in cells); k=(1-eps)/D
    return [[[(k*x,k*y) for x,y in P] for P in c] for c in cells],k
def run(tag,seeds,U1,U2,choix,rho,essai6=True):
    cells=construit(seeds,U1,U2,choix,rho)
    cells,k=norm(cells); U1=(k*U1[0],k*U1[1]); U2=(k*U2[0],k*U2[1])
    adj,mm=graphe(cells,U1,U2,margin=0.01)
    w,cl=clique_max(adj)
    deg=sum(len(a) for a in adj)/len(adj)
    six=None
    if essai6 and w is not None and w<=6:
        r6,c6=k_color(adj,6); six="TROUVE" if isinstance(r6,list) else ("impossible" if r6 is False else "budget")
    print(f"  {tag:36s} n={len(cells):3d} deg={deg:5.1f} m={sum(len(a) for a in adj)//2:5d} | omega={w}"
          + (f"  6 couleurs -> {six}" if six else ""),flush=True)
    return dict(tag=tag,n=len(cells),omega=w,deg=round(deg,1),six=six,
                coloriage=(c6 if six=="TROUVE" else None),U1=U1,U2=U2,cells=cells if six=="TROUVE" else None)
m=14; RES=[]
for jit in (0.0,0.15):
    seeds=germes(m,jit,1); U1=(m*b1[0],m*b1[1]); U2=(m*b2[0],m*b2[1])
    print(f"=== desordre {jit} ===")
    ref=run("reference, aucune cellule trouee",seeds,U1,U2,lambda i:False,0.0)
    RES.append({k:v for k,v in ref.items() if k not in ('coloriage','cells','U1','U2')})
    # clique maximale de reference
    cells=construit(seeds,U1,U2,lambda i:False,0.0); cells,k=norm(cells)
    adj,_=graphe(cells,(k*U1[0],k*U1[1]),(k*U2[0],k*U2[1]),margin=0.01)
    w,cl=clique_max(adj); CL=set(cl)
    print(f"    (clique maximale de reference : {len(CL)} cellules)")
    for rho in (0.3,0.5,0.7):
        RES.append({k:v for k,v in run(f"toutes les cellules trouees, rho={rho}",seeds,U1,U2,lambda i:True,rho).items() if k not in ('coloriage','cells','U1','U2')})
    for rho in (0.3,0.5,0.7):
        RES.append({k:v for k,v in run(f"clique seule trouee, rho={rho}",seeds,U1,U2,(lambda CL: lambda i: i in CL)(CL),rho).items() if k not in ('coloriage','cells','U1','U2')})
    RES.append({k:v for k,v in run("une classe de couleur sur 7, rho=0.5",seeds,U1,U2,lambda i:(i%m+3*(i//m))%7==0,0.5).items() if k not in ('coloriage','cells','U1','U2')})
    RES.append({k:v for k,v in run("moitie aleatoire, rho=0.5",seeds,U1,U2,(lambda S: lambda i: i in S)(set(random.Random(5).sample(range(m*m),m*m//2))),0.5).items() if k not in ('coloriage','cells','U1','U2')})
json.dump(RES,open('res_trous.json','w'),ensure_ascii=False)
print("\nBILAN : omega =",sorted({r['omega'] for r in RES}),"| 6-coloriages :",sum(1 for r in RES if r['six']=='TROUVE'))
