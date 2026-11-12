"""La recherche de 6-coloriage, reellement lancee sur les 18 configurations trouees.

L'audit a montre que exp_trous.py ne l'executait jamais (garde omega <= 6). Ici on la lance
toujours, avec un budget de noeuds explicite, et on distingue les trois issues :
  "impossible" (recherche epuisee), "budget" (non conclu), "TROUVE".
"""
import sys, math, random, json
sys.path.insert(0, '.'); sys.path.insert(0, '../phase6')
from trous import *
from partition2 import voronoi_tore, k_color, clique_max

b1 = (1, 0); b2 = (0.5, math.sqrt(3) / 2)

def germes(m, jit, sd):
    rnd = random.Random(sd); out = []
    for i in range(m):
        for j in range(m):
            x = i * b1[0] + j * b2[0] + (b1[0] + b2[0]) / 3
            y = i * b1[1] + j * b2[1] + (b1[1] + b2[1]) / 3
            if jit:
                a = rnd.uniform(0, 2 * math.pi); r = jit * math.sqrt(rnd.uniform(0, 1))
                x += r * math.cos(a); y += r * math.sin(a)
            out.append((x, y))
    return out

def norm(cells, eps=1e-4):
    D = max(diam_cell(c) for c in cells); k = (1 - eps) / D
    return [[[(k * x, k * y) for x, y in P] for P in c] for c in cells], k

RES = []
m = 14
for jit in (0.0, 0.15):
    seeds = germes(m, jit, 1); U1 = (m * b1[0], m * b1[1]); U2 = (m * b2[0], m * b2[1])
    cells = construit(seeds, U1, U2, lambda i: False, 0.0); cells, k = norm(cells)
    adj, _ = graphe(cells, (k * U1[0], k * U1[1]), (k * U2[0], k * U2[1]), margin=0.01)
    w, cl = clique_max(adj); CL = set(cl)
    configs = [("reference, aucune cellule trouee", lambda i: False, 0.0)]
    for rho in (0.3, 0.5, 0.7):
        configs.append((f"toutes les cellules trouees, rho={rho}", lambda i: True, rho))
    for rho in (0.3, 0.5, 0.7):
        configs.append((f"clique seule trouee, rho={rho}", (lambda CL: lambda i: i in CL)(CL), rho))
    configs.append(("une classe de couleur sur 7, rho=0.5", lambda i: (i % m + 3 * (i // m)) % 7 == 0, 0.5))
    S = set(random.Random(5).sample(range(m * m), m * m // 2))
    configs.append(("moitie aleatoire, rho=0.5", (lambda S: lambda i: i in S)(S), 0.5))
    for (tag, choix, rho) in configs:
        cells = construit(seeds, U1, U2, choix, rho); cells, k = norm(cells)
        adj, _ = graphe(cells, (k * U1[0], k * U1[1]), (k * U2[0], k * U2[1]), margin=0.01)
        w, _ = clique_max(adj)
        r6, c6 = k_color(adj, 6, budget=200_000)
        issue = "TROUVE" if isinstance(r6, list) else ("impossible" if r6 is False else "budget")
        RES.append(dict(tag=tag, n=len(adj), omega=w, issue=issue))
        print(f"  {tag:40s} n={len(adj):3d} omega={w}  6 couleurs -> {issue}", flush=True)
json.dump(RES, open("res_trous_six.json", "w"), ensure_ascii=False)
print("issues :", {i: sum(1 for r in RES if r["issue"] == i) for i in ("TROUVE", "impossible", "budget")})
