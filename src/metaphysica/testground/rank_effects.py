"""What forcing each option measurably changes, read from finished runs.

Theory-agnostic. A sweep runs each option on its own (a single: a selection
naming one fork); comparing that run's reading with the adopted run's says
what the option reaches:

  scored         chi2 or dof moves: a value scored against data changed;
  unscored       chi2 and dof are equal but consistency, ladder or gates move;
  none           no tier moves (the adopted option itself is the baseline);
  not_evaluable  no finished single run measures the option (declared only,
                 or swept only jointly with another fork).

Only forks of kind ``physics`` rank. A policy or narrative fork (how a build
renders, how a validator reads uncertainties) is not a path through the
theory, so a run that departs on one is reported unranked.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

__all__ = ["EFFECTS", "PATH_KIND", "reading_effect", "option_effects",
           "off_path_reason", "validate_effects"]

EFFECTS = ("scored", "unscored", "none", "not_evaluable")
PATH_KIND = "physics"


def reading_effect(reading: Any, base: Any) -> str:
    """The effect of one run's reading against the adopted run's."""
    if (reading.chi2, reading.dof) != (base.chi2, base.dof):
        return "scored"
    unscored = ("consistent", "ladder_failed", "ladder_total", "gates_failed",
                "gates_applicable")
    if any(getattr(reading, k) != getattr(base, k) for k in unscored):
        return "unscored"
    return "none"


def _singles(entries: Sequence[Any]) -> Dict[tuple, Any]:
    out: Dict[tuple, Any] = {}
    for e in entries:
        if len(e.selection) != 1:
            continue
        key = next(iter(e.selection.items()))
        if key in out:
            raise ValueError("two finished single runs for %s=%s: %s, %s"
                             % (key[0], key[1], out[key].path_id, e.path_id))
        out[key] = e
    return out


def option_effects(entries: Sequence[Any], selected: str,
                   forks: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    """fork id -> option id -> {output_effect, path_id} for every option."""
    base = {e.path_id: e for e in entries}[selected].reading
    singles = _singles(entries)
    out: Dict[str, Dict[str, Any]] = {}
    for fid, fork in forks.items():
        adopted = fork.default()
        row: Dict[str, Any] = {}
        for oid in fork.option_ids():
            if oid == adopted:
                row[oid] = {"output_effect": "none", "path_id": selected,
                            "baseline": True}
                continue
            e = singles.get((fid, oid))
            row[oid] = ({"output_effect": "not_evaluable", "path_id": None}
                        if e is None else
                        {"output_effect": reading_effect(e.reading, base),
                         "path_id": e.path_id})
        out[fid] = row
    return out


def off_path_reason(selection: Mapping[str, str],
                    forks: Mapping[str, Any]) -> str:
    """Why a run with *selection* does not rank, or "" when it does."""
    if not forks:
        return ""
    unknown = sorted(f for f in selection if f not in forks)
    if unknown:
        raise ValueError("selection names undeclared forks %s" % unknown)
    off = sorted("%s (%s)" % (f, forks[f].kind) for f in selection
                 if forks[f].kind != PATH_KIND)
    return ("departs on a fork that is not a %s path: %s"
            % (PATH_KIND, ", ".join(off))) if off else ""


def validate_effects(effects: Any) -> List[str]:
    """Problems with an option_effects block; empty when it validates."""
    if not isinstance(effects, dict):
        return ["option_effects is not an object"]
    bad: List[str] = []
    for fid, row in effects.items():
        if not isinstance(row, dict) or not row:
            bad.append("option_effects.%s lists no options" % fid)
            continue
        bad += ["option_effects.%s.%s has no valid output_effect" % (fid, oid)
                for oid, cell in row.items()
                if not isinstance(cell, dict)
                or cell.get("output_effect") not in EFFECTS]
    return bad
