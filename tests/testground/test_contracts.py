"""Contract tests for the test-ground models (Phase 2.0).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from metaphysica.testground.assessment.score import (
    CRITERIA,
    CriterionScore,
    ScoreVector,
)
from metaphysica.testground.configurations.model import (
    Configuration,
    digest_of,
)
from metaphysica.testground.constraints import Excludes, Requires, violations
from metaphysica.testground.signals.model import (
    ARTIFACT,
    FULL,
    Measurement,
    Signal,
    SignalContext,
)
from metaphysica.testground.switches.model import (
    DISABLED,
    Fork,
    VariantOption,
)

_PKG = Path(__file__).resolve().parents[2] / "src" / "metaphysica" / "testground"
_FORBIDDEN = ("metaphysica.simulations", "metaphysica.generators",
              "metaphysica.website", "metaphysica.theories")


def test_the_test_ground_imports_no_theory_code():
    """Dependency rule: theories depend on the test ground, never the reverse."""
    offenders = []
    for path in _PKG.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                if name.startswith(_FORBIDDEN):
                    offenders.append("%s: %s" % (path.name, name))
    assert not offenders, offenders


def test_the_digest_matches_the_preferred_path_digest():
    sel = {"b": "x", "a": "y"}
    from metaphysica.simulations.core.preferred_path import digest_of as legacy

    assert digest_of(sel) == legacy(sel)
    assert Configuration.of("t", sel).digest == digest_of(sel)


def test_a_configuration_is_order_independent():
    a = Configuration.of("t", {"a": "1", "b": "2"})
    b = Configuration.of("t", {"b": "2", "a": "1"})
    assert a == b and a.digest == b.digest
    assert a.differs_from(a.with_overrides({"a": "3"})) == {"a": ("1", "3")}


def test_option_reconciliation_still_refuses_contradictions():
    with pytest.raises(ValueError):
        VariantOption("x", "s", "c", adopted=True, status=DISABLED)
    with pytest.raises(ValueError):
        VariantOption("x", "s", "c", status="considered", certainty="certain")
    o = VariantOption("x", "s", "c", status=DISABLED, certainty="certain")
    assert o.priority == 2 and o.retired_certain


def test_fork_validates_its_new_fields():
    opts = [VariantOption("a", "s", "c", adopted=True),
            VariantOption("b", "s", "c")]
    assert Fork("f", "q", "src", opts, "OPEN").default() == "a"
    with pytest.raises(ValueError):
        Fork("f", "q", "src", opts, "OPEN", kind="magic")
    with pytest.raises(ValueError):
        Fork("f", "q", "src", opts, "OPEN", legacy_option="zzz")


def test_constraints_report_violations_with_their_rationale():
    req = Requires("origin", "input_24", "seed", frozenset({"seed_24"}),
                   "an origin for 24", "test")
    exc = Excludes("a", "1", "b", "2", "cannot co-occur", "test")
    assert violations({"origin": "input_24", "seed": "seed_43"}, [req]) == [
        (req.describe(), "an origin for 24")]
    assert not violations({"origin": "input_24", "seed": "seed_24"}, [req])
    assert len(violations({"a": "1", "b": "2"}, [exc])) == 1


def test_an_artifact_signal_without_a_stamp_is_unmeasured():
    sig = Signal("s", "consistency", ARTIFACT, FULL,
                 lambda ctx: Measurement("s", count=0))
    ctx = SignalContext("t", "d" * 16, (("a", "1"),))
    assert sig(ctx).status == "UNMEASURED"


def test_a_crashing_signal_is_unmeasured_not_raised():
    def boom(ctx):
        raise RuntimeError("no")
    sig = Signal("s", "validity", "live", "screen", boom)
    m = sig(SignalContext("t", "d" * 16, ()))
    assert m.status == "UNMEASURED" and "RuntimeError" in m.reasons[0]


def test_the_criteria_order_is_the_decision_rule():
    """D-019: validity > closure > consistency > elegance > data (tie-break)."""
    assert CRITERIA == ("validity", "closure", "consistency", "elegance",
                        "data")


def test_score_vectors_cover_every_criterion_in_order():
    scores = tuple(CriterionScore(c, (0,)) for c in CRITERIA)
    ScoreVector("d" * 16, scores, "ADOPTABLE")
    with pytest.raises(ValueError):
        ScoreVector("d" * 16, scores[::-1], "ADOPTABLE")
    with pytest.raises(ValueError):
        CriterionScore("closure", (1.5,))


def test_the_schemas_are_valid_json():
    for path in (_PKG / "schemas").glob("*.json"):
        assert json.loads(path.read_text(encoding="utf-8"))["$id"]
