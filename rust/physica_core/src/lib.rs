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
//! * [`g2_manifold`] — manifold primitives, racetrack radius, spectral geometry
//! * [`validation`] — CMB anisotropy + isotropic-flow validators
//! * [`pyfacade`] — PyO3 bindings (gated `python` feature)
//! * [`arithmos_bridge`] — symbolic export of `Constant` records as
//!   `arithmos_core::expression::ArithmosExpression` (gated `with-arithmos`
//!   feature; intended for the engine path / git-checkout build only — *not*
//!   for the PyPI wheel)
//!
//! All public types are stub bodies; algorithm bodies are populated in later
//! waves of the porting plan. This wave-1 scaffold compiles cleanly and is
//! the contract every downstream consumer (the engine plugin `pt-physica`,
//! the Python facade, future tests) depends on.

pub mod constants;
pub mod quarks;
pub mod ckm;
pub mod gates;
pub mod simulations;
pub mod g2_manifold;
pub mod validation;
// cosmology.rs was never declared here, so the whole file -- including the
// Ricci-flow solver and its PyO3 wrapper -- was dead code that cargo never
// compiled. The C4 Ricci-invariant suite imports py_ricci_flow_solve from
// the extension and errored out on ImportError as a result.
pub mod cosmology;

#[cfg(feature = "python")]
pub mod pyfacade;

#[cfg(feature = "with-arithmos")]
pub mod arithmos_bridge;

// ─── Re-exports ─────────────────────────────────────────────────────────────
pub use ckm::CKMMatrix;
pub use constants::{Constant, ConstantStatus, FormulasRegistry};
pub use g2_manifold::{compute_spectral_geometry, G2Manifold};
pub use gates::gate_28_iterative;
pub use quarks::{QuarkPrediction, QuarkRegistry};
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

    #[test]
    fn version_matches_pypi() {
        // Kept in lock-step with `pyproject.toml`'s `[project] version`
        // in the parent metaphysica package — both must agree so wheel
        // metadata and Rust crate metadata report the same version.
        assert_eq!(version(), "2.0.0-alpha.0");
    }
}
