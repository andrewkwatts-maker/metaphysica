"""`testground rank`: order the finished paths, consistency first, fit last.

Owner direction (2026-10-28): the path is selected from the best output. The
order is lexicographic:

  1. internally consistent (a measurement-free verdict);
  2. fewest failing master-action ladder checks;
  3. fewest failing gates among those that apply to the path;
  4. lowest chi-squared against measured anchors (the tie-break only).

A fitted choice is disclosed as one: the file names the selected path and how
many paths were searched. The theory declares how a run is read
(`Theory.ranking`); this module is theory-agnostic. A tier a run did not publish
is None and listed under `missing`; it sorts after every known value and is
never filled in.

Output: `path_ranking.json`, schema `path_ranking/1`
(docs/plan/paths/track_s_selection.md).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from metaphysica.testground.runner.isolation import read_stamp
from metaphysica.testground.runner.worker import RUN_LOG_NAME
from metaphysica.testground.theory import RunReading, Theory

__all__ = ["SCHEMA", "RULE", "REASONABLE_RULE", "REASONABLE_DELTA_CHI2",
           "RankEntry", "rank_entries", "load_entries", "validate_ranking",
           "add_parsers", "cmd_rank"]

SCHEMA = "path_ranking/1"
RULE = "lexicographic: consistent, ladder_failed, gates_failed, chi2"
#: A path is reasonable when it is consistent, fails no more ladder checks than
#: the selected path, and its chi-squared exceeds the selected path's by no more
#: than this.
REASONABLE_DELTA_CHI2 = 4.0
REASONABLE_RULE = ("consistent, ladder_failed <= selected, delta_chi2 <= %g"
                   % REASONABLE_DELTA_CHI2)
_DONE = ("COMPLETED", "COMPLETED_WITH_FAILURES")
_ROW_KEYS = ("path_id", "selection", "rank", "consistent", "ladder_failed",
             "ladder_total", "gates_failed", "gates_applicable", "chi2", "dof",
             "delta_chi2", "reasonable", "missing")


@dataclass(frozen=True)
class RankEntry:
    path_id: str
    selection: Mapping[str, str]
    reading: RunReading


def _sort_key(r: RunReading) -> Tuple[float, float, float, float]:
    """Smaller is better; an unknown tier sorts after every known value."""
    inf = math.inf
    return (0.0 if r.consistent else (1.0 if r.consistent is False else 2.0),
            inf if r.ladder_failed is None else r.ladder_failed,
            inf if r.gates_failed is None else r.gates_failed,
            inf if r.chi2 is None else r.chi2)


def _delta(chi2: Optional[float], base: Optional[float]) -> Optional[float]:
    return None if chi2 is None or base is None else round(chi2 - base, 9)


def _reasonable(r: RunReading, delta: Optional[float],
                chosen: RunReading) -> bool:
    if r.consistent is not True:
        return False
    if r.ladder_failed is None or chosen.ladder_failed is None:
        return False
    return (r.ladder_failed <= chosen.ladder_failed and delta is not None
            and delta <= REASONABLE_DELTA_CHI2)


def _row(e: RankEntry, rank: int, chosen: RunReading) -> Dict[str, Any]:
    r = e.reading
    delta = _delta(r.chi2, chosen.chi2)
    return {"path_id": e.path_id, "selection": dict(e.selection), "rank": rank,
            "consistent": r.consistent, "ladder_failed": r.ladder_failed,
            "ladder_total": r.ladder_total, "gates_failed": r.gates_failed,
            "gates_applicable": r.gates_applicable, "chi2": r.chi2,
            "dof": r.dof, "delta_chi2": delta,
            "reasonable": _reasonable(r, delta, chosen),
            "missing": sorted(r.missing)}


def rank_entries(entries: Sequence[RankEntry], selected: str
                 ) -> Dict[str, Any]:
    """The ranking document; ``selected`` is the path id the build adopts now."""
    by_id = {e.path_id: e for e in entries}
    if len(by_id) != len(entries):
        raise ValueError("duplicate path ids in the runs to rank")
    if selected not in by_id:
        raise ValueError("the selected path %r is not among the %d finished "
                         "runs" % (selected, len(entries)))
    chosen = by_id[selected].reading
    ordered = sorted(entries, key=lambda e: (_sort_key(e.reading), e.path_id))
    rows: List[Dict[str, Any]] = []
    for i, e in enumerate(ordered):
        tied = i > 0 and _sort_key(e.reading) == _sort_key(ordered[i - 1].reading)
        rows.append(_row(e, rows[-1]["rank"] if tied else i + 1, chosen))
    return {"schema": SCHEMA, "rule": RULE, "reasonable_rule": REASONABLE_RULE,
            "searched": len(rows), "selected": selected, "rows": rows}


def validate_ranking(doc: Mapping[str, Any]) -> List[str]:
    """Problems against the contract; an empty list means it validates."""
    bad: List[str] = []
    if doc.get("schema") != SCHEMA:
        bad.append("schema is not %s" % SCHEMA)
    for key in ("rule", "reasonable_rule", "selected"):
        if not isinstance(doc.get(key), str):
            bad.append("%s is not a string" % key)
    rows = doc.get("rows")
    if not isinstance(rows, list):
        return bad + ["rows is not a list"]
    if doc.get("searched") != len(rows):
        bad.append("searched != number of rows")
    ids = [r.get("path_id") for r in rows]
    if len(set(ids)) != len(ids):
        bad.append("duplicate path_id")
    if doc.get("selected") not in ids:
        bad.append("selected is not a row")
    for r in rows:
        absent = [k for k in _ROW_KEYS if k not in r]
        if absent:
            bad.append("%s lacks %s" % (r.get("path_id"), ",".join(absent)))
    return bad


# ----------------------------------------------------------------- loading


def _finished(root: Path) -> Optional[Dict[str, Any]]:
    """The run's stamp when it finished with rows, else None."""
    stamp = read_stamp(root)
    if not stamp or not isinstance(stamp.get("selection"), dict):
        return None
    try:
        log = json.loads((root / RUN_LOG_NAME).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    ok = isinstance(log, dict) and log.get("status") in _DONE
    return stamp if ok else None


def load_entries(theory: Theory, fp_dir: Path) -> List[RankEntry]:
    """Read every finished run under ``<runs>/<theory>/<fingerprint>``."""
    if theory.ranking is None:
        raise ValueError("theory %r declares no ranking reader" % theory.id)
    out: List[RankEntry] = []
    for root in sorted(p for p in Path(fp_dir).iterdir() if p.is_dir()):
        stamp = _finished(root)
        if stamp is None:
            continue
        sel = {str(k): str(v) for k, v in stamp["selection"].items()}
        out.append(RankEntry(root.name, sel, theory.ranking.read(root, sel)))
    return out


def _fingerprint_dir(theory: Theory, runs_dir: Path,
                     fingerprint: Optional[str]) -> Path:
    base = Path(runs_dir) / theory.id
    dirs = sorted(p.name for p in base.iterdir() if p.is_dir()) \
        if base.is_dir() else []
    if fingerprint:
        if fingerprint not in dirs:
            raise ValueError("no fingerprint %s under %s (have: %s)"
                             % (fingerprint, base, ", ".join(dirs) or "none"))
        return base / fingerprint
    if len(dirs) != 1:
        raise ValueError("%s holds %d fingerprints (%s); choose one with "
                         "--fingerprint" % (base, len(dirs), ", ".join(dirs)))
    return base / dirs[0]


def _selected_id(entries: Sequence[RankEntry]) -> str:
    defaults = [e.path_id for e in entries if not e.selection]
    if len(defaults) != 1:
        raise ValueError("expected one finished default run (empty selection),"
                         " found %d" % len(defaults))
    return defaults[0]


# --------------------------------------------------------------------- CLI


def add_parsers(sub: Any) -> None:
    p = sub.add_parser("rank", help="order finished runs: consistency, "
                                    "ladder, gates, then chi-squared")
    p.add_argument("--theory", help="theory name, or module:ATTRIBUTE")
    p.add_argument("--runs-dir", required=True, help="base directory of runs")
    p.add_argument("--fingerprint", help="engine fingerprint directory to "
                                         "read (needed when there are several)")
    p.add_argument("--out", required=True, help="path_ranking.json to write")


def cmd_rank(args: Any, theory: Theory) -> int:
    fp_dir = _fingerprint_dir(theory, Path(args.runs_dir), args.fingerprint)
    entries = load_entries(theory, fp_dir)
    doc = rank_entries(entries, _selected_id(entries))
    problems = validate_ranking(doc)
    if problems:
        raise ValueError("ranking does not validate: " + "; ".join(problems))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    n_ok = sum(1 for r in doc["rows"] if r["reasonable"])
    print("rank: %d paths searched, %d reasonable, selected %s is rank %d"
          % (doc["searched"], n_ok, doc["selected"],
             next(r["rank"] for r in doc["rows"]
                  if r["path_id"] == doc["selected"])))
    return 0
