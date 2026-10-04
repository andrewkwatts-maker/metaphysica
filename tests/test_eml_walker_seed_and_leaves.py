"""The EML dependency walker roots formulas by LABEL against the LIVE seed,
and gives the same answer every time and through every instrument.

WHY THIS EXISTS
---------------
Three defects, each pinned below:

1. ``b3_leaf()`` was invisible. The tree parser emits it as a childless
   compound node labelled ``b3_leaf``; the walker recognised neither that
   label nor ``flavour_b3_leaf``, so 88 of the 89 formulas whose tree calls
   ``b3_leaf()`` were reported as not rooted in b3.
2. The seed was a literal. ``B3_VALUE = 24.0`` and ``root_seed: "b3=24"``
   survived the 2026-09-22 adoption of ``seed_43_joyce``, so a bare 24 (the
   Leech dimension, D_space_24) was counted as the seed.
3. The count moved between runs. The walk was a pure function of its inputs,
   but it changed instrument with the state of the disk: with eml_trees.json
   present it walked parsed trees (b3_leaf unseen), without it it scanned for
   the substring "b3" (b3_leaf seen) -- 113 vs 208 rooted on one unchanged
   formulas.json. Every representation now applies one rule set.

Nothing here writes into an artifact tree: walks are run in memory or into
pytest's tmp_path, and the walker is never pointed at autogen_dir().
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from metaphysica.generators import _dependency_walk_common as common
from metaphysica.generators import generate_eml_dependency_walker as walker
from metaphysica.simulations.PM.geometry.b3_path import seed_values


def _corpus():
    """Small formulas.json stand-in covering every leaf rule."""
    return {
        "via-b3-leaf":   {"eml_tree_str": "ops.mul(eml_scalar(6.0), b3_leaf())"},
        "via-flavour":   {"eml_tree_str": "ops.div(flavour_b3_leaf(), eml_scalar(8.0))"},
        "via-name":      {"eml_tree_str": "ops.inv(ops.sqrt(b3))"},
        "via-vec":       {"eml_tree_str": "ops.div(eml_vec('topology.elder_kads'), eml_scalar(2))"},
        "negated-leaf":  {"eml_tree_str": "ops.add(-b3, eml_scalar(1.0))"},
        "raw-24":        {"eml_tree_str": "ops.add(eml_scalar(24.0), eml_scalar(2.0))"},
        "lookalike":     {"eml_tree_str": "ops.mul(b3_over_2pi, delta_b3)"},
        "comment-only":  {"eml_tree_str": "ops.mul(eml_scalar(2.0), x)  # b3_leaf() not here"},
        "prose-desc":    {"eml_tree_str": "", "eml_description": "depends on b3 somehow"},
        "eml-desc":      {"eml_tree_str": "",
                          "eml_description": "EML: ops.mul(b3_leaf(), eml_scalar(2)) — prose b3"},
        "no-tree":       {"eml_tree_str": "", "eml_description": ""},
        "raw-seed": {"eml_tree_str": "ops.add(eml_scalar(%s.0), eml_scalar(1.0))" % seed_values()[0]},
    }


def _walk(formulas, **kw):
    kw.setdefault("sites", [])
    return walker.walk(formulas, **kw)


def _verdicts(out):
    return {fid: ("rooted" if c["b3_rooted"] else
                  "ambiguous" if c["ambiguous"] else "not_rooted")
            for fid, c in out["chains"].items()}


# ── 1. b3_leaf() is a b3 root ────────────────────────────────────────────────

@pytest.mark.parametrize("label", ["b3_leaf", "b3_leaf()", "flavour_b3_leaf",
                                   "flavour_b3_leaf()", "b3", "-b3",
                                   "topology.elder_kads"])
def test_b3_leaf_labels_are_recognised(label):
    assert common.is_b3_label(label)


@pytest.mark.parametrize("label", ["b3_over_2pi", "delta_b3", "b30", "kb3", "", None])
def test_lookalikes_are_not_b3(label):
    assert not common.is_b3_label(label)


def test_a_parsed_b3_leaf_node_roots_the_formula():
    """The exact shape the parser emits: a childless compound named b3_leaf."""
    b3 = seed_values()[0]
    tree = ["mul", "c", ["6", "#"], ["b3_leaf", "c"]]
    chain = walker._chain_for_tree(tree, "compact", b3)
    assert chain["b3_rooted"] and chain["b3_leaf_count"] == 1
    assert chain["paths"] == [["mul", "b3_leaf"]]
    flavour = walker._chain_for_tree(["flavour_b3_leaf", "c"], "compact", b3)
    assert flavour["b3_rooted"]


def test_the_corpus_verdicts():
    v = _verdicts(_walk(_corpus()))
    assert v == {
        "via-b3-leaf": "rooted", "via-flavour": "rooted", "via-name": "rooted",
        "via-vec": "rooted", "negated-leaf": "rooted", "eml-desc": "rooted",
        "raw-seed": "ambiguous",
        "raw-24": "not_rooted", "lookalike": "not_rooted",
        "comment-only": "not_rooted", "prose-desc": "not_rooted",
        "no-tree": "not_rooted",
    }


# ── 2. the seed is the live one ──────────────────────────────────────────────

def test_the_walker_seed_is_the_live_b3():
    b3, b2 = seed_values()
    assert common.live_b3() == b3
    assert common.B3_VALUE == float(b3)          # the old name, now live
    out = _walk(_corpus())
    assert out["root_seed"] == f"b3={b3}"
    assert out["seed"]["b3"] == b3 and out["seed"]["b2"] == b2


def test_the_walker_follows_a_seed_override(monkeypatch):
    """Under the seed_24 override the walk measures against 24, and says so."""
    monkeypatch.setenv("METAPHYSICA_VARIANT_B3_SEED", "seed_24")
    assert common.live_b3() == seed_values()[0] == 24
    out = _walk(_corpus())
    assert out["root_seed"] == "b3=24"
    assert _verdicts(out)["raw-24"] == "ambiguous"


def test_a_raw_24_is_not_the_adopted_seed():
    if seed_values()[0] == 24:
        pytest.skip("seed_24 override in force")
    assert not common.is_b3_scalar("24", seed_values()[0])
    assert common.is_b3_scalar("%d.0" % seed_values()[0])


# ── 3. determinism ───────────────────────────────────────────────────────────

def test_the_three_counts_partition_the_total():
    out = _walk(_corpus())
    assert (out["b3_rooted_count"] + out["ambiguous_count"]
            + out["non_b3_rooted_count"]) == out["total_formulas"]


def test_every_instrument_gives_the_same_verdicts():
    """Parsed tree, cached tree, string scan: one rule set, one answer.

    This is the instability itself. The cache here is built with the same
    parser, standing in for eml_trees.json.
    """
    formulas = _corpus()
    parse = walker.load_parser()
    if parse is None:
        pytest.skip("eml_math not importable")
    cache = {}
    for fid, f in formulas.items():
        expr, _ = walker.tree_expression(f)
        if expr:
            cache[fid] = {"c": parse(expr)}
    parsed = _walk(formulas, eml_trees=cache)
    cached = _walk(formulas, eml_trees=cache, parser=None)
    scanned = _walk(formulas, eml_trees=None, parser=None)
    assert parsed["tree_source_counts"]["parsed"] > 0
    assert cached["tree_source_counts"]["compact"] > 0
    assert scanned["tree_source_counts"]["string_scan"] > 0
    assert _verdicts(parsed) == _verdicts(cached) == _verdicts(scanned)
    assert parsed["cache_check"]["stale"] == 0


def test_a_stale_cache_is_reported_not_trusted():
    formulas = {"f": {"eml_tree_str": "ops.mul(eml_scalar(6.0), b3_leaf())"}}
    if walker.load_parser() is None:
        pytest.skip("eml_math not importable")
    stale = {"f": {"c": ["mul", "c", ["6", "#"], ["24", "#"]]}}
    out = _walk(formulas, eml_trees=stale)
    assert out["chains"]["f"]["b3_rooted"]
    assert out["cache_check"]["stale_ids"] == ["f"]


def test_two_consecutive_walks_are_identical():
    formulas = _corpus()
    a = json.dumps(_walk(formulas), sort_keys=True)
    b = json.dumps(_walk(formulas), sort_keys=True)
    assert a == b


def _published_artifacts():
    here = Path(__file__).resolve()
    for base in (here.parents[1] / "AutoGenerated",
                 here.parents[2] / "PrincipiaMetaphysica" / "AutoGenerated"):
        if (base / "formulas.json").is_file():
            return base
    pytest.skip("formulas.json not available; run the build first")


def test_two_consecutive_cli_walks_of_the_real_corpus_agree(tmp_path):
    """The full CLI path, twice, on the published formulas -- written to tmp."""
    src = _published_artifacts()
    outs = []
    for i in (1, 2):
        out_path = tmp_path / f"chains_{i}.json"
        assert walker.main(["--autogen", str(src), "--out", str(out_path)]) == 0
        outs.append(json.loads(out_path.read_text(encoding="utf-8")))
    keys = ("total_formulas", "b3_rooted_count", "ambiguous_count",
            "non_b3_rooted_count", "tree_source_counts")
    assert {k: outs[0][k] for k in keys} == {k: outs[1][k] for k in keys}
    assert outs[0]["chains"] == outs[1]["chains"]
    assert (outs[0]["b3_rooted_count"] + outs[0]["ambiguous_count"]
            + outs[0]["non_b3_rooted_count"]) == outs[0]["total_formulas"]


def test_interpolated_tree_sites_are_found_and_stable():
    """Tree strings built from runtime values are located in the source."""
    a = common.formula_tree_sites()
    b = common.formula_tree_sites()
    assert a == b
    computed = [s for s in a if s["field"] and s["how"]]
    assert computed, "no computed tree strings found -- the scan is blind"
    hows = {s["how"] for s in computed}
    assert hows <= {"f-string", "%-format", ".format", "computed"}
