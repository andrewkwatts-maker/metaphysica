"""Every 72-gate formula is numeric (triple-checked) or a named predicate.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.paper.appendices.appendix_f_72gates import (
    Appendix72Gates, GateRegistry,
)


def _formulas():
    return Appendix72Gates().get_formulas()


def test_every_gate_formula_is_numeric_or_predicate():
    bad = []
    for f in _formulas():
        numeric = f.value is not None and f.arithma is not None and f.eml is not None
        predicate = bool(f.non_numeric) and f.value is None
        if numeric == predicate:
            bad.append(f.id)
    assert not bad, "neither numeric nor predicate (or both): %s" % bad


def test_predicate_reason_names_the_gate():
    for f in _formulas():
        if f.non_numeric:
            assert f.non_numeric.startswith("pass/fail gate "), f.id
            assert f.non_numeric.endswith(", evaluated by validate_gate"), f.id


def test_numeric_gates_agree_across_legs():
    from metaphysica.simulations.core.triple_helpers import _to_float
    n = 0
    for f in _formulas():
        if f.value is None:
            continue
        n += 1
        a = _to_float(f.arithma.evaluate({"pi": 3.141592653589793, **f.triple_env}))
        assert a == pytest.approx(f.value, rel=1e-9), f.id
    assert n >= 10


def test_validate_gate_runs_for_all_72_on_model_data():
    results = {}
    for gid in range(1, 73):
        passed, msg = GateRegistry.validate_gate(gid, {})
        assert isinstance(msg, str) and msg
        results[gid] = bool(passed)
    print("gates pass %d fail %d failing %s" % (
        sum(results.values()), sum(not v for v in results.values()),
        [g for g, v in results.items() if not v]))
    assert len(results) == 72
