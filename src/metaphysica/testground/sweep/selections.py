"""Which selections a sweep runs: singles, joint sets, seeded samples.

A selection id is the canonical sparse selection (only non-default, gate-open
entries); selections that canonicalise to one id run once.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from metaphysica.testground.audit import interaction_sets, sample_selections
from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.constraints import is_valid, violations
from metaphysica.testground.switches.gates import canonical

__all__ = ["BASELINE", "sweep_forks", "label", "defaults", "canon", "compatible_fn",
           "parse_only", "single_selections", "SinglesPlan", "constrained_singles", "joint_selections",
           "sampled_selections", "dedupe", "configuration_for"]

BASELINE = "default"
Sel = Dict[str, str]


def sweep_forks(theory: Any) -> Dict[str, Any]:
    """The theory's forks that have an adopted option (declared-only forks, with
    none, cannot be deviated from and are left out)."""
    out = {}
    for fid, fork in theory.switches.forks().items():
        if any(o.status == "active" for o in fork.options):
            out[fid] = fork
    return out


def label(sel: Mapping[str, str]) -> str:
    """Readable id: ``fork=opt,fork=opt`` sorted, or ``default`` when empty."""
    return ",".join("%s=%s" % p for p in sorted(sel.items())) or BASELINE


def defaults(forks: Mapping[str, Any]) -> Sel:
    return {fid: fork.default() for fid, fork in forks.items()}


def canon(forks: Mapping[str, Any], sel: Mapping[str, str]) -> Sel:
    return canonical(forks, sel)


def compatible_fn(theory: Any):
    """True when no constraint refuses the selection (other forks at default)."""
    forks = sweep_forks(theory)
    constraints = list(theory.switches.constraints())
    base = defaults(forks)
    return lambda sel: is_valid({**base, **dict(sel)}, constraints)


def parse_only(items: Optional[Iterable[str]],
               forks: Mapping[str, Any]) -> List[Tuple[str, Optional[str]]]:
    """``FORK`` or ``FORK=OPT`` items; unknown ids raise ValueError."""
    out: List[Tuple[str, Optional[str]]] = []
    for item in items or ():
        fork, _, opt = item.partition("=")
        if fork not in forks:
            raise ValueError("unknown fork %r; declared: %s" % (fork, sorted(forks)))
        if opt and opt not in forks[fork].option_ids():
            raise ValueError("fork %r has no option %r" % (fork, opt))
        out.append((fork, opt or None))
    return out


def dedupe(forks: Mapping[str, Any], sels: Iterable[Mapping[str, str]]) -> List[Sel]:
    """Canonical selections, first occurrence kept, the default run excluded."""
    seen, out = set(), []
    for sel in sels:
        c = canon(forks, sel)
        key = label(c)
        if c and key not in seen:
            seen.add(key)
            out.append(c)
    return out


def single_selections(forks: Mapping[str, Any],
                      only: Sequence[Tuple[str, Optional[str]]] = ()) -> List[Sel]:
    """Every option of every fork, one deviation from the default."""
    def wanted(fid: str, opt: str) -> bool:
        return not only or any(f == fid and o in (None, opt) for f, o in only)

    raw = [{fid: opt} for fid, fork in forks.items() for opt in fork.option_ids()
           if opt != fork.default() and wanted(fid, opt)]
    return dedupe(forks, raw)


@dataclass
class SinglesPlan:
    """Singles after the constraints: what runs, what was repaired, what is refused."""

    selections: List[Sel] = field(default_factory=list)
    #: run id -> why the run is not the plain single (a one-option repair).
    repaired: Dict[str, str] = field(default_factory=dict)
    #: (option label, reason) of singles no unique repair rescues.
    refused: List[Tuple[str, str]] = field(default_factory=list)


def _repairs(forks: Mapping[str, Any], sel: Mapping[str, str],
             constraints: Sequence) -> List[Sel]:
    """Selections ``sel`` plus ONE other fork's live (non-DISABLED) option that the
    constraints accept."""
    base = defaults(forks)
    out = []
    for gid, fork in forks.items():
        if gid in sel:
            continue
        for opt in fork.sweepable_ids():
            cand = {**sel, gid: opt}
            if opt != base[gid] and is_valid({**base, **cand}, constraints):
                out.append(cand)
    return out


def constrained_singles(forks: Mapping[str, Any], singles: Sequence[Mapping[str, str]],
                        constraints: Sequence) -> SinglesPlan:
    """Keep singles the constraints accept; a refused single with exactly one
    one-option repair runs as the repaired pair (labelled), otherwise it is refused
    with the reason. Nothing is dropped silently."""
    base, plan = defaults(forks), SinglesPlan()
    for sel in singles:
        why = violations({**base, **dict(sel)}, constraints)
        if not why:
            plan.selections.append(dict(sel))
            continue
        fixes = _repairs(forks, sel, constraints)
        reason = "; ".join(d for d, _ in why)
        if len(fixes) == 1:
            plan.selections.append(fixes[0])
            plan.repaired[label(canon(forks, fixes[0]))] = (
                "repair of %s (%s)" % (label(sel), reason))
        else:
            how = ("no other fork's live option repairs it" if not fixes else
                   "%d repairs, none unique: %s" % (len(fixes), "; ".join(
                       label(f) for f in fixes)))
            plan.refused.append((label(sel), "%s; %s" % (reason, how)))
    plan.selections = dedupe(forks, plan.selections)
    return plan


def joint_selections(forks: Mapping[str, Any], footprint: Mapping, k: int,
                     compatible) -> List[Sel]:
    """Interaction sets of 2..k options the constraints allow, canonicalised."""
    if not 2 <= k <= 3:
        raise ValueError("--joint K must be 2 or 3, got %d" % k)
    sets = interaction_sets(footprint, k_max=k, compatible=compatible)
    return dedupe(forks, (dict(s) for s in sets))


def sampled_selections(forks: Mapping[str, Any], n: int, seed: int,
                       compatible) -> List[Sel]:
    picks = sample_selections(list(forks.values()), n, seed=seed,
                              canonical=lambda s: canon(forks, s),
                              compatible=compatible)
    return dedupe(forks, picks)


def configuration_for(theory: Any, sel: Mapping[str, str]) -> Configuration:
    """The Configuration of a sparse canonical selection.

    Not runnable when an option is unimplemented. The Classifier is not used: it
    needs an adopted option on every fork, which declared-only forks lack.
    """
    forks = theory.switches.forks()
    missing = ["%s=%s is not implemented" % (f, o) for f, o in sorted(sel.items())
               if not forks[f].option(o).implemented]
    return Configuration.of(theory.id, dict(sel), not_runnable=bool(missing),
                            reasons=tuple(missing))
