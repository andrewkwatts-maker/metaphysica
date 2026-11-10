"""generate_statistics: write-back is data-driven, gate totals come from the tally."""
import ast
import json
from pathlib import Path

import pytest

from metaphysica.generators import generate_statistics as gs

SRC = Path(gs.__file__)
STATS = {
    "framework_statistics": {
        "pass_count": 3, "pending_count": 1, "not_testable_count": 4,
        "mathematical_count": 2, "total_gates": 71, "testable_count": 67,
        "exact_matches": 0, "status": "POOR_FIT",
        **{k: 1 for k in gs.HEADLINE_KEYS},
    },
    "validation": {"within_1sigma": 1, "within_2sigma": 2, "total_predictions": 5,
                   "success_rate": "40.0%"},
}


def test_no_function_over_sixty_lines():
    tree = ast.parse(SRC.read_text(encoding="utf-8"))
    long = [f.name for f in ast.walk(tree) if isinstance(f, ast.FunctionDef)
            and f.end_lineno - f.lineno + 1 > 60]
    assert long == []


def test_no_gate_total_literal_in_text():
    assert "eml_scalar(72" not in SRC.read_text(encoding="utf-8")
    assert "Gates Total = 72" not in SRC.read_text(encoding="utf-8")


def test_write_back_uses_computed_gate_total(tmp_path, monkeypatch):
    path = tmp_path / "parameters.json"
    path.write_text(json.dumps({"parameters": {"keep": {"value": 1}}}), encoding="utf-8")
    monkeypatch.setattr(gs, "PARAMETERS_FILE", str(path))
    gs._write_back_parameters(STATS)
    rows = json.loads(path.read_text(encoding="utf-8"))["parameters"]
    assert rows["keep"] == {"value": 1}
    assert rows["framework_statistics.total_gates"]["value"] == 71
    assert "eml_scalar(71)" in rows["framework_statistics.total_gates"]["eml_description"]
    assert rows["validation.success_rate"]["value"] == "40.0%"
    assert rows["framework_statistics.pending_count"]["value"] == 1


def test_missing_key_raises(tmp_path, monkeypatch):
    path = tmp_path / "parameters.json"
    path.write_text(json.dumps({"parameters": {}}), encoding="utf-8")
    monkeypatch.setattr(gs, "PARAMETERS_FILE", str(path))
    bad = json.loads(json.dumps(STATS))
    del bad["validation"]["within_1sigma"]
    with pytest.raises(KeyError):
        gs._write_back_parameters(bad)


def test_status_is_not_a_declarative_count_label():
    text = SRC.read_text(encoding="utf-8")
    assert "MAJORITY_VERIFIED" not in text.replace("MAJORITY_VERIFIED from the", "")
    assert "_collect_sigmas" in text
