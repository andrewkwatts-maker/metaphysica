"""Engine-driven SVG figures for the closed G2 geometry beginner topics."""
import re
import xml.etree.ElementTree as ET

import pytest

from metaphysica.simulations.PM.geometry.closed_geometry.simulation import (
    ClosedGeometrySimulation,
)
from metaphysica.simulations.PM.geometry.figures import (
    betti_figure, eh_profile_figure, figure_data, fold_figure,
    geometry_figures, proof_flow_figure,
    proof_figures, proof_steps,
)
from metaphysica.simulations.PM.geometry.g2_geometry import G2GeometryV16


def _parse(svg):
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg") and root.get("viewBox")
    assert root.find("{http://www.w3.org/2000/svg}title") is not None
    assert root.find("{http://www.w3.org/2000/svg}desc") is not None
    return root


def _alltext(svg):
    return " ".join(_parse(svg).itertext())


def test_all_figures_parse_on_active_path():
    data = figure_data()
    for svg in (fold_figure(data), betti_figure(data), eh_profile_figure(),
                proof_flow_figure(data)):
        _parse(svg)


def test_numbers_equal_engine_values():
    data = figure_data()
    res = data["resolution"]
    assert data["refusal"] is None
    fold = _alltext(fold_figure(data))
    assert "%d singular 3-tori" % res["n_components"] in fold
    assert "%d folding generators" % res["n_singular_involutions"] in fold
    assert "b2 = %d" % res["b2"] in fold
    betti = _alltext(betti_figure(data))
    assert "b3 = %d" % res["b3"] in betti
    assert "3 × %d = %d" % (res["b2"], 3 * res["b2"]) in betti
    assert (res["b2"], res["b3"]) == (data["declared_b2"], data["declared_b3"])


def test_eh_profile_is_sampled_from_formula():
    root = _parse(eh_profile_figure(samples=5))
    pts = root.find(".//{http://www.w3.org/2000/svg}polyline").get("points").split()
    assert len(pts) == 5
    assert pts[0].endswith(",220.0")          # f(a) = 0 at the bolt


def test_proof_flow_reports_each_hypothesis():
    data = figure_data()
    txt = _alltext(proof_flow_figure(data))
    for row in data["closure"]["hypotheses"]:
        assert row["id"] in txt
    for c in data["closure"]["conclusions"]:
        assert c["by"].split(":")[0] in txt
    assert "Joyce 2000, Thm 11.6.1" in txt


def test_seed_24_carries_refusal_reason(monkeypatch):
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_24")
    data = figure_data()
    assert data["refusal"] and "declares (b2, b3) = (4, 24)" in data["refusal"]
    for svg in (fold_figure(data), betti_figure(data)):
        txt = _alltext(svg)
        assert "declares (b2, b3) = (4, 24)" in txt
        assert not re.search(r"b3 = \d", txt)
    flow = _alltext(proof_flow_figure(data))
    assert "not measured" in flow and "not reached" in flow


def test_topics_carry_figures_and_steps():
    for topic in (G2GeometryV16().get_beginner_explanation(),
                  ClosedGeometrySimulation().get_beginner_explanation()):
        assert topic["steps"] and all(isinstance(s, str) and s for s in topic["steps"])
        assert topic["figures"]
        for fig in topic["figures"]:
            assert set(fig) == {"id", "title", "caption", "svg", "data_source"}
            _parse(fig["svg"])
    steps = ClosedGeometrySimulation().get_beginner_explanation()["steps"]
    assert all("Source:" in s for s in steps)
    assert len(steps) == len(figure_data()["closure"]["hypotheses"]) + 3
