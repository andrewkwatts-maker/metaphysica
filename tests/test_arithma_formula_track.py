"""The shared Arithma formula track, and a coverage ratchet.

ArithmaFormula exists so the third track costs a few lines instead of a copied
guard, an ad-hoc environment and a hand-rolled comparison. The tests that matter
here are the ones proving the DRIFT CHECK can fail: a checker that always
reports agreement verifies nothing, which is the defect class this whole
campaign keeps finding.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from metaphysica.simulations.core.arithma_formula import (
    ArithmaFormula,
    arithma_constant,
    available,
    registry_value,
)

pytestmark = pytest.mark.skipif(not available(),
                                reason="arithma backend unusable (stub or absent)")


def _simple() -> ArithmaFormula:
    return ArithmaFormula(
        name="half_of_b3",
        latex_hint="b_3 / 2",
        build=lambda E, v: E.div(v("b3"), E.number(2.0)),
        inputs={"b3": "topology.elder_kads"},
        python=lambda b3: b3 / 2.0,
    )


# ------------------------------------------------------------- the basics


def test_a_declared_formula_builds_exports_and_evaluates():
    f = _simple()
    assert f.expression() is not None
    assert "b3" in f.latex()
    assert f.compact()
    assert f.roundtrips() is True
    assert f.evaluate() == pytest.approx(12.0)


def test_the_exact_derivative_is_symbolic_not_a_difference():
    """d(b3/2)/d b3 = 1/2 exactly, for any b3."""
    f = _simple()
    assert f.derivative("b3") == pytest.approx(0.5, abs=1e-12)


def test_numbers_come_from_the_registry_not_the_formula():
    f = _simple()
    assert f.provenance() == {"b3": "topology.elder_kads"}
    assert registry_value("topology.elder_kads") == pytest.approx(24.0)


def test_mathematical_constants_come_from_arithmas_table():
    """pi is not a physics parameter and must not be a literal either."""
    assert arithma_constant("pi") == pytest.approx(3.141592653589793)
    f = ArithmaFormula(
        name="two_pi_over_b3",
        latex_hint="2 pi / b_3",
        build=lambda E, v: E.div(E.mul(E.number(2.0), v("pi")), v("b3")),
        inputs={"b3": "topology.elder_kads"},
        constants={"pi": "pi"},
        python=lambda b3, pi: 2.0 * pi / b3,
    )
    assert f.check()["agrees"] is True
    assert "arithma constant table" in f.provenance()["pi"]


# --------------------------------------------- THE drift check, both ways


def test_the_drift_check_passes_on_a_consistent_formula():
    assert _simple().check()["status"] == "OK"


def test_the_drift_check_FAILS_when_the_two_tracks_disagree():
    """The load-bearing test. A checker that cannot fail verifies nothing."""
    drifted = ArithmaFormula(
        name="drifted",
        latex_hint="b_3 / 2",
        build=lambda E, v: E.div(v("b3"), E.number(2.0)),
        inputs={"b3": "topology.elder_kads"},
        python=lambda b3: b3 / 3.0,          # deliberately wrong
    )
    result = drifted.check()
    assert result["status"] == "DISAGREES"
    assert result["agrees"] is False
    assert result["rel_error"] > 0.1


def test_a_missing_input_refuses_to_evaluate_rather_than_guessing():
    f = ArithmaFormula(
        name="unknown_input",
        latex_hint="x",
        build=lambda E, v: v("x"),
        inputs={"x": "no.such.registry.path"},
        python=lambda x: x,
    )
    assert f.evaluate() is None
    result = f.check()
    assert result["status"] == "INPUTS_MISSING"
    assert "x" in result["missing"]


def test_a_formula_with_no_python_reference_says_so():
    f = ArithmaFormula(
        name="no_reference",
        latex_hint="b_3",
        build=lambda E, v: v("b3"),
        inputs={"b3": "topology.elder_kads"},
    )
    assert f.check()["status"] == "NO_PYTHON_REFERENCE"


def test_a_broken_build_degrades_instead_of_crashing():
    f = ArithmaFormula(
        name="broken",
        latex_hint="?",
        build=lambda E, v: 1 / 0,
        inputs={},
    )
    assert f.expression() is None
    assert f.latex() is None
    assert f.check()["status"] in ("TREE_FAILED", "NO_PYTHON_REFERENCE")


# --------------------------------------------------- the b_3 track, live


def test_the_b3_relations_all_agree_across_tracks():
    from metaphysica.simulations.PM.geometry.b3_candidate_sweep import (
        arithma_track_report,
    )

    report = arithma_track_report()
    assert report["n_formulas"] >= 4
    assert report["statuses"] == ["OK"], report["checks"]
    assert report["all_agree"] is True


def test_every_b3_formula_exports_latex_and_roundtrips():
    from metaphysica.simulations.PM.geometry.b3_candidate_sweep import (
        arithma_formulas,
    )

    for name, f in arithma_formulas().items():
        assert f.latex(), "%s exported no LaTeX" % name
        assert f.roundtrips() is True, "%s compact form did not roundtrip" % name
        assert f.provenance(), "%s declares no provenance" % name


# ------------------------------------------------------ coverage ratchet


def _arithma_coverage() -> tuple:
    root = pathlib.Path(__file__).resolve().parents[1] / "src" / "metaphysica" \
        / "simulations"
    total = 0
    covered = 0
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "SimulationBase" not in text or "class " not in text:
            continue
        total += 1
        if "arithma" in text or "ARITHMA" in text:
            covered += 1
    return covered, total


#: Measured 2026-09-14: 51 of 121 simulation modules carry the Arithma track.
#: A ratchet -- coverage may rise but must not fall.
ARITHMA_COVERAGE_BASELINE = 51


def test_arithma_coverage_does_not_regress():
    covered, total = _arithma_coverage()
    assert total > 0
    assert covered >= ARITHMA_COVERAGE_BASELINE, (
        "Arithma coverage fell to %d of %d simulation modules, below the %d "
        "baseline. The third track is how formula drift gets caught; removing "
        "it from a module removes that check." % (covered, total,
                                                 ARITHMA_COVERAGE_BASELINE)
    )


def test_the_coverage_baseline_is_not_stale():
    """If coverage has risen, raise the ratchet so it keeps its grip."""
    covered, total = _arithma_coverage()
    assert covered <= ARITHMA_COVERAGE_BASELINE + 10, (
        "coverage is now %d of %d; raise ARITHMA_COVERAGE_BASELINE from %d so "
        "the ratchet still bites." % (covered, total, ARITHMA_COVERAGE_BASELINE)
    )
