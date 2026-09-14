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

#: Registered rows that each claim to be the sum of the neutrino masses, in eV.
#: Named rather than pattern-matched, so the set is auditable and a row cannot
#: join or leave it silently. Measured 2026-09-14, all under the framework's own
#: declared INVERTED ordering (`neutrino.ordering`, PREDICTED):
#:
#:     neutrino.sum_masses        0.101975   DERIVED   matter_sector_complete_v19
#:     particle.sigma_m_base_eV   0.060517   DERIVED   neutrino_sector v26.0
#:     particle.sigma_m_refined_eV 0.042517  DERIVED   neutrino_sector v26.0
#:
#: neutrino.mass_sum (0.101214) is deliberately EXCLUDED: it is FITTED, and a fit
#: disagreeing with a derivation is not the theory contradicting itself.
#: base and refined are also both listed on purpose -- the module presents the
#: refined value as superseding the base one, yet registers both as DERIVED, so
#: the register carries two live derived answers rather than one.
NEUTRINO_MASS_SUM_ROWS = (
    "neutrino.sum_masses",
    "particle.sigma_m_base_eV",
    "particle.sigma_m_refined_eV",
)


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
        statuses = list(report["statuses"])
        # An absent backend is not a disagreement. Every published arithma
        # binds Expression to None, so check() returns BACKEND_UNAVAILABLE for
        # every formula and there is no second statement to disagree WITH.
        # Scoring that as CONTRADICTION made all 16 combinations report a
        # contradiction the framework does not have, and drove
        # n_internally_consistent to 0 for a reason that is about the
        # environment rather than the theory. It is VACUOUS by this module's
        # own definition -- a check that cannot fail in this configuration --
        # and a configuration whose consistency rests on a check that cannot
        # fail is still not demonstrated consistent, so it still counts
        # against the row.
        unevaluable = {"BACKEND_UNAVAILABLE", "INPUTS_MISSING", "TREE_FAILED",
                       "NO_PYTHON_REFERENCE"}
        if report["all_agree"]:
            kind, ok, here = None, True, True
        elif statuses and set(statuses) <= unevaluable:
            kind, ok, here = "VACUOUS", False, False
        else:
            kind, ok, here = "CONTRADICTION", False, True
        checks.append({
            "name": "arithma_track_agrees",
            "kind": kind,
            "ok": ok,
            # False means THIS ENVIRONMENT could not evaluate the check, which
            # is different from the theory being vacuous here. The Joyce check
            # below is genuinely VACUOUS -- a branch asserting what it cannot
            # compute is a property of the theory -- and must keep counting
            # against its row.
            "evaluable_here": here,
            "detail": "statuses %s" % statuses,
        })
    except Exception as exc:
        checks.append({"name": "arithma_track_agrees", "kind": "ERROR",
                       "ok": False, "detail": type(exc).__name__})

    # 5. Is the neutrino mass sum stated ONCE? Three registered rows claim to
    #    be the sum of the neutrino masses and disagree by a factor of 2.4.
    #    This compares the framework's own rows against each other; nothing
    #    measured enters, and the row names live in a module constant so the
    #    anti-anchor source scan over this function stays exact.
    try:
        from metaphysica.simulations.core.arithma_formula import (
            registry_value,
            reset_cache,
        )

        reset_cache()
        values = {path: registry_value(path) for path in NEUTRINO_MASS_SUM_ROWS}
        live = {k: v for k, v in values.items() if v is not None}
        # 1e-9 is not a tolerance chosen here: it is the relative tolerance
        # ArithmaFormula.check() already uses for "two statements of one
        # number agree", reused so this check invents nothing.
        agree = True
        if len(live) > 1:
            lo, hi = min(live.values()), max(live.values())
            agree = abs(hi - lo) <= 1e-9 * max(abs(hi), 1e-300)
        checks.append({
            "name": "neutrino_mass_sum_is_stated_once",
            "kind": None if agree else "CONTRADICTION",
            "ok": bool(agree),
            "evaluable_here": len(live) > 1,
            "detail": ("%d rows claim the neutrino mass sum: %s"
                       % (len(live),
                          ", ".join("%s=%.6g" % (k, v)
                                    for k, v in sorted(live.items())))),
        })
    except Exception as exc:
        checks.append({"name": "neutrino_mass_sum_is_stated_once", "kind": "ERROR",
                       "ok": False, "detail": type(exc).__name__})

    # 6. Is the Joyce Betti route actually decidable here, or is a branch
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

    # 6. THE A4 BAR, as a consistency check.
    #
    #    Added after the first search showed the other five checks were BLIND
    #    to b3_origin: input_24, arc_flag_stabiliser and d4_root_shell all came
    #    out identically consistent. They are not equivalent. Two of them CLAIM
    #    an origin for b_3 while being recorded NUMERICAL -- they reproduce the
    #    integer 24 without exhibiting 24 three-cycles or harmonic 3-forms.
    #
    #    Claiming a geometric origin that does not clear that bar is an
    #    internal contradiction, and it references no measurement. input_24
    #    claims nothing, so it passes; the Joyce branch would clear the bar if
    #    it could be computed, which check 5 handles separately.
    try:
        from metaphysica.simulations.core.variants import FORKS, resolve

        origin = resolve("b3_origin")
        numerical_origins = {"arc_flag_stabiliser", "d4_root_shell"}
        claims_geometry = origin in numerical_origins
        checks.append({
            "name": "b3_origin_clears_the_a4_bar",
            "kind": "CONTRADICTION" if claims_geometry else None,
            "ok": not claims_geometry,
            "detail": (
                "b3_origin = %s asserts a geometric origin for b_3 but is "
                "recorded NUMERICAL: it reproduces the integer without "
                "exhibiting 24 three-cycles or harmonic 3-forms" % origin
                if claims_geometry else
                "b3_origin = %s claims no unearned geometric origin" % origin
            ),
        })
    except Exception as exc:
        checks.append({"name": "b3_origin_clears_the_a4_bar", "kind": "ERROR",
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
    # A row held back ONLY by checks that could not be evaluated here is a
    # different state from a row that contradicts itself, and conflating the
    # two makes the search unreadable wherever an optional backend is absent
    # -- which, for arithma, is everywhere it installs from PyPI. Reported
    # separately; NOT counted as consistent, because an unevaluated check is
    # not a passed one.
    blocked_only_by_unevaluable = bool(problems) and all(
        c.get("evaluable_here") is False for c in problems)
    return {
        "selection": selection,
        "digest": digest_of(selection),
        "checks": checks,
        "n_problems": len(problems),
        "problem_kinds": kinds,
        "internally_consistent": not problems,
        "blocked_only_by_unevaluable_checks": blocked_only_by_unevaluable,
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
    blocked = [r for r in rows if r["blocked_only_by_unevaluable_checks"]]

    # A check with the same outcome in EVERY combination says nothing about the
    # switches -- it is a standing property of the theory that no setting of
    # these forks addresses. Reporting it per row buries the structure the
    # search exists to expose: one fork-independent contradiction makes all
    # sixteen rows inconsistent and the sweep stops discriminating.
    #
    # Separated, NOT excused. A standing contradiction still makes every row
    # internally inconsistent, and `internally_consistent` is unchanged.
    names = sorted({c["name"] for r in rows for c in r["checks"]})
    outcomes = {n: {tuple(c["ok"] for c in r["checks"] if c["name"] == n)
                    for r in rows} for n in names}
    failing_everywhere = sorted(
        n for n in names
        if outcomes[n] == {(False,)} )
    varies_with_the_switches = sorted(
        n for n in names if len(outcomes[n]) > 1)
    fork_dependent_clean = [
        r for r in rows
        if not [c for c in r["checks"]
                if not c["ok"] and c["name"] in varies_with_the_switches]
    ]
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
        "n_blocked_only_by_unevaluable_checks": len(blocked),
        "blocked_only_by_unevaluable_digests": [r["digest"] for r in blocked],
        "problems_no_combination_fixes": failing_everywhere,
        "problems_the_switches_control": varies_with_the_switches,
        "n_clean_on_every_switch_controlled_check": len(fork_dependent_clean),
        "clean_on_every_switch_controlled_check_digests": [
            r["digest"] for r in fork_dependent_clean],
        "why_those_are_separated": (
            "A check failing in every combination is a standing property of "
            "the theory that no setting of these forks addresses. It is "
            "reported apart so one such defect does not flatten the sweep, "
            "and it is NOT excused: those rows remain internally "
            "inconsistent. The last count is 'as good as these switches can "
            "make it', which is a structural statement and not a ranking -- "
            "no row is ordered ahead of another and the digests are sorted."
        ),
        "why_that_second_count_exists": (
            "A check that cannot be evaluated is not a check that failed. "
            "With no usable arithma the third-track check is VACUOUS for every "
            "combination, so n_internally_consistent reads 0 for a reason "
            "about the environment rather than the theory. These rows have "
            "nothing else against them."
        ),
        "ordering": "digest; never by residual or agreement",
        "closure_would_look_like": (
            "exactly one internally consistent combination whose free set has "
            "no load-bearing input left. Both numbers are reported per row so "
            "that state is recognisable; this module does not declare it."
        ),
        "verdict": VERDICT,
    }
