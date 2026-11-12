import math,sys; sys.path.insert(0,'.')
from partition2 import voronoi_tore
b1=(1,0); b2=(0.5,math.sqrt(3)/2)
for m in (7,14):
    seeds=[(i*b1[0]+j*b2[0]+(b1[0]+b2[0])/3, i*b1[1]+j*b2[1]+(b1[1]+b2[1])/3) for i in range(m) for j in range(m)]
    cells=voronoi_tore(seeds,(m*b1[0],m*b1[1]),(m*b2[0],m*b2[1]))
    for dec in (9,6,4):
        d={}
        for i,c in enumerate(cells):
            for k in range(len(c)):
                a=c[k]; bb=c[(k+1)%len(c)]
                ka=(round(a[0],dec),round(a[1],dec)); kb=(round(bb[0],dec),round(bb[1],dec))
                if ka==kb: continue
                d.setdefault(frozenset((ka,kb)),set()).add(i)
        partage=sum(1 for v in d.values() if len(v)==2)
        print(f"m={m:2d} arrondi {dec} dec : {len(d):4d} aretes distinctes, {partage:4d} partagees par 2 cellules "
              f"({100*partage/len(d):.0f}%), {sum(1 for v in d.values() if len(v)>2)} partagees par >2")
