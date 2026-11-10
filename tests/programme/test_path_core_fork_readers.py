"""L1 path-core: fork readers measure behaviour or say they cannot.

core-paths-15: the metric reader returned "quadratic_contraction" when the
live metric matched neither option. core-paths-16: the re_t_adoption and
b3_seed readers returned literals and so could never report drift.
"""
import numpy as np
import pytest

from metaphysica.simulations.core.variants import SourceUnmeasurable, selection
from metaphysica.simulations.core.variants import adopted


def _patch_live_metric(monkeypatch, live):
    from metaphysica.simulations.PM.geometry import g2_differential as gd

    monkeypatch.setattr(gd.G2DifferentialGeometry, "metric_by_convention",
                        lambda self: live)


def test_metric_reader_raises_when_no_option_matches(monkeypatch):
    _patch_live_metric(monkeypatch, 5.0 * np.eye(7))
    with pytest.raises(SourceUnmeasurable, match="matches neither option"):
        adopted._metric_construction_adopted()


def test_metric_reader_raises_when_hitchin_metric_is_absent(monkeypatch):
    from metaphysica.simulations.PM.geometry import g2_differential as gd

    def no_metric(self):
        raise ValueError("unstable phi")

    _patch_live_metric(monkeypatch, 5.0 * np.eye(7))
    monkeypatch.setattr(gd.G2DifferentialGeometry, "compute_hitchin_metric",
                        no_metric)
    with pytest.raises(SourceUnmeasurable, match="hitchin_cubic"):
        adopted._metric_construction_adopted()


def test_metric_reader_still_measures_the_adopted_metric():
    assert adopted._metric_construction_adopted() == "quadratic_contraction"


@pytest.mark.parametrize("reader, fork", [
    (adopted._re_t_adoption_adopted, "re_t_adoption"),
    (adopted._b3_seed_adopted, "b3_seed"),
])
def test_self_referential_readers_are_declared_not_measured(reader, fork):
    with pytest.raises(SourceUnmeasurable, match=f"fork {fork}: declared"):
        reader()


def test_describe_reports_declared_readers_as_unmeasurable():
    from metaphysica.simulations.core.variants import describe

    forks = describe()["forks"]
    for fork in ("re_t_adoption", "b3_seed"):
        assert forks[fork]["source_read"].startswith("unmeasurable:")
        assert forks[fork]["drift"] is None


def test_h0_off_path_names_the_seed_without_the_literal_reader():
    from metaphysica.simulations.core.observable_groups import (
        h0_off_adopted_path,
    )

    assert h0_off_adopted_path() is None
    with selection.forced({"b3_seed": "seed_24"}):
        assert h0_off_adopted_path() == "b3_seed"
