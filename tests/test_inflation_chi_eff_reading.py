"""The canonical n_s reads chi_eff from the D-009 K3 reading, not 6 b3.

6 b3 was refuted by D-009 and gives 258 on the adopted b3 = 43; the value 144
the paper publishes is 2 sum chi(K3_sigma) = 48 n at n = 3.
"""

import inspect

from metaphysica.simulations.PM.cosmology import inflation
from metaphysica.simulations.PM.geometry.closed_geometry.theorem import _active
from metaphysica.simulations.PM.geometry.kummer_index import k3_reading


def test_chi_eff_total_is_the_k3_reading_on_the_active_point():
    _, _, point = _active()
    assert point is not None
    reading = k3_reading(point)
    assert reading["consistent"]
    assert reading["n_singular"] == inflation.N_SINGULAR
    assert reading["chi_eff"] == inflation.CHI_EFF_TOTAL == 144


def test_no_published_text_justifies_chi_eff_as_six_b3():
    src = inspect.getsource(inflation)
    assert "6*b3 = 144" not in src and "6 · b₃ = 144" not in src
