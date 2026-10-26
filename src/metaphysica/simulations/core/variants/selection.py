"""Selection: constraints, ids, the resolve order, and the in-process override.

Mutable module state (_FORCED, _SELECTION_CACHE) lives here once.
Split out of the former single-file variants.py; text moved verbatim.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from .catalogue import FORKS
from .model import DISABLED, _ENV_PREFIX, _SELECTION_ENV, Fork

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




def violations(sel: Dict[str, str]) -> List[str]:
    """Declared constraints *sel* breaks, as readable strings.

    *sel* may be partial: a constraint is judged only when the fork it names
    is also in *sel*, so a partial selection is never refused for what it
    does not say.
    """
    out: List[str] = []
    for fid, oid in sel.items():
        opt = FORKS[fid].option(oid)
        req: Dict[str, List[str]] = {}
        for rf, ro in opt.requires:
            req.setdefault(rf, []).append(ro)
        for rf, ros in req.items():
            if rf in sel and sel[rf] not in ros:
                out.append(f"{fid}={oid} requires {rf} in {ros}, got {sel[rf]}")
        for rf, ro in opt.excludes:
            if sel.get(rf) == ro:
                out.append(f"{fid}={oid} excludes {rf}={ro}")
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


def selection_id(sel: Dict[str, str]) -> str:
    """Canonical id: 12 hex of sha256 over the sorted JSON of the departures."""
    dep = departures(sel)
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


def resolve(fork_id: str, override: Optional[str] = None) -> str:
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
    return fork.option(resolve(fork_id, override)).status


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
        chosen = resolve(fid)
        if FORKS[fid].option(chosen).status == DISABLED:
            out[fid] = chosen
    return out


def active_selection() -> Dict[str, str]:
    """Every fork's currently selected option, including env overrides."""
    return {fid: resolve(fid) for fid in FORKS}
