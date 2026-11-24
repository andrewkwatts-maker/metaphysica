//! Unit tests for the `pyfacade` module.
//!
//! These run under `cargo test --features python`, which links libpython
//! because `extension-module` is a separate feature. Fold the two together
//! and this whole module silently stops being executed anywhere.

use crate::constants::{ConstantStatus, FormulasRegistry};

#[test]
fn registry_round_trip() {
    let r = FormulasRegistry::new();
    assert!(r.get("b3").is_ok());
}

/// The regression this facade was rewritten for: every registry entry must
/// resolve to its derived value, not to the 0.0 placeholder.
#[test]
fn every_registry_constant_derives_to_a_real_value() {
    let r = FormulasRegistry::new();
    let names = r.known_names();
    assert!(names.len() >= 17, "registry shrank: {} names", names.len());
    for name in names.iter().take(super::MAX_SEQUENCE_LEN) {
        let v = r
            .derive(name)
            .unwrap_or_else(|e| panic!("`{name}` failed to derive: {e}"));
        assert!(v.is_finite(), "`{name}` derived to {v}");
        let stored = r.get(name).expect("entry vanished after derive");
        assert_ne!(
            stored.status,
            ConstantStatus::Pending,
            "`{name}` is still Pending after derive()"
        );
        assert_eq!(stored.value, v, "cached value disagrees with derive()");
    }
}

#[test]
fn known_derived_values_are_correct() {
    let r = FormulasRegistry::new();
    assert_eq!(r.derive("n_gen_sq").unwrap(), 9.0);
    assert_eq!(r.derive("sterile_check").unwrap(), 163.0);
    assert_eq!(r.derive("topo_gen_check").unwrap(), 3.0);
    assert_eq!(r.derive("h0_central").unwrap(), 70.0);
    assert_eq!(r.derive("w0_central").unwrap(), -1.0);
}

#[test]
fn unknown_constant_is_an_error() {
    let r = FormulasRegistry::new();
    assert!(r.derive("no_such_constant").is_err());
}

/// The constant relation this used to assert is now checked at compile
/// time (`const _: () = assert!(...)` above), so the runtime test would be
/// vacuous. What is worth testing is that the guard actually refuses.
#[test]
fn the_sequence_guard_refuses_an_oversized_request() {
    assert!(super::check_sequence_len(super::MAX_SEQUENCE_LEN).is_ok());
    assert!(super::check_sequence_len(super::MAX_SEQUENCE_LEN + 1).is_err());
}
