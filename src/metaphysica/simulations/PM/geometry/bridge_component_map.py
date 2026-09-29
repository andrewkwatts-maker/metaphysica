"""The bulk's 12 bridges and the resolved manifold's 12 A1 components: one
3 x 4 structure (G1b; pre-registered as D-008 in the site repo's
docs/DECISION_LOG.md, 2026-09-30, before this was run).

THE TWO TWELVES
===============
Bridges (docs/BRIDGE_CHANNEL_ASSIGNMENT.md in the site repo): the directed
edges of K4 on a Fano arc of four "faces"; the three E8 blocks are K4's three
perfect matchings, labelled by the points of the arc's complement line. That
record leaves the arc "unique up to symmetry" -- one PSL(3,2) orbit -- and
notes that a preferred structure "would break PSL(3,2) and make the choice of
arc physical again".

Components: each singular involution fixes a Fano line (its three fixed
coordinates) and contributes 4 Gamma-orbits of fixed 3-tori (D-001).

THE CORRESPONDENCE
==================
Three singular involutions spanning Gamma are three NON-CONCURRENT lines: a
point on all three would carry a character trivial on Gamma, and no
coordinate does. They therefore form a triangle, and fix an arc canonically:

    arc = { pairwise intersections } + { the one point on none of them }

(the three lines cover 3*3 - 3 = 6 of the 7 points). The complement line is
the unique line missing all four. On K4 over that arc, every perfect
matching contains exactly one side of the triangle -- a matching pairs one
triangle edge with one edge to the missed point -- and the triangle's sides
lie on the three singular lines. So blocks <-> singular involutions is a
canonical bijection, and the 4 bridges of a block <-> the 4 components of its
involution is a bijection of (Z/2)^2-torsors, canonical up to a Klein-four
relabelling inside each block.

Where it fails, and why that selects: on Joyce's Example-4 classes one
involution carries 8 components (T^3/Z_2 families; D-006), so no
structure-preserving bijection exists. The correspondence holds exactly on
the all-plain members.

STATUS
======
The combinatorics is a theorem about PG(2,2). "One bridge per resolved A1
component, i.e. one U(1)" is a MODEL IDENTIFICATION (working assumption
WA-1): it costs no parameter, fixes which Fano points are faces, and is
checked against Lukas-Morris's gauge-kinetic functions, which depend on the
blow-up type only (hep-th/0305078, eq. 1.3) -- three quartets, one per block.

A4: bridges and components count directed edges and connected 3-tori; blocks
count perfect matchings; none is converted into another -- the map is a
bijection of labelled sets, not an equality of numbers.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "singular_lines",
    "canonical_arc",
    "k4_blocks",
    "block_involutions",
    "components_per_involution",
    "correspondence",
    "n3_family_selection",
]

Line = Tuple[int, ...]


def singular_lines(point: Dict[str, Any]) -> List[Tuple[Tuple[int, ...], Line]]:
    """(involution label, its fixed Fano line) for each singular involution."""
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        fixed_coords,
    )

    return [(tuple(label), tuple(sorted(fixed_coords(el[0]))))
            for label, el in point["singular"]]


def canonical_arc(lines: Sequence[Line]) -> Optional[Dict[str, Any]]:
    """The arc three non-concurrent lines fix, and its complement line.

    None when the lines are concurrent or not three -- then there is no
    triangle and nothing is canonical.
    """
    from metaphysica.simulations.PM.geometry.arc_flag_structure import (
        arcs_and_complements,
    )

    if len(lines) != 3:
        return None
    sets = [set(l) for l in lines]
    if sets[0] & sets[1] & sets[2]:
        return None
    vertices = sorted(next(iter(a & b)) for a, b in
                      itertools.combinations(sets, 2))
    missed = sorted(set(range(7)) - set().union(*sets))
    if len(missed) != 1:
        return None
    arc = tuple(sorted(vertices + missed))
    complement = next((tuple(c) for a, c in arcs_and_complements()
                       if tuple(sorted(a)) == arc), None)
    if complement is None:
        return None
    return {"arc": arc, "complement": complement, "vertices": tuple(vertices),
            "missed_point": missed[0]}


def _line_through(p: int, q: int) -> Line:
    from metaphysica.simulations.PM.geometry.arc_flag_structure import (
        fano_lines,
    )

    return next(tuple(l) for l in fano_lines() if p in l and q in l)


def k4_blocks(arc: Sequence[int], complement: Sequence[int]
              ) -> Dict[int, List[Tuple[int, int]]]:
    """K4's perfect matchings on the arc, keyed by the complement point where
    both of a matching's lines meet the complement line (BRIDGE_CHANNEL_
    ASSIGNMENT: the block partition is canonical given the arc)."""
    blocks: Dict[int, List[Tuple[int, int]]] = {}
    for p, q in itertools.combinations(sorted(arc), 2):
        meet = set(_line_through(p, q)) & set(complement)
        (point,) = meet
        blocks.setdefault(point, []).append((p, q))
    return blocks


def block_involutions(blocks: Dict[int, List[Tuple[int, int]]],
                      lines: Sequence[Tuple[Tuple[int, ...], Line]]
                      ) -> Dict[int, List[Tuple[int, ...]]]:
    """For each block, the singular involutions whose line is one of its
    edges. The hypothesis is exactly one per block."""
    out: Dict[int, List[Tuple[int, ...]]] = {}
    for point, edges in blocks.items():
        out[point] = [label for label, line in lines
                      if any(set(e) <= set(line) for e in edges)]
    return out


def components_per_involution(point: Dict[str, Any]) -> Dict[Tuple[int, ...], int]:
    from metaphysica.simulations.PM.geometry.joyce_resolution import (
        singular_components,
    )

    counts: Dict[Tuple[int, ...], int] = {}
    for row in singular_components(point):
        counts[row["involution"]] = counts.get(row["involution"], 0) + 1
    return counts


def correspondence(point: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The 3 x 4 structures on both sides, and whether they match."""
    if point is None:
        from metaphysica.simulations.PM.geometry.intersection_tensor import (
            canonical_point,
        )

        point = canonical_point()
    lines = singular_lines(point)
    geo = canonical_arc([l for _lab, l in lines])
    out: Dict[str, Any] = {"singular_lines": [l for _lab, l in lines],
                           "canonical_arc": geo}
    if geo is None:
        out.update(bijection=False, reason="no canonical arc")
        return out
    blocks = k4_blocks(geo["arc"], geo["complement"])
    per_block = block_involutions(blocks, lines)
    comps = components_per_involution(point)
    one_each = all(len(v) == 1 for v in per_block.values())
    bridges_per_block = {p: 2 * len(edges) for p, edges in blocks.items()}
    matched = one_each and all(
        bridges_per_block[p] == comps.get(per_block[p][0], 0)
        for p in blocks)
    out.update(
        blocks={p: edges for p, edges in sorted(blocks.items())},
        block_involution={p: v[0] if len(v) == 1 else v
                          for p, v in sorted(per_block.items())},
        one_singular_side_per_block=one_each,
        bridges_per_block=bridges_per_block,
        components_per_involution={str(k): v for k, v in comps.items()},
        n_bridges=sum(bridges_per_block.values()),
        n_components=sum(comps.values()),
        bijection=matched,
        canonical_up_to=("a Klein-four relabelling inside each block: both "
                         "sides are (Z/2)^2-torsors"),
    )
    return out


def n3_family_selection() -> Dict[str, Any]:
    """Over every n = 3 pairwise-disjoint class of the first generating
    triple: the correspondence holds exactly on the all-plain ones?"""
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        _group,
        _non_identity,
        assignments,
        elements,
        fixed_sets_disjoint,
        generating_triples,
        is_singular,
    )
    from metaphysica.simulations.PM.geometry.joyce_reachability import (
        class_options,
    )

    group = _group()
    nz = _non_identity(group)
    triple = generating_triples(group)[0]
    gens = [nz[i] for i in triple]
    tally: Dict[str, int] = {}
    violations: List[Dict[str, Any]] = []
    for svecs in assignments(triple, group, include_relative=True):
        els = elements(gens, svecs)
        singular = [(b, e) for b, e in els.items()
                    if b != (0, 0, 0) and is_singular(e)]
        if len(singular) != 3 or not all(
                fixed_sets_disjoint(a[1], b[1])
                for a, b in itertools.combinations(singular, 2)):
            continue
        profile, pairs = class_options(els, singular)
        all_plain = profile == {2: 12}
        result = correspondence({"elements": els, "singular": singular})
        key = "%s/%s" % ("all_plain" if all_plain else "not_all_plain",
                         "bijection" if result["bijection"] else "none")
        tally[key] = tally.get(key, 0) + 1
        if result["bijection"] != all_plain or not result.get(
                "one_singular_side_per_block", False):
            if len(violations) < 5:
                violations.append({"shifts": svecs, "profile": profile,
                                   "result": result})
    return {
        "tally": dict(sorted(tally.items())),
        "violations": violations,
        "holds": not violations and tally.get("all_plain/bijection", 0) > 0,
        "selects": (12, 43),
    }
