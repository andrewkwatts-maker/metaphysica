"""XB-09: generate_statistics text says what the code computes, and every
zero or empty fallback for "no scored rows" raises instead of answering."""

import inspect

import pytest

from metaphysica.generators import generate_statistics as gs


@pytest.mark.parametrize("report", [
    {},
    None,
    {"chi_squared_from_rows": {}},
    {"chi_squared_from_rows": {"scored_rows": []}},
])
def test_extractor_raises_without_scored_rows(report):
    with pytest.raises(ValueError, match="no scored rows"):
        gs.extract_sigma_deviations_from_statistical_report(report)


def test_collect_sigmas_raises_without_scored_rows():
    with pytest.raises(ValueError, match="no scored rows"):
        gs._collect_sigmas({"chi_squared_from_rows": {"scored_rows": []}})


def test_compute_statistics_raises_on_empty_sigmas():
    with pytest.raises(ValueError, match="no scored rows"):
        gs.compute_statistics([])


def test_success_rate_raises_on_zero_total():
    with pytest.raises(ValueError, match="no scored rows"):
        gs._success_rate({"total_predictions": 0, "within_2sigma": 0})


def test_success_rate_still_computes_and_passes_not_available():
    assert gs._success_rate({"total_predictions": 4, "within_2sigma": 3}) == "75.0%"
    assert gs._success_rate({"total_predictions": gs.NOT_AVAILABLE,
                             "within_2sigma": gs.NOT_AVAILABLE}) == gs.NOT_AVAILABLE


def test_compute_statistics_dof_is_scored_count_minus_ansatz():
    stats = gs.compute_statistics([0.5, 3.0, 0.0])
    assert stats["degrees_of_freedom"] == max(1, 3 - gs.DOF_SUBTRAHEND_ANSATZ)
    assert stats["total_predictions"] == 3 and stats["exact_matches"] == 1


def test_text_names_no_retired_source_or_gate_dof():
    module_text = inspect.getsource(gs)
    assert "CERTIFICATES_v16_2_FINAL" not in module_text
    assert "verified gates - fitted parameters" not in gs.__doc__
    assert "DOF_SUBTRAHEND_ANSATZ" in gs.__doc__
    assert "CERTIFICATES_v16_2_FINAL" not in gs.compute_statistics([1.0])["note"]
