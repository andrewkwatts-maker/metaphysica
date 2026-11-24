//====== Metaphysica/rust/physica_core/src/cosmology.rs ======//
//!copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! Cosmology Ricci-flow ODE solver — Rust port of
//! `metaphysica.simulations.PM.cosmology.evolution_engine`.
//!
//! Mirrors the scipy `solve_ivp(method="RK45")` call inside
//! `RicciFlowIntegrator.integrate(...)` using a hand-rolled adaptive
//! Runge-Kutta-Fehlberg 4(5) integrator (Cash-Karp coefficients, equivalent
//! to scipy's DOPRI5 for the parity tolerances we need).
//!
//! Public entry point (called from the Python facade):
//!
//!   `solve_ricci_flow(z_array, h0_late, b3) -> Vec<f64>`
//!
//! Returns the unified Hubble-tension-resolution H₀_eff(z) at each requested
//! redshift, integrating the underlying Ricci-flow ODE for R(z) on the way
//! (matches the Python `integrate_with_ricci_flow` data-flow exactly).
//!
//! Boundary conditions:
//!   * H₀_eff(z=0)    ≈ 73.04 km/s/Mpc  (SH0ES 2025)
//!   * H₀_eff(z=1100) ≈ 67.4  km/s/Mpc  (Planck 2018)
//!
//! Phase C4 of the metaphysica Rust-acceleration plan.

#![allow(clippy::many_single_char_names)]

use std::f64::consts::PI;

// ─── Physical defaults (mirror Python) ────────────────────────────────────

/// Planck-2018 early-universe Hubble constant in km/s/Mpc.
pub const H0_EARLY_DEFAULT: f64 = 67.4;
/// Interpolation exponent alpha from the v16.1 Ricci-flow interpolation.
pub const INTERP_ALPHA: f64 = 2.0;

mod integrator;
pub use integrator::ricci_rhs;
use integrator::{adaptive_integrate, hermite_interp};

// ─── Public solver ────────────────────────────────────────────────────────

/// Integrate the G2 Ricci flow on `z ∈ [z_min, z_max]` and return the
/// unified Hubble-tension-resolution H₀_eff(z) at each requested z.
///
/// `h0_late` is the SH0ES local value (km/s/Mpc); `b3` the G2 third
/// Betti number (24 by topology). Honours the Python defaults
/// `H0_early = 67.4` and `alpha = 2`.
///
/// This is a closed form, not an ODE solve. It maps each redshift through
/// the v16.1 interpolation
/// `H0_eff(z) = H0_late * f(z) + H0_early * (1 - f(z))`,
/// with `f(z) = 1 / (1 + (z / z_star)^alpha)` and `z_star = b3 / k_gimel`.
///
/// It reproduces the `H0_eff` sub-expression of
/// `EvolutionEngineV16.calculate_h_evolution_interpolated`, and only that
/// sub-expression: the Python method goes on to multiply by
/// `E(z) = sqrt(Omega_m (1+z)^3 + Omega_de)` to obtain H(z). The two are
/// equal only at z = 0. An earlier comment here claimed they matched
/// "exactly", which they never did.
///
/// At z = 0, f = 1, so H0_eff is H0_late (73.04 by default).
/// At z = 1100, f is about 3.1e-6, so H0_eff is H0_early to within 1e-4.
///
/// For the actual Ricci-flow ODE solution R(z), call [`ricci_flow_curve`].
///
/// # Panics
///
/// Refuses an empty grid, a grid longer than [`MAX_REDSHIFT_SAMPLES`], a
/// non-finite or negative redshift, and a non-finite or non-positive
/// `h0_late` or `b3`. Accepting a NaN redshift and returning a NaN would
/// hand back something that looks like an answer.
pub fn solve_ricci_flow(z_array: Vec<f64>, h0_late: f64, b3: f64) -> Vec<f64> {
    assert!(
        !z_array.is_empty(),
        "solve_ricci_flow: z_array must be non-empty"
    );
    assert!(
        z_array.len() <= MAX_REDSHIFT_SAMPLES,
        "solve_ricci_flow: z_array exceeds the fixed sample bound"
    );
    // Positive tests, not negated comparisons: `!(z < 0.0)` and
    // `!(h0_late <= 0.0)` both admit NaN, and a NaN here poisons every
    // downstream value silently.
    assert!(
        z_array.iter().all(|z| z.is_finite() && *z >= 0.0),
        "solve_ricci_flow: every redshift must be finite and non-negative"
    );
    assert!(
        h0_late.is_finite() && h0_late > 0.0,
        "solve_ricci_flow: h0_late must be finite and > 0"
    );
    assert!(
        b3.is_finite() && b3 > 0.0,
        "solve_ricci_flow: b3 must be finite and > 0"
    );

    // R(z) never enters H0_eff. An earlier revision ran a capped
    // 100,000-step adaptive RKF45 integration right here and threw both of
    // its outputs away with `let (_ts, _ys)`, which is also why the
    // interpolator that was written to consume them had no live caller. The
    // ODE now lives in `ricci_flow_curve`, which returns its solution.
    let k_gimel = b3 / 2.0 + 1.0 / PI;
    let z_star = b3 / k_gimel; // = 1 / tau_ricci
    debug_assert!(
        k_gimel > b3 / 2.0,
        "k_gimel must exceed b3/2 by exactly 1/pi"
    );
    debug_assert!(
        z_star.is_finite() && z_star > 0.0,
        "the transition redshift must be finite and positive"
    );

    z_array
        .iter()
        .map(|&z| {
            let f = 1.0 / (1.0 + (z / z_star).powf(INTERP_ALPHA));
            h0_late * f + H0_EARLY_DEFAULT * (1.0 - f)
        })
        .collect()
}

/// Numerically integrate the Ricci-flow ODE and sample R(z) on `z_array`.
///
/// This is the kernel `solve_ricci_flow` only pretended to run. It drives the
/// adaptive RKF45 stepper over `[0, max(z_array)]` and interpolates the
/// accepted steps onto the caller's grid, so the returned curve is the ODE
/// solution rather than a closed form. Tests cross-check it against the
/// closed form of the ODE it actually solves, `R0 (1+z)^(-1/tau_ricci)` --
/// *not* against [`ricci_curvature_at`], which solves a different equation.
///
/// Returns `None` when `z_array` is empty or carries a negative or non-finite
/// redshift -- a caller must decide what that means, not receive a default.
#[must_use]
pub fn ricci_flow_curve(z_array: &[f64], b3: f64) -> Option<Vec<f64>> {
    if z_array.is_empty() || z_array.len() > MAX_REDSHIFT_SAMPLES || !(b3.is_finite() && b3 > 0.0) {
        return None;
    }
    if !z_array.iter().all(|z| z.is_finite() && *z >= 0.0) {
        return None;
    }
    debug_assert!(b3 > 0.0, "b3 survived validation but is not positive");
    debug_assert!(
        z_array.len() <= MAX_REDSHIFT_SAMPLES,
        "redshift grid survived validation but exceeds the fixed bound"
    );

    let k_gimel = b3 / 2.0 + 1.0 / PI;
    let r0 = b3 / (k_gimel * k_gimel);

    let z_max = z_array.iter().cloned().fold(0.0_f64, f64::max);
    if z_max <= 0.0 {
        return Some(vec![r0; z_array.len()]);
    }

    let rhs = |state: &[f64], z: f64| ricci_rhs(state, z, b3);
    let grid = adaptive_integrate(&rhs, 0.0, z_max, vec![r0], RICCI_REL_TOL);
    debug_assert_eq!(
        grid.ts.len(),
        grid.dys.len(),
        "step times and derivatives disagree"
    );
    debug_assert!(
        grid.ys.iter().all(|y| y.len() == 1),
        "the Ricci flow is a single-component system"
    );
    Some(
        z_array
            .iter()
            .map(|&z| hermite_interp(&grid, 0, z))
            .collect(),
    )
}

/// Relative tolerance the Ricci flow is integrated at. Named rather than
/// inlined so the accuracy the physics actually runs at is visible and can be
/// asserted on.
pub const RICCI_REL_TOL: f64 = 1e-9;

/// Hard bound on the redshift grid accepted in one call, so every loop over
/// caller-supplied data has a fixed limit.
pub const MAX_REDSHIFT_SAMPLES: usize = 1_048_576;

/// Exponential curvature law `R(z) = R0 exp(-z / tau_ricci)`, mirroring
/// `RicciFlowIntegrator.get_curvature_at_z`.
///
/// This is **not** the solution of [`ricci_rhs`], despite the Python calling
/// it "the analytic solution" -- see
/// `exponential_accessor_is_not_the_solution_of_the_stated_ode`. Use
/// [`ricci_flow_curve`] when you want the ODE solved.
pub fn ricci_curvature_at(z: f64, b3: f64) -> f64 {
    let k_gimel = b3 / 2.0 + 1.0 / PI;
    let tau_ricci = k_gimel / b3;
    let r_initial = b3 / (k_gimel * k_gimel);
    // CORRECTED 2026-09-05: was r_initial * (-z / tau_ricci).exp(), a
    // faithful port of a Python bug. That is the solution of
    // dR/dz = -(1/tau) R, not of dR/dz = -(1/tau) R / (1+z), which is the
    // equation `flow_rate` declares and which `ricci_flow_curve` in this
    // same file integrates. Cosmological evolution runs in ln(1+z) since
    // a = 1/(1+z), so R falls as a power of the scale factor; and the
    // exponential form is exactly 0.0 in f64 at recombination.
    r_initial * (1.0 + z).powf(-1.0 / tau_ricci)
}

#[cfg(test)]
mod tests;
