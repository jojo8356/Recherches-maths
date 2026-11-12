import math,sys; sys.path.insert(0,'.')
from courbes import pavage_courbe5, aire, diam
from partition2 import normaliser
b1=(1,0); b2=(0.5,math.sqrt(3)/2); m=14
# ---------- FIG 1 : omega vs courbure ----------
L=1/math.sqrt(3)
def sag(R): return 0 if R is None else R-math.sqrt(R*R-L*L/4)
Rs=[None,3.0,1.5,1.0,0.7,0.45,0.35]
serie={0.00:[7,7,7,7,7,7,7],0.15:[7,7,7,7,7,8,10],0.30:[9,9,9,9,9,11,10]}
W,H=860,380; MARG_L,MARG_R,T,B=74,150,44,62
def X(s): return MARG_L+s/0.17*(W-MARG_L-MARG_R)
def Y(w): return H-B-(w-6)/(12-6)*(H-T-B)
COL={0.00:"#1f6f4a",0.15:"#8a4b2a",0.30:"#5b4580"}
sv=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="omega en fonction de la courbure des bords">',
    f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>']
for w in range(6,13):
    sv.append(f'<line x1="{MARG_L}" y1="{Y(w):.1f}" x2="{W-MARG_R}" y2="{Y(w):.1f}" stroke="{"#c4bfb2" if w==7 else "#eae6dc"}" stroke-width="{1.5 if w==7 else 1}"/>')
    sv.append(f'<text x="{MARG_L-12}" y="{Y(w)+5:.1f}" text-anchor="end" font-family="Georgia,serif" font-size="14" fill="#5c5850">{w}</text>')
for s in (0,0.05,0.10,0.15):
    sv.append(f'<line x1="{X(s):.1f}" y1="{T}" x2="{X(s):.1f}" y2="{H-B}" stroke="#f0ece3"/>')
    sv.append(f'<text x="{X(s):.1f}" y="{H-B+22}" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#5c5850">{s:.2f}</text>')
sv.append(f'<rect x="{MARG_L}" y="{Y(7.5):.1f}" width="{W-MARG_L-MARG_R}" height="{Y(6.5)-Y(7.5):.1f}" fill="#1f6f4a" opacity="0.07"/>')
for jit,vals in serie.items():
    pts=" ".join(f"{X(sag(R)):.1f},{Y(v):.1f}" for R,v in zip(Rs,vals))
    sv.append(f'<polyline points="{pts}" fill="none" stroke="{COL[jit]}" stroke-width="2.4"/>')
    for R,v in zip(Rs,vals):
        sv.append(f'<circle cx="{X(sag(R)):.1f}" cy="{Y(v):.1f}" r="4.8" fill="{COL[jit]}"/>')

bx,by=MARG_L+16,T+52
sv.append(f'<rect x="{bx-10}" y="{by-46}" width="196" height="62" rx="7" fill="#fbfaf7" stroke="#e3ded4"/>')
for n,(jit,vals) in enumerate(serie.items()):
    yy=by-30+18*n
    sv.append(f'<circle cx="{bx+6}" cy="{yy}" r="4.6" fill="{COL[jit]}"/>')
    lab="bords droits" if jit==0 else f"désordre {jit:.2f}"
    sv.append(f'<text x="{bx+20}" y="{yy+4.5}" font-family="Georgia,serif" font-size="12.5" fill="#3d3a34">{lab}</text>')
sv.append(f'<line x1="{MARG_L}" y1="{H-B}" x2="{W-MARG_R}" y2="{H-B}" stroke="#8b857a" stroke-width="1.6"/>')
sv.append(f'<line x1="{MARG_L}" y1="{T}" x2="{MARG_L}" y2="{H-B}" stroke="#8b857a" stroke-width="1.6"/>')
sv.append(f'<text x="{(MARG_L+W-MARG_R)/2:.0f}" y="{H-16}" text-anchor="middle" font-family="Georgia,serif" font-size="15" fill="#3d3a34">courbure : flèche de l\'arc (0 = bord droit)</text>')
sv.append(f'<text x="24" y="{(T+H-B)/2:.0f}" transform="rotate(-90 24 {(T+H-B)/2:.0f})" text-anchor="middle" font-family="Georgia,serif" font-size="15" fill="#3d3a34">ω du graphe de conflit</text>')

# repere R=1, dessine en dernier
xr=X(sag(1.0))
sv.append(f'<line x1="{xr:.1f}" y1="{T}" x2="{xr:.1f}" y2="{H-B}" stroke="#b34a3c" stroke-width="1.3" stroke-dasharray="4 4"/>')
sv.append(f'<text x="{xr+8:.1f}" y="{Y(11.55):.1f}" font-family="Georgia,serif" font-size="12.5" fill="#b34a3c" font-style="italic">R = 1 (hypothèse du preprint)</text>')
sv.append('</svg>')
open('fig_courbure.svg','w').write("\n".join(sv)); print("fig_courbure ok")

# ---------- FIG 2 : le pavage a bords courbes ----------
seeds=[(i*b1[0]+j*b2[0]+(b1[0]+b2[0])/3, i*b1[1]+j*b2[1]+(b1[1]+b2[1])/3) for i in range(m) for j in range(m)]
U1=(m*b1[0],m*b1[1]); U2=(m*b2[0],m*b2[1])
cells=pavage_courbe5(seeds,U1,U2,1.0,M=6)
cells,k=normaliser(cells,1e-4)
cen=[(sum(p[0] for p in c)/len(c),sum(p[1] for p in c)/len(c)) for c in cells]
# fenetre autour du germe le plus central
mx=sum(q[0] for q in cen)/len(cen); my=sum(q[1] for q in cen)/len(cen)
cx0,cy0=sorted(cen,key=lambda q:math.hypot(q[0]-mx, q[1]-my))[0]
W2,H2=720,520; sc=66; ox,oy=W2/2,H2/2+6
def T(p): return (ox+(p[0]-cx0)*sc, oy-(p[1]-cy0)*sc)
sv=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W2} {H2}" width="100%" role="img" aria-label="pavage hexagonal a bords courbes, arcs de rayon 1">',
    f'<rect width="{W2}" height="{H2}" fill="#fbfaf7"/>']
pal=["#e8f0ea","#f6e7d7","#e2e7f2","#f3e2e8","#e6f1f4","#efe9d8","#e9e3f2"]
for idx,c in enumerate(cells):
    P=[T(p) for p in c]
    if max(abs(p[0]-ox) for p in P)>W2*0.75 or max(abs(p[1]-oy) for p in P)>H2*0.75: continue
    d=" ".join(("M" if n==0 else "L")+f"{p[0]:.1f},{p[1]:.1f}" for n,p in enumerate(P))+"Z"
    trois=["#eee8da","#e2e9ef","#f2e6e2"]
    sv.append(f'<path d="{d}" fill="{trois[idx%3]}" stroke="#7d7663" stroke-width="1.4"/>')
sv.append(f'<rect x="0" y="0" width="{W2}" height="46" fill="#fbfaf7"/><rect x="0" y="{H2-52}" width="{W2}" height="52" fill="#fbfaf7"/>')
sv.append(f'<text x="{W2/2}" y="26" text-anchor="middle" font-family="Georgia,serif" font-size="15.5" fill="#3d3a34">Un pavage à bords courbes — chaque bord est un arc de rayon exactement 1</text>')
sv.append(f'<text x="{W2/2}" y="{H2-32}" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#5c5850" font-style="italic">c’est l’hypothèse que le preprint interdit ; ici elle est satisfaite, et ω vaut toujours 7</text>')
sv.append(f'<text x="{W2/2}" y="{H2-14}" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#5c5850" font-style="italic">la partition est exacte : aire des cellules = aire du tore à 10⁻¹³ près</text>')
sv.append('</svg>')
open('fig_arcs.svg','w').write("\n".join(sv)); print("fig_arcs ok")
