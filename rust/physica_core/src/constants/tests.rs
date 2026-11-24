//! Unit tests for the `constants` module.

use super::*;

#[test]
fn registry_seeds_ten_pillars() {
    let r = FormulasRegistry::new();
    // 10 seeds + derived first-tier; assert seeds are all present.
    for nm in [
        "b3",
        "chi_eff",
        "n_gen",
        "roots_total",
        "visible_sector",
        "sterile_sector",
        "phi",
        "gamma_em",
        "jc_constant",
        "logic_closure",
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
    let v = evaluate_expression("(roots_total - visible_sector) / n_gen", &r, &mut visiting)
        .unwrap();
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
    let err = r
        .load_from_json(Path::new("h:/does/not/exist.json"))
        .unwrap_err();
    assert!(matches!(err, ConstantError::Io { .. }));
}
