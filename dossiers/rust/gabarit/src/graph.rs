//! Graphe de conflit sur des bitsets, et clique maximale (Bron–Kerbosch avec pivot).
//!
//! Complexité. Pour n sommets :
//!   * construction dense (fenêtre complète) : O(n²) tests de conflit ;
//!   * clique maximale : O(3^{n/3}) dans le pire cas (B–K avec pivot, Tomita) mais
//!     l'élagage est en pratique quasi linéaire sur ces graphes (densité modérée) ;
//!   * les opérations d'ensemble sont des ET/OU sur u64 : 64 sommets par instruction.
//!
//! C'est cette couche qui sert à *valider* (retrouver ω = 24 à h = 10, ω = 16 à h = 20)
//! et à rattraper le coup si la construction rapide par rangées ne suffit pas.

#[derive(Clone, Debug)]
pub struct Bits {
    pub w: Vec<u64>,
    pub n: usize,
}

impl Bits {
    pub fn new(n: usize) -> Bits {
        Bits { w: vec![0u64; (n + 63) / 64], n }
    }
    #[inline]
    pub fn set(&mut self, i: usize) {
        self.w[i >> 6] |= 1u64 << (i & 63);
    }
    #[inline]
    pub fn clear(&mut self, i: usize) {
        self.w[i >> 6] &= !(1u64 << (i & 63));
    }
    #[inline]
    pub fn get(&self, i: usize) -> bool {
        (self.w[i >> 6] >> (i & 63)) & 1 == 1
    }
    #[inline]
    pub fn count(&self) -> usize {
        self.w.iter().map(|x| x.count_ones() as usize).sum()
    }
    #[inline]
    pub fn and(&self, o: &Bits) -> Bits {
        Bits { w: self.w.iter().zip(&o.w).map(|(a, b)| a & b).collect(), n: self.n }
    }
    #[inline]
    pub fn andnot(&self, o: &Bits) -> Bits {
        Bits { w: self.w.iter().zip(&o.w).map(|(a, b)| a & !b).collect(), n: self.n }
    }
    pub fn is_empty(&self) -> bool {
        self.w.iter().all(|&x| x == 0)
    }
    /// Indices des bits à 1.
    pub fn to_vec(&self) -> Vec<usize> {
        let mut out = Vec::new();
        for (k, &word) in self.w.iter().enumerate() {
            let mut x = word;
            while x != 0 {
                let b = x.trailing_zeros() as usize;
                out.push(k * 64 + b);
                x &= x - 1;
            }
        }
        out
    }
}

pub struct Graph {
    pub n: usize,
    pub adj: Vec<Bits>,
}

impl Graph {
    pub fn new(n: usize) -> Graph {
        Graph { n, adj: (0..n).map(|_| Bits::new(n)).collect() }
    }
    #[inline]
    pub fn link(&mut self, a: usize, b: usize) {
        self.adj[a].set(b);
        self.adj[b].set(a);
    }
    #[inline]
    pub fn are_linked(&self, a: usize, b: usize) -> bool {
        self.adj[a].get(b)
    }

    /// Sous-graphe induit par `keep` (dans cet ordre), avec la correspondance inverse.
    pub fn induced(&self, keep: &[usize]) -> (Graph, Vec<usize>) {
        let mut g = Graph::new(keep.len());
        for a in 0..keep.len() {
            for b in (a + 1)..keep.len() {
                if self.are_linked(keep[a], keep[b]) {
                    g.link(a, b);
                }
            }
        }
        (g, keep.to_vec())
    }
}

/// Clique maximale par Bron–Kerbosch avec pivot (Tomita et al.), sur bitsets.
/// `budget` borne le nombre d'appels récursifs (protection contre un graphe hostile).
pub fn max_clique(g: &Graph, budget: u64) -> Vec<usize> {
    let n = g.n;
    let mut best: Vec<usize> = Vec::new();
    let mut steps: u64 = 0;
    let mut p = Bits::new(n);
    for i in 0..n {
        p.set(i);
    }
    let x = Bits::new(n);
    let mut r: Vec<usize> = Vec::new();
    bk(g, &mut r, p, x, &mut best, &mut steps, budget);
    best
}

fn bk(
    g: &Graph,
    r: &mut Vec<usize>,
    mut p: Bits,
    mut x: Bits,
    best: &mut Vec<usize>,
    steps: &mut u64,
    budget: u64,
) {
    *steps += 1;
    if *steps > budget {
        return;
    }
    if p.is_empty() && x.is_empty() {
        if r.len() > best.len() {
            *best = r.clone();
        }
        return;
    }
    // élagage : même en prenant tout P on ne battrait pas le record
    if r.len() + p.count() <= best.len() {
        return;
    }
    // pivot : sommet de P ∪ X maximisant |P ∩ N(u)|
    let mut pivot = usize::MAX;
    let mut best_deg = 0usize;
    for u in p.to_vec().into_iter().chain(x.to_vec()) {
        let d = p.and(&g.adj[u]).count();
        if pivot == usize::MAX || d > best_deg {
            pivot = u;
            best_deg = d;
        }
    }
    let cand = if pivot == usize::MAX {
        p.clone()
    } else {
        p.andnot(&g.adj[pivot])
    };
    for v in cand.to_vec() {
        if !p.get(v) {
            continue;
        }
        r.push(v);
        let np = p.and(&g.adj[v]);
        let nx = x.and(&g.adj[v]);
        bk(g, r, np, nx, best, steps, budget);
        r.pop();
        p.clear(v);
        x.set(v);
    }
}
