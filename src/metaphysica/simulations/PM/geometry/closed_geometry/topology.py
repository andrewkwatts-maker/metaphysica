"""The topological theorems CG.1-CG.4: independent of the metric and of
the real form of phi. Each is evidence, a verdict, a rendered statement, a
closed-form track and LaTeX, all read from the live enumeration.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from metaphysica.simulations.PM.geometry.closed_geometry.references import (
    REF_ARMSTRONG,
    REF_JOYCE_1996,
    REF_JOYCE_1996_II,
    REF_JOYCE_2000,
)
from metaphysica.simulations.PM.geometry.closed_geometry.theorem import (
    Spec,
    Theorem,
    _active,
    _fmt,
    _off_family,
)

_TEST = "tests/test_family_topology.py::"


# ------------------------------------------------------------ resolved Betti

def _betti_evidence() -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        flat_betti_report,
    )
    from metaphysica.simulations.PM.geometry.joyce_resolution import (
        resolution_report,
    )

    path, profile, point = _active()
    ev = {"path": path, "declared": (profile["b2"], profile["b3"]),
          "derived": point is not None}
    if point is None:
        return ev
    rep = resolution_report(point)
    ev.update(betti=rep["betti"], duality=rep["poincare_duality_holds"],
              n_components=rep["n_components"],
              flat=dict(flat_betti_report()["flat_betti"]))
    return ev


def _betti_holds(ev: Dict[str, Any]) -> bool:
    return (ev["derived"] and ev["duality"]
            and (ev["betti"][2], ev["betti"][3]) == ev["declared"])


def _betti_statement(ev: Dict[str, Any]) -> str:
    if not ev["derived"]:
        return _off_family(ev)
    return (
        "The resolution Y_7 has Betti numbers b = (%s), derived from Joyce's "
        "resolution formula: the flat sector (%s) of T^7/Gamma plus the "
        "cohomology of each of its %d singular three-tori, shifted up by two "
        "degrees. It reproduces the declared pair (b_2, b_3) = (%d, %d)."
        % (_fmt(ev["betti"]), _fmt(ev["flat"]), ev["n_components"],
           ev["declared"][0], ev["declared"][1]))


def _betti_track(ev: Dict[str, Any]) -> Tuple[float, Spec]:
    """b_3 from the resolution vs b_3^flat + 3 x (number of components)."""
    return (float(ev["betti"][3]),
            ("add", ev["flat"][3], ("mul", 3, ev["n_components"])))


# ------------------------------------------------------------ chi(Y_7) = 0

def _chi_evidence() -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.family_topology import (
        family_table,
    )

    ev = _betti_evidence()
    rows = family_table()
    ev["family"] = [(r["path"], r["derived"], r["euler_characteristic"],
                     r["poincare_duality_holds"]) for r in rows]
    if ev["derived"]:
        ev["chi"] = sum((-1) ** k * b for k, b in ev["betti"].items())
    return ev


def _chi_holds(ev: Dict[str, Any]) -> bool:
    return (ev["derived"] and ev["chi"] == 0
            and all(chi == 0 and dual for _p, _d, chi, dual in ev["family"]))


def _chi_statement(ev: Dict[str, Any]) -> str:
    if not ev["derived"]:
        return _off_family(ev) + (
            " chi = 0 still holds by Poincare duality, as on every closed "
            "odd-dimensional manifold.")
    n_derived = sum(1 for _p, d, _c, _u in ev["family"] if d)
    return (
        "chi(Y_7) = sum (-1)^k b_k = 0. The derived sequence is Poincare-dual "
        "term by term, and each singular three-torus contributes chi(T^3) = 0. "
        "The same holds on all %d derived members of the reachable family. "
        "The effective index published as euler-characteristic (chi_eff) is "
        "a different quantity whose definition is an open ruling." % n_derived)


def _chi_track(ev: Dict[str, Any]) -> Tuple[float, Spec]:
    """The alternating sum vs the same terms regrouped into Poincare-dual
    pairs (b_0 - b_7) + (b_2 - b_5) + (b_4 - b_3) + (b_6 - b_1), each of
    which cancels on its own."""
    b = ev["betti"]
    spec: Spec = 0
    for hi, lo in ((0, 7), (2, 5), (4, 3), (6, 1)):
        spec = ("add", spec, ("sub", b[hi], b[lo]))
    return float(ev["chi"]), spec


# ------------------------------------------------------------ the components

def _components_evidence() -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.joyce_resolution import (
        singular_components,
    )

    path, profile, point = _active()
    ev = {"path": path, "declared": (profile["b2"], profile["b3"]),
          "derived": point is not None}
    if point is None:
        return ev
    rows = singular_components(point)
    ev.update(n_involutions=len(point["singular"]), n_components=len(rows),
              betti=sorted({r["betti"] for r in rows}),
              orbit_sizes=sorted({r["orbit_size"] for r in rows}),
              a1=all(r["a1"] for r in rows))
    return ev


def _components_holds(ev: Dict[str, Any]) -> bool:
    return (ev["derived"] and ev["a1"]
            and ev["betti"] in ([(1, 3, 3, 1)], [])
            and ev["n_components"] == 4 * ev["n_involutions"])


def _components_statement(ev: Dict[str, Any]) -> str:
    if not ev["derived"]:
        return _off_family(ev)
    return (
        "The singular set of T^7/Gamma is %d disjoint three-tori, one Gamma-"
        "orbit of %s fixed tori each, from %d singular involutions. Every one "
        "is an A_1 locus and a flat T^3 with Betti numbers (1, 3, 3, 1), so "
        "b_1 = 3 on each. The resolution adds one 2-class per component "
        "(b_2 = %d) and three 3-classes per component (b_3 = 7 + 3 x %d)."
        % (ev["n_components"], "/".join(str(s) for s in ev["orbit_sizes"]),
           ev["n_involutions"], ev["n_components"], ev["n_components"]))


def _components_track(ev: Dict[str, Any]) -> Tuple[float, Spec]:
    """Counted orbits vs (singular involutions) x (16 tori / orbit size)."""
    per = 16 // max(ev["orbit_sizes"] or [4])
    return float(ev["n_components"]), ("mul", ev["n_involutions"], per)


# ------------------------------------------------------------ pi_1

def _pi1_evidence() -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.family_topology import (
        family_table,
    )
    from metaphysica.simulations.PM.geometry.fundamental_group import (
        pi1_finiteness,
    )

    path, profile, point = _active()
    ev = {"path": path, "declared": (profile["b2"], profile["b3"]),
          "derived": point is not None}
    rows = [r for r in family_table() if r["derived"]]
    ev["finite_members"] = [r["declared"] for r in rows if r["pi1_finite"]]
    ev["flat_ranks"] = [(r["declared"], r["flat_rank_k"]) for r in rows]
    if point is not None:
        pi1 = pi1_finiteness(point)
        ev.update(n_singular=len(point["singular"]),
                  k=pi1["flat_rank_k"], finite=pi1["pi1_finite"],
                  trivial=pi1["pi1_trivial"], agree=pi1["sides_agree"],
                  witness=pi1["surviving_directions"])
    return ev


def _pi1_holds(ev: Dict[str, Any]) -> bool:
    return (ev["derived"] and ev["agree"]
            and ev["k"] == 2 ** (3 - ev["n_singular"]) - 1
            and len(ev["finite_members"]) == 1)


def _pi1_statement(ev: Dict[str, Any]) -> str:
    if not ev["derived"]:
        return _off_family(ev)
    if ev["finite"]:
        here = ("pi_1(Y_7) = 1: the %d singular involutions span Gamma and "
                "flip every coordinate, so every generator of the orbifold "
                "group lies in the subgroup generated by elements with fixed "
                "points" % ev["n_singular"])
    else:
        here = ("pi_1(Y_7) is infinite: coordinate(s) %s are fixed by every "
                "singular involution, and the translation along each survives "
                "with infinite order (k = %d flat directions)"
                % (list(ev["witness"]), ev["k"]))
    return (
        "%s. On representatives of n = 0, 1, 2, 3 singular involutions the "
        "flat ranks are %s: pi_1 is finite exactly when all three generating "
        "involutions are singular (n = 3), and infinite otherwise."
        % (here, ", ".join("%s: %d" % (d, k) for d, k in ev["flat_ranks"])))


def _pi1_track(ev: Dict[str, Any]) -> Tuple[float, Spec]:
    """Counted surviving coordinates vs the closed form 2^(3-n) - 1."""
    return (float(ev["k"]),
            ("sub", ("pow", 2, 3 - ev["n_singular"]), 1))


# ------------------------------------------------------------ LaTeX, from evidence

def _betti_latex(ev: Dict[str, Any]) -> str:
    return (r"b_3(Y_7) = b_3^{\mathrm{flat}} + \sum_j b_1(L_j) = %d + 3 \cdot %d"
            r" = %d,\quad b_2(Y_7) = \sum_j b_0(L_j) = %d"
            % (ev["flat"][3], ev["n_components"], ev["betti"][3],
               ev["betti"][2]))


def _chi_latex(ev: Dict[str, Any]) -> str:
    return r"\chi(Y_7) = \sum_{k=0}^{7} (-1)^k\, b_k(Y_7) = %d" % ev["chi"]


def _components_latex(ev: Dict[str, Any]) -> str:
    per = 16 // max(ev["orbit_sizes"] or [4])
    return (r"n_{\mathrm{comp}} = n_{\mathrm{sing}} \cdot \frac{16}{%d} = "
            r"%d \cdot %d = %d,\quad L_j \cong T^3,\ b_1(L_j) = 3"
            % (16 // per, ev["n_involutions"], per, ev["n_components"]))


def _pi1_latex(ev: Dict[str, Any]) -> str:
    verdict = (r"\pi_1(Y_7) = 1" if ev["finite"]
               else r"|\pi_1(Y_7)| = \infty")
    return (r"k = 2^{3 - n_{\mathrm{sing}}} - 1 = 2^{%d} - 1 = %d "
            r"\;\Rightarrow\; %s" % (3 - ev["n_singular"], ev["k"], verdict))




# ------------------------------------------------------------ derivation steps

def _betti_steps(ev: Dict[str, Any]) -> List[str]:
    if not ev["derived"]:
        return [_off_family(ev)]
    return [
        "Flat sector: the Gamma-invariant constant forms on T^7 give "
        "H^*(T^7/Gamma) = (%s)." % _fmt(ev["flat"]),
        "Singular set: %d flat three-tori L_j, each with Betti numbers "
        "(1, 3, 3, 1) (y7-singular-components)." % ev["n_components"],
        "Resolution: each transverse C^2/{+-1} is replaced by an "
        "Eguchi-Hanson space, whose exceptional 2-class shifts H^*(L_j) up by "
        "two degrees: H^k(Y) = H^k(T^7/Gamma) + sum_j H^{k-2}(L_j).",
        "Result: b(Y_7) = (%s), so (b_2, b_3) = (%d, %d) as declared."
        % (_fmt(ev["betti"]), ev["declared"][0], ev["declared"][1]),
    ]


def _chi_steps(ev: Dict[str, Any]) -> List[str]:
    if not ev["derived"]:
        return [_off_family(ev)]
    return [
        "Take the derived sequence b(Y_7) = (%s)." % _fmt(ev["betti"]),
        "Group the alternating sum into Poincare-dual pairs: (b_0 - b_7) + "
        "(b_2 - b_5) + (b_4 - b_3) + (b_6 - b_1).",
        "Each pair cancels: the flat sector is self-dual, and each singular "
        "T^3 is a closed orientable 3-manifold with chi = 0.",
        "chi(Y_7) = %d, on this member and on every derived member of the "
        "family." % ev["chi"],
    ]


def _components_steps(ev: Dict[str, Any]) -> List[str]:
    if not ev["derived"]:
        return [_off_family(ev)]
    return [
        "Each of the %d singular involutions fixes 16 three-tori in T^7."
        % ev["n_involutions"],
        "Gamma permutes them in orbits of %s; each orbit is one singular "
        "component of the quotient." % "/".join(
            str(s) for s in ev["orbit_sizes"] or [4]),
        "Under A_1 admissibility a torus's stabiliser {1, sigma} acts "
        "trivially on its own coordinates, so each component is a flat T^3.",
        "Result: %d components, each with Betti numbers (1, 3, 3, 1)."
        % ev["n_components"],
    ]


def _pi1_steps(ev: Dict[str, Any]) -> List[str]:
    if not ev["derived"]:
        return [_off_family(ev)]
    return [
        "Armstrong: pi_1(T^7/Gamma) is the affine orbifold group modulo the "
        "subgroup E generated by elements with fixed points; resolving the "
        "A_1 loci leaves it unchanged.",
        "A coordinate fixed by every singular involution survives: projecting "
        "onto it kills E and sends its lattice translation to x -> x + 1.",
        "With %d independent singular involutions, 2^(3-%d) - 1 = %d "
        "coordinates survive." % (ev["n_singular"], ev["n_singular"],
                                  ev["k"]),
        "Hence pi_1(Y_7) is %s on this member, and finite exactly when "
        "n = 3." % ("trivial" if ev["finite"] else "infinite"),
    ]


_BETTI_TERMS = {
    "b_k": {"symbol": "b_k", "description": (
        "k-th Betti number of Y_7: the real dimension of H^k(Y_7)")},
    "L_j": {"symbol": "L_j", "description": (
        "a singular component of T^7/Gamma: a flat three-torus")},
    r"\Gamma": {"symbol": "Gamma", "description": (
        "the (Z/2)^3 group generated by three commuting half-shift "
        "involutions preserving phi")},
}
_CHI_TERMS = {
    r"\chi(Y_7)": {"symbol": "chi", "description": (
        "Euler characteristic: the alternating sum of the Betti numbers")},
    "b_k": _BETTI_TERMS["b_k"],
}
_COMPONENT_TERMS = {
    r"n_{\mathrm{sing}}": {"symbol": "n_sing", "description": (
        "number of involutions in Gamma that have fixed points")},
    r"n_{\mathrm{comp}}": {"symbol": "n_comp", "description": (
        "number of singular components of T^7/Gamma")},
    "L_j": _BETTI_TERMS["L_j"],
}
_PI1_TERMS = {
    "k": {"symbol": "k", "description": (
        "number of coordinates fixed by every singular involution: loops of "
        "infinite order in pi_1")},
    r"\pi_1(Y_7)": {"symbol": "pi_1", "description": (
        "the fundamental group of the resolved manifold")},
    r"n_{\mathrm{sing}}": _COMPONENT_TERMS[r"n_{\mathrm{sing}}"],
}


# ------------------------------------------------------------ the reachable set

def _reach_evidence() -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.joyce_reachability import (
        reachable_set,
    )

    rep = reachable_set()
    by_total: Dict[int, List[int]] = {}
    for b2, b3 in rep["literature_checked"]:
        by_total.setdefault(b2 + b3, []).append(b2)
    # n singular involutions add 16 n to b_2 + b_3 over the flat 7, so each
    # literature-checked line is labelled by the n it comes from.
    lines = {(total - 7) // 16: (min(b2s), max(b2s), [total])
             for total, b2s in sorted(by_total.items())}
    return {"derived": True, "report": rep, "lines": lines,
            "n_checked": len(rep["literature_checked"]),
            "unchecked": rep["only_via_unchecked_stabilisers"]}


def _reach_holds(ev: Dict[str, Any]) -> bool:
    rep = ev["report"]
    return (not rep["b3_24_reachable"]
            and all(len(v[2]) == 1 for v in ev["lines"].values())
            and not set(rep["literature_checked"]) & set(ev["unchecked"]))


def _reach_statement(ev: Dict[str, Any]) -> str:
    rep = ev["report"]
    lines = "; ".join("n = %d: b_2 + b_3 = %d, b_2 = %d..%d" % (
        n, v[2][0], v[0], v[1]) for n, v in sorted(ev["lines"].items()))
    return (
        "Joyce's construction from phi's diagonal (Z/2)^3 -- pairwise-disjoint "
        "singular sets, each family resolved by Eguchi-Hanson spaces with "
        "every admissible lift -- reaches %d literature-checked pairs "
        "(b_2, b_3): %s. The off-path seed b_3 = 24 is %s. The computation "
        "reproduces Joyce's "
        "JDG II Example 4, b_2 = 8 + l, b_3 = 47 - l, by computing each "
        "family's contribution rather than looking it up. %d further pairs "
        "arise only through lifts on order-8 stabilisers that no published "
        "example covers, and are not counted."
        % (ev["n_checked"], lines,
           "not among them" if not rep["b3_24_reachable"] else "REACHABLE",
           len(ev["unchecked"])))


def _reach_track(ev: Dict[str, Any]) -> Tuple[float, Spec]:
    """Counted pairs vs 1 flat point + 3 lines of 9 points."""
    return float(ev["n_checked"]), ("add", 1, ("mul", 3, 9))


def _reach_latex(ev: Dict[str, Any]) -> str:
    return (r"b_2 + b_3 = 7 + 16\,n,\quad n \in \{0,1,2,3\},\quad "
            r"|\mathcal{R}| = 1 + 3 \cdot 9 = %d,\quad 24 \notin b_3"
            r"(\mathcal{R})" % ev["n_checked"])


def _reach_steps(ev: Dict[str, Any]) -> List[str]:
    return [
        "Admissibility is Joyce's Condition 2.1.2: pairwise-disjoint singular "
        "sets. Then every singular point has isotropy {1, sigma}, and any "
        "further stabiliser of a fixed torus acts freely on it.",
        "Each family's resolution adds the part of H^*(T^3) that transforms "
        "by a lift character eps: Stab -> {+-1}, eps(sigma) = +1: plain tori "
        "give (1, 3); T^3/Z_2 gives (1, 1) or (0, 2), Joyce's eq. (27).",
        "Summing over families and lifts, class by class, gives b_2 + b_3 = "
        "7 + 16 n for n singular involutions.",
        _reach_statement(ev),
    ]


_REACH_TERMS = {
    r"\mathcal{R}": {"symbol": "R", "description": (
        "the set of (b_2, b_3) Joyce's construction reaches from phi's "
        "(Z/2)^3, counting literature-checked lifts only")},
    "n": {"symbol": "n", "description": (
        "number of singular involutions of an admissible assignment")},
    "b_2 + b_3": {"symbol": "b_2 + b_3", "description": (
        "total Betti number of degrees 2 and 3, fixed by n")},
}


TOPOLOGY_THEOREMS: Tuple[Theorem, ...] = (
    Theorem(
        id="y7-resolved-betti-numbers",
        label="(CG.1)",
        title="Resolved Betti numbers of Y_7",
        counts="b_k counts real cohomology classes of degree k",
        proof=(
            "Joyce's resolution formula H^k(Y) = H^k(T^7/Gamma) + sum_j "
            "H^{k-2}(L_j): the flat sector is the Gamma-invariant constant "
            "forms; each singular component L_j contributes its own "
            "cohomology, computed from its stabiliser's action on the fixed "
            "coordinates, tensored with the exceptional 2-class of the "
            "Eguchi-Hanson space that resolves the transverse C^2/{+-1}."),
        test=_TEST + "test_the_resolved_sequence_has_the_predicted_shape",
        falsifier=(
            "a derived (b_2, b_3) that differs from the declared seed, or a "
            "sequence that is not Poincare-dual"),
        evidence=_betti_evidence,
        holds=_betti_holds,
        statement=_betti_statement,
        track=_betti_track,
        latex=_betti_latex,
        steps=_betti_steps,
        terms=_BETTI_TERMS,
        references=(REF_JOYCE_1996, REF_JOYCE_2000),
    ),
    Theorem(
        id="y7-euler-characteristic",
        label="(CG.2)",
        title="Euler characteristic of Y_7",
        counts="an Euler characteristic: the alternating sum of Betti numbers",
        proof=(
            "Sum (-1)^k b_k over the derived sequence. It vanishes because the "
            "flat sector is self-dual and each singular component is a closed "
            "orientable 3-manifold with chi = 0; a stabiliser acting with the "
            "wrong orientation would break the duality visibly."),
        test=_TEST + "test_poincare_duality_and_chi_zero_on_every_profile",
        falsifier="any family member with a non-zero alternating sum",
        evidence=_chi_evidence,
        holds=_chi_holds,
        statement=_chi_statement,
        track=_chi_track,
        latex=_chi_latex,
        steps=_chi_steps,
        terms=_CHI_TERMS,
        references=(REF_JOYCE_2000,),
    ),
    Theorem(
        id="y7-singular-components",
        label="(CG.3)",
        title="Singular components of T^7/Gamma",
        counts=(
            "components count connected 3-tori of the singular set; b_1 "
            "counts each component's 1-cohomology classes"),
        proof=(
            "Each singular involution fixes 16 three-tori; Gamma permutes "
            "them, and each orbit is one component of the quotient. Under A_1 "
            "admissibility the stabiliser of a torus is {1, sigma}, which "
            "acts trivially on the fixed coordinates, so every component is "
            "a flat T^3 and every orbit has 4 elements."),
        test=_TEST + "test_the_adopted_point_has_twelve_components_each_"
                     "with_b1_three",
        falsifier="a component with b_1 != 3, or an orbit that is not free",
        evidence=_components_evidence,
        holds=_components_holds,
        statement=_components_statement,
        track=_components_track,
        latex=_components_latex,
        steps=_components_steps,
        terms=_COMPONENT_TERMS,
        references=(REF_JOYCE_1996,),
    ),
    Theorem(
        id="y7-fundamental-group",
        label="(CG.4)",
        title="Fundamental group of Y_7 across the family",
        counts=(
            "k counts coordinates of T^7 left unflipped by every singular "
            "involution: loops of infinite order. pi_1 is finite iff k = 0"),
        proof=(
            "Armstrong: pi_1 of the quotient is the orbifold group modulo the "
            "subgroup generated by elements with fixed points, and resolving "
            "A_1 loci does not change it. Along a coordinate fixed by every "
            "singular involution, the projection to Isom(R) kills that "
            "subgroup and sends the lattice translation to x -> x + 1, so "
            "pi_1 is infinite. With no such coordinate the singular "
            "involutions span Gamma and pi_1 = 1. Singular involutions are "
            "independent over F_2, so k = 2^(3-n) - 1 for n of them."),
        test=_TEST + "test_pi1_is_finite_exactly_at_the_adopted_pair",
        falsifier=(
            "an assignment with n < 3 and finite pi_1, or an admissible "
            "assignment with dependent singular involutions"),
        evidence=_pi1_evidence,
        holds=_pi1_holds,
        statement=_pi1_statement,
        track=_pi1_track,
        latex=_pi1_latex,
        steps=_pi1_steps,
        terms=_PI1_TERMS,
        references=(REF_ARMSTRONG, REF_JOYCE_1996),
    ),
    Theorem(
        id="joyce-reachable-set",
        label="(CG.7)",
        title="What Joyce's construction reaches from phi's (Z/2)^3",
        counts=(
            "pairs (b_2, b_3) count cohomology classes; n counts singular "
            "involutions (group elements)"),
        proof=(
            "Enumerate every conjugacy class of half-shift actions of phi's "
            "diagonal (Z/2)^3; keep the pairwise-disjoint ones (Joyce's "
            "Condition 2.1.2); for each family compute the lift-character "
            "cohomology of T^3/Stab and sum over families and lifts. The "
            "result is checked against Joyce's JDG II Example 4 by "
            "computation, and matches an independent red-team enumeration."),
        test="tests/test_joyce_reachability.py::"
             "test_the_literature_checked_set_is_the_three_lines",
        falsifier=(
            "an admissible class reaching the off-path seed b_3 = 24, or a "
            "computed contribution that disagrees with Joyce's eq. (27)"),
        evidence=_reach_evidence,
        holds=_reach_holds,
        statement=_reach_statement,
        track=_reach_track,
        latex=_reach_latex,
        steps=_reach_steps,
        terms=_REACH_TERMS,
        references=(REF_JOYCE_1996, REF_JOYCE_1996_II),
        seed_following=False,
    ),
)
