import itertools, math, json

# ---------- E1 : le fuseau de Moser, exhaustif ----------
V = {'A':(-math.sqrt(3)/2,0),'B':(math.sqrt(3)/2,0),'C':(0,0.5),'D':(0,-0.5)}
B,A = V['B'], V['A']
c1,c2,r1,r2 = B,A,math.sqrt(3),1.0
d=math.dist(c1,c2); a=(d*d+r1*r1-r2*r2)/(2*d); h=math.sqrt(r1*r1-a*a)
ux,uy=(c2[0]-c1[0])/d,(c2[1]-c1[1])/d
E=(c1[0]+a*ux-h*uy, c1[1]+a*uy+h*ux)
mid=((B[0]+E[0])/2,(B[1]+E[1])/2)
vx,vy=(E[0]-B[0])/math.sqrt(3),(E[1]-B[1])/math.sqrt(3)
F=(mid[0]+0.5*vy, mid[1]-0.5*vx); G=(mid[0]-0.5*vy, mid[1]+0.5*vx)
V.update({'E':E,'F':F,'G':G})
edges=[('A','C'),('A','D'),('B','C'),('B','D'),('C','D'),
       ('B','F'),('B','G'),('E','F'),('E','G'),('F','G'),('A','E')]
names=sorted(V); idx={n:i for i,n in enumerate(names)}
adj=[[False]*7 for _ in range(7)]
for u,v in edges:
    adj[idx[u]][idx[v]]=adj[idx[v]][idx[u]]=True
assert all(abs(math.dist(V[u],V[v])-1)<1e-9 for u,v in edges), "arêtes non unité"

def count_proper(k):
    n=7; tot=0; chrom=[]
    col=[-1]*n
    def rec(i):
        nonlocal tot
        if i==n:
            tot+=1; return
        for c in range(k):
            if all(not adj[i][j] or col[j]!=c for j in range(i)):
                col[i]=c; rec(i+1); col[i]=-1
    rec(0); return tot

res_e1={k:count_proper(k) for k in (2,3,4,5)}
print("E1 fuseau de Moser — coloriages propres, couleurs étiquetées :", res_e1)
print("   -> χ =", min(k for k,v in res_e1.items() if v>0),
      "| 3-coloriable ?", res_e1[3]>0)

# ---------- E2 : ce que force un diamant ----------
D_edges=[(0,1),(0,2),(1,2),(0,3),(1,3)]   # 0,1 = pointes ; 2,3 = milieux ; K4 moins arete 2-3
def count_diamond(k, force_equal=None):
    tot=0; col=[-1]*4
    def rec(i):
        nonlocal tot
        if i==4:
            if force_equal is None or (col[0]==col[1])==force_equal: tot+=1
            return
        for c in range(k):
            if all(not (i in e and j in e) or col[j]!=c for e in D_edges for j in e if j<i):
                col[i]=c; rec(i+1); col[i]=-1
    rec(0); return tot
d3_eq=count_diamond(3,True); d3_ne=count_diamond(3,False)
d4_eq=count_diamond(4,True); d4_ne=count_diamond(4,False)
print(f"E2 diamant, 3 couleurs : pointes egales={d3_eq}, pointes differentes={d3_ne}  -> égalité FORCÉE")
print(f"   diamant, 4 couleurs : pointes egales={d4_eq}, pointes differentes={d4_ne}  -> plus forcée")
json.dump({'e1':res_e1,'diamond':{'d3_eq':d3_eq,'d3_ne':d3_ne,'d4_eq':d4_eq,'d4_ne':d4_ne}},open('res_ab.json','w'))
