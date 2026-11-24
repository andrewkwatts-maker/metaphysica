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
/// Floor on the number of accepted steps across the span, imposed by capping
/// `h` from above. This is a grid-resolution floor, not an accuracy crutch:
/// it stops the controller leaping the whole span in one or two steps and
/// handing back a grid too coarse to interpolate on. It used to be 4_096,
/// which was large enough that the step size was pinned at `h_max` on every
/// step of every realistic problem -- so the error controller never bound and
/// `rel_tol` had no observable effect, even after it was plumbed through. The
/// fix was to make the interpolation fourth order (see [`hermite_interp`])
/// rather than to over-resolve the grid.
const MIN_ACCEPTED_STEPS: usize = 16;
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

/// Accepted-step record produced by the driver.
///
/// `dys[i]` is the RHS evaluated at `(ts[i], ys[i])`. Carrying it costs one
/// extra RHS call per accepted step and buys fourth-order interpolation; the
/// alternative is a second-order interpolant that has to be propped up with a
/// far finer grid, which is what this module used to do.
struct StepGrid {
    ts: Vec<f64>,
    ys: Vec<Vec<f64>>,
    dys: Vec<Vec<f64>>,
}

/// Adaptive RKF45 driver from `t0` to `t_end`.
///
/// Step-size control mirrors scipy's classic PI controller with safety
/// factor 0.9 and shrink/grow bounds (0.1, 5.0). Every accepted step is
/// recorded in the returned [`StepGrid`] for later interpolation onto the
/// caller's evaluation grid.
fn adaptive_integrate<F>(rhs: &F, t0: f64, t_end: f64, y0: Vec<f64>, rel_tol: f64) -> StepGrid
where
    F: Fn(&[f64], f64) -> Vec<f64>,
{
    assert!(t_end > t0, "adaptive_integrate: t_end must exceed t0");
    assert!(
        rel_tol.is_finite() && rel_tol > 0.0,
        "adaptive_integrate: rel_tol must be finite and > 0"
    );

    let mut ts = vec![t0];
    let mut dys = vec![rhs(&y0, t0)];
    let mut ys = vec![y0.clone()];

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
            dys.push(rhs(&y, t));
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
    debug_assert!(
        ts.len() > MIN_ACCEPTED_STEPS,
        "the h_max cap must force more than MIN_ACCEPTED_STEPS grid points"
    );

    // Not a debug_assert: falling short of t_end means the step cap was hit
    // and every interpolated value past the last step would silently be the
    // clamped endpoint rather than a solution.
    assert!(
        t >= t_end - 1e-9,
        "adaptive_integrate: failed to reach t_end within its step cap"
    );
    StepGrid { ts, ys, dys }
}

/// Index pair bracketing `z`, i.e. `ts[lo] <= z <= ts[hi]` with `hi == lo + 1`.
///
/// Caller must have ruled out `z` outside `[ts[0], ts[last]]`.
fn bracket(ts: &[f64], z: f64) -> (usize, usize) {
    debug_assert!(ts.len() >= 2, "bracketing needs at least two grid points");
    debug_assert!(
        z > ts[0] && z < ts[ts.len() - 1],
        "bracket called on a point outside the grid"
    );
    let mut lo = 0usize;
    let mut hi = ts.len() - 1;
    // The window halves every pass, so this terminates in at most log2(len).
    while hi - lo > 1 {
        let mid = lo + (hi - lo) / 2;
        if ts[mid] <= z {
            lo = mid;
        } else {
            hi = mid;
        }
    }
    (lo, hi)
}

/// Cubic Hermite interpolation of component `component` onto `z`.
///
/// This replaces a linear interpolant. Linear interpolation is second order,
/// so it was the accuracy floor of a fifth-order integrator: the driver had to
/// be pinned to 4_096 near-fixed steps to hide it, which in turn meant the
/// error controller never bound and the `rel_tol` argument -- already once
/// fixed for being discarded outright -- still changed nothing observable.
/// Hermite uses the derivative the RHS supplies at both ends of the interval,
/// so it is fourth order and the controller is free to choose the step.
fn hermite_interp(grid: &StepGrid, component: usize, z: f64) -> f64 {
    debug_assert!(!grid.ts.is_empty(), "cannot interpolate an empty grid");
    debug_assert_eq!(
        grid.ts.len(),
        grid.ys.len(),
        "step times and states disagree in length"
    );
    let last = grid.ts.len() - 1;
    if z <= grid.ts[0] {
        return grid.ys[0][component];
    }
    if z >= grid.ts[last] {
        return grid.ys[last][component];
    }
    let (lo, hi) = bracket(&grid.ts, z);
    let h = grid.ts[hi] - grid.ts[lo];
    debug_assert!(h > 0.0, "the step grid must be strictly increasing");
    let s = (z - grid.ts[lo]) / h;
    let s2 = s * s;
    let s3 = s2 * s;
    let h00 = 2.0 * s3 - 3.0 * s2 + 1.0;
    let h10 = s3 - 2.0 * s2 + s;
    let h01 = -2.0 * s3 + 3.0 * s2;
    let h11 = s3 - s2;
    h00 * grid.ys[lo][component]
        + h10 * h * grid.dys[lo][component]
        + h01 * grid.ys[hi][component]
        + h11 * h * grid.dys[hi][component]
}

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
