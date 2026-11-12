import json, math, itertools
def hexdist(dq,dr): return max(abs(dq),abs(dr),abs(dq+dr))
D=[(q,r) for q in range(-2,3) for r in range(-2,3) if 0<hexdist(q,r)<=2]
assert len(D)==18, len(D)

class Lat:
    def __init__(s,a,b,c,d):
        s.gen=((a,b),(c,d)); s.det=a*d-b*c   # colonnes : (a,b) et (c,d)
    def key(s,p,q):
        a,b=s.gen[0]; c,d=s.gen[1]; det=s.det
        i=( d*p - c*q)/det; j=(-b*p + a*q)/det
        u=round((i-math.floor(i+1e-12))*abs(det))%abs(det)
        v=round((j-math.floor(j+1e-12))*abs(det))%abs(det)
        return (u,v)
    def classes(s):
        S={s.key(p,q) for p in range(-8,9) for q in range(-8,9)}
        return S

def quotient_graph(L):
    cl=sorted(L.classes()); m=len(cl); idx={c:i for i,c in enumerate(cl)}
    dk={L.key(*v) for v in D}
    if (0,0) in dk: return None            # un vecteur de conflit est dans le réseau -> impossible
    nb=[0]*m
    for c in cl:
        u=idx[c]
        for (x,y) in dk:
            v=idx.get(((c[0]+x)%abs(L.det),(c[1]+y)%abs(L.det)))
            if v is not None: nb[u]|=1<<v; nb[v]|=1<<u
    return cl,nb,dk,m

def color_graph(nb,k):
    n=len(nb); order=sorted(range(n), key=lambda v:-bin(nb[v]).count('1'))
    col=[-1]*n
    def rec(t):
        if t==n: return True
        v=order[t]
        used={col[u] for u in range(n) if col[u]!=-1 and (nb[v]>>u)&1}
        for c in range(k):
            if c not in used:
                col[v]=c
                if rec(t+1): return True
                col[v]=-1
        return False
    return col if rec(0) else None

best=None
for det in range(2,31):
    for a in range(-7,8):
      for b in range(-7,8):
        for c in range(-7,8):
          for d in range(-7,8):
            if abs(a*d-b*c)!=det: continue
            L=Lat(a,b,c,d); Q=quotient_graph(L)
            if not Q: continue
            cl,nb,dk,m=Q
            r=color_graph(nb,7)
            if r is not None:
                if best is None or m<best[0]: best=(m,L,cl,r,dk, sorted(dk))
                break
          else: continue
          break
        else: continue
        break
      else: continue
      break
    if best and best[0]<=det: break

m,L,cl,col,dk,dl=sorted(best[0:1])[0] if False else None,None,None,None,None,None
m,L,cl,col,dk,dl=best
print(f"plus petit indice trouvé : m={m}, réseau engendré par {L.gen[0]} et {L.gen[1]} (det={L.det})")
print("classes :",cl)
print("couleurs :",dict(zip(cl,col)))
# --- vérification exhaustive sur un grand patch ---
S=set()
for p in range(-16,17):
    for q in range(-16,17): S.add(L.key(p,q))
assert S==set(cl), "classes non stables"
viol=0; checks=0
for p in range(-16,17):
    for q in range(-16,17):
        for (dq,dr) in D:
            checks+=1
            if L.key(p,q)==L.key(p+dq,q+dr): viol+=1
print(f"vérification : {checks} contraintes sur le patch R≈16 -> {viol} violation(s)")
cmap=dict(zip(cl,col))
print("fleur (7 cellules) -> couleurs :", sorted({cmap[L.key(*f)] for f in [(0,0)]+[(x,y) for x in range(-1,2) for y in range(-1,2) if hexdist(x,y)==1]}))
json.dump({'gen':L.gen,'det':L.det,'classes':cl,'colors':col,'D':D},open('res_hex3.json','w'))
print("OK")
