//====== Metaphysica/rust/physica_core/src/arithmos_bridge.rs ======//
//!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! Arithmos symbolic-expression bridge. **NOT COMPILED.**
//!
//! This file is not a module of `physica_core` and never has been. `lib.rs`
//! declared it behind `#[cfg(feature = "with-arithmos")]`, but that feature
//! was never added to `Cargo.toml`, so the cfg was permanently false: the
//! code below -- including its two unit tests -- has never been built by any
//! `cargo` invocation, not even `cargo check --all-features`.
//!
//! It cannot simply be switched on. It imports `arithmos_core`, which is not
//! a declared dependency, and the upstream crate has since been renamed to
//! `arithma_core` (live at the sibling Arithma repository). Reconciling that
//! spans several repositories and is deliberately out of scope here. The file
//! is kept as the record of intent; the module declaration was removed so the
//! crate stops advertising a capability it does not have.
//!
//! Originally gated behind the `with-arithmos` feature. **This is the engine path
//! ONLY** — it is *never* part of the metaphysica PyPI wheel because the
//! Arithmos dependency is wired by relative `path =` (git-submodule layout)
//! and would not resolve from a published Cargo registry build.
//!
//! Plan §J motivates the bridge: when the engine consumes physica_core via
//! the workspace, `FormulasRegistry::derive_with_arithmos(name)` returns
//! both an `f64` value and a parallel `ArithmosExpression` so the engine can
//! re-evaluate, simplify or differentiate constants symbolically without
//! losing precision.
//!
//! Wave-1 status: scaffold only. The expression returned is a named
//! variable (`ArithmosExpression::var(name)`) — i.e. an opaque symbol that
//! preserves the constant's identity for later substitution. Wave-2 will
//! upgrade this to a full derivation tree once
//! `ArithmosExpression::from_f64` is fleshed out upstream.

#![cfg(feature = "with-arithmos")]

use arithmos_core::expression::ArithmosExpression;

/// Bridge that converts physica_core records into Arithmos expressions.
///
/// Stateless utility type — all methods are static. Kept as a struct (vs.
/// free functions) so the engine can extend it with state-bearing helpers
/// later without breaking the public surface.
#[derive(Debug, Default, Clone, Copy)]
pub struct ArithmosConstantBridge;

impl ArithmosConstantBridge {
    /// Build an `ArithmosExpression` representing the constant `name` whose
    /// numeric value is `_value`.
    ///
    /// Wave-1 returns a named variable that downstream code can resolve via
    /// the Arithmos `SYMBOL_REGISTRY`. The numeric value is accepted (and
    /// kept in the call signature) so the future Wave-2 implementation can
    /// emit a `Number` literal alongside the symbolic name.
    #[must_use]
    pub fn expression_for(name: &str, _value: f64) -> ArithmosExpression {
        ArithmosExpression::var(name)
    }

    /// Convenience: convert a `&Constant` directly.
    #[must_use]
    pub fn from_constant(c: &crate::constants::Constant) -> ArithmosExpression {
        Self::expression_for(&c.name, c.value)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::constants::Constant;

    #[test]
    fn expression_for_returns_variable() {
        let e = ArithmosConstantBridge::expression_for("alpha_em", 0.0072973525693);
        // Round-trip: `ArithmosExpression::Variable` matches by debug-string.
        let dbg = format!("{:?}", e);
        assert!(dbg.contains("alpha_em"));
    }

    #[test]
    fn from_constant_uses_name() {
        let c = Constant::seed("phi", crate::constants::SEED_GOLDEN_RATIO, "dimensionless");
        let e = ArithmosConstantBridge::from_constant(&c);
        let dbg = format!("{:?}", e);
        assert!(dbg.contains("phi"));
    }
}
