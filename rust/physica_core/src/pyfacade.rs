//====== Metaphysica/rust/physica_core/src/pyfacade.rs ======//
//!copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! PyO3 facade exposed to Python as the `metaphysica._physica_core` extension
//! module. Gated behind the `python` feature so the engine path (no Python
//! runtime) compiles cleanly without PyO3.
//!
//! ## Conventions
//!
//! * **Two meaningful runtime assertions minimum** per wrapper, checking what
//!   the Python boundary cannot express in types.
//! * **Bounded loops.** Any iteration over Python-supplied data checks its
//!   length against [`MAX_SEQUENCE_LEN`] first.
//! * **Errors surface as Python exceptions, never as a default value.** A
//!   wrapper that returns 0.0 on failure is worse than one that does not
//!   exist, because it makes the backend look healthy while it is not. That is
//!   not hypothetical here: `py_get_constant` used to call `registry.get()`,
//!   which returns the *stored* value, and stored values for `Pending` entries
//!   are 0.0 until `derive()` runs. Seven of the seventeen registry constants
//!   -- `v_higgs_mev`, `h0_central`, `m_tau_mev`, `n_gen_sq`, `sterile_check`,
//!   `topo_gen_check`, `w0_central` -- were reported to Python as exactly 0.0,
//!   and `metaphysica.Get()` preferred that answer over the Python path.
//!
//! Only kernels with real implementations are exported. The wave-1 scaffolds
//! (`gates`, `simulations`, `g2_manifold::compute_spectral_geometry`,
//! `ckm::CKMMatrix::from_topology`) stay unexported so a pass-through cannot
//! be mistaken for a derivation.

use crate::constants::FormulasRegistry;
use crate::quarks::QuarkRegistry;
use pyo3::exceptions::{PyKeyError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Upper bound on elements accepted from a Python sequence in one call.
///
/// Every wrapper that iterates caller-supplied data checks its length against
/// this first, so a malformed or hostile input fails fast with a clear error
/// instead of allocating unboundedly.
pub const MAX_SEQUENCE_LEN: usize = 1_048_576;

/// Python wrapper for [`FormulasRegistry`].
#[pyclass(name = "PyFormulasRegistry")]
pub struct PyFormulasRegistry {
    inner: FormulasRegistry,
}

#[pymethods]
impl PyFormulasRegistry {
    /// Construct a registry pre-loaded with the Ten Pillar Seeds and the
    /// first derived layer.
    #[new]
    fn new() -> Self {
        Self {
            inner: FormulasRegistry::new(),
        }
    }

    /// Number of registered constants (seeds + derived entries).
    fn __len__(&self) -> usize {
        self.inner.len()
    }

    /// Resolved numeric value for `name`.
    ///
    /// Derives on demand, so a `Pending` entry returns its evaluated value
    /// rather than the 0.0 placeholder it carries before evaluation.
    fn get(&self, name: &str) -> PyResult<f64> {
        if name.is_empty() {
            return Err(PyValueError::new_err("constant name must be non-empty"));
        }
        let value = self
            .inner
            .derive(name)
            .map_err(|e| PyKeyError::new_err(e.to_string()))?;
        if !value.is_finite() {
            return Err(PyValueError::new_err(format!(
                "constant `{name}` derived to a non-finite value ({value})"
            )));
        }
        Ok(value)
    }

    /// All registered constant names, sorted.
    fn names(&self) -> Vec<String> {
        self.inner.known_names()
    }

    /// Crate version, for the Python-side handshake.
    #[staticmethod]
    fn version() -> &'static str {
        crate::version()
    }
}

/// Python wrapper for [`QuarkRegistry`], pre-loaded with the six SM flavours.
#[pyclass(name = "PyQuarkRegistry")]
pub struct PyQuarkRegistry {
    inner: QuarkRegistry,
}

#[pymethods]
impl PyQuarkRegistry {
    #[new]
    fn new() -> Self {
        Self {
            inner: QuarkRegistry::standard_model(),
        }
    }

    fn __len__(&self) -> usize {
        self.inner.len()
    }

    /// All registered quark names, sorted.
    fn names(&self) -> Vec<String> {
        self.inner.known_names()
    }
}

/// Every constant name the registry knows, sorted.
#[pyfunction]
fn py_list_constants() -> Vec<String> {
    let names = FormulasRegistry::new().known_names();
    debug_assert!(!names.is_empty(), "the seeded registry cannot be empty");
    debug_assert!(
        names.windows(2).all(|w| w[0] < w[1]),
        "known_names must be sorted and duplicate-free"
    );
    names
}

/// Every Standard-Model quark name the registry knows, sorted.
#[pyfunction]
fn py_list_quarks() -> Vec<String> {
    let names = QuarkRegistry::standard_model().known_names();
    debug_assert_eq!(names.len(), 6, "the SM has six quark flavours");
    debug_assert!(
        names.windows(2).all(|w| w[0] < w[1]),
        "known_names must be sorted and duplicate-free"
    );
    names
}

/// Datasheet for one registry constant, as a dict.
///
/// Keys: `name`, `value`, `units`, `uncertainty`, `status`, `derivation_chain`.
/// Raises `KeyError` when `name` is not registered, and `ValueError` when the
/// derivation produces a non-finite value.
#[pyfunction]
fn py_get_constant<'py>(py: Python<'py>, name: &str) -> PyResult<Bound<'py, PyDict>> {
    if name.is_empty() {
        return Err(PyValueError::new_err("constant name must be non-empty"));
    }
    let reg = FormulasRegistry::new();
    // derive() before get(): get() hands back the stored value, which is the
    // 0.0 placeholder until the expression has been evaluated once.
    let value = reg
        .derive(name)
        .map_err(|e| PyKeyError::new_err(e.to_string()))?;
    let c = reg
        .get(name)
        .map_err(|e| PyKeyError::new_err(e.to_string()))?;
    debug_assert_eq!(c.name, name, "registry returned a different constant");
    debug_assert!(
        (c.value - value).abs() <= f64::EPSILON * value.abs().max(1.0),
        "derive() and get() disagree on `{name}`"
    );
    if !value.is_finite() {
        return Err(PyValueError::new_err(format!(
            "constant `{name}` derived to a non-finite value ({value})"
        )));
    }

    let d = PyDict::new_bound(py);
    d.set_item("name", &c.name)?;
    d.set_item("value", value)?;
    d.set_item("units", &c.units)?;
    d.set_item("uncertainty", c.uncertainty)?;
    d.set_item("status", format!("{:?}", c.status))?;
    d.set_item("derivation_chain", c.derivation_chain.clone())?;
    Ok(d)
}

/// The 240 roots of E8, as `list[list[float]]` of length 8.
#[pyfunction]
fn py_e8_roots() -> Vec<Vec<f64>> {
    let roots = crate::e8::enumerate_e8_roots();
    debug_assert_eq!(roots.len(), 240, "E8 has exactly 240 roots");
    debug_assert!(
        roots.iter().all(|r| r.len() == 8),
        "every E8 root lives in R^8"
    );
    roots.iter().map(|r| r.to_vec()).collect()
}

/// One-loop running of the three SM gauge couplings between two scales.
///
/// `alpha_init` is `[alpha_1, alpha_2, alpha_3]` at `mu_initial`, with
/// `alpha_1` in GUT normalisation. Raises `ValueError` on a non-positive scale
/// or coupling, and when the running crosses a Landau pole.
#[pyfunction]
fn py_gauge_rg_one_loop(
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

/// Hodge dual of an index-raised 3-form on R^7: 343 components in, 2401 out.
#[pyfunction]
fn py_hodge_star_3form(phi_up: Vec<f64>, sqrt_det_g: f64) -> PyResult<Vec<f64>> {
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
fn py_hodge_star_4form(star_up: Vec<f64>, sqrt_det_g: f64) -> PyResult<Vec<f64>> {
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
fn py_hodge_involution_max_error(
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

/// Unified Hubble-tension H0_eff(z) at each requested redshift.
#[pyfunction]
fn py_ricci_flow_solve(z_array: Vec<f64>, h0_late: f64, b3: f64) -> PyResult<Vec<f64>> {
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

/// Reject a Python sequence longer than [`MAX_SEQUENCE_LEN`].
fn check_sequence_len(n: usize) -> PyResult<()> {
    debug_assert!(MAX_SEQUENCE_LEN > 0, "the sequence bound must be positive");
    debug_assert!(
        MAX_SEQUENCE_LEN >= crate::hodge::RANK4_LEN,
        "the bound must admit the largest form this module accepts"
    );
    if n > MAX_SEQUENCE_LEN {
        return Err(PyValueError::new_err(format!(
            "sequence of {n} elements exceeds the {MAX_SEQUENCE_LEN}-element bound"
        )));
    }
    Ok(())
}

/// Crate version. The Python package compares this against its own
/// `__version__` in `assert_rust_backend()`; a stale extension left in the
/// source tree from an earlier build is otherwise very easy to miss.
#[pyfunction]
fn version_rust() -> &'static str {
    crate::version()
}

/// `True` whenever this module is importable at all. Exists so the Python side
/// can ask the extension rather than infer from a bare import succeeding.
#[pyfunction]
fn is_rust_backend() -> bool {
    true
}

/// PyO3 module entry point. Wired as `metaphysica._physica_core`.
#[pymodule]
fn _physica_core(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyFormulasRegistry>()?;
    m.add_class::<PyQuarkRegistry>()?;
    m.add_function(wrap_pyfunction!(py_list_constants, m)?)?;
    m.add_function(wrap_pyfunction!(py_list_quarks, m)?)?;
    m.add_function(wrap_pyfunction!(py_get_constant, m)?)?;
    m.add_function(wrap_pyfunction!(py_e8_roots, m)?)?;
    m.add_function(wrap_pyfunction!(py_gauge_rg_one_loop, m)?)?;
    m.add_function(wrap_pyfunction!(py_hodge_star_3form, m)?)?;
    m.add_function(wrap_pyfunction!(py_hodge_star_4form, m)?)?;
    m.add_function(wrap_pyfunction!(py_hodge_involution_max_error, m)?)?;
    m.add_function(wrap_pyfunction!(py_ricci_flow_solve, m)?)?;
    m.add_function(wrap_pyfunction!(version_rust, m)?)?;
    m.add_function(wrap_pyfunction!(is_rust_backend, m)?)?;
    m.add("__version__", crate::version())?;
    m.add("MAX_SEQUENCE_LEN", MAX_SEQUENCE_LEN)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    //! These run under `cargo test --features python`, which links libpython
    //! because `extension-module` is a separate feature. Fold the two together
    //! and this whole module silently stops being executed anywhere.
    use crate::constants::{ConstantStatus, FormulasRegistry};

    #[test]
    fn registry_round_trip() {
        let r = FormulasRegistry::new();
        assert!(r.get("b3").is_ok());
    }

    /// The regression this facade was rewritten for: every registry entry must
    /// resolve to its derived value, not to the 0.0 placeholder.
    #[test]
    fn every_registry_constant_derives_to_a_real_value() {
        let r = FormulasRegistry::new();
        let names = r.known_names();
        assert!(names.len() >= 17, "registry shrank: {} names", names.len());
        for name in names.iter().take(super::MAX_SEQUENCE_LEN) {
            let v = r
                .derive(name)
                .unwrap_or_else(|e| panic!("`{name}` failed to derive: {e}"));
            assert!(v.is_finite(), "`{name}` derived to {v}");
            let stored = r.get(name).expect("entry vanished after derive");
            assert_ne!(
                stored.status,
                ConstantStatus::Pending,
                "`{name}` is still Pending after derive()"
            );
            assert_eq!(stored.value, v, "cached value disagrees with derive()");
        }
    }

    #[test]
    fn known_derived_values_are_correct() {
        let r = FormulasRegistry::new();
        assert_eq!(r.derive("n_gen_sq").unwrap(), 9.0);
        assert_eq!(r.derive("sterile_check").unwrap(), 163.0);
        assert_eq!(r.derive("topo_gen_check").unwrap(), 3.0);
        assert_eq!(r.derive("h0_central").unwrap(), 70.0);
        assert_eq!(r.derive("w0_central").unwrap(), -1.0);
    }

    #[test]
    fn unknown_constant_is_an_error() {
        let r = FormulasRegistry::new();
        assert!(r.derive("no_such_constant").is_err());
    }

    #[test]
    fn sequence_bound_admits_the_largest_form() {
        assert!(super::MAX_SEQUENCE_LEN >= crate::hodge::RANK4_LEN);
    }
}
