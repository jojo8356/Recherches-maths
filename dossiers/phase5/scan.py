exec(open('treillis.py').read().split('# ----------families ----------')[0])
import json
def omega(b1,b2,R=3,eps=1e-3,margin=0.0):
    cell=voronoi(b1,b2); D=diam(cell); k=(1-eps)/D
    cell=[(k*x,k*y) for x,y in cell]; b1=(k*b1[0],k*b1[1]); b2=(k*b2[0],k*b2[1])
    P=[(i,j) for i in range(-R,R+1) for j in range(-R,R+1)]
    S=[]
    for (i,j) in P:
        c=(i*b1[0]+j*b2[0], i*b1[1]+j*b2[1]); S.append([(c[0]+x,c[1]+y) for x,y in cell])
    n=len(P); adj=[set() for _ in range(n)]
    for a in range(n):
        for b in range(a+1,n):
            lo=dmin(S[a],S[b]); hi=dmax(S[a],S[b])
            if lo<1-margin and hi>1+margin: adj[a].add(b); adj[b].add(a)
    best=[0]
    def bk(Rr,Pp,Xx):
        if not Pp and not Xx:
            best[0]=max(best[0],len(Rr)); return
        u=max(Pp|Xx,key=lambda v:len(adj[v]&Pp)) if (Pp|Xx) else None
        for v in list(Pp-adj[u]):
            bk(Rr|{v},Pp&adj[v],Xx&adj[v]); Pp.discard(v); Xx.add(v)
    bk(set(),set(range(n)),set())
    return best[0], len(cell), max(len(s) for s in adj)

print("A. réseau rhombique, |b1|=|b2|=1, angle θ (cellules = hexagones)  [R=4]")
rowsA=[]
for th in range(30,155,5):
    b1=(1,0); b2=(math.cos(math.radians(th)),math.sin(math.radians(th)))
    w,nv,dg=omega(b1,b2,R=4)
    rowsA.append((th,w)); print(f"   θ={th:3d}°   ω={w:2d}   (cellule à {nv} sommets, degré max {dg})")
print("\nB. réseau rectangulaire, aspect ρ  [R=3]")
rowsB=[]
for rho in [1.0,1.1,1.2,1.3,1.5,1.75,2.0,2.5,3.0]:
    w,nv,dg=omega((1,0),(0,1/rho),R=3)
    rowsB.append((rho,w)); print(f"   ρ={rho:4.2f}   ω={w:2d}")
print("\nC. robustesse en ε (marge 0) et en marge de sécurité, cas rhombique 60° et carré")
for tag,b1,b2 in (("hex 60°",(1,0),(0.5,math.sqrt(3)/2)),("carré",(1,0),(0,1)),("rhomb 40°",(1,0),(math.cos(math.radians(40)),math.sin(math.radians(40))))):
    out=[]
    for eps in (1e-2,1e-3,1e-4,1e-5):
        for margin in (0.0,0.01):
            out.append(f"ε={eps:g},m={margin:g}:ω={omega(b1,b2,R=3,eps=eps,margin=margin)[0]}")
    print(f"   {tag:10s} "+" | ".join(out))
json.dump({"rhombique":rowsA,"rectangulaire":rowsB},open('res_scan.json','w'))
print("\nMINIMUM global : ω =", min([w for _,w in rowsA]+[w for _,w in rowsB]))
