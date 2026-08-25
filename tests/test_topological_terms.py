"""Tests for the topological cross-shadow coupling.

These pin the two results the interaction sector depends on: that the flux term
is non-vanishing at the orthogonal vacuum (so a cross-shadow coupling exists at
all), and that it obeys an exact selection rule (so the non-vanishing is
structural rather than a lucky choice of indices).

Both directions are tested. An allowed channel must be non-zero AND a forbidden
one must be zero -- checking only the first would leave "42 channels" looking
like an artifact of the enumeration.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from metaphysica.simulations.PM.gauge.topological_terms import (
    CS7Result,
    allowed_channels,
    area_two_form,
    associative_triples,
    cs7_density_epsilon,
    cs7_density_star_phi,
    cs7_result,
    metric_two_form,
    vacuum_comparison,
)
from metaphysica.simulations.PM.geometry.g2_differential import (
    G2DifferentialGeometry,
)


@pytest.fixture(scope="module")
def g2():
    return G2DifferentialGeometry()


# ── the two independent routes ───────────────────────────────────────────────


def test_two_routes_agree_on_random_forms(g2):
    """The epsilon contraction and the *phi route share no code.

    phi ^ omega = <*phi, omega> vol for any 4-form omega, so agreement is a
    genuine cross-check rather than the same computation run twice.
    """
    rng = np.random.default_rng(11)
    for _ in range(5):
        f_a = rng.standard_normal((7, 7))
        f_b = rng.standard_normal((7, 7))
        f_a, f_b = 0.5 * (f_a - f_a.T), 0.5 * (f_b - f_b.T)
        res = cs7_result(f_a, f_b, g2=g2)
        assert abs(res.density_via_epsilon) > 1e-9, "vacuous: density is zero"
        assert res.routes_agree, (
            f"routes disagree by {res.max_route_discrepancy:.3e}"
        )


def test_routes_agree_to_twelve_digits(g2):
    rng = np.random.default_rng(5)
    f_a = rng.standard_normal((7, 7))
    f_b = rng.standard_normal((7, 7))
    f_a, f_b = 0.5 * (f_a - f_a.T), 0.5 * (f_b - f_b.T)
    eps_val = cs7_density_epsilon(g2.phi, f_a, f_b)
    star_val = cs7_density_star_phi(f_a, f_b, g2=g2)
    assert eps_val == pytest.approx(star_val, rel=1e-12)


# ── the selection rule ───────────────────────────────────────────────────────


def test_phi_has_seven_associative_triples(g2):
    assert len(associative_triples(g2)) == 7


def test_exactly_42_of_210_channels_survive(g2):
    """7 associative triples x 6 ordered pair-splits of each complement."""
    ch = allowed_channels(g2)
    assert ch["n_disjoint_placements"] == 210
    assert ch["n_allowed"] == 42


def test_every_allowed_channel_has_an_associative_complement(g2):
    """The selection rule, stated as a property of all 42 survivors."""
    ch = allowed_channels(g2)
    for entry in ch["channels"]:
        assert entry["complement_is_associative"], (
            f"channel {entry['f_a']}^{entry['f_b']} is non-zero but its "
            f"complement {entry['complement']} is not associative"
        )


def test_forbidden_channel_vanishes(g2):
    """F_A(0,1) ^ F_B(2,3): complement (4,5,6) is NOT associative.

    Without this, "42 channels are non-zero" could be an artifact -- it is the
    vanishing of the other 168 that makes it a selection rule.
    """
    assert (4, 5, 6) not in associative_triples(g2)
    density = cs7_density_epsilon(
        g2.phi,
        area_two_form(1.0, 1.0, math.pi / 2, 0, 1),
        area_two_form(1.0, 1.0, math.pi / 2, 2, 3),
    )
    assert density == pytest.approx(0.0, abs=1e-12)


def test_allowed_channel_does_not_vanish(g2):
    """The paired positive case: complement (2,4,5) IS associative."""
    assert (2, 4, 5) in associative_triples(g2)
    density = cs7_density_epsilon(
        g2.phi,
        area_two_form(1.0, 1.0, math.pi / 2, 0, 1),
        area_two_form(1.0, 1.0, math.pi / 2, 3, 6),
    )
    assert abs(density) > 1e-9


# ── the vacuum result ────────────────────────────────────────────────────────


def test_topological_coupling_survives_the_orthogonal_vacuum():
    """The result Priority 1 turned on.

    The stabilised vacuum sits at theta = 90 deg on all 12 bridge pairs, which
    kills the metric channel (proportional to cos theta). The topological
    channel couples to the AREA (sin theta) and is maximal there.
    """
    vac = vacuum_comparison()
    assert math.degrees(vac["moduli"]["theta_rad"]) == pytest.approx(90.0, abs=1e-6)

    area = vac["at_vacuum"]["area_route"]
    metric = vac["at_vacuum"]["metric_route"]
    assert abs(area) > 1.0, "the topological coupling vanished at the vacuum"
    assert abs(metric) < 1e-20, "the metric channel should be dead at 90 deg"
    assert abs(area) > 1e20 * abs(metric)


def test_area_channel_is_maximal_at_ninety_degrees():
    """sin^2 theta peaks at 90 deg; the sweep must show it rising to the end."""
    vac = vacuum_comparison()
    areas = [r["area_route"] for r in vac["sweep"]]
    assert areas == sorted(areas), "area channel is not monotone in theta"
    assert areas[-1] == max(areas)


def test_metric_channel_is_minimal_at_ninety_degrees():
    vac = vacuum_comparison()
    metrics = [r["metric_route"] for r in vac["sweep"]]
    assert metrics == sorted(metrics, reverse=True)
    assert metrics[-1] == min(metrics)


def test_forbidden_channel_is_zero_for_every_theta(g2):
    """A forbidden channel says nothing about theta -- it is zero throughout.

    Guards against reading a selection-rule zero as a statement about the
    vacuum, which is exactly the mistake made when this was first swept.
    """
    vac = vacuum_comparison(channel=((0, 1), (2, 3)))
    for row in vac["sweep"]:
        assert row["area_route"] == pytest.approx(0.0, abs=1e-12)
        assert row["metric_route"] == pytest.approx(0.0, abs=1e-12)


# ── scope ────────────────────────────────────────────────────────────────────


def test_result_carries_its_own_scope_limit():
    res = CS7Result(1.0, 1.0, True, 0.0, 1.0, 1.0)
    assert "not a topological invariant" in res.scope


def test_module_does_not_overclaim_topology():
    """Flat R^7 has no non-trivial 7-cycles; this is a number, not an invariant.

    Mirrors test_report_does_not_overclaim_decision_two in the Clifford module:
    scoping the claim is part of the deliverable.
    """
    import metaphysica.simulations.PM.gauge.topological_terms as tt

    doc = tt.__doc__ or ""
    assert "WHAT IS NOT ESTABLISHED" in doc
    assert "NOT A TOPOLOGICAL INVARIANT" in doc.upper()
    assert "compact G2 manifold" in doc
    assert "NOT derived" in doc  # the bridge-to-channel assignment


# ── the Stage-4 report ───────────────────────────────────────────────────────
#
# The evaluation was computable long before it was captured: main() printed
# the answer and the build kept no artifact, so the one result Priority 1 was
# gated on left no record. These tests defend the artifact, and -- more
# importantly -- prove its checks can come out FAIL. A report that always
# writes PASS is the fake-pass disease in report form.


@pytest.fixture(scope="module")
def report(tmp_path_factory):
    import json

    from metaphysica.simulations.PM.gauge.topological_terms import write_report

    out = write_report(
        out_path=tmp_path_factory.mktemp("flux") / "topological_flux.json"
    )
    return json.loads(out.read_text(encoding="utf-8"))


def test_report_schema(report):
    assert report["schema_version"] == 1
    assert report["degrees"] == [3, 2, 2]
    assert report["domain_dim"] == 7
    assert sum(report["degrees"]) == report["domain_dim"], "term must be top-degree"
    assert report["count"] == len(report["checks"])
    assert report["n_pass"] + report["n_fail"] == report["count"]


def test_report_records_the_affirmative_answer(report):
    """The question Priority 1 was gated on, and its scope."""
    assert report["verdict"] == "NONZERO_INTEGRAND_FLAT_R7"
    assert abs(report["density_via_epsilon"]) > 1e-9
    assert report["n_fail"] == 0, [c for c in report["checks"]
                                   if c["status"] == "FAIL"]


def test_report_carries_the_anti_overclaim_scope(report):
    """Scoping the claim is part of the deliverable, not a caveat bolted on."""
    assert "not a topological invariant" in report["scope"]
    assert "compact G2 manifold" in report["not_established"]
    assert "modelling input" in report["not_established"]


def test_report_states_a_kill_condition_in_advance(report):
    """42 of 210 channels are allowed, so the rule can rule the physical
    configuration out -- that is what makes this falsifiable rather than
    merely non-zero."""
    assert "dead" in report["kill_condition"]
    assert "42" in report["kill_condition"]


def test_path_a_is_blocked_not_faked(report):
    """Path A is degree-valid and computable, but no 13D C_3 is derived.

    The report must say so rather than carry a number produced from an
    invented ansatz -- the Kahler-Ricci ruling applies here too. If a C_3
    on the 13D shadow is ever derived, this status changes and the
    Path-A-vs-B ruling becomes decidable on computed evidence.
    """
    path_a = report["path_a_boundary13"]
    assert sum(path_a["degrees"]) == path_a["domain_dim"] == 13
    assert path_a["degree_valid"] is True
    assert path_a["status"] == "BLOCKED_ON_UNDERIVED_INPUT"
    assert "inventing" in path_a["blocker"]
    assert path_a["unblocks_when"]


def test_every_check_has_a_substantive_note(report):
    for check in report["checks"]:
        assert check["status"] in ("PASS", "FAIL")
        assert len(check["note"]) > 20, f"{check['id']} has no substantive note"


def test_report_counts_are_computed_not_asserted(tmp_path, monkeypatch):
    """Mutation: break the kernel and the report must say so.

    Without this, n_pass = 5 could be a literal and the artifact would keep
    announcing success against a broken evaluation -- exactly the failure
    mode the certificate layer was cured of.
    """
    import json

    import metaphysica.simulations.PM.gauge.topological_terms as tt

    real = tt.cs7_result

    def dead_coupling(f_a, f_b, **kwargs):
        res = real(f_a, f_b, **kwargs)
        return tt.CS7Result(0.0, 0.0, True, 0.0, res.volume, 0.0)

    monkeypatch.setattr(tt, "cs7_result", dead_coupling)
    out = tt.write_report(out_path=tmp_path / "mutated.json")
    payload = json.loads(out.read_text(encoding="utf-8"))

    statuses = {c["id"]: c["status"] for c in payload["checks"]}
    assert statuses["coupling_nonzero_at_vacuum"] == "FAIL", (
        "a zero coupling must be reported as FAIL -- if this passes, the "
        "report cannot distinguish the affirmative answer from a null one"
    )
    assert payload["n_fail"] >= 1
    assert payload["n_pass"] == payload["count"] - payload["n_fail"]


def test_selection_rule_check_can_fail(tmp_path, monkeypatch):
    """Mutation on the other independent check: a wrong channel count must
    trip the rule, not be waved through."""
    import json

    import metaphysica.simulations.PM.gauge.topological_terms as tt

    monkeypatch.setattr(
        tt, "allowed_channels",
        lambda g2=None: {"n_disjoint_placements": 210, "n_allowed": 41,
                         "selection_rule": "mutated", "channels": []},
    )
    payload = json.loads(
        tt.write_report(out_path=tmp_path / "m2.json").read_text(encoding="utf-8")
    )
    statuses = {c["id"]: c["status"] for c in payload["checks"]}
    assert statuses["selection_rule_42_of_210"] == "FAIL"


def test_main_exits_nonzero_when_a_check_fails(tmp_path, monkeypatch):
    """The build must trip on a failing evaluation, not log it and continue."""
    import metaphysica.simulations.PM.gauge.topological_terms as tt

    monkeypatch.setenv("METAPHYSICA_OUT", str(tmp_path))
    assert tt.main() == 0

    monkeypatch.setattr(
        tt, "allowed_channels",
        lambda g2=None: {"n_disjoint_placements": 210, "n_allowed": 0,
                         "selection_rule": "mutated", "channels": []},
    )
    assert tt.main() == 1, "a failing check must make the build step fail"
