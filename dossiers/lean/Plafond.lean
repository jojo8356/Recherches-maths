/-
  Plafond.lean — formalisation en Lean 4 (noyau pur, SANS Mathlib)

  Deux piliers des notes Hadwiger–Nelson, formalisés :

  1. BORNE DE CLIQUE (forme finie) : un coloriage propre est injectif sur une clique.
     C'est l'argument utilisé partout : « 7 cellules deux à deux incompatibles ⇒ 7 couleurs ».

  2. THÉORÈME DU PLAFOND (forme arithmétique) : un argument de type « densité d'une classe »
     ne peut pas dépasser 5 couleurs dès que la borne de densité vaut au moins 1/5.
     Avec la constante de la littérature, 0,2267 = 2267/10000, il donne au mieux 5.

  CE QUI N'EST PAS FORMALISÉ, ET QUI RESTE HYPOTHÈSE :
    - l'existence d'une densité pour une classe mesurable sans distance 1 ;
    - la borne de densité 0,2267 elle-même (résultat de la littérature, non revérifié ici) ;
    - le fait qu'un coloriage partitionne le plan en classes dont les densités somment à 1.
  Ces trois points sont les hypothèses du théorème, pas des théorèmes.
-/

namespace Plafond

/-! ## 1. Borne de clique -/

/-- `EstClique adj l` : les éléments de `l` sont deux à deux adjacents, et distincts. -/
def EstClique {α : Type} (adj : α → α → Prop) (l : List α) : Prop :=
  (∀ x ∈ l, ∀ y ∈ l, x ≠ y → adj x y) ∧ l.Nodup

/-- `ColoriagePropre adj c` : aucune arête n'est monochrome. -/
def ColoriagePropre {α : Type} (adj : α → α → Prop) (c : α → Nat) : Prop :=
  ∀ x y, adj x y → c x ≠ c y

/-- Borne de clique : un coloriage propre est injectif sur une clique. Deux sommets
distincts d'une clique reçoivent des couleurs distinctes, donc une clique de `n` sommets
exige `n` couleurs. C'est exactement l'argument utilisé dans toutes les notes. -/
theorem injectif_sur_clique {α : Type} (adj : α → α → Prop) (c : α → Nat) (l : List α)
    (hcl : EstClique adj l) (hcol : ColoriagePropre adj c) :
    ∀ x ∈ l, ∀ y ∈ l, c x = c y → x = y := by
  intro x hx y hy heq
  by_cases h : x = y
  · exact h
  · exact absurd heq (hcol x y (hcl.1 x hx y hy h))

/-! ## 2. Le plafond des arguments de densité

On code les densités en dix-millièmes entiers : une classe de densité `d` a un poids
`w = d * 10000`. « Les classes partitionnent le plan » devient « la somme des poids vaut
10000 ». La borne de densité `0,2267` devient « chaque poids est au plus 2267 ». -/

/-- Somme d'une liste d'entiers (définie ici pour ne dépendre d'aucune bibliothèque). -/
def somme : List Nat → Nat
  | [] => 0
  | x :: xs => x + somme xs

/-- Si chaque élément d'une liste est au plus `d`, la somme est au plus `longueur * d`. -/
theorem somme_le : ∀ (l : List Nat) (d : Nat), (∀ x ∈ l, x ≤ d) → somme l ≤ l.length * d
  | [], d, _ => by simp [somme]
  | x :: xs, d, h => by
      have hx : x ≤ d := h x (by simp)
      have hxs : ∀ y ∈ xs, y ≤ d := fun y hy => h y (by simp [hy])
      have ih := somme_le xs d hxs
      have hcons : somme (x :: xs) = x + somme xs := rfl
      rw [hcons, List.length_cons, Nat.add_mul, Nat.one_mul]
      omega

/-- Théorème du plafond (constante 0,2267). Si chaque classe a une densité au plus
2267/10000 et si les classes partitionnent le plan, tout coloriage propre a au moins
5 classes. Quatre ne suffiraient pas (4 x 2267 = 9068 < 10000), cinq est le minimum. -/
theorem plafond_cinq (w : List Nat) (hsomme : somme w = 10000)
    (hborne : ∀ x ∈ w, x ≤ 2267) : 5 ≤ w.length := by
  have h := somme_le w 2267 hborne
  rw [hsomme] at h
  suffices h5 : ¬ w.length < 5 by omega
  intro hlt
  have h4 : w.length ≤ 4 := by omega
  have hmul : w.length * 2267 ≤ 4 * 2267 := Nat.mul_le_mul_right 2267 h4
  omega

/-- Le plafond est atteint : 5 est compatible avec les hypothèses.
Un découpage en 5 classes de poids 2267, 2267, 2267, 2267, 932 les satisfait toutes. -/
theorem cinq_compatible :
    ∃ w : List Nat, somme w = 10000 ∧ (∀ x ∈ w, x ≤ 2267) ∧ w.length = 5 := by
  refine ⟨[2267, 2267, 2267, 2267, 932], ?_, ?_, ?_⟩
  · decide
  · decide
  · decide

/-- Conséquence : aucun argument de cette forme ne peut conclure à 6 couleurs.
Il n'est pas vrai que les hypothèses de densité forcent 6 classes, puisque 5 les satisfait
toutes. C'est la formulation exacte de « l'argument tue une méthode, pas une valeur ». -/
theorem aucun_plafond_six :
    ¬ (∀ w : List Nat, somme w = 10000 → (∀ x ∈ w, x ≤ 2267) → 6 ≤ w.length) := by
  intro h
  obtain ⟨w, h1, h2, h3⟩ := cinq_compatible
  have hh := h w h1 h2
  rw [h3] at hh
  omega

/-- Version générale : pour toute borne de densité `d` comprise entre 1/5 (2000) et 1/4
(2500), un découpage en 5 classes satisfait les hypothèses. La constante de la littérature,
2267, tombe dans cet intervalle. Pour d > 2500 le plafond est encore plus bas (4 classes ou
moins), donc l'énoncé « au plus 5 » vaut a fortiori. -/
theorem aucun_plafond_six_general (d : Nat) (h2000 : 2000 ≤ d) (h2500 : d ≤ 2500) :
    ¬ (∀ w : List Nat, somme w = 10000 → (∀ x ∈ w, x ≤ d) → 6 ≤ w.length) := by
  intro h
  have hlast : 10000 - 4 * d ≤ d := by omega
  have hw : somme [d, d, d, d, 10000 - 4 * d] = 10000 := by
    simp only [somme]
    omega
  have hb : ∀ x ∈ [d, d, d, d, 10000 - 4 * d], x ≤ d := by
    intro x hx
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
    omega
  have hh := h [d, d, d, d, 10000 - 4 * d] hw hb
  simp only [List.length_cons, List.length_nil] at hh
  omega

end Plafond

-- Base de confiance : aucune preuve ne doit dépendre de `sorryAx`.
#print axioms Plafond.injectif_sur_clique
#print axioms Plafond.plafond_cinq
#print axioms Plafond.aucun_plafond_six
#print axioms Plafond.aucun_plafond_six_general
