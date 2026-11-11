"""XV-05 (EDOF half): ``calculate_p_value_with_edof`` is 60 lines or fewer.

The split moved the justification text and the dof comparison into
``_edof_justification`` and ``_dof_comparison``; the returned dict keeps its
keys and values. The function was 92 lines before the split (2eb361f).
"""
import inspect
import json

import pytest
from scipy.stats import chi2

from metaphysica.simulations.PM.validation import statistical_rigor_validator as srv

V = srv.StatisticalRigorValidator
EDOF_KEYS = {
    "chi_squared", "effective_dof", "effective_dof_is_ansatz",
    "traditional_dof", "free_variable_count", "free_variable_count_source",
    "reduced_chi_squared", "p_value", "status", "is_credible", "is_verdict",
    "verdict_source", "interpretation", "justification", "comparison",
}


def _validator(tmp_path, sigmas):
    """A validator over measured, scored rows with the given residual sigmas."""
    rows = [{"path": f"gauge.r{i}", "value": 1.0 + 0.1 * s,
             "experimental_value": 1.0, "experimental_uncertainty": 0.1,
             "verdict": "PASS", "registry_status": "DERIVED",
             "bound_type": "measured", "sigma": s}
            for i, s in enumerate(sigmas)]
    f = tmp_path / "validation_report.json"
    f.write_text(json.dumps({"validations": rows}), encoding="utf-8")
    return V(str(f))


@pytest.mark.parametrize("name", [
    "calculate_p_value_with_edof", "_edof_justification", "_dof_comparison"])
def test_edof_functions_are_60_lines_or_fewer(name):
    lines = inspect.getsource(getattr(V, name)).splitlines()
    assert len(lines) <= 60, f"{name} is {len(lines)} lines"


def test_edof_dict_keys_and_values_after_split(tmp_path):
    v = _validator(tmp_path, [1.0, 2.0])
    out = v.calculate_p_value_with_edof()
    assert set(out) == EDOF_KEYS
    edof, chi_sq = out["effective_dof"], out["chi_squared"]
    assert chi_sq == pytest.approx(5.0)
    assert out["p_value"] == pytest.approx(float(1 - chi2.cdf(chi_sq, edof)))
    assert out["reduced_chi_squared"] == pytest.approx(chi_sq / edof)
    assert out["traditional_dof"] == 2
    assert out["justification"] == V._edof_justification(out["free_variable_count"])
    assert out["comparison"] == v._dof_comparison(edof, chi_sq / edof)
    assert out["comparison"]["traditional_approach"]["reduced_chi_sq"] == (
        pytest.approx(chi_sq / 2))
