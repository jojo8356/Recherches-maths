import math, json, itertools, heapq, sys
SQ3=math.sqrt(3)
Q=1e-7            # pas de quantification pour le dédoublonnage
EDGE=1e-9

def uniq(P):
    seen={}
    for p in P:
        k=(round(p[0]/Q), round(p[1]/Q))
        if k not in seen: seen[k]=p
    return list(seen.values())

def graph(P):
    n=len(P); grid={}
    for i,p in enumerate(P): grid.setdefault((math.floor(p[0]),math.floor(p[1])),[]).append(i)
    adj=[set() for _ in range(n)]
    for i,(x,y) in enumerate(P):
        cx,cy=math.floor(x),math.floor(y)
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                for j in grid.get((cx+dx,cy+dy),()):
                    if j<=i: continue
                    ex,ey=P[j][0]-x,P[j][1]-y
                    if abs(ex*ex+ey*ey-1.0)<EDGE: adj[i].add(j); adj[j].add(i)
    return adj

def degeneracy(adj):
    n=len(adj); A=[set(s) for s in adj]
    h=[(len(A[v]),v) for v in range(n)]; heapq.heapify(h); alive=[True]*n; d=0
    while h:
        dv,v=heapq.heappop(h)
        if not alive[v] or dv!=len(A[v]): continue
        alive[v]=False; d=max(d,dv)
        for u in A[v]:
            A[u].discard(v); heapq.heappush(h,(len(A[u]),u))
    return d

def kcore(adj,k):
    n=len(adj); A=[set(s) for s in adj]; alive=set(range(n)); dq=[]
    for v in range(n): dq.append((len(A[v]),v))
    heapq.heapify(dq)
    while dq:
        dv,v=heapq.heappop(dq)
        if v not in alive or dv!=len(A[v]): continue
        if dv>=k: break
        alive.discard(v)
        for u in A[v]:
            A[u].discard(v); heapq.heappush(dq,(len(A[u]),u))
    return alive

def stats(name,P,verbose=True):
    P=uniq(P); adj=graph(P); d=degeneracy(adj)
    n=len(P); m=sum(len(s) for s in adj)//2
    mind=min((len(s) for s in adj),default=0); maxd=max((len(s) for s in adj),default=0)
    cs={k:len(kcore(adj,k)) for k in range(1,d+1)}
    if verbose:
        print(f"{name:44s} n={n:4d} m={m:5d} dmin={mind:2d} dmax={maxd:2d} DÉG={d}  cores={cs}",flush=True)
    return dict(name=name,n=n,m=m,mind=mind,maxd=maxd,deg=d,cores=cs)

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
def rot(p,k,th):
    c,s=math.cos(th),math.sin(th); return (k*(c*p[0]-s*p[1]), k*(s*p[0]+c*p[1]))
def spindle():
    V=[(-SQ3/2,0),(SQ3/2,0),(0,0.5),(0,-0.5)]; B,A_=V[1],V[0]
    d=math.dist(B,A_); a=(d*d+2)/(2*d); h=math.sqrt(max(0,3-a*a))
    ux,uy=(A_[0]-B[0])/d,(A_[1]-B[1])/d
    E=(B[0]+a*ux-h*uy,B[1]+a*uy+h*ux); mid=((B[0]+E[0])/2,(B[1]+E[1])/2)
    vx,vy=(E[0]-B[0])/SQ3,(E[1]-B[1])/SQ3
    return V+[E,(mid[0]+0.5*vy,mid[1]-0.5*vx),(mid[0]-0.5*vy,mid[1]+0.5*vx)]

res=[]
res.append(stats("triangulaire hexagonal R=8",hexpatch(8)))
res.append(stats("kagomé R=3",kagome(3)))
res.append(stats("triangulaire + translaté R=4",hexpatch(4)+[(x+.5,y+SQ3/6) for x,y in hexpatch(4)]))
res.append(stats("triangulaire + copie R30/√3 (dédoublonné)",hexpatch(4)+[rot(p,1/SQ3,math.pi/6) for p in hexpatch(4)]))
for n in (3,4):
    P=[]
    for j in range(n): P+=[rot(p,1/SQ3**j,math.pi/6*j) for p in hexpatch(3)]
    res.append(stats(f"{n} copies emboîtées 1/√3^j",P))
res.append(stats("fuseau de Moser",spindle()))

print(flush=True)
def closure(seed,rmax=2.0,maxn=260,iters=6):
    S=uniq(seed)
    for it in range(iters):
        add=[]
        for a,b in itertools.combinations(S,2):
            d=math.dist(a,b)
            if d>2 or d<1e-9: continue
            mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
            h=math.sqrt(max(0.0,1-(d/2)**2)); ux,uy=(b[0]-a[0])/d,(b[1]-a[1])/d
            for sg in (1,-1): add.append((mx-sg*h*uy,my+sg*h*ux))
        S=uniq(S+[p for p in add if p[0]**2+p[1]**2<=rmax*rmax])
        if len(S)>=maxn: break
    return S
for name,s in {"triangle":[(0,0),(1,0),(0.5,SQ3/2)],
               "fuseau":spindle(),
               "triangle+centre":[(0,0),(1,0),(0.5,SQ3/2),(0.5,SQ3/6)]}.items():
    for rmax in (1.5,2.0):
        P=closure(s,rmax=rmax)
        res.append(stats(f"fermeture {name} r<={rmax}",P))
json.dump(res,open('res_robuste2.json','w'),ensure_ascii=False)
b=max(res,key=lambda r:r['deg'])
print(f"\nMEILLEURE DÉGÉNÉRESCENCE : {b['deg']} ({b['name']}, n={b['n']})",flush=True)
