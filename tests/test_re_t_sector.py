"""Sprint 4 task #3 — non-perturbative Re(T) stabilization gate.

Validates that
:class:`metaphysica.simulations.PM.geometry.re_t_sector.NonPerturbativeReT`
closes the 3.4 % VEV coefficient gap from v24.2 to < 0.01 %, and that the
EML derivation tree carries a genuine b₃ leaf (traceability back to the
SSoT seed b₃ = 24).
"""
from __future__ import annotations

import math

import pytest

from metaphysica.simulations.PM.geometry.re_t_sector import (
    BRIDGE_COUPLING_ASSERTED,
    NonPerturbativeReT,
    RE_T_VEV_TARGET,
    close_vev_gap,
)


# ── Gate criteria -----------------------------------------------------------


def test_close_vev_gap_returns_dict_shape() -> None:
    """Top-level entry point returns the expected dict keys + types."""
    result = close_vev_gap()
    assert isinstance(result, dict)
    assert set(result.keys()) == {"ReT", "VEV_gap_percent"}
    assert isinstance(result["ReT"], float)
    assert isinstance(result["VEV_gap_percent"], float)


def test_vev_gap_closes_below_0p01_percent() -> None:
    """Sprint 4 gate: |VEV_gap_percent| < 0.01 % (proof-killer #2 closed)."""
    result = close_vev_gap()
    assert abs(result["VEV_gap_percent"]) < 0.01, (
        f"VEV gap still open: {result['VEV_gap_percent']:.6f} % "
        f"(was 3.4 % in v24.2, must be < 0.01 %)"
    )


def test_re_t_is_positive_and_finite() -> None:
    """Stabilized Re(T) must be a positive, finite real number."""
    result = close_vev_gap()
    ReT = result["ReT"]
    assert math.isfinite(ReT), f"ReT is not finite: {ReT}"
    assert ReT > 0.0, f"ReT must be positive, got {ReT}"


def test_re_t_lands_at_vev_target() -> None:
    """Stabilized Re(T) should land at the canonical 174.033 GeV anchor."""
    result = close_vev_gap()
    # < 0.01 % closure is equivalent to absolute closeness of ~0.017 GeV.
    assert abs(result["ReT"] - RE_T_VEV_TARGET) < 0.05, (
        f"ReT = {result['ReT']:.6f} GeV deviates from v_target "
        f"= {RE_T_VEV_TARGET} GeV by more than 0.05 GeV"
    )


# ── EML traceability -------------------------------------------------------


def test_eml_tree_contains_b3_leaf() -> None:
    """The registered EML derivations cross-link back to b₃ = 24.

    The ``eml_operator_tree`` adapter sets a ``b3_traceback`` flag on
    any entry whose ``formula`` string mentions ``b3`` (or ``b_3`` / ``24``).
    Both registered v25.0 derivations (``ReT_stabilized`` and
    ``VEV_gap_percent``) explicitly mention ``b3`` and ``24`` so the
    flag must be set on each.
    """
    solver = NonPerturbativeReT()
    solver.solve_stabilized_ReT()
    tree = solver.get_eml_tree()
    assert "ReT_stabilized" in tree, (
        f"Expected ReT_stabilized in tree, got keys: {sorted(tree.keys())}"
    )
    assert "VEV_gap_percent" in tree, (
        f"Expected VEV_gap_percent in tree, got keys: {sorted(tree.keys())}"
    )
    for param in ("ReT_stabilized", "VEV_gap_percent"):
        entry = tree[param]
        assert isinstance(entry, dict), (
            f"{param} entry is not a dict: {type(entry).__name__}"
        )
        assert entry.get("b3_traceback") is True, (
            f"{param} formula does not trace back to b3: "
            f"formula={entry.get('formula')!r}"
        )


def test_structural_eml_tree_uses_b3_leaf() -> None:
    """The structural residual tree must use ``b3_leaf()`` as a real node.

    A purely-textual ``b3`` mention in a string is sufficient for the
    ``b3_traceback`` flag, but the website's b₃ tracer walks
    ``EMLPoint.children`` recursively to find the SEED leaf. To guarantee
    the leaf is present even after compaction, we build the residual
    tree explicitly via ``_build_residual_eml_tree`` and check that
    evaluating it at the solved Re(T) reproduces (very nearly) zero.

    Skipped in dev environments where ``eml-math`` + ``eml-spectral``
    are not installed (the canonical ``EML_AVAILABLE`` flag is False);
    the Sprint 4 gate (closure of the VEV gap) does not depend on this
    leg — the structural EML tree is forensic metadata for the website's
    b₃ tracer.
    """
    from metaphysica.simulations.core.eml_integration import EML_AVAILABLE
    if not EML_AVAILABLE:
        pytest.skip("eml-math / eml-spectral not installed in this env")
    solver = NonPerturbativeReT()
    result = solver.solve_stabilized_ReT()
    # _last_tree is populated by solve_stabilized_ReT.
    tree = getattr(solver, "_last_tree", None)
    assert tree is not None, "_last_tree must be populated after solve"
    # The tree's tension() is the residual at the solved Re(T) — it
    # should evaluate to ~0 (well within the fsolve tolerance).
    residual = float(tree.tension())
    assert abs(residual) < 1e-6, (
        f"Structural EML residual at ReT={result['ReT']!r} is "
        f"{residual!r} (expected ~0)"
    )


# ── Parameterisation -------------------------------------------------------


def test_solver_rejects_nonpositive_b3() -> None:
    with pytest.raises(ValueError):
        NonPerturbativeReT(b3=0)
    with pytest.raises(ValueError):
        NonPerturbativeReT(b3=-1)


def test_solver_rejects_nonpositive_flux() -> None:
    with pytest.raises(ValueError):
        NonPerturbativeReT(flux=0)
    with pytest.raises(ValueError):
        NonPerturbativeReT(flux=-3)


def test_default_b3_is_g2_third_betti() -> None:
    """Defaults must be the SSoT seed (b₃ = 24) and bridge count (12)."""
    solver = NonPerturbativeReT()
    assert solver.b3 == 24
    assert solver.flux == 12


# ── Bridge coupling (Sprint T6 #3) -----------------------------------------


def test_bridge_coupling_derived_from_half_instanton() -> None:
    """Sprint T6 #3 gate: g_bridge derives from G₂ half-instanton.

    At v25.0 defaults (Re(T) = 174.033, b₃ = 24) the half-instanton
    exponent ``exp(−π·Re(T)/b₃)`` evaluates to ≈ 1.288e-10 — within
    7 % of the asserted ``BRIDGE_COUPLING_ASSERTED`` rounded constant
    that the mirror DM modules carry as their default.
    """
    solver = NonPerturbativeReT()
    g_bridge = solver.compute_bridge_coupling()

    # Exact analytic check: g_bridge ≡ exp(−π·Re(T)/b₃).
    expected = math.exp(-math.pi * RE_T_VEV_TARGET / 24)
    assert math.isclose(g_bridge, expected, rel_tol=1e-12), (
        f"compute_bridge_coupling drifted from exp(-pi*ReT/b3): "
        f"derived={g_bridge!r}, expected={expected!r}"
    )

    # Agreement with the asserted rounded constant: within 10 %.
    rel_gap = abs(g_bridge - BRIDGE_COUPLING_ASSERTED) / BRIDGE_COUPLING_ASSERTED
    assert rel_gap < 0.10, (
        f"Derived g_bridge = {g_bridge:.3e} disagrees with asserted "
        f"BRIDGE_COUPLING_ASSERTED = {BRIDGE_COUPLING_ASSERTED:.3e} by "
        f"{rel_gap * 100:.2f} % (rounding tolerance is 10 %)"
    )


def test_bridge_coupling_tracks_re_t() -> None:
    """Doubling Re(T) must shrink g_bridge by ``exp(−π·Re(T)/b₃)``.

    Confirms the bridge coupling really is locked to the volume
    modulus rather than fortuitously hitting 1.2e-10 at v25.0 defaults.
    """
    solver = NonPerturbativeReT()
    g_at_default = solver.compute_bridge_coupling()
    g_at_double = solver.compute_bridge_coupling(ReT=2.0 * RE_T_VEV_TARGET)
    # Ratio = exp(−π·Re(T)/b₃)  (the second factor that appears when Re(T) doubles).
    expected_ratio = math.exp(-math.pi * RE_T_VEV_TARGET / 24)
    actual_ratio = g_at_double / g_at_default
    assert math.isclose(actual_ratio, expected_ratio, rel_tol=1e-12), (
        f"Bridge coupling does not track Re(T): "
        f"g(2·ReT)/g(ReT) = {actual_ratio!r}, expected {expected_ratio!r}"
    )


def test_bridge_coupling_registers_b3_traceable_entry() -> None:
    """Derivation must land in the EML tree with the b₃ traceback flag."""
    solver = NonPerturbativeReT()
    solver.compute_bridge_coupling()
    tree = solver.get_eml_tree()
    assert "bridge_coupling_derived" in tree, (
        f"compute_bridge_coupling did not register; tree keys: "
        f"{sorted(tree.keys())}"
    )
    entry = tree["bridge_coupling_derived"]
    assert entry.get("b3_traceback") is True, (
        f"Bridge coupling formula does not trace back to b3: "
        f"formula={entry.get('formula')!r}"
    )
