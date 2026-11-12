import json
import collections

scan = json.load(open('scan_fin.json'))
thetas = [60 + 0.25 * k for k in range(241)]
rhos = [1.0 + 0.005 * k for k in range(201)]


def get(th, rho):
    return scan.get(f"{round(th,2)},{round(rho,3)}")


idx_t = list(range(0, 241, 2))   # 121 valeurs de theta (axe horizontal)
idx_r = list(range(0, 201, 2))   # 101 valeurs de rho   (axe vertical)

COL = {7: "#1f6f4a", 8: "#d3bd63", 9: "#c2703d", 10: "#8a3b2a"}
W, H = 780, 470
L, R, T, B = 78, 168, 40, 62
cw = (W - L - R) / len(idx_t)
ch = (H - T - B) / len(idx_r)


def X(i):
    return L + cw * i


def Y(j):
    return H - B - ch * j


sv = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" '
      f'aria-label="carte de omega sur l espace des reseaux">',
      f'<rect width="{W}" height="{H}" fill="#fbfaf7"/>']

# corps de la carte, avec fusion des segments horizontaux
for a_j, j in enumerate(idx_r):
    rho = rhos[j]
    run_start = None
    run_val = None
    for a_i, i in enumerate(idx_t):
        w = get(thetas[i], rho)
        if w != run_val:
            if run_val is not None:
                sv.append(f'<rect x="{X(run_start):.1f}" y="{Y(a_j)-ch:.1f}" '
                          f'width="{cw*(a_i-run_start)+0.4:.1f}" height="{ch+1.2:.1f}" '
                          f'fill="{COL[run_val]}"/>')
            run_start = a_i
            run_val = w
    if run_val is not None:
        sv.append(f'<rect x="{X(run_start):.1f}" y="{Y(a_j)-ch:.1f}" '
                  f'width="{cw*(len(idx_t)-run_start)+0.4:.1f}" height="{ch+1.2:.1f}" '
                  f'fill="{COL[run_val]}"/>')

# axes
for th in (60, 70, 80, 90, 100, 110, 120):
    i = (th - 60) / 0.25 / 2
    sv.append(f'<text x="{X(i):.1f}" y="{H-B+20}" text-anchor="middle" '
              f'font-family="Georgia,serif" font-size="12.5" fill="#4a463f">{th}°</text>')
for rho in (1.0, 1.25, 1.5, 1.75, 2.0):
    j = (rho - 1.0) / 0.005 / 2
    sv.append(f'<text x="{L-9}" y="{Y(j)+4:.1f}" text-anchor="end" '
              f'font-family="Georgia,serif" font-size="12.5" fill="#4a463f">{rho:.2f}</text>')
sv.append(f'<rect x="{L}" y="{T}" width="{W-L-R}" height="{H-T-B}" fill="none" '
          f'stroke="#8b857a" stroke-width="1.2"/>')
sv.append(f'<text x="{(L+W-R)/2:.0f}" y="{H-14}" text-anchor="middle" font-family="Georgia,serif" '
          f'font-size="14" fill="#3d3a34">angle θ de la base réduite (degrés)</text>')
sv.append(f'<text x="24" y="{(T+H-B)/2:.0f}" transform="rotate(-90 24 {(T+H-B)/2:.0f})" '
          f'text-anchor="middle" font-family="Georgia,serif" font-size="14" fill="#3d3a34">ρ = |b₂| / |b₁|</text>')

# reperes
for (th, rho, lab, dx, dy) in ((60, 1.0, "hexagonal", 10, -12), (90, 1.0, "carré", 10, -12)):
    i = (th - 60) / 0.25 / 2
    j = (rho - 1.0) / 0.005 / 2
    sv.append(f'<circle cx="{X(i):.1f}" cy="{Y(j):.1f}" r="5.5" fill="none" stroke="#1a2233" stroke-width="2.2"/>')
    sv.append(f'<text x="{X(i)+dx:.1f}" y="{Y(j)+dy:.1f}" font-family="Georgia,serif" '
              f'font-size="12" fill="#1a2233">{lab}</text>')

# legende
lx, ly = W - R + 12, T + 132
sv.append(f'<rect x="{lx-10}" y="{ly-18}" width="140" height="94" rx="8" fill="#fbfaf7" opacity="0.93" stroke="#ddd8cc"/>')
for k, w in enumerate(sorted(COL)):
    yy = ly + 18 * k
    sv.append(f'<rect x="{lx}" y="{yy-9}" width="15" height="12" fill="{COL[w]}"/>')
    sv.append(f'<text x="{lx+23}" y="{yy+1}" font-family="Georgia,serif" font-size="12.5" fill="#3d3a34">ω = {w}</text>')

# encart statistiques
sx, sy = W - R + 12, T + 6
sv.append(f'<text x="{sx}" y="{sy+10}" font-family="Georgia,serif" font-size="11.5" fill="#6b6559">48 441 réseaux</text>')
for k, line in enumerate(("55,2 %", "39,0 %", "5,7 %", "0,1 %")):
    sv.append(f'<text x="{sx}" y="{sy+34+k*17}" font-family="Georgia,serif" font-size="11.5" fill="#6b6559">ω={7+k} : {line}</text>')
sv.append('</svg>')
open('fig_carte.svg', 'w').write("\n".join(sv))
print("figure ok ;", len("\n".join(sv)) // 1000, "ko ;", "\n".join(sv).count("<rect"), "rectangles")
