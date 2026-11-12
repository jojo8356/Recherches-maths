//! Arithmétique exacte et géométrie de la cellule de Voronoï d'un réseau.
//!
//! Tout est calculé en **entiers** dans un repère mis à l'échelle une fois pour toutes
//! (`dd`). Aucune division en virgule flottante n'intervient dans une décision : la
//! virgule flottante ne sert qu'à *suggérer* des candidats, jamais à les valider.
//!
//! Les idées de complexité, dans l'ordre où elles payent :
//!
//! 1. **Corps de différences.** Pour deux cellules translatées V et V + d,
//!      dmin(V, V+d) = dist(d, V − V),      dmax(V, V+d) = max_{z ∈ V−V} |z − d|.
//!    Le polygone K = V − V ne dépend QUE du réseau : on le calcule une fois (O(1)),
//!    puis chaque test de conflit coûte O(#sommets de K) = O(6) au lieu d'un calcul
//!    polygone-polygone en O(6 × 6). C'est la mémoïsation structurelle du problème.
//!
//! 2. **Vecteurs pertinents de Voronoï.** Pour une base réduite (|g| ≤ 1/2, h ≥ √3/2),
//!    les facettes de V sont portées par ±b₁, ±b₂, ±(b₁±b₂) : quatre paires au plus.
//!    Inutile d'énumérer les vecteurs du réseau jusqu'à 4h² comme le fait le code
//!    Python — c'est O(h) candidats pour rien.
//!
//! 3. **Repère entier.** Sommets de V et de K, vecteurs du réseau, offsets : tout est
//!    ramené à des entiers d'un même repère. Le conflit est alors une comparaison
//!    croisée d'entiers, sans pgcd ni division dans la boucle chaude.

use std::cmp::Ordering;

fn gcd(mut a: i128, mut b: i128) -> i128 {
    a = a.abs();
    b = b.abs();
    while b != 0 {
        let t = a % b;
        a = b;
        b = t;
    }
    a
}

pub fn lcm(a: i128, b: i128) -> i128 {
    if a == 0 || b == 0 {
        return 0;
    }
    (a / gcd(a, b)).checked_mul(b).expect("lcm : dépassement i128")
}

/// Rationnel exact, toujours normalisé (dénominateur > 0, pgcd = 1).
#[derive(Clone, Copy, Debug)]
pub struct Rat {
    pub n: i128,
    pub d: i128,
}

impl Rat {
    pub fn new(n: i128, d: i128) -> Rat {
        assert!(d != 0, "dénominateur nul");
        let s = if d < 0 { -1i128 } else { 1i128 };
        let g = gcd(n, d).max(1);
        Rat { n: s * n / g, d: s * d / g }
    }
    pub fn int(n: i128) -> Rat {
        Rat { n, d: 1 }
    }
    pub fn zero() -> Rat {
        Rat { n: 0, d: 1 }
    }
    pub fn add(self, o: Rat) -> Rat {
        Rat::new(self.n * o.d + o.n * self.d, self.d * o.d)
    }
    pub fn sub(self, o: Rat) -> Rat {
        Rat::new(self.n * o.d - o.n * self.d, self.d * o.d)
    }
    pub fn mul(self, o: Rat) -> Rat {
        Rat::new(self.n * o.n, self.d * o.d)
    }
    pub fn div(self, o: Rat) -> Rat {
        Rat::new(self.n * o.d, self.d * o.n)
    }
    pub fn neg(self) -> Rat {
        Rat { n: -self.n, d: self.d }
    }
    pub fn to_f64(self) -> f64 {
        self.n as f64 / self.d as f64
    }
    pub fn is_zero(self) -> bool {
        self.n == 0
    }
}

impl PartialEq for Rat {
    fn eq(&self, o: &Self) -> bool {
        self.n == o.n && self.d == o.d
    }
}
impl Eq for Rat {}
impl PartialOrd for Rat {
    fn partial_cmp(&self, o: &Self) -> Option<Ordering> {
        Some(self.cmp(o))
    }
}
impl Ord for Rat {
    fn cmp(&self, o: &Self) -> Ordering {
        (self.n * o.d).cmp(&(o.n * self.d))
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct R2 {
    pub x: Rat,
    pub y: Rat,
}

impl R2 {
    pub fn new(x: Rat, y: Rat) -> R2 {
        R2 { x, y }
    }
    pub fn add(self, o: R2) -> R2 {
        R2::new(self.x.add(o.x), self.y.add(o.y))
    }
    pub fn sub(self, o: R2) -> R2 {
        R2::new(self.x.sub(o.x), self.y.sub(o.y))
    }
    pub fn dot(self, o: R2) -> Rat {
        self.x.mul(o.x).add(self.y.mul(o.y))
    }
    pub fn cross(self, o: R2) -> Rat {
        self.x.mul(o.y).sub(self.y.mul(o.x))
    }
    pub fn norm2(self) -> Rat {
        self.dot(self)
    }
    pub fn scale(self, k: Rat) -> R2 {
        R2::new(self.x.mul(k), self.y.mul(k))
    }
    pub fn to_f64(self) -> (f64, f64) {
        (self.x.to_f64(), self.y.to_f64())
    }
}

/// Géométrie d'une cellule de Voronoï, tout en entiers dans un repère d'échelle `dd`.
///
/// Convention : un point de coordonnées rationnelles (px, py) est stocké en entier
/// (px·dd, py·dd). Deux cellules décalées de d (entier) sont testées via le corps de
/// différences `kverts` (lui aussi à l'échelle dd).
#[derive(Clone, Debug)]
pub struct Cell {
    pub dd: i128,
    pub b1: (i128, i128),
    pub b2: (i128, i128),
    /// sommets de V, à l'échelle dd
    pub verts: Vec<(i128, i128)>,
    /// mêmes sommets, rationnels (pour la sortie JSON)
    pub verts_rat: Vec<R2>,
    /// sommets de K = V − V
    pub kverts: Vec<(i128, i128)>,
    /// diamètre² de la cellule, à l'échelle dd²
    pub diam2: i128,
    /// normales des facettes (vecteurs du réseau porteurs), à l'échelle dd
    pub facets: Vec<(i128, i128)>,
    /// vecteurs (i, j) de réseau, à l'échelle dd (pour les contraintes de `paires`)
    pub cons: Vec<((i128, i128), (i128, i128), i128)>, // (ij, vecteur, |v|²)
}

fn det2(a: (i128, i128), b: (i128, i128)) -> i128 {
    a.0 * b.1 - a.1 * b.0
}

impl Cell {
    pub fn build(g: Rat, h: Rat) -> Cell {
        // --- base réduite : b1 = (1, 0), b2 = (g, h)
        let b1 = R2::new(Rat::int(1), Rat::zero());
        let b2 = R2::new(g, h);
        // --- vecteurs candidats (théorème de Voronoï pour une base réduite)
        let cand_ij: [(i128, i128); 8] = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, -1), (-1, 1), (1, 1), (-1, -1),
        ];
        let cand: Vec<((i128, i128), R2, Rat)> = cand_ij
            .iter()
            .map(|&(i, j)| {
                let v = b1.scale(Rat::int(i)).add(b2.scale(Rat::int(j)));
                ((i, j), v, v.norm2())
            })
            .collect();

        // --- sommets de V : intersections des droites 2⟨x,v⟩ = |v|²
        let mut verts: Vec<R2> = Vec::new();
        for a in 0..cand.len() {
            for b in (a + 1)..cand.len() {
                let (va, na) = (cand[a].1, cand[a].2);
                let (vb, nb) = (cand[b].1, cand[b].2);
                let d = va.cross(vb);
                if d.is_zero() {
                    continue;
                }
                // x = (na·vb_y − nb·va_y, va_x·nb − vb_x·na) / (2·det)
                let two_d = d.mul(Rat::int(2));
                let x = R2::new(
                    na.mul(vb.y).sub(nb.mul(va.y)).div(two_d),
                    va.x.mul(nb).sub(vb.x.mul(na)).div(two_d),
                );
                // faisable pour toutes les contraintes ?
                let ok = cand.iter().all(|c| {
                    x.dot(c.1).mul(Rat::int(2)).cmp(&c.2) != Ordering::Greater
                });
                if ok && !verts.iter().any(|w| *w == x) {
                    verts.push(x);
                }
            }
        }
        assert!(verts.len() >= 3, "cellule dégénérée (réseau de rang 1 ?)");
        // tri par angle
        verts.sort_by(|p, q| {
            let ap = p.y.to_f64().atan2(p.x.to_f64());
            let aq = q.y.to_f64().atan2(q.x.to_f64());
            ap.partial_cmp(&aq).unwrap()
        });

        // --- facettes : contraintes tendues en au moins deux sommets
        let mut facets: Vec<(i128, i128)> = Vec::new();
        for c in cand.iter() {
            let tight = verts
                .iter()
                .filter(|x| x.dot(c.1).mul(Rat::int(2)) == c.2)
                .count();
            if tight >= 2 {
                let f = c.1;
                let key = (f.x.n * f.y.d, f.y.n * f.x.d); // direction, signe inclus
                let _ = key;
                // on garde une seule fois chaque paire ±v : on stocke tout, K gère les ±
                facets.push(c.0);
                // (on ne stocke pas le vecteur ici ; il sera reconstruit après l'échelle)
                let _ = f;
            }
        }
        // les facettes doivent venir par paires ±v : on garde les paires
        facets.retain(|ij| {
            let opp = (-ij.0, -ij.1);
            // garder (1,0) plutôt que (-1,0) : ordre lexicographique sur la paire
            *ij < opp
        });
        assert!(facets.len() >= 2, "moins de deux paires de facettes");

        // --- corps de différences K = { z : |⟨z,v⟩| ≤ |v|² pour tout v facette }
        // contraintes : 2·|facettes| demi-plans
        let mut cons_k: Vec<(R2, Rat)> = Vec::new(); // ⟨z, n⟩ ≤ c
        for &(i, j) in facets.iter() {
            let v = b1.scale(Rat::int(i)).add(b2.scale(Rat::int(j)));
            let n = v.norm2();
            cons_k.push((v, n));
            cons_k.push((v.scale(Rat::int(-1)), n));
        }
        let mut kverts: Vec<R2> = Vec::new();
        for a in 0..cons_k.len() {
            for b in (a + 1)..cons_k.len() {
                let (na, ca) = cons_k[a];
                let (nb, cb) = cons_k[b];
                let d = na.cross(nb);
                if d.is_zero() {
                    continue;
                }
                let x = R2::new(
                    ca.mul(nb.y).sub(cb.mul(na.y)).div(d),
                    na.x.mul(cb).sub(nb.x.mul(ca)).div(d),
                );
                let ok = cons_k
                    .iter()
                    .all(|(n, c)| x.dot(*n).cmp(c) != Ordering::Greater);
                if ok && !kverts.iter().any(|w| *w == x) {
                    kverts.push(x);
                }
            }
        }
        assert!(kverts.len() >= 4, "corps de différences dégénéré");

        // --- échelle commune
        let mut dd: i128 = 1;
        for p in verts.iter().chain(kverts.iter()) {
            dd = lcm(dd, p.x.d);
            dd = lcm(dd, p.y.d);
        }
        dd = lcm(dd, g.d);
        dd = lcm(dd, h.d);

        // garde-fou : au-delà, les produits d'entiers pourraient dépasser i128 et
        // (en release, sans overflow-checks) déborder SILENCIEUSEMENT.
        let ampleur = dd.saturating_mul(h.n / h.d).saturating_mul(4);
        assert!(
            ampleur < 1_000_000_000_000,
            "réseau hors de portée de l'arithmétique i128 (dd·h = {}) : réduire h",
            ampleur
        );

        let to_int = |p: R2| -> (i128, i128) {
            (p.x.n * (dd / p.x.d), p.y.n * (dd / p.y.d))
        };
        let verts_i: Vec<(i128, i128)> = verts.iter().map(|p| to_int(*p)).collect();
        let kverts_i: Vec<(i128, i128)> = kverts.iter().map(|p| to_int(*p)).collect();
        let b1_i = (dd, 0);
        let b2_i = (g.n * (dd / g.d), h.n * (dd / h.d));

        let cons: Vec<((i128, i128), (i128, i128), i128)> = Vec::new(); // rempli à la demande

        let facets_i: Vec<(i128, i128)> = facets
            .iter()
            .map(|&(i, j)| (i * b1_i.0 + j * b2_i.0, i * b1_i.1 + j * b2_i.1))
            .collect();

        // --- diamètre² = max |z|² sur K (fonction convexe ⇒ atteinte aux sommets)
        let mut diam2: i128 = 0;
        for z in kverts_i.iter() {
            let v = z.0 * z.0 + z.1 * z.1;
            if v > diam2 {
                diam2 = v;
            }
        }

        Cell {
            dd,
            b1: b1_i,
            b2: b2_i,
            verts: verts_i,
            verts_rat: verts,
            kverts: kverts_i,
            diam2,
            facets: facets_i,
            cons,
        }
    }

    /// Contraintes tendues possibles : les huit vecteurs de Voronoï suffisent, puisque
    /// le test d'égalité est exact (aucune tolérance). Le code Python énumérait |v|² ≤ 4h²,
    /// soit O(h) vecteurs, pour retrouver au plus douze contraintes utiles.
    pub fn cons_utiles(&self) -> Vec<((i128, i128), (i128, i128), i128)> {
        let cand: [(i128, i128); 8] = [
            (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1), (1, 1), (-1, -1),
        ];
        cand.iter()
            .map(|&(i, j)| {
                let v = self.offset(i, j);
                ((i, j), v, v.0 * v.0 + v.1 * v.1)
            })
            .collect()
    }

    /// Milieux de Delaunay dans la fenêtre |i|,|j| ≤ 6 : O(1) en h (la borne verticale
    /// est 2|w|/h ≤ 14/h, la borne horizontale |i| ≤ 14).
    pub fn mids(&self, fen: i128) -> Vec<(i128, i128)> {
        let mut out = vec![(0, 0)];
        for i in -fen..=fen {
            for j in -fen..=fen {
                if i == 0 && j == 0 {
                    continue;
                }
                let wi = self.offset(i, j);
                let nw2 = wi.0 * wi.0 + wi.1 * wi.1;
                let lim = 4 * nw2 + 4 * self.dd * self.dd;
                let mut ok = true;
                for k in -14i128..=14i128 {
                    for l in -14i128..=14i128 {
                        if k == 0 && l == 0 {
                            continue;
                        }
                        let v = self.offset(k, l);
                        let n2 = v.0 * v.0 + v.1 * v.1;
                        if n2 > lim {
                            continue;
                        }
                        // w/2 ∈ V  ⟺  ⟨w, v⟩ ≤ |v|²  (PAS 2⟨w,v⟩ : le facteur 2 est déjà dans la définition)
                        if wi.0 * v.0 + wi.1 * v.1 > n2 {
                            ok = false;
                            break;
                        }
                    }
                    if !ok {
                        break;
                    }
                }
                if ok {
                    out.push((i, j));
                }
            }
        }
        out
    }

    /// Vecteur du réseau (i, j), à l'échelle dd.
    #[inline]
    pub fn offset(&self, i: i128, j: i128) -> (i128, i128) {
        (i * self.b1.0 + j * self.b2.0, i * self.b1.1 + j * self.b2.1)
    }

    /// dmin²(V, V+d) = dist²(d, K), en unités de dd², exact.
    pub fn dmin2(&self, d: (i128, i128)) -> (i128, i128) {
        // d ∈ K ?  ⇔  |⟨d, v⟩| ≤ |v|² pour chaque facette v
        let inside = self.facets.iter().all(|&v| {
            (d.0 * v.0 + d.1 * v.1).abs() <= v.0 * v.0 + v.1 * v.1
        });
        if inside {
            return (0, 1);
        }
        // sinon distance au plus proche segment de K
        let n = self.kverts.len();
        let mut best: (i128, i128) = (i128::MAX, 1);
        for k in 0..n {
            let a = self.kverts[k];
            let b = self.kverts[(k + 1) % n];
            let (num, den) = seg_dist2(d, a, b);
            // comparaison de fractions
            if best.0 == i128::MAX || num * best.1 < best.0 * den {
                best = (num, den);
            }
        }
        best
    }

    /// dmax²(V, V+d) = max_{z ∈ K} |z − d|², exact (entier, unités de dd²).
    pub fn dmax2(&self, d: (i128, i128)) -> i128 {
        let mut best: i128 = 0;
        for z in self.kverts.iter() {
            let x = z.0 - d.0;
            let y = z.1 - d.1;
            let v = x * x + y * y;
            if v > best {
                best = v;
            }
        }
        best
    }
}

/// Distance² point-segment exacte, rendue comme fraction (num, den > 0).
#[inline]
fn seg_dist2(p: (i128, i128), a: (i128, i128), b: (i128, i128)) -> (i128, i128) {
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
    // |ap|² − num²/den
    let ap2 = ap.0 * ap.0 + ap.1 * ap.1;
    (ap2 * den - num * num, den)
}

pub fn isqrt_i128(n: i128) -> i128 {
    if n <= 0 {
        return 0;
    }
    let mut x = (n as f64).sqrt() as i128;
    while x * x > n {
        x -= 1;
    }
    while (x + 1) * (x + 1) <= n {
        x += 1;
    }
    x
}

/// Test de conflit : ε² · dmin² ≤ D² ≤ ε² · dmax².
///
/// Toutes les quantités sont en unités de dd² ; dd² se simplifie dans les deux
/// inégalités, il ne reste que des comparaisons d'entiers.
#[derive(Clone, Debug)]
pub struct Test {
    pub cell: Cell,
    pub en2: i128,
    pub ed2: i128,
}

impl Test {
    pub fn new(cell: Cell, eps: Rat) -> Test {
        Test { cell, en2: eps.n * eps.n, ed2: eps.d * eps.d }
    }

    /// (dmin2 ≤ D²) ∧ (D² ≤ ε² dmax2)
    #[inline]
    pub fn conflict(&self, i: i128, j: i128) -> bool {
        let d = self.cell.offset(i, j);
        if self.en2 * self.cell.dmax2(d) < self.ed2 * self.cell.diam2 {
            return false; // D > ε·dmax : trop loin
        }
        let (num, den) = self.cell.dmin2(d);
        self.en2 * num <= self.ed2 * self.cell.diam2 * den
    }
}

// =======================================================================================
// Variante flottante (f64) : SÉLECTION des témoins, pas démonstration.
//
// Sur ce problème, la géométrie exacte en i128 est nécessaire à la *preuve* (côté Python,
// encadrements d'intervalles), mais pas au *choix* des témoins. Or le repère entier coûte
// cher : ses coordonnées valent dd·h, avec dd ~ 2h dès que g ≠ 0, d'où des produits en
// (dd·h)⁴ qui débordent i128 vers h ≈ 10⁵. En f64, aucun débordement dans la plage utile
// (h ≤ 10⁹) et un facteur ~10 en vitesse.
//
// Conséquence assumée : un gabarit produit ici n'est qu'une CONJECTURE. C'est le certificat
// Python (arithmétique rationnelle exacte, encadrements sur la boîte) qui décide. Une
// conjecture fausse fait échouer un certificat — elle ne prouve jamais rien de faux.
// =======================================================================================

#[derive(Clone, Debug)]
pub struct CellF {
    pub b1: (f64, f64),
    pub b2: (f64, f64),
    /// sommets de la cellule (unités réelles)
    pub verts: Vec<(f64, f64)>,
    /// sommets du corps de différences K = V − V
    pub kverts: Vec<(f64, f64)>,
    pub diam2: f64,
    /// normales de facettes (vecteurs du réseau), pour tester l'appartenance à K
    pub facets: Vec<(f64, f64)>,
}

impl CellF {
    pub fn build(g: f64, h: f64) -> CellF {
        let b1 = (1.0f64, 0.0f64);
        let b2 = (g, h);
        let cand_ij: [(i128, i128); 8] = [
            (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1), (1, 1), (-1, -1),
        ];
        let vec = |i: i128, j: i128| (i as f64 * b1.0 + j as f64 * b2.0, i as f64 * b1.1 + j as f64 * b2.1);
        let norm2 = |v: (f64, f64)| v.0 * v.0 + v.1 * v.1;
        let cand: Vec<(i128, i128, (f64, f64), f64)> = cand_ij
            .iter()
            .map(|&(i, j)| {
                let v = vec(i, j);
                (i, j, v, norm2(v))
            })
            .collect();

        // sommets de V : intersections de 2⟨x,v_a⟩ = |v_a|² et 2⟨x,v_b⟩ = |v_b|²
        let mut verts: Vec<(f64, f64)> = Vec::new();
        for a in 0..cand.len() {
            for b in (a + 1)..cand.len() {
                let (va, na) = (cand[a].2, cand[a].3);
                let (vb, nb) = (cand[b].2, cand[b].3);
                let det = va.0 * vb.1 - va.1 * vb.0;
                if det.abs() < 1e-300 {
                    continue;
                }
                let x = (na * vb.1 - nb * va.1) / (2.0 * det);
                let y = (va.0 * nb - vb.0 * na) / (2.0 * det);
                let ok = cand.iter().all(|c| 2.0 * (x * c.2 .0 + y * c.2 .1) <= c.3 * (1.0 + 1e-12) + 1e-12);
                if ok && !verts.iter().any(|w| (w.0 - x).abs() < 1e-12 && (w.1 - y).abs() < 1e-12) {
                    verts.push((x, y));
                }
            }
        }
        assert!(verts.len() >= 3, "cellule dégénérée");
        verts.sort_by(|p, q| p.1.atan2(p.0).partial_cmp(&q.1.atan2(q.0)).unwrap());

        // facettes : contraintes tendues en deux sommets au moins
        let mut facets: Vec<(f64, f64)> = Vec::new();
        for c in cand.iter() {
            let tight = verts
                .iter()
                .filter(|x| (2.0 * (x.0 * c.2 .0 + x.1 * c.2 .1) - c.3).abs() <= 1e-9 * (1.0 + c.3))
                .count();
            if tight >= 2 {
                facets.push(c.2);
            }
        }
        // ne garder qu'un représentant par paire ±v
        let mut fac: Vec<(f64, f64)> = Vec::new();
        for v in facets {
            if !fac.iter().any(|w| (w.0 + v.0).abs() < 1e-12 && (w.1 + v.1).abs() < 1e-12 || (w.0 - v.0).abs() < 1e-12 && (w.1 - v.1).abs() < 1e-12) {
                fac.push(v);
            }
        }
        assert!(!fac.is_empty(), "aucune facette");

        // K = { z : |⟨z,v⟩| ≤ |v|² }, sommets par intersection de contraintes
        let mut cons: Vec<((f64, f64), f64)> = Vec::new();
        for v in fac.iter() {
            cons.push((*v, norm2(*v)));
            cons.push(((-v.0, -v.1), norm2(*v)));
        }
        let mut kverts: Vec<(f64, f64)> = Vec::new();
        for a in 0..cons.len() {
            for b in (a + 1)..cons.len() {
                let ((nx, ny), ca) = cons[a];
                let ((mx, my), cb) = cons[b];
                let det = nx * my - ny * mx;
                if det.abs() < 1e-300 {
                    continue;
                }
                let x = (ca * my - cb * ny) / det;
                let y = (nx * cb - mx * ca) / det;
                let ok = cons.iter().all(|(n, c)| x * n.0 + y * n.1 <= c * (1.0 + 1e-12) + 1e-12);
                if ok && !kverts.iter().any(|w| (w.0 - x).abs() < 1e-10 && (w.1 - y).abs() < 1e-10) {
                    kverts.push((x, y));
                }
            }
        }
        assert!(kverts.len() >= 4, "corps de différences dégénéré");
        let diam2 = kverts.iter().map(|z| z.0 * z.0 + z.1 * z.1).fold(0.0, f64::max);
        CellF { b1, b2, verts, kverts, diam2, facets: fac }
    }

    #[inline]
    pub fn offset(&self, i: i128, j: i128) -> (f64, f64) {
        (i as f64 * self.b1.0 + j as f64 * self.b2.0, i as f64 * self.b1.1 + j as f64 * self.b2.1)
    }
}

#[derive(Clone, Debug)]
pub struct TestF {
    pub cell: CellF,
    pub eps: f64,
}

impl TestF {
    pub fn new(cell: CellF, eps: f64) -> TestF {
        TestF { cell, eps }
    }
    /// dmin² entre V et V+d, en unités réelles.
    pub fn dmin2(&self, d: (f64, f64)) -> f64 {
        let inside = self
            .cell
            .facets
            .iter()
            .all(|v| (d.0 * v.0 + d.1 * v.1).abs() <= v.0 * v.0 + v.1 * v.1);
        if inside {
            return 0.0;
        }
        let n = self.cell.kverts.len();
        let mut best = f64::INFINITY;
        for k in 0..n {
            let a = self.cell.kverts[k];
            let b = self.cell.kverts[(k + 1) % n];
            let ab = (b.0 - a.0, b.1 - a.1);
            let ap = (d.0 - a.0, d.1 - a.1);
            let t = (ap.0 * ab.0 + ap.1 * ab.1) / (ab.0 * ab.0 + ab.1 * ab.1);
            let t = t.clamp(0.0, 1.0);
            let x = a.0 + t * ab.0 - d.0;
            let y = a.1 + t * ab.1 - d.1;
            best = best.min(x * x + y * y);
        }
        best
    }
    pub fn dmax2(&self, d: (f64, f64)) -> f64 {
        self.cell
            .kverts
            .iter()
            .map(|z| {
                let x = z.0 - d.0;
                let y = z.1 - d.1;
                x * x + y * y
            })
            .fold(0.0, f64::max)
    }
    /// Conflicte, avec une marge relative pour ne pas proposer de cas tangents.
    #[inline]
    pub fn conflict(&self, i: i128, j: i128) -> bool {
        let d = self.cell.offset(i, j);
        let dm = self.dmax2(d);
        if self.eps * self.eps * dm < self.cell.diam2 * (1.0 + 1e-9) {
            return false;
        }
        self.dmin2(d) <= self.cell.diam2 * (1.0 - 1e-9)
    }
}
