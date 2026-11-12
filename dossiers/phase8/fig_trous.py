import sys,math; sys.path.insert(0,'.'); sys.path.insert(0,'../phase6')
from trous import *
from partition2 import voronoi_tore
b1=(1,0); b2=(0.5,math.sqrt(3)/2); m=6
seeds=[(i*b1[0]+j*b2[0]+(b1[0]+b2[0])/3, i*b1[1]+j*b2[1]+(b1[1]+b2[1])/3) for i in range(m) for j in range(m)]
U1=(m*b1[0],m*b1[1]); U2=(m*b2[0],m*b2[1])
cells0=voronoi_tore(seeds,U1,U2)
D=max(max(math.dist(a,b) for a in c for b in c) for c in cells0); k=(1-1e-4)/D
rho=0.5
W,H=640,560; sc=72; ox,oy=W/2,H/2+4
mx=sum(p[0] for c in cells0 for p in c)/sum(len(c) for c in cells0)
my=sum(p[1] for c in cells0 for p in c)/sum(len(c) for c in cells0)
def T(p): return (ox+(k*p[0]-k*mx)*sc, oy-(k*p[1]-k*my)*sc)
sv=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="pavage dont chaque cellule est un anneau avec sa cellule interieure">',
    f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>']
trois=["#e7dfd0","#dfe5e0","#eadfd9"]
for idx,c in enumerate(cells0):
    n=len(c); cen=(sum(p[0] for p in c)/n, sum(p[1] for p in c)/n)
    inner=[(cen[0]+rho*(p[0]-cen[0]), cen[1]+rho*(p[1]-cen[1])) for p in c]
    ext=" ".join(("M" if i==0 else "L")+f"{T(p)[0]:.1f},{T(p)[1]:.1f}" for i,p in enumerate(c))+"Z"
    inte=" ".join(("M" if i==0 else "L")+f"{T(p)[0]:.1f},{T(p)[1]:.1f}" for i,p in enumerate(inner))+"Z"
    sv.append(f'<path d="{ext} {inte}" fill="{trois[idx%3]}" fill-rule="evenodd" stroke="#7d7663" stroke-width="1.4"/>')
    sv.append(f'<path d="{inte}" fill="#ccdae4" stroke="#7d7663" stroke-width="1.4"/>')
sv.append(f'<rect x="0" y="0" width="{W}" height="52" fill="#fbfaf7"/><rect x="0" y="{H-64}" width="{W}" height="64" fill="#fbfaf7"/>')
sv.append(f'<text x="{W/2}" y="28" text-anchor="middle" font-family="Georgia,serif" font-size="15.5" fill="#3d3a34">Chaque cellule est un anneau (beige) avec sa cellule intérieure (bleu)</text>')
sv.append(f'<text x="{W/2}" y="{H-40}" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#5c5850" font-style="italic">l’anneau est connexe, non simplement connexe, et de même diamètre que la cellule d’origine</text>')
sv.append(f'<text x="{W/2}" y="{H-20}" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#5c5850" font-style="italic">aire totale = aire du tore à 10⁻¹³ près ; ω reste égal à 7</text>')
sv.append('</svg>')
open('fig_trous.svg','w').write("\n".join(sv)); print("ok",len(sv))
