import sys; sys.path.insert(0,'.')
from partition2 import *
# test 1 : K9 avec 6 couleurs -> doit etre Impossible
adj=[set(range(9))-{i} for i in range(9)]
print("K9, k=6 :", k_color(adj,6)[0], " (attendu False)")
print("K9, k=9 :", type(k_color(adj,9)[0]), " (attendu une liste)")
# test 2 : coloration valide ? verification directe
r,_=k_color(adj,6)
print("valeur brute :", repr(r)[:80])
# test 3 : sur un graphe reel, compter les aretes monochromes du coloriage rendu
P=12; seeds=[(i+0.5,j+0.5) for i in range(P) for j in range(P)]
cells=voronoi_tore(seeds,(P,0),(0,P)); cells,k=normaliser(cells,1e-4)
adj,_=graphe(cells,(k*P,0),(0,k*P))
r,_=k_color(adj,6)
print("carre, k=6 :", type(r), "| aretes monochromes =", sum(1 for i in range(len(adj)) for j in adj[i] if j>i and r[i]==r[j]) if isinstance(r,list) else "n/a")
