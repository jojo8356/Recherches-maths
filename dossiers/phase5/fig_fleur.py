exec(open('treillis.py').read().split('# ----------families ----------')[0])
s3=math.sqrt(3); b1=(1,0); b2=(0.5,s3/2)
cell=voronoi(b1,b2); k=0.98/diam(cell)
cell=[(k*x,k*y) for x,y in cell]; B1=(k*b1[0],k*b1[1]); B2=(k*b2[0],k*b2[1])
COL=["#dfe9e0","#f6e2cd","#dbe2f0","#f2dce6","#d7ecef","#eee4c8","#e6ddf1"]
flower={(0,0),(1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1)}
def cen(i,j): return (i*B1[0]+j*B2[0], i*B1[1]+j*B2[1])
def hexa(i,j):
    c=cen(i,j); return [(c[0]+x,c[1]+y) for x,y in cell]
Rg=2; r_cell=max(math.dist((0,0),p) for p in cell)
ext=max(max(abs(cen(i,j)[0])+r_cell for i in range(-Rg,Rg+1) for j in range(-Rg,Rg+1)),
        max(abs(cen(i,j)[1])+r_cell for i in range(-Rg,Rg+1) for j in range(-Rg,Rg+1)))
W,H=720,560; sc=(min(W,H)-120)/(2*ext); cx,cy=W/2,H/2+8
def T(p): return (cx+sc*p[0], cy-sc*p[1])
sv=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="les sept cellules de la fleur sont deux a deux en conflit">',
    f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>']
for i in range(-Rg,Rg+1):
    for j in range(-Rg,Rg+1):
        A=hexa(i,j); col=COL[(i+3*j)%7]; inF=(i,j) in flower
        d=" ".join(("M" if n==0 else "L")+f"{T(p)[0]:.1f},{T(p)[1]:.1f}" for n,p in enumerate(A))+"Z"
        sv.append(f'<path d="{d}" fill="{col}" stroke="{"#1f6f4a" if inF else "#c2bdb0"}" stroke-width="{2.6 if inF else 1.1}"/>')
        pc=T(cen(i,j))
        sv.append(f'<text x="{pc[0]:.1f}" y="{pc[1]+5:.1f}" text-anchor="middle" font-family="Georgia,serif" font-size="{17 if inF else 12}" fill="{"#14482f" if inF else "#a9a294"}" font-weight="{700 if inF else 400}">{(i+3*j)%7}</text>')
sv.append(f'<text x="{W/2}" y="30" text-anchor="middle" font-family="Georgia,serif" font-size="16.5" fill="#3d3a34">La fleur : sept cellules deux à deux en conflit</text>')
sv.append(f'<text x="{W/2}" y="{H-16}" text-anchor="middle" font-family="Georgia,serif" font-size="13.5" fill="#5c5850" font-style="italic">chiffre = couleur (i+3j) mod 7 — sept couleurs distinctes sur sept cellules mutuellement en conflit</text>')
sv.append('</svg>')
open('fig_fleur.svg','w').write("\n".join(sv))
# contrôle des bornes
xs=[T(p)[0] for i in range(-Rg,Rg+1) for j in range(-Rg,Rg+1) for p in hexa(i,j)]
ys=[T(p)[1] for i in range(-Rg,Rg+1) for j in range(-Rg,Rg+1) for p in hexa(i,j)]
print(f"bornes x [{min(xs):.1f},{max(xs):.1f}]  y [{min(ys):.1f},{max(ys):.1f}]  (canvas {W}x{H})")
assert min(xs)>2 and max(xs)<W-2 and min(ys)>40 and max(ys)<H-30, "débordement"
print("OK, pas de débordement")
