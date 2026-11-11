"""XV-11: the validator has one row adapter, the one its constructor uses.

``_adapt_validation_rows`` was called only by tests; production reads rows
through ``_adapt_report_rows`` and ``observables.partition_rows``. It is
removed, and the scored rows are checked through the constructor.
"""
import json

from metaphysica.simulations.PM.validation.statistical_rigor_validator import (
    StatisticalRigorValidator,
)


def test_test_only_adapter_is_gone():
    assert not hasattr(StatisticalRigorValidator, "_adapt_validation_rows")


def test_constructor_scores_only_two_sided_rows(tmp_path):
    data = {"validations": [
        {"path": "two_sided", "verdict": "PASS", "value": 1.0,
         "bound_type": "measured", "experimental_value": 1.0,
         "experimental_uncertainty": 0.1},
        {"path": "one_sided", "verdict": "PASS", "value": 2.0e16,
         "bound_type": "lower", "experimental_value": 1.0e15,
         "experimental_uncertainty": 1.0e14},
        {"path": "input", "verdict": "INPUT", "value": 2.0,
         "bound_type": "measured", "experimental_value": 2.0,
         "experimental_uncertainty": 0.2},
    ]}
    report = tmp_path / "validation_report.json"
    report.write_text(json.dumps(data), encoding="utf-8")
    validator = StatisticalRigorValidator(validation_file=str(report))
    assert [r["path"] for r in validator.validation_results] == ["two_sided"]
    assert validator.dof_claimed == 1
