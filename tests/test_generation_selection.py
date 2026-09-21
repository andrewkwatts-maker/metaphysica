"""Three generations selects the topology, and three is the maximum available.

The framework has treated n_gen = 3 as an output to be reproduced. On the Joyce
family it is better than that: the four reachable profiles give n_gen in
{0, 1, 2, 3}, so three generations picks (b_2, b_3) = (12, 43) UNIQUELY -- and
three is the largest count the construction admits at all.

The candidates are enumerated before the count is applied, which is what makes
this a selection rather than a fit.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.generation_selection import (
    family_profiles,
    generations_by_route,
    select_by_generation_count,
    selection_report,
)


@pytest.fixture(scope="module")
def report():
    return selection_report()


# ------------------------------------------------- the family

def test_one_topological_input_not_two(report):
    """b_2 and b_3 are both functions of n_T3."""
    assert report["family_relation"] == "b_3 = 7 + 3 b_2"
    assert report["family_relation_holds"] is True
    for row in report["table"]:
        assert row["b3"] == 7 + 3 * row["b2"]
        assert row["b2"] == row["n_T3"]


def test_the_family_has_four_distinct_profiles():
    """If they collapsed, 'unique selection' would be trivially true."""
    profiles = family_profiles()
    assert len(profiles) == 4
    assert len({p["b2"] for p in profiles}) == 4
    assert len({p["b3"] for p in profiles}) == 4


# ------------------------------------------------- the selection

def test_three_generations_selects_exactly_one_profile(report):
    result = report["selection_by_b2_route"]
    assert result["n_candidates_before"] == 4
    assert result["n_matching"] == 1
    assert result["is_unique"] is True
    assert (result["selected"]["b2"], result["selected"]["b3"]) == (12, 43)


def test_three_is_the_maximum_the_construction_admits(report):
    assert report["reachable_generation_counts"] == [0, 1, 2, 3]
    assert report["max_generations"] == 3
    assert report["three_is_the_maximum"] is True
    assert "n_T3 <= 12" in report["why_three_is_maximal"]


@pytest.mark.parametrize("n_gen,expected", [(0, 1), (1, 1), (2, 1), (3, 1),
                                            (4, 0), (5, 0)])
def test_the_selector_is_not_vacuous(n_gen, expected):
    """Each reachable count selects one profile; unreachable counts select none.

    A selector that returned one match for every input would prove nothing.
    """
    result = select_by_generation_count(n_gen, "b2_over_faces")
    assert result["n_matching"] == expected, (n_gen, result["matches"])


# ------------------------------------------------- the other route is empty

def test_the_b3_over_dim_O_route_yields_no_integer_anywhere(report):
    """Stronger than '43/8 is not an integer', which is about one point."""
    assert report["selection_by_b3_route"]["n_matching"] == 0
    assert report["b3_route_is_empty_on_this_family"] is True
    for row in report["table"]:
        assert row["b3_over_dim_O_is_integer"] is False, row


def test_the_reason_is_parity_not_arithmetic_accident(report):
    """b_3 is odd at every profile, and 8 divides no odd number."""
    assert "ODD at every profile" in report["why_the_b3_route_is_empty"]
    for row in report["table"]:
        assert row["b3"] % 2 == 1, row


def test_both_routes_are_computed_at_every_profile():
    """The comparison must not be made by evaluating only the favoured one."""
    for prof in family_profiles():
        routes = generations_by_route(prof["b2"], prof["b3"])
        assert set(routes) == {"b2_over_faces", "b3_over_dim_O"}
        for entry in routes.values():
            assert entry["formula"]


# ------------------------------------------------- scope and exclusion

def test_the_adopted_pair_is_not_among_the_candidates(report):
    """A third independent route to excluding (24, 4)."""
    assert report["adopted_pair_is_on_the_family"] is False
    assert 7 + 3 * 4 == 19
    assert all((row["b2"], row["b3"]) != (4, 24) for row in report["table"])


def test_the_scope_is_stated_as_conditional(report):
    """This selects within the construction; it does not prove the construction."""
    scope = report["scope"]
    assert scope.startswith("a selection WITHIN")
    assert "IF the manifold is a Joyce" in scope
    assert "author rulings" in scope


def test_the_premises_are_named_and_traceable(report):
    premises = report["premises"]
    assert set(premises) == {"R1", "A1", "R2"}
    assert "forced" in premises["R1"]
    assert "SU(2)" in premises["A1"]


def test_the_report_declares_what_it_counts(report):
    """A4 bar: n_gen is a class count over a coordinate count."""
    counts = report["counts"]
    assert "cohomology classes" in counts
    assert "moved coordinates" in counts


# ------------------------------------------------- why the cap is 3

@pytest.fixture(scope="module")
def census():
    from metaphysica.simulations.PM.geometry.generation_selection import (
        singular_involution_census,
    )
    return singular_involution_census()


def test_families_are_always_four_per_singular_involution(census):
    """So b_2/4 RECOVERS the singular-involution count; it is not a ratio."""
    assert census["families_always_four_per_singular"] is True
    assert set(census["by_singular_count"]) == {0, 1, 2, 3}
    for n_s, row in census["by_singular_count"].items():
        assert row["assignments"] == row["families_is_four_times"], (n_s, row)


def test_the_singular_involutions_form_a_basis_of_gamma(census):
    """Which is why there can never be more than rank(Gamma) = 3 of them."""
    assert census["n_three_singular_assignments"] > 0
    assert census["n_of_those_independent_over_f2"] == \
        census["n_three_singular_assignments"]
    assert census["singular_set_is_always_a_basis"] is True


def test_no_assignment_exceeds_the_group_rank(census):
    assert census["max_singular_observed"] == census["group_rank"] == 3


def test_the_rank_routine_is_not_trivially_three():
    """A rank function that always returned 3 would make the basis claim empty."""
    from metaphysica.simulations.PM.geometry.generation_selection import (
        rank_over_f2,
    )
    assert rank_over_f2([(1, 0, 0), (0, 1, 0), (0, 0, 1)]) == 3
    assert rank_over_f2([(1, 0, 0), (0, 1, 0), (1, 1, 0)]) == 2   # dependent
    assert rank_over_f2([(1, 0, 0), (1, 0, 0)]) == 1
    assert rank_over_f2([]) == 0


def test_the_chain_and_its_types_are_stated(census):
    """A4 bar: the chain crosses type boundaries and must say so."""
    chain = census["the_chain"]
    assert "rank(Gamma)" in chain and "n_gen" in chain
    counts = census["counts"]
    assert "group ELEMENTS" in counts
    assert "COHOMOLOGY CLASSES" in counts
    assert "not an identification" in counts
