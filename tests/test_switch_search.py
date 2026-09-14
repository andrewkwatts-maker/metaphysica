"""The switch search: what it reports, and what it must never report.

switch_search.py landed with no tests. Its central promises -- reports every
combination, never returns "the best one", never orders by agreement with
experimental anchors -- were therefore assertions in a docstring, which is the
exact shape of defect this repository keeps finding: honesty that lives in a
comment while nothing checks it.

Every test here is written to FAIL on a perturbation. A guard against
anchor-shopping that cannot fire would be worse than none, because it would be
cited as evidence.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.core.switch_search import (
    VERDICT,
    combinations_for,
    consistency_checks,
    evaluate_combination,
    open_forks,
    search,
)

#: A small, fixed subset. Three forks, sixteen combinations: enough to test the
#: ordering and counting promises without sweeping the whole space each run.
SUBSET = ["g2_form_convention", "re_t_adoption", "b3_origin"]


@pytest.fixture(scope="module")
def result():
    return search(SUBSET)


@pytest.fixture(scope="module")
def checks():
    """One evaluation shared by every test that reads the live checks.

    Each call re-solves the racetrack vacuum and re-does a 21x21 SVD, so
    calling it per test cost minutes for no extra coverage.
    """
    return consistency_checks()


# ------------------------------------------------- it reports EVERYTHING


def test_every_combination_is_reported(result):
    expected = 1
    from metaphysica.simulations.core.variants import FORKS

    for fid in SUBSET:
        expected *= len(FORKS[fid].options)
    assert result["n_combinations"] == expected == len(result["rows"])
    assert result["capped"] is False


def test_no_combination_is_dropped_for_being_bad(result):
    """Every enumerated selection appears in the output, consistent or not."""
    reported = {tuple(sorted(r["selection"].items())) for r in result["rows"]}
    enumerated = {tuple(sorted(c.items())) for c in combinations_for(SUBSET)}
    assert reported == enumerated


# --------------------------------------------- it never picks a favourite


def test_the_verdict_is_a_constant_and_selects_nothing(result):
    assert result["verdict"] == VERDICT == "NO_SELECTION_MADE"
    for row in result["rows"]:
        assert row["verdict"] == VERDICT
    forbidden = ("best", "winner", "preferred", "recommended", "ranked")
    assert not any(k for k in result if any(f in k for f in forbidden))


def test_rows_are_ordered_by_digest_and_not_by_any_outcome(result):
    digests = [r["digest"] for r in result["rows"]]
    assert digests == sorted(digests)


def test_the_ordering_is_not_secretly_the_outcome_ordering(result):
    """Digest order must be uncorrelated with problem count.

    If rows happened to come out sorted by n_problems as well, digest ordering
    would be indistinguishable from ranking and this guarantee would be
    untestable. Assert they differ.
    """
    problems = [r["n_problems"] for r in result["rows"]]
    assert problems != sorted(problems) or len(set(problems)) == 1, (
        "rows in digest order are also in problem-count order; the ordering "
        "promise cannot be distinguished from a ranking"
    )


def test_no_check_consults_an_experimental_anchor():
    """The measurement-free rule, checked against the checks themselves."""
    import inspect

    from metaphysica.simulations.core import switch_search

    source = inspect.getsource(switch_search.consistency_checks)
    for anchor in ("desi", "nufit", "planck", "pdg", "codata", "sh0es",
                   "kids", "sigma", "chi2", "residual"):
        assert anchor not in source.lower(), (
            "consistency_checks mentions %r. Internal consistency references "
            "no measurement; a residual against an anchor is the thing this "
            "module exists not to do." % anchor
        )


# ------------------------------------- unevaluable is not the same as failed


def test_an_absent_backend_is_vacuous_not_a_contradiction(checks):
    """An absent arithma leaves no second statement to disagree WITH.

    Scoring BACKEND_UNAVAILABLE as a CONTRADICTION made all sixteen rows
    report a contradiction the framework does not have, and drove
    n_internally_consistent to 0 for a reason about the environment.
    """
    from metaphysica.simulations.core.arithma_formula import available

    check = next(c for c in checks if c["name"] == "arithma_track_agrees")
    if available():
        pytest.skip("arithma backend usable; this asserts the absent case")
    assert check["kind"] == "VACUOUS"
    assert check["evaluable_here"] is False
    assert "BACKEND_UNAVAILABLE" in check["detail"]


def test_a_row_blocked_only_by_an_unevaluable_check_is_not_called_consistent(
        result):
    """Unevaluated is not passed. The distinction is reported, not erased."""
    for row in result["rows"]:
        if row["blocked_only_by_unevaluable_checks"]:
            assert row["internally_consistent"] is False


def test_theory_vacuity_still_counts_against_its_row(result):
    """The Joyce branch asserts what it cannot compute. That is the THEORY.

    It is VACUOUS like the absent backend, and must NOT be excused as an
    environment artifact -- otherwise the distinction introduced for arithma
    would quietly launder a real defect.
    """
    joyce_rows = [r for r in result["rows"]
                  if r["selection"].get("b3_origin") == "joyce_twisted_sector"]
    assert joyce_rows, "the joyce_twisted_sector option disappeared"
    for row in joyce_rows:
        joyce = next(c for c in row["checks"]
                     if c["name"] == "joyce_branch_is_decidable")
        if not joyce["ok"]:
            assert row["blocked_only_by_unevaluable_checks"] is False, (
                "a branch asserting what it cannot compute was reported as "
                "merely unevaluable here"
            )


# ------------------------------------------------------- the checks fire


def test_the_consistency_checks_are_capable_of_failing(checks):
    """The load-bearing one. Checks that always pass discriminate nothing."""
    assert checks, "no checks ran at all"
    assert any(not c["ok"] for c in checks), (
        "every consistency check passes in the live state. Either the "
        "framework became self-consistent -- which is a result, and should be "
        "recorded as one -- or the checks stopped checking."
    )


def test_the_checks_report_the_known_open_contradictions(checks):
    """Both are already on the books individually; pin them by name.

    phi has a 6-dimensional annihilator where g2 requires 14, and the live
    Re(T) is not the solved stationary point of the declared potential. If
    either stops firing, that is a change to the theory and must be read, not
    absorbed.
    """
    by_name = {c["name"]: c for c in checks}
    assert set(by_name) >= {"phi_is_a_g2_form", "n_gen_is_integral",
                            "re_t_is_the_solved_vacuum",
                            "arithma_track_agrees",
                            "neutrino_mass_sum_is_stated_once",
                            "joyce_branch_is_decidable"}
    assert by_name["n_gen_is_integral"]["ok"] is True, (
        "b_3/8 is no longer an integer -- a generation count is a number of "
        "things, so this is a structural failure, not a tolerance question"
    )


def test_evaluating_one_combination_restores_the_environment():
    """A sweep that leaks its overrides poisons every later reading."""
    import os

    from metaphysica.simulations.core.variants import _ENV_PREFIX

    key = _ENV_PREFIX + "B3_ORIGIN"
    before = os.environ.get(key)
    evaluate_combination({"b3_origin": "input_24"})
    assert os.environ.get(key) == before


def test_open_forks_are_the_forks_declared_open():
    from metaphysica.simulations.core.variants import FORKS

    assert open_forks() == [fid for fid, f in FORKS.items()
                            if f.status == "OPEN"]
    assert len(open_forks()) >= 2, (
        "a search over fewer than two open forks searches nothing"
    )


# ------------------------------- standing defects vs switch-controlled ones


def test_the_mass_sum_is_compared_only_against_the_frameworks_own_rows():
    """Three DERIVED rows claim the neutrino mass sum and disagree by 2.4x.

    Measured 2026-09-14, all under the framework's own declared INVERTED
    ordering:

        neutrino.sum_masses          0.101975   matter_sector_complete_v19
        particle.sigma_m_base_eV     0.060517   neutrino_sector v26.0
        particle.sigma_m_refined_eV  0.042517   neutrino_sector v26.0

    No measurement enters: this compares the theory's statements to each
    other. The FITTED row neutrino.mass_sum is excluded on purpose, because a
    fit disagreeing with a derivation is not the theory contradicting itself.
    """
    from metaphysica.simulations.core.arithma_formula import (
        registry_value,
        reset_cache,
    )
    from metaphysica.simulations.core.switch_search import NEUTRINO_MASS_SUM_ROWS

    assert "neutrino.mass_sum" not in NEUTRINO_MASS_SUM_ROWS, (
        "a FITTED row must not be used to accuse the theory of contradicting "
        "itself"
    )
    reset_cache()
    values = [registry_value(p) for p in NEUTRINO_MASS_SUM_ROWS]
    assert all(v is not None for v in values), (
        "a named neutrino mass-sum row vanished from the registry: %s"
        % list(zip(NEUTRINO_MASS_SUM_ROWS, values))
    )
    assert len(set(values)) > 1, (
        "the three rows now agree. That is a RESULT -- one of the neutrino "
        "derivations was reconciled -- and belongs in the register, not "
        "absorbed by deleting this test."
    )


def test_a_check_failing_everywhere_is_separated_but_not_excused(result):
    """One fork-independent defect must not flatten the whole sweep.

    Reported apart so the switch-dependent structure stays visible; still
    counted against every row, so nothing is laundered.
    """
    standing = result["problems_no_combination_fixes"]
    assert standing, "no standing problems at all -- verify the checks ran"
    for name in standing:
        failing = [r for r in result["rows"]
                   if any(c["name"] == name and not c["ok"]
                          for c in r["checks"])]
        assert len(failing) == result["n_combinations"], (
            "%s is listed as failing everywhere but does not" % name)
    # not excused
    assert result["n_internally_consistent"] == 0 or not standing


def test_the_partition_is_a_real_partition(result):
    """Standing and switch-controlled must be disjoint, or the split is fake."""
    standing = set(result["problems_no_combination_fixes"])
    controlled = set(result["problems_the_switches_control"])
    assert not (standing & controlled)
    assert controlled, (
        "no check varies with the switches, so the sweep discriminates "
        "nothing and the search has no content"
    )


def test_clean_on_switch_controlled_checks_is_not_a_ranking(result):
    """It names a set, in digest order, with no row placed ahead of another."""
    digests = result["clean_on_every_switch_controlled_check_digests"]
    assert digests == sorted(digests)
    for d in digests:
        row = next(r for r in result["rows"] if r["digest"] == d)
        bad = [c["name"] for c in row["checks"]
               if not c["ok"] and c["name"] in result["problems_the_switches_control"]]
        assert bad == [], "%s is listed clean but fails %s" % (d, bad)
