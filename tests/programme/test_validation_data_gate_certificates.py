"""G12/pipeline-12 and pipeline-14: certificate text and anchors come from computed data."""
import pytest

from metaphysica.generators import generate_72_certificates as g
from metaphysica.simulations.data.experimental_data_loader import get_loader


def test_registry_gate_result_is_built_from_the_check():
    ev = {"tier": "registry", "checks": [
        {"path": "p.x", "value": 1.5, "expected": 1.0, "sigma": 4.0, "ok": False}]}
    text = g.declared_result(12, {"result": "0.68 sigma agreement"}, ev)
    assert "4.00 sigma" in text and "0.68" not in text
    assert g.result_basis(ev) == "computed_from_registry"


def test_non_registry_result_is_labelled_declared():
    assert g.result_basis({"tier": "none"}) == "declared"
    assert g.result_basis({"tier": "arithmetic"}).startswith("declared_text")


def test_gate12_typed_entry_has_no_sigma_claim():
    entry = g.VERIFIABLE_GATES[12]
    assert "0.68" not in entry["result"] and "0.68" not in entry["note"]


def test_certificate_for_gate12_carries_basis_and_no_unmatched():
    cert = g.create_certificate({"id": 12, "name": "Weinberg angle"}, [])
    assert cert["result_basis"] == "computed_from_registry"
    assert "sigma" in cert["result"] and cert["result_unmatched_numbers"] == []


def test_anchors_are_read_from_data_not_literals():
    pdg = get_loader().get_value("pdg_2024_values.json", "couplings", "sin2_theta_W")
    ev = g._eval_registry_spec(g.GATE_EVAL_SPECS[12], g._load_registry_params())
    assert ev["checks"][0]["expected"] == pdg.value
    for gid, spec in g.GATE_EVAL_SPECS.items():
        if "exp" in spec:
            assert spec.get("source_unverified"), gid


def test_literal_sigma_anchor_without_flag_raises():
    with pytest.raises(KeyError):
        g._spec_entries({"path": "a.b", "kind": "sigma", "exp": 1.0, "unc": 0.1})


def test_get_value_missing_key_raises():
    with pytest.raises(KeyError):
        get_loader().get_value("pdg_2024_values.json", "couplings", "nope")


def test_planck_mass_uncertainties_flagged_unverified():
    """sim-validation-data-23: three M_Pl errors disagree with G_N's; flagged, not edited."""
    ldr = get_loader()
    for keys in (("codata_2022.json", "fundamental_constants", "M_PLANCK"),
                 ("codata_2022.json", "fundamental_constants", "M_PLANCK_reduced"),
                 ("pdg_2024_values.json", "fundamental_constants", "M_PLANCK_REDUCED")):
        node = ldr._load_json(keys[0])
        for k in keys[1:]:
            node = node[k]
        assert node.get("source_unverified"), keys


def test_parameter_write_back_error_is_not_swallowed(tmp_path, monkeypatch):
    """sim-validation-data-27 (part): a broken parameters file raises, not a warning."""
    import json
    from metaphysica.generators import generate_statistics as gs
    bad = tmp_path / "parameters.json"
    bad.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(gs, "PARAMETERS_FILE", str(bad))
    with pytest.raises(json.JSONDecodeError):
        gs._write_back_parameters({"framework_statistics": {}, "validation": {}})


def test_dead_modules_are_gone():
    import importlib.util as u
    for m in ("PM.validation.rigor_covariance", "PM.validation.tolerance_sweep",
              "validation.verify_content_migration"):
        assert u.find_spec("metaphysica.simulations." + m) is None
