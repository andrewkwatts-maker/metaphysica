//====== Metaphysica/rust/physica_core/src/ckm.rs ======//
//!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! CKM matrix derivation and unitarity check.
//!
//! Ports `simulations/PM/particle/ckm_matrix.py`. The matrix is built once
//! at registry init from the underlying topology and cached; queries from
//! pt-physica's per-frame frame loop hit the cached rows directly.
//!
//! Wave-1 status: the constructor builds an identity-shaped placeholder so
//! the type signatures match the Python facade. Real derivation lands in
//! Wave-4.

use serde::{Deserialize, Serialize};
use thiserror::Error;

/// Errors surfaced by CKM construction / queries.
#[derive(Debug, Error)]
pub enum CkmError {
    /// The matrix failed unitarity check at the given tolerance.
    #[error("CKM unitarity violated: max row deviation = {0:e} (tol {1:e})")]
    NonUnitary(f64, f64),
}

/// Cabibbo-Kobayashi-Maskawa quark-mixing matrix.
///
/// Stored as a row-major 3×3 of magnitudes (sign + phase information lives
/// downstream in Python until Wave-5 brings full complex support).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CKMMatrix {
    /// Row-major 3×3 of magnitudes.
    pub rows: [[f64; 3]; 3],
    /// Jarlskog CP-violation invariant J.
    pub jarlskog_invariant: f64,
    /// Cabibbo angle θ_C in radians.
    pub cabibbo_angle: f64,
}

impl CKMMatrix {
    /// Build a CKM matrix from the G2-manifold topology.
    ///
    /// Wave-1 stub returns the 3×3 identity (so unitarity_check passes) plus
    /// zero CP-violation parameters. Real construction ports
    /// `ckm_matrix.py::derive_ckm_from_topology` in Wave-4.
    #[must_use]
    pub fn from_topology() -> Self {
        Self {
            rows: [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            jarlskog_invariant: 0.0,
            cabibbo_angle: 0.0,
        }
    }

    /// Verify each row sums (in modulus-squared) to 1.0 within `tol`.
    ///
    /// Plan §D.7 sets the production tolerance to `1e-8`.
    pub fn unitarity_check(&self, tol: f64) -> Result<(), CkmError> {
        debug_assert!(tol > 0.0);
        let mut max_dev: f64 = 0.0;
        for row in &self.rows {
            let s: f64 = row.iter().map(|v| v * v).sum();
            let dev = (s - 1.0).abs();
            if dev > max_dev {
                max_dev = dev;
            }
        }
        if max_dev <= tol {
            Ok(())
        } else {
            Err(CkmError::NonUnitary(max_dev, tol))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn from_topology_is_unitary_identity() {
        let m = CKMMatrix::from_topology();
        assert!(m.unitarity_check(1e-12).is_ok());
        assert_eq!(m.rows[0][0], 1.0);
        assert_eq!(m.rows[1][1], 1.0);
        assert_eq!(m.rows[2][2], 1.0);
    }

    #[test]
    fn non_unitary_matrix_fails_check() {
        let mut m = CKMMatrix::from_topology();
        m.rows[0][0] = 0.5;
        let err = m.unitarity_check(1e-8).unwrap_err();
        matches!(err, CkmError::NonUnitary(_, _));
    }
}
