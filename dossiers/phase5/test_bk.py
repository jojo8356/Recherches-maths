import itertools
def bk_clique(n, adj):
    best=[0,None]
    def bk(Rr,Pp,Xx):
        if not Pp and not Xx:
            if len(Rr)>best[0]: best[0]=len(Rr); best[1]=set(Rr)
            return
        u=max(Pp|Xx, key=lambda v:len(adj[v]&Pp)) if (Pp|Xx) else None
        for v in list(Pp-adj[u]):
            bk(Rr|{v}, Pp&adj[v], Xx&adj[v]); Pp.discard(v); Xx.add(v)
    bk(set(),set(range(n)),set())
    return best[0],best[1]
# test 1 : graphe complet K_25
n=25; adj=[set(range(n))-{i} for i in range(n)]
print("K_25 ->", bk_clique(n,adj)[0], "(attendu 25)")
# test 2 : K_25 privé d'une arête
adj2=[set(a) for a in adj]; adj2[0].discard(1); adj2[1].discard(0)
print("K_25 - 1 arête ->", bk_clique(n,adj2)[0], "(attendu 24)")
