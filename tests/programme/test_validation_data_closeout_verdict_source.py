"""XV-03: the verdict and the headline p-value come from dof = N scored rows.

The EDOF=3 reading stays in ``edof_analysis`` as a labelled side figure and
never supplies ``summary.status`` or ``summary.p_value``.
"""
import json

import pytest
from scipy.stats import chi2

from metaphysica.simulations.PM.validation import statistical_rigor_validator as srv


@pytest.fixture(autouse=True)
def _no_build_output(monkeypatch):
    """The free-variable count is fixed here, not read from build output."""
    monkeypatch.setattr(srv.StatisticalRigorValidator, "free_variable_count",
                        staticmethod(lambda: 11))


def _validator(tmp_path, sigmas):
    """A validator over measured, scored rows with the given residual sigmas."""
    rows = [{"path": f"gauge.r{i}", "value": 1.0 + 0.1 * s,
             "experimental_value": 1.0, "experimental_uncertainty": 0.1,
             "verdict": "PASS", "registry_status": "DERIVED",
             "bound_type": "measured", "sigma": s}
            for i, s in enumerate(sigmas)]
    f = tmp_path / "validation_report.json"
    f.write_text(json.dumps({"validations": rows}), encoding="utf-8")
    return srv.StatisticalRigorValidator(str(f))


def test_headline_p_value_is_the_row_count_p_value(tmp_path):
    # Ten rows at 1.5 sigma: chi^2 = 22.5, N = 10 gives p ~ 0.013 (MARGINAL),
    # EDOF = 3 gives p ~ 5e-5 (POOR_FIT): the two readings disagree.
    rep = _validator(tmp_path, [1.5] * 10).generate_report()
    s, edof = rep["summary"], rep["edof_analysis"]
    expected = float(1 - chi2.cdf(s["chi_squared"], s["n_scored"]))
    assert s["dof"] == s["n_scored"] == 10
    assert s["p_value"] == pytest.approx(expected)
    assert s["p_value"] == s["p_value_n_dof"]
    assert "dof = N" in s["p_value_basis"]
    assert s["status"] == srv.StatisticalRigorValidator._p_value_status(expected)
    assert s["status"] != edof["status"]
    assert s["p_value"] != pytest.approx(edof["p_value"])
    assert s["status_edof_ansatz"] == edof["status"]
    assert s["dof"] == rep["chi_squared_from_rows"]["all_scoring_rows"]["n"]
    assert s["dof_is_ansatz"] is False
    assert s["p_value_edof_ansatz"] == edof["p_value"]


def test_edof_block_is_a_labelled_side_figure(tmp_path):
    rep = _validator(tmp_path, [0.5, 0.5, 0.5]).generate_report()
    edof = rep["edof_analysis"]
    assert edof["is_verdict"] is False
    assert edof["effective_dof_is_ansatz"] is True
    assert "summary.status" in edof["verdict_source"]
    assert "not the verdict" in edof["interpretation"]
    # No text in the block presents the ansatz as the correct reading.
    text = json.dumps(edof)
    assert "Properly accounts" not in text
    assert "inappropriate for topologically unified theory" not in text
    assert "side figure" in edof["comparison"]["edof_approach"]["role"]
    assert "verdict" in edof["comparison"]["traditional_approach"]["role"]


def test_edof_band_uses_the_shared_status_bands(tmp_path):
    v = _validator(tmp_path, [0.2, 0.2])
    edof = v.calculate_p_value_with_edof()
    assert edof["status"] == v._p_value_status(edof["p_value"])
    assert edof["reduced_chi_squared"] == pytest.approx(
        edof["chi_squared"] / edof["effective_dof"])


def test_band_edges_are_defined_once_and_drive_status_and_text(
        tmp_path, monkeypatch):
    # chi^2 = 0.08 over EDOF: p is close to 1, TOO_GOOD under the shipped
    # edges. Moving the upper edge above p must move both status and text.
    v = _validator(tmp_path, [0.2, 0.2])
    p = v.calculate_p_value_with_edof()["p_value"]
    assert v.calculate_p_value_with_edof()["status"] == "TOO_GOOD"
    assert f"p > {srv.P_CREDIBLE_HIGH}" in (
        v.calculate_p_value_with_edof()["interpretation"])
    monkeypatch.setattr(srv, "P_CREDIBLE_HIGH", (p + 1.0) / 2)
    edof = v.calculate_p_value_with_edof()
    assert edof["status"] == "CREDIBLE"
    assert edof["interpretation"].startswith(
        f"p in [{srv.P_CREDIBLE_LOW}, {srv.P_CREDIBLE_HIGH}] under EDOF = "
        f"{edof['effective_dof']}")


def test_edof_text_is_built_from_the_computed_edof(tmp_path, monkeypatch):
    monkeypatch.setattr(srv.StatisticalRigorValidator,
                        "calculate_effective_dof", lambda self: 4)
    rep = _validator(tmp_path, [0.5, 0.5]).generate_report()
    assert rep["edof_analysis"]["justification"].startswith("EDOF = 4 is an")
    assert "from 4 independent seeds" in rep["edof_analysis"]["justification"]
    assert rep["scaffold_notes"]["edof_ansatz"].startswith("EDOF = 4 is")
    assert "EDOF=3" not in json.dumps(rep)


def test_missing_validation_report_message_has_no_historical_literals(tmp_path):
    with pytest.raises(FileNotFoundError) as err:
        srv.StatisticalRigorValidator(str(tmp_path / "absent.json"))
    message = str(err.value)
    assert "absent.json" in message and "validation step" in message
    for stale in ("0.23", "DoF = 25", "TOO_GOOD", "v23.9"):
        assert stale not in message
