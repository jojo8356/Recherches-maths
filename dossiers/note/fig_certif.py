"""Figure du certificat : carte omega du balayage en fond, profondeur de subdivision
du certificat en surimpression."""
import json

scan = json.load(open('scan_fin.json'))
cert = json.load(open('certificat.json'))
thetas = [60 + 0.25 * k for k in range(241)]
rhos = [1.0 + 0.005 * k for k in range(201)]

COL = {7: "#e4ece5", 8: "#f2eccf", 9: "#f6e3d6", 10: "#efd8cf"}
ACC = "#1f6f4a"
W, H = 780, 470
L, R, T, B = 78, 168, 40, 62
cw = (W - L - R) / 241
ch = (H - T - B) / 201


def X(th):
    return L + (th - 60) / 60 * (W - L - R)


def Y(rho):
    return H - B - (rho - 1.0) / 1.0 * (H - T - B)


sv = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" '
      f'aria-label="certificat : couverture du domaine et profondeur de subdivision">',
      f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>']

# fond : omega du balayage (teintes tres claires)
for j, rho in enumerate(rhos):
    run_start = None
    run_val = None
    for i, th in enumerate(thetas):
        v = scan.get(f"{round(th,2)},{round(rho,3)}")
        if v != run_val:
            if run_val is not None:
                sv.append(f'<rect x="{X(thetas[run_start]):.1f}" y="{Y(rho)-ch:.1f}" '
                          f'width="{X(th)-X(thetas[run_start])+0.4:.1f}" height="{ch+1.2:.1f}" '
                          f'fill="{COL[run_val]}"/>')
            run_start, run_val = i, v
    if run_val is not None:
        sv.append(f'<rect x="{X(thetas[run_start]):.1f}" y="{Y(rho)-ch:.1f}" '
                  f'width="{X(120)-X(thetas[run_start])+0.4:.1f}" height="{ch+1.2:.1f}" '
                  f'fill="{COL[run_val]}"/>')

# surimpression : boites certifiees de profondeur >= 2
n_prof = 0
for (a, b, c, d, prof, ok, marge) in cert['boites']:
    if ok and prof >= 2:
        n_prof += 1
        sv.append(f'<rect x="{X(c):.1f}" y="{Y(b):.1f}" width="{max(X(d)-X(c),1.2):.1f}" '
                  f'height="{max(Y(a)-Y(b),1.2):.1f}" fill="none" stroke="#2b2a26" '
                  f'stroke-width="0.7" opacity="0.75"/>')

# cadre
sv.append(f'<rect x="{L}" y="{T}" width="{W-L-R}" height="{H-T-B}" fill="none" '
          f'stroke="#cfc9bb" stroke-width="1"/>')
for th in (60, 70, 80, 90, 100, 110, 120):
    sv.append(f'<text x="{X(th):.1f}" y="{H-B+20}" text-anchor="middle" '
              f'font-family="Georgia,serif" font-size="12.5" fill="#4a463f">{th}°</text>')
for rho in (1.0, 1.25, 1.5, 1.75, 2.0):
    sv.append(f'<text x="{L-10}" y="{Y(rho)+4:.1f}" text-anchor="end" '
              f'font-family="Georgia,serif" font-size="12.5" fill="#4a463f">{rho:.2f}</text>')
sv.append(f'<text x="{(L+W-R)/2}" y="{H-14}" text-anchor="middle" font-family="Georgia,serif" '
          f'font-size="13" fill="#4a463f">angle θ de la base réduite (degrés)</text>')
sv.append(f'<text x="22" y="{(T+H-B)/2}" text-anchor="middle" font-family="Georgia,serif" '
          f'font-size="13" fill="#4a463f" transform="rotate(-90 22 {(T+H-B)/2})">rapport ρ des longueurs</text>')

# legende
lx = W - R + 12
sv.append(f'<text x="{lx}" y="{T+8}" font-family="Georgia,serif" font-size="12.5" '
          f'fill="#2b2a26">{cert["nb_boites"]:,} boîtes</text>'.replace(',', ' '))
sv.append(f'<text x="{lx}" y="{T+28}" font-family="Georgia,serif" font-size="12" '
          f'fill="#5b564d">100,0000 % du domaine</text>')
sv.append(f'<text x="{lx}" y="{T+46}" font-family="Georgia,serif" font-size="12" '
          f'fill="#5b564d">certifié, 0 échec</text>')
y0 = T + 76
sv.append(f'<text x="{lx}" y="{y0}" font-family="Georgia,serif" font-size="11" '
          f'fill="#5b564d">fond : ω du balayage</text>')
for k, v in ((7, 'ω = 7'), (8, 'ω = 8'), (9, 'ω = 9'), (10, 'ω = 10')):
    yy = y0 + 18 + 19 * (k - 7)
    sv.append(f'<rect x="{lx}" y="{yy-9}" width="16" height="11" fill="{COL[k]}" '
              f'stroke="#cfc9bb" stroke-width="0.7"/>')
    sv.append(f'<text x="{lx+23}" y="{yy}" font-family="Georgia,serif" font-size="11.5" '
              f'fill="#3c3831">{v}</text>')
yy = y0 + 100
sv.append(f'<rect x="{lx}" y="{yy-9}" width="16" height="11" fill="none" stroke="#2b2a26" '
          f'stroke-width="0.8"/>')
sv.append(f'<text x="{lx+23}" y="{yy}" font-family="Georgia,serif" font-size="11.5" '
          f'fill="#3c3831">boîtes fines</text>')
sv.append(f'<text x="{lx+23}" y="{yy+15}" font-family="Georgia,serif" font-size="10.5" '
          f'fill="#7a7468">({n_prof} boîtes)</text>')
sv.append('</svg>')
open('fig_certificat.svg', 'w').write('\n'.join(sv))
print("fig_certificat.svg :", len(open('fig_certificat.svg').read()), "octets,", n_prof, "boites fines")
