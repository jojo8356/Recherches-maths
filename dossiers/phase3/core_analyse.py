from decimal import Decimal as D, getcontext
import heapq, json
getcontext().prec=45
pts=[tuple(D(t) for t in l.split('\t')) for l in open('coeur4_sommets.tsv') if not l.startswith('#')]
n=len(pts)
def build(tol):
    tol=D(tol); adj=[set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            dx=pts[i][0]-pts[j][0]; dy=pts[i][1]-pts[j][1]
            if abs(dx*dx+dy*dy-D(1))<tol: adj[i].add(j); adj[j].add(i)
    return adj
def degens(adj):
    A=[set(s) for s in adj]; h=[(len(A[v]),v) for v in range(n)]; heapq.heapify(h)
    alive=[True]*n; d=0
    while h:
        dv,v=heapq.heappop(h)
        if not alive[v] or dv!=len(A[v]): continue
        alive[v]=False; d=max(d,dv)
        for u in A[v]: A[u].discard(v); heapq.heappush(h,(len(A[u]),u))
    return d
print(f"cœur : {n} sommets")
tab=[]
for tol in ('1e-40','1e-33','1e-28','1e-24','1e-21','1e-20','1e-18'):
    adj=build(tol); m=sum(len(s) for s in adj)//2; d=degens(adj)
    md=min(len(s) for s in adj)
    tab.append((tol,m,d,md))
    print(f"   tolérance {tol:6s} : {m:4d} arêtes, degré min={md:2d}, DÉGÉNÉRESCENCE={d}")
adj=build('1e-33')
degs=sorted((len(s) for s in adj),reverse=True)
print("\ndistribution des degrés (tol 1e-33) :",degs)
import collections
print("histogramme :",dict(sorted(collections.Counter(degs).items())))
json.dump({'tab':tab,'degs':degs},open('res_core_analyse.json','w'))
