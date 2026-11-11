"""L6 close-out, gaugino_condensation XA-05: formula A4.3 carries the FALSIFIED status its
description and its output parameter carry (one status per claim)."""
import math

from metaphysica.simulations.PM.algebra.gaugino_condensation import GauginoCondensationSimulation


def test_cabibbo_proxy_formula_is_falsified_like_its_parameter():
    sim = GauginoCondensationSimulation()
    formula = next(f for f in sim.get_formulas() if f.id == "gaugino-cabibbo-proxy")
    param = next(p for p in sim.get_output_param_definitions()
                 if p.path == "algebra.gaugino_cabibbo_proxy")
    assert formula.category == "FALSIFIED" == param.status
    assert formula.description.startswith("FALSIFIED.")


def test_cabibbo_proxy_sigma_is_built_from_the_value():
    sim = GauginoCondensationSimulation()
    formula = next(f for f in sim.get_formulas() if f.id == "gaugino-cabibbo-proxy")
    cab = math.exp(-2.0 * math.pi / 24) ** 3  # lambda_eff^3 at the formula's off-path seed N1 = 24
    assert f"{cab:.4f}" in formula.plain_text
    assert f"{abs(cab - 0.22500) / 0.00067:.1f}σ" in formula.description
