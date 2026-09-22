"""Codimension-7 conical points DO exist in the Joyce shift family. Measured.

THE QUESTION, AND WHY IT MATTERS
================================
Flavour is blocked on a named missing object: chiral matter in M-theory on a
G2 space needs codimension-7 CONICAL singularities, and the A1-admissible
enumeration provably has none -- fixed sets of involutions are 3-dimensional
tori, and admissibility IS their pairwise disjointness. The Wilson-line dock
closed too (pi_1 = 1). So the only known chiral mechanisms were dead ON THE
ADMISSIBLE BRANCH. This module asks the next question: do conical points
exist ANYWHERE in the (Z/2)^3 shift family, admissible or not?

THE CRITERION (exact, finite)
=============================
A point of T^7 fixed by the WHOLE group has transverse cone R^7/(Z/2)^3 --
codimension 7. Such a point exists iff
  (a) every non-identity element is non-free: its shift is integral on every
      coordinate it fixes (composite shifts are DERIVED via the cocycle
      s_{gd} = s_g + g s_d, so this constrains the 2^21 generator-shift
      space, not 7 independent choices); and
  (b) on each coordinate, the four elements flipping it agree on their shift
      component there (their half-integer fixed loci must intersect).

MEASURED 2026-09-22 (this module's report recomputes it live):
  2,097,152 generator-shift assignments scanned; 128 admit a full-group
  fixed point. The zero-shift assignment (the maximally singular orbifold)
  is one of them.

WHAT THIS DOES AND DOES NOT SAY -- the A4 bar, sharpened
========================================================
DOES say: the Joyce shift family CONTAINS codimension-7 conical candidates.
The flavour dock is not structurally absent from the family; it is absent
from the A1-ADMISSIBLE branch, which is where (12, 43) lives.

Does NOT say:
  * that any of the 128 is compatible with the adopted topology -- all-7-
    singular forces massively intersecting fixed sets, the opposite of
    admissibility, so these assignments are NOT A1-resolvable and their
    smooth-resolution question is OPEN mathematics (the order-2-but-
    intersecting analogue of the non-A1 wall the register already records);
  * that R^7/(Z/2)^3 is a chirality-supporting cone -- which cones carry
    chiral states is its own M-theory question, and no fermion is produced
    here;
  * that a path exists from (12, 43) to any of the 128 -- they are different
    points of the assignment moduli, and connecting them (partial smoothing,
    deformation) is a further open question.

The honest statement: the boundary of the theory moved from "the framework's
family has no conical points" to "the framework's family has 128 conical
assignments whose resolution physics is open" -- a smaller, sharper wall.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from itertools import product
from typing import Any, Dict, List, Sequence, Tuple

__all__ = [
    "compose_all_elements",
    "full_group_fixed_points",
    "conical_assignment_survey",
    "conical_report",
]

_GENS = ((0, 0, 1), (0, 1, 0), (1, 0, 0))


def _generator_signs() -> List[Tuple[int, ...]]:
    from metaphysica.simulations.PM.geometry.intersection_tensor import (
        canonical_point,
    )

    elements = {tuple(k): v
                for k, v in canonical_point()["elements"].items()}
    return [elements[g][0] for g in _GENS]


def compose_all_elements(shifts3: Sequence[Sequence[int]]
                         ) -> Dict[Tuple[int, ...], Tuple[Tuple[int, ...],
                                                          Tuple[int, ...]]]:
    """All 7 non-identity (signs, shift) with DERIVED composite shifts.

    Shifts are in half-units (1 means 1/2); composites follow the cocycle,
    never chosen independently -- 2^21 assignments, not 2^49.
    """
    gen_signs = _generator_signs()
    out = {}
    for bits in product((0, 1), repeat=3):
        if bits == (0, 0, 0):
            continue
        signs = [1] * 7
        shift = [0] * 7
        for idx in (0, 1, 2):
            if bits[idx]:
                shift = [(gen_signs[idx][i] * shift[i]
                          + shifts3[idx][i]) % 2 for i in range(7)]
                signs = [gen_signs[idx][i] * signs[i] for i in range(7)]
        out[bits] = (tuple(signs), tuple(shift))
    return out


def full_group_fixed_points(shifts3: Sequence[Sequence[int]]) -> int:
    """Number of T^7 points fixed by the WHOLE group; 0 if none.

    Counts points, not orbits: each surviving coordinate constraint leaves 2
    half-integer solutions, so a hit contributes 2^7 = 128 points on the
    cover before any identification. Returned as the honest cover count.
    """
    els = compose_all_elements(shifts3)
    for signs, shift in els.values():
        for i in range(7):
            if signs[i] == 1 and shift[i] % 2 != 0:
                return 0
    for i in range(7):
        comps = {shift[i] for signs, shift in els.values()
                 if signs[i] == -1}
        if len(comps) > 1:
            return 0
    return 2 ** 7


def conical_assignment_survey() -> Dict[str, Any]:
    """Scan the full 2^21 generator-shift space for conical assignments."""
    gen_signs = _generator_signs()
    n_scanned = 0
    hits: List[Tuple[Tuple[int, ...], ...]] = []
    for s1 in product((0, 1), repeat=7):
        # generator 1 must itself be singular or no full fix exists
        if any(gen_signs[0][i] == 1 and s1[i] for i in range(7)):
            n_scanned += 2 ** 14
            continue
        for s2 in product((0, 1), repeat=7):
            if any(gen_signs[1][i] == 1 and s2[i] for i in range(7)):
                n_scanned += 2 ** 7
                continue
            for s3 in product((0, 1), repeat=7):
                n_scanned += 1
                if any(gen_signs[2][i] == 1 and s3[i] for i in range(7)):
                    continue
                if full_group_fixed_points((s1, s2, s3)):
                    hits.append((s1, s2, s3))
    return {
        "n_assignments_scanned": n_scanned,
        "n_conical_assignments": len(hits),
        "zero_shift_is_one_of_them": ((0,) * 7,) * 3 in
        [tuple(h) for h in hits],
        "examples": [tuple(h) for h in hits[:4]],
        "counts": (
            "assignments of generator shifts (composites derived by the "
            "cocycle). A hit means at least one T^7 point is fixed by the "
            "whole group; each hit carries 2^7 such points on the cover."
        ),
    }


def conical_report() -> Dict[str, Any]:
    """The boundary statement, computed live."""
    survey = conical_assignment_survey()
    return {
        **survey,
        "transverse_cone": "R^7/(Z/2)^3 -- codimension 7, conical",
        "on_the_admissible_branch": (
            "NONE: all-7-singular forces intersecting fixed sets, the "
            "opposite of A1-admissibility, so no conical assignment is "
            "A1-resolvable and none carries the (12, 43) topology"
        ),
        "what_remains_open": (
            "whether R^7/(Z/2)^3 cones support chiral states in M-theory; "
            "whether these orbifolds admit any G2 resolution or smoothing; "
            "whether a deformation connects the admissible branch to a "
            "conical assignment. Three separate questions, none answered "
            "here."
        ),
        "the_boundary_moved": (
            "from 'the family has no conical points' to 'the family has "
            "%d conical assignments whose resolution physics is open'"
            % survey["n_conical_assignments"]
        ),
    }
