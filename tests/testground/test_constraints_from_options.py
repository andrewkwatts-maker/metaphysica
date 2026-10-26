"""Option requires/excludes become testground Constraints, partial-safe."""
from __future__ import annotations

from metaphysica.testground.constraints import (
    Excludes, Requires, constraints_from_options, is_valid)
from metaphysica.testground.switches.model import Fork, VariantOption


def _forks():
    a = Fork("a", "q", "src.a", [
        VariantOption("a0", "s", "c", adopted=True),
        VariantOption("a1", "s", "c", requires=(("b", "b0"), ("b", "b1"),
                                                ("c", "c1")),
                      excludes=(("c", "c0"),)),
    ], "OPEN")
    b = Fork("b", "q", "src.b", [
        VariantOption("b0", "s", "c", adopted=True),
        VariantOption("b1", "s", "c"), VariantOption("b2", "s", "c")], "OPEN")
    c = Fork("c", "q", "src.c", [
        VariantOption("c0", "s", "c", adopted=True),
        VariantOption("c1", "s", "c")], "OPEN")
    return {"a": a, "b": b, "c": c}


def test_requires_group_per_fork_and_excludes_are_derived():
    cons = constraints_from_options(_forks())
    reqs = [c for c in cons if isinstance(c, Requires)]
    exs = [c for c in cons if isinstance(c, Excludes)]
    assert {(r.needs_fork, r.needs_options) for r in reqs} == {
        ("b", frozenset({"b0", "b1"})), ("c", frozenset({"c1"}))}
    assert len(exs) == 1 and (exs[0].fork_b, exs[0].option_b) == ("c", "c0")
    assert all(c.rationale == "declared on a.a1" and c.source == "src.a"
               for c in cons)


def test_requires_is_partial_safe():
    cons = constraints_from_options(_forks())
    assert is_valid({"a": "a1"}, cons[:0]) is True
    assert is_valid({"a": "a1"}, [c for c in cons if isinstance(c, Requires)])
    assert not is_valid({"a": "a1", "b": "b2"}, cons)
    assert not is_valid({"a": "a1", "b": "b0", "c": "c0"}, cons)
    assert is_valid({"a": "a1", "b": "b1", "c": "c1"}, cons)
