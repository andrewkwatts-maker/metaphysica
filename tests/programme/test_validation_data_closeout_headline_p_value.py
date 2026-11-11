"""XV-02: the headline p-value and dof are the row-count ones the verdict uses."""
import pytest

from metaphysica.generators import headline_stats as hs

REPORT = {
    "chi_squared_from_rows": {"all_scoring_rows": {"chi_squared": 40.0, "n": 7}},
    "edof_analysis": {"effective_dof": 3, "effective_dof_is_ansatz": True,
                      "p_value": 0.111},
    "summary": {"status": "POOR_FIT", "p_value": 0.0042, "p_value_n_dof": 0.0042}}


def test_fit_publishes_the_row_count_p_value_and_dof():
    fit = hs._fit(REPORT)
    assert fit["p_value"] == 0.0042
    assert fit["dof"] == fit["rows"] == 7
    assert fit["dof_is_ansatz"] is False
    assert fit["verdict"] == "POOR_FIT"


def test_fit_raises_without_the_row_count_p_value():
    report = {**REPORT, "summary": {"status": "POOR_FIT"}}
    with pytest.raises(KeyError, match="p_value_n_dof"):
        hs._fit(report)


def test_fit_does_not_need_the_edof_block():
    report = {k: v for k, v in REPORT.items() if k != "edof_analysis"}
    assert hs._fit(report)["p_value"] == 0.0042
