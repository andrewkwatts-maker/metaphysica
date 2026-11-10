"""Volume modulus: omega and gamma_PPN from the symbolic reduction, with failing controls."""

from __future__ import annotations

import pytest
import sympy as sp

from metaphysica.actions.controls import volume_modulus as vm


@pytest.mark.parametrize("n", [1, 2, 3, 6, 9])
def test_omega_and_gamma_from_the_reduction(n):
    assert vm.omega(n) == -1 + sp.Rational(1, n)
    assert vm.gamma_ppn(n) == sp.Rational(1, n + 1)


def test_kaluza_klein_correspondence_holds_and_gr_control_fails():
    assert vm.correspondence().run().holds
    assert not vm.control().run().holds
    assert not vm.control(9).run().holds


def test_ppn_check_against_a_bound():
    assert not vm.ppn_check("cassini_like", 9, 2.3e-5).holds
    assert vm.ppn_check("loose", 9, 0.95).holds


def test_bad_dimension_raises():
    with pytest.raises(ValueError):
        vm.reduced_lagrangian(0)
