"""Wave A round 2, PT-14 (clifford part): the row algebra.clifford_boost_conservation
declares the formula clifford-quadratic-unification, and that formula lists the row in
its output params. Checked in-process with the shared rule of the derivation chains.

R2-08: the section row label and the callout of the Minkowski rotor check say FAILS or
passes from run()["_boost_ok"], not from typed text."""
import math

import pytest

from metaphysica.generators.derivation_chain import declared_formula_errors
from metaphysica.simulations.PM.algebra import clifford_unification
from metaphysica.simulations.PM.algebra.clifford_unification import CliffordUnificationSimulation

BOOST = "algebra.clifford_boost_conservation"
FORMULA = "clifford-quadratic-unification"


def _formulas():
    return {f.id: {"input_params": list(f.input_params), "output_params": list(f.output_params)}
            for f in CliffordUnificationSimulation().get_formulas()}


def _rows():
    return {p.path: {"derivation_formula": p.derivation_formula}
            for p in CliffordUnificationSimulation().get_output_param_definitions()}


def test_boost_row_declares_the_quadratic_formula():
    assert _rows()[BOOST]["derivation_formula"] == FORMULA


def test_quadratic_formula_lists_the_boost_row():
    assert BOOST in _formulas()[FORMULA]["output_params"]


def test_boost_row_has_no_declared_formula_error():
    errors = declared_formula_errors({BOOST: _rows()[BOOST]}, _formulas())
    assert errors == []


def test_boost_row_is_computed_by_the_run_of_the_same_simulation():
    sim = CliffordUnificationSimulation()
    assert FORMULA in sim.output_formulas
    assert BOOST in sim.output_params
    assert BOOST in sim.run(None)


ROTOR_ROW = "Minkowski interval under cos/sin rotor"


def _boost_texts(section):
    """(row of the rotor check, callout text) of the section."""
    table = next(b for b in section.content_blocks if b.type == "table")
    callout = next(b for b in section.content_blocks if b.type == "callout")
    row = next(r for r in table.rows if r[0].startswith(ROTOR_ROW))
    return row, callout.content


def _force_boost_flag(monkeypatch, ok):
    """run() of the simulation with only the flag _boost_ok replaced."""
    real_run = CliffordUnificationSimulation.run

    def run(self, registry):
        results = real_run(self, registry)
        results["_boost_ok"] = ok
        return results

    monkeypatch.setattr(CliffordUnificationSimulation, "run", run)


def test_section_with_a_passing_boost_does_not_say_fails(monkeypatch):
    # A bound no error can reach: run() itself computes a passing boost.
    monkeypatch.setattr(clifford_unification, "BOOST_BOUND", math.inf)
    sim = CliffordUnificationSimulation()
    assert sim.run(None)["_boost_ok"] is True
    row, callout = _boost_texts(sim.get_section_content())
    assert row[0] == f"{ROTOR_ROW} (passes)"
    assert row[3] == "✓"
    assert "FAILS" not in row[0] and "FAILS" not in callout
    assert ", passes)" in callout


@pytest.mark.parametrize("ok, word, mark", [(True, "passes", "✓"), (False, "FAILS", "✗")])
def test_section_reads_the_flag_of_run_not_a_second_comparison(monkeypatch, ok, word, mark):
    _force_boost_flag(monkeypatch, ok)
    row, callout = _boost_texts(CliffordUnificationSimulation().get_section_content())
    assert row[0] == f"{ROTOR_ROW} ({word})"
    assert row[3] == mark
    assert f", {word})" in callout
    other = "FAILS" if ok else "passes"
    assert other not in row[0] and other not in callout
