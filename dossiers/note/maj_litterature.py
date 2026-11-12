#!/usr/bin/env python3
"""Met à jour le dossier après l'étape 1 (littérature). Idempotent.

Corrections factuelles portées :
  1. Sokolov–Voronov : publié (Discrete Math. 349(12), 2026, art. 115321) — plus « prépublication non validée ».
  2. Manta : énoncé du théorème 2.2 = degré >= 4 (et non 5) ; publié Discrete Math. 344(7), 2021.
  3. Coulson 2004 : deux énoncés distincts (>= 6 polygones ; >= 7 réseau-sous-réseau).
  4. Ajout de Dutour Sikirić–Madore–Moustrou–Vallentin 2021 (l'objet « colorier la tessellation de Voronoï d'un réseau »).
  5. verdict_etape1 : le champ n'est pas libre.
"""
import json, pathlib, datetime

BASE = pathlib.Path(__file__).resolve().parent.parent
TODO = BASE / "todo-hadwiger-nelson.json"
CHG = BASE / "note" / "CHANGELOG.md"

d = json.loads(TODO.read_text(encoding="utf-8"))
src = d["sources_externes"]

def upsert(url, sujet, apport, statut):
    for e in src:
        if e["url"] == url:
            e.update({"sujet": sujet, "apport": apport, "statut": statut})
            return "maj"
    src.append({"sujet": sujet, "url": url, "apport": apport, "statut": statut})
    return "ajout"

journal = []
journal.append(upsert(
    "https://doi.org/10.1016/j.disc.2026.115321",
    "cartes polygonales >= 7",
    "Sokolov-Voronov, « On the chromatic number of the plane for map-type colorings », "
    "Discrete Mathematics 349(12), déc. 2026, art. 115321 (arXiv:2502.01958). "
    "Thm 1 : >= 7 pour un coloriage de type carte sans arc de cercle unité sur les bords et trois bords par sommet ; "
    "Cor. 1 : cas cubique (exactement trois arêtes par sommet) ; Thm 2 : chi_poly(R^2) = 7. "
    "PUBLIÉ (révision du 03/11/2026 : ce n'est plus une prépublication).",
    "publie ; preuve contestée par une revue automatique (pith.science, 09/08/2026 : 5 objections majeures), non vérifiée par nous"))
journal.append(upsert(
    "https://arxiv.org/pdf/1909.02708",
    "polygones : degré >= 4 => >= 7 couleurs",
    "Manta, « Triangle colorings require at least seven colors », Discrete Math. 344(7), 2021, art. 112411. "
    "Thm 2.2 : un sommet de degré >= 4 impose >= 7 couleurs ; Thm 2.3 : les coloriages triangulaires exigent 7. "
    "Cas laissé ouvert : tous les sommets de degré <= 3 (section 6). NB : la preuve discute d'abord un sommet de "
    "degré 5 ; notre dossier disait « degré >= 5 », c'est l'énoncé du théorème (>= 4) qui fait foi.",
    "publie"))
journal.append(upsert(
    "https://www.cambridge.org/core/journals/journal-of-the-australian-mathematical-society/article/on-the-chromatic-number-of-plane-tilings/",
    "Coulson 2004 : deux énoncés à ne pas confondre",
    "Coulson, J. Austral. Math. Soc. 77 (2004), 191-196. (a) >= 6 couleurs pour des tuiles polygonales convexes "
    "d'aire minorée ; (b) « any lattice-sublattice colouring scheme for R^2 must use at least 7 colours to have "
    "an excluded distance ». L'énoncé (b) porte sur la sous-classe des coloriages par classes d'un sous-réseau, "
    "plus restrictive que la nôtre : il n'implique pas notre cas, mais il occupe le terrain « réseau + 7 » dès 2004.",
    "publie"))
journal.append(upsert(
    "https://arxiv.org/abs/1907.09751",
    "colorier la tessellation de Voronoï d'un réseau (objet déjà nommé)",
    "Dutour Sikirić, Madore, Moustrou, Vallentin, « Coloring the Voronoi tessellation of lattices », "
    "J. London Math. Soc. 2021. Définit chi(Lambda) = chromatique du graphe de Cayley sur les vecteurs de Voronoï "
    "stricts (cellules partageant une FACETTE). Valeurs : Z^n 2, A_n = A_n* n+1, D_n* 4, E6 9, E7 14, E8 16, "
    "Lambda24 4096 ; chi(A2) = 3. À ne pas confondre avec notre omega (adjacence par distance 1) : notre graphe "
    "contient le leur.",
    "publie"))

d["verdict_etape1_litterature"] = {
    "date": "2026-11-03",
    "question": "la cible T (réseaux à cellules hexagonales => omega >= 7) est-elle nouvelle ?",
    "verdict": "NON — le champ n'est pas libre",
    "raisons": [
        "La conclusion (chi >= 7 pour ces pavages) est impliquée par le théorème 2 de Sokolov–Voronov "
        "(chi_poly(R^2) = 7), publié en 2026 : aucun coloriage polygonal à 6 couleurs du plan n'existe, "
        "donc aucun coloriage à 6 couleurs des cellules de nos réseaux.",
        "L'ingrédient « réseau » était déjà à 7 chez Coulson (2004) pour les schémas réseau-sous-réseau.",
        "L'objet « colorier la tessellation de Voronoï d'un réseau » est déjà nommé et calculé "
        "(Dutour Sikirić et al. 2021), pour une adjacence par facette.",
    ],
    "ce_qui_reste_non_couvert": [
        "L'énoncé de CLIQUE (omega >= 7 avec témoin explicite) n'est pas impliqué par chi >= 7 : "
        "un graphe 7-chromatique peut n'avoir que des triangles. Mais un témoin de taille 7 pour une famille "
        "de réseaux est un calcul, pas un théorème.",
        "Le paysage quantitatif omega(rho, theta, delta) et les seuils delta*(Lambda) : non tabulés à ma "
        "connaissance — note de calcul, pas découverte.",
        "Le cas degré <= 3 des pavages NON-réseaux (trou laissé par Manta) et la question 2 de S-V "
        "(arcs de cercle unité + sommets trichromatiques de degré > 3) : ouverts, mais hors de portée de "
        "nos outils (sans translation, pas de graphe de Cayley).",
    ],
    "suites_proposees": [
        {"id": "A", "titre": "audit adverse de la preuve SV sur la tranche réseaux",
         "apport": "décision par calcul exact d'un cas d'un théorème publié mais contesté", "cout": "2-3 seances"},
        {"id": "B", "titre": "publier la mesure : paysage omega et seuils delta*(Lambda)",
         "apport": "table de référence, honnête et modeste", "cout": "1-2 seances"},
        {"id": "C", "titre": "sortir des réseaux (cas degré <= 3 non-réseau)",
         "apport": "seule voie vers une vraie découverte", "cout": "semaines-mois, incertain"},
    ],
    "artefact": "dossiers/note/etape1-litterature.md",
    "interdit": "aucune revendication sur chi(R^2) ; ne pas présenter la cible T comme nouvelle",
}
d["mis_a_jour"] = "2026-11-03"
TODO.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
json.loads(TODO.read_text(encoding="utf-8"))  # relecture : le fichier doit rester du JSON valide
print("todo-hadwiger-nelson.json :", ", ".join(f"{j} ({len(src)} sources)" for j in journal))

entree = """
## Geste 18 — étape 1 du chemin de découverte : la littérature (03/11/2026, soir)

**Question** : la cible T (réseaux à cellules hexagonales ⇒ ω ≥ 7) est-elle une découverte disponible ?
**Verdict** : non. Le champ n'est pas libre.

- Sokolov–Voronov n'est plus un preprint : *Discrete Mathematics* **349**(12), déc. 2026, art. 115321.
  Leur théorème 2 (χ_poly(ℝ²) = 7) **subsume** notre conclusion ; leur corollaire 1 (cas cubique) couvre le
  cas trivalent que Manta laissait ouvert. Publication ≠ validité : preuve contestée (revue automatique
  du 09/08/2026, 5 objections majeures), non vérifiée par nous.
- Coulson (2004) donnait déjà ≥ 7 pour tout schéma réseau-sous-réseau — terrain « réseau + 7 » occupé depuis 22 ans.
- Dutour Sikirić–Madore–Moustrou–Vallentin (JLMS 2021) ont déjà nommé et calculé l'objet « colorier la
  tessellation de Voronoï d'un réseau », pour l'adjacence par **facette** (χ(A₂) = 3 ; notre ω vaut 7–10 :
  ce sont deux paramètres différents, ne jamais les confondre).

**Corrections portées au dossier** : statut de S-V (5 fichiers HTML + biblio de `note-reseaux.html`),
énoncé de Manta (degré ≥ 4 et non 5), les deux moitiés du résumé de Coulson, ajout de Dutour et al. 2021.
**Ce qui reste** : la clé de voûte clique/chromatique, le paysage quantitatif, et le cas degré ≤ 3 non-réseau.
**Artefact** : `note/etape1-litterature.md`.
"""
cur = CHG.read_text(encoding="utf-8")
if "## Geste 18" in cur:
    print("CHANGELOG.md : geste 18 déjà présent (rien à faire)")
else:
    CHG.write_text(cur.rstrip() + "\n" + entree, encoding="utf-8")
    print("CHANGELOG.md : geste 18 ajouté")
