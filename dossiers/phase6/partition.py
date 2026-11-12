"""Phase 6 - experience A : partition aleatoire periodique du plan.
Le plan est pave periodiquement (tore de periode P) par les cellules de Voronoi
d'un jeu de germes aleatoires ; on normalise pour que le diametre maximal vaille
1 - eps, puis on construit le graphe de conflit exact et on cherche omega / chi."""
import math, random, itertools, json

# ---------- geometrie ----------
def clip(poly, nx, ny, c):
    out=[]; n=len(poly)
    for i in range(n):
        a=poly[i]; b=poly[(i+1)%n]
        da=nx*a[0]+ny*a[1]-c; db=nx*b[0]+ny*b[1]-c
        if da<=0: out.append(a)
        if (da<0<db) or (db<0<da):
            t=da/(da-db); out.append((a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])))
    return out
def wrap(v,P):
    return ((v[0]+P/2)%P-P/2, (v[1]+P/2)%P-P/2)
def voronoi_tore(seeds,P):
    cells=[]
    for i,(px,py) in enumerate(seeds):
        poly=[(-P/2,-P/2),(P/2,-P/2),(P/2,P/2),(-P/2,P/2)]
        for j,(qx,qy) in enumerate(seeds):
            if i==j: continue
            v=wrap((qx-px,qy-py),P)
            d2=v[0]*v[0]+v[1]*v[1]
            if d2>4*(P/2)**2: pass
            poly=clip(poly, v[0], v[1], d2/2)
            if len(poly)<3: return None
        cells.append([(px+x,py+y) for x,y in poly])   # ramene au voisinage du germe
    return cells
def diam(poly): return max(math.dist(a,b) for a,b in itertools.combinations(poly,2))
def edges(P_):
    return list(zip(P_,P_[1:]+P_[:1]))
def segd(p,a,b):
    ax,ay=a; bx,by=b; dx,dy=bx-ax,by-ay; L=dx*dx+dy*dy
    t=0.0 if L==0 else max(0.0,min(1.0,((p[0]-ax)*dx+(p[1]-ay)*dy)/L))
    return math.dist(p,(ax+t*dx,ay+t*dy))
def dmin(A,B): return min(min(segd(p,a,b) for a,b in edges(B)) for p in A)
def dmax(A,B): return max(math.dist(p,q) for p in A for q in B)

# ---------- graphe de conflit ----------
def graphe_conflit(cells, P, diam_max, verbose=False):
    n=len(cells); rad=[diam(c)/2 for c in cells]
    cen=[(sum(p[0] for p in c)/len(c), sum(p[1] for p in c)/len(c)) for c in cells]
    adj=[set() for _ in range(n)]; marges=[]
    for i in range(n):
        for j in range(i+1,n):
            dv=wrap((cen[j][0]-cen[i][0], cen[j][1]-cen[i][1]), P)
            if math.hypot(*dv) > 1.0+rad[i]+rad[j]+0.05: continue
            B=[(cen[i][0]+dv[0]+x-cen[j][0], cen[i][1]+dv[1]+y-cen[j][1]) for x,y in cells[j]]
            lo=dmin(cells[i],B); hi=dmax(cells[i],B)
            # test conservateur : on ajoute l'arete des que l'intervalle [lo,hi] touche 1
            if lo <= 1+1e-9 and hi >= 1-1e-9:
                adj[i].add(j); adj[j].add(i); marges.append(min(hi-1.0, 1.0-lo))
    return adj, marges

# ---------- clique maximum (Bron-Kerbosch avec pivot, budget) ----------
def clique_max(adj, budget=3_000_000):
    n=len(adj); best=[0,None]; calls=[0]
    def bk(R,P,X):
        calls[0]+=1
        if calls[0]>budget: raise TimeoutError
        if not P and not X:
            if len(R)>best[0]: best[0]=len(R); best[1]=set(R)
            return
        u=max(P|X,key=lambda v:len(adj[v]&P)) if (P|X) else None
        for v in list(P-adj[u]):
            bk(R|{v},P&adj[v],X&adj[v]); P.discard(v); X.add(v)
    try: bk(set(),set(range(n)),set())
    except TimeoutError: return None,best[1]
    return best[0],best[1]

# ---------- k-coloriage exact (DSATUR + retour arriere, budget) ----------
def k_coloriage(adj,k,budget=2_000_000):
    n=len(adj); col=[-1]*n; nodes=[0]
    def rec(restant):
        nodes[0]+=1
        if nodes[0]>budget: raise TimeoutError
        if not restant: return True
        v=max(restant, key=lambda x:(len({col[u] for u in adj[x] if col[u]>=0}), len(adj[x])))
        used={col[u] for u in adj[v] if col[u]>=0}
        for c in range(k):
            if c in used: continue
            col[v]=c; restant.discard(v)
            if rec(restant): return True
            restant.add(v); col[v]=-1
        return False
    try:
        ok=rec(set(range(n)))
    except TimeoutError:
        return None,col
    return (col if ok else False),col

# ---------- generation des germes ----------
def germes_hex_jitter(P,s,jit,seed):
    rnd=random.Random(seed); out=[]
    ny=int(P/(s*math.sqrt(3)/2))+1
    for j in range(ny):
        for i in range(int(P/s)+1):
            x=i*s+(j%2)*s/2; y=j*s*math.sqrt(3)/2
            a=rnd.uniform(0,2*math.pi); r=jit*s*math.sqrt(rnd.uniform(0,1))
            out.append(((x+r*math.cos(a))%P,(y+r*math.sin(a))%P))
    return out
def germes_poisson(P,n,seed):
    rnd=random.Random(seed); return [(rnd.uniform(0,P),rnd.uniform(0,P)) for _ in range(n)]

def experience(tag,seeds,P,eps=1e-4,do_color=True,verbose=True):
    cells=voronoi_tore(seeds,P)
    if cells is None: return dict(tag=tag,erreur="cellule vide")
    D=max(diam(c) for c in cells); k=(1-eps)/D
    cells=[[(k*x,k*y) for x,y in c] for c in cells]; P2=k*P
    dm=[diam(c) for c in cells]
    adj,marges=graphe_conflit(cells,P2,D)
    deg=[len(a) for a in adj]
    w,cl=clique_max(adj)
    res=dict(tag=tag,n=len(cells),P=P2,diam_max=max(dm),diam_moy=sum(dm)/len(dm),
             diam_min=min(dm),aretes=sum(deg)//2,deg_moy=sum(deg)/len(deg),deg_max=max(deg),
             omega=w,marge_min=(min(marges) if marges else None))
    if do_color:
        chi=None; col=None
        for kk in range(max(3,w if w else 3),8):
            r,c=k_coloriage(adj,kk)
            if r is None: chi=f">{kk}(budget)"; break
            if r: chi=kk; col=c; break
        res["chi"]=chi
        if col and all(c>=0 for c in col): res["coloriage"]=col
    if verbose:
        print(f"  {tag:30s} n={res['n']:4d} diam {res['diam_min']:.3f}-{res['diam_max']:.4f} (moy {res['diam_moy']:.3f}) "
              f"aretes={res['aretes']:5d} deg moy {res['deg_moy']:.1f} max {res['deg_max']:3d} | "
              f"omega={res['omega']} chi={res.get('chi')} marge_min={res['marge_min']}")
    return res
