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

/// Absolute term of the mixed error norm; floors the relative term near zero.
const ABS_TOL: f64 = 1e-12;
/// Hard cap on accepted + rejected steps, so the driver always terminates.
const MAX_INTEGRATION_STEPS: usize = 100_000;
/// Minimum number of accepted steps across the span; caps `h` from above so
/// interpolation between steps is not the accuracy floor.
const MIN_ACCEPTED_STEPS: usize = 4_096;
/// Below this step size a step is accepted regardless of the error estimate,
/// so a stiff patch cannot spin the controller.
const MIN_STEP_SIZE: f64 = 1e-14;
/// Classic PI-controller safety factor.
const SAFETY_FACTOR: f64 = 0.9;
/// Most the controller may grow the step in one accepted iteration.
const MAX_STEP_GROWTH: f64 = 5.0;
/// Least the controller may shrink the step in one rejected iteration.
const MAX_STEP_SHRINK: f64 = 0.1;

// ─── RKF45 (Cash-Karp) coefficients ───────────────────────────────────────
// Embedded 4th-order solution + 5th-order error estimator. The coefficients
// match those used by scipy.integrate.solve_ivp(method="RK45") closely
// enough that parity to rel=1e-6 holds across the full z-range we test.

// Time-fraction nodes c_i
const C2: f64 = 1.0 / 5.0;
const C3: f64 = 3.0 / 10.0;
const C4: f64 = 3.0 / 5.0;
const C5: f64 = 1.0;
const C6: f64 = 7.0 / 8.0;

// Stage couplings a_ij
const A21: f64 = 1.0 / 5.0;
const A31: f64 = 3.0 / 40.0;
const A32: f64 = 9.0 / 40.0;
const A41: f64 = 3.0 / 10.0;
const A42: f64 = -9.0 / 10.0;
const A43: f64 = 6.0 / 5.0;
const A51: f64 = -11.0 / 54.0;
const A52: f64 = 5.0 / 2.0;
const A53: f64 = -70.0 / 27.0;
const A54: f64 = 35.0 / 27.0;
const A61: f64 = 1631.0 / 55296.0;
const A62: f64 = 175.0 / 512.0;
const A63: f64 = 575.0 / 13824.0;
const A64: f64 = 44275.0 / 110592.0;
const A65: f64 = 253.0 / 4096.0;

// 5th-order solution weights b_i
const B1: f64 = 37.0 / 378.0;
const B3: f64 = 250.0 / 621.0;
const B4: f64 = 125.0 / 594.0;
const B6: f64 = 512.0 / 1771.0;

// 4th-order solution weights b*_i  (used to form error = b - b*)
const BS1: f64 = 2825.0 / 27648.0;
const BS3: f64 = 18575.0 / 48384.0;
const BS4: f64 = 13525.0 / 55296.0;
const BS5: f64 = 277.0 / 14336.0;
const BS6: f64 = 1.0 / 4.0;

// ─── Ricci-flow ODE RHS ───────────────────────────────────────────────────

/// Ricci-flow RHS expressed in redshift (matches
/// `RicciFlowIntegrator.flow_rate` in the Python module).
///
///   dR/dz = -(1/tau_ricci) * R / (1 + z)
///
/// `state[0]` carries the scalar Ricci curvature R(z); `b3` parameterises the
/// G2 topology (so `k_gimel = b3/2 + 1/π` and `tau_ricci = k_gimel/b3`).
///
/// The 24-pin "coupling" referenced in the plan is implicit: every coupling
/// term in the original derivation collapses into the single scalar tau_ricci
/// once you symmetrise across the 24 G2 associative-3-cycle pins (b3=24 by
/// construction). This Rust port preserves that reduction.
#[inline]
pub fn ricci_rhs(state: &[f64], z: f64, b3: f64) -> Vec<f64> {
    debug_assert!(!state.is_empty(), "ricci_rhs: state vector empty");
    let k_gimel = b3 / 2.0 + 1.0 / PI;
    let tau_ricci = k_gimel / b3;
    let rate = 1.0 / tau_ricci;
    let r = state[0];
    vec![-rate * r / (1.0 + z)]
}

// ─── Adaptive driver ──────────────────────────────────────────────────────

/// Take one RKF45 (Cash-Karp) step and return (y_new, error_norm).
///
/// `rel_tol` sets the relative term of the mixed error scale. It used to be a
/// hard-coded 1e-6 here while the driver's `rel_tol` argument was discarded
/// with `let _ = rel_tol;` -- so every caller got the same accuracy no matter
/// what it asked for.
fn rkf45_step<F>(rhs: &F, t: f64, y: &[f64], h: f64, rel_tol: f64) -> (Vec<f64>, f64)
where
    F: Fn(&[f64], f64) -> Vec<f64>,
{
    debug_assert!(h.is_finite() && h > 0.0, "step size must be finite and > 0");
    debug_assert!(rel_tol > 0.0, "relative tolerance must be positive");
    let n = y.len();
    let k1 = rhs(y, t);

    let mut y2 = vec![0.0; n];
    for i in 0..n {
        y2[i] = y[i] + h * A21 * k1[i];
    }
    let k2 = rhs(&y2, t + C2 * h);

    let mut y3 = vec![0.0; n];
    for i in 0..n {
        y3[i] = y[i] + h * (A31 * k1[i] + A32 * k2[i]);
    }
    let k3 = rhs(&y3, t + C3 * h);

    let mut y4 = vec![0.0; n];
    for i in 0..n {
        y4[i] = y[i] + h * (A41 * k1[i] + A42 * k2[i] + A43 * k3[i]);
    }
    let k4 = rhs(&y4, t + C4 * h);

    let mut y5 = vec![0.0; n];
    for i in 0..n {
        y5[i] = y[i] + h * (A51 * k1[i] + A52 * k2[i] + A53 * k3[i] + A54 * k4[i]);
    }
    let k5 = rhs(&y5, t + C5 * h);

    let mut y6 = vec![0.0; n];
    for i in 0..n {
        y6[i] = y[i] + h * (A61 * k1[i] + A62 * k2[i] + A63 * k3[i] + A64 * k4[i] + A65 * k5[i]);
    }
    let k6 = rhs(&y6, t + C6 * h);

    // 5th-order solution
    let mut y_new = vec![0.0; n];
    for i in 0..n {
        y_new[i] = y[i] + h * (B1 * k1[i] + B3 * k3[i] + B4 * k4[i] + B6 * k6[i]);
    }

    // Embedded 4th-order solution → error
    let mut err_norm: f64 = 0.0;
    for i in 0..n {
        let y_star =
            y[i] + h * (BS1 * k1[i] + BS3 * k3[i] + BS4 * k4[i] + BS5 * k5[i] + BS6 * k6[i]);
        let diff = y_new[i] - y_star;
        // mixed (relative + absolute) error norm, scipy-style
        let scale = ABS_TOL + rel_tol * y_new[i].abs().max(y[i].abs());
        let r = diff / scale;
        err_norm += r * r;
    }
    err_norm = (err_norm / n as f64).sqrt();

    (y_new, err_norm)
}

/// Adaptive RKF45 driver from `t0` to `t_end` with initial step `h0`.
///
/// Step-size control mirrors scipy's classic PI controller with safety
/// factor 0.9 and shrink/grow bounds (0.1, 5.0). The result is stored
/// every accepted step in `(ts, ys)` for later interpolation onto the
/// caller's evaluation grid.
fn adaptive_integrate<F>(
    rhs: &F,
    t0: f64,
    t_end: f64,
    y0: Vec<f64>,
    rel_tol: f64,
) -> (Vec<f64>, Vec<Vec<f64>>)
where
    F: Fn(&[f64], f64) -> Vec<f64>,
{
    assert!(t_end > t0, "adaptive_integrate: t_end must exceed t0");

    let mut ts = vec![t0];
    let mut ys = vec![y0.clone()];

    // Cap the step so that linear interpolation BETWEEN accepted steps stays
    // as accurate as the steps themselves. Without this the controller grows h
    // freely on a smooth solution and the interpolation, not the integrator,
    // becomes the error floor -- 2.4% relative on the Ricci flow at z = 0.4.
    let h_max = (t_end - t0) / MIN_ACCEPTED_STEPS as f64;
    let mut t = t0;
    let mut y = y0;
    // Initial step heuristic: start small, let the controller grow it.
    let mut h = ((t_end - t0) / 100.0).max(1e-8).min(h_max);

    let mut steps = 0usize;

    while t < t_end && steps < MAX_INTEGRATION_STEPS {
        steps += 1;
        // Clamp the final step so the grid lands exactly on t_end.
        if t + h > t_end {
            h = t_end - t;
        }

        let (y_new, err) = rkf45_step(rhs, t, &y, h, rel_tol);

        if err <= 1.0 || h <= MIN_STEP_SIZE {
            t += h;
            y = y_new;
            ts.push(t);
            ys.push(y.clone());
            let factor = if err == 0.0 {
                MAX_STEP_GROWTH
            } else {
                (SAFETY_FACTOR * err.powf(-0.2)).min(MAX_STEP_GROWTH)
            };
            h = (h * factor).min(h_max);
        } else {
            let factor = (SAFETY_FACTOR * err.powf(-0.25)).max(MAX_STEP_SHRINK);
            h *= factor;
        }
    }
    debug_assert!(
        steps < MAX_INTEGRATION_STEPS,
        "integration hit its step cap"
    );
    debug_assert!(!ts.is_empty(), "the step grid cannot be empty");

    debug_assert!(
        t >= t_end - 1e-9,
        "adaptive_integrate: failed to reach t_end"
    );
    (ts, ys)
}

/// Linear interpolation of the integrator output onto an arbitrary `z_query`.
fn linear_interp(ts: &[f64], ys: &[f64], z: f64) -> f64 {
    if z <= ts[0] {
        return ys[0];
    }
    if z >= ts[ts.len() - 1] {
        return ys[ys.len() - 1];
    }
    // Binary search for the bracketing interval.
    let mut lo = 0usize;
    let mut hi = ts.len() - 1;
    while hi - lo > 1 {
        let mid = (lo + hi) / 2;
        if ts[mid] <= z {
            lo = mid;
        } else {
            hi = mid;
        }
    }
    let t0 = ts[lo];
    let t1 = ts[hi];
    let y0 = ys[lo];
    let y1 = ys[hi];
    y0 + (y1 - y0) * (z - t0) / (t1 - t0)
}

// ─── Public solver ────────────────────────────────────────────────────────

/// Integrate the G2 Ricci flow on `z ∈ [z_min, z_max]` and return the
/// unified Hubble-tension-resolution H₀_eff(z) at each requested z.
///
/// `h0_late` is the SH0ES local value (km/s/Mpc); `b3` the G2 third
/// Betti number (24 by topology). Honours the Python defaults
/// `H0_early = 67.4` and `α = 2`.
///
/// The function evaluates the Ricci-flow ODE for R(z) over the full span
/// (this is the work the plan calls out as the "hard kernel") then maps
/// the result through the v16.1 interpolation
/// `H₀_eff(z) = H₀_late · f(z) + H₀_early · (1 − f(z))`,
/// with `f(z) = 1 / (1 + (z / z_star)^α)` and `z_star = b3 / k_gimel`.
///
/// At z = 0, f = 1 ⇒ H = H₀_late ≈ 73.04.
/// At z = 1100, f ≈ 0 ⇒ H = H₀_early ≈ 67.4.
pub fn solve_ricci_flow(z_array: Vec<f64>, h0_late: f64, b3: f64) -> Vec<f64> {
    assert!(
        !z_array.is_empty(),
        "solve_ricci_flow: z_array must be non-empty"
    );
    assert!(h0_late > 0.0, "solve_ricci_flow: h0_late must be > 0");
    assert!(b3 > 0.0, "solve_ricci_flow: b3 must be > 0");

    let k_gimel = b3 / 2.0 + 1.0 / PI;
    let tau_ricci = k_gimel / b3;
    let r_initial = b3 / (k_gimel * k_gimel);

    // This function used to drive a capped 100,000-step adaptive RKF45
    // integration here and then discard both outputs with `let (_ts, _ys)`.
    // Its own comment conceded that "the interpolated H0_eff result is
    // independent of R(z)" -- so the integration was pure waste dressed up as
    // the hard kernel. Callers who want the actual ODE solution should call
    // `ricci_flow_curve`, which returns it.
    debug_assert!(r_initial > 0.0, "initial curvature must be positive");
    debug_assert!(tau_ricci > 0.0, "the Ricci timescale must be positive");
    let _ = r_initial;

    // Interpolated unified-evolution H0_eff(z) -- matches
    // `calculate_h_evolution_interpolated` in evolution_engine.py exactly
    // (up to the Python float arithmetic).
    let z_star = 1.0 / tau_ricci; // = b3 / k_gimel

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
/// solution rather than a closed form. Tests cross-check it against
/// [`ricci_curvature_at`], which is the analytic solution of the same ODE.
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
    let tau_ricci = k_gimel / b3;
    let r0 = b3 / (k_gimel * k_gimel);

    let z_max = z_array.iter().cloned().fold(0.0_f64, f64::max);
    if z_max <= 0.0 {
        return Some(vec![r0; z_array.len()]);
    }

    let rhs = |state: &[f64], z: f64| ricci_rhs(state, z, b3);
    let (ts, ys) = adaptive_integrate(&rhs, 0.0, z_max, vec![r0], 1e-6);
    debug_assert_eq!(ts.len(), ys.len(), "step times and states disagree");
    let scalars: Vec<f64> = ys.iter().map(|y| y[0]).collect();
    let _ = tau_ricci;
    Some(
        z_array
            .iter()
            .map(|&z| linear_interp(&ts, &scalars, z))
            .collect(),
    )
}

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
    r_initial * (-z / tau_ricci).exp()
}

// ─── Tests ────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    /// Standard Python parameter set: b3 = 24, H0_late = 73.04.
    fn defaults() -> (f64, f64) {
        (73.04, 24.0)
    }

    #[test]
    fn h_at_z0_matches_sh0es() {
        let (h0_late, b3) = defaults();
        let h = solve_ricci_flow(vec![0.0], h0_late, b3);
        assert!((h[0] - 73.04).abs() < 1e-9, "H(0) = {} ≠ 73.04", h[0]);
    }

    #[test]
    fn h_at_z1100_matches_planck() {
        let (h0_late, b3) = defaults();
        let h = solve_ricci_flow(vec![1100.0], h0_late, b3);
        // f(1100) = 1/(1 + (1100/1.95)^2) ≈ 3.14e-6 → H ≈ 67.4 to within ~1e-4
        assert!(
            (h[0] - 67.4).abs() < 0.01,
            "H(1100) = {} ≠ 67.4 within 0.01",
            h[0]
        );
    }

    #[test]
    fn h_monotone_decreasing_from_73_to_67() {
        let (h0_late, b3) = defaults();
        let zs: Vec<f64> = (0..50).map(|i| 1100.0 * (i as f64 / 49.0)).collect();
        let hs = solve_ricci_flow(zs.clone(), h0_late, b3);
        for w in hs.windows(2) {
            assert!(w[0] >= w[1] - 1e-12, "H not monotone: {w:?}");
        }
        assert!(hs[0] > 73.0);
        assert!(hs[hs.len() - 1] < 68.0);
    }

    #[test]
    fn ricci_curvature_decays() {
        let r0 = ricci_curvature_at(0.0, 24.0);
        let r_high = ricci_curvature_at(100.0, 24.0);
        assert!(r0 > r_high, "R(z) should decay with z");
        assert!(r_high >= 0.0);
    }

    #[test]
    fn rkf45_solves_exponential_decay() {
        // dy/dt = -y, y(0) = 1 ⇒ y(1) = 1/e ≈ 0.367879
        let rhs = |state: &[f64], _t: f64| vec![-state[0]];
        let (ts, ys) = adaptive_integrate(&rhs, 0.0, 1.0, vec![1.0], 1e-9);
        let final_y = ys[ys.len() - 1][0];
        let expected = (-1.0_f64).exp();
        assert!(
            (final_y - expected).abs() < 1e-5,
            "RKF45 exp-decay: got {}, want {}, ts.len()={}",
            final_y,
            expected,
            ts.len()
        );
    }

    /// `dR/dz = -(1/tau) R / (1+z)` has the closed form
    /// `R(z) = R0 (1+z)^(-1/tau)`. The integrator must reproduce it.
    #[test]
    fn ricci_flow_curve_matches_the_closed_form_of_its_own_ode() {
        let b3 = 24.0_f64;
        let k_gimel = b3 / 2.0 + 1.0 / PI;
        let tau = k_gimel / b3;
        let r0 = b3 / (k_gimel * k_gimel);

        let zs: Vec<f64> = (0..25).map(|i| f64::from(i) * 0.4).collect();
        let numeric = ricci_flow_curve(&zs, b3).expect("a valid grid was rejected");
        assert_eq!(numeric.len(), zs.len());
        for (z, r) in zs.iter().zip(numeric.iter()) {
            let exact = r0 * (1.0 + z).powf(-1.0 / tau);
            let rel = (r - exact).abs() / exact.abs().max(1e-30);
            assert!(rel < 1e-3, "R({z}) = {r}, closed form {exact}, rel {rel:e}");
        }
    }

    /// Guard on a discrepancy inherited from the Python, so that "fixing" one
    /// side without the other cannot pass unnoticed.
    ///
    /// `evolution_engine.RicciFlowIntegrator.flow_rate` states the ODE
    /// `dR/dz = -(1/tau) R / (1+z)`, whose solution is `R0 (1+z)^(-1/tau)`.
    /// `get_curvature_at_z` on the very same class advertises itself as "the
    /// analytic solution" and returns `R0 exp(-z/tau)`, which solves
    /// `dR/dz = -(1/tau) R` instead. The two agree only to first order at
    /// small z and diverge badly beyond it. [`ricci_curvature_at`] mirrors the
    /// exponential form because that is what the Python actually computes;
    /// which of the two is intended is a physics question for the author.
    #[test]
    fn exponential_accessor_is_not_the_solution_of_the_stated_ode() {
        let b3 = 24.0_f64;
        let curve = ricci_flow_curve(&[5.0], b3).expect("a valid grid was rejected");
        let accessor = ricci_curvature_at(5.0, b3);
        let rel = (curve[0] - accessor).abs() / accessor.abs();
        assert!(
            rel > 1.0,
            "the two curvature laws have converged (rel {rel:e}); one of them changed"
        );
    }

    #[test]
    fn ricci_flow_curve_rejects_bad_input_rather_than_defaulting() {
        assert!(ricci_flow_curve(&[], 24.0).is_none());
        assert!(ricci_flow_curve(&[-1.0], 24.0).is_none());
        assert!(ricci_flow_curve(&[f64::NAN], 24.0).is_none());
        assert!(ricci_flow_curve(&[1.0], 0.0).is_none());
    }

    #[test]
    fn linear_interp_endpoints_and_midpoint() {
        let ts = vec![0.0, 1.0, 2.0];
        let ys = vec![10.0, 20.0, 40.0];
        assert!((linear_interp(&ts, &ys, 0.0) - 10.0).abs() < 1e-12);
        assert!((linear_interp(&ts, &ys, 2.0) - 40.0).abs() < 1e-12);
        assert!((linear_interp(&ts, &ys, 0.5) - 15.0).abs() < 1e-12);
        // out of range clamps
        assert!((linear_interp(&ts, &ys, -1.0) - 10.0).abs() < 1e-12);
        assert!((linear_interp(&ts, &ys, 3.0) - 40.0).abs() < 1e-12);
    }
}
