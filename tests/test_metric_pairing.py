"""K_IJ must be non-isotropic, block-structured, and honest about its t-order.

WHY NON-ISOTROPY IS THE CLAIM WORTH TESTING
===========================================
The Leech and E8^3 routes both produced forms proportional to the identity, and
`intersection_tensor` diagnosed why: a shell form carrying a large symmetry group
is forced isotropic by Schur's lemma, so it can encode nothing. K_IJ is built
from a metric rather than a lattice shell and must not share that fate.

THE PREDICATE MUST BE ABLE TO SAY YES
=====================================
Asserting "K is not proportional to the identity" is worth nothing unless the
same rule returns True on something that is. So `is_proportional_to_identity` is
fed c * I directly and must accept it -- that is the test which would fail if the
predicate were hardcoded to False, and it is the specification's "must FAIL if
fed Q proportional to I" read in the only direction that makes it a test.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

sp = pytest.importorskip("sympy")

from metaphysica.simulations.PM.geometry import metric_pairing as mp
from metaphysica.simulations.PM.geometry.eguchi_hanson import l2_norm_squared


@pytest.fixture(scope="module")
def report():
    return mp.pairing_report("orbit_sum")


# --------------------------------------------- the predicate, both ways

def test_the_isotropy_predicate_accepts_a_multiple_of_the_identity():
    """THE GUARD. If this fails the non-isotropy claim below is vacuous."""
    c = sp.Symbol("c", positive=True)
    for n in (3, 7, 43):
        assert mp.is_proportional_to_identity(c * sp.eye(n)) is True
        assert mp.is_proportional_to_identity(sp.eye(n)) is True


def test_the_isotropy_predicate_rejects_things_that_are_not():
    q = sp.eye(3)
    q[1, 1] = 5
    assert mp.is_proportional_to_identity(q) is False
    off = sp.eye(3)
    off[0, 2] = 1
    assert mp.is_proportional_to_identity(off) is False


# ------------------------------------------------------ the matrix

def test_the_pairing_is_forty_three_by_forty_three(report):
    assert report["shape"] == (43, 43)


def test_the_pairing_is_not_proportional_to_the_identity(report):
    """The central result, taken over expressions so it holds for every L."""
    assert report["is_isotropic"] is False
    assert len(report["distinct_diagonal_entries"]) > 1


def test_the_block_sizes_are_seven_twelve_twelve_twelve(report):
    assert report["block_sizes"] == [7, 12, 12, 12]
    assert sum(report["block_sizes"]) == 43


def test_the_flat_entry_is_the_orbifold_volume():
    L, _t = mp.pairing_symbols()
    expected = L ** 7 / mp.orbifold_group_order()
    assert sp.simplify(mp.flat_block_entry() - expected) == 0
    # |Gamma| is read live, not written as 8
    assert mp.orbifold_group_order() == 8


def test_the_twisted_entry_is_the_t3_volume_times_the_eh_norm():
    L, _t = mp.pairing_symbols()
    entry = mp.twisted_block_entry(4, "orbit_sum")
    assert sp.simplify(entry - 4 * L ** 3 * l2_norm_squared()) == 0
    # and the EH norm is the one that module computes, not a copy
    assert sp.simplify(l2_norm_squared() - 8 * sp.pi ** 2) == 0


def test_the_flat_and_twisted_entries_are_different_functions_of_l():
    """Why no scalar can make K isotropic: L^7 against L^3."""
    L, _t = mp.pairing_symbols()
    ratio = sp.simplify(mp.flat_block_entry() / mp.twisted_block_entry(4))
    assert L in ratio.free_symbols, (
        "the block ratio lost its dependence on the modulus, so the blocks "
        "would be comparable by a constant and the isotropy argument fails"
    )


# ---------------------------------------------------- the perturbations

def test_the_entries_move_when_the_orbit_convention_flips():
    """A fork with no effect is a constant wearing a switch's clothes."""
    summed = mp.twisted_block_entry(4, "orbit_sum")
    averaged = mp.twisted_block_entry(4, "orbit_average")
    assert sp.simplify(summed - averaged) != 0
    assert sp.simplify(summed / averaged) == 4


def test_both_conventions_leave_the_pairing_non_isotropic():
    """The fork must be costed, and its cost is not the isotropy verdict."""
    for convention in ("orbit_sum", "orbit_average"):
        assert mp.pairing_report(convention)["is_isotropic"] is False


def test_an_unknown_convention_is_refused():
    with pytest.raises(ValueError, match="orbit_convention"):
        mp.twisted_block_entry(4, "whatever")


def test_a_different_orbit_size_moves_the_twisted_entry():
    """Guards against the orbit size being read and then ignored."""
    assert sp.simplify(mp.twisted_block_entry(2, "orbit_sum")
                       - mp.twisted_block_entry(4, "orbit_sum")) != 0


# ----------------------------------------------- exact vs asymptotic

def test_every_block_carries_its_order_in_t(report):
    orders = report["t_orders"]
    assert orders["flat_block"] == 0
    assert orders["twisted_blocks"] == 0
    assert orders["cross_blocks"] == mp.CROSS_BLOCK_T_ORDER == 2
    for block in report["blocks"]:
        assert "t_order" in block


def test_the_cross_blocks_are_not_claimed_to_vanish_exactly():
    """The specification expected character orthogonality. It does not apply,
    and the module must say so rather than assert an exact zero."""
    structure = mp.block_structure("orbit_sum")
    assert structure["cross_block_value_at_leading_order"] == 0
    assert structure["cross_block_t_order"] == 2
    note = structure["cross_block_is_not_exactly_zero"]
    assert "NOT identically zero" in note
    assert "Character orthogonality does not apply" in note


def test_the_report_says_it_is_asymptotic_not_exact(report):
    assert "ASYMPTOTIC" in report["exact_or_asymptotic"]


def test_the_unbound_modulus_is_declared_rather_than_filled_in(report):
    """L is a modulus the framework does not fix. It must not acquire a value."""
    L, _t = mp.pairing_symbols()
    assert "L" in report["unbound"]
    assert "MODULUS" in report["unbound"]["L"]
    for entry in report["distinct_diagonal_entries"]:
        assert "L" in entry, (
            "a diagonal entry lost its modulus, which means a number was "
            "invented for it"
        )
