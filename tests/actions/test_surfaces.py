"""Gauss-Bonnet: a Ricci-flat compact surface is a torus; the sphere is the failing control."""

from __future__ import annotations

import pytest
import sympy as sp

from metaphysica.actions.surfaces import (
    euler_characteristic, flat_torus, genus_from_metric, integrated_curvature,
    ricci_flat_check, ricci_flat_genus, sphere,
)


def test_ricci_flat_genus_is_one():
    assert ricci_flat_genus() == 1


def test_gauss_bonnet_from_explicit_metrics():
    assert sp.simplify(integrated_curvature(*sphere()) - 4 * sp.pi) == 0
    assert genus_from_metric(*sphere()) == 0
    assert integrated_curvature(*flat_torus()) == 0
    assert genus_from_metric(*flat_torus()) == 1


def test_torus_passes_and_sphere_fails():
    assert ricci_flat_check("T2", 1).holds
    control = ricci_flat_check("S2", 0)
    assert not control.holds and "4*pi" in control.detail


def test_euler_characteristic_and_bad_genus():
    assert [euler_characteristic(g) for g in (0, 1, 2)] == [2, 0, -2]
    with pytest.raises(ValueError):
        euler_characteristic(-1)
