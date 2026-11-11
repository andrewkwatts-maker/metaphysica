"""L6 close-out, gaugino_condensation XA-05: formula A4.3 carries the FALSIFIED status its
description and its output parameter carry (one status per claim)."""
import math

from metaphysica.simulations.PM.algebra import gaugino_condensation as gc
from metaphysica.simulations.PM.algebra.gaugino_condensation import GauginoCondensationSimulation


def test_cabibbo_proxy_formula_is_falsified_like_its_parameter():
    sim = GauginoCondensationSimulation()
    formula = next(f for f in sim.get_formulas() if f.id == "gaugino-cabibbo-proxy")
    param = next(p for p in sim.get_output_param_definitions()
                 if p.path == "algebra.gaugino_cabibbo_proxy")
    assert formula.category == "FALSIFIED" == param.status
    assert formula.description.startswith("FALSIFIED.")


def _formulas_with_pdg(monkeypatch, value, unc):
    monkeypatch.setattr(gc, "_pdg_lambda_w", lambda: (value, unc))
    return {f.id: f for f in GauginoCondensationSimulation().get_formulas()}


def test_cabibbo_proxy_sigma_follows_the_pdg_input(monkeypatch):
    formula = _formulas_with_pdg(monkeypatch, 0.30000, 0.00200)["gaugino-cabibbo-proxy"]
    cab = math.exp(-2.0 * math.pi / 24) ** 3  # lambda_eff^3 at the formula's off-path seed N1 = 24
    assert f"{cab:.4f}" in formula.plain_text
    assert f"0.30000 ± 0.00200 — {abs(cab - 0.30) / 0.002:.1f}σ" in formula.description
    assert "344.7σ" not in formula.description and "0.22500" not in formula.description


def test_cabibbo_derived_sigma_follows_the_pdg_input(monkeypatch):
    formula = _formulas_with_pdg(monkeypatch, 0.30000, 0.00200)["gaugino-cabibbo-derived"]
    cab_derived = float(formula.plain_text.rsplit("= ", 1)[1].split()[0])
    assert f"0.30000 ± 0.00200 — {abs(cab_derived - 0.30) / 0.002:.1f}σ" in formula.description
    assert "37.6σ" not in formula.description and "0.22500" not in formula.plain_text
