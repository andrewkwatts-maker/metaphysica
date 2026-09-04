//====== Metaphysica/rust/physica_core/src/hodge.rs ======//
//!copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! Hodge-star kernels on R^7 -- the measured hot path of the simulation suite.
//!
//! Ports the two pure-Python contraction loops in
//! `simulations/PM/geometry/g2_differential.py`:
//!
//! * `compute_hodge_star`      -- 3-form to 4-form, the coassociative `*phi`
//! * `check_hodge_involution`  -- 4-form back to 3-form, verifying `**phi = phi`
//!
//! A cProfile run of the whole simulation suite (20.2 s wall, 13.4 s of which
//! is `_io.open`) attributed 1.98 s of *self* time to `check_hodge_involution`
//! alone -- roughly half of all non-I/O compute in the suite. The reason is the
//! seven-deep Python loop: `7^3` output components, each summing `7^4` products
//! against a dense `7^7` Levi-Civita tensor, i.e. 823,543 interpreted
//! multiply-adds per call.
//!
//! ## Why this is also an algorithmic fix, not only a language fix
//!
//! `eps[a,b,c,d,i,j,k]` vanishes unless `{a,b,c,d}` is exactly the complement
//! of `{i,j,k}` in `0..7`. Of the 2401 inner terms only 24 -- the permutations
//! of that complement -- can be non-zero. Enumerating the complement directly
//! turns `7^3 * 7^4` into `7^3 * 4!`, a hundred-fold cut in term count, and the
//! dense `7^7` tensor (823,543 f64 = 6.6 MB, rebuilt on every
//! `G2DifferentialGeometry.__init__`) is never allocated at all.
//!
//! ## Bit-exactness with the Python loop
//!
//! Skipped terms are exactly the terms that contributed `x * 0.0`, which cannot
//! perturb a running sum of finite values. The surviving terms are visited in
//! ascending lexicographic `(a,b,c,d)` order -- the same order the full loop
//! reaches them in -- so the accumulation order, and hence the result, is
//! identical to the last bit. [`PERM4`] is what guarantees that ordering, and
//! `four_form_shortcut_matches_the_dense_contraction` asserts it on `to_bits`.

use thiserror::Error;

/// Ambient dimension. Fixed at 7: G2 acts on R^7 and nowhere else, so this is a
/// named constant rather than a parameter.
pub const DIM: usize = 7;

/// Component count of a densely stored 3-form on R^7 (`DIM^3`).
pub const RANK3_LEN: usize = DIM * DIM * DIM;

/// Component count of a densely stored 4-form on R^7 (`DIM^4`).
pub const RANK4_LEN: usize = DIM * DIM * DIM * DIM;

/// Errors surfaced by the Hodge kernels.
///
/// Every one of these is returned, never absorbed: a wrong-shaped or
/// non-finite form must reach the caller as a Python exception, because a
/// silently-zeroed Hodge dual reads downstream as "torsion-free, Ricci-flat"
/// -- a physics result rather than a bug.
#[derive(Debug, Error)]
pub enum HodgeError {
    /// A caller-supplied dense tensor had the wrong flattened length.
    #[error("expected a flattened tensor of {expected} components, got {got}")]
    BadLength {
        /// Number of `f64` components the kernel requires.
        expected: usize,
        /// Number of `f64` components the caller actually supplied.
        got: usize,
    },

    /// The metric volume factor was not a usable positive scalar.
    #[error("sqrt_det_g must be finite and > 0, got {0}")]
    BadDeterminant(f64),

    /// An input component was NaN or infinite.
    #[error("input component {index} is not finite ({value})")]
    NonFiniteInput {
        /// Flattened index of the offending component.
        index: usize,
        /// The offending value.
        value: f64,
    },
}

/// The 24 permutations of `(0,1,2,3)` in ascending lexicographic order.
///
/// The order matters. Applied to a sorted 4-element index set it reproduces
/// exactly the visit order of Python's `itertools.permutations` over that set,
/// and equally the ascending `(a,b,c,d)` order of the dense loop this kernel
/// replaces. That is what makes the shortcut bit-exact rather than merely
/// close.
const PERM4: [[usize; 4]; 24] = [
    [0, 1, 2, 3],
    [0, 1, 3, 2],
    [0, 2, 1, 3],
    [0, 2, 3, 1],
    [0, 3, 1, 2],
    [0, 3, 2, 1],
    [1, 0, 2, 3],
    [1, 0, 3, 2],
    [1, 2, 0, 3],
    [1, 2, 3, 0],
    [1, 3, 0, 2],
    [1, 3, 2, 0],
    [2, 0, 1, 3],
    [2, 0, 3, 1],
    [2, 1, 0, 3],
    [2, 1, 3, 0],
    [2, 3, 0, 1],
    [2, 3, 1, 0],
    [3, 0, 1, 2],
    [3, 0, 2, 1],
    [3, 1, 0, 2],
    [3, 1, 2, 0],
    [3, 2, 0, 1],
    [3, 2, 1, 0],
];

/// The 6 permutations of `(0,1,2)` in ascending lexicographic order. Same
/// ordering contract as [`PERM4`].
const PERM3: [[usize; 3]; 6] = [
    [0, 1, 2],
    [0, 2, 1],
    [1, 0, 2],
    [1, 2, 0],
    [2, 0, 1],
    [2, 1, 0],
];

/// Parity of a permutation, by inversion count: `+1.0` even, `-1.0` odd.
///
/// Callers guarantee the entries are distinct, which is why this is private
/// and why it does not fold the duplicate check in.
fn parity(perm: &[usize]) -> f64 {
    debug_assert!(!perm.is_empty(), "parity of an empty permutation");
    debug_assert!(
        perm.len() <= DIM,
        "parity: length {} exceeds the ambient dimension",
        perm.len()
    );
    let mut sign = 1.0_f64;
    for i in 0..perm.len() {
        for j in (i + 1)..perm.len() {
            if perm[i] > perm[j] {
                sign = -sign;
            }
        }
    }
    sign
}

/// Levi-Civita symbol on `DIM` indices: `+1`, `-1`, or `0` when any repeats.
///
/// This replaces the dense `7^7` array the Python builds on every
/// `G2DifferentialGeometry.__init__`. Evaluating the symbol costs a fixed 21
/// comparisons, so materialising 6.6 MB of it buys nothing.
#[must_use]
pub fn levi_civita_sign(idx: &[usize; DIM]) -> f64 {
    debug_assert!(
        idx.iter().all(|&i| i < DIM),
        "Levi-Civita index outside 0..DIM: {idx:?}"
    );
    let mut seen = 0_u32;
    for &i in idx.iter() {
        let bit = 1_u32 << i;
        if seen & bit != 0 {
            return 0.0;
        }
        seen |= bit;
    }
    let s = parity(idx);
    debug_assert!(s == 1.0 || s == -1.0, "distinct indices must give a unit sign");
    s
}

/// Indices of `0..DIM` absent from `used`, ascending, written into `out`.
///
/// Returns how many were written so the caller asserts the count it expects
/// rather than trusting a slice length it did not compute.
fn complement(used: &[usize], out: &mut [usize; DIM]) -> usize {
    debug_assert!(used.len() <= DIM, "complement: more used indices than DIM");
    debug_assert!(
        used.iter().all(|&i| i < DIM),
        "complement: index outside 0..DIM"
    );
    let mut mask = 0_u32;
    for &u in used {
        mask |= 1_u32 << u;
    }
    let mut n = 0_usize;
    for i in 0..DIM {
        if mask & (1_u32 << i) == 0 {
            out[n] = i;
            n += 1;
        }
    }
    // Fails when the caller passed a repeated index, which would otherwise
    // produce a quietly over-long complement and a wrong contraction.
    debug_assert_eq!(n + used.len(), DIM, "complement: `used` had a repeat");
    n
}

/// Reject a dense form that is the wrong size, non-finite, or paired with an
/// unusable metric volume factor.
///
/// Called first by every kernel below. A NaN that slips in from a mis-derived
/// metric otherwise propagates into the curvature scalars, where it reads as a
/// result rather than as a fault.
fn validate_form(values: &[f64], expected: usize, sqrt_det_g: f64) -> Result<(), HodgeError> {
    debug_assert!(
        expected == RANK3_LEN || expected == RANK4_LEN,
        "kernels accept dense 3- or 4-forms on R^7 only, not {expected} components"
    );
    debug_assert_eq!(
        PERM3.len() * 4,
        PERM4.len(),
        "permutation tables disagree: 3! * 4 must equal 4!"
    );
    if values.len() != expected {
        return Err(HodgeError::BadLength {
            expected,
            got: values.len(),
        });
    }
    if !sqrt_det_g.is_finite() || sqrt_det_g <= 0.0 {
        return Err(HodgeError::BadDeterminant(sqrt_det_g));
    }
    for (index, &value) in values.iter().enumerate() {
        if !value.is_finite() {
            return Err(HodgeError::NonFiniteInput { index, value });
        }
    }
    Ok(())
}

/// Write `val` into all 24 index orderings of `quad`, signed by parity.
fn scatter_antisymmetric(star: &mut [f64], quad: &[usize; 4], val: f64) {
    debug_assert_eq!(star.len(), RANK4_LEN, "scatter target is not a dense 4-form");
    debug_assert!(val.is_finite(), "scattering a non-finite component");
    for p in PERM4.iter() {
        let sign = parity(p);
        let idx = (((quad[p[0]] * DIM + quad[p[1]]) * DIM) + quad[p[2]]) * DIM + quad[p[3]];
        star[idx] = sign * val;
    }
}

/// Hodge dual of a 3-form on R^7:
/// `*phi_{ijkl} = (sqrt|g| / 3!) * phi^{abc} * eps_{abcijkl}`.
///
/// `phi_up` is the index-raised 3-form flattened row-major to [`RANK3_LEN`];
/// the raising itself stays in NumPy, where it is one cheap `einsum`. Returns
/// the fully antisymmetrised 4-form flattened to [`RANK4_LEN`], matching
/// `G2DifferentialGeometry.compute_hodge_star` component for component.
pub fn hodge_star_3form(phi_up: &[f64], sqrt_det_g: f64) -> Result<Vec<f64>, HodgeError> {
    validate_form(phi_up, RANK3_LEN, sqrt_det_g)?;

    let mut star = vec![0.0_f64; RANK4_LEN];
    let mut comp = [0_usize; DIM];

    // Independent components are the ascending 4-index sets; the rest follow by
    // antisymmetry, exactly as the Python does.
    for i in 0..DIM {
        for j in (i + 1)..DIM {
            for k in (j + 1)..DIM {
                for l in (k + 1)..DIM {
                    let quad = [i, j, k, l];
                    let n = complement(&quad, &mut comp);
                    debug_assert_eq!(n, DIM - 4, "a 4-index complement must hold 3 indices");
                    let mut val = 0.0_f64;
                    for p in PERM3.iter() {
                        let (a, b, c) = (comp[p[0]], comp[p[1]], comp[p[2]]);
                        let eps = levi_civita_sign(&[a, b, c, i, j, k, l]);
                        val += phi_up[(a * DIM + b) * DIM + c] * eps;
                    }
                    val *= sqrt_det_g / 6.0;
                    scatter_antisymmetric(&mut star, &quad, val);
                }
            }
        }
    }
    debug_assert!(
        star.iter().all(|v| v.is_finite()),
        "finite input produced a non-finite dual"
    );
    Ok(star)
}

/// Hodge dual of a 4-form on R^7:
/// `*psi_{ijk} = (sqrt|g| / 4!) * psi^{abcd} * eps_{abcdijk}`.
///
/// `star_up` is the index-raised 4-form flattened to [`RANK4_LEN`]; returns the
/// 3-form flattened to [`RANK3_LEN`]. This is the kernel that dominated the
/// profile -- see the module header for why only 24 of each 2401 inner terms
/// can be non-zero.
pub fn hodge_star_4form(star_up: &[f64], sqrt_det_g: f64) -> Result<Vec<f64>, HodgeError> {
    validate_form(star_up, RANK4_LEN, sqrt_det_g)?;

    let mut out = vec![0.0_f64; RANK3_LEN];
    let mut comp = [0_usize; DIM];

    for i in 0..DIM {
        for j in 0..DIM {
            for k in 0..DIM {
                // eps vanishes on any repeated index, so the entire inner sum
                // is zero and the output component stays at 0.0.
                if i == j || j == k || i == k {
                    continue;
                }
                let triple = [i, j, k];
                let n = complement(&triple, &mut comp);
                debug_assert_eq!(n, DIM - 3, "a 3-index complement must hold 4 indices");
                let mut val = 0.0_f64;
                for p in PERM4.iter() {
                    let (a, b, c, d) = (comp[p[0]], comp[p[1]], comp[p[2]], comp[p[3]]);
                    let eps = levi_civita_sign(&[a, b, c, d, i, j, k]);
                    val += star_up[((a * DIM + b) * DIM + c) * DIM + d] * eps;
                }
                out[(i * DIM + j) * DIM + k] = val * sqrt_det_g / 24.0;
            }
        }
    }
    debug_assert!(
        out.iter().all(|v| v.is_finite()),
        "finite input produced a non-finite dual"
    );
    Ok(out)
}

/// Largest absolute componentwise deviation of `**phi` from `phi`.
///
/// Folded into one call so the involution check crosses the FFI boundary once
/// instead of shipping 343 floats back for a subtraction Python would loop.
pub fn hodge_involution_max_error(
    phi: &[f64],
    star_up: &[f64],
    sqrt_det_g: f64,
) -> Result<f64, HodgeError> {
    validate_form(phi, RANK3_LEN, sqrt_det_g)?;
    let round_trip = hodge_star_4form(star_up, sqrt_det_g)?;
    debug_assert_eq!(round_trip.len(), RANK3_LEN, "the round trip changed rank");
    debug_assert_eq!(phi.len(), round_trip.len(), "operands are not comparable");
    let mut max_error = 0.0_f64;
    for (a, b) in round_trip.iter().zip(phi.iter()) {
        let d = (a - b).abs();
        if d > max_error {
            max_error = d;
        }
    }
    Ok(max_error)
}

#[cfg(test)]
mod tests {
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
}
