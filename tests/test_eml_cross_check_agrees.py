"""The EML path of each simulation must reproduce its normal path. Fixed
2026-10-26: g2_geometry EML used chi = 6 b3 (258, n_gen 5 at b3 = 43) and
ckm EML dropped the V_cd sign that run() restored."""
import pytest

from metaphysica.simulations.base.registry import PMRegistry
from metaphysica.simulations.PM.geometry.g2_geometry import G2GeometryV16
from metaphysica.simulations.PM.particle.ckm_matrix import CKMMatrixSimulation


class _Inputs:
    """The three registry inputs ckm_matrix reads (values from the build)."""
    _V = {"fermion.epsilon_fn": 0.2236, "fermion.n_generations": 3,
          "topology.K_MATCHING": 4}

    def get_param(self, path):
        return self._V[path]

    def get(self, path, default=None, **_):
        return self._V.get(path, default)

    def has_param(self, path):
        return path in self._V


def _both(sim, paths, reg=None):
    reg = reg or PMRegistry.get_instance()
    normal, eml = sim.run(reg), sim.run_eml(reg)
    return [(p, normal[p], eml[p]) for p in paths]


def test_g2_topology_agrees():
    for path, n, e in _both(G2GeometryV16(),
                            ["topology.mephorash_chi", "topology.n_gen"]):
        assert n == pytest.approx(e), path


def test_ckm_v_cd_sign_agrees():
    for path, n, e in _both(CKMMatrixSimulation(), ["ckm.V_cd"], _Inputs()):
        assert n == pytest.approx(e, rel=1e-6), path


def test_gauge_sector_never_publishes_pdg_literals():
    from metaphysica.simulations.PM.derivations.gauge_sector_complete import (
        _derived_elsewhere,
    )

    class _Reg(_Inputs):
        _V = {"gauge.weak_coupling_g2": 0.6524}

    assert _derived_elsewhere(_Reg(), "gauge.weak_coupling_g2") == 0.6524
    with pytest.raises(RuntimeError):
        _derived_elsewhere(_Reg(), "gauge.qcd_alpha_s_mz")
