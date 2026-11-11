"""XV-15: every PM STOCHASTIC pointer resolves in the report its file names.

The pointers are checked against a report that StatisticalRigorValidator
generates, not against fixed wording, so a pointer to a removed subtree fails
however the comment beside it is phrased.
"""
from __future__ import annotations

import json

from metaphysica.simulations.PM.validation import statistical_rigor_validator as srv
from metaphysica.theories.pm import results

RIGOR = "statistical_rigor_report.json"


def _rigor_report(tmp_path):
    rows = [
        {"path": "gauge.a", "value": 1.2, "experimental_value": 1.0,
         "experimental_uncertainty": 0.1, "verdict": "FAIL",
         "registry_status": "DERIVED", "bound_type": "measured", "sigma": 2.0},
        {"path": "geometry.alpha_inverse", "value": 2.0,
         "experimental_value": 1.0, "experimental_uncertainty": 0.5,
         "verdict": "PASS", "registry_status": "GEOMETRIC",
         "bound_type": "measured", "sigma": 2.0},
    ]
    f = tmp_path / "validation_report.json"
    f.write_text(json.dumps({"validations": rows}), encoding="utf-8")
    report = srv.StatisticalRigorValidator(str(f)).generate_report()
    return json.loads(json.dumps(report, default=str))


def _resolves(doc, pointer):
    """True when the JSON pointer (``*`` matches any key) hits a value."""
    nodes = [doc]
    for raw in pointer.lstrip("/").split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        nxt = []
        for node in nodes:
            if isinstance(node, dict):
                nxt += list(node.values()) if key == "*" else (
                    [node[key]] if key in node else [])
            elif isinstance(node, list) and key.isdigit() and int(key) < len(node):
                nxt.append(node[int(key)])
        nodes = nxt
    return bool(nodes)


def test_every_stochastic_pointer_resolves_in_a_generated_report(tmp_path):
    # Only the rigor report has a generator checked here; a pointer into any
    # other file needs its own resolution check before it is declared.
    assert set(results.STOCHASTIC) <= {RIGOR}, sorted(results.STOCHASTIC)
    report = _rigor_report(tmp_path)
    for pointer in results.STOCHASTIC.get(RIGOR, ()):
        assert _resolves(report, pointer), pointer


def test_removed_jacobian_subtree_no_longer_resolves(tmp_path):
    # Guards the check above against passing vacuously: the resolver finds
    # live subtrees and rejects the one XV-15 removed from STOCHASTIC.
    report = _rigor_report(tmp_path)
    assert _resolves(report, "/summary/status")
    assert _resolves(report, "/edof_analysis/*")
    assert not _resolves(report, "/jacobian_analysis")
    assert not hasattr(srv.StatisticalRigorValidator, "generate_jacobian_matrix")
