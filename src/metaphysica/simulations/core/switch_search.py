"""Search switch combinations for INTERNAL CONSISTENCY, never for agreement.

WHAT THIS IS FOR
================
Eight forks are open. Each encodes a decision nobody has been able to make from
the armchair, and their combinations are a space the theory might close
somewhere inside. This module enumerates that space and reports what each
combination does.

WHAT IT MUST NOT BECOME, AND THE REASON
=======================================
variants.py states the rule: a comparison reports EVERY option's outcome, never
returns "the best one", and never orders options by agreement with experimental
anchors. A switchboard that ranks combinations by how well they fit DESI or
NuFIT is a parameter fitter with better tooling, and this repository has already
retired one advertised agreement that came from exactly that pattern.

So this search deliberately cannot tell you which combination is right. It
orders by digest, it reports every row, and its verdict field is a constant.

WHAT IT CAN LEGITIMATELY DECIDE
===============================
Internal consistency, which references no measurement:

  CONTRADICTION       two live statements of the same quantity disagree -- for
                      example a row published DERIVED whose own seed is an
                      INPUT, or phi declared a G2 form while its annihilator is
                      6-dimensional.
  VACUOUS             a check that cannot fail in this configuration.
  STRUCTURAL_FAILURE  a constraint that mentions no experiment is violated --
                      n_gen = b_3/8 must be an integer; a generation count is a
                      number of things.

A combination with none of these is INTERNALLY_CONSISTENT. That is a real,
measurement-free discriminator, and it is the only kind this module applies.

Closure, if it happens, will look like: exactly one combination is internally
consistent AND has no LOAD_BEARING_INPUT left in the free set. This module
reports both numbers per combination so that state is recognisable when it
arrives. It does not declare it.

COST
====
The full product over eight open forks is large and each evaluation imports and
computes, so `search()` takes an explicit fork subset and a cap. Fork branches
also write to shared gitignored build artifacts, so anything reading a built
artifact must be rebuilt between branches -- the observables here read live code
and the registry, which is why they are safe to sweep.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
import os
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

__all__ = [
    "open_forks",
    "combinations_for",
    "evaluate_combination",
    "search",
    "consistency_checks",
]

VERDICT = "NO_SELECTION_MADE"


def _variants():
    from metaphysica.simulations.core import variants

    return variants


def open_forks() -> List[str]:
    """The forks still genuinely undecided, in declaration order."""
    forks = _variants().FORKS
    return [fid for fid, fork in forks.items() if fork.status == "OPEN"]


def combinations_for(fork_ids: Iterable[str],
                     cap: Optional[int] = None
                     ) -> List[Dict[str, str]]:
    """Every combination over the named forks, in declaration order."""
    forks = _variants().FORKS
    ids = [f for f in fork_ids if f in forks]
    option_lists = [forks[f].option_ids() for f in ids]
    out: List[Dict[str, str]] = []
    for choice in itertools.product(*option_lists):
        out.append(dict(zip(ids, choice)))
        if cap is not None and len(out) >= cap:
            break
    return out


# ----------------------------------------------------------- the checks


def _phi_annihilator_dim() -> Optional[int]:
    import itertools as it

    import numpy as np

    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )

    phi = np.asarray(G2DifferentialGeometry().phi, dtype=float)
    pairs = list(it.combinations(range(7), 2))

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
    cols = np.array([action(as_matrix(basis[b])).ravel() for b in range(21)]).T
    sv = np.linalg.svd(cols, compute_uv=False)
    return 21 - int((sv > 1e-9 * max(sv)).sum())


def consistency_checks() -> List[Dict[str, Any]]:
    """Measurement-free checks, evaluated in whatever state is live.

    Each returns a dict with `name`, `kind` and `ok`. Nothing here compares a
    prediction to an experiment; every check is about the theory agreeing with
    itself.
    """
    checks: List[Dict[str, Any]] = []

    # 1. Is phi actually a G2 form? g2 has dimension 14 by definition.
    try:
        dim = _phi_annihilator_dim()
        checks.append({
            "name": "phi_is_a_g2_form",
            "kind": "CONTRADICTION" if dim != 14 else None,
            "ok": dim == 14,
            "detail": "dim ann(phi) in so(7) = %s; g2 requires 14" % dim,
        })
    except Exception as exc:
        checks.append({"name": "phi_is_a_g2_form", "kind": "ERROR",
                       "ok": False, "detail": type(exc).__name__})

    # 2. n_gen = b_3/8 must be an integer. A generation count is a number of
    #    things -- this references no measurement.
    try:
        from metaphysica.simulations.core.arithma_formula import (
            registry_value,
            reset_cache,
        )

        reset_cache()
        b3 = registry_value("topology.elder_kads")
        integral = b3 is not None and abs(b3 / 8.0 - round(b3 / 8.0)) < 1e-12
        checks.append({
            "name": "n_gen_is_integral",
            "kind": None if integral else "STRUCTURAL_FAILURE",
            "ok": bool(integral),
            "detail": "b_3 = %s, b_3/8 = %s" % (b3, None if b3 is None else b3 / 8.0),
        })
    except Exception as exc:
        checks.append({"name": "n_gen_is_integral", "kind": "ERROR",
                       "ok": False, "detail": type(exc).__name__})

    # 3. Re(T) should be a stationary point of the declared potential, not a
    #    calibration. Compares the live Re(T) against the solved vacuum -- both
    #    internal to the theory.
    try:
        from metaphysica.simulations.PM.cosmology.baryon_asymmetry import (
            BaryonAsymmetryV18,
        )
        from metaphysica.simulations.PM.cosmology.racetrack_vacuum import (
            stationary_points,
        )

        live = float(BaryonAsymmetryV18._resolve_re_t())
        minima = [p for p in stationary_points(3) if p["kind"] == "minimum"]
        vacuum = minima[0]["re_t"] if minima else None
        at_vacuum = vacuum is not None and abs(live - vacuum) / vacuum < 1e-3
        checks.append({
            "name": "re_t_is_the_solved_vacuum",
            "kind": None if at_vacuum else "CONTRADICTION",
            "ok": bool(at_vacuum),
            "detail": "live Re(T) = %.4f, solved vacuum = %s" % (live, vacuum),
        })
    except Exception as exc:
        checks.append({"name": "re_t_is_the_solved_vacuum", "kind": "ERROR",
                       "ok": False, "detail": type(exc).__name__})

    # 4. Arithma third-track agreement on the b_3 relations: three independent
    #    statements of the same formulas must not disagree.
    try:
        from metaphysica.simulations.PM.geometry.b3_candidate_sweep import (
            arithma_track_report,
        )

        report = arithma_track_report()
        checks.append({
            "name": "arithma_track_agrees",
            "kind": None if report["all_agree"] else "CONTRADICTION",
            "ok": bool(report["all_agree"]),
            "detail": "statuses %s" % report["statuses"],
        })
    except Exception as exc:
        checks.append({"name": "arithma_track_agrees", "kind": "ERROR",
                       "ok": False, "detail": type(exc).__name__})

    # 5. Is the Joyce Betti route actually decidable here, or is a branch
    #    claiming what it cannot compute?
    try:
        from metaphysica.simulations.core.variants import resolve
        from metaphysica.simulations.PM.geometry.joyce_contributions import (
            table_is_supplied,
        )

        claims_joyce = resolve("b3_origin") == "joyce_twisted_sector"
        decidable = table_is_supplied()
        ok = (not claims_joyce) or decidable
        checks.append({
            "name": "joyce_branch_is_decidable",
            "kind": None if ok else "VACUOUS",
            "ok": ok,
            "detail": ("b3_origin claims the Joyce route but no validated "
                       "contribution table is present, so it asserts what it "
                       "cannot compute" if not ok else
                       "not claiming the Joyce route, or a table is present"),
        })
    except Exception as exc:
        checks.append({"name": "joyce_branch_is_decidable", "kind": "ERROR",
                       "ok": False, "detail": type(exc).__name__})

    return checks


def _free_set_load_bearing() -> Optional[int]:
    try:
        from metaphysica.simulations.core.free_set import build_free_set

        return int(build_free_set()["free_set_size"])
    except Exception:
        return None


# ------------------------------------------------------------- the search


def evaluate_combination(selection: Dict[str, str]) -> Dict[str, Any]:
    """Run the consistency checks under one switch combination."""
    from metaphysica.simulations.core.arithma_formula import reset_cache
    from metaphysica.simulations.core.preferred_path import digest_of
    from metaphysica.simulations.core.variants import _ENV_PREFIX

    saved: Dict[str, Optional[str]] = {}
    try:
        for fid, opt in selection.items():
            key = _ENV_PREFIX + fid.upper()
            saved[key] = os.environ.get(key)
            os.environ[key] = opt
        reset_cache()
        checks = consistency_checks()
        free_set_size = _free_set_load_bearing()
    finally:
        for key, old in saved.items():
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old
        reset_cache()

    problems = [c for c in checks if not c["ok"]]
    kinds = sorted({c["kind"] for c in problems if c.get("kind")})
    return {
        "selection": selection,
        "digest": digest_of(selection),
        "checks": checks,
        "n_problems": len(problems),
        "problem_kinds": kinds,
        "internally_consistent": not problems,
        "free_set_size": free_set_size,
        "verdict": VERDICT,
    }


def search(fork_ids: Optional[Iterable[str]] = None,
           cap: Optional[int] = 64) -> Dict[str, Any]:
    """Enumerate combinations and report every one. Selects nothing.

    Rows are ordered by DIGEST, deliberately: any ordering derived from the
    outcomes would be the first step towards ranking by agreement.
    """
    ids = list(fork_ids) if fork_ids is not None else open_forks()
    combos = combinations_for(ids, cap=cap)
    rows = [evaluate_combination(c) for c in combos]
    rows.sort(key=lambda r: r["digest"])

    consistent = [r for r in rows if r["internally_consistent"]]
    return {
        "what_this_reports": (
            "Every combination's internal consistency and cost. It does not "
            "say which is right, and it never orders by agreement with "
            "experiment."
        ),
        "forks_searched": ids,
        "n_combinations": len(rows),
        "capped": cap is not None and len(combos) >= cap,
        "rows": rows,
        "n_internally_consistent": len(consistent),
        "internally_consistent_digests": [r["digest"] for r in consistent],
        "ordering": "digest; never by residual or agreement",
        "closure_would_look_like": (
            "exactly one internally consistent combination whose free set has "
            "no load-bearing input left. Both numbers are reported per row so "
            "that state is recognisable; this module does not declare it."
        ),
        "verdict": VERDICT,
    }
