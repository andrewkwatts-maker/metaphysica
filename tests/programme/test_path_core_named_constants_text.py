"""L1 path-core round 6: named-constants formula text and the b3_origin
options quote the path in force; chi_R reads chi_eff_total."""
from __future__ import annotations

import math

import pytest

from metaphysica.simulations.core.variants import selection
from metaphysica.simulations.PM.geometry.b3_path import resolve_path, seed_values


def _forced(seed):
    return selection.forced({"b3_seed": seed}) if seed else selection.forced({})


def test_reid_invariant_reads_chi_eff_total(monkeypatch):
    import importlib

    mod = importlib.import_module("metaphysica.simulations.core.FormulasRegistry")
    monkeypatch.setattr(mod.FormulasRegistry, "_chi_eff_from_route",
                        staticmethod(lambda b3: 288))
    reg = mod.FormulasRegistry()
    assert reg.reid_invariant == pytest.approx(1 / 288)
    assert reg.chi_parity_product == pytest.approx(288)
    consts = reg.generate_named_constants_json()
    assert "1/288" in consts["constants"]["reid_invariant"]["formula"]
    assert "IDENTITY" in consts["derived_values"]["parity_product"]["formula"]


@pytest.mark.parametrize("seed", [None, "seed_24"])
def test_named_constants_formula_text_quotes_the_path(seed):
    from metaphysica.simulations.core.FormulasRegistry import (
        FROZEN_PLEROMA, FormulasRegistry)

    with _forced(seed):
        b3 = seed_values(resolve_path())[0]
        reg = FormulasRegistry()
        manifest = reg.generate_named_constants_json()
    gates = manifest["gates"] if "gates" in manifest else {}
    flat = {}
    for block in manifest.values():
        if isinstance(block, dict):
            flat.update({k: v for k, v in block.items() if isinstance(v, dict)})
    flat.update(gates)
    for key in ("gate_07_torsion_alignment", "gate_10_dimensional_anchor",
                "gate_24_manifold_completion", "gate_49_scale_factor_prime",
                "gate_70_entropy_reversal"):
        assert str(b3) in flat[key]["formula"], key
    assert "10/%d" % b3 in flat["z6_pneuma"]["formula"]
    assert "18/%d" % b3 in flat["geometric_ratio"]["formula"]
    assert "3/4 Harmonic" not in flat["geometric_ratio"]["expanded"]
    assert "(B3/2) + 1 = 13" not in flat["penrose_hameroff_bridge"]["formula"]
    assert "= b3 + 2" not in flat["horos"]["formula"]
    assert "gamma/b3" in flat["mass_ratio"]["formula"]
    assert "frozen" in flat["hossenfelder_root"]["formula"]
    assert reg.hossenfelder_root == math.sqrt(FROZEN_PLEROMA) == math.sqrt(24)
    assert "n_gen = b2/4 = %d" % reg.n_gen in flat["chi_eff"]["formula"]


def test_b3_origin_options_for_24_are_marked_seed_24():
    from metaphysica.simulations.core.variants.catalogue.seed import FORKS

    fork = FORKS["b3_origin"]
    assert "whichever seed is live" not in fork.question
    for opt in fork.options:
        if not opt.adopted:
            assert opt.summary.startswith("seed_24 only:"), opt.id
