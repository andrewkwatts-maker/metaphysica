"""The FREE SET: how many independent knobs, not how many registration sites.

free_variable_ledger.py answers "which quantities did this framework not
derive", and answers it well. It counts ROWS. This module answers the different
question the framework actually needs: **how many of those rows are
independent?**

The two differ a lot. The three PMNS angles are registered three times each --
once as a geometry anchor, once as a neutrino prediction, once as a triality
branch -- and six CKM rows are arithmetic on three Wolfenstein inputs. Counting
sites inflates the number; counting knobs is what a free-parameter claim means.

That number is the RANK of the free set, and it is exactly what EDOF is supposed
to be. `statistical_rigor_validator.calculate_effective_dof` still returns a
hardcoded 3 with `# ANSATZ` above it, so the framework currently has one number
that is measured but inflated and one that is meaningful but asserted.

THE RULE THIS MODULE ENFORCES
=============================
A row is removed from the free set ONLY for a reason that can be checked:

  DERIVED_ARITHMETIC  a formula reproduces the registered value from other
                      rows, to tolerance. Verified numerically every run --
                      if the reproduction ever stops working the reduction is
                      withdrawn and the row returns to the free set.
  DUPLICATE           the same physical quantity registered under another name.
                      Structural, and the duplicate group is named.
  NOT_A_MODEL_KNOB    external data or an uncertainty. These are what
                      predictions are scored AGAINST. An error bar cannot be a
                      free parameter of the theory under any reading.

Nothing is removed because it looks redundant. A reduction with no check is
recorded as CLAIMED and still counts against the total, because the whole point
of this file is that the count cannot be improved by assertion.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Optional

__all__ = [
    "REASON_DERIVED",
    "REASON_DUPLICATE",
    "REASON_NOT_A_KNOB",
    "artifact_seed_provenance",
    "build_free_set",
    "duplicate_groups",
    "not_model_knobs",
    "verify_ckm_block",
]

REASON_DERIVED = "DERIVED_ARITHMETIC"
REASON_DUPLICATE = "DUPLICATE"
REASON_NOT_A_KNOB = "NOT_A_MODEL_KNOB"
REASON_CLAIMED = "CLAIMED_UNVERIFIED"

#: Relative tolerance for accepting that a formula reproduces a registered value.
#: Loose enough for a documented higher-order truncation (V_tb is exact only to
#: O(lambda^4)), tight enough that a wrong formula cannot sneak through.
_REL_TOL = 2e-2


def _param_candidates():
    """Where `parameters.json` may live. Delegated, not reimplemented.

    This lookup was open-coded here and broken: `parents[3]` resolves to
    `src/`, which the build never writes to, so an absolute Windows path from
    the author's machine was the only candidate that could match and on any
    other machine the lookup returned an EMPTY dict. `b3_path._registry`
    carried a second, differently-broken copy. Both now go through
    `parameter_artifact`, so the bug cannot be fixed in one and left in the
    other.
    """
    from metaphysica.simulations.core.parameter_artifact import candidate_paths

    return candidate_paths()


def params_source() -> Dict[str, Any]:
    """WHERE the parameter rows came from, or why there are none.

    Kept as a name here because the reduction's own report cites it. The
    resolution itself lives in `parameter_artifact`.
    """
    from metaphysica.simulations.core.parameter_artifact import params_source

    return params_source()


def _params() -> Dict[str, Any]:
    return params_source()["params"]


def _value(params, name):
    row = params.get(name)
    return row.get("value") if isinstance(row, dict) else None


# --------------------------------------------------------------- reductions


def verify_ckm_block(params=None) -> Dict[str, Any]:
    """Six CKM rows are arithmetic on the Wolfenstein inputs. Checked, not assumed.

    The standard parameterisation gives, with lambda = V_us:

        V_cb = A lambda^2
        V_ub = A lambda^3 sqrt(rho^2 + eta^2)
        V_td = A lambda^3 |1 - rho - i eta|
        V_tb = 1 - A^2 lambda^4 / 2            (exact only to O(lambda^4))
        J    = A^2 lambda^6 eta

    Every one is recomputed from the registry's own A, rho, eta and V_us and
    compared against the registered value. A row only leaves the free set if its
    own formula reproduces it.
    """
    params = params if params is not None else _params()
    A = _value(params, "ckm.A_wolfenstein")
    rho = _value(params, "ckm.rho_wolfenstein")
    eta = _value(params, "ckm.eta_wolfenstein")
    lam = _value(params, "ckm.V_us")

    inputs = {"ckm.A_wolfenstein": A, "ckm.rho_wolfenstein": rho,
              "ckm.eta_wolfenstein": eta, "ckm.V_us": lam}
    if any(v is None for v in inputs.values()):
        return {"available": False, "inputs": inputs, "derived": {},
                "note": "Wolfenstein inputs not all registered; no reduction made"}

    formulas: Dict[str, Callable[[], float]] = {
        "ckm.V_cb": lambda: A * lam ** 2,
        "ckm.V_ts": lambda: A * lam ** 2,
        "ckm.V_ub": lambda: A * lam ** 3 * math.hypot(rho, eta),
        "ckm.V_td": lambda: A * lam ** 3 * math.hypot(1.0 - rho, eta),
        "ckm.V_tb": lambda: 1.0 - A ** 2 * lam ** 4 / 2.0,
        "ckm.jarlskog_invariant": lambda: A ** 2 * lam ** 6 * eta,
    }

    derived = {}
    for name, fn in formulas.items():
        actual = _value(params, name)
        if actual is None:
            continue
        predicted = fn()
        rel = abs(predicted - actual) / abs(actual) if actual else abs(predicted)
        derived[name] = {
            "registered": actual,
            "from_free_set": predicted,
            "rel_error": rel,
            "reproduced": rel < _REL_TOL,
        }
    return {"available": True, "inputs": inputs, "derived": derived}


def verify_geometric_identities(params=None) -> Dict[str, Any]:
    """Rows whose values are exact arithmetic on geometric rows. Checked.

    Three, each verified to tolerance every run, each with its caveat stated:

    * fermion.n_generations = b_3 / 8. The ANSATZ row restates arithmetic on
      the registered particle.b3; its free content is b_3's, counted (or
      contested) there, not here.
    * yukawa.lambda_eff = (1 + sqrt 5)/2 exactly. The free content is the
      DISCRETE choice yukawa.best_scaling = "phi", which STAYS in the free
      set; the continuous value adds nothing once the choice is made.
    * cosmology.wa_thawing = -4 / sqrt(b_3) exactly. That formula is RETIRED
      on the register ("do not resurrect") -- removing the row from the free
      set does not revive the physics claim, it records that a legacy artefact
      of a falsified derivation carries no independent numeric content.
    """
    import math

    params = params if params is not None else _params()
    b3 = _value(params, "particle.b3")

    checks: Dict[str, Dict[str, Any]] = {}

    def _check(name: str, predicted, detail: str,
               uses_b3: bool = False) -> None:
        actual = _value(params, name)
        if actual is None or predicted is None:
            return
        rel = abs(predicted - actual) / max(abs(actual), 1e-300)
        checks[name] = {
            "registered": actual,
            "predicted": predicted,
            "rel_error": rel,
            "reproduced": rel < 1e-9,
            "detail": detail,
            "uses_b3": uses_b3,
        }

    # n_generations follows the RULED n_gen_source route, not b_3/8. The
    # b_3/8 form was the seed_24 route and yields 5.375 on the adopted seed
    # -- a non-integral generation count, which is exactly the structural
    # failure that moved the ruling. Checking the abandoned route here made
    # the row look un-reproducible and pushed it back into the free set
    # (b3_seed adoption, 2026-09-22).
    try:
        from metaphysica.simulations.PM.geometry.b3_path import n_gen_report

        _ruled_n_gen = n_gen_report()
        _check("fermion.n_generations", float(_ruled_n_gen["n_gen"]),
               "the RULED n_gen_source route (%s); the b_3/8 form is the "
               "seed_24 route and is non-integral on the adopted seed"
               % _ruled_n_gen["declared_source"])
    except ImportError:                    # import cycle only
        pass
        _check("cosmology.wa_thawing", -4.0 / math.sqrt(b3),
               "-4/sqrt(b_3) -- the RETIRED formula's legacy artefact; "
               "removal records no independent content, not a revival",
               uses_b3=True)
    if _value(params, "yukawa.best_scaling") == "phi":
        _check("yukawa.lambda_eff", (1.0 + math.sqrt(5.0)) / 2.0,
               "the golden ratio, determined by the discrete choice "
               "yukawa.best_scaling = 'phi', which stays in the free set")
    if b3:
        _check("algebra.freudenthal_quartic", 16.0 * (b3 / 27.0) ** 2,
               "16 (b_3/27)^2 -- a function of b_3 alone, verified against "
               "the eml_spectral path's output. NOTE the module's ImportError "
               "fallback computes a DIFFERENT formula (27 c^4 / 4, exactly 3x "
               "smaller); that inconsistency is registered separately",
               uses_b3=True)
    _check("abstract.alpha_gut_coefficient",
           round(1.0 / (10.0 * math.pi), 6),
           "declared in code as round(1/(10 pi), 6) at paper/abstract.py; "
           "the value is arithmetic on pi. The FORMULA choice 1/(10 pi) is a "
           "discrete ansatz with no row of its own -- listed under "
           "dissolved_discrete_choices so the count's caveat is explicit")
    return checks


def metadata_rows(params=None) -> Dict[str, str]:
    """Rows that describe the fit rather than parameterise the model.

    abstract.fitted_pmns = 2 is a COUNT of fitted parameters -- bookkeeping
    about the model, not a quantity the model could turn. Counting it as a
    free parameter double-counts the parameters it counts.
    """
    params = params if params is not None else _params()
    reasons = {
        "abstract.fitted_pmns": "a count of fitted parameters, not a knob",
    }
    return {k: v for k, v in reasons.items() if k in params}


def duplicate_groups(params=None) -> Dict[str, List[str]]:
    """The same physical quantity registered under more than one name.

    Structural rather than numerical: the triality rows are an alternative
    PARAMETERISATION of the same angles, not additional freedom, and the
    geometry/neutrino/pmns copies are the same three angles three times.
    """
    params = params if params is not None else _params()
    groups = {
        "pmns.theta_12": ["geometry.theta_12", "neutrino.theta_12_pred",
                          "pmns.theta_12_triality"],
        "pmns.theta_13": ["geometry.theta_13", "neutrino.theta_13_pred",
                          "pmns.theta_13_triality"],
        "pmns.theta_23": ["geometry.theta_23", "neutrino.theta_23_pred",
                          "pmns.theta_23_triality"],
        "pmns.delta_CP": ["geometry.delta_CP_PMNS", "neutrino.delta_CP_pred"],
        "cosmology.H0_local": ["geometry.H0_local", "cosmology.H0_local"],
        "ckm.A": ["geometry.A_Wolfenstein", "ckm.A_wolfenstein"],
        "ckm.V_cb_group": ["ckm.V_cb", "ckm.V_cb_triality"],
        "ckm.V_ub_group": ["ckm.V_ub", "ckm.V_ub_triality"],
    }
    return {k: [n for n in v if n in params] for k, v in groups.items()}


def not_model_knobs(params=None) -> Dict[str, str]:
    """External data and uncertainties. Not freedom of the theory.

    These are what predictions are scored against. w0_error_DESI is an ERROR
    BAR; it cannot be a free parameter under any reading, and its presence in a
    free-variable count is the clearest sign the count was measuring sites
    rather than knobs.
    """
    params = params if params is not None else _params()
    reasons = {
        "geometry.w0_error_DESI": "an experimental uncertainty, not a quantity",
        "geometry.w0_observed_DESI": "DESI datum; predictions are scored against it",
        "geometry.wa_observed_DESI": "DESI datum; predictions are scored against it",
        "geometry.omega_Lambda_Planck": "Planck datum, comparison only",
        "geometry.Omega_radiation": "measured cosmological datum, comparison only",
        "geometry.m_KK_bound": "an experimental bound, not a fitted value",
        "cosmology.M_Pl_4D": "a unit convention fixed by measurement",
    }
    return {k: v for k, v in reasons.items() if k in params}


# --------------------------------------------------------------- the free set


def artifact_seed_provenance(params=None) -> Dict[str, Any]:
    """Which seed built the artifact this module reads, versus the live fork.

    _params() reads AutoGenerated/parameters.json -- a BUILD ARTIFACT that
    fork branches share (it is gitignored, and flipping the env var does not
    rebuild it). Every b_3-arithmetic removal below verifies against the
    ARTIFACT's b_3, not the fork's. That is internally consistent -- the
    dependent rows in the same artifact moved together -- but presenting it
    as the live fork's free count would be the shared-artifact trap inside
    the free set itself. This function makes the provenance explicit so a
    mismatch is labelled rather than silent.
    """
    params = params if params is not None else _params()
    artifact_b3 = _value(params, "particle.b3")

    try:
        from metaphysica.simulations.PM.geometry.b3_path import (
            resolve_path,
            seed_values,
        )

        seed = resolve_path()
        live_b3, live_b2 = seed_values(seed)
    except Exception as exc:               # pragma: no cover - import failure
        return {
            "artifact_b3": artifact_b3,
            "live_fork_seed": None,
            "live_fork_b3": None,
            "consistent": None,
            "note": "b3_path unavailable (%s); provenance UNKNOWN, which is "
                    "a reportable state, not a pass" % type(exc).__name__,
        }

    consistent = (artifact_b3 == live_b3) if artifact_b3 is not None else None
    return {
        "artifact_b3": artifact_b3,
        "live_fork_seed": seed,
        "live_fork_b3": live_b3,
        "consistent": consistent,
        "note": (
            "b_3-arithmetic removals verify against the ARTIFACT's b_3. When "
            "consistent is False the artifact was built under a different "
            "seed than the live fork resolves to, and those removals are "
            "artifact-truth, not fork-truth: rebuild before reading the free "
            "count as the fork's."
        ),
    }


def build_free_set(params=None) -> Dict[str, Any]:
    """Reduce the ledger's rows to independent knobs, checking every removal."""
    from metaphysica.simulations.core.free_variable_ledger import build_ledger

    if params is not None:
        source = {"available": bool(params), "path": "supplied by caller",
                  "n_rows": len(params)}
    else:
        source = params_source()
        params = source["params"]

    rows = [r["name"] for r in build_ledger()["rows"]]
    removals: Dict[str, Dict[str, str]] = {}

    ckm = verify_ckm_block(params)
    if ckm["available"]:
        for name, rec in ckm["derived"].items():
            if name in rows and rec["reproduced"]:
                removals[name] = {
                    "reason": REASON_DERIVED,
                    "detail": "reproduced from the Wolfenstein inputs, rel err "
                              "%.1e" % rec["rel_error"],
                }
            elif name in rows:
                removals[name] = {
                    "reason": REASON_CLAIMED,
                    "detail": "formula did NOT reproduce the registered value "
                              "(rel err %.1e); stays in the free set"
                              % rec["rel_error"],
                }

    geometric = verify_geometric_identities(params)
    for name, rec in geometric.items():
        if name in rows and rec["reproduced"]:
            removals.setdefault(name, {
                "reason": REASON_DERIVED,
                "detail": rec["detail"] + " (rel err %.1e)" % rec["rel_error"],
            })
        elif name in rows:
            removals.setdefault(name, {
                "reason": REASON_CLAIMED,
                "detail": "identity did NOT reproduce the registered value "
                          "(rel err %.1e); stays in the free set"
                          % rec["rel_error"],
            })

    for canonical, members in duplicate_groups(params).items():
        present = [m for m in members if m in rows]
        for name in present[1:]:
            removals.setdefault(name, {
                "reason": REASON_DUPLICATE,
                "detail": "same quantity as %s (group %s)" % (present[0], canonical),
            })

    for name, why in not_model_knobs(params).items():
        if name in rows:
            removals.setdefault(name, {"reason": REASON_NOT_A_KNOB, "detail": why})

    for name, why in metadata_rows(params).items():
        if name in rows:
            removals.setdefault(name, {"reason": REASON_NOT_A_KNOB, "detail": why})

    removed = {k: v for k, v in removals.items() if v["reason"] != REASON_CLAIMED}
    free = [r for r in rows if r not in removed]

    by_reason: Dict[str, int] = {}
    for rec in removed.values():
        by_reason[rec["reason"]] = by_reason.get(rec["reason"], 0) + 1

    provenance = artifact_seed_provenance(params)
    resting_on_stale_b3 = sorted(
        name for name, rec in geometric.items()
        if rec.get("uses_b3") and name in removed
    ) if provenance["consistent"] is False else []

    return {
        "what_this_counts": (
            "Independent knobs. A row leaves the free set only for a checkable "
            "reason, and an unverified claim leaves it in."
        ),
        "ledger_rows": len(rows),
        "free_set_size": len(free),
        "removed_count": len(removed),
        "artifact_seed_provenance": provenance,
        "removals_resting_on_stale_b3": resting_on_stale_b3,
        "removed_by_reason": by_reason,
        #: WHERE the values every removal was checked against came from. Without
        #: it an unreachable artifact looks like a physics result: no parameters
        #: means no verification means no removals means free_set == ledger_rows.
        "parameters_source": {k: v for k, v in source.items()
                              if k != "params"},
        "reduction_ran": bool(source.get("available")),
        "unverified_claims": {k: v for k, v in removals.items()
                              if v["reason"] == REASON_CLAIMED},
        "dissolved_discrete_choices": {
            "abstract.alpha_gut_coefficient": "the formula 1/(10 pi)",
            "yukawa.lambda_eff": "carried by yukawa.best_scaling, which stays",
        },
        "removed": removed,
        "free_set": sorted(free),
        "still_asserted_edof": (
            "statistical_rigor_validator.calculate_effective_dof returns a "
            "hardcoded 3 with ANSATZ above it. This module measures the same "
            "notion; the two should be reconciled, and that is an open ruling."
        ),
    }


def main(argv=None) -> int:
    import json

    report = build_free_set()
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ("removed", "free_set")}, indent=2))
    print("free set (%d):" % report["free_set_size"])
    for name in report["free_set"]:
        print("   ", name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
