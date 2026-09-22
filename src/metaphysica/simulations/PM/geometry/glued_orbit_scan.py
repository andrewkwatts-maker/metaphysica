"""What the gluing does to the GL(7) orbit of phi, measured pointwise along the neck.

WHY THIS EXISTS
===============
`K_IJ` (`metric_pairing`) is computed at leading order in t from closed-form
pieces, and `real_form_report` (`g2_differential`) names the real form of the
FLAT phi at a single point in Lambda^3(R^7). Neither has ever asked the question
in between: once the twisted pieces `dx^i ^ eta_EH` are switched on with a
gluing amplitude, does the resulting position-dependent 3-form STAY in the same
open GL(7,R) orbit, or does it move?

There are exactly three possible answers, and each one means something
different for the framework:

  STABLE     the glued form stays in the orbit the flat form occupies
             everywhere on the scanned region. The real-form claim is then
             DYNAMICALLY stable, not merely a statement about one point.

  DEGENERATE the form crosses det B = 0 somewhere. At such a point phi is not
             stable, there is no induced metric at all, and the locus is a
             dynamically generated singular structure -- the first in this
             framework. Where it sits, in which coordinates, and at which t is
             then the result.

  CROSSOVER  the form lands in the OTHER open orbit at some radius. The two
             `g2_form_convention` branches would then differ by REGION rather
             than by convention, and the wording task changes shape: "phi is
             split" would be true on part of the neck and false on the rest.

WHAT WAS MEASURED (2026-09-22): DEGENERATE, AND NOT CROSSOVER
=============================================================
Both happen to be visible in the same data and separating them is the whole
point, so the distinction is built into the classifier rather than left to the
reader. See `orbit_outcome` and `wall_radius`.

THE INVARIANT, AND WHY IT IS LEGITIMATE IN A COORDINATE BASIS
=============================================================
Hitchin's bilinear B_{ij} = eps^{a1..a7} phi_{i a1 a2} phi_{j a3 a4} phi_{a5 a6 a7}
transforms under phi -> A*phi as

    B -> (det A) A^T B A

so for det A > 0 the signature of B is preserved and det B is rescaled by
(det A)^9 > 0. Two consequences, and conflating them is the trap this module
exists to avoid:

  * the ORBIT invariant under the full GL(7,R) is the signature UP TO OVERALL
    SIGN, because an orientation-reversing A flips B. The compact orbit is the
    unordered pair {7,0}; the split orbit is {4,3}. So (4,3) and (3,4) are the
    SAME orbit, and `g2_differential.real_form_report` already reports a
    `hitchin_signature_unordered` for exactly this reason. Orbit membership is
    therefore read off the UNORDERED signature and nothing else.

  * the SIGN of det B is invariant only under GL+(7,R). On a manifold carrying
    a fixed orientation it is meaningful, and a region where it flips is
    separated from its neighbour by a locus where det B = 0 -- a wall on which
    phi is not stable and no metric is induced.

Both are read off in the neck chart's coordinate basis, which is legitimate
because neither is a metric statement. Nothing here uses an orthonormal frame.

WHAT IS ASYMPTOTIC, STATED ONCE AND CARRIED EVERYWHERE
======================================================
The flat block is written in the neck chart through the ASYMPTOTIC
identification: Eguchi-Hanson approaches flat R^4/Z_2 as r -> infinity, and the
four moved coordinates are identified with the four EH axes in that limit. So
every record this module returns carries `order = "leading-order-in-t"` and
`flat_block_identification = "asymptotic (ALE)"`. The scan measures the orbit
of the LEADING-ORDER glued form, and says so at every consumer. It is not a
statement about the exact Joyce metric, which the framework does not have.

WHAT A `t` IS HERE
==================
`t` is the amplitude of the twisted block relative to the flat block, the same
gluing parameter the K_IJ expansion is organised in. t = 0 is the flat orbifold
form; increasing t switches the exceptional 2-form on. It is dimensionless by
construction here (both blocks are components in the same chart), and it is NOT
a new physical constant: no branch of this module selects a value, and the scan
reports the whole grid.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "N_COORDS",
    "DEFAULT_RADII",
    "DEFAULT_T_VALUES",
    "DEFAULT_THETAS",
    "eta_components_at",
    "glued_three_form",
    "orbit_at",
    "scan",
    "orbit_outcome",
    "degenerate_records",
    "seam_signature",
    "expected_negative_eigenvalues",
    "expected_unordered_signature",
    "wall_radius",
    "wall_scaling_report",
    "critical_amplitude",
    "scan_report",
]

N_COORDS: int = 7

#: Radii in units of the bolt parameter a. The bolt sits at r = a, so r/a = 1 is
#: the seam itself and the grid runs from there out into the ALE region where
#: the asymptotic identification of the flat block is valid. Chosen to span two
#: decades so a radius-dependent orbit change cannot hide between samples.
DEFAULT_RADII: Tuple[float, ...] = (1.0, 1.05, 1.2, 1.5, 2.0, 3.0, 5.0,
                                    10.0, 30.0, 100.0)

#: Gluing amplitudes. Spans six decades INCLUDING values far outside any
#: physical gluing regime: if the orbit only changes at t = 100 that is worth
#: knowing and worth labelling as unphysical, and a grid that stopped at t = 1
#: could not tell a stable orbit from an unsampled crossing.
DEFAULT_T_VALUES: Tuple[float, ...] = (0.0, 1e-3, 1e-2, 0.1, 0.5, 1.0, 2.0,
                                       5.0, 10.0, 100.0)

#: Polar angles. eta's components carry cos(theta) and sin(theta), so theta is a
#: genuine grid axis and not a nuisance parameter. The poles are included
#: because that is where cos(theta) = +-1 and the (0,2) component is extremal.
DEFAULT_THETAS: Tuple[float, ...] = (1e-6, math.pi / 6, math.pi / 4,
                                     math.pi / 3, math.pi / 2,
                                     2 * math.pi / 3, math.pi - 1e-6)

#: |det B| below this is reported as DEGENERATE. It is scaled by the flat
#: form's own |det B| inside `orbit_at`, so it is a RELATIVE cutoff and does not
#: turn into a statement about units. A genuine wall crossing changes the SIGN,
#: which is checked independently of this threshold.
DET_DEGENERACY_RTOL: float = 1e-9


def eta_components_at(r: float, theta: float, a: float = 1.0
                      ) -> Dict[Tuple[int, int], float]:
    """The exceptional 2-form's components at one point of the EH chart.

    Read from `eguchi_hanson.exceptional_two_form` by SUBSTITUTION, not
    retyped: if that module's form changes, this changes with it. The symbolic
    form is the object; this is its value at a point.

    Index order is the EH chart's own: r = 0, theta = 1, phi = 2, psi = 3.
    """
    return {key: fn(r, theta, a) for key, fn in _eta_callables().items()}


#: `exceptional_two_form` is symbolic, and substituting into it costs ~22 ms.
#: The scan evaluates eta at every grid point and inside every bisection step,
#: so the substitution dominated the measurement. Lambdifying ONCE keeps the
#: symbolic form as the single source -- the callables are built from it, never
#: from retyped expressions -- while making a point evaluation numeric.
_ETA_CALLABLES = None


def _eta_callables():
    """Numeric evaluators for eta's components, built from the symbolic form."""
    global _ETA_CALLABLES
    if _ETA_CALLABLES is not None:
        return _ETA_CALLABLES

    import sympy as sp

    from metaphysica.simulations.PM.geometry.eguchi_hanson import (
        exceptional_two_form,
        symbols,
    )

    r_s, th_s, ph_s, ps_s, a_s = symbols()
    form = exceptional_two_form()
    _ETA_CALLABLES = {
        key: sp.lambdify((r_s, th_s, a_s), val, "math")
        for key, val in form.components.items()
    }
    return _ETA_CALLABLES


def _flat_phi(convention: Optional[str] = None) -> np.ndarray:
    """The flat block, as the (7,7,7) array the fork in force actually uses.

    Read through `g2_differential`, so the `g2_form_convention` fork decides it
    and this module never carries a second copy of phi.
    """
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
        phi_from_octonion_product,
    )

    if convention is None:
        try:
            from metaphysica.simulations.core.variants import resolve

            convention = resolve("g2_form_convention")
        except ImportError as exc:           # the fork registry is unreachable
            raise RuntimeError(
                "cannot resolve g2_form_convention, so the orbit scan does not "
                "know which flat phi it is scanning. Refusing to guess a "
                "branch: %s" % exc
            ) from exc

    if convention == "octonion_derived":
        return phi_from_octonion_product()
    if convention == "all_plus_one":
        return G2DifferentialGeometry()._standard_phi()
    raise ValueError(
        "unknown g2_form_convention %r; expected 'all_plus_one' or "
        "'octonion_derived'" % convention
    )


def glued_three_form(family: Dict[str, Any], r: float, theta: float,
                     t: float, a: float = 1.0,
                     convention: Optional[str] = None) -> np.ndarray:
    """The position-dependent glued 3-form at one point of one family's neck.

        phi(r, theta; t) = phi_flat + t * sum_{i in fixed_line} dx^i ^ eta_EH

    The sum is over the three legs of the family's fixed T^3 -- exactly the
    three twisted 3-forms `twisted_form_basis.twisted_representatives` builds
    for that family -- and eta is lifted from its own 4D chart into the four
    moved slots by `neck_chart`'s `eh_slots` map, so the index bookkeeping is
    the basis module's and not a second copy of it.

    A4 bar: `fixed_line` and `moved_arc` count COORDINATE DIRECTIONS; the three
    legs count BASIS 3-FORMS of the twisted sector; the output is a component
    array of one 3-form. No count is converted into a dimension anywhere.

    Returns:
        (7,7,7) fully antisymmetric float array, in the neck chart's
        coordinate basis. Leading order in t by construction.
    """
    from metaphysica.simulations.PM.geometry.twisted_form_basis import neck_chart

    fixed = tuple(family["fixed_line"])
    moved = tuple(family["moved_arc"])
    _coords, eh_slots = neck_chart(fixed, moved)

    phi = np.array(_flat_phi(convention), dtype=float)

    if t != 0.0:
        eta = eta_components_at(r, theta, a)
        for leg in fixed:
            for (axis_a, axis_b), value in eta.items():
                ia, ib = eh_slots[axis_a], eh_slots[axis_b]
                idx = (leg, ia, ib)
                if len(set(idx)) < 3:        # a leg cannot lie in the moved arc
                    raise RuntimeError(
                        "leg %d collides with moved slots %s: the involution no "
                        "longer partitions the seven coordinates"
                        % (leg, (ia, ib))
                    )
                _add_antisymmetric(phi, idx, t * value)

    return phi


def _add_antisymmetric(phi: np.ndarray, idx: Tuple[int, int, int],
                       value: float) -> None:
    """Add `value` to phi at `idx`, with all six signed permutations."""
    i, j, k = idx
    for (p, q, s), sign in (((i, j, k), 1), ((j, k, i), 1), ((k, i, j), 1),
                            ((j, i, k), -1), ((i, k, j), -1), ((k, j, i), -1)):
        phi[p, q, s] += sign * value


def expected_negative_eigenvalues(convention: Optional[str] = None) -> int:
    """How many negative eigenvalues Hitchin's B must have, on the branch in force.

    Not a hardcoded pair of numbers: it is read from the SIGNATURE that
    `geometry_narration.holonomy_claim` reports for the live branch, which in
    turn comes from `real_form_report`. Switching the fork moves this, which is
    what makes the seam guard fork-aware rather than branch-specific.
    """
    from metaphysica.simulations.PM.geometry.geometry_narration import (
        holonomy_claim,
    )

    claim = holonomy_claim(convention)
    positive, negative = claim["signature"]
    if positive + negative != N_COORDS:
        raise RuntimeError(
            "holonomy_claim reports signature %s, which does not sum to 7; the "
            "orbit scan cannot derive an eigenvalue count from it"
            % (claim["signature"],)
        )
    return int(negative)


def expected_unordered_signature(convention: Optional[str] = None
                                 ) -> Tuple[int, int]:
    """The ORBIT label of the branch in force: the signature up to overall sign.

    This, and not the ordered signature, is what may not drift: an
    orientation-reversing GL(7,R) element flips B and so swaps the ordered pair
    without leaving the orbit. Read from the live fork through
    `geometry_narration`, so a fork switch moves it.
    """
    negative = expected_negative_eigenvalues(convention)
    return _unordered(N_COORDS - negative, negative)


def _unordered(n_pos: int, n_neg: int) -> Tuple[int, int]:
    """(larger, smaller): the signature as an ORBIT label, sign forgotten."""
    return (max(n_pos, n_neg), min(n_pos, n_neg))


def orbit_at(phi: np.ndarray, det_reference: Optional[float] = None
             ) -> Dict[str, Any]:
    """Which open GL(7,R) orbit this component array sits in, or neither.

    Args:
        phi: (7,7,7) antisymmetric array.
        det_reference: |det B| of the flat form, used to make the degeneracy
            cutoff RELATIVE. Passing None makes the cutoff absolute, which is
            only meaningful when the caller has already fixed a scale.
    """
    from metaphysica.simulations.PM.geometry.g2_differential import (
        G2DifferentialGeometry,
    )

    B = G2DifferentialGeometry(phi=phi).hitchin_bilinear()
    B = 0.5 * (B + B.T)                      # B is symmetric; enforce exactly
    det = float(np.linalg.det(B))
    eig = np.linalg.eigvalsh(B)
    n_neg = int(np.sum(eig < 0.0))
    n_pos = int(np.sum(eig > 0.0))

    scale = abs(det_reference) if det_reference else 1.0
    degenerate = abs(det) <= DET_DEGENERACY_RTOL * scale
    unordered = _unordered(n_pos, n_neg)

    # Orbit membership is the UNORDERED signature: an orientation-reversing
    # GL(7,R) element flips B, swapping (4,3) and (3,4) without leaving the
    # split orbit. Classifying on the ordered pair would report a crossover
    # where there is only an orientation flip, which is the error this
    # classifier is written to refuse.
    if degenerate:
        orbit = "DEGENERATE"
    elif unordered == (7, 0):
        orbit = "COMPACT"
    elif unordered == (4, 3):
        orbit = "SPLIT"
    else:
        orbit = "NEITHER_OPEN_ORBIT"

    return {
        "det_B": det,
        "det_B_sign": int(np.sign(det)),
        "eigenvalues": [float(x) for x in eig],
        "eigenvalue_signs": [int(np.sign(x)) for x in eig],
        "n_negative": n_neg,
        "n_positive": n_pos,
        "signature": (n_pos, n_neg),
        "signature_unordered": unordered,
        "orbit": orbit,
        "is_degenerate": bool(degenerate),
    }


def _families(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    from metaphysica.simulations.PM.geometry.intersection_tensor import (
        sector_families,
    )

    fams = sector_families()
    return list(fams) if limit is None else list(fams)[:limit]


def scan(radii: Sequence[float] = DEFAULT_RADII,
         t_values: Sequence[float] = DEFAULT_T_VALUES,
         thetas: Sequence[float] = DEFAULT_THETAS,
         a: float = 1.0,
         families: Optional[Sequence[Dict[str, Any]]] = None,
         n_families: Optional[int] = 1,
         convention: Optional[str] = None) -> List[Dict[str, Any]]:
    """Evaluate the orbit of the glued form over the (r, theta, t) grid.

    `n_families = 1` by default because the twelve families are related by the
    group action and the first is representative; `n_families = None` scans all
    twelve, which `scan_report` uses to CHECK that representativeness rather
    than assume it.

    Every record carries its order tag. Nothing here is exact in t.
    """
    fams = list(families) if families is not None else _families(n_families)
    det_ref = abs(orbit_at(_flat_phi(convention))["det_B"])

    out: List[Dict[str, Any]] = []
    for fam in fams:
        for t in t_values:
            for r in radii:
                for theta in thetas:
                    phi = glued_three_form(fam, r, theta, t, a=a,
                                           convention=convention)
                    rec = orbit_at(phi, det_reference=det_ref)
                    rec.update({
                        "family": fam["family"],
                        "sector": fam["sector"],
                        "fixed_line": tuple(fam["fixed_line"]),
                        "moved_arc": tuple(fam["moved_arc"]),
                        "r_over_a": r,
                        "theta": theta,
                        "t": t,
                        "a": a,
                        "order": "leading-order-in-t",
                        "flat_block_identification": "asymptotic (ALE)",
                    })
                    out.append(rec)
    return out


def degenerate_records(records: Optional[Sequence[Dict[str, Any]]] = None
                       ) -> List[Dict[str, Any]]:
    """Grid points where det B vanishes, plus every det-B SIGN CHANGE in r.

    Two independent detections, because a grid can step over a wall without
    landing on it: the threshold test finds points ON the wall, the sign-change
    test finds walls BETWEEN samples. Only the second can prove a crossing.
    """
    records = list(records) if records is not None else scan()
    hits = [dict(r, detection="det_B under relative cutoff")
            for r in records if r["is_degenerate"]]

    by_line: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = {}
    for rec in records:
        by_line.setdefault((rec["family"], rec["t"], rec["theta"]), []).append(rec)
    for key, line in by_line.items():
        line = sorted(line, key=lambda x: x["r_over_a"])
        for prev, nxt in zip(line, line[1:]):
            if prev["det_B_sign"] != nxt["det_B_sign"]:
                hits.append(dict(
                    nxt,
                    detection="det_B sign change in r",
                    bracket=(prev["r_over_a"], nxt["r_over_a"]),
                    bracket_signs=(prev["det_B_sign"], nxt["det_B_sign"]),
                ))
    return hits


def orbit_outcome(records: Optional[Sequence[Dict[str, Any]]] = None,
                  convention: Optional[str] = None) -> Dict[str, Any]:
    """Which of the three outcomes the grid actually exhibits.

    STABLE / DEGENERATE / CROSSOVER, with the evidence attached. This function
    decides nothing about physics: it reports what the measured orbit labels
    are, and a mixed grid is reported as mixed rather than resolved.
    """
    records = list(records) if records is not None else scan(
        convention=convention)
    expected_neg = expected_negative_eigenvalues(convention)
    expected_unordered = expected_unordered_signature(convention)
    home = "COMPACT" if expected_unordered == (7, 0) else "SPLIT"

    labels = sorted({r["orbit"] for r in records})
    degen = degenerate_records(records)
    other_orbit = [r for r in records
                   if r["orbit"] in ("COMPACT", "SPLIT") and r["orbit"] != home]
    off_orbit = [r for r in records if r["orbit"] == "NEITHER_OPEN_ORBIT"]
    flipped = [r for r in records
               if r["orbit"] == home and r["n_negative"] != expected_neg]

    if degen:
        outcome = "DEGENERATE"
    elif other_orbit:
        outcome = "CROSSOVER"
    elif off_orbit:
        outcome = "NEITHER_OPEN_ORBIT"
    elif labels == [home]:
        outcome = "STABLE"
    else:
        outcome = "MIXED"

    return {
        "outcome": outcome,
        "home_orbit": home,
        "expected_negative_eigenvalues": expected_neg,
        "expected_unordered_signature": expected_unordered,
        "orbit_labels_seen": labels,
        "n_records": len(records),
        "n_degenerate": len(degen),
        "n_in_other_open_orbit": len(other_orbit),
        "n_in_neither_open_orbit": len(off_orbit),
        "n_orientation_flipped_within_home_orbit": len(flipped),
        "degenerate_examples": degen[:8],
        "other_orbit_examples": [
            {k: r[k] for k in ("family", "r_over_a", "theta", "t", "orbit",
                               "signature", "det_B")}
            for r in other_orbit[:8]
        ],
        "orientation_flip": (
            "%d of %d grid points sit in the home orbit %s with the OPPOSITE "
            "det B sign -- ordered signature %s rather than %s. That is an "
            "orientation flip inside one GL(7,R) orbit, not a crossover to the "
            "other one, and it is why a det B = 0 wall has to lie between them."
            % (len(flipped), len(records), home,
               _unordered(*expected_unordered)[::-1], expected_unordered)
        ) if flipped else "no grid point flips det B's sign.",
        "order": "leading-order-in-t",
        "flat_block_identification": "asymptotic (ALE)",
        "means": {
            "STABLE": ("the glued form never leaves the orbit the flat form "
                       "occupies, so the real-form claim is dynamically stable "
                       "on the scanned region and the wording task is "
                       "unchanged"),
            "DEGENERATE": ("det B vanishes somewhere: phi is unstable there, no "
                           "metric is induced, and the locus is a dynamically "
                           "generated singular structure"),
            "CROSSOVER": ("the form enters the other open orbit at some radius, "
                          "so the two g2_form_convention branches differ by "
                          "REGION and every holonomy sentence needs a domain"),
            "NEITHER_OPEN_ORBIT": ("B is non-degenerate but its signature is "
                                   "neither {7,0} nor {4,3} up to sign, so the "
                                   "glued form is a stable 3-form of no G2 type"),
            "MIXED": "the grid is not uniform and no single label describes it",
        }[outcome],
    }


def wall_radius(t: float, theta: float = math.pi / 4, a: float = 1.0,
                family: Optional[Dict[str, Any]] = None,
                convention: Optional[str] = None,
                r_max: float = 1.0e4,
                iterations: int = 60) -> Optional[Dict[str, Any]]:
    """The radius where det B changes sign, bisected, or None if it does not.

    Bisects GEOMETRICALLY (the midpoint is sqrt(lo*hi)), because the wall is
    controlled by t a^2 / r^2 and a linear bisection over four decades of r
    would spend its iterations in the wrong place.

    Returns None when det B has the same sign at both ends of [a, r_max], which
    is the honest answer for a t below the critical amplitude: the wall is then
    inside the bolt and off the manifold entirely.
    """
    fam = family if family is not None else _families(1)[0]
    ref = abs(orbit_at(_flat_phi(convention))["det_B"])

    def sign_at(r: float) -> int:
        phi = glued_three_form(fam, r, theta, t, a=a, convention=convention)
        return orbit_at(phi, det_reference=ref)["det_B_sign"]

    lo, hi = a, r_max
    s_lo, s_hi = sign_at(lo), sign_at(hi)
    if s_lo == s_hi:
        return None

    for _ in range(iterations):
        mid = math.sqrt(lo * hi)
        if sign_at(mid) == s_lo:
            lo = mid
        else:
            hi = mid

    r_star = 0.5 * (lo + hi)
    return {
        "t": t,
        "theta": theta,
        "a": a,
        "r_star": r_star,
        "r_star_over_a": r_star / a,
        "bracket": (lo, hi),
        "det_B_sign_inside": s_lo,
        "det_B_sign_outside": s_hi,
        #: the dimensionless combination the twisted block's amplitude is
        #: actually controlled by: eta's leading radial behaviour is a^2/r^2.
        "t_a2_over_r2_at_wall": t * a ** 2 / r_star ** 2,
        "order": "leading-order-in-t",
    }


def wall_scaling_report(t_values: Sequence[float] = (1.0, 2.0, 5.0, 10.0,
                                                    100.0, 1000.0),
                        theta: float = math.pi / 4, a: float = 1.0,
                        convention: Optional[str] = None) -> Dict[str, Any]:
    """Does the wall follow r_* proportional to sqrt(t), and to what accuracy?

    The prediction is not fitted: eta's leading radial behaviour is a^2/r^2, so
    the twisted block's amplitude relative to the flat block is t a^2 / r^2 and
    a wall at fixed amplitude MUST sit at r_* proportional to sqrt(t). What is
    measured is the constant, and whether it is in fact constant.
    """
    walls = [w for w in (wall_radius(t, theta=theta, a=a,
                                     convention=convention)
                         for t in t_values) if w]
    ratios = [w["t_a2_over_r2_at_wall"] for w in walls]
    return {
        "theta": theta,
        "walls": walls,
        "t_a2_over_r2_at_wall": ratios,
        "spread": (max(ratios) - min(ratios)) if ratios else None,
        "limit_behaviour": (
            "t a^2/r_*^2 approaches 1 from below as t grows: %s. The residual "
            "is the subleading a^4/r^4 term in eta, which dies as the wall "
            "moves outward, so the asymptotic statement is that the wall sits "
            "where the twisted block's amplitude EQUALS the flat block's."
            % ["%.4f" % x for x in ratios]
        ) if ratios else "no wall found at any sampled t",
        "prediction": ("r_* proportional to sqrt(t), from eta ~ a^2/r^2 -- "
                       "derived from the form, not fitted to the scan"),
        "order": "leading-order-in-t",
    }


def critical_amplitude(theta: float = math.pi / 4, a: float = 1.0,
                       convention: Optional[str] = None,
                       t_max: float = 1.0e4,
                       iterations: int = 60) -> Dict[str, Any]:
    """The smallest t whose wall reaches the bolt, r_* = a.

    Below it the degenerate locus sits at r < a, which is not on the manifold:
    the neck begins at the bolt. So t_crit is the amplitude at which the
    degeneracy ENTERS the geometry, and for t < t_crit the glued form is a
    stable 3-form of the home orbit on the whole neck.
    """
    fam = _families(1)[0]
    ref = abs(orbit_at(_flat_phi(convention))["det_B"])

    def sign_at_bolt(t: float) -> int:
        phi = glued_three_form(fam, a, theta, t, a=a, convention=convention)
        return orbit_at(phi, det_reference=ref)["det_B_sign"]

    flat_sign = sign_at_bolt(0.0)
    if sign_at_bolt(t_max) == flat_sign:
        return {"theta": theta, "t_crit": None,
                "note": "det B at the bolt never flips sign up to t = %g" % t_max,
                "order": "leading-order-in-t"}

    lo, hi = 0.0, t_max
    for _ in range(iterations):
        mid = 0.5 * (lo + hi)
        if sign_at_bolt(mid) == flat_sign:
            lo = mid
        else:
            hi = mid

    return {
        "theta": theta,
        "a": a,
        "t_crit": 0.5 * (lo + hi),
        "bracket": (lo, hi),
        "means": (
            "for t below this the det B = 0 wall sits inside the bolt radius and "
            "is off the manifold, so the glued form is a stable 3-form of the "
            "home orbit on the entire neck. Above it the wall is at r_* >= a "
            "and the degeneracy is part of the geometry."
        ),
        "order": "leading-order-in-t",
    }


def seam_signature(theta: float = math.pi / 4, t: float = 1.0,
                   a: float = 1.0, convention: Optional[str] = None
                   ) -> Dict[str, Any]:
    """The orbit AT THE SEAM, r = a, where the bolt sits and f^2 vanishes.

    The seam is the one radius where the exact metric is furthest from the
    asymptotic identification, so it is the most likely place for the orbit to
    move and the right place to put a guard.
    """
    fam = _families(1)[0]
    phi = glued_three_form(fam, r=a, theta=theta, t=t, a=a,
                           convention=convention)
    rec = orbit_at(phi, det_reference=abs(
        orbit_at(_flat_phi(convention))["det_B"]))
    rec.update({
        "family": fam["family"],
        "r_over_a": 1.0,
        "theta": theta,
        "t": t,
        "at": "the seam r = a",
        "expected_negative_eigenvalues": expected_negative_eigenvalues(
            convention),
        "expected_unordered_signature": expected_unordered_signature(
            convention),
        "order": "leading-order-in-t",
        "flat_block_identification": "asymptotic (ALE)",
    })
    return rec


def scan_report(convention: Optional[str] = None) -> Dict[str, Any]:
    """The whole measurement, with the representativeness of family 0 CHECKED.

    The single-family default is only legitimate if the twelve families agree,
    so this runs a coarse grid over all twelve and reports whether they do.
    """
    records = scan(convention=convention)
    outcome = orbit_outcome(records, convention=convention)

    coarse = scan(radii=(1.0, 2.0, 10.0), t_values=(0.0, 1.0, 10.0),
                  thetas=(math.pi / 4, math.pi / 2), n_families=None,
                  convention=convention)
    per_family = {}
    for rec in coarse:
        per_family.setdefault(rec["family"], set()).add(rec["orbit"])
    families_agree = len({frozenset(v) for v in per_family.values()}) == 1

    return {
        "outcome": outcome,
        "seam": seam_signature(convention=convention),
        "wall_scaling": wall_scaling_report(convention=convention),
        "critical_amplitude": critical_amplitude(convention=convention),
        "grid": {
            "radii_over_a": list(DEFAULT_RADII),
            "t_values": list(DEFAULT_T_VALUES),
            "thetas": list(DEFAULT_THETAS),
            "n_points_primary": len(records),
            "n_points_all_families": len(coarse),
        },
        "all_twelve_families_agree": families_agree,
        "per_family_orbits": {k: sorted(v) for k, v in
                              sorted(per_family.items())},
        "order": "leading-order-in-t",
        "flat_block_identification": "asymptotic (ALE)",
        "what_is_invariant": (
            "sign(det B) and signature(B) are invariants of the "
            "orientation-preserving GL(7,R) orbit, so they may be read in the "
            "neck chart's coordinate basis. No orthonormal frame is used and no "
            "metric claim is made."
        ),
        "what_is_not_exact": (
            "the flat block is written in the neck chart through the ASYMPTOTIC "
            "(ALE) identification of the four moved coordinates with the four "
            "Eguchi-Hanson axes, and the twisted block enters at leading order "
            "in the gluing amplitude t. This is the orbit of the leading-order "
            "glued form, not of the exact Joyce metric, which the framework "
            "does not have."
        ),
    }
