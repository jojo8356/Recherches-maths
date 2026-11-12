/-
  Geometrie.lean — la géométrie de T8, formalisée (Lean 4 + Mathlib)

  Objets : réseau (sous-groupe additif de ℝ²), cellule de Voronoï d'un point du réseau,
  relation de conflit « deux cellules portent un segment de longueur 1 », convexité,
  et invariance par translation.

  Le théorème central est `conflit_translation` : la relation de conflit ne dépend que de la
  DIFFÉRENCE des deux points du réseau. C'est ce qui fait du graphe de conflit un graphe de
  Cayley, donc ce qui autorise le calcul exact de ω en ne cherchant que les cliques passant
  par 0 (T8, `echelle.clique_max_avec0`). Sans ce lemme, ce calcul serait une fenêtre.
-/
import Mathlib.Analysis.Convex.Topology
import Mathlib.Topology.Order.IntermediateValue
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Topology.MetricSpace.Basic

open Set
open scoped InnerProductSpace

namespace Geometrie

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-! ## 1. Cellule de Voronoï et convexité -/

/-- **Cellule de Voronoï** d'un point `v` pour le réseau `L` : l'ensemble des points du plan
au moins aussi proches de `v` que de tout autre point du réseau. -/
def cellule (L : AddSubgroup E) (v : E) : Set E :=
  {x | ∀ w ∈ L, dist x v ≤ dist x w}

/-- Réécriture clé : l'inégalité de distance est une inégalité **linéaire** en `x`.
C'est ce qui fait d'une cellule de Voronoï une intersection de demi-espaces. -/
theorem dist_le_dist_iff (x v w : E) :
    dist x v ≤ dist x w ↔ 2 * ⟪x, w - v⟫_ℝ ≤ ‖w‖ ^ 2 - ‖v‖ ^ 2 := by
  rw [dist_eq_norm, dist_eq_norm, inner_sub_right]
  constructor
  · intro h
    have h2 : ‖x - v‖ ^ 2 ≤ ‖x - w‖ ^ 2 :=
      pow_le_pow_left₀ (norm_nonneg _) h 2
    rw [norm_sub_sq_real, norm_sub_sq_real] at h2
    nlinarith
  · intro h
    have h2 : ‖x - v‖ ^ 2 ≤ ‖x - w‖ ^ 2 := by
      rw [norm_sub_sq_real, norm_sub_sq_real]
      nlinarith
    exact (pow_le_pow_iff_left₀ (norm_nonneg _) (norm_nonneg _) (by norm_num : (2 : ℕ) ≠ 0)).mp h2

/-- Une cellule de Voronoï est une intersection de demi-espaces, donc un convexe.
C'est l'hypothèse « cellules convexes » utilisée partout dans les notes. -/
theorem cellule_convexe (L : AddSubgroup E) (v : E) : Convex ℝ (cellule L v) := by
  have hEq : cellule L v = ⋂ w ∈ L, {x : E | dist x v ≤ dist x w} := by
    ext x
    simp [cellule]
  rw [hEq]
  refine convex_iInter₂ (fun w _ => ?_)
  have hset : {x : E | dist x v ≤ dist x w}
      = {x : E | 2 * ⟪x, w - v⟫_ℝ ≤ ‖w‖ ^ 2 - ‖v‖ ^ 2} := by
    ext x
    exact dist_le_dist_iff x v w
  rw [hset]
  have hlin : IsLinearMap ℝ (fun y : E => (2 : ℝ) * ⟪y, w - v⟫_ℝ) := by
    refine ⟨?_, ?_⟩
    · intro a b
      simp only [inner_add_left, mul_add]
    · intro c a
      simp [inner_smul_left, mul_comm, mul_assoc]
  exact convex_halfSpace_le (𝕜 := ℝ) hlin (‖w‖ ^ 2 - ‖v‖ ^ 2)

/-! ## 2. Invariance par translation -/

omit [InnerProductSpace ℝ E] in
/-- Distance et translation : `dist (x - t) a = dist x (a + t)`. -/
theorem dist_sub_left (x t a : E) : dist (x - t) a = dist x (a + t) := by
  rw [dist_eq_norm, dist_eq_norm]
  congr 1
  abel

omit [InnerProductSpace ℝ E] in
/-- **La cellule se translate avec son point.** Si `t` est dans le réseau, la cellule de
`v + t` est la translatée de celle de `v`. -/
theorem cellule_translate (L : AddSubgroup E) {t : E} (ht : t ∈ L) (v : E) :
    cellule L (v + t) = (fun x => x + t) '' cellule L v := by
  ext x
  constructor
  · intro hx
    refine ⟨x - t, ?_, by abel⟩
    intro w hw
    have h1 := hx (w + t) (L.add_mem hw ht)
    rw [← dist_sub_left x t v, ← dist_sub_left x t w] at h1
    exact h1
  · rintro ⟨y, hy, rfl⟩
    intro w hw
    have hwt : w - t ∈ L := L.sub_mem hw ht
    have h1 := hy (w - t) hwt
    have e1 : dist (y + t) (v + t) = dist y v := by
      rw [dist_eq_norm, dist_eq_norm]; congr 1; abel
    have e2 : dist (y + t) w = dist y (w - t) := by
      rw [dist_eq_norm, dist_eq_norm]; congr 1; abel
    rw [e1, e2]
    exact h1

/-! ## 3. Le conflit ne dépend que de la différence -/

/-- **Conflit** entre deux cellules : il existe un segment de longueur 1 joignant un point
de l'une à un point de l'autre. C'est la relation dont le code calcule la fermeture
transitive par cliques. -/
def Conflit (L : AddSubgroup E) (v w : E) : Prop :=
  ∃ p ∈ cellule L v, ∃ q ∈ cellule L w, dist p q = 1

omit [InnerProductSpace ℝ E] in
/-- **Théorème central de T8.** La relation de conflit est invariante par translation le long
du réseau : elle ne dépend que de la différence `w - v`. Donc le graphe de conflit est un
graphe de Cayley sur `L`, sommet-transitif, et chercher les cliques passant par 0 ne perd
aucune clique. -/
theorem conflit_translation (L : AddSubgroup E) {t : E} (ht : t ∈ L) (v w : E) :
    Conflit L (v + t) (w + t) ↔ Conflit L v w := by
  constructor
  · rintro ⟨p, hp, q, hq, hd⟩
    rw [cellule_translate L ht v] at hp
    rw [cellule_translate L ht w] at hq
    obtain ⟨p', hp', rfl⟩ := hp
    obtain ⟨q', hq', rfl⟩ := hq
    refine ⟨p', hp', q', hq', ?_⟩
    have e : dist (p' + t) (q' + t) = dist p' q' := by
      rw [dist_eq_norm, dist_eq_norm]; congr 1; abel
    rw [e] at hd
    exact hd
  · rintro ⟨p, hp, q, hq, hd⟩
    refine ⟨p + t, ?_, q + t, ?_, ?_⟩
    · rw [cellule_translate L ht v]
      exact mem_image_of_mem _ hp
    · rw [cellule_translate L ht w]
      exact mem_image_of_mem _ hq
    · have e : dist (p + t) (q + t) = dist p q := by
        rw [dist_eq_norm, dist_eq_norm]; congr 1; abel
      rw [e]; exact hd

omit [InnerProductSpace ℝ E] in
omit [InnerProductSpace ℝ E] in
/-- **Le conflit est symétrique** (la distance l'est). -/
theorem conflit_symm (L : AddSubgroup E) (v w : E) (h : Conflit L v w) : Conflit L w v := by
  obtain ⟨p, hp, q, hq, hd⟩ := h
  exact ⟨q, hq, p, hp, by rw [dist_comm]; exact hd⟩

/-- **Corollaire : le conflit ne dépend que de la différence.** C'est la forme utilisée par le
code (chercher les cliques passant par 0 ne perd rien) : pour `v ∈ L`, confict de `v` avec
`v + d` ⟺ conflit de `0` avec `d`. -/
theorem conflit_iff_zero (L : AddSubgroup E) {v : E} (hv : v ∈ L) (d : E) :
    Conflit L v (v + d) ↔ Conflit L 0 d := by
  have hneg : -v ∈ L := L.neg_mem hv
  have h := conflit_translation L hneg v (v + d)
  simpa [add_assoc, add_comm, add_left_comm] using h.symm

/-! ## 4. Le pont : convexité ⇒ les distances forment un intervalle

C'est le second fait géométrique sur lequel repose la lecture des calculs. Deux cellules de
Voronoï sont convexes ; l'ensemble des distances réalisées entre un point de l'une et un point
de l'autre est donc un **intervalle** de ℝ. Conséquence : pour décider s'il existe une paire à
distance exactement 1, il suffit de trouver une paire à distance ≤ 1 et une paire à distance
≥ 1. C'est exactement ce que fait `exact_tangence.py` (encadrement exact, pas de test flottant),
et c'est ce qui distingue « seuil 1 » de « seuil strictement inférieur à 1 ».
-/

/-- L'ensemble des distances réalisées entre deux convexes est préconnexe. -/
theorem isPreconnected_dist_set (A B : Set E) (hA : Convex ℝ A) (hB : Convex ℝ B) :
    IsPreconnected {d : ℝ | ∃ p ∈ A, ∃ q ∈ B, dist p q = d} := by
  have hAB : IsPreconnected (A ×ˢ B) := (hA.prod hB).isPreconnected
  have himg := hAB.image (fun z : E × E => dist z.1 z.2) continuous_dist.continuousOn
  convert himg using 1
  ext d
  simp [Set.mem_image]

/-- **Théorème du pont.** Si deux convexes portent une paire de points à distance `≤ 1` et une
paire à distance `≥ 1`, alors ils portent une paire à distance exactement `1`.
Autrement dit : « δ⁻ ≤ 1 ≤ δ⁺ ⇒ tangence », sans aucun calcul flottant. -/
theorem existe_paire_distance_un (A B : Set E) (hA : Convex ℝ A) (hB : Convex ℝ B)
    (hlo : ∃ p ∈ A, ∃ q ∈ B, dist p q ≤ 1)
    (hhi : ∃ p ∈ A, ∃ q ∈ B, 1 ≤ dist p q) :
    ∃ p ∈ A, ∃ q ∈ B, dist p q = 1 := by
  set S : Set ℝ := {d : ℝ | ∃ p ∈ A, ∃ q ∈ B, dist p q = d} with hS
  have hpre : IsPreconnected S := isPreconnected_dist_set A B hA hB
  have hord : OrdConnected S := isPreconnected_iff_ordConnected.mp hpre
  obtain ⟨p, hp, q, hq, hle⟩ := hlo
  obtain ⟨p', hp', q', hq', hge⟩ := hhi
  have h1 : dist p q ∈ S := ⟨p, hp, q, hq, rfl⟩
  have h2 : dist p' q' ∈ S := ⟨p', hp', q', hq', rfl⟩
  have hiff := (ordConnected_iff (s := S)).mp hord
  have hone : (1 : ℝ) ∈ S :=
    hiff (dist p q) h1 (dist p' q') h2 (le_trans hle hge) ⟨hle, hge⟩
  obtain ⟨p, hp, q, hq, hd⟩ := hone
  exact ⟨p, hp, q, hq, hd⟩

/-- **Conflit ⟺ encadrement.** Pour deux cellules, l'existence d'une paire à distance 1 est
équivalente à l'existence d'une paire à distance ≤ 1 ET d'une paire à distance ≥ 1. -/
theorem conflit_iff_encadrement (L : AddSubgroup E) (v w : E) :
    Conflit L v w ↔
      ((∃ p ∈ cellule L v, ∃ q ∈ cellule L w, dist p q ≤ 1) ∧
       (∃ p ∈ cellule L v, ∃ q ∈ cellule L w, 1 ≤ dist p q)) := by
  constructor
  · rintro ⟨p, hp, q, hq, hd⟩
    exact ⟨⟨p, hp, q, hq, le_of_eq hd⟩, ⟨p, hp, q, hq, le_of_eq hd.symm⟩⟩
  · rintro ⟨hlo, hhi⟩
    exact existe_paire_distance_un _ _ (cellule_convexe L v) (cellule_convexe L w) hlo hhi

/-! ## 5. Ce qui est ici une **hypothèse** et non un théorème

Rien dans ce fichier ne parle de χ(ℝ²). Ce qui est prouvé ci-dessus est la couche géométrique
*locale* : convexité des cellules, invariance par translation du conflit, et le fait que la
recherche d'une tangence se ramène à un encadrement. Ce qui reste **hors de la formalisation**
et doit continuer à être présenté comme hypothèse ou comme calcul :

* `δ* = 0,2267` : valeur obtenue par balayage numérique (`phase7`, `phase8`), jamais démontrée ;
  le fichier ne l'énonce nulle part comme un théorème.
* la **densité** des réseaux couverts par le calcul : le code énumère des familles
  paramétrées et un paysage fini ; rien ici ne prouve que ces familles couvrent tous les
  réseaux admissibles.
* la **partition** utilisée pour passer d'un résultat sur une cellule à un coloriage du plan :
  aucune formalisation de coloriage de ℝ² n'est faite ici — il n'y a donc, dans ce fichier,
  aucun énoncé sur χ(ℝ²).
* les **nombres** (ω des réseaux, 0/55, 26 423 boîtes) : ce sont des sorties de programmes,
  revérifiées par un second moteur, pas des preuves Lean.
-/

/-- Un **réseau** au sens de la note : un sous-groupe additif discret de l'espace. La discrétude
est l'hypothèse de « réseau » ; elle n'est utilisée nulle part ci-dessus (les théorèmes valent
pour tout sous-groupe additif), elle est déclarée ici pour mémoire. -/
def Reseau (E : Type*) [NormedAddCommGroup E] := {L : AddSubgroup E // DiscreteTopology L}

/-! ## 6. Contrôles : un cas concret, positif ET négatif

Un théorème de la forme « conflit ⟺ encadrement » ne vaut que s'il **discrimine**. On
l'instancie donc sur le réseau `ℤ ⊂ ℝ` (le plus petit cas non trivial), avec deux contrôles :
un conflit réellement présent (`0` et `1` à distance 1) et un conflit réellement absent
(les cellules de `0` et de `3` sont à distance ≥ 2). Le contrôle négatif est **sain** : on
n'utilise que *deux* des contraintes définissant chaque cellule, donc on minore la cellule
(la conclusion « pas de paire à distance 1 » reste vraie pour les vraies cellules).
-/

/-- Le réseau `ℤ` vu comme sous-groupe additif de `ℝ`. -/
abbrev Lint : AddSubgroup ℝ := AddSubgroup.zmultiples (1 : ℝ)

theorem mem_Lint {x : ℝ} : x ∈ Lint ↔ ∃ k : ℤ, (k : ℝ) = x := by
  rw [AddSubgroup.mem_zmultiples_iff]
  constructor
  · rintro ⟨k, hk⟩
    exact ⟨k, by simpa using hk⟩
  · rintro ⟨k, rfl⟩
    exact ⟨k, by simp⟩

/-- Le centre appartient toujours à sa propre cellule. -/
theorem centre_mem_cellule (L : AddSubgroup E) {v : E} (hv : v ∈ L) : v ∈ cellule L v := by
  intro w _
  rw [dist_self]
  exact dist_nonneg

/-- **Contrôle positif** : si le réseau contient un vecteur de longueur 1, le conflit est là. -/
theorem conflit_vecteur_unitaire {L : AddSubgroup E} {d : E} (hd : d ∈ L) (h1 : dist 0 d = 1) :
    Conflit L 0 d :=
  ⟨0, centre_mem_cellule L (L.zero_mem), d, centre_mem_cellule L hd, h1⟩

example : Conflit Lint 0 1 :=
  conflit_vecteur_unitaire (by rw [mem_Lint]; exact ⟨1, by norm_num⟩) (by norm_num)

/-- Dans `ℤ ⊂ ℝ`, une cellule ne dépasse pas son centre de `1/2` vers la droite. -/
theorem cellule_Lint_le (n : ℤ) {x : ℝ} (hx : x ∈ cellule Lint (n : ℝ)) :
    x ≤ (n : ℝ) + 1 / 2 := by
  have h := hx ((n : ℝ) + 1) (by
    rw [mem_Lint]
    exact ⟨n + 1, by push_cast; ring⟩)
  rw [Real.dist_eq, Real.dist_eq] at h
  have h2 : (x - (n : ℝ)) ^ 2 ≤ (x - ((n : ℝ) + 1)) ^ 2 := by
    have h3 := pow_le_pow_left₀ (abs_nonneg (x - (n : ℝ))) h 2
    rwa [sq_abs, sq_abs] at h3
  nlinarith

/-- Dans `ℤ ⊂ ℝ`, une cellule ne descend pas sous son centre de `1/2`. -/
theorem cellule_Lint_ge (n : ℤ) {x : ℝ} (hx : x ∈ cellule Lint (n : ℝ)) :
    (n : ℝ) - 1 / 2 ≤ x := by
  have h := hx ((n : ℝ) - 1) (by
    rw [mem_Lint]
    exact ⟨n - 1, by push_cast; ring⟩)
  rw [Real.dist_eq, Real.dist_eq] at h
  have h2 : (x - (n : ℝ)) ^ 2 ≤ (x - ((n : ℝ) - 1)) ^ 2 := by
    have h3 := pow_le_pow_left₀ (abs_nonneg (x - (n : ℝ))) h 2
    rwa [sq_abs, sq_abs] at h3
  nlinarith

/-- **Contrôle négatif** : dans `ℤ ⊂ ℝ`, les cellules de `0` et de `3` ne portent aucun
segment de longueur 1 (elles sont à distance ≥ 2 l'une de l'autre). -/
theorem controle_negatif : ¬ Conflit Lint 0 3 := by
  rintro ⟨p, hp, q, hq, hd⟩
  have hp' : p ≤ 1 / 2 := by simpa using cellule_Lint_le 0 hp
  have hq' : (5 : ℝ) / 2 ≤ q := by
    have h := cellule_Lint_ge 3 hq
    norm_num at h
    linarith
  rw [Real.dist_eq] at hd
  have hle : p - q ≤ 0 := by linarith
  have habs : |p - q| = -(p - q) := abs_of_nonpos hle
  linarith [hd, habs]

/-- Le contrôle négatif vu par l'encadrement : l'une des deux inégalités doit échouer. -/
theorem controle_negatif_encadrement :
    ¬ ((∃ p ∈ cellule Lint 0, ∃ q ∈ cellule Lint 3, dist p q ≤ 1) ∧
       (∃ p ∈ cellule Lint 0, ∃ q ∈ cellule Lint 3, 1 ≤ dist p q)) :=
  fun h => controle_negatif ((conflit_iff_encadrement Lint 0 3).mpr h)

end Geometrie

#print axioms Geometrie.centre_mem_cellule
#print axioms Geometrie.cellule_Lint_le
#print axioms Geometrie.cellule_Lint_ge
#print axioms Geometrie.controle_negatif
#print axioms Geometrie.controle_negatif_encadrement
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
#print axioms Geometrie.conflit_vecteur_unitaire
