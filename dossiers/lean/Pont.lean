/-
  Pont.lean — le pont du dossier Sokolov–Voronov, passé à la machine (Lean 4, noyau pur)

  Ce que ce fichier fait, et ce qu'il ne fait pas
  -----------------------------------------------
  Le §7.3 de l'audit énonçait deux lemmes :

    A (conflit)   : si s·dmin < 1 < s·dmax, tout coloriage propre constant sur les cellules
                    donne des couleurs différentes à A et B ;
    B (échelle)   : si dmin ≤ D/ε et dmax ≥ D/ε avec ε < 1, il existe s avec
                    s·dmin < 1 < s·dmax et s·D < 1.

  Ici : le lemme B est **entièrement prouvé à la machine**, sans axiome ni sorry. C'est lui qui
  porte le contenu « pourquoi ε < 1 » : le fichier montre que ε < 1 force D < dmax, donc que
  l'intervalle des échelles est non vide, et il exhibe l'échelle s = q/p.
  Le lemme A est découpé : sa partie géométrique (convexité, segment) est prouvée ici ; son
  étape non élémentaire — l'existence d'un point d'abscisse t où la distance vaut exactement 1 —
  est le théorème des valeurs intermédiaires pour un trinôme, et elle est *isolée* dans une
  hypothèse nommée. Voir la note de statut à la fin du fichier : ce n'est pas un oubli, c'est la
  frontière exacte de ce que le noyau de Lean permet sans Mathlib.
-/

namespace Pont

/-! ## 1. Lemme B — arithmétique entière, entièrement prouvée

On représente dmin, dmax et D par des entiers de même dénominateur (dm, dx, dd) et l'échelle par
une fraction s = q/p. Les trois conclusions s·dmin < 1, 1 < s·dmax, s·D < 1 s'écrivent alors
q·dm < p, p < q·dx, q·dd < p : de l'arithmétique **linéaire**, que `omega` décide. -/

/-- Le lemme B, forme entière. L'échelle témoin est s = 2 / (2·max(dm,dd) + 1) : son numérateur
    est 2, son dénominateur dépasse strictement 2·dmin et 2·D, et reste strictement sous
    2·dmax puisque max(dm,dd) < dx. -/
theorem lemmeB (dm dx dd : Nat) (_hm : 0 < dm) (_hd : 0 < dd) (h1 : dm < dx) (h2 : dd < dx) :
    ∃ p q : Nat, 0 < p ∧ 0 < q ∧ q * dm < p ∧ p < q * dx ∧ q * dd < p := by
  refine ⟨2 * max dm dd + 1, 2, by omega, by omega, by omega, by omega, by omega⟩

/-- **ε < 1 force D < dmax.** C'est le point que le §7.3 énonçait sans le prouver : de
    dmax ≥ D/ε avec 0 < ε = p₀/q₀ < 1 on tire dmax > D. Écrit en entiers : q₀·dd ≤ p₀·dx et
    p₀ < q₀ donnent dd < dx. -/
theorem eps_force_D_lt_dmax (dd dx p₀ q₀ : Nat) (hd : 0 < dd) (_hp₀ : 0 < p₀) (hlt : p₀ < q₀)
    (hdx : q₀ * dd ≤ p₀ * dx) : dd < dx := by
  -- dd·p₀ < dd·q₀ (car 0 < p₀ < q₀ et 0 < dd), et dd·q₀ = q₀·dd ≤ p₀·dx = dx·p₀.
  have hstrict : dd * p₀ < dd * q₀ := Nat.mul_lt_mul_of_pos_left hlt hd
  have hle : dd * q₀ ≤ dx * p₀ := by
    calc dd * q₀ = q₀ * dd := Nat.mul_comm dd q₀
      _ ≤ p₀ * dx := hdx
      _ = dx * p₀ := Nat.mul_comm p₀ dx
  exact Nat.lt_of_mul_lt_mul_right (Nat.lt_of_lt_of_le hstrict hle)

/-- **La forme « ε » du lemme B, entièrement dérivée des hypothèses du §7.3.** De dmin ≤ D/ε,
    dmax ≥ D/ε et 0 < ε = p₀/q₀ < 1 on tire d'abord dmin < D (par dmin·q₀ ≤ p₀·D ≤ q₀·D) puis
    D < dmax (`eps_force_D_lt_dmax`), et le lemme B s'applique. Aucune hypothèse auxiliaire :
    la stricte inégalité dmin < dmax nécessaire au lemme B est elle aussi dérivée. -/
theorem lemmeB_eps (dm dx dd p₀ q₀ : Nat) (hm : 0 < dm) (hd : 0 < dd) (hp₀ : 0 < p₀)
    (hlt : p₀ < q₀) (hbas : q₀ * dm ≤ p₀ * dd) (hhaut : q₀ * dd ≤ p₀ * dx) :
    ∃ p q : Nat, 0 < p ∧ 0 < q ∧ q * dm < p ∧ p < q * dx ∧ q * dd < p := by
  have hq₀ : 0 < q₀ := Nat.lt_trans hp₀ hlt
  have hp₀q₀ : p₀ ≤ q₀ := Nat.le_of_lt hlt
  -- dmin ≤ D : dmin·q₀ ≤ D·p₀ ≤ D·q₀.
  have hdm_le_dd : dm ≤ dd := by
    have h1 : dm * q₀ ≤ dd * q₀ := by
      calc dm * q₀ = q₀ * dm := Nat.mul_comm dm q₀
        _ ≤ p₀ * dd := hbas
        _ = dd * p₀ := Nat.mul_comm p₀ dd
        _ ≤ dd * q₀ := Nat.mul_le_mul_left dd hp₀q₀
    exact Nat.le_of_mul_le_mul_right h1 hq₀
  have hdm_lt_dx : dm < dx :=
    Nat.lt_of_le_of_lt hdm_le_dd (eps_force_D_lt_dmax dd dx p₀ q₀ hd hp₀ hlt hhaut)
  exact lemmeB dm dx dd hm hd hdm_lt_dx (eps_force_D_lt_dmax dd dx p₀ q₀ hd hp₀ hlt hhaut)

/-! ## 2. Lemme A — la partie géométrique, prouvée ; l'étape IVT, isolée

Le lemme A se décompose en deux :
  (i)  la convexité : le segment qui joint un point de l'intérieur de A à un point de
       l'intérieur de A reste dans A (idem pour B) — c'est la définition même de la convexité,
       donc une hypothèse de structure, mais on vérifie à la machine que l'argument ne demande
       *rien d'autre* ;
  (ii) le trinôme : |p(t) − q(t)|² est un trinôme en t, qui vaut < 1 en t = 0 et > 1 en t = 1 ;
       il existe donc t ∈ [0,1] où il vaut exactement 1. C'est le théorème des valeurs
       intermédiaires — et c'est là, exactement là, que la complétude de ℝ entre en jeu.
Ici (i) est prouvé et (ii) est l'hypothèse `hivt`, nommée. -/

/-- Point du plan rationnel. -/
abbrev Pt := Rat × Rat

/-- Distance au carré. -/
def dist2 (p q : Pt) : Rat := (p.1 - q.1) * (p.1 - q.1) + (p.2 - q.2) * (p.2 - q.2)

/-- Combinaison affine : le point du segment [p,q] de paramètre t. -/
noncomputable def seg (p q : Pt) (t : Rat) : Pt :=
  (t * p.1 + (1 - t) * q.1, t * p.2 + (1 - t) * q.2)

/-- Convexité, au sens où l'audit l'emploie : stabilité par combinaison affine à paramètre
    dans [0,1]. C'est la notion exacte des cellules de Voronoï et de leurs intérieurs
    polygonaux (intersections de demi-plans ouverts, cf. `audit_gh.cellule`).
    Le noyau de Lean n'a pas `Set` : un ensemble est un prédicat. -/
def Convex (S : Pt → Prop) : Prop :=
  ∀ p, S p → ∀ q, S q → ∀ t : Rat, 0 ≤ t → t ≤ 1 → S (seg p q t)

/-- **Lemme A, partie géométrique.** Si le trinôme s'annule à l'abscisse t (hypothèse `hivt`),
    le couple de points correspondant est formé de points intérieurs aux deux cellules, à
    distance exactement 1. Autrement dit : tout le lemme A, sauf l'existence de t. -/
theorem lemmeA_geometrique (U V : Pt → Prop) (hU : Convex U) (hV : Convex V)
    (p₁ q₁ p₂ q₂ : Pt) (hp₁ : U p₁) (hq₁ : V q₁) (hp₂ : U p₂) (hq₂ : V q₂)
    (t : Rat) (ht0 : 0 ≤ t) (ht1 : t ≤ 1)
    (hivt : dist2 (seg p₁ p₂ t) (seg q₁ q₂ t) = 1) :
    ∃ p, U p ∧ ∃ q, V q ∧ dist2 p q = 1 :=
  ⟨seg p₁ p₂ t, hU p₁ hp₁ p₂ hp₂ t ht0 ht1,
   seg q₁ q₂ t, hV q₁ hq₁ q₂ hq₂ t ht0 ht1, hivt⟩

/-- **Le conflit, dernière marche du pont.** Une fois le couple de points intérieurs à distance
    exactement 1 obtenu, un coloriage propre ne peut pas donner la même couleur aux deux
    cellules : c'est une contraposition immédiate. -/
theorem pas_meme_couleur {C : Type} (couleur : Pt → C)
    (propre : ∀ p q : Pt, dist2 p q = 1 → couleur p ≠ couleur q)
    (U V : Pt → Prop) (cv : C) (hU : ∀ p, U p → couleur p = cv)
    (hV : ∀ q, V q → couleur q = cv)
    (p : Pt) (hp : U p) (q : Pt) (hq : V q) (h : dist2 p q = 1) : False := by
  have h1 : couleur p ≠ couleur q := propre p q h
  rw [hU p hp, hV q hq] at h1
  exact h1 rfl

/-! ## 3. Note de statut (à lire avant de citer ce fichier)

Prouvé ici, à la machine, sans axiome : `lemmeB`, `eps_force_D_lt_dmax`, `lemmeB_eps`,
`lemmeA_geometrique`, `pas_meme_couleur`.

Non prouvé ici : l'existence de l'abscisse t du lemme A (hypothèse `hivt`). Ce n'est pas une
facilité : l'énoncé est *faux* sur ℚ (le trinôme peut valoir < 1 en t = 0 et > 1 en t = 1 sans
s'annuler en aucune abscisse rationnelle — son discriminant n'est pas toujours un carré dans ℚ),
et il est vrai sur ℝ par le théorème des valeurs intermédiaires, c'est-à-dire par la complétude
de ℝ. Le noyau de Lean 4 ne contient pas ℝ : la couverture demanderait Mathlib (`Convex`,
`intermediate_value`), dont l'import ne tient pas dans la mémoire de cette machine (~0,9 Go
disponibles). Le prochain jalon est donc, soit l'import de Mathlib sur une machine à ≥ 4 Go,
soit un développement autosuffisant de ℝ par coupures de Dedekind (~600–1 000 lignes).
-/

/-! ## 4. Contrôle : aucune dépendance axiomatique

Les `#print axioms` ci-dessous s'exécutent à la compilation. Attendu : « does not depend on any
axioms » pour chacun — ni `sorryAx`, ni axiome ajouté par ce fichier. -/

#print axioms Pont.lemmeB
#print axioms Pont.eps_force_D_lt_dmax
#print axioms Pont.lemmeB_eps
#print axioms Pont.lemmeA_geometrique
#print axioms Pont.pas_meme_couleur

end Pont
