exec(open('haute_precision.py').read().split('seed_tc=')[0])
import json
seed=[(0,0),(1,0),(0.5,SQ3/2),(0.5,SQ3/6)]
P=closed(seed,1.5)
adj=graph(P); d=degeneracy(adj)
core=sorted(kcore(adj,4))
print(f"graphe : {len(P)} sommets, {sum(len(s) for s in adj)//2} arêtes, DÉG={d}, 4-core={len(core)}")
idx={v:i for i,v in enumerate(core)}; E=[]
for v in core:
    for u in adj[v]:
        if u in idx and u>v: E.append((idx[v],idx[u]))
deg=[0]*len(core)
for i,j in E: deg[i]+=1; deg[j]+=1
print(f"cœur : {len(core)} sommets, {len(E)} arêtes, degré min={min(deg)} max={max(deg)}")
open('coeur4_sommets.tsv','w').write("# x\ty\n"+"\n".join(f"{P[v][0]:.25f}\t{P[v][1]:.25f}" for v in core)+"\n")
open('coeur4_aretes.tsv','w').write("\n".join(f"{i}\t{j}" for i,j in E)+"\n")
json.dump({'n_graph':len(P),'m_graph':sum(len(s) for s in adj)//2,'deg':d,'core_n':len(core),
           'core_m':len(E),'core_mindeg':min(deg),'core_maxdeg':max(deg)},open('res_coeur4.json','w'))
print("fichiers écrits")
