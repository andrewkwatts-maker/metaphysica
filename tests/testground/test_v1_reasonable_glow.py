"""V1: reasonable alternatives are marked on the path graph (path_ranking/1)."""
from __future__ import annotations

import json

import pytest

from metaphysica.testground.graph.build import build_graph
from metaphysica.testground.graph.export import export_graph, validate_graph
from metaphysica.testground.graph.ranking import (RankingInvalid,
                                                  load_ranking)
from metaphysica.theories.toy import THEORY


def _fixture(selected_sel, alt_sel):
    def row(pid, sel, rank, reasonable):
        return {"path_id": pid, "selection": sel, "rank": rank,
                "consistent": True, "ladder_failed": 0, "ladder_total": 3,
                "gates_failed": 0, "gates_applicable": 5, "chi2": 1.0,
                "dof": 2, "delta_chi2": 0.5 * rank, "reasonable": reasonable,
                "missing": []}
    return {"schema": "path_ranking/1", "rule": "lexicographic",
            "reasonable_rule": "consistent, delta_chi2 <= 4", "searched": 2,
            "selected": "sel", "rows": [row("sel", selected_sel, 1, True),
                                        row("alt", alt_sel, 2, True)]}


def _alt_selection():
    graph = build_graph(THEORY)
    opts = [n for n in graph["nodes"] if n["type"] == "option"
            and not n["attrs"]["on_active_path"]]
    assert opts, "toy theory needs an inactive option"
    n = opts[0]
    return {n["attrs"]["fork"]: n["label"]}


def test_fixture_ranking_marks_reasonable_options_and_edges():
    alt = _alt_selection()
    graph = build_graph(THEORY, ranking=_fixture({}, alt))
    marked = [n for n in graph["nodes"]
              if n["type"] == "option" and n["attrs"].get("reasonable")]
    assert [(n["attrs"]["fork"], n["label"]) for n in marked] == list(
        alt.items())
    assert marked[0]["attrs"]["rank"] == 2
    assert marked[0]["attrs"]["delta_chi2"] == 1.0
    assert not any(n["attrs"].get("reasonable") for n in graph["nodes"]
                   if n["attrs"].get("on_active_path"))
    assert any(e["class"] == "reasonable" for e in graph["edges"])
    assert graph["ranking"]["paths"][0]["path_id"] == "alt"
    assert "reasonable" in graph["legend"]
    assert validate_graph(graph) == []


def test_missing_ranking_sets_no_attributes():
    graph = build_graph(THEORY)
    assert "ranking" not in graph and "reasonable" not in graph["legend"]
    assert not any("reasonable" in n["attrs"] for n in graph["nodes"]
                   if n["type"] == "option")
    assert not any(e["class"] == "reasonable" for e in graph["edges"])


def test_export_reads_a_ranking_file_and_tolerates_absence(tmp_path):
    absent = export_graph(THEORY, tmp_path / "a.json",
                          ranking_path=tmp_path / "none.json")
    assert "ranking" not in absent
    rk = tmp_path / "path_ranking.json"
    rk.write_text(json.dumps(_fixture({}, _alt_selection())))
    got = export_graph(THEORY, tmp_path / "b.json", ranking_path=rk)
    assert got["ranking"]["selected"] == "sel"


def test_a_ranking_with_the_wrong_schema_fails_early(tmp_path):
    rk = tmp_path / "r.json"
    rk.write_text(json.dumps({"schema": "other", "rows": []}))
    with pytest.raises(RankingInvalid):
        load_ranking(rk)
