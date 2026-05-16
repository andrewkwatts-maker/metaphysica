//====== Metaphysica/rust/physica_core/src/pyfacade.rs ======//
//!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! PyO3 facade exposed to Python as the `metaphysica._physica_core`
//! extension module. Gated behind the `python` feature so the engine path
//! (no Python runtime) compiles cleanly without PyO3.
//!
//! Wave-1: minimum-viable bindings — instantiate the core registries from
//! Python and read seed values back. The full datasheet round-trip lands as
//! the Python facade migrates over in Wave-2.

#![cfg(feature = "python")]

use crate::ckm::CKMMatrix;
use crate::constants::FormulasRegistry;
use crate::quarks::QuarkRegistry;
use pyo3::exceptions::PyKeyError;
use pyo3::prelude::*;

/// Python wrapper for [`FormulasRegistry`].
#[pyclass(name = "PyFormulasRegistry")]
pub struct PyFormulasRegistry {
    inner: FormulasRegistry,
}

#[pymethods]
impl PyFormulasRegistry {
    /// Construct a new registry pre-loaded with the Ten Pillar Seeds.
    #[new]
    fn new() -> Self {
        Self {
            inner: FormulasRegistry::new(),
        }
    }

    /// Number of registered constants (seeds + cached derivations).
    fn __len__(&self) -> usize {
        self.inner.len()
    }

    /// Retrieve the numeric value for `name`.
    fn get(&self, name: &str) -> PyResult<f64> {
        self.inner
            .get(name)
            .map(|c| c.value)
            .map_err(|e| PyKeyError::new_err(e.to_string()))
    }

    /// Library-version round-trip helper.
    #[staticmethod]
    fn version() -> &'static str {
        crate::version()
    }
}

/// Python wrapper for [`QuarkRegistry`].
#[pyclass(name = "PyQuarkRegistry")]
pub struct PyQuarkRegistry {
    inner: QuarkRegistry,
}

#[pymethods]
impl PyQuarkRegistry {
    #[new]
    fn new() -> Self {
        Self {
            inner: QuarkRegistry::new(),
        }
    }

    fn __len__(&self) -> usize {
        self.inner.len()
    }
}

/// Python wrapper for [`CKMMatrix`].
#[pyclass(name = "PyCKMMatrix")]
pub struct PyCKMMatrix {
    inner: CKMMatrix,
}

#[pymethods]
impl PyCKMMatrix {
    /// Build the CKM matrix from the underlying topology.
    #[staticmethod]
    fn from_topology() -> Self {
        Self {
            inner: CKMMatrix::from_topology(),
        }
    }

    /// `True` when the matrix is unitary within `tol`.
    fn is_unitary(&self, tol: f64) -> bool {
        self.inner.unitarity_check(tol).is_ok()
    }

    /// CP-violation Jarlskog invariant J.
    fn jarlskog(&self) -> f64 {
        self.inner.jarlskog_invariant
    }
}

/// Rust-accelerated twin of `metaphysica.list_constants`.
///
/// Returns all known constant names from the FormulasRegistry.
#[pyfunction]
fn py_list_constants() -> Vec<String> {
    FormulasRegistry::new().known_names()
}

/// Rust-accelerated twin of `metaphysica.list_quarks`.
///
/// Returns all SM quark names from the QuarkRegistry.
#[pyfunction]
fn py_list_quarks() -> Vec<String> {
    use crate::quarks::QuarkRegistry;
    QuarkRegistry::standard_model().known_names()
}

/// Rust-accelerated twin of `metaphysica.Get` for the constants branch.
///
/// Returns a JSON-serialised dict with `name`, `value`, `units`,
/// `uncertainty`, and `status` fields — matching the Python constant
/// datasheet schema so callers don't need to branch.
///
/// Raises `PyKeyError` when `name` is not in the registry.
#[pyfunction]
fn py_get_constant(py: Python<'_>, name: &str) -> PyResult<PyObject> {
    assert!(!name.is_empty(), "py_get_constant: name must be non-empty");
    let reg = FormulasRegistry::new();
    let c = reg
        .get(name)
        .map_err(|e| pyo3::exceptions::PyKeyError::new_err(e.to_string()))?;
    let map = serde_json::json!({
        "name": c.name,
        "value": c.value,
        "units": c.units,
        "uncertainty": c.uncertainty,
        "status": format!("{:?}", c.status),
    });
    let json_str = serde_json::to_string(&map)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    let json_mod = py.import_bound("json")?;
    json_mod.call_method1("loads", (json_str,))?.extract()
}

/// PyO3 module entry point. Wired as `metaphysica._physica_core`.
#[pymodule]
fn _physica_core(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyFormulasRegistry>()?;
    m.add_class::<PyQuarkRegistry>()?;
    m.add_class::<PyCKMMatrix>()?;
    m.add_function(wrap_pyfunction!(py_list_constants, m)?)?;
    m.add_function(wrap_pyfunction!(py_list_quarks, m)?)?;
    m.add_function(wrap_pyfunction!(py_get_constant, m)?)?;
    m.add("__version__", crate::version())?;
    Ok(())
}

#[cfg(test)]
mod tests {
    // The PyO3-decorated functions can only run inside a Python interpreter,
    // so the unit tests here cover only the plain logic.
    use crate::ckm::CKMMatrix;
    use crate::constants::FormulasRegistry;

    #[test]
    fn registry_round_trip() {
        let r = FormulasRegistry::new();
        assert!(r.get("b3").is_ok());
    }

    #[test]
    fn ckm_topology_is_unitary() {
        let m = CKMMatrix::from_topology();
        assert!(m.unitarity_check(1e-12).is_ok());
    }
}
