"""Génère les fichiers `Axiomes.lean` : un `#print axioms` par théorème, sans exception.

Pourquoi ce fichier existe
--------------------------
Le dossier annonce « 66 théorèmes, 0 sorry », et les journaux du 03/11 citent des axiomes. Mais
les `#print axioms` sont répartis dans les fichiers de preuve et n'en couvrent qu'une partie :
`Queue.lean` déclare 28 théorèmes et n'en interroge que 5. Un théorème non interrogé compile,
et c'est tout ce qu'on sait de lui. Ces fichiers d'audit ne prouvent rien de nouveau : ils
DEMANDENT, pour chacun des 70 théorèmes, la liste exacte de ses axiomes.

Deux fichiers, parce que les deux projets sont séparés (toolchains différentes, l'un avec
Mathlib, l'autre sans) :
  dossiers/geom/Axiomes.lean   17 + 6 + 28 + 4 = 55 théorèmes
  dossiers/lean/Axiomes.lean    6 + 4 + 5      = 15 théorèmes
                                 total          70

Usage : python3 gen_axiomes.py
"""
import re
import sys

GEOM = [("Geometrie", "Geometrie.lean"), ("Pont", "Pont.lean"),
        ("Queue", "Queue.lean"), ("Boites", "Boites.lean")]
LEAN = [("Plafond", "Plafond.lean"), ("T8", "T8.lean"), ("Pont", "Pont.lean")]

RACINE = "/home/user/Recherches-maths/dossiers"


def noms_qualifies(chemin):
    """Noms complets (namespace inclus) des `theorem` déclarés, dans l'ordre du fichier."""
    ns, noms = [], []
    for ligne in open(chemin).read().splitlines():
        m = re.match(r"^namespace (\S+)", ligne)
        if m:
            ns.append(m.group(1))
            continue
        if re.match(r"^end\b", ligne) and ns:
            ns.pop()
            continue
        m = re.match(r"^theorem (\S+)", ligne)
        if m:
            noms.append(".".join(ns + [m.group(1)]))
    return noms


def ecrit(dossier_sortie, modules, chemin, outil):
    lignes = [f"""/-
  {outil} — AUDIT, GÉNÉRÉ par note/gen_axiomes.py. Ne pas éditer à la main.

  Un `#print axioms` par théorème déclaré dans {", ".join(m for m, _ in modules)}.
  Ce fichier ne définit rien et ne prouve rien : il DEMANDE à Lean, pour chaque théorème,
  la liste de ses axiomes. Le but est qu'aucun théorème du dossier ne reste non interrogé —
  un théorème qui compile sans qu'on connaisse ses axiomes n'est pas un résultat vérifié.

  Attendu pour chacun : [propext, Classical.choice, Quot.sound], ou un sous-ensemble
  (le projet sans Mathlib ne rend que [propext, Quot.sound]).
-/
"""]
    lignes.append("")
    for module, fichier in modules:
        lignes.append(f"import {fichier[:-5]}")
    total = 0
    for module, fichier in modules:
        noms = noms_qualifies(f"{RACINE}/{dossier_sortie}/{fichier}")
        lignes.append("")
        lignes.append(f"/- {module} : {len(noms)} théorème(s) -/")
        for n in noms:
            lignes.append(f"#print axioms {n}")
        total += len(noms)
    lignes.append("")
    lignes.append(f"/- Total interrogé : {total} théorème(s). -/")
    open(f"{RACINE}/{dossier_sortie}/Axiomes.lean", "w").write("\n".join(lignes) + "\n")
    return total


if __name__ == "__main__":
    n1 = ecrit("geom", GEOM, "Axiomes.lean", "geom/Axiomes")
    n2 = ecrit("lean", LEAN, "Axiomes.lean", "lean/Axiomes")
    print(f"écrit geom/Axiomes.lean  : {n1} #print axioms")
    print(f"écrit lean/Axiomes.lean  : {n2} #print axioms")
    print(f"TOTAL interrogé          : {n1 + n2}")
    sys.exit(0)
