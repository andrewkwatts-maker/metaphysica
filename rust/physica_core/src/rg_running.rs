//====== Metaphysica/rust/physica_core/src/rg_running.rs ======//
//!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! One-loop gauge coupling RG running.
//!
//! Ports the one-loop subset of `simulations/PM/gauge/gauge_unification.py`
//! (`GaugeRGRunner`). The Python kernel implements up to 3-loop running via
//! `scipy.integrate.odeint`; this Rust kernel evaluates the closed-form
//! one-loop solution
//!
//! ```text
//!     1/α_i(μ)  =  1/α_i(μ_0)  −  (b_i / 2π) · ln(μ / μ_0)
//! ```
//!
//! and is the production fast-path used when the higher-loop and threshold
//! corrections are not requested by the caller.
//!
//! Beta coefficients use the Standard Model one-loop values that
//! `GaugeRGRunner.__init__` hard-codes:
//!
//! * `b_1 = 41/10` (GUT-normalised U(1)_Y),
//! * `b_2 = -19/6` (SU(2)_L),
//! * `b_3 = -7`    (SU(3)_c).
//!
//! For the inverse coupling the β-function has the trivial form
//! `d(1/α_i)/dt = -b_i / (2π)` (with `t = ln μ`), and analytic integration
//! over `t ∈ [ln μ₀, ln μ]` reproduces the formula above.

use std::f64::consts::PI;

/// Standard-Model one-loop β-function coefficients in the order
/// `[b_1 (U(1)_Y, GUT-normalised), b_2 (SU(2)_L), b_3 (SU(3)_c)]`.
///
/// These mirror `GaugeRGRunner.b1 / b2 / elder_kads` in the Python kernel.
pub const SM_ONE_LOOP_BETA: [f64; 3] = [41.0 / 10.0, -19.0 / 6.0, -7.0];

/// Evolve the three SM gauge couplings from `mu_initial` to `mu_final`
/// at one-loop, in inverse-coupling form.
///
/// # Arguments
///
/// * `mu_initial` — starting scale (GeV), e.g. `M_Z`.
/// * `mu_final`   — target scale (GeV), e.g. `M_GUT`.
/// * `alpha_init` — `[α_1(μ_initial), α_2(μ_initial), α_3(μ_initial)]` in
///   GUT-normalised convention for α_1.
///
/// # Returns
///
/// `[α_1(μ_final), α_2(μ_final), α_3(μ_final)]`.
///
/// # Panics (debug)
///
/// In debug builds, panics when any scale or coupling is non-positive.
/// In release builds the function simply returns `NaN` entries in those
/// pathological cases (the `1/α` arithmetic propagates naturally).
#[must_use]
pub fn gauge_rg_one_loop(mu_initial: f64, mu_final: f64, alpha_init: [f64; 3]) -> [f64; 3] {
    debug_assert!(mu_initial > 0.0, "mu_initial must be positive");
    debug_assert!(mu_final > 0.0, "mu_final must be positive");
    debug_assert!(
        alpha_init.iter().all(|a| *a > 0.0),
        "all initial couplings must be positive"
    );

    let t = (mu_final / mu_initial).ln();
    let two_pi = 2.0 * PI;

    let mut out = [0.0_f64; 3];
    for i in 0..3 {
        let inv_init = 1.0 / alpha_init[i];
        let inv_final = inv_init - SM_ONE_LOOP_BETA[i] * t / two_pi;
        out[i] = 1.0 / inv_final;
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Closed-form sanity check: identity when `mu_final == mu_initial`.
    #[test]
    fn identity_at_same_scale() {
        let a0 = [1.0 / 59.0, 1.0 / 29.6, 1.0 / 8.5];
        let out = gauge_rg_one_loop(91.2, 91.2, a0);
        for i in 0..3 {
            assert!((out[i] - a0[i]).abs() < 1e-15);
        }
    }

    /// Round-trip: running up then back down recovers the input exactly
    /// (no numerical integration; closed form is reversible).
    #[test]
    fn round_trip_is_exact() {
        let a0 = [1.0 / 59.0, 1.0 / 29.6, 1.0 / 8.5];
        let up = gauge_rg_one_loop(91.2, 2.0e16, a0);
        let down = gauge_rg_one_loop(2.0e16, 91.2, up);
        for i in 0..3 {
            let rel = (down[i] - a0[i]).abs() / a0[i].abs();
            assert!(rel < 1e-12, "round-trip rel error too large: {rel:e}");
        }
    }

    /// Closed-form analytic value: at one-loop,
    ///   1/α_3(μ) = 1/α_3(M_Z) − (b_3 / 2π) · ln(μ/M_Z),
    /// with b_3 = -7, so α_3⁻¹ should *grow* by 7/(2π) per e-fold.
    #[test]
    fn alpha3_growth_matches_closed_form() {
        let mz = 91.2;
        let mu = mz * std::f64::consts::E; // one e-fold up
        let a0 = [1.0 / 59.0, 1.0 / 29.6, 1.0 / 8.5];
        let out = gauge_rg_one_loop(mz, mu, a0);
        let expected_inv = 1.0 / a0[2] - (-7.0) / (2.0 * PI);
        let got_inv = 1.0 / out[2];
        assert!((got_inv - expected_inv).abs() < 1e-12);
    }
}
