import math, itertools, json
SQ3=math.sqrt(3)
TOL=1e-7

def build(pts, tol=TOL):
    n=len(pts); adj=[set() for _ in range(n)]
    for i in range(n):
        xi,yi=pts[i]
        for j in range(i+1,n):
            dx=xi-pts[j][0]; dy=yi-pts[j][1]
            if abs(dx*dx+dy*dy-1.0)<tol: adj[i].add(j); adj[j].add(i)
    return adj

def degeneracy(adj):
    A=[set(s) for s in adj]; alive=set(range(len(adj))); order=[]; degs=[]
    while alive:
        v=min(alive,key=lambda x:(len(A[x]),x)); degs.append(len(A[v])); order.append(v)
        for u in list(A[v]): A[u].discard(v)
        alive.discard(v)
    d=max(degs) if degs else 0
    return d, degs

def core_sizes(adj, kmax):
    """taille du k-core pour chaque k"""
    out={}
    A=[set(s) for s in adj]; alive=set(range(len(adj)))
    cur=kmax+1
    # peeling par degré croissant
    import heapq
    deg={v:len(A[v]) for v in range(len(adj))}
    h=[(deg[v],v) for v in range(len(adj))]; heapq.heapify(h); removed=set(); k=max(deg.values()) if deg else 0
    # on enregistre la taille des cores : recompter simplement
    for kk in range(1,kmax+1):
        A=[set(s) for s in adj]; alive=set(range(len(adj)))
        changed=True
        while changed:
            changed=False
            for v in list(alive):
                if len(A[v])<kk:
                    alive.discard(v)
                    for u in A[v]: A[u].discard(v)
                    changed=True
        out[kk]=len(alive)
    return out

def report(name, pts, verbose=True):
    adj=build(pts)
    d,degs=degeneracy(adj)
    n=len(pts); m=sum(len(s) for s in adj)//2
    mind=min(len(s) for s in adj) if n else 0
    cs=core_sizes(adj, d+1)
    if verbose:
        print(f"{name:52s} n={n:4d} m={m:5d} degré min={mind:2d} max={max(len(s) for s in adj) if n else 0:2d}  DÉGÉNÉRESCENCE={d}")
        print(f"{'':52s} cores : "+" ".join(f"C{k}={v}" for k,v in cs.items() if v>0))
    return dict(name=name,n=n,m=m,mind=mind,d=d,cores=cs)

res=[]
# ---------- F1 : patchs de réseau triangulaire (hexagonaux) ----------
def hexpatch(R, spacing=1.0):
    P=[]
    for q in range(-R,R+1):
        for r in range(-R,R+1):
            if max(abs(q),abs(r),abs(q+r))<=R:
                P.append((spacing*(q+r/2), spacing*(r*SQ3/2)))
    return P
for R in (2,3,4,6):
    res.append(report(f"F1 réseau triangulaire hexagonal R={R}",hexpatch(R)))

# ---------- F2 : kagomé (milieux des arêtes du réseau triangulaire) ----------
def kagome(R):
    P=set()
    base=hexpatch(R,2.0)
    for i in range(len(base)):
        for j in range(i+1,len(base)):
            if abs(math.dist(base[i],base[j])-2)<TOL:
                P.add(((base[i][0]+base[j][0])/2,(base[i][1]+base[j][1])/2))
    return list(P)
for R in (2,3):
    res.append(report(f"F2 kagomé R={R}",kagome(R)))

# ---------- F3 : superposition Lambda + (Lambda + v) ----------
def sup(R):
    base=hexpatch(R)
    v=(0.5, SQ3/6)      # centre d'un triangle unité : 3 points du réseau à distance 1
    P=base+[(x+v[0],y+v[1]) for x,y in base]
    return P
for R in (3,4):
    res.append(report(f"F3 réseau + translaté (3 arêtes croisées/point) R={R}",sup(R)))

# ---------- F4 : superposition de DEUX réseaux triangulaires tournés de 30°, échelle 1/sqrt(3) ----------
def sup2(R):
    base=hexpatch(R)
    s=1/SQ3; th=math.pi/6; c,si=math.cos(th),math.sin(th)
    P=list(base)
    for x,y in base:
        P.append((s*(c*x-si*y), s*(si*x+c*y)))
    return P
for R in (3,4):
    res.append(report(f"F4 réseau + copie tournée 30°, échelle 1/√3  R={R}",sup2(R)))
json.dump(res,open('res_atelier1.json','w'),ensure_ascii=False)
print("\nmeilleure dégénérescence observée :",max(r['d'] for r in res))
