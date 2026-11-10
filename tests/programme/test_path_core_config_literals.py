"""L1 path-core: config parameter classes read the topology of the path.

core-paths-11 (remainder): EFTValidity, G2SpinorGeometry, TCSTopology,
PneumaRacetrack, MashiachStabilization, QuantumFRStability,
TopologicalCPPhase, DoubletTripletSplitting, AnomalyCancellation and
TorsionClass.N_FLUX typed B3 = 24, B2 = 4, CHI_EFF = 144, N_FLUX = 24 or
N_GENERATIONS = 3 from the retired TCS #187 reading under the live names.
"""
import math

import pytest

from metaphysica.config.parameters import fermion, fitted, geometry, moduli
from metaphysica.config.parameters import proton_decay
from metaphysica.simulations.core import active_path
from metaphysica.simulations.core.active_path import Topology
from metaphysica.simulations.core.variants import selection

STUB = Topology(path="stub", b3=31, b2=8, n_gen=2, chi_eff=96)

CLASSES = {
    geometry.EFTValidityParameters: ("B3",),
    geometry.G2SpinorGeometryParameters: ("B3", "CHI_EFF"),
    geometry.TCSTopologyParameters: ("B3", "B2", "CHI_EFF"),
    moduli.PneumaRacetrackParameters: ("B3", "CHI_EFF", "N_FLUX"),
    moduli.MashiachStabilizationParameters: ("CHI_EFF", "N_FLUX"),
    moduli.QuantumFRStabilityParameters: ("CHI_EFF", "N_FLUX"),
    fermion.TopologicalCPPhaseParameters: ("B3",),
    proton_decay.DoubletTripletSplittingParameters: ("B2", "CHI_EFF"),
    fitted.AnomalyCancellation: ("N_GENERATIONS",),
    fitted.TorsionClass: ("N_FLUX",),
}
EXPECT = {"B3": lambda t: t.b3, "B2": lambda t: t.b2,
          "CHI_EFF": lambda t: t.chi_eff, "N_FLUX": lambda t: t.chi_eff / 6,
          "N_GENERATIONS": lambda t: t.n_gen}


@pytest.fixture
def stub_path(monkeypatch):
    monkeypatch.setattr(active_path, "topology", lambda path=None: STUB)


@pytest.mark.parametrize("cls", list(CLASSES), ids=lambda c: c.__name__)
def test_config_class_follows_the_path_in_force(cls, stub_path):
    for name in CLASSES[cls]:
        assert getattr(cls, name) == EXPECT[name](STUB), (cls.__name__, name)


@pytest.mark.parametrize("seed", [None, "seed_24"])
def test_config_b3_follows_the_seed(seed):
    with selection.forced({"b3_seed": seed} if seed else {}):
        topo = active_path.topology()
        assert geometry.EFTValidityParameters.B3 == topo.b3
        assert geometry.TCSTopologyParameters.B2 == topo.b2
        assert fermion.TopologicalCPPhaseParameters.B3 == topo.b3


def test_derived_constants_follow_the_flux(stub_path):
    n = STUB.chi_eff / 6
    for cls in (moduli.PneumaRacetrackParameters,
                moduli.MashiachStabilizationParameters):
        assert cls.A_COEFF == pytest.approx(2 * math.pi / n)
        assert cls.B_COEFF == pytest.approx(2 * math.pi / (n + 1))
    cp = fermion.TopologicalCPPhaseParameters
    assert cp.DELTA_CP_RAD == pytest.approx(math.pi * 12 / STUB.b3)
    assert cp.MAXIMAL_CP is False
    assert fitted.AnomalyCancellation.GS_COUNTERTERM == STUB.n_gen
    assert fitted.AnomalyCancellation.is_anomaly_free()


def test_retired_records_are_kept():
    assert geometry.TCSTopologyParameters.RETIRED_TCS187_B3 == 24
    assert geometry.TCSTopologyParameters.RETIRED_TCS187_HODGE_H31 == 68
    assert fitted.TorsionClass.TCS187_N_FLUX == 24
    assert fitted.TorsionClass.T_OMEGA == -0.875
    retired = geometry.TCSTopologyParameters.export_data()["retired_tcs187"]
    assert retired["gluing_formula"].endswith("= 24 (retired)")


def test_an_undefined_name_still_raises():
    with pytest.raises(AttributeError):
        geometry.TCSTopologyParameters.NO_SUCH_NAME
