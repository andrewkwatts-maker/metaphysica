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

// PyO3 0.22's `#[pyfunction]` / `#[pymethods]` expansion trips
// `clippy::useless_conversion` on the `PyResult<T>` return type of every
// wrapper in this file. The lint fires on generated code, and its suggestion
// -- "consider removing" the return type -- does not compile. Silenced here
// rather than obeyed. Note this only ever appears under
// `cargo clippy --all-features`; the default-feature run does not compile
// this module at all, which is how fourteen clippy errors sat here unseen.
#![allow(clippy::useless_conversion)]

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

/// Upper bound on elements accepted from a Python sequence in one call.
///
/// Every wrapper that iterates caller-supplied data checks its length against
/// this first, so a malformed or hostile input fails fast with a clear error
/// instead of allocating unboundedly.
pub const MAX_SEQUENCE_LEN: usize = 1_048_576;

mod geometry;
mod hodge;
mod physics;
mod registry;

pub use registry::{PyFormulasRegistry, PyQuarkRegistry};

use geometry::{
    py_e8_density_convergence, py_e8_lattice_complete, py_e8_lattice_points, py_e8_roots,
    py_flat_torus_dirac_spectrum, py_orbifold_analyse, py_orbifold_close_group,
};
use hodge::{py_hodge_involution_max_error, py_hodge_star_3form, py_hodge_star_4form};
use physics::{py_gauge_rg_one_loop, py_ricci_flow_curve, py_ricci_flow_solve};
use registry::{py_get_constant, py_list_constants, py_list_quarks};

// Compile-time, not debug-time. These two facts are about constants, so a
// `debug_assert!` on them is vacuous -- always true, and compiled out of
// release anyway. Clippy was right to reject them; the fix is to make a
// violation a build failure rather than to weaken the check.
const _: () = assert!(MAX_SEQUENCE_LEN > 0);
const _: () = assert!(MAX_SEQUENCE_LEN >= crate::hodge::RANK4_LEN);

/// Reject a Python sequence longer than [`MAX_SEQUENCE_LEN`].
///
/// This is the boundary guard itself, so it refuses rather than asserting:
/// a caller that sends an oversized sequence gets a `ValueError`, not a panic.
fn check_sequence_len(n: usize) -> PyResult<()> {
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
    m.add_function(wrap_pyfunction!(py_ricci_flow_curve, m)?)?;
    m.add_function(wrap_pyfunction!(py_e8_lattice_points, m)?)?;
    m.add_function(wrap_pyfunction!(py_e8_lattice_complete, m)?)?;
    m.add_function(wrap_pyfunction!(py_e8_density_convergence, m)?)?;
    m.add_function(wrap_pyfunction!(py_flat_torus_dirac_spectrum, m)?)?;
    m.add_function(wrap_pyfunction!(py_orbifold_close_group, m)?)?;
    m.add_function(wrap_pyfunction!(py_orbifold_analyse, m)?)?;
    m.add_function(wrap_pyfunction!(version_rust, m)?)?;
    m.add_function(wrap_pyfunction!(is_rust_backend, m)?)?;
    m.add("__version__", crate::version())?;
    m.add("MAX_SEQUENCE_LEN", MAX_SEQUENCE_LEN)?;
    Ok(())
}

#[cfg(test)]
mod tests;
