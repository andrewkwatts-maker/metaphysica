"""Established-physics controls: each correspondence holds, each failing control fails."""

from __future__ import annotations

from functools import lru_cache

import pytest

from metaphysica.actions.controls import (
    four_d, g2_zero_modes, kaluza_klein, ricci_flat_compactification as rfc,
)


@lru_cache(maxsize=None)
def _run(corr):
    return corr.run()


def _by_id(items):
    return {c.id: c for c in items}


KK = _by_id(kaluza_klein.correspondences())
FOUR = _by_id(four_d.correspondences())
FOUR_CTL = _by_id(four_d.controls())
RFC = _by_id(rfc.correspondences())
RFC_CTL = _by_id(rfc.controls())


@pytest.mark.parametrize("cid", sorted(KK))
def test_kaluza_klein_correspondences_hold(cid):
    assert _run(KK[cid]).holds


def test_kaluza_klein_control_without_phi_squared_fails():
    assert not _run(kaluza_klein.control()).holds


@pytest.mark.parametrize("cid", sorted(FOUR))
def test_four_d_correspondences_hold(cid):
    assert _run(FOUR[cid]).holds


@pytest.mark.parametrize("cid", sorted(FOUR_CTL))
def test_four_d_controls_fail(cid):
    assert not _run(FOUR_CTL[cid]).holds


@pytest.mark.parametrize("cid", sorted(RFC))
def test_ricci_flat_correspondences_hold(cid):
    assert _run(RFC[cid]).holds


@pytest.mark.parametrize("cid", sorted(RFC_CTL))
def test_ricci_flat_controls_fail(cid):
    assert not _run(RFC_CTL[cid]).holds


def test_sphere_adds_two_over_r_squared():
    import sympy as sp
    assert sp.simplify(rfc.sphere_excess() - 2 / rfc.R_S2 ** 2) == 0


def test_g2_counting_holds_and_swapped_control_fails():
    assert g2_zero_modes.correspondence().run().holds
    assert not g2_zero_modes.control().run().holds
