"""Partition periodique du plan : tore de periode (U1,U2) quelconque."""
import math, random, itertools

def clip(poly,nx,ny,c):
    out=[]
    for i in range(len(poly)):
        a=poly[i]; b=poly[(i+1)%len(poly)]
        da=nx*a[0]+ny*a[1]-c; db=nx*b[0]+ny*b[1]-c
        if da<=0: out.append(a)
        if (da<0<db) or (db<0<da):
            t=da/(da-db); out.append((a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])))
    return out

def _coords(v,U1,U2):
    det=U1[0]*U2[1]-U1[1]*U2[0]
    return ((v[0]*U2[1]-v[1]*U2[0])/det, (U1[0]*v[1]-U1[1]*v[0])/det)
def wrap(v,U1,U2):
    a,b=_coords(v,U1,U2); a-=round(a); b-=round(b)
    return (a*U1[0]+b*U2[0], a*U1[1]+b*U2[1])

def voronoi_tore(seeds,U1,U2):
    R=0.7*(math.hypot(*U1)+math.hypot(*U2)); cells=[]
    for i,(px,py) in enumerate(seeds):
        poly=[(-R,-R),(R,-R),(R,R),(-R,R)]
        for j,(qx,qy) in enumerate(seeds):
            if i==j: continue
            v=wrap((qx-px,qy-py),U1,U2); d2=v[0]**2+v[1]**2
            poly=clip(poly,v[0],v[1],d2/2)
            if len(poly)<3: return None
        cells.append([(px+x,py+y) for x,y in poly])
    return cells

def diam(poly): return max(math.dist(a,b) for a,b in itertools.combinations(poly,2))
def edges(P): return list(zip(P,P[1:]+P[:1]))
def segd(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; L=dx*dx+dy*dy
    t=0.0 if L==0 else max(0.0,min(1.0,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/L))
    return math.dist(p,(a[0]+t*dx,a[1]+t*dy))
def dmin(A,B): return min(min(segd(p,a,b) for a,b in edges(B)) for p in A)
def dmax(A,B): return max(math.dist(p,q) for p in A for q in B)

def graphe(cells,U1,U2,verbose=False):
    n=len(cells); rad=[diam(c)/2 for c in cells]
    cen=[(sum(p[0] for p in c)/len(c),sum(p[1] for p in c)/len(c)) for c in cells]
    adj=[set() for _ in range(n)]; marges=[]
    for i in range(n):
        for j in range(i+1,n):
            dv=wrap((cen[j][0]-cen[i][0],cen[j][1]-cen[i][1]),U1,U2)
            if math.hypot(*dv)>1.0+rad[i]+rad[j]+0.05: continue
            B=[(x-cen[j][0]+cen[i][0]+dv[0], y-cen[j][1]+cen[i][1]+dv[1]) for x,y in cells[j]]
            lo=dmin(cells[i],B); hi=dmax(cells[i],B)
            if lo<=1+1e-9 and hi>=1-1e-9:
                adj[i].add(j); adj[j].add(i); marges.append(min(hi-1.0,1.0-lo))
    return adj,marges

def clique_max(adj,budget=4_000_000):
    best=[0,None]; calls=[0]
    def bk(R,P,X):
        calls[0]+=1
        if calls[0]>budget: raise TimeoutError
        if not P and not X:
            if len(R)>best[0]: best[0]=len(R); best[1]=set(R)
            return
        u=max(P|X,key=lambda v:len(adj[v]&P)) if (P|X) else None
        for v in list(P-adj[u]):
            bk(R|{v},P&adj[v],X&adj[v]); P.discard(v); X.add(v)
    try: bk(set(),set(range(len(adj))),set())
    except TimeoutError: return None,best[1]
    return best[0],best[1]

def k_color(adj,k,budget=3_000_000):
    n=len(adj); col=[-1]*n; nodes=[0]
    def rec(rest):
        nodes[0]+=1
        if nodes[0]>budget: raise TimeoutError
        if not rest: return True
        v=max(rest,key=lambda x:(len({col[u] for u in adj[x] if col[u]>=0}),len(adj[x])))
        used={col[u] for u in adj[v] if col[u]>=0}
        for c in range(k):
            if c in used: continue
            col[v]=c; rest.discard(v)
            if rec(rest): return True
            rest.add(v); col[v]=-1
        return False
    try: ok=rec(set(range(n)))
    except TimeoutError: return None,col
    return (col if ok else False),col

def normaliser(cells,eps):
    D=max(diam(c) for c in cells); k=(1-eps)/D
    return [[(k*x,k*y) for x,y in c] for c in cells], k
