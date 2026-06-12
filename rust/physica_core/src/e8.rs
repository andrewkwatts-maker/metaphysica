//====== Metaphysica/rust/physica_core/src/e8.rs ======//
//!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! E8 root system enumeration.
//!
//! Ports `simulations/PM/algebra/e8_root_system.py::_enumerate_roots`. The
//! standard E8 root set in R^8 is the disjoint union of:
//!
//!   * **Type I** — 112 integer roots: all permutations of
//!     (±1, ±1, 0, 0, 0, 0, 0, 0). Choose 2 of the 8 coordinates (C(8,2) = 28)
//!     and assign each chosen coordinate an independent ± sign (4 sign
//!     choices) → 28 × 4 = 112.
//!   * **Type II** — 128 half-integer roots: (±½)⁸ with an even number of
//!     minus signs (256 total sign patterns, exactly half — 128 — have an
//!     even minus-sign count).
//!
//! Total: 240 roots, each with squared length 2.
//!
//! This is a one-shot precompute, cached in a `OnceLock` so the second-onwards
//! call is a pointer return. Used by the Python `E8RootSystem` class at init
//! time via the `@rust_accelerated("py_e8_roots")` decorator on
//! `_enumerate_roots`.

use std::sync::OnceLock;

#[cfg(feature = "python")]
use pyo3::prelude::*;

/// Cached 240-root enumeration. Populated on first call to [`enumerate_e8_roots`].
static ROOTS: OnceLock<Vec<[f64; 8]>> = OnceLock::new();

/// Build the full E8 root system in R^8.
///
/// Returns a reference to the cached `Vec<[f64; 8]>` of length 240. Every root
/// is verified (debug-only) to have squared length exactly 2.
///
/// # Determinism
///
/// The enumeration order is:
/// 1. Type I: nested loop over `(i, j)` pairs with `i < j`, inner over
///    `(sign_i, sign_j) ∈ {+1, -1}²` (with `+1` before `-1`).
/// 2. Type II: ascending `mask ∈ 0..256`, where bit `k = 0` means `+½` at
///    coordinate `k` and bit `k = 1` means `-½`; only even-parity masks pass.
///
/// Callers should not rely on ordering; the Python parity test sorts both
/// sides as a set.
#[must_use]
pub fn enumerate_e8_roots() -> &'static Vec<[f64; 8]> {
    ROOTS.get_or_init(|| {
        let mut roots: Vec<[f64; 8]> = Vec::with_capacity(240);

        // Type I: 112 integer roots — all permutations of (±1, ±1, 0⁶).
        for i in 0..8 {
            for j in (i + 1)..8 {
                for &si in &[1.0_f64, -1.0_f64] {
                    for &sj in &[1.0_f64, -1.0_f64] {
                        let mut v = [0.0_f64; 8];
                        v[i] = si;
                        v[j] = sj;
                        debug_assert!(
                            (v.iter().map(|x| x * x).sum::<f64>() - 2.0).abs() < 1e-15,
                            "Type I root failed length²=2 check"
                        );
                        roots.push(v);
                    }
                }
            }
        }

        // Type II: 128 half-integer roots — (±½)⁸ with an even number of minuses.
        for mask in 0..256_u32 {
            // bit k == 0 → +1, bit k == 1 → -1
            let mut signs = [0.0_f64; 8];
            let mut neg_count = 0_u32;
            for k in 0..8 {
                if (mask >> k) & 1 == 0 {
                    signs[k] = 1.0;
                } else {
                    signs[k] = -1.0;
                    neg_count += 1;
                }
            }
            if neg_count % 2 == 0 {
                let mut v = [0.0_f64; 8];
                for k in 0..8 {
                    v[k] = 0.5 * signs[k];
                }
                debug_assert!(
                    (v.iter().map(|x| x * x).sum::<f64>() - 2.0).abs() < 1e-15,
                    "Type II root failed length²=2 check"
                );
                roots.push(v);
            }
        }

        debug_assert_eq!(roots.len(), 240, "E8 root count must be 240");
        roots
    })
}

/// PyO3 binding: returns the 240 E8 roots as `list[list[float]]`.
///
/// `[f64; 8]` does not have a direct PyO3 `IntoPy` impl, so each root is
/// converted to `Vec<f64>` on the way out. The conversion runs once per
/// Python-level call; the underlying enumeration is cached, so subsequent
/// calls only re-copy the array, not re-enumerate.
#[cfg(feature = "python")]
#[pyfunction]
pub fn py_e8_roots() -> Vec<Vec<f64>> {
    enumerate_e8_roots()
        .iter()
        .map(|r| r.to_vec())
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    /// E8 has exactly 240 roots — non-negotiable algebraic invariant.
    #[test]
    fn root_count_is_240() {
        let roots = enumerate_e8_roots();
        assert_eq!(roots.len(), 240);
    }

    /// Every root has squared length exactly 2 (the E8 lattice minimal vector
    /// norm).
    #[test]
    fn all_roots_norm_squared_two() {
        let roots = enumerate_e8_roots();
        for r in roots {
            let norm_sq: f64 = r.iter().map(|x| x * x).sum();
            assert!(
                (norm_sq - 2.0).abs() < 1e-12,
                "root {:?} has norm² = {}, expected 2",
                r,
                norm_sq
            );
        }
    }

    /// 112 Type-I integer roots, 128 Type-II half-integer roots.
    #[test]
    fn root_type_partition() {
        let roots = enumerate_e8_roots();
        let mut integer_count = 0;
        let mut half_int_count = 0;
        for r in roots {
            // Type I: all coords are -1, 0, or +1 → all coords squared in {0, 1}.
            // Type II: all coords are ±½ → all coords squared = 0.25.
            let all_integer = r.iter().all(|&x| x == 0.0 || x.abs() == 1.0);
            let all_half = r.iter().all(|&x| x.abs() == 0.5);
            if all_integer {
                integer_count += 1;
            } else if all_half {
                half_int_count += 1;
            } else {
                panic!("root {:?} is neither Type I nor Type II", r);
            }
        }
        assert_eq!(integer_count, 112, "Type I count");
        assert_eq!(half_int_count, 128, "Type II count");
    }

    /// Type II roots must have an even number of minus signs.
    #[test]
    fn type_ii_even_minus_signs() {
        let roots = enumerate_e8_roots();
        for r in roots {
            let all_half = r.iter().all(|&x| x.abs() == 0.5);
            if all_half {
                let neg = r.iter().filter(|&&x| x < 0.0).count();
                assert_eq!(neg % 2, 0, "Type II root {:?} has odd minus-sign count", r);
            }
        }
    }

    /// Root set is closed under negation (E8 is a root system).
    #[test]
    fn closed_under_negation() {
        let roots = enumerate_e8_roots();
        let to_key = |r: &[f64; 8]| -> [i64; 8] {
            // Multiply by 2 so ±½ → ±1 and ±1 → ±2; rounded to integer for
            // hash equality.
            let mut out = [0_i64; 8];
            for k in 0..8 {
                out[k] = (r[k] * 2.0).round() as i64;
            }
            out
        };
        let mut set = std::collections::HashSet::new();
        for r in roots {
            set.insert(to_key(r));
        }
        for r in roots {
            let mut neg = *r;
            for k in 0..8 {
                neg[k] = -neg[k];
            }
            assert!(set.contains(&to_key(&neg)), "negation of {:?} missing", r);
        }
    }

    /// Cache returns identical pointers on repeated calls.
    #[test]
    fn cache_is_stable() {
        let a = enumerate_e8_roots() as *const _;
        let b = enumerate_e8_roots() as *const _;
        assert_eq!(a, b, "OnceLock should hand back the same allocation");
    }
}
