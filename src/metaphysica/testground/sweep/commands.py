"""The `sweep` and `audit` commands: parsers and handlers.

Handlers raise ValueError for refusals (the CLI maps it to a refusal exit).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from metaphysica.testground.audit import to_markdown
from metaphysica.testground.runner.fingerprint import engine_fingerprint
from metaphysica.testground.sweep.auditing import build_report, has_findings
from metaphysica.testground.sweep.execute import check_jobs, run_selections
from metaphysica.testground.sweep.loading import load_runs
from metaphysica.testground.sweep.selections import (BASELINE, sweep_forks, compatible_fn, dedupe,
                                                     joint_selections, label,
                                                     parse_only, sampled_selections,
                                                     single_selections)
from metaphysica.testground.audit import footprints

__all__ = ["EXIT_FINDINGS", "add_parsers", "cmd_sweep", "cmd_audit", "plan"]

EXIT_FINDINGS = 3


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--theory", help="theory name, or module:ATTRIBUTE")
    p.add_argument("--runs-dir", required=True, help="base directory of run roots")
    p.add_argument("--fingerprint-root", action="append", default=[],
                   help="source root hashed into the engine fingerprint (repeatable)")


def add_parsers(sub: Any) -> None:
    p = sub.add_parser("sweep", help="run single deviations, joint sets or a "
                                     "seeded sample, resumably")
    _common(p)
    p.add_argument("--singles", action="store_true",
                   help="every option of every fork, one deviation from the default")
    p.add_argument("--only", nargs="+", metavar="FORK[=OPT]",
                   help="restrict --singles to these forks or options")
    p.add_argument("--joint", type=int, metavar="K",
                   help="overlapping option sets of size 2..K (K <= 3) from finished singles")
    p.add_argument("--sample", type=int, metavar="N", help="N seeded random full paths")
    p.add_argument("--seed", type=int, default=0, help="sample seed (default 0)")
    p.add_argument("--dry-run", action="store_true", help="print the ids; run nothing")
    p.add_argument("--jobs", type=int, default=1, help="parallel runs (default 1)")
    p.add_argument("--timeout", type=float, help="per-stage timeout, seconds")
    p = sub.add_parser("audit", help="classes, no-ops, interactions, reads and "
                                     "failures over a runs directory")
    _common(p)
    p.add_argument("--out", help="write the JSON report here")
    p.add_argument("--md", help="write the markdown report here")
    p.add_argument("--k", type=int, default=3, help="largest interaction set (2..3)")


def _fingerprint(args: argparse.Namespace) -> str:
    return engine_fingerprint([Path(p) for p in args.fingerprint_root])


def _joint(theory: Any, args: argparse.Namespace, fingerprint: str) -> List[Dict[str, str]]:
    forks = sweep_forks(theory)
    loaded = load_runs(Path(args.runs_dir), theory.id, fingerprint)
    usable = {r.id: r for r in loaded.runs.values() if r.rows is not None}
    if BASELINE not in usable:
        raise ValueError("--joint needs finished single runs (including the "
                         "default) in %s; run --singles first" % args.runs_dir)
    base = usable[BASELINE].rows
    singles = {}
    for sel in single_selections(forks):
        run = usable.get(label(sel))
        if run is not None:
            singles.update({next(iter(sel.items())): run.rows})
    return joint_selections(forks, footprints(base, singles), args.joint,
                            compatible_fn(theory))


def plan(theory: Any, args: argparse.Namespace, fingerprint: str) -> List[Dict[str, str]]:
    """The deviation selections requested (the default run is added by the caller)."""
    forks = sweep_forks(theory)
    if not (args.singles or args.joint or args.sample):
        raise ValueError("choose at least one of --singles, --joint K, --sample N")
    sels: List[Dict[str, str]] = []
    if args.singles:
        sels += single_selections(forks, parse_only(args.only, forks))
    if args.joint:
        sels += _joint(theory, args, fingerprint)
    if args.sample:
        sels += sampled_selections(forks, args.sample, args.seed, compatible_fn(theory))
    return dedupe(forks, sels)


def cmd_sweep(args: argparse.Namespace, theory: Any) -> int:
    check_jobs(theory, args.jobs)
    fingerprint = _fingerprint(args)
    sels = plan(theory, args, fingerprint)
    ids = [BASELINE] + [label(s) for s in sels]
    if args.dry_run:
        print("\n".join(ids))
        print("%d selections (including the default run); nothing run" % len(ids))
        return 0
    results = run_selections(theory, [{}] + sels, args.runs_dir, fingerprint,
                             jobs=args.jobs, timeout=args.timeout)
    reused = sum(1 for r in results if getattr(r.value, "cached", False))
    bad = [r for r in results if r.status != "COMPLETED"]
    print("%d selections: %d run, %d reused, %d not completed"
          % (len(results), len(results) - reused, reused, len(bad)))
    return 0


def _write(path: str, text: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text, encoding="utf-8")


def cmd_audit(args: argparse.Namespace, theory: Any) -> int:
    fingerprint = _fingerprint(args)
    loaded = load_runs(Path(args.runs_dir), theory.id, fingerprint)
    if loaded.stale:
        print("skipped stale fingerprints: %s" % ", ".join(sorted(loaded.stale)))
    report = build_report(theory, loaded, k_max=args.k)
    if args.out:
        _write(args.out, json.dumps(report, indent=2, sort_keys=True) + "\n")
    if args.md:
        _write(args.md, to_markdown(report))
    print("audit: %d runs, %d classes, %d no-op options, %d non-additive runs, "
          "%d closed-gate reads" % (report["runs"], len(report["classes"]),
                                    len(report["no_op_options"]), len(report["mismatches"]),
                                    len(report["closed_gate_reads"])))
    return EXIT_FINDINGS if has_findings(report) else 0
