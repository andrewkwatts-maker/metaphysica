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
    """A falsifier must be on record, and it must be one that can fire.

    The original condition ("if the bridges sit only on non-associative
    complements every channel is forbidden") turned out to describe an
    impossible event -- see test_twelve_bridges_can_never_switch_the_
    coupling_off. It is retired in the artifact and replaced by the
    face-triangle identification, which 35 of 293930 placements satisfy and
    the rest refute.
    """
    assert "dead" in report["kill_condition"]
    assert "35" in report["kill_condition"], (
        "the kill condition must name the size of the surviving set, so a "
        "reader can see it is falsifiable"
    )


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


# ── the coupling graph (bridge-channel assignment evidence) ─────────────────


def test_coupling_graph_is_seven_triangles():
    """The selection rule restated as geometry.

    21 coordinate pairs, 21 allowed couplings, every vertex degree 2 -- so
    a disjoint union of cycles, and it resolves into seven triangles.
    """
    from metaphysica.simulations.PM.gauge.topological_terms import coupling_graph

    g = coupling_graph()
    assert g["n_vertices"] == 21
    assert g["n_edges"] == 21
    assert g["is_two_regular"] is True
    assert g["n_components"] == 7
    assert g["component_sizes"] == [3] * 7


def test_each_triangle_omits_one_point_and_carries_its_three_lines():
    """Triangle T_k is a perfect matching of the six points other than k,
    and its three edges are the three Fano lines through k. Verified by
    enumeration rather than asserted."""
    from metaphysica.simulations.PM.gauge.topological_terms import coupling_graph

    omitted = set()
    for comp in coupling_graph()["components"]:
        assert isinstance(comp["omitted_point"], int), comp
        assert len(comp["support"]) == 6
        assert comp["edges_are_lines_through_omitted_point"] is True
        omitted.add(comp["omitted_point"])
    assert omitted == set(range(7)), "one triangle per coordinate"


def test_twelve_bridges_can_never_switch_the_coupling_off():
    """The retired kill condition, pinned so it cannot be reinstated.

    The Stage-4 report claimed the route dies if the bridges land only on
    non-associative complements. Over all C(21,12) placements the live
    coupling count runs 5..12 and is never 0, so that outcome cannot occur.
    """
    from metaphysica.simulations.PM.gauge.topological_terms import (
        bridge_placement_spectrum,
    )

    s = bridge_placement_spectrum()
    assert s["n_placements"] == 293930
    assert s["minimum"] == 5
    assert s["all_channels_forbidden_is_possible"] is False


def test_maximum_coupling_is_exactly_the_four_complete_triangles():
    """12 live couplings, reached by exactly C(7,4) = 35 placements.

    This is the whole basis of the face-triangle proposal: the framework
    independently carries four faces of three bridges, and four complete
    triangles is the unique way to maximise coupling.
    """
    import math

    from metaphysica.simulations.PM.gauge.topological_terms import (
        bridge_placement_spectrum,
    )

    s = bridge_placement_spectrum()
    assert s["maximum"] == 12
    assert s["n_maximal_placements"] == math.comb(7, 4) == 35
    assert 11 not in s["live_couplings_histogram"], "no placement reaches 11"


def test_report_retires_the_unfireable_kill_condition(report):
    """A kill condition that cannot fire must not be left standing."""
    assert "kill_condition_retired" in report
    assert "CANNOT OCCUR" in report["kill_condition_retired"]
    # and the replacement must name something that can happen
    assert "four" in report["kill_condition"].lower()
    assert "35" in report["kill_condition"]


# ── the decisive test for the face-triangle identification ──────────────────


def _published_bridge_pairs():
    """The bridge -> coordinate-pair map, if the framework publishes one.

    Contract, so this activates the moment the input exists:
      * registry parameter ``geometry.bridge_coordinate_pairs``, OR
      * ``four_face_structure.BRIDGE_COORDINATE_PAIRS``
    either being a sequence of twelve [i, j] pairs indexed by bridge number.
    """
    import json
    import os
    from pathlib import Path

    try:
        from metaphysica.simulations.PM.geometry import four_face_structure as ffs
        pairs = getattr(ffs, "BRIDGE_COORDINATE_PAIRS", None)
        if pairs:
            return [tuple(p) for p in pairs]
    except ImportError:
        pass

    raw = os.environ.get("METAPHYSICA_OUT")
    candidates = []
    if raw:
        candidates.append(Path(raw) / "AutoGenerated" / "parameters.json")
    candidates += [
        Path("H:/Github/PrincipiaMetaphysica/AutoGenerated/parameters.json"),
        Path(__file__).resolve().parents[1] / "AutoGenerated" / "parameters.json",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        params = json.loads(path.read_text(encoding="utf-8"))["parameters"]
        entry = params.get("geometry.bridge_coordinate_pairs")
        if entry and isinstance(entry.get("value"), list):
            return [tuple(p) for p in entry["value"]]
    return None


def test_face_triangle_identification():
    """THE decisive test for docs/BRIDGE_CHANNEL_ASSIGNMENT.md.

    The coupling graph is seven triangles; the twelve bridges reach maximal
    coupling (12) only by occupying four COMPLETE triangles, which happens
    for 35 = C(7,4) of 293930 placements. The framework independently
    carries four faces of three bridges. The proposal is that each face IS a
    triangle.

    This test cannot run yet: the bridge -> coordinate-pair map is the
    modelling input the topological module records as NOT derived, and it is
    absent from the registry (which publishes geometry.n_faces and the four
    face moduli, but no channel assignment). It is written now so that
    supplying that map immediately either confirms or kills the proposal,
    rather than the question being re-opened from scratch later.

    Deliberately NOT skipped-and-forgotten: the skip message states exactly
    what would activate it.
    """
    from metaphysica.simulations.PM.gauge.topological_terms import coupling_graph

    pairs = _published_bridge_pairs()
    if pairs is None:
        pytest.skip(
            "bridge->coordinate-pair map not published; define "
            "geometry.bridge_coordinate_pairs (12 [i,j] pairs) or "
            "four_face_structure.BRIDGE_COORDINATE_PAIRS to activate the "
            "face-triangle check"
        )

    assert len(pairs) == 12, f"expected 12 bridges, got {len(pairs)}"
    assert len(set(pairs)) == 12, "two bridges share a coordinate pair"

    triangles = [
        {tuple(v) for v in comp["vertices"]}
        for comp in coupling_graph()["components"]
    ]
    faces = [pairs[i::4] for i in range(4)]  # standard {i, i+4, i+8} grouping
    for face_idx, face in enumerate(faces):
        assert set(face) in triangles, (
            f"face {face_idx} occupies {sorted(face)}, which is not one of "
            f"the seven triangles -- the face=triangle identification in "
            f"docs/BRIDGE_CHANNEL_ASSIGNMENT.md is FALSIFIED"
        )


def test_maximal_placements_are_exactly_the_four_triangle_unions():
    """Guard the claim the decisive test rests on.

    If the 35 maximal placements were ever NOT four complete triangles, the
    face-triangle proposal would lose its basis even before the mapping
    arrives.
    """
    from itertools import combinations

    from metaphysica.simulations.PM.gauge.topological_terms import coupling_graph

    triangles = [
        {tuple(v) for v in comp["vertices"]}
        for comp in coupling_graph()["components"]
    ]
    unions = {
        frozenset().union(*combo)
        for combo in combinations(triangles, 4)
    }
    assert len(unions) == 35
    assert all(len(u) == 12 for u in unions), "a triangle union is not 12 pairs"


# ── narrowing the four-face choice ──────────────────────────────────────────


def test_four_subsets_split_into_exactly_two_fano_orbits():
    """35 = 7 + 28, computed rather than asserted.

    Choosing four faces is choosing a 4-subset of the seven Fano points
    (each triangle is labelled by the coordinate it omits). Those subsets
    either contain a line or they do not, and the split is 28 / 7.
    """
    from metaphysica.simulations.PM.gauge.topological_terms import (
        face_assignment_candidates,
    )

    d = face_assignment_candidates()
    assert d["n_choices_total"] == 35
    assert d["n_line_containing"] == 28
    assert d["n_generic"] == 7
    assert d["n_line_containing"] + d["n_generic"] == d["n_choices_total"]


def test_every_generic_choice_leaves_exactly_a_line_unchosen():
    """The seven arcs are precisely the complements of the seven lines.

    That is what makes the residual freedom a labelling rather than a
    further structural decision: the candidates are in bijection with the
    lines.
    """
    from metaphysica.simulations.PM.gauge.topological_terms import (
        associative_triples,
        face_assignment_candidates,
    )

    lines = {frozenset(t) for t in associative_triples()}
    candidates = face_assignment_candidates()["generic_candidates"]
    assert len(candidates) == 7
    omitted = set()
    for c in candidates:
        assert c["unchosen_is_a_line"] is True, c
        assert frozenset(c["unchosen_triangles"]) in lines
        omitted.add(frozenset(c["unchosen_triangles"]))
    assert len(omitted) == 7, "the seven candidates omit seven distinct lines"


def test_the_narrowing_is_labelled_as_a_criterion_not_a_derivation():
    """Nothing in the framework forbids three collinear face labels.

    The 7/28 split is a fact; that the generic orbit is the physical one is
    an assumption. It must be carried as such, or a later reader will take
    35 -> 7 for a derived result.
    """
    from metaphysica.simulations.PM.gauge.topological_terms import (
        face_assignment_candidates,
    )

    d = face_assignment_candidates()
    assert d["status"] == "CRITERION_STATED_NOT_DERIVED"
    assert "NOT derived" in d["caveat"]
    assert d["criterion"] and d["residual_freedom"]
