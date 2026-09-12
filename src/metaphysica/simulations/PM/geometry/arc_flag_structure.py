"""The flag structure of a Fano arc, and what it does and does not explain.

The framework derives a 4 + 3 split: each non-identity element of
Gamma = (Z/2)^3 -- the diagonal stabiliser of phi -- moves exactly 4 of the 7
coordinates (an arc of PG(2,2), the "faces") and fixes exactly 3 (the
complementary line, the "blocks"). See geometry/joyce_orbifold.py, R2.

This module asks what 4 x 3 = 12 is as a geometric object, and what the doubling
to 24 is. The answer is an orbit-stabiliser identity:

    24 = 12 x 2 = (4 faces x 3 blocks) x (flag stabiliser)

and every step is computed from the Fano plane's own automorphism group rather
than asserted:

  (i)   Each point a of the arc lies on exactly 3 lines. Each such line differs
        from L (because a is not on L) and so meets L in exactly one point, and
        those 3 points are distinct -- two lines sharing both a and l would be
        equal. So the map from lines through a to L is a bijection, and the 12
        flags (a, line) biject with the 12 pairs (a, l) in A x L. The incidence
        is the complete bipartite K(4,3).
  (ii)  PSL(3,2) has order 168 and is transitive on the 7 arcs, so an arc
        stabiliser has order 168/7 = 24. Four points in general position form a
        frame of PG(2,2), so the stabiliser injects into Sym(A) and is therefore
        isomorphic to S4.
  (iii) The stabiliser fixes L setwise, giving S4 onto Sym(L) = S3 with kernel
        V4. V4 acts freely on A, so Stab(a) = S3 meets the kernel trivially and
        maps onto Sym(L) -- hence Stab(a) is transitive on L, and S4 is
        transitive on the 12 pairs.
  (iv)  Therefore the flag stabiliser has order 24/12 = 2.

WHAT THIS IS NOT
================
It is a statement about a GROUP ORDER. The diagnosed failure mode in this
project is index structure mistaken for geometric structure: every previous
attempt on the number 24 matched an integer without producing geometry. A group
order is an integer. So the verdict recorded here is NUMERICAL, not GEOMETRIC,
and it is NOT adopted as the origin of b_3 = 24. To become geometric it would
have to exhibit 24 actual 3-cycles or harmonic 3-forms, and it does not.

Note also the standing CANON ruling in simulations/core/canonical_values.py:
"4 x 3 IS NOT A STRUCTURE ON 24" -- the 4x3 array is the MiniMOG, serving M_12
and the ternary Golay code on 12 points, and M_24 is 5-transitive hence
primitive, so no partition of 24 points is M_24-invariant. That ruling stands and
is NOT contradicted here, because nothing below partitions 24 points: the 4 and
the 3 live on the SEVEN coordinates of PG(2,2), and the 24 that appears is the
order of a stabiliser subgroup, not a set of 24 objects being carved up.

WHERE THE GEOMETRIC ROUTE ACTUALLY RUNS
=======================================
fixed_locus_components() computes the one thing here made of genuine 3-cycles:
the fixed loci of the involutions in T^7 are 3-tori. Under the LINEAR action
alone there are 7 x 16 = 112 of them and no group element identifies any two,
because negating a half-period coordinate returns it to itself mod 1. Only a
half-shift exchanges 0 and 1/2. So the half-shift data is load-bearing rather
than a refinement, and it is the route to the twisted sector and hence to b_3.
That computation is not done here.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Sequence, Tuple

_N_COORDS = 7


def fano_lines(g2=None) -> List[Tuple[int, int, int]]:
    """The 7 lines of PG(2,2), read from the framework's own phi."""
    from metaphysica.simulations.PM.gauge.topological_terms import (
        associative_triples,
    )

    return [tuple(sorted(t)) for t in associative_triples(g2)]


def fano_automorphisms(g2=None) -> List[Tuple[int, ...]]:
    """Aut(PG(2,2)) = PSL(3,2), as permutations of the 7 coordinates.

    Exhaustive over all 7! = 5040 permutations, keeping those that map the line
    set to itself. No tolerance, nothing to converge; the order must come out
    168, and it is the ONLY source of the 24 below.
    """
    lines = {frozenset(line) for line in fano_lines(g2)}
    out = []
    for p in itertools.permutations(range(_N_COORDS)):
        if {frozenset(p[i] for i in line) for line in lines} == lines:
            out.append(p)
    return out


def arcs_and_complements(g2=None) -> List[Tuple[Tuple[int, ...], Tuple[int, ...]]]:
    """The 7 (arc, complementary line) pairs, taken from the group action.

    Read from involution_arc_correspondence so these are the framework's derived
    moved/fixed split rather than a construction local to this module.
    """
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        involution_arc_correspondence,
    )

    return [(tuple(c["moved"]), tuple(c["fixed"]))
            for c in involution_arc_correspondence(g2)]


def flags(arc: Sequence[int], lines: Sequence[Sequence[int]]
          ) -> List[Tuple[int, Tuple[int, ...]]]:
    """The (arc point, line through it) incidences -- twelve, for an arc."""
    out = []
    for a in sorted(arc):
        for line in lines:
            if a in line:
                out.append((a, tuple(sorted(line))))
    return out


def flag_pair_bijection(arc: Sequence[int], line: Sequence[int],
                        lines: Sequence[Sequence[int]]) -> Dict[str, Any]:
    """Step (i): the flags biject with A x L, giving the complete K(4,3)."""
    line_set = frozenset(line)
    mapping = {}
    ok = True
    for a in sorted(arc):
        through = [frozenset(m) for m in lines
                   if a in m and frozenset(m) != line_set]
        hits = []
        for m in through:
            meet = m & line_set
            if len(meet) != 1:
                ok = False
            else:
                hits.append(next(iter(meet)))
        if len(through) != 3 or len(set(hits)) != 3:
            ok = False
        mapping[a] = tuple(sorted(hits))

    n_flags = len(flags(arc, lines))
    n_pairs = len(arc) * len(line)
    return {
        "n_flags": n_flags,
        "n_pairs": n_pairs,
        "is_bijection": ok and n_flags == n_pairs,
        "arc_point_to_line_points": mapping,
    }


def arc_stabiliser(arc: Sequence[int], autos: Sequence[Sequence[int]]
                   ) -> List[Tuple[int, ...]]:
    """The subgroup of PSL(3,2) fixing the arc setwise."""
    pts = set(arc)
    return [tuple(p) for p in autos if {p[i] for i in pts} == pts]


def orbit_and_stabiliser(arc: Sequence[int], line: Sequence[int],
                         stab: Sequence[Sequence[int]]) -> Dict[str, Any]:
    """Steps (iii) and (iv): transitivity on A x L, and the flag stabiliser."""
    pairs = [(a, l) for a in sorted(arc) for l in sorted(line)]
    base = pairs[0]

    orbit = {base}
    frontier = [base]
    while frontier:
        x = frontier.pop()
        for p in stab:
            y = (p[x[0]], p[x[1]])
            if y not in orbit:
                orbit.add(y)
                frontier.append(y)

    fixers = [p for p in stab if (p[base[0]], p[base[1]]) == base]
    return {
        "n_pairs": len(pairs),
        "orbit_size": len(orbit),
        "is_transitive": len(orbit) == len(pairs),
        "flag_stabiliser_order": len(fixers),
    }


def kernel_to_line_symmetry(arc: Sequence[int], line: Sequence[int],
                            stab: Sequence[Sequence[int]]) -> Dict[str, Any]:
    """The kernel of Stab(A) -> Sym(L): order 4, and it acts freely on the arc.

    Freeness is what forces Stab(a) to map ONTO Sym(L), which is what makes the
    action on A x L transitive. Without it step (iii) does not go through, so
    this is reported rather than assumed.
    """
    ker = [p for p in stab if all(p[l] == l for l in line)]
    identity = tuple(range(_N_COORDS))
    free = all(all(p[a] != a for a in arc) for p in ker if p != identity)
    return {"kernel_order": len(ker), "acts_freely_on_arc": free}


def fixed_locus_components(g2=None) -> Dict[str, Any]:
    """The genuine 3-cycles here, and why the linear action is not enough.

    For an involution moving the 4 coordinates of an arc and fixing the 3 of a
    line, its fixed locus in T^7 = R^7/Z^7 is the set of points whose 4 moved
    coordinates each sit at a half-period: 2^4 = 16 components, each a 3-torus
    in the fixed directions.

    A pure sign flip cannot permute those components -- negating a coordinate
    sends 0 to 0 and 1/2 to -1/2 = 1/2 mod 1, so every component label is
    preserved. Only a half-shift exchanges 0 and 1/2. Hence the linear part of
    Gamma identifies nothing and the count stays at 7 x 16 = 112.
    """
    corr = arcs_and_complements(g2)
    n_moved = len(corr[0][0]) if corr else 0
    per = 2 ** n_moved
    return {
        "n_involutions": len(corr),
        "moved_coordinates_per_involution": n_moved,
        "components_per_involution": per,
        "total_three_torus_components": len(corr) * per,
        "linear_action_identifies_any": False,
        "half_shifts_are_load_bearing": True,
        "note": (
            "A sign flip fixes every half-period coordinate mod 1, so the "
            "linear action cannot reduce the count. Only the half-shift data "
            "can, and it therefore determines the twisted sector and b_3. Not "
            "computed here."
        ),
    }


def arc_flag_report(g2=None) -> Dict[str, Any]:
    """The whole derivation, with its verdict."""
    lines = fano_lines(g2)
    autos = fano_automorphisms(g2)
    pairs = arcs_and_complements(g2)

    if not pairs:
        return {
            "n_lines": len(lines),
            "automorphism_order": len(autos),
            "n_arcs": 0,
            "verdict": "DEGENERATE",
            "verdict_reason": (
                "The form supplied has no involution moving an arc, so there "
                "is no 4 + 3 split to build flags on."
            ),
        }

    arc, line = pairs[0]
    stab = arc_stabiliser(arc, autos)
    actions_on_arc = {tuple(p[i] for i in sorted(arc)) for p in stab}
    orbit = orbit_and_stabiliser(arc, line, stab)

    return {
        "n_lines": len(lines),
        "automorphism_order": len(autos),
        "n_arcs": len(pairs),
        "arc": arc,
        "complement_line": line,
        "bijection": flag_pair_bijection(arc, line, lines),
        "stabiliser_order": len(stab),
        "distinct_actions_on_arc": len(actions_on_arc),
        "stabiliser_is_faithful_and_onto_sym_arc": (
            len(actions_on_arc) == len(stab) == 24
        ),
        "kernel": kernel_to_line_symmetry(arc, line, stab),
        "orbit": orbit,
        "identity": "24 = 12 x 2 = (4 faces x 3 blocks) x (flag stabiliser)",
        "identity_holds": (
            len(stab) == orbit["n_pairs"] * orbit["flag_stabiliser_order"]
            and orbit["is_transitive"]
        ),
        "fixed_loci": fixed_locus_components(g2),
        "verdict": "NUMERICAL",
        "verdict_reason": (
            "This is the order of a stabiliser subgroup, not a count of "
            "3-cycles or harmonic 3-forms. It is NOT adopted as the origin of "
            "b_3 = 24. The geometric route runs through the fixed loci, which "
            "need the half-shift data that is not computed here."
        ),
        "does_not_contradict_canon_4x3_ruling": (
            "Nothing here partitions 24 points. The 4 and the 3 live on the "
            "seven coordinates of PG(2,2); the 24 is a subgroup order."
        ),
    }
