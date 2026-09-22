"""The Leech deep-hole anchor's kill condition, adjudicated.

MEASURED 2026-09-22: THE KILL DOES NOT FIRE, and the honest cost is 24.

The register retained the anchor with a clean kill: if no Gamma-equivariant
linear map 24 -> 7 exists, it is dead as geometry. One does. Because Gamma is
abelian with eight one-dimensional real irreps, and because the 7 carries every
NON-TRIVIAL character exactly once and the trivial one not at all,

    dim Hom_Gamma(24, 7) = 24 - m_trivial(24)

so the dimension vanishes only when Gamma acts trivially on the whole 24 --
which is not an embedding. Over all 512 block-sign actions on E8^3 the single
zero is the trivial action, and every one of the 168 FAITHFUL actions gives
dimension exactly 24.

So equivariance is a real reduction, 168 -> 24 real parameters, a factor of 7.
It is not the reduction to zero the proposal claimed. 24 continuous parameters
is the honest cost of the anchor.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools

import pytest

from metaphysica.simulations.PM.geometry import leech_equivariance as le


def test_gamma_has_exactly_eight_characters():
    chars = le.characters()
    assert len(chars) == le.GROUP_ORDER == 8
    assert len(set(chars)) == 8
    assert all(len(c) == 8 for c in chars)
    assert all(v in (1, -1) for c in chars for v in c)


def test_the_characters_are_closed_under_multiplication():
    """They must form the dual GROUP, or the multiplicity algebra is wrong."""
    chars = set(le.characters())
    for a, b in itertools.product(chars, repeat=2):
        product = tuple(x * y for x, y in zip(a, b))
        assert product in chars, (
            "the character set is not closed under multiplication, so it is "
            "not the dual group of Gamma"
        )


def test_the_seven_is_the_regular_representation_minus_the_trivial():
    """Measured, and it is what makes the whole computation collapse."""
    table = le.multiplicities_of_the_seven()
    trivial = tuple([1] * le.GROUP_ORDER)
    assert table[trivial] == 0, (
        "a Gamma-invariant coordinate direction appeared in the 7; Gamma would "
        "then fix a direction of T^7 and R2 has broken"
    )
    assert sum(table.values()) == 7
    assert all(v == 1 for chi, v in table.items() if chi != trivial), (
        "the 7 non-trivial characters do not each appear exactly once"
    )


def test_the_block_decomposition_accounts_for_all_twenty_four_dimensions():
    chars = le.characters()
    table = le.block_sign_multiplicities(chars[:3])
    assert sum(table.values()) == le.LEECH_RANK == 24
    assert le.N_E8_BLOCKS * le.E8_BLOCK_RANK == 24


def test_a_wrong_number_of_blocks_is_refused():
    with pytest.raises(ValueError):
        le.block_sign_multiplicities(le.characters()[:2])


# ------------------------------------------------------------- the verdict

def test_every_faithful_embedding_gives_dimension_twenty_four():
    report = le.enumerate_block_embeddings()
    assert report["n_embeddings_enumerated"] == 512
    assert report["n_faithful"] == 168
    assert report["faithful_dimensions"] == [24], (
        "faithful block-sign embeddings no longer all give 24: %s"
        % report["faithful_dimensions"]
    )


def test_the_only_zero_is_the_trivial_action():
    """The kill condition, tested where it could actually fire."""
    report = le.enumerate_block_embeddings()
    assert report["n_with_zero_dimension"] == 1
    assert report["zeros_are_all_trivial_actions"] is True, (
        "a NON-trivial action gave a zero equivariant space, which would kill "
        "the anchor; that is a finding, not a test to adjust"
    )


def test_the_dimension_formula_can_return_zero():
    """The computation must be capable of producing the kill, or it proves nothing.

    Feed it a source that is entirely trivial-character and require zero.
    Without this, "the dimension is 24" could mean the function cannot return
    anything else.
    """
    trivial = tuple([1] * le.GROUP_ORDER)
    all_trivial = {chi: (24 if chi == trivial else 0) for chi in le.characters()}
    assert le.equivariant_dimension(all_trivial) == 0, (
        "a representation with no non-trivial character still admits an "
        "equivariant map to the 7, which is impossible"
    )


def test_the_dimension_is_twenty_four_minus_the_invariant_directions():
    """The collapsed formula, checked against the general one at several points."""
    chars = le.characters()
    trivial = tuple([1] * le.GROUP_ORDER)
    for block_chars in itertools.islice(
            itertools.product(chars, repeat=3), 0, 512, 37):
        m = le.block_sign_multiplicities(block_chars)
        assert le.equivariant_dimension(m) == le.LEECH_RANK - m[trivial]


def test_the_verdict_records_a_survival_with_its_cost():
    report = le.equivariance_report()
    assert report["verdict"] == "SURVIVES_WITH_A_MEASURED_COST"
    assert report["naive_parameter_count"] == 168
    assert report["equivariant_parameter_count"] == 24
    assert report["reduction_factor"] == pytest.approx(7.0)
    assert report["scope"], (
        "the result covers block-sign embeddings only; the limit must travel "
        "with it"
    )
    assert report["a4_bar"]


def test_the_one_sixty_eight_coincidence_is_flagged_not_used():
    """168 faithful embeddings and 168 matrix entries are unrelated integers.

    |GL(3,2)| = 7*6*4 = 168 counts EMBEDDINGS; 7*24 = 168 counts real MATRIX
    ENTRIES. The module must say so, because this is exactly the shape the
    register's "two twelves" note warns about.
    """
    report = le.enumerate_block_embeddings()
    assert report["n_faithful"] == 7 * 6 * 4 == 168
    assert le.LEECH_RANK * 7 == 168
    assert "coincidence" in le.__doc__.lower(), (
        "the module does not flag the 168/168 coincidence, so the next reader "
        "may promote it to a structure"
    )
