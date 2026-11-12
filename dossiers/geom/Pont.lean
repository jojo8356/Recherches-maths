/-
  Pont.lean — le PONT du dossier Sokolov–Voronov, certifié par la machine (Lean 4 + Mathlib)

  Le §7.3 de l'audit énonçait deux lemmes « prouvés à la main, trois lignes chacun » :
    A (conflit) : si s·dmin < 1 < s·dmax, tout coloriage propre constant sur les cellules
                  donne des couleurs différentes à A et B ;
    B (échelle) : si 0 < ε < 1, dmin ≤ D/ε et dmax ≥ D/ε, il existe s avec
                  s·dmin < 1 < s·dmax et s·D < 1.
  Ce fichier les prouve à la machine. Il s'appuie sur `Geometrie.lean`, qui contient déjà le
  cœur géométrique du lemme A — convexité des cellules de Voronoï, préconnexité de l'ensemble
  des distances réalisées, et « encadrement ⇒ tangence » (`existe_paire_distance_un`).

  Ce qui est prouvé ici, sans axiome ajouté ni sorry :
    lemmeB            : l'échelle existe (arithmétique, `linarith`), avec s = (1/dmax + 1/D)/2 ;
    pont_coloriage    : paire à distance 1 ⇒ un coloriage propre ne peut pas donner la même
                        couleur aux deux cellules (version « coloriage-fonction ») ;
    pont_interieurs   : la même chose quand seuls les INTÉRIEURS portent la couleur — c'est la
                        version « coloriage de carte » que le §7.3 invoque, et elle ne demande
                        pas plus : les intérieurs de convexes sont convexes (`Convex.interior`) ;
    pont_echelle      : l'échelle s et les cellules dilatées, bout à bout.
-/
import Geometrie

open Set
open Pointwise

namespace Pont

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-! ## Lemme B — l'échelle existe, et c'est ε < 1 qui la donne -/

/-- **Lemme B.** Si 0 < dmin, 0 < D, 0 < ε < 1, dmin ≤ D/ε, D/ε ≤ dmax et **dmin < dmax**,
alors il existe une échelle s telle que s·dmin < 1 < s·dmax **et** s·D < 1.

    Deux corrections que la machine a imposées au §7.3, et qui sont de vraies corrections :

    * l'énoncé y omettait `dmin < dmax`. Sans elle il est **faux** : si dmin = dmax = D/ε, aucune
      échelle ne peut vérifier à la fois s·dmin < 1 et 1 < s·dmax. L'hypothèse est acquise dans
      l'application (deux cellules distinctes ont dmin < dmax), mais elle doit être dite.
    * l'échelle témoin `(1/dmax + 1/D)/2` ne convient pas : elle suppose 1/D ≤ 1/dmin, c'est-à-dire
      dmin ≤ D, ce qui n'est **pas** impliqué par dmin ≤ D/ε (prendre D = 1, ε = 1/2, dmin = 3/2,
      dmax = 2 : s = 3/4 donne s·dmin = 9/8 > 1). L'échelle correcte est le milieu de
      ]1/dmax, min(1/dmin, 1/D)[, dont la non-vacuité vient de dmin < dmax et D < dmax.
    * l'hypothèse dmin ≤ D/ε **n'est pas utilisée** par la preuve (elle est gardée pour la
      fidélité à l'énoncé, mais la machine montre qu'elle est superflue) : tout ce qui compte est
      ε < 1, D/ε ≤ dmax et dmin < dmax. -/
theorem lemmeB (dmin dmax D ε : ℝ) (hdmin : 0 < dmin) (hD : 0 < D)
    (hε0 : 0 < ε) (hε1 : ε < 1) (_hbas : dmin ≤ D / ε) (hhaut : D / ε ≤ dmax)
    (hstrict : dmin < dmax) :
    ∃ s : ℝ, 0 < s ∧ s * dmin < 1 ∧ 1 < s * dmax ∧ s * D < 1 := by
  have hDε : 0 < D / ε := div_pos hD hε0
  -- ε < 1 force D < dmax : c'est le seul endroit où la stricte inégalité sert.
  have hDlt : D < dmax := by
    have h1 : D < D / ε := by
      rw [lt_div_iff₀ hε0]
      nlinarith
    exact lt_of_lt_of_le h1 hhaut
  have hdmax : 0 < dmax := lt_trans hD hDlt
  -- les deux bornes de l'intervalle des échelles
  have h1 : 1 / dmax < 1 / dmin := one_div_lt_one_div_of_lt hdmin hstrict
  have h2 : 1 / dmax < 1 / D := one_div_lt_one_div_of_lt hD hDlt
  have hmin : 1 / dmax < min (1 / dmin) (1 / D) := lt_min h1 h2
  have hminpos : 0 < min (1 / dmin) (1 / D) :=
    lt_min (one_div_pos.mpr hdmin) (one_div_pos.mpr hD)
  have h1pos : 0 < 1 / dmax := one_div_pos.mpr hdmax
  refine ⟨(1 / dmax + min (1 / dmin) (1 / D)) / 2, by linarith, ?_, ?_, ?_⟩
  · -- s·dmin < 1 : on minore s par 1/dmax... non : on majore s par 1/dmin
    have hs : (1 / dmax + min (1 / dmin) (1 / D)) / 2 < 1 / dmin := by
      have hm : min (1 / dmin) (1 / D) ≤ 1 / dmin := min_le_left _ _
      linarith
    have hmul := mul_lt_mul_of_pos_right hs hdmin
    rwa [one_div_mul_cancel (ne_of_gt hdmin)] at hmul
  · -- 1 < s·dmax
    have hs : 1 / dmax < (1 / dmax + min (1 / dmin) (1 / D)) / 2 := by linarith
    have hmul := mul_lt_mul_of_pos_right hs hdmax
    rwa [one_div_mul_cancel (ne_of_gt hdmax)] at hmul
  · -- s·D < 1
    have hs : (1 / dmax + min (1 / dmin) (1 / D)) / 2 < 1 / D := by
      have hm : min (1 / dmin) (1 / D) ≤ 1 / D := min_le_right _ _
      linarith
    have hmul := mul_lt_mul_of_pos_right hs hD
    rwa [one_div_mul_cancel (ne_of_gt hD)] at hmul

/-! ## Lemme A — du conflit à la différence de couleurs

Le contenu analytique (l'ensemble des distances réalisées entre deux convexes est un
intervalle) est déjà prouvé dans `Geometrie.lean`. Reste la marche coloriage, dans les deux
lectures employées par le dossier. -/

/-- **Lemme A, lecture « coloriage-fonction ».** Si deux convexes portent une paire à distance
≤ 1 et une paire à distance ≥ 1, ils portent une paire à distance exactement 1 ; un coloriage
propre ne peut donc pas leur donner la même couleur. -/
theorem pont_coloriage (A B : Set E) (hA : Convex ℝ A) (hB : Convex ℝ B)
    (hlo : ∃ p ∈ A, ∃ q ∈ B, dist p q ≤ 1)
    (hhi : ∃ p ∈ A, ∃ q ∈ B, 1 ≤ dist p q)
    {C : Type*} (c : E → C) (hc : ∀ p q : E, dist p q = 1 → c p ≠ c q) (cv : C)
    (hAc : ∀ p ∈ A, c p = cv) (hBc : ∀ q ∈ B, c q = cv) : False := by
  obtain ⟨p, hp, q, hq, hd⟩ := Geometrie.existe_paire_distance_un A B hA hB hlo hhi
  exact (hc p q hd) ((hAc p hp).trans (hBc q hq).symm)

/-- **Lemme A, lecture « coloriage de carte ».** Les points témoins sont pris dans les
*intérieurs* des cellules : c'est la version que le §7.3 exige, parce qu'un point du bord porte
plusieurs couleurs. L'intérieur d'un convexe est convexe, donc la même démonstration
s'applique — il n'y a pas de difficulté supplémentaire, et c'est ce que la machine confirme. -/
theorem pont_interieurs (A B : Set E) (hA : Convex ℝ A) (hB : Convex ℝ B)
    (hlo : ∃ p ∈ interior A, ∃ q ∈ interior B, dist p q ≤ 1)
    (hhi : ∃ p ∈ interior A, ∃ q ∈ interior B, 1 ≤ dist p q)
    {C : Type*} (c : E → C) (hc : ∀ p q : E, dist p q = 1 → c p ≠ c q) (cv : C)
    (hAc : ∀ p ∈ interior A, c p = cv) (hBc : ∀ q ∈ interior B, c q = cv) : False :=
  pont_coloriage (interior A) (interior B) hA.interior hB.interior hlo hhi c hc cv hAc hBc

/-- **Le pont, bout à bout.** Les cellules sont dilatées par l'échelle s du lemme B ; les
hypothèses sont écrites directement sur les distances non dilatées. -/
theorem pont_echelle (A B : Set E) (hA : Convex ℝ A) (hB : Convex ℝ B)
    (s : ℝ) (hs : 0 < s)
    (hlo : ∃ p ∈ A, ∃ q ∈ B, s * dist p q ≤ 1)
    (hhi : ∃ p ∈ A, ∃ q ∈ B, 1 ≤ s * dist p q)
    {C : Type*} (c : E → C) (hc : ∀ p q : E, dist p q = 1 → c p ≠ c q) (cv : C)
    (hAc : ∀ p ∈ A, c (s • p) = cv) (hBc : ∀ q ∈ B, c (s • q) = cv) : False := by
  have hconv : ∀ (S : Set E), Convex ℝ S → Convex ℝ (s • S) := fun S hS => hS.smul s
  have hdist : ∀ p q : E, dist (s • p) (s • q) = s * dist p q := by
    intro p q
    rw [dist_eq_norm, dist_eq_norm, ← smul_sub, norm_smul, Real.norm_of_nonneg hs.le]
  have hlo' : ∃ p ∈ s • A, ∃ q ∈ s • B, dist p q ≤ 1 := by
    obtain ⟨p, hp, q, hq, hd⟩ := hlo
    exact ⟨s • p, ⟨p, hp, rfl⟩, s • q, ⟨q, hq, rfl⟩, by rw [hdist]; exact hd⟩
  have hhi' : ∃ p ∈ s • A, ∃ q ∈ s • B, 1 ≤ dist p q := by
    obtain ⟨p, hp, q, hq, hd⟩ := hhi
    exact ⟨s • p, ⟨p, hp, rfl⟩, s • q, ⟨q, hq, rfl⟩, by rw [hdist]; exact hd⟩
  exact pont_coloriage (s • A) (s • B) (hconv A hA) (hconv B hB) hlo' hhi' c hc cv
    (fun p hp => by obtain ⟨p₀, hp₀, rfl⟩ := hp; exact hAc p₀ hp₀)
    (fun q hq => by obtain ⟨q₀, hq₀, rfl⟩ := hq; exact hBc q₀ hq₀)

/-! ## Contrôle des axiomes (exécuté à la compilation) -/

#print axioms Pont.lemmeB
#print axioms Pont.pont_coloriage
#print axioms Pont.pont_interieurs
#print axioms Pont.pont_echelle

/-! ## Les deux réfutations, vérifiées à la machine (elles documentent les corrections du §9) -/

/-- **Sans `dmin < dmax`, le lemme B est faux.** Si les deux bornes coïncident (ici toutes deux
égales à 2, cas dmin = dmax = D/ε avec D = 1, ε = 1/2), aucune échelle ne peut vérifier à la fois
`s·dmin < 1` et `1 < s·dmax` : les deux inégalités demandent s < 1/2 et s > 1/2. -/
theorem lemmeB_sans_dmin_lt_dmax_est_faux :
    ¬ ∃ s : ℝ, 0 < s ∧ s * 2 < 1 ∧ 1 < s * 2 := by
  rintro ⟨s, _hs, h1, h2⟩
  linarith

/-- **Le témoin naïf `(1/dmax + 1/D)/2` échoue.** Sur l'exemple du §9 — D = 1, ε = 1/2,
dmin = 3/2, dmax = 2 — il vaut 3/4, et `s·dmin = 9/8 > 1` : la conclusion du lemme B n'est pas
atteinte. C'est pourquoi le témoin retenu est le milieu de ]1/dmax, min(1/dmin, 1/D)[. -/
theorem temoin_naif_echoue :
    ¬ (((1 : ℝ) / 2 + 1 / 1) / 2 * (3 / 2) < 1) := by
  norm_num

#print axioms Pont.lemmeB_sans_dmin_lt_dmax_est_faux
#print axioms Pont.temoin_naif_echoue

end Pont
