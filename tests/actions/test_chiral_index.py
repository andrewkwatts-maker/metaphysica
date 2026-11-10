"""Chiral index of the child fermions: zero for flat tori and G2, two for K3 (the control)."""

from __future__ import annotations

import pytest

from metaphysica.actions.zero_modes import chiral_index, chirality_check


@pytest.mark.parametrize("n", [1, 2, 3, 6, 7])
def test_flat_torus_is_not_chiral(n):
    assert chiral_index(n, "flat") == 0


def test_g2_is_not_chiral():
    assert chiral_index(7, "G2") == 0
    assert not chirality_check("Y7", 7, "G2").holds


def test_k3_is_chiral_and_t2_fails():
    assert chiral_index(4, "SU2") == 2
    assert chirality_check("K3", 4, "SU2").holds
    control = chirality_check("T2", 2, "flat")
    assert not control.holds and control.measured == 0


def test_bad_inputs_raise():
    for args in ((6, "G2"), (6, "SU2"), (6, "SU3"), (0, "flat")):
        with pytest.raises(ValueError):
            chiral_index(*args)
