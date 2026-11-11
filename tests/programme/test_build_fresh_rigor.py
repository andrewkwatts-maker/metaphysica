"""XB-03: the rigor validator fails early, by name, when no row is scored.

Before the fix, ``calculate_p_value_with_edof`` and ``generate_report``
divided chi^2 by N = 0 and raised a bare ZeroDivisionError.
"""
import json

import pytest

from metaphysica.simulations.PM.validation.statistical_rigor_validator import (
    StatisticalRigorValidator,
)


def _validator(tmp_path, validations):
    path = tmp_path / "validation_report.json"
    path.write_text(json.dumps({"validations": validations}), encoding="utf-8")
    return StatisticalRigorValidator(validation_file=str(path))


UNSCORED_ROW = {
    "path": "demo.no_uncertainty", "verdict": "PASS", "value": 1.0,
    "experimental_value": 1.0, "experimental_uncertainty": None,
    "bound_type": "measured", "sigma": None, "registry_status": None,
}


@pytest.mark.parametrize("rows", [[], [UNSCORED_ROW]])
def test_p_value_without_scored_rows_raises_by_name(tmp_path, rows):
    validator = _validator(tmp_path, rows)
    with pytest.raises(ValueError, match="no scored prediction rows"):
        validator.calculate_p_value_with_edof()


@pytest.mark.parametrize("rows", [[], [UNSCORED_ROW]])
def test_report_without_scored_rows_raises_by_name(tmp_path, rows):
    validator = _validator(tmp_path, rows)
    with pytest.raises(ValueError, match="validation_report.json"):
        validator.generate_report()
