"""The two b_3 paths, side by side, with honest derived-vs-input accounting.

WHY THERE ARE NOW TWO
=====================
derived_contribution_table settled the reachable Betti numbers of a Joyce
(Z/2)^3 resolution of T^7/Gamma, with Gamma the diagonal stabiliser of the
framework's own phi:

    b_3 = 7 + 3 n_T3,  n_T3 in {0, 4, 8, 12}   =>   b_3 in {7, 19, 31, 43}
    b_3 = 7 (mod 12),  and 24 = 0 (mod 12)

So b_3 = 24 is not reachable, and (12, 43) -- which IS reachable -- is also the
Betti pair of Joyce's canonical published example, reproduced by machinery that
was never told it.

That leaves two live paths, and this module runs both:

  seed_24        b_3 = 24 as an INPUT, its origin open. The status quo.
  seed_43_joyce  b_3 = 43, b_2 = 12, DERIVED from the resolution count.

WHAT THE 43 PATH BUYS, AND IT IS THE POINT
==========================================
b_3 stops being an input. It becomes 7 + 3*12 where the 7 is the derived flat
contribution (joyce_orbifold R3) and the 12 is the derived count of A1 T^3
families. And b_2 = 12 arrives derived at the same time, from the same count.

The generation count survives, but MOVES. At b_3 = 24, n_gen = b_3/8 = 3. At
b_3 = 43 that fails -- 43/8 is not an integer, and a generation count is a
number of things. But b_2 = 12 is now available, and

    n_gen = b_2 / n_faces = 12 / 4 = 3

with n_faces = 4 derived as the moved coordinates of an involution (R2). So the
43 path does not lose the three generations; it relocates their origin from
b_3 and dim O to b_2 and the faces, and both sides of that are derived.

WHAT IT COSTS, STATED PLAINLY
=============================
  w_0 = -(b_3-1)/b_3 moves from -0.958333 to -0.976744, i.e. from 0.017 sigma
  to 0.94 sigma against the registry's DESI anchor. Worse agreement -- and
  derived rather than input, which is the trade the framework's own
  dark_energy_betti ruling already chose once, deliberately, "which is the
  point".

  The '+2' identity D_bulk - b_3 = 2 BREAKS: 26 - 43 = -17. Either D_bulk is
  not 26 on this path, or the identity was never structural. It is recorded as
  broken rather than quietly dropped, and a test asserts it.

  Everything with b_3 in it moves: the racetrack exponent 2pi/b_3, k_bary =
  b_3 - 14, chi/b_3, alpha_T. Those are consequences, not costs -- they follow
  from the seed whatever it is.

ADOPTED 2026-09-22, by author ruling: `b3_seed = seed_43_joyce`, so (b_2, b_3)
= (12, 43) is the default everywhere and `n_gen_source = b2_over_faces` with
it. This paragraph previously read "NOT ADOPTED. seed_24 remains the adopted
branch so no published number moves until the author rules" -- written before
the ruling and left standing after it, so the module's own explanation
asserted the opposite of what it does. seed_24 stays RUNNABLE via
METAPHYSICA_VARIANT_B3_SEED=seed_24 and stays LABELLED unreachable; keeping it
is the point, and so is not pretending it is on the family.

AND THERE ARE NOT TWO PATHS. The section above says "two live paths" because
PATHS was two hand-written entries. It is now GENERATED from b_3 = 7 + 3 n_T3
over n_T3 in {0, 4, 8, 12}, so the reachable family is FOUR profiles -- b_3 in
{7, 19, 31, 43} -- plus the off-family seed_24, five in all. Only b_2 = 12
gives n_gen = b_2/4 = 3; the other three fail STRUCTURALLY at 0, 1 and 2
generations, which is a different kind of refutation from disagreeing with
data. See PATHS below for the generator and the measured selection.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "PATHS",
    "resolve_path",
    "seed_values",
    "downstream",
    "compare_paths",
    "n_gen_report",
]

#: path id -> (b_3, b_2, how each was obtained)
#: The Joyce-reachable family, GENERATED rather than listed.
#:
#: derived_contribution_table settles b_3 = 7 + 3 n_T3 with n_T3 in
#: {0, 4, 8, 12} over the admissible enumeration, and b_2 = n_T3 (one
#: exceptional 2-class per A1 family). That is FOUR profiles, and until
#: 2026-09-23 only two entries existed here -- so "n_gen = 3 selects
#: (12, 43) uniquely out of four candidates" was a claim about candidates
#: the pipeline could not run. Every profile is now executable, which turns
#: the selection argument into something the suite can CHECK rather than
#: restate: n_gen = b_2/4 gives 0, 1, 2, 3 across the family, and only the
#: last is three.
#:
#: Off-family entries (seed_24) stay declared by hand and LABELLED, because
#: the point of keeping them is that they are not reachable.
def _joyce_family() -> Dict[str, Dict[str, Any]]:
    """The reachable profiles, from the contribution table's own relation."""
    out: Dict[str, Dict[str, Any]] = {}
    for n_t3 in (0, 4, 8, 12):
        b3 = 7 + 3 * n_t3
        b2 = n_t3
        out["seed_%d_joyce" % b3] = {
            "b3": b3,
            "b2": b2,
            "b3_provenance": (
                "DERIVED: 7 flat (joyce_orbifold R3) + 3 x %d A1 families "
                "(derived_contribution_table, b_3 = 7 + 3 n_T3)" % n_t3
            ),
            "b2_provenance":
                "DERIVED: one exceptional 2-class per A1 family, %d" % b2,
            "n_gen_source": "b2_over_faces",
            "reachable_by_joyce": True,
            "n_t3": n_t3,
        }
    return out


PATHS: Dict[str, Dict[str, Any]] = {
    "seed_24": {
        "b3": 24,
        "b2": 4,
        "b3_provenance": "INPUT, origin open (2026-09-14 ruling)",
        "b2_provenance": "h^{1,1} of TCS #187, previously FITTED",
        "n_gen_source": "b3_over_dim_O",
        "reachable_by_joyce": False,
    },
}
PATHS.update(_joyce_family())

#: Back-compatible alias: the adopted profile was named before the family
#: was generated, and the register, the forks and every override that users
#: have typed say `seed_43_joyce`. The generator produces the same key, so
#: this is an assertion that the naming did not drift, not a remapping.
assert "seed_43_joyce" in PATHS, "the generated family lost the adopted key"


def resolve_path() -> str:
    """Which path is in force. ADOPTED: seed_43_joyce, author ruling 2026-09-22.

    The author directed that the active path match the found solution:
    (12, 43), selected by n_gen = rank(Gamma) = 3 with b_3 = 7 + 3 b_2.
    seed_24 stays runnable as the labelled off-path branch via the override.

    Narrowed from `except Exception` on 2026-09-22. This is the most widely
    consumed fork read in the geometry tree -- `seed_values`, `n_gen_report`
    and `geometry_narration.betti_claim` all route through it -- so a
    swallowed KeyError or ValueError here would put the ADOPTED seed under
    every downstream number while an override said otherwise, which is the
    worst possible place for a silent default. Only the import cycle is
    tolerated, and its fallback must MATCH the adopted branch.
    """
    try:
        from metaphysica.simulations.core.variants import resolve
    except ImportError:                    # import cycle: the one real case
        return "seed_43_joyce"
    return resolve("b3_seed")


def seed_values(path: Optional[str] = None) -> Tuple[int, int]:
    """(b_3, b_2) for a path."""
    spec = PATHS[path or resolve_path()]
    return spec["b3"], spec["b2"]


def _registry(path: str):
    """One registry row's value, or None when the artifact or row is absent.

    The lookup used to be open-coded here as a CWD-relative
    `AutoGenerated/parameters.json` plus an absolute path from the author's
    machine, so off that machine and outside the repository root it returned
    None and every cross-check it fed was silently skipped. It now goes through
    `parameter_artifact`, which is the single resolver -- `free_set` carried a
    second, differently-broken copy of the same lookup.
    """
    from metaphysica.simulations.core.parameter_artifact import parameter_value

    return parameter_value(path)


def n_gen_report(path: Optional[str] = None) -> Dict[str, Any]:
    """Where three generations come from on this path, and whether it holds.

    A generation count must be a positive integer -- that is structural and
    references no measurement, which is why it is the decisive discriminator
    between the paths rather than w_0.
    """
    key = path or resolve_path()
    b3, b2 = seed_values(key)
    n_faces = 4                      # derived: moved coordinates of an involution
    dim_o = 8                        # dim of the octonions

    from_b3 = b3 / dim_o
    from_b2 = b2 / n_faces

    # The n_gen_source fork was INERT: this line read PATHS[key]["n_gen_source"]
    # and nothing ever called resolve("n_gen_source"), so the fork was slaved to
    # b3_seed and could not select anything. That also made the coupling between
    # the two forks unfalsifiable -- no inconsistent state was reachable, so a
    # guard against one could not fire, and a check that cannot fire is a defect.
    #
    # The fork is now live, with the path's own declaration as the default. An
    # EXPLICIT override selects the other source, which makes the inconsistent
    # combination reachable and therefore checkable: seed_43_joyce with
    # b3_over_dim_O gives 43/8 = 5.375, not a generation count.
    declared = PATHS[key]["n_gen_source"]
    try:
        from metaphysica.simulations.core.variants import _ENV_PREFIX, resolve
    except ImportError:                    # import cycle: the one real case
        pass
    else:
        # Narrowed from `except Exception` on 2026-09-22. The override is the
        # whole point of this block -- it is what makes the inconsistent
        # combination reachable and therefore checkable -- so a fork that has
        # been renamed or an option that does not exist must NOT leave the
        # declaration silently in place while the environment says otherwise.
        # resolve() raises KeyError for an undeclared fork and ValueError for
        # an unknown option, and both now surface.
        if os.environ.get(_ENV_PREFIX + "N_GEN_SOURCE"):
            declared = resolve("n_gen_source")

    value = from_b3 if declared == "b3_over_dim_O" else from_b2

    def integral(x: float) -> bool:
        return abs(x - round(x)) < 1e-12

    return {
        "path": key,
        "declared_source": declared,
        "n_gen": value,
        "is_integer": integral(value),
        "equals_three": integral(value) and round(value) == 3,
        "b3_over_dim_O": {"value": from_b3, "integer": integral(from_b3),
                          "formula": "b_3 / 8, the 8 being dim O"},
        "b2_over_faces": {"value": from_b2, "integer": integral(from_b2),
                          "formula": "b_2 / 4, the 4 being the faces (R2)"},
        "why_this_decides": (
            "a generation count is a number of things, so integrality is a "
            "structural constraint referencing no measurement -- unlike w_0, "
            "which cannot discriminate (it moves 0.0017 per unit b_3)"
        ),
    }


def downstream(path: Optional[str] = None) -> Dict[str, Any]:
    """Every registered relation that consumes the seed, on this path."""
    key = path or resolve_path()
    b3, b2 = seed_values(key)
    d_bulk = _registry("dimensions.D_bulk")
    chi = _registry("topology.mephorash_chi")
    w0_obs = _registry("geometry.w0_observed_DESI")
    w0_err = _registry("geometry.w0_error_DESI")

    w0 = -(b3 - 1) / b3
    gen = n_gen_report(key)
    out: Dict[str, Any] = {
        "path": key,
        "b3": b3,
        "b2": b2,
        "b3_provenance": PATHS[key]["b3_provenance"],
        "b2_provenance": PATHS[key]["b2_provenance"],
        "reachable_by_joyce": PATHS[key]["reachable_by_joyce"],
        "w0": w0,
        "w0_formula": "-(b_3 - 1)/b_3",
        "n_gen": gen["n_gen"],
        "n_gen_source": gen["declared_source"],
        "n_gen_holds": gen["equals_three"],
        "racetrack_exponent": 2.0 * math.pi / b3,
        "k_bary_cycles": b3 - 14,
        "wa_thawing": -4.0 / math.sqrt(b3),
    }
    if w0_obs is not None and w0_err:
        out["w0_sigma_vs_desi"] = abs(w0 - w0_obs) / w0_err
        # NAME THE ANCHOR. This module's docstring quotes "0.94 sigma against
        # the registry's DESI anchor" as the adopted path's cost, as though the
        # framework had one anchor for w_0. It has at least three, and the same
        # prediction scores very differently against them:
        #
        #   geometry.w0_observed_DESI  -0.958 +/- 0.02   -> 0.937 sigma  (here)
        #   desi.w0                    -0.957 +/- 0.067  -> 0.295 sigma
        #   desi.w0_thawing            -0.957 +/- 0.33   -> 0.060 sigma
        #
        # established.py declares desi.w0 the PRIMARY scoring anchor (the DR2
        # headline), and cosmology_sector_complete, dark_energy_thawing and
        # established itself all cite that. This module scores against the
        # geometry.* pair instead -- the tightest of the three, so it reports
        # the cost as WORSE than the primary anchor gives, which is the safe
        # direction to be wrong in but still an undeclared choice.
        #
        # The number is unchanged. What is added is which anchor produced it
        # and what the declared primary anchor gives, so a reader cannot take
        # one sigma for the sigma. Choosing a single anchor for w_0 is the
        # AUTHOR'S ruling; publishing both is not.
        out["w0_sigma_anchor"] = "geometry.w0_observed_DESI +/- geometry.w0_error_DESI"
        out["w0_sigma_anchor_is_primary"] = False
        # Read the uncertainty from its registered row rather than typing it:
        # there is no desi.w0_sigma row, the value lives at
        # abstract.desi_w0_uncertainty, and a literal here would be the very
        # ghost literal this file's campaign exists to remove. No row means no
        # comparison, which is the honest outcome.
        primary_obs = _registry("desi.w0")
        primary_err = _registry("abstract.desi_w0_uncertainty")
        if primary_obs is not None and primary_err:
            out["w0_sigma_vs_primary_anchor"] = abs(w0 - primary_obs) / primary_err
            out["w0_primary_anchor"] = "desi.w0 (established.py: primary scoring anchor)"
    if chi:
        out["chi_over_b3"] = chi / b3
    if d_bulk:
        gap = d_bulk - b3
        out["d_bulk_minus_b3"] = gap
        out["plus_two_identity_holds"] = abs(gap - 2) < 1e-9
        if not out["plus_two_identity_holds"]:
            out["plus_two_identity_note"] = (
                "BROKEN on this path: D_bulk - b_3 = %g, not 2. Either D_bulk "
                "is not %g here, or the identity was never structural. "
                "Recorded, not dropped." % (gap, d_bulk)
            )
    return out


def narration(path: Optional[str] = None) -> Dict[str, str]:
    """Paper wording generated FROM the active path, not hardcoded.

    The appendices narrated "b3 = 24 from TCS #187 yields exactly 3
    generations". Two things are wrong with that sentence and both are fixed by
    generating it:

      * the TCS provenance is false. fano_tcs exhibits 71 <= b_3 <= 155, so it
        does not supply 24 at all -- the register has carried that exclusion
        for several passes while the paper kept citing it.
      * it hardcodes the seed, so the text cannot follow a ruling.

    Every string here is built from the path's own values, so switching
    b3_seed rewrites the paper's claim instead of contradicting it.
    """
    key = path or resolve_path()
    b3, b2 = seed_values(key)
    gen = n_gen_report(key)
    n_faces, dim_o = 4, 8

    if gen["declared_source"] == "b3_over_dim_O":
        gen_sentence = (
            "n_gen = b_3 / %d = %d / %d = %g" % (dim_o, b3, dim_o, gen["n_gen"])
        )
        gen_basis = "the %d being dim O" % dim_o
    else:
        gen_sentence = (
            "n_gen = b_2 / %d = %d / %d = %g" % (n_faces, b2, n_faces,
                                                 gen["n_gen"])
        )
        gen_basis = (
            "the %d being the faces, derived as the moved coordinates of an "
            "involution" % n_faces
        )

    if key == "seed_43_joyce":
        seed_sentence = (
            "b_3 = %d and b_2 = %d are DERIVED from the resolution of "
            "T^7/(Z/2)^3: b_3 = 7 flat invariants + 3 x %d A1 families, and "
            "b_2 = %d from one exceptional 2-class per family. The pair "
            "(%d, %d) is Joyce's canonical example."
            % (b3, b2, b2, b2, b2, b3)
        )
    else:
        seed_sentence = (
            "b_3 = %d is an INPUT whose origin is open. It is NOT supplied by "
            "TCS #187, which exhibits 71 <= b_3 <= 155, and it is not "
            "reachable by a Joyce (Z/2)^3 resolution, which reaches only "
            "b_3 = 7 (mod 12). b_2 = %d traces to a previously fitted h^{1,1}."
            % (b3, b2)
        )

    return {
        "path": key,
        "seed_sentence": seed_sentence,
        "n_gen_sentence": gen_sentence,
        "n_gen_basis": gen_basis,
        "n_gen_assertion": "Fermion generation count %s (exact)" % gen_sentence,
        "n_gen_condition": "%s, %s" % (gen_sentence, gen_basis),
        "provenance_correction": (
            "Earlier wording attributed b_3 = 24 to TCS #187. That is false: "
            "fano_tcs exhibits 71 <= b_3 <= 155. Corrected here."
        ),
    }


def compare_paths() -> Dict[str, Any]:
    """Both paths side by side. Reports; does not choose.

    Per variants.py's standing rule this never orders by agreement with
    experiment. The one discriminator applied is structural: whether the
    generation count is an integer.
    """
    rows = [downstream(key) for key in sorted(PATHS)]
    structural_pass = [r["path"] for r in rows if r["n_gen_holds"]]
    return {
        "rows": rows,
        "ordering": "path id; never by agreement with experiment",
        "structural_discriminator": (
            "n_gen must be a positive integer. This references no measurement."
        ),
        "paths_passing_structural": structural_pass,
        "both_pass_structurally": len(structural_pass) == len(rows),
        # Sharper framing, available since the whole reachable family became
        # runnable (2026-09-23). The structural discriminator DOES select
        # now -- it eliminates the family members giving 0, 1 and 2
        # generations -- but it does not separate the two candidates that
        # both give three. Those are separated by REACHABILITY instead:
        # seed_24 fails b_3 = 7 + 3 b_2, b_3 = 7 (mod 12) and the TCS range.
        # Two independent criteria, and together they are unique.
        "reachable_paths_passing_structural": sorted(
            p for p in structural_pass
            if PATHS[p].get("reachable_by_joyce")),
        "structural_test_is_decisive_within_the_family": (
            len([p for p in structural_pass
                 if PATHS[p].get("reachable_by_joyce")]) == 1),
        "what_separates_the_two_that_pass": (
            "REACHABILITY, not the generation count: seed_24 also gives "
            "three (24/8) but fails b_3 = 7 + 3 b_2, b_3 = 7 (mod 12) and "
            "the exhibited TCS range, so it is not on the family at all. "
            "The generation count selects WITHIN the family; reachability "
            "excludes the off-family candidate. Neither criterion "
            "references a measurement."
        ),
        "note_on_w0": (
            "w_0 residuals are reported per row because hiding them would be "
            "its own dishonesty, but they order nothing: w_0 moves only 0.0017 "
            "per unit b_3 and cannot discriminate."
        ),
        "verdict": "NO_SELECTION_MADE",
        "what_the_author_is_ruling_on": (
            "seed_24 keeps the better w_0 and an INPUT b_3 whose origin has no "
            "geometric home left among the declared constructions. "
            "seed_43_joyce derives b_3 AND b_2 from the resolution count, "
            "reproduces Joyce's canonical published pair, relocates the "
            "generation count from b_3/8 to b_2/4 (still exactly 3), and pays "
            "for it with w_0 at ~0.94 sigma and a broken +2 identity."
        ),
    }
