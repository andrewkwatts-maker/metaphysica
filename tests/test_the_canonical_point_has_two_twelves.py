"""Five modules agree on 3. Two of them say 12 and mean different things.

WHAT THIS GUARDS
================
The canonical point carries a numerical coincidence that invites exactly the
identification the A4 bar forbids:

    b_2               = 12  =  12 families x 1 exceptional 2-class   (H^2)
    K_IJ block size   = 12  =   4 families x 3 three-forms per sector (H^3)

They are equal as integers and unrelated as objects. One counts 2-classes over
every family; the other counts 3-classes within one sector. Writing
"b_2 = the block size" would be true arithmetic and false geometry, and it is the
kind of step that has already cost this project a withdrawn verdict.

What the modules ACTUALLY share is the count 3 -- and that one is real, arrived
at five independent ways:

    rank(Gamma)                              group theory
    number of singular involutions           the enumeration
    sectors in the intersection tensor       resolution combinatorics
    twisted blocks in K_IJ                   the glued metric
    n_gen = b_2 / n_faces                    the generation route

This file pins the agreement that holds and the identification that must not be
made.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def bundle():
    from metaphysica.simulations.PM.geometry.generation_selection import (
        selection_report,
    )
    from metaphysica.simulations.PM.geometry.intersection_tensor import (
        sector_families,
        tensor_report,
    )
    from metaphysica.simulations.PM.geometry.metric_pairing import pairing_report

    k = pairing_report()
    return {
        "k_blocks": k["block_sizes"],
        "k_twisted": [b for b in k["block_sizes"] if b != 7],
        "tensor": tensor_report(),
        "selection": selection_report(),
        "families": sector_families(),
    }


# ------------------------------------------------------- the real agreement

def test_five_independent_modules_agree_on_three(bundle):
    selected = bundle["selection"]["selection_by_b2_route"]["selected"]
    n_gen = selected["b2"] // 4

    assert len(bundle["k_twisted"]) == 3, bundle["k_blocks"]
    assert bundle["tensor"]["n_sectors"] == 3
    assert n_gen == 3
    assert bundle["selection"]["max_generations"] == 3

    from metaphysica.simulations.PM.geometry.generation_selection import (
        singular_involution_census,
    )
    census = singular_involution_census()
    assert census["group_rank"] == 3
    assert census["max_singular_observed"] == 3


def test_the_agreement_is_not_trivially_true(bundle):
    """If every count in sight were 3 this would prove nothing."""
    assert bundle["selection"]["selection_by_b2_route"]["selected"]["b2"] == 12
    assert bundle["k_blocks"][0] == 7
    assert sum(bundle["k_twisted"]) == 36
    assert len({3, 12, 7, 36}) == 4


# ------------------------------------------------------- the two twelves

def test_b2_and_the_k_ij_block_are_both_twelve(bundle):
    """The coincidence itself, stated so the next reader meets it deliberately."""
    b2 = bundle["selection"]["selection_by_b2_route"]["selected"]["b2"]
    assert b2 == 12
    assert bundle["k_twisted"][0] == 12
    assert b2 == bundle["k_twisted"][0]


def test_but_they_count_different_objects(bundle):
    """b_2 is 12 families x 1 two-class; the block is 4 families x 3 three-forms."""
    families = bundle["families"]
    assert len(families) == 12

    # b_2 counts ONE exceptional 2-class per family, over ALL families.
    b2 = bundle["selection"]["selection_by_b2_route"]["selected"]["b2"]
    assert b2 == len(families) * 1

    # A K_IJ twisted block counts THREE 3-forms per family, within ONE sector.
    per_sector = len([f for f in families if f["sector"] == 0])
    assert per_sector == 4
    assert bundle["k_twisted"][0] == per_sector * 3

    # Same integer, different factorisation, different cohomology degree.
    assert len(families) * 1 == per_sector * 3 == 12


def test_the_twisted_total_is_b3_minus_the_flat_part(bundle):
    """36 = 3 sectors x 12, and 43 = 7 + 36. The block size is not b_2."""
    assert sum(bundle["k_twisted"]) == 36
    assert 7 + sum(bundle["k_twisted"]) == 43
    b2 = bundle["selection"]["selection_by_b2_route"]["selected"]["b2"]
    assert sum(bundle["k_twisted"]) != b2


def test_the_degrees_differ_and_the_audit_says_so(bundle):
    """b_2 lives in H^2, the K_IJ blocks in H^3. Different spaces entirely."""
    from metaphysica.simulations.PM.geometry.multilinear_degree_audit import (
        degree_audit_report,
    )

    audit = degree_audit_report()
    assert audit["betti"][2] == 12
    assert audit["betti"][3] == 43
    # the K_IJ pairing is H^3 x H^3 via the metric; the integer tensor uses H^2
    assert audit["metric_free_cubic_shape"] == (12, 12, 43)


def test_a_naive_identification_would_be_caught_by_dimension(bundle):
    """If b_2 WERE the block size, K_IJ would be 7 + 3*12 = 43 by accident.

    It is 43 -- which is exactly why the coincidence is dangerous. The check
    that separates them is that b_2 = 12 counts H^2 while the 36 counts H^3.
    """
    assert 7 + 3 * 12 == 43
    b2 = bundle["selection"]["selection_by_b2_route"]["selected"]["b2"]
    assert 7 + 3 * b2 == 43, (
        "the family relation and the block structure produce the same 43 from "
        "different objects; this is a coincidence to respect, not an identity "
        "to use"
    )
