"""Assemble the path audit from loaded runs (singles, joint and sampled runs).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Tuple

from metaphysica.testground.audit import (audit, equivalence_classes, footprints,
                                          interaction_sets, no_op_options,
                                          non_additive, reconcile_reads)
from metaphysica.testground.audit.rows import Option
from metaphysica.testground.sweep.loading import Loaded, LoadedRun
from metaphysica.testground.sweep.selections import (BASELINE, sweep_forks, canon,
                                                     compatible_fn, defaults,
                                                     label)
from metaphysica.testground.switches.gates import gate_open

__all__ = ["build_report", "has_findings", "group_failures"]


def _singles(forks: Mapping[str, Any],
             usable: Mapping[str, LoadedRun]) -> Dict[Option, Mapping[str, Any]]:
    out: Dict[Option, Mapping[str, Any]] = {}
    for fid, fork in forks.items():
        for opt in fork.option_ids():
            run = usable.get(label(canon(forks, {fid: opt})))
            if opt != fork.default() and run is not None:
                out[(fid, opt)] = run.rows
    return out


def _mismatches(base: Mapping[str, Any], singles: Mapping, usable: Mapping[str, LoadedRun]
                ) -> Dict[str, List[str]]:
    out = {}
    for rid, run in usable.items():
        if len(run.selection) >= 2:
            out[rid] = non_additive(base, singles, run.selection, run.rows)
    return {k: v for k, v in out.items() if v}


def _reads(forks: Mapping[str, Any], runs: Mapping[str, LoadedRun]):
    with_reads = {rid: (r.selection, r.reads) for rid, r in runs.items()
                  if r.reads is not None}
    if not with_reads:
        return None
    base = defaults(forks)
    return reconcile_reads(list(forks.values()), with_reads,
                           gate_open=lambda f, s: gate_open(forks, f, {**base, **dict(s)}))


def group_failures(runs: Mapping[str, LoadedRun], width: int = 110) -> Dict[str, List[str]]:
    """Group unclean runs by failed build step and reason (as triage.py did)."""
    groups: Dict[str, List[str]] = {}
    for rid, run in runs.items():
        if run.failed_steps:
            ids = ",".join(sorted(str(s.get("id")) for s in run.failed_steps))
            reason = str(run.failed_steps[0].get("reason") or "null")[:width]
            key = "failed: %s: %s" % (ids, reason)
        elif run.status != "COMPLETED":
            key = "%s: %s" % (run.status or "no status", run.reason[:width])
        else:
            continue
        groups.setdefault(key, []).append(rid)
    return groups


def build_report(theory: Any, loaded: Loaded, *, k_max: int = 3) -> Dict[str, Any]:
    """The audit dict; raises ValueError when there is no usable default run."""
    forks = sweep_forks(theory)
    usable = {rid: r for rid, r in loaded.runs.items() if r.rows is not None}
    if BASELINE not in usable:
        raise ValueError("no finished default run with parameters in the runs "
                         "directory; run `sweep --singles` first")
    base = usable[BASELINE].rows
    singles = _singles(forks, usable)
    fp = footprints(base, singles)
    sets = interaction_sets(fp, k_max=k_max, compatible=compatible_fn(theory))
    report = audit(
        classes=equivalence_classes({rid: r.rows for rid, r in usable.items()}),
        no_ops=no_op_options(base, singles), interaction_sets=sets,
        mismatches=_mismatches(base, singles, usable),
        reads=_reads(forks, loaded.runs), failures=group_failures(loaded.runs))
    report["stale_fingerprints"] = sorted(loaded.stale)
    report["runs"] = len(loaded.runs)
    return dict(sorted(report.items()))


def has_findings(report: Mapping[str, Any]) -> bool:
    """True for a closed-gate read or a non-additive row (the CI gate)."""
    return bool(report["closed_gate_reads"] or report["mismatches"])
