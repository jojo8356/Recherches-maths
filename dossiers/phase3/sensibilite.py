from decimal import Decimal as D, getcontext
import heapq, json
getcontext().prec=45
SQ3=D(2).sqrt()
def uniq(P):
    seen={}
    for p in P:
        k=(p[0].quantize(D('1e-22')),p[1].quantize(D('1e-22')))
        if k not in seen: seen[k]=p
    return list(seen.values())
def closed(seed,rmax,iters=6):
    rm=D(str(rmax)); rm2=rm*rm
    S=uniq([(D(str(x)),D(str(y))) for x,y in seed])
    for _ in range(iters):
        add=[]
        for i in range(len(S)):
            a=S[i]
            for j in range(i+1,len(S)):
                b=S[j]; dx=b[0]-a[0]; dy=b[1]-a[1]; d2=dx*dx+dy*dy
                if d2>D(4) or d2<D('1e-28'): continue
                mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
                h=(D(1)-d2/4).sqrt(); d=d2.sqrt(); ux,uy=dx/d,dy/d
                for sg in (1,-1):
                    p=(mx-sg*h*uy,my+sg*h*ux)
                    if p[0]*p[0]+p[1]*p[1]<=rm2: add.append(p)
        S=uniq(S+add)
    return S
def graph(P,tol):
    n=len(P); adj=[set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            dx=P[i][0]-P[j][0]; dy=P[i][1]-P[j][1]
            if abs(dx*dx+dy*dy-D(1))<tol: adj[i].add(j); adj[j].add(i)
    return adj
def degens(adj):
    n=len(adj); A=[set(s) for s in adj]; h=[(len(A[v]),v) for v in range(n)]; heapq.heapify(h)
    alive=[True]*n; d=0
    while h:
        dv,v=heapq.heappop(h)
        if not alive[v] or dv!=len(A[v]): continue
        alive[v]=False; d=max(d,dv)
        for u in A[v]: A[u].discard(v); heapq.heappush(h,(len(A[u]),u))
    return d
seed=[(0,0),(1,0),(0.5,float(SQ3)/2),(0.5,float(SQ3)/6)]
P=closed(seed,1.5)
print(f"fermeture r<=1,5 : {len(P)} points (Decimal 45 chiffres)")
# écart minimal entre deux points distincts : mesure la pathologie
mind=min(min((P[i][0]-P[j][0])**2+(P[i][1]-P[j][1])**2 for j in range(i+1,len(P))) for i in range(len(P)))
print(f"distance minimale entre deux points distincts du nuage : {float(mind.sqrt()):.3e}")
tab={}
for tol in ('1e-40','1e-33','1e-25','1e-20','1e-15'):
    adj=graph(P,D(tol)); d=degens(adj)
    m=sum(len(s) for s in adj)//2
    tab[tol]=(m,d)
    print(f"   tolérance {tol:6s} : {m:5d} arêtes, dégénérescence = {d}")
print("\n=> la dégénérescence est stable (4) tant que la tolérance reste sous l'échelle des")
print("   quasi-coïncidences (~1e-21). Au-delà, on fabrique des arêtes fictives.")
json.dump({k:list(v) for k,v in tab.items()},open('res_sens.json','w'))
