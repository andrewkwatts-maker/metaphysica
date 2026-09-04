//====== Metaphysica/rust/physica_core/src/g2_manifold.rs ======//
//!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! G2-manifold primitives used by the spectral-geometry derivations.
//!
//! Ports `simulations/PM/geometry/spectral_geometry.py`.
//!
//! [`G2Manifold`] captures the data shape (Euler characteristic, Betti
//! numbers, racetrack radius) and [`compute_spectral_geometry`] is still a
//! declared stub -- see its doc comment.
//!
//! [`flat_torus_dirac_spectrum`] is real: it is the port of
//! `FlatTorusDirac.analytic_eigenvalues`, which is the one genuinely hot
//! kernel in that Python module. The Python enumerates `Z^d` inside
//! `[-max_mode, max_mode]^d` with a `dim`-deep **recursive generator**
//! (`FlatTorusDirac._mode_vectors`) that allocates a fresh tuple per level,
//! then does a `zip`-genexp sum and a `set` insert per vector. At the
//! defaults used in the codebase that is 7^7 = 823_543 vectors, and
//! `counting_function`'s default `max_mode = 5` is 11^7 = 19_487_171. The
//! port is an iterative odometer with no recursion and no per-vector
//! allocation.

use serde::{Deserialize, Serialize};
use std::f64::consts::PI;

/// Topological & metric invariants of the G2 manifold underlying
/// metaphysica's derivation chain.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct G2Manifold {
    /// Euler characteristic χ.
    pub euler_characteristic: i32,
    /// Betti numbers `[b0, b1, b2, b3]`. `b3` is the seed `SEED_B3 = 24`.
    pub betti_numbers: [i32; 4],
    /// Racetrack radius (dimensionless ratio used downstream).
    pub racetrack_radius: f64,
}

impl G2Manifold {
    /// Default G2 manifold built from the Ten Pillar Seeds.
    #[must_use]
    pub fn from_seeds() -> Self {
        Self {
            euler_characteristic: crate::constants::SEED_CHI_EFF as i32,
            betti_numbers: [1, 0, 0, crate::constants::SEED_B3 as i32],
            racetrack_radius: 0.0,
        }
    }
}

impl Default for G2Manifold {
    fn default() -> Self {
        Self::from_seeds()
    }
}

/// Spectral-geometry result (eigenvalues + derived scalars). Wave-1 stub.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct SpectralGeometry {
    /// First N Laplacian eigenvalues.
    pub laplacian_eigenvalues: Vec<f64>,
    /// Scalar curvature R averaged over the manifold.
    pub mean_scalar_curvature: f64,
}

/// Compute spectral geometry of `manifold`.
///
/// **Still a stub.** It discards its argument and returns an empty record.
/// It is deliberately not exported to Python (see `pyfacade.rs`) so that a
/// pass-through cannot be mistaken for a derivation. The real eigenvalue
/// kernel from the same Python module is [`flat_torus_dirac_spectrum`];
/// wiring it to a [`G2Manifold`] needs the manifold to carry its periods,
/// which it does not, and inventing them here would be worse than the stub.
#[must_use]
pub fn compute_spectral_geometry(manifold: &G2Manifold) -> SpectralGeometry {
    let _ = manifold;
    SpectralGeometry::default()
}

// --- Flat-torus Dirac spectrum ------------------------------------------

/// Hard cap on the number of mode vectors enumerated in one call.
///
/// `(2 * max_mode + 1) ^ dim` grows explosively: d = 7 reaches this at
/// `max_mode = 5` (19_487_171) and blows past it at `max_mode = 6`
/// (28_629_151 -- still admitted) and `max_mode = 7` (170_859_375).
pub const MAX_MODE_VECTORS: u64 = 50_000_000;

/// Largest torus dimension accepted, so `spinor_dim` and the odometer both
/// stay in fixed, checked bounds.
pub const MAX_TORUS_DIM: usize = 16;

/// Two eigenvalues closer than this are the same eigenvalue.
///
/// The Python collapses its eigenvalue set with `round(lam, 12)`; this is the
/// same intent expressed as an absolute separation, which is order-independent
/// and does not depend on decimal formatting.
const EIGENVALUE_MERGE_TOL: f64 = 1e-12;

/// Exact Dirac eigenvalues on the flat torus `T^d = R^d / (L_1 Z x ... x L_d Z)`.
///
/// `lambda = +/- 2 pi sqrt(sum_i (n_i / L_i)^2)` for every integer mode vector
/// `n` in `[-max_mode, max_mode]^d`, deduplicated, then repeated
/// `spinor_dim = 2^(d/2)` times each, ascending. This is the exact contract of
/// `FlatTorusDirac.analytic_eigenvalues`.
///
/// Returns `None` -- never a default or an empty vector -- when `periods` is
/// empty or longer than [`MAX_TORUS_DIM`], when any period is not finite and
/// strictly positive, or when the requested grid exceeds
/// [`MAX_MODE_VECTORS`]. A caller has to decide what an unusable request
/// means; silently handing back an empty spectrum would read as "this torus
/// has no modes".
#[must_use]
pub fn flat_torus_dirac_spectrum(periods: &[f64], max_mode: u32) -> Option<Vec<f64>> {
    let dim = periods.len();
    if dim == 0 || dim > MAX_TORUS_DIM {
        return None;
    }
    if !periods.iter().all(|l| l.is_finite() && *l > 0.0) {
        return None;
    }
    let side = u64::from(max_mode).checked_mul(2)?.checked_add(1)?;
    let total = side.checked_pow(u32::try_from(dim).ok()?)?;
    if total > MAX_MODE_VECTORS {
        return None;
    }
    debug_assert!(total >= 1, "an empty mode grid should have been rejected");
    debug_assert!(
        dim <= MAX_TORUS_DIM,
        "dimension survived validation but exceeds the fixed bound"
    );

    // Distinct lambda^2 values, kept sorted. For positive finite doubles the
    // IEEE-754 bit pattern is monotonic in the value, so ordering and equality
    // on `to_bits()` are exact -- no epsilon, no hashing.
    let mut distinct_sq: Vec<u64> = Vec::new();

    // Odometer over [-max_mode, max_mode]^dim: no recursion, and the trip
    // count is fixed at `total` before the loop starts.
    let mut digits = vec![0_u32; dim];
    let offset = f64::from(max_mode);
    for _ in 0..total {
        let mut lambda_sq = 0.0_f64;
        for (d, &digit) in digits.iter().enumerate() {
            let n = f64::from(digit) - offset;
            let term = 2.0 * PI * n / periods[d];
            lambda_sq += term * term;
        }
        if let Err(pos) = distinct_sq.binary_search(&lambda_sq.to_bits()) {
            distinct_sq.insert(pos, lambda_sq.to_bits());
        }
        // Increment the odometer, last axis fastest.
        for digit in digits.iter_mut().rev() {
            *digit += 1;
            if u64::from(*digit) < side {
                break;
            }
            *digit = 0;
        }
    }
    debug_assert!(
        !distinct_sq.is_empty(),
        "the zero mode is always in the grid"
    );

    // Signed eigenvalues, ascending: -lambda_max .. 0 .. +lambda_max.
    let mut signed: Vec<f64> = Vec::with_capacity(distinct_sq.len() * 2);
    for bits in distinct_sq.iter().rev() {
        let lambda = f64::from_bits(*bits).sqrt();
        if lambda > 0.0 {
            signed.push(-lambda);
        }
    }
    for bits in &distinct_sq {
        let lambda = f64::from_bits(*bits).sqrt();
        signed.push(if lambda > 0.0 { lambda } else { 0.0 });
    }
    debug_assert!(
        signed.windows(2).all(|w| w[0] <= w[1]),
        "the signed spectrum was built out of order"
    );

    // Collapse eigenvalues the Python's `round(lam, 12)` would have merged.
    signed.dedup_by(|a, b| (*a - *b).abs() <= EIGENVALUE_MERGE_TOL);

    let spinor_dim = 1_usize << (dim / 2);
    let mut out = Vec::with_capacity(signed.len() * spinor_dim);
    for lambda in signed {
        for _ in 0..spinor_dim {
            out.push(lambda);
        }
    }
    Some(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn from_seeds_uses_b3_24() {
        let m = G2Manifold::from_seeds();
        assert_eq!(m.betti_numbers[3], 24);
    }

    #[test]
    fn spectral_stub_returns_empty() {
        let m = G2Manifold::from_seeds();
        let s = compute_spectral_geometry(&m);
        assert!(s.laplacian_eigenvalues.is_empty());
    }

    /// On the unit torus lambda^2 = 4 pi^2 k for integer k, so the distinct
    /// eigenvalues are 2 pi sqrt(k). Checked against the closed form rather
    /// than against a recorded fixture.
    #[test]
    fn unit_torus_eigenvalues_are_two_pi_root_k() {
        let periods = [1.0_f64; 3];
        let evals = flat_torus_dirac_spectrum(&periods, 2).expect("valid torus rejected");
        let spinor_dim = 1_usize << (3 / 2); // 2
        assert_eq!(evals.len() % spinor_dim, 0, "multiplicity is not uniform");

        // k ranges over the sums of 3 squares drawn from {0, 1, 4}.
        let mut ks: Vec<i64> = Vec::new();
        for a in [0_i64, 1, 4] {
            for b in [0_i64, 1, 4] {
                for c in [0_i64, 1, 4] {
                    let k = a + b + c;
                    if !ks.contains(&k) {
                        ks.push(k);
                    }
                }
            }
        }
        ks.sort_unstable();
        // Every nonzero k contributes a plus and a minus eigenvalue.
        let expected_distinct = ks.len() * 2 - 1;
        assert_eq!(
            evals.len(),
            expected_distinct * spinor_dim,
            "distinct-eigenvalue count disagrees with the closed form"
        );
        for k in &ks {
            let want = 2.0 * PI * (*k as f64).sqrt();
            assert!(
                evals.iter().any(|e| (e - want).abs() < 1e-9),
                "2 pi sqrt({k}) = {want} missing from the spectrum"
            );
        }
    }

    /// The Dirac spectrum is symmetric under lambda -> -lambda, and the
    /// multiplicity of every eigenvalue is exactly the spinor dimension.
    #[test]
    fn spectrum_is_sign_symmetric_with_spinor_multiplicity() {
        let periods = [1.0, 1.5, 2.0, 1.0, 1.0, 1.0, 1.0];
        let evals = flat_torus_dirac_spectrum(&periods, 1).expect("valid torus rejected");
        let spinor_dim = 1_usize << (7 / 2); // 8
        assert!(
            evals.windows(2).all(|w| w[0] <= w[1]),
            "the spectrum must come back ascending"
        );
        for (i, e) in evals.iter().enumerate() {
            let mirror = evals[evals.len() - 1 - i];
            assert!(
                (e + mirror).abs() < 1e-9,
                "spectrum not symmetric at index {i}: {e} vs {mirror}"
            );
        }
        for chunk in evals.chunks(spinor_dim) {
            assert!(
                chunk.iter().all(|v| (v - chunk[0]).abs() < 1e-12),
                "an eigenvalue does not carry the full spinor multiplicity"
            );
        }
    }

    #[test]
    fn spectrum_refuses_bad_input_rather_than_defaulting() {
        assert!(flat_torus_dirac_spectrum(&[], 3).is_none());
        assert!(flat_torus_dirac_spectrum(&[1.0, 0.0], 3).is_none());
        assert!(flat_torus_dirac_spectrum(&[1.0, -1.0], 3).is_none());
        assert!(flat_torus_dirac_spectrum(&[1.0, f64::NAN], 3).is_none());
        // 15^7 = 170_859_375 blows the mode-vector cap.
        assert!(flat_torus_dirac_spectrum(&[1.0; 7], 7).is_none());
        // 11^7 = 19_487_171 is inside it, but too slow for a debug test run;
        // check the boundary arithmetic instead of running it.
        assert!(11_u64.pow(7) < MAX_MODE_VECTORS);
        assert!(15_u64.pow(7) > MAX_MODE_VECTORS);
    }
}
