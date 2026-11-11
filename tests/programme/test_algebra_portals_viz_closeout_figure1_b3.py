"""L6 close-out, figure1_m27_decomposition XA-09: the b3 label is the registry row's value,
and the Leech box no longer says "24D G2 Core" (G2 holonomy is Y_7's, seven dimensions)."""
import pytest

pytest.importorskip("matplotlib")
import matplotlib  # noqa: E402

matplotlib.use("Agg")
from matplotlib.axes import Axes  # noqa: E402

from metaphysica.simulations.visualizations import figure1_m27_decomposition as f1  # noqa: E402


def _labels(tmp_path, monkeypatch, b3):
    monkeypatch.setenv("METAPHYSICA_OUT", str(tmp_path))
    seen = []
    real = Axes.text

    def spy(self, x, y, s, *a, **k):
        seen.append(str(s))
        return real(self, x, y, s, *a, **k)

    monkeypatch.setattr(Axes, "text", spy)
    f1.generate_figure1_m27_decomposition({"parameters": {f1.B3_ROW: {"value": b3}}})
    return seen


def test_b3_label_follows_the_registry_row(tmp_path, monkeypatch):
    assert "$b_3 = 43$ of $Y_7$ (registry)" in _labels(tmp_path, monkeypatch, 43)
    assert "$b_3 = 17$ of $Y_7$ (registry)" in _labels(tmp_path, monkeypatch, 17)


def test_no_24d_g2_core_label(tmp_path, monkeypatch):
    assert not any("24D G$_2$ Core" in s for s in _labels(tmp_path, monkeypatch, 43))


def test_missing_b3_row_raises():
    with pytest.raises(KeyError):
        f1.b3_from_registry({"parameters": {}})
    with pytest.raises(KeyError):
        f1.b3_from_registry({"parameters": {f1.B3_ROW: {"value": None}}})
