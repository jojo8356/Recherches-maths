exec(open('treillis.py').read().split('# ----------families ----------')[0])
import json
s3=math.sqrt(3); b1=(1,0); b2=(0.5,s3/2)
cell=voronoi(b1,b2); k=0.99999/diam(cell)
cell=[(k*x,k*y) for x,y in cell]; B1=(k*b1[0],k*b1[1]); B2=(k*b2[0],k*b2[1])
def hexa(i,j):
    c=(i*B1[0]+j*B2[0], i*B1[1]+j*B2[1]); return [(c[0]+x,c[1]+y) for x,y in cell]
def inside(poly,p):
    x,y=p; r=False; n=len(poly)
    for i in range(n):
        a=poly[i]; b=poly[(i+1)%n]
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]: r=not r
    return r
def onb(p,poly,tol=1e-9): return min(segd(p,a,b) for a,b in edges(poly))<tol
def col_at(p,kk=3):
    cols=set()
    for i in range(-8,9):
        for j in range(-8,9):
            A=hexa(i,j)
            c=(i*B1[0]+j*B2[0], i*B1[1]+j*B2[1])
            if math.dist(c,p)<1.6 and (inside(A,p) or onb(p,A)): cols.add((i+kk*j)%7)
    return cols
tests=[("centre de cellule (intérieur)",(0.0,0.0)),
       ("milieu d'arête (2 cellules)",((cell[0][0]+cell[1][0])/2*k,(cell[0][1]+cell[1][1])/2*k)),
       ("sommet (3 cellules)",(0.5*k,s3/6*k)),
       ("autre sommet",(0.5*k,-s3/6*k))]
for tag,p in tests:
    c=col_at(p); print(f"  {tag:32s} chromaticité {len(c)}  couleurs {sorted(c)}")
