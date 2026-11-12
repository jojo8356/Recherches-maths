//! Construction du gabarit (jeu d'offsets formant une clique) en temps O(log h).
//!
//! Le point clé de complexité
//! --------------------------
//! Le code Python énumérait une fenêtre |i| ≤ τ+3, |j| ≤ 2 puis testait toutes les
//! paires : O(h²) tests de conflit (413 s pour la fenêtre h ∈ [20,100]). Or on n'a
//! jamais besoin de *tout* le graphe : il suffit d'une clique de 7 à 9 sommets.
//!
//! Trois réductions, cumulées :
//!
//! 1. **Condition nécessaire d'anneau.** Un conflit exige
//!        dmin ≤ D  ⟹  |d| ≤ 2D      et      dmax ≥ D/ε  ⟹  |d| ≥ D/ε − D.
//!    Les offsets utiles vivent donc dans un anneau, et pour chaque rangée j
//!    (|j| ≤ 3 suffit : |d| ≤ 2D et |b₂| ≥ h ⟹ |j| ≤ 2D/h + 1 ≈ 2/ε + 1) l'ensemble
//!    des i en conflit est un INTERVALLE [i₁, i₂].
//!
//! 2. **Dichotomie.** Pour j fixé, k ↦ dmax²(k·b₁ + j·b₂) est convexe et 0 ∈ K,
//!    donc dmax² est croissante en k ≥ 0 : « ε·dmax ≥ D » est un prédicat MONOTONE
//!    et le plus petit décalage en conflit se trouve par dichotomie en O(log D).
//!
//! 3. **Invariance par translation.** Deux cellules d'une même rangée séparées de k
//!    se testent par conflict(k, 0) : le pas k₁ vaut donc le même pour toutes les
//!    rangées, et le nombre de places dans une rangée vaut ≈ (i₂−i₁)/k₁ + 1, qui
//!    est ≈ 1/√(1−ε²) — indépendant de h. D'où O(1) candidats par rangée.
//!
//! Total : O(log h) tests de conflit, puis O(k²) vérifications exactes pour k ≤ 9.

use crate::geom::{Cell, CellF, Rat, Test, TestF};
use crate::graph::{max_clique, Graph};

pub struct Gabarit {
    pub clique: Vec<(i128, i128)>,
    pub omega_local: usize,
    pub k1: i128,
    pub rows: Vec<i128>,
}

/// Fenêtre [k₁, k₂] des pas en conflit, sur la variante flottante.
///
/// Deux prédicats MONOTONES, donc deux dichotomies en O(log D) :
///   P₁(k) = [ε·dmax(k·b₁) ≥ D]   croissant (0 ∈ K ⟹ dmax² convexe, minimum en k = 0) ;
///   P₂(k) = [dmin(k·b₁) ≤ D]     décroissant (distance à un convexe contenant 0, le long
///                                 d'un rayon : croissante).
/// Les k en conflit forment donc exactement l'intervalle [k₁, k₂], et k₁ est le pas de la
/// rangée — c'est lui qui remplace l'énumération en O(h) du code Python.
pub fn fenetre_pas(t: &TestF) -> Option<(i128, i128)> {
    let diam = t.cell.diam2.sqrt();
    let k_hi = (2.0 * diam).floor() as i128 + 2;
    let p1 = |k: i128| -> bool {
        let d = t.cell.offset(k, 0);
        t.eps * t.eps * t.dmax2(d) >= t.cell.diam2
    };
    let p2 = |k: i128| -> bool {
        let d = t.cell.offset(k, 0);
        t.dmin2(d) <= t.cell.diam2
    };
    if !p1(k_hi) || !p2(1) {
        return None;
    }
    let (mut lo, mut hi) = (1i128, k_hi);
    while lo < hi {
        let m = (lo + hi) / 2;
        if p1(m) {
            hi = m;
        } else {
            lo = m + 1;
        }
    }
    let k1 = lo;
    if !p2(k1) {
        return None;
    }
    let k2 = if p2(k_hi) {
        k_hi
    } else {
        let (mut a, mut b) = (k1, k_hi);
        while a < b {
            let m = (a + b + 1) / 2;
            if p2(m) {
                a = m;
            } else {
                b = m - 1;
            }
        }
        a
    };
    Some((k1, k2))
}

/// Construit une clique d'au moins `want` sommets en temps O(log h) + O(1).
pub fn construire(t: &TestF, want: usize) -> Option<Gabarit> {
    let dbg = std::env::var("GABARIT_DEBUG").is_ok();
    let (k1, k2) = fenetre_pas(t)?;
    if dbg {
        eprintln!("[gabarit] k1 = {}, k2 = {}, diam = {:.6}", k1, k2, t.cell.diam2.sqrt());
    }

    // Candidats : dans chaque rangée j, l'ensemble des i en conflit avec 0 est un
    // intervalle contenu dans [−k₂, k₂] ; on l'échantillonne au pas k₁. Le nombre de
    // points vaut O(k₂/k₁) = O(1/√(1−ε²)) — INDÉPENDANT de h.
    let mut cands: Vec<(i128, i128)> = vec![(0, 0)];
    let mut rows: Vec<i128> = Vec::new();
    let n_slots = (k2 / k1.max(1)) as usize + 2;
    for j in -3i128..=3i128 {
        let mut added = 0;
        for m in 0..=n_slots {
            let base = m as i128 * k1;
            for signe in [-1i128, 1i128] {
                for delta in [-1i128, 0, 1] {
                    let ii = signe * base + delta;
                    if (ii, j) == (0, 0) {
                        continue;
                    }
                    if t.conflict(ii, j) && !cands.contains(&(ii, j)) {
                        cands.push((ii, j));
                        added += 1;
                    }
                }
            }
        }
        if added > 0 {
            rows.push(j);
        }
    }
    if cands.len() < 2 {
        return None;
    }

    // Glouton : O(|c|·want) tests de conflit.
    let mut glouton: Vec<(i128, i128)> = vec![(0, 0)];
    for &c in cands.iter() {
        if glouton.len() >= want {
            break;
        }
        if c == (0, 0) {
            continue;
        }
        if glouton.iter().all(|&a| t.conflict(c.0 - a.0, c.1 - a.1)) {
            glouton.push(c);
        }
    }
    // 7 suffit pour le certificat ; `want` (9) n'est qu'une marge. On rend donc le
    // meilleur résultat utilisable dès qu'il atteint 7.
    if glouton.len() >= want.min(7) {
        return Some(Gabarit { omega_local: glouton.len(), clique: glouton, k1, rows });
    }
    if dbg {
        eprintln!("[gabarit] glouton = {} sommets seulement", glouton.len());
    }
    None
}

/// ω exact par énumération dense, avec la MÊME fenêtre que le code Python
/// (ni = ⌊√(D²(1+1/ε)²)⌋ + 3, |j| ≤ 2). Sert de contrôle croisé.
pub fn omega_dense(t: &Test) -> (usize, Vec<(i128, i128)>) {
    let dd = t.cell.dd as f64;
    let diam = (t.cell.diam2 as f64).sqrt() / dd;
    let eps = (t.en2 as f64).sqrt() / (t.ed2 as f64).sqrt();
    let cible2 = diam * diam * (1.0 / eps + 1.0) * (1.0 / eps + 1.0);
    let ni = (cible2.sqrt().floor() as i128) + 3;
    let cible2_int = (cible2 * dd * dd * 1.0000001).ceil() as i128;

    let mut offs: Vec<(i128, i128)> = Vec::new();
    for i in -ni..=ni {
        for j in -2i128..=2i128 {
            offs.push((i, j));
        }
    }
    let n = offs.len();
    let mut g = Graph::new(n);
    let mut n_edges = 0usize;
    for a in 0..n {
        for b in (a + 1)..n {
            let d = (offs[b].0 - offs[a].0, offs[b].1 - offs[a].1);
            let dv = t.cell.offset(d.0, d.1);
            if dv.0 * dv.0 + dv.1 * dv.1 > cible2_int {
                continue; // pré-filtre de norme, comme le code Python
            }
            if t.conflict(d.0, d.1) {
                g.link(a, b);
                n_edges += 1;
            }
        }
    }
    if std::env::var("GABARIT_DEBUG").is_ok() {
        eprintln!("[dense] n = {}, arêtes = {}, ni = {}", n, n_edges, ni);
    }
    // deux quantités distinctes, souvent confondues à tort :
    //   ω  = clique maximale du graphe entier
    //   ω0 = clique maximale contenant 0 (sous-graphe induit par {0} ∪ N(0))
    let cl = max_clique(&g, 30_000_000);
    let zero = offs.iter().position(|&o| o == (0, 0)).unwrap();
    let mut keep: Vec<usize> = vec![zero];
    for v in 0..n {
        if v != zero && g.are_linked(zero, v) {
            keep.push(v);
        }
    }
    let (sub, map) = g.induced(&keep);
    let mut cl0 = max_clique(&sub, 30_000_000);
    cl0.sort();
    if std::env::var("GABARIT_DEBUG").is_ok() {
        eprintln!("[dense] n = {}, arêtes = {}, ω = {}, ω(avec 0) = {}", n, n_edges, cl.len(), cl0.len());
    }
    let res: Vec<(i128, i128)> = cl0.iter().map(|&k| offs[map[k]]).collect();
    (res.len(), res)
}

/// Vérification indépendante d'un conflit : distance polygone-polygone directe,
/// sans passer par le corps de différences (contrôle du contrôle).
pub fn conflit_direct(cell: &Cell, t: &Test, di: i128, dj: i128) -> bool {
    let d = cell.offset(di, dj);
    let n = cell.verts.len();
    // dmax² : max sur les couples de sommets (V, V+d)
    let mut dmax2: i128 = 0;
    for p in cell.verts.iter() {
        for q in cell.verts.iter() {
            let x = q.0 + d.0 - p.0;
            let y = q.1 + d.1 - p.1;
            let v = x * x + y * y;
            if v > dmax2 {
                dmax2 = v;
            }
        }
    }
    // dmin² : 0 si les polygones s'intersectent, sinon min des distances sommet-arête
    let mut dmin2 = (i128::MAX, 1i128);
    // test d'intersection : un sommet de l'un dans l'autre, ou arêtes qui se croisent
    let inside = |p: (i128, i128), poly: &Vec<(i128, i128)>| -> bool {
        let mut sign = 0i32;
        for k in 0..poly.len() {
            let a = poly[k];
            let b = poly[(k + 1) % poly.len()];
            let cr = (b.0 - a.0) * (p.1 - a.1) - (b.1 - a.1) * (p.0 - a.0);
            let s = if cr > 0 {
                1
            } else if cr < 0 {
                -1
            } else {
                0
            };
            if s != 0 {
                if sign == 0 {
                    sign = s;
                } else if sign != s {
                    return false;
                }
            }
        }
        true
    };
    let dec: Vec<(i128, i128)> = cell.verts.iter().map(|p| (p.0 + d.0, p.1 + d.1)).collect();
    let mut inter = cell.verts.iter().any(|&p| inside(p, &dec))
        || dec.iter().any(|&p| inside(p, &cell.verts));
    // croisements d'arêtes
    let seg_int = |a1: (i128, i128), a2: (i128, i128), b1: (i128, i128), b2: (i128, i128)| {
        let o = |p: (i128, i128), q: (i128, i128), r: (i128, i128)| {
            (q.0 - p.0) * (r.1 - p.1) - (q.1 - p.1) * (r.0 - p.0)
        };
        let d1 = o(a1, a2, b1);
        let d2 = o(a1, a2, b2);
        let d3 = o(b1, b2, a1);
        let d4 = o(b1, b2, a2);
        (d1.signum() != d2.signum()) && (d3.signum() != d4.signum())
    };
    if !inter {
        for k in 0..n {
            for l in 0..n {
                if seg_int(
                    cell.verts[k],
                    cell.verts[(k + 1) % n],
                    dec[l],
                    dec[(l + 1) % n],
                ) {
                    inter = true;
                }
            }
        }
    }
    if inter {
        return t.en2 * 0 <= t.ed2 * cell.diam2 && t.ed2 * cell.diam2 <= t.en2 * dmax2;
    }
    for k in 0..n {
        for poly in [&cell.verts, &dec] {
            for p in poly.iter() {
                let a = cell.verts[k];
                let b = cell.verts[(k + 1) % n];
                let (num, den) = seg_dist2_pub(*p, a, b);
                if dmin2.0 == i128::MAX || num * dmin2.1 < dmin2.0 * den {
                    dmin2 = (num, den);
                }
            }
        }
    }
    let (num, den) = dmin2;
    t.en2 * num <= t.ed2 * cell.diam2 * den && t.ed2 * cell.diam2 <= t.en2 * dmax2
}

pub fn seg_dist2_pub(p: (i128, i128), a: (i128, i128), b: (i128, i128)) -> (i128, i128) {
    let ab = (b.0 - a.0, b.1 - a.1);
    let ap = (p.0 - a.0, p.1 - a.1);
    let num = ap.0 * ab.0 + ap.1 * ab.1;
    let den = ab.0 * ab.0 + ab.1 * ab.1;
    if num <= 0 {
        return (ap.0 * ap.0 + ap.1 * ap.1, 1);
    }
    if num >= den {
        let bp = (p.0 - b.0, p.1 - b.1);
        return (bp.0 * bp.0 + bp.1 * bp.1, 1);
    }
    let ap2 = ap.0 * ap.0 + ap.1 * ap.1;
    (ap2 * den - num * num, den)
}

/// Rationnel = entier / dd, pour la sortie JSON.
pub fn rat_dd(n: i128, dd: i128) -> Rat {
    Rat::new(n, dd)
}
