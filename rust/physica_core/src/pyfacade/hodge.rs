//! Hodge-star kernels on R^7.

use super::{check_sequence_len, MAX_SEQUENCE_LEN};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

/// Hodge dual of an index-raised 3-form on R^7: 343 components in, 2401 out.
#[pyfunction]
pub(super) fn py_hodge_star_3form(phi_up: Vec<f64>, sqrt_det_g: f64) -> PyResult<Vec<f64>> {
    check_sequence_len(phi_up.len())?;
    debug_assert!(
        phi_up.len() <= MAX_SEQUENCE_LEN,
        "length guard let an oversized form through"
    );
    let out = crate::hodge::hodge_star_3form(&phi_up, sqrt_det_g)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;
    debug_assert_eq!(
        out.len(),
        crate::hodge::RANK4_LEN,
        "dual of a 3-form is a 4-form"
    );
    Ok(out)
}

/// Hodge dual of an index-raised 4-form on R^7: 2401 components in, 343 out.
#[pyfunction]
pub(super) fn py_hodge_star_4form(star_up: Vec<f64>, sqrt_det_g: f64) -> PyResult<Vec<f64>> {
    check_sequence_len(star_up.len())?;
    debug_assert!(
        star_up.len() <= MAX_SEQUENCE_LEN,
        "length guard let an oversized form through"
    );
    let out = crate::hodge::hodge_star_4form(&star_up, sqrt_det_g)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;
    debug_assert_eq!(
        out.len(),
        crate::hodge::RANK3_LEN,
        "dual of a 4-form is a 3-form"
    );
    Ok(out)
}

/// Largest componentwise deviation of `**phi` from `phi`.
#[pyfunction]
pub(super) fn py_hodge_involution_max_error(
    phi: Vec<f64>,
    star_up: Vec<f64>,
    sqrt_det_g: f64,
) -> PyResult<f64> {
    check_sequence_len(phi.len())?;
    check_sequence_len(star_up.len())?;
    let err = crate::hodge::hodge_involution_max_error(&phi, &star_up, sqrt_det_g)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;
    debug_assert!(
        err.is_finite(),
        "a finite input produced a non-finite error"
    );
    debug_assert!(
        err >= 0.0,
        "a maximum absolute deviation cannot be negative"
    );
    Ok(err)
}
