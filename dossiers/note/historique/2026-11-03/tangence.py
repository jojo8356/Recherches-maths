"""Conflit et tangence : tolerance calibree, deux conventions, juge exact.

Historique de ce module (a garder) :
 1. le flottant, avec une tolerance arbitraire, donnait des valeurs instables ;
 2. une decision « a 60 chiffres » a semble trancher (omega = 5 au lieu de 7) mais elle
    partait de coordonnees FLOTTANTES : l'erreur de 1e-17 sur les sommets etait ensuite
    lue comme un ecart de 1e-17 a la tangence, donc du bruit;
 3. exact_tangence.py (corps Q(sqrt d), aucun flottant) a tranche : omega = 7 a delta=1/2
    pour l'hexagonal. Les valeurs publiees etaient justes ; c'est la tolerance nulle qui
    etait fausse.

Regle retenue : la tolerance doit etre au-dessus de l'erreur d'arrondi (1e-16) et bien
au-dessous du plus petit ecart geometrique reel. TOL = 1e-12. Le juge est exact_tangence.py.

Deux conventions, parce que la question a un sens :
  - "large"  : une tangence exacte (dmin = 1) COMPTE comme un conflit  -> cellules fermees,
               c'est la convention utilisee partout dans la note (et celle du juge exact) ;
  - "strict" : une tangence exacte NE COMPTE PAS -> borne valable meme si l'on reattribue
               les points de bord entre cellules voisines.
On a toujours omega_strict <= omega_large, et omega_strict est la borne inconditionnelle.
"""
import math
import numpy as np

import echelle

TOL = 1e-12


def matrices(rho, thd, delta):
    """Matrices de distances min/max entre polygones, et la liste des decalages."""
    P, b1, b2 = echelle.reseau_unite(rho, thd)
    det = abs(b1[0] * b2[1] - b1[1] * b2[0])
    Rmax = 1.0 / delta + 1.2
    Ri = int(math.ceil(math.hypot(*b2) * Rmax / det)) + 1
    Rj = int(math.ceil(math.hypot(*b1) * Rmax / det)) + 1
    cand = []
    for i in range(-Ri, Ri + 1):
        for j in range(-Rj, Rj + 1):
            if (i, j) == (0, 0):
                continue
            D = math.hypot(delta * (i * b1[0] + j * b2[0]), delta * (i * b1[1] + j * b2[1]))
            if abs(D - 1) <= delta * 1.05:          # condition necessaire (diametre de cellule = delta)
                cand.append((i, j))
    Pd = [(delta * x, delta * y) for (x, y) in P]
    offsets = [(0, 0)] + cand
    n, nv = len(offsets), len(Pd)
    cen = np.array([(delta * (i * b1[0] + j * b2[0]), delta * (i * b1[1] + j * b2[1])) for (i, j) in offsets])
    Vp = (np.asarray(Pd)[None, :, :] + cen[:, None, :]).reshape(-1, 2)
    Vn = np.roll(Vp.reshape(n, nv, 2), -1, axis=1).reshape(-1, 2)
    A = Vp[None, :, :]
    B = Vn[None, :, :]
    AB = B - A
    L = np.maximum((AB ** 2).sum(-1), 1e-30)
    t = np.clip(((Vp[:, None, :] - A) * AB).sum(-1) / L, 0, 1)
    pr = A + t[..., None] * AB
    Dm = np.sqrt(((Vp[:, None, :] - pr) ** 2).sum(-1)).reshape(n, nv, n, nv)
    lo = Dm.min(axis=(1, 3))
    vv = np.sqrt(((Vp[:, None, :] - Vp[None, :, :]) ** 2).sum(-1)).reshape(n, nv, n, nv).max(axis=(1, 3))
    return offsets, lo, vv


def adjacences(lo, vv, tol=TOL):
    """(adj_large, adj_strict) a partir des matrices de distances."""
    n = lo.shape[0]
    large = (lo <= 1 + tol) & (vv >= 1 - tol)
    strict = (lo <= 1 - tol) & (vv >= 1 + tol)
    np.fill_diagonal(large, False)
    np.fill_diagonal(strict, False)
    return ([set(np.nonzero(large[r])[0]) for r in range(n)],
            [set(np.nonzero(strict[r])[0]) for r in range(n)])


def omega_deux(rho, thd, delta, tol=TOL):
    """(omega strict, omega large)."""
    offsets, lo, vv = matrices(rho, thd, delta)
    al, as_ = adjacences(lo, vv, tol)
    return echelle.clique_max_avec0(as_)[0], echelle.clique_max_avec0(al)[0]


def adjacence(rho, thd, delta, convention="large", tol=TOL):
    offsets, lo, vv = matrices(rho, thd, delta)
    al, as_ = adjacences(lo, vv, tol)
    return offsets, (al if convention == "large" else as_)


if __name__ == "__main__":
    import json
    exact = json.load(open("exact_tangence.json"))
    print("juge exact vs calcul flottant (tolerance 1e-12) :")
    CAS = [("hexagonal (60 deg)", 1.0, 60, ["3/10", "1/2", "7/10", "9/10"]),
           ("carre (90 deg)", 1.0, 90, ["3/10", "1/2", "7/10", "9/10"]),
           ("rectangle 2:1 (90 deg)", 2.0, 90, ["2/5", "1/2", "7/10", "49/50"])]
    import fractions
    ok = 0; tot = 0
    for nom, rho, th, deltas in CAS:
        for ds in deltas:
            d = float(fractions.Fraction(ds))
            ws, wl = omega_deux(rho, th, d)
            ref = exact.get(f"{nom}|{ds}")
            tot += 1
            good = (ref == wl)
            ok += good
            print(f"  {nom:24s} delta={d:.3f} : strict {ws} | large {wl} | exact {ref} "
                  f"{'ok' if good else 'ECART'}{'' if ws == wl else '   (convention decide)'}")
    print(f"  => {ok}/{tot} valeurs conformes au juge exact")
    print("\nla convention change-t-elle la valeur ? echantillon large :")
    import random
    rnd = random.Random(2)
    diff = 0
    for _ in range(40):
        rho = rnd.uniform(1.0, 2.0); th = rnd.uniform(60, 120); d = rnd.choice([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.98])
        ws, wl = omega_deux(rho, th, d)
        if ws != wl:
            diff += 1
            print(f"  ({rho:.3f},{th:.1f},{d}) : strict {ws} / large {wl}")
    print(f"  {diff} cas sur 40 ou la convention decide")
