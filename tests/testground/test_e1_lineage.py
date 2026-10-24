"""E1: lineage model/loader/layout, path_graph/2, the PM adapter, the build step.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from metaphysica.testground.graph.build import SCHEMA_ID, build_graph
from metaphysica.testground.graph.export import export_graph, validate_graph
from metaphysica.testground.lineage.layout import layout_lineage
from metaphysica.testground.lineage.load import (LineageError, load_lineage,
                                                 parse_lineage)

TOY_LINEAGE = (Path(__file__).resolve().parents[2] / "src" / "metaphysica"
               / "theories" / "toy" / "configs" / "lineage.yaml")


def _doc():
    return {
        "schema": "metaphysica.lineage/1",
        "sources": "tests",
        "versions": [
            {"id": "a", "label": "A", "era": "2025-07", "status": "trunk",
             "parent": None, "superseded_by": "b"},
            {"id": "b", "label": "B", "era": "2025-08", "status": "active",
             "parent": "a"},
            {"id": "c", "label": "C", "era": "2025-08", "status": "branch",
             "parent": "a",
             "branches_considered": [{"title": "t", "answer": "x"}]},
        ],
        "forks": [{"id": "df", "question": "q?"}],
        "options": [{"fork": "df", "id": "o1", "summary": "s"}],
    }


def test_a_valid_catalogue_loads_with_pass_through_fields():
    lin = parse_lineage(_doc())
    assert [v.id for v in lin.versions] == ["a", "b", "c"]
    assert lin.sources == "tests"
    assert lin.versions[2].branches_considered[0]["title"] == "t"
    assert lin.active.id == "b"


@pytest.mark.parametrize("mutate,text", [
    (lambda d: d["versions"][1].update(parent="zz"), "unknown parent"),
    (lambda d: d["versions"][0].update(superseded_by="zz"),
     "unknown superseded_by"),
    (lambda d: d["versions"][0].update(parent="b"), "cycle"),
    (lambda d: d["versions"][1].update(status="trunk"), "exactly one"),
    (lambda d: d["versions"][2].update(status="active"), "exactly one"),
    (lambda d: d["versions"][2].update(status="weird"), "unknown status"),
    (lambda d: d["versions"][2].update(id="a"), "duplicate version"),
    (lambda d: d["options"][0].update(fork="nope"), "not declared"),
    (lambda d: d["options"][0].update(status="odd"), "unknown status"),
])
def test_the_loader_fails_early(mutate, text):
    doc = _doc()
    mutate(doc)
    with pytest.raises(LineageError, match=text):
        parse_lineage(doc)


def test_an_option_may_attach_to_a_known_engine_fork():
    doc = _doc()
    doc["options"][0]["fork"] = "engine_fork"
    assert parse_lineage(doc, known_forks=["engine_fork"]).options


def test_layout_lanes_have_no_overlaps_and_trunk_is_lane_zero():
    lay = layout_lineage(parse_lineage(_doc()))
    pos = lay["positions"]
    assert pos["version:a"][1] == pos["version:b"][1] == lay["lanes"][0]["y"]
    assert pos["version:c"][1] > pos["version:b"][1]
    assert pos["version:b"][0] == pos["version:c"][0] > pos["version:a"][0]
    assert [e["label"] for e in lay["eras"]] == ["2025-07", "2025-08"]
    assert all(isinstance(n, int) for b in pos.values() for n in b)
    boxes = list(pos.values())
    for i, p in enumerate(boxes):
        for q in boxes[i + 1:]:
            assert p[:2] != q[:2]


def test_two_trunk_versions_in_one_era_do_not_overlap():
    doc = _doc()
    doc["versions"][1]["status"] = "trunk"
    doc["versions"][2]["status"] = "active"
    doc["versions"][2]["era"] = "2025-08"
    pos = layout_lineage(parse_lineage(doc))["positions"]
    assert pos["version:b"][:2] != pos["version:c"][:2]


def test_toy_exports_path_graph_2_with_lineage(tmp_path):
    from metaphysica.theories.toy import THEORY
    graph = export_graph(THEORY, tmp_path / "g.json")
    assert graph["schema"] == SCHEMA_ID == "metaphysica.path_graph/2"
    assert graph["views"] == ["lineage", "switches"]
    versions = [n for n in graph["nodes"] if n["type"] == "version"]
    assert len(versions) == 3
    kinds = {e["type"] for e in graph["edges"]}
    assert {"evolves_to", "superseded_by", "maps_to"} <= kinds
    assert set(graph["layout"]["lineage"]["positions"]) == {
        n["id"] for n in versions}
    assert "layout" in graph and graph["layout"]["columns"]
    assert validate_graph(graph) == []
    v = next(n for n in versions if n["id"] == "version:fitted_coupling")
    assert v["attrs"]["era_order"] == 1 and v["class"] == "dead_end"


def test_a_theory_without_lineage_has_only_the_switches_view():
    from dataclasses import replace
    from metaphysica.theories.toy import THEORY
    graph = build_graph(replace(THEORY, lineage=None))
    assert graph["views"] == ["switches"] and "lineage" not in graph["layout"]
    assert not [n for n in graph["nodes"] if n["type"] == "version"]


def test_declared_only_options_are_not_implemented_nodes(tmp_path):
    from dataclasses import replace
    from metaphysica.theories.toy import THEORY
    doc = _doc()
    doc["options"] = [{"fork": "cutoff", "id": "ghost", "summary": "s",
                       "status": "rejected", "restored_from": "abc:x.py"}]
    doc["forks"] = [{"id": "df", "question": "q?"}]
    import yaml
    path = tmp_path / "l.yaml"
    path.write_text(yaml.safe_dump(doc), encoding="utf-8")
    graph = build_graph(replace(THEORY, lineage=path))
    node = next(n for n in graph["nodes"] if n["id"] == "option:cutoff.ghost")
    assert node["class"] == "not_implemented"
    assert node["attrs"]["implemented"] is False
    assert node["attrs"]["restored_from"] == "abc:x.py"
    assert any(n["id"] == "fork:df" for n in graph["nodes"])
    assert validate_graph(graph) == []


def test_decision_titles_keep_their_unicode(tmp_path):
    """The log is read as UTF-8: an em dash must not become mojibake."""
    from metaphysica.theories.toy import THEORY
    log = tmp_path / "LOG.md"
    log.write_text("## D-001 · 2026-01-01 · G0 · PRE-REGISTERED"
                   " — the em dash — title\n\nbody\n",
                   encoding="utf-8", newline="\n")
    graph = build_graph(THEORY, decision_log=log)
    text = json.dumps(graph, ensure_ascii=False)
    assert "â€" not in text
    titles = [d["title"] for d in graph["decisions"] if d["in_log"]]
    assert all("â" not in t for t in titles)
    from metaphysica.testground.decisions.log import DecisionLog
    entry = DecisionLog.load(log).entries[0]
    assert "—" in entry.title or "em dash" in entry.title


def test_cli_imports_and_renders_the_accept_text():
    from metaphysica.testground import cli
    text = cli._act_text({"log_path": "LOG.md", "entry_text": "E\n",
                          "pending_edits": ["p"], "stale_reasons": ["s"]})
    assert "decision log LOG.md:\nE" in text
    assert text.splitlines()[0] != ""
    assert "pending edit: p" in text and "stale: s" in text


def test_the_pm_theory_exports_a_valid_graph(tmp_path):
    from metaphysica.theories.pm import THEORY
    graph = export_graph(THEORY, tmp_path / "pm.json")
    assert validate_graph(graph) == []
    options = [n for n in graph["nodes"] if n["type"] == "option"]
    assert any(n["attrs"]["implemented"] for n in options)
    assert any(n["class"] == "not_implemented" for n in options)
    assert sum(n["type"] == "version" for n in graph["nodes"]) == len(
        load_lineage(THEORY.lineage, THEORY.switches.forks()).versions)


def test_the_pm_selection_is_read_only():
    from metaphysica.theories.pm import THEORY
    from metaphysica.testground.configurations.model import Configuration
    cfg = THEORY.selections.active()
    assert dict(cfg.mapping) and THEORY.env_prefix == "METAPHYSICA_VARIANT_"
    with pytest.raises(RuntimeError, match="read-only"):
        THEORY.selections.write_active(Configuration.of("pm", {}), "D-000")


def test_the_pm_decision_log_follows_the_environment(monkeypatch, tmp_path):
    from metaphysica.theories import pm
    log = tmp_path / "DL.md"
    log.write_text("x", encoding="utf-8")
    monkeypatch.setenv(pm.ENV_DECISION_LOG, str(log))
    assert pm.find_decision_log() == log
    monkeypatch.setenv(pm.ENV_DECISION_LOG, str(tmp_path / "absent.md"))
    assert pm.find_decision_log() is None


def test_the_path_graph_step_writes_one_file_and_keeps_paths(tmp_path):
    import importlib
    build = importlib.import_module("metaphysica.build")
    paths = tmp_path / "AutoGenerated" / "paths" / "main"
    paths.mkdir(parents=True)
    keep = paths / "summary.json"
    keep.write_text("{}", encoding="utf-8")
    target = build.write_path_graph(tmp_path)
    assert target == tmp_path / "AutoGenerated" / "path_graph.json"
    assert json.loads(target.read_text(encoding="utf-8"))["schema"] == \
        SCHEMA_ID
    assert keep.read_text(encoding="utf-8") == "{}"
    assert any(label == "Export the path graph" and not extra
               for label, _, extra in build.STEPS)


def test_the_toy_lineage_file_is_valid():
    assert len(load_lineage(TOY_LINEAGE).versions) == 3
    assert copy.deepcopy(_doc())
