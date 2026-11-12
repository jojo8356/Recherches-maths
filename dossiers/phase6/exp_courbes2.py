import math,sys,json,random; sys.path.insert(0,'.')
from courbes import pavage_courbe5, graphe_np, aire, dmin_np
from partition2 import clique_max, k_color, normaliser, diam
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
def verifier(cells,col,U1,U2,marge=0.01):
    import itertools
    from partition2 import wrap
    cen=[(sum(p[0] for p in c)/len(c),sum(p[1] for p in c)/len(c)) for c in cells]
    bad=0
    for i,j in itertools.combinations(range(len(cells)),2):
        if col[i]!=col[j]: continue
        dv=wrap((cen[j][0]-cen[i][0],cen[j][1]-cen[i][1]),U1,U2)
        B=[(x-cen[j][0]+cen[i][0]+dv[0],y-cen[j][1]+cen[i][1]+dv[1]) for x,y in cells[j]]
        lo=dmin_np(cells[i],B)
        if lo<=1+marge: 
            hi=max(math.dist(p,q) for p in cells[i] for q in B)
            if hi>=1-marge: bad+=1
    return bad
def run(m,jit,R,sd=1,M=6,marge=0.01):
    U1=(m*b1[0],m*b1[1]); U2=(m*b2[0],m*b2[1])
    cells=pavage_courbe5(germes(m,jit,sd),U1,U2,R,M=M)
    if cells is None: return None
    at=abs(U1[0]*U2[1]-U1[1]*U2[0]); ecart=sum(abs(aire(c)) for c in cells)-at
    cells,k=normaliser(cells,1e-4); U1=(k*U1[0],k*U1[1]); U2=(k*U2[0],k*U2[1])
    dm=[diam(c) for c in cells]
    adj,mm=graphe_np(cells,U1,U2,margin=marge)
    w,cl=clique_max(adj); r6,c6=k_color(adj,6)
    deg=sum(len(a) for a in adj)/len(adj)
    tag=f"j={jit:.2f} R={str(R):4s}"
    six="IMPOSSIBLE" if r6 is False else ("TROUVE" if isinstance(r6,list) else "budget")
    print(f"  {tag:20s} n={len(cells):3d} aire_err={ecart:+.0e} D={min(dm):.3f}-{max(dm):.3f} deg={deg:5.1f} "
          f"| omega={w:2d}  6->{six}",flush=True)
    out=dict(jit=jit,R=R,omega=w,deg=round(deg,1),six=six,dmin=round(min(dm),4),dmax=round(max(dm),4),
             aire_err=ecart,n=len(cells))
    if isinstance(r6,list):
        out["verif"]=verifier(cells,r6,U1,U2,marge)
        out["coloriage"]=r6
        print(f"     >>> VERIFICATION : {out['verif']} paire(s) fautive(s)")
    return out
RES=[]
print("BORDS COURBES : arcs de rayon R.  R = 1,0 = l'hypothese exacte du preprint de 2025.")
print("marge 0,01 (> erreur d'approximation polygonale des arcs, 0,0033 au pire)\n")
for jit in (0.0,0.15,0.30):
    print(f" -- germes hexagonaux, desordre {jit} --")
    for R in (None,3.0,1.5,1.0,0.7,0.45,0.35):
        r=run(14,jit,R)
        if r: RES.append(r)
    print()
json.dump(RES,open('res_courbes2.json','w'),ensure_ascii=False)
print("BILAN : omega =",sorted({r['omega'] for r in RES})," | 6-coloriages valides :",sum(1 for r in RES if r['six']=='TROUVE'))
