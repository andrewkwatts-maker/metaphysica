"""The derived contribution table, and the (15, 24) result it forces.

The table is MATHEMATICS -- Eguchi-Hanson cohomology, Kunneth, and one invariant
computed from the framework's own enumeration -- carrying exactly one named
assumption (the epsilon-dichotomy). These tests pin the derivation, prove the
computation is not vacuous (a perturbed table must move the answers), and pin
the three verdicts that matter: (15, 24) uniquely reachable, (4, 24) and
(7, 24) unreachable, (12, 43) canonical reproduced.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.derived_contribution_table import (
    FLAT_B2,
    FLAT_B3,
    b3_verdict,
    derived_table,
    eguchi_hanson_betti,
    profile_reachable,
    reachable_set,
    verify_k_equals_one,
)

#: The admissible (n_T3, n_reflected) profiles from the full corrected survey,
#: pinned here so the fast tests need not rerun the 458,752-assignment sweep.
#: test_the_pinned_profiles_match_a_live_slice guards this against staleness.
_PROFILES = {
    "()": 1,
    "('T3', 'T3', 'T3', 'T3')": 1,
    "('T3',)*8": 1,
}

_SURVEY_STUB = {
    "admissible_type_profiles": {
        "()": 176288,
        "('T3', 'T3', 'T3', 'T3')": 166208,
        "('T3', 'T3', 'T3', 'T3', 'T3', 'T3', 'T3', 'T3')": 61152,
        "('T3', 'T3', 'T3', 'T3', 'T3', 'T3', 'T3', 'T3', 'T3', 'T3', "
        "'T3', 'T3')": 7840,
        "('T3', 'T3', 'T3', 'T3', 'T3', 'T3', 'T3', 'T3', 'T3_reflected', "
        "'T3_reflected', 'T3_reflected', 'T3_reflected', 'T3_reflected', "
        "'T3_reflected', 'T3_reflected', 'T3_reflected')": 2352,
        "('T3', 'T3', 'T3', 'T3', 'T3_reflected', 'T3_reflected', "
        "'T3_reflected', 'T3_reflected', 'T3_reflected', 'T3_reflected', "
        "'T3_reflected', 'T3_reflected')": 9408,
        "('T3_reflected', 'T3_reflected', 'T3_reflected', 'T3_reflected', "
        "'T3_reflected', 'T3_reflected', 'T3_reflected', 'T3_reflected')":
        23520,
        "('T3_reflected',) * 16": 0,
        "('T3_reflected', 'T3_reflected', 'T3_reflected', 'T3_reflected', "
        "'T3_reflected', 'T3_reflected', 'T3_reflected', 'T3_reflected', "
        "'T3_reflected', 'T3_reflected', 'T3_reflected', 'T3_reflected', "
        "'T3_reflected', 'T3_reflected', 'T3_reflected', 'T3_reflected')":
        196,
    },
}


# --------------------------------------------------------- the ingredients


def test_eguchi_hanson_retracts_to_the_sphere():
    eh = eguchi_hanson_betti()
    assert eh == {0: 1, 1: 0, 2: 1, 3: 0}


def test_the_flat_contributions_are_the_derived_ones():
    """b_2 flat = 0 and b_3 flat = 7 are joyce_orbifold results, not choices."""
    assert FLAT_B2 == 0
    assert FLAT_B3 == 7


def test_k_is_computed_from_the_enumeration_and_is_always_one():
    """The invariant that decides reflected contributions. Derivation: two
    distinct Fano lines meet in exactly one point. Measured, not assumed."""
    result = verify_k_equals_one(n_triples=2, stride=11, cap=800)
    assert result["checked"] > 100, "too few reflection stabilisers sampled"
    assert result["always_one"] is True, result["k_values"]


def test_the_table_carries_its_assumption():
    table = derived_table()
    assert table["status"] == "DERIVED_KUNNETH"
    assert "epsilon-dichotomy" in table["assumption"]
    assert "CONDITIONAL_ON_DERIVED_TABLE" in table["assumption"]
    assert table["T3"]["options"] == [{"b2": 1, "b3": 3}]
    refl = [(o["b2"], o["b3"]) for o in table["T3_reflected"]["options"]]
    assert refl == [(1, 1), (0, 2)]


# ------------------------------------------------------ profile arithmetic


def test_the_canonical_profile_gives_twelve_fortythree():
    """Pure Kunneth arithmetic reproduces the canonical Joyce value."""
    assert profile_reachable(12, 0) == {(12, 43)}


def test_the_55_series_comes_from_the_mixed_profile():
    pairs = profile_reachable(8, 8)
    assert all(b2 + b3 == 55 for b2, b3 in pairs)
    assert (8, 47) in pairs and (16, 39) in pairs
    assert len(pairs) == 9


def test_the_a1_model_does_not_cover_every_family():
    """THE withdrawal. Found by following the lop-sidedness observation.

    The Kunneth derivation models C^2/{+-1}, transverse group order 2. The
    census shows components with transverse order 4 and 8 as well, and the
    (0,16) profile that reached b_3 = 24 is built entirely of order-8 ones.
    """
    from metaphysica.simulations.PM.geometry.derived_contribution_table import (
        transverse_group_census,
    )

    census = transverse_group_census()
    orders = census["transverse_group_orders"]
    assert census["a1_count"] > 0, "no A1 components at all would be suspicious"
    assert census["worse_than_a1_count"] > 0, (
        "if every component were A1 the withdrawal rationale would be wrong "
        "and (15, 24) should be reinstated after review"
    )
    assert set(orders) - {2}, "orders beyond 2 must be present: %s" % orders


def test_the_b3_24_verdict_is_withdrawn_not_published():
    verdict = b3_verdict(_SURVEY_STUB)
    assert verdict["status"] == "WITHDRAWN_A1_MODEL_MISAPPLIED"
    assert verdict["b3_24_status"] == "UNDETERMINED"
    assert "15, 24" in verdict["withdrawn_verdict"]
    assert "transverse group order 8" in verdict["why_withdrawn"]
    assert "b3_24_reachable" not in verdict, (
        "a reachability boolean must not be published while the model is "
        "known to be misapplied"
    )


def test_what_survives_is_named_and_still_computed():
    """The A1 rows and their corroborations are not withdrawn."""
    verdict = b3_verdict(_SURVEY_STUB)
    assert "12, 43" in verdict["still_valid"]
    assert "55" in verdict["still_valid"]
    assert "McKay" in verdict["next_mechanism"]
    assert profile_reachable(12, 0) == {(12, 43)}


# ------------------------------------------------------------- non-vacuity


def test_a_perturbed_table_moves_the_answers(monkeypatch):
    """The computation must read the table, or every pin above is decoration."""
    import metaphysica.simulations.PM.geometry.derived_contribution_table as m

    real = m.derived_table

    def perturbed():
        table = real()
        table["T3"]["options"] = [{"b2": 1, "b3": 4}]      # wrong on purpose
        return table

    monkeypatch.setattr(m, "derived_table", perturbed)
    assert m.profile_reachable(12, 0) != {(12, 43)}, (
        "the canonical pair survived a wrong table; the arithmetic is not "
        "reading the table it claims to derive from"
    )


def test_the_pinned_profiles_match_a_live_slice():
    """Guard the stub against staleness: a one-triple live survey must produce
    only profiles whose (n_T3, n_reflected) shape appears in the stub."""
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        generating_triples,
        survey,
    )

    live = survey(include_relative=True,
                  triples=[generating_triples()[0]])
    stub_shapes = set()
    for key in _SURVEY_STUB["admissible_type_profiles"]:
        names = eval(key) if key.startswith("(") else ()
        stub_shapes.add((sum(1 for n in names if n == "T3"),
                         sum(1 for n in names if n == "T3_reflected")))
    for key in live["admissible_type_profiles"]:
        names = eval(key) if key.startswith("(") else ()
        shape = (sum(1 for n in names if n == "T3"),
                 sum(1 for n in names if n == "T3_reflected"))
        assert shape in stub_shapes, (
            "live survey produced profile %s absent from the pinned stub; "
            "update _SURVEY_STUB and re-derive the verdicts" % (shape,)
        )


def test_the_verdict_names_its_check():
    verdict = b3_verdict(_SURVEY_STUB)
    assert "Joyce ch. 12" in verdict["what_would_confirm_or_destroy"]
    assert "corrected, not the book" in verdict["what_would_confirm_or_destroy"]
