//! Fixed loci of affine maps on the torus R^7/Z^7 (lattice coordinates) and
//! their images, intersections and pointwise-fixing tests.

use super::iso::{Iso, DEN};
use super::num::{hnf_rows, smith, Mat, Rat, N};
use std::collections::HashMap;

/// Canonical key of a locus: Hermite form of its annihilator plus the phase
/// of `u0` against it.
#[derive(Clone, PartialEq, Eq, Hash, Debug)]
pub struct Key {
    pub h: Vec<[i128; N]>,
    pub phase: Vec<Rat>,
}

/// `u0 + span(b)` inside the torus; `k` annihilates `b` (rows).
#[derive(Clone, Debug)]
pub struct Locus {
    pub u0: [Rat; N],
    pub b: Vec<[i128; N]>,
    pub k: Vec<[i128; N]>,
    pub dim: usize,
    pub key: Key,
}

fn dot(row: &[i128; N], u: &[Rat; N]) -> Rat {
    (0..N).fold(Rat::ZERO, |s, j| s.add(Rat::int(row[j]).mul(u[j])))
}

pub fn finish(u0: [Rat; N], b: Vec<[i128; N]>, k: Vec<[i128; N]>) -> Locus {
    let h = hnf_rows(&k);
    let phase = h.iter().map(|r| dot(r, &u0).frac()).collect();
    let dim = b.len();
    Locus { u0, b, k, dim, key: Key { h, phase } }
}

/// Saturated integer rows annihilating the columns `b`.
fn annihilator(b: &[[i128; N]]) -> Vec<[i128; N]> {
    if b.is_empty() {
        return (0..N).map(|i| std::array::from_fn(|j| (i == j) as i128)).collect();
    }
    let bt: Mat = b.iter().map(|c| c.to_vec()).collect();
    let s = smith(&bt);
    (s.rank..N).map(|c| std::array::from_fn(|i| s.v[i][c])).collect()
}

pub fn make_locus(u0: [Rat; N], b: Vec<[i128; N]>) -> Locus {
    let k = annihilator(&b);
    finish(u0, b, k)
}

/// All solutions of `a y = rhs (mod 1)`: base points and free columns.
pub struct TorusSolution {
    pub points: Vec<Vec<Rat>>,
    pub free: Vec<Vec<i128>>,
}

fn mat_vec(a: &Mat, x: &[Rat]) -> Vec<Rat> {
    a.iter()
        .map(|row| row.iter().zip(x).fold(Rat::ZERO, |s, (&c, &v)| s.add(Rat::int(c).mul(v))))
        .collect()
}

fn product(choices: &[Vec<Rat>]) -> Vec<Vec<Rat>> {
    let mut out: Vec<Vec<Rat>> = vec![vec![]];
    for ch in choices {
        out = out
            .iter()
            .flat_map(|pre| ch.iter().map(move |&c| [pre.clone(), vec![c]].concat()))
            .collect();
    }
    out
}

pub fn torus_solve(a: &Mat, rhs: &[Rat]) -> TorusSolution {
    let s = smith(a);
    let n = a[0].len();
    let t = mat_vec(&s.u, rhs);
    let none = TorusSolution { points: vec![], free: vec![] };
    if t[s.rank..].iter().any(|x| !x.is_int()) {
        return none;
    }
    let choices: Vec<Vec<Rat>> = (0..s.rank)
        .map(|i| {
            let d = s.d[i][i];
            (0..d.abs()).map(|k| t[i].add(Rat::int(k)).div(Rat::int(d))).collect()
        })
        .collect();
    let points = product(&choices)
        .into_iter()
        .map(|mut y| {
            y.resize(n, Rat::ZERO);
            mat_vec(&s.v, &y).into_iter().map(Rat::frac).collect()
        })
        .collect();
    let free = (s.rank..n).map(|c| (0..n).map(|i| s.v[i][c]).collect()).collect();
    TorusSolution { points, free }
}

fn to_arr<T: Copy>(v: &[T]) -> [T; N] {
    std::array::from_fn(|i| v[i])
}

/// Components of Fix(g); empty when g has no fixed point.
pub fn fixed_loci(g: &Iso) -> Vec<Locus> {
    let a: Mat = (0..N)
        .map(|i| (0..N).map(|j| g.m[i][j] as i128 - (i == j) as i128).collect())
        .collect();
    let rhs: Vec<Rat> = g.c.iter().map(|&x| Rat::new(-(x as i128), DEN as i128)).collect();
    let sol = torus_solve(&a, &rhs);
    let b: Vec<[i128; N]> = sol.free.iter().map(|c| to_arr(c)).collect();
    sol.points.iter().map(|p| make_locus(to_arr(p), b.clone())).collect()
}

/// Image of a locus under `h`, given the integer inverse `minv` of its matrix.
pub fn image_locus(h: &Iso, minv: &[[i64; N]; N], a: &Locus) -> Locus {
    let u0: [Rat; N] = std::array::from_fn(|i| {
        let mu = (0..N).fold(Rat::ZERO, |s, j| s.add(Rat::int(h.m[i][j] as i128).mul(a.u0[j])));
        mu.add(Rat::new(h.c[i] as i128, DEN as i128)).frac()
    });
    let b = a
        .b
        .iter()
        .map(|c| std::array::from_fn(|i| (0..N).map(|j| h.m[i][j] as i128 * c[j]).sum()))
        .collect();
    let k = a
        .k
        .iter()
        .map(|r| std::array::from_fn(|j| (0..N).map(|i| r[i] * minv[i][j] as i128).sum()))
        .collect();
    finish(u0, b, k)
}

/// h fixes every point of the locus.
pub fn fixes_pointwise(h: &Iso, loc: &Locus) -> bool {
    let n = |i: usize, j: usize| h.m[i][j] as i128 - (i == j) as i128;
    let kills_dirs = loc.b.iter().all(|c| (0..N).all(|i| (0..N).map(|j| n(i, j) * c[j]).sum::<i128>() == 0));
    kills_dirs
        && (0..N).all(|i| {
            let s = (0..N).fold(Rat::ZERO, |s, j| s.add(Rat::int(n(i, j)).mul(loc.u0[j])));
            s.add(Rat::new(h.c[i] as i128, DEN as i128)).is_int()
        })
}

/// Components of the intersection of two loci (possibly empty).
pub fn meet(a: &Locus, b: &Locus) -> Vec<Locus> {
    let (da, db) = (a.b.len(), b.b.len());
    if da + db == 0 {
        return vec![];
    }
    let cols: Mat = (0..N)
        .map(|i| a.b.iter().map(|c| c[i]).chain(b.b.iter().map(|c| -c[i])).collect())
        .collect();
    let rhs: Vec<Rat> = (0..N).map(|i| b.u0[i].sub(a.u0[i])).collect();
    let sol = torus_solve(&cols, &rhs);
    let newb: Vec<[i128; N]> = sol
        .free
        .iter()
        .map(|f| std::array::from_fn(|i| (0..da).map(|j| a.b[j][i] * f[j]).sum()))
        .collect();
    sol.points
        .iter()
        .map(|t| {
            let u = std::array::from_fn(|i| {
                (0..da).fold(a.u0[i], |s, j| s.add(Rat::int(a.b[j][i]).mul(t[j]))).frac()
            });
            make_locus(u, newb.clone())
        })
        .collect()
}

/// Insertion-ordered set of loci keyed by `Key` (Python dict semantics).
#[derive(Default)]
pub struct LocusMap {
    pub items: Vec<Locus>,
    index: HashMap<Key, usize>,
}

impl LocusMap {
    pub fn contains(&self, k: &Key) -> bool {
        self.index.contains_key(k)
    }
    /// Insert if the key is new; returns whether it was.
    pub fn insert(&mut self, l: Locus) -> bool {
        if self.contains(&l.key) {
            return false;
        }
        self.index.insert(l.key.clone(), self.items.len());
        self.items.push(l);
        true
    }
    pub fn position(&self, k: &Key) -> Option<usize> {
        self.index.get(k).copied()
    }
}
