"""CONTRE-EXEMPLE : un temoin du certificat sort de sa cellule a l'interieur de SA PROPRE boite.

Le certificat verifie l'appartenance d'un point a la cellule en evaluant, en arithmetique
d'intervalles, la quantite  <p,v> - |v|^2/2  ou v = i*b1 + j*b2 depend de (rho, theta).
Les deux termes dependent des MEMES variables : l'intervalle obtenu pour
   sup<p,v> - inf(|v|^2/2)
n'est pas un majorant serre de la quantite reelle... il en est un majorant, mais tres lache,
et le code du certificat prend la borne HAUTE de la difference des intervalles, qui peut etre
INFERIEURE a la vraie valeur (intervalle retourne). Resultat : un temoin peut sortir de la
cellule sans que le test le voie.

Ce script evalue la quantite aux QUATRE COINS de la boite, en arithmetique rationnelle
rigoureuse, et cherche les cas ou elle est PROUVE positive : le temoin est alors dehors.
"""
import gzip
import json
from fractions import Fraction as F
import verif_exacte as V

def f_corner(p, ij, rho, th_deg, borne="lo"):
    """<p,v> - |v|^2/2 au coin (rho, theta), encadre en arithmetique rationnelle."""
    a = V.rnd((F(th_deg) * V.PI_LO / 180, F(th_deg) * V.PI_HI / 180))
    c = V.cos_iv(a[0], a[1]) if a[0] >= 0 else None
    s = V.sin_iv(a[0], a[1])
    r = V.rnd((F(rho), F(rho)))
    bx, by = V.mul(r, c), V.mul(r, s)          # v = i*b1 + j*b2, b1=(1,0)
    i, j = ij
    vx = V.add(V.I(F(i)), V.scale(j, bx))
    vy = V.scale(j, by)
    val = V.sub(V.add(V.mul(V.I(F(p[0])), vx), V.mul(V.I(F(p[1])), vy)),
                V.scale(F(1, 2), V.norm2(vx, vy)))
    return val[0] if borne == "lo" else val[1]

def main():
    rec = json.loads(gzip.open("certificat_temoins_echantillon.jsonl.gz","rt").readline())
    (rho0, rho1), (th0, th1) = rec["r"], rec["t"]
    gen = [(F(p[0]), F(p[1])) for p in rec["tem"]["gen"]]
    A = [tuple(o) for o in rec["tem"]["A"]]
    print(f"boite = rho [{rho0}, {rho1}] x theta [{th0}, {th1}] ; {len(gen)} temoins ; A = {A}")
    coins = [(rho0, th0), (rho0, th1), (rho1, th0), (rho1, th1)]
    pires = []
    n_viol = 0
    for gi, p in enumerate(gen):
        for ij in A:
            lb = max(f_corner(p, ij, r, t, "lo") for (r, t) in coins)
            if lb > 0:
                n_viol += 1
                pires.append((float(lb), gi, ij, p))
    pires.sort(reverse=True)
    print(f"\npaires (temoin, contrainte) PROUVEES violEES a un coin : {n_viol} / {len(gen)*len(A)}")
    for (lb, gi, ij, p) in pires[:6]:
        print(f"  temoin #{gi} = ({float(p[0]):.6f}, {float(p[1]):.6f}) contrainte {ij} : "
              f"valeur >= {lb:.3e} > 0")
    if pires:
        lb, gi, ij, p = pires[0]
        print(f"\nLe temoin #{gi} est donc DEHORS de la cellule au coin concerne : le certificat")
        print("de cette boite ne vaut pas, alors que le fichier le classe 'certifie'.")
        print("Attendu : un temoin valide a une valeur <= 0 partout dans la boite.")
        json.dump({"boite": rec["r"] + rec["t"], "n_violations": n_viol,
                   "exemples": [{"temoin": [float(x) for x in p], "contrainte": list(ij),
                                 "valeur_min": str(lb)} for (lb, gi, ij, p) in pires[:20]]},
                  open("contre_exemple.json", "w"), ensure_ascii=False, indent=1)
    return n_viol

if __name__ == "__main__":
    main()
