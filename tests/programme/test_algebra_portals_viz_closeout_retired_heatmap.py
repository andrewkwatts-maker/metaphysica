"""XA-04 (part): the stale stability-heatmap output sits beside the retired figures.

stability_heatmap.py is RETIRED_FROM_PAPER and writes to ``<its folder>/retired``
(``_retired.output_dir_for``). The tracked HTML and data file it once wrote at
the top of the visualizations folder are kept (rule 5) but moved there, so no
plot list or site scan of the live folder picks them up.
"""
from importlib.util import find_spec
from pathlib import Path

from metaphysica.simulations.visualizations import _retired

_NAMES = ("stability_heatmap.html", "stability_heatmap_data.json")


def _viz_dir() -> Path:
    spec = find_spec("metaphysica.simulations.visualizations")
    assert spec is not None and spec.submodule_search_locations
    return Path(list(spec.submodule_search_locations)[0])


def test_stale_heatmap_outputs_are_not_in_the_live_folder():
    live = _viz_dir()
    for name in _NAMES:
        assert not (live / name).exists(), f"{name} still in the live figure folder"


def test_stale_heatmap_outputs_are_kept_in_the_retired_folder():
    retired = _viz_dir() / _retired.RETIRED_SUBDIR
    for name in _NAMES:
        path = retired / name
        assert path.is_file(), f"{name} not kept under {retired}"
        assert path.stat().st_size > 0
