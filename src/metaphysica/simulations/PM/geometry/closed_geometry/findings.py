"""Certificate theorems CG.8-CG.11: the findings of G1b, G1, C2 and C3.

Each was pre-registered (site repo docs/DECISION_LOG.md, D-008 .. D-010)
before it was computed. The family-level sweeps are pure functions of the
enumeration, so they are cached once per process.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import functools
import math
from typing import Any, Dict, List, Tuple

from metaphysica.simulations.PM.geometry.closed_geometry.references import (
    REF_ACHARYA_1996,
    REF_ACHARYA_1999,
    REF_ADV_2005,
    REF_JOYCE_1996_II,
    REF_LUKAS_MORRIS,
)
from metaphysica.simulations.PM.geometry.closed_geometry.theorem import (
    Spec,
    Theorem,
    _active,
    _off_family,
)

_WA1_SCOPE = (
    "combinatorial: a theorem about PG(2,2) and the enumeration. Reading one "
    "bridge as one resolved A1 component (one U(1)) is working assumption "
    "WA-1, the author's ruling (D-008)")
_FAMILY_SCOPE = "family-level: holds on every member, whichever seed is active"


@functools.lru_cache(maxsize=None)
def _n3_selection() -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.bridge_component_map import (
        n3_family_selection,
    )

    return n3_family_selection()


@functools.lru_cache(maxsize=None)
def _confinement() -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.gauge_sectors import (
        confinement_sweep,
    )

    return confinement_sweep()


@functools.lru_cache(maxsize=None)
def _acceleration() -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.flux_vacuum import (
        acceleration_report,
    )

    return acceleration_report()


# ------------------------------------------------------------ CG.8 bridges

def _bridge_evidence() -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.bridge_component_map import (
        correspondence,
    )

    path, profile, point = _active()
    ev = {"path": path, "declared": (profile["b2"], profile["b3"]),
          "derived": point is not None}
    if point is not None:
        ev["map"] = correspondence(point)
        ev["family"] = _n3_selection()
    return ev


def _bridge_holds(ev: Dict[str, Any]) -> bool:
    return (ev["derived"] and ev["map"].get("bijection", False)
            and ev["family"]["holds"])


def _bridge_statement(ev: Dict[str, Any]) -> str:
    if not ev["derived"]:
        return _off_family(ev)
    m = ev["map"]
    if not m.get("bijection"):
        return ("This member has no canonical arc: the bridge correspondence "
                "needs three singular involutions (%s)."
                % m.get("reason", "no bijection"))
    t = ev["family"]["tally"]
    return (
        "The three singular Fano lines %s fix the arc %s with complement "
        "%s; each of K4's three perfect matchings (the E8 blocks) holds "
        "exactly one singular side, so blocks and singular involutions "
        "biject, and the 12 bridges match the 12 A1 components as one 3 x 4 "
        "structure. Over every n = 3 class: %d all-plain classes admit it, "
        "%d Example-4 classes do not, so it exists only at (12, 43)."
        % (m["singular_lines"], list(m["canonical_arc"]["arc"]),
           list(m["canonical_arc"]["complement"]),
           t.get("all_plain/bijection", 0), t.get("not_all_plain/none", 0)))


def _bridge_track(ev: Dict[str, Any]) -> Tuple[float, Spec]:
    return float(ev["map"]["n_bridges"]), ("mul", 3, 4)


def _bridge_latex(ev: Dict[str, Any]) -> str:
    return (r"\#\mathrm{bridges} = 3_{E_8\ \mathrm{blocks}} \times 4 = 12 = "
            r"3_{\mathrm{involutions}} \times 4_{\mathrm{components}}")


def _bridge_steps(ev: Dict[str, Any]) -> List[str]:
    if not ev["derived"] or not ev["map"].get("bijection"):
        return [_bridge_statement(ev)]
    return [
        "Three singular involutions spanning Gamma are three non-concurrent "
        "Fano lines, forming a triangle.",
        "The triangle's vertices plus the one point on none of the lines form "
        "an arc; its complement is the line missing all four.",
        "A perfect matching of K4 on the arc pairs one triangle side with one "
        "edge to the missed point, so each E8 block holds one singular side.",
        _bridge_statement(ev),
    ]


_BRIDGE_TERMS = {
    "K_4": {"symbol": "K4", "description": (
        "the complete graph on the arc's four faces; bridges are its "
        "directed edges")},
    "E_8\\ \\mathrm{blocks}": {"symbol": "E8 blocks", "description": (
        "K4's three perfect matchings, labelled by the complement line")},
}


# ------------------------------------------------------------ CG.9 K3 reading

def _k3_evidence() -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.kummer_index import k3_reading

    path, profile, point = _active()
    ev = {"path": path, "declared": (profile["b2"], profile["b3"]),
          "derived": point is not None}
    if point is not None:
        ev["reading"] = k3_reading(point)
    return ev


def _k3_holds(ev: Dict[str, Any]) -> bool:
    r = ev.get("reading", {})
    return (ev["derived"] and r["consistent"]
            and r["n_gen"] == r["n_singular"])


def _k3_statement(ev: Dict[str, Any]) -> str:
    if not ev["derived"]:
        return _off_family(ev)
    r = ev["reading"]
    return (
        "Each of the %d singular involutions acts as -1 on its transverse "
        "T^4 with 16 fixed points (counted); resolving them gives a Kummer "
        "K3 with chi = 24, both from the quotient and from its Betti numbers. "
        "Read as 2 x sum chi(K3) over the two shadows, chi_eff = %d (%d per "
        "shadow) and, on this still-unruled reading, chi_eff/48 = %s: the same statement as counting singular "
        "involutions, and it holds on every class of the family, where b_2/4 "
        "does not. Adopting this as chi_eff's definition is the author's "
        "ruling." % (r["n_singular"], r["chi_eff"], r["per_shadow"],
                     r["n_gen"]))


def _k3_track(ev: Dict[str, Any]) -> Tuple[float, Spec]:
    r = ev["reading"]
    return float(r["chi_eff"]), ("mul", 48, r["n_singular"])


def _k3_latex(ev: Dict[str, Any]) -> str:
    r = ev["reading"]
    return (r"\chi_{\mathrm{eff}} = 2\sum_{\sigma}\chi(K3_\sigma) = 2 \cdot %d "
            r"\cdot 24 = %d,\quad n_{\mathrm{gen}} = \chi_{\mathrm{eff}}/48 = %s"
            % (r["n_singular"], r["chi_eff"], r["n_gen"]))


def _k3_steps(ev: Dict[str, Any]) -> List[str]:
    if not ev["derived"]:
        return [_off_family(ev)]
    return [
        "A singular involution flips four coordinates: on that transverse T^4 "
        "it is the Kummer involution x -> -x + s.",
        "Its 16 fixed points are counted on the quarter lattice.",
        "chi(T^4/{+-1} resolved) = (0 - 16)/2 + 16 + 16 = 24; b_2 = 6 + 16 = "
        "22.",
        _k3_statement(ev),
    ]


_K3_TERMS = {
    "K3_\\sigma": {"symbol": "K3_sigma", "description": (
        "the Kummer surface resolving sigma's transverse T^4/{+-1}")},
    "\\chi_{\\mathrm{eff}}": {"symbol": "chi_eff", "description": (
        "the effective index under the K3 reading (an open ruling)")},
}


# ------------------------------------------------------------ CG.10 confinement

def _conf_evidence() -> Dict[str, Any]:
    return {"derived": True, "sweep": _confinement()}


def _conf_holds(ev: Dict[str, Any]) -> bool:
    s = ev["sweep"]
    return (not s["full_holonomy_can_confine"]
            and 0 in s["min_b1_by_n"].get(1, {}))


def _conf_statement(ev: Dict[str, Any]) -> str:
    s = ev["sweep"]
    return (
        "Pure N = 1 super Yang-Mills, the confining sector every "
        "racetrack-type stabilisation needs, requires a singular locus with "
        "b_1 = 0. Across phi's Joyce family such loci occur only at n = %s; "
        "every n = 3 class has smallest b_1 in %s. Holonomy exactly G2 and a "
        "confining sector are mutually exclusive inside the construction."
        % (s["n_with_a_confining_locus"],
           sorted(s["min_b1_by_n"].get(3, {}))))


def _conf_track(ev: Dict[str, Any]) -> Tuple[float, Spec]:
    confining_at_3 = ev["sweep"]["min_b1_by_n"].get(3, {}).get(0, 0)
    return float(confining_at_3), 0


def _conf_latex(ev: Dict[str, Any]) -> str:
    return (r"\#\{\text{classes with } n = 3,\ b_1(Q) = 0\} = 0,\quad "
            r"\mathcal{N}_{\mathrm{loc}} = 1 + b_1(Q)")


def _conf_steps(ev: Dict[str, Any]) -> List[str]:
    return [
        "Acharya: C^2/{+-1} over Q carries pure N = (1 + b_1(Q)) SYM.",
        "A locus is Q = T^3/Stab; b_1(Q) counts the torus 1-forms every "
        "stabilising element preserves.",
        "Swept over every pairwise-disjoint class of the family.",
        _conf_statement(ev),
    ]


_CONF_TERMS = {
    "b_1(Q)": {"symbol": "b_1(Q)", "description": (
        "first Betti number of a singular locus Q")},
    "\\mathcal{N}_{\\mathrm{loc}}": {"symbol": "N_loc", "description": (
        "supersymmetries of the gauge theory on the locus")},
}


# ------------------------------------------------------------ CG.11 no acceleration

def _acc_evidence() -> Dict[str, Any]:
    return {"derived": True, "report": _acceleration()}


def _acc_holds(ev: Dict[str, Any]) -> bool:
    r = ev["report"]
    return r["bound_respected"] and not r["can_accelerate"]


def _acc_statement(ev: Dict[str, Any]) -> str:
    r = ev["report"]
    return (
        "Homogeneity of the G2 volume gives K_ij s^i s^j = 7 and "
        "s.grad V = -5 V, so the canonical slope of the flux potential obeys "
        "|grad V|/V >= 5 sqrt(2/7) = %.3f everywhere (measured minimum %.3f), "
        "far above the acceleration threshold sqrt(2) = %.3f. The "
        "leading-order flux potential cannot accelerate the universe; dark "
        "energy is open." % (r["bound"], r["min_slope"],
                             r["acceleration_threshold"]))


def _acc_track(ev: Dict[str, Any]) -> Tuple[float, Spec]:
    return 5.0 * math.sqrt(2.0 / 7.0), ("mul", 5, ("pow", 2.0 / 7.0, 0.5))


def _acc_latex(ev: Dict[str, Any]) -> str:
    return (r"\frac{|\nabla V|}{V} \ge 5\sqrt{2/7} \approx 2.673 > \sqrt{2}")


def _acc_steps(ev: Dict[str, Any]) -> List[str]:
    return [
        "K = -3 ln Vol with Vol homogeneous of degree 7/3 gives "
        "K_ij s^i s^j = 7.",
        "V = 4 e^K K^ij N_i N_j scales as lambda^-5, so s.grad V = -5 V.",
        "In the canonical metric K_ij/2 the radial unit vector has norm "
        "sqrt(7/2); the gradient is at least its radial component.",
        _acc_statement(ev),
    ]


_ACC_TERMS = {
    "V": {"symbol": "V", "description": "the flux potential"},
    "\\sqrt{2}": {"symbol": "sqrt(2)", "description": (
        "the slope below which an exponential potential accelerates")},
}


FINDINGS_THEOREMS: Tuple[Theorem, ...] = (
    Theorem(
        id="bridge-component-correspondence", label="(CG.8)",
        title="The 12 bridges and the 12 A1 components are one structure",
        counts=("bridges count directed edges of K4; components count "
                "connected fixed 3-tori; blocks count perfect matchings"),
        proof=("Three non-concurrent Fano lines fix an arc; K4's perfect "
               "matchings each hold one triangle side; both 4-sets per block "
               "are Klein-four torsors."),
        test="tests/test_bridge_component_map.py::"
             "test_the_correspondence_holds_exactly_on_the_all_plain_members",
        falsifier="a block holding 0 or 2 singular sides, or a bijection on a "
                  "non-all-plain n = 3 class",
        evidence=_bridge_evidence, holds=_bridge_holds,
        statement=_bridge_statement, track=_bridge_track,
        latex=_bridge_latex, steps=_bridge_steps, terms=_BRIDGE_TERMS,
        references=(REF_JOYCE_1996_II, REF_LUKAS_MORRIS),
        scope=_WA1_SCOPE),
    Theorem(
        id="k3-reading-generations", label="(CG.9)",
        title="One Kummer K3 per singular involution",
        counts=("fixed points count points; chi counts an alternating sum of "
                "Betti numbers; the factor 2 counts shadows"),
        proof=("Count sigma's transverse fixed points; resolve T^4/{+-1}; "
               "compute chi two ways; sum over singular involutions."),
        test="tests/test_kummer_index.py::"
             "test_the_k3_reading_equals_n_on_every_class",
        falsifier="a singular involution whose transverse quotient is not 16 "
                  "A1 points, or a class where the unruled reading chi_eff/48 != n",
        evidence=_k3_evidence, holds=_k3_holds, statement=_k3_statement,
        track=_k3_track, latex=_k3_latex, steps=_k3_steps, terms=_K3_TERMS,
        references=(REF_ACHARYA_1996,),
        scope="topological; the adoption of this reading as chi_eff is the "
              "author's ruling (D-009)"),
    Theorem(
        id="confinement-exclusion", label="(CG.10)",
        title="Holonomy G2 and a confining sector are mutually exclusive",
        counts="b_1 counts 1-cohomology classes of a locus; n counts "
               "singular involutions",
        proof=("Acharya's local N = 1 + b_1(Q); b_1 of every locus of every "
               "pairwise-disjoint class computed from invariant forms."),
        test="tests/test_gauge_sectors.py::"
             "test_confining_loci_exist_only_without_full_holonomy",
        falsifier="an n = 3 class with a b_1 = 0 locus",
        evidence=_conf_evidence, holds=_conf_holds,
        statement=_conf_statement, track=_conf_track, latex=_conf_latex,
        steps=_conf_steps, terms=_CONF_TERMS,
        references=(REF_ACHARYA_1999,), scope=_FAMILY_SCOPE,
        seed_following=False),
    Theorem(
        id="flux-no-acceleration", label="(CG.11)",
        title="The flux potential cannot accelerate the universe",
        counts="the slope is a dimensionless ratio in Planck units",
        proof=("Homogeneity of the volume bounds the canonical slope below by "
               "its radial component, 5 sqrt(2/7); checked numerically on the "
               "Lukas-Morris Kahler potential."),
        test="tests/test_gauge_sectors.py::"
             "test_the_flux_potential_cannot_accelerate",
        falsifier="a point where |grad V|/V < 5 sqrt(2/7)",
        evidence=_acc_evidence, holds=_acc_holds,
        statement=_acc_statement, track=_acc_track, latex=_acc_latex,
        steps=_acc_steps, terms=_ACC_TERMS,
        references=(REF_LUKAS_MORRIS, REF_ADV_2005),
        scope=("leading-order Kahler potential, single-field reading; "
               "multi-field rapid-turn trajectories are not excluded"),
        seed_following=False),
)
