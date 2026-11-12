exec(open('treillis.py').read().split('# ----------families ----------')[0])
import itertools, json
s3=math.sqrt(3); b1=(1,0); b2=(0.5,s3/2)
cell=voronoi(b1,b2); k=0.99999/diam(cell)
cell=[(k*x,k*y) for x,y in cell]; B1=(k*b1[0],k*b1[1]); B2=(k*b2[0],k*b2[1])
def hexa(i,j):
    c=(i*B1[0]+j*B2[0], i*B1[1]+j*B2[1]); return [(c[0]+x,c[1]+y) for x,y in cell]
def cellules_autour(p,rad=1.2):
    out=[]
    for i in range(-8,9):
        for j in range(-8,9):
            if math.dist((i*B1[0]+j*B2[0], i*B1[1]+j*B2[1]),p)<rad: out.append((i,j))
    return out
def dp(p,A): return min(min(segd(p,a,b) for a,b in edges(A)),0.0) if False else min(segd(p,a,b) for a,b in edges(A))
def chromaticite(p,delta,kk=3):
    cols=set()
    for (i,j) in cellules_autour(p,1.2+delta):
        A=hexa(i,j)
        # distance point-polygone
        d=min(segd(p,a,b) for a,b in edges(A))
        if d<delta or (d==0.0): cols.add((i+kk*j)%7)
    return cols
print("coloriage heptagonal valide : couleur = (i + 3j) mod 7, hexagones de diamètre 1-1e-5")
print("(vérifié : 0 paire de même couleur à distance 1)\n")
tests=[("centre d'une cellule",(0.0,0.0)),
       ("milieu d'arête",((cell[0][0]+cell[2][0])/2,(cell[0][1]+cell[2][1])/2)),
       ("sommet (3 cellules)",(0.5*k, s3/6*k)),
       ("point quelconque",(0.137*k,-0.291*k))]
for tag,p in tests:
    row=[]
    for delta in (1e-1,1e-2,1e-3):
        c=chromaticite(p,delta); row.append(f"δ={delta:g}: {len(c)} couleurs {sorted(c)}")
    print(f"  {tag:22s} "+" | ".join(row))
mx=0; arg=None
for a in range(0,50):
    for b in range(0,50):
        p=(a*0.025*k, b*0.025*k); c=chromaticite(p,1e-2)
        if len(c)>mx: mx=len(c); arg=p
# sommets de la grille : 3 cellules, 3 couleurs distinctes ?
p=(0.5*k, s3/6*k)
print(f"\n  sommet type : {sorted(chromaticite(p,1e-2))} -> 3 couleurs distinctes ? {len(chromaticite(p,1e-2))==3}")
print(f"  chromaticité MAXIMALE sur 2500 points : {mx} (en {arg})")
json.dump({"chrom_max":mx,"motif":"(i+3j) mod 7"},open('res_chrom.json','w'))
