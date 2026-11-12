//! gabarit — cliques de conflit pour le certificat χ ≥ 7 (audit Sokolov–Voronov).
//!
//! Rôle exact du programme : il **choisit les témoins** (une clique d'offsets, les paires de
//! contraintes tendues, les milieux de Delaunay). Il ne **prouve** rien : la preuve est le
//! certificat Python, en arithmétique rationnelle exacte, sur la boîte entière. Un gabarit
//! faux fait donc échouer un certificat, jamais accepter une conclusion fausse.
//!
//! Deux moteurs :
//!   * `--exact` (i128) : géométrie rationnelle exacte, pour la VALIDATION à petit h
//!     (retrouve ω = 24 à h = 10 et ω = 16 à h = 20, mesurés côté Python) ;
//!   * défaut (f64) : sélection en temps constant, utilisable jusqu'à h ~ 10⁹.
//!
//! Usage :
//!   gabarit cell    --g 0 --h 10
//!   gabarit omega   --g 0 --h 10 --eps 99/100          (ω exact, validation)
//!   gabarit run     --g 0 --h 1000 --eps 99/100 [--json] [--want 9]
//!   gabarit bench   --eps 99/100 --hs 10,100,1000,10000,100000,1000000
//!   gabarit selftest

mod gabarit;
mod geom;
mod graph;

use std::env;
use std::time::Instant;

use crate::gabarit::{conflit_direct, construire, omega_dense};
use crate::geom::{Cell, CellF, Rat, Test, TestF};

const DEN: i128 = 1 << 20; // dénominateur de rationalisation de la sortie JSON

fn rat_from(s: &str) -> Rat {
    if let Some((a, b)) = s.split_once('/') {
        Rat::new(a.parse().expect("numérateur"), b.parse().expect("dénominateur"))
    } else {
        Rat::int(s.parse().expect("entier"))
    }
}

fn rat_to_string(r: Rat) -> String {
    if r.d == 1 {
        format!("{}", r.n)
    } else {
        format!("{}/{}", r.n, r.d)
    }
}

/// Rationalise un flottant avec un dénominateur fixe (sortie JSON).
fn quant(x: f64) -> String {
    let n = (x * DEN as f64).round() as i128;
    rat_to_string(Rat::new(n, DEN))
}

/// Rationalisation RÉTRACTÉE : les sommets de cellule et les milieux de Delaunay sont sur le
/// BORD de la cellule. Un arrondi au plus proche les fait sortir d'un epsilon, et le certificat
/// doit alors les retirer un à un (chacun coûtait une reconstruction complète du plan).
/// On les ramène donc vers l'intérieur d'un facteur (1 − 2⁻¹¹) avant d'arrondir : marge
/// relative de 5·10⁻⁴, très au-delà de la variation des contraintes sur une boîte.
const RETRAIT: f64 = 1.0 - 1.0 / 2048.0;

fn quant_in(x: f64) -> String {
    quant(x * RETRAIT)
}

fn q(x: &str) -> String {
    format!("\"{}\"", x)
}

fn arg(args: &[String], key: &str) -> Option<String> {
    args.iter().position(|a| a == key).and_then(|i| args.get(i + 1).cloned())
}

fn has(args: &[String], key: &str) -> bool {
    args.iter().any(|a| a == key)
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let cmd = args.get(1).map(|s| s.as_str()).unwrap_or("help");
    match cmd {
        "cell" => {
            let g = rat_from(&arg(&args, "--g").unwrap_or_else(|| "0".into()));
            let h = rat_from(&arg(&args, "--h").unwrap_or_else(|| "1".into()));
            let c = Cell::build(g, h);
            println!("dd = {}  |  b1 = {:?}  b2 = {:?}", c.dd, c.b1, c.b2);
            println!("{} sommets de cellule :", c.verts.len());
            for v in c.verts.iter() {
                println!("  ({}, {})",
                         rat_to_string(Rat::new(v.0, c.dd)),
                         rat_to_string(Rat::new(v.1, c.dd)));
            }
            println!("corps de différences : {} sommets, diamètre² = {} / dd²",
                     c.kverts.len(), c.diam2);
        }
        "omega" => {
            let g = rat_from(&arg(&args, "--g").unwrap_or_else(|| "0".into()));
            let h = rat_from(&arg(&args, "--h").unwrap_or_else(|| "1".into()));
            let eps = rat_from(&arg(&args, "--eps").unwrap_or_else(|| "99/100".into()));
            let t = Test::new(Cell::build(g, h), eps);
            let t0 = Instant::now();
            let (k, cl) = omega_dense(&t);
            println!("h = {} : ω(avec 0) = {} ({} ms), clique {}",
                     rat_to_string(h), k, t0.elapsed().as_millis(), cl.len());
            println!("  {:?}", cl);
        }
        "run" => {
            let gs = arg(&args, "--g").unwrap_or_else(|| "0".into());
            let hs = arg(&args, "--h").unwrap_or_else(|| "1".into());
            let es = arg(&args, "--eps").unwrap_or_else(|| "99/100".into());
            let g = rat_from(&gs);
            let h = rat_from(&hs);
            let eps = rat_from(&es);
            let want: usize = arg(&args, "--want").and_then(|s| s.parse().ok()).unwrap_or(9);

            let t0 = Instant::now();
            let cell = CellF::build(g.to_f64(), h.to_f64());
            let t_cell = t0.elapsed();
            let t = TestF::new(cell.clone(), eps.to_f64());
            let t1 = Instant::now();
            let gab = construire(&t, want);
            let t_gab = t1.elapsed();

            match gab {
                Some(gb) => {
                    // vérification exacte des paires quand le repère i128 est sûr
                    let mut etat = String::new();
                    if has(&args, "--check") {
                        let sur = g.to_f64() * h.to_f64();
                        if sur.abs() < 1e4 && h.to_f64() < 1e4 {
                            let te = Test::new(Cell::build(g, h), eps);
                            let mut ok = true;
                            for a in 0..gb.clique.len() {
                                for b in (a + 1)..gb.clique.len() {
                                    let (i, j) = (gb.clique[a].0 - gb.clique[b].0,
                                                  gb.clique[a].1 - gb.clique[b].1);
                                    if !te.conflict(i, j) || !conflit_direct(&te.cell, &te, i, j) {
                                        ok = false;
                                    }
                                }
                            }
                            etat = if ok { " | vérifié exactement".into() } else { " | ÉCHEC".into() };
                            if !ok {
                                std::process::exit(3);
                            }
                        } else {
                            etat = " | exact non applicable (h trop grand), conjecture".into();
                        }
                    }
                    let ligne = format!(
                        "g = {:>6} h = {:>10} eps = {} : clique {} | pas k1 = {} | rangées {:?} | cellule {:.3} ms, gabarit {:.3} ms{}",
                        gs, hs, rat_to_string(eps), gb.clique.len(), gb.k1, gb.rows,
                        t_cell.as_secs_f64() * 1e3, t_gab.as_secs_f64() * 1e3, etat);
                    if has(&args, "--json") {
                        eprintln!("{}", ligne);
                        print!("{}", json_motif(&cell, g, h, &gb.clique));
                    } else {
                        println!("{}", ligne);
                    }
                }
                None => {
                    eprintln!("échec : pas de clique de {} au centre (g = {}, h = {}, eps = {})",
                              want, gs, hs, rat_to_string(eps));
                    std::process::exit(2);
                }
            }
        }
        "bench" => {
            let eps = rat_from(&arg(&args, "--eps").unwrap_or_else(|| "99/100".into()));
            let hs = arg(&args, "--hs").unwrap_or_else(|| "10,100,1000,10000".into());
            println!("{:>12} | {:>8} | {:>13} | {:>13} | {:>10}", "h", "|clique|", "cellule (ms)", "gabarit (ms)", "pas k1");
            for s in hs.split(',') {
                let h = rat_from(s.trim());
                let t0 = Instant::now();
                let cell = CellF::build(0.0, h.to_f64());
                let t_cell = t0.elapsed();
                let t = TestF::new(cell, eps.to_f64());
                let t1 = Instant::now();
                match construire(&t, 9) {
                    Some(gb) => println!("{:>12} | {:>8} | {:>13.4} | {:>13.4} | {:>10}",
                                         s.trim(), gb.clique.len(),
                                         t_cell.as_secs_f64() * 1e3,
                                         t1.elapsed().as_secs_f64() * 1e3, gb.k1),
                    None => println!("{:>12} | échec", s.trim()),
                }
            }
        }
        "selftest" => {
            let mut fails = 0;
            {
                let mut g = graph::Graph::new(5);
                for a in 0..5 {
                    for b in (a + 1)..5 {
                        g.link(a, b);
                    }
                }
                let cl = graph::max_clique(&g, 100_000);
                println!("K5 : clique {} (attendu 5) {}", cl.len(), if cl.len() == 5 { "OK" } else { "ÉCHEC" });
                if cl.len() != 5 {
                    fails += 1;
                }
            }
            // validation croisée avec les valeurs mesurées côté Python
            for (h, attendu) in [("10", 24usize), ("20", 16)] {
                let t = Test::new(Cell::build(Rat::int(0), rat_from(h)), Rat::new(99, 100));
                let (k, _) = omega_dense(&t);
                let ok = k == attendu;
                println!("ω(0, h={}, 99/100) = {} (attendu {}) {}", h, k, attendu,
                         if ok { "OK" } else { "ÉCHEC" });
                if !ok {
                    fails += 1;
                }
            }
            // gabarits flottants, vérifiés exactement quand c'est possible
            // la voie rapide vise la queue : à h < 3 le motif hexagonal n'est pas une rangée,
            // c'est le code Python (rapide à ces tailles) qui s'en charge.
            for h in ["10", "20", "100", "1000"] {
                let hr = rat_from(h);
                let t = TestF::new(CellF::build(0.0, hr.to_f64()), 0.99);
                match construire(&t, 9) {
                    Some(gb) => {
                        let te = Test::new(Cell::build(Rat::int(0), hr), Rat::new(99, 100));
                        let mut ok = true;
                        for a in 0..gb.clique.len() {
                            for b in (a + 1)..gb.clique.len() {
                                let (i, j) = (gb.clique[a].0 - gb.clique[b].0,
                                              gb.clique[a].1 - gb.clique[b].1);
                                if !conflit_direct(&te.cell, &te, i, j) {
                                    ok = false;
                                }
                            }
                        }
                        println!("gabarit g=0 h={:>6} : {} sommets, k1 = {}, vérifié = {}",
                                 h, gb.clique.len(), gb.k1, ok);
                        if !ok || gb.clique.len() < 7 {
                            fails += 1;
                        }
                    }
                    None => {
                        println!("gabarit g=0 h={:>6} : ÉCHEC DE CONSTRUCTION", h);
                        fails += 1;
                    }
                }
            }
            // coins anisotropes : g ≠ 0
            // coins anisotropes ; le coin exactement hexagonal (g = −1/2, h = 1) a une
            // clique MARGINALE (ω = 7 sans marge) : c'est le domaine du chemin Python.
            for (gs, hs) in [("1/4", "6"), ("1/2", "3"), ("-1/4", "1000"), ("1/4", "1000000")] {
                let t = TestF::new(CellF::build(rat_from(gs).to_f64(), rat_from(hs).to_f64()), 0.99);
                match construire(&t, 7) {
                    Some(gb) => println!("gabarit g={:>5} h={:>4} : {} sommets, k1 = {}", gs, hs, gb.clique.len(), gb.k1),
                    None => {
                        println!("gabarit g={:>5} h={:>4} : ÉCHEC", gs, hs);
                        fails += 1;
                    }
                }
            }
            println!("{}", if fails == 0 { "selftest : tout est vert" } else { "selftest : ÉCHECS" });
            std::process::exit(if fails == 0 { 0 } else { 1 });
        }
        "mctest" => {
            let n: usize = arg(&args, "--n").and_then(|s| s.parse().ok()).unwrap_or(200);
            let mut g = graph::Graph::new(n);
            let mut seed: u64 = 12345;
            let mut edges = 0;
            for a in 0..n {
                for b in (a + 1)..n {
                    seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
                    if (seed >> 33) % 10 < 3 {
                        g.link(a, b);
                        edges += 1;
                    }
                }
            }
            let cl = graph::max_clique(&g, 50_000_000);
            println!("{} sommets, {} arêtes, clique trouvée {}", n, edges, cl.len());
        }
        _ => {
            println!("gabarit — cliques de conflit (audit S-V)");
            println!("  cell | omega | run | bench | selftest | mctest   (voir l'en-tête du source)");
        }
    }
}

/// Motif au format attendu par le pont Python (`audit_certificat3.motif_queue`).
fn json_motif(cell: &CellF, g: Rat, h: Rat, clique: &[(i128, i128)]) -> String {
    let cand: [(i128, i128); 8] = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1), (1, 1), (-1, -1)];
    let cons: Vec<((i128, i128), (f64, f64), f64)> = cand
        .iter()
        .map(|&(i, j)| {
            let v = cell.offset(i, j);
            ((i, j), v, v.0 * v.0 + v.1 * v.1)
        })
        .collect();

    let mut s = String::from("{\n");
    s.push_str(&format!("  \"centre\": [{}, {}],\n", q(&rat_to_string(g)), q(&rat_to_string(h))));
    s.push_str("  \"clique\": [");
    for (k, o) in clique.iter().enumerate() {
        if k > 0 {
            s.push(',');
        }
        s.push_str(&format!("[{}, {}]", o.0, o.1));
    }
    s.push_str("],\n");
    s.push_str("  \"paires\": [");
    for (k, p) in cell.verts.iter().enumerate() {
        let mut tenues: Vec<(i128, i128)> = Vec::new();
        for (ij, v, n2) in cons.iter() {
            if (2.0 * (p.0 * v.0 + p.1 * v.1) - n2).abs() <= 1e-9 * (1.0 + n2) {
                tenues.push(*ij);
            }
        }
        let a = *tenues.first().unwrap_or(&(1, 0));
        let b = *tenues.get(1).unwrap_or(&(0, 1));
        if k > 0 {
            s.push(',');
        }
        s.push_str(&format!("[[{}, {}], [{}, {}]]", a.0, a.1, b.0, b.1));
    }
    s.push_str("],\n");

    // milieux de Delaunay : w/2 ∈ V  ⟺  ⟨w, v⟩ ≤ |v|² pour tout v du réseau
    let mut mids: Vec<(i128, i128)> = vec![(0, 0)];
    for i in -6i128..=6i128 {
        for j in -6i128..=6i128 {
            if i == 0 && j == 0 {
                continue;
            }
            let wi = cell.offset(i, j);
            let lim = 4.0 * (wi.0 * wi.0 + wi.1 * wi.1) + 4.0;
            let mut ok = true;
            'outer: for k in -14i128..=14i128 {
                for l in -14i128..=14i128 {
                    if k == 0 && l == 0 {
                        continue;
                    }
                    let v = cell.offset(k, l);
                    let n2 = v.0 * v.0 + v.1 * v.1;
                    if n2 > lim {
                        continue;
                    }
                    if wi.0 * v.0 + wi.1 * v.1 > n2 * (1.0 + 1e-12) {
                        ok = false;
                        break 'outer;
                    }
                }
            }
            if ok {
                mids.push((i, j));
            }
        }
    }
    s.push_str("  \"mids\": [");
    for (k, o) in mids.iter().enumerate() {
        if k > 0 {
            s.push(',');
        }
        s.push_str(&format!("[{}, {}]", o.0, o.1));
    }
    s.push_str("],\n");
    s.push_str("  \"pts_mid\": {");
    for (k, o) in mids.iter().enumerate() {
        let wi = cell.offset(o.0, o.1);
        if k > 0 {
            s.push(',');
        }
        s.push_str(&format!("\"{},{}\": [{}, {}]", o.0, o.1, q(&quant_in(wi.0 / 2.0)), q(&quant_in(wi.1 / 2.0))));
    }
    s.push_str("},\n");
    s.push_str("  \"pts_centre\": [");
    for (k, p) in cell.verts.iter().enumerate() {
        if k > 0 {
            s.push(',');
        }
        s.push_str(&format!("[{}, {}]", q(&quant_in(p.0)), q(&quant_in(p.1))));
    }
    s.push_str("],\n");
    s.push_str(&format!("  \"omega\": {},\n", clique.len()));
    s.push_str(&format!("  \"n_sommets\": {},\n", cell.verts.len()));
    s.push_str("  \"dd\": 0\n}\n");
    s
}
