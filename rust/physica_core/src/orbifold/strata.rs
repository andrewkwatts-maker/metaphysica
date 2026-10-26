//! Orbits of loci, stabilisers, stratum types and codimension-7 points.

use super::iso::{compose, element_order, int_inverse, Iso, DEN};
use super::locus::{fixed_loci, fixes_pointwise, image_locus, meet, Locus, LocusMap};
use super::num::{elem_sym, rank, restriction, Mat, Rat, N};
use std::collections::{BTreeSet, HashSet};

pub type Res<T> = Result<T, String>;
const ORDER_LIMIT: usize = 1536;

/// The group with the inverse of every element.
pub struct Ctx<'a> {
    pub elems: &'a [Iso],
    pub inv: Vec<Iso>,
}

impl<'a> Ctx<'a> {
    pub fn new(elems: &'a [Iso]) -> Res<Ctx<'a>> {
        let inv = elems
            .iter()
            .map(|g| {
                let mi = int_inverse(&g.m)?;
                let c = std::array::from_fn(|i| {
                    (-(0..N).map(|j| mi[i][j] * g.c[j]).sum::<i64>()).rem_euclid(DEN)
                });
                Ok(Iso { m: mi, c })
            })
            .collect::<Res<Vec<Iso>>>()?;
        Ok(Ctx { elems, inv })
    }

    pub fn image(&self, i: usize, loc: &Locus) -> Locus {
        image_locus(&self.elems[i], &self.inv[i].m, loc)
    }
}

/// Distinct fixed components over all non-identity elements.
pub fn unique_loci(elems: &[Iso]) -> LocusMap {
    let e = Iso::identity();
    let mut out = LocusMap::default();
    for g in elems.iter().filter(|g| **g != e) {
        for loc in fixed_loci(g) {
            out.insert(loc);
        }
    }
    out
}

/// Gamma-orbits of loci, as sorted index lists.
pub fn orbits_of_loci(ctx: &Ctx, loci: &LocusMap) -> Res<Vec<Vec<usize>>> {
    let mut left: BTreeSet<usize> = (0..loci.items.len()).collect();
    let mut orbits = Vec::new();
    while let Some(&i) = left.iter().next() {
        let mut orb = BTreeSet::new();
        for h in 0..ctx.elems.len() {
            let key = ctx.image(h, &loci.items[i]).key;
            orb.insert(loci.position(&key).ok_or("image of a locus is not a locus")?);
        }
        for x in &orb {
            left.remove(x);
        }
        orbits.push(orb.into_iter().collect());
    }
    Ok(orbits)
}

// ------------------------------------------------------------ type tests

fn is_cyclic(h: &[&Iso]) -> Res<bool> {
    for g in h {
        if element_order(g, ORDER_LIMIT)? == h.len() {
            return Ok(true);
        }
    }
    Ok(false)
}

fn stratum_type(d: usize, h: &[&Iso]) -> Res<(String, String)> {
    let (k, cyc) = (h.len(), is_cyclic(h)?);
    Ok(match (d, cyc) {
        (3, true) => ("A".into(), format!("A{}", k - 1)),
        (3, false) => ("ADE-noncyclic".into(), format!("D/E(|H|={k})")),
        (0, _) => ("codim7".into(), format!("pt(|H|={k})")),
        (1, true) => ("circle".into(), format!("C3/Z{k}")),
        (1, false) => ("circle".into(), format!("nonabelian(|H|={k})")),
        (_, _) => (format!("other-dim{d}"), format!("dim{d}(|H|={k})")),
    })
}

fn fix_matrix(g: &Iso) -> Mat {
    (0..N)
        .map(|i| (0..N).map(|j| g.m[i][j] as i128 - (i == j) as i128).collect())
        .collect()
}

/// Every non-identity element of H has no fixed normal vector.
fn normal_free(h: &[&Iso], d: usize) -> bool {
    let e = Iso::identity();
    h.iter().filter(|g| ***g != e).all(|g| rank(&fix_matrix(g)) == N - d)
}

/// Trace of h on the k-1 exceptional classes of C^2/Z_k (identity or swap).
fn tau(ctx: &Ctx, hi: usize, gen: &Iso, k: usize) -> Res<i64> {
    let conj = compose(&compose(&ctx.elems[hi], gen), &ctx.inv[hi]);
    let mut cur = Iso::identity();
    for j in 1..k {
        cur = compose(gen, &cur);
        if cur == conj {
            return match j {
                1 => Ok(k as i64 - 1),
                _ if j == k - 1 => Ok((k as i64 - 1) % 2),
                _ => Err("stabiliser acts on exceptional curves non-simply".into()),
            };
        }
    }
    Err("stabiliser does not normalise the local group".into())
}

// ------------------------------------------------------ invariant forms

fn m128(g: &Iso) -> [[i128; N]; N] {
    std::array::from_fn(|i| std::array::from_fn(|j| g.m[i][j] as i128))
}

/// sum_i w_i e_p(R_i) / n for p = 0..=dim (exact rationals).
pub fn avg_forms(mats: &[Mat], dim: usize, w: Option<&[i64]>) -> Vec<Rat> {
    let es: Vec<Vec<i128>> = mats.iter().map(elem_sym).collect();
    let n = mats.len() as i128;
    (0..=dim)
        .map(|p| {
            let s: i128 = es
                .iter()
                .enumerate()
                .map(|(i, e)| w.map_or(1, |w| w[i]) as i128 * e[p])
                .sum();
            Rat::new(s, n)
        })
        .collect()
}

pub fn as_ints(v: &[Rat]) -> Res<Vec<i64>> {
    if v.iter().any(|x| !x.is_int()) {
        return Err(format!("non-integer invariant dimension {:?}", v));
    }
    Ok(v.iter().map(|x| x.n as i64).collect())
}

/// b_0..b_7 of T^7/Gamma: Gamma-invariant constant forms.
pub fn flat_betti(elems: &[Iso]) -> Res<Vec<i64>> {
    let mats: Vec<Mat> = elems
        .iter()
        .map(|g| g.m.iter().map(|r| r.iter().map(|&x| x as i128).collect()).collect())
        .collect();
    as_ints(&avg_forms(&mats, N, None))
}

// ------------------------------------------------------------ stratum row

pub struct Row {
    pub kind: String,
    pub k: usize,
    pub label: String,
    pub dim: usize,
    pub orbit_size: usize,
    pub stabiliser_order: usize,
    pub free_normal: bool,
    pub betti: Vec<i64>,
    pub exceptional: Option<Vec<f64>>,
}

fn exceptional_forms(ctx: &Ctx, h: &[&Iso], sidx: &[usize], mats: &[Mat], d: usize) -> Res<Vec<f64>> {
    let gen = h
        .iter()
        .find(|g| element_order(g, ORDER_LIMIT).ok() == Some(h.len()))
        .ok_or("no generator of the local group")?;
    let taus = sidx.iter().map(|&i| tau(ctx, i, gen, h.len())).collect::<Res<Vec<i64>>>()?;
    let f = avg_forms(mats, d, Some(&taus));
    Ok(f.iter().map(|x| x.n as f64 / x.d as f64).collect())
}

pub fn stratum_row(ctx: &Ctx, loc: &Locus, orbit_size: usize) -> Res<Row> {
    let d = loc.dim;
    let all = 0..ctx.elems.len();
    let hidx: Vec<usize> = all.clone().filter(|&i| fixes_pointwise(&ctx.elems[i], loc)).collect();
    let sidx: Vec<usize> = all.filter(|&i| ctx.image(i, loc).key == loc.key).collect();
    let h: Vec<&Iso> = hidx.iter().map(|&i| &ctx.elems[i]).collect();
    let (kind, label) = stratum_type(d, &h)?;
    let mats = sidx
        .iter()
        .map(|&i| restriction(&m128(&ctx.elems[i]), &loc.b).ok_or("locus is not preserved by its stabiliser"))
        .collect::<Result<Vec<Mat>, _>>()?;
    let betti = as_ints(&avg_forms(&mats, d, None))?;
    let exceptional =
        if kind == "A" { Some(exceptional_forms(ctx, &h, &sidx, &mats, d)?) } else { None };
    Ok(Row {
        kind,
        k: h.len(),
        label,
        dim: d,
        orbit_size,
        stabiliser_order: sidx.len(),
        free_normal: normal_free(&h, d),
        betti,
        exceptional,
    })
}

// ------------------------------------------------------- codimension 7

/// Order-preserving parallel map over `items` with `threads` workers.
fn par_map<T: Sync, R: Send>(items: &[T], threads: usize, f: impl Fn(&T) -> R + Sync) -> Vec<R> {
    let threads = threads.clamp(1, items.len().max(1));
    if threads == 1 {
        return items.iter().map(&f).collect();
    }
    let chunk = items.len().div_ceil(threads);
    std::thread::scope(|sc| {
        let hs: Vec<_> = items
            .chunks(chunk)
            .map(|c| sc.spawn(|| c.iter().map(&f).collect::<Vec<R>>()))
            .collect();
        hs.into_iter().flat_map(|h| h.join().expect("meet worker panicked")).collect()
    })
}

/// Meets of every orbit representative with every other locus.
pub fn rep_meets(loci: &LocusMap, reps: &[usize], threads: usize) -> Vec<Vec<Vec<Locus>>> {
    par_map(reps, threads, |&r| {
        let a = &loci.items[r];
        loci.items
            .iter()
            .map(|b| if a.key == b.key { vec![] } else { meet(a, b) })
            .collect()
    })
}

/// Meets (m, l) for m among pool items from `from` on, l over the whole pool.
/// A pair with a 0-dimensional member can only return that point itself,
/// which the pool already holds, so only pairs of positive dimension are met
/// (the result is identical to meeting every pair).
fn next_meets(pool: &LocusMap, from: usize, threads: usize) -> Vec<Locus> {
    let ms: Vec<&Locus> = pool.items[from..].iter().filter(|m| m.dim > 0).collect();
    let per_m = par_map(&ms, threads, |m| {
        let mut out = Vec::new();
        for l in pool.items.iter().filter(|l| l.dim > 0 && l.key != m.key) {
            out.extend(meet(m, l));
        }
        out
    });
    per_m.into_iter().flatten().collect()
}

/// 0-dimensional loci reached by repeated intersection (3 rounds) from the
/// representatives; `cached` holds the first round (rep x locus meets).
pub fn point_loci(loci: &LocusMap, cached: &[Vec<Vec<Locus>>], threads: usize) -> Vec<Locus> {
    let mut pool = LocusMap::default();
    for l in &loci.items {
        pool.insert(l.clone());
    }
    let mut new: Vec<Locus> = cached.iter().flatten().flatten().cloned().collect();
    for round in 0..3 {
        let before = pool.items.len();
        for m in new {
            pool.insert(m);
        }
        if pool.items.len() == before || round == 2 {
            break;
        }
        new = next_meets(&pool, before, threads);
    }
    pool.items.into_iter().filter(|p| p.dim == 0).collect()
}

fn no_fixed_vector(h: &[&Iso]) -> bool {
    let rows: Mat = h.iter().flat_map(|g| fix_matrix(g)).collect();
    rank(&rows) == N
}

/// Gamma-orbits of points whose stabiliser fixes no vector: (orbit size, |H|).
pub fn codim7_points(ctx: &Ctx, pts: &[Locus]) -> Vec<(usize, usize)> {
    let mut out = Vec::new();
    let mut seen = HashSet::new();
    for p in pts {
        let h: Vec<&Iso> = ctx.elems.iter().filter(|g| fixes_pointwise(g, p)).collect();
        if !no_fixed_vector(&h) || seen.contains(&p.key) {
            continue;
        }
        let orb: HashSet<_> = (0..ctx.elems.len()).map(|i| ctx.image(i, p).key).collect();
        out.push((orb.len(), h.len()));
        seen.extend(orb);
    }
    out
}
