import math,sys,json,itertools; sys.path.insert(0,'.')
from partition2 import *
b1=(1,0); b2=(0.5,math.sqrt(3)/2)
def germes_hex(m,s,jit,seed):
    import random; rnd=random.Random(seed); out=[]
    for i in range(m):
        for j in range(m):
            x=i*b1[0]+j*b2[0]+(b1[0]+b2[0])/3; y=i*b1[1]+j*b2[1]+(b1[1]+b2[1])/3
            if jit>0:
                a=rnd.uniform(0,2*math.pi); r=jit*s*math.sqrt(rnd.uniform(0,1))
                x+=r*math.cos(a); y+=r*math.sin(a)
            out.append((x,y))
    return out
def germes_poisson(n,side,seed):
    import random; rnd=random.Random(seed)
    return [(rnd.uniform(0,side),rnd.uniform(0,side)) for _ in range(n)]
def verifier(cells,col,U1,U2):
    cen=[(sum(p[0] for p in c)/len(c),sum(p[1] for p in c)/len(c)) for c in cells]
    bad=[]
    for i,j in itertools.combinations(range(len(cells)),2):
        if col[i]!=col[j]: continue
        dv=wrap((cen[j][0]-cen[i][0],cen[j][1]-cen[i][1]),U1,U2)
        B=[(x-cen[j][0]+cen[i][0]+dv[0], y-cen[j][1]+cen[i][1]+dv[1]) for x,y in cells[j]]
        lo=dmin(cells[i],B); hi=dmax(cells[i],B)
        if lo<=1<=hi: bad.append((i,j,round(lo,6),round(hi,6)))
    return bad
def run(tag,seeds,U1,U2,eps=1e-4):
    cells=voronoi_tore(seeds,U1,U2)
    if cells is None: return dict(tag=tag,erreur="cellule vide")
    cells,k=normaliser(cells,eps)
    U1=(k*U1[0],k*U1[1]); U2=(k*U2[0],k*U2[1])
    dm=[diam(c) for c in cells]
    adj,marg=graphe(cells,U1,U2)
    w,cl=clique_max(adj)
    r6,c6=k_color(adj,6); r7,_=k_color(adj,7)
    out=dict(tag=tag,n=len(cells),dmax=round(max(dm),5),dmoy=round(sum(dm)/len(dm),4),
             dmin=round(min(dm),4),aretes=sum(len(a) for a in adj)//2,
             degmoy=round(sum(len(a) for a in adj)/len(adj),1),degmax=max(len(a) for a in adj),
             omega=w,chi6=("impossible" if r6 is False else "budget" if r6 is None else 6),
             chi7=("impossible" if r7 is False else "budget" if r7 is None else 7),
             marge_min=round(min(marg),6) if marg else None)
    if isinstance(r6,list):
        bad=verifier(cells,r6,U1,U2)
        out["verif_6"]=len(bad); out["coloriage"]=r6
        out["U1"],out["U2"]=U1,U2
    print(f"  {tag:26s} n={out['n']:4d} D={out['dmin']:.3f}-{out['dmax']:.3f} (moy {out['dmoy']:.3f}) "
          f"m={out['aretes']:5d} deg {out['degmoy']:.1f}/{out['degmax']:3d} | omega={w} 6->{out['chi6']}"
          + (f" [verif {out['verif_6']} faute]" if 'verif_6' in out else ""), flush=True)
    return out
if __name__=='__main__':
    RES=[]
    print("A. HEXAGONAL PERTURBE (14x14 = 196 cellules, tore rhombique)")
    for jit in (0.10,0.15,0.20,0.25,0.30,0.40):
        for sd in (1,2):
            RES.append(run(f"hex jit={jit} s={sd}",germes_hex(14,1.0,jit,sd),(14*b1[0],14*b1[1]),(14*b2[0],14*b2[1])))
    print("\nB. POISSON (tore carre 21x21)")
    for n in (300,420):
        for sd in (1,2):
            RES.append(run(f"poisson n={n} s={sd}",germes_poisson(n,21,sd),(21,0),(0,21)))
    json.dump(RES,open('res_expA.json','w'),ensure_ascii=False)
    print("\nRESUME")
    om=[r['omega'] for r in RES if 'omega' in r]
    print(f"  omega observe : min={min(om)} max={max(om)}  |  configurations a omega<=6 : {sum(1 for o in om if o<=6)}/{len(om)}")
    print(f"  6-coloriages valides (verifies) : {sum(1 for r in RES if r.get('verif_6')==0)}")
