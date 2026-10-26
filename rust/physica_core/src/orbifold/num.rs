//! Exact arithmetic for the D-028 orbifold scan: rationals, Smith and Hermite
//! forms, rank, and elementary symmetric functions of integer matrices.
//!
//! Every routine is a line-for-line port of the Python reference in
//! `metaphysica.simulations.PM.geometry.orbifold_gauge_scan`, including the
//! pivot order of the Smith form, so that results agree record for record.

pub const N: usize = 7;
/// Integer matrix, row major.
pub type Mat = Vec<Vec<i128>>;

fn gcd(a: i128, b: i128) -> i128 {
    let (mut a, mut b) = (a.abs(), b.abs());
    while b != 0 {
        let t = a % b;
        a = b;
        b = t;
    }
    a
}

/// Reduced rational with a positive denominator.
#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug)]
pub struct Rat {
    pub n: i128,
    pub d: i128,
}

impl Rat {
    pub const ZERO: Rat = Rat { n: 0, d: 1 };

    pub fn new(n: i128, d: i128) -> Rat {
        assert!(d != 0, "zero denominator");
        let g = gcd(n, d).max(1);
        let s = if d < 0 { -1 } else { 1 };
        Rat { n: s * n / g, d: s * d / g }
    }
    pub fn int(n: i128) -> Rat {
        Rat { n, d: 1 }
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
    /// Fractional part in [0, 1).
    pub fn frac(self) -> Rat {
        Rat { n: self.n.rem_euclid(self.d), d: self.d }
    }
    pub fn is_int(self) -> bool {
        self.d == 1
    }
    pub fn is_zero(self) -> bool {
        self.n == 0
    }
}

/// Floor division (Python `//`), valid for negative divisors.
pub fn fdiv(a: i128, b: i128) -> i128 {
    let q = a / b;
    if a % b != 0 && ((a < 0) != (b < 0)) {
        q - 1
    } else {
        q
    }
}

pub fn identity_mat(n: usize) -> Mat {
    (0..n).map(|i| (0..n).map(|j| (i == j) as i128).collect()).collect()
}

// ------------------------------------------------------------ Smith form

/// `u * a * v = d` (diagonal, not divisibility ordered) and the rank.
pub struct Smith {
    pub u: Mat,
    pub d: Mat,
    pub v: Mat,
    pub rank: usize,
}

fn swap_cols(a: &mut Mat, v: &mut Mat, i: usize, j: usize) {
    for m in [a, v] {
        for row in m.iter_mut() {
            row.swap(i, j);
        }
    }
}

fn row_add(a: &mut Mat, u: &mut Mat, i: usize, r: usize, f: i128) {
    for m in [a, u] {
        let src = m[r].clone();
        for (x, y) in m[i].iter_mut().zip(src) {
            *x += f * y;
        }
    }
}

fn col_add(a: &mut Mat, v: &mut Mat, j: usize, r: usize, f: i128) {
    for m in [a, v] {
        for row in m.iter_mut() {
            row[j] += f * row[r];
        }
    }
}

fn pivot(a: &Mat, r: usize) -> Option<(usize, usize)> {
    let mut best: Option<(i128, usize, usize)> = None;
    for i in r..a.len() {
        for j in r..a[0].len() {
            let v = a[i][j].abs();
            if v != 0 && best.map_or(true, |b| v < b.0) {
                best = Some((v, i, j));
            }
        }
    }
    best.map(|b| (b.1, b.2))
}

fn clear(a: &mut Mat, u: &mut Mat, v: &mut Mat, r: usize) -> bool {
    let p = a[r][r];
    for i in r + 1..a.len() {
        let q = fdiv(a[i][r], p);
        if q != 0 {
            row_add(a, u, i, r, -q);
        }
    }
    for j in r + 1..a[0].len() {
        let q = fdiv(a[r][j], p);
        if q != 0 {
            col_add(a, v, j, r, -q);
        }
    }
    (r + 1..a.len()).all(|i| a[i][r] == 0) && (r + 1..a[0].len()).all(|j| a[r][j] == 0)
}

pub fn smith(a_in: &Mat) -> Smith {
    let mut a = a_in.clone();
    let (m, n) = (a.len(), a[0].len());
    let (mut u, mut v) = (identity_mat(m), identity_mat(n));
    let mut r = 0;
    while r < m.min(n) {
        let Some((pi, pj)) = pivot(&a, r) else { break };
        a.swap(r, pi);
        u.swap(r, pi);
        swap_cols(&mut a, &mut v, r, pj);
        if clear(&mut a, &mut u, &mut v, r) {
            r += 1;
        }
    }
    Smith { u, d: a, v, rank: r }
}

// --------------------------------------------------------- Hermite form

fn sub_row(rows: &mut [[i128; N]], i: usize, src: usize, q: i128) {
    let s = rows[src];
    for (x, y) in rows[i].iter_mut().zip(s) {
        *x -= q * y;
    }
}

fn reduce_column(rows: &mut [[i128; N]], r: usize, col: usize) {
    loop {
        let nz: Vec<usize> = (r..rows.len()).filter(|&i| rows[i][col] != 0).collect();
        if nz.len() <= 1 {
            return;
        }
        let i0 = *nz.iter().min_by_key(|&&i| rows[i][col].abs()).unwrap();
        for &i in &nz {
            if i != i0 {
                let q = fdiv(rows[i][col], rows[i0][col]);
                sub_row(rows, i, i0, q);
            }
        }
    }
}

/// Row Hermite normal form (canonical for the row lattice).
pub fn hnf_rows(k: &[[i128; N]]) -> Vec<[i128; N]> {
    let mut rows = k.to_vec();
    let mut r = 0;
    for col in 0..N {
        reduce_column(&mut rows, r, col);
        let Some(p) = (r..rows.len()).find(|&i| rows[i][col] != 0) else { continue };
        rows.swap(r, p);
        if rows[r][col] < 0 {
            rows[r].iter_mut().for_each(|x| *x = -*x);
        }
        for i in 0..r {
            let q = fdiv(rows[i][col], rows[r][col]);
            sub_row(&mut rows, i, r, q);
        }
        r += 1;
    }
    rows.truncate(r);
    rows
}

// ------------------------------------------------------ rank and solving

/// Gauss-Jordan on the first `ncols` columns of `rows` (rationals). Returns
/// the pivot count; rows are left reduced with unit pivots in rows 0..rank.
fn eliminate(rows: &mut [Vec<Rat>], ncols: usize) -> usize {
    let mut r = 0;
    for c in 0..ncols {
        let Some(p) = (r..rows.len()).find(|&i| !rows[i][c].is_zero()) else { continue };
        rows.swap(r, p);
        let inv = Rat::int(1).div(rows[r][c]);
        rows[r].iter_mut().for_each(|x| *x = x.mul(inv));
        for i in 0..rows.len() {
            if i != r && !rows[i][c].is_zero() {
                let f = rows[i][c];
                let src = rows[r].clone();
                for (x, y) in rows[i].iter_mut().zip(src) {
                    *x = x.sub(f.mul(y));
                }
            }
        }
        r += 1;
    }
    r
}

fn to_rat(m: &[Vec<i128>]) -> Vec<Vec<Rat>> {
    m.iter().map(|r| r.iter().map(|&x| Rat::int(x)).collect()).collect()
}

/// Rank over Q of an integer matrix.
pub fn rank(m: &[Vec<i128>]) -> usize {
    if m.is_empty() {
        return 0;
    }
    let mut rows = to_rat(m);
    let nc = rows[0].len();
    eliminate(&mut rows, nc)
}

/// Integer `R` with `B R = M B` (`B` given as `d` columns), or `None` when
/// the column span of `B` is not `M`-invariant or `R` is not integral.
pub fn restriction(m: &[[i128; N]; N], b: &[[i128; N]]) -> Option<Mat> {
    let d = b.len();
    let mut rows: Vec<Vec<Rat>> = (0..N)
        .map(|i| {
            let mb = b.iter().map(|col| (0..N).map(|j| m[i][j] * col[j]).sum::<i128>());
            b.iter().map(|c| Rat::int(c[i])).chain(mb.map(Rat::int)).collect()
        })
        .collect();
    if eliminate(&mut rows, d) != d {
        return None;
    }
    if rows[d..].iter().any(|r| r[d..].iter().any(|x| !x.is_zero())) {
        return None;
    }
    let out: Vec<Vec<Rat>> = rows[..d].iter().map(|r| r[d..].to_vec()).collect();
    out.iter().all(|r| r.iter().all(|x| x.is_int())).then(|| {
        out.iter().map(|r| r.iter().map(|x| x.n).collect()).collect()
    })
}

// ------------------------------------------- elementary symmetric functions

fn matmul(a: &Mat, b: &Mat) -> Mat {
    let n = a.len();
    (0..n)
        .map(|i| (0..n).map(|j| (0..n).map(|k| a[i][k] * b[k][j]).sum()).collect())
        .collect()
}

/// e_0..e_n of the eigenvalues of the integer matrix `a` (Newton identities;
/// the divisions are exact).
pub fn elem_sym(a: &Mat) -> Vec<i128> {
    let n = a.len();
    let mut pw = a.clone();
    let mut traces = vec![0i128];
    for _ in 0..n {
        traces.push((0..n).map(|i| pw[i][i]).sum());
        pw = matmul(&pw, a);
    }
    let mut e = vec![1i128];
    for k in 1..=n {
        let s: i128 = (1..=k)
            .map(|i| if i % 2 == 1 { 1 } else { -1 } * e[k - i] * traces[i])
            .sum();
        e.push(s / k as i128);
    }
    e
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn floor_division_matches_python() {
        assert_eq!(fdiv(7, -2), -4);
        assert_eq!(fdiv(-7, 2), -4);
        assert_eq!(fdiv(-7, -2), 3);
        assert_eq!(fdiv(6, -3), -2);
    }

    #[test]
    fn newton_identities_on_a_rotation() {
        let a: Mat = vec![vec![0, -1], vec![1, -1]]; // order 3
        assert_eq!(elem_sym(&a), vec![1, -1, 1]);
    }

    #[test]
    fn smith_reduces_to_diagonal() {
        let a: Mat = vec![vec![2, 4], vec![6, 8]];
        let s = smith(&a);
        assert_eq!(s.rank, 2);
        assert_eq!(s.d[0][1], 0);
        assert_eq!(s.d[1][0], 0);
    }

    #[test]
    fn rank_and_hnf() {
        assert_eq!(rank(&[vec![1, 2], vec![2, 4]]), 1);
        let mut k = [[0i128; N]; 2];
        k[0][0] = 2;
        k[1][0] = 3;
        assert_eq!(hnf_rows(&k)[0][0], 1);
    }
}
