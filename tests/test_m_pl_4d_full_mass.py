"""cosmology.M_Pl_4D is declared the FULL Planck mass (CODATA 1.22089e19);
cosmology_intro computed it as the REDUCED constants.M_PLANCK (2.435e18)."""
from metaphysica.simulations.PM.cosmology.cosmology_intro import CosmologyIntroV16


class _Inputs:
    _V = {"constants.M_PLANCK": 2.435e18, "codata.M_PLANCK": 1.220890e19,
          "topology.mephorash_chi": 144, "topology.b2": 12,
          "topology.elder_kads": 43}

    def get_param(self, path):
        return self._V[path]

    def get(self, path, default=None, **_):
        return self._V.get(path, default)

    def has_param(self, path):
        return path in self._V


def test_m_pl_4d_is_full_mass():
    sim = CosmologyIntroV16()
    sim.validate_inputs = lambda registry: None
    assert sim.run(_Inputs())["cosmology.M_Pl_4D"] == 1.220890e19
