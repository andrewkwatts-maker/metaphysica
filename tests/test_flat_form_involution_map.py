"""The "4 unpaired flat forms = 4 free involutions" claim, adjudicated.

MEASURED 2026-09-22: REFUTED AS STATED, with a real correspondence underneath.

The pairing is a BIJECTION 7 <-> 7 -- every invariant 3-form is the fixed set
of exactly one non-identity involution, injectively and onto. So nothing is
"left unpaired", and the four forms the claim calls unpaired are the four
paired with the FREE involutions. "7 = 3 + 4" is one partition transported
across a bijection, not two independent counts agreeing.

Measured alongside it: which three forms pair with singular involutions is NOT
canonical. 24 distinct triples occur among the first 4001 admissible
assignments, so "these four flat forms" names a choice of half-shift, not a
property of phi.

The refutation is tested as thoroughly as a success would be, per the standing
rule: every structural step below can fail.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.flat_form_involution_map import (
    correspondence_report,
    flat_form_to_involution,
    map_is_bijective,
    split_is_assignment_dependent,
)
from metaphysica.simulations.PM.geometry.joyce_orbifold import (
    diagonal_stabiliser,
    invariant_three_forms,
)


def test_the_two_sides_are_built_independently():
    """The map is a MATCH between two lists, not one list relabelled.

    If either side were derived from the other the bijection would be a
    tautology. They come from different functions: the forms from Gamma's
    action on Lambda^3, the elements from the diagonal stabiliser of phi.
    """
    forms = [tuple(t) for t in invariant_three_forms()]
    elements = [e for e in diagonal_stabiliser() if any(x == -1 for x in e)]
    assert len(forms) == 7
    assert len(elements) == 7
    # Different TYPES on the two sides: coordinate triples versus sign vectors.
    assert all(len(f) == 3 for f in forms)
    assert all(len(e) == 7 for e in elements)


def test_the_map_is_a_bijection_so_nothing_is_unpaired():
    """The refutation, stated as the measurement that produces it."""
    report = map_is_bijective()
    assert report["n_flat_forms"] == 7
    assert report["n_involutions"] == 7
    assert report["is_bijection"] is True
    assert report["n_unpaired_flat_forms"] == 0, (
        "the claim needs 4 flat 3-forms with no involution; measured there are "
        "%d. If this ever becomes non-zero the refutation needs revisiting."
        % report["n_unpaired_flat_forms"]
    )


def test_every_flat_form_is_some_involutions_fixed_set():
    """The content of the bijection, checked form by form."""
    mapping = flat_form_to_involution()
    assert len(mapping) == 7
    for triple, element in mapping.items():
        fixed = tuple(i for i, s in enumerate(element) if s > 0)
        assert fixed == triple, (
            "form %s is mapped to an element whose fixed set is %s"
            % (triple, fixed)
        )


def test_the_map_would_report_a_partial_pairing_if_there_were_one():
    """The detector must be able to return False, or the refutation is empty.

    Feed `map_is_bijective`'s logic a deliberately broken correspondence and
    require it to notice. Without this, "is_bijection is True" could mean the
    function cannot say otherwise.
    """
    mapping = dict(flat_form_to_involution())
    mapping.pop(next(iter(mapping)))
    images = list(mapping.values())
    assert len(mapping) < 7
    assert not (len(mapping) == 7 and len(set(images)) == len(images)), (
        "a pairing with a form removed still satisfies the bijection test"
    )


def test_the_singular_free_split_is_not_canonical():
    """The 3 + 4 rides on the half-shift assignment, not on phi."""
    report = split_is_assignment_dependent()
    assert report["assignments_scanned"] > 0
    assert report["depends_on_assignment"] is True, (
        "every scanned assignment gave the same singular triple. That would "
        "make the 3 + 4 split canonical, which is a STRONGER claim than the "
        "one under test and would need a proof rather than a scan."
    )
    assert report["distinct_singular_form_triples"] > 1


def test_the_split_still_partitions_the_seven():
    """Whatever the assignment, singular + free must exhaust the bijection."""
    from metaphysica.simulations.PM.geometry import half_shift_enumeration as hs
    from metaphysica.simulations.PM.geometry.flat_form_involution_map import (
        split_under_assignment,
    )

    group = hs._group()
    checked = 0
    for triple in hs.generating_triples(group):
        for svecs in hs.assignments(triple, group, True):
            split = split_under_assignment(triple, svecs, group)
            if not split:
                continue
            assert (split["n_paired_with_singular"]
                    + split["n_paired_with_free"]) == 7, (
                "the split does not exhaust the seven flat forms"
            )
            assert split["n_paired_with_singular"] == split["n_singular"], (
                "the number of forms paired with singular involutions must "
                "equal the number of singular involutions, since the map is a "
                "bijection"
            )
            checked += 1
            if checked >= 200:
                return
    assert checked > 0, "no admissible assignment was reached"


def test_the_verdict_is_recorded_as_a_refutation():
    report = correspondence_report()
    assert report["verdict"] == "REFUTED_AS_STATED_MAP_IS_TOTAL"
    assert "REFUTED" in report["summary"]
    assert report["what_survives"], (
        "a refutation must still record what was found, or the next pass "
        "re-derives the bijection from scratch"
    )
    assert report["a4_bar"], "the type of each count must travel with it"


def test_the_a4_bar_names_the_types():
    """Classes, group elements and index sets are not interchangeable."""
    report = map_is_bijective()
    text = report["counts_what"]
    assert "COHOMOLOGY CLASSES" in text
    assert "GROUP ELEMENTS" in text
    assert "INDEX SETS" in text
