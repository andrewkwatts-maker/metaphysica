//! Registry classes and constant/quark lookups.

use crate::constants::FormulasRegistry;
use crate::quarks::QuarkRegistry;
use pyo3::exceptions::{PyKeyError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;

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
pub(super) fn py_list_constants() -> Vec<String> {
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
pub(super) fn py_list_quarks() -> Vec<String> {
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
pub(super) fn py_get_constant<'py>(py: Python<'py>, name: &str) -> PyResult<Bound<'py, PyDict>> {
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
