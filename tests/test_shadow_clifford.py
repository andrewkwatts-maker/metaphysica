"""Tests for the explicit Cl(12,1) shadow Clifford algebra.

These verify by construction what the (s-t) mod 8 table asserts, and pin the
spinor counts the framework relies on.
"""
from __future__ import annotations

import numpy as np
import pytest

from metaphysica.simulations.PM.algebra.shadow_clifford import (
    conjugation_candidates,
    shadow_clifford_report,
    shadow_gammas,
)


def test_thirteen_gammas_of_dimension_64():
    g = shadow_gammas()
    assert len(g) == 13
    assert all(m.shape == (64, 64) for m in g)


def test_clifford_relations_with_one_timelike_direction():
    """{gamma_a, gamma_b} = 2 eta_ab with eta = diag(-1, +1 x 12)."""
    g = shadow_gammas()
    for i, a in enumerate(g):
        for j, b in enumerate(g):
            eta = -1.0 if (i == 0 and j == 0) else (1.0 if i == j else 0.0)
            assert np.allclose(a @ b + b @ a, 2 * eta * np.eye(64), atol=1e-9)


def test_timelike_gamma_squares_to_minus_one():
    g = shadow_gammas()
    assert np.allclose(g[0] @ g[0], -np.eye(64), atol=1e-9)


def test_spacelike_gammas_square_to_plus_one():
    g = shadow_gammas()
    for m in g[1:]:
        assert np.allclose(m @ m, np.eye(64), atol=1e-9)


def test_conjugation_is_quaternionic():
    """Both standard conjugation candidates satisfy B B* = -1.

    This is the explicit verification that a 13D(12,1) shadow admits only
    SYMPLECTIC Majorana spinors -- and hence that any Theta built from the
    Clifford conjugation carries Theta^2 = (-1)^F, which is what
    Bisognano-Wichmann requires for J^2 = +1.
    """
    g = shadow_gammas()
    cands = conjugation_candidates(g)
    assert cands, "no conjugation candidates constructed"
    for name, B in cands.items():
        BB = B @ B.conj()
        lam = BB[0, 0]
        assert np.allclose(BB, lam * np.eye(64), atol=1e-8), f"{name} not scalar"
        assert np.real(lam) < 0, f"{name} should square to -1 (quaternionic)"


def test_signature_invariant_matches_table():
    """(s - t) mod 8 = 3 is the quaternionic class."""
    r = shadow_clifford_report()
    assert r["signature_invariant_s_minus_t_mod_8"] == 3
    assert r["reality_type"] == "quaternionic"


def test_shadow_pair_spinor_is_4096():
    """64 x 64 = 4096 -- the framework's Pneuma spinor count."""
    r = shadow_clifford_report()
    assert r["spinor_dim"] == 64
    assert r["shadow_pair_spinor"] == 4096


def test_report_does_not_overclaim_decision_two():
    """The module must state its own limits: spinor level, not field theory."""
    r = shadow_clifford_report()
    assert "not closed" in r["scope"]
