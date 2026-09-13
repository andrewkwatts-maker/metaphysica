"""The half-shift moduli space of (Z/2)^3 actions on T^7 — corrected.

WITHDRAWN: THE PARITY REFUTATION OF b_3 = 24
============================================
An earlier version of this module claimed to refute b_3 = 24 for the Joyce
(Z/2)^3 construction by a parity theorem over 14,336 shift assignments. That
result is WITHDRAWN, for three reasons found on review, each verifiable here:

1. INCOMPLETE COVERAGE. The old reduction claimed shifts on flipped coordinates
   are removable by conjugation. False for coordinates flipped by MORE THAN ONE
   generator: conjugation by a translation moves every flipping generator's
   shift by the same -2t_a, so the pairwise DIFFERENCES are invariants, and the
   commutator constraint pins each difference to {0, 1/2}. Those relative bits
   are 5 per generating triple (2 on the triply-flipped coordinate, 1 on each
   of the 3 doubly-flipped ones), so the true moduli space is
   8^3 x 2^5 x 28 = 458,752 assignments — the old enumeration visited 1/32 of
   it, and Joyce's own examples (shifts of the form 1/2 - x on flipped
   coordinates) live precisely in the missed strata.

2. INVALID PREMISE ON WHAT WAS COVERED. The parity argument assumed resolution
   contributes additively over disjoint singular families. In the covered
   stratum the fixed sets of distinct involutions INTERSECT (two pure sign
   flips share a 1-torus of common fixed points), so the isolated-A1 model the
   argument needed does not apply there. Joyce's construction requires the
   singular sets to be pairwise disjoint, and it is exactly the missed relative
   shifts that separate them.

3. A LABELLING DEFECT. The old component action omitted the singular element's
   own flipped-coordinate shift (the s^sigma twist below), which composed
   elements carry even in the old stratum, so the old family counts are not
   trusted either.

Consequently b_3 = 24 for the Joyce (Z/2)^3 construction is UNDETERMINED again,
and the register records the withdrawal. Everything below is the corrected
machinery.

THE CORRECTED MODULI SPACE
==========================
An element is x -> eps x + s on T^7 with eps diagonal signs and s a shift.
g^2 = 1 and commutativity of the group force every meaningful shift component
into {0, 1/2}; conjugation by a global translation removes exactly one shift
per coordinate among the generators flipping it. The residual data is:

  * one bit per generator per coordinate of its FIXED line   (3 x 3 bits)
  * one relative bit per extra flipper per multiply-flipped
    coordinate                                               (5 bits)

Shifts are encoded as bits, one unit = 1/2, composed mod 2.

ADMISSIBILITY (Joyce's condition)
=================================
An element (eps, s) has fixed points iff s vanishes on every coordinate it
fixes; its fixed set is then 2^4 = 16 parallel 3-tori, positioned by its
flipped-coordinate shifts. An assignment is ADMISSIBLE when the fixed sets of
its singular elements are PAIRWISE DISJOINT — which happens iff each pair
shares a flipped coordinate on which their shifts differ. Only for admissible
assignments is the singular locus a disjoint union of T^3 families with A1
transverse structure, the situation in which resolution contributes additively
per family.

WHAT THIS MODULE DOES AND DOES NOT CONCLUDE
===========================================
Computed here, unconditionally: the moduli space, admissibility, the family
count and each family's stabiliser type for every admissible assignment.

NOT computed here: Betti numbers of the resolutions. Converting families into
(b_2, b_3) needs the per-type contribution table from the literature (Joyce,
Compact Manifolds with Special Holonomy, ch. 12 — the reference the register
already carries for this construction). Until that table is transcribed from
the source and the machinery calibrated against a known example per the A6
gate, every Betti statement is CONDITIONAL and is labelled so. What can be said
unconditionally is the bound dim H^1(T^3) = 3: no A1 family contributes more
than 3 to b_3, so an admissible assignment needs at least ceil(17/3) = 6
families before b_3 = 24 = 7 + 17 is even arithmetically possible.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, Iterator, List, Sequence, Tuple

import numpy as np

_N = 7

Element = Tuple[Tuple[int, ...], Tuple[int, ...]]     # (eps, shift-bits)


def _group():
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        diagonal_stabiliser,
    )

    return diagonal_stabiliser()


def _non_identity(group) -> List[Tuple[int, ...]]:
    return [g for g in group if any(s < 0 for s in g)]


def fixed_coords(eps: Sequence[int]) -> Tuple[int, ...]:
    return tuple(a for a in range(_N) if eps[a] > 0)


def moved_coords(eps: Sequence[int]) -> Tuple[int, ...]:
    return tuple(a for a in range(_N) if eps[a] < 0)


def _compose(e1, s1, e2, s2) -> Element:
    """(e1,s1) after (e2,s2); shifts in half-units mod 2, so -1/2 = +1/2."""
    return (tuple(e1[a] * e2[a] for a in range(_N)),
            tuple((e1[a] * s2[a] + s1[a]) % 2 for a in range(_N)))


def generating_triples(group=None) -> List[Tuple[int, int, int]]:
    """Non-collinear triples of the 7 non-identity elements: 28 of the 35."""
    group = group or _group()
    nz = _non_identity(group)
    ones = np.ones(_N, dtype=int)
    out = []
    for t in itertools.combinations(range(len(nz)), 3):
        prod = np.array(nz[t[0]]) * np.array(nz[t[1]]) * np.array(nz[t[2]])
        if not np.array_equal(prod, ones):
            out.append(t)
    return out


def flip_profile(gens: Sequence[Sequence[int]]) -> Dict[int, Tuple[int, ...]]:
    """Which generators flip each coordinate. The triangle structure gives
    counts {3: 1 coordinate, 2: 3 coordinates, 1: 3 coordinates}."""
    return {a: tuple(i for i, g in enumerate(gens) if g[a] < 0)
            for a in range(_N)}


def relative_slots(gens) -> List[Tuple[int, int]]:
    """(coordinate, generator) pairs carrying a non-removable relative bit.

    Per coordinate, the FIRST flipping generator's shift is normalised to zero
    by the global translation; every further flipper keeps one bit. These are
    the strata the withdrawn enumeration missed.
    """
    prof = flip_profile(gens)
    return [(a, gi) for a in range(_N) for gi in prof[a][1:]]


def assignments(triple: Sequence[int], group=None,
                include_relative: bool = True
                ) -> Iterator[Tuple[Tuple[int, ...], ...]]:
    """Every shift assignment for one generating triple.

    include_relative=False reproduces the WITHDRAWN stratum (512 per triple),
    kept only so the old numbers remain checkable; the full space is 16,384
    per triple.
    """
    group = group or _group()
    nz = _non_identity(group)
    gens = [nz[i] for i in triple]
    lines = [fixed_coords(g) for g in gens]
    slots = relative_slots(gens) if include_relative else []

    for fixed_bits in itertools.product((0, 1), repeat=9):
        base = [[0] * _N for _ in range(3)]
        it = iter(fixed_bits)
        for gi, line in enumerate(lines):
            for a in line:
                base[gi][a] = next(it)
        if not slots:
            yield tuple(tuple(r) for r in base)
            continue
        for rel_bits in itertools.product((0, 1), repeat=len(slots)):
            sv = [row[:] for row in base]
            for (a, gi), bit in zip(slots, rel_bits):
                sv[gi][a] = bit
            yield tuple(tuple(r) for r in sv)


def elements(gens, svecs) -> Dict[Tuple[int, int, int], Element]:
    """The 8 affine elements. Faithful automatically: the linear parts of a
    non-collinear triple already generate (Z/2)^3."""
    out = {}
    for bits in itertools.product((0, 1), repeat=3):
        e, s = tuple([1] * _N), tuple([0] * _N)
        for use, g, sv in zip(bits, gens, svecs):
            if use:
                e, s = _compose(e, s, g, sv)
        out[bits] = (e, s)
    return out


def is_singular(elem: Element) -> bool:
    """Fixed points exist iff the shift vanishes on every FIXED coordinate."""
    eps, s = elem
    return all(s[a] == 0 for a in range(_N) if eps[a] > 0)


def fixed_sets_disjoint(a: Element, b: Element) -> bool:
    """Joyce's separation: a shared flipped coordinate with differing shifts.

    On such a coordinate the two fixed sets sit at {s/4, s/4 + 1/2} with
    different s, and {0, 1/2} is disjoint from {1/4, 3/4}.
    """
    (ea, sa), (eb, sb) = a, b
    return any(ea[c] < 0 and eb[c] < 0 and sa[c] != sb[c] for c in range(_N))


def act_on_component(delta: Element, sigma: Element,
                     comp: Dict[int, int]) -> Tuple[Tuple[int, int], ...]:
    """Where delta sends a labelled T^3 component of Fix(sigma).

    A component is x_a = s^sigma_a / 4 + c_a / 2 on each flipped coordinate a.
    Applying x -> d x + t/2 and re-expressing in the same form gives

        c'_a = c_a + t_a                (d_a = +1)
        c'_a = c_a + t_a + s^sigma_a    (d_a = -1)

    all mod 2. The s^sigma term is the twist the withdrawn version omitted.
    """
    (de, ds) = delta
    (_se, ss) = sigma
    out = []
    for a, c in comp.items():
        if de[a] > 0:
            out.append((a, (c + ds[a]) % 2))
        else:
            out.append((a, (c + ds[a] + ss[a]) % 2))
    return tuple(sorted(out))


def families_of(elems: Dict, sigma: Element) -> List[Dict[str, Any]]:
    """Gamma-orbits of the 16 components of Fix(sigma), with stabiliser type."""
    eps, _s = sigma
    moved = moved_coords(eps)
    comps = [dict(zip(moved, c))
             for c in itertools.product((0, 1), repeat=len(moved))]
    fam: List[Dict[str, Any]] = []
    seen = set()
    fixed = fixed_coords(eps)
    for comp in comps:
        key = tuple(sorted(comp.items()))
        if key in seen:
            continue
        orbit = {key}
        frontier = [comp]
        while frontier:
            cur = frontier.pop()
            for delta in elems.values():
                nxt = act_on_component(delta, sigma, cur)
                if nxt not in orbit:
                    orbit.add(nxt)
                    frontier.append(dict(nxt))
        seen |= orbit

        # stabiliser of the representative component, classified by its
        # induced action on the T^3 (the coordinates sigma fixes)
        stab_types = set()
        for delta in elems.values():
            if act_on_component(delta, sigma, comp) != key:
                continue
            de, ds = delta
            if all(de[b] > 0 for b in fixed):
                if all(ds[b] == 0 for b in fixed):
                    stab_types.add("trivial")
                else:
                    stab_types.add("translation")
            else:
                stab_types.add("reflection")
        if stab_types <= {"trivial"}:
            ftype = "T3"
        elif "reflection" in stab_types:
            ftype = "T3_reflected"
        else:
            ftype = "T3_translated"
        fam.append({"orbit_size": len(orbit), "type": ftype})
    return fam


def survey_assignment(triple, svecs, group=None) -> Dict[str, Any]:
    """Singular structure of one assignment: admissibility, families, types."""
    group = group or _group()
    nz = _non_identity(group)
    gens = [nz[i] for i in triple]
    elems = elements(gens, svecs)

    singular = [(bits, el) for bits, el in elems.items()
                if bits != (0, 0, 0) and is_singular(el)]
    admissible = all(fixed_sets_disjoint(a[1], b[1])
                     for a, b in itertools.combinations(singular, 2))

    record: Dict[str, Any] = {
        "n_singular": len(singular),
        "n_free": 7 - len(singular),
        "admissible": admissible,
    }
    if admissible:
        fams: List[Dict[str, Any]] = []
        for _bits, el in singular:
            fams.extend(families_of(elems, el))
        record["n_families"] = len(fams)
        record["family_types"] = tuple(sorted(f["type"] for f in fams))
    return record


def survey(include_relative: bool = True, group=None,
           triples=None) -> Dict[str, Any]:
    """The whole moduli space (or the withdrawn stratum, for the record)."""
    group = group or _group()
    triples = triples if triples is not None else generating_triples(group)
    nz = _non_identity(group)

    total = 0
    n_admissible = 0
    family_counts: Dict[int, int] = {}
    type_profiles: Dict[Tuple[str, ...], int] = {}
    joyce_structure = 0        # 3 singular, disjoint, 12 plain-T3 families

    for triple in triples:
        for svecs in assignments(triple, group, include_relative):
            total += 1
            rec = survey_assignment(triple, svecs, group)
            if not rec["admissible"]:
                continue
            n_admissible += 1
            n = rec.get("n_families", 0)
            family_counts[n] = family_counts.get(n, 0) + 1
            prof = rec.get("family_types", ())
            type_profiles[prof] = type_profiles.get(prof, 0) + 1
            if (rec["n_singular"] == 3 and n == 12
                    and set(prof) == {"T3"}):
                joyce_structure += 1

    return {
        "include_relative": include_relative,
        "n_assignments": total,
        "n_admissible": n_admissible,
        "admissible_family_counts": dict(sorted(family_counts.items())),
        "admissible_type_profiles": {str(k): v for k, v in
                                     sorted(type_profiles.items())},
        "joyce_structure_assignments": joyce_structure,
    }


def status_report() -> Dict[str, Any]:
    """What is established, what is withdrawn, and what remains open."""
    return {
        "withdrawn": (
            "The parity refutation of b_3 = 24. Its enumeration covered 1/32 "
            "of the moduli space (relative flipped-coordinate shifts are "
            "conjugation invariants pinned to {0, 1/2} and were not "
            "enumerated); its additivity premise fails on the covered stratum "
            "(singular sets there intersect); and its component action "
            "omitted the s^sigma twist."
        ),
        "b3_24_status": "UNDETERMINED",
        "unconditional_bound": (
            "dim H^1(T^3) = 3, so no A1 family contributes more than 3 to "
            "b_3; b_3 = 24 = 7 + 17 therefore needs at least 6 disjoint "
            "families."
        ),
        "conditional_gate": (
            "Converting family counts to (b_2, b_3) requires the per-type "
            "contribution table transcribed from Joyce ch. 12 and an A6 "
            "calibration against a known example. Not asserted here."
        ),
        "flat_contribution": 7,
        "moduli_space_size": 8 ** 3 * 2 ** 5 * 28,
        "withdrawn_stratum_size": 8 ** 3 * 28,
    }
