import math
# ---------- FIG A : extrapolation de la taille des témoins ----------
data=[(2,2),(3,3),(4,7),(5,509)]
pred=[("M1 — le ratio stagne (×72,7)",37012,"#8ea653"),
      ("M2 — le ratio croît comme au cran précédent",1153401,"#d99544"),
      ("M3 — double exponentielle",2798255,"#b34a3c")]
W,H=700,360; L,R,T,Bt=64,150,30,48
def X(k): return L+(W-L-R)*(k-1.6)/4.9
def Y(v): return H-Bt-(math.log10(v)/7.0)*(H-Bt-T)
g=""
for e in range(0,8):
    y=Y(10**e)
    g+=f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="#eae5db" stroke-width="1"/>'
    g+=f'<text x="{L-10}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="#9a9a90" font-family="ui-monospace,monospace">10^{e}</text>'
for k in range(2,7):
    g+=f'<text x="{X(k):.1f}" y="{H-Bt+22}" text-anchor="middle" font-size="12" fill="#6b7280" font-family="system-ui,sans-serif">k = {k}</text>'
for lab,v,c in pred:
    g+=f'<line x1="{X(5):.1f}" y1="{Y(509):.1f}" x2="{X(6):.1f}" y2="{Y(v):.1f}" stroke="{c}" stroke-width="2" stroke-dasharray="5 4"/>'
    g+=f'<circle cx="{X(6):.1f}" cy="{Y(v):.1f}" r="5" fill="{c}"/>'
    g+=f'<text x="{X(6)+12:.1f}" y="{Y(v)+4:.1f}" font-size="11.5" fill="{c}" font-family="system-ui,sans-serif">{v:,.0f}'.replace(","," ")+'</text>'
g+=f'<polyline points="{" ".join(f"{X(k):.1f},{Y(v):.1f}" for k,v in data)}" fill="none" stroke="#2b3a55" stroke-width="2.6"/>'
for k,v in data:
    g+=f'<circle cx="{X(k):.1f}" cy="{Y(v):.1f}" r="5.5" fill="#2b3a55"/>'
    g+=f'<text x="{X(k)+9:.1f}" y="{Y(v)-8:.1f}" font-size="12" fill="#1a2233" font-family="ui-monospace,monospace">{v}</text>'
leg="".join(f'<text x="{W-R+6}" y="{T+16+i*17}" font-size="10.5" fill="{c}" font-family="system-ui,sans-serif">{lab}</text>' for i,(lab,v,c) in enumerate(pred))
open('fig_extrap.svg','w').write(f'''<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="extrapolation">
<rect width="{W}" height="{H}" fill="#fbf8f3"/>{g}{leg}
<text x="{(L+W-R)/2}" y="{H-8}" text-anchor="middle" font-size="12" fill="#6b7280" font-family="system-ui,sans-serif">taille du plus petit graphe unité k-chromatique connu (échelle log) et trois extrapolations pour k = 6</text></svg>''')

# ---------- FIG B : la droite des densités ----------
W,H=700,240; x0,x1=70,630; lo,hi=0.12,0.25
def X(d): return x0+(d-lo)/(hi-lo)*(x1-x0)
marks=[(1/7,"1/7 = 0,1429","classe du 7-coloriage (E5)",'#4b6fa8','up'),
       (1/6,"1/6 = 0,1667","seuil qu'il faudrait franchir",'#7b5ea7','down'),
       (math.pi/(8*math.sqrt(3)),"π/(8√3) = 0,2267","classe SANS distance 1, densité atteignable",'#b34a3c','up')]
g=f'<line x1="{x0}" y1="120" x2="{x1}" y2="120" stroke="#2b3a55" stroke-width="2"/>'
for d in (0.12,0.15,0.20,0.25):
    g+=f'<line x1="{X(d):.1f}" y1="114" x2="{X(d):.1f}" y2="126" stroke="#2b3a55" stroke-width="1.4"/><text x="{X(d):.1f}" y="146" text-anchor="middle" font-size="10.5" fill="#9a9a90" font-family="ui-monospace,monospace">{d}</text>'
g+=f'<rect x="{X(1/6):.1f}" y="106" width="{X(math.pi/(8*math.sqrt(3)))-X(1/6):.1f}" height="28" fill="#f6e9e6"/>'
for d,lab,note,c,side in marks:
    g+=f'<circle cx="{X(d):.1f}" cy="120" r="6.5" fill="{c}"/>'
    if side=='up':
        g+=f'<line x1="{X(d):.1f}" y1="113" x2="{X(d):.1f}" y2="70" stroke="{c}" stroke-width="1.2" stroke-dasharray="3 3"/>'
        g+=f'<text x="{X(d):.1f}" y="60" text-anchor="middle" font-size="12.5" fill="{c}" font-family="ui-monospace,monospace">{lab}</text>'
        g+=f'<text x="{X(d):.1f}" y="44" text-anchor="middle" font-size="10.5" fill="#6b7280" font-family="system-ui,sans-serif">{note}</text>'
    else:
        g+=f'<line x1="{X(d):.1f}" y1="127" x2="{X(d):.1f}" y2="170" stroke="{c}" stroke-width="1.2" stroke-dasharray="3 3"/>'
        g+=f'<text x="{X(d):.1f}" y="186" text-anchor="middle" font-size="12.5" fill="{c}" font-family="ui-monospace,monospace">{lab}</text>'
        g+=f'<text x="{X(d):.1f}" y="202" text-anchor="middle" font-size="10.5" fill="#6b7280" font-family="system-ui,sans-serif">{note}</text>'
g+=f'<text x="{(x0+x1)/2}" y="226" text-anchor="middle" font-size="11.5" fill="#8f3a2c" font-family="system-ui,sans-serif">la classe rouge dépasse le seuil violet : aucune borne de densité ne peut interdire 6 couleurs</text>'
open('fig_density.svg','w').write(f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="densités"><rect width="{W}" height="{H}" fill="#fbf8f3"/>{g}</svg>')
print("figures 2 ok")
