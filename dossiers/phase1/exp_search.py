import math, random, json, itertools, time
random.seed(7)

def unit_graph(pts, tol=1e-6):
    n=len(pts); nb=[0]*n
    for i in range(n):
        xi,yi=pts[i]
        for j in range(i+1,n):
            dx=xi-pts[j][0]; dy=yi-pts[j][1]
            if abs(dx*dx+dy*dy-1.0)<tol: nb[i]|=1<<j; nb[j]|=1<<i
    return nb

def chromatic(nb, kmax=None, budget=200000):
    n=len(nb); kmax=kmax or n; nodes=[0]
    order=None
    def attempt(k):
        col=[-1]*n
        def rec(done):
            nodes[0]+=1
            if nodes[0]>budget: raise TimeoutError
            if done==n: return True
            bv,bs,bd=-1,-1,-1
            for v in range(n):
                if col[v]!=-1: continue
                m=nb[v]; used=0
                while m:
                    b=(m&-m).bit_length()-1; m&=m-1
                    if col[b]!=-1: used|=1<<col[b]
                sat=bin(used).count('1')
                if (sat,bin(nb[v]).count('1'))>(bs,bd): bv,bs,bd=v,sat,bin(nb[v]).count('1')
            used=0; m=nb[bv]
            while m:
                b=(m&-m).bit_length()-1; m&=m-1
                if col[b]!=-1: used|=1<<col[b]
            for c in range(k):
                if not (used>>c)&1:
                    col[bv]=c
                    if rec(done+1): return True
                    col[bv]=-1
            return False
        return rec(0)
    for k in range(1,kmax+1):
        try:
            if attempt(k): return k
        except TimeoutError:
            return None
    return None

def tri_lattice(n):
    return [(i+j/2, j*math.sqrt(3)/2) for i in range(-n,n+1) for j in range(-n,n+1)
            if abs(i+j/2)<=n and abs(j*math.sqrt(3)/2)<=n]

def rot(pts,th,tx,ty):
    c,s=math.cos(th),math.sin(th)
    return [(c*x-s*y+tx, s*x+c*y+ty) for x,y in pts]

# --- E3a : un seul réseau triangulaire ---
base=tri_lattice(3)
print(f"E3a réseau triangulaire, {len(base)} points -> χ =", chromatic(unit_graph(base)))

# --- E3b : union de copies tournées (stratégie 'de Grey' en miniature) ---
results=[]; best=(0,None)
t0=time.time()
trials=0
for trial in range(300):
    if time.time()-t0>150: break
    k=random.choice([2,2,3])
    pts=[]
    for _ in range(k):
        th=random.uniform(0,math.pi)
        tx,ty=random.uniform(-1,1),random.uniform(-1,1)
        sub=tri_lattice(random.choice([2,2,3]))
        pts+=rot(sub,th,tx,ty)
    # dédoublonnage grossier
    seen=set(); P=[]
    for x,y in pts:
        key=(round(x,7),round(y,7))
        if key in seen: continue
        seen.add(key); P.append((x,y))
    if len(P)>90: P=random.sample(P,90)
    nb=unit_graph(P)
    chi=chromatic(nb,kmax=6,budget=60000)
    trials+=1
    if chi is not None:
        results.append((len(P),chi))
        if chi>best[0]: best=(chi,len(P))
print(f"E3b {trials} essais d'unions de réseaux tournés (<=90 points) — meilleur χ trouvé : {best[0]} (n={best[1]})")
from collections import Counter
print("   distribution des χ :", dict(Counter(c for _,c in results)))
json.dump({'chi_tri':3,'trials':trials,'best':best,'dist':dict(Counter(c for _,c in results))},open('res_search.json','w'))
