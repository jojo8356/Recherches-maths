import math,sys; sys.path.insert(0,'.')
from partition2 import *
from experience import germes_hex
b1=(1,0); b2=(0.5,math.sqrt(3)/2)

# ================= FIG 1 =================
scan={0.0:7,0.02:7,0.05:7,0.08:7,0.10:7,0.12:7,0.15:7,0.18:8,0.20:8,0.25:9,0.30:9,0.40:11}
ctrl=[(0.0,7),(0.10,7),(0.20,7),(0.30,8),(0.40,9)]
W,H=880,400; L,R,T,B=72,40,58,60
def X(t): return L+t/0.42*(W-L-R)
def Y(w): return H-B-(w-6)/(12-6)*(H-T-B)
sv=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="omega en fonction du desordre">',
    f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>']
for w in range(6,13):
    sv.append(f'<line x1="{L}" y1="{Y(w):.1f}" x2="{W-R}" y2="{Y(w):.1f}" stroke="{"#c4bfb2" if w==7 else "#eae6dc"}" stroke-width="{1.5 if w==7 else 1}"/>')
    sv.append(f'<text x="{L-12}" y="{Y(w)+5:.1f}" text-anchor="end" font-family="Georgia,serif" font-size="14" fill="#5c5850">{w}</text>')
for t in (0,0.1,0.2,0.3,0.4):
    sv.append(f'<line x1="{X(t):.1f}" y1="{T}" x2="{X(t):.1f}" y2="{H-B}" stroke="#f0ece3"/>')
    sv.append(f'<text x="{X(t):.1f}" y="{H-B+22}" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#5c5850">{("%.1f"%t) if t>0 else "0"}</text>')
sv.append(f'<rect x="{L}" y="{Y(7.5):.1f}" width="{W-L-R}" height="{Y(6.5)-Y(7.5):.1f}" fill="#1f6f4a" opacity="0.07"/>')
sv.append(f'<text x="{W-R-8}" y="{Y(6.72):.1f}" text-anchor="end" font-family="Georgia,serif" font-size="12.5" fill="#1f6f4a" font-style="italic">plancher : 7</text>')
# serie valide
pts=" ".join(f"{X(t):.1f},{Y(w):.1f}" for t,w in sorted(scan.items()))
sv.append(f'<polyline points="{pts}" fill="none" stroke="#8a4b2a" stroke-width="2.5"/>')
for t,w in sorted(scan.items()): sv.append(f'<circle cx="{X(t):.1f}" cy="{Y(w):.1f}" r="5" fill="#8a4b2a"/>')
# controle, dessine en dernier (tirets + cercles vides) pour ne jamais etre masque
p2=" ".join(f"{X(t):.1f},{Y(w):.1f}" for t,w in ctrl)
sv.append(f'<polyline points="{p2}" fill="none" stroke="#2b5fa8" stroke-width="1.8" stroke-dasharray="6 4"/>')
for t,w in ctrl: sv.append(f'<circle cx="{X(t):.1f}" cy="{Y(w):.1f}" r="5.6" fill="none" stroke="#2b5fa8" stroke-width="1.8"/>')
# legende
lx,ly=L+18,T+10
sv.append(f'<rect x="{lx-8}" y="{ly-14}" width="392" height="52" rx="7" fill="#fbfaf7" stroke="#e3ded4"/>')
sv.append(f'<circle cx="{lx+10}" cy="{ly-1}" r="4.6" fill="#8a4b2a"/>')
sv.append(f'<text x="{lx+24}" y="{ly+4}" font-family="Georgia,serif" font-size="12.5" fill="#3d3a34">normalisation par le diamètre max (partition valide)</text>')
sv.append(f'<circle cx="{lx+10}" cy="{ly+21}" r="5.4" fill="none" stroke="#2b5fa8" stroke-width="1.8"/>')
sv.append(f'<text x="{lx+24}" y="{ly+26}" font-family="Georgia,serif" font-size="12.5" fill="#3d3a34">normalisation par la moyenne (contrôle, partition invalide)</text>')
# poisson, en encart
sv.append(f'<rect x="{W-R-196}" y="{Y(12)-6}" width="186" height="46" rx="7" fill="#f4f0f7" stroke="#ddd4e6"/>')
sv.append(f'<text x="{W-R-106}" y="{Y(12)+12}" text-anchor="middle" font-family="Georgia,serif" font-size="12.5" fill="#5b4580">germes de Poisson :</text>')
sv.append(f'<text x="{W-R-106}" y="{Y(12)+30}" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#5b4580">ω = 9, 11, 11, 11</text>')
sv.append(f'<line x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}" stroke="#8b857a" stroke-width="1.6"/>')
sv.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H-B}" stroke="#8b857a" stroke-width="1.6"/>')
sv.append(f'<text x="{(L+W-R)/2:.0f}" y="{H-16}" text-anchor="middle" font-family="Georgia,serif" font-size="15" fill="#3d3a34">amplitude du désordre (déplacement aléatoire des germes, en pas de réseau)</text>')
sv.append(f'<text x="22" y="{(T+H-B)/2:.0f}" transform="rotate(-90 22 {(T+H-B)/2:.0f})" text-anchor="middle" font-family="Georgia,serif" font-size="15" fill="#3d3a34">ω du graphe de conflit</text>')
sv.append('</svg>')
open('fig_desordre.svg','w').write("\n".join(sv)); print("fig1 ok")

# ================= FIG 2 : zoom sur la clique =================
cells=voronoi_tore(germes_hex(14,1.0,0.30,1),(14*b1[0],14*b1[1]),(14*b2[0],14*b2[1]))
cells,k=normaliser(cells,1e-4); U1=(k*14*b1[0],k*14*b1[1]); U2=(k*14*b2[0],k*14*b2[1])
adj,_=graphe(cells,U1,U2); w,cl0=clique_max(adj); cl=sorted(cl0)
cen=[(sum(p[0] for p in c)/len(c),sum(p[1] for p in c)/len(c)) for c in cells]
cx0=sum(cen[i][0] for i in cl)/len(cl); cy0=sum(cen[i][1] for i in cl)/len(cl)
rad=max(math.hypot(cen[i][0]-cx0,cen[i][1]-cy0) for i in cl)+1.35
W2,H2=720,560; sc=(min(W2-40,H2-110))/(2*rad); ox,oy=W2/2,H2/2+12
def T(p): return (ox+(p[0]-cx0)*sc, oy-(p[1]-cy0)*sc)
sv=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W2} {H2}" width="100%" role="img" aria-label="neuf cellules deux a deux incompatibles dans un pavage desordonne">',
    f'<rect width="{W2}" height="{H2}" fill="#fbfaf7"/>']
ordre=[i for i in range(len(cells)) if math.hypot(cen[i][0]-cx0,cen[i][1]-cy0)<rad*1.9]
for idx in [i for i in ordre if i not in cl]+[i for i in ordre if i in cl]:
    P=[T(p) for p in cells[idx]]
    d=" ".join(("M" if n==0 else "L")+f"{p[0]:.1f},{p[1]:.1f}" for n,p in enumerate(P))+"Z"
    if idx in cl:
        sv.append(f'<path d="{d}" fill="#e5ae82" stroke="#8a3b2a" stroke-width="2.6"/>')
    else:
        sv.append(f'<path d="{d}" fill="{"#f3efe6" if idx%2 else "#eee9dd"}" stroke="#c9c3b4" stroke-width="0.9"/>')
for n,idx in enumerate(cl):
    p=T(cen[idx]); sv.append(f'<text x="{p[0]:.1f}" y="{p[1]+6:.1f}" text-anchor="middle" font-family="Georgia,serif" font-size="17" font-weight="700" fill="#6d2a1c">{n+1}</text>')
sv.append(f'<rect x="0" y="0" width="{W2}" height="46" fill="#fbfaf7"/><rect x="0" y="{H2-52}" width="{W2}" height="52" fill="#fbfaf7"/>')
sv.append(f'<text x="{W2/2}" y="25" text-anchor="middle" font-family="Georgia,serif" font-size="15.5" fill="#3d3a34">Neuf cellules deux à deux incompatibles, dans un pavage sans aucune symétrie</text>')
sv.append(f'<text x="{W2/2}" y="{H2-32}" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#5c5850" font-style="italic">germes hexagonaux déplacés de 0,30 pas : la fleur de 7 se déforme en une clique de 9</text>')
sv.append(f'<text x="{W2/2}" y="{H2-14}" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#5c5850" font-style="italic">tout coloriage de ce pavage exige donc au moins 9 couleurs</text>')
sv.append('</svg>')
open('fig_partition.svg','w').write("\n".join(sv)); print("fig2 ok | omega =",w)
