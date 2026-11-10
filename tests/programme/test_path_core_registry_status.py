"""L1 path-core round 3: registry statuses, loader failures, literal fallbacks.

Findings: sim-geometry-structure-05, sim-particle-27 (base/registry.py part),
sim-particle-01 (FormulasRegistry part), core-paths-13, core-paths-26,
core-paths-18.
"""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from metaphysica.simulations.base import registry as base_registry
from metaphysica.simulations.base.registry import (
    ENTRY_POINT_KEY_STATUSES,
    PMRegistry,
)

_SRC = Path(__file__).resolve().parents[2] / "src" / "metaphysica"
_QED_KERNELS = ("avogadro", "compton_wavelength", "faraday", "hartree_energy",
                "magnetic_flux", "molar_gas", "stefan_boltzmann",
                "von_klitzing", "weak_mixing")


@pytest.fixture
def reg():
    PMRegistry.reset_instance()
    yield PMRegistry.get_instance()
    PMRegistry.reset_instance()


def _load(reg, importer, label="re_t_sector", **kw):
    return reg._register_entry_point(
        label, importer, prefix="geometry.", version="v25.0",
        status="DERIVED", metadata={}, verbose=False,
        drop_status_key=False,
        key_statuses=kw.get("key_statuses",
                            ENTRY_POINT_KEY_STATUSES.get(label)))


def test_re_t_rows_are_calibrated_not_derived(reg):
    _load(reg, lambda: {"ReT": 174.0, "VEV_gap_percent": 0.0})
    for key in ("geometry.ReT", "geometry.VEV_gap_percent"):
        entry = reg.get_entry(key)
        assert entry.status == "CALIBRATED", (key, entry.status)
        assert entry.metadata["status_reason"]


def test_entry_point_failure_raises_instead_of_skipping(reg):
    def broken():
        raise RuntimeError("module not built")

    with pytest.raises(RuntimeError, match="module not built"):
        _load(reg, broken, label="yukawa_derivation")
    with pytest.raises(TypeError):
        _load(reg, lambda: [1, 2], label="yukawa_derivation")
    with pytest.raises(KeyError, match="ReT"):
        _load(reg, lambda: {"VEV_gap_percent": 0.0})


def test_loader_source_swallows_nothing():
    src = (_SRC / "simulations/base/registry.py").read_text(encoding="utf-8")
    assert "swallow everything" not in src
    assert '{"error":' not in src


def test_qed_manifest_rows_are_declared_identities():
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

    table = FormulasRegistry.QED_ROUNDTRIP_IDENTITIES
    reg = FormulasRegistry()
    for prop, codata in table.items():
        value, ref = getattr(reg, prop), getattr(FormulasRegistry, codata)
        assert math.isclose(value, ref, rel_tol=1e-12), (prop, value, ref)
    stems = {p.replace("manifest_", "") for p in table}
    for kernel in _QED_KERNELS:
        assert any(s.startswith(kernel) for s in stems), kernel


def test_registry_has_no_literal_seed_fallbacks():
    src = (_SRC / "simulations/core/FormulasRegistry.py").read_text(
        encoding="utf-8")
    assert "self._b3 = 43" not in src
    assert "return 144  # import cycle" not in src
    assert "return 3                       # rank(Gamma)" not in src


def test_b3_clusters_is_not_stated_at_the_active_seed():
    from metaphysica.simulations.core.variants.catalogue.g2_forms import FORKS

    fork = FORKS["moduli_indexing"]
    opts = {o.id: o for o in fork.options}
    clusters = opts["b3_clusters"]
    assert "b3 = 24 3-cycles" not in clusters.summary
    assert "retired seed_24" in clusters.summary
    assert "STALE ON THE ACTIVE PATH" in clusters.consequence
    assert "b3 = 24 chiral moduli" not in opts["b2_gauge"].consequence
    assert set(opts) == {"b3_clusters", "b2_gauge", "cy3_shadow"}


def test_master_action_names_the_weyl_spinor():
    from metaphysica.config.parameters.master_action import (
        MasterActionParameters as M,
    )

    assert M.PNEUMA_WEYL_26D == 4096
    assert not hasattr(M, "PNEUMA_25D")
    assert M.PNEUMA_WEYL_26D // M.PNEUMA_SHADOW_FULL == M.BRIDGE_REDUCTION
    assert base_registry is not None
