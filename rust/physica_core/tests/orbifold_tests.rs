//! Closed-form tests for the exact-arithmetic and isometry layers of the
//! orbifold module (`num` and `iso`). Expectations are hand-computed.

use physica_core::orbifold::iso::{close_group, compose, element_order, int_inverse, Iso, DEN};
use physica_core::orbifold::num::{
    elem_sym, hnf_rows, identity_mat, rank, restriction, smith, Mat, Rat, N,
};
use physica_core::orbifold::{analyse_rows, close_group_rows};

fn unit(i: usize) -> [i128; N] {
    std::array::from_fn(|j| (i == j) as i128)
}

fn row(pairs: &[(usize, i128)]) -> [i128; N] {
    let mut r = [0i128; N];
    pairs.iter().for_each(|&(i, v)| r[i] = v);
    r
}

fn flip(coords: &[usize]) -> Iso {
    let mut g = Iso::identity();
    coords.iter().for_each(|&i| g.m[i][i] = -1);
    g
}

fn swap01() -> Iso {
    let mut g = Iso::identity();
    g.m[0][0] = 0;
    g.m[1][1] = 0;
    g.m[0][1] = 1;
    g.m[1][0] = 1;
    g
}

fn matmul(a: &Mat, b: &Mat) -> Mat {
    let n = a.len();
    (0..n).map(|i| (0..n).map(|j| (0..n).map(|k| a[i][k] * b[k][j]).sum()).collect()).collect()
}

// ------------------------------------------------------------------ Rat

#[test]
fn rat_new_reduces_and_normalises_sign() {
    assert_eq!(Rat::new(2, 4), Rat { n: 1, d: 2 });
    assert_eq!(Rat::new(3, -6), Rat { n: -1, d: 2 });
    assert_eq!(Rat::new(-3, -6), Rat { n: 1, d: 2 });
    assert_eq!(Rat::new(0, 7), Rat::ZERO);
    assert_eq!(Rat::int(5), Rat { n: 5, d: 1 });
}

#[test]
#[should_panic(expected = "zero denominator")]
fn rat_new_rejects_zero_denominator() {
    let _ = Rat::new(1, 0);
}

#[test]
fn rat_arithmetic_matches_hand_values() {
    let (h, t, q) = (Rat::new(1, 2), Rat::new(1, 3), Rat::new(1, 4));
    assert_eq!(h + t, Rat::new(5, 6));
    assert_eq!(h - t, Rat::new(1, 6));
    assert_eq!(Rat::new(2, 3) * Rat::new(3, 4), h);
    assert_eq!(h / q, Rat::int(2));
    assert_eq!(t - t, Rat::ZERO);
}

#[test]
#[should_panic]
fn rat_division_by_zero_panics() {
    let _ = Rat::int(1) / Rat::ZERO;
}

#[test]
fn rat_frac_and_predicates() {
    assert_eq!(Rat::new(7, 2).frac(), Rat::new(1, 2));
    assert_eq!(Rat::new(-1, 3).frac(), Rat::new(2, 3));
    assert_eq!(Rat::int(-4).frac(), Rat::ZERO);
    assert!(Rat::int(3).is_int() && !Rat::new(1, 2).is_int());
    assert!(Rat::ZERO.is_zero() && !Rat::new(1, 9).is_zero());
}

// ------------------------------------------------------- matrix helpers

#[test]
fn identity_mat_is_the_unit_matrix() {
    let m = identity_mat(3);
    assert_eq!(m, vec![vec![1, 0, 0], vec![0, 1, 0], vec![0, 0, 1]]);
    assert!(identity_mat(0).is_empty());
}

#[test]
fn rank_of_known_matrices() {
    assert_eq!(rank(&[]), 0);
    assert_eq!(rank(&identity_mat(N)), N);
    assert_eq!(rank(&[vec![0, 0], vec![0, 0]]), 0);
    assert_eq!(rank(&[vec![1, 2, 3], vec![4, 5, 6], vec![7, 8, 9]]), 2);
    assert_eq!(rank(&[vec![1, 2, 3], vec![2, 4, 6]]), 1);
}

#[test]
fn elem_sym_of_known_spectra() {
    assert_eq!(elem_sym(&identity_mat(2)), vec![1, 2, 1]);
    assert_eq!(elem_sym(&vec![vec![0, 0], vec![0, 0]]), vec![1, 0, 0]);
    assert_eq!(elem_sym(&vec![vec![2, 0], vec![0, 3]]), vec![1, 5, 6]);
    assert_eq!(elem_sym(&vec![vec![0, 1], vec![1, 0]]), vec![1, 0, -1]);
}

#[test]
fn smith_satisfies_u_a_v_equals_d() {
    let cases: Vec<Mat> = vec![
        vec![vec![2, 4], vec![6, 8]],
        vec![vec![1, 2, 3], vec![4, 5, 6], vec![7, 8, 10]],
        vec![vec![0, 3], vec![5, 0]],
    ];
    for a in cases {
        let s = smith(&a);
        assert_eq!(matmul(&matmul(&s.u, &a), &s.v), s.d);
        let n = a.len();
        for i in 0..n {
            for j in (0..n).filter(|&j| j != i) {
                assert_eq!(s.d[i][j], 0);
            }
        }
    }
}

#[test]
fn smith_diagonal_product_is_the_determinant_magnitude() {
    let s = smith(&vec![vec![2, 4], vec![6, 8]]);
    assert_eq!((s.d[0][0] * s.d[1][1]).abs(), 8);
    let s = smith(&vec![vec![1, 2, 3], vec![4, 5, 6], vec![7, 8, 10]]);
    assert_eq!((s.d[0][0] * s.d[1][1] * s.d[2][2]).abs(), 3);
}

#[test]
fn smith_rank_of_deficient_and_zero_matrices() {
    assert_eq!(smith(&vec![vec![1, 2], vec![2, 4]]).rank, 1);
    assert_eq!(smith(&vec![vec![0, 0], vec![0, 0]]).rank, 0);
    assert_eq!(smith(&identity_mat(4)).rank, 4);
}

#[test]
fn hnf_of_known_lattices() {
    let two = [row(&[(0, 2), (1, 4)]), row(&[(1, 6)])];
    assert_eq!(hnf_rows(&two), two.to_vec());
    let diag = [row(&[(0, 1), (1, 1)]), row(&[(0, 1), (1, -1)])];
    assert_eq!(hnf_rows(&diag), vec![row(&[(0, 1), (1, 1)]), row(&[(1, 2)])]);
    let dup = [unit(3), unit(3)];
    assert_eq!(hnf_rows(&dup), vec![unit(3)]);
    assert!(hnf_rows(&[[0i128; N]]).is_empty());
    assert!(hnf_rows(&[]).is_empty());
}

#[test]
fn hnf_is_idempotent_and_sign_normalised() {
    let rows = [row(&[(0, -3), (2, 6)]), row(&[(0, 2), (1, 5)]), row(&[(2, 4)])];
    let h = hnf_rows(&rows);
    assert_eq!(hnf_rows(&h), h);
    assert!(h.iter().all(|r| r.iter().find(|&&x| x != 0).is_some_and(|&x| x > 0)));
}

fn swapped_identity() -> [[i128; N]; N] {
    let mut sw: [[i128; N]; N] = std::array::from_fn(unit);
    sw[0] = unit(1);
    sw[1] = unit(0);
    sw
}

#[test]
fn restriction_of_invariant_spans() {
    let ident: [[i128; N]; N] = std::array::from_fn(unit);
    let r = restriction(&ident, &[unit(0), unit(1)]).unwrap();
    assert_eq!(r, vec![vec![1, 0], vec![0, 1]]);
    let sw = swapped_identity();
    let r = restriction(&sw, &[unit(0), unit(1)]).unwrap();
    assert_eq!(r, vec![vec![0, 1], vec![1, 0]]);
    assert_eq!(restriction(&sw, &[]), Some(vec![]));
}

#[test]
fn restriction_rejects_non_invariant_and_non_integral() {
    assert_eq!(restriction(&swapped_identity(), &[unit(0)]), None);
    let mut shear: [[i128; N]; N] = std::array::from_fn(unit);
    shear[0][1] = 1;
    let b = [row(&[(0, 2)]), unit(1)];
    assert_eq!(restriction(&shear, &b), None);
}

// ------------------------------------------------------------------ Iso

#[test]
fn identity_row_has_ones_on_the_matrix_diagonal() {
    let r = Iso::identity().to_row();
    assert_eq!(r.len(), N * N + N);
    for (k, v) in r.iter().enumerate() {
        let on_diag = k < N * N && k % (N + 1) == 0;
        assert_eq!(*v, on_diag as i64, "entry {k}");
    }
}

#[test]
fn from_row_round_trips_and_reduces_translations() {
    let mut r = Iso::identity().to_row();
    r[N * N] = -1;
    r[N * N + 1] = 13;
    let g = Iso::from_row(&r).unwrap();
    assert_eq!(&g.c[..2], &[DEN - 1, 1]);
    assert_eq!(Iso::from_row(&g.to_row()).unwrap(), g);
}

#[test]
fn from_row_rejects_wrong_lengths() {
    assert!(Iso::from_row(&[]).is_err());
    assert!(Iso::from_row(&vec![0; N * N + N - 1]).is_err());
    assert!(Iso::from_row(&vec![0; N * N + N + 1]).is_err());
}

#[test]
fn compose_adds_translations_modulo_den() {
    let (mut a, mut b) = (Iso::identity(), Iso::identity());
    a.c[0] = 5;
    b.c[0] = 9;
    assert_eq!(compose(&a, &b).c[0], 2);
    assert_eq!(compose(&a, &Iso::identity()), a);
    assert_eq!(compose(&Iso::identity(), &a), a);
}

#[test]
fn compose_applies_the_right_factor_first() {
    let mut f = flip(&[0]);
    f.c[0] = 3;
    let mut t = Iso::identity();
    t.c[0] = 2;
    assert_eq!(compose(&f, &t).c[0], 1);
    assert_eq!(compose(&t, &f).c[0], 5);
}

#[test]
fn int_inverse_of_known_matrices() {
    let id = Iso::identity().m;
    assert_eq!(int_inverse(&id).unwrap(), id);
    let mut shear = id;
    shear[0][1] = 3;
    let inv = int_inverse(&shear).unwrap();
    assert_eq!(inv[0][1], -3);
    assert_eq!(inv[1][1], 1);
    assert_eq!(int_inverse(&flip(&[2]).m).unwrap(), flip(&[2]).m);
}

#[test]
fn int_inverse_rejects_singular_and_non_unimodular() {
    assert_eq!(int_inverse(&[[0; N]; N]).unwrap_err(), "singular matrix");
    let mut two = Iso::identity().m;
    two[0][0] = 2;
    assert!(int_inverse(&two).unwrap_err().contains("not integral"));
}

#[test]
fn element_order_of_known_elements() {
    assert_eq!(element_order(&Iso::identity(), 5).unwrap(), 1);
    assert_eq!(element_order(&flip(&[0, 1, 2, 3]), 5).unwrap(), 2);
    assert_eq!(element_order(&swap01(), 5).unwrap(), 2);
    let mut t = Iso::identity();
    t.c[0] = 4;
    assert_eq!(element_order(&t, 12).unwrap(), 3);
}

#[test]
fn element_order_fails_above_the_limit() {
    let mut t = Iso::identity();
    t.c[0] = 1;
    assert!(element_order(&t, 11).unwrap_err().contains("exceeds 11"));
    assert!(element_order(&flip(&[0]), 0).is_err());
}

#[test]
fn close_group_orders_of_small_groups() {
    assert_eq!(close_group(&[], 4).unwrap(), vec![Iso::identity()]);
    assert_eq!(close_group(&[flip(&[0, 1, 2, 3])], 10).unwrap().len(), 2);
    assert_eq!(close_group(&[flip(&[0]), flip(&[1])], 10).unwrap().len(), 4);
    assert_eq!(close_group(&[flip(&[0]), flip(&[1]), flip(&[2])], 10).unwrap().len(), 8);
    let mut c3 = Iso::identity();
    c3.m[0][0] = 0;
    c3.m[1][1] = 0;
    c3.m[2][2] = 0;
    c3.m[1][0] = 1;
    c3.m[2][1] = 1;
    c3.m[0][2] = 1;
    assert_eq!(close_group(&[c3, swap01()], 10).unwrap().len(), 6);
}

#[test]
fn close_group_starts_with_identity_and_has_no_duplicates() {
    let g = close_group(&[flip(&[0]), flip(&[1])], 10).unwrap();
    assert_eq!(g[0], Iso::identity());
    let set: std::collections::HashSet<_> = g.iter().collect();
    assert_eq!(set.len(), g.len());
}

#[test]
fn close_group_rows_round_trips_the_flat_encoding() {
    let flat = flip(&[0, 1]).to_row();
    let out = close_group_rows(&flat, 10).unwrap();
    assert_eq!(out.len(), 2 * (N * N + N));
    assert_eq!(&out[..N * N + N], &Iso::identity().to_row()[..]);
}

#[test]
fn close_group_rows_rejects_bad_buffer_and_over_limit() {
    assert!(close_group_rows(&[1, 2, 3], 10).unwrap_err().contains("not a multiple"));
    let mut t = Iso::identity();
    t.c[0] = 1;
    assert!(close_group_rows(&t.to_row(), 11).unwrap_err().contains("exceeds"));
}

#[test]
fn analyse_rows_on_the_negation_group_has_128_codim7_points() {
    let neg = flip(&[0, 1, 2, 3, 4, 5, 6]);
    let flat = close_group_rows(&neg.to_row(), 10).unwrap();
    let v: serde_json::Value = serde_json::from_str(&analyse_rows(&flat, 2).unwrap()).unwrap();
    assert_eq!(v["order"], 2);
    assert_eq!(v["n_loci"], 128);
    assert_eq!(v["crossings"], 0);
    assert_eq!(v["flat_betti"], serde_json::json!([1, 0, 21, 0, 35, 0, 7, 0]));
    let c7 = v["codim7"].as_array().unwrap();
    assert_eq!(c7.len(), 128);
    assert!(c7.iter().all(|p| p["orbit_size"] == 1 && p["stabiliser_order"] == 2));
}

#[test]
fn analyse_rows_rejects_a_singular_element() {
    let mut bad = Iso::identity().to_row();
    bad.iter_mut().take(N * N).for_each(|x| *x = 0);
    assert!(analyse_rows(&bad, 1).is_err());
}
