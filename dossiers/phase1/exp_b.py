import json, math
# diamant = K4 moins l'arete (0,1) : 0,1 = pointes (distance sqrt3) ; 2,3 = milieux adjacents
adj=[[False]*4 for _ in range(4)]
for i in range(4):
    for j in range(i+1,4):
        if (i,j)!=(0,1): adj[i][j]=adj[j][i]=True
def count(k, cond=lambda c: True):
    tot=0; col=[-1]*4
    def rec(i):
        nonlocal tot
        if i==4:
            tot+= cond(col); return
        for c in range(k):
            if all(not adj[i][j] or col[j]!=c for j in range(i)):
                col[i]=c; rec(i+1); col[i]=-1
    rec(0); return tot
out={}
for k in (3,4):
    eq=count(k, lambda c: c[0]==c[1]); ne=count(k, lambda c: c[0]!=c[1])
    out[k]={'pointes_egales':eq,'pointes_differentes':ne}
    print(f"diamant, {k} couleurs : pointes egales={eq:3d}  pointes differentes={ne:3d}", "=> égalité FORCÉE" if ne==0 else "=> égalité NON forcée")
# accessoirement : χ du diamant
for k in (2,3):
    print(f"  χ(diamant) > {k} ?", count(k)==0)
json.dump(out,open('res_diamond.json','w'))
