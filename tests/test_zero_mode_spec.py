"""The zero-mode docking spec: a specification, and it must stay one.

The single most important property of this module is what it does NOT do. It
produces no wavefunction and no Yukawa number, and the tests below are mostly
there to keep it that way: a future pass that "implements" it by fabricating a
mode would retire 13 FLAVOUR ledger rows for nothing.

MEASURED 2026-09-22: of 8 required structures, 1 exists, 3 are partial or
specifiable, and 4 are missing entirely. The precise missing object is a
**codimension-7 conical point**. The enumerated loci are 3-dimensional A_1
families of codimension 4 -- gauge enhancement, not chirality -- and the
enumeration contains no codimension-7 point at any admissible assignment.
Independently, disjointness IS the admissibility predicate, so
intersection-localised couplings have no point to live on anywhere Joyce
applies.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry import zero_mode_spec as zms


# --------------------------------------------- it is a spec and must stay one

def test_it_declares_itself_a_specification():
    report = zms.spec_report()
    assert report["this_is_a_specification"] is True
    assert report["produces_no_yukawa"] is True


def test_no_function_returns_a_coupling_or_a_wavefunction():
    """Guard against a later pass quietly turning the spec into a claim."""
    report = zms.spec_report()
    forbidden = ("yukawa_value", "coupling", "wavefunction", "Y_ijk",
                 "overlap_value", "mode")
    for key in report:
        assert key not in forbidden, (
            "the spec has grown a key that looks like a computed result: %s"
            % key
        )
    assert report["what_must_not_be_done"], (
        "the prohibition must be stated in the module, not only in a test"
    )


# ------------------------------------------------------ the structure census

def test_every_structure_states_whether_it_exists():
    for item in zms.required_structures():
        assert item["exists_today"] in (True, False, "PARTIAL", "SPECIFIABLE"), (
            "%s has an unreadable existence state: %r"
            % (item["name"], item["exists_today"])
        )
        assert item["what"] and item["computed_against"]
        if item["exists_today"] is not True:
            assert item["gap"], (
                "%s is not present but states no gap" % item["name"])


def test_the_census_is_one_present_three_partial_four_missing():
    report = zms.spec_report()
    assert report["n_structures_required"] == 8
    assert report["n_present"] == 1
    assert report["n_partial"] == 3
    assert report["n_missing_entirely"] == 4
    assert (report["n_present"] + report["n_partial"]
            + report["n_missing_entirely"]) == report["n_structures_required"]


def test_the_singular_locus_is_the_one_thing_that_exists():
    present = [s["name"] for s in zms.required_structures()
               if s["exists_today"] is True]
    assert present == ["the singular locus"]


def test_the_wavefunctions_and_the_operator_are_both_missing():
    missing = {item["name"] for item in zms.missing_objects()}
    assert "the zero-mode wavefunctions" in missing
    assert "the Dirac operator" in missing
    assert "codimension-7 conical points" in missing


# --------------------------------------------------------- the codimension

def test_the_enumerated_loci_are_codimension_four():
    report = zms.locus_codimension_report()
    assert report["n_families"] == 12
    assert report["locus_dimension"] == 3
    assert report["codimension"] == 4
    assert report["ambient_dimension"] == 7
    assert report["gives"] == "GAUGE_ENHANCEMENT"
    assert report["does_not_give"] == "CHIRAL_MATTER"


def test_there_are_no_codimension_seven_points():
    report = zms.locus_codimension_report()
    assert report["chiral_matter_needs_codimension"] == 7
    assert report["n_codimension_7_points_in_the_enumeration"] == 0, (
        "a codimension-7 point has appeared in the enumeration. That would "
        "unblock the FLAVOUR layer and is a finding, not a test to adjust."
    )


def test_the_codimension_report_states_its_types():
    report = zms.locus_codimension_report()
    assert "DIMENSIONS" in report["counts_what"]
    assert "ORBITS" in report["counts_what"]


# ------------------------------------------------------- the disjointness

def test_disjointness_is_the_admissibility_predicate_not_a_canonical_fact():
    report = zms.why_intersection_couplings_are_unavailable()
    assert report["predicate"] == "half_shift_enumeration.fixed_sets_disjoint"
    assert "every admissible assignment" in report["consequence_pairwise"]
    assert "a fortiori" in report["consequence_triple"]


def test_the_disjointness_claim_matches_the_live_predicate():
    """Check the spec against the code it cites, not against itself."""
    import inspect

    from metaphysica.simulations.PM.geometry import half_shift_enumeration as hs

    source = inspect.getsource(hs.survey_assignment)
    assert "fixed_sets_disjoint" in source, (
        "admissibility no longer turns on disjointness, so the spec's "
        "exclusion of intersection-localised couplings is out of date"
    )


def test_the_exclusion_states_its_scope():
    report = zms.why_intersection_couplings_are_unavailable()
    assert "INTERSECTION-LOCALISED" in report["scope"]


# ----------------------------------------------------------- the blockage

def test_the_thirteen_flavour_rows_are_named_live():
    report = zms.spec_report()
    assert report["n_flavour_rows_blocked"] == 13
    assert len(report["flavour_rows_blocked"]) == 13


def test_the_precise_missing_object_is_the_conical_point():
    report = zms.spec_report()
    assert "codimension-7" in report["the_precise_missing_object"]
    assert "conical" in report["the_precise_missing_object"].lower()


def test_something_concrete_is_identified_as_doable_today():
    """A spec that says only 'everything is missing' helps nobody."""
    report = zms.spec_report()
    assert "Eguchi-Hanson" in report["what_could_be_done_today"]
    assert "does not unblock" in report["what_could_be_done_today"], (
        "the one doable item must be honest about not unblocking a row"
    )
