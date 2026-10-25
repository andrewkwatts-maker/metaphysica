"""D-025 falsifiers for the geometry-to-physics walkthrough.

Run with METAPHYSICA_OUT pointing at the built site (it reads the artifacts).
"""
import json

import pytest

from metaphysica.generators import generate_geometry_to_physics as gen
from metaphysica.generators._common import autogen_dir
from metaphysica.simulations.PM.paper.physics_chain import (
    CHAIN, STAGE_IDS, Step)


@pytest.fixture(scope="module")
def ctx():
    try:
        return gen.load_context()
    except FileNotFoundError as exc:
        pytest.skip(str(exc))


@pytest.fixture(scope="module")
def doc(ctx):
    return gen.build_walkthrough(ctx)


def _load(name):
    with open(autogen_dir() / name, encoding="utf-8") as fh:
        return json.load(fh)


def test_chain_size_and_stage_order():
    assert 20 <= len(CHAIN) <= 35
    idx = [STAGE_IDS.index(s.stage) for s in CHAIN]
    assert idx == sorted(idx)
    assert set(idx) == set(range(len(STAGE_IDS)))


def test_values_equal_parameters_json(ctx, doc):
    params = ctx["params"]
    checked = 0
    for s in doc["steps"]:
        if s["param_path"] and not s["theorem_id"]:
            assert s["value"] == params[s["param_path"]]["value"], s["id"]
            checked += 1
    assert checked >= 15


def test_status_equals_registry_status(ctx, doc):
    for s in doc["steps"]:
        if s["theorem_id"]:
            continue
        entry = ctx["params"][s["param_path"]]
        want = entry.get("status") or ctx["formulas"][s["formula_id"]]["category"]
        assert s["status"] == want, s["id"]


def test_output_stage_order_matches_declared(doc):
    declared = [st["id"] for st in doc["stages"]]
    assert declared == list(STAGE_IDS)
    seen = []
    for s in doc["steps"]:
        if not seen or seen[-1] != s["stage"]:
            seen.append(s["stage"])
    assert seen == list(STAGE_IDS)


def test_unknown_param_path_is_open_not_a_crash(ctx):
    bogus = Step("x", "bulk", "in", "op", "X", param_path="no.such.param",
                 section_id="2.1")
    out = gen.build_walkthrough(ctx, chain=(bogus,))["steps"][0]
    assert out["value"] == gen.OPEN
    assert out["status"] == gen.OPEN
    assert out["tone"] == "open"
    assert "value" in out["why"]


def test_unknown_formula_is_open(ctx):
    bogus = Step("x", "bulk", "in", "op", "X", formula_id="no-such-formula",
                 param_path="dimensions.D_bulk")
    out = gen.build_walkthrough(ctx, chain=(bogus,))["steps"][0]
    assert out["formula"]["latex"] == gen.OPEN
    assert "formula" in out["why"]


def test_a_failing_step_is_shown_when_the_report_has_fails(ctx, doc):
    report = _load("validation_report.json")
    if report["summary"]["fail"] == 0:
        pytest.skip("validation_report has no fails")
    assert any(s["tone"] == "fail" for s in doc["steps"])
    assert doc["summary"]["by_verdict"].get("FAIL", 0) >= 1


def test_experiment_matches_validation_report(ctx, doc):
    for s in doc["steps"]:
        row = ctx["validations"].get(s["param_path"])
        if row:
            assert s["experiment"]["pull"] == row["sigma"], s["id"]
            assert s["experiment"]["verdict"] == row["verdict"], s["id"]


def test_missing_parameters_fails_early(tmp_path, monkeypatch):
    monkeypatch.setenv("METAPHYSICA_OUT", str(tmp_path))
    with pytest.raises(FileNotFoundError):
        gen.load_context()
