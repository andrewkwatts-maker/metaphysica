"""Zero modes: controls, refusals and Poincare symmetry."""

from fractions import Fraction
from math import comb

import pytest

from metaphysica.actions.controls import g2_zero_modes, torus_sugra
from metaphysica.actions.controls.g2_zero_modes import JOYCE_EXAMPLE, SUGRA_11D
from metaphysica.actions.model import Field
from metaphysica.actions.zero_modes import dualise_forms, full_betti, zero_modes

T7 = {k: comb(7, k) for k in range(8)}


def test_g2_joyce_control_and_failing_control():
    assert g2_zero_modes.correspondence().run().holds
    assert not g2_zero_modes.control().run().holds
    got = zero_modes(SUGRA_11D, 7, JOYCE_EXAMPLE["betti"], "G2")
    assert (got["vector"], got["scalar"], got["spinor"], got["metric"]) == (12, 86, 1, 1)


def test_t7_n8_control_and_failing_control():
    assert torus_sugra.correspondence().run().holds
    assert not torus_sugra.control().run().holds
    got = zero_modes(SUGRA_11D, 7, T7, "flat")
    assert (got["vector"], got["scalar"], got["form:2"], got["spinor"]) == (28, 63, 7, 8)
    assert dualise_forms(got, 4)["scalar"] == 70


def test_refuses_other_holonomy_and_bad_inputs():
    with pytest.raises(ValueError, match="holonomy"):
        zero_modes(SUGRA_11D, 6, {}, "SU3")
    with pytest.raises(ValueError, match="b1"):
        zero_modes(SUGRA_11D, 7, {1: 1, 2: 12, 3: 43}, "G2")
    with pytest.raises(ValueError, match="dimension 7"):
        zero_modes(SUGRA_11D, 6, {1: 0, 2: 1, 3: 1}, "G2")
    with pytest.raises(ValueError, match="unknown kind"):
        zero_modes((Field("x", "weird", 1, Fraction(0)),), 7, T7, "flat")


def test_poincare_symmetry_enforced_and_filled():
    assert full_betti({1: 0, 2: 12, 3: 43}, 7) == {0: 1, 1: 0, 2: 12, 3: 43,
                                                   4: 43, 5: 12, 6: 0, 7: 1}
    with pytest.raises(ValueError, match="Poincare"):
        full_betti({0: 1, 1: 0, 2: 12, 3: 43, 4: 40, 5: 12, 6: 0, 7: 1}, 7)
    with pytest.raises(ValueError, match="missing"):
        full_betti({1: 0}, 7)
