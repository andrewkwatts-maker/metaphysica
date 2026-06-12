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


def _bucket(status: str) -> str:
    s = (status or "").upper()
    if s in LOCKED:
        return "locked"
    if s in OPEN:
        return "open"
    if s in AXIOM:
        return "axiom"
    return "other"


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

    for c in certs:
        status = c.get("verification_status") or c.get("status") or ""
        b = _bucket(status)
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
        },
        "by_phase": {k: dict(v) for k, v in sorted(by_phase.items())},
        "by_block": {k: dict(v) for k, v in sorted(by_block.items())},
        "locked_gate_ids": locked_gates,
        "open_gate_ids": open_gates,
        "status_summary": (
            f"{n_locked}/{n_testable} testable gates LOCKED "
            f"({completion_pct:.1f}% complete); {n_axiom} axiomatic."
        ),
    }

    out = ag / "improvement_scorecard.json"
    out.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
    print(f"improvement_scorecard: {n_locked}/{n_testable} locked ({completion_pct:.1f}%)")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
