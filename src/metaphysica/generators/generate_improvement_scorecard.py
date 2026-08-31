#!/usr/bin/env python3
"""Generate improvement_scorecard.json.

Computes gate LOCKED vs OPEN tally and completion percentage from the
canonical GATES_CERTIFICATES.json (and GATES_72_v16_2.json as fallback).
Provides a per-block / per-phase breakdown so the website can render a
progress dashboard. All counts trace back to the 72-gate certification
scheme anchored on the single seed b3 = 24.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from metaphysica.generators._common import autogen_dir


def _load(p: Path) -> Dict[str, Any]:
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


# Status strings considered "locked" (fully passed) vs "open" (still pending).
LOCKED = {"VERIFIED", "LOCKED", "MATHEMATICAL", "PASS"}
OPEN = {"PENDING_LOCK", "OPEN", "FAIL", "NOT_VERIFIED"}
AXIOM = {"NOT_TESTABLE", "AXIOM"}


#: The executed evaluation layer's verdicts, which OUTRANK the declarative
#: verification_status when present.
EVALUATION_BUCKET = {
    "COMPUTED_PASS": "locked",
    "COMPUTED_FAIL": "open",
    "COMPUTED_INFO": "other",
}


def _bucket(status: str) -> str:
    s = (status or "").upper()
    if s in LOCKED:
        return "locked"
    if s in OPEN:
        return "open"
    if s in AXIOM:
        return "axiom"
    return "other"


def _bucket_certificate(cert: Dict[str, Any]) -> str:
    """Bucket one gate, letting the executed result win.

    This read only ``verification_status`` -- the DECLARATIVE field, which
    says VERIFIED for a gate whose executable form has never been run. The
    evaluation layer added in 2026-08 records what actually happened in
    ``evaluation_status``, and it was ignored here. The visible consequence
    was a scorecard reading "42/42 testable gates LOCKED (100.0% complete),
    open_gate_ids: []" while listing G12 as locked, at the same time as the
    evaluation layer reported G12 COMPUTED_FAIL at 17.1 sigma and the G72
    seal FAILING on it. Two artifacts in the same build directory, flatly
    contradicting each other.

    A gate with no executable form keeps its declarative status, which is
    the honest reading: nothing has been run, so nothing has failed. Those
    are counted separately as ``declarative`` so the completion figure is
    not mistaken for an execution result.
    """
    evaluated = EVALUATION_BUCKET.get(
        str(cert.get("evaluation_status") or "").upper())
    if evaluated is not None:
        return evaluated
    return _bucket(cert.get("verification_status") or cert.get("status") or "")


def main() -> int:
    ag = autogen_dir()
    gates_cert = _load(ag / "GATES_CERTIFICATES.json")
    gates_72 = _load(ag / "GATES_72_v16_2.json")

    # Primary source: GATES_CERTIFICATES has per-gate verification_status.
    certs: List[Dict[str, Any]] = gates_cert.get("certificates") or []
    if not certs:
        # Fallback: GATES_72 has gates list w/ optional status.
        certs = gates_72.get("gates") or []

    bucket_counts: Counter = Counter()
    by_phase: Dict[str, Counter] = {}
    by_block: Dict[str, Counter] = {}
    locked_gates: List[str] = []
    open_gates: List[str] = []

    n_declarative = 0
    for c in certs:
        if not (c.get("evaluation_status") or "").upper().startswith("COMPUTED"):
            n_declarative += 1
        b = _bucket_certificate(c)
        bucket_counts[b] += 1
        gate_id = c.get("gate_id") or c.get("id") or c.get("name") or "?"
        phase = str(c.get("phase", "?"))
        block = str(c.get("block", "?"))
        by_phase.setdefault(phase, Counter())[b] += 1
        by_block.setdefault(block, Counter())[b] += 1
        if b == "locked":
            locked_gates.append(str(gate_id))
        elif b == "open":
            open_gates.append(str(gate_id))

    total = sum(bucket_counts.values())
    n_locked = bucket_counts["locked"]
    n_open = bucket_counts["open"]
    n_axiom = bucket_counts["axiom"]
    n_testable = total - n_axiom
    completion_pct = (n_locked / n_testable * 100.0) if n_testable else 0.0

    scorecard = {
        "framework": "Principia Metaphysica",
        "scorecard_type": "Gate LOCKED vs OPEN tally + completion percentage",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "seed_provenance": "All 72 gates trace back to seed b3 = 24 (G2 manifold).",
        "totals": {
            "total_gates": total,
            "locked": n_locked,
            "open": n_open,
            "axiom_not_testable": n_axiom,
            "other": bucket_counts["other"],
            "testable_total": n_testable,
            "completion_percent": round(completion_pct, 2),
            # Gates with no executable form. They keep their declarative
            # status because nothing has been run on them -- which is also
            # why the completion figure above must not be read as an
            # execution result.
            "declarative_no_executable_form": n_declarative,
        },
        "by_phase": {k: dict(v) for k, v in sorted(by_phase.items())},
        "by_block": {k: dict(v) for k, v in sorted(by_block.items())},
        "locked_gate_ids": locked_gates,
        "open_gate_ids": open_gates,
        "counts_source": (
            "evaluation_status where the gate has an executable form, "
            "verification_status otherwise. This previously read "
            "verification_status alone, so gates the evaluation layer had "
            "already failed were still counted LOCKED."
        ),
        "status_summary": (
            f"{n_locked}/{n_testable} testable gates LOCKED "
            f"({completion_pct:.1f}% complete); {n_axiom} axiomatic; "
            f"{n_declarative} declarative (no executable form, never run)."
        ),
    }

    out = ag / "improvement_scorecard.json"
    out.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
    print(f"improvement_scorecard: {n_locked}/{n_testable} locked ({completion_pct:.1f}%)")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
