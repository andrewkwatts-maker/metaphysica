"""Every claimed integer identity, evaluated LIVE per fork state.

WHY THIS EXISTS
===============
The b3_seed adoption (author ruling 2026-09-22: (b_2, b_3) = (12, 43)) broke a
family of integer coincidences that had been load-bearing without ever being
labelled as coincidences. The breakages were found ONE AT A TIME, each by a
different accident:

  D_bulk = b_3 + 2      found because three simulations hard-failed under 43
  tau_24 = b_3          found because the ambiguous-alias guard saw two rows
                        with the same short name and different values
  n(n-1)/2 + 12 = 288   found because appendix_h started emitting 915
  163 = 7 b_3 - 5       found by the shadow-derivation audit

Four instruments catching four instances of ONE class means the class was
never searched for -- the same argument that produced `core/seed_blindness.py`.
This module is the search: every identity anyone has claimed is registered
here with the fork state it is evaluated in, and the next broken coincidence
is a REPORT rather than a crash in whichever simulation happened to assert it.

WHAT AN ENTRY MUST CARRY, AND WHY
=================================
Three fields beyond the arithmetic, all mandatory:

  ``counts``   what each number in the identity COUNTS. This is the A4 bar,
               and it is the field that does the work: `24` as the Leech
               lattice dimension and `24` as b_3 are different objects that
               happened to be equal on the off-path seed, and every defect
               this campaign found was two such objects wearing one integer.
  ``claimed``  the value the identity is claimed to produce, as a literal. An
               identity whose right-hand side is recomputed from the same
               expression as its left cannot fail, so the claim is FROZEN here
               and the evaluation is compared against it.
  ``source``   where the claim is made, so a BROKEN row is actionable rather
               than merely interesting.

A row is never removed because it broke. `seed_24` remains runnable and its
column remains in the report, so "this held at 24 and nowhere else" is a
published fact rather than a deleted one -- the same rule that keeps falsified
candidates on the books.

WHAT THIS MODULE MUST NOT BECOME
================================
It reports HOLDS / BROKEN per branch. It does not rank branches, does not
prefer the branch where more identities hold, and does not treat a broken
identity as evidence against the ruling. A count of surviving coincidences is
exactly the kind of number that would make this a fitter, and the adoption was
ruled on reachability and generation count, not on coincidence survival.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, NamedTuple, Optional

__all__ = [
    "Identity",
    "IDENTITIES",
    "identity_by_id",
    "evaluate_identity",
    "evaluate_all",
    "identity_report",
    "write_report",
]


class Identity(NamedTuple):
    """One claimed integer identity, with everything needed to falsify it."""

    id: str
    claim: str
    #: What each number in the identity counts. Mandatory; see module docstring.
    counts: str
    #: The literal the identity is claimed to produce. Frozen, not recomputed.
    claimed: Any
    #: Where the claim is made.
    source: str
    #: (b3, b2, chi_eff) -> computed value, or None when not evaluable.
    evaluate: Callable[[int, int, Optional[float]], Any]
    #: True when the identity references chi_eff, whose route is UNRULED.
    chi_eff_dependent: bool = False


# ---------------------------------------------------------------------------
# The registry.
#
# Ordered by id so the emitted artifact is deterministic. Every `evaluate`
# takes the full (b3, b2, chi_eff) state even when it uses one of them, so a
# row can be re-scoped without changing the call site.
# ---------------------------------------------------------------------------

IDENTITIES: List[Identity] = [
    Identity(
        id="ancestral_roots_from_so_n",
        claim="b_3(b_3-1)/2 + 2*12 - 12 = 288",
        counts=(
            "b_3(b_3-1)/2 counts the generators of SO(n) on n transverse "
            "directions; 2*12 counts torsion pins over two shadow branes; "
            "-12 counts symmetry directions spent projecting onto the "
            "manifold. The identity holds only where n = 24, and whether n "
            "is b_3 or the BULK's 24 spacelike core dimensions is the open "
            "reading -- appendix_h reads it from topology.elder_kads."
        ),
        claimed=288,
        source="PM.paper.appendices.appendix_h_288_roots.run",
        evaluate=lambda b3, b2, chi: b3 * (b3 - 1) // 2 + 12,
    ),
    Identity(
        id="alpha_f_curvature_coefficient",
        claim="1/b_3^2 = 1/576",
        counts=(
            "b_3^2 counts ordered pairs of associative 3-cycles; the "
            "coefficient is claimed to be fixed 'from topology alone'."
        ),
        claimed=576,
        source="PM.derivations.cosmology_sector_complete (alpha_F = 1/b3^2)",
        evaluate=lambda b3, b2, chi: b3 * b3,
    ),
    Identity(
        id="bridge_pairs_half_b3",
        claim="P_12 = b_3/2 = 12",
        counts=(
            "b_3/2 is claimed to count bridge PAIRS. 12 is independently the "
            "K_4 directed-edge count and the derived A1 T^3 family count "
            "(= b_2), and nothing shows those three 12s to be the same 12."
        ),
        claimed=12,
        source="PM.paper.appendices.appendix_g_omega_seal (P_12 = b3/2)",
        evaluate=lambda b3, b2, chi: b3 / 2,
    ),
    Identity(
        id="chi_eff_over_b3_is_three",
        claim="chi_eff / b_3 = 3",
        counts=(
            "chi_eff is an effective Euler characteristic; b_3 counts "
            "associative 3-cycles; 3 is the generation count. This was one "
            "of the routes to n_gen and is NOT the ruled one "
            "(n_gen_source = b2_over_faces)."
        ),
        claimed=3,
        source="PM.geometry.chi_eff_branches; FormulasRegistry.n_gen (retired route)",
        evaluate=lambda b3, b2, chi: (chi / b3) if chi else None,
        chi_eff_dependent=True,
    ),
    Identity(
        id="chi_pressure_from_b3_squared",
        claim="b_3^2 / 4 = 144",
        counts=(
            "b_3^2/4 is claimed to give the pressure divisor 144. 144 also "
            "arrives as 2(h11 - h21 + h31), a route that does not reference "
            "the seed -- two derivations of one integer, agreeing only at 24."
        ),
        claimed=144,
        source="PM.paper.appendices.appendix_h_288_roots (H.9 pressure divisor)",
        evaluate=lambda b3, b2, chi: b3 * b3 / 4,
    ),
    Identity(
        id="d_bulk_is_b3_plus_two",
        claim="D_bulk = b_3 + 2 = 26",
        counts=(
            "b_3 counts associative 3-cycles; the +2 counts lightcone "
            "directions (time + longitudinal). 26 is the BULK dimension, "
            "ruled independently at signature (24,2). RECORDED BROKEN at the "
            "adoption: 26 - 43 = -17."
        ),
        claimed=26,
        source="PM.geometry.modular_invariance; PM.validation.consistency_beacons",
        evaluate=lambda b3, b2, chi: b3 + 2,
    ),
    Identity(
        id="hidden_supports_seven_b3_minus_five",
        claim="7 b_3 - 5 = 163",
        counts=(
            "163 is the hidden-support count (ancestral roots minus active "
            "residues). The 7 and the -5 are fitted integers, not counted "
            "objects -- which is why this row is the clearest coincidence in "
            "the ledger."
        ),
        claimed=163,
        source="simulations.validation.eta_s_derivation_test (formula='7 * b3 - 5')",
        evaluate=lambda b3, b2, chi: 7 * b3 - 5,
    ),
    Identity(
        id="modular_anomaly_b3_mod_24",
        claim="b_3 = 0 (mod 24)",
        counts=(
            "the modular anomaly condition asks b_3 to be divisible by 24, "
            "where 24 is the eta-function's transverse oscillator count -- a "
            "BULK property. Imposing it ON b_3 is the conflation itself."
        ),
        claimed=0,
        source="PM.geometry.modular_invariance (modular-anomaly-condition)",
        evaluate=lambda b3, b2, chi: b3 % 24,
    ),
    Identity(
        id="n_eff_cycles_b3_minus_14",
        claim="N_eff = b_3 - 14 = 10",
        counts=(
            "b_3 counts 3-cycles; 14 is subtracted as the dimension of g_2. "
            "A cycle count minus a Lie-algebra dimension is a subtraction "
            "between different kinds of object."
        ),
        claimed=10,
        source="PM.derivations.cosmology_sector_complete (N_eff = b3 - 14)",
        evaluate=lambda b3, b2, chi: b3 - 14,
    ),
    Identity(
        id="n_gen_from_b2_over_faces",
        claim="b_2 / 4 = 3",
        counts=(
            "b_2 counts exceptional 2-classes (one per A1 T^3 family); 4 "
            "counts the faces of K_4, derived as the moved coordinates of an "
            "involution. This is the RULED n_gen_source."
        ),
        claimed=3,
        source="PM.geometry.b3_path.n_gen_report; variants fork n_gen_source",
        evaluate=lambda b3, b2, chi: b2 / 4,
    ),
    Identity(
        id="n_gen_from_b3_over_eight",
        claim="b_3 / 8 = 3",
        counts=(
            "b_3 counts 3-cycles; 8 is dim(O). REFUTED ROUTE, kept runnable "
            "and labelled: it is not the ruled n_gen_source, and a "
            "generation count is a number of things, so a non-integer here "
            "is a structural failure rather than a disagreement with data."
        ),
        claimed=3,
        source="PM.geometry.chi_eff_branches.route_c_is_the_b3_over_8_route",
        evaluate=lambda b3, b2, chi: b3 / 8,
    ),
    Identity(
        id="reachability_b3_is_seven_plus_three_b2",
        claim="b_3 = 7 + 3 b_2",
        counts=(
            "7 counts the flat b_3 contribution of the Joyce orbifold; 3 "
            "counts the 3-cycles each resolved A1 T^3 family contributes; "
            "b_2 counts those families. This is the REACHABILITY relation, "
            "and it is the criterion that excludes seed_24 -- so it is "
            "expected to hold on the Joyce family and fail off it."
        ),
        claimed=0,
        source="PM.geometry.derived_contribution_table; b3_path.PATHS",
        evaluate=lambda b3, b2, chi: b3 - (7 + 3 * b2),
    ),
    Identity(
        id="roots_total_twelve_b3",
        claim="R_288 = 12 b_3 = 288",
        counts=(
            "12 is the bridge count (K_4 directed edges); b_3 counts "
            "3-cycles. Gives 288 at b_3 = 24, the SAME integer the SO(n) "
            "route gives -- two unrelated routes agreeing at one seed."
        ),
        claimed=288,
        source="PM.qed._triple_track; PM.paper.appendices.appendix_g_omega_seal",
        evaluate=lambda b3, b2, chi: 12 * b3,
    ),
    Identity(
        id="shadow_dim_half_b3_plus_one",
        claim="13 = b_3/2 + 1",
        counts=(
            "13 is the shadow-brane dimension (12 bridge dims + 1 time), "
            "ruled as half of the 26D bulk. Deriving it from b_3 makes a "
            "BULK quantity depend on the seed."
        ),
        claimed=13,
        source="PM.paper.appendices.appendix_c_gauge_matrices (I_13 rank)",
        evaluate=lambda b3, b2, chi: b3 / 2 + 1,
    ),
    Identity(
        id="shadow_torsion_total_is_b3",
        claim="tau_24 = b_3 = 24",
        counts=(
            "tau_24 counts torsion pins, 12 per shadow brane over two "
            "branes. Binding it to b_3 is the conflation that made "
            "strategy_a's G22 read reg.b3 for a quantity its own header "
            "calls shadow_pins."
        ),
        claimed=24,
        source="PM.paper.appendices.appendix_g_omega_seal (tau_24 = b3)",
        evaluate=lambda b3, b2, chi: b3,
    ),
]


def identity_by_id(identity_id: str) -> Optional[Identity]:
    """The registered identity with this id, or None."""
    for row in IDENTITIES:
        if row.id == identity_id:
            return row
    return None


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def _status(computed: Any, claimed: Any) -> str:
    """HOLDS / BROKEN / NOT_EVALUABLE for one computed-vs-claimed pair."""
    if computed is None:
        return "NOT_EVALUABLE"
    try:
        return "HOLDS" if abs(float(computed) - float(claimed)) < 1e-12 \
            else "BROKEN"
    except (TypeError, ValueError):
        return "HOLDS" if computed == claimed else "BROKEN"


def evaluate_identity(identity: Identity, b3: int, b2: int,
                      chi_eff: Optional[float] = None) -> Dict[str, Any]:
    """Evaluate one identity in an explicit fork state.

    The state is passed in rather than read from the environment so a report
    can cover every branch without process-level flipping. `chi_eff` is
    optional because its route is UNRULED -- a chi_eff-dependent row reports
    NOT_EVALUABLE rather than picking a side.
    """
    try:
        computed = identity.evaluate(b3, b2, chi_eff)
    except Exception as exc:                  # a broken row is data too
        return {
            "identity": identity.id,
            "claim": identity.claim,
            "computed": None,
            "claimed": identity.claimed,
            "status": "ERROR",
            "detail": "%s: %s" % (type(exc).__name__, exc),
        }
    return {
        "identity": identity.id,
        "claim": identity.claim,
        "computed": computed,
        "claimed": identity.claimed,
        "status": _status(computed, identity.claimed),
    }


def evaluate_all(b3: int, b2: int,
                 chi_eff: Optional[float] = None) -> List[Dict[str, Any]]:
    """Every identity evaluated in one fork state, ordered by id."""
    return [evaluate_identity(row, b3, b2, chi_eff)
            for row in sorted(IDENTITIES, key=lambda r: r.id)]


def identity_report(chi_eff: Optional[float] = None) -> Dict[str, Any]:
    """The full per-branch matrix: every identity against every b3_seed path.

    Reads the seed family from `b3_path.PATHS`, which is GENERATED from the
    reachability relation, so a new reachable profile appears here without
    being added by hand.
    """
    from metaphysica.simulations.PM.geometry.b3_path import (
        PATHS,
        resolve_path,
        seed_values,
    )

    adopted = resolve_path()
    branches = sorted(PATHS)

    rows: List[Dict[str, Any]] = []
    for identity in sorted(IDENTITIES, key=lambda r: r.id):
        per_branch: Dict[str, Any] = {}
        for path in branches:
            b3, b2 = seed_values(path)[:2]
            per_branch[path] = evaluate_identity(identity, b3, b2, chi_eff)
        rows.append({
            "identity": identity.id,
            "claim": identity.claim,
            "counts": identity.counts,
            "claimed": identity.claimed,
            "source": identity.source,
            "chi_eff_dependent": identity.chi_eff_dependent,
            "per_branch": per_branch,
            "status_on_adopted": per_branch[adopted]["status"],
            "branches_holding": sorted(
                p for p in branches if per_branch[p]["status"] == "HOLDS"),
        })

    holds_on_adopted = [r["identity"] for r in rows
                        if r["status_on_adopted"] == "HOLDS"]
    broken_on_adopted = [r["identity"] for r in rows
                         if r["status_on_adopted"] == "BROKEN"]

    return {
        "generator": "identity_ledger",
        "adopted_branch": adopted,
        "branches": branches,
        "chi_eff_supplied": chi_eff,
        "n_identities": len(rows),
        "identities": rows,
        "holds_on_adopted": sorted(holds_on_adopted),
        "broken_on_adopted": sorted(broken_on_adopted),
        "ordering": "identity id; never by how many branches an identity survives",
        "verdict": "NO_SELECTION_MADE",
        "note": (
            "A broken identity is a recorded cost of the b3_seed ruling, not "
            "evidence against it. Branch columns are reported, never ranked."
        ),
    }


def write_report(out_path=None) -> Dict[str, Any]:
    """Emit ``AutoGenerated/identity_ledger.json`` and return the payload."""
    from metaphysica.generators._common import autogen_dir, write_json_stable

    payload = identity_report()
    path = out_path or (autogen_dir() / "identity_ledger.json")
    write_json_stable(path, payload)
    return payload


def main(argv=None) -> int:
    """CLI entry point: write the ledger and print the adopted-branch summary."""
    payload = write_report()
    print("identity ledger: %d identities, adopted branch %s"
          % (payload["n_identities"], payload["adopted_branch"]))
    print("  HOLDS  on adopted: %d" % len(payload["holds_on_adopted"]))
    print("  BROKEN on adopted: %d" % len(payload["broken_on_adopted"]))
    for row in payload["identities"]:
        print("  %-8s %-44s %s"
              % (row["status_on_adopted"], row["claim"],
                 ",".join(row["branches_holding"]) or "(no branch)"))
    return 0


if __name__ == "__main__":       # pragma: no cover - CLI
    raise SystemExit(main())
