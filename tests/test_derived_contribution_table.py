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


def test_b3_24_is_reachable_only_at_b2_15():
    """THE result. (0,16) with exactly one epsilon=-1 family."""
    hits = {p for p in profile_reachable(0, 16) if p[1] == 24}
    assert hits == {(15, 24)}
    for n_t3, n_refl in ((0, 0), (4, 0), (8, 0), (12, 0), (4, 8), (8, 8),
                         (0, 8)):
        assert not any(b3 == 24 for _b2, b3 in
                       profile_reachable(n_t3, n_refl)), (
            "profile (%d,%d) reached b_3 = 24; the uniqueness claim is wrong"
            % (n_t3, n_refl)
        )


def test_the_published_pairs_are_unreachable():
    verdict = b3_verdict(_SURVEY_STUB)
    assert verdict["b3_24_reachable"] is True
    assert verdict["pairs_with_b3_24"] == [(15, 24)]
    assert verdict["pair_4_24_reachable"] is False
    assert verdict["pair_7_24_reachable"] is False
    assert verdict["canonical_12_43_reachable"] is True
    assert verdict["status"] == "CONDITIONAL_ON_DERIVED_TABLE"


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
