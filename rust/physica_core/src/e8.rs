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
//! This is a one-shot precompute, cached in a `OnceLock` so the second call
//! onwards is a pointer return.
//!
//! NOTE ON THE OLD HEADER: this file used to claim the Python `E8RootSystem`
//! reached it "via the `@rust_accelerated(\"py_e8_roots\")` decorator on
//! `_enumerate_roots`". It never did. This module was not declared in
//! `lib.rs`, so `py_e8_roots` was never in the extension, and
//! `rust_accelerated` has no call sites anywhere in the Python package. The
//! module is wired up now; the Python side is not, because the measured cost
//! of `_enumerate_roots` is 1.5 ms once per process and porting it would buy
//! nothing.

use std::sync::OnceLock;

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
            for (k, sign) in signs.iter_mut().enumerate() {
                if (mask >> k) & 1 == 0 {
                    *sign = 1.0;
                } else {
                    *sign = -1.0;
                    neg_count += 1;
                }
            }
            if neg_count % 2 == 0 {
                let mut v = [0.0_f64; 8];
                for (slot, sign) in v.iter_mut().zip(signs.iter()) {
                    *slot = 0.5 * sign;
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

// The `py_e8_roots` binding lives in `pyfacade`, with the rest of the
// Python surface, so there is one place to look for what the wheel exports.

// --- E8 lattice-point enumeration inside a ball -------------------------
//
// Ports `simulations/PM/geometry/sphere_packing.py::SpherePacking`:
// `enumerate_lattice_points` and `density_convergence`.
//
// WHY THIS ONE. The Python builds the candidate set with
// `np.meshgrid(*([arange(-bound, bound+1)] * 8), indexing="ij")`. For any
// radius that pushes `bound` to its cap of 3 that is 7^8 = 5_764_801 rows of
// 8 float64s: 369 MB for `all_vecs`, another 369 MB for the eight meshgrid
// grids, and another 369 MB for `half_vecs` -- about 1.1 GB of transient
// allocation per call. `density_convergence` calls it once per radius step,
// twenty times by default. The port is an odometer that allocates only the
// survivors.

/// Per-coordinate search bound cap, `bound = min(ceil(radius) + 1, 3)` in the
/// Python original. Reproduced deliberately -- see [`E8_COMPLETE_RADIUS`].
pub const LATTICE_COORD_CAP: i32 = 3;

/// Largest radius for which the [`LATTICE_COORD_CAP`] enumeration is complete.
///
/// An integer lattice point in the ball needs `|n_i| <= radius`; a
/// half-integer one needs `|n_i| <= radius + 1/2`. With the coordinate bound
/// pinned at 3, both hold only up to `radius = 2.5`. Past that the Python --
/// and therefore this port, which matches it for parity -- silently drops
/// points, so `density_convergence(max_radius = 5.0)` reports a falling
/// density that is an artefact of the truncation, not of the lattice.
/// [`e8_lattice_points_are_complete`] returns that fact to the caller instead
/// of leaving it implicit.
pub const E8_COMPLETE_RADIUS: f64 = 2.5;

/// Slack the Python allows on the squared-norm test, `norms_sq <= r_sq + 1e-10`.
const NORM_SQ_TOL: f64 = 1e-10;

/// Upper bound on radius-convergence steps evaluated in one call.
pub const MAX_DENSITY_STEPS: usize = 4_096;

/// Whether [`e8_lattice_points`] enumerates every lattice point in the ball,
/// or is truncated by the inherited coordinate cap.
#[must_use]
pub fn e8_lattice_points_are_complete(radius: f64) -> bool {
    radius.is_finite() && radius <= E8_COMPLETE_RADIUS
}

/// Every E8 lattice point with squared norm at most `radius^2`.
///
/// E8 = D8 union (D8 + s): all integer vectors with even coordinate sum,
/// plus all half-integer vectors `n + (1/2, ..., 1/2)` whose underlying
/// integer vector also has even coordinate sum.
///
/// Order matches the Python exactly -- every integer point first, then every
/// half-integer point, each family in odometer order with the last coordinate
/// varying fastest -- so the two can be compared elementwise, not just as
/// sets.
///
/// Returns `None` for a negative or non-finite radius rather than an empty
/// vector, which would be indistinguishable from "no points in the ball".
#[must_use]
pub fn e8_lattice_points(radius: f64) -> Option<Vec<[f64; 8]>> {
    if !(radius.is_finite() && radius >= 0.0) {
        return None;
    }
    // Saturating cast: a huge radius clamps to the cap, which is what the
    // Python's `min(..., 3)` does too.
    let bound = (radius.ceil() as i64 + 1).min(i64::from(LATTICE_COORD_CAP)) as i32;
    debug_assert!(
        bound >= 1,
        "the bound must admit at least the origin's neighbours"
    );
    debug_assert!(
        bound <= LATTICE_COORD_CAP,
        "the coordinate bound escaped its cap"
    );

    let r_sq = radius * radius + NORM_SQ_TOL;
    let side = (2 * bound + 1) as usize;
    let total = side.checked_pow(8)?;

    let mut integer_points: Vec<[f64; 8]> = Vec::new();
    let mut half_points: Vec<[f64; 8]> = Vec::new();

    // Odometer over [-bound, bound]^8; fixed trip count, no recursion.
    let mut digits = [0_usize; 8];
    for _ in 0..total {
        let mut coord_sum = 0_i32;
        let mut norm_sq = 0.0_f64;
        let mut half_norm_sq = 0.0_f64;
        let mut v = [0.0_f64; 8];
        for k in 0..8 {
            let n = digits[k] as i32 - bound;
            coord_sum += n;
            let x = f64::from(n);
            v[k] = x;
            norm_sq += x * x;
            let xh = x + 0.5;
            half_norm_sq += xh * xh;
        }
        // Sum(n_i + 1/2) = Sum(n_i) + 4, so both cosets test the same parity.
        if coord_sum % 2 == 0 {
            if norm_sq <= r_sq {
                integer_points.push(v);
            }
            if half_norm_sq <= r_sq {
                let mut h = v;
                for c in &mut h {
                    *c += 0.5;
                }
                half_points.push(h);
            }
        }
        for digit in digits.iter_mut().rev() {
            *digit += 1;
            if *digit < side {
                break;
            }
            *digit = 0;
        }
    }

    integer_points.extend_from_slice(&half_points);
    Some(integer_points)
}

/// Packing-density convergence: `(radius, density, point_count)` per step.
///
/// `density = n_points * V8(r_pack) / V8(radius)` with
/// `V8(r) = pi^4 r^8 / 24` and `r_pack = sqrt(2)/2 * lattice_constant`, which
/// is what `SpherePacking.density_convergence` computes.
///
/// Returns `None` on a non-finite or non-positive `max_radius` or
/// `lattice_constant`, on `num_steps` of zero, or on more than
/// [`MAX_DENSITY_STEPS`] steps.
#[must_use]
pub fn e8_density_convergence(
    max_radius: f64,
    num_steps: usize,
    lattice_constant: f64,
) -> Option<Vec<(f64, f64, usize)>> {
    if !(max_radius.is_finite() && max_radius > 0.0) {
        return None;
    }
    if !(lattice_constant.is_finite() && lattice_constant > 0.0) {
        return None;
    }
    if num_steps == 0 || num_steps > MAX_DENSITY_STEPS {
        return None;
    }
    debug_assert!(num_steps <= MAX_DENSITY_STEPS, "step count escaped its cap");
    debug_assert!(max_radius > 0.0, "a zero radius encloses no ball");

    let r_pack = std::f64::consts::SQRT_2 / 2.0 * lattice_constant;
    let v_sphere = sphere_volume_8d(r_pack);

    let mut out = Vec::with_capacity(num_steps);
    for step in 1..=num_steps {
        let r = max_radius * step as f64 / num_steps as f64;
        let points = e8_lattice_points(r)?;
        let n = points.len();
        let v_ball = sphere_volume_8d(r);
        // v_ball is positive for every r the guards above admit, but a caller
        // reading this needs to see that the zero case is handled, not
        // assumed away.
        let density = if v_ball > 0.0 {
            n as f64 * v_sphere / v_ball
        } else {
            0.0
        };
        out.push((r, density, n));
    }
    Some(out)
}

/// Volume of the 8-ball of radius `r`: `pi^4 r^8 / 24`.
#[must_use]
pub fn sphere_volume_8d(r: f64) -> f64 {
    debug_assert!(r.is_finite(), "an 8-ball radius must be finite");
    debug_assert!(r >= 0.0, "an 8-ball radius cannot be negative");
    let r4 = r * r * r * r;
    std::f64::consts::PI.powi(4) * r4 * r4 / 24.0
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
                "root {r:?} has norm² = {norm_sq}, expected 2"
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
                panic!("root {r:?} is neither Type I nor Type II");
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
                assert_eq!(neg % 2, 0, "Type II root {r:?} has odd minus-sign count");
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
            for component in neg.iter_mut() {
                *component = -*component;
            }
            assert!(set.contains(&to_key(&neg)), "negation of {r:?} missing");
        }
    }

    /// Cache returns identical pointers on repeated calls.
    #[test]
    fn cache_is_stable() {
        let a = enumerate_e8_roots() as *const _;
        let b = enumerate_e8_roots() as *const _;
        assert_eq!(a, b, "OnceLock should hand back the same allocation");
    }

    /// The E8 theta series is known: 1 point at norm^2 = 0, 240 at 2, 2160 at
    /// 4. Any ball radius in [2, 2.5] must therefore hold exactly 2401 points.
    /// This is a check against the mathematics, not against the Python.
    #[test]
    fn lattice_ball_reproduces_the_e8_theta_series() {
        let origin_only = e8_lattice_points(0.5).expect("valid radius rejected");
        assert_eq!(origin_only.len(), 1, "only the origin has norm^2 <= 0.25");

        let first_shell = e8_lattice_points(std::f64::consts::SQRT_2).expect("valid radius");
        assert_eq!(first_shell.len(), 241, "1 + 240 through the first shell");

        let second_shell = e8_lattice_points(2.0).expect("valid radius");
        assert_eq!(
            second_shell.len(),
            2401,
            "1 + 240 + 2160 through norm^2 = 4"
        );

        // Every point really is in E8: even coordinate sum in both cosets.
        for v in &second_shell {
            let doubled: f64 = v.iter().map(|x| x * 2.0).sum();
            assert!(
                (doubled / 2.0).fract().abs() < 1e-12,
                "point {v:?} has a non-integral coordinate sum"
            );
        }
    }

    /// Norm^2 of every enumerated point is an even integer -- E8 is an even
    /// unimodular lattice, so this is a structural check the Python never made.
    #[test]
    fn every_lattice_point_has_even_squared_norm() {
        let points = e8_lattice_points(2.0).expect("valid radius rejected");
        for v in &points {
            let n_sq: f64 = v.iter().map(|x| x * x).sum();
            let rounded = n_sq.round();
            assert!(
                (n_sq - rounded).abs() < 1e-9,
                "norm^2 {n_sq} is not integral"
            );
            assert_eq!(
                (rounded as i64) % 2,
                0,
                "norm^2 {n_sq} is odd; E8 is an even lattice"
            );
        }
    }

    /// The inherited coordinate cap truncates past radius 2.5. Pinning the
    /// boundary means a future change to `LATTICE_COORD_CAP` cannot quietly
    /// move it.
    #[test]
    fn the_coordinate_cap_truncates_above_two_and_a_half() {
        assert!(e8_lattice_points_are_complete(2.5));
        assert!(!e8_lattice_points_are_complete(2.6));
        assert!(!e8_lattice_points_are_complete(5.0));
        assert!(!e8_lattice_points_are_complete(f64::INFINITY));

        // At radius 4 the true count is far larger than what the cap admits:
        // (4,0,0,0,0,0,0,0) has norm^2 = 16 <= 16 but coordinate 4 > 3.
        let truncated = e8_lattice_points(4.0).expect("valid radius rejected");
        assert!(
            !truncated.iter().any(|v| v.iter().any(|x| x.abs() > 3.5)),
            "a point outside the coordinate cap slipped through"
        );
    }

    #[test]
    fn lattice_enumeration_refuses_bad_input_rather_than_defaulting() {
        assert!(e8_lattice_points(-1.0).is_none());
        assert!(e8_lattice_points(f64::NAN).is_none());
        assert!(e8_density_convergence(0.0, 4, 1.0).is_none());
        assert!(e8_density_convergence(1.0, 0, 1.0).is_none());
        assert!(e8_density_convergence(1.0, 4, f64::NAN).is_none());
        assert!(e8_density_convergence(f64::NAN, 4, 1.0).is_none());
        assert!(e8_density_convergence(1.0, MAX_DENSITY_STEPS + 1, 1.0).is_none());
    }

    #[test]
    fn density_convergence_reports_one_row_per_step_with_rising_radius() {
        let rows = e8_density_convergence(2.5, 5, 1.0).expect("valid request rejected");
        assert_eq!(rows.len(), 5);
        for w in rows.windows(2) {
            assert!(w[0].0 < w[1].0, "radii must ascend");
            assert!(w[0].2 <= w[1].2, "point counts must not fall as r grows");
        }
        assert!(rows.iter().all(|r| r.1.is_finite() && r.1 >= 0.0));
    }
}
