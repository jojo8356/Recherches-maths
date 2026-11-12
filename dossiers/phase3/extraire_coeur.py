exec(open('hp2.py').read().split('seed_tc=')[0])   # récupère closure, build, degeneracy, kcore
import json
seed=[(0,0),(1,0),(0.5,SQ3/2),(0.5,SQ3/6)]
P=closure(seed,1.5)
adj=build(P); d=degeneracy(adj)
core=sorted(kcore(adj,4))
print(f"graphe : {len(P)} sommets, {sum(len(s) for s in adj)//2} arêtes, DÉG={d}, 4-core = {len(core)} sommets")
idx={v:i for i,v in enumerate(core)}
E=[]
for v in core:
    for u in adj[v]:
        if u in idx and u>v: E.append((idx[v],idx[u]))
deg=[0]*len(core)
for i,j in E: deg[i]+=1; deg[j]+=1
print(f"cœur : {len(core)} sommets, {len(E)} arêtes, degré min={min(deg)}")
with open('coeur4_sommets.tsv','w') as f:
    f.write("# x\ty  (45 chiffres, tronqués à 25)\n")
    for v in core: f.write(f"{P[v][0]:.25f}\t{P[v][1]:.25f}\n")
with open('coeur4_aretes.tsv','w') as f:
    for i,j in E: f.write(f"{i}\t{j}\n")
print("écrit : coeur4_sommets.tsv, coeur4_aretes.tsv")
json.dump({'n_graph':len(P),'m_graph':sum(len(s) for s in adj)//2,'deg':d,
           'core_n':len(core),'core_m':len(E),'core_mindeg':min(deg)},open('res_coeur4.json','w'))
