from decimal import Decimal as D, getcontext
getcontext().prec=45
pts=[tuple(D(t) for t in l.split('\t')) for l in open('coeur4_sommets.tsv') if not l.startswith('#')]
E=[tuple(map(int,l.split())) for l in open('coeur4_aretes.tsv')]
print(f"{len(pts)} sommets, {len(E)} arêtes déclarées")
bad=[(i,j) for i,j in E if abs((pts[i][0]-pts[j][0])**2+(pts[i][1]-pts[j][1])**2-D(1))>D('1e-20')]
print("arêtes déclarées non de longueur 1 :",len(bad))
deg=[0]*len(pts)
for i,j in E: deg[i]+=1; deg[j]+=1
S=set(E)|set((j,i) for i,j in E); missing=[]
for i in range(len(pts)):
    for j in range(i+1,len(pts)):
        d2=(pts[i][0]-pts[j][0])**2+(pts[i][1]-pts[j][1])**2
        if abs(d2-D(1))<D('1e-20') and (i,j) not in S: missing.append((i,j))
print("arêtes unité manquantes :",len(missing))
print("degré min :",min(deg),"| degré max :",max(deg))
print("VERDICT :", "cœur 4 VALIDE" if min(deg)>=4 and not bad and not missing else "PROBLÈME")
