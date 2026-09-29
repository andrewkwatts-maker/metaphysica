"""The reachable family's topology, derived member by member (D-001, D-002).

Pre-registered 2026-09-30 in the site repo's docs/DECISION_LOG.md, committed
before anything here was run.

D-001: Joyce's resolution formula, applied to a representative admissible
assignment of each member, gives b = (1, 0, 4n, 7 + 12n, 7 + 12n, 4n, 0, 1)
for n singular involutions -- the declared pair of every member, Poincare
duality, chi = 0, and every singular component a flat T^3 with b_1 = 3.

D-002: pi_1 is finite on the family exactly at (12, 43). Where it is
infinite, a coordinate fixed by every singular involution is an explicit
witness. On the compact real form that makes (12, 43) the only member with
holonomy exactly G_2 (Joyce's criterion, cited), so n_gen = 3 is an output of
the selection rather than its input.

MEASURED 2026-09-30: the full sweep visits 458,752 assignments, 411,488
admissible (176,288 / 166,208 / 61,152 / 7,840 with n = 0 / 1 / 2 / 3), with no
violation of independence, of the flat ranks 7 / 3 / 1 / 0, or of "pi_1 finite
iff n = 3". It takes about 45 s, so it is a slow test; a capped sweep runs
always.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools

import pytest

from metaphysica.simulations.PM.geometry.family_topology import (
    EXPECTED_FLAT_RANK,
    family_table,
    holonomy_selection,
    independence_sweep,
)
from metaphysica.simulations.PM.geometry.fundamental_group import (
    pi1_finiteness,
    surviving_directions,
)
from metaphysica.simulations.PM.geometry.intersection_tensor import (
    canonical_point,
)
from metaphysica.simulations.PM.geometry.joyce_resolution import (
    _admissible,
    _search_space,
    _singular_of,
    euler_characteristic,
    poincare_duality_holds,
    representative_point,
    resolution_report,
    resolved_betti,
)


@pytest.fixture(scope="module")
def table():
    return {row["path"]: row for row in family_table()}


def _members(table):
    return [row for row in table.values() if row["derived"]]


# ------------------------------------------------------------ D-001

def test_every_member_is_derived_and_matches_its_declared_pair(table):
    members = _members(table)
    assert len(members) == 4
    for row in members:
        assert row["matches_declared"], row


def test_the_resolved_sequence_has_the_predicted_shape(table):
    for row in _members(table):
        n = row["n_singular"]
        assert row["betti"] == {0: 1, 1: 0, 2: 4 * n, 3: 7 + 12 * n,
                                4: 7 + 12 * n, 5: 4 * n, 6: 0, 7: 1}


def test_poincare_duality_and_chi_zero_on_every_profile(table):
    assert len(table) == 5
    for row in table.values():
        assert row["poincare_duality_holds"], row["path"]
        assert row["euler_characteristic"] == 0, row["path"]


def test_the_off_family_seed_is_labelled_declared_not_derived(table):
    row = table["seed_24"]
    assert row["derived"] is False
    assert "DECLARED" in row["label"] and "not derived" in row["label"]


def test_every_singular_component_is_a_flat_three_torus(table):
    for row in _members(table):
        assert row["every_component_is_flat_T3"], row["path"]
        assert row["n_components"] == 4 * row["n_singular"]


def test_the_adopted_point_has_twelve_components_each_with_b1_three():
    """G2 step 1's input: b_1(L_j) = 3 for every component."""
    rep = resolution_report(canonical_point())
    assert rep["n_components"] == 12
    assert rep["component_betti"] == [(1, 3, 3, 1)]
    assert rep["component_b1_values"] == [3]
    assert rep["orbit_sizes"] == [4]
    assert (rep["b2"], rep["b3"]) == (12, 43)


def test_the_duality_and_euler_checks_can_fail():
    """A check that cannot fail is a defect: feed them a non-dual sequence."""
    lopsided = {0: 1, 1: 0, 2: 12, 3: 43, 4: 42, 5: 12, 6: 0, 7: 1}
    assert not poincare_duality_holds(lopsided)
    assert euler_characteristic(lopsided) == -1     # b_4 enters with +


def test_a_non_a1_component_is_refused_rather_than_counted():
    """Pairwise-disjoint but not A1: the Eguchi-Hanson model does not apply,
    and the resolution formula must say so instead of returning numbers."""
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        elements,
        fixed_sets_disjoint,
    )

    for _triple, gens, svecs in _search_space():
        els = elements(gens, svecs)
        singular = _singular_of(els)
        disjoint = all(fixed_sets_disjoint(a[1], b[1])
                       for a, b in itertools.combinations(singular, 2))
        if singular and disjoint and not _admissible(els, singular):
            with pytest.raises(ValueError, match="not A1"):
                resolved_betti({"elements": els, "singular": singular})
            return
    pytest.fail("no disjoint non-A1 assignment found; the survey changed")


def test_representative_three_is_the_canonical_point():
    rep = representative_point(3)
    can = canonical_point()
    assert rep["triple"] == can["triple"]
    assert rep["shifts"] == can["shifts"]


def test_representative_points_are_fresh_objects():
    first = representative_point(2)
    first["singular"].clear()
    assert len(representative_point(2)["singular"]) == 2


def test_there_is_no_fourth_singular_involution():
    with pytest.raises(LookupError):
        representative_point(4)


# ------------------------------------------------------------ D-002

def test_flat_rank_follows_the_singular_span(table):
    for row in _members(table):
        assert row["flat_rank_k"] == EXPECTED_FLAT_RANK[row["n_singular"]]
        assert row["pi1_sides_agree"], row["path"]


def test_pi1_is_finite_exactly_at_the_adopted_pair(table):
    finite = [row["path"] for row in _members(table) if row["pi1_finite"]]
    assert finite == ["seed_43_joyce"]


def test_holonomy_selects_one_member_and_it_predicts_three_generations():
    sel = holonomy_selection()
    assert sel["unique"]
    assert sel["selected"] == (12, 43)
    assert sel["n_gen_at_selection"] == 3
    assert "compact real form" in sel["scope"]
    assert "N = 1" in sel["not_a_discriminator"]


def test_the_witness_refuses_an_inconsistent_singular_element():
    """A 'singular' element with a shift on its own fixed coordinate has no
    fixed point; the witness must not be built on it."""
    signs = (1, 1, 1, -1, -1, -1, -1)
    bogus = {"elements": {}, "singular": [((1, 0, 0), (signs,
                                                     (1, 0, 0, 0, 0, 0, 0)))]}
    with pytest.raises(ValueError, match="no fixed point"):
        surviving_directions(bogus)


def test_the_no_singular_control_keeps_every_direction():
    point = representative_point(0)
    assert surviving_directions(point) == tuple(range(7))
    assert pi1_finiteness(point)["pi1_finite"] is False


def test_capped_sweep_holds():
    out = independence_sweep(max_assignments=20_000)
    assert out["holds"], out["violations"]
    assert out["admissible"] > 0


@pytest.mark.slow
def test_full_sweep_holds_across_every_admissible_assignment():
    out = independence_sweep()
    assert out["visited"] == 458_752
    assert out["admissible"] == 411_488
    assert out["admissible_by_n_singular"] == {0: 176_288, 1: 166_208,
                                               2: 61_152, 3: 7_840}
    assert out["holds"], out["violations"]
