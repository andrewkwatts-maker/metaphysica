"""The final statistics pass must follow the step that writes its sigma source."""
from __future__ import annotations

import importlib

build_mod = importlib.import_module("metaphysica.build")


def _index(module: str) -> list:
    return [i for i, (_, cmd, _) in enumerate(build_mod.STEPS) if cmd[-1] == module]


def test_statistics_are_refreshed_after_the_rigor_report_is_written():
    stats = _index("metaphysica.generators.generate_statistics")
    rigor = _index("metaphysica.simulations.PM.validation.statistical_rigor_validator")
    assert rigor and stats
    assert max(stats) > max(rigor), (
        "a fresh build would compute statistics from a fallback or stale report")
