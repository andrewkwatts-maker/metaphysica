"""The racetrack vacuum on BOTH seeds -- and on the adopted one it does not exist.

HEADLINE FINDING (measured 2026-09-22, by this file's own runs)
===============================================================
The b3_seed fork was ruled on 2026-09-22: ``seed_43_joyce`` -- (b_3, b_2) =
(43, 12) -- is now ADOPTED, and ``seed_24`` -- (24, 4) -- remains runnable as
the labelled off-path branch via ``METAPHYSICA_VARIANT_B3_SEED=seed_24``.

The racetrack exponent rides on the seed, a = 2 pi / b_3, so the ruling moved
it from 0.261799 to 0.146121. The bulk exponent b = 2 pi / D_bulk = 0.241661
did not move. That flips the ordering:

    seed_24        a = 2 pi / 24 = 0.261799  >  b = 0.241661
    seed_43_joyce  a = 2 pi / 43 = 0.146121  <  b = 0.241661

and the racetrack mechanism is exactly the statement a > b. With a < b the
cancellation that makes the minimum moves to negative volume: W vanishes at
Re(T) = ln|A/B| / (a - b), which is +34.419 on the 24 path and -7.255 on the
43 path -- outside the domain, where there is no manifold.

Measured consequence on the adopted (43) path, scanning the module's own
default window Re(T) in (0.5, 300) under BOTH Kahler slopes n = 3 and n = 7:

    * ZERO stationary points of V. Not a shifted minimum -- none at all.
    * ZERO real roots of D_T W = 0. No supersymmetric point exists.
    * V > 0 everywhere sampled and strictly decreasing: a pure runaway to
      V -> 0+ at large volume. No AdS minimum, no dS saddle, no barrier.

So Re(T) = 37.85 was the seed_24 vacuum and has no successor. It is not that
the number moved; the vacuum was deleted by the seed ruling. That is the cost
this file now carries as evidence for the OPEN ``re_t_adoption`` ruling, whose
``computed_vacuum`` branch has nothing left to compute on the adopted seed.

The solver is not broken, and a guard below proves it: feed the same solver the
same two exponents with the ordering restored (a = 2 pi / 26, b = 2 pi / 43)
and a supersymmetric AdS minimum reappears at Re(T) = 10.2085 with its dS
saddle at 15.6529. The absence at 43 is structural -- b_3 = 43 exceeds
D_bulk = 26 -- and is the same broken "+2 identity" (D_bulk - b_3 = -17) that
b3_path already records, arriving here as a lost vacuum.

TWO DRIFTS PINNED BELOW
=======================
1. ``vacuum_report`` / ``_declared_coefficients`` do NOT respond to the fork
   override. They read ``topology.elder_kads`` out of the built
   ``parameters.json`` artifact, so the report is slaved to whatever seed the
   last build wrote (currently 43, ``seed_path: seed_43_joyce``) no matter what
   ``METAPHYSICA_VARIANT_B3_SEED`` says. The per-seed tests here therefore
   drive the branch through the fork-aware declared source,
   ``b3_path.downstream(seed)["racetrack_exponent"]``, and feed it to the
   module's own solver via its ``coeffs`` argument.
2. ``DynamicalLambdaRelaxation.RACETRACK_a`` is still 2 pi / 24. It is the
   module's fallback when the registry row is missing, so on an unbuilt tree
   the racetrack silently reverts to the off-path seed and finds 37.85 again.

Companion to test_racetrack_is_an_ansatz_not_a_vacuum.py: that file pins what
the OLD minimiser was not. This file pins what the corrected solve IS on each
seed, and every statement here must move when the declared coefficients move --
otherwise this file is reporting constants, not solving equations.
"""

from __future__ import annotations

import functools
import math

import pytest

from metaphysica.simulations.PM.cosmology.racetrack_vacuum import (
    INCUMBENT_RE_T,
    scalar_potential,
    stationary_points,
    susy_condition_roots,
    vacuum_report,
)

#: The fork's environment switch, spelled once.
SEED_ENV = "METAPHYSICA_VARIANT_B3_SEED"

#: Both branches of the b3_seed fork. seed_43_joyce is ADOPTED (author ruling
#: 2026-09-22); seed_24 is the labelled off-path branch, still runnable.
SEEDS = ("seed_24", "seed_43_joyce")

KAHLER_SLOPES = (("cy_no_scale", 3), ("g2_seven_thirds", 7))


@functools.lru_cache(maxsize=1)
def _cached_report():
    """The module's own report, solved once. Slaved to the build artifact."""
    return vacuum_report()


@pytest.fixture(scope="module")
def report():
    return _cached_report()


@functools.lru_cache(maxsize=None)
def _solve(seed):
    """Run the module's OWN solver on one seed's declared exponents.

    ``a`` comes from ``b3_path.downstream(seed)["racetrack_exponent"]`` -- the
    fork-aware declared source, 2 pi / b_3 -- because the module's internal
    coefficient read is slaved to the built artifact and cannot see the
    override (pinned in ``test_the_report_is_slaved_to_the_build_artifact``).
    ``A``, ``B`` and the bulk exponent ``b`` are taken unchanged from the
    module's declared block; none of them rides on the seed.
    """
    from metaphysica.simulations.PM.geometry.b3_path import (
        downstream,
        seed_values,
    )

    declared = _cached_report()["declared"]
    a = downstream(seed)["racetrack_exponent"]
    coeffs = (declared["A"], declared["B"], a, declared["b"])
    b3, b2 = seed_values(seed)

    out = {
        "seed": seed,
        "b3": b3,
        "b2": b2,
        "coeffs": coeffs,
        "a": a,
        "b": declared["b"],
        "w_zero_at": (math.log(abs(declared["A"] / declared["B"]))
                      / (a - declared["b"])),
        "branches": {},
    }
    for label, n in KAHLER_SLOPES:
        points = stationary_points(n, coeffs=coeffs)
        minima = [p for p in points if p["kind"] == "minimum"]
        out["branches"][label] = {
            "n": n,
            "points": points,
            "minima": minima,
            "susy_roots": susy_condition_roots(n, coeffs=coeffs),
            "vacuum_re_t": minima[0]["re_t"] if minima else None,
        }
    return out


@pytest.fixture(params=SEEDS)
def branch(request, monkeypatch):
    """One seed of the b3_seed fork, selected through the fork's own switch.

    The ``resolve_path`` assertion is load-bearing: if the fork ever stops
    honouring the environment override, every per-seed pin below would silently
    collapse onto one branch, so it is checked before any physics is read.
    """
    seed = request.param
    monkeypatch.setenv(SEED_ENV, seed)

    from metaphysica.simulations.PM.geometry.b3_path import resolve_path

    assert resolve_path() == seed, (
        "METAPHYSICA_VARIANT_B3_SEED=%s did not select that branch; the "
        "per-seed pins below would all be measuring the same path" % seed
    )
    return _solve(seed)


# ------------------------------------------------------------ the vacuum


def test_whether_the_declared_equations_stabilise_the_modulus(branch):
    """seed_24 stabilises the modulus. seed_43_joyce does not stabilise it.

    b3_seed adoption 2026-09-22. Measured 2026-09-22 by running the module's
    ``stationary_points`` on each seed's declared exponents over its default
    window (0.5, 300).
    """
    # seed_24: one minimum plus one saddle per Kahler slope -- the 37.85
    # branch, physics unchanged by the ruling.
    # seed_43_joyce: ZERO stationary points under either slope. Measured
    # 2026-09-22 from stationary_points(n, coeffs=(1.0, -0.5, 2pi/43, 2pi/26)).
    expected_minima = {"seed_24": 1, "seed_43_joyce": 0}[branch["seed"]]
    expected_points = {"seed_24": 2, "seed_43_joyce": 0}[branch["seed"]]

    for label, _n in KAHLER_SLOPES:
        solved = branch["branches"][label]
        assert len(solved["minima"]) == expected_minima, (
            "%s/%s: expected %d minima, found %d"
            % (branch["seed"], label, expected_minima, len(solved["minima"]))
        )
        assert len(solved["points"]) == expected_points, (
            "%s/%s: expected %d stationary points, found %d"
            % (branch["seed"], label, expected_points, len(solved["points"]))
        )
        if expected_minima:
            assert solved["vacuum_re_t"] > 0
        else:
            assert solved["vacuum_re_t"] is None


def test_whether_a_supersymmetric_point_exists_at_all(branch):
    """D_T W = 0 and full stationarity of V agree -- where either exists.

    b3_seed adoption 2026-09-22. On seed_43_joyce D_T W = 0 has NO real root on
    the module's (1, 300) scan under either slope, so there is no
    supersymmetric point for the stationarity of V to agree with. Measured
    2026-09-22 from susy_condition_roots.
    """
    # seed_24: exactly one SUSY root per slope; n = 3 gives 37.85273132391373
    # and n = 7 gives 37.31409033362665 (measured 2026-09-22, unchanged).
    # seed_43_joyce: none under either slope (measured 2026-09-22).
    expected_roots = {"seed_24": 1, "seed_43_joyce": 0}[branch["seed"]]

    for label, _n in KAHLER_SLOPES:
        solved = branch["branches"][label]
        assert len(solved["susy_roots"]) == expected_roots, (
            "%s/%s: expected %d SUSY roots, found %r"
            % (branch["seed"], label, expected_roots, solved["susy_roots"])
        )
        if expected_roots:
            assert solved["vacuum_re_t"] == pytest.approx(
                solved["susy_roots"][0], rel=1e-3)


def test_whether_there_is_an_ads_minimum_with_a_ds_saddle_above_it(branch):
    """The barrier before runaway is part of the physics -- when there is one.

    b3_seed adoption 2026-09-22. On seed_43_joyce there is neither minimum nor
    barrier: V is strictly positive and strictly decreasing across the whole
    window, a bare runaway. Measured 2026-09-22.
    """
    solved = branch["branches"]["cy_no_scale"]

    if branch["seed"] == "seed_24":
        minimum = solved["minima"][0]
        saddles = [p for p in solved["points"] if p["kind"] != "minimum"]
        assert minimum["V"] < 0, "the SUSY racetrack vacuum must be AdS"
        assert minimum["vacuum_energy_sign"] == "AdS"
        assert any(p["V"] > 0 and p["re_t"] > minimum["re_t"]
                   for p in saddles), (
            "the barrier before runaway is part of the physics and must be "
            "found"
        )
        # Measured 2026-09-22: minimum 37.852731, dS saddle 41.732212.
        assert saddles[0]["re_t"] == pytest.approx(41.7322, abs=0.005)
        return

    # seed_43_joyce, measured 2026-09-22 over (0.5, 300) at n = 3:
    # V(0.7) = +1.486954e-02 falling monotonically to V(300) = +1.064829e-43.
    assert not solved["points"], "a barrier appeared where none was measured"
    sampled = [scalar_potential(t, 0.0, 3, branch["coeffs"])
               for t in (0.7, 1.0, 5.0, 20.0, 37.85, 100.0, 300.0)]
    assert all(v > 0 for v in sampled), (
        "the 43-path potential was measured strictly positive; a negative "
        "sample means an AdS region opened and the finding must be re-measured"
    )
    assert all(later < earlier
               for earlier, later in zip(sampled, sampled[1:])), (
        "the 43-path potential was measured strictly decreasing -- a runaway "
        "with no barrier"
    )


def test_whether_the_axion_direction_is_stabilised_too(branch):
    """A minimum along Re(T) alone would not be a vacuum.

    b3_seed adoption 2026-09-22. seed_43_joyce has no minimum in the Re(T)
    direction either, so there is nothing whose axion curvature to take.
    Measured 2026-09-22.
    """
    minima = branch["branches"]["cy_no_scale"]["minima"]

    if branch["seed"] == "seed_24":
        assert minima[0]["V_axion"] > 0
        assert minima[0]["V_tt"] > 0
    else:
        assert minima == [], (
            "a minimum appeared on the 43 path; the no-vacuum finding recorded "
            "in this file's docstring must be re-measured"
        )


# --------------------------------------------- the six-way Re(T) verdict


def test_the_six_way_re_t_verdict_on_this_seed(branch):
    """Which of the six shipped Re(T) values the equations actually produce.

    b3_seed adoption 2026-09-22. On seed_24 the answer is 37.85 and the
    incumbent registry value is the genuine vacuum -- that is the pre-ruling
    result, unchanged. On seed_43_joyce the answer is NONE OF THEM, not because
    the others are wrong but because the equations have no stationary point to
    offer at all. Measured 2026-09-22.
    """
    solved = branch["branches"]["cy_no_scale"]

    if branch["seed"] == "seed_24":
        # Measured 2026-09-22: 37.852731 at n = 3, the pre-ruling value.
        assert solved["vacuum_re_t"] == pytest.approx(37.85, abs=0.05)
        matched = [c for c in INCUMBENT_RE_T
                   if abs(c - solved["vacuum_re_t"]) / c < 0.01]
        assert matched == [37.85]
        return

    # seed_43_joyce, measured 2026-09-22: no stationary points, so no incumbent
    # can match and the vacuum is undefined rather than relocated.
    assert solved["vacuum_re_t"] is None
    matched = [c for c in INCUMBENT_RE_T
               if any(abs(p["re_t"] - c) / c < 0.01 for p in solved["points"])]
    assert matched == [], (
        "an incumbent Re(T) matched a stationary point on the 43 path, which "
        "was measured to have none"
    )


def test_the_bbn_and_higgs_values_are_not_stationary_points(branch):
    """7.086 and 9.865 are in live use; nothing declared produces them.

    b3_seed adoption 2026-09-22. True on both seeds, but for different reasons,
    and the reason is pinned rather than left implicit: on seed_24 there ARE
    stationary points and none of these is one; on seed_43_joyce there are
    none at all, so the statement would otherwise be vacuous.
    """
    # Measured 2026-09-22: 2 stationary points per slope on seed_24, 0 per
    # slope on seed_43_joyce.
    expected_points = {"seed_24": 2, "seed_43_joyce": 0}[branch["seed"]]

    for label, _n in KAHLER_SLOPES:
        points = branch["branches"][label]["points"]
        assert len(points) == expected_points, (
            "%s/%s: the stationary-point count moved from the measured %d to "
            "%d; the verdict below is no longer about the same solve"
            % (branch["seed"], label, expected_points, len(points))
        )
        for cand in (7.086, 9.865, 1.833, 3.739, 174.03):
            assert not any(abs(p["re_t"] - cand) / cand < 0.01
                           for p in points), (
                "%s appeared as a stationary point under %s/%s; the register's "
                "contradiction entry is stale"
                % (cand, branch["seed"], label)
            )


def test_what_the_kahler_fork_does_to_the_vacuum_on_this_seed(branch):
    """n = 3 -> n = 7 barely moves the vacuum -- where there is one.

    b3_seed adoption 2026-09-22. On seed_43_joyce neither slope has a vacuum,
    so the sensitivity is undefined rather than small: the Kahler fork has
    nothing left to be robust about. Measured 2026-09-22.
    """
    v3 = branch["branches"]["cy_no_scale"]["vacuum_re_t"]
    v7 = branch["branches"]["g2_seven_thirds"]["vacuum_re_t"]

    if branch["seed"] == "seed_24":
        # Measured 2026-09-22: 37.852731 (n = 3) vs 37.314090 (n = 7), giving
        # sensitivity 0.0142299 -- the pre-ruling result, unchanged.
        assert v3 == pytest.approx(37.8527, abs=0.005)
        assert v7 == pytest.approx(37.3141, abs=0.005)
        sensitivity = abs(v3 - v7) / v3
        assert sensitivity == pytest.approx(0.014230, abs=0.0005)
        assert sensitivity < 0.02
    else:
        assert v3 is None and v7 is None, (
            "the 43 path was measured to have no vacuum under either slope"
        )


# ------------------------------------------------ falsifiability guards


def test_the_solve_responds_to_the_ratio_it_depends_on(branch):
    """The solve must read its inputs, on whichever seed is in force.

    B/A -> -0.25 shifts ln|A/B| by ln 2, so W's zero moves by ln(2)/(a - b).
    On seed_24 that displacement is positive and the vacuum follows it. On
    seed_43_joyce the displacement already points out of the domain, so
    doubling it cannot bring a vacuum back -- and the measured zero moves
    further out. Both outcomes are measured, not assumed.
    """
    A, _B, a, b = branch["coeffs"]
    moved = stationary_points(3, coeffs=(A, -0.25, a, b))
    minima = [p for p in moved if p["kind"] == "minimum"]

    if branch["seed"] == "seed_24":
        # Measured 2026-09-22: the minimum moves 37.852731 -> 72.510827 when
        # B/A goes -0.5 -> -0.25.
        assert minima, "changing B/A must not destroy the seed_24 vacuum"
        assert minima[0]["re_t"] == pytest.approx(72.5108, abs=0.005)
        assert abs(minima[0]["re_t"] - 37.85) > 5.0, (
            "the vacuum did not respond to the coefficient it depends on"
        )
    else:
        # b3_seed adoption 2026-09-22. Measured 2026-09-22: still zero
        # stationary points, and W's zero moves -7.255 -> -14.510.
        assert moved == [], (
            "a vacuum appeared on the 43 path at B/A = -0.25; the no-vacuum "
            "finding is ratio-specific and must be re-measured"
        )
        assert math.log(abs(A / -0.25)) / (a - b) == pytest.approx(
            -14.5100, abs=0.005)


def test_the_43_path_has_no_vacuum_because_of_the_ordering_not_the_solver():
    """The absence at b_3 = 43 is structural, and this proves the solver works.

    b3_seed adoption 2026-09-22. Same solver, same two exponents, ordering
    restored (a = 2 pi / D_bulk = 0.241661, b = 2 pi / b_3 = 0.146121): a
    supersymmetric AdS minimum reappears with its dS saddle above it. So the
    empty result on the adopted seed is the racetrack condition a > b failing
    because b_3 = 43 exceeds D_bulk = 26 -- the same broken "+2 identity"
    b3_path records -- and not a solver that stopped finding roots.

    This branch is a DIAGNOSTIC, not a proposal: swapping the exponents is not
    a declared configuration and nothing here adopts it.
    """
    from metaphysica.simulations.PM.geometry.b3_path import downstream

    declared = _cached_report()["declared"]
    a43 = downstream("seed_43_joyce")["racetrack_exponent"]
    assert a43 < declared["b"], (
        "the 43-path exponent is no longer the smaller one; the mechanism "
        "recorded in this file's docstring must be re-measured"
    )

    swapped = (declared["A"], declared["B"], declared["b"], a43)
    points = stationary_points(3, coeffs=swapped)
    minima = [p for p in points if p["kind"] == "minimum"]
    saddles = [p for p in points if p["kind"] != "minimum"]

    # Measured 2026-09-22: minimum Re(T) = 10.208498 (V = -2.6966e-07, AdS),
    # dS saddle 15.652901 (V = +1.4889e-07), single SUSY root
    # 10.208498433918741 sitting on the minimum.
    assert len(minima) == 1
    assert minima[0]["re_t"] == pytest.approx(10.2085, abs=0.005)
    assert minima[0]["V"] < 0
    assert saddles and saddles[0]["re_t"] == pytest.approx(15.6529, abs=0.005)
    assert saddles[0]["V"] > 0
    roots = susy_condition_roots(3, coeffs=swapped)
    assert len(roots) == 1
    assert roots[0] == pytest.approx(minima[0]["re_t"], rel=1e-3)


def test_where_w_vanishes_on_this_seed(branch):
    """W = 0 at ln|A/B| / (a - b) -- inside the domain on 24, outside on 43.

    b3_seed adoption 2026-09-22. Cross-checked against the register's recorded
    34.419 on the off-path branch; the adopted branch's -7.255 is measured
    2026-09-22 and is the structural reason the vacuum is gone.
    """
    expected = {
        # register's recorded W = 0 location, unchanged on the off-path branch
        "seed_24": 34.419,
        # measured 2026-09-22 under the adopted seed: negative volume
        "seed_43_joyce": -7.255,
    }[branch["seed"]]
    assert branch["w_zero_at"] == pytest.approx(expected, abs=0.01)

    if branch["seed"] == "seed_43_joyce":
        assert branch["w_zero_at"] < 0, (
            "W's zero is at negative Re(T) on the adopted seed, so the "
            "racetrack cancellation never happens at physical volume"
        )


# ----------------------------------------- what the module itself reads


@pytest.mark.parametrize("seed", SEEDS)
def test_the_report_is_slaved_to_the_build_artifact(seed, monkeypatch, report):
    """DRIFT PINNED: ``vacuum_report`` cannot see the b3_seed override.

    b3_seed adoption 2026-09-22. ``_declared_coefficients`` reads
    ``topology.elder_kads`` out of the built ``parameters.json``, so the
    reported exponent follows whatever seed the last build wrote -- currently
    43 -- under either value of the environment switch. Measured 2026-09-22.
    This is why the per-seed tests above drive the branch through ``b3_path``
    and pass ``coeffs`` explicitly rather than trusting the report.

    The private ``_declared_coefficients`` is imported deliberately: it is the
    exact function whose blindness to the fork is being pinned.
    """
    from metaphysica.simulations.PM.cosmology.racetrack_vacuum import (
        _declared_coefficients,
    )
    from metaphysica.simulations.PM.geometry.b3_path import (
        downstream,
        resolve_path,
    )

    monkeypatch.setenv(SEED_ENV, seed)
    assert resolve_path() == seed, "the fork stopped honouring its own switch"

    _A, _B, a, _b = _declared_coefficients()
    assert a == report["declared"]["a"], (
        "the declared exponent moved with the fork override; the drift "
        "recorded in this file's docstring is fixed, and the per-seed tests "
        "should now read the module directly instead of passing coeffs"
    )

    if seed == "seed_24":
        off_path = downstream(seed)["racetrack_exponent"]
        assert a != pytest.approx(off_path), (
            "seed_24 is the OFF-path branch, yet the report followed it"
        )


def test_the_artifact_seed_is_the_adopted_one(report):
    """The build the report reads must be the ruled seed's build.

    b3_seed adoption 2026-09-22: ``topology.elder_kads`` is 43 with
    ``metadata.seed_path = seed_43_joyce``, so a = 2 pi / 43 = 0.146121.
    Measured 2026-09-22 from the parameter artifact and vacuum_report.
    """
    from metaphysica.simulations.core.parameter_artifact import parameter_value
    from metaphysica.simulations.PM.geometry.b3_path import seed_values

    registered = parameter_value("topology.elder_kads")
    adopted_b3, _b2 = seed_values("seed_43_joyce")
    assert registered == adopted_b3
    assert report["declared"]["a"] == pytest.approx(
        2.0 * math.pi / adopted_b3, rel=1e-12)
    assert report["declared"]["B_over_A"] == pytest.approx(-0.5)


def test_the_declaring_modules_exponent_follows_the_fork(monkeypatch):
    """DRIFT HEALED (same day it was pinned): RACETRACK_a is now a property
    reading the live seed fork, never a frozen literal.

    The drift this test originally pinned: the class constant carried
    2 pi / 24, so on an unbuilt tree the racetrack silently reverted to the
    off-path seed and found the 37.85 vacuum again while the fork said 43.
    Fixed by making RACETRACK_a a property over b3_path; this test now pins
    the FIX on both branches so the literal cannot quietly come back. The
    bulk exponent's fallback stays a constant: b = 2 pi / D_bulk does not
    ride on the seed.
    """
    from metaphysica.simulations.PM.cosmology.dynamical_lambda import (
        DynamicalLambdaRelaxation,
    )
    from metaphysica.simulations.PM.geometry.b3_path import downstream

    monkeypatch.delenv("METAPHYSICA_VARIANT_B3_SEED", raising=False)
    adopted = downstream("seed_43_joyce")["racetrack_exponent"]
    assert DynamicalLambdaRelaxation().RACETRACK_a == pytest.approx(
        adopted, rel=1e-12), (
        "the exponent no longer follows the adopted seed; a frozen literal "
        "is back"
    )

    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_24")
    off_path = downstream("seed_24")["racetrack_exponent"]
    assert DynamicalLambdaRelaxation().RACETRACK_a == pytest.approx(
        off_path, rel=1e-12), (
        "the exponent does not follow the off-path override"
    )

    assert DynamicalLambdaRelaxation.RACETRACK_b == pytest.approx(
        _cached_report()["declared"]["b"], rel=1e-12), (
        "the bulk exponent does not ride on the seed and must still agree"
    )


def test_the_report_does_not_adopt(report):
    assert "author" in report["not_adopted"]
    assert "7.086" in report["not_adopted"]


def test_the_potential_is_finite_and_real_everywhere_sampled(branch):
    """Finite on both seeds.

    b3_seed adoption 2026-09-22: the 43 path fails by having no stationary
    point, not by the potential blowing up, so this guard must keep passing on
    both branches. Measured 2026-09-22.
    """
    for t in (0.7, 5.0, 37.85, 120.0):
        for th in (0.0, 3.0):
            for _label, n in KAHLER_SLOPES:
                v = scalar_potential(t, th, n, branch["coeffs"])
                assert math.isfinite(v)
