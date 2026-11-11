"""Wave A round 2, R2-09: the derivation steps, references and terms of formula A4.4
(gaugino-cabibbo-derived) build the PDG value and the sigma from the loaded input."""
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
