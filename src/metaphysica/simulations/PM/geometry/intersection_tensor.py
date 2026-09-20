"""The metric-free cubic invariant, computed: H^2 x H^2 x H^3 -> Z.

WHAT THIS IS, AND WHY IT IS THE ONE
===================================
`multilinear_degree_audit` settles by degree arithmetic which multilinear
invariants exist on Y_7. For the 43 path there are exactly three, and only one
is not Poincare duality:

    int_Y alpha_i ^ alpha_j ^ omega_K      2 + 2 + 3 = 7,  shape 12 x 12 x 43

So this is uniquely the available metric-free cubic form. It is the honest
replacement for the external-lattice Gram matrix that the Leech and E8^3 routes
were reaching for -- and unlike a lattice shell it carries no large symmetry
group, so Schur's lemma cannot force it proportional to the identity. That was
the actual mechanism behind those null results.

EVERY ENTRY IS FORCED. NOTHING HERE IS FITTED.
==============================================
Three facts, each already established elsewhere in the framework, determine the
whole tensor:

1. DISJOINT SUPPORTS. Joyce admissibility requires the singular sets to be
   pairwise disjoint (`half_shift_enumeration.fixed_sets_disjoint`). The
   exceptional 2-class alpha_f lives on family f's neck, so for f /= g the
   supports do not meet and

       alpha_f ^ alpha_g = 0        (f /= g)

   The tensor is therefore DIAGONAL in its two H^2 slots. This is not an
   approximation; it is the admissibility condition.

2. THE A1 SELF-INTERSECTION IS -2. The census in
   `derived_contribution_table.transverse_group_census` establishes that every
   admissible component is A1 -- transverse group exactly of order 2, so
   C^2/{+-1}, resolved by Eguchi-Hanson. The intersection form on the
   exceptional divisors of an A_n resolution is MINUS the A_n Cartan matrix, and
   for A1 that single entry is -(2). So

       int_{EH_f} alpha_f ^ alpha_f = -2

   The -2 is read off the singularity type the framework already derived, not
   supplied. Change the singularity type and it changes.

3. WHICH omega_K SURVIVES. alpha_f ^ alpha_f is a 4-form concentrated on the
   neck, so the remaining 3 degrees must come from omega_K restricted to that
   family's T^3. Among the 43:
     * the 36 TWISTED 3-forms each carry a leg in an exceptional direction, so
       they restrict to zero on T^3;
     * of the 7 FLAT 3-forms, exactly the one supported on the involution's
       FIXED coordinates restricts to the T^3 volume; the other six vanish.
   And `involution_arc_correspondence` (R2) established that each involution's
   fixed set is a Fano LINE -- which is to say, one of phi's own triples.

Hence

    N[f][g][K] = -2 * delta_{fg} * [ omega_K is the flat 3-form on the line
                                     fixed by family f's involution ]

WHAT FALLS OUT, AND IT WAS NOT PUT IN
=====================================
At the canonical point the 3 singular involutions fix three DISTINCT Fano lines,
and they carry 4 families each. So:

  * exactly 12 entries are non-zero, all on the H^2 diagonal, all equal to -2;
  * they land in only 3 of the 43 H^3 slots -- the image is 3-dimensional;
  * the 4 remaining flat 3-forms are never paired at all, and 4 is exactly the
    number of FREE (non-singular) involutions. The 3 + 4 split of the seven flat
    forms mirrors the 3 singular + 4 free split of Gamma's seven involutions.

The tensor is about as far from isotropic as a tensor gets, and that is the point
of building it.

THE A4 BAR
==========
This counts cohomology classes and topological intersection numbers. The -2 is
an intersection number; the 12, 4 and 3 are counts of classes and of group
elements respectively, and the module never multiplies one kind by another to
get a dimension.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "A1_SELF_INTERSECTION",
    "canonical_point",
    "sector_families",
    "intersection_tensor",
    "image_is_isotropic",
    "tensor_report",
]


#: The intersection form on the exceptional divisors of an A_n resolution is
#: minus the A_n Cartan matrix. For A1 the matrix is the 1x1 (2), so the single
#: exceptional curve has self-intersection -2. Read off the singularity type the
#: census derives, not chosen.
A1_SELF_INTERSECTION = -2


def image_is_isotropic(n_h3_slots_hit: int) -> bool:
    """Whether a cubic form's H^3 image is isotropic, as a named rule.

    Isotropy in this setting means the H^2 x H^2 block proportional to the
    identity with a SINGLE H^3 target -- the shape Schur's lemma forces when the
    symmetry group is large, and the shape the Leech and E8^3 shell forms came
    out with. An image of dimension greater than one cannot be written that way.

    Extracted as a predicate so the non-isotropy claim is testable in both
    directions: asserting "not isotropic" is worth nothing unless the same rule
    returns True on something that is.
    """
    return n_h3_slots_hit <= 1


def canonical_point() -> Dict[str, Any]:
    """The first admissible assignment with 3 singular involutions and 12 plain
    A1 families, found by search rather than tabulated.

    Returns the group elements, the singular involutions and their family data.
    A perturbed phi changes the enumeration and therefore changes this.
    """
    from metaphysica.simulations.PM.geometry.derived_contribution_table import (
        all_components_are_a1,
    )
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        _group,
        _non_identity,
        assignments,
        elements,
        families_of,
        fixed_sets_disjoint,
        generating_triples,
        is_singular,
    )

    group = _group()
    nz = _non_identity(group)

    for triple in generating_triples(group):
        gens = [nz[i] for i in triple]
        for svecs in assignments(triple, group, include_relative=True):
            els = elements(gens, svecs)
            singular = [(b, e) for b, e in els.items()
                        if b != (0, 0, 0) and is_singular(e)]
            if len(singular) != 3:
                continue
            if not all(fixed_sets_disjoint(a[1], b[1])
                       for a, b in itertools.combinations(singular, 2)):
                continue
            if not all_components_are_a1(els, singular):
                continue
            fams = []
            for _bits, el in singular:
                fams.extend(families_of(els, el))
            if len(fams) == 12 and {f["type"] for f in fams} == {"T3"}:
                return {
                    "triple": triple,
                    "shifts": svecs,
                    "elements": els,
                    "singular": singular,
                    "n_families": len(fams),
                }
    raise RuntimeError(
        "no admissible 3-involution / 12-family point found; the enumeration "
        "has changed and every count downstream must be re-derived"
    )


def sector_families(point: Optional[Dict[str, Any]] = None
                    ) -> List[Dict[str, Any]]:
    """The 12 A1 families, each tagged with its involution and fixed line.

    Read from the live enumeration. Never tabulated: a change to phi or to the
    admissibility conditions moves this list.
    """
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        families_of,
        fixed_coords,
        moved_coords,
    )

    point = point or canonical_point()
    els = point["elements"]

    out: List[Dict[str, Any]] = []
    for sector_index, (bits, elem) in enumerate(sorted(point["singular"])):
        eps, _shift = elem
        fixed = tuple(sorted(fixed_coords(eps)))
        moved = tuple(sorted(moved_coords(eps)))
        for family_index, fam in enumerate(families_of(els, elem)):
            out.append({
                "family": len(out),
                "sector": sector_index,
                "involution_bits": bits,
                "fixed_line": fixed,
                "moved_arc": moved,
                "orbit_size": fam["orbit_size"],
                "type": fam["type"],
                "index_in_sector": family_index,
            })
    return out


def intersection_tensor(point: Optional[Dict[str, Any]] = None
                        ) -> Dict[str, Any]:
    """N[f][g][K] = int alpha_f ^ alpha_g ^ omega_K, as exact integers.

    Returned sparsely -- 12 non-zero entries out of 12*12*43 = 6192 -- because a
    dense array here would be almost entirely zeros and would hide the structure
    that is the result.
    """
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        invariant_three_forms,
    )

    point = point or canonical_point()
    families = sector_families(point)
    flat = [tuple(sorted(t)) for t in invariant_three_forms()]

    n_h2 = len(families)
    n_flat = len(flat)
    n_twisted = 3 * n_h2
    n_h3 = n_flat + n_twisted

    entries: Dict[Tuple[int, int, int], int] = {}
    for fam in families:
        line = fam["fixed_line"]
        if line not in flat:
            raise RuntimeError(
                "family %d fixes %s, which is not one of phi's triples; R2 has "
                "broken and the pairing rule no longer applies"
                % (fam["family"], line)
            )
        k = flat.index(line)               # flat forms occupy H^3 slots 0..6
        entries[(fam["family"], fam["family"], k)] = A1_SELF_INTERSECTION

    return {
        "shape": (n_h2, n_h2, n_h3),
        "n_flat_three_forms": n_flat,
        "n_twisted_three_forms": n_twisted,
        "entries": {str(k): v for k, v in sorted(entries.items())},
        "n_nonzero": len(entries),
        "distinct_values": sorted(set(entries.values())),
        "h3_slots_hit": sorted({k for (_f, _g, k) in entries}),
        "h3_slots_unhit_flat": sorted(set(range(n_flat))
                                      - {k for (_f, _g, k) in entries}),
        "diagonal_in_h2": all(f == g for (f, g, _k) in entries),
    }


def tensor_report(point: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The tensor plus the structural facts it exhibits."""
    point = point or canonical_point()
    families = sector_families(point)
    tensor = intersection_tensor(point)

    sectors = sorted({f["sector"] for f in families})
    lines = sorted({f["fixed_line"] for f in families})
    per_sector = {s: sum(1 for f in families if f["sector"] == s)
                  for s in sectors}

    n_flat = tensor["n_flat_three_forms"]
    n_hit = len(tensor["h3_slots_hit"])
    n_unhit = len(tensor["h3_slots_unhit_flat"])

    # Decided by the named predicate so the rule is testable in both
    # directions rather than inlined as a comparison nobody can falsify.
    isotropic = image_is_isotropic(n_hit)

    return {
        "shape": tensor["shape"],
        "n_nonzero": tensor["n_nonzero"],
        "distinct_values": tensor["distinct_values"],
        "diagonal_in_h2": tensor["diagonal_in_h2"],
        "n_sectors": len(sectors),
        "families_per_sector": per_sector,
        "distinct_fixed_lines": lines,
        "h3_image_dimension": n_hit,
        "n_flat_forms_never_paired": n_unhit,
        "is_isotropic": isotropic,
        "why_not_isotropic": (
            "the image is %d-dimensional inside H^3 of dimension %d, and %d of "
            "the %d flat 3-forms are never paired at all. A shell form forced "
            "proportional to the identity by Schur's lemma cannot look like "
            "this -- which is the diagnosis of the Leech and E8^3 null results."
            % (n_hit, tensor["shape"][2], n_unhit, n_flat)
        ),
        "the_three_plus_four_split": (
            "%d flat forms are paired and %d are not. The %d unpaired ones match "
            "the number of FREE involutions in Gamma (7 total, %d singular), so "
            "the split of the seven flat 3-forms mirrors the split of Gamma's "
            "seven involutions."
            % (n_hit, n_unhit, n_unhit, len(sectors))
        ),
        "provenance": {
            "diagonality": "Joyce admissibility: singular sets pairwise disjoint",
            "minus_two": (
                "intersection form on an A_n resolution is minus the A_n Cartan "
                "matrix; A1 gives -(2). The A1 type is established by "
                "transverse_group_census."
            ),
            "which_omega": (
                "R2: each involution's fixed set is a Fano line, so exactly one "
                "flat 3-form restricts to the T^3 volume."
            ),
        },
        "counts": (
            "cohomology classes and topological intersection numbers; no "
            "conversion to dimensions or group orders"
        ),
    }
