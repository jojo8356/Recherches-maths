import math, itertools, json
RHO=0.49                      # rayon circonscrit : diamètre 0.98 < 1
S=math.sqrt(3)*RHO            # espacement des centres
def center(q,r): return (S*(q+r/2), S*(r*math.sqrt(3)/2))
VERT=[(RHO*math.cos(math.pi/6+k*math.pi/3), RHO*math.sin(math.pi/6+k*math.pi/3)) for k in range(6)]
def poly(q,r):
    cx,cy=center(q,r); return [(cx+vx,cy+vy) for vx,vy in VERT]
def hexdist(dq,dr): return max(abs(dq),abs(dr),abs(dq+dr))
def seg_dist(p,a,b):
    ax,ay=a; bx,by=b; px,py=p
    dx,dy=bx-ax,by-ay; L=dx*dx+dy*dy
    t=0 if L==0 else max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L))
    return math.dist(p,(ax+t*dx,ay+t*dy))
def edges_of(P): return list(zip(P,P[1:]+P[:1]))
def poly_min(A,B):
    d=min(min(seg_dist(p,a,b) for a,b in edges_of(B)) for p in A)
    d=min(d, min(min(seg_dist(p,a,b) for a,b in edges_of(A)) for p in B))
    return d
def poly_max(A,B): return max(math.dist(p,q) for p in A for q in B)

P={ (q,r):poly(q,r) for q in range(-3,4) for r in range(-3,4) if hexdist(q,r)<=3 }
print("cellules dans le patch R=3 :", len(P))
mismatch=[]; table={}
for (q1,r1),A in P.items():
    for (q2,r2),B in P.items():
        if (q2,r2)<=(q1,r1): continue
        lo,hi=poly_min(A,B),poly_max(A,B)
        conflict = (lo<=1.0<=hi)
        k=hexdist(q2-q1,r2-r1)
        table.setdefault(k,set()).add(conflict)
        if conflict != (k<=2): mismatch.append(((q1,r1),(q2,r2),k,round(lo,3),conflict))
print("relation 'conflit <-> distance hexagonale <= 2' :", "VALIDÉE" if not mismatch else f"FAUX {mismatch[:5]}")
print("par distance hexagonale :", {k:sorted(v) for k,v in sorted(table.items())})

# graphe de conflit sur un patch, puis nombre chromatique exact
def build(R):
    cells=[(q,r) for q in range(-R,R+1) for r in range(-R,R+1) if hexdist(q,r)<=R]
    idx={c:i for i,c in enumerate(cells)}
    nb=[0]*len(cells)
    for i,(q1,r1) in enumerate(cells):
        for j in range(i+1,len(cells)):
            q2,r2=cells[j]
            if hexdist(q2-q1,r2-r1)<=2:
                nb[i]|=1<<j; nb[j]|=1<<i
    return cells,nb
cells,nb=build(3)
print("graphe de conflit R=3 :", len(cells),"sommets,", sum(bin(x).count('1') for x in nb)//2, "arêtes")

def chromatic(nb):
    n=len(nb); best=None
    def dsat_coloring(k):
        col=[-1]*n
        def rec(done):
            if done==n: return True
            # choisir le sommet non colorié de saturation max
            bv,bs,bd=-1,-1,-1
            for v in range(n):
                if col[v]!=-1: continue
                sat=0; m=col and 0
                s=set()
                x=nb[v]
                while x:
                    b=(x&-x).bit_length()-1; x&=x-1
                    if col[b]!=-1: s.add(col[b])
                if (len(s),bin(nb[v]).count('1'))>(bs,bd): bv,bs,bd=v,len(s),bin(nb[v]).count('1')
            used={col[b] for b in range(n) if col[b]!=-1 and (nb[bv]>>b)&1}
            for c in range(k):
                if c not in used:
                    col[bv]=c
                    if rec(done+1): return True
                    col[bv]=-1
            return False
        if rec(0): return col[:]
        return None
    for k in range(1,n+1):
        r=dsat_coloring(k)
        if r: return k,r
    return None,None
chi,col=chromatic(nb)
print("nombre chromatique du graphe de conflit (patch R=3) :", chi)
# la fleur : centre + 6 voisins forme-t-elle une clique ?
flower=[(0,0)]+[(q,r) for q in range(-1,2) for r in range(-1,2) if hexdist(q,r)==1]
ix={c:i for i,c in enumerate(cells)}
clique=all(hexdist(b[0]-a[0],b[1]-a[1])<=2 for a,b in itertools.combinations(flower,2))
print(f"la 'fleur' de 7 cellules est-elle une clique ? {clique}  -> toute coloration cellulaire exige >= 7 couleurs")
json.dump({'rho':RHO,'chi_patch':chi,'flower_clique':clique},open('res_hex1.json','w'))
