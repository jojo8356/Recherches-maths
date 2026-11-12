"""Met à jour CHANGELOG + todo après la séance 1 de l'audit S-V. Idempotent."""
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent
CHG = BASE / "note" / "CHANGELOG.md"
TODO = BASE / "todo-hadwiger-nelson.json"

ENTREE = """
## Geste 19 — audit S-V, séance 1 (03/11/2026, nuit)

Décision : auditer la tranche « réseaux » du théorème 2 de Sokolov–Voronov par calcul exact,
en visant une **clique de 7** (plus fort, dans sa forme, qu'une borne sur χ).

Trois corrections structurelles, toutes nées du travail et non de la relecture :

1. **Le domaine de T7 était faux.** [1,2]×[60°,120°] n'est pas un domaine fondamental : les
   réseaux anisotropes (ρ > 2) en sortent, et ils sont hexagonaux donc concernés. Domaine correct
   en coordonnée de module τ = g + ih : |g| ≤ 1/2, g²+h² ≥ 1, h > 0.
2. **L'arithmétique transcendante était inutile.** En (g,h) toute la géométrie est rationnelle
   (det des systèmes 2×2 = h·(entier)). La couche Machin/Taylor–Lagrange — celle qui a produit la
   rétractation — disparaît par changement de paramétrage.
3. **Règle de comparaison.** Pour une condition serrée, jamais deux encadrements comparés :
   une seule fonction différence ≥ 0. C'est exactement ce que T7 violait.

Deux fautes de ma part, attrapées en route : encadrement d'une expression identiquement nulle
(256/256 boîtes tombaient) et troncature de la récursion de la forme de la moyenne — une troncature
de Taylor n'est pas un encadrement. Vitesse : 74 ms/boîte après compilation des dérivées.

État : certificat sain, 3/3 contrôles négatifs, couverture PARTIELLE (transitions combinatoires et
queue h → ∞ non traitées). Aucun énoncé nouveau sur χ(ℝ²). Voir `dossiers/audit-sv.html`.
"""

cur = CHG.read_text(encoding="utf-8")
if "## Geste 19" in cur:
    print("CHANGELOG : geste 19 déjà présent")
else:
    CHG.write_text(cur.rstrip() + "\n" + ENTREE, encoding="utf-8")
    print("CHANGELOG : geste 19 ajouté")

d = json.loads(TODO.read_text(encoding="utf-8"))
d["audit_sv"] = {
    "direction": "A — audit de la preuve publiée sur la tranche réseaux",
    "seance": 1,
    "date": "2026-11-03",
    "enonce_vise": "pour tout réseau Λ à cellules hexagonales, à l'échelle ε = 99/100, "
                   "ω(Λ,ε) ≥ 7 (donc χ ≥ 7)",
    "acquis": [
        "domaine correct : |g| ≤ 1/2, g²+h² ≥ 1, h > 0 dans τ = g+ih (le rectangle de T7 ratait les anisotropes)",
        "géométrie rationnelle exacte en (g,h) : plus aucune trigonométrie d'intervalles",
        "règle : jamais deux encadrements comparés, une seule fonction différence ≥ 0",
        "moteur exact validé : carré 9, A2 7, τ=20i 11 ; balayage 8349 réseaux, min ω = 7, aucun sous 7",
        "certificat par boîtes : 74 ms/boîte, boîtes de côté 0.04, 3/3 contrôles négatifs",
        "couverture partielle : g ∈ [-1/2,-1/4] × h ∈ [0.9,1.2] entièrement certifiée",
    ],
    "non_acquis": [
        "transitions combinatoires : droite g = 0 (cellules rectangulaires, 4 sommets), |g| = 1/2, courbes de Delaunay",
        "queue h → ∞ (réseaux très anisotropes) : argument asymptotique à écrire",
        "couverture complète du domaine → l'audit N'EST PAS conclu",
    ],
    "controles_negatifs": [
        {"cas": "ε = 1/2", "attendu": "refus", "obtenu": "refus (ω = 6 < 7)"},
        {"cas": "témoin éloigné pris pour témoin proche", "attendu": "refus", "obtenu": "refus (F min = -3.38)"},
        {"cas": "boîte hors domaine", "attendu": "refus", "obtenu": "refus"},
    ],
    "scripts": ["note/audit_domaine2.py", "note/audit_gh.py", "note/poly2.py", "note/audit_certificat2.py"],
    "artefact": "dossiers/audit-sv.html",
    "prochaine_seance": "transitions + queue h→∞, puis énoncé final de la tranche et rédaction",
}
d["mis_a_jour"] = "2026-11-03"
etapes = d.setdefault("prochaines_etapes", [])
if not any(e.get("id") == "T0-audit-sv" for e in etapes):
    etapes.insert(0, {"id": "T0-audit-sv", "statut": "en_cours", "priorite": 1,
                      "titre": "Audit S-V, séance 2 : transitions et queue anisotrope",
                      "pourquoi": "seule voie vers un énoncé complet sur la tranche réseaux, "
                                  "indépendant de la preuve contestée",
                      "sortie": "couverture complète du domaine des modules, puis audit rédigé"})
    print("todo : étape T0-audit-sv insérée")
else:
    print("todo : étape T0-audit-sv déjà présente")
TODO.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
json.loads(TODO.read_text(encoding="utf-8"))
print("todo JSON relu : valide")
