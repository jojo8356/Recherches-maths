exec(open('treillis.py').read().split('# ----------families ----------')[0])
import itertools
def build(b1,b2,R,eps=1e-3):
    cell=voronoi(b1,b2); D=diam(cell); k=(1-eps)/D
    cell=[(k*x,k*y) for x,y in cell]; b1=(k*b1[0],k*b1[1]); b2=(k*b2[0],k*b2[1])
    P=[(i,j) for i in range(-R,R+1) for j in range(-R,R+1)]
    S={}
    for (i,j) in P:
        c=(i*b1[0]+j*b2[0], i*b1[1]+j*b2[1])
        S[(i,j)]=[(c[0]+x,c[1]+y) for x,y in cell]
    return P,S
def conflict(S,u,v):
    lo=dmin(S[u],S[v]); hi=dmax(S[u],S[v])
    return lo<1-1e-9 and hi>1+1e-9, lo, hi
for tag,b1,b2,R in (("carré",(1,0),(0,1),2),("hexagonal",(1,0),(0.5,math.sqrt(3)/2),3)):
    P,S=build(b1,b2,R)
    nonconf=[]
    for u,v in itertools.combinations(P,2):
        c,lo,hi=conflict(S,u,v)
        if not c: nonconf.append((u,v,round(lo,4),round(hi,4)))
    print(f"\n{tag} : bloc {len(P)} cellules ; paires NON en conflit : {len(nonconf)}")
    for x in nonconf[:8]: print("   ",x)
    # taille de la clique maximale dans le bloc (recherche exacte, blocs petits)
    n=len(P); adj=[[False]*n for _ in range(n)]
    for a in range(n):
        for b in range(a+1,n):
            c,_,_=conflict(S,P[a],P[b]); adj[a][b]=adj[b][a]=c
    best=0
    for size in range(1,n+1):
        found=False
        for comb in itertools.combinations(range(n),size):
            if all(adj[a][b] for a,b in itertools.combinations(comb,2)): found=True; break
        if found: best=size
        elif size>best+1: break
    print(f"   -> clique maximale EXACTE dans le bloc : {best} (sur {n} cellules)")
