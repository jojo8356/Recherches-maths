import math, heapq, json, itertools
# famille pentagonale : symétrie d'ordre 5, distances en puissances du nombre d'or
PHI=(1+math.sqrt(5))/2
def rot(p,th): c,s=math.cos(th),math.sin(th); return (c*p[0]-s*p[1], s*p[0]+c*p[1])
def ring(r,n,phase=0.0):
    return [ (r*math.cos(phase+2*math.pi*k/n), r*math.sin(phase+2*math.pi*k/n)) for k in range(n)]
def uniq(P):
    out=[]
    for p in P:
        if not any(abs(p[0]-q[0])<1e-9 and abs(p[1]-q[1])<1e-9 for q in out): out.append(p)
    return out
def graph(P):
    n=len(P); adj=[set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            dx=P[i][0]-P[j][0]; dy=P[i][1]-P[j][1]
            if abs(dx*dx+dy*dy-1)<1e-9: adj[i].add(j); adj[j].add(i)
    return adj
def degeneracy(adj):
    n=len(adj); A=[set(s) for s in adj]; h=[(len(A[v]),v) for v in range(n)]; heapq.heapify(h)
    alive=[True]*n; d=0
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
def chi(adj,kmax=6,budget=400000):
    n=len(adj); order=sorted(range(n),key=lambda v:(-len(adj[v]),v)); nodes=[0]
    for k in range(1,kmax+1):
        col=[-1]*n
        def rec(t):
            nodes[0]+=1
            if nodes[0]>budget: raise TimeoutError
            if t==n: return True
            v=order[t]; used={col[u] for u in adj[v] if col[u]!=-1}
            for c in range(k):
                if c not in used:
                    col[v]=c
                    if rec(t+1): return True
                    col[v]=-1
            return False
        try:
            if rec(0): return k
        except TimeoutError: return None
    return None

res=[]
# pentagone de côté 1
R5=1/(2*math.sin(math.pi/5))
# pentagramme : rayon tel que la diagonale vaille 1
Rd=1/(2*math.sin(2*math.pi/5))
def famille(r_out, ajoute_centre=False, ajoute_interieur=False, n=5):
    P=ring(r_out,n,math.pi/2)
    if ajoute_interieur:
        k=2*math.sin(math.pi/n)/(2*math.sin(2*math.pi/n))   # rapport interieur/exterieur (pentagone)
        P+=ring(r_out*k,n,math.pi/2+math.pi/n)
    if ajoute_centre: P+= [(0.0,0.0)]
    return P
for r,lab,ci,ii in [(R5,"pentagone 5-gone rayon 0,8507",False,False),
                    (R5,"+ centre (roue W5)",True,False),
                    (Rd,"pentagone rayon 0,5257 (diagonales=1)",False,False),
                    (Rd,"+ centre",True,False),
                    (Rd,"+ centre + pentagone interieur",True,True),
                    (R5,"+ centre + pentagone interieur",True,True)]:
    P=uniq(famille(r,ci,ii)); adj=graph(P); d=degeneracy(adj)
    cs={k:len(kcore(adj,k)) for k in range(1,d+1)}
    print(f"{lab:44s} n={len(P):3d} dmin={min((len(s) for s in adj),default=0)} dmax={max((len(s) for s in adj),default=0)} DÉG={d} cores={cs}")
    res.append(dict(lab=lab,n=len(P),deg=d))

# --- et sur la famille de disques concentriques : degré min élevé ? ---
best=(0,None)
for n in (5,6,8,10,12,16,20):
    for k in (2,3):
        P=[]
        for j in range(1,k+1):
            r=j/(2*math.sin(math.pi/n)) if n>=3 else 1
            P+=ring(r,n)
        P=uniq(P); adj=graph(P); d=degeneracy(adj)
        md=min((len(s) for s in adj),default=0)
        if d>best[0]: best=(d,(n,k,md,len(P)))
        if d>=3: print(f"anneaux concentriques n={n:2d}, {k} anneaux : n={len(P):3d} dmin={md} DÉG={d}")
print("\nmeilleure dégénérescence (familles structurées) :",best)
json.dump({'res':res,'best':best},open('res_penta.json','w'),ensure_ascii=False)
