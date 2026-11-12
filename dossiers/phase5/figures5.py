exec(open('treillis.py').read().split('# ----------families ----------')[0])
import json
# ---------- FIG 1 : ω(θ) ----------
data={30:8,35:7,40:7,45:7,50:7,55:7,60:7,65:7,70:7,75:7,80:8,85:8,90:9,95:8,100:8,105:7,110:7,115:7,120:7,125:7,130:7,135:7,140:7,145:7,150:8}
W,H=860,360; L,Rp,T,B=64,24,34,54
def X(t): return L+(t-25)/(155-25)*(W-L-Rp)
def Y(w): return H-B-(w-6)/(10-6)*(H-T-B)
sv=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="clique de conflit en fonction de l angle du reseau rhombique">']
sv.append(f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>')
for w in range(6,11):
    y=Y(w); sv.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-Rp}" y2="{y:.1f}" stroke="{"#c9c4b8" if w%2 else "#e3dfd6"}" stroke-width="{1.2 if w==7 else 1}"/>')
    sv.append(f'<text x="{L-10}" y="{y+5:.1f}" text-anchor="end" font-family="Georgia,serif" font-size="14" fill="#5c5850">{w}</text>')
for t in range(30,155,15):
    sv.append(f'<line x1="{X(t):.1f}" y1="{T}" x2="{X(t):.1f}" y2="{H-B}" stroke="#efebe2"/>')
    sv.append(f'<text x="{X(t):.1f}" y="{H-B+22}" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#5c5850">{t}°</text>')
# bande du plateau 7
sv.append(f'<rect x="{X(35):.1f}" y="{Y(7.5):.1f}" width="{X(75)-X(35):.1f}" height="{Y(6.5)-Y(7.5):.1f}" fill="#1f6f4a" opacity="0.09"/>')
sv.append(f'<rect x="{X(105):.1f}" y="{Y(7.5):.1f}" width="{X(145)-X(105):.1f}" height="{Y(6.5)-Y(7.5):.1f}" fill="#1f6f4a" opacity="0.09"/>')
sv.append(f'<text x="{X(55):.1f}" y="{Y(6.55):.1f}" text-anchor="middle" font-family="Georgia,serif" font-size="14" fill="#1f6f4a" font-style="italic">ω = 7 (plancher)</text>')
pts=" ".join(f"{X(t):.1f},{Y(w):.1f}" for t,w in sorted(data.items()))
sv.append(f'<polyline points="{pts}" fill="none" stroke="#8a4b2a" stroke-width="2.4" stroke-linejoin="round"/>')
for t,w in sorted(data.items()):
    c="#1f6f4a" if w==7 else "#8a4b2a"
    sv.append(f'<circle cx="{X(t):.1f}" cy="{Y(w):.1f}" r="4.6" fill="{c}"/>')
sv.append(f'<line x1="{L}" y1="{H-B}" x2="{W-Rp}" y2="{H-B}" stroke="#8b857a" stroke-width="1.6"/>')
sv.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H-B}" stroke="#8b857a" stroke-width="1.6"/>')
sv.append(f'<text x="{(L+W-Rp)/2:.0f}" y="{H-12}" text-anchor="middle" font-family="Georgia,serif" font-size="15" fill="#3d3a34">angle θ du réseau rhombique (degré)</text>')
sv.append(f'<text x="18" y="{(T+H-B)/2:.0f}" transform="rotate(-90 18 {(T+H-B)/2:.0f})" text-anchor="middle" font-family="Georgia,serif" font-size="15" fill="#3d3a34">ω du graphe de conflit</text>')
sv.append(f'<text x="{X(90):.1f}" y="{Y(9)-12:.1f}" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#8a4b2a">carré</text>')
sv.append('</svg>')
open('fig_omega.svg','w').write("\n".join(sv))
print("fig_omega.svg", len("\n".join(sv)))

# ---------- FIG 2 : la fleur, 7-clique ----------
s3=math.sqrt(3); b1=(1,0); b2=(0.5,s3/2)
cell=voronoi(b1,b2); k=0.98/diam(cell)
cell=[(k*x,k*y) for x,y in cell]; B1=(k*b1[0],k*b1[1]); B2=(k*b2[0],k*b2[1])
COL=["#e8f0ea","#f6e7d7","#e2e7f2","#f3e2e8","#e6f1f4","#efe9d8","#e9e3f2"]
def hexa(i,j):
    c=(i*B1[0]+j*B2[0], i*B1[1]+j*B2[1]); return [(c[0]+x,c[1]+y) for x,y in cell]
W2,H2=760,520; sc=330.0; cx,cy=W2/2,H2/2-10
def T(p): return (cx+sc*p[0]*0.75, cy-sc*p[1]*0.75)
sv=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W2} {H2}" width="100%" role="img" aria-label="les sept hexagones de la fleur, tous deux a deux en conflit">']
sv.append(f'<rect width="{W2}" height="{H2}" fill="#fbfaf7"/>')
flower={(0,0),(1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1)}
for i in range(-3,4):
    for j in range(-3,4):
        A=hexa(i,j); col=COL[(i+3*j)%7]
        d=" ".join(("M" if n==0 else "L")+f"{T(p)[0]:.1f},{T(p)[1]:.1f}" for n,p in enumerate(A))+"Z"
        inF=(i,j) in flower
        sv.append(f'<path d="{d}" fill="{col}" stroke="{"#1f6f4a" if inF else "#b8b3a6"}" stroke-width="{2.2 if inF else 1}"/>')
        pc=T((i*B1[0]+j*B2[0]+0.0, i*B1[1]+j*B2[1]+0.0))
        sv.append(f'<text x="{pc[0]:.1f}" y="{pc[1]+5:.1f}" text-anchor="middle" font-family="Georgia,serif" font-size="{15 if inF else 12}" fill="{"#1f6f4a" if inF else "#9a9488"}" font-weight="{600 if inF else 400}">{i+3*j}</text>')
sv.append(f'<text x="{W2/2}" y="26" text-anchor="middle" font-family="Georgia,serif" font-size="16" fill="#3d3a34">La fleur : 7 cellules deux à deux en conflit (nombre écrit = couleur, soit (i+3j) mod 7)</text>')
sv.append(f'<text x="{W2/2}" y="{H2-14}" text-anchor="middle" font-family="Georgia,serif" font-size="13.5" fill="#5c5850" font-style="italic">sept couleurs deux à deux distinctes sur sept cellules mutuellement en conflit : aucun coloriage à 6 couleurs n’existe pour ce pavage</text>')
sv.append('</svg>')
open('fig_fleur.svg','w').write("\n".join(sv))
print("fig_fleur.svg", len("\n".join(sv)))
