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

#: 2026-09-14: this was a MODULE-LEVEL pytestmark, so every test here skipped
#: when the backend was a stub -- including the coverage ratchet, which reads
#: source files and needs no backend at all. A ratchet that never runs is not a
#: ratchet. The skip now decorates only the tests that genuinely evaluate an
#: Arithma expression.
needs_backend = pytest.mark.skipif(
    not available(), reason="arithma backend unusable (stub or absent)")


def _simple() -> ArithmaFormula:
    return ArithmaFormula(
        name="half_of_b3",
        latex_hint="b_3 / 2",
        build=lambda E, v: E.div(v("b3"), E.number(2.0)),
        inputs={"b3": "topology.elder_kads"},
        python=lambda b3: b3 / 2.0,
    )


# ------------------------------------------------------------- the basics


@needs_backend
def test_a_declared_formula_builds_exports_and_evaluates():
    f = _simple()
    assert f.expression() is not None
    assert "b3" in f.latex()
    assert f.compact()
    assert f.roundtrips() is True
    # b_3 / 2 on the live registry seed. Measured 2026-09-22, b3_seed
    # adoption: topology.elder_kads = 43, so the half is 21.5 where it was
    # 12.0 before the ruling. Read from the registry as well as pinned, so
    # the formula is asserted to CONSUME the seed rather than to equal a
    # number someone typed.
    assert f.evaluate() == pytest.approx(
        registry_value("topology.elder_kads") / 2.0
    )
    assert f.evaluate() == pytest.approx(21.5)


@needs_backend
def test_the_exact_derivative_is_symbolic_not_a_difference():
    """d(b3/2)/d b3 = 1/2 exactly, for any b3."""
    f = _simple()
    assert f.derivative("b3") == pytest.approx(0.5, abs=1e-12)


@needs_backend
def test_numbers_come_from_the_registry_not_the_formula():
    f = _simple()
    assert f.provenance() == {"b3": "topology.elder_kads"}
    # Measured 2026-09-22, b3_seed adoption: the registry's seed row is 43
    # on the adopted seed_43_joyce branch, where it read 24 before the
    # ruling. Checked against the fork's own declared value so this pins the
    # registry FOLLOWING the seed, not a restated constant.
    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path,
        seed_values,
    )

    assert seed_values(resolve_path())[0] == 43
    assert registry_value("topology.elder_kads") == pytest.approx(
        float(seed_values(resolve_path())[0])
    )
    assert registry_value("topology.elder_kads") == pytest.approx(43.0)


@needs_backend
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


@needs_backend
def test_the_drift_check_passes_on_a_consistent_formula():
    assert _simple().check()["status"] == "OK"


@needs_backend
def test_the_drift_check_FAILS_when_the_two_tracks_disagree():
    """The load-bearing test. A checker that cannot fail verifies nothing.

    Note what the skip above costs: with a stub backend check() returns
    BACKEND_UNAVAILABLE for every formula, so in CI this proof that the drift
    check CAN fail does not run. The drift check is unverified wherever the
    backend is unusable, which is everywhere the package installs from PyPI.
    """
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


@needs_backend
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


@needs_backend
def test_a_formula_with_no_python_reference_says_so():
    f = ArithmaFormula(
        name="no_reference",
        latex_hint="b_3",
        build=lambda E, v: v("b3"),
        inputs={"b3": "topology.elder_kads"},
    )
    assert f.check()["status"] == "NO_PYTHON_REFERENCE"


@needs_backend
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


@needs_backend
def test_the_b3_relations_all_agree_across_tracks():
    from metaphysica.simulations.PM.geometry.b3_candidate_sweep import (
        arithma_track_report,
    )

    report = arithma_track_report()
    assert report["n_formulas"] >= 4
    assert report["statuses"] == ["OK"], report["checks"]
    assert report["all_agree"] is True


@needs_backend
def test_every_b3_formula_exports_latex_and_roundtrips():
    from metaphysica.simulations.PM.geometry.b3_candidate_sweep import (
        arithma_formulas,
    )

    for name, f in arithma_formulas().items():
        assert f.latex(), "%s exported no LaTeX" % name
        assert f.roundtrips() is True, "%s compact form did not roundtrip" % name
        assert f.provenance(), "%s declares no provenance" % name


# ------------------------------------------------------ coverage ratchet


def _simulation_modules():
    root = pathlib.Path(__file__).resolve().parents[1] / "src" / "metaphysica" \
        / "simulations"
    for path in sorted(root.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "SimulationBase" not in text or "class " not in text:
            continue
        yield path, text


def _mentions_arithma() -> tuple:
    """Modules where the WORD arithma appears. Not a measure of anything."""
    total = covered = 0
    for _path, text in _simulation_modules():
        total += 1
        if "arithma" in text or "ARITHMA" in text:
            covered += 1
    return covered, total


def _declares_arithma_formula() -> tuple:
    """Modules that declare an ArithmaFormula: the real third-track count.

    Counted by PARSING for a call to ArithmaFormula(...), so a mention in a
    docstring, a comment, or the legacy ``except ImportError`` guard does not
    count. That distinction is the entire point of this measurement.

    Scanned over the WHOLE simulations tree rather than the SimulationBase
    corpus, because b3_candidate_sweep -- the only module declaring the new
    track at all -- contains no SimulationBase and is therefore invisible to
    that corpus. The worked example of the third track was outside the thing
    measuring third-track coverage.
    """
    root = pathlib.Path(__file__).resolve().parents[1] / "src" / "metaphysica" \
        / "simulations"
    total = covered = 0
    for path in sorted(root.rglob("*.py")):
        total += 1
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:                    # not this test's business
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = (func.id if isinstance(func, ast.Name)
                        else getattr(func, "attr", None))
                if name == "ArithmaFormula":
                    covered += 1
                    break
    return covered, total


# 2026-09-14: THE RATCHET WAS COUNTING THE WORD "arithma".
#
# It reported 51 of 121 modules "covered", and the campaign brief read that as
# 51 working third tracks with 70 to go. Measured: of those 51, the number
# declaring an ArithmaFormula is ZERO. All 51 are the legacy copied guard
#
#     try:
#         import arithma as _A
#     except ImportError:
#         _A = None
#
# which is the scaffolding ArithmaFormula exists to REPLACE. A substring match
# cannot tell a third track from a comment about one, so the old number could
# be raised by writing the word in a docstring.
#
# Both counts are kept, because the gap between them IS the backlog, and both
# ratchet. The mention count may not fall (removing the legacy guard is fine
# only if a real declaration replaces it, which raises the other number).
MENTION_BASELINE = 51
#: Modules declaring an ArithmaFormula, over the whole simulations tree.
#: Measured 2026-09-14: b3_candidate_sweep, and nothing else.
DECLARATION_BASELINE = 1


def test_the_two_coverage_measures_are_not_the_same_measure():
    """The load-bearing one. If these agreed, the substring count was fine."""
    mentions, total = _mentions_arithma()
    declarations, total_all = _declares_arithma_formula()
    assert total > 0 and total_all >= total
    assert mentions > declarations, (
        "mentions (%d) and declarations (%d) agree, so counting the substring "
        "would be harmless -- rewrite this test rather than deleting it, "
        "because the gap is what the backlog is measured by"
        % (mentions, declarations)
    )


def test_arithma_declaration_coverage_does_not_regress():
    """The third track, counted by what declares one."""
    declarations, total = _declares_arithma_formula()
    assert declarations >= DECLARATION_BASELINE, (
        "ArithmaFormula declarations fell to %d of %d simulation modules, "
        "below the %d baseline. The third track is how formula drift gets "
        "caught; removing a declaration removes that check."
        % (declarations, total, DECLARATION_BASELINE)
    )


def test_the_declaration_baseline_is_not_stale():
    declarations, total = _declares_arithma_formula()
    assert declarations <= DECLARATION_BASELINE + 10, (
        "declarations are now %d of %d; raise DECLARATION_BASELINE from %d so "
        "the ratchet still bites." % (declarations, total, DECLARATION_BASELINE)
    )


def test_the_legacy_guard_count_does_not_regress():
    mentions, total = _mentions_arithma()
    assert mentions >= MENTION_BASELINE, (
        "modules mentioning arithma fell to %d of %d, below %d. This counts "
        "the legacy import guard as well as real declarations, so a fall "
        "means a guard was deleted without a declaration replacing it."
        % (mentions, total, MENTION_BASELINE)
    )
