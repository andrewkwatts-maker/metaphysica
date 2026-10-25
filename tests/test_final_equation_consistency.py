"""Final equations: one value per quantity, honest labels, cited sources.

Covers the conflicts of docs/plan/geometry/2026-10-25-conclusions-audit.md
(top-10 fixes 3, 5-9): w0, H0, ALP mass, M_KK, Appendix Z arithmetic, and
the references of the final equations. Adopted path: seed_43_joyce, b3 = 43.
"""
import math

import pytest

from metaphysica.simulations.core.FormulasRegistry import get_registry
from metaphysica.simulations.PM.paper.abstract import AbstractV17_2
from metaphysica.simulations.PM.paper.appendices.appendix_z_terminal_ledger import (
    AppendixZTerminalLedger,
)
from metaphysica.simulations.PM.paper.predictions_aggregator import (
    PredictionsAggregatorV16,
)
from metaphysica.simulations.PM.paper.results import ResultsV16_2

B3 = int(get_registry().elder_kads)


def _by_label(module_cls):
    return {f.label: f for f in module_cls().get_formulas()}


def test_adopted_seed_is_43():
    assert B3 == 43


def test_w0_reads_the_computed_adopted_value():
    from metaphysica.simulations.PM.cosmology.dark_energy_thawing import (
        DarkEnergyEvolution,
    )
    computed = DarkEnergyEvolution().calculate_w_params_w0(B3)
    f31 = _by_label(ResultsV16_2)["(3.1)"]
    assert f31.value == pytest.approx(computed)
    assert f31.value == pytest.approx(-42.0 / 43.0)
    assert "-42/43" in f31.plain_text


def test_w0_off_path_value_is_labelled_superseded():
    f31 = _by_label(ResultsV16_2)["(3.1)"]
    assert "superseded" in f31.plain_text
    f88 = _by_label(PredictionsAggregatorV16)["(8.8)"]
    assert "-23/24" in f88.plain_text and "off-path" in f88.plain_text
    assert "OFF-PATH" in f88.description.upper()


def test_h0_71_55_is_not_labelled_derived():
    forms = _by_label(ResultsV16_2)
    for label in ("(3.2)", "(3.2b)"):
        assert forms[label].category == "FITTED"
        assert "OPEN" in forms[label].description


def test_off_path_results_formulas_say_so():
    forms = _by_label(ResultsV16_2)
    for label in ("(3.3)", "(3.4)"):
        assert "OFF-PATH" in forms[label].description


def _z():
    return _by_label(AppendixZTerminalLedger)


def test_z6_sum_is_not_two_thirds_so_not_derived():
    f = _z()["(Z.6)"]
    total = 8 / B3 + 3 / 12 + 1 / 12
    assert not math.isclose(total, 2 / 3)
    assert f.category == "FALSIFIED"
    assert f"{total:.6f}" in f.plain_text
    assert "= 2/3" not in f.plain_text.split("(equals")[0]


def test_z10_closure_is_not_derived_when_it_fails():
    f = _z()["(Z.10)"]
    lhs = 276 + B3 - 12
    assert lhs != 288
    assert f.category == "FALSIFIED"
    assert str(lhs) in f.plain_text and "FAILS" in f.plain_text


def test_z_ratios_and_h0_follow_the_adopted_seed():
    forms = _z()
    for label in ("(Z.7)", "(Z.8)", "(Z.9)", "(Z.11)"):
        assert forms[label].category == "FALSIFIED"
        assert "retired" in forms[label].plain_text or "FALSIFIED" in forms[label].plain_text
    assert "40.8" in forms["(Z.11)"].plain_text


def test_z_identities_are_not_labelled_derived():
    forms = _z()
    for label in ("(Z.1)", "(Z.2)", "(Z.3)", "(Z.4)", "(Z.5)"):
        assert forms[label].category in ("GEOMETRIC", "ANSATZ")
        assert forms[label].description.startswith(("IDENTITY", "ANSATZ"))


def test_no_derived_z_formula_with_false_stated_arithmetic():
    for f in _z().values():
        assert f.category != "DERIVED", f.label


def test_alp_mass_has_no_derived_3p51_meV():
    import metaphysica.simulations.PM.algebra.e7_representation as e7
    cls = next(v for v in vars(e7).values() if isinstance(v, type)
               and v.__module__ == e7.__name__ and hasattr(v, "get_formulas"))
    f = next(x for x in cls().get_formulas() if x.id == "e7-alp-mass")
    assert f.category != "DERIVED"
    assert "OPEN" in f.description and "3.51 meV" in f.description
    from metaphysica.simulations.PM.portals import alp_portals
    pc = next(v for v in vars(alp_portals).values() if isinstance(v, type)
              and hasattr(v, "compute_alp"))
    assert pc().compute_alp().m_alp != pytest.approx(3.51e-3)


def test_mkk_is_marked_open():
    from metaphysica.config.core_formulas import CoreFormulas
    desc = CoreFormulas.KK_GRAVITON.description
    assert "OPEN" in desc and "4.5 TeV" in desc and "5.0 TeV" in desc


LISTED = [
    (AbstractV17_2, ["(0.1)"]),
    (ResultsV16_2, ["(3.1)", "(3.2)", "(3.2b)", "(3.3)", "(3.4)", "(3.5)"]),
    (PredictionsAggregatorV16, [f"(8.{i})" for i in range(1, 9)]),
    (AppendixZTerminalLedger, [f"(Z.{i})" for i in range(1, 12)]),
]


@pytest.mark.parametrize("module_cls,labels", LISTED)
def test_listed_final_equations_cite_registered_references(module_cls, labels):
    forms = _by_label(module_cls)
    known = {r["id"] for r in module_cls().get_references()}
    for label in labels:
        refs = forms[label].references
        assert refs, f"{label} has no references"
        assert set(refs) <= known, f"{label} cites unregistered ids {set(refs) - known}"


def test_joyce_existence_citation_has_no_explicit_metric_claim():
    ref = next(r for r in AbstractV17_2().get_references() if r["id"] == "joyce2000")
    assert "Thm 11.6.1" in ref["notes"] and "no explicit metric" in ref["notes"]
