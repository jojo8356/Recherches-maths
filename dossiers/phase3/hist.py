exec(open('haute_precision.py').read().split('seed_tc=')[0])
import json, collections
seed=[(0,0),(1,0),(0.5,SQ3/2),(0.5,SQ3/6)]
P=closed(seed,1.5); adj=graph(P); d=degeneracy(adj)
core=sorted(kcore(adj,4)); idx={v:i for i,v in enumerate(core)}
adjc=[set() for _ in core]
for v in core:
    for u in adj[v]:
        if u in idx: adjc[idx[v]].add(idx[u])
degs=[len(s) for s in adjc]
h=dict(sorted(collections.Counter(degs).items()))
print(f"cœur 97 sommets, degrés min={min(degs)} max={max(degs)}, histogramme={h}")
json.dump({'hist':{str(k):v for k,v in h.items()},'min':min(degs),'max':max(degs),
           'n':len(core),'m':sum(degs)//2},open('res_hist.json','w'))
