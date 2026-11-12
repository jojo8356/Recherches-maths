import math, json, itertools
from fractions import Fraction as Fr

# ---------------- arithmétique exacte dans Q(sqrt3) : a + b*sqrt3 ----------------
class A:
    __slots__=('a','b')
    def __init__(s,a=0,b=0): s.a=Fr(a); s.b=Fr(b)
    def __add__(s,o): return A(s.a+o.a,s.b+o.b)
    def __sub__(s,o): return A(s.a-o.a,s.b-o.b)
    def __mul__(s,o): return A(s.a*o.a+3*s.b*o.b, s.a*o.b+s.b*o.a)
    def __eq__(s,o): return s.a==o.a and s.b==o.b
    def __hash__(s): return hash((s.a,s.b))
    def __repr__(s): return f"({s.a}+{s.b}r3)"
ZERO=A(0); ONE=A(1)

def d2(p,q):
    dx=p[0]-q[0]; dy=p[1]-q[1]
    return dx*dx+dy*dy

def hexpatch(R):
    """points du réseau triangulaire de pas 1 (coordonnées axiales q,r), exacts dans Q(sqrt3)"""
    P=[]
    for q in range(-R,R+1):
        for r in range(-R,R+1):
            if max(abs(q),abs(r),abs(q+r))<=R:
                P.append((A(Fr(q)+Fr(r,2), 0), A(0,Fr(r,2))))  # (q + r/2 , r*sqrt3/2)
    return P

def rot30_scale(p):
    """rotation de 30 degres et mise a l'echelle 1/sqrt3 : sqrt3/3 * R30"""
    x,y=p
    c=A(0,Fr(1,2))          # cos30 = sqrt3/2
    s=A(Fr(1,2))            # sin30 = 1/2
    k=A(0,Fr(1,3))          # 1/sqrt3 = sqrt3/3
    return (k*(c*x-s*y), k*(s*x+c*y))

def build_exact(pts):
    n=len(pts); adj=[set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            if d2(pts[i],pts[j])==ONE: adj[i].add(j); adj[j].add(i)
    return adj

def degeneracy(adj):
    A_=[set(s) for s in adj]; alive=set(range(len(adj))); d=0
    while alive:
        v=min(alive,key=lambda x:(len(A_[x]),x)); d=max(d,len(A_[v]))
        for u in list(A_[v]): A_[u].discard(v)
        alive.discard(v)
    return d

def kcore(adj,k):
    A_=[set(s) for s in adj]; alive=set(range(len(adj))); ch=True
    while ch:
        ch=False
        for v in list(alive):
            if len(A_[v])<k:
                alive.discard(v)
                for u in A_[v]: A_[u].discard(v)
                ch=True
    return alive

def chi(adj,kmax=7):
    n=len(adj)
    for k in range(1,kmax+1):
        col=[-1]*n; order=sorted(range(n),key=lambda v:-len(adj[v]))
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

print("tests d'arithmétique : (1+sqrt3)^2 =",A(1)+A(0,1),"->", (A(1)+A(0,1))*(A(1)+A(0,1)))
print("   dist2 entre (0,0) et (1/2, sqrt3/2) :", d2((A(0),A(0)),(A(Fr(1,2)),A(0,Fr(1,2))))==ONE)

out={}
for R,label in ((3,"R=3"),(4,"R=4"),(5,"R=5")):
    base=hexpatch(R)
    copy=[rot30_scale(p) for p in base]
    pts=list({p for p in base+copy})
    adj=build_exact(pts)
    d=degeneracy(adj)
    cores={k:len(kcore(adj,k)) for k in range(1,d+1)}
    mind=min(len(s) for s in adj); maxd=max(len(s) for s in adj)
    core=d and kcore(adj,d)
    # sous-graphe induit sur le coeur maximal
    idx={v:i for i,v in enumerate(sorted(core))}
    adjc=[set() for _ in core]
    for v in core:
        for u in adj[v]:
            if u in idx: adjc[idx[v]].add(idx[u])
    mind_core=min(len(s) for s in adjc) if adjc else 0
    ch=chi(adjc,7) if len(adjc)<=40 else None
    print(f"\nF4 {label} : {len(pts)} points, {sum(len(s) for s in adj)//2} arêtes exactes")
    print(f"   degré min={mind} max={maxd} | DÉGÉNÉRESCENCE EXACTE = {d}")
    print(f"   cores : {cores}")
    print(f"   coeur maximal : {len(adjc)} sommets, degré min = {mind_core}"+(f", chi = {ch}" if ch else ""))
    out[label]=dict(n=len(pts),m=sum(len(s) for s in adj)//2,mind=mind,maxd=maxd,deg=d,
                    cores=cores,core_n=len(adjc),core_mindeg=mind_core,core_chi=ch)
json.dump(out,open('res_exact.json','w'),ensure_ascii=False)
