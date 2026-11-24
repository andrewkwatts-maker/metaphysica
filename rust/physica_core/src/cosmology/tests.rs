//! Unit tests for the `cosmology` module.

use super::integrator::{bracket, StepGrid, MIN_ACCEPTED_STEPS};
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
    let grid = adaptive_integrate(&rhs, 0.0, 1.0, vec![1.0], 1e-9);
    let final_y = grid.ys[grid.ys.len() - 1][0];
    let expected = (-1.0_f64).exp();
    assert!(
        (final_y - expected).abs() < 1e-5,
        "RKF45 exp-decay: got {}, want {}, ts.len()={}",
        final_y,
        expected,
        grid.ts.len()
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
/// RESOLVED 2026-09-05. This asserted the two laws DISAGREE, which they
/// did, and pinning it rather than quietly converging them was right --
/// which law is intended was a physics question, not a tidying one.
///
/// It is answered now, and the power law wins three ways: it is the
/// solution of the ODE `flow_rate` declares; cosmological evolution runs
/// in ln(1+z) because a = 1/(1+z), so the curvature falls as a power of
/// the scale factor while treating z as the affine parameter means
/// nothing; and the exponential underflows to exactly 0.0 in f64 at
/// recombination, so it makes the curvature vanish identically at
/// z = 1100. `ricci_flow_curve` already integrated the ODE correctly, so
/// the closed-form accessor was the odd one out.
#[test]
fn the_accessor_now_solves_the_stated_ode() {
    let b3 = 24.0_f64;
    let k_gimel = b3 / 2.0 + 1.0 / PI;
    let tau = k_gimel / b3;
    let r0 = b3 / (k_gimel * k_gimel);
    for &z in &[1.0_f64, 5.0, 50.0] {
        let curve = ricci_flow_curve(&[0.0, z], b3).expect("a valid grid was rejected");
        let accessor = ricci_curvature_at(z, b3);
        let closed = r0 * (1.0 + z).powf(-1.0 / tau);
        assert!(
            ((accessor - closed).abs() / closed).abs() < 1e-12,
            "accessor {accessor} is not the closed form {closed} at z={z}"
        );
        let rel = (curve[1] - accessor).abs() / accessor.abs();
        assert!(
            rel < 1e-4,
            "the ODE and the accessor have parted company at z={z} (rel {rel:e})"
        );
    }
}

/// The old law differs by ~1e39 at z = 50, so its return would be loud.
#[test]
fn the_exponential_law_is_not_silently_reintroduced() {
    let b3 = 24.0_f64;
    let k_gimel = b3 / 2.0 + 1.0 / PI;
    let tau = k_gimel / b3;
    let r0 = b3 / (k_gimel * k_gimel);
    let old_law = r0 * (-50.0_f64 / tau).exp();
    assert!(
        old_law < 1e-40,
        "the exponential no longer underflows at z=50"
    );
    assert!(
        ricci_curvature_at(50.0, b3) > 1e-20,
        "the exponential law is back"
    );
}

#[test]
fn ricci_flow_curve_rejects_bad_input_rather_than_defaulting() {
    assert!(ricci_flow_curve(&[], 24.0).is_none());
    assert!(ricci_flow_curve(&[-1.0], 24.0).is_none());
    assert!(ricci_flow_curve(&[f64::NAN], 24.0).is_none());
    assert!(ricci_flow_curve(&[1.0], 0.0).is_none());
}

/// `rel_tol` used to be taken by the driver and thrown away, with
/// `rkf45_step` hard-coding 1e-6 instead, so every caller got the same
/// accuracy whatever it asked for. Loosening the tolerance must now
/// visibly cost accuracy, and tightening it must visibly cost steps.
#[test]
fn rel_tol_is_honoured_rather_than_discarded() {
    let rhs = |state: &[f64], _t: f64| vec![-state[0]];
    let exact = (-1.0_f64).exp();

    let loose = adaptive_integrate(&rhs, 0.0, 1.0, vec![1.0], 1e-2);
    let tight = adaptive_integrate(&rhs, 0.0, 1.0, vec![1.0], 1e-13);

    let loose_err = (loose.ys[loose.ys.len() - 1][0] - exact).abs();
    let tight_err = (tight.ys[tight.ys.len() - 1][0] - exact).abs();

    assert!(
        tight_err < loose_err,
        "rel_tol changed nothing: loose {loose_err:e} vs tight {tight_err:e}"
    );
    assert!(
        tight.ts.len() > loose.ts.len(),
        "a 1e-13 tolerance took no more steps ({}) than 1e-2 ({})",
        tight.ts.len(),
        loose.ts.len()
    );
}

/// The step cap that keeps linear interpolation off the critical path.
/// Removing it silently degrades every sampled value between steps.
#[test]
fn the_driver_takes_at_least_the_minimum_number_of_steps() {
    let rhs = |state: &[f64], _t: f64| vec![-state[0]];
    // A tolerance this loose would otherwise let the controller cross the
    // whole span in a handful of steps.
    let grid = adaptive_integrate(&rhs, 0.0, 1.0, vec![1.0], 1e-1);
    assert!(
        grid.ts.len() > MIN_ACCEPTED_STEPS,
        "only {} accepted steps, the h_max cap is not being applied",
        grid.ts.len()
    );
}

/// The ODE path must stay accurate all the way out to recombination, not
/// only over the short span the first test covers. Measured worst case is
/// ~6.1e-5 relative; 1e-3 leaves headroom without hiding a regression.
#[test]
fn ricci_flow_curve_is_accurate_out_to_recombination() {
    let b3 = 24.0_f64;
    let k_gimel = b3 / 2.0 + 1.0 / PI;
    let tau = k_gimel / b3;
    let r0 = b3 / (k_gimel * k_gimel);

    let zs: Vec<f64> = (0..=40).map(|i| 1100.0 * f64::from(i) / 40.0).collect();
    let numeric = ricci_flow_curve(&zs, b3).expect("a valid grid was rejected");
    for (z, r) in zs.iter().zip(numeric.iter()) {
        let exact = r0 * (1.0 + z).powf(-1.0 / tau);
        let rel = (r - exact).abs() / exact;
        assert!(rel < 1e-3, "R({z}) rel error {rel:e} exceeds 1e-3");
    }
    for w in numeric.windows(2) {
        assert!(w[0] > w[1], "curvature must fall with redshift: {w:?}");
    }
}

/// `solve_ricci_flow` returns H0_eff, NOT the H(z) that the Python method
/// of the nearest name returns. The Python multiplies by
/// `E(z) = sqrt(Om (1+z)^3 + Ode)`; the two agree only at z = 0. A future
/// edit that "fixes parity" by folding E(z) in here must break this test
/// and be made deliberately.
#[test]
fn solve_ricci_flow_returns_h0_eff_and_not_h_of_z() {
    let (h0_late, b3) = defaults();
    let z = 1.0_f64;
    let h0_eff = solve_ricci_flow(vec![0.0, z], h0_late, b3);

    assert!(
        (h0_eff[0] - h0_late).abs() < 1e-12,
        "z=0 must be the identity"
    );

    // Omega_m and Omega_de as hard-coded in calculate_h_evolution_interpolated.
    let e_z = (0.311 * (1.0 + z).powi(3) + 0.689).sqrt();
    let h_of_z = h0_eff[1] * e_z;
    assert!(
        (h_of_z - h0_eff[1]).abs() > 10.0,
        "E(z) has become the identity; the two quantities are no longer distinct"
    );
}

#[test]
#[should_panic(expected = "every redshift must be finite and non-negative")]
fn solve_ricci_flow_refuses_a_nan_redshift() {
    // NaN in, NaN out would have looked exactly like an answer.
    let _ = solve_ricci_flow(vec![0.0, f64::NAN], 73.04, 24.0);
}

#[test]
#[should_panic(expected = "h0_late must be finite and > 0")]
fn solve_ricci_flow_refuses_a_nan_h0() {
    let _ = solve_ricci_flow(vec![0.0], f64::NAN, 24.0);
}

/// The Hermite interpolant must pass through every node exactly, clamp
/// outside the grid, and reproduce a cubic in between -- a cubic is the
/// highest order it is exact for, so that is the sharpest check available.
#[test]
fn hermite_interp_is_exact_on_nodes_and_on_cubics() {
    // y(t) = t^3 - 2t + 1, dy/dt = 3t^2 - 2.
    let f = |t: f64| t * t * t - 2.0 * t + 1.0;
    let df = |t: f64| 3.0 * t * t - 2.0;
    let ts = vec![0.0, 1.0, 2.5];
    let grid = StepGrid {
        ys: ts.iter().map(|&t| vec![f(t)]).collect(),
        dys: ts.iter().map(|&t| vec![df(t)]).collect(),
        ts: ts.clone(),
    };
    for &t in &ts {
        assert!(
            (hermite_interp(&grid, 0, t) - f(t)).abs() < 1e-12,
            "node {t} not reproduced"
        );
    }
    for k in 1..40 {
        let t = 2.5 * f64::from(k) / 40.0;
        let got = hermite_interp(&grid, 0, t);
        assert!(
            (got - f(t)).abs() < 1e-10,
            "cubic not reproduced at {t}: {got} vs {}",
            f(t)
        );
    }
    // Outside the grid the value clamps to the nearest endpoint.
    assert!((hermite_interp(&grid, 0, -1.0) - f(0.0)).abs() < 1e-12);
    assert!((hermite_interp(&grid, 0, 9.0) - f(2.5)).abs() < 1e-12);
}

/// Regression on the fix: on the grid the controller now chooses, the
/// second-order interpolant that used to be used here is orders of
/// magnitude worse -- which is exactly why the step count had to be
/// inflated to 4_096 to hide it.
#[test]
fn hermite_beats_the_linear_interpolant_it_replaced() {
    let b3 = 24.0_f64;
    let k_gimel = b3 / 2.0 + 1.0 / PI;
    let tau = k_gimel / b3;
    let r0 = b3 / (k_gimel * k_gimel);
    let rhs = |state: &[f64], z: f64| ricci_rhs(state, z, b3);
    let grid = adaptive_integrate(&rhs, 0.0, 20.0, vec![r0], RICCI_REL_TOL);

    let mut worst_hermite = 0.0_f64;
    let mut worst_linear = 0.0_f64;
    for k in 1..200 {
        let z = 20.0 * f64::from(k) / 200.0;
        let exact = r0 * (1.0 + z).powf(-1.0 / tau);
        let (lo, hi) = bracket(&grid.ts, z);
        let w = (z - grid.ts[lo]) / (grid.ts[hi] - grid.ts[lo]);
        let lin = grid.ys[lo][0] + (grid.ys[hi][0] - grid.ys[lo][0]) * w;
        worst_hermite = worst_hermite.max((hermite_interp(&grid, 0, z) - exact).abs() / exact);
        worst_linear = worst_linear.max((lin - exact).abs() / exact);
    }
    assert!(
        worst_hermite * 100.0 < worst_linear,
        "hermite {worst_hermite:e} is not decisively better than linear {worst_linear:e}"
    );
}
