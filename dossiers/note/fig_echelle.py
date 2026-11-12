"""Figure T8 : omega(delta) et carte de delta* (plus grande echelle ou omega <= 6)."""
import json
import echelle

CAS = [(1.0, 60, "hexagonal", "#1f6f4a"),
       (1.0, 90, "carré", "#8a3b2a"),
       (2.0, 90, "rectangulaire ρ = 2", "#c2703d"),
       (1.9, 70, "anisotrope 1,9 / 70°", "#b08a2e"),
       (1.4, 100, "1,4 / 100°", "#4a6fa5"),
       (1.5, 75, "1,5 / 75°", "#7a5c9e")]
DEL = [round(0.05 + 0.02 * k, 3) for k in range(48)]

courbes = {}
for (rho, th, nom, col) in CAS:
    courbes[nom] = [echelle.omega_echelle(rho, th, d) for d in DEL]
json.dump({"delta": DEL, "courbes": courbes}, open("courbes_echelle.json", "w"))
print("courbes calculees")

W, H = 780, 400
sv = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" '
      f'aria-label="omega selon l echelle et carte de delta etoile">',
      f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>']

# ---- panneau A : courbes
L, R, T, B = 56, 470, 34, 58
x0, x1 = L, R
y0, y1 = T, H - B
ymax = 12
def X(d): return x0 + (d - 0.05) / 0.94 * (x1 - x0)
def Y(v): return y1 - (v - 1) / (ymax - 1) * (y1 - y0)
sv.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff" stroke="#cfc9bb"/>')
for v in (1, 3, 5, 7, 9, 12):
    sv.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="#e8e3d8" stroke-width="1"/>')
    sv.append(f'<text x="{x0-8}" y="{Y(v)+4:.1f}" text-anchor="end" font-family="Georgia,serif" font-size="10.5" fill="#6d675d">{v}</text>')
sv.append(f'<line x1="{x0}" y1="{Y(7):.1f}" x2="{x1}" y2="{Y(7):.1f}" stroke="#1f6f4a" stroke-width="1.4" stroke-dasharray="5 3"/>')
for d in (0.1, 0.3, 0.5, 0.7, 0.9):
    sv.append(f'<text x="{X(d):.1f}" y="{y1+18}" text-anchor="middle" font-family="Georgia,serif" font-size="10.5" fill="#6d675d">{d}</text>')
sv.append(f'<text x="{(x0+x1)/2:.0f}" y="{H-14}" text-anchor="middle" font-family="Georgia,serif" font-size="12" fill="#4a463f">diamètre δ des cellules</text>')
sv.append(f'<text x="{x0-40}" y="{y0+4}" font-family="Georgia,serif" font-size="11" fill="#4a463f">ω</text>')
for (rho, th, nom, col) in CAS:
    # segments <line> : ImageMagick ne rend pas fill="none" sur un chemin
    for (d1, v1), (d2, v2) in zip(list(zip(DEL, courbes[nom]))[:-1], list(zip(DEL, courbes[nom]))[1:]):
        sv.append(f'<line x1="{X(d1):.1f}" y1="{Y(v1):.1f}" x2="{X(d2):.1f}" y2="{Y(v2):.1f}" '
                  f'stroke="{col}" stroke-width="1.9" opacity="0.92"/>')
# ---- panneau B : carte de delta*
pay = json.load(open("paysage.json"))
THE, RHO, dstar = pay["theta"], pay["rho"], pay["delta_etoile"]
L2, R2, T2 = 540, 760, 34
H2 = H - B
cw = (R2 - L2) / (len(THE) - 1)
ch = (H2 - T2) / (len(RHO) - 1)
def X2(th): return L2 + (th - 60) / 60 * (R2 - L2)
def Y2(rho): return H2 - (rho - 1.0) / 1.0 * (H2 - T2)
sv.append(f'<rect x="{L2}" y="{T2}" width="{R2-L2}" height="{H2-T2}" fill="#fff" stroke="#cfc9bb"/>')
for th in THE:
    for rho in RHO:
        v = dstar.get(f"{th},{rho:.4f}")
        if v is None: continue
        t = (v - 0.48) / (0.78 - 0.48)
        t = max(0.0, min(1.0, t))
        r = int(247 - 190 * t); g = int(243 - 120 * t); b = int(232 - 60 * t)
        sv.append(f'<rect x="{X2(th)-cw*0.55:.1f}" y="{Y2(rho)-ch*0.55:.1f}" '
                  f'width="{cw*1.1:.1f}" height="{ch*1.1:.1f}" fill="rgb({r},{g},{b})"/>')
for th in (60, 80, 100, 120):
    sv.append(f'<text x="{X2(th):.1f}" y="{H2+18}" text-anchor="middle" font-family="Georgia,serif" font-size="10" fill="#6d675d">{th}°</text>')
for rho in (1.0, 1.5, 2.0):
    sv.append(f'<text x="{L2-6}" y="{Y2(rho)+4:.1f}" text-anchor="end" font-family="Georgia,serif" font-size="10" fill="#6d675d">{rho:.1f}</text>')
sv.append(f'<text x="{(L2+R2)/2:.0f}" y="{H-14}" text-anchor="middle" font-family="Georgia,serif" font-size="11" fill="#4a463f">θ (degrés) — δ* de 0,48 (clair) à 0,78 (sombre)</text>')
sv.append(f'<text x="{(L2+R2)/2:.0f}" y="{T2-10}" text-anchor="middle" font-family="Georgia,serif" font-size="11.5" fill="#2b2a26">δ* : plus grande échelle sans clique de 7</text>')
# legende du panneau A
ly = H - 2
for idx, (rho, th, nom, col) in enumerate(CAS):
    cx = L + (idx % 2) * 210
    cy = T - 20 + (idx // 2) * 0 + 0 if False else None
    pass
for idx, (rho, th, nom, col) in enumerate(CAS):
    cx = L + (idx % 3) * 158
    cy = 14 + (idx // 3) * 16
    sv.append(f'<line x1="{cx}" y1="{cy-3}" x2="{cx+16}" y2="{cy-3}" stroke="{col}" stroke-width="2.2"/>')
    sv.append(f'<text x="{cx+21}" y="{cy}" font-family="Georgia,serif" font-size="9.5" fill="#3c3831">{nom}</text>')
sv.append('</svg>')
open("fig_echelle.svg", "w").write("\n".join(sv))
print("fig_echelle.svg :", len(open("fig_echelle.svg").read()), "octets")
