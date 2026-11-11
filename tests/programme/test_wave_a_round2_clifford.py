"""Wave A round 2, PT-14 (clifford part): the row algebra.clifford_boost_conservation
declares the formula clifford-quadratic-unification, and that formula lists the row in
its output params. Checked in-process with the shared rule of the derivation chains."""
from metaphysica.generators.derivation_chain import declared_formula_errors
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
