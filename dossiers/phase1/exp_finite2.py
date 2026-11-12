import json
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
def sub(adj,n,d):
    keep=[v for v in range(n) if v!=d]; m=len(keep)
    return [[adj[keep[i]][keep[j]] for j in range(m)] for i in range(m)],m
found={}
for n in range(2,7):
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    for mask in range(1<<n*(n-1)//2):
        adj=[[False]*n for _ in range(n)]
        for b,(i,j) in enumerate(pairs):
            if (mask>>b)&1: adj[i][j]=adj[j][i]=True
        if chi(adj,n)!=4: continue
        if all(chi(*sub(adj,n,d))<=3 for d in range(n)):
            deg=tuple(sorted((sum(adj[i]) for i in range(n)),reverse=True))
            found[(n,deg)]=found.get((n,deg),0)+1
print("graphes 4-critiques à n<=6 sommets (n, degrés triés) -> nb d'étiquetages :")
for k,v in sorted(found.items()): print("   ",k,":",v)
print("\nSeuls K4 (n=4, degrés 3,3,3,3) et W5 = C5+moyeu (n=6, degrés 5,3,3,3,3) apparaissent.")
json.dump({str(k):v for k,v in found.items()},open('res_finite2.json','w'))
