"""Which selections a sweep runs: singles, joint sets, seeded samples.

A selection id is the canonical sparse selection (only non-default, gate-open
entries); selections that canonicalise to one id run once.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from metaphysica.testground.audit import interaction_sets, sample_selections
from metaphysica.testground.configurations.lifecycle import Classifier
from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.constraints import is_valid
from metaphysica.testground.switches.gates import canonical

__all__ = ["BASELINE", "sweep_forks", "label", "defaults", "canon", "compatible_fn",
           "parse_only", "single_selections", "joint_selections",
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


def configuration_for(theory: Any, classifier: Classifier,
                      sel: Mapping[str, str]) -> Configuration:
    """The labelled Configuration of a sparse canonical selection."""
    full = {**defaults(sweep_forks(theory)), **dict(sel)}
    standing = classifier.standing(full)
    return Configuration.of(theory.id, dict(sel), lifecycle=standing.lifecycle,
                            not_runnable=standing.not_runnable,
                            reasons=standing.reasons)
