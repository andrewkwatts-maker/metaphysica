"""Wave A round 2, R2-09: the derivation steps, references and terms of formula A4.4
(gaugino-cabibbo-derived) build the PDG value and the sigma from the loaded input.

Review RG: the A4.2 and A4.3 steps and terms build λ_W, λ_eff, the proxy and the matching
exponent from the computed values, and the A4.4 text takes its exponent and its count from
the generation count in force."""
import inspect
import math
import re

from metaphysica.simulations.core.variants import selection
from metaphysica.simulations.PM.algebra import gaugino_condensation as gc
from metaphysica.simulations.PM.algebra.gaugino_condensation import GauginoCondensationSimulation

PDG, UNC = 0.30000, 0.00200  # deliberately not the loaded pair: typed text cannot follow it
TYPED = ("0.22500", "0.00067", "37.6σ")  # what the strings carried when they were typed


def _a44():
    return next(f for f in GauginoCondensationSimulation().get_formulas()
                if f.id == "gaugino-cabibbo-derived")


def _a44_with_pdg(monkeypatch):
    monkeypatch.setattr(gc, "_pdg_lambda_w", lambda: (PDG, UNC))
    return _a44()


def _cab_derived(formula) -> float:
    return float(formula.plain_text.rsplit("= ", 1)[1].split()[0])


def test_a44_derivation_step_sigma_follows_the_pdg_input(monkeypatch):
    formula = _a44_with_pdg(monkeypatch)
    sigma = abs(_cab_derived(formula) - PDG) / UNC
    steps = formula.derivation["steps"]
    assert f"PDG Wolfenstein λ_W = 0.30000 ± 0.00200 — {sigma:.1f}σ away, FALSIFIED" in steps[-1]
    assert not [s for s in steps for typed in TYPED if typed in s]


def test_a44_terms_pdg_value_follows_the_pdg_input(monkeypatch):
    formula = _a44_with_pdg(monkeypatch)
    assert formula.terms[r"\lambda_W"].endswith("(PDG: 0.30000)")
    assert not [t for t in formula.terms.values() for typed in TYPED if typed in t]


def test_a44_reference_value_follows_the_pdg_input(monkeypatch):
    references = _a44_with_pdg(monkeypatch).derivation["references"]
    assert references[-1].endswith("Wolfenstein λ = 0.30000±0.00200")
    assert not [r for r in references for typed in TYPED if typed in r]


def test_a44_step_and_reference_read_the_loader_record():
    from metaphysica.simulations.data.experimental_data_loader import get_loader

    record = get_loader().get_pdg("ckm", "V_us")
    formula = _a44()
    derivation = formula.derivation
    assert gc._vs_pdg(_cab_derived(formula)) + " away" in derivation["steps"][-1]
    assert derivation["references"][-1] == (
        f"{record.source} CKM review: Wolfenstein λ = "
        f"{record.value:.5f}±{record.uncertainty:.5f}"
    )
    assert formula.terms[r"\lambda_W"].endswith(f"(PDG: {record.value:.5f})")


def _formula(formula_id):
    return next(f for f in GauginoCondensationSimulation().get_formulas() if f.id == formula_id)


def _texts(formula):
    """Every derivation step and every term description of a formula."""
    terms = [t["description"] if isinstance(t, dict) else t for t in formula.terms.values()]
    return list(formula.derivation["steps"]) + terms


def test_a43_steps_and_terms_follow_the_pdg_input(monkeypatch):
    monkeypatch.setattr(gc, "_pdg_lambda_w", lambda: (PDG, UNC))
    formula = _formula("gaugino-cabibbo-proxy")
    assert formula.derivation["steps"][0].endswith("the leading CKM parameter λ_W ≈ 0.3000")
    proxy = formula.terms[r"\varepsilon_{\text{proxy}}"]["description"]
    assert proxy.startswith("Coarse proxy for Wolfenstein λ_W ≈ 0.3000; ")
    assert not [t for t in _texts(formula) if "0.2250" in t]


def test_a43_matching_exponent_is_computed_from_the_pdg_input(monkeypatch):
    monkeypatch.setattr(gc, "_pdg_lambda_w", lambda: (PDG, UNC))
    p = math.log(PDG) / (-2.0 * math.pi / 24)  # λ_eff^p = λ_W with λ_eff = exp(-2π/24)
    step = _formula("gaugino-cabibbo-proxy").derivation["steps"][3]
    assert step.endswith(f"(p ≈ {p:.1f})")  # typed "p ≈ 3.4" before; 3.4 solves neither pair


def test_a43_matching_exponent_reproduces_the_loaded_lambda_w():
    pdg = gc._pdg_lambda_w()[0]
    step = _formula("gaugino-cabibbo-proxy").derivation["steps"][3]
    p = float(re.search(r"\(p ≈ ([\d.]+)\)$", step).group(1))
    assert abs(p - math.log(pdg) / (-2.0 * math.pi / 24)) <= 0.05  # one printed decimal


def test_a42_a43_steps_build_lambda_eff_and_the_proxy_from_the_computed_values():
    source = inspect.getsource(GauginoCondensationSimulation.get_formulas)
    assert "0.7697" not in source and "≈ 0.456" not in source  # typed in three steps before
    leff = math.exp(-2.0 * math.pi / 24)
    assert _formula("gaugino-lambda-eff").derivation["steps"][1].endswith(f"≈ {leff:.4f}")
    steps = _formula("gaugino-cabibbo-proxy").derivation["steps"]
    assert steps[1].endswith(f"λ_eff ≈ {leff:.4f} is the suppression scale")
    assert steps[2].startswith(f"The third power ε ≈ λ_eff³ ≈ {leff ** 3:.3f} is the coarse proxy")


def _a44_generation_text_matches(formula, n_gen):
    steps = formula.derivation["steps"]
    assert steps[-3].endswith(f"has {n_gen} eigenvalues (n_gen={n_gen})")
    eps, exponent, value = re.search(
        r"= ([\d.]+)\^\(1/([\d.]+)\) = ([\d.]+)$", steps[-2]).groups()
    assert float(exponent) == n_gen
    assert abs(float(eps) ** (1.0 / float(exponent)) - float(value)) < 1e-5
    assert float(value) == _cab_derived(formula)
    assert f"ε_rt^(1/{n_gen}) ≈ " in formula.description
    assert f"and n_gen = {n_gen}: " in formula.description
    assert formula.eml_tree_str.endswith(f"ops.inv(eml_scalar({n_gen})))")
    assert formula.eml_description.endswith(f"n_gen = {n_gen}.")
    assert formula.terms[r"n_{\text{gen}}"].startswith(
        f"Number of fermion generations = {n_gen} (")


def test_a44_exponent_and_count_follow_another_n_gen_source():
    with selection.forced({"b3_seed": "seed_43_joyce", "n_gen_source": "b3_over_dim_O"}):
        n_gen = gc._resolved_n_gen()
        formula = _a44()
    assert n_gen != 3  # b3/8 on the Joyce seed, not the b2/4 = 3 of the path in force
    _a44_generation_text_matches(formula, n_gen)
