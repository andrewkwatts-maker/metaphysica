"""L7 validation-data: asymmetric errors are kept; a missing error raises."""
import json

import pytest

from metaphysica.simulations.data import experimental_data_loader as edl


def test_uncertainty_toward_uses_the_side_the_prediction_lies_on():
    v = edl.ExperimentalValue(10.0, 1.5, "u", "s",
                              uncertainty_plus=2.0, uncertainty_minus=1.0)
    assert v.uncertainty_toward(11.0) == 2.0
    assert v.uncertainty_toward(9.0) == 1.0


def test_symmetric_value_falls_back_to_its_uncertainty():
    v = edl.ExperimentalValue(10.0, 1.5, "u", "s")
    assert v.uncertainty_toward(9.0) == 1.5


def test_nufit_keeps_both_sides():
    nu = edl.ExperimentalDataLoader().get_nufit("theta_23")
    assert nu.uncertainty_plus is not None and nu.uncertainty_minus is not None
    assert nu.uncertainty == pytest.approx((nu.uncertainty_plus + nu.uncertainty_minus) / 2)


def test_entry_without_an_error_raises_not_zero():
    with pytest.raises(KeyError):
        edl._errors({"value": 1.0}, "x")


def test_nufit_files_flag_the_unverified_source():
    d = edl.ExperimentalDataLoader.DATA_DIR
    for name in ("nufit_6_0.json", "nufit_6_0_parameters.json"):
        meta = json.loads((d / name).read_text(encoding="utf-8"))["metadata"]
        assert meta["source_unverified"] is True
