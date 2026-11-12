from decimal import Decimal as D, getcontext
import math, itertools, heapq, json, time
getcontext().prec=45
SQ3=math.sqrt(3); ONE=D(1); TOL=D('1e-33'); CELL=D(2)

def key(p): return (int(math.floor(float(p[0]))), int(math.floor(float(p[1]))))

def uniqq(P,seen):
    out=[]
    for p in P:
        k=(p[0].quantize(D('1e-22')),p[1].quantize(D('1e-22')))
        if k not in seen: seen[k]=p; out.append(p)
    return out

def pockets(P):
    g={}
    for i,p in enumerate(P): g.setdefault(key(p),[]).append(i)
    return g

def close_pairs(P,g,r):
    """paires (i,j) à distance <= 2 (Decimal) via grille"""
    out=[]
    for (cx,cy),lst in g.items():
        for dx in (-2,-1,0,1,2):
            for dy in (-2,-1,0,1,2):
                oth=g.get((cx+dx,cy+dy))
                if not oth: continue
                for i in lst:
                    for j in oth:
                        if j<=i: continue
                        if abs(dx)==2 and abs(dy)==2 and dx*dy!=0: pass
                        out.append((i,j))
    return set(out)

def closure(seed,rmax,iters=6,maxn=9000):
    rm=D(str(rmax)); rm2=rm*rm; seen={}
    S=uniqq([(D(str(x)),D(str(y))) for x,y in seed],seen)
    for it in range(iters):
        g=pockets(S); add=[]
        for i,j in close_pairs(S,g,rm):
            a,b=S[i],S[j]
            dx=b[0]-a[0]; dy=b[1]-a[1]; d2=dx*dx+dy*dy
            if d2>D(4) or d2<D('1e-28'): continue
            mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
            h=(ONE-d2/4).sqrt(); d=d2.sqrt(); ux,uy=dx/d,dy/d
            for sg in (1,-1):
                p=(mx-sg*h*uy, my+sg*h*ux)
                if p[0]*p[0]+p[1]*p[1]<=rm2: add.append(p)
        S=uniqq(S+add,seen)
        if len(S)>=maxn: break
    return S

def build(P):
    g=pockets(P); n=len(P); adj=[set() for _ in range(n)]
    for i,j in close_pairs(P,g,D(2)):
        dx=P[i][0]-P[j][0]; dy=P[i][1]-P[j][1]
        if abs(dx*dx+dy*dy-ONE)<TOL: adj[i].add(j); adj[j].add(i)
    return adj

def degeneracy(adj):
    n=len(adj); A=[set(s) for s in adj]; h=[(len(A[v]),v) for v in range(n)]
    heapq.heapify(h); alive=[True]*n; d=0
    while h:
        dv,v=heapq.heappop(h)
        if not alive[v] or dv!=len(A[v]): continue
        alive[v]=False; d=max(d,dv)
        for u in A[v]: A[u].discard(v); heapq.heappush(h,(len(A[u]),u))
    return d
def kcore(adj,k):
    n=len(adj); A=[set(s) for s in adj]; alive=set(range(n)); h=[(len(A[v]),v) for v in range(n)]
    heapq.heapify(h)
    while h:
        dv,v=heapq.heappop(h)
        if v not in alive or dv!=len(A[v]): continue
        if dv>=k: break
        alive.discard(v)
        for u in A[v]: A[u].discard(v); heapq.heappush(h,(len(A[u]),u))
    return alive

seed_tc=[(0,0),(1,0),(0.5,SQ3/2),(0.5,SQ3/6)]
out={}
for rmax in (1.7,1.9):
    t0=time.time(); P=closure(seed_tc,rmax)
    print(f"r<={rmax} : {len(P)} points générés ({time.time()-t0:.0f}s)",flush=True)
    adj=build(P); d=degeneracy(adj)
    cs={k:len(kcore(adj,k)) for k in range(1,d+1)}
    n=len(P); m=sum(len(s) for s in adj)//2
    print(f"   m={m} degmin={min(len(s) for s in adj)} degmax={max(len(s) for s in adj)} DÉG={d} cores={cs} ({time.time()-t0:.0f}s)",flush=True)
    out[str(rmax)]=dict(n=n,m=m,deg=d,cores=cs,
        degmax=max(len(s) for s in adj),degmin=min(len(s) for s in adj))
json.dump(out,open('res_hp2.json','w'))
