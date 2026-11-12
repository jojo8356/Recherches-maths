import math, json, itertools
def hexdist(dq,dr): return max(abs(dq),abs(dr),abs(dq+dr))
D=[(q,r) for q in range(-2,3) for r in range(-2,3) if 0<hexdist(q,r)<=2]   # ensemble des différences en conflit
assert len(D)==18

def quotient(a,b,c,d):
    det=abs(a*d-b*c)
    if det==0: return None
    # classes : (i,j) -> representant modulo le reseau engendre par (a,b),(c,d) ; on indexe par (i,j) dans [0,det)
    def key(p,q):
        # resoudre p = i*a + j*c , q = i*b + j*d  (mod rien) -> coordonnees dans la base, puis modulo det
        # coordonnees entieres dans la base du reseau (matrice [[a,c],[b,d]])
        inv=1.0/(a*d-b*c)
        i=( d*p - c*q)*inv; j=(-b*p + a*q)*inv
        if abs(i-round(i))>1e-9 or abs(j-round(j))>1e-9: return None
        return (round(i)%det, round(j)%det)
    cells=[(i,j) for i in range(det) for j in range(det)]
    idx={c:n for n,c in enumerate(cells)}
    # aretes : difference v in D, en coordonnees de la base
    ds=set()
    for (p,q) in D:
        k=key(p,q)
        if k: ds.add(k)
    nb=[0]*len(cells)
    for (i,j) in cells:
        u=idx[(i,j)]
        for (di,dj) in ds:
            v=idx[((i+di)%det,(j+dj)%det)]
            nb[u]|=1<<v
    return cells,nb,ds,(a,b,c,d)

def col7(nb,k=7):
    n=len(nb); col=None
    def rec(col):
        if all(c!=-1 for c in col): return col
        # sommet de saturation max
        best=None
        for v in range(n):
            if col[v]!=-1: continue
            used={col[u] for u in range(n) if col[u]!=-1 and (nb[v]>>u)&1}
            cand=[c for c in range(k) if c not in used]
            srt=(len(used), -len(cand))
            if best is None or srt>best[0]: best=(srt,v,cand)
        _,v,cand=best
        for c in cand:
            col[v]=c
            r=rec(col)
            if r: return r
            col[v]=-1
        return None
    return rec([-1]*n)

found=None
for det_target in range(7,43):
    for a in range(-6,7):
      for b in range(-6,7):
        for c in range(-6,7):
          for d in range(-6,7):
            if abs(a*d-b*c)!=det_target: continue
            Q=quotient(a,b,c,d)
            if not Q: continue
            cells,nb,ds,gen=Q
            r=col7(nb)
            if r is not None:
                found=(gen,det_target,cells,nb,ds,r); break
          if found: break
        if found: break
      if found: break
    if found: break
gen,m,cells,nb,ds,col=found
print(f"coloriage périodique trouvé : réseau engendré par {gen[:2]} et {gen[2:]} (indice m={m})")
print("vecteurs de conflit dans la base :", sorted(ds))
print("couleurs des m classes :", col)

# ---- vérification sur un grand patch : la couleur est-elle bien invariante par le réseau ? ----
a,b,c,d=gen
def color_of(q,r):
    inv=1.0/(a*d-b*c)
    i=( d*q - c*r)*inv; j=(-b*q + a*r)*inv
    assert abs(i-round(i))<1e-7 and abs(j-round(j))<1e-7, "point hors réseau"
    return col[(round(i)%m)*m + (round(j)%m)] if False else col[[k for k,x in enumerate(cells) if x==(round(i)%m,round(j)%m)][0]]
ok=True; checks=0
for q in range(-14,15):
    for r in range(-14,15):
        for (dq,dr) in D:
            checks+=1
            if color_of(q,r)==color_of(q+dq,r+dr): ok=False; print("VIOLATION",q,r,dq,dr)
print(f"vérification : {checks} contraintes de conflit testées sur le patch R=14 -> {'AUCUNE VIOLATION' if ok else 'ÉCHEC'}")

# couleurs distinctes sur la fleur ?
print("fleur :", sorted({color_of(*f) for f in [(0,0)]+[(q,r) for q in range(-1,2) for r in range(-1,2) if hexdist(q,r)==1]}))
json.dump({'gen':gen,'m':m,'col':col,'cells':cells,'D':D},open('res_hex2.json','w'))
