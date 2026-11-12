/-
  geom/Axiomes — AUDIT, GÉNÉRÉ par note/gen_axiomes.py. Ne pas éditer à la main.

  Un `#print axioms` par théorème déclaré dans Geometrie, Pont, Queue, Boites.
  Ce fichier ne définit rien et ne prouve rien : il DEMANDE à Lean, pour chaque théorème,
  la liste de ses axiomes. Le but est qu'aucun théorème du dossier ne reste non interrogé —
  un théorème qui compile sans qu'on connaisse ses axiomes n'est pas un résultat vérifié.

  Attendu pour chacun : [propext, Classical.choice, Quot.sound], ou un sous-ensemble
  (le projet sans Mathlib ne rend que [propext, Quot.sound]).
-/


import Geometrie
import Pont
import Queue
import Boites

/- Geometrie : 17 théorème(s) -/
#print axioms Geometrie.dist_le_dist_iff
#print axioms Geometrie.cellule_convexe
#print axioms Geometrie.dist_sub_left
#print axioms Geometrie.cellule_translate
#print axioms Geometrie.conflit_translation
#print axioms Geometrie.conflit_symm
#print axioms Geometrie.conflit_iff_zero
#print axioms Geometrie.isPreconnected_dist_set
#print axioms Geometrie.existe_paire_distance_un
#print axioms Geometrie.conflit_iff_encadrement
#print axioms Geometrie.mem_Lint
#print axioms Geometrie.centre_mem_cellule
#print axioms Geometrie.conflit_vecteur_unitaire
#print axioms Geometrie.cellule_Lint_le
#print axioms Geometrie.cellule_Lint_ge
#print axioms Geometrie.controle_negatif
#print axioms Geometrie.controle_negatif_encadrement

/- Pont : 6 théorème(s) -/
#print axioms Pont.lemmeB
#print axioms Pont.pont_coloriage
#print axioms Pont.pont_interieurs
#print axioms Pont.pont_echelle
#print axioms Pont.lemmeB_sans_dmin_lt_dmax_est_faux
#print axioms Pont.temoin_naif_echoue

/- Queue : 28 théorème(s) -/
#print axioms Queue.continuous_dist2
#print axioms Queue.isPreconnected_dist2_set
#print axioms Queue.tangence
#print axioms Queue.mem_Reseau
#print axioms Queue.zero_mem
#print axioms Queue.sub_mem
#print axioms Queue.centre_mem
#print axioms Queue.cell_iff
#print axioms Queue.cell_convex
#print axioms Queue.centre_in_cell
#print axioms Queue.abs_step
#print axioms Queue.int_abs_le_sq
#print axioms Queue.segment_mem
#print axioms Queue.ceil_ge
#print axioms Queue.ceil_lt
#print axioms Queue.pas_borne
#print axioms Queue.proche_eps
#print axioms Queue.loin_eps
#print axioms Queue.cent_un
#print axioms Queue.dist2_smul'
#print axioms Queue.dist2_axe
#print axioms Queue.dist2_segment
#print axioms Queue.ecart_sq
#print axioms Queue.close_ineq
#print axioms Queue.far_ineq
#print axioms Queue.mem_segment
#print axioms Queue.queue
#print axioms Queue.sept_couleurs

/- Boites : 4 théorème(s) -/
#print axioms Boites.clique_de_temoins
#print axioms Boites.contrainte_auto
#print axioms Boites.cell_iff_translate
#print axioms Boites.cell_of_fini

/- Total interrogé : 55 théorème(s). -/
