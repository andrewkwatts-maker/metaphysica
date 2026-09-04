//====== Metaphysica/rust/physica_core/src/lib.rs ======//
//!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! `physica_core` — Rust core for metaphysica.
//!
//! Mirrors the upstream Python package `metaphysica` (PyPI v1.3.1) with a
//! high-performance native implementation of the hot-paths identified in the
//! integration plan §D:
//!
//! * [`constants`] — `Constant` records and `FormulasRegistry` (125 constants
//!   derived from the Ten Pillar Seeds)
//! * [`quarks`] — Yukawa φ-scaling for the six SM quarks (+ anti-partners)
//! * [`ckm`] — CKM matrix derivation + unitarity check
//! * [`gates`] — `gate_28_iterative` (stack-based; never recursive — see plan
//!   §D.2 #4)
//! * [`simulations`] — `TemporalSimulator` (RK4 over the 24-pin torsion cage)
//! * [`g2_manifold`] -- manifold primitives, racetrack radius, spectral geometry
//! * [`hodge`] -- Hodge-star kernels on R^7; the measured hot path
//! * [`e8`] -- the 240-root E8 enumeration
//! * [`rg_running`] -- one-loop gauge-coupling running
//! * [`cosmology`] -- Ricci-flow ODE solver
//! * [`validation`] -- CMB anisotropy + isotropic-flow validators
//! * [`pyfacade`] -- PyO3 bindings (gated `python` feature)
//!
//! ## Honest status
//!
//! Only [`hodge`], [`e8`], [`rg_running`], [`cosmology`] and the expression
//! evaluator in [`constants`] carry real algorithms. [`gates`],
//! [`simulations`], [`g2_manifold::compute_spectral_geometry`],
//! [`ckm::CKMMatrix::from_topology`] and [`validation`] are still wave-1
//! scaffolding -- pass-through or bracket checks whose doc comments say so.
//! None of them is wired into the Python facade, precisely so that a scaffold
//! cannot masquerade as a derivation.
//!
//! `src/arithmos_bridge.rs` is present but is **not a module of this crate**:
//! its `with-arithmos` cargo feature was never declared and the
//! `arithmos_core` dependency it imports was never added, so it has never been
//! compiled. Wiring it up needs an upstream decision that is outside this
//! crate -- see the file header.

pub mod ckm;
pub mod constants;
// cosmology.rs was never declared here, so the whole file -- including the
// Ricci-flow solver and its PyO3 wrapper -- was dead code that cargo never
// compiled. The C4 Ricci-invariant suite imports py_ricci_flow_solve from
// the extension and errored out on ImportError as a result.
pub mod cosmology;
// e8.rs and rg_running.rs had the same defect and went unnoticed for longer:
// 341 lines with 8 unit tests that cargo never saw, and a `py_e8_roots`
// binding that e8.rs's own header claims Python calls through
// `@rust_accelerated`. It could not have: the symbol was never in the module.
pub mod e8;
pub mod g2_manifold;
pub mod gates;
pub mod hodge;
pub mod quarks;
pub mod rg_running;
pub mod simulations;
pub mod validation;

#[cfg(feature = "python")]
pub mod pyfacade;

// ─── Re-exports ─────────────────────────────────────────────────────────────
pub use ckm::CKMMatrix;
pub use constants::{Constant, ConstantStatus, FormulasRegistry};
pub use cosmology::{ricci_curvature_at, ricci_flow_curve, solve_ricci_flow};
pub use e8::{e8_density_convergence, e8_lattice_points, enumerate_e8_roots};
pub use g2_manifold::{compute_spectral_geometry, flat_torus_dirac_spectrum, G2Manifold};
pub use gates::gate_28_iterative;
pub use hodge::{hodge_involution_max_error, hodge_star_3form, hodge_star_4form};
pub use quarks::{QuarkPrediction, QuarkRegistry};
pub use rg_running::gauge_rg_one_loop;
pub use simulations::{TemporalSimulator, TemporalState};
pub use validation::{validate_cmb_anisotropy, validate_isotropic_flow};

/// Library identifier.
pub fn name() -> &'static str {
    "physica_core"
}

/// Crate version pulled from `Cargo.toml` at compile time.
pub fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn name_is_physica_core() {
        assert_eq!(name(), "physica_core");
    }

    /// The crate version and the Python package version must agree, because
    /// `metaphysica.assert_rust_backend()` compares them at import time and a
    /// mismatch there is a hard failure for every user.
    ///
    /// The previous form of this test hard-coded "2.0.0-alpha.0" against a
    /// crate at 2.3.1 and simply failed, which is why the whole `cargo test`
    /// run was red and nobody in CI noticed: CI never invoked cargo at all.
    /// Reading pyproject.toml here means the check cannot go stale again.
    #[test]
    fn version_matches_pypi() {
        const PYPROJECT: &str = include_str!("../../../pyproject.toml");
        let mut in_project = false;
        let mut declared: Option<&str> = None;
        // Bounded: a source file cannot yield more lines than it has bytes.
        for line in PYPROJECT.lines().take(PYPROJECT.len()) {
            let line = line.trim();
            if line.starts_with('[') {
                in_project = line == "[project]";
                continue;
            }
            if in_project {
                if let Some(rest) = line.strip_prefix("version") {
                    declared = rest
                        .trim_start_matches(|c: char| c == '=' || c.is_whitespace())
                        .trim_matches('"')
                        .into();
                    break;
                }
            }
        }
        let declared = declared.expect("no [project] version in pyproject.toml");
        assert_eq!(
            version(),
            declared,
            "crate version and pyproject version have drifted"
        );
    }
}
