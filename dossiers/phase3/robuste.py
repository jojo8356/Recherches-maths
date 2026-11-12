import math, json, itertools
SQ3=math.sqrt(3); DEDUP=1e-9; EDGE=1e-9

def uniq(P):
    out=[]
    for p in P:
        if not any(abs(p[0]-q[0])<DEDUP and abs(p[1]-q[1])<DEDUP for q in out): out.append(p)
    return out

def graph(P):
    n=len(P); adj=[set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            dx=P[i][0]-P[j][0]; dy=P[i][1]-P[j][1]
            if abs(dx*dx+dy*dy-1.0)<EDGE: adj[i].add(j); adj[j].add(i)
    return adj

def degeneracy(adj):
    A=[set(s) for s in adj]; alive=set(range(len(adj))); d=0; hist=[]
    while alive:
        v=min(alive,key=lambda x:(len(A[x]),x)); hist.append(len(A[v])); d=max(d,len(A[v]))
        for u in list(A[v]): A[u].discard(v)
        alive.discard(v)
    return d,hist

def kcore(adj,k):
    A=[set(s) for s in adj]; alive=set(range(len(adj))); ch=True
    while ch:
        ch=False
        for v in list(alive):
            if len(A[v])<k:
                alive.discard(v)
                for u in A[v]: A[u].discard(v)
                ch=True
    return alive

def stats(name,P,verbose=True):
    P=uniq(P); adj=graph(P); d,_=degeneracy(adj)
    n=len(P); m=sum(len(s) for s in adj)//2
    mind=min((len(s) for s in adj),default=0); maxd=max((len(s) for s in adj),default=0)
    cs={k:len(kcore(adj,k)) for k in range(1,d+1)}
    if verbose: print(f"{name:46s} n={n:4d} m={m:5d} dmin={mind} dmax={maxd} DÉG={d}  cores={cs}")
    return dict(name=name,n=n,m=m,mind=mind,maxd=maxd,deg=d,cores=cs)

res=[]
# ---- familles de référence ----
def hexpatch(R,sp=1.0):
    return [(sp*(q+r/2), sp*(r*SQ3/2)) for q in range(-R,R+1) for r in range(-R,R+1)
            if max(abs(q),abs(r),abs(q+r))<=R]
def kagome(R):
    base=hexpatch(R,2.0); P=[]
    for i in range(len(base)):
        for j in range(i+1,len(base)):
            if abs(math.dist(base[i],base[j])-2)<1e-9:
                P.append(((base[i][0]+base[j][0])/2,(base[i][1]+base[j][1])/2))
    return P
def rot30_scale(p,k=1/SQ3,th=math.pi/6):
    c,s=math.cos(th),math.sin(th)
    return (k*(c*p[0]-s*p[1]), k*(s*p[0]+c*p[1]))
res.append(stats("triangulaire hexagonal R=6",hexpatch(6)))
res.append(stats("kagomé R=3",kagome(3)))
res.append(stats("triangulaire + translaté (1/2,√3/6) R=4",hexpatch(4)+[(x+.5,y+SQ3/6) for x,y in hexpatch(4)]))
res.append(stats("triangulaire + copie R30/√3 R=4  [AVEC dédoublonnage]",hexpatch(4)+[rot30_scale(p) for p in hexpatch(4)]))
for n in (2,3):
    P=[]
    for j in range(n):
        P+=[rot30_scale(p,1/SQ3**j,math.pi/6*j) for p in hexpatch(4)]
    res.append(stats(f"{n} copies emboîtées (échelles 1/√3^j)",P))
print()
# ---- fermeture sous 'point à distance 1 de deux points existants' ----
def closure(seed, rmax=2.2, maxn=420, iters=12):
    S=uniq(seed)
    for it in range(iters):
        add=[]
        for a,b in itertools.combinations(S,2):
            d=math.dist(a,b)
            if d<=1e-12 or d>2: continue
            mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
            h=math.sqrt(max(0.0,1-(d/2)**2)); ux,uy=(b[0]-a[0])/d,(b[1]-a[1])/d
            for sgn in (1,-1):
                p=(mx-sgn*h*uy, my+sgn*h*ux)
                if p[0]**2+p[1]**2<=rmax*rmax: add.append(p)
        S=uniq(S+add)
        if len(S)>maxn: S=S[:maxn]
    return S
def spindle():
    V=[(-SQ3/2,0),(SQ3/2,0),(0,0.5),(0,-0.5)]
    B,A_=V[1],V[0]; d=math.dist(B,A_); a=(d*d+2)/(2*d); h=math.sqrt(max(0,3-a*a))
    ux,uy=(A_[0]-B[0])/d,(A_[1]-B[1])/d
    E=(B[0]+a*ux-h*uy,B[1]+a*uy+h*ux); mid=((B[0]+E[0])/2,(B[1]+E[1])/2)
    vx,vy=(E[0]-B[0])/SQ3,(E[1]-B[1])/SQ3
    return V+[E,(mid[0]+0.5*vy,mid[1]-0.5*vx),(mid[0]-0.5*vy,mid[1]+0.5*vx)]
seeds={"triangle équilatéral":[(0,0),(1,0),(0.5,SQ3/2)],
       "fuseau de Moser":spindle(),
       "triangle + centre de gravité":[(0,0),(1,0),(0.5,SQ3/2),(0.5,SQ3/6)]}
for name,s in seeds.items():
    for rmax in (1.6,2.2):
        P=closure(s,rmax=rmax)
        res.append(stats(f"fermeture de {name} (r<= {rmax})",P))
json.dump(res,open('res_robuste.json','w'),ensure_ascii=False)
best=max(res,key=lambda r:r['deg'])
print(f"\nMEILLEURE DÉGÉNÉRESCENCE OBSERVÉE (pipeline dédoublonné) : {best['deg']}  ({best['name']})")
