"""Pont entre le moteur Rust `gabarit` et le certificat Python.

Le certificat symbolique (repère w = 1/h, encadrements d'intervalles) reste en Python :
c'est lui qui *prouve*. Le Rust ne fait que **choisir les témoins** : il produit le motif
(clique d'offsets, paires de contraintes tendues, milieux de Delaunay) au centre d'une boîte,
en temps constant en h. C'est exactement le goulot qu'on cherchait à desserrer.

Le format renvoyé est celui de `audit_certificat3.motif_queue`, si bien que
`audit_certificat3.plan_de` et `certifie_w` s'en servent sans modification.
"""
import json
import subprocess
from fractions import Fraction as F
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
BIN = RACINE / "rust" / "gabarit" / "target" / "release" / "gabarit"


def disponible():
    return BIN.exists()


def motif_rust(gc, hc, ech, want=9, timeout=60):
    """Motif calculé par le moteur Rust, au format de `C3.motif_queue`."""
    if not disponible():
        raise RuntimeError(f"binaire absent : {BIN} (cargo build --release)")
    cmd = [str(BIN), "run", "--g", str(F(gc)), "--h", str(F(hc)), "--eps", str(F(ech)),
           "--want", str(want), "--json"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1][:200] if (r.stderr or r.stdout) else "échec")
    js = json.loads(r.stdout)
    return {
        "paires": [tuple(tuple(int(t) for t in pa) for pa in x) for x in js["paires"]],
        "clique": [tuple(int(t) for t in x) for x in js["clique"]],
        "omega": int(js["omega"]),
        "mids": [tuple(int(t) for t in x) for x in js["mids"]],
        "pts_mid": {tuple(int(t) for t in k.split(",")): (F(v[0]), F(v[1]))
                    for k, v in js["pts_mid"].items()},
        "pts_centre": [(F(x[0]), F(x[1])) for x in js["pts_centre"]],
        "centre": (F(gc), F(hc)),
        "n_sommets": int(js["n_sommets"]),
    }


def controle(gc, hc, ech, want=9):
    """Contrôle de bout en bout : motif Rust + certificat Python."""
    import audit_certificat3 as C3
    mot = motif_rust(gc, hc, ech, want)
    plan = C3.plan_de(mot, F(ech))
    r = C3.certifie_w(plan, (F(gc), F(gc)), (1 / F(hc), 1 / F(hc)), F(ech))
    return mot, r


if __name__ == "__main__":
    from fractions import Fraction as F
    print("binaire :", BIN, "| présent :", disponible())
    for gc, hc, ech in [(F(0), F(21, 2), F(99, 100)), (F(1, 4), F(20), F(99, 100)),
                        (F(-1, 2), F(1), F(99, 100))]:
        mot = motif_rust(gc, hc, ech)
        print(f"g={gc}, h={hc} : clique {len(mot['clique'])}, "
              f"{len(mot['mids'])} milieux, {len(mot['paires'])} sommets")
