"""audit.sampling, audit.reads, audit.report."""
import json

import pytest

from metaphysica.testground.audit import (RunClass, audit, reconcile_reads,
                                          sample_selections, to_markdown)
from metaphysica.theories.toy.forks import fork_list


def test_sampling_toy_forks_deterministic_and_non_default():
    forks = fork_list()
    a = sample_selections(forks, 8, seed=7)
    assert a == sample_selections(forks, 8, seed=7)
    assert a != sample_selections(forks, 8, seed=8)
    default = {f.id: f.default() for f in forks}
    assert default not in a
    assert len({json.dumps(s, sort_keys=True) for s in a}) == 8
    for s in a:
        for f in forks:
            assert f.option(s[f.id]).status in ("active", "considered")


def test_sampling_canonical_dedups_and_unreachable_raises():
    forks = fork_list()
    with pytest.raises(ValueError, match=r"found \d+ of 5"):
        sample_selections(forks, 5, seed=1, canonical=lambda s: {"k": 0})
    with pytest.raises(ValueError, match="found 0 of 1"):
        sample_selections(forks, 1, seed=1, compatible=lambda s: False, max_tries=20)


class _F:
    def __init__(self, id):
        self.id = id


def test_gate_findings():
    forks = [_F("A"), _F("B"), _F("C")]
    gate = lambda f, s: not (f == "B" and s["A"] == "x")
    runs = {
        "r1": ({"A": "x"}, {"A": 1, "B": 0, "C": 2}),   # B unread, gate closed: fine
        "r2": ({"A": "y"}, {"A": 1, "B": 0, "C": 1}),   # B unread, gate open: undeclared
        "r3": ({"A": "x"}, {"A": 1, "B": 3, "C": 1}),   # B read, gate closed: violation
    }
    f = reconcile_reads(forks, runs, gate_open=gate)
    assert f.never_read == []
    assert f.undeclared_gates == [("B", "r2")]
    assert f.closed_gate_reads == [("B", "r3")]


def test_never_read():
    f = reconcile_reads([_F("A"), _F("Z")], {"r": ({}, {"A": 1})})
    assert f.never_read == ["Z"]
    assert f.undeclared_gates == [("Z", "r")]


def test_report_shape_and_markdown():
    reads = reconcile_reads([_F("A"), _F("Z")], {"r": ({}, {"A": 1})})
    rep = audit(classes=[RunClass("r1", ["r1", "r2"])], no_ops=[("f", "o")],
                interaction_sets=[(("a", "1"), ("b", "1"))], mismatches={"j": ["y", "x"], "k": []},
                reads=reads, failures={"step x: boom": ["r2", "r1"], "none": []})
    assert list(rep) == sorted(rep)
    assert rep["schema"] == "metaphysica.path_audit/2"
    assert rep["failures"] == {"step x: boom": ["r1", "r2"]}
    assert rep["mismatches"] == {"j": ["x", "y"]}
    assert rep["no_op_options"] == [{"fork": "f", "option": "o"}]
    assert json.loads(json.dumps(rep)) == rep
    md = to_markdown(rep)
    assert "## No-op options" in md and "a=1 + b=1" in md and "| Z | r |" in md
    assert "## Closed-gate reads" not in md and "## Failures" in md
    assert audit() == audit()
