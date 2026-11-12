/-
  T8.lean — pourquoi le calcul exact de ω est exact (Lean 4, noyau pur, sans Mathlib)

  Le point de méthode de T8 : le graphe de conflit d'un pavage de réseau est un graphe de
  Cayley sur ℤ², donc sommet-transitif ; par conséquent toute clique est la translatée
  d'une clique contenant 0, et chercher les cliques passant par 0 ne perd rien.

  Ce fichier formalise exactement cela. C'est la justification de `clique_max_avec0` :
  sans ce lemme, chercher les cliques par 0 serait une fenêtre heuristique, et les valeurs
  de ω de T8 n'auraient pas de statut exact.
-/

namespace T8

/-- Point du réseau ℤ². -/
structure P where
  a : Int
  b : Int
  deriving DecidableEq, Repr

namespace P

instance : Sub P := ⟨fun x y => ⟨x.a - y.a, x.b - y.b⟩⟩
instance : Add P := ⟨fun x y => ⟨x.a + y.a, x.b + y.b⟩⟩
instance : Neg P := ⟨fun x => ⟨-x.a, -x.b⟩⟩
instance : Zero P := ⟨⟨0, 0⟩⟩

@[simp] theorem sub_a (x y : P) : (x - y).a = x.a - y.a := rfl
@[simp] theorem sub_b (x y : P) : (x - y).b = x.b - y.b := rfl
@[simp] theorem add_a (x y : P) : (x + y).a = x.a + y.a := rfl
@[simp] theorem add_b (x y : P) : (x + y).b = x.b + y.b := rfl
@[simp] theorem zero_a : (0 : P).a = 0 := rfl
@[simp] theorem zero_b : (0 : P).b = 0 := rfl
@[simp] theorem neg_a (x : P) : (-x).a = -x.a := rfl
@[simp] theorem neg_b (x : P) : (-x).b = -x.b := rfl

/-- Deux points sont égaux si leurs coordonnées le sont. -/
theorem ext {x y : P} (h1 : x.a = y.a) (h2 : x.b = y.b) : x = y := by
  cases x; cases y; simp_all

/-- L'ensemble des différences en conflit est symétrique : si `v` est un conflit, `-v` aussi.
C'est vrai géométriquement (la relation « deux cellules sont en conflit » est symétrique). -/
def Symetrique (E : P → Prop) : Prop := ∀ v, E v → E (-v)

/-- Adjacence dans le graphe de Cayley : `x` et `y` sont en conflit si leur différence
appartient à l'ensemble `E` des différences en conflit. -/
def Voisin (E : P → Prop) (x y : P) : Prop := E (y - x)

/-- **Invariance par translation** : la relation de conflit ne dépend que de la différence.
C'est le fait qui fait de ce graphe un graphe de Cayley. -/
theorem voisin_translation (E : P → Prop) (x y t : P) :
    Voisin E (x + t) (y + t) ↔ Voisin E x y := by
  unfold Voisin
  have h : (y + t) - (x + t) = y - x := by
    apply P.ext <;> simp <;> omega
  rw [h]

/-- `Clique E C` : les éléments de `C` sont deux à deux en conflit, et distincts. -/
def Clique (E : P → Prop) (C : List P) : Prop :=
  (∀ x ∈ C, ∀ y ∈ C, x ≠ y → Voisin E x y) ∧ C.Nodup

/-- **Lemme de recentrage (le cœur de T8).** Toute clique se translate en une clique de même
taille contenant l'origine. C'est ce qui autorise à chercher ω parmi les seules cliques
passant par 0 — sans fenêtre, sans perte. -/
theorem recentrage (E : P → Prop) (C : List P) (hC : Clique E C) (c : P) (hc : c ∈ C) :
    Clique E (C.map (fun x => x - c)) ∧ (0 : P) ∈ C.map (fun x => x - c) := by
  obtain ⟨hcl, hnd⟩ := hC
  have hinj : ∀ a b : P, a - c = b - c → a = b := by
    intro a b h
    apply P.ext
    · have h1 : (a - c).a = (b - c).a := by rw [h]
      simp at h1; omega
    · have h2 : (a - c).b = (b - c).b := by rw [h]
      simp at h2; omega
  constructor
  · constructor
    · intro x hx y hy hxy
      simp only [List.mem_map] at hx hy
      obtain ⟨x', hx', rfl⟩ := hx
      obtain ⟨y', hy', rfl⟩ := hy
      have hne : x' ≠ y' := by
        intro h
        exact hxy (by rw [h])
      have hadj : Voisin E x' y' := hcl x' hx' y' hy' hne
      have heq : (y' - c) - (x' - c) = y' - x' := by
        apply P.ext <;> simp <;> omega
      unfold Voisin at hadj ⊢
      rw [heq]; exact hadj
    · exact hnd.map (fun x => x - c) (fun a b hne => by
        intro heq
        exact hne (hinj a b heq))
  · exact List.mem_map.mpr ⟨c, hc, by apply P.ext <;> simp⟩

/-- Corollaire : si une clique non vide de taille `n` existe, il en existe une de taille `n`
passant par 0. C'est l'énoncé utilisé par `echelle.clique_max_avec0` — et la raison pour
laquelle les valeurs de ω de T8 sont exactes et non fenêtrées. -/
theorem existe_clique_par_zero (E : P → Prop) (c : P) (rest : List P)
    (hC : Clique E (c :: rest)) :
    ∃ D : List P, Clique E D ∧ (0 : P) ∈ D ∧ D.length = (c :: rest).length := by
  refine ⟨(c :: rest).map (fun x => x - c), ?_, ?_, by simp⟩
  · exact (recentrage E (c :: rest) hC c (by simp)).1
  · exact (recentrage E (c :: rest) hC c (by simp)).2

end P

end T8

#print axioms T8.P.voisin_translation
#print axioms T8.P.recentrage
#print axioms T8.P.existe_clique_par_zero
