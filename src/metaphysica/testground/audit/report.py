"""Assemble the audit findings into one JSON-ready dict and a markdown view.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional

from metaphysica.testground.audit.classes import RunClass
from metaphysica.testground.audit.reads import ReadFindings
from metaphysica.testground.audit.rows import Option

__all__ = ["SCHEMA", "audit", "to_markdown"]

SCHEMA = "metaphysica.path_audit/2"


def _opt(o: Option) -> Dict[str, str]:
    return {"fork": o[0], "option": o[1]}


def _pair(p) -> Dict[str, str]:
    return {"fork": p[0], "run": p[1]}


def audit(*, classes: Iterable[RunClass] = (), no_ops: Iterable[Option] = (),
          interaction_sets: Iterable[Iterable[Option]] = (),
          mismatches: Optional[Mapping[str, List[str]]] = None,
          reads: Optional[ReadFindings] = None,
          failures: Optional[Mapping[str, List[str]]] = None) -> Dict[str, Any]:
    """One dict with sorted keys. *mismatches* maps run id to its non-additive rows;
    *failures* maps a failure description (failed build step and reason) to run ids."""
    reads = reads or ReadFindings()
    report = {
        "schema": SCHEMA,
        "classes": [{"representative": c.representative, "members": list(c.members)}
                    for c in classes],
        "no_op_options": [_opt(o) for o in sorted(no_ops)],
        "interaction_sets": [[_opt(o) for o in s]
                             for s in sorted(tuple(x) for x in interaction_sets)],
        "failures": {k: sorted(v) for k, v in sorted((failures or {}).items()) if v},
        "mismatches": {k: sorted(v) for k, v in sorted((mismatches or {}).items()) if v},
        "never_read": sorted(reads.never_read),
        "undeclared_gates": [_pair(p) for p in sorted(reads.undeclared_gates)],
        "closed_gate_reads": [_pair(p) for p in sorted(reads.closed_gate_reads)],
    }
    return dict(sorted(report.items()))


def _table(title: str, head: List[str], rows: List[List[str]]) -> List[str]:
    if not rows:
        return []
    lines = [f"## {title}", "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return lines + [""]


def _name(d: Mapping[str, str]) -> str:
    return f"{d['fork']}={d['option']}"


def to_markdown(report: Mapping[str, Any]) -> str:
    """One short table per finding kind; empty kinds are omitted."""
    lines = ["# Path audit", ""]
    lines += _table("Output classes", ["representative", "members"],
                    [[c["representative"], ", ".join(c["members"])]
                     for c in report["classes"] if len(c["members"]) > 1])
    lines += _table("No-op options", ["option"], [[_name(x)] for x in report["no_op_options"]])
    lines += _table("Interaction sets", ["options"],
                    [[" + ".join(_name(x) for x in s)] for s in report["interaction_sets"]])
    lines += _table("Non-additive rows", ["run", "rows"],
                    [[k, ", ".join(v)] for k, v in report["mismatches"].items()])
    lines += _table("Failures", ["failure", "runs"],
                    [[k, ", ".join(v)] for k, v in report["failures"].items()])
    lines += _table("Never read", ["fork"], [[f] for f in report["never_read"]])
    lines += _table("Undeclared gates", ["fork", "run"],
                    [[p["fork"], p["run"]] for p in report["undeclared_gates"]])
    lines += _table("Closed-gate reads", ["fork", "run"],
                    [[p["fork"], p["run"]] for p in report["closed_gate_reads"]])
    return "\n".join(lines) + "\n"
