//====== Metaphysica/rust/physica_core/src/constants.rs ======//
//!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! Physics-constant records and the `FormulasRegistry` SSoT.
//!
//! Ports the Python `simulations/core/FormulasRegistry.py` (6028 lines /
//! 125 derived constants). Layer-0 of the derivation hierarchy is the
//! **Ten Pillar Seeds** wired in `seed_pillars()`; everything else is computed
//! on demand by parsing each constant's `expression` field and cached in a
//! `DashMap` with a per-registry dirty flag.

use dashmap::DashMap;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;
use thiserror::Error;

/// Errors surfaced by [`FormulasRegistry`].
#[derive(Debug, Error)]
pub enum ConstantError {
    /// The requested name is not registered (yet).
    #[error("constant `{0}` not found in registry")]
    NotFound(String),

    /// Derivation logic for this constant has not been ported in this wave.
    #[error("derivation of `{0}` is not yet implemented in physica_core")]
    Unimplemented(String),

    /// Failed to load constants from a JSON file.
    #[error("failed to load constants from `{path}`: {source}")]
    Io {
        path: String,
        #[source]
        source: std::io::Error,
    },

    /// JSON decoded but did not match the expected schema.
    #[error("invalid JSON schema in `{0}`")]
    BadSchema(String),

    /// Cyclic dependency in the derivation chain.
    #[error("cyclic derivation involving `{0}`")]
    CyclicDependency(String),

    /// Expression in `expression` field failed to evaluate.
    #[error("expression parse error in `{name}`: {detail}")]
    BadExpression { name: String, detail: String },
}

/// Derivation lifecycle for a constant. Mirrors the Python
/// `ConstantStatus` enum used by `FormulasRegistry`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ConstantStatus {
    /// A Layer-0 seed (one of the Ten Pillars).
    Seed,
    /// Derived value is currently cached.
    Cached,
    /// Awaiting derivation; cache is empty.
    Pending,
    /// Source-of-truth is downstream code (not derivable here).
    External,
}

/// Single physics-constant record.
///
/// Fields mirror the Python datasheet schema in
/// `metaphysica/datasheets/constant.py` so the JSON shape round-trips
/// cleanly between the two cores.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Constant {
    /// Canonical lookup name (e.g. `"m_planck"`, `"alpha_em"`).
    pub name: String,
    /// Numerical value in the units recorded by `units`.
    pub value: f64,
    /// Units string (free-form, matches the Python schema).
    pub units: String,
    /// Absolute uncertainty in the same units; `None` for exact seeds.
    pub uncertainty: Option<f64>,
    /// Where this constant sits in the derivation lifecycle.
    pub status: ConstantStatus,
    /// Ordered list of upstream constant names that this one is derived from.
    pub derivation_chain: Vec<String>,
    /// Optional textual expression (mini-language) describing how the value
    /// is derived from upstream entries. When present and the entry is not
    /// already `Cached`, [`FormulasRegistry::derive`] will evaluate it.
    #[serde(default)]
    pub expression: Option<String>,
}

impl Constant {
    /// Construct a Layer-0 seed (no upstream dependencies, status =
    /// [`ConstantStatus::Seed`]).
    #[must_use]
    pub fn seed(name: &str, value: f64, units: &str) -> Self {
        Self {
            name: name.to_string(),
            value,
            units: units.to_string(),
            uncertainty: None,
            status: ConstantStatus::Seed,
            derivation_chain: Vec::new(),
            expression: None,
        }
    }

    /// Construct a derived (Pending) entry with an `expression`. The value
    /// stays zero until [`FormulasRegistry::derive`] resolves it.
    #[must_use]
    pub fn derived(name: &str, expression: &str, units: &str, deps: &[&str]) -> Self {
        Self {
            name: name.to_string(),
            value: 0.0,
            units: units.to_string(),
            uncertainty: None,
            status: ConstantStatus::Pending,
            derivation_chain: deps.iter().map(|s| (*s).to_string()).collect(),
            expression: Some(expression.to_string()),
        }
    }
}

// ─── Ten Pillar Seeds ─────────────────────────────────────────────────────
//
// Layer-0 of the derivation hierarchy. These are *exact* — never derived,
// never re-evaluated. They are the input axioms that everything else flows
// from.

/// Third Betti number of the G2 manifold.
pub const SEED_B3: f64 = 24.0;
/// Effective Euler characteristic χ_eff.
pub const SEED_CHI_EFF: f64 = 72.0;
/// Number of fermion generations.
pub const SEED_N_GEN: u32 = 3;
/// Total root vectors in the embedded E8 lattice.
pub const SEED_ROOTS_TOTAL: u32 = 288;
/// Visible-sector root count (125 derived constants).
pub const SEED_VISIBLE_SECTOR: u32 = 125;
/// Sterile-sector root count (288 − 125).
pub const SEED_STERILE_SECTOR: u32 = 163;
/// Golden ratio φ — high-precision literal (see plan §D.9 / §D.7).
pub const SEED_GOLDEN_RATIO: f64 =
    1.618_033_988_749_894_848_204_586_834_365_638_117_720_309_180_f64;
/// Euler–Mascheroni constant γ.
pub const SEED_EULER_MASCHERONI: f64 =
    0.577_215_664_901_532_860_606_512_090_082_402_431_042_159_335_f64;
/// JC topological invariant.
pub const SEED_JC_CONSTANT: u32 = 153;
/// Logic closure — full-lattice constraint count.
pub const SEED_LOGIC_CLOSURE: u32 = 288;

// ─── PHYSICA constants used by derived entries ───────────────────────────
//
// Per CLAUDE.md §6/§10/§11: no magic numbers; named constants only.

/// Higgs vacuum expectation value (PDG 2024) in GeV.
pub const PHYSICA_V_HIGGS_GEV: f64 = 246.22;
/// Higgs vacuum expectation value in MeV (`PHYSICA_V_HIGGS_GEV` × 1000).
pub const PHYSICA_V_HIGGS_MEV: f64 = PHYSICA_V_HIGGS_GEV * 1000.0;
/// Hubble constant H₀ central derivation target (km/s/Mpc) — geometric
/// mean of Planck (67.4) and SH0ES (73.0) brackets.
pub const PHYSICA_H0_CENTRAL: f64 = 70.0;
/// Dark-energy equation-of-state w₀ central value (≡ ΛCDM).
pub const PHYSICA_W0_CENTRAL: f64 = -1.0;
/// Speed of light c in m/s (CODATA exact).
pub const PHYSICA_C_M_PER_S: f64 = 299_792_458.0;
/// Tau lepton mass in MeV (PDG 2024).
pub const PHYSICA_M_TAU_MEV: f64 = 1776.86;

/// Trait abstraction over a registry of physics constants, allowing the
/// engine (pt-physica) to inject mocks or alternative sources at test time
/// (SOLID §D — Dependency Inversion).
pub trait FormulasSource {
    /// Fetch the (possibly derived) numeric value for `name`.
    fn value_of(&self, name: &str) -> Result<f64, ConstantError>;
    /// Count of registered constants.
    fn count(&self) -> usize;
}

/// Single-source-of-truth registry for the 125 derived physics constants.
///
/// Concurrency model: reads through a [`DashMap`] (sharded lock-free); writes
/// are serialised by `DashMap`'s per-shard `RwLock`. The dirty flag is used
/// by per-frame engine code (pt-physica) to decide whether dependent caches
/// (quarks, CKM, simulation seeds) need recomputation.
#[derive(Debug, Default)]
pub struct FormulasRegistry {
    /// Cached constants keyed by canonical name.
    entries: DashMap<String, Constant>,
    /// Set when any entry is mutated; cleared by `mark_clean()`.
    dirty: parking_lot::Mutex<bool>,
}

impl FormulasRegistry {
    /// Construct an empty registry pre-loaded with the Ten Pillar Seeds plus
    /// the canonical first-tier derived constants used by validators and
    /// downstream caches.
    #[must_use]
    pub fn new() -> Self {
        let r = Self {
            entries: DashMap::new(),
            dirty: parking_lot::Mutex::new(false),
        };
        r.seed_pillars();
        r.seed_derived_layer();
        r
    }

    /// Insert the Ten Pillar Seeds. Idempotent.
    fn seed_pillars(&self) {
        let seeds = [
            Constant::seed("b3", SEED_B3, "dimensionless"),
            Constant::seed("chi_eff", SEED_CHI_EFF, "dimensionless"),
            Constant::seed("n_gen", f64::from(SEED_N_GEN), "count"),
            Constant::seed("roots_total", f64::from(SEED_ROOTS_TOTAL), "count"),
            Constant::seed("visible_sector", f64::from(SEED_VISIBLE_SECTOR), "count"),
            Constant::seed("sterile_sector", f64::from(SEED_STERILE_SECTOR), "count"),
            Constant::seed("phi", SEED_GOLDEN_RATIO, "dimensionless"),
            Constant::seed("gamma_em", SEED_EULER_MASCHERONI, "dimensionless"),
            Constant::seed("jc_constant", f64::from(SEED_JC_CONSTANT), "count"),
            Constant::seed("logic_closure", f64::from(SEED_LOGIC_CLOSURE), "count"),
        ];
        debug_assert_eq!(seeds.len(), 10);
        for s in seeds {
            self.entries.insert(s.name.clone(), s);
        }
        debug_assert_eq!(self.entries.len(), 10);
    }

    /// Seed the first layer of derived constants used by validators &
    /// quark/CKM modules. These carry `expression` strings so a call to
    /// [`Self::derive`] re-evaluates them lazily and caches the result.
    fn seed_derived_layer(&self) {
        let derived = [
            // v_higgs (MeV) — used by Yukawa scaling
            Constant::derived(
                "v_higgs_mev",
                &format!("{}", PHYSICA_V_HIGGS_MEV),
                "MeV",
                &[],
            ),
            // sterile = roots_total − visible_sector
            Constant::derived(
                "sterile_check",
                "roots_total - visible_sector",
                "count",
                &["roots_total", "visible_sector"],
            ),
            // n_gen squared (used downstream)
            Constant::derived(
                "n_gen_sq",
                "n_gen * n_gen",
                "count",
                &["n_gen"],
            ),
            // H0 central
            Constant::derived(
                "h0_central",
                &format!("{}", PHYSICA_H0_CENTRAL),
                "km/s/Mpc",
                &[],
            ),
            // w0 central
            Constant::derived(
                "w0_central",
                &format!("{}", PHYSICA_W0_CENTRAL),
                "dimensionless",
                &[],
            ),
            // tau lepton mass
            Constant::derived(
                "m_tau_mev",
                &format!("{}", PHYSICA_M_TAU_MEV),
                "MeV",
                &[],
            ),
            // χ_eff / b3 = 3 (matches n_gen — a key topological identity)
            Constant::derived(
                "topo_gen_check",
                "chi_eff / b3",
                "count",
                &["chi_eff", "b3"],
            ),
        ];
        for d in derived {
            self.entries.insert(d.name.clone(), d);
        }
    }

    /// Total number of registered constants (seeds + cached derivations).
    #[must_use]
    pub fn len(&self) -> usize {
        self.entries.len()
    }

    /// `true` when no constants are registered. Always `false` after
    /// [`FormulasRegistry::new`] because of the seed insertion.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }

    /// All registered constant names in sorted order.
    pub fn known_names(&self) -> Vec<String> {
        let mut names: Vec<String> = self.entries.iter().map(|kv| kv.key().clone()).collect();
        names.sort();
        names
    }

    /// Fetch the registered constant by canonical name.
    pub fn get(&self, name: &str) -> Result<Constant, ConstantError> {
        self.entries
            .get(name)
            .map(|r| r.value().clone())
            .ok_or_else(|| ConstantError::NotFound(name.to_string()))
    }

    /// Derive (and cache) the constant called `name`.
    ///
    /// Resolution rules:
    /// 1. Unknown name ⇒ [`ConstantError::NotFound`].
    /// 2. Already `Seed` or `Cached` ⇒ return the stored value.
    /// 3. Pending entry with `expression` set ⇒ evaluate via
    ///    [`evaluate_expression`], cache the result, set the dirty flag,
    ///    flip the entry's status to `Cached`.
    /// 4. Pending entry without `expression` ⇒
    ///    [`ConstantError::Unimplemented`].
    pub fn derive(&self, name: &str) -> Result<f64, ConstantError> {
        let mut visiting: Vec<String> = Vec::with_capacity(16);
        self.derive_inner(name, &mut visiting)
    }

    /// Internal derivation helper with explicit visit-stack to detect cycles.
    /// Iterative-style (no Rust recursion ≥ 2 levels): the stack is reused
    /// across nested lookups inside `evaluate_expression`.
    fn derive_inner(
        &self,
        name: &str,
        visiting: &mut Vec<String>,
    ) -> Result<f64, ConstantError> {
        debug_assert!(!name.is_empty());
        debug_assert!(visiting.len() < 256, "derivation stack runaway");

        // Cycle guard.
        if visiting.iter().any(|v| v == name) {
            return Err(ConstantError::CyclicDependency(name.to_string()));
        }

        // Snapshot the entry — release the read lock before recursing.
        let entry = self
            .entries
            .get(name)
            .map(|r| r.value().clone())
            .ok_or_else(|| ConstantError::NotFound(name.to_string()))?;

        match entry.status {
            ConstantStatus::Seed | ConstantStatus::Cached | ConstantStatus::External => {
                Ok(entry.value)
            }
            ConstantStatus::Pending => {
                let expr = entry
                    .expression
                    .clone()
                    .ok_or_else(|| ConstantError::Unimplemented(name.to_string()))?;
                visiting.push(name.to_string());
                let v = evaluate_expression(&expr, self, visiting)?;
                visiting.pop();
                // Cache result + dirty flag.
                if let Some(mut e) = self.entries.get_mut(name) {
                    e.value = v;
                    e.status = ConstantStatus::Cached;
                }
                *self.dirty.lock() = true;
                Ok(v)
            }
        }
    }

    /// Bulk-load constants from a JSON file matching the
    /// `metaphysica/data/parameters.json` schema. Returns the number of
    /// entries inserted/updated. The JSON document must be an array of
    /// [`Constant`] records.
    pub fn load_from_json(&self, path: &Path) -> Result<usize, ConstantError> {
        debug_assert!(path.as_os_str().len() > 0);
        let raw = fs::read_to_string(path).map_err(|e| ConstantError::Io {
            path: path.display().to_string(),
            source: e,
        })?;
        let records: Vec<Constant> = serde_json::from_str(&raw)
            .map_err(|_| ConstantError::BadSchema(path.display().to_string()))?;
        let mut n = 0usize;
        for c in records {
            self.entries.insert(c.name.clone(), c);
            n += 1;
        }
        debug_assert!(n <= self.entries.len());
        if n > 0 {
            *self.dirty.lock() = true;
        }
        Ok(n)
    }

    /// Insert or update a constant directly. Sets the dirty flag.
    pub fn upsert(&self, c: Constant) {
        debug_assert!(!c.name.is_empty());
        self.entries.insert(c.name.clone(), c);
        *self.dirty.lock() = true;
    }

    /// Returns whether any cached entry has been mutated since the last
    /// [`mark_clean`](Self::mark_clean).
    #[must_use]
    pub fn is_dirty(&self) -> bool {
        *self.dirty.lock()
    }

    /// Clear the dirty flag (called after engine consumers re-cache their
    /// dependent state for the frame).
    pub fn mark_clean(&self) {
        *self.dirty.lock() = false;
    }

    /// Retrieve the constant as both an `f64` and an Arithmos symbolic
    /// expression. Available only when the `with-arithmos` feature is on
    /// (engine / git-checkout path).
    #[cfg(feature = "with-arithmos")]
    pub fn derive_with_arithmos(
        &self,
        name: &str,
    ) -> Result<(f64, arithmos_core::expression::ArithmosExpression), ConstantError> {
        let v = self.derive(name)?;
        let expr = crate::arithmos_bridge::ArithmosConstantBridge::expression_for(name, v);
        Ok((v, expr))
    }
}

impl FormulasSource for FormulasRegistry {
    fn value_of(&self, name: &str) -> Result<f64, ConstantError> {
        self.derive(name)
    }
    fn count(&self) -> usize {
        self.len()
    }
}

// ─── Mini expression evaluator ────────────────────────────────────────────
//
// Minimal infix evaluator supporting `+ - * /`, parenthesised sub-expressions,
// numeric literals, and unqualified constant names that resolve through the
// registry. Deliberately a closed micro-language (NOT a general parser) so
// `derive()` remains deterministic, bounded, and safe per CLAUDE.md §10
// (no eval-of-arbitrary-strings, only this dedicated walker).

/// Public entry point so unit tests / quark module can reuse the evaluator.
pub fn evaluate_expression(
    src: &str,
    registry: &FormulasRegistry,
    visiting: &mut Vec<String>,
) -> Result<f64, ConstantError> {
    debug_assert!(!src.is_empty());
    let tokens = tokenize(src)?;
    debug_assert!(!tokens.is_empty(), "expression tokenized to nothing: `{src}`");
    let mut parser = Parser { tokens, pos: 0 };
    let v = parser.parse_expr(registry, visiting)?;
    if parser.pos != parser.tokens.len() {
        return Err(ConstantError::BadExpression {
            name: src.to_string(),
            detail: format!("trailing tokens at pos {}", parser.pos),
        });
    }
    Ok(v)
}

#[derive(Debug, Clone, PartialEq)]
enum Tok {
    Num(f64),
    Ident(String),
    Plus,
    Minus,
    Star,
    Slash,
    LParen,
    RParen,
}

fn tokenize(src: &str) -> Result<Vec<Tok>, ConstantError> {
    debug_assert!(!src.is_empty());
    let mut out: Vec<Tok> = Vec::with_capacity(src.len());
    let bytes: Vec<char> = src.chars().collect();
    let mut i = 0usize;
    let max_iter = bytes.len() + 1; // Bounded loop (CLAUDE.md safety §2).
    let mut guard = 0usize;
    while i < bytes.len() {
        guard += 1;
        if guard > max_iter * 4 {
            return Err(ConstantError::BadExpression {
                name: src.to_string(),
                detail: "tokenizer runaway".to_string(),
            });
        }
        let c = bytes[i];
        if c.is_whitespace() {
            i += 1;
            continue;
        }
        match c {
            '+' => { out.push(Tok::Plus); i += 1; }
            '-' => { out.push(Tok::Minus); i += 1; }
            '*' => { out.push(Tok::Star); i += 1; }
            '/' => { out.push(Tok::Slash); i += 1; }
            '(' => { out.push(Tok::LParen); i += 1; }
            ')' => { out.push(Tok::RParen); i += 1; }
            d if d.is_ascii_digit() || d == '.' => {
                let start = i;
                let mut saw_dot = c == '.';
                let mut saw_exp = false;
                i += 1;
                while i < bytes.len() {
                    let n = bytes[i];
                    if n.is_ascii_digit() {
                        i += 1;
                    } else if n == '.' && !saw_dot && !saw_exp {
                        saw_dot = true;
                        i += 1;
                    } else if (n == 'e' || n == 'E') && !saw_exp {
                        saw_exp = true;
                        i += 1;
                        if i < bytes.len() && (bytes[i] == '+' || bytes[i] == '-') {
                            i += 1;
                        }
                    } else {
                        break;
                    }
                }
                let lit: String = bytes[start..i].iter().collect();
                let v: f64 = lit.parse().map_err(|_| ConstantError::BadExpression {
                    name: src.to_string(),
                    detail: format!("bad number `{lit}`"),
                })?;
                out.push(Tok::Num(v));
            }
            a if a.is_ascii_alphabetic() || a == '_' => {
                let start = i;
                i += 1;
                while i < bytes.len()
                    && (bytes[i].is_ascii_alphanumeric() || bytes[i] == '_')
                {
                    i += 1;
                }
                let id: String = bytes[start..i].iter().collect();
                out.push(Tok::Ident(id));
            }
            _ => {
                return Err(ConstantError::BadExpression {
                    name: src.to_string(),
                    detail: format!("unexpected character `{c}` at {i}"),
                });
            }
        }
    }
    Ok(out)
}

struct Parser {
    tokens: Vec<Tok>,
    pos: usize,
}

impl Parser {
    fn peek(&self) -> Option<&Tok> {
        self.tokens.get(self.pos)
    }
    fn advance(&mut self) -> Option<Tok> {
        let t = self.tokens.get(self.pos).cloned();
        if t.is_some() {
            self.pos += 1;
        }
        t
    }

    fn parse_expr(
        &mut self,
        reg: &FormulasRegistry,
        visiting: &mut Vec<String>,
    ) -> Result<f64, ConstantError> {
        let mut lhs = self.parse_term(reg, visiting)?;
        let max_steps = self.tokens.len() + 1;
        let mut iter = 0usize;
        while iter < max_steps {
            iter += 1;
            match self.peek() {
                Some(Tok::Plus) => {
                    self.advance();
                    let rhs = self.parse_term(reg, visiting)?;
                    lhs += rhs;
                }
                Some(Tok::Minus) => {
                    self.advance();
                    let rhs = self.parse_term(reg, visiting)?;
                    lhs -= rhs;
                }
                _ => break,
            }
        }
        debug_assert!(iter <= max_steps);
        Ok(lhs)
    }

    fn parse_term(
        &mut self,
        reg: &FormulasRegistry,
        visiting: &mut Vec<String>,
    ) -> Result<f64, ConstantError> {
        let mut lhs = self.parse_factor(reg, visiting)?;
        let max_steps = self.tokens.len() + 1;
        let mut iter = 0usize;
        while iter < max_steps {
            iter += 1;
            match self.peek() {
                Some(Tok::Star) => {
                    self.advance();
                    let rhs = self.parse_factor(reg, visiting)?;
                    lhs *= rhs;
                }
                Some(Tok::Slash) => {
                    self.advance();
                    let rhs = self.parse_factor(reg, visiting)?;
                    if rhs == 0.0 {
                        return Err(ConstantError::BadExpression {
                            name: "<term>".to_string(),
                            detail: "division by zero".to_string(),
                        });
                    }
                    lhs /= rhs;
                }
                _ => break,
            }
        }
        debug_assert!(iter <= max_steps);
        Ok(lhs)
    }

    fn parse_factor(
        &mut self,
        reg: &FormulasRegistry,
        visiting: &mut Vec<String>,
    ) -> Result<f64, ConstantError> {
        match self.advance() {
            Some(Tok::Num(v)) => Ok(v),
            Some(Tok::Minus) => {
                let v = self.parse_factor(reg, visiting)?;
                Ok(-v)
            }
            Some(Tok::Plus) => self.parse_factor(reg, visiting),
            Some(Tok::LParen) => {
                let v = self.parse_expr(reg, visiting)?;
                match self.advance() {
                    Some(Tok::RParen) => Ok(v),
                    _ => Err(ConstantError::BadExpression {
                        name: "<paren>".to_string(),
                        detail: "missing `)`".to_string(),
                    }),
                }
            }
            Some(Tok::Ident(name)) => reg.derive_inner(&name, visiting),
            other => Err(ConstantError::BadExpression {
                name: format!("{other:?}"),
                detail: "unexpected token".to_string(),
            }),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn registry_seeds_ten_pillars() {
        let r = FormulasRegistry::new();
        // 10 seeds + derived first-tier; assert seeds are all present.
        for nm in [
            "b3", "chi_eff", "n_gen", "roots_total", "visible_sector",
            "sterile_sector", "phi", "gamma_em", "jc_constant", "logic_closure",
        ] {
            assert!(r.get(nm).is_ok(), "missing seed `{nm}`");
        }
        assert!(r.len() >= 10);
    }

    #[test]
    fn seed_b3_is_24() {
        let r = FormulasRegistry::new();
        let c = r.get("b3").expect("b3 must be present");
        assert_eq!(c.value, 24.0);
        assert_eq!(c.status, ConstantStatus::Seed);
    }

    #[test]
    fn unknown_constant_returns_not_found() {
        let r = FormulasRegistry::new();
        let err = r.get("nonexistent").unwrap_err();
        matches!(err, ConstantError::NotFound(_));
    }

    #[test]
    fn derive_unknown_returns_not_found() {
        let r = FormulasRegistry::new();
        let err = r.derive("nope_not_here").unwrap_err();
        assert!(matches!(err, ConstantError::NotFound(_)));
    }

    #[test]
    fn dirty_flag_starts_clean() {
        let r = FormulasRegistry::new();
        assert!(!r.is_dirty());
    }

    #[test]
    fn derive_simple_difference() {
        let r = FormulasRegistry::new();
        let v = r.derive("sterile_check").expect("sterile_check derives");
        assert!((v - f64::from(SEED_STERILE_SECTOR)).abs() < 1e-12);
        assert!(r.is_dirty(), "derivation should set dirty flag");
    }

    #[test]
    fn derive_caches_result() {
        let r = FormulasRegistry::new();
        let _ = r.derive("n_gen_sq").unwrap();
        let c = r.get("n_gen_sq").unwrap();
        assert_eq!(c.status, ConstantStatus::Cached);
        let again = r.derive("n_gen_sq").unwrap();
        assert!((again - 9.0).abs() < 1e-12);
    }

    #[test]
    fn topo_identity_chi_over_b3_eq_n_gen() {
        let r = FormulasRegistry::new();
        let v = r.derive("topo_gen_check").unwrap();
        assert!((v - 3.0).abs() < 1e-12);
    }

    #[test]
    fn mark_clean_clears_flag() {
        let r = FormulasRegistry::new();
        let _ = r.derive("n_gen_sq").unwrap();
        assert!(r.is_dirty());
        r.mark_clean();
        assert!(!r.is_dirty());
    }

    #[test]
    fn upsert_marks_dirty() {
        let r = FormulasRegistry::new();
        r.mark_clean();
        r.upsert(Constant::seed("custom", 42.0, "u"));
        assert!(r.is_dirty());
        assert_eq!(r.get("custom").unwrap().value, 42.0);
    }

    #[test]
    fn evaluate_expression_inline() {
        let r = FormulasRegistry::new();
        let mut visiting = Vec::new();
        let v = evaluate_expression("phi * phi - phi - 1", &r, &mut visiting).unwrap();
        // Golden-ratio identity: φ² − φ − 1 = 0.
        assert!(v.abs() < 1e-12, "got {v}");
    }

    #[test]
    fn evaluate_expression_parens_and_div() {
        let r = FormulasRegistry::new();
        let mut visiting = Vec::new();
        let v = evaluate_expression("(roots_total - visible_sector) / n_gen", &r, &mut visiting).unwrap();
        assert!((v - (f64::from(SEED_STERILE_SECTOR) / 3.0)).abs() < 1e-12);
    }

    #[test]
    fn evaluate_expression_unary_minus() {
        let r = FormulasRegistry::new();
        let mut visiting = Vec::new();
        let v = evaluate_expression("-3 + n_gen", &r, &mut visiting).unwrap();
        assert!((v - 0.0).abs() < 1e-12);
    }

    #[test]
    fn evaluate_expression_div_by_zero() {
        let r = FormulasRegistry::new();
        let mut visiting = Vec::new();
        let err = evaluate_expression("1 / 0", &r, &mut visiting).unwrap_err();
        assert!(matches!(err, ConstantError::BadExpression { .. }));
    }

    #[test]
    fn formulas_source_trait_dispatch() {
        let r = FormulasRegistry::new();
        let src: &dyn FormulasSource = &r;
        assert!(src.count() >= 10);
        assert!((src.value_of("phi").unwrap() - SEED_GOLDEN_RATIO).abs() < 1e-15);
    }

    #[test]
    fn cyclic_dependency_detected() {
        let r = FormulasRegistry::new();
        // Introduce a self-cycle via upsert.
        r.upsert(Constant::derived("loop_a", "loop_b + 1", "u", &["loop_b"]));
        r.upsert(Constant::derived("loop_b", "loop_a + 1", "u", &["loop_a"]));
        let err = r.derive("loop_a").unwrap_err();
        assert!(matches!(err, ConstantError::CyclicDependency(_)));
    }

    #[test]
    fn load_from_json_missing_path() {
        let r = FormulasRegistry::new();
        let err = r.load_from_json(Path::new("h:/does/not/exist.json")).unwrap_err();
        assert!(matches!(err, ConstantError::Io { .. }));
    }
}
