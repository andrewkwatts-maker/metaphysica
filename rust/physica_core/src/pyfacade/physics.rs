//! Gauge-coupling running and Ricci-flow cosmology.

use super::{check_sequence_len, MAX_SEQUENCE_LEN};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

/// One-loop running of the three SM gauge couplings between two scales.
///
/// `alpha_init` is `[alpha_1, alpha_2, alpha_3]` at `mu_initial`, with
/// `alpha_1` in GUT normalisation. Raises `ValueError` on a non-positive scale
/// or coupling, and when the running crosses a Landau pole.
#[pyfunction]
pub(super) fn py_gauge_rg_one_loop(
    mu_initial: f64,
    mu_final: f64,
    alpha_init: Vec<f64>,
) -> PyResult<Vec<f64>> {
    if alpha_init.len() != 3 {
        return Err(PyValueError::new_err(format!(
            "alpha_init must hold 3 couplings, got {}",
            alpha_init.len()
        )));
    }
    if !(mu_initial.is_finite() && mu_initial > 0.0 && mu_final.is_finite() && mu_final > 0.0) {
        return Err(PyValueError::new_err(
            "both scales must be finite and strictly positive",
        ));
    }
    if !alpha_init.iter().all(|a| a.is_finite() && *a > 0.0) {
        return Err(PyValueError::new_err(
            "every initial coupling must be finite and strictly positive",
        ));
    }
    let fixed = [alpha_init[0], alpha_init[1], alpha_init[2]];
    let out = crate::rg_running::gauge_rg_one_loop(mu_initial, mu_final, fixed);
    debug_assert_eq!(out.len(), 3, "three gauge couplings in, three out");
    debug_assert!(
        mu_initial != mu_final || out == fixed,
        "running to the same scale must be the identity"
    );
    // A sign flip in 1/alpha means the run passed through a Landau pole; the
    // resulting negative coupling is not a physical answer and must not be
    // handed back as though it were.
    if !out.iter().all(|a| a.is_finite() && *a > 0.0) {
        return Err(PyValueError::new_err(format!(
            "one-loop running from {mu_initial} to {mu_final} GeV crossed a Landau pole"
        )));
    }
    Ok(out.to_vec())
}

/// Unified Hubble-tension H0_eff(z) at each requested redshift.
#[pyfunction]
pub(super) fn py_ricci_flow_solve(z_array: Vec<f64>, h0_late: f64, b3: f64) -> PyResult<Vec<f64>> {
    check_sequence_len(z_array.len())?;
    if z_array.is_empty() {
        return Err(PyValueError::new_err("z_array must be non-empty"));
    }
    if !z_array.iter().all(|z| z.is_finite() && *z >= 0.0) {
        return Err(PyValueError::new_err(
            "every redshift must be finite and non-negative",
        ));
    }
    if !(h0_late.is_finite() && h0_late > 0.0) {
        return Err(PyValueError::new_err("h0_late must be finite and > 0"));
    }
    if !(b3.is_finite() && b3 > 0.0) {
        return Err(PyValueError::new_err("b3 must be finite and > 0"));
    }
    let out = crate::cosmology::solve_ricci_flow(z_array.clone(), h0_late, b3);
    debug_assert_eq!(
        out.len(),
        z_array.len(),
        "one H0_eff per requested redshift"
    );
    debug_assert!(
        out.iter().all(|h| h.is_finite()),
        "the solver produced a non-finite H0_eff"
    );
    Ok(out)
}

/// Ricci curvature R(z) from the numerically integrated flow ODE.
///
/// This is the ODE solve itself, as opposed to [`py_ricci_flow_solve`], which
/// evaluates the closed-form H0_eff interpolation and never touches R(z). The
/// kernel existed but was reachable only from Rust unit tests.
#[pyfunction]
pub(super) fn py_ricci_flow_curve(z_array: Vec<f64>, b3: f64) -> PyResult<Vec<f64>> {
    check_sequence_len(z_array.len())?;
    debug_assert!(
        z_array.len() <= MAX_SEQUENCE_LEN,
        "length guard let an oversized grid through"
    );
    // `ricci_flow_curve` returns None rather than a default on bad input; the
    // boundary turns that into a Python exception instead of a silent value.
    let out = crate::cosmology::ricci_flow_curve(&z_array, b3).ok_or_else(|| {
        PyValueError::new_err(
            "z_array must be non-empty with finite non-negative redshifts, and b3 finite and > 0",
        )
    })?;
    debug_assert_eq!(out.len(), z_array.len(), "one curvature per redshift");
    debug_assert!(
        out.iter().all(|r| r.is_finite() && *r > 0.0),
        "the Ricci flow produced a non-finite or non-positive curvature"
    );
    Ok(out)
}
