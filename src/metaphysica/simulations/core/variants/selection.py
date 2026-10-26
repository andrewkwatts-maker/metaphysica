"""Selection: constraints, ids, the resolve order, and the in-process override.

Mutable module state (_FORCED, _SELECTION_CACHE) lives here once.
Split out of the former single-file variants.py; text moved verbatim.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import atexit
import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from metaphysica.testground.constraints import (
    Constraint,
    Excludes,
    Requires,
    constraints_from_options,
)

from metaphysica.testground.switches.gates import (
    canonical,
    gate_open,
    gate_reads,
    validate_gates,
)

from .catalogue import FORKS
from .model import DISABLED, _ENV_PREFIX, _SELECTION_ENV, Fork

#: Env var naming the directory each process writes its fork reads to.
READS_DIR_ENV = "METAPHYSICA_FORK_READS_DIR"

def validate_constraints(forks: Dict[str, Fork]) -> None:
    """Refuse a requires/excludes naming a fork or option that is not declared."""
    for fid, fork in forks.items():
        for opt in fork.options:
            for kind in ("requires", "excludes"):
                for ref in getattr(opt, kind):
                    rf, ro = ref
                    if rf == fid:
                        raise ValueError(
                            f"{fid}.{opt.id} {kind} {ref}: a fork cannot "
                            f"constrain itself")
                    if rf not in forks:
                        raise ValueError(
                            f"{fid}.{opt.id} {kind} unknown fork {rf!r}")
                    if ro not in forks[rf].option_ids():
                        raise ValueError(
                            f"{fid}.{opt.id} {kind} unknown option {ro!r} of "
                            f"fork {rf!r}; available: {forks[rf].option_ids()}")




validate_gates(FORKS)


def _declared_constraints(forks: Dict[str, Fork]) -> Dict[Any, List[Constraint]]:
    """The options' own requires/excludes as testground Constraints, keyed by
    the (fork, option) that declares them, in declaration order."""
    by_option: Dict[Any, List[Constraint]] = {}
    for c in constraints_from_options(forks):
        by_option.setdefault((c.fork, c.option) if isinstance(c, Requires)
                             else (c.fork_a, c.option_a), []).append(c)
    return by_option


_CONSTRAINTS = _declared_constraints(FORKS)


def _describe_violation(c: Constraint, sel: Dict[str, str]) -> str:
    """The long-standing wording: declaration order of the listed options."""
    if isinstance(c, Excludes):
        return f"{c.fork_a}={c.option_a} excludes {c.fork_b}={c.option_b}"
    opt = FORKS[c.fork].option(c.option)
    ros = [ro for rf, ro in opt.requires if rf == c.needs_fork]
    return (f"{c.fork}={c.option} requires {c.needs_fork} in {ros}, "
            f"got {sel[c.needs_fork]}")


def violations(sel: Dict[str, str]) -> List[str]:
    """Declared constraints *sel* breaks, as readable strings.

    *sel* may be partial: a constraint is judged only when the fork it names
    is also in *sel*, so a partial selection is never refused for what it
    does not say. The judging is `testground.constraints`'.
    """
    out: List[str] = []
    for fid, oid in sel.items():
        FORKS[fid].option(oid)
        out += [_describe_violation(c, sel)
                for c in _CONSTRAINTS.get((fid, oid), ())
                if c.violated_by(sel)]
    return out


def compatible(sel: Dict[str, str]) -> bool:
    """True when *sel* breaks no declared requires/excludes."""
    return not violations(sel)


def departures(sel: Dict[str, str]) -> Dict[str, str]:
    """Entries of *sel* that differ from the adopted default (missing = default)."""
    out: Dict[str, str] = {}
    for fid, oid in sel.items():
        if fid not in FORKS:
            raise ValueError(f"unknown fork {fid!r}; declared: {sorted(FORKS)}")
        FORKS[fid].option(oid)
        if oid != FORKS[fid].default():
            out[fid] = oid
    return out


def canonical_departures(sel: Dict[str, str]) -> Dict[str, str]:
    """`departures` without the forks whose gate is closed under *sel*."""
    return canonical(FORKS, departures(sel))


def selection_id(sel: Dict[str, str]) -> str:
    """Canonical id: 12 hex of sha256 over the sorted JSON of the departures."""
    dep = canonical_departures(sel)
    if not dep:
        return "active"
    blob = json.dumps(dep, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def load_selection(path: Any) -> Dict[str, str]:
    """Read and validate a JSON {fork: option} file; unknown names fail early."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"selection {path}: expected a JSON object")
    for fid, oid in data.items():
        if fid not in FORKS:
            raise ValueError(
                f"selection {path}: unknown fork {fid!r}; declared: {sorted(FORKS)}")
        if oid not in FORKS[fid].option_ids():
            raise ValueError(
                f"selection {path}: fork {fid!r} has no option {oid!r}; "
                f"available: {FORKS[fid].option_ids()}")
    return data


_SELECTION_CACHE: Dict[Any, Dict[str, str]] = {}


def _env_selection() -> Dict[str, str]:
    """The METAPHYSICA_SELECTION map, cached per (path, mtime)."""
    path = os.environ.get(_SELECTION_ENV)
    if not path:
        return {}
    key = (path, os.stat(path).st_mtime_ns)
    if key not in _SELECTION_CACHE:
        _SELECTION_CACHE[key] = load_selection(path)
    return _SELECTION_CACHE[key]


#: In-process forced choices (see ``forced``); outranks the selection file.
_FORCED: Dict[str, str] = {}


@contextmanager
def forced(selection: Dict[str, str]):
    """Resolve *selection* in this process for the duration of the block.

    Ranks above the selection file and the per-fork env vars, which is what a
    comparison of two switch states needs. The env vars are set as well so a
    subprocess started inside the block sees the same choice (unless a
    selection file is also set, which outranks them there).
    """
    saved_forced = dict(_FORCED)
    saved_env = {k: os.environ.get(k)
                 for k in (_ENV_PREFIX + f.upper() for f in selection)}
    _FORCED.update(selection)
    for fid, oid in selection.items():
        os.environ[_ENV_PREFIX + fid.upper()] = oid
    try:
        yield
    finally:
        _FORCED.clear()
        _FORCED.update(saved_forced)
        for key, old in saved_env.items():
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old


def is_explicit(fork_id: str) -> bool:
    """True when something other than the default chose *fork_id*'s option."""
    return bool(fork_id in _FORCED or fork_id in _env_selection()
                or os.environ.get(_ENV_PREFIX + fork_id.upper()))


#: Reads per fork since the last `reset_reads`; kept apart from _FORCED.
_READS: Dict[str, int] = {}
#: Reads of a fork whose gate was closed under the current resolution.
_CLOSED_GATE_READS: Dict[str, int] = {}


def reads() -> Dict[str, int]:
    """Fork id -> reads by `resolve` while its gate was open."""
    return dict(_READS)


def closed_gate_reads() -> Dict[str, int]:
    """Fork id -> reads by `resolve` while its gate was closed."""
    return dict(_CLOSED_GATE_READS)


def reset_reads() -> None:
    _READS.clear()
    _CLOSED_GATE_READS.clear()


def _count_read(fork_id: str) -> None:
    """Record one consumer read of *fork_id*, in the open or closed counter."""
    fork = FORKS[fork_id]
    closed = bool(fork.applies_when) and not gate_open(
        FORKS, fork_id,
        {g: _resolve(g) for g in gate_reads(FORKS, fork_id)})
    counter = _CLOSED_GATE_READS if closed else _READS
    counter[fork_id] = counter.get(fork_id, 0) + 1


@contextmanager
def untracked():
    """Resolve inside the block without counting reads (diagnostics only)."""
    saved = (dict(_READS), dict(_CLOSED_GATE_READS))
    try:
        yield
    finally:
        _READS.clear()
        _READS.update(saved[0])
        _CLOSED_GATE_READS.clear()
        _CLOSED_GATE_READS.update(saved[1])


def write_reads(directory: Any) -> Path:
    """Write this process's counters to <directory>/<pid>.json."""
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("%d.json" % os.getpid())
    path.write_text(json.dumps({"reads": reads(),
                                "closed_gate_reads": closed_gate_reads()},
                               sort_keys=True), encoding="utf-8")
    return path


def _register_reads_hook() -> None:
    """With METAPHYSICA_FORK_READS_DIR set, write the counters at exit."""
    directory = os.environ.get(READS_DIR_ENV)
    if directory:
        atexit.register(write_reads, directory)


def resolve(fork_id: str, override: Optional[str] = None) -> str:
    """Selected option for *fork_id*, counted as a read (see `reads`).

    Internal callers that only inspect the selection use `_resolve`.
    """
    chosen = _resolve(fork_id, override)
    _count_read(fork_id)
    return chosen


def _resolve(fork_id: str, override: Optional[str] = None) -> str:
    """Selected option for *fork_id*.

    Precedence: explicit *override*, then ``forced`` (in-process), then the
    ``METAPHYSICA_SELECTION`` file,
    then ``METAPHYSICA_VARIANT_<ID>``, then
    the adopted default -- the same order build() uses for its output root,
    so callers do not have to remember a second convention.
    """
    fork = FORKS.get(fork_id)
    if fork is None:
        raise KeyError(
            f"unknown fork {fork_id!r}; declared: {sorted(FORKS)}"
        )
    chosen = (override or _FORCED.get(fork_id) or _env_selection().get(fork_id)
              or os.environ.get(_ENV_PREFIX + fork_id.upper()))
    if chosen is None:
        return fork.default()
    if chosen not in fork.option_ids():
        raise ValueError(
            f"fork {fork_id!r} has no option {chosen!r}; "
            f"available: {fork.option_ids()}"
        )
    # A DISABLED option resolves exactly like any other. It is refuted, not
    # broken, and a refutation nobody can re-run is folklore -- so the
    # override is honoured and the choice is merely recorded as off-table
    # rather than refused.
    return chosen


def selected_status(fork_id: str, override: Optional[str] = None) -> str:
    """Status of whatever ``resolve`` would select for *fork_id*.

    Lets a caller say "this run is off the table" without re-deriving the
    resolution order, and lets an artifact record that it was produced under
    a refuted option instead of publishing the numbers unlabelled.
    """
    fork = FORKS[fork_id]
    return fork.option(_resolve(fork_id, override)).status


def off_table_selections() -> Dict[str, str]:
    """Forks currently resolving to a DISABLED option, fork id -> option id.

    Empty on a default run. Non-empty means the process is executing a
    candidate the framework has already refuted, which is a legitimate thing
    to do deliberately and a serious thing to do by accident -- so the
    publishing path can check it rather than trusting that nobody set an
    environment variable.
    """
    out: Dict[str, str] = {}
    for fid in FORKS:
        chosen = _resolve(fid)
        if FORKS[fid].option(chosen).status == DISABLED:
            out[fid] = chosen
    return out


def active_selection() -> Dict[str, str]:
    """Every fork's currently selected option, including env overrides."""
    return {fid: _resolve(fid) for fid in FORKS}


_register_reads_hook()
