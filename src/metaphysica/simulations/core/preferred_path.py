"""The preferred path: one declared switch state, all others kept runnable.

WHY
===
There are now twelve executable forks. Without a single declared state, three
things go wrong: the documentation and theory output silently depend on
whichever environment variables happened to be set; "what does the theory
actually say" has no answer; and comparing two configurations means
remembering what you changed.

This module is that single place. It declares ONE state -- the preferred path
-- which documentation and theory output are generated from, while every other
combination stays selectable for testing. It is a *view* over variants.py, not
a second store: the preferred selection is exactly each fork's adopted option,
so it cannot drift from the forks, and a test enforces that.

    from ...core.preferred_path import preferred_selection, snapshot
    preferred_selection()        -> {fork_id: option_id} for generation
    snapshot()                   -> the full state + a stable digest

WHAT THE DIGEST IS FOR
======================
Every snapshot carries a digest over (fork, option) pairs. Two runs with the
same digest were the same configuration; different digests mean the switches
moved. Recording the digest alongside a theory output makes "which
configuration produced this number" answerable after the fact, which is what
lets history comparison mean anything.

COMPARISON, AND THE RULE IT OBEYS
=================================
compare_states() runs a named set of observables under two selections and
reports both columns plus the delta. It deliberately does NOT rank by agreement
with experiment, per variants.py's standing rule -- a switchboard that reports
"which option fits best" is a parameter fitter. Residuals against registered
anchors are shown per row so nothing is hidden, but the ordering is always the
observable name and the verdict is always the same string.

The legitimate use is: see WHAT MOVES, how far, and in which direction. Deciding
which state is right remains an author ruling recorded at the fork's source.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

__all__ = [
    "PREFERRED_PATH_NAME",
    "preferred_selection",
    "active_selection_with_overrides",
    "snapshot",
    "digest_of",
    "is_on_preferred_path",
    "compare_states",
    "history_entry",
]

#: A human name for the declared state, carried into snapshots so a recorded
#: output says which path it came from rather than only a digest.
PREFERRED_PATH_NAME = "adopted-2026-09-14"


def _forks():
    from metaphysica.simulations.core.variants import FORKS

    return FORKS


def preferred_selection() -> Dict[str, str]:
    """The declared state: every fork at its adopted option.

    Sourced from the forks themselves, so this cannot disagree with them.
    """
    return {fid: fork.default() for fid, fork in sorted(_forks().items())}


def active_selection_with_overrides() -> Dict[str, str]:
    """What is ACTUALLY in force right now, environment overrides included."""
    from metaphysica.simulations.core.variants import resolve

    return {fid: resolve(fid) for fid in sorted(_forks())}


def digest_of(selection: Dict[str, str]) -> str:
    """A stable short digest over (fork, option) pairs."""
    payload = json.dumps(sorted(selection.items()), separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def is_on_preferred_path() -> Tuple[bool, Dict[str, Dict[str, str]]]:
    """Whether the live state is the declared one, and every departure."""
    preferred = preferred_selection()
    active = active_selection_with_overrides()
    departures = {
        fid: {"preferred": preferred[fid], "active": active[fid]}
        for fid in preferred
        if preferred.get(fid) != active.get(fid)
    }
    return (not departures), departures


def snapshot() -> Dict[str, Any]:
    """The full switch state, for stamping onto generated output."""
    preferred = preferred_selection()
    active = active_selection_with_overrides()
    on_path, departures = is_on_preferred_path()
    return {
        "preferred_path_name": PREFERRED_PATH_NAME,
        "preferred_selection": preferred,
        "preferred_digest": digest_of(preferred),
        "active_selection": active,
        "active_digest": digest_of(active),
        "on_preferred_path": on_path,
        "departures": departures,
        "n_forks": len(preferred),
        "open_forks": sorted(fid for fid, f in _forks().items()
                             if f.status == "OPEN"),
        "what_generation_should_use": (
            "preferred_selection. Documentation and theory output are "
            "generated on the preferred path; other states are for testing "
            "and comparison and must not be published as the theory."
        ),
    }


# --------------------------------------------------------------- comparison


#: Observables worth watching across states: (name, zero-arg callable).
#: Each reads live code, so a switch flip is reflected without wiring.
def _default_observables() -> Dict[str, Callable[[], Any]]:
    def re_t() -> Any:
        from metaphysica.simulations.PM.cosmology.baryon_asymmetry import (
            BaryonAsymmetryV18,
        )

        return BaryonAsymmetryV18._resolve_re_t()

    def phi_annihilator_dim() -> Any:
        import itertools

        import numpy as np

        from metaphysica.simulations.PM.geometry.g2_differential import (
            G2DifferentialGeometry,
        )

        phi = np.asarray(G2DifferentialGeometry().phi, dtype=float)
        pairs = list(itertools.combinations(range(7), 2))

        def as_matrix(vec):
            a = np.zeros((7, 7))
            for c, (i, j) in zip(vec, pairs):
                a[i, j] = c
                a[j, i] = -c
            return a

        def action(a):
            return (np.einsum("mi,mjk->ijk", a, phi)
                    + np.einsum("mj,imk->ijk", a, phi)
                    + np.einsum("mk,ijm->ijk", a, phi))

        basis = np.eye(21)
        cols = np.array([action(as_matrix(basis[b])).ravel()
                         for b in range(21)]).T
        sv = np.linalg.svd(cols, compute_uv=False)
        return 21 - int((sv > 1e-9 * max(sv)).sum())

    def free_set_size() -> Any:
        from metaphysica.simulations.core.free_set import build_free_set

        return build_free_set()["free_set_size"]

    def lattice_kissing() -> Any:
        from metaphysica.simulations.PM.algebra.leech_lattice import LeechLattice

        return getattr(LeechLattice(), "kissing_number", None)

    return {
        "free_set_size": free_set_size,
        "phi_annihilator_dim": phi_annihilator_dim,
        "racetrack_Re_T": re_t,
        "lattice_kissing_number": lattice_kissing,
    }


def _evaluate(observables: Dict[str, Callable[[], Any]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for name in sorted(observables):
        try:
            out[name] = observables[name]()
        except Exception as exc:               # a broken branch is data too
            out[name] = "ERROR: %s" % type(exc).__name__
    return out


def compare_states(state_a: Optional[Dict[str, str]] = None,
                   state_b: Optional[Dict[str, str]] = None,
                   observables: Optional[Dict[str, Callable[[], Any]]] = None
                   ) -> Dict[str, Any]:
    """Evaluate the observables under two switch states and show both columns.

    Implemented by setting the fork environment variables around each
    evaluation and restoring them afterwards, so no module needs to know it is
    being compared. Reports the delta; never orders by agreement with data.
    """
    from metaphysica.simulations.core.variants import _ENV_PREFIX

    state_a = state_a or preferred_selection()
    state_b = state_b or preferred_selection()
    observables = observables or _default_observables()

    def run_under(selection: Dict[str, str]) -> Dict[str, Any]:
        saved: Dict[str, Optional[str]] = {}
        try:
            for fid, opt in selection.items():
                key = _ENV_PREFIX + fid.upper()
                saved[key] = os.environ.get(key)
                os.environ[key] = opt
            _invalidate_caches()
            return _evaluate(observables)
        finally:
            for key, old in saved.items():
                if old is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = old
            _invalidate_caches()

    col_a = run_under(state_a)
    col_b = run_under(state_b)

    rows = []
    for name in sorted(observables):
        va, vb = col_a.get(name), col_b.get(name)
        delta: Any
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)) \
                and not isinstance(va, bool) and not isinstance(vb, bool):
            delta = vb - va
        else:
            delta = "changed" if va != vb else "same"
        rows.append({"observable": name, "state_a": va, "state_b": vb,
                     "delta": delta})

    return {
        "state_a": state_a,
        "state_a_digest": digest_of(state_a),
        "state_b": state_b,
        "state_b_digest": digest_of(state_b),
        "rows": rows,
        "n_changed": sum(1 for r in rows if r["delta"] not in ("same", 0)),
        "ordering": "observable name; never by agreement with experiment",
        "verdict": "NO_SELECTION_MADE",
    }


def _invalidate_caches() -> None:
    """Drop module caches that would otherwise survive a switch flip."""
    try:
        from metaphysica.simulations.PM.cosmology import racetrack_vacuum

        racetrack_vacuum._PARAMS_CACHE = None
    except Exception:
        pass


def history_entry(label: str, notes: str = "") -> Dict[str, Any]:
    """A record suitable for appending to a run history.

    Carries the switch state and its digest so a stored output can be traced
    back to the configuration that produced it. Timestamps are deliberately
    NOT added here: the caller stamps them, keeping this function pure and
    reproducible.
    """
    snap = snapshot()
    return {
        "label": label,
        "notes": notes,
        "preferred_path_name": snap["preferred_path_name"],
        "active_selection": snap["active_selection"],
        "active_digest": snap["active_digest"],
        "on_preferred_path": snap["on_preferred_path"],
        "departures": snap["departures"],
    }
