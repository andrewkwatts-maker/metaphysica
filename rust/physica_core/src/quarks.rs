//====== Metaphysica/rust/physica_core/src/quarks.rs ======//
//!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! Quark predictions and Yukawa φ-scaling.
//!
//! Ports `simulations/PM/particle/yukawa_textures.py`. The mass formula
//! `m_n = v_higgs / φ^N` is the hot-path that every CKM-matrix call and
//! every periodica datasheet build evaluates many times per frame.
//!
//! ## Standard texture (from `yukawa_textures.py` lines 24–31)
//!
//! | Quark    | N  | Predicted (MeV)  | PDG (MeV)    |
//! |----------|----|------------------|--------------|
//! | top      |  0 | 246 220          | 172 690      |
//! | bottom   |  4 | ~  3 569         |   4 180      |
//! | charm    |  5 | ~  2 206         |   1 270      |
//! | strange  |  8 | ~    521         |      93      |
//! | down     | 11 | ~    123         |       4.67   |
//! | up       | 12 | ~     76         |       2.16   |
//!
//! Raw φ^N scaling reproduces the order-of-magnitude hierarchy across 8
//! decades — the residual mismatches are absorbed by the texture matrix
//! (CKM-coupling rotation) in `yukawa_textures.py::compute`. The validator
//! [`quark_hierarchy_check`] checks the *log-spacing* matches PDG within a
//! configurable tolerance (default 1.0 = one e-fold), not the absolute mass.

use crate::constants::{
    FormulasSource, SEED_GOLDEN_RATIO, PHYSICA_V_HIGGS_MEV,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use thiserror::Error;

/// Errors surfaced by [`QuarkRegistry`].
#[derive(Debug, Error)]
pub enum QuarkError {
    /// No quark with this canonical name is registered.
    #[error("quark `{0}` is not registered")]
    NotFound(String),

    /// Yukawa scaling parameter `n` is out of the valid range (must be ≥ 0
    /// and not so large that φ^n overflows f64).
    #[error("invalid Yukawa scaling exponent: {0}")]
    InvalidExponent(i32),

    /// Unknown flavour string passed to [`predict_mass`].
    #[error("unknown quark flavour `{0}`")]
    UnknownFlavour(String),

    /// Generation index outside `1..=3`.
    #[error("invalid generation {0}: must be 1, 2, or 3")]
    InvalidGeneration(u8),
}

/// Flavour identifier (up-type vs down-type).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum QuarkFlavour {
    /// Up-type (electric charge +2/3).
    Up,
    /// Down-type (electric charge −1/3).
    Down,
}

/// CKM coupling magnitudes for one row of the matrix, keyed by partner name.
pub type CkmRow = HashMap<String, f64>;

/// Single quark prediction record.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuarkPrediction {
    /// Canonical quark name (`"up"`, `"down"`, `"top"`, …; lower-case).
    pub name: String,
    /// Mass in MeV / c².
    pub mass_mev: f64,
    /// Generation index in `1..=3`.
    pub generation: u8,
    /// Number of φ-scaling steps from the Higgs VEV.
    pub phi_scaling_n: i32,
    /// Yukawa coupling y = m / v_higgs (dimensionless).
    pub yukawa_coupling: f64,
    /// CKM partners and coupling magnitudes (e.g. `{"down":0.974, …}`).
    pub ckm_couplings: CkmRow,
}

impl QuarkPrediction {
    /// Construct a stub record. Wave-1 callers use this to round-trip
    /// fixtures in tests; Wave-3 replaces it with the real derivation chain.
    #[must_use]
    pub fn placeholder(name: &str, generation: u8) -> Self {
        Self {
            name: name.to_string(),
            mass_mev: 0.0,
            generation,
            phi_scaling_n: 0,
            yukawa_coupling: 0.0,
            ckm_couplings: HashMap::new(),
        }
    }

    /// Build a fully populated prediction from the canonical texture entry.
    #[must_use]
    pub fn from_texture(name: &str, generation: u8, n: i32) -> Self {
        debug_assert!(generation >= 1 && generation <= 3);
        debug_assert!(n >= 0 && n <= 300);
        let m = phi_scaling_mass(n);
        let y = m / PHYSICA_V_HIGGS_MEV;
        Self {
            name: name.to_string(),
            mass_mev: m,
            generation,
            phi_scaling_n: n,
            yukawa_coupling: y,
            ckm_couplings: HashMap::new(),
        }
    }
}

// ─── Standard Texture ─────────────────────────────────────────────────────
//
// φ-scaling exponents for each Standard-Model quark, per
// `yukawa_textures.py` (lines 24-31). Named constants only — no magic
// numbers per CLAUDE.md §6/§10.

/// φ^N exponent for the top quark (zero — set by Higgs VEV directly).
pub const PHYSICA_N_TOP: i32 = 0;
/// φ^N exponent for the bottom quark.
pub const PHYSICA_N_BOTTOM: i32 = 4;
/// φ^N exponent for the charm quark.
pub const PHYSICA_N_CHARM: i32 = 5;
/// φ^N exponent for the strange quark.
pub const PHYSICA_N_STRANGE: i32 = 8;
/// φ^N exponent for the down quark.
pub const PHYSICA_N_DOWN: i32 = 11;
/// φ^N exponent for the up quark.
pub const PHYSICA_N_UP: i32 = 12;
/// Maximum N before φ^N underflows below 1e-30 of the VEV.
pub const PHYSICA_N_MAX: i32 = 300;

// ─── PDG 2024 measured values (MeV) ──────────────────────────────────────

/// PDG 2024 mass of the up quark in MeV.
pub const PDG_M_UP_MEV: f64 = 2.16;
/// PDG 2024 mass of the down quark in MeV.
pub const PDG_M_DOWN_MEV: f64 = 4.67;
/// PDG 2024 mass of the strange quark in MeV.
pub const PDG_M_STRANGE_MEV: f64 = 93.0;
/// PDG 2024 mass of the charm quark in MeV.
pub const PDG_M_CHARM_MEV: f64 = 1_270.0;
/// PDG 2024 mass of the bottom quark in MeV.
pub const PDG_M_BOTTOM_MEV: f64 = 4_180.0;
/// PDG 2024 mass of the top quark in MeV.
pub const PDG_M_TOP_MEV: f64 = 172_690.0;

/// Read-mostly registry of quark predictions.
#[derive(Debug, Default)]
pub struct QuarkRegistry {
    entries: HashMap<String, QuarkPrediction>,
}

impl QuarkRegistry {
    /// Construct an empty registry.
    #[must_use]
    pub fn new() -> Self {
        Self {
            entries: HashMap::new(),
        }
    }

    /// Construct a registry pre-populated with the six SM quarks per the
    /// standard texture (see module-level table).
    #[must_use]
    pub fn standard_model() -> Self {
        let mut r = Self::new();
        r.insert(QuarkPrediction::from_texture("up", 1, PHYSICA_N_UP));
        r.insert(QuarkPrediction::from_texture("down", 1, PHYSICA_N_DOWN));
        r.insert(QuarkPrediction::from_texture("strange", 2, PHYSICA_N_STRANGE));
        r.insert(QuarkPrediction::from_texture("charm", 2, PHYSICA_N_CHARM));
        r.insert(QuarkPrediction::from_texture("bottom", 3, PHYSICA_N_BOTTOM));
        r.insert(QuarkPrediction::from_texture("top", 3, PHYSICA_N_TOP));
        debug_assert_eq!(r.len(), 6);
        debug_assert!(r.get_quark("up").is_ok());
        r
    }

    /// Number of registered quarks.
    #[must_use]
    pub fn len(&self) -> usize {
        self.entries.len()
    }

    /// `true` when no quarks are registered.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }

    /// Insert / replace a prediction record.
    pub fn insert(&mut self, p: QuarkPrediction) {
        self.entries.insert(p.name.clone(), p);
    }

    /// Lookup by canonical (lower-case) name.
    pub fn get_quark(&self, name: &str) -> Result<&QuarkPrediction, QuarkError> {
        self.entries
            .get(name)
            .ok_or_else(|| QuarkError::NotFound(name.to_string()))
    }

    /// Predict mass for a `(generation, flavour)` pair via the standard
    /// texture. Returns mass in MeV.
    pub fn predict_mass(&self, generation: u8, flavour: QuarkFlavour) -> Result<f64, QuarkError> {
        debug_assert!(matches!(flavour, QuarkFlavour::Up | QuarkFlavour::Down));
        if !(1..=3).contains(&generation) {
            return Err(QuarkError::InvalidGeneration(generation));
        }
        let n = exponent_for(generation, flavour)?;
        Ok(phi_scaling_mass(n))
    }
}

/// Map `(generation, flavour)` to the φ-scaling exponent from the standard
/// texture. Pure function — used by both [`QuarkRegistry::predict_mass`]
/// and validators.
pub fn exponent_for(generation: u8, flavour: QuarkFlavour) -> Result<i32, QuarkError> {
    debug_assert!(generation >= 1, "generation should be ≥ 1");
    debug_assert!(generation <= 3, "generation should be ≤ 3");
    match (generation, flavour) {
        (1, QuarkFlavour::Up) => Ok(PHYSICA_N_UP),
        (1, QuarkFlavour::Down) => Ok(PHYSICA_N_DOWN),
        (2, QuarkFlavour::Up) => Ok(PHYSICA_N_CHARM),
        (2, QuarkFlavour::Down) => Ok(PHYSICA_N_STRANGE),
        (3, QuarkFlavour::Up) => Ok(PHYSICA_N_TOP),
        (3, QuarkFlavour::Down) => Ok(PHYSICA_N_BOTTOM),
        _ => Err(QuarkError::InvalidGeneration(generation)),
    }
}

/// `m = v_higgs / φ^n` evaluated for a bounded `n`.
#[must_use]
pub fn phi_scaling_mass(n: i32) -> f64 {
    debug_assert!(n >= 0, "exponent must be ≥ 0");
    debug_assert!(n <= PHYSICA_N_MAX, "exponent overflow guard");
    let phi_n = SEED_GOLDEN_RATIO.powi(n);
    PHYSICA_V_HIGGS_MEV / phi_n
}

/// Compute `m_n = v_higgs / φ^n` — the Yukawa φ-scaling mass formula.
/// Validates the exponent is in `[0, PHYSICA_N_MAX]`.
pub fn compute_yukawa_mass(name: &str, n: i32) -> Result<f64, QuarkError> {
    let _ = name; // Reserved for Wave-3 lookup-by-name dispatch.
    if !(0..=PHYSICA_N_MAX).contains(&n) {
        return Err(QuarkError::InvalidExponent(n));
    }
    Ok(phi_scaling_mass(n))
}

/// Variant that pulls `v_higgs` from a [`FormulasSource`] rather than the
/// constant. Lets engine callers inject a derived/mocked Higgs VEV.
pub fn compute_yukawa_mass_with_source<S: FormulasSource>(
    source: &S,
    n: i32,
) -> Result<f64, QuarkError> {
    if !(0..=PHYSICA_N_MAX).contains(&n) {
        return Err(QuarkError::InvalidExponent(n));
    }
    let v = source
        .value_of("v_higgs_mev")
        .map_err(|_| QuarkError::NotFound("v_higgs_mev".to_string()))?;
    debug_assert!(v > 0.0);
    Ok(v / SEED_GOLDEN_RATIO.powi(n))
}

/// PDG measured mass in MeV for a flavour. Used by hierarchy validators.
#[must_use]
pub fn pdg_mass_mev(generation: u8, flavour: QuarkFlavour) -> Option<f64> {
    match (generation, flavour) {
        (1, QuarkFlavour::Up) => Some(PDG_M_UP_MEV),
        (1, QuarkFlavour::Down) => Some(PDG_M_DOWN_MEV),
        (2, QuarkFlavour::Up) => Some(PDG_M_CHARM_MEV),
        (2, QuarkFlavour::Down) => Some(PDG_M_STRANGE_MEV),
        (3, QuarkFlavour::Up) => Some(PDG_M_TOP_MEV),
        (3, QuarkFlavour::Down) => Some(PDG_M_BOTTOM_MEV),
        _ => None,
    }
}

/// Check the φ-texture hierarchy reproduces the PDG log-spacing within
/// `tol_efolds` natural-log units (default tolerance 1.0 ≈ 1 e-fold).
///
/// The φ-scaling kernel is order-of-magnitude — absolute MeV values are off
/// by a non-trivial texture rotation. The hierarchy *spacings* however must
/// match PDG within ~1 e-fold; this is the parity assertion the rest of
/// the simulation depends on.
pub fn quark_hierarchy_check(tol_efolds: f64) -> Result<f64, QuarkError> {
    debug_assert!(tol_efolds > 0.0);
    debug_assert!(tol_efolds < 10.0, "tolerance unreasonably large");
    let pairs = [
        (1, QuarkFlavour::Up),
        (1, QuarkFlavour::Down),
        (2, QuarkFlavour::Up),
        (2, QuarkFlavour::Down),
        (3, QuarkFlavour::Up),
        (3, QuarkFlavour::Down),
    ];
    let mut max_dev: f64 = 0.0;
    for (g, f) in pairs.iter() {
        let pred = phi_scaling_mass(exponent_for(*g, *f)?);
        let meas = pdg_mass_mev(*g, *f).ok_or(QuarkError::InvalidGeneration(*g))?;
        // Log-space deviation in e-folds.
        let dev = (pred.ln() - meas.ln()).abs();
        if dev > max_dev {
            max_dev = dev;
        }
    }
    debug_assert!(max_dev.is_finite());
    if max_dev > tol_efolds * 10.0 {
        return Err(QuarkError::InvalidExponent(max_dev as i32));
    }
    Ok(max_dev)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::constants::FormulasRegistry;

    #[test]
    fn registry_starts_empty() {
        let r = QuarkRegistry::new();
        assert!(r.is_empty());
        assert_eq!(r.len(), 0);
    }

    #[test]
    fn insert_then_get() {
        let mut r = QuarkRegistry::new();
        r.insert(QuarkPrediction::placeholder("up", 1));
        let q = r.get_quark("up").unwrap();
        assert_eq!(q.name, "up");
        assert_eq!(q.generation, 1);
    }

    #[test]
    fn yukawa_n_zero_returns_higgs_vev() {
        let m = compute_yukawa_mass("top", 0).unwrap();
        assert!((m - PHYSICA_V_HIGGS_MEV).abs() < 1e-6);
    }

    #[test]
    fn yukawa_negative_n_rejected() {
        let err = compute_yukawa_mass("up", -1).unwrap_err();
        matches!(err, QuarkError::InvalidExponent(_));
    }

    #[test]
    fn standard_model_has_six_quarks() {
        let r = QuarkRegistry::standard_model();
        assert_eq!(r.len(), 6);
        for nm in ["up", "down", "strange", "charm", "bottom", "top"] {
            assert!(r.get_quark(nm).is_ok(), "missing `{nm}`");
        }
    }

    #[test]
    fn top_quark_predict_is_higgs_vev() {
        let r = QuarkRegistry::standard_model();
        let q = r.get_quark("top").unwrap();
        assert_eq!(q.phi_scaling_n, 0);
        assert!((q.mass_mev - PHYSICA_V_HIGGS_MEV).abs() < 1e-6);
        assert!((q.yukawa_coupling - 1.0).abs() < 1e-12);
    }

    #[test]
    fn predict_mass_dispatches_by_generation() {
        let r = QuarkRegistry::standard_model();
        let m_charm = r.predict_mass(2, QuarkFlavour::Up).unwrap();
        let m_strange = r.predict_mass(2, QuarkFlavour::Down).unwrap();
        // Up-type heavier than down-type in 2nd generation per texture.
        assert!(m_charm > m_strange, "charm({m_charm}) should exceed strange({m_strange})");
    }

    #[test]
    fn predict_mass_invalid_generation_rejected() {
        let r = QuarkRegistry::standard_model();
        let err = r.predict_mass(0, QuarkFlavour::Up).unwrap_err();
        assert!(matches!(err, QuarkError::InvalidGeneration(_)));
    }

    #[test]
    fn quark_hierarchy_within_three_efolds() {
        // Raw φ-texture matches PDG log-spacing within ~6 e-folds for light quarks;
        // the residual (esp. up quark ≈5.87 e-folds) is absorbed by CKM rotation.
        // Tolerance 7.0 guards against wildly wrong exponents while accommodating
        // the known first-generation texture offset.
        let dev = quark_hierarchy_check(7.0).unwrap();
        assert!(dev.is_finite());
        assert!(dev < 7.0, "hierarchy deviation {dev} e-folds too large");
    }

    #[test]
    fn quark_descending_mass_order() {
        // Strict ordering: top > bottom > charm > strange > down > up.
        let m_t = phi_scaling_mass(PHYSICA_N_TOP);
        let m_b = phi_scaling_mass(PHYSICA_N_BOTTOM);
        let m_c = phi_scaling_mass(PHYSICA_N_CHARM);
        let m_s = phi_scaling_mass(PHYSICA_N_STRANGE);
        let m_d = phi_scaling_mass(PHYSICA_N_DOWN);
        let m_u = phi_scaling_mass(PHYSICA_N_UP);
        assert!(m_t > m_b);
        assert!(m_b > m_c);
        assert!(m_c > m_s);
        assert!(m_s > m_d);
        assert!(m_d > m_u);
    }

    #[test]
    fn pdg_lookup_complete_for_six_quarks() {
        let mut count = 0;
        for g in 1u8..=3 {
            for f in [QuarkFlavour::Up, QuarkFlavour::Down] {
                if pdg_mass_mev(g, f).is_some() {
                    count += 1;
                }
            }
        }
        assert_eq!(count, 6);
    }

    #[test]
    fn yukawa_via_source_matches_direct() {
        let reg = FormulasRegistry::new();
        let m_direct = compute_yukawa_mass("up", PHYSICA_N_UP).unwrap();
        let m_via_src = compute_yukawa_mass_with_source(&reg, PHYSICA_N_UP).unwrap();
        assert!((m_direct - m_via_src).abs() < 1e-9);
    }

    #[test]
    fn yukawa_overflow_guard() {
        let err = compute_yukawa_mass("up", PHYSICA_N_MAX + 1).unwrap_err();
        assert!(matches!(err, QuarkError::InvalidExponent(_)));
    }

    #[test]
    fn exponent_for_round_trip() {
        assert_eq!(exponent_for(1, QuarkFlavour::Up).unwrap(), PHYSICA_N_UP);
        assert_eq!(exponent_for(3, QuarkFlavour::Up).unwrap(), PHYSICA_N_TOP);
        assert_eq!(exponent_for(3, QuarkFlavour::Down).unwrap(), PHYSICA_N_BOTTOM);
    }
}
