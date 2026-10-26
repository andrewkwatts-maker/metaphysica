"""Fork gates: a fork that acts only under named options of other forks.

A closed gate makes the fork inert, not forbidden: `canonical` drops its entry
so a selection id, an enumeration and a path count see one path where the
gated-off fork's options all compute the same thing.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Set, Tuple

from .model import Fork

__all__ = ["validate_gates", "gate_open", "canonical", "gate_reads"]


def _groups(fork: Fork) -> Dict[str, List[str]]:
    """The gate as {gating fork: options, OR'd}; forks are AND'd."""
    out: Dict[str, List[str]] = {}
    for gf, go in fork.applies_when:
        out.setdefault(gf, []).append(go)
    return out


def _check_edges(forks: Mapping[str, Fork]) -> None:
    for fid, fork in forks.items():
        for gf, go in fork.applies_when:
            if gf == fid:
                raise ValueError("%s.applies_when names itself" % fid)
            if gf not in forks:
                raise ValueError("%s.applies_when names unknown fork %r"
                                 % (fid, gf))
            if go not in forks[gf].option_ids():
                raise ValueError(
                    "%s.applies_when names unknown option %r of fork %r; "
                    "available: %s" % (fid, go, gf, forks[gf].option_ids()))


def _check_acyclic(forks: Mapping[str, Fork]) -> None:
    done: Set[str] = set()

    def visit(fid: str, path: Tuple[str, ...]) -> None:
        if fid in path:
            raise ValueError("gate cycle: %s" % " -> ".join(path + (fid,)))
        if fid in done:
            return
        for gf in _groups(forks[fid]):
            visit(gf, path + (fid,))
        done.add(fid)

    for fid in forks:
        visit(fid, ())


def validate_gates(forks: Mapping[str, Fork]) -> None:
    """Refuse an unknown fork or option, a self-reference, or a cycle."""
    _check_edges(forks)
    _check_acyclic(forks)


def _effective(forks: Mapping[str, Fork], fid: str,
               selection: Mapping[str, str]) -> str:
    """The option *fid* acts as: its pick if its gate is open, else default."""
    if fid in selection and gate_open(forks, fid, selection):
        return selection[fid]
    return forks[fid].default()


def gate_open(forks: Mapping[str, Fork], fork_id: str,
              selection: Mapping[str, str]) -> bool:
    """True when *fork_id* acts under *selection*.

    A missing fork counts as its default; a gating fork whose own gate is
    closed counts as its default too.
    """
    for gf, options in _groups(forks[fork_id]).items():
        if _effective(forks, gf, selection) not in options:
            return False
    return True


def gate_reads(forks: Mapping[str, Fork], fork_id: str) -> Tuple[str, ...]:
    """Every fork whose pick decides whether *fork_id*'s gate is open."""
    seen: List[str] = []
    stack = list(_groups(forks[fork_id]))
    while stack:
        gf = stack.pop()
        if gf not in seen:
            seen.append(gf)
            stack.extend(_groups(forks[gf]))
    return tuple(seen)


def canonical(forks: Mapping[str, Fork],
              selection: Mapping[str, str]) -> Dict[str, str]:
    """*selection* without entries whose gate is closed or that equal the
    default. Iterated to a fixed point (bounded by ``len(forks)`` passes)."""
    current = dict(selection)
    for _ in range(len(forks) + 1):
        nxt = {f: o for f, o in current.items()
               if o != forks[f].default()
               and gate_open(forks, f, current)}
        if nxt == current:
            return current
        current = nxt
    raise RuntimeError("canonical did not reach a fixed point in %d passes"
                       % len(forks))
