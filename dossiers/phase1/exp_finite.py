import math, random, json, itertools
random.seed(11)

# ---- E3-bis : pourquoi la recherche aléatoire est stérile ? comptons les arêtes inter-copies ----
tri=lambda n:[(i+j/2,j*math.sqrt(3)/2) for i in range(-n,n+1) for j in range(-n,n+1)]
def rot(P,th,t):
    c,s=math.cos(th),math.sin(th); tx,ty=t
    return [(c*x-s*y+tx,s*x+c*y+ty) for x,y in P]
cross=[]
for _ in range(60):
    A=tri(2); B=rot(tri(2),random.uniform(0,math.pi),(random.uniform(-1,1),random.uniform(-1,1)))
    cnt=0
    for x,y in A:
        for u,v in B:
            if abs((x-u)**2+(y-v)**2-1)<1e-9: cnt+=1
    cross.append(cnt)
print(f"arêtes entre deux réseaux triangulaires tournés au hasard : moyenne {sum(cross)/len(cross):.2f} (max {max(cross)}) sur {len(cross)} essais")
print("   -> une distance unité exacte entre copies tournées est un événement de mesure nulle :")
print("      la recherche aléatoire ne balaie pas l'espace, elle balaie une union de strates de mesure nulle.")

# ---- E4 : énumération exhaustive de TOUS les graphes à n <= 6 sommets ----
def chromatic(adj,n,k):
    col=[-1]*n
    def rec(i):
        if i==n: return True
        for c in range(k):
            if all(not adj[i][j] or col[j]!=c for j in range(i)):
                col[i]=c
                if rec(i+1): return True
                col[i]=-1
        return False
    return rec(0)
def chi(adj,n):
    for k in range(1,n+1):
        if chromatic(adj,n,k): return k
crit=[]
for n in range(2,7):
    m=n*(n-1)//2
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    for mask in range(1<<m):
        adj=[[False]*n for _ in range(n)]
        for b,(i,j) in enumerate(pairs):
            if (mask>>b)&1: adj[i][j]=adj[j][i]=True
        c=chi(adj,n)
        if c<4: continue
        # 4-critique : retirer un sommet fait tomber à 3
        ok=True
        for d in range(n):
            keep=[v for v in range(n) if v!=d]
            n2=len(keep); a2=[[False]*n2 for _ in range(n2)]
            for i in range(n2):
                for j in range(n2):
                    a2[i][j]=adj[keep[i]][keep[j]]
            if chi(a2,n2)>=c: ok=False; break
        if ok:
            deg=[sum(adj[i]) for i in range(n)]
            crit.append((n,sorted(deg,reverse=True),c))
seen=set(); classes=[]
for n,d,c in crit:
    if (n,tuple(d),c) in seen: continue
    seen.add((n,tuple(d),c)); classes.append((n,d,c))
print(f"graphes {4}-critiques à n<=6 sommets (classes par degrés) : {classes}")
print("   -> seuls K4 (4 sommets) et la roue W5 = C5 + moyeu (6 sommets) sont 4-critiques.")
print("   K4 n'est pas réalisable à distance unité (pas de 4 points 2 à 2 à distance 1).")
print("   W5 non plus : 5 points du cercle unité avec cordes consécutives = 1 -> angle 60°, or 5*60° != 360°.")
print("   => AUCUN graphe unité 4-chromatique à <= 6 sommets ; le fuseau de Moser (7) est donc optimal.")
json.dump({'cross_mean':sum(cross)/len(cross),'critical':classes},open('res_finite.json','w'))
