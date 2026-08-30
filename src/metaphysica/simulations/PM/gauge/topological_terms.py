#!/usr/bin/env python3
"""Topological cross-shadow coupling on the G2 associative cycle.

WHY THIS EXISTS
---------------
The bridge sector had NO cross-shadow interaction. The breathing mode is a
scalar tied to bridge size, no antisymmetric or Chern-Simons term existed
anywhere, and the one metric channel that could carry a coupling -- the
off-diagonal L1*L2*cos(theta) -- is identically zero at the stabilised vacuum,
because that vacuum sits at theta = 90 degrees exactly on all 12 bridge pairs.
That is why reflection_positivity_gate reports MARGINAL_VACUOUS rather than
PASS: there is nothing there whose positivity could be certified.

The question this module answers is whether a TOPOLOGICAL term can carry the
coupling instead, leaving the orthogonal background intact.

WHAT IS ESTABLISHED HERE
------------------------
1. A SELECTION RULE. For F_A supported on coordinate pair (i,j) and F_B on
   (k,l), all distinct, the density

       C_3 ^ F_A ^ F_B      with C_3 = phi, the associative 3-form

   is non-zero if and only if the COMPLEMENTARY triple {0..6} \\ {i,j,k,l} is
   one of phi's seven associative triples. Exactly 42 of the 210 disjoint
   channels survive: 7 associative triples x 6 ordered pair-splits of each
   complementary 4-set. This is verified by enumeration, not asserted.

2. THE COUPLING SURVIVES THE ORTHOGONAL VACUUM, AND IS MAXIMAL THERE. The
   topological term couples to the bridge AREA, L1*L2*sin(theta), whereas the
   metric channel couples to L1*L2*cos(theta). At the stabilised vacuum:

       area route   :  5.647615e+02      (maximal at theta = 90 deg)
       metric route :  2.117516e-30      (dead at theta = 90 deg)

   The two channels are exactly complementary -- the topological one peaks
   where the metric one vanishes.

3. TWO INDEPENDENT ROUTES AGREE. The general epsilon contraction and the
   specialised coassociative form <*phi, F_A ^ F_B> share no code, and agree
   to ratio 1.000000000. Since phi ^ omega = <*phi, omega> vol for any 4-form
   omega, this is a real cross-check rather than one computation run twice.

WHAT IS NOT ESTABLISHED
-----------------------
This is flat R^7 with constant-coefficient forms, so the integral is
coefficient x volume -- A NUMBER, NOT A TOPOLOGICAL INVARIANT. Flat R^7 has
trivial holonomy and no non-trivial 7-cycles. g2_differential.py's own
docstring concedes the same point about its setting.

So a non-zero result establishes that THE INTEGRAND IS NON-VANISHING, which is
what the interaction sector needed in order to exist at all. It does NOT
establish topological content. That requires harmonic representatives on a
compact G2 manifold with b3 = 24, which is deferred discrete-exterior-calculus
work, not something assumed here.

Which coordinate pairs the twelve physical bridges occupy on the cycle is also
NOT derived. The selection rule is exact; the assignment of bridges to channels
is a modelling input still to be fixed.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import combinations, permutations
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "CS7Result",
    "area_two_form",
    "metric_two_form",
    "cs7_density_epsilon",
    "cs7_density_star_phi",
    "cs7_result",
    "associative_triples",
    "allowed_channels",
    "coupling_graph",
    "bridge_placement_spectrum",
    "face_assignment_candidates",
    "vacuum_comparison",
    "write_report",
    "main",
]

#: Wedge-product normalisation for C_3 ^ F_2 ^ F_2 -- 3! x 2! x 2! = 24.
_WEDGE_NORM: float = 24.0


@dataclass(frozen=True)
class CS7Result:
    """Both routes, their agreement, and the honest scope."""

    density_via_epsilon: float
    density_via_star_phi: Optional[float]
    routes_agree: bool
    max_route_discrepancy: float
    volume: float
    action: float
    scope: str = field(
        default=(
            "Flat R^7 with constant coefficients: this is coefficient x "
            "volume, a number, not a topological invariant. It establishes "
            "that the integrand is non-vanishing, not that the term carries "
            "topological content -- that needs a compact G2 manifold."
        )
    )


def _g2():
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )

    return G2DifferentialGeometry()


def area_two_form(L1: float, L2: float, theta: float, i: int, j: int, n: int = 7):
    """Bridge AREA (Kahler) 2-form: magnitude L1*L2*sin(theta).

    This is the channel the topological term couples to. It is MAXIMAL at
    theta = 90 degrees, where the metric channel vanishes.
    """
    import numpy as np

    F = np.zeros((n, n))
    a = L1 * L2 * math.sin(theta)
    F[i, j], F[j, i] = a, -a
    return F


def metric_two_form(L1: float, L2: float, theta: float, i: int, j: int, n: int = 7):
    """Bridge METRIC off-diagonal: magnitude L1*L2*cos(theta).

    Provided for the A/B comparison. It is identically zero at the stabilised
    vacuum, which is the defect this module exists to route around.
    """
    import numpy as np

    F = np.zeros((n, n))
    a = L1 * L2 * math.cos(theta)
    F[i, j], F[j, i] = a, -a
    return F


def cs7_density_epsilon(c3, f_a, f_b) -> float:
    """Route 1 -- the general epsilon contraction. Valid for any C_3."""
    import numpy as np

    from metaphysica.simulations.PM.geometry.exterior_algebra import (
        levi_civita_7d,
    )

    eps = levi_civita_7d()
    return float(
        np.einsum("abcdefg,abc,de,fg->", eps, c3, f_a, f_b) / _WEDGE_NORM
    )


def _wedge_two_two(f_a, f_b):
    """(F_A ^ F_B)_{ijkl}, fully antisymmetrised."""
    import numpy as np

    W = np.einsum("ij,kl->ijkl", f_a, f_b)
    out = np.zeros_like(W)
    for p in permutations(range(4)):
        sign = np.linalg.det(np.eye(4)[list(p)])
        out += sign * np.transpose(W, p)
    return out / 4.0


def cs7_density_star_phi(f_a, f_b, g2=None) -> float:
    """Route 2 -- via the coassociative 4-form, valid when C_3 = phi.

    Uses phi ^ omega = <*phi, omega> vol. Shares no code with route 1 and
    reuses the *phi that g2_differential already computes exactly
    (check_hodge_involution returns max_error = 0.0), so agreement between the
    two is a genuine cross-check.
    """
    import numpy as np

    g2 = g2 or _g2()
    star_phi = g2.compute_hodge_star()
    return float(
        np.einsum("ijkl,ijkl->", star_phi, _wedge_two_two(f_a, f_b)) / _WEDGE_NORM
    )


def cs7_result(f_a, f_b, *, volume: float = 1.0, g2=None, tol: float = 1e-9) -> CS7Result:
    """Evaluate the density by both routes and record their agreement."""
    g2 = g2 or _g2()
    eps_val = cs7_density_epsilon(g2.phi, f_a, f_b)
    star_val = cs7_density_star_phi(f_a, f_b, g2=g2)
    discrepancy = abs(eps_val - star_val)
    scale = max(abs(eps_val), abs(star_val), 1.0)
    return CS7Result(
        density_via_epsilon=eps_val,
        density_via_star_phi=star_val,
        routes_agree=discrepancy / scale < tol,
        max_route_discrepancy=discrepancy,
        volume=volume,
        action=eps_val * volume,
    )


def associative_triples(g2=None) -> List[Tuple[int, int, int]]:
    """The seven index triples on which phi is supported."""
    g2 = g2 or _g2()
    phi = g2.phi
    return [t for t in combinations(range(7), 3) if abs(phi[t]) > 1e-12]


def allowed_channels(g2=None) -> Dict[str, Any]:
    """Enumerate which disjoint (F_A, F_B) placements give a non-zero density.

    Bounded by construction: C(7,2) x C(7,2) = 441 placements, of which 210 are
    disjoint. No search, no convergence loop.
    """
    g2 = g2 or _g2()
    triples = set(associative_triples(g2))
    allowed: List[Dict[str, Any]] = []
    total = 0
    for (i, j) in combinations(range(7), 2):
        for (k, l) in combinations(range(7), 2):
            if len({i, j, k, l}) < 4:
                continue
            total += 1
            complement = tuple(sorted(set(range(7)) - {i, j, k, l}))
            density = cs7_density_epsilon(
                g2.phi, area_two_form(1.0, 1.0, math.pi / 2, i, j),
                area_two_form(1.0, 1.0, math.pi / 2, k, l),
            )
            if abs(density) > 1e-12:
                allowed.append(
                    {"f_a": (i, j), "f_b": (k, l),
                     "complement": complement,
                     "complement_is_associative": complement in triples,
                     "density": density}
                )
    return {
        "n_disjoint_placements": total,
        "n_allowed": len(allowed),
        "selection_rule": (
            "non-zero iff the complementary triple is associative; "
            "7 triples x 6 ordered pair-splits = 42"
        ),
        "channels": allowed,
    }


def coupling_graph(g2=None) -> Dict[str, Any]:
    """The allowed-channel structure as a graph on the 21 coordinate pairs.

    WHAT THIS COMPUTES, and why it matters for the open assignment problem.

    The 42 allowed ordered channels are 21 unordered ones. Treating each
    coordinate pair (i,j) as a vertex and each allowed coupling as an edge
    gives a graph on C(7,2) = 21 vertices with 21 edges, and **every vertex
    has degree exactly 2** -- so it is a disjoint union of cycles. It
    resolves into **seven triangles**, one per coordinate k, whose three
    vertices are a perfect matching of the six points other than k and whose
    three edges are the three Fano lines through k.

    That is the selection rule restated as geometry rather than as a filter:
    phi's seven associative triples ARE the Fano plane, and the coupling
    graph is its point-line incidence turned inside out.

    Consequence for the twelve bridges: they occupy twelve of the
    twenty-one vertices, and the number of live couplings is the number of
    edges internal to that choice. Enumerated over all C(21,12) = 293930
    placements, that count runs from 5 to 12 and is **never zero**, with the
    maximum 12 reached by exactly C(7,4) = 35 placements -- precisely those
    that take four complete triangles.

    Bounded by construction: 21 vertices, 21 edges, C(21,12) placements.
    No search, no convergence loop.
    """
    g2 = g2 or _g2()
    channels = allowed_channels(g2)
    undirected = {
        frozenset((tuple(c["f_a"]), tuple(c["f_b"])))
        for c in channels["channels"]
    }
    adjacency: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
    for edge in undirected:
        a, b = tuple(edge)
        adjacency.setdefault(a, []).append(b)
        adjacency.setdefault(b, []).append(a)

    seen: set = set()
    components: List[List[Tuple[int, int]]] = []
    for vertex in adjacency:
        if vertex in seen:
            continue
        stack, comp = [vertex], []
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            comp.append(node)
            stack.extend(adjacency[node])
        components.append(sorted(comp))

    triples = set(associative_triples(g2))
    described = []
    for comp in sorted(components):
        support = set()
        for pair in comp:
            support |= set(pair)
        omitted = sorted(set(range(7)) - support)
        described.append({
            "vertices": [list(v) for v in comp],
            "support": sorted(support),
            "omitted_point": omitted[0] if len(omitted) == 1 else omitted,
            "edges_are_lines_through_omitted_point": all(
                tuple(sorted(set(range(7)) - (set(a) | set(b)))) in triples
                for a, b in combinations(comp, 2)
            ),
        })

    degrees = {len(v) for v in adjacency.values()}
    return {
        "n_vertices": len(adjacency),
        "n_edges": len(undirected),
        "degrees_present": sorted(degrees),
        "is_two_regular": degrees == {2},
        "n_components": len(components),
        "component_sizes": sorted(len(c) for c in components),
        "components": described,
    }


def bridge_placement_spectrum(n_bridges: int = 12, g2=None) -> Dict[str, Any]:
    """How many couplings survive, over every placement of the bridges.

    Answers the question the Stage-4 report left open -- and, in doing so,
    retires the kill condition that report stated. See the ``kill_condition``
    note in write_report: "if the physical bridges sit only on
    non-associative complements, every channel is forbidden and the route is
    dead" describes an outcome that **cannot occur**. The minimum over all
    C(21,12) placements is five live couplings, never zero.

    A kill condition that cannot fire is not a kill condition, and leaving it
    stated would have been exactly the sort of unfalsifiable guard this
    framework audits out of its own gates.
    """
    from itertools import combinations as _combinations

    graph = coupling_graph(g2)
    vertices = sorted({tuple(v) for comp in graph["components"]
                       for v in map(tuple, comp["vertices"])})
    index = {v: i for i, v in enumerate(vertices)}
    edges = []
    for comp in graph["components"]:
        verts = [tuple(v) for v in comp["vertices"]]
        for a, b in _combinations(verts, 2):
            edges.append((index[a], index[b]))
    # Only edges that are genuinely allowed couplings (triangles are complete)
    channels = allowed_channels(g2)
    allowed_pairs = {
        frozenset((tuple(c["f_a"]), tuple(c["f_b"])))
        for c in channels["channels"]
    }
    edges = [(i, j) for i, j in edges
             if frozenset((vertices[i], vertices[j])) in allowed_pairs]

    histogram: Dict[int, int] = {}
    best, best_selection = -1, None
    for selection in _combinations(range(len(vertices)), n_bridges):
        chosen = set(selection)
        live = sum(1 for i, j in edges if i in chosen and j in chosen)
        histogram[live] = histogram.get(live, 0) + 1
        if live > best:
            best, best_selection = live, selection

    return {
        "n_bridges": n_bridges,
        "n_placements": sum(histogram.values()),
        "live_couplings_histogram": dict(sorted(histogram.items())),
        "minimum": min(histogram),
        "maximum": best,
        "n_maximal_placements": histogram[best],
        "one_maximal_placement": [list(vertices[i]) for i in best_selection],
        "all_channels_forbidden_is_possible": min(histogram) == 0,
    }


def face_assignment_candidates(g2=None) -> Dict[str, Any]:
    """Narrow the four-face choice from 35 to 7 on a symmetry criterion.

    Each triangle T_k is labelled by the coordinate k it OMITS, so choosing
    four faces means choosing a 4-subset of the seven Fano points. Under the
    Fano symmetry those 35 subsets fall into exactly two orbits:

      * **28** that contain a line (three of the four labels collinear)
      * **7** that contain none -- the arcs, and each is precisely the
        complement of one of the seven lines

    So requiring the four face labels to be *generic* -- no three of them
    forming an associative triple -- picks out seven candidates, canonically
    indexed by the single line left over. The three unchosen triangles are
    then exactly that line.

    WHAT THIS DOES AND DOES NOT SETTLE. The 7/28 split is a fact about the
    Fano plane and is computed here, not asserted. Whether the *generic*
    orbit is the physical one is a separate question this cannot answer: it
    needs a reason why three collinear face labels would be disallowed, and
    no such reason is derived anywhere in the framework. The narrowing is
    therefore offered as a criterion with a name, not as a result -- 35 -> 7
    IF genericity holds, and 7 -> 1 would still require fixing which line is
    omitted.
    """
    g2 = g2 or _g2()
    lines = [set(t) for t in associative_triples(g2)]
    all_points = set(range(7))

    generic, line_containing = [], []
    for four in combinations(range(7), 4):
        subset = set(four)
        if any(line <= subset for line in lines):
            line_containing.append(list(four))
        else:
            generic.append(list(four))

    candidates = []
    for four in generic:
        omitted = sorted(all_points - set(four))
        candidates.append({
            "face_labels": list(four),
            "unchosen_triangles": omitted,
            "unchosen_is_a_line": set(omitted) in lines,
        })

    return {
        "n_choices_total": len(generic) + len(line_containing),
        "n_line_containing": len(line_containing),
        "n_generic": len(generic),
        "generic_candidates": candidates,
        "criterion": (
            "no three of the four face labels are collinear in the Fano "
            "plane, i.e. no three form an associative triple of phi"
        ),
        "residual_freedom": (
            "which of the seven lines is the omitted one; the candidates are "
            "in bijection with the lines, so the remaining choice is a "
            "labelling rather than a further structural decision"
        ),
        "status": "CRITERION_STATED_NOT_DERIVED",
        "caveat": (
            "The 7/28 orbit split is computed. That the generic orbit is the "
            "physical one is NOT derived -- nothing in the framework forbids "
            "three collinear face labels. Adopting it narrows 35 -> 7; "
            "without it the choice remains 35."
        ),
    }


def vacuum_comparison(
    channel: Sequence[Tuple[int, int]] = ((0, 1), (3, 6)),
    thetas_deg: Sequence[float] = (10, 30, 45, 60, 80, 89, 90),
) -> Dict[str, Any]:
    """Compare the area and metric channels across theta, at the vacuum moduli.

    The default channel is an ALLOWED one -- complement (2,4,5) is associative.
    Picking a forbidden channel returns zeros for every theta, which says
    nothing about theta and everything about the selection rule.
    """
    from metaphysica.simulations.PM.geometry.bridge_geometry import BridgeSystem

    g2 = _g2()
    moduli, _ = BridgeSystem().stabilize_moduli()
    L1, L2, theta_vac = (float(v) for v in moduli[0])
    (ia, ja), (ib, jb) = channel

    rows = []
    for deg in thetas_deg:
        th = math.radians(deg)
        rows.append({
            "theta_deg": float(deg),
            "area_route": cs7_density_epsilon(
                g2.phi, area_two_form(L1, L2, th, ia, ja),
                area_two_form(L1, L2, th, ib, jb)),
            "metric_route": cs7_density_epsilon(
                g2.phi, metric_two_form(L1, L2, th, ia, ja),
                metric_two_form(L1, L2, th, ib, jb)),
        })

    at_vac = {
        "theta_deg": math.degrees(theta_vac),
        "area_route": cs7_density_epsilon(
            g2.phi, area_two_form(L1, L2, theta_vac, ia, ja),
            area_two_form(L1, L2, theta_vac, ib, jb)),
        "metric_route": cs7_density_epsilon(
            g2.phi, metric_two_form(L1, L2, theta_vac, ia, ja),
            metric_two_form(L1, L2, theta_vac, ib, jb)),
    }
    return {
        "moduli": {"L1": L1, "L2": L2, "theta_rad": theta_vac},
        "channel": {"f_a": tuple(channel[0]), "f_b": tuple(channel[1])},
        "sweep": rows,
        "at_vacuum": at_vac,
        "finding": (
            "The topological channel couples to the bridge AREA "
            "(L1*L2*sin theta) and is MAXIMAL at the orthogonal vacuum, "
            "where the metric channel (L1*L2*cos theta) is identically zero. "
            "The two are exactly complementary."
        ),
    }


def write_report(out_path=None):
    """Emit AutoGenerated/topological_flux.json -- the Stage 4 verdict.

    WHY THIS EXISTS: the evaluation was computable but ephemeral. main()
    printed the answer to stdout and the build never captured it, so the
    one result Priority 1 was gated on left no artifact -- the same class
    of defect as a gate that never runs. Every check below is recomputed
    here rather than restated, and each is a PASS/FAIL the build can trip
    on.

    The FORBIDDEN-channel row is the load-bearing one: a prohibition that
    is exactly zero (not 1e-15) is what distinguishes a real selection
    rule from a coincidence of magnitudes.
    """
    import json
    import os
    from pathlib import Path

    if out_path is None:
        raw = os.environ.get("METAPHYSICA_OUT")
        base = Path(raw).resolve() if raw else Path(__file__).resolve().parents[5]
        out_path = base / "AutoGenerated" / "topological_flux.json"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    from metaphysica.simulations.PM.geometry.bridge_geometry import BridgeSystem

    g2 = _g2()
    moduli, _ = BridgeSystem().stabilize_moduli()
    L1, L2, theta_vac = (float(v) for v in moduli[0])

    channels = allowed_channels(g2)
    vac = vacuum_comparison()

    # Allowed channel at the vacuum, both routes.
    f_a = area_two_form(L1, L2, theta_vac, 0, 1)
    f_b = area_two_form(L1, L2, theta_vac, 3, 6)
    allowed_res = cs7_result(f_a, f_b, g2=g2)

    # Forbidden channel: complement (2,3,4) is NOT an associative triple.
    forbidden_res = cs7_result(
        area_two_form(L1, L2, theta_vac, 0, 1),
        area_two_form(L1, L2, theta_vac, 5, 6),
        g2=g2,
    )

    checks = [
        {
            "id": "coupling_nonzero_at_vacuum",
            "claim": "topological density is non-zero at the theta=90deg vacuum",
            "measured": allowed_res.density_via_epsilon,
            "status": "PASS" if abs(allowed_res.density_via_epsilon) > 1e-9 else "FAIL",
            "note": "the question Priority 1 was gated on; a zero here would "
                    "have been a genuine negative result, recorded as such",
        },
        {
            "id": "two_routes_agree",
            "claim": "epsilon contraction == <*phi, F_A ^ F_B>, sharing no code",
            "measured": allowed_res.max_route_discrepancy,
            "status": "PASS" if allowed_res.routes_agree else "FAIL",
            "note": "phi ^ omega = <*phi, omega> vol; independent derivations, "
                    "so agreement is a cross-check rather than a repeat",
        },
        {
            "id": "selection_rule_42_of_210",
            "claim": "exactly 42 of 210 disjoint channels are non-vanishing",
            "measured": channels["n_allowed"],
            "status": "PASS" if (channels["n_allowed"] == 42
                                 and channels["n_disjoint_placements"] == 210)
                      else "FAIL",
            "note": "7 associative triples x 6 ordered pair-splits, by "
                    "enumeration; not asserted",
        },
        {
            "id": "forbidden_channel_is_exactly_zero",
            "claim": "non-associative complement (2,3,4) gives density == 0",
            "measured": forbidden_res.density_via_epsilon,
            "status": "PASS" if forbidden_res.density_via_epsilon == 0.0 else "FAIL",
            "note": "structural zero, not a tolerance -- the prohibition is "
                    "the clean falsifier of the selection rule",
        },
        {
            "id": "metric_channel_dead_at_vacuum",
            "claim": "the metric route vanishes where the topological one peaks",
            "measured": vac["at_vacuum"]["metric_route"],
            "status": "PASS" if abs(vac["at_vacuum"]["metric_route"]) < 1e-20 else "FAIL",
            "note": "cos(90deg) = 0 -- this is the defect the topological "
                    "route exists to bypass, and why the RP gate reads "
                    "MARGINAL_VACUOUS",
        },
    ]
    n_fail = sum(1 for c in checks if c["status"] == "FAIL")

    payload = {
        "schema_version": 1,
        "term": "int_{Sigma_7} C_3 ^ F_A ^ F_B  with C_3 = phi",
        "degrees": [3, 2, 2],
        "domain_dim": 7,
        "vacuum_moduli": {"L1": L1, "L2": L2,
                          "theta_deg": math.degrees(theta_vac)},
        "channel_evaluated": {"f_a": [0, 1], "f_b": [3, 6],
                              "complement": [2, 4, 5],
                              "complement_is_associative": True},
        "density_via_epsilon": allowed_res.density_via_epsilon,
        "density_via_star_phi": allowed_res.density_via_star_phi,
        "route_discrepancy": allowed_res.max_route_discrepancy,
        "selection_rule": {
            "n_disjoint_placements": channels["n_disjoint_placements"],
            "n_allowed": channels["n_allowed"],
            "rule": channels["selection_rule"],
        },
        "theta_sweep": vac["sweep"],
        "at_vacuum": vac["at_vacuum"],
        "path_a_boundary13": {
            "term": "int_{13} C_3 ^ G_4 ^ G_4 ^ F_2  with G_4 = dC_3",
            "degrees": [3, 4, 4, 2],
            "domain_dim": 13,
            "degree_valid": True,
            "status": "BLOCKED_ON_UNDERIVED_INPUT",
            "blocker": (
                "The calculus layer exists (exterior_algebra.exterior_d) and "
                "the degree gate passes this term, so it is COMPUTABLE the "
                "moment C_3 is supplied. It is not evaluated because the "
                "framework derives no 3-form on the 13D shadow: phi is the "
                "G2 associative 3-form on the 7D cycle (shape (7,7,7)), and "
                "the 13D side carries only the 12 bridge moduli (L1, L2, "
                "theta) -- scalars, not a 3-form. Producing a number here "
                "would require inventing a C_3 ansatz, which is the same "
                "error the Kahler-Ricci ruling forbade. The absence is the "
                "finding; a fabricated evaluation would not be."
            ),
            "unblocks_when": (
                "a C_3 on the 13D shadow is derived from the compactification "
                "rather than posited -- at which point Path A becomes "
                "directly comparable to Path B and the canonical-flux-term "
                "ruling can be made on computed evidence"
            ),
        },
        "verdict": "NONZERO_INTEGRAND_FLAT_R7",
        "count": len(checks),
        "n_pass": len(checks) - n_fail,
        "n_fail": n_fail,
        "checks": checks,
        "scope": CS7Result(0.0, 0.0, True, 0.0, 1.0, 0.0).scope,
        "not_established": (
            "Topological content. Flat R^7 has trivial holonomy and no "
            "non-trivial 7-cycles, so this integral is coefficient x volume. "
            "Harmonic representatives on a compact G2 manifold with b3 = 24 "
            "are required, and that is deferred DEC work. The assignment of "
            "the twelve physical bridges to coordinate channels is also a "
            "modelling input, not derived."
        ),
        "kill_condition_retired": (
            "SUPERSEDED 2026-08-30. This report previously stated: 'if the "
            "bridge-to-channel assignment places the physical bridges only "
            "on complementary NON-associative 4-sets, every channel is "
            "forbidden and this route is dead'. Enumeration over all "
            "C(21,12) = 293930 placements shows that outcome CANNOT OCCUR -- "
            "the live-coupling count runs 5..12 and is never zero. A kill "
            "condition that cannot fire is not a kill condition, and it is "
            "retired here rather than left standing as an unfalsifiable "
            "guard. See coupling_graph / bridge_placement_spectrum."
        ),
        "kill_condition": (
            "The coupling graph is seven disjoint triangles, and the maximum "
            "12 live couplings is reached only by placements that take four "
            "COMPLETE triangles (35 of them, C(7,4)). The framework "
            "independently carries four faces of three bridges each. If the "
            "face grouping, once derived, does NOT correspond to four "
            "complete triangles, then faces and coupling channels are "
            "unrelated structures and the identification proposed in "
            "docs/BRIDGE_CHANNEL_ASSIGNMENT.md is dead -- 35 of the 293930 "
            "placements qualify, so the data can rule it out."
        ),
        "coupling_graph": coupling_graph(g2),
        "face_assignment": face_assignment_candidates(g2),
        "note": (
            "Stage 4 of the action-layer plan. The topological route carries "
            "cross-shadow coupling at the orthogonal vacuum where the metric "
            "route is identically zero; the two are exactly complementary "
            "(area L1*L2*sin theta vs metric L1*L2*cos theta). This answers "
            "the question that gated Priority 1 in the affirmative, at the "
            "scope stated above and no wider."
        ),
    }
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return out_path


def main() -> int:
    g2 = _g2()
    print("=" * 70)
    print(" TOPOLOGICAL CROSS-SHADOW COUPLING  int_Sigma7 phi ^ F_A ^ F_B")
    print("=" * 70)

    triples = associative_triples(g2)
    print(f"  associative triples of phi : {len(triples)}")
    print(f"    {triples}")

    ch = allowed_channels(g2)
    print(f"  disjoint placements        : {ch['n_disjoint_placements']}")
    print(f"  non-vanishing channels     : {ch['n_allowed']}")
    print(f"  selection rule             : {ch['selection_rule']}")

    vac = vacuum_comparison()
    print()
    print(f"  vacuum theta               : "
          f"{math.degrees(vac['moduli']['theta_rad']):.2f} deg")
    print("  theta      area route          metric route")
    for r in vac["sweep"]:
        print(f"  {r['theta_deg']:5.0f}   {r['area_route']: .6e}   "
              f"{r['metric_route']: .6e}")
    print()
    print(f"  AT VACUUM  area={vac['at_vacuum']['area_route']: .6e}   "
          f"metric={vac['at_vacuum']['metric_route']: .6e}")
    print()
    print("  " + vac["finding"])
    print()
    print("  SCOPE: " + CS7Result(0, 0, True, 0, 1, 0).scope)
    out = write_report()
    import json
    payload = json.loads(out.read_text(encoding="utf-8"))
    print()
    print(f"  checks: {payload['n_pass']}/{payload['count']} PASS"
          + (f"  ({payload['n_fail']} FAIL)" if payload["n_fail"] else ""))
    for c in payload["checks"]:
        print(f"    [{c['status']}] {c['id']}")
    print(f"\n  Report written to: {out}")
    return 1 if payload["n_fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
