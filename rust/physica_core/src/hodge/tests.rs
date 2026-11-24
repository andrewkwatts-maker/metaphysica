//! Unit tests for the `hodge` module.

use super::*;

/// The standard flat G2 3-form. The metric is the identity, so the raised
/// form equals the lowered one and `phi_up == phi`.
fn standard_phi() -> Vec<f64> {
    const TRIPLES: [[usize; 3]; 7] = [
        [0, 1, 2],
        [0, 3, 4],
        [0, 5, 6],
        [1, 3, 5],
        [1, 4, 6],
        [2, 3, 6],
        [2, 4, 5],
    ];
    let mut phi = vec![0.0_f64; RANK3_LEN];
    for t in TRIPLES.iter() {
        for p in PERM3.iter() {
            let (a, b, c) = (t[p[0]], t[p[1]], t[p[2]]);
            phi[(a * DIM + b) * DIM + c] = parity(p);
        }
    }
    phi
}

#[test]
fn levi_civita_is_zero_exactly_on_repeats() {
    // Bounded sweep over every index 7-tuple: 7^7 = 823,543.
    let total = DIM.pow(7);
    let mut nonzero = 0_usize;
    for flat in 0..total {
        let mut idx = [0_usize; DIM];
        let mut rest = flat;
        for slot in idx.iter_mut().rev() {
            *slot = rest % DIM;
            rest /= DIM;
        }
        let mut sorted = idx;
        sorted.sort_unstable();
        let distinct = sorted.windows(2).all(|w| w[0] != w[1]);
        let s = levi_civita_sign(&idx);
        if distinct {
            assert_eq!(s.abs(), 1.0, "distinct tuple {idx:?} gave {s}");
            nonzero += 1;
        } else {
            assert_eq!(s, 0.0, "repeated tuple {idx:?} gave {s}");
        }
    }
    assert_eq!(nonzero, 5040, "7! tuples must be non-zero");
}

#[test]
fn levi_civita_flips_sign_on_a_transposition() {
    let base = [0, 1, 2, 3, 4, 5, 6];
    assert_eq!(levi_civita_sign(&base), 1.0);
    let swapped = [1, 0, 2, 3, 4, 5, 6];
    assert_eq!(levi_civita_sign(&swapped), -1.0);
    let twice = [1, 0, 3, 2, 4, 5, 6];
    assert_eq!(levi_civita_sign(&twice), 1.0);
}

#[test]
fn perm4_is_lexicographic_and_complete() {
    let mut seen = std::collections::HashSet::new();
    for p in PERM4.iter() {
        assert!(seen.insert(*p), "duplicate permutation {p:?}");
    }
    assert_eq!(seen.len(), 24);
    for w in PERM4.windows(2) {
        assert!(w[0] < w[1], "PERM4 is not ascending at {:?}", w[0]);
    }
}

#[test]
fn perm3_is_lexicographic_and_complete() {
    let mut seen = std::collections::HashSet::new();
    for p in PERM3.iter() {
        assert!(seen.insert(*p), "duplicate permutation {p:?}");
    }
    assert_eq!(seen.len(), 6);
    for w in PERM3.windows(2) {
        assert!(w[0] < w[1], "PERM3 is not ascending at {:?}", w[0]);
    }
}

#[test]
fn complement_of_a_triple_has_four_ascending_indices() {
    let mut out = [0_usize; DIM];
    let n = complement(&[2, 0, 5], &mut out);
    assert_eq!(n, 4);
    assert_eq!(&out[..4], &[1, 3, 4, 6]);
}

#[test]
fn star_of_phi_has_the_coassociative_support() {
    let phi = standard_phi();
    let star = hodge_star_3form(&phi, 1.0).unwrap();
    // *phi is the coassociative 4-form: 7 index quadruples, each with 24
    // signed orderings, so 168 non-zero components of magnitude 1.
    let nonzero = star.iter().filter(|v| v.abs() > 1e-12).count();
    assert_eq!(nonzero, 7 * 24, "star-phi support");
    assert!(star
        .iter()
        .all(|v| v.abs() < 1e-12 || (v.abs() - 1.0).abs() < 1e-12));
}

#[test]
fn hodge_involution_holds_for_the_standard_g2_form() {
    let phi = standard_phi();
    let star = hodge_star_3form(&phi, 1.0).unwrap();
    let err = hodge_involution_max_error(&phi, &star, 1.0).unwrap();
    assert!(err < 1e-12, "double dual differs from phi by {err:e}");
}

#[test]
fn wrong_length_is_an_error_not_a_default() {
    let err = hodge_star_3form(&[0.0; 10], 1.0).unwrap_err();
    assert!(matches!(
        err,
        HodgeError::BadLength {
            expected: 343,
            got: 10
        }
    ));
}

#[test]
fn non_finite_input_is_rejected() {
    let mut phi = standard_phi();
    phi[17] = f64::NAN;
    let err = hodge_star_3form(&phi, 1.0).unwrap_err();
    assert!(matches!(err, HodgeError::NonFiniteInput { index: 17, .. }));
}

#[test]
fn non_positive_determinant_is_rejected() {
    let phi = standard_phi();
    assert!(matches!(
        hodge_star_3form(&phi, 0.0).unwrap_err(),
        HodgeError::BadDeterminant(_)
    ));
    assert!(matches!(
        hodge_star_3form(&phi, f64::INFINITY).unwrap_err(),
        HodgeError::BadDeterminant(_)
    ));
}

/// The shortcut must agree with the dense `7^4` inner sum term for term,
/// not merely to a tolerance. This is the claim the module rests on.
#[test]
fn four_form_shortcut_matches_the_dense_contraction() {
    let phi = standard_phi();
    let star = hodge_star_3form(&phi, 1.0).unwrap();
    let fast = hodge_star_4form(&star, 1.0).unwrap();

    let mut slow = vec![0.0_f64; RANK3_LEN];
    for i in 0..DIM {
        for j in 0..DIM {
            for k in 0..DIM {
                let mut val = 0.0_f64;
                for a in 0..DIM {
                    for b in 0..DIM {
                        for c in 0..DIM {
                            for d in 0..DIM {
                                let eps = levi_civita_sign(&[a, b, c, d, i, j, k]);
                                val += star[((a * DIM + b) * DIM + c) * DIM + d] * eps;
                            }
                        }
                    }
                }
                slow[(i * DIM + j) * DIM + k] = val / 24.0;
            }
        }
    }
    for (f, s) in fast.iter().zip(slow.iter()) {
        assert_eq!(f.to_bits(), s.to_bits(), "the shortcut is not bit-exact");
    }
}
