"""Tests for the PhysicsConfig frozen facade.

The point of PhysicsConfig is that it is a VIEW, not a store. These tests exist
to keep it that way: if someone later adds a literal default to a field, the
codebase gains a sixth independent copy of the dimensional integers and the
config-drift audit's ORPHAN count goes up. The AST test below is what stops it.
"""
from __future__ import annotations

import ast
import io
from pathlib import Path

import pytest

from metaphysica.simulations.core.FormulasRegistry import get_registry
from metaphysica.simulations.core.physics_config import PhysicsConfig

_MODULE = (
    Path(__file__).resolve().parents[1]
    / "src" / "metaphysica" / "simulations" / "core" / "physics_config.py"
)


def test_every_field_matches_its_registry_property():
    """No field may drift from FormulasRegistry -- it is the SSOT."""
    reg = get_registry()
    cfg = PhysicsConfig.from_registry(reg)
    expected = {
        "d_ancestral_total": reg.D_ancestral_total,
        "d_ancestral_space": reg.D_ancestral_space,
        "d_ancestral_time": reg.D_ancestral_time,
        "d_shadow_total": reg.D_shadow_total,
        "d_shadow_space": reg.D_shadow_space,
        "d_shadow_time": reg.D_shadow_time,
        "d_g2_total": reg.D_G2_total,
        "d_visible_total": reg.D_visible_total,
        "d_visible_space": reg.D_visible_space,
        "d_visible_time": reg.D_visible_time,
        "elder_kads": reg.elder_kads,
        "bridge_local": reg.bridge_local,
        "bridge_effective": reg.bridge_effective,
    }
    for name, want in expected.items():
        assert getattr(cfg, name) == want, f"{name} drifted from the registry"


def test_module_contains_no_dimensional_literal():
    """A literal default would make this a store rather than a view.

    Permitted: 0, 1, 2 (they appear in `2 ** (n // 2)` and `math.pi / 2`,
    and all three are in the sterility audit's sterile set) and 8, which is
    Bott periodicity -- a theorem about real Clifford algebras, not a
    framework value, and named as _CLIFFORD_PERIOD at its one use site.

    This test earns its keep: it caught the bare `% 8` on first run.
    """
    tree = ast.parse(io.open(_MODULE, encoding="utf-8").read())
    offenders = [
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant)
        and isinstance(n.value, (int, float))
        and not isinstance(n.value, bool)
        and n.value not in (0, 1, 2, 8)
    ]
    assert not offenders, f"dimensional literals leaked into the view: {offenders}"


def test_config_is_frozen():
    cfg = PhysicsConfig.from_registry()
    with pytest.raises(Exception):
        cfg.elder_kads = 99  # type: ignore[misc]


def test_default_construction_uses_the_singleton():
    """from_registry() with no argument must match an explicit registry."""
    assert PhysicsConfig.from_registry() == PhysicsConfig.from_registry(get_registry())


def test_signature_identity_is_enforced():
    """total = space + time, checked at every level.

    Deliberately NOT asserted: bulk == 2 * shadow. That holds at 26D and fails
    at 28D, and CANON["D_bulk"] is STRUCTURAL_CHALLENGED -- baking it in would
    hard-fail an open author ruling.
    """
    cfg = PhysicsConfig.from_registry()
    assert cfg.d_ancestral_total == cfg.d_ancestral_space + cfg.d_ancestral_time
    assert cfg.d_shadow_total == cfg.d_shadow_space + cfg.d_shadow_time
    assert cfg.d_visible_total == cfg.d_visible_space + cfg.d_visible_time


def test_inconsistent_signature_is_rejected():
    """The validator must be able to FAIL -- otherwise it certifies nothing."""
    cfg = PhysicsConfig.from_registry()
    fields = {
        f: getattr(cfg, f)
        for f in cfg.__dataclass_fields__  # type: ignore[attr-defined]
    }
    fields["d_shadow_space"] = fields["d_shadow_space"] + 1  # break s + t = total
    with pytest.raises(ValueError, match="shadow signature inconsistent"):
        PhysicsConfig(**fields)


def test_derived_spinor_matches_the_explicit_clifford_construction():
    """Cross-check against Cl(12,1) built as actual 64x64 matrices.

    Two independent routes to the same numbers: this config derives them
    arithmetically from the signature, while shadow_clifford builds the gamma
    matrices and reads their shape.
    """
    from metaphysica.simulations.PM.algebra.shadow_clifford import (
        shadow_clifford_report,
    )

    cfg = PhysicsConfig.from_registry()
    report = shadow_clifford_report()
    assert cfg.shadow_spinor_dim == report["spinor_dim"]
    assert cfg.shadow_pair_spinor == report["shadow_pair_spinor"]
    assert cfg.signature_invariant == report["signature_invariant_s_minus_t_mod_8"]


def test_orthogonal_bound_matches_the_rp_gate():
    """The RP bound is 90 degrees, and bridge_geometry must agree."""
    import math

    cfg = PhysicsConfig.from_registry()
    assert cfg.orthogonal_bound == pytest.approx(math.pi / 2)


def test_config_fundamental_constants_track_the_registry():
    """config.FundamentalConstants must not be a parallel store.

    Its own module comment concedes it is not authoritative, and the drift
    audit classes a hand literal with no registry path as ORPHAN -- "the worst
    class". These are now read from FormulasRegistry at class-definition time,
    so a change to the open (24,2)/26D vs (26,2)/28D ruling propagates instead
    of needing a hand edit.
    """
    from metaphysica.config import FundamentalConstants as FC

    reg = get_registry()
    assert FC.D_BULK == reg.D_ancestral_total
    assert FC.SIGNATURE_BULK == (reg.D_ancestral_space, reg.D_ancestral_time)
    assert FC.D_PER_SHADOW == reg.D_shadow_total
    assert FC.SIGNATURE_SHADOW == (reg.D_shadow_space, reg.D_shadow_time)
    assert FC.N_BRIDGE_PAIRS == reg.bridge_local


def test_config_has_no_dimensional_literals_left():
    """The literals must be gone, not merely shadowed by a matching value."""
    import io
    from pathlib import Path

    cfg = (
        Path(__file__).resolve().parents[1]
        / "src" / "metaphysica" / "config.py"
    )
    # Every class that mirrored these -- FundamentalConstants,
    # V21BridgeParameters, PneumaVielbeinParameters and the two dimensional
    # -structure blocks -- now reads the registry.
    #
    # Matches ASSIGNMENTS only. A plain substring search also hits prose such
    # as "# Check 2: v22 dual-shadow structure (D_PER_SHADOW = 13)", which is a
    # comment describing the value, not a second copy of it.
    literals = ("D_BULK = 26", "D_PER_SHADOW = 13",
                "SIGNATURE_BULK = (24, 2)", "BULK_SIGNATURE = (24, 2)",
                "SHADOW_SIGNATURE = (12, 1)", "SIGNATURE_SHADOW = (12, 1)",
                "N_BRIDGE_PAIRS = 12", "D_AFTER_SP2R = 13",
                "SIGNATURE_INITIAL = (24, 2)", "D_SHADOW_NORMAL = 13",
                "D_SHADOW_MIRROR = 13")
    offenders = []
    for lineno, line in enumerate(
        io.open(cfg, encoding="utf-8").read().splitlines(), 1
    ):
        code = line.split("#", 1)[0]
        for literal in literals:
            if code.strip().startswith(literal):
                offenders.append(f"{lineno}: {line.strip()[:70]}")
    assert not offenders, "dimensional literals survived:\n" + "\n".join(offenders)
