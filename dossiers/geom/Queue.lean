/-
  Queue.lean — le LEMBRE DE LA QUEUE (lemme du pas ⌈h/10⌉), certifié par la machine.

  C'était le dernier texte non machine du dossier : le §6.5 de l'audit le prouvait à la main
  (« cinq faits élémentaires et deux inégalités strictes »). Ce fichier le compile.

  Énoncé. Soit Λ = ℤ(1,0) ⊕ ℤ(g,h) avec |g| ≤ 1/2 et h ≥ 20 ; posons k = ⌈h/10⌉. Alors il existe
  une échelle s > 0 telle que les sept cellules s·V₀, s·V_{(k,0)}, …, s·V_{(6k,0)} soient deux à
  deux en conflit : tout coloriage propre (toute paire à distance 1 a deux couleurs) et constant
  sur chaque cellule doit donner sept couleurs DISTINCTES à ces sept cellules.

  Autrement dit : χ ≥ 7 pour le réseau sΛ, et c'est la queue h → ∞ qui est fermée.

  Ce que la machine change dans la preuve du §6.5 (voir `audit-sv.html`, §6.5 et §9) :
  sur les cinq faits annoncés, un seul est nécessaire — le segment vertical (fait 1). Le pas
  k ≈ h/10 sert uniquement à garantir que l'écart i entre deux des sept cellules vérifie i ≤ h :
  à l'échelle s = 1/h la paire de centres est à distance i/h ≤ 1 et la paire
  (centre, centre ± h/2) est à distance √(i²+h²)/h ≥ 1. Les faits 2 à 5 (contenance, boule de
  rayon 1/2, bornes de dmin, diamètre) servent à la route ε = 999/1000 du §7.3, que ce fichier
  vérifie aussi, en arithmétique pure, mais dont la conclusion n'a pas besoin.
-/
import Mathlib.Analysis.Convex.Topology
import Mathlib.Topology.Order.IntermediateValue
open Set
open scoped Pointwise

namespace Queue

/-! ## 0. Outils : distance au carré, préconnexité, tangence -/

/-- Distance euclidienne au carré dans le plan. Travailler au carré évite toute racine carrée
dans les inégalités, donc tout arrondi. -/
def dist2 (p q : ℝ × ℝ) : ℝ := (p.1 - q.1) ^ 2 + (p.2 - q.2) ^ 2

theorem continuous_dist2 : Continuous (fun z : (ℝ × ℝ) × (ℝ × ℝ) => dist2 z.1 z.2) := by
  unfold dist2
  fun_prop

/-- L'ensemble des distances (au carré) réalisées entre deux convexes est un intervalle. -/
theorem isPreconnected_dist2_set (A B : Set (ℝ × ℝ)) (hA : Convex ℝ A) (hB : Convex ℝ B) :
    IsPreconnected {d : ℝ | ∃ p ∈ A, ∃ q ∈ B, dist2 p q = d} := by
  have hAB : IsPreconnected (A ×ˢ B) := (hA.prod hB).isPreconnected
  have himg := hAB.image (fun z : (ℝ × ℝ) × (ℝ × ℝ) => dist2 z.1 z.2) continuous_dist2.continuousOn
  convert himg using 1
  ext d
  simp [Set.mem_prod, Prod.exists]

/-- **Tangence.** Si deux convexes portent une paire à distance au carré ≤ 1 et une paire à
distance au carré ≥ 1, ils portent une paire à distance exactement 1. Aucun calcul flottant :
c'est le critère d'encadrement du §7.2, transposé ici au plan euclidien en coordonnées. -/
theorem tangence (A B : Set (ℝ × ℝ)) (hA : Convex ℝ A) (hB : Convex ℝ B)
    (hlo : ∃ p ∈ A, ∃ q ∈ B, dist2 p q ≤ 1)
    (hhi : ∃ p ∈ A, ∃ q ∈ B, 1 ≤ dist2 p q) :
    ∃ p ∈ A, ∃ q ∈ B, dist2 p q = 1 := by
  set S : Set ℝ := {d : ℝ | ∃ p ∈ A, ∃ q ∈ B, dist2 p q = d} with hS
  have hpre : IsPreconnected S := isPreconnected_dist2_set A B hA hB
  have hord : OrdConnected S := isPreconnected_iff_ordConnected.mp hpre
  obtain ⟨p, hp, q, hq, hle⟩ := hlo
  obtain ⟨p', hp', q', hq', hge⟩ := hhi
  have h1 : dist2 p q ∈ S := ⟨p, hp, q, hq, rfl⟩
  have h2 : dist2 p' q' ∈ S := ⟨p', hp', q', hq', rfl⟩
  have hiff := (ordConnected_iff (s := S)).mp hord
  have hone : (1 : ℝ) ∈ S :=
    hiff (dist2 p q) h1 (dist2 p' q') h2 (le_trans hle hge) ⟨hle, hge⟩
  obtain ⟨p, hp, q, hq, hd⟩ := hone
  exact ⟨p, hp, q, hq, hd⟩

/-! ## 1. Le réseau Λ = ℤ(1,0) ⊕ ℤ(g,h) et ses cellules -/

/-- Le réseau Λ = ℤ(1,0) ⊕ ℤ(g,h), comme sous-ensemble de ℝ². -/
def Reseau (g h : ℝ) : Set (ℝ × ℝ) :=
  {v | ∃ i j : ℤ, v = ((i : ℝ) + (j : ℝ) * g, (j : ℝ) * h)}

theorem mem_Reseau {g h : ℝ} {v : ℝ × ℝ} :
    v ∈ Reseau g h ↔ ∃ i j : ℤ, v = ((i : ℝ) + (j : ℝ) * g, (j : ℝ) * h) := Iff.rfl

theorem zero_mem (g h : ℝ) : (0, 0) ∈ Reseau g h := ⟨0, 0, by simp⟩

theorem sub_mem {g h : ℝ} {v w : ℝ × ℝ} (hv : v ∈ Reseau g h) (hw : w ∈ Reseau g h) :
    v - w ∈ Reseau g h := by
  obtain ⟨i, j, rfl⟩ := hv
  obtain ⟨i', j', rfl⟩ := hw
  refine ⟨i - i', j - j', ?_⟩
  simp only [Prod.mk_sub_mk]
  push_cast
  ring

theorem centre_mem (g h : ℝ) (i j : ℤ) :
    (((i : ℝ) + (j : ℝ) * g), (j : ℝ) * h) ∈ Reseau g h := ⟨i, j, rfl⟩

/-- **Cellule de Voronoï** de `v` pour Λ : les points au moins aussi proches de `v` que de tout
point du réseau. -/
def cell (g h : ℝ) (v : ℝ × ℝ) : Set (ℝ × ℝ) :=
  {x | ∀ w ∈ Reseau g h, dist2 x v ≤ dist2 x w}

/-- Forme linéaire de la contrainte : c'est ce qui rend les cellules convexes et ce qui permet
de tout faire à l'algèbre linéaire, sans racine carrée. -/
theorem cell_iff (g h : ℝ) (v x : ℝ × ℝ) :
    x ∈ cell g h v ↔
      ∀ w ∈ Reseau g h,
        2 * (x.1 * (w.1 - v.1) + x.2 * (w.2 - v.2)) + (v.1 ^ 2 + v.2 ^ 2) ≤ w.1 ^ 2 + w.2 ^ 2 := by
  simp only [cell, dist2]
  constructor
  · intro h w hw
    have := h w hw
    nlinarith
  · intro h w hw
    have := h w hw
    nlinarith

theorem cell_convex (g h : ℝ) (v : ℝ × ℝ) : Convex ℝ (cell g h v) := by
  intro x hx y hy a b ha hb hab
  rw [cell_iff]
  intro w hw
  rw [cell_iff] at hx hy
  have hxv := hx w hw
  have hyv := hy w hw
  simp only [Prod.smul_fst, Prod.smul_snd, Prod.fst_add, Prod.snd_add, smul_eq_mul]
  nlinarith

theorem centre_in_cell (g h : ℝ) (v : ℝ × ℝ) : v ∈ cell g h v := by
  rw [cell_iff]
  intro w hw
  nlinarith [sq_nonneg (w.1 - v.1), sq_nonneg (w.2 - v.2)]

/-! ## 2. Le seul fait géométrique nécessaire : le segment vertical -/

/-- Étape d'arithmétique : pour `|t| ≤ h/2`, le produit `2t(jh)` est dominé par `|j|h²`. -/
theorem abs_step (t h : ℝ) (hh : 0 ≤ h) (ht : |t| ≤ h / 2) (j : ℤ) :
    2 * t * ((j : ℝ) * h) ≤ |((j : ℝ))| * h ^ 2 := by
  have h1 : 2 * t * ((j : ℝ) * h) ≤ |2 * t * ((j : ℝ) * h)| := le_abs_self _
  have h2 : |2 * t * ((j : ℝ) * h)| = 2 * |t| * |((j : ℝ))| * h := by
    rw [abs_mul, abs_mul, abs_mul, abs_of_nonneg hh]
    ring
  have h3 : 2 * |t| * |((j : ℝ))| * h ≤ 2 * (h / 2) * |((j : ℝ))| * h := by
    have hm : 2 * |t| ≤ 2 * (h / 2) := by linarith
    have h0 : 0 ≤ |((j : ℝ))| * h := by positivity
    nlinarith
  have h4 : 2 * (h / 2) * |((j : ℝ))| * h = |((j : ℝ))| * h ^ 2 := by ring
  rw [h2] at h1
  linarith

theorem int_abs_le_sq (j : ℤ) : |((j : ℝ))| ≤ (j : ℝ) ^ 2 := by
  rcases eq_or_ne j 0 with rfl | hj
  · simp
  · have h1 : (1 : ℤ) ≤ |j| := Int.one_le_abs hj
    have h2 : (1 : ℝ) ≤ ((|j| : ℤ) : ℝ) := by exact_mod_cast h1
    have h3 : ((|j| : ℤ) : ℝ) = |((j : ℝ))| := Int.cast_abs
    rw [h3] at h2
    nlinarith [h2, abs_nonneg ((j : ℝ)), sq_abs ((j : ℝ))]

/-- **Fait 1.** Le segment vertical `v + {0}×[−h/2, h/2]` est dans la cellule de `v`, pour tout
`v` du réseau. C'est le seul fait géométrique dont la preuve du pas a besoin. -/
theorem segment_mem (g h : ℝ) (hh : 0 < h) {v : ℝ × ℝ}
    (hv : v ∈ Reseau g h) {t : ℝ} (ht : |t| ≤ h / 2) : v + (0, t) ∈ cell g h v := by
  rw [cell_iff]
  intro w hw
  have hsub : w - v ∈ Reseau g h := sub_mem hw hv
  obtain ⟨i, j, hwv⟩ := hsub
  have hw1 : w.1 = v.1 + ((i : ℝ) + (j : ℝ) * g) := by
    have := congrArg Prod.fst hwv
    simp only [Prod.fst_sub] at this
    linarith
  have hw2 : w.2 = v.2 + (j : ℝ) * h := by
    have := congrArg Prod.snd hwv
    simp only [Prod.snd_sub] at this
    linarith
  have hstep : 2 * t * ((j : ℝ) * h) ≤ |((j : ℝ))| * h ^ 2 := abs_step t h hh.le ht j
  have hjsq : |((j : ℝ))| * h ^ 2 ≤ ((j : ℝ) * h) ^ 2 := by
    have h1 := int_abs_le_sq j
    nlinarith
  have hsq : ((j : ℝ) * h) ^ 2 ≤ (((i : ℝ) + (j : ℝ) * g) ^ 2 + ((j : ℝ) * h) ^ 2) := by
    nlinarith [sq_nonneg ((i : ℝ) + (j : ℝ) * g)]
  rw [hw1, hw2]
  simp only [Prod.fst_add, Prod.snd_add]
  nlinarith [hstep, hjsq, hsq]

/-! ## 3. Le pas k = ⌈h/10⌉ : l'écart entre deux des sept cellules est ≤ h -/

/-- Le plafond majore : `⌈x⌉ ≥ x`. -/
theorem ceil_ge (x : ℝ) : x ≤ ((⌈x⌉ : ℤ) : ℝ) := Int.le_ceil x

/-- Le plafond est à moins de 1 au-dessus : c'est ce qui borne le pas. -/
theorem ceil_lt (x : ℝ) : ((⌈x⌉ : ℤ) : ℝ) < x + 1 := Int.ceil_lt_add_one x

/-- **Le pas ne dépasse pas h/6** dès que h ≥ 15 : `6⌈h/10⌉ ≤ h`. C'est la seule inégalité
« de comptage » du lemme, et elle remplace les deux inégalités strictes du §6.5. -/
theorem pas_borne (h : ℝ) (hh : 15 ≤ h) : 6 * ((⌈h / 10⌉ : ℤ) : ℝ) ≤ h := by
  have h1 : ((⌈h / 10⌉ : ℤ) : ℝ) < h / 10 + 1 := ceil_lt (h / 10)
  linarith

/-! ## 4. Les deux inégalités du §6.5, vérifiées en arithmétique pure

Elles servent à la route ε = 999/1000 (lemme B, §7.3). La preuve ci-dessus n'en a pas besoin,
mais les nombres du dossier doivent être justes : c'est ce que `lemme_queue.py` vérifiait
exactement, et c'est ici démontré. -/

/-- *Proche* : `ε·i < h` pour tout écart i ≤ 3h/5 + 6, dès h ≥ 20 (le seuil exact est
29970/2003 ≈ 14,96). -/
theorem proche_eps (h : ℝ) (hh : 20 ≤ h) : (999 / 1000) * (3 * h / 5 + 6) < h := by
  nlinarith

/-- *Loin* : `D ≤ ε·dmax` avec D = h + 3/(4h) et dmax ≥ √(101/100)·h — au carré, pour éviter
toute racine : `1 + (h + 3/(4h))² ≤ ε²·(101/100)·h²`, vrai dès h = 20. -/
theorem loin_eps (h : ℝ) (hh : 20 ≤ h) :
    1 + (h + 3 / (4 * h)) ^ 2 ≤ (999 / 1000) ^ 2 * (101 / 100) * h ^ 2 := by
  have hh0 : (0 : ℝ) < h := by linarith
  have hkey : 1 + (h + 3 / (4 * h)) ^ 2 = h ^ 2 + 5 / 2 + 9 / (16 * h ^ 2) := by
    field_simp
    ring
  have hpetit : 9 / (16 * h ^ 2) ≤ 1 / 4 := by
    rw [div_le_iff₀ (by positivity)]
    nlinarith
  rw [hkey]
  nlinarith

/-- Le réel 101/100 est bien `|(g,h)|² ≥ 101/100` quand `i ≥ h/10` : c'est la constante du
§6.5, vérifiée ici comme identité. -/
theorem cent_un (i h : ℝ) (hi : h / 10 ≤ i) (hh : 0 < h) : (101 / 100) * h ^ 2 ≤ i ^ 2 + h ^ 2 := by
  nlinarith

/-! ## 5. Le lemme de la queue : sept cellules deux à deux en conflit -/

/-- Dilater la distance au carré. -/
theorem dist2_smul' (a : ℝ) (p q : ℝ × ℝ) : dist2 (a • p) (a • q) = a ^ 2 * dist2 p q := by
  unfold dist2
  simp only [Prod.smul_fst, Prod.smul_snd, smul_eq_mul]
  ring

/-- Distance au carré entre deux centres sur l'axe. -/
theorem dist2_axe (x y : ℝ) : dist2 ((x, (0 : ℝ))) (y, (0 : ℝ)) = (x - y) ^ 2 := by
  unfold dist2
  norm_num

/-- Distance au carré entre les extrémités hautes du segment vertical de deux cellules. -/
theorem dist2_segment (x y h : ℝ) :
    dist2 (((x, (0 : ℝ)) + (0, h / 2))) ((y, (0 : ℝ)) + (0, -(h / 2))) = (x - y) ^ 2 + h ^ 2 := by
  unfold dist2
  simp only [Prod.fst_add, Prod.snd_add]
  ring

/-- L'écart entre les deux centres vaut, au carré, le carré de l'écart des indices fois le pas. -/
theorem ecart_sq (m n K : ℤ) :
    ((((m * K : ℤ) : ℝ) - ((n * K : ℤ) : ℝ)) ^ 2) = ((((n - m) * K : ℤ) : ℝ) ^ 2) := by
  have h1 : ((m * K : ℤ) : ℝ) - ((n * K : ℤ) : ℝ) = -(((n - m) * K : ℤ) : ℝ) := by
    push_cast
    ring
  rw [h1, neg_sq]

/-- La paire de centres, une fois dilatée par 1/h, est à distance au carré ≤ 1. -/
theorem close_ineq (i h : ℝ) (hi : i ≤ h) (hi0 : 0 ≤ i) (hh : 0 < h) :
    (1 / h) ^ 2 * i ^ 2 ≤ 1 := by
  have hid : (1 / h) ^ 2 * i ^ 2 = (i / h) ^ 2 := by field_simp
  rw [hid]
  have h1 : i / h ≤ 1 := by
    rw [div_le_one hh]
    exact hi
  have h0 : (0 : ℝ) ≤ i / h := div_nonneg hi0 hh.le
  nlinarith

/-- La paire d'extrémités du segment vertical, dilatée par 1/h, est à distance au carré ≥ 1. -/
theorem far_ineq (i h : ℝ) (hh : 0 < h) : 1 ≤ (1 / h) ^ 2 * (i ^ 2 + h ^ 2) := by
  have hid : (1 / h) ^ 2 * (i ^ 2 + h ^ 2) = (i / h) ^ 2 + 1 := by
    field_simp
  rw [hid]
  nlinarith [sq_nonneg (i / h)]

/-- Le segment vertical d'un centre du réseau est dans la cellule de ce centre (forme explicite). -/
theorem mem_segment (g h : ℝ) (hh : 0 < h) (x : ℝ) (t : ℝ)
    (ht : |t| ≤ h / 2) (hx : ((x, (0 : ℝ)) : ℝ × ℝ) ∈ Reseau g h) :
    ((x, (0 : ℝ)) + (0, t)) ∈ cell g h ((x, (0 : ℝ))) :=
  segment_mem g h hh hx ht

/-- **Lemme de la queue (forme machine).** Soit Λ = ℤ(1,0) ⊕ ℤ(g,h) avec h ≥ 20, et
k = ⌈h/10⌉. Il existe une échelle s > 0 telle que, pour tout couple de cellules `m·k` et `n·k`
avec `0 ≤ m < n ≤ 6`, les cellules dilatées `s·V_{m k}` et `s·V_{n k}` portent une paire de points
à distance **exactement** 1.

L'échelle est s = 1/h. La preuve ne demande qu'un fait géométrique — le segment vertical — et une
inégalité de comptage, `6⌈h/10⌉ ≤ h` dès h ≥ 15 : à cette échelle la paire de centres est à
distance `(n−m)k/h ≤ 6k/h ≤ 1`, et la paire « centres ± h/2 » est à distance
`√(((n−m)k)² + h²)/h ≥ 1`. La tangence vient de `tangence` (préconnexité + convexité). -/
theorem queue (g h : ℝ) (hh : 20 ≤ h) :
    ∃ s : ℝ, 0 < s ∧ ∀ (m n : ℤ), 0 ≤ m → m < n → n ≤ 6 →
      ∃ p ∈ s • cell g h (((m * ⌈h / 10⌉ : ℤ) : ℝ), 0),
      ∃ q ∈ s • cell g h (((n * ⌈h / 10⌉ : ℤ) : ℝ), 0), dist2 p q = 1 := by
  have hh0 : (0 : ℝ) < h := by linarith
  have hk0 : (0 : ℤ) ≤ ⌈h / 10⌉ := by
    have h1 : (0 : ℝ) ≤ h / 10 := by linarith
    have h2 : h / 10 ≤ ((⌈h / 10⌉ : ℤ) : ℝ) := ceil_ge (h / 10)
    have h3 : (0 : ℝ) ≤ ((⌈h / 10⌉ : ℤ) : ℝ) := le_trans h1 h2
    exact_mod_cast h3
  have hkborne : 6 * ((⌈h / 10⌉ : ℤ) : ℝ) ≤ h := pas_borne h (by linarith)
  refine ⟨1 / h, by positivity, ?_⟩
  intro m n hm hmn hn6
  have hd0 : (0 : ℤ) ≤ n - m := by omega
  have hdle : n - m ≤ 6 := by omega
  have hi_ge : (0 : ℝ) ≤ (((n - m) * ⌈h / 10⌉ : ℤ) : ℝ) := by
    have h1 : (0 : ℤ) ≤ (n - m) * ⌈h / 10⌉ := Int.mul_nonneg hd0 hk0
    have h2 : ((0 : ℤ) : ℝ) ≤ (((n - m) * ⌈h / 10⌉ : ℤ) : ℝ) := by exact_mod_cast h1
    simpa using h2
  have hi_le : (((n - m) * ⌈h / 10⌉ : ℤ) : ℝ) ≤ h := by
    have h1 : ((n - m) * ⌈h / 10⌉ : ℤ) ≤ (6 * ⌈h / 10⌉ : ℤ) :=
      Int.mul_le_mul_of_nonneg_right hdle hk0
    have h2 : (((n - m) * ⌈h / 10⌉ : ℤ) : ℝ) ≤ ((6 * ⌈h / 10⌉ : ℤ) : ℝ) := by exact_mod_cast h1
    have h3 : ((6 * ⌈h / 10⌉ : ℤ) : ℝ) = 6 * ((⌈h / 10⌉ : ℤ) : ℝ) := by push_cast; ring
    linarith
  have hA : Convex ℝ ((1 / h) • cell g h (((m * ⌈h / 10⌉ : ℤ) : ℝ), (0 : ℝ))) :=
    (cell_convex g h _).smul (1 / h)
  have hB : Convex ℝ ((1 / h) • cell g h (((n * ⌈h / 10⌉ : ℤ) : ℝ), (0 : ℝ))) :=
    (cell_convex g h _).smul (1 / h)
  refine tangence _ _ hA hB ?_ ?_
  · -- paire proche : les deux centres
    refine ⟨(1 / h) • ((((m * ⌈h / 10⌉ : ℤ) : ℝ), (0 : ℝ)) : ℝ × ℝ), ⟨_, centre_in_cell g h _, rfl⟩,
      (1 / h) • ((((n * ⌈h / 10⌉ : ℤ) : ℝ), (0 : ℝ)) : ℝ × ℝ), ⟨_, centre_in_cell g h _, rfl⟩, ?_⟩
    rw [dist2_smul', dist2_axe, ecart_sq]
    exact close_ineq _ h hi_le hi_ge hh0
  · -- paire lointaine : les extrémités du segment vertical
    have hxa : ((((m * ⌈h / 10⌉ : ℤ) : ℝ), (0 : ℝ)) : ℝ × ℝ) ∈ Reseau g h :=
      by simpa using centre_mem g h (m * ⌈h / 10⌉) 0
    have hxb : ((((n * ⌈h / 10⌉ : ℤ) : ℝ), (0 : ℝ)) : ℝ × ℝ) ∈ Reseau g h :=
      by simpa using centre_mem g h (n * ⌈h / 10⌉) 0
    have hhalf : |h / 2| ≤ h / 2 := by
      rw [abs_le]; constructor <;> linarith
    have hpa : ((((m * ⌈h / 10⌉ : ℤ) : ℝ), (0 : ℝ)) + (0, h / 2)) ∈
        cell g h (((m * ⌈h / 10⌉ : ℤ) : ℝ), (0 : ℝ)) :=
      mem_segment g h hh0 _ (h / 2) hhalf hxa
    have hpb : ((((n * ⌈h / 10⌉ : ℤ) : ℝ), (0 : ℝ)) + (0, -(h / 2))) ∈
        cell g h (((n * ⌈h / 10⌉ : ℤ) : ℝ), (0 : ℝ)) :=
      mem_segment g h hh0 _ (-(h / 2)) (by rw [abs_neg]; exact hhalf) hxb
    refine ⟨(1 / h) • ((((m * ⌈h / 10⌉ : ℤ) : ℝ), (0 : ℝ)) + (0, h / 2)), ⟨_, hpa, rfl⟩,
      (1 / h) • ((((n * ⌈h / 10⌉ : ℤ) : ℝ), (0 : ℝ)) + (0, -(h / 2))), ⟨_, hpb, rfl⟩, ?_⟩
    rw [dist2_smul', dist2_segment, ecart_sq]
    exact far_ineq _ h hh0

/-! ## 6. La conséquence coloriage : sept couleurs sont nécessaires -/

/-- **Sept couleurs.** Pour tout réseau du domaine avec h ≥ 20, il existe une échelle s > 0 telle
que tout coloriage propre du plan (toute paire à distance 1 a deux couleurs différentes) qui est
constant sur chacune des sept cellules `s·V_{jk}`, j = 0,…,6, doit donner sept couleurs
**distinctes** à ces cellules. C'est exactement χ ≥ 7 pour le réseau sΛ, sans exception de
queue. -/
theorem sept_couleurs (g h : ℝ) (hh : 20 ≤ h) {C : Type*} (c : ℝ × ℝ → C)
    (hc : ∀ p q : ℝ × ℝ, dist2 p q = 1 → c p ≠ c q) :
    ∃ s : ℝ, 0 < s ∧ ∀ (col : Fin 7 → C),
      (∀ (j : Fin 7) (p : ℝ × ℝ), p ∈ s • cell g h ((((j : ℤ) * ⌈h / 10⌉ : ℤ) : ℝ), 0) →
        c p = col j) →
      Function.Injective col := by
  obtain ⟨s, hs, hqueue⟩ := queue g h hh
  refine ⟨s, hs, ?_⟩
  intro col hcol
  intro a b hab
  by_contra hne
  rcases lt_or_gt_of_ne hne with hlt | hlt
  · -- a < b
    have ha0 : 0 ≤ (a : ℤ) := by exact_mod_cast Nat.zero_le a.val
    have hb6 : (b : ℤ) ≤ 6 := by
      have : b.val ≤ 6 := by omega
      exact_mod_cast this
    obtain ⟨p, hp, q, hq, hd⟩ := hqueue (a : ℤ) (b : ℤ) ha0 (by exact_mod_cast hlt) hb6
    have h1 : c p = col a := hcol a p hp
    have h2 : c q = col b := hcol b q hq
    exact (hc p q hd) (by rw [h1, h2]; exact hab)
  · have hb0 : 0 ≤ (b : ℤ) := by exact_mod_cast Nat.zero_le b.val
    have ha6 : (a : ℤ) ≤ 6 := by
      have : a.val ≤ 6 := by omega
      exact_mod_cast this
    obtain ⟨p, hp, q, hq, hd⟩ := hqueue (b : ℤ) (a : ℤ) hb0 (by exact_mod_cast hlt) ha6
    have h1 : c p = col b := hcol b p hp
    have h2 : c q = col a := hcol a q hq
    exact (hc p q hd) (by rw [h1, h2]; exact hab.symm)

/-! ## 7. Contrôle des axiomes (exécuté à la compilation) -/

#print axioms Queue.pas_borne
#print axioms Queue.proche_eps
#print axioms Queue.loin_eps
#print axioms Queue.queue
#print axioms Queue.sept_couleurs

end Queue
