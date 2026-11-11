"""generate_statistics fails early, with a reason, when no sigma set exists.

FOUND 2026-10-25: a path whose simulations were blocked left no
parameters.json; generate_statistics then died on KeyError 'chi_squared',
hiding the real cause. Since XB-02 the one sigma source is this build's
statistical_rigor_report.json: a missing report raises FileNotFoundError
naming it, a report without scored rows raises ValueError.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
import json

import pytest

from metaphysica.generators import generate_statistics as gs


def _point_at(tmp_path, monkeypatch):
    for name in ("GATES_CERT_FILE", "PARAMETERS_FILE"):
        monkeypatch.setattr(gs, name, str(tmp_path / (name + ".json")))
    rigor = tmp_path / "statistical_rigor_report.json"
    monkeypatch.setattr(gs, "STATISTICAL_RIGOR_FILE", str(rigor))
    return rigor


def test_empty_inputs_raise_a_clear_error(tmp_path, monkeypatch):
    _point_at(tmp_path, monkeypatch)
    with pytest.raises(FileNotFoundError, match="statistical_rigor_report.json"):
        gs.generate_statistics()


def test_report_without_scored_rows_raises(tmp_path, monkeypatch):
    rigor = _point_at(tmp_path, monkeypatch)
    rigor.write_text(json.dumps({"chi_squared_from_rows": {"scored_rows": []}}),
                     encoding="utf-8")
    with pytest.raises(ValueError, match="no scored rows"):
        gs.generate_statistics()
