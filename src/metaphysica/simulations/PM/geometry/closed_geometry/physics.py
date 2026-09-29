"""The scoped physics theorems CG.5-CG.6 (closure plan item G2): what
gauge sector the adopted geometry carries, and whether four-form flux fixes
its moduli. Each states the regime it holds in.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from metaphysica.simulations.PM.geometry.closed_geometry.references import (
    REF_ACHARYA_1999,
    REF_ADV_2005,
    REF_LUKAS_MORRIS,
)
from metaphysica.simulations.PM.geometry.closed_geometry.theorem import (
    Spec,
    Theorem,
    _off_family,
)
from metaphysica.simulations.PM.geometry.closed_geometry.topology import (
    _components_evidence,
)


# ------------------------------------------------------------ gauge content (G2)

_M_THEORY_SCOPE = (
    "M-theory at leading order: the local gauge theory at the orbifold point "
    "and the massless multiplets of the resolved manifold")


def _gauge_evidence() -> Dict[str, Any]:
    ev = _components_evidence()
    if ev["derived"]:
        b1 = {row[1] for row in ev["betti"]}
        ev["component_b1"] = sorted(b1)
        ev["local_susy"] = 1 + max(b1) if b1 else None
        ev["trivial_monodromy"] = ev["orbit_sizes"] in ([4], [])
    return ev


def _gauge_holds(ev: Dict[str, Any]) -> bool:
    if not ev["derived"] or not ev["n_components"]:
        return False
    return (ev["component_b1"] == [3] and ev["trivial_monodromy"]
            and ev["local_susy"] == 4)


def _gauge_statement(ev: Dict[str, Any]) -> str:
    if not ev["derived"]:
        return _off_family(ev)
    if not ev["n_components"]:
        return ("This family member has no singular locus, so no gauge "
                "sector: b_2 = 0 vector multiplets.")
    return (
        "M-theory on the resolved Y_7 gives b_2 = %d U(1) vector multiplets "
        "and b_3 neutral chiral multiplets. At the orbifold point each of the "
        "%d singular loci is C^2/Z_2 x T^3 with trivial monodromy, carrying "
        "SU(2) with 1 + b_1(T^3) = %d fermion zero modes: the content of pure "
        "N = %d super Yang-Mills, which neither confines nor forms a gaugino "
        "condensate. A gaugino-condensation racetrack has no gauge sector to "
        "come from on this geometry; pure N = 1 would need b_1 = 0, the "
        "reflected case that A_1 admissibility excludes."
        % (ev["n_components"], ev["n_components"], ev["local_susy"],
           ev["local_susy"]))


def _gauge_track(ev: Dict[str, Any]) -> Tuple[float, Spec]:
    """1 + b_1 from the computed components vs the closed form 1 + 3."""
    return float(ev["local_susy"]), ("add", 1, 3)


def _gauge_latex(ev: Dict[str, Any]) -> str:
    return (r"\mathcal{N}_{\mathrm{loc}} = 1 + b_1(T^3) = %d,\quad "
            r"G_{\mathrm{res}} = U(1)^{b_2} = U(1)^{%d}"
            % (ev["local_susy"], ev["n_components"]))


# ------------------------------------------------------------ flux runaway (G2)

_FLUX_SCOPE = (
    "classical supergravity at large volume, the leading-order Kahler "
    "potential (Lukas-Morris, to quadratic order in U/T), G4 flux; membrane "
    "instantons and corrections to K are not covered")


def _flux_evidence() -> Dict[str, Any]:
    from metaphysica.simulations.PM.geometry.flux_vacuum import (
        flux_vacuum_report,
    )

    ev = _components_evidence()
    if not ev["derived"]:
        return ev
    rep = flux_vacuum_report()
    ev.update(report=rep, exponent=rep["measured_scaling_exponent"],
              flat_loci=ev["betti"] in ([(1, 3, 3, 1)], []))
    return ev


def _flux_holds(ev: Dict[str, Any]) -> bool:
    if not ev["derived"]:
        return False
    rep = ev["report"]
    return (ev["flat_loci"] and rep["metric_positive_definite"]
            and rep["potential_positive_everywhere_sampled"]
            and rep["controls_find_a_vacuum"]
            and max(rep["worst_residuals"].values()) < 1e-12)


def _flux_statement(ev: Dict[str, Any]) -> str:
    if not ev["derived"]:
        return _off_family(ev)
    return (
        "With the Lukas-Morris Kahler potential for this manifold and the "
        "flux superpotential W = N_i z^i + c, homogeneity of the volume "
        "reduces the potential to V = 4 e^K K^{ij} N_i N_j whenever the "
        "Chern-Simons invariant c is real. It is positive and scales as "
        "lambda^%.0f along the volume ray, so it runs away for every flux: no "
        "metric modulus, Re(T) included, is fixed at leading order. c is real "
        "here because every singular locus is a flat T^3, whose flat SU(2) "
        "connections are abelian. The control with a non-real c finds the "
        "supersymmetric AdS vacuum W = -(2/5) Im c, so the method finds a "
        "vacuum when one exists." % ev["exponent"])


def _flux_track(ev: Dict[str, Any]) -> Tuple[float, Spec]:
    """Measured scaling exponent vs e^K ~ lambda^-7 times K^{ij} ~ lambda^2."""
    return float(round(ev["exponent"], 9)), ("add", -7, 2)


def _flux_latex(ev: Dict[str, Any]) -> str:
    return (r"V = 4\,e^{K} K^{i\bar j} N_i N_j > 0,\quad V(\lambda s) = "
            r"\lambda^{%.0f}\, V(s)" % ev["exponent"])




# ------------------------------------------------------------ derivation steps

def _gauge_steps(ev: Dict[str, Any]) -> List[str]:
    if not ev["derived"]:
        return [_off_family(ev)]
    if not ev["n_components"]:
        return [_gauge_statement(ev)]
    return [
        "M-theory on a smooth G2 manifold gives b_2 U(1) vector multiplets "
        "and b_3 neutral chiral multiplets; here b_2 = %d."
        % ev["n_components"],
        "At the orbifold point each singular locus is C^2/Z_2 x T^3 with "
        "trivial monodromy (y7-singular-components).",
        "Acharya: C^2/Gamma over a 3-manifold M gives the content of pure "
        "N = (1 + b_1(M)) super Yang-Mills; b_1(T^3) = 3 gives N = %d."
        % ev["local_susy"],
        "N = 4 super Yang-Mills does not confine and has no gaugino "
        "condensate, so no condensation racetrack arises.",
    ]


def _flux_steps(ev: Dict[str, Any]) -> List[str]:
    if not ev["derived"]:
        return [_off_family(ev)]
    return [
        "Kahler potential: Lukas-Morris eq. (5.10) for exactly this manifold, "
        "7 bulk and 36 blow-up moduli; homogeneity gives K_i s^i = -7 and "
        "K^{ij} K_j = -s^i.",
        "Superpotential: W = N_i z^i + c (ADV eq. 3.4). c is real because "
        "every singular locus is a flat T^3.",
        "With real c the potential reduces to V = 4 e^K K^{ij} N_i N_j > 0.",
        "V scales as lambda^%.0f along s -> lambda s, so it runs away for "
        "every flux; checked numerically on the Lukas-Morris K."
        % ev["exponent"],
    ]


_GAUGE_TERMS = {
    r"\mathcal{N}_{\mathrm{loc}}": {"symbol": "N_loc", "description": (
        "number of supersymmetries of the gauge theory on one singular "
        "locus: 1 + b_1 of the locus")},
    r"G_{\mathrm{res}}": {"symbol": "G_res", "description": (
        "gauge group of the resolved manifold: one U(1) per H^2 class")},
    "b_1(T^3)": {"symbol": "b_1", "description": (
        "first Betti number of a singular locus")},
}
_FLUX_TERMS = {
    "V": {"symbol": "V", "description": (
        "the four-dimensional N = 1 supergravity potential")},
    "K": {"symbol": "K", "description": (
        "the moduli Kahler potential, -3 ln of the volume")},
    "N_i": {"symbol": "N_i", "description": (
        "integer G4 flux quanta through the 4-cycles")},
    r"\lambda": {"symbol": "lambda", "description": (
        "overall rescaling of the moduli s -> lambda s")},
}


PHYSICS_THEOREMS: Tuple[Theorem, ...] = (
    Theorem(
        id="y7-gauge-content",
        label="(CG.5)",
        title="Gauge content of Y_7",
        counts=(
            "vector multiplets count H^2 classes (b_2); 1 + b_1(Q) counts the "
            "fermion zero modes, i.e. the supersymmetries of the local gauge "
            "theory on a singular locus Q"),
        proof=(
            "Acharya: M-theory on C^2/Gamma fibred over a 3-manifold M gives "
            "one gauge field, 2 b_1(M) scalars and 1 + b_1(M) fermions in the "
            "adjoint, the content of pure N = (1 + b_1) super Yang-Mills. "
            "Every locus here is a flat T^3 with trivial monodromy "
            "(y7-singular-components), so b_1 = 3 and the local theory is "
            "N = 4. On the resolution the 12 SU(2)s break to U(1)^12, with "
            "gauge kinetic functions T^7, T^6, T^5 by blow-up type "
            "(Lukas-Morris eq. 1.3)."),
        test="tests/test_closed_geometry.py::"
             "test_every_theorem_holds_on_the_adopted_seed",
        falsifier=(
            "a singular locus with b_1 = 0 (pure N = 1, which confines and "
            "condenses), or non-trivial monodromy on a component"),
        evidence=_gauge_evidence,
        holds=_gauge_holds,
        statement=_gauge_statement,
        track=_gauge_track,
        latex=_gauge_latex,
        steps=_gauge_steps,
        terms=_GAUGE_TERMS,
        references=(REF_ACHARYA_1999, REF_LUKAS_MORRIS),
        scope=_M_THEORY_SCOPE,
    ),
    Theorem(
        id="y7-flux-potential-runaway",
        label="(CG.6)",
        title="G4 flux fixes no modulus of Y_7 at leading order",
        counts=(
            "s^i are periods of phi (metric moduli); N_i count flux quanta "
            "through 4-cycles; c is a Chern-Simons invariant; the exponent is "
            "the degree of V under s -> lambda s"),
        proof=(
            "K = -3 ln Vol with Vol homogeneous of degree 7/3 gives "
            "K_i s^i = -7 and K^{ij} K_j = -s^i. With real c the F-terms "
            "F_i = N_i + K_i W / 2 give 4 K^{ij} F_i F_j = 4 K^{ij} N_i N_j "
            "+ 3 W^2, so V = 4 e^K K^{ij} N_i N_j > 0; e^K scales as "
            "lambda^-7 and K^{ij} as lambda^2. Checked numerically on the "
            "Lukas-Morris K at random points of its domain."),
        test="tests/test_flux_vacuum.py::"
             "test_the_potential_runs_away_along_the_volume_ray",
        falsifier=(
            "a finite-volume critical point of V with real c for some flux; "
            "or a flat SU(2) connection on T^3 with non-zero Chern-Simons "
            "invariant"),
        evidence=_flux_evidence,
        holds=_flux_holds,
        statement=_flux_statement,
        track=_flux_track,
        latex=_flux_latex,
        steps=_flux_steps,
        terms=_FLUX_TERMS,
        references=(REF_LUKAS_MORRIS, REF_ADV_2005),
        scope=_FLUX_SCOPE,
    ),
)
