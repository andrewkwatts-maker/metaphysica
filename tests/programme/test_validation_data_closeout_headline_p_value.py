"""XV-02: the headline p-value and dof are the row-count ones the verdict uses."""
import pytest

from metaphysica.generators import headline_stats as hs

REPORT = {
    "chi_squared_from_rows": {"all_scoring_rows": {"chi_squared": 40.0, "n": 7}},
    "edof_analysis": {"effective_dof": 3, "effective_dof_is_ansatz": True,
                      "p_value": 0.111},
    "summary": {"status": "POOR_FIT", "p_value": 0.0042, "p_value_n_dof": 0.0042,
                "dof": 7, "dof_is_ansatz": False}}


def test_fit_publishes_the_row_count_p_value_and_dof():
    fit = hs._fit(REPORT)
    assert fit["p_value"] == 0.0042
    assert fit["dof"] == fit["rows"] == 7
    assert fit["dof_is_ansatz"] is False
    assert fit["verdict"] == "POOR_FIT"


def test_fit_raises_without_the_row_count_p_value():
    summary = {k: v for k, v in REPORT["summary"].items() if k != "p_value_n_dof"}
    report = {**REPORT, "summary": summary}
    with pytest.raises(KeyError, match="p_value_n_dof"):
        hs._fit(report)


def test_fit_does_not_need_the_edof_block():
    report = {k: v for k, v in REPORT.items() if k != "edof_analysis"}
    assert hs._fit(report)["p_value"] == 0.0042


def test_fit_reads_dof_and_its_ansatz_flag_from_the_summary():
    summary = {**REPORT["summary"], "dof_is_ansatz": "from-the-report"}
    fit = hs._fit({**REPORT, "summary": summary})
    assert fit["dof_is_ansatz"] == "from-the-report"


def test_fit_raises_when_summary_dof_differs_from_the_row_count():
    report = {**REPORT, "summary": {**REPORT["summary"], "dof": 3}}
    with pytest.raises(ValueError, match="summary.dof = 3 .* n = 7"):
        hs._fit(report)


def test_fit_raises_without_the_dof_ansatz_flag():
    summary = {k: v for k, v in REPORT["summary"].items() if k != "dof_is_ansatz"}
    with pytest.raises(KeyError, match="dof_is_ansatz"):
        hs._fit({**REPORT, "summary": summary})
