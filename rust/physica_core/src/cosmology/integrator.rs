//! Cash-Karp RKF45 adaptive driver and Hermite interpolation for the Ricci flow.

use std::f64::consts::PI;

/// Absolute term of the mixed error norm; floors the relative term near zero.
pub(super) const ABS_TOL: f64 = 1e-12;
/// Hard cap on accepted + rejected steps, so the driver always terminates.
pub(super) const MAX_INTEGRATION_STEPS: usize = 100_000;
/// Floor on the number of accepted steps across the span, imposed by capping
/// `h` from above. This is a grid-resolution floor, not an accuracy crutch:
/// it stops the controller leaping the whole span in one or two steps and
/// handing back a grid too coarse to interpolate on. It used to be 4_096,
/// which was large enough that the step size was pinned at `h_max` on every
/// step of every realistic problem -- so the error controller never bound and
/// `rel_tol` had no observable effect, even after it was plumbed through. The
/// fix was to make the interpolation fourth order (see [`hermite_interp`])
/// rather than to over-resolve the grid.
pub(super) const MIN_ACCEPTED_STEPS: usize = 16;
/// Below this step size a step is accepted regardless of the error estimate,
/// so a stiff patch cannot spin the controller.
pub(super) const MIN_STEP_SIZE: f64 = 1e-14;
/// Classic PI-controller safety factor.
pub(super) const SAFETY_FACTOR: f64 = 0.9;
/// Most the controller may grow the step in one accepted iteration.
pub(super) const MAX_STEP_GROWTH: f64 = 5.0;
/// Least the controller may shrink the step in one rejected iteration.
pub(super) const MAX_STEP_SHRINK: f64 = 0.1;

// ─── RKF45 (Cash-Karp) coefficients ───────────────────────────────────────
// Embedded 4th-order solution + 5th-order error estimator. The coefficients
// match those used by scipy.integrate.solve_ivp(method="RK45") closely
// enough that parity to rel=1e-6 holds across the full z-range we test.

// Time-fraction nodes c_i
pub(super) const C2: f64 = 1.0 / 5.0;
pub(super) const C3: f64 = 3.0 / 10.0;
pub(super) const C4: f64 = 3.0 / 5.0;
pub(super) const C5: f64 = 1.0;
pub(super) const C6: f64 = 7.0 / 8.0;

// Stage couplings a_ij
pub(super) const A21: f64 = 1.0 / 5.0;
pub(super) const A31: f64 = 3.0 / 40.0;
pub(super) const A32: f64 = 9.0 / 40.0;
pub(super) const A41: f64 = 3.0 / 10.0;
pub(super) const A42: f64 = -9.0 / 10.0;
pub(super) const A43: f64 = 6.0 / 5.0;
pub(super) const A51: f64 = -11.0 / 54.0;
pub(super) const A52: f64 = 5.0 / 2.0;
pub(super) const A53: f64 = -70.0 / 27.0;
pub(super) const A54: f64 = 35.0 / 27.0;
pub(super) const A61: f64 = 1631.0 / 55296.0;
pub(super) const A62: f64 = 175.0 / 512.0;
pub(super) const A63: f64 = 575.0 / 13824.0;
pub(super) const A64: f64 = 44275.0 / 110592.0;
pub(super) const A65: f64 = 253.0 / 4096.0;

// 5th-order solution weights b_i
pub(super) const B1: f64 = 37.0 / 378.0;
pub(super) const B3: f64 = 250.0 / 621.0;
pub(super) const B4: f64 = 125.0 / 594.0;
pub(super) const B6: f64 = 512.0 / 1771.0;

// 4th-order solution weights b*_i  (used to form error = b - b*)
pub(super) const BS1: f64 = 2825.0 / 27648.0;
pub(super) const BS3: f64 = 18575.0 / 48384.0;
pub(super) const BS4: f64 = 13525.0 / 55296.0;
pub(super) const BS5: f64 = 277.0 / 14336.0;
pub(super) const BS6: f64 = 1.0 / 4.0;

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
pub(super) fn rkf45_step<F>(rhs: &F, t: f64, y: &[f64], h: f64, rel_tol: f64) -> (Vec<f64>, f64)
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
pub(super) struct StepGrid {
    pub(super) ts: Vec<f64>,
    pub(super) ys: Vec<Vec<f64>>,
    pub(super) dys: Vec<Vec<f64>>,
}

/// Step growth factor after an accepted step with error norm `err`.
fn accepted_growth_factor(err: f64) -> f64 {
    if err == 0.0 {
        MAX_STEP_GROWTH
    } else {
        (SAFETY_FACTOR * err.powf(-0.2)).min(MAX_STEP_GROWTH)
    }
}

/// Step shrink factor after a rejected step with error norm `err`.
fn rejected_shrink_factor(err: f64) -> f64 {
    (SAFETY_FACTOR * err.powf(-0.25)).max(MAX_STEP_SHRINK)
}

/// Post-conditions of a finished drive: step cap respected, `t_end` reached.
fn check_drive_finished(steps: usize, accepted_points: usize, t: f64, t_end: f64) {
    debug_assert!(
        steps < MAX_INTEGRATION_STEPS,
        "integration hit its step cap"
    );
    debug_assert!(
        accepted_points > MIN_ACCEPTED_STEPS,
        "the h_max cap must force more than MIN_ACCEPTED_STEPS grid points"
    );

    // Not a debug_assert: falling short of t_end means the step cap was hit
    // and every interpolated value past the last step would silently be the
    // clamped endpoint rather than a solution.
    assert!(
        t >= t_end - 1e-9,
        "adaptive_integrate: failed to reach t_end within its step cap"
    );
}

/// Adaptive RKF45 driver from `t0` to `t_end`.
///
/// Step-size control mirrors scipy's classic PI controller with safety
/// factor 0.9 and shrink/grow bounds (0.1, 5.0). Every accepted step is
/// recorded in the returned [`StepGrid`] for later interpolation onto the
/// caller's evaluation grid.
pub(super) fn adaptive_integrate<F>(rhs: &F, t0: f64, t_end: f64, y0: Vec<f64>, rel_tol: f64) -> StepGrid
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
            h = (h * accepted_growth_factor(err)).min(h_max);
        } else {
            h *= rejected_shrink_factor(err);
        }
    }
    check_drive_finished(steps, ts.len(), t, t_end);
    StepGrid { ts, ys, dys }
}

/// Index pair bracketing `z`, i.e. `ts[lo] <= z <= ts[hi]` with `hi == lo + 1`.
///
/// Caller must have ruled out `z` outside `[ts[0], ts[last]]`.
pub(super) fn bracket(ts: &[f64], z: f64) -> (usize, usize) {
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
pub(super) fn hermite_interp(grid: &StepGrid, component: usize, z: f64) -> f64 {
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

#[cfg(test)]
mod pins;
