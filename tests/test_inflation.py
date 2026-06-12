"""Sprint 5 task #2 + T1 fix — G2 inflation observables gate.

Validates that
:class:`metaphysica.simulations.PM.cosmology.inflation.G2Inflation`
derives the scalar spectral index ``n_s`` and the tensor-to-scalar
ratio ``r`` from the Sprint 4 Re(T) stabilization potential, and that
the EML derivation tree cross-links back to b₃ = 24 (the SSoT seed).

T1 fix (2026-06): the canonical ``n_s`` is the golden-modulated
e-fold derivation ``n_s = 1 - 2*phi^2 / chi_eff = 1 - 2/55 ≈ 0.9636``
(0.30σ from Planck 2018).  Sprint T5 #2 (Option (b), 2026-06): this
derivation is now native to ``inflation.py`` (the "infrared closure"
formula) so the inflation module is independently Planck-compatible
without delegating to
:class:`metaphysica.simulations.PM.geometry.geometric_anchors_core.GeometricAnchors`.

The leading-order slow-roll on the Re(T) potential is preserved as
``n_s_slow_roll ≈ 0.9996`` for diagnostic purposes (the near-linear
potential is too flat to reproduce the observed ~3.5% red tilt — see
module docstring).
"""
from __future__ import annotations

import math

import pytest

from metaphysica.simulations.PM.cosmology.inflation import (
    DEFAULT_RE_T_STABILIZED,
    G2Inflation,
    PLANCK_N_S_CENTRAL,
    PLANCK_N_S_SIGMA,
    PLANCK_R_UPPER_95,
    get_inflation_observables,
)


# ── Shape ------------------------------------------------------------------


def test_get_inflation_observables_returns_dict_shape() -> None:
    """Top-level entry point returns the expected dict keys + types."""
    result = get_inflation_observables()
    assert isinstance(result, dict)
    expected_keys = {
        "n_s",
        "r",
        "n_s_slow_roll",
        "n_s_canonical_source",
        "status",
    }
    missing = expected_keys - set(result)
    assert not missing, f"Missing keys in result: {missing}"
    assert isinstance(result["n_s"], float)
    assert isinstance(result["r"], float)
    assert isinstance(result["n_s_slow_roll"], float)
    assert isinstance(result["n_s_canonical_source"], str)
    assert isinstance(result["status"], str)


def test_default_re_t_anchor() -> None:
    """Default Re(T) anchor inherits the Sprint 4 v_target 174.033."""
    sim = G2Inflation()
    assert sim.ReT_stabilized == DEFAULT_RE_T_STABILIZED
    assert math.isclose(sim.ReT_stabilized, 174.033, rel_tol=1e-12)


# ── Slow-roll formulas ----------------------------------------------------


def test_slow_roll_parameters_formula() -> None:
    """ε = 3 / (2 · Re(T)²), η = -1.5 / Re(T)² at the default anchor."""
    sim = G2Inflation()
    epsilon, eta = sim.slow_roll_parameters()
    ReT_sq = 174.033 * 174.033
    assert math.isclose(epsilon, 3.0 / (2.0 * ReT_sq), rel_tol=1e-12)
    assert math.isclose(eta, -1.5 / ReT_sq, rel_tol=1e-12)


def test_observables_match_textbook_slow_roll() -> None:
    """n_s_slow_roll = 1 - 6ε + 2η; r = 16ε at the default anchor.

    Post-T1 / Sprint T5 #2 the canonical ``n_s`` is sourced from the
    native infrared-closure formula in ``inflation.py``; the slow-roll
    value is preserved under ``n_s_slow_roll``.
    """
    sim = G2Inflation()
    epsilon, eta = sim.slow_roll_parameters()
    result = sim.derive_observables()
    assert math.isclose(
        result["n_s_slow_roll"],
        1.0 - 6.0 * epsilon + 2.0 * eta,
        rel_tol=1e-12,
    )
    assert math.isclose(result["r"], 16.0 * epsilon, rel_tol=1e-12)


def test_epsilon_positive_eta_negative() -> None:
    """ε must be strictly positive, η strictly negative."""
    epsilon, eta = G2Inflation().slow_roll_parameters()
    assert epsilon > 0.0
    assert eta < 0.0


# ── Planck bounds ---------------------------------------------------------


def test_tensor_to_scalar_ratio_below_planck_upper_bound() -> None:
    """r must respect the Planck 2018/2026 95 % CL upper bound r < 0.036."""
    result = get_inflation_observables()
    assert 0.0 < result["r"] < PLANCK_R_UPPER_95, (
        f"r = {result['r']:.6e} violates the Planck 2018/2026 "
        f"95 % CL upper bound r < {PLANCK_R_UPPER_95}"
    )


def test_canonical_n_s_matches_planck_within_one_sigma() -> None:
    """Post-T1: the canonical ``n_s`` agrees with Planck 2018 to <1σ.

    n_s = 1 - 2*phi^2/chi_eff = 1 - 2/55 ≈ 0.9636 from the native
    infrared closure (chi_eff = 6*b3 = 144), 0.30σ from Planck 2018
    (0.9649 ± 0.0042).
    """
    result = get_inflation_observables()
    assert abs(result["n_s"] - PLANCK_N_S_CENTRAL) <= PLANCK_N_S_SIGMA, (
        f"Canonical n_s = {result['n_s']!r} is outside the Planck "
        f"1sigma window ({PLANCK_N_S_CENTRAL} ± {PLANCK_N_S_SIGMA})."
    )
    # Sanity: must be the canonical golden-modulated value, not the
    # slow-roll fallback (sentinel: 0.9636384168229182).
    assert math.isclose(result["n_s"], 0.9636384168229182, rel_tol=1e-12), (
        f"Expected canonical n_s ≈ 0.9636384168229182, got "
        f"{result['n_s']!r}."
    )
    assert result["n_s_canonical_source"].startswith(
        "infrared_closure"
    ), (
        f"Expected canonical n_s sourced from the native infrared "
        f"closure, got {result['n_s_canonical_source']!r}."
    )


def test_slow_roll_divergence_is_preserved_as_documented_divergence() -> None:
    """The slow-roll n_s ≈ 0.9996 is preserved as ``n_s_slow_roll``.

    Post-T1 the *canonical* n_s lands inside the Planck window, but
    the leading-order slow-roll on the Re(T) potential still sits
    outside it.  The module must surface that as a
    ``documented_divergence`` rather than discarding the diagnostic.
    """
    result = get_inflation_observables()
    # Slow-roll diagnostic still lies outside the Planck window.
    assert (
        abs(result["n_s_slow_roll"] - PLANCK_N_S_CENTRAL) > PLANCK_N_S_SIGMA
    ), (
        f"Expected n_s_slow_roll = {result['n_s_slow_roll']!r} to lie "
        f"outside the Planck 1sigma window "
        f"({PLANCK_N_S_CENTRAL} ± {PLANCK_N_S_SIGMA})."
    )
    # The status string must flag this as a documented divergence.
    assert "documented_divergence" in result["status"], (
        f"Expected status to contain 'documented_divergence', got "
        f"{result['status']!r}"
    )


# ── b₃ traceback -----------------------------------------------------------


def test_eml_tree_contains_n_s_and_r_with_b3_traceback() -> None:
    """The registered EML derivations cross-link back to b₃ = 24.

    Both ``n_s`` and ``r`` derivations explicitly mention ``b3`` in
    their formula strings so the ``b3_traceback`` flag must be set on
    each entry.
    """
    sim = G2Inflation()
    sim.derive_observables()
    tree = sim.get_eml_tree()
    assert "n_s" in tree, (
        f"Expected 'n_s' in tree, got keys: {sorted(tree.keys())}"
    )
    assert "r" in tree, (
        f"Expected 'r' in tree, got keys: {sorted(tree.keys())}"
    )
    for param in ("n_s", "r"):
        entry = tree[param]
        assert isinstance(entry, dict), (
            f"{param} entry is not a dict: {type(entry).__name__}"
        )
        assert entry.get("b3_traceback") is True, (
            f"{param} formula does not trace back to b3: "
            f"formula={entry.get('formula')!r}"
        )


def test_structural_eml_tree_uses_b3_leaf() -> None:
    """The structural ``n_s`` tree must use ``b3_leaf()`` as a real node.

    A purely-textual ``b3`` mention in a string is sufficient for the
    ``b3_traceback`` flag, but the website's b₃ tracer walks
    ``EMLPoint.children`` recursively to find the SEED leaf.  We
    construct the tree explicitly via ``_build_observables_eml_tree``
    and check that evaluating it at the derived ε, η reproduces
    ``n_s`` to within floating-point tolerance.

    Skipped in dev environments where ``eml-math`` + ``eml-spectral``
    are not installed.
    """
    from metaphysica.simulations.core.eml_integration import EML_AVAILABLE

    if not EML_AVAILABLE:
        pytest.skip("eml-math / eml-spectral not installed in this env")
    sim = G2Inflation()
    result = sim.derive_observables()
    tree = getattr(sim, "_last_tree", None)
    assert tree is not None, "_last_tree must be populated after derive"
    # The structural tree encodes the slow-roll formula owned by this
    # module (the canonical n_s is the infrared-closure value); evaluating
    # the tree should therefore reproduce ``n_s_slow_roll``.
    tree_value = float(tree.tension())
    assert math.isclose(
        tree_value, result["n_s_slow_roll"], rel_tol=1e-9, abs_tol=1e-12
    ), (
        f"Structural EML tree evaluates to {tree_value!r}, expected "
        f"n_s_slow_roll = {result['n_s_slow_roll']!r}"
    )


# ── Parameterisation -------------------------------------------------------


def test_constructor_rejects_nonpositive_re_t() -> None:
    """Re(T) must be strictly positive."""
    with pytest.raises(ValueError):
        G2Inflation(ReT_stabilized=0.0)
    with pytest.raises(ValueError):
        G2Inflation(ReT_stabilized=-174.0)


def test_large_re_t_drives_slow_roll_to_de_sitter_limit() -> None:
    """In the Re(T) → ∞ limit ε, η → 0 so ``n_s_slow_roll`` → 1 and r → 0.

    Sanity check that the slow-roll formulas have the right asymptotic
    behaviour (the slow-roll approximation degenerates to exact
    de-Sitter as the inflaton potential flattens).  The canonical
    ``n_s`` is sourced from the native infrared closure and does *not*
    depend on Re(T), so it remains pinned at the golden-modulated value.
    """
    sim = G2Inflation(ReT_stabilized=1.0e6)
    epsilon, eta = sim.slow_roll_parameters()
    result = sim.derive_observables()
    assert epsilon < 1e-10
    assert abs(eta) < 1e-10
    assert math.isclose(result["n_s_slow_roll"], 1.0, abs_tol=1e-9)
    assert result["r"] < 1e-9
    # Canonical n_s is Re(T)-independent: still the infrared-closure
    # value (0.9636), not the de-Sitter slow-roll limit (1.0).
    assert math.isclose(result["n_s"], 0.9636384168229182, rel_tol=1e-12)
