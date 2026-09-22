"""The preferred path, the b_3 candidate sweep, and the Joyce table gate.

Three things are pinned here. That the preferred path is a VIEW over the forks
and cannot drift from them. That the sweep and the comparison machinery obey
variants.py's anti-tuning rule -- report everything, order by name, never
select. And that the Joyce gate refuses an uncited table rather than trusting
it, which is the whole reason it exists.
"""

from __future__ import annotations

import os

import pytest

from metaphysica.simulations.core.preferred_path import (
    PREFERRED_PATH_NAME,
    compare_states,
    digest_of,
    history_entry,
    is_on_preferred_path,
    preferred_selection,
    snapshot,
)


# ------------------------------------------------------- the preferred path


def test_the_preferred_path_is_a_view_over_the_forks():
    """Not a second store: every entry is the fork's own adopted option."""
    from metaphysica.simulations.core.variants import FORKS

    selection = preferred_selection()
    assert set(selection) == set(FORKS)
    for fid, option in selection.items():
        assert option == FORKS[fid].default(), (
            "%s: preferred path says %s but the fork adopts %s"
            % (fid, option, FORKS[fid].default())
        )


def test_the_snapshot_declares_what_generation_should_use():
    snap = snapshot()
    assert snap["preferred_path_name"] == PREFERRED_PATH_NAME
    assert "preferred_selection" in snap["what_generation_should_use"]
    assert snap["n_forks"] == len(snap["preferred_selection"])
    assert snap["open_forks"], "some forks must still be open"


def test_a_clean_environment_is_on_the_preferred_path(monkeypatch):
    from metaphysica.simulations.core.variants import FORKS, _ENV_PREFIX

    for fid in FORKS:
        monkeypatch.delenv(_ENV_PREFIX + fid.upper(), raising=False)
    on_path, departures = is_on_preferred_path()
    assert on_path, "unexpected departures: %s" % departures


def test_an_override_is_detected_as_a_departure(monkeypatch):
    from metaphysica.simulations.core.variants import _ENV_PREFIX

    monkeypatch.setenv(_ENV_PREFIX + "RE_T_ADOPTION", "computed_vacuum")
    on_path, departures = is_on_preferred_path()
    assert not on_path
    assert departures["re_t_adoption"]["active"] == "computed_vacuum"


def test_the_digest_separates_states_and_is_stable():
    a = preferred_selection()
    b = dict(a)
    b["re_t_adoption"] = "computed_vacuum"
    assert digest_of(a) == digest_of(dict(a)), "digest must be order-stable"
    assert digest_of(a) != digest_of(b)


def test_history_entry_carries_the_state_but_stamps_no_time():
    entry = history_entry("unit-test", notes="pinned")
    assert entry["label"] == "unit-test"
    assert entry["active_digest"]
    assert "timestamp" not in entry and "generated_at" not in entry


# ------------------------------------------------------------ comparison


def test_comparison_shows_what_moves_without_selecting():
    a = preferred_selection()
    b = dict(a)
    b["re_t_adoption"] = "computed_vacuum"
    result = compare_states(a, b)
    assert result["verdict"] == "NO_SELECTION_MADE"
    assert "never by agreement" in result["ordering"]
    names = [r["observable"] for r in result["rows"]]
    assert names == sorted(names), "rows must be ordered by name"
    re_t = [r for r in result["rows"] if r["observable"] == "racetrack_Re_T"]
    assert re_t, "the Re(T) observable must still be reported"
    # delta 0.0 measured 2026-09-22, b3_seed adoption (it moved before).
    # The switch is not broken, it is INERT: the published seed is now
    # b_3 = 43, the declared racetrack has no minimum there, and
    # computed_vacuum takes its documented fallback to the calibration. The
    # cause is pinned in test_the_re_t_switch_is_inert_under_the_adopted_seed.
    # If a minimum ever returns, this row moves and this fires.
    assert re_t[0]["delta"] == 0.0
    assert re_t[0]["state_a"] == re_t[0]["state_b"]


def test_comparison_restores_the_environment(monkeypatch):
    from metaphysica.simulations.core.variants import _ENV_PREFIX

    key = _ENV_PREFIX + "RE_T_ADOPTION"
    monkeypatch.delenv(key, raising=False)
    a = preferred_selection()
    b = dict(a)
    b["re_t_adoption"] = "computed_vacuum"
    compare_states(a, b)
    assert os.environ.get(key) is None, "comparison leaked an override"


# --------------------------------------------------------- the b_3 sweep


def test_the_sweep_reports_every_candidate_and_selects_none():
    from metaphysica.simulations.PM.geometry.b3_candidate_sweep import (
        CANDIDATES,
        sweep,
    )

    result = sweep()
    assert result["verdict"] == "NO_SELECTION_MADE"
    assert result["n_candidates"] == len(CANDIDATES)
    values = [r["b3"] for r in result["rows"]]
    assert values == [c[0] for c in CANDIDATES], (
        "rows must stay in declaration order, not be sorted by any residual"
    )
    for row in result["rows"]:
        for banned in ("best", "preferred", "recommended", "closest"):
            assert banned not in str(row).lower()


def test_only_the_flat_seven_is_marked_derived():
    from metaphysica.simulations.PM.geometry.b3_candidate_sweep import sweep

    derived = [r["b3"] for r in sweep()["rows"] if r["is_derived"]]
    assert derived == [7], (
        "only the flat contribution is derived; got %s" % derived
    )


def test_the_structural_constraints_need_no_measurement():
    """The one legitimate narrowing: integrality plus the +2 identity."""
    from metaphysica.simulations.PM.geometry.b3_candidate_sweep import (
        structural_constraints,
    )

    result = structural_constraints()
    assert result["status"] == "CONDITIONAL"
    assert len(result["conditions"]) >= 2
    assert "not anchor-shopping" in result["what_it_is_not"]
    if result["unique"]:
        assert result["value_if_unique"] == 24


def test_the_sensitivity_report_is_not_a_ranking():
    from metaphysica.simulations.PM.geometry.b3_candidate_sweep import (
        sensitivity_report,
    )

    result = sensitivity_report()
    keys = list(result["fractional_change_per_unit_b3"])
    assert keys == sorted(keys), "must be ordered by name, not magnitude"
    assert "not by magnitude" in result["note"]


def test_w0_barely_responds_to_b3():
    """Recorded so the earlier finding cannot be quietly forgotten."""
    from metaphysica.simulations.PM.geometry.b3_candidate_sweep import (
        sensitivity_report,
    )

    changes = sensitivity_report()["fractional_change_per_unit_b3"]
    assert changes["w0"] < 0.01, (
        "w_0 moves %.4f per unit b_3; the 'w_0 cannot discriminate' finding "
        "needs revisiting" % changes["w0"]
    )


# ------------------------------------------------------ the Joyce gate


def test_the_gate_is_closed_and_publishes_no_betti_numbers():
    from metaphysica.simulations.PM.geometry.joyce_contributions import (
        gate_report,
        reachable_betti,
    )

    gate = gate_report()
    assert gate["active"] is False
    assert "invent" in gate["refuses_to"]
    result = reachable_betti()
    assert result["decided"] is False
    assert "b3_24_reachable" not in result
    assert result["flat_b3"] == 7
    assert "at least 6 families" in result["unconditional_bound"]


def test_an_uncited_table_is_refused():
    """The failure mode the gate exists to prevent."""
    from metaphysica.simulations.PM.geometry.joyce_contributions import (
        validate_table,
    )

    assert validate_table(None)["valid"] is False
    assert validate_table({"entries": {}})["valid"] is False
    no_cite = {"source": "somewhere",
               "entries": {"T3": {"b2": 1, "b3": 3, "citation": ""}}}
    verdict = validate_table(no_cite)
    assert verdict["valid"] is False
    assert "citation" in verdict["reason"]


def test_a_properly_cited_table_validates():
    """And the validator must be capable of accepting, or it is vacuous."""
    from metaphysica.simulations.PM.geometry.joyce_contributions import (
        validate_table,
    )

    good = {
        "source": "a real reference",
        "entries": {
            "T3": {"b2": 1, "b3": 3, "citation": "thm X"},
            "T3_reflected": [
                {"b2": 1, "b3": 2, "citation": "thm Y, resolution 1"},
                {"b2": 2, "b3": 1, "citation": "thm Y, resolution 2"},
            ],
        },
    }
    verdict = validate_table(good)
    assert verdict["valid"] is True, verdict["reason"]
    assert verdict["family_types"] == ["T3", "T3_reflected"]


def test_the_gate_needs_both_the_fork_and_a_table(monkeypatch):
    """Flipping the fork alone must not open the gate."""
    from metaphysica.simulations.core.variants import _ENV_PREFIX
    from metaphysica.simulations.PM.geometry import joyce_contributions

    monkeypatch.setenv(_ENV_PREFIX + "JOYCE_CONTRIBUTION_TABLE", "supplied")
    monkeypatch.setattr(joyce_contributions, "load_table", lambda: None)
    assert joyce_contributions.table_is_supplied() is False


# ------------------------------------------------------- the new forks


@pytest.mark.parametrize("fork_id", ["re_t_adoption", "b3_origin",
                                     "joyce_contribution_table"])
def test_each_new_fork_is_declared_and_open(fork_id):
    from metaphysica.simulations.core.variants import FORKS

    fork = FORKS[fork_id]
    assert fork.status == "OPEN"
    assert len(fork.options) >= 2
    assert sum(1 for o in fork.options if o.adopted) == 1
    for option in fork.options:
        assert len(option.consequence) > 40


def test_the_re_t_switch_is_inert_under_the_adopted_seed(monkeypatch):
    """Both options resolve to the calibration, and the reason is asserted.

    This required computed_vacuum to land more than 5 above the calibration.
    The b3_seed adoption (author ruling 2026-09-22) put b_3 = 43 into the
    published topology, which INVERTS the racetrack hierarchy: the exponent
    a = 2 pi / b_3 is now smaller than b = 2 pi / D_bulk, and the declared
    potential has no minimum left on the scanned range. _resolve_re_t
    therefore takes its documented fallback rather than inventing a vacuum.

    Pinned as measured rather than deleted: the day a minimum returns --
    from a rebuilt topology row or a chi_eff ruling -- every assertion below
    fires and the switch must be re-examined.
    """
    from metaphysica.simulations.core.variants import _ENV_PREFIX
    from metaphysica.simulations.PM.cosmology.baryon_asymmetry import (
        RE_T_CALIBRATED,
        BaryonAsymmetryV18,
    )
    from metaphysica.simulations.PM.cosmology.racetrack_vacuum import (
        _declared_coefficients,
        stationary_points,
    )

    monkeypatch.delenv(_ENV_PREFIX + "RE_T_ADOPTION", raising=False)
    assert BaryonAsymmetryV18._resolve_re_t() == pytest.approx(RE_T_CALIBRATED)

    # the cause, measured 2026-09-22, b3_seed adoption: a = 2 pi / 43 is
    # below b = 2 pi / 26, so the two exponentials no longer race
    a_exponent, b_exponent = _declared_coefficients()[2:]
    assert a_exponent < b_exponent, (
        "the racetrack hierarchy is back; the inertness below no longer "
        "has its recorded cause"
    )
    assert [pt for pt in stationary_points(3) if pt["kind"] == "minimum"] == []

    monkeypatch.setenv(_ENV_PREFIX + "RE_T_ADOPTION", "computed_vacuum")
    switched = BaryonAsymmetryV18._resolve_re_t()
    assert switched == pytest.approx(RE_T_CALIBRATED), (
        "with no minimum to adopt, computed_vacuum must fall back to the "
        "calibration rather than publishing a vacuum nothing computed"
    )


def test_the_racetrack_coefficients_come_from_the_registry():
    """No magic numerals: the exponents are built from registered topology."""
    from metaphysica.simulations.PM.cosmology.racetrack_vacuum import (
        superpotential_export,
    )

    export = superpotential_export()
    if not export.get("available"):
        pytest.skip("arithma not installed")
    provenance = export["environment_provenance"]
    assert "topology.elder_kads" in provenance["a"]
    assert "dimensions.D_bulk" in provenance["b"]


def test_arithma_builds_and_exports_the_superpotential():
    """Formula building and export go through Arithma, with exact derivatives."""
    from metaphysica.simulations.PM.cosmology.racetrack_vacuum import (
        _arithma_dw,
        superpotential_export,
    )

    export = superpotential_export()
    if not export.get("available"):
        pytest.skip("arithma not installed")
    # symbolic, so the LaTeX carries variables rather than expanded rationals
    assert "e^{" in export["latex"]
    for symbol in ("A", "B", "a", "b", "T"):
        assert symbol in export["latex"]
    assert export["compact"], "compact tree export must be non-empty"
    assert export["roundtrips"] is True
    # the exact derivative agrees with a finite difference of the same W
    exact = _arithma_dw(37.8527)
    assert exact is not None
    # -5.660329399629858e-04 measured 2026-09-22, b3_seed adoption
    # (was -1.4096631e-07). 37.8527 was the stationary point when the
    # exponent read a = 2 pi / 24, which is why dW sat at ~1e-07 there; with
    # b_3 = 43 it is an ordinary point of W and the derivative is finite.
    # Tolerance unchanged at rel=1e-4.
    assert exact == pytest.approx(-5.660329399629858e-04, rel=1e-4)


# ------------------------------------------------- the A4 bar as a check


def test_the_a4_bar_discriminates_the_b3_origins():
    """Added after the first search proved the other checks blind to b3_origin.

    input_24 claims no origin and passes. arc_flag_stabiliser and d4_root_shell
    each ASSERT a geometric origin while being recorded NUMERICAL -- they
    reproduce the integer 24 without exhibiting 24 three-cycles -- so claiming
    one is an internal contradiction. This references no measurement.
    """
    import os

    from metaphysica.simulations.core.switch_search import consistency_checks
    from metaphysica.simulations.core.variants import _ENV_PREFIX

    key = _ENV_PREFIX + "B3_ORIGIN"
    saved = os.environ.get(key)
    try:
        verdicts = {}
        for option in ("input_24", "arc_flag_stabiliser", "d4_root_shell"):
            os.environ[key] = option
            check = [c for c in consistency_checks()
                     if c["name"] == "b3_origin_clears_the_a4_bar"][0]
            verdicts[option] = check["ok"]
    finally:
        if saved is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = saved

    assert verdicts["input_24"] is True, "claiming nothing cannot be a contradiction"
    assert verdicts["arc_flag_stabiliser"] is False
    assert verdicts["d4_root_shell"] is False


def test_consistency_does_not_imply_closure():
    """The finding that matters: the two rulings buy coherence, not closure.

    Every internally consistent combination still carries the same free set.
    If this ever fails, a switch has started reducing the parameter count and
    that is a result worth chasing.
    """
    from metaphysica.simulations.core.free_set import build_free_set
    from metaphysica.simulations.core.switch_search import search

    baseline = build_free_set()["free_set_size"]
    result = search(["g2_form_convention", "re_t_adoption"], cap=8)
    for row in result["rows"]:
        if row["internally_consistent"] and row["free_set_size"] is not None:
            assert row["free_set_size"] == baseline, (
                "a consistent combination changed the free set from %d to %d "
                "-- investigate, this would be closure progress"
                % (baseline, row["free_set_size"])
            )


def test_the_search_still_selects_nothing():
    """Even with one survivor, the module must not crown it."""
    from metaphysica.simulations.core.switch_search import VERDICT, search

    result = search(["g2_form_convention", "re_t_adoption"], cap=8)
    assert result["verdict"] == VERDICT == "NO_SELECTION_MADE"
    assert "never orders by agreement" in result["what_this_reports"]
    digests = [r["digest"] for r in result["rows"]]
    assert digests == sorted(digests), "rows must stay digest-ordered"
