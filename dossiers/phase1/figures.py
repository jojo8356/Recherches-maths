import math, json
SQ3=math.sqrt(3); RHO=0.49; S=SQ3*RHO
def hexdist(dq,dr): return max(abs(dq),abs(dr),abs(dq+dr))
def color(q,r): return (q+3*r)%7
# --- vérification directe du motif sur un très grand patch ---
D=[(q,r) for q in range(-2,3) for r in range(-2,3) if 0<hexdist(q,r)<=2]
viol=sum(1 for q in range(-40,41) for r in range(-40,41) for dq,dr in D if color(q,r)==color(q+dq,r+dr))
print(f"motif couleur = (q + 3r) mod 7 : {viol} violation(s) sur {81*81*18} contraintes de conflit")
assert viol==0

PAL=['#b34a3c','#d99544','#8ea653','#3f8a7a','#4b6fa8','#7b5ea7','#9a9a90']

# ---------- FIG 1 : fuseau de Moser annoté ----------
V={'A':(-SQ3/2,0),'B':(SQ3/2,0),'C':(0,0.5),'D':(0,-0.5)}
B,A=V['B'],V['A']; d=math.dist(B,A); a=(d*d+3-1)/(2*d); h=math.sqrt(3-a*a)
ux,uy=(A[0]-B[0])/d,(A[1]-B[1])/d
E=(B[0]+a*ux-h*uy, B[1]+a*uy+h*ux)
mid=((B[0]+E[0])/2,(B[1]+E[1])/2); vx,vy=(E[0]-B[0])/SQ3,(E[1]-B[1])/SQ3
F=(mid[0]+0.5*vy,mid[1]-0.5*vx); G=(mid[0]-0.5*vy,mid[1]+0.5*vx)
V.update({'E':E,'F':F,'G':G})
E_edges=[('A','C'),('A','D'),('B','C'),('B','D'),('C','D'),('B','F'),('B','G'),('E','F'),('E','G'),('F','G'),('A','E')]
Sc=215; ox,oy=300,235
tr=lambda p:(ox+Sc*p[0], oy-Sc*p[1])
g=""
for u,v in E_edges:
    x1,y1=tr(V[u]); x2,y2=tr(V[v]); hero=(u,v)==('A','E')
    g+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{"#b34a3c" if hero else "#3b4657"}" stroke-width="{3.2 if hero else 2.1}" stroke-linecap="round"/>\n'
for k,p in V.items():
    x,y=tr(p); col='#b34a3c' if k in 'ABE' else '#3b4657'
    g+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="{col}"/>\n'
    g+=f'<text x="{x+11:.1f}" y="{y-9:.1f}" font-size="14" fill="#6b7280" font-family="ui-monospace,monospace">{k}</text>\n'
x1,y1=tr(V['A']); x2,y2=tr(V['E'])
g+=f'''<text x="300" y="34" text-anchor="middle" font-size="14.5" fill="#b34a3c" font-family="system-ui,sans-serif" font-weight="600">diamant 1 : A et B contraints à la même couleur</text>
<text x="300" y="54" text-anchor="middle" font-size="14.5" fill="#b34a3c" font-family="system-ui,sans-serif" font-weight="600">diamant 2 : B et E contraints à la même couleur</text>
<text x="300" y="74" text-anchor="middle" font-size="14.5" fill="#3b4657" font-family="system-ui,sans-serif">or A et E sont à distance 1 : contradiction ⇒ 4 couleurs</text>'''
open('fig_spindle.svg','w').write(f'<svg viewBox="0 0 600 330" width="100%" role="img" aria-label="fuseau de Moser"><rect width="600" height="330" fill="#fbf8f3"/>{g}</svg>')

# ---------- FIG 2 : le 7-coloriage hexagonal ----------
R=5; size=470; cxo,cyo=size/2,size/2+16; k=24.5
def vtx(q,r):
    cx,cy=S*(q+r/2), S*(r*SQ3/2)
    return [(cxo+k*cx+RHO*k*math.cos(math.pi/6+i*math.pi/3), cyo-k*cy+RHO*k*math.sin(math.pi/6+i*math.pi/3)) for i in range(6)]
g=""
for q in range(-R-1,R+2):
    for r in range(-R-1,R+2):
        if hexdist(q,r)>R: continue
        pts=" ".join(f"{x:.1f},{y:.1f}" for x,y in vtx(q,r))
        flower = hexdist(q,r)<=1
        g+=f'<polygon points="{pts}" fill="{PAL[color(q,r)]}" stroke="{"#1a2233" if flower else "rgba(0,0,0,.18)"}" stroke-width="{1.6 if flower else .7}"/>\n'
open('fig_hex.svg','w').write(f'''<svg viewBox="0 0 {size} {size+34}" width="100%" role="img" aria-label="7-coloriage du plan">
<rect width="{size}" height="{size+34}" fill="#fbf8f3"/><g>{g}</g>
<text x="{size/2}" y="{size+18}" text-anchor="middle" font-size="13.5" fill="#6b7280" font-family="system-ui,sans-serif">
hexagones de diamètre 0,98 &lt; 1 · couleur(q,r) = (q + 3r) mod 7 · les 7 cellules cerclées forment une clique de conflit</text>
</svg>''')

# ---------- FIG 3 : croissance de la taille du témoin ----------
data=[("χ = 2",2,"segment"),("χ = 3",3,"triangle"),("χ = 4",7,"fuseau de Moser"),("χ = 5",509,"de Grey / Polymath16")]
W,H=620,300; L,Rt=140,60; top=54; bh=46; gap=16
g=""
for i,(lab,n,note) in enumerate(data):
    y=top+i*(bh+gap)
    w=(W-L-Rt)*math.log10(n)/math.log10(1000)
    g+=f'<text x="{L-14}" y="{y+bh/2+5}" text-anchor="end" font-size="13.5" fill="#3b4657" font-family="system-ui,sans-serif">{lab}</text>'
    g+=f'<rect x="{L}" y="{y}" width="{max(w,2):.1f}" height="{bh}" rx="3" fill="{PAL[i*2]}"/>'
    g+=f'<text x="{L+w+9:.1f}" y="{y+bh/2+5}" font-size="13" fill="#1a2233" font-family="ui-monospace,monospace">{n} sommets</text>'
    g+=f'<text x="{L+w+9+70:.1f}" y="{y+bh/2+5}" font-size="12" fill="#9a9a90" font-family="system-ui,sans-serif">{note}</text>'
for t in (1,10,100,1000):
    x=L+(W-L-Rt)*math.log10(t)/math.log10(1000)
    g+=f'<line x1="{x:.1f}" y1="{top-8}" x2="{x:.1f}" y2="{top+4*(bh+gap)-gap+8}" stroke="#e3ded4" stroke-width="1"/><text x="{x:.1f}" y="{top-14}" text-anchor="middle" font-size="11" fill="#9a9a90" font-family="ui-monospace,monospace">{t}</text>'
open('fig_growth.svg','w').write(f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="croissance"><rect width="{W}" height="{H}" fill="#fbf8f3"/>{g}<text x="{W/2}" y="{H-14}" text-anchor="middle" font-size="12.5" fill="#6b7280" font-family="system-ui,sans-serif">nombre minimal (connu) de sommets d\u2019un graphe unité k-chromatique — échelle log</text></svg>')
print("figures écrites")
