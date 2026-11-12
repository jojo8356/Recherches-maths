from decimal import Decimal as D, getcontext
import math, itertools, heapq, json, time
getcontext().prec=45
SQ3=math.sqrt(3)
ONE=D(1); TOL=D('1e-35')

def uniq(P):
    seen={}
    for p in P:
        k=(p[0].quantize(D('1e-25')), p[1].quantize(D('1e-25')))
        if k not in seen: seen[k]=p
    return list(seen.values())

def graph(P):
    n=len(P); adj=[set() for _ in range(n)]
    for i in range(n):
        xi,yi=P[i]
        for j in range(i+1,n):
            dx=xi-P[j][0]; dy=yi-P[j][1]
            if abs(dx*dx+dy*dy-ONE)<TOL: adj[i].add(j); adj[j].add(i)
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
    n=len(adj); A=[set(s) for s in adj]; alive=set(range(n)); h=[(len(A[v]),v) for v in range(n)]
    heapq.heapify(h)
    while h:
        dv,v=heapq.heappop(h)
        if v not in alive or dv!=len(A[v]): continue
        if dv>=k: break
        alive.discard(v)
        for u in A[v]: A[u].discard(v); heapq.heappush(h,(len(A[u]),u))
    return alive

def chi(adj,kmax=6):
    n=len(adj); order=sorted(range(n),key=lambda v:-len(adj[v]))
    for k in range(1,kmax+1):
        col=[-1]*n
        def rec(t):
            if t==n: return True
            v=order[t]
            used={col[u] for u in adj[v] if col[u]!=-1}
            for c in range(k):
                if c not in used:
                    col[v]=c
                    if rec(t+1): return True
                    col[v]=-1
            return False
        if rec(0): return k
    return None

def closed(seed, rmax, iters=6, maxn=700):
    rm=D(str(rmax)); rm2=rm*rm
    S=uniq([(D(str(x)),D(str(y))) for x,y in seed])
    for it in range(iters):
        add=[]
        for a,b in itertools.combinations(S,2):
            dx=b[0]-a[0]; dy=b[1]-a[1]; d2=dx*dx+dy*dy
            if d2>D(4) or d2<D('1e-30'): continue
            mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
            h=(ONE-d2/4).sqrt()
            d=abs(d2).sqrt(); ux,uy=dx/d,dy/d
            for sg in (1,-1):
                p=(mx-sg*h*uy, my+sg*h*ux)
                if p[0]*p[0]+p[1]*p[1]<=rm2: add.append(p)
        S=uniq(S+add)
        if len(S)>=maxn: break
    return S

seed_tc=[(0,0),(1,0),(0.5,SQ3/2),(0.5,SQ3/6)]
for rmax in (1.2,1.5):
    t0=time.time()
    P=closed(seed_tc,rmax)
    adj=graph(P); d=degeneracy(adj)
    cs={k:len(kcore(adj,k)) for k in range(1,d+1)}
    n=len(P); m=sum(len(s) for s in adj)//2
    print(f"[45 chiffres] triangle+centre, r<={rmax} : n={n} m={m} "
          f"degmin={min(len(s) for s in adj)} degmax={max(len(s) for s in adj)} DÉG={d} cores={cs} ({time.time()-t0:.0f}s)",flush=True)
    if d>=4:
        core=sorted(kcore(adj,d)); idx={v:i for i,v in enumerate(core)}
        adjc=[set() for _ in core]
        for v in core:
            for u in adj[v]:
                if u in idx: adjc[idx[v]].add(idx[u])
        print(f"    coeur {d} : {len(core)} sommets, degré min {min(len(s) for s in adjc)}",
              f"| chi = {chi(adjc,6) if len(core)<=60 else 'non calculé (trop gros)'}",flush=True)
        json.dump({'rmax':rmax,'n':n,'m':m,'deg':d,'cores':cs,'core_n':len(core),
                   'core_mindeg':min(len(s) for s in adjc)},open(f'res_hp_{rmax}.json','w'))
