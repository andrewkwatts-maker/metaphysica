//====== Metaphysica/rust/physica_core/src/validation.rs ======//
//!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! CMB-anisotropy & isotropic-flow validators (plan §D.7).
//!
//! Ports `simulations/validation/{audit,sim}/`. These run at low frequency
//! (post-derivation, not per frame) so the Wave-1 stubs are intentionally
//! conservative and just bracket-check the derived predictions.

use serde::{Deserialize, Serialize};
use thiserror::Error;

/// Errors surfaced by validation routines.
#[derive(Debug, Error)]
pub enum ValidationError {
    /// Predicted value falls outside the empirical bracket.
    #[error("validation failed: {what} = {got} not in [{lo}, {hi}]")]
    OutOfBracket {
        what: String,
        got: f64,
        lo: f64,
        hi: f64,
    },

    /// Empty prediction batch.
    #[error("predictions empty: nothing to validate")]
    EmptyPredictions,
}

/// One CMB-anisotropy prediction (multipole ℓ + amplitude).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CmbPrediction {
    /// Multipole index ℓ (≥ 2).
    pub ell: u32,
    /// Predicted amplitude in μK².
    pub amplitude_uk2: f64,
}

/// Validate a batch of CMB-anisotropy predictions.
///
/// Wave-1 stub: requires at least one entry and that all amplitudes are
/// non-negative. Real Planck-era bracket checks land in Wave-6.
pub fn validate_cmb_anisotropy(predictions: &[CmbPrediction]) -> Result<(), ValidationError> {
    if predictions.is_empty() {
        return Err(ValidationError::EmptyPredictions);
    }
    for p in predictions {
        if p.amplitude_uk2 < 0.0 {
            return Err(ValidationError::OutOfBracket {
                what: format!("CMB ℓ={} amplitude", p.ell),
                got: p.amplitude_uk2,
                lo: 0.0,
                hi: f64::INFINITY,
            });
        }
    }
    Ok(())
}

/// Validate isotropic-flow parameters: `H0` (km / s / Mpc) and `w0` (DE EOS).
///
/// Plan §D.7 bracket: H0 ∈ [67, 73]; w0 within ±0.5% of −1.0 ⇒ [-1.005, −0.995].
pub fn validate_isotropic_flow(h0: f64, w0: f64) -> Result<(), ValidationError> {
    const H0_LO: f64 = 67.0;
    const H0_HI: f64 = 73.0;
    const W0_LO: f64 = -1.005;
    const W0_HI: f64 = -0.995;

    if !(H0_LO..=H0_HI).contains(&h0) {
        return Err(ValidationError::OutOfBracket {
            what: "H0".to_string(),
            got: h0,
            lo: H0_LO,
            hi: H0_HI,
        });
    }
    if !(W0_LO..=W0_HI).contains(&w0) {
        return Err(ValidationError::OutOfBracket {
            what: "w0".to_string(),
            got: w0,
            lo: W0_LO,
            hi: W0_HI,
        });
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_cmb_rejected() {
        let err = validate_cmb_anisotropy(&[]).unwrap_err();
        matches!(err, ValidationError::EmptyPredictions);
    }

    #[test]
    fn negative_amplitude_rejected() {
        let p = vec![CmbPrediction {
            ell: 2,
            amplitude_uk2: -1.0,
        }];
        let err = validate_cmb_anisotropy(&p).unwrap_err();
        matches!(err, ValidationError::OutOfBracket { .. });
    }

    #[test]
    fn isotropic_flow_in_range_passes() {
        assert!(validate_isotropic_flow(70.0, -1.0).is_ok());
    }

    #[test]
    fn isotropic_flow_h0_too_low_fails() {
        let err = validate_isotropic_flow(50.0, -1.0).unwrap_err();
        matches!(err, ValidationError::OutOfBracket { .. });
    }
}
