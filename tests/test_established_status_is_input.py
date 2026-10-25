"""An ESTABLISHED-status record is an input, whatever its source string
(higgs.vev = 246 scored PASS against PDG 246.22 via source higgs_mass_v16_0)."""
from metaphysica.generators.generate_validation_certificates import _is_input_anchor


def test_established_status_is_input():
    rec = {"source": "higgs_mass_v16_0", "status": "ESTABLISHED"}
    assert _is_input_anchor(rec, 246.0, 246.22)


def test_prediction_is_not_input():
    rec = {"source": "higgs_mass_v16_0", "status": "PREDICTED"}
    assert not _is_input_anchor(rec, 125.1, 125.25)
