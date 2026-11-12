import math
SQ3=math.sqrt(3)
W,H=680,340; L,R,T,B=70,150,36,56
def X(d): return L+(W-L-R)*(d-0.05)/0.97
def Y(v): return H-B-(v/0.26)*(H-B-T)
def dens(d): return (math.pi*d*d/4)/((SQ3/2)*(1+d)**2)
g=""
for e in [0,0.05,0.1,0.15,0.2,0.25]:
    y=Y(e); g+=f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="#eae5db"/><text x="{L-9}" y="{y+4:.1f}" text-anchor="end" font-size="10.5" fill="#9a9a90" font-family="ui-monospace,monospace">{e:.2f}</text>'
pts=" ".join(f"{X(d/100):.1f},{Y(dens(d/100)):.1f}" for d in range(5,101))
g+=f'<polyline points="{pts}" fill="none" stroke="#2b3a55" stroke-width="2.6"/>'
for v,lab,c,dy in ((1/6,"1/6 = 0,1667 : seuil à franchir pour 6 couleurs","#7b5ea7",-6),
                   (1/7,"1/7 = 0,1429 : une classe du 7-coloriage","#4b6fa8",14)):
    y=Y(v); g+=f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="{c}" stroke-width="1.6" stroke-dasharray="6 4"/>'
    g+=f'<text x="{W-R+6}" y="{y+dy-2:.1f}" font-size="10.5" fill="{c}" font-family="system-ui,sans-serif">{lab}</text>'
y=Y(dens(1.0))
g+=f'<circle cx="{X(1.0):.1f}" cy="{y:.1f}" r="6" fill="#b34a3c"/>'
g+=f'<text x="{X(1.0)-12:.1f}" y="{y-12:.1f}" text-anchor="end" font-size="13" fill="#b34a3c" font-family="ui-monospace,monospace">0,2267</text>'
g+=f'<text x="{X(1.0)-12:.1f}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="#6b7280" font-family="system-ui,sans-serif">diamètre 1, pas 2 (limite)</text>'
for d in (0.2,0.4,0.6,0.8,1.0):
    g+=f'<text x="{X(d):.1f}" y="{H-B+18}" text-anchor="middle" font-size="11" fill="#6b7280" font-family="ui-monospace,monospace">{d}</text>'
g+=f'<text x="{(L+W-R)/2}" y="{H-14}" text-anchor="middle" font-size="12" fill="#6b7280" font-family="system-ui,sans-serif">diamètre maximal d\u2019un disque d\u2019une classe sans distance 1 (pas = 1 + d)</text>'
open('fig_plafond.svg','w').write(f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="densité"><rect width="{W}" height="{H}" fill="#fbf8f3"/>{g}</svg>')
print("ok", dens(1.0))
