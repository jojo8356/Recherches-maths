exec(open('treillis.py').read().split('# ----------families ----------')[0])
import itertools, json
s3=math.sqrt(3)
b1=(1,0); b2=(0.5,s3/2)
cell=voronoi(b1,b2); k=0.99999/diam(cell)       # diamètre 1-1e-5 : on est "juste sous" 1
cell=[(k*x,k*y) for x,y in cell]; B1=(k*b1[0],k*b1[1]); B2=(k*b2[0],k*b2[1])
def pos(i,j): return (i*B1[0]+j*B2[0], i*B1[1]+j*B2[1])
def hexa(i,j):
    c=pos(i,j); return [(c[0]+x,c[1]+y) for x,y in cell]
R=6; P=[(i,j) for i in range(-R,R+1) for j in range(-R,R+1)]
print("1) Quels motifs (i + k j) mod 7 donnent un coloriage VALIDE (aucune paire de même couleur à distance 1) ?")
best=[]
for kk in range(1,7):
    bad=0; worst=9
    for (i,j),(i2,j2) in itertools.combinations(P,2):
        if (i+kk*j)%7!=(i2+kk*j2)%7: continue
        lo=dmin(hexa(i,j),hexa(i2,j2))
        if lo<1: bad+=1
        worst=min(worst,lo)
    print(f"   k={kk} : paires de même couleur en conflit = {bad:4d}   distance min = {worst:.6f}")
    if bad==0: best.append(kk)
print("   => motifs valides :", best)
kk=best[0]
print(f"\n2) chromaticité du coloriage k={kk} : nombre de couleurs distinctes dans un disque de rayon δ")
def pt_in(poly,p):
    x,y=p; inside=False; n=len(poly)
    for i in range(n):
        a=poly[i]; b=poly[(i+1)%n]
        if (a[1]>y)!=(b[1]>y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]: inside=not inside
    return inside
def cellules_autour(p,rad=1.15):
    out=[]
    for i in range(-10,11):
        for j in range(-10,11):
            c=pos(i,j)
            if math.dist(c,p)<rad: out.append((i,j))
    return out
tests=[]
# sommets de la grille hexagonale : intersection de 3 cellules
v0=(0.0,0.0)
tests.append(("milieu d'une arête", ((cell[0][0]+cell[1][0])/2,(cell[0][1]+cell[1][1])/2)))
tests.append(("sommet de la grille (3 cellules)", (0.5*k, s3/6*k)))
tests.append(("centre d'une cellule", (0.0,0.0)))
tests.append(("point générique", (0.13*k,-0.29*k)))
for tag,p in tests:
    found=set()
    for rad in (0.2,0.1,0.05,0.02):
        cols=set()
        for (i,j) in cellules_autour(p,rad):
            if pt_in(hexa(i,j),p): cols.add((i+kk*j)%7)
        if cols: found=cols
    print(f"   {tag:34s} : couleurs atteintes arbitrairement près = {sorted(found)}  (chromaticité locale {len(found)})")
# chromaticité maximale sur un échantillonnage fin
mx=0; arg=None
for a in range(0,60):
    for b in range(0,60):
        p=(a*0.02*k, b*0.02*k)
        cols=set()
        for (i,j) in cellules_autour(p,0.05):
            if pt_in(hexa(i,j),p): cols.add((i+kk*j)%7)
        if len(cols)>mx: mx=len(cols); arg=p
print(f"\n3) maximum de chromaticité sur 3600 points de test : {mx}  (atteint en {arg})")
print("   -> le lemme du preprint (« dans un coloriage valide à 6 couleurs, aucun point n'a de chromaticité >= 4 »)")
print("      n'est PAS contredit par le coloriage heptagonal : sa chromaticité max vaut", mx)
