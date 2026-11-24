//! Closed-form tests for the locus and strata layers of the orbifold module.
//! Expectations are hand-computed from small groups on the 7-torus.

use physica_core::orbifold::iso::{close_group, int_inverse, Iso};
use physica_core::orbifold::locus::{
    fixed_loci, fixes_pointwise, image_locus, make_locus, meet, torus_solve, Locus, LocusMap,
};
use physica_core::orbifold::num::{Mat, Rat, N};
use physica_core::orbifold::strata::{
    as_ints, avg_forms, codim7_points, flat_betti, orbits_of_loci, point_loci, rep_meets,
    stratum_row, unique_loci, Ctx,
};
use physica_core::orbifold::analyse_rows;

fn unit(i: usize) -> [i128; N] {
    std::array::from_fn(|j| (i == j) as i128)
}

fn flip(coords: &[usize]) -> Iso {
    let mut g = Iso::identity();
    coords.iter().for_each(|&i| g.m[i][i] = -1);
    g
}

fn shift(i: usize, twelfths: i64) -> Iso {
    let mut g = Iso::identity();
    g.c[i] = twelfths;
    g
}

fn point(vals: &[(usize, Rat)]) -> [Rat; N] {
    let mut u = [Rat::ZERO; N];
    vals.iter().for_each(|&(i, v)| u[i] = v);
    u
}

fn half() -> Rat {
    Rat::new(1, 2)
}

/// Group of order 4: x0 -> -x0.. flip of x0..x3 and a half shift of x0.
fn flip_and_half_shift() -> Vec<Iso> {
    close_group(&[flip(&[0, 1, 2, 3]), shift(0, 6)], 16).unwrap()
}

// ---------------------------------------------------------- torus_solve

#[test]
fn torus_solve_scalar_equations() {
    let two: Mat = vec![vec![2]];
    let s = torus_solve(&two, &[Rat::ZERO]);
    let mut pts: Vec<Rat> = s.points.iter().map(|p| p[0]).collect();
    pts.sort_by_key(|r| (r.n * 10) / r.d);
    assert_eq!(pts, vec![Rat::ZERO, half()]);
    assert!(s.free.is_empty());
    let s = torus_solve(&two, &[half()]);
    let mut pts: Vec<Rat> = s.points.iter().map(|p| p[0]).collect();
    pts.sort_by_key(|r| (r.n * 10) / r.d);
    assert_eq!(pts, vec![Rat::new(1, 4), Rat::new(3, 4)]);
}

#[test]
fn torus_solve_unit_and_zero_coefficients() {
    let one: Mat = vec![vec![1]];
    let s = torus_solve(&one, &[Rat::new(1, 3)]);
    assert_eq!(s.points, vec![vec![Rat::new(1, 3)]]);
    let zero: Mat = vec![vec![0]];
    let s = torus_solve(&zero, &[Rat::ZERO]);
    assert_eq!(s.points, vec![vec![Rat::ZERO]]);
    assert_eq!(s.free, vec![vec![1]]);
}

#[test]
fn torus_solve_inconsistent_system_has_no_solution() {
    let zero: Mat = vec![vec![0]];
    let s = torus_solve(&zero, &[half()]);
    assert!(s.points.is_empty() && s.free.is_empty());
}

// ------------------------------------------------------------ make_locus

#[test]
fn make_locus_of_a_coordinate_subtorus() {
    let l = make_locus(point(&[(0, half())]), vec![unit(4), unit(5), unit(6)]);
    assert_eq!(l.dim, 3);
    assert_eq!(l.key.h, vec![unit(0), unit(1), unit(2), unit(3)]);
    assert_eq!(l.key.phase, vec![half(), Rat::ZERO, Rat::ZERO, Rat::ZERO]);
    for row in &l.k {
        for b in &l.b {
            assert_eq!((0..N).map(|i| row[i] * b[i]).sum::<i128>(), 0);
        }
    }
}

#[test]
fn make_locus_of_a_point_annihilates_everything() {
    let l = make_locus(point(&[(2, Rat::new(1, 3))]), vec![]);
    assert_eq!(l.dim, 0);
    assert_eq!(l.key.h, (0..N).map(unit).collect::<Vec<_>>());
    assert_eq!(l.key.phase[2], Rat::new(1, 3));
}

#[test]
fn locus_key_ignores_whole_number_shifts_of_the_base_point() {
    let a = make_locus(point(&[(0, Rat::new(1, 4))]), vec![unit(1)]);
    let b = make_locus(point(&[(0, Rat::new(5, 4)), (1, half())]), vec![unit(1)]);
    assert_eq!(a.key, b.key);
    let c = make_locus(point(&[(0, Rat::new(3, 4))]), vec![unit(1)]);
    assert_ne!(a.key, c.key);
}

// ---------------------------------------------------------- fixed_loci

#[test]
fn identity_fixes_the_whole_torus() {
    let loci = fixed_loci(&Iso::identity());
    assert_eq!(loci.len(), 1);
    assert_eq!(loci[0].dim, N);
}

#[test]
fn pure_translation_has_no_fixed_point() {
    assert!(fixed_loci(&shift(0, 1)).is_empty());
}

#[test]
fn four_coordinate_flip_has_sixteen_three_dimensional_loci() {
    let g = flip(&[0, 1, 2, 3]);
    let loci = fixed_loci(&g);
    assert_eq!(loci.len(), 16);
    let keys: std::collections::HashSet<_> = loci.iter().map(|l| &l.key).collect();
    assert_eq!(keys.len(), 16);
    for l in &loci {
        assert_eq!(l.dim, 3);
        assert!(l.u0.iter().all(|x| (Rat::int(2) * *x).is_int()));
        assert!(fixes_pointwise(&g, l));
    }
}

#[test]
fn flip_with_half_translation_fixes_quarter_points() {
    let mut g = flip(&[0]);
    g.c[0] = 6;
    let loci = fixed_loci(&g);
    assert_eq!(loci.len(), 2);
    let mut x0: Vec<Rat> = loci.iter().map(|l| l.u0[0]).collect();
    x0.sort_by_key(|r| r.n * 8 / r.d);
    assert_eq!(x0, vec![Rat::new(1, 4), Rat::new(3, 4)]);
    assert!(loci.iter().all(|l| l.dim == 6));
}

// ------------------------------------------------------ fixes_pointwise

#[test]
fn fixes_pointwise_distinguishes_set_and_pointwise_fixing() {
    let loci = fixed_loci(&flip(&[0, 1, 2, 3]));
    let l = &loci[0];
    assert!(fixes_pointwise(&Iso::identity(), l));
    assert!(!fixes_pointwise(&flip(&[4]), l));
    assert!(!fixes_pointwise(&shift(0, 6), l));
    let mut swap45 = Iso::identity();
    swap45.m[4] = [0, 0, 0, 0, 0, 1, 0];
    swap45.m[5] = [0, 0, 0, 0, 1, 0, 0];
    assert!(!fixes_pointwise(&swap45, l));
}

// ---------------------------------------------------------- image_locus

#[test]
fn image_locus_under_identity_is_unchanged() {
    let l = make_locus(point(&[(0, half())]), vec![unit(4)]);
    let id = Iso::identity();
    let img = image_locus(&id, &id.m, &l);
    assert_eq!(img.key, l.key);
}

#[test]
fn image_locus_moves_the_base_point_by_the_map() {
    let l = make_locus(point(&[(0, half())]), vec![unit(4)]);
    let mut g = Iso::identity();
    g.m[0][0] = 0;
    g.m[1][1] = 0;
    g.m[1][0] = 1;
    g.m[0][1] = 1;
    g.c[2] = 3;
    let inv = int_inverse(&g.m).unwrap();
    let img = image_locus(&g, &inv, &l);
    assert_eq!(img.u0, point(&[(1, half()), (2, Rat::new(1, 4))]));
    assert_eq!(img.dim, 1);
    let expect = make_locus(img.u0, vec![unit(4)]);
    assert_eq!(img.key, expect.key);
}

// ----------------------------------------------------------------- meet

fn line(dir: &[(usize, i128)]) -> Locus {
    let mut d = [0i128; N];
    dir.iter().for_each(|&(i, v)| d[i] = v);
    make_locus([Rat::ZERO; N], vec![d])
}

#[test]
fn meet_of_two_coordinate_lines_is_the_origin() {
    let m = meet(&line(&[(0, 1)]), &line(&[(1, 1)]));
    assert_eq!(m.len(), 1);
    assert_eq!(m[0].dim, 0);
    assert_eq!(m[0].u0, [Rat::ZERO; N]);
}

#[test]
fn meet_of_diagonal_lines_has_two_points() {
    let m = meet(&line(&[(0, 1), (1, 1)]), &line(&[(0, 1), (1, -1)]));
    assert_eq!(m.len(), 2);
    assert!(m.iter().all(|l| l.dim == 0));
    let mut pts: Vec<[Rat; N]> = m.iter().map(|l| l.u0).collect();
    pts.sort_by_key(|p| p[0].n);
    assert_eq!(pts[0], [Rat::ZERO; N]);
    assert_eq!(pts[1], point(&[(0, half()), (1, half())]));
}

#[test]
fn meet_of_a_locus_with_itself_is_itself() {
    let a = line(&[(0, 1)]);
    let m = meet(&a, &a);
    assert_eq!(m.len(), 1);
    assert_eq!(m[0].key, a.key);
}

#[test]
fn meet_of_disjoint_parallel_lines_is_empty() {
    let a = line(&[(0, 1)]);
    let b = make_locus(point(&[(1, half())]), vec![unit(0)]);
    assert!(meet(&a, &b).is_empty());
}

#[test]
fn meet_of_two_points_is_empty_by_convention() {
    let p = make_locus([Rat::ZERO; N], vec![]);
    assert!(meet(&p, &p).is_empty());
}

// ------------------------------------------------------------ LocusMap

#[test]
fn locus_map_keeps_insertion_order_and_rejects_duplicates() {
    let mk = |q: i128| make_locus(point(&[(0, Rat::new(q, 8))]), vec![unit(1)]);
    let mut map = LocusMap::default();
    assert!(map.insert(mk(1)));
    assert!(map.insert(mk(2)));
    assert!(!map.insert(mk(9)));
    assert_eq!(map.items.len(), 2);
    assert!(map.contains(&mk(1).key) && !map.contains(&mk(3).key));
    assert_eq!(map.position(&mk(2).key), Some(1));
    assert_eq!(map.position(&mk(1).key), Some(0));
    assert_eq!(map.position(&mk(5).key), None);
}

// ------------------------------------------------------------------ Ctx

#[test]
fn ctx_inverses_compose_to_the_identity() {
    let elems = flip_and_half_shift();
    let ctx = Ctx::new(&elems).unwrap();
    for (g, h) in elems.iter().zip(&ctx.inv) {
        assert_eq!(physica_core::orbifold::iso::compose(g, h), Iso::identity());
    }
}

#[test]
fn ctx_rejects_a_singular_element_without_partial_output() {
    let mut bad = Iso::identity();
    bad.m = [[0; N]; N];
    assert!(Ctx::new(&[Iso::identity(), bad]).is_err());
}

#[test]
fn ctx_image_by_identity_keeps_the_locus() {
    let elems = flip_and_half_shift();
    let ctx = Ctx::new(&elems).unwrap();
    let l = make_locus(point(&[(0, Rat::new(1, 4))]), vec![unit(4)]);
    assert_eq!(ctx.image(0, &l).key, l.key);
    let moved = ctx.image(elems.iter().position(|g| *g == shift(0, 6)).unwrap(), &l);
    assert_eq!(moved.u0[0], Rat::new(3, 4));
}

// ------------------------------------------------- unique_loci / orbits

#[test]
fn unique_loci_excludes_the_identity() {
    assert!(unique_loci(&[Iso::identity()]).items.is_empty());
    assert_eq!(unique_loci(&[Iso::identity(), flip(&[0, 1, 2, 3])]).items.len(), 16);
}

#[test]
fn flip_with_shift_group_has_32_loci_in_16_orbits_of_two() {
    let elems = flip_and_half_shift();
    assert_eq!(elems.len(), 4);
    let loci = unique_loci(&elems);
    assert_eq!(loci.items.len(), 32);
    let ctx = Ctx::new(&elems).unwrap();
    let orbs = orbits_of_loci(&ctx, &loci).unwrap();
    assert_eq!(orbs.len(), 16);
    assert!(orbs.iter().all(|o| o.len() == 2));
    let mut all: Vec<usize> = orbs.concat();
    all.sort_unstable();
    assert_eq!(all, (0..32).collect::<Vec<_>>());
}

#[test]
fn orbits_of_loci_rejects_a_locus_set_not_closed_under_the_group() {
    let elems = flip_and_half_shift();
    let ctx = Ctx::new(&elems).unwrap();
    let mut partial = LocusMap::default();
    partial.insert(fixed_loci(&flip(&[0, 1, 2, 3])).remove(0));
    assert!(orbits_of_loci(&ctx, &partial).is_err());
}

// --------------------------------------------- forms and Betti numbers

#[test]
fn avg_forms_weights_and_averages_exactly() {
    let id2: Mat = vec![vec![1, 0], vec![0, 1]];
    let neg: Mat = vec![vec![-1, 0], vec![0, -1]];
    let mats = [id2, neg];
    let plain = avg_forms(&mats, 2, None);
    assert_eq!(plain, vec![Rat::int(1), Rat::ZERO, Rat::int(1)]);
    let weighted = avg_forms(&mats, 2, Some(&[3, 1]));
    assert_eq!(weighted, vec![Rat::int(2), Rat::int(2), Rat::int(2)]);
    assert_eq!(avg_forms(&mats[..1], 0, None), vec![Rat::int(1)]);
}

#[test]
fn as_ints_accepts_integers_and_rejects_fractions() {
    assert_eq!(as_ints(&[Rat::int(3), Rat::new(-4, 2)]).unwrap(), vec![3, -2]);
    assert!(as_ints(&[Rat::int(1), half()]).unwrap_err().contains("non-integer"));
    assert!(as_ints(&[]).unwrap().is_empty());
}

#[test]
fn flat_betti_of_trivial_and_flip_groups() {
    assert_eq!(flat_betti(&[Iso::identity()]).unwrap(), vec![1, 7, 21, 35, 35, 21, 7, 1]);
    let g = [Iso::identity(), flip(&[0, 1, 2, 3])];
    assert_eq!(flat_betti(&g).unwrap(), vec![1, 3, 9, 19, 19, 9, 3, 1]);
    assert_eq!(flat_betti(&flip_and_half_shift()).unwrap(), vec![1, 3, 9, 19, 19, 9, 3, 1]);
}

#[test]
fn flat_betti_rejects_a_non_group_with_fractional_average() {
    let elems = [Iso::identity(), Iso::identity(), flip(&[0, 1, 2, 3])];
    assert!(flat_betti(&elems).is_err());
}

// ---------------------------------------------------------- stratum_row

#[test]
fn stratum_row_of_a1_locus_in_the_shift_group() {
    let elems = flip_and_half_shift();
    let ctx = Ctx::new(&elems).unwrap();
    let loci = unique_loci(&elems);
    let orbs = orbits_of_loci(&ctx, &loci).unwrap();
    let r = stratum_row(&ctx, &loci.items[orbs[0][0]], orbs[0].len()).unwrap();
    assert_eq!((r.kind.as_str(), r.label.as_str()), ("A", "A1"));
    assert_eq!((r.k, r.dim, r.orbit_size, r.stabiliser_order), (2, 3, 2, 2));
    assert!(r.free_normal);
    assert_eq!(r.betti, vec![1, 3, 3, 1]);
    assert_eq!(r.exceptional, Some(vec![1.0, 3.0, 3.0, 1.0]));
}

#[test]
fn stratum_row_of_an_isolated_point_is_codim7() {
    let elems = close_group(&[flip(&[0, 1, 2, 3, 4, 5, 6])], 4).unwrap();
    let ctx = Ctx::new(&elems).unwrap();
    let loci = unique_loci(&elems);
    let r = stratum_row(&ctx, &loci.items[0], 1).unwrap();
    assert_eq!(r.kind, "codim7");
    assert_eq!(r.label, "pt(|H|=2)");
    assert_eq!((r.dim, r.stabiliser_order, r.betti.clone()), (0, 2, vec![1]));
    assert!(r.exceptional.is_none());
}

#[test]
fn stratum_row_of_a_locus_with_trivial_stabiliser() {
    let elems = close_group(&[flip(&[0, 1, 2, 3])], 4).unwrap();
    let ctx = Ctx::new(&elems).unwrap();
    let skew = make_locus([Rat::ZERO; N], vec![[1, 0, 0, 0, 1, 0, 0]]);
    let r = stratum_row(&ctx, &skew, 2).unwrap();
    assert_eq!((r.kind.as_str(), r.label.as_str()), ("circle", "C3/Z1"));
    assert_eq!((r.dim, r.k, r.stabiliser_order, r.betti), (1, 1, 1, vec![1, 1]));
}

// ------------------------------------------- meets, points, codim 7

#[test]
fn rep_meets_is_thread_count_independent_and_skips_self() {
    let elems = close_group(&[flip(&[0, 1, 2, 3, 4, 5, 6])], 4).unwrap();
    let loci = unique_loci(&elems);
    let reps = [0usize, 5, 100];
    let one = rep_meets(&loci, &reps, 1);
    let four = rep_meets(&loci, &reps, 4);
    assert_eq!(one.len(), 3);
    assert!(one.iter().all(|per| per.len() == 128));
    assert!(one.iter().flatten().all(|m| m.is_empty()));
    assert_eq!(four.len(), one.len());
}

#[test]
fn point_loci_of_isolated_points_returns_them_all() {
    let elems = close_group(&[flip(&[0, 1, 2, 3, 4, 5, 6])], 4).unwrap();
    let loci = unique_loci(&elems);
    let cached = rep_meets(&loci, &[0], 1);
    assert_eq!(point_loci(&loci, &cached, 2).len(), 128);
}

#[test]
fn point_loci_of_parallel_three_tori_has_no_points() {
    let elems = close_group(&[flip(&[0, 1, 2, 3])], 4).unwrap();
    let loci = unique_loci(&elems);
    let cached = rep_meets(&loci, &[0], 1);
    assert!(point_loci(&loci, &cached, 1).is_empty());
}

#[test]
fn codim7_points_of_the_negation_group() {
    let elems = close_group(&[flip(&[0, 1, 2, 3, 4, 5, 6])], 4).unwrap();
    let ctx = Ctx::new(&elems).unwrap();
    let loci = unique_loci(&elems);
    let out = codim7_points(&ctx, &loci.items);
    assert_eq!(out.len(), 128);
    assert!(out.iter().all(|&p| p == (1, 2)));
    assert!(codim7_points(&ctx, &[]).is_empty());
}

#[test]
fn codim7_points_skip_points_whose_stabiliser_fixes_a_vector() {
    let elems = close_group(&[flip(&[0, 1, 2, 3])], 4).unwrap();
    let ctx = Ctx::new(&elems).unwrap();
    let p = make_locus([Rat::ZERO; N], vec![]);
    assert!(codim7_points(&ctx, &[p]).is_empty());
}

#[test]
fn shift_group_analysis_reports_sixteen_orbit_strata() {
    let elems = flip_and_half_shift();
    let flat: Vec<i64> = elems.iter().flat_map(|g| g.to_row()).collect();
    let v: serde_json::Value = serde_json::from_str(&analyse_rows(&flat, 2).unwrap()).unwrap();
    assert_eq!((v["order"].clone(), v["n_loci"].clone()), (4.into(), 32.into()));
    let strata = v["strata"].as_array().unwrap();
    assert_eq!(strata.len(), 16);
    assert!(strata.iter().all(|s| s["orbit_size"] == 2 && s["stabiliser_order"] == 2));
    assert_eq!(v["codim7"].as_array().unwrap().len(), 0);
}
