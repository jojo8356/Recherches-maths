/-
  Boites.lean — le MOTEUR du certificat par boîtes, en machine.

  Le certificat par boîtes (§4, `audit_certificat3.py`) vérifie, boîte par boîte, que sept
  cellules de Voronoï sont deux à deux en conflit. Ce fichier compile la partie générique de
  cet argument — celle qui ne dépend d'aucune boîte : dès que, pour sept points du réseau, on
  exhibe pour chaque paire des témoins à distance au carré ≤ 1 et des témoins à distance au
  carré ≥ 1, les sept cellules reçoivent sept couleurs distinctes.

  Ce qui reste hors Lean est donc *uniquement* la donnée par boîte (les sept décalages et les
  témoins rationnels) : le raisonnement, lui, est ici.
-/
import Queue

open Set

namespace Boites

/-- **Moteur du certificat.** Soient sept points du réseau Λ et, pour chaque paire de cellules,
une paire de points à distance au carré ≤ 1 et une paire à distance au carré ≥ 1. Alors tout
coloriage propre (toute paire à distance 1 a deux couleurs) constant sur chacune des sept cellules
doit leur donner sept couleurs **distinctes**. -/
theorem clique_de_temoins (g h : ℝ) (v : Fin 7 → ℝ × ℝ)
    (hlo : ∀ i j : Fin 7, i ≠ j → ∃ p ∈ Queue.cell g h (v i), ∃ q ∈ Queue.cell g h (v j),
      Queue.dist2 p q ≤ 1)
    (hhi : ∀ i j : Fin 7, i ≠ j → ∃ p ∈ Queue.cell g h (v i), ∃ q ∈ Queue.cell g h (v j),
      1 ≤ Queue.dist2 p q)
    {C : Type*} (c : ℝ × ℝ → C) (hc : ∀ p q : ℝ × ℝ, Queue.dist2 p q = 1 → c p ≠ c q)
    (col : Fin 7 → C) (hcol : ∀ (i : Fin 7), ∀ p ∈ Queue.cell g h (v i), c p = col i) :
    Function.Injective col := by
  intro i j hij
  by_contra hne
  obtain ⟨p, hp, q, hq, hd⟩ :=
    Queue.tangence _ _ (Queue.cell_convex g h _) (Queue.cell_convex g h _) (hlo i j hne) (hhi i j hne)
  exact (hc p q hd) (by rw [hcol i p hp, hcol j q hq]; exact hij)

#print axioms Boites.clique_de_temoins

/-! ## 2. La réduction au fini : au-delà d'un rayon, la contrainte est automatique

C'est le seul lemme de géométrie qui manquait pour vérifier une boîte : si un point est dans la
boule de rayon r et qu'un vecteur du réseau a une longueur ≥ 2r, alors l'inégalité de Voronoï
`2⟨p,v⟩ ≤ |v|²` est automatique. Il ramène « pour tout v ∈ Λ » à « pour les v de longueur < 2r »,
qui sont en nombre finí dès que le réseau est discret. -/

/-- **Contrainte automatique au-delà de 2r.** Si `|p|² ≤ r²` et `|v|² ≥ 4r²` (r ≥ 0), alors
`2⟨p,v⟩ ≤ |v|²`. C'est Cauchy–Schwarz au carré, sans racine carrée. -/
theorem contrainte_auto (p v : ℝ × ℝ) (r : ℝ) (hr : 0 ≤ r)
    (hp : p.1 ^ 2 + p.2 ^ 2 ≤ r ^ 2) (hv : 4 * r ^ 2 ≤ v.1 ^ 2 + v.2 ^ 2) :
    2 * (p.1 * v.1 + p.2 * v.2) ≤ v.1 ^ 2 + v.2 ^ 2 := by
  have hnn : (0 : ℝ) ≤ v.1 ^ 2 + v.2 ^ 2 := by positivity
  have hcs : (2 * (p.1 * v.1 + p.2 * v.2)) ^ 2 ≤ (v.1 ^ 2 + v.2 ^ 2) ^ 2 := by
    nlinarith [sq_nonneg (p.1 * v.2 - p.2 * v.1), sq_nonneg (v.1 ^ 2 + v.2 ^ 2), hp, hv, hr]
  by_cases hpos : 0 ≤ 2 * (p.1 * v.1 + p.2 * v.2)
  · nlinarith [hcs, hpos, hnn]
  · push_neg at hpos
    linarith [hpos.le, hnn]

#print axioms Boites.contrainte_auto

/-! ## 3. Les deux briques du portage : forme translatée, et réduction au fini -/

/-- Forme translatée de la contrainte de cellule : tout se lit en `p - v` et `w - v`. -/
theorem cell_iff_translate (g h : ℝ) (v p : ℝ × ℝ) :
    p ∈ Queue.cell g h v ↔
      ∀ w ∈ Queue.Reseau g h,
        2 * ((p.1 - v.1) * (w.1 - v.1) + (p.2 - v.2) * (w.2 - v.2)) ≤
          (w.1 - v.1) ^ 2 + (w.2 - v.2) ^ 2 := by
  simp only [Queue.cell, Set.mem_setOf_eq, Queue.dist2]
  constructor
  · intro hyp w hw
    have := hyp w hw
    nlinarith
  · intro hyp w hw
    have := hyp w hw
    nlinarith


#print axioms Boites.cell_iff_translate
/-- **Réduction au fini.** Si `|p − v|² ≤ r²` et si la contrainte de Voronoï tient pour les seuls
`w` tels que `|w − v|² < 4r²`, alors `p ∈ cell v` : les autres sont traités par `contrainte_auto`.
C'est ce qui ramène une vérification infinie à un calcul fini, boîte par boîte. -/
theorem cell_of_fini (g h : ℝ) (v p : ℝ × ℝ) (r : ℝ) (hr : 0 ≤ r)
    (hp : (p.1 - v.1) ^ 2 + (p.2 - v.2) ^ 2 ≤ r ^ 2)
    (hfini : ∀ w ∈ Queue.Reseau g h, (w.1 - v.1) ^ 2 + (w.2 - v.2) ^ 2 < 4 * r ^ 2 →
      2 * ((p.1 - v.1) * (w.1 - v.1) + (p.2 - v.2) * (w.2 - v.2)) ≤
        (w.1 - v.1) ^ 2 + (w.2 - v.2) ^ 2) :
    p ∈ Queue.cell g h v := by
  rw [cell_iff_translate]
  intro w hw
  by_cases hbig : 4 * r ^ 2 ≤ (w.1 - v.1) ^ 2 + (w.2 - v.2) ^ 2
  · have h := contrainte_auto ((p.1 - v.1, p.2 - v.2) : ℝ × ℝ)
      ((w.1 - v.1, w.2 - v.2) : ℝ × ℝ) r hr hp hbig
    simpa using h
  · push_neg at hbig
    exact hfini w hw hbig

#print axioms Boites.cell_of_fini

end Boites
