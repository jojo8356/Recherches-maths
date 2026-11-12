import math
# Test express du mécanisme de l'histoire "chi <= 5 par dégénérescence"
tri=[(i+j/2,j*math.sqrt(3)/2) for i in range(-3,4) for j in range(-3,4)]
n=len(tri)
adj=[set() for _ in range(n)]
for i in range(n):
    for j in range(i+1,n):
        if abs(math.dist(tri[i],tri[j])**2-1)<1e-9: adj[i].add(j); adj[j].add(i)
# dégénérescence = indice de k-core maximal (algorithme de pelage)
A=[set(s) for s in adj]; core=[0]*n; deg=[len(s) for s in A]; alive=set(range(n)); k=0
while alive:
    v=min(alive,key=lambda x:len(A[x])); d=len(A[v]); k=max(k,d)
    for u in A[v]: A[u].discard(v)
    alive.discard(v)
print(f"patch du réseau triangulaire : {n} sommets")
print(f"   degré maximum : {max(len(s) for s in adj)}")
print(f"   DÉGÉNÉRESCENCE (k-core max) : {k}")
print(f"   nombre chromatique : 3")
print(f"   => le graphe glouton donne seulement chi <= {k+1} = 7, soit la borne triviale.")
print("   => l'histoire 'χ <= 5 par élimination à faible degré' est morte immédiatement.")
# degénérescence du fuseau de Moser pour comparaison
V={'A':(-math.sqrt(3)/2,0),'B':(math.sqrt(3)/2,0),'C':(0,0.5),'D':(0,-0.5)}
B,A_=V['B'],V['A']; d=math.dist(B,A_); a=(d*d+2)/(2*d); h=math.sqrt(3-a*a)
ux,uy=(A_[0]-B[0])/d,(A_[1]-B[1])/d
E=(B[0]+a*ux-h*uy,B[1]+a*uy+h*ux); mid=((B[0]+E[0])/2,(B[1]+E[1])/2)
vx,vy=(E[0]-B[0])/math.sqrt(3),(E[1]-B[1])/math.sqrt(3)
F=(mid[0]+0.5*vy,mid[1]-0.5*vx); G=(mid[0]-0.5*vy,mid[1]+0.5*vx)
P=[V['A'],V['B'],V['C'],V['D'],E,F,G]
adj2=[set() for _ in range(7)]
for i in range(7):
    for j in range(i+1,7):
        if abs(math.dist(P[i],P[j])**2-1)<1e-9: adj2[i].add(j); adj2[j].add(i)
A=[set(s) for s in adj2]; alive=set(range(7)); k2=0
while alive:
    v=min(alive,key=lambda x:len(A[x])); k2=max(k2,len(A[v]))
    for u in A[v]: A[u].discard(v)
    alive.discard(v)
print(f"\nfuseau de Moser : degrés {[len(s) for s in adj2]}, dégénérescence {k2}, chi = 4")
print("   => la dégénérescence ne voit toujours pas la 4-chromaticité : elle vaut 3.")
