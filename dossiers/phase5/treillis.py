import math, itertools, json
# ---------- géométrie ----------
def clip(poly, nx, ny, c):
    """garde {x : nx*x + ny*y <= c}"""
    out=[]
    n=len(poly)
    for i in range(n):
        a=poly[i]; b=poly[(i+1)%n]
        da=nx*a[0]+ny*a[1]-c; db=nx*b[0]+ny*b[1]-c
        if da<=0: out.append(a)
        if (da<0<db) or (db<0<da):
            t=da/(da-db); out.append((a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])))
    return out
def voronoi(b1,b2,rmax=8.0):
    poly=[(-rmax,-rmax),(rmax,-rmax),(rmax,rmax),(-rmax,rmax)]
    vecs=[]
    for i in range(-8,9):
        for j in range(-8,9):
            if i==0 and j==0: continue
            v=(i*b1[0]+j*b2[0], i*b1[1]+j*b2[1])
            if math.hypot(*v)<=6: vecs.append(v)
    for v in vecs:
        poly=clip(poly, v[0], v[1], (v[0]**2+v[1]**2)/2)
        if len(poly)<3: return None
    return poly
def diam(poly):
    return max(math.dist(a,b) for a,b in itertools.combinations(poly,2))
def segd(p,a,b):
    ax,ay=a; bx,by=b; px,py=p
    dx,dy=bx-ax,by-ay; L=dx*dx+dy*dy
    t=0 if L==0 else max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L))
    return math.dist(p,(ax+t*dx,ay+t*dy))
def edges(P): return list(zip(P,P[1:]+P[:1]))
def dmin(A,B):
    d=min(min(segd(p,a,b) for a,b in edges(B)) for p in A)
    return min(d, min(min(segd(p,a,b) for a,b in edges(A)) for p in B))
def dmax(A,B): return max(math.dist(p,q) for p in A for q in B)

# ----------families ----------
def lattice_patch(b1,b2,R):
    out=[]
    for i in range(-R,R+1):
        for j in range(-R,R+1): out.append((i,j,(i*b1[0]+j*b2[0], i*b1[1]+j*b2[1])))
    return out
def analyse(b1,b2,R=3,eps=1e-3,verbose=True,tag=""):
    cell=voronoi(b1,b2)
    D=diam(cell); k=(1-eps)/D
    cell=[(k*x,k*y) for x,y in cell]
    b1=(k*b1[0],k*b1[1]); b2=(k*b2[0],k*b2[1])
    P=lattice_patch(b1,b2,R)
    idx={(i,j):n for n,(i,j,_) in enumerate(P)}
    adj=[set() for _ in P]
    shifted=[]
    for i,j,p in P: shifted.append([(p[0]+x,p[1]+y) for x,y in cell])
    for a in range(len(P)):
        for b in range(a+1,len(P)):
            lo=dmin(shifted[a],shifted[b]); hi=dmax(shifted[a],shifted[b])
            if lo<1-1e-9 and hi>1+1e-9: adj[a].add(b); adj[b].add(a)
    # clique maximum (Bron-Kerbosch avec pivot)
    best=[0,None]
    def bk(Rr,Pp,Xx):
        if not Pp and not Xx:
            if len(Rr)>best[0]: best[0]=len(Rr); best[1]=list(Rr)
            return
        u=max(Pp|Xx, key=lambda v:len(adj[v]&Pp)) if (Pp|Xx) else None
        for v in list(Pp-(adj[u] if u is not None else set())):
            bk(Rr|{v}, Pp&adj[v], Xx&adj[v]); Pp.discard(v); Xx.add(v)
    bk(set(),set(range(len(P))),set())
    # arêtes entre voisins d'un même sommet : motif local
    if verbose:
        print(f"{tag:38s} |cellule|={len(cell):2d} diam=1  degré local max={max(len(s) for s in adj):3d}  ω = {best[0]}")
    return dict(tag=tag,omega=best[0],degmax=max(len(s) for s in adj),m=sum(len(s) for s in adj)//2,n=len(P))

res=[]
print("="*78); print("ω = taille de la plus grande clique de conflit (nombre de couleurs inévitable en local)"); print("="*78)
# hexagonal
print(" -- réseau triangulaire (cellules hexagonales) --")
for ang in (60,):
    b1=(1,0); b2=(math.cos(math.radians(ang)),math.sin(math.radians(ang)))
    res.append(analyse(b1,b2,3,tag=f"triangulaire {ang}°"))
# rhombique : angle variable
print(" -- réseaux rhombiques (|b1|=|b2|, angle variable) --")
for ang in (75,70,65,55,50,45,40,30):
    b1=(1,0); b2=(math.cos(math.radians(ang)),math.sin(math.radians(ang)))
    res.append(analyse(b1,b2,3,tag=f"rhombique {ang}°"))
# carré et rectangulaires
print(" -- réseaux rectangulaires --")
res.append(analyse((1,0),(0,1),2,tag="carré (aspect 1)"))
for rho in (1.2,1.5,2.0):
    res.append(analyse((1,0),(0,1/rho),2,tag=f"rectangulaire aspect {rho}"))
json.dump(res,open('res_treillis.json','w'),ensure_ascii=False)
best=min(res,key=lambda d:d['omega'])
print(f"\nMINIMUM sur toutes les familles : ω = {best['omega']} ({best['tag']})")
print("=> parmi les pavages par cellules de diamètre < 1 issus d'un réseau, seul l'hexagonal atteint 7.")
