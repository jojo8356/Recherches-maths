import json,sys,math
sys.path.insert(0,'.')
scan=json.load(open('scan_fin.json'))
def get(th,rho):
    return scan.get(f"{round(th,2)},{round(rho,3)}")
thetas=[60+0.25*k for k in range(241)]
rhos=[1.0+0.005*k for k in range(201)]
# ---- carte SVG (sous-echantillonnage) ----
idx_t=[i for i in range(0,241,2)]      # 121 colonnes
idx_r=[i for i in range(0,201,2)]      # 101 lignes
COL={7:"#1f6f4a",8:"#c9b458",9:"#c2703d",10:"#8a3b2a"}
W,H=760,470; L,R,T,B=74,150,34,60
cw=(W-L-R)/len(idx_r); ch=(H-T-B)/len(idx_t)
def X(i): return L+cw*i
def Y(i): return T+ch*i
sv=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="carte de omega sur l espace des reseaux">',
    f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>']
for a,i in enumerate(idx_t):
    th=thetas[i]
    for b,j in enumerate(idx_r):
        rho=rhos[j]; w=get(th,rho)
        if w is None: continue
        sv.append(f'<rect x="{X(b):.1f}" y="{Y(a):.1f}" width="{cw+0.6:.1f}" height="{ch+0.6:.1f}" fill="{COL[w]}" opacity="0.85"/>')
# axes
for th in (60,70,80,90,100,110,120):
    a=(th-60)/0.25/2; sv.append(f'<text x="{X(a):.1f}" y="{H-B+20}" text-anchor="middle" font-family="Georgia,serif" font-size="12.5" fill="#4a463f">{th}°</text>')
    sv.append(f'<text x="{X(a):.1f}" y="{H-B+36}" text-anchor="middle" font-family="Georgia,serif" font-size="11" fill="#8b857a"> </text>')
for rho in (1.0,1.25,1.5,1.75,2.0):
    b=(rho-1.0)/0.005/2; sv.append(f'<text x="{L-8}" y="{Y(b)+4:.1f}" text-anchor="end" font-family="Georgia,serif" font-size="12.5" fill="#4a463f">{rho:.2f}</text>')
sv.append(f'<rect x="{L}" y="{T}" width="{W-L-R}" height="{H-T-B}" fill="none" stroke="#8b857a" stroke-width="1.2"/>')
sv.append(f'<text x="{(L+W-R)/2}" y="{H-12}" text-anchor="middle" font-family="Georgia,serif" font-size="14" fill="#3d3a34">angle θ de la base réduite (degrés)</text>')
sv.append(f'<text x="22" y="{(T+H-B)/2}" transform="rotate(-90 22 {(T+H-B)/2})" text-anchor="middle" font-family="Georgia,serif" font-size="14" fill="#3d3a34">rapport ρ = |b₂|/|b₁|</text>')
# reperes
a=(60-60)/0.25/2; b=0
sv.append(f'<circle cx="{X(b)+3:.1f}" cy="{Y(a)+3:.1f}" r="5" fill="none" stroke="#1a2233" stroke-width="2"/>')
sv.append(f'<text x="{X(b)+12:.1f}" y="{Y(a)+8:.1f}" font-family="Georgia,serif" font-size="11.5" fill="#1a2233">hexagonal</text>')
a=(90-60)/0.25/2
sv.append(f'<circle cx="{X(0)+3:.1f}" cy="{Y(a)+3:.1f}" r="5" fill="none" stroke="#1a2233" stroke-width="2"/>')
sv.append(f'<text x="{X(0)+12:.1f}" y="{Y(a)+8:.1f}" font-family="Georgia,serif" font-size="11.5" fill="#1a2233">carré</text>')
# legende
lx=L+14; ly=H-B-64
sv.append(f'<rect x="{lx-8}" y="{ly-16}" width="150" height="86" rx="7" fill="#fbfaf7" opacity="0.94" stroke="#ddd8cc"/>')
for k,(w,c) in enumerate(sorted(COL.items())):
    yy=ly+4+18*k
    sv.append(f'<rect x="{lx}" y="{yy-8}" width="14" height="12" fill="{c}"/>')
    sv.append(f'<text x="{lx+22}" y="{yy+2}" font-family="Georgia,serif" font-size="12.5" fill="#3d3a34">ω = {w}</text>')
sv.append('</svg>')
open('fig_carte.svg','w').write("\n".join(sv))
print("figure ok ; taille", len("\n".join(sv))//1000,"ko")
# ---- statistiques ----
import collections
vals=collections.Counter(scan.values())
tot=sum(vals.values())
for w in sorted(vals): print(f"  omega={w:2d} : {vals[w]:6d} reseaux ({100*vals[w]/tot:.1f} %)")
