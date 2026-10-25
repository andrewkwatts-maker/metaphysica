"""Tests for the exact T^7/Gamma scalar spectrum (C5)."""
import itertools
import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from metaphysica.simulations.PM.geometry import kk_spectrum as kk  # noqa: E402

G = kk.joyce_gamma()


def _permute(sig, g):
    eps, s = g
    ne, ns = [0] * 7, [0] * 7
    for i in range(7):
        ne[sig[i]], ns[sig[i]] = eps[i], s[i]
    return tuple(ne), tuple(ns)


def test_group_is_z2_cubed():
    assert len(G) == 8
    assert all(kk.compose(g, g) == kk._ID for g in G)


def test_zero_mode_is_one():
    # spectrum() raises ArithmeticError if the zero mode is not 1
    kk.spectrum(G, 1)
    assert kk.invariant_count(G, [(0,) * 7]) == 1


def test_trivial_gamma_matches_lattice_counts():
    rows = kk.spectrum(kk.trivial_gamma(), 4)
    assert [(r[1], r[2]) for r in rows] == [(14, 14), (84, 84), (280, 280),
                                            (574, 574)]


def test_multiplicities_are_integers_and_bounded():
    for q, m7, mg in kk.spectrum(G, 8):
        assert isinstance(mg, int) and 0 < mg <= m7


def test_hand_checked_level_one():
    # k = +-e_i; only i = 1..4 survive (eps_i=+1 with s_i=0 on all 4 such g)
    q, m7, mg = kk.spectrum(G, 1)[0]
    assert (q, m7, mg) == (1, 14, 4)


def test_permutation_covariance_and_no_nontrivial_symmetry():
    radii = [Fraction(n) for n in (1, 2, 3, 1, 2, 3, 1)]
    base = kk.spectrum(kk.trivial_gamma(), 5, radii)
    sig = (3, 0, 5, 1, 6, 2, 4)
    perm_r = [None] * 7
    for i in range(7):
        perm_r[sig[i]] = radii[i]
    assert kk.spectrum(kk.trivial_gamma(), 5, perm_r) == base
    Gp = [_permute(sig, g) for g in G]
    assert kk.spectrum(Gp, 5, perm_r) == kk.spectrum(G, 5, radii)
    stab = [s for s in itertools.permutations(range(7))
            if {_permute(s, g) for g in G} == set(G)]
    assert stab == [tuple(range(7))]


def test_bad_input_fails_early():
    with pytest.raises(ValueError):
        kk.spectrum(G, 3, [1] * 6)
    with pytest.raises(ValueError):
        kk.spectrum(G, 3, [1, 1, 1, 1, 1, 1, 0])
    with pytest.raises(ValueError):
        kk.spectrum([], 3)


def test_generic_classes_radius_independent():
    cl = kk.generic_classes(G, 1)
    assert cl[(1, 0, 0, 0, 0, 0, 0)] == (2, 1)
    assert cl[(0, 0, 0, 0, 1, 0, 0)] == (2, 0)
