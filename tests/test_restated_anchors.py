"""E4: rows that restate the SH0ES anchor are CALIBRATED, never predictions."""
from types import SimpleNamespace

from metaphysica.generators.parameter_ledger import (
    CALIBRATION_CHECK, RESTATED_ANCHORS, label_class)
from metaphysica.simulations.run_all_simulations import SimulationRunner  # noqa


def _row(status, val="NO_DATA", exp=None):
    return {"value": 73.04, "status": status, "validation_status": val,
            "experimental_value": exp, "experimental_source": "SH0ES 2022"}


def test_restated_anchors_are_marked_calibrated_and_keep_their_values():
    params = {n: _row("DERIVED") for n in RESTATED_ANCHORS}
    params["cosmology.H0_late_evolved"] = _row("PREDICTED", "PASS", 73.04)
    fake = SimpleNamespace(registry=SimpleNamespace(export_formulas=lambda: {}))
    SimulationRunner._record_chains_and_calibration_checks(fake, params)
    for name in RESTATED_ANCHORS:
        assert params[name]["status"] == "CALIBRATED"
        assert params[name]["value"] == 73.04
        assert label_class(params[name]["status"]) == "CALIBRATED"
    assert params["cosmology.H0_late_evolved"]["validation_status"] == CALIBRATION_CHECK
