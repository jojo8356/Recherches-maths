/-
  lean/Axiomes — AUDIT, GÉNÉRÉ par note/gen_axiomes.py. Ne pas éditer à la main.

  Un `#print axioms` par théorème déclaré dans Plafond, T8, Pont.
  Ce fichier ne définit rien et ne prouve rien : il DEMANDE à Lean, pour chaque théorème,
  la liste de ses axiomes. Le but est qu'aucun théorème du dossier ne reste non interrogé —
  un théorème qui compile sans qu'on connaisse ses axiomes n'est pas un résultat vérifié.

  Attendu pour chacun : [propext, Classical.choice, Quot.sound], ou un sous-ensemble
  (le projet sans Mathlib ne rend que [propext, Quot.sound]).
-/


import Plafond
import T8
import Pont

/- Plafond : 6 théorème(s) -/
#print axioms Plafond.injectif_sur_clique
#print axioms Plafond.somme_le
#print axioms Plafond.plafond_cinq
#print axioms Plafond.cinq_compatible
#print axioms Plafond.aucun_plafond_six
#print axioms Plafond.aucun_plafond_six_general

/- T8 : 4 théorème(s) -/
#print axioms T8.P.ext
#print axioms T8.P.voisin_translation
#print axioms T8.P.recentrage
#print axioms T8.P.existe_clique_par_zero

/- Pont : 5 théorème(s) -/
#print axioms Pont.lemmeB
#print axioms Pont.eps_force_D_lt_dmax
#print axioms Pont.lemmeB_eps
#print axioms Pont.lemmeA_geometrique
#print axioms Pont.pas_meme_couleur

/- Total interrogé : 15 théorème(s). -/
