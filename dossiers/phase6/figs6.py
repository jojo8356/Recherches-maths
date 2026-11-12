import math,sys,json; sys.path.insert(0,'.')
from partition2 import *
from experience import germes_hex
b1=(1,0); b2=(0.5,math.sqrt(3)/2)
# ---------- FIG 1 : omega vs desordre ----------
scan={0.0:[7,7,7],0.02:[7,7,7],0.05:[7,7,7],0.08:[7,7,7],0.10:[7,7,7],0.12:[7,7,7],0.15:[7,7,7],0.18:[8,8,8],0.20:[8,8,8],
      0.25:[9,9],0.30:[9,9],0.40:[11,11]}
ctrl_max=[(0.0,7),(0.10,7),(0.20,8),(0.30,9),(0.40,11)]
ctrl_moy=[(0.0,7),(0.10,7),(0.20,7),(0.30,8),(0.40,9)]
W,H=880,380; L,R,T,B=70,150,40,58
def X(t): return L+t/0.42*(W-L-R)
def Y(w): return H-B-(w-6)/(12-6)*(H-T-B)
sv=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="omega en fonction du desordre">',
    f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>']
for w in range(6,13):
    y=Y(w); sv.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="{"#c9c4b8" if w==7 else "#eae6dc"}" stroke-width="{1.4 if w==7 else 1}"/>')
    sv.append(f'<text x="{L-12}" y="{y+5:.1f}" text-anchor="end" font-family="Georgia,serif" font-size="14" fill="#5c5850">{w}</text>')
for t in (0,0.1,0.2,0.3,0.4):
    sv.append(f'<line x1="{X(t):.1f}" y1="{T}" x2="{X(t):.1f}" y2="{H-B}" stroke="#f0ece3"/>')
    sv.append(f'<text x="{X(t):.1f}" y="{H-B+22}" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#5c5850">{t:.1f}</text>')
# bande omega=7
sv.append(f'<rect x="{L}" y="{Y(7.5):.1f}" width="{W-L-R}" height="{Y(6.5)-Y(7.5):.1f}" fill="#1f6f4a" opacity="0.07"/>')
sv.append(f'<text x="{X(0.03):.1f}" y="{Y(6.62):.1f}" font-family="Georgia,serif" font-size="14" fill="#1f6f4a" font-style="italic">plancher 7 — jamais franchi par le bas</text>')
pts=" ".join(f"{X(t):.1f},{Y(sum(v)/len(v)):.1f}" for t,v in sorted(scan.items()))
sv.append(f'<polyline points="{pts}" fill="none" stroke="#8a4b2a" stroke-width="2.4"/>')
for t,v in sorted(scan.items()):
    c="#1f6f4a" if v[0]==7 else "#8a4b2a"
    sv.append(f'<circle cx="{X(t):.1f}" cy="{Y(sum(v)/len(v)):.1f}" r="4.8" fill="{c}"/>')
    if len(set(v))>1: sv.append(f'<text x="{X(t)+9:.1f}" y="{Y(v[0])-5:.1f}" font-family="Georgia,serif" font-size="10" fill="#8a4b2a">{v}</text>')
p2=" ".join(f"{X(t):.1f},{Y(w):.1f}" for t,w in ctrl_moy)
sv.append(f'<polyline points="{p2}" fill="none" stroke="#2b5fa8" stroke-width="1.8" stroke-dasharray="5 4"/>')
for t,w in ctrl_moy: sv.append(f'<circle cx="{X(t):.1f}" cy="{Y(w):.1f}" r="3.4" fill="none" stroke="#2b5fa8" stroke-width="1.8"/>')
# poisson
for i,(lab,w) in enumerate((("Poisson 300",9),("Poisson 420",11))):
    yy=Y(w); sv.append(f'<circle cx="{X(0.415):.1f}" cy="{yy:.1f}" r="4.4" fill="#5b4580"/>')
    sv.append(f'<text x="{X(0.40)+2:.1f}" y="{yy-9:.1f}" text-anchor="end" font-family="Georgia,serif" font-size="11.5" fill="#5b4580">{lab}</text>')
sv.append(f'<line x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}" stroke="#8b857a" stroke-width="1.6"/>')
sv.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H-B}" stroke="#8b857a" stroke-width="1.6"/>')
sv.append(f'<text x="{(L+W-R)/2:.0f}" y="{H-14}" text-anchor="middle" font-family="Georgia,serif" font-size="15" fill="#3d3a34">amplitude du désordre (déplacement des germes, en pas de réseau)</text>')
sv.append(f'<text x="20" y="{(T+H-B)/2:.0f}" transform="rotate(-90 20 {(T+H-B)/2:.0f})" text-anchor="middle" font-family="Georgia,serif" font-size="15" fill="#3d3a34">ω du graphe de conflit</text>')
sv.append(f'<text x="{X(0.30):.1f}" y="{T-14}" text-anchor="middle" font-family="Georgia,serif" font-size="12.5" fill="#2b5fa8" font-style="italic">tirets : normalisation par la moyenne (partition invalide, contrôle)</text>')
sv.append(f'<text x="{X(0.30):.1f}" y="{T+2}" text-anchor="middle" font-family="Georgia,serif" font-size="12.5" fill="#8a4b2a" font-style="italic">trait plein : normalisation par le diamètre maximal (partition valide)</text>')
sv.append('</svg>')
open('fig_desordre.svg','w').write("\n".join(sv))
print("fig_desordre.svg ok")

# ---------- FIG 2 : la partition desordonnee et sa 9-clique ----------
cells=voronoi_tore(germes_hex(14,1.0,0.30,1),(14*b1[0],14*b1[1]),(14*b2[0],14*b2[1]))
cells,k=normaliser(cells,1e-4); U1=(k*14*b1[0],k*14*b1[1]); U2=(k*14*b2[0],k*14*b2[1])
adj,_=graphe(cells,U1,U2); w,cl0=clique_max(adj); cl=sorted(cl0)
print('omega =',w,'clique de',len(cl))
# dessin : on garde les cellules dont le centre est dans une fenetre
cen=[(sum(p[0] for p in c)/len(c),sum(p[1] for p in c)/len(c)) for c in cells]
W2,H2=760,540; sc=52; ox,oy=W2/2,H2/2+10
def T(p): return (ox+(p[0]-cen[cl[0]][0])*sc, oy-(p[1]-cen[cl[0]][1])*sc)
sv=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W2} {H2}" width="100%" role="img" aria-label="partition desordonnee avec une clique de conflit">',
    f'<rect width="{W2}" height="{H2}" fill="#fbfaf7"/>']
for idx,c in enumerate(cells):
    P=[T(p) for p in c]
    if max(abs(p[0]-ox) for p in P)>W2 or max(abs(p[1]-oy) for p in P)>H2: continue
    inC=idx in cl
    d=" ".join(("M" if n==0 else "L")+f"{p[0]:.1f},{p[1]:.1f}" for n,p in enumerate(P))+"Z"
    sv.append(f'<path d="{d}" fill="{"#e8b48a" if inC else "#f2eee4"}" stroke="{"#8a3b2a" if inC else "#c9c3b4"}" stroke-width="{2.4 if inC else 0.8}"/>')
sv.append(f'<rect x="0" y="0" width="{W2}" height="44" fill="#fbfaf7"/><rect x="0" y="{H2-46}" width="{W2}" height="46" fill="#fbfaf7"/>')
sv.append(f'<text x="{W2/2}" y="24" text-anchor="middle" font-family="Georgia,serif" font-size="15.5" fill="#3d3a34">Un pavage sans aucune symétrie, et pourtant {len(cl)} cellules deux à deux incompatibles</text>')
sv.append(f'<text x="{W2/2}" y="{H2-26}" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#5c5850" font-style="italic">germes hexagonaux déplacés aléatoirement de 0,30 pas — la fleur survit, et se déforme en une clique plus grosse</text>')
sv.append('</svg>')
open('fig_partition.svg','w').write("\n".join(sv))
print("fig_partition.svg ok")
