"""What would have to exist before a Yukawa could be computed. A SPECIFICATION.

THIS MODULE COMPUTES NO PHYSICS AND MUST NOT
============================================
It produces no wavefunction, no overlap integral and no Yukawa number. Every
function here returns a DESCRIPTION of a missing object: what it is, what it
would have to be computed against, and what in the framework already exists to
supply its inputs. Inventing any of it would manufacture exactly the object
the FLAVOUR layer is blocked on, and the blockage is the finding.

WHY THE FLAVOUR LAYER IS BLOCKED
================================
`closure_ledger` puts 13 rows in FLAVOUR -- mixing angles, mass ratios and
Yukawa-sector quantities. Each needs an overlap integral of zero modes, which
needs three things at once:

    the METRIC            leading-order-in-t only (metric_pairing gives K_IJ
                          with values; the exact Joyce metric does not exist)
    the SINGULAR LOCUS    EXISTS -- 12 A_1 families, enumerated and measured
    the WAVEFUNCTIONS     DO NOT EXIST AT ALL

Two of three is not two thirds of the way: the wavefunctions are where the
physics lives.

THE PRECISE MISSING OBJECT, FROM THE 2026-09-22 ADJUDICATION
============================================================
It is sharper than "wavefunctions are hard", and the sharpening is the useful
part of this spec.

1. **The enumerated loci are 3-dimensional A_1 families** -- T^3 x (EH neck),
   codimension 4 in Y_7. In M-theory on a G_2 manifold, a codimension-4 A_1
   singularity along a 3-manifold gives **GAUGE ENHANCEMENT**: non-abelian
   vector multiplets on the locus. It does NOT give chiral matter.

2. **Chiral matter needs codimension-7 CONICAL points** -- isolated points
   where the singularity type jumps, at which chiral fermions localise. **The
   enumeration contains NONE.** Every admissible assignment yields T^3 families
   and nothing of codimension 7.

3. **Intersection-localised couplings are unavailable at every admissible
   assignment.** `half_shift_enumeration.fixed_sets_disjoint` IS the
   admissibility predicate: an assignment is admissible exactly when the fixed
   sets of distinct involutions are pairwise DISJOINT. So pairwise
   intersections are empty everywhere Joyce applies, and triple intersections
   are empty a fortiori. A Yukawa from three loci meeting at a point has no
   point to live on -- not at the canonical point, not anywhere.

So the missing object is not a wavefunction. It is a **codimension-7 conical
point**, and the construction as enumerated does not produce one. Any route to
Yukawas from this geometry must first exhibit one, and exhibiting one means
leaving the admissible stratum or deforming beyond Joyce's resolution.

WHAT A SPEC IS FOR
==================
So that the next attempt starts from the missing object rather than rediscovering
the blockage, and so that a partial implementation cannot be mistaken for
progress: every item below carries `exists_today`, and the honest total is the
count of False.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "required_structures",
    "missing_objects",
    "locus_codimension_report",
    "why_intersection_couplings_are_unavailable",
    "spec_report",
]


def required_structures() -> List[Dict[str, Any]]:
    """Every structure an overlap integral needs, and whether it exists today.

    Ordered from the geometry outward. `exists_today` is the only field that
    matters for the blockage; the rest says what the object IS so the next pass
    does not have to re-derive the question.
    """
    return [
        {
            "name": "the G2 metric on Y_7",
            "what": ("a Riemannian metric with holonomy in the compact G2, "
                     "needed to define the Dirac operator and the L^2 inner "
                     "product the overlap integral is taken in"),
            "computed_against": ("Joyce's existence theorem for resolutions of "
                                 "T^7/Gamma; the metric is not known in closed "
                                 "form for any such resolution"),
            "framework_has": ("K_IJ at LEADING ORDER IN T, with values "
                              "(metric_pairing), diagonal, depending on L only"),
            "exists_today": "PARTIAL",
            "gap": ("leading-order only. The O(t^2) cross-blocks are reported "
                    "as an order, not a value, and the exact metric does not "
                    "exist"),
        },
        {
            "name": "the singular locus",
            "what": ("the fixed loci of the singular involutions: 12 A_1 "
                     "families, each T^3 x (Eguchi-Hanson neck)"),
            "computed_against": ("the live half-shift enumeration; measured, "
                                 "not assumed"),
            "framework_has": ("intersection_tensor.sector_families -- 12 "
                              "families in 3 sectors, 16 fixed T^3 on the "
                              "cover per singular involution"),
            "exists_today": True,
            "gap": None,
        },
        {
            "name": "the gauge bundle on the locus",
            "what": ("the ADE gauge bundle carried by the codimension-4 "
                     "singularity. For A_1 this is an SU(2) bundle; the matter "
                     "would sit in a representation of it"),
            "computed_against": ("the resolution data: the exceptional "
                                 "2-classes and their intersection form, which "
                                 "eguchi_hanson and intersection_tensor supply"),
            "framework_has": ("the exceptional 2-form eta, its self-intersection "
                              "-2, and the 12x12x43 integer tensor"),
            "exists_today": "PARTIAL",
            "gap": ("the classes exist; no bundle, connection or "
                    "representation assignment has been constructed on them"),
        },
        {
            "name": "codimension-7 conical points",
            "what": ("isolated points where the singularity type jumps. In "
                     "M-theory on G2 these are where CHIRAL matter localises; "
                     "codimension-4 families give gauge enhancement only"),
            "computed_against": ("the enumeration of fixed loci across "
                                 "admissible assignments"),
            "framework_has": "NOTHING -- the enumeration contains none",
            "exists_today": False,
            "gap": ("THE PRECISE MISSING OBJECT. Without one there is no "
                    "chiral matter to write a Yukawa for, whatever else is "
                    "built"),
        },
        {
            "name": "the Dirac operator",
            "what": ("the twisted Dirac operator on Y_7 coupled to the gauge "
                     "bundle, whose kernel is the zero-mode space"),
            "computed_against": ("the metric and the bundle above -- it cannot "
                                 "be written before either exists"),
            "framework_has": ("g2_differential builds a Hodge star, torsion "
                              "classes and curvature from phi, but no spinor "
                              "bundle and no Dirac operator"),
            "exists_today": False,
            "gap": "needs the metric and the bundle first",
        },
        {
            "name": "boundary conditions on the Eguchi-Hanson neck",
            "what": ("normalisability at the ALE end and regularity at the "
                     "bolt. A mode must be L^2 on the neck and smooth at "
                     "r = a, where f^2 = 1 - (a/r)^4 vanishes"),
            "computed_against": ("the EH metric, which DOES exist in closed "
                                 "form and is Ricci-flat as an exact symbolic "
                                 "zero -- so this is the one item that could be "
                                 "specified concretely today"),
            "framework_has": ("eguchi_hanson.metric_matrix, the ALE decay "
                              "measurement (-4.000087), and the normalisable "
                              "2-form eta with ||eta||^2 = 8 pi^2"),
            "exists_today": "SPECIFIABLE",
            "gap": ("no mode has been solved for; only the ambient conditions "
                    "a mode would have to satisfy are available"),
        },
        {
            "name": "the zero-mode wavefunctions",
            "what": ("normalisable solutions of the Dirac equation localised "
                     "on the singular locus, one per chiral generation"),
            "computed_against": "the Dirac operator and the boundary conditions",
            "framework_has": "NOTHING",
            "exists_today": False,
            "gap": "do not exist at all",
        },
        {
            "name": "the overlap integral",
            "what": ("Y_ijk = integral over Y_7 of psi_i psi_j psi_k times the "
                     "appropriate volume form, giving the Yukawa coupling"),
            "computed_against": "three wavefunctions and the metric",
            "framework_has": "NOTHING",
            "exists_today": False,
            "gap": ("every input is missing; and on this geometry the "
                    "intersection-localised form of it is unavailable in "
                    "principle -- see why_intersection_couplings_are_unavailable"),
        },
    ]


def locus_codimension_report() -> Dict[str, Any]:
    """What codimension the enumerated loci actually have, measured.

    The A4 bar matters here: codimension is a DIMENSION, the 12 is a count of
    FAMILIES, and the 3 is a count of COORDINATE DIRECTIONS in the fixed line.
    """
    from metaphysica.simulations.PM.geometry.intersection_tensor import (
        sector_families,
    )

    families = sector_families()
    fixed_dims = {len(fam["fixed_line"]) for fam in families}
    moved_dims = {len(fam["moved_arc"]) for fam in families}

    if len(fixed_dims) != 1 or len(moved_dims) != 1:
        raise RuntimeError(
            "the families no longer share a fixed/moved split: %s / %s"
            % (sorted(fixed_dims), sorted(moved_dims)))

    fixed = fixed_dims.pop()
    moved = moved_dims.pop()

    return {
        "n_families": len(families),
        "locus_dimension": fixed,
        "codimension": moved,
        "ambient_dimension": fixed + moved,
        "gives": "GAUGE_ENHANCEMENT",
        "does_not_give": "CHIRAL_MATTER",
        "chiral_matter_needs_codimension": 7,
        "n_codimension_7_points_in_the_enumeration": 0,
        "counts_what": ("locus_dimension and codimension are DIMENSIONS; "
                        "n_families counts ORBITS of fixed-locus components"),
        "why": (
            "a codimension-4 A_1 singularity along a 3-manifold gives "
            "non-abelian vector multiplets on that 3-manifold. Chiral fermions "
            "in M-theory on G2 localise at codimension-7 CONICAL points, of "
            "which the enumeration contains none."
        ),
    }


def why_intersection_couplings_are_unavailable() -> Dict[str, Any]:
    """Disjointness is the admissibility predicate, so intersections are empty.

    Not a statement about the canonical point: it holds at EVERY admissible
    assignment, because it is what admissibility means.
    """
    return {
        "predicate": "half_shift_enumeration.fixed_sets_disjoint",
        "statement": (
            "an assignment is admissible exactly when the fixed sets of "
            "distinct singular involutions are pairwise DISJOINT -- that "
            "disjointness is what makes Joyce's family-by-family resolution "
            "work"
        ),
        "consequence_pairwise": "empty at every admissible assignment",
        "consequence_triple": "empty a fortiori",
        "so": (
            "a Yukawa from three singular loci meeting at a point has no point "
            "to live on anywhere Joyce applies. This is not a gap to be filled "
            "by more computation; it is excluded by the construction."
        ),
        "scope": (
            "the exclusion is of INTERSECTION-LOCALISED couplings specifically. "
            "It says nothing about couplings from a mechanism that does not "
            "need intersecting loci -- but such a mechanism still needs the "
            "codimension-7 points, which are also absent."
        ),
    }


def missing_objects() -> List[Dict[str, Any]]:
    """Only the structures that do not exist at all. The honest blocker list."""
    return [item for item in required_structures()
            if item["exists_today"] is False]


def spec_report() -> Dict[str, Any]:
    """The specification, with the blockage stated where it actually is."""
    structures = required_structures()
    missing = missing_objects()
    codim = locus_codimension_report()
    disjoint = why_intersection_couplings_are_unavailable()

    from metaphysica.simulations.core.closure_ledger import closure_ledger

    flavour_rows = [r["name"] for r in closure_ledger()
                    if r["layer"] == "FLAVOUR"]

    return {
        "this_is_a_specification": True,
        "produces_no_yukawa": True,
        "n_structures_required": len(structures),
        "n_missing_entirely": len(missing),
        "n_partial": len([s for s in structures
                          if s["exists_today"] in ("PARTIAL", "SPECIFIABLE")]),
        "n_present": len([s for s in structures if s["exists_today"] is True]),
        "structures": structures,
        "missing": [m["name"] for m in missing],
        "locus": codim,
        "disjointness": disjoint,
        "flavour_rows_blocked": flavour_rows,
        "n_flavour_rows_blocked": len(flavour_rows),
        "the_precise_missing_object": (
            "a codimension-7 CONICAL point. The enumerated loci are "
            "3-dimensional A_1 families of codimension 4, which give gauge "
            "enhancement and not chirality, and the enumeration contains no "
            "codimension-7 point at any admissible assignment. Everything "
            "downstream -- Dirac operator, wavefunctions, overlap integral -- "
            "is blocked behind it, and the disjointness result independently "
            "removes the intersection-localised route."
        ),
        "what_could_be_done_today": (
            "the boundary conditions on the Eguchi-Hanson neck are the one "
            "item that is SPECIFIABLE now: the EH metric exists in closed form "
            "and is Ricci-flat as an exact symbolic zero, so normalisability "
            "at the ALE end and regularity at the bolt can be written down "
            "precisely. That is a real piece of work and it does not unblock a "
            "single FLAVOUR row on its own."
        ),
        "what_must_not_be_done": (
            "fabricating a wavefunction, or producing a Yukawa number from a "
            "geometry that has no chiral matter in it. A number here would be "
            "unfalsifiable and would retire %d ledger rows for no reason."
            % len(flavour_rows)
        ),
    }
