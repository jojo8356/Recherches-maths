import json
PAL={'float':'#b34a3c','exact':'#3f8a7a','acc':'#2b3a55'}
# ---------- FIG 1 : flottant vs exact ----------
groups=[("arêtes",402,246,450),("degré maximal",12,6,14),("dégénérescence",6,3,7)]
W,H=660,300; x0=110; bw=150; gap=30; top=56; bh=110
g=""
for i,(lab,vf,ve,scale) in enumerate(groups):
    xx=x0+i*(bw+gap)
    hf=bh*vf/scale; he=bh*ve/scale
    g+=f'<rect x="{xx}" y="{top+bh-hf:.1f}" width="{bw/2-4:.0f}" height="{hf:.1f}" fill="{PAL["float"]}" rx="3"/>'
    g+=f'<rect x="{xx+bw/2+4:.1f}" y="{top+bh-he:.1f}" width="{bw/2-4:.0f}" height="{he:.1f}" fill="{PAL["exact"]}" rx="3"/>'
    g+=f'<text x="{xx+bw/4-2:.0f}" y="{top+bh-hf-7:.1f}" text-anchor="middle" font-size="13" fill="{PAL["float"]}" font-family="ui-monospace,monospace">{vf}</text>'
    g+=f'<text x="{xx+3*bw/4+2:.0f}" y="{top+bh-he-7:.1f}" text-anchor="middle" font-size="13" fill="{PAL["exact"]}" font-family="ui-monospace,monospace">{ve}</text>'
    g+=f'<line x1="{xx}" y1="{top+bh}" x2="{xx+bw}" y2="{top+bh}" stroke="#2b3a55" stroke-width="1.5"/>'
    g+=f'<text x="{xx+bw/2}" y="{top+bh+22}" text-anchor="middle" font-size="12.5" fill="#3c4459" font-family="system-ui,sans-serif">{lab}</text>'
g+=f'<rect x="{x0}" y="18" width="12" height="12" fill="{PAL["float"]}" rx="2"/><text x="{x0+18}" y="29" font-size="12.5" fill="#3c4459" font-family="system-ui,sans-serif">flottant, sans dédoublonnage (74 → 122 points fantômes)</text>'
g+=f'<rect x="{x0+330}" y="18" width="12" height="12" fill="{PAL["exact"]}" rx="2"/><text x="{x0+348}" y="29" font-size="12.5" fill="#3c4459" font-family="system-ui,sans-serif">exact dans ℚ(√3), dédoublonné</text>'
g+=f'<text x="{W/2}" y="{H-14}" text-anchor="middle" font-size="12" fill="#8f3a2c" font-family="system-ui,sans-serif">même configuration, deux régimes arithmétiques : le 6-core n\'existe que dans le premier</text>'
open('fig_illusion.svg','w').write(f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="illusion"><rect width="{W}" height="{H}" fill="#fbf8f3"/>{g}</svg>')

# ---------- FIG 2 : histogramme des degrés du cœur ----------
hist={int(k):v for k,v in json.load(open('res_hist.json'))['hist'].items()}
W,H=660,280; L,R,T,B=62,24,40,52
ks=sorted(hist); kmax=max(hist.values())
g=""
for e in range(0,kmax+1,10):
    y=H-B-(H-B-T)*e/kmax
    g+=f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="#eae5db"/><text x="{L-8}" y="{y+4:.1f}" text-anchor="end" font-size="10.5" fill="#9a9a90" font-family="ui-monospace,monospace">{e}</text>'
bw=(W-L-R)/len(ks)
for i,k in enumerate(ks):
    h=(H-B-T)*hist[k]/kmax
    x=L+i*bw+bw*0.15
    g+=f'<rect x="{x:.1f}" y="{H-B-h:.1f}" width="{bw*0.7:.1f}" height="{h:.1f}" fill="{PAL["exact"] if k==min(ks) else PAL["acc"]}" rx="2"/>'
    g+=f'<text x="{x+bw*0.35:.1f}" y="{H-B+16}" text-anchor="middle" font-size="11" fill="#6b7280" font-family="ui-monospace,monospace">{k}</text>'
    if hist[k]>=3: g+=f'<text x="{x+bw*0.35:.1f}" y="{H-B-h-5:.1f}" text-anchor="middle" font-size="10.5" fill="#6b7280" font-family="ui-monospace,monospace">{hist[k]}</text>'
g+=f'<text x="{(L+W-R)/2}" y="{H-12}" text-anchor="middle" font-size="12" fill="#6b7280" font-family="system-ui,sans-serif">degré dans le cœur (97 sommets, 273 arêtes, degré minimal 4)</text>'
open('fig_hist.svg','w').write(f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="histogramme"><rect width="{W}" height="{H}" fill="#fbf8f3"/>{g}</svg>')
print("figures ok")
