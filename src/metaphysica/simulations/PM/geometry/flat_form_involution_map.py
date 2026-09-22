"""Is "4 unpaired flat 3-forms = 4 free involutions" a correspondence, or arithmetic?

THE CLAIM UNDER TEST
====================
Gamma = (Z/2)^3 has 7 non-identity elements; at the canonical point 3 are
singular and 4 are free. The flat sector has b_3 = 7 (derived, R5). A claim in
circulation: 3 flat 3-forms "pair" with the singular involutions and the
remaining **4 are left unpaired**, matching the 4 free involutions.

THE VERDICT, MEASURED
=====================
A map exists -- and it REFUTES the claim as stated, because it is TOTAL.

`involution_arc_correspondence` gives each of the 7 non-identity elements a
fixed set, and measured over the live enumeration every one of those 7 fixed
sets IS one of the 7 invariant 3-forms, injectively and onto. So the pairing is
a BIJECTION 7 <-> 7. Nothing is left unpaired at all.

The 4 is therefore real and its stated reason is wrong. The four forms the
claim calls "unpaired" are precisely the four PAIRED WITH THE FREE
INVOLUTIONS. "7 = 3 + 4" is not two facts meeting; it is one partition --
singular versus free, on the involution side -- transported across a bijection
that was already there. Reading it as a coincidence between two independent
counts would be counting the same split twice.

WHY THE BIJECTION IS NOT ITSELF A COINCIDENCE
=============================================
Both sides are indexed by the same third object. phi's support is the 7 lines
of the Fano plane PG(2,2); the Gamma-invariant 3-forms are exactly those lines
(R3/R5), and each non-identity element of the diagonal stabiliser fixes exactly
one line. The map is not form -> element directly: it is
form -> Fano line -> element, and both legs are forced by phi.

WHAT IS CANONICAL AND WHAT IS NOT -- the part that matters most
==============================================================
The bijection depends only on phi, so it is canonical. The 3 + 4 SPLIT does
not: which three involutions are singular is a property of the HALF-SHIFT
ASSIGNMENT, and different admissible assignments make different triples
singular. So "these particular 4 flat forms" is not a well-defined set on the
moduli space; only "the 4 paired with whichever involutions are free here" is.
Any argument that attaches physics to a specific four is attaching it to a
choice.

THE A4 BAR, per arrow, because this chain crosses type boundaries
================================================================
    invariant 3-form     a COHOMOLOGY CLASS (a Gamma-invariant element of
                         Lambda^3, one per Fano line)
    Fano line            a LINE of PG(2,2) -- an incidence-geometry object
    involution           a GROUP ELEMENT of Gamma
    singular / free      a property of a group element UNDER AN ASSIGNMENT,
                         not of the element alone

Nothing here converts a count of classes into a dimension, and the bijection is
a correspondence of INDEX SETS, not an identification of the objects indexed.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "flat_form_to_involution",
    "map_is_bijective",
    "split_under_assignment",
    "split_is_assignment_dependent",
    "correspondence_report",
]


#: The map depends only on phi, so it is constant for the process. It is asked
#: for once per admissible assignment by the canonicity scan, which walks
#: thousands of them.
_MAP_CACHE: Optional[Dict[Tuple[int, int, int], Tuple[int, ...]]] = None


def flat_form_to_involution() -> Dict[Tuple[int, int, int], Tuple[int, ...]]:
    """Each invariant 3-form, and the involution whose fixed set it is.

    Built by MATCHING, not by construction: the two lists are produced
    independently by `joyce_orbifold` and the pairing is whatever the fixed
    sets turn out to be. A form with no matching element simply does not appear,
    which is what lets `map_is_bijective` come back False.
    """
    global _MAP_CACHE
    if _MAP_CACHE is not None:
        return dict(_MAP_CACHE)

    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        invariant_three_forms,
        involution_arc_correspondence,
    )

    by_fixed = {tuple(rec["fixed"]): tuple(rec["element"])
                for rec in involution_arc_correspondence()}
    _MAP_CACHE = {tuple(triple): by_fixed[tuple(triple)]
                  for triple in invariant_three_forms()
                  if tuple(triple) in by_fixed}
    return dict(_MAP_CACHE)


def map_is_bijective() -> Dict[str, Any]:
    """Is the pairing total and one-to-one, or partial as the claim assumes?

    A4 bar: `n_flat_forms` counts COHOMOLOGY CLASSES, `n_involutions` counts
    GROUP ELEMENTS. The report states that the map is a bijection between two
    INDEX SETS; it does not identify a class with an element.
    """
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        diagonal_stabiliser,
        invariant_three_forms,
    )

    flats = [tuple(t) for t in invariant_three_forms()]
    non_identity = [e for e in diagonal_stabiliser() if any(x == -1 for x in e)]
    mapping = flat_form_to_involution()
    images = list(mapping.values())

    return {
        "n_flat_forms": len(flats),
        "n_involutions": len(non_identity),
        "n_paired": len(mapping),
        "n_unpaired_flat_forms": len(flats) - len(mapping),
        "injective": len(set(images)) == len(images),
        "surjective_onto_involutions": set(images) == {tuple(e) for e
                                                       in non_identity},
        "is_bijection": (len(mapping) == len(flats)
                         and len(set(images)) == len(images)
                         and set(images) == {tuple(e) for e in non_identity}),
        "counts_what": ("n_flat_forms counts COHOMOLOGY CLASSES; "
                        "n_involutions counts GROUP ELEMENTS; the map is "
                        "between INDEX SETS"),
        "via": ("form -> Fano line -> element. phi's support is the 7 lines of "
                "PG(2,2); the invariant 3-forms are those lines and each "
                "non-identity element fixes exactly one."),
    }


def split_under_assignment(triple: Sequence[int], svecs,
                           group=None) -> Optional[Dict[str, Any]]:
    """Which flat forms pair with SINGULAR involutions under one assignment.

    Returns None for an inadmissible assignment, because the singular/free
    split is only defined where Joyce's construction applies.
    """
    from metaphysica.simulations.PM.geometry import half_shift_enumeration as hs

    group = group or hs._group()
    non_identity = hs._non_identity(group)
    gens = [non_identity[i] for i in triple]
    elems = hs.elements(gens, svecs)

    singular = [(bits, el) for bits, el in elems.items()
                if bits != (0, 0, 0) and hs.is_singular(el)]
    if not all(hs.fixed_sets_disjoint(a[1], b[1])
               for a, b in itertools.combinations(singular, 2)):
        return None

    # `Element` is the plain tuple (eps, shift-bits), so eps is el[0] and
    # `fixed_coords` takes eps.
    singular_fixed = {tuple(hs.fixed_coords(el[0])) for _bits, el in singular}

    mapping = flat_form_to_involution()
    paired_singular = sorted(f for f in mapping if f in singular_fixed)
    paired_free = sorted(f for f in mapping if f not in singular_fixed)

    return {
        "n_singular": len(singular),
        "n_free": 7 - len(singular),
        "flat_forms_paired_with_singular": paired_singular,
        "flat_forms_paired_with_free": paired_free,
        "n_paired_with_singular": len(paired_singular),
        "n_paired_with_free": len(paired_free),
    }


def split_is_assignment_dependent(limit: int = 4000,
                                  group=None) -> Dict[str, Any]:
    """Does WHICH three forms pair with singular involutions depend on the choice?

    Walks admissible assignments until it has either found two different
    singular triples -- which settles it -- or exhausted `limit`. The answer
    decides whether "these four flat forms" names anything on the moduli space.
    """
    from metaphysica.simulations.PM.geometry import half_shift_enumeration as hs

    group = group or hs._group()
    seen: Dict[Tuple[Tuple[int, ...], ...], int] = {}
    scanned = 0

    for triple in hs.generating_triples(group):
        for svecs in hs.assignments(triple, group, True):
            scanned += 1
            if scanned > limit:
                break
            split = split_under_assignment(triple, svecs, group)
            if not split or split["n_singular"] != 3:
                continue
            key = tuple(split["flat_forms_paired_with_singular"])
            seen[key] = seen.get(key, 0) + 1
        if scanned > limit:
            break

    distinct = sorted(seen)
    return {
        "assignments_scanned": scanned,
        "distinct_singular_form_triples": len(distinct),
        "examples": distinct[:6],
        "depends_on_assignment": len(distinct) > 1,
        "means": (
            "the set of flat 3-forms paired with SINGULAR involutions is not "
            "canonical: %d distinct triples occur among the admissible "
            "assignments scanned. 'these four flat forms' therefore names a "
            "CHOICE, not a property of the geometry. The 7 <-> 7 bijection is "
            "canonical; the 3 + 4 split on top of it is not."
            % len(distinct)
        ) if len(distinct) > 1 else (
            "every admissible assignment scanned made the SAME three flat "
            "forms singular, so the split may be canonical after all -- which "
            "would be a stronger result than the claim asked for and needs a "
            "proof rather than a scan."
        ),
    }


def correspondence_report() -> Dict[str, Any]:
    """The adjudication, with the refutation stated as plainly as a success."""
    bijection = map_is_bijective()
    dependence = split_is_assignment_dependent()

    if not bijection["is_bijection"]:
        verdict = "NO_TOTAL_MAP"
        summary = (
            "the pairing is partial: %d of %d flat 3-forms have no involution. "
            "The claim's premise survives and its arithmetic needs a separate "
            "check." % (bijection["n_unpaired_flat_forms"],
                        bijection["n_flat_forms"])
        )
    else:
        verdict = "REFUTED_AS_STATED_MAP_IS_TOTAL"
        summary = (
            "REFUTED. A map exists and it is a BIJECTION: all %d invariant "
            "3-forms pair with all %d non-identity involutions, injectively "
            "and onto. Nothing is 'left unpaired'. The four forms the claim "
            "calls unpaired are the four paired with the FREE involutions, so "
            "'7 = 3 + 4' is one partition seen twice, not two counts agreeing. "
            "The number 4 is right and the reason given for it is wrong."
            % (bijection["n_flat_forms"], bijection["n_involutions"])
        )

    return {
        "claim": ("4 flat 3-forms are left unpaired after 3 pair with the "
                  "singular involutions, matching the 4 free involutions"),
        "verdict": verdict,
        "summary": summary,
        "bijection": bijection,
        "split_canonicity": dependence,
        "what_survives": (
            "the correspondence itself, which is real and was not previously "
            "recorded as a bijection: flat 3-form <-> Fano line <-> involution, "
            "both legs forced by phi. What does not survive is 'unpaired', and "
            "with it any reading of 7 = 3 + 4 as corroboration."
        ),
        "a4_bar": bijection["counts_what"],
        "caution": (
            "the 3 + 4 split rides on the half-shift assignment, not on phi, "
            "so no specific four flat forms are distinguished on the moduli "
            "space."
        ),
    }
