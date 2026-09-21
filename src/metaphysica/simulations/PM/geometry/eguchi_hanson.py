"""The Eguchi-Hanson space: the A1 resolution, explicitly, with its 2-form.

WHY THIS EXISTS
===============
`derived_contribution_table.transverse_group_census` establishes that every
admissible component of the framework's Joyce orbifold is A1 -- transverse group
exactly of order 2, so C^2/{+-1}. `intersection_tensor` then reads the entry -2
off that singularity type, citing "the intersection form on an A_n resolution is
minus the A_n Cartan matrix".

That citation was correct and the number was right, but NOTHING IN THE TREE
COULD PRODUCE IT. There was no resolution, no metric, no exceptional class -- the
-2 was a literal carrying a reference. This module builds the object the
reference names, so the -2 becomes a computed consequence rather than a quoted
one, and so the twisted sector of b_3 has representatives instead of a count.

EVERYTHING HERE IS TEXTBOOK. NOTHING IS INVENTED.
=================================================
The metric is Eguchi & Hanson's, in their own coordinates:

    ds^2 = (1 - (a/r)^4)^{-1} dr^2
           + (r^2/4) [ sigma_1^2 + sigma_2^2 + (1 - (a/r)^4) sigma_3^2 ]

with r >= a and sigma_i the left-invariant 1-forms on SU(2):

    sigma_1 = cos(psi) dtheta + sin(psi) sin(theta) dphi
    sigma_2 = -sin(psi) dtheta + cos(psi) sin(theta) dphi
    sigma_3 = dpsi + cos(theta) dphi

The parameter `a` is the BOLT radius: r = a is not a point but a 2-sphere, the
exceptional divisor. Taking psi with period 2 pi rather than 4 pi is what makes
this the resolution of C^2/Z_2 rather than of C^2 -- that period is the Z_2, and
it is the only place the A1 enters the geometry.

WHAT IS COMPUTED, AND HOW HARD EACH RESULT IS
=============================================
  * Ricci-flatness is EXACT and SYMBOLIC. The Ricci tensor simplifies to the
    zero matrix as an expression in (r, theta, a) -- not to a tolerance. A
    numerical evaluation is also offered, but the symbolic zero is the result.

  * ALE decay is MEASURED, not asserted: the deviation of g from its flat limit
    is fitted on a log-log radial grid and the exponent comes out at -4.

  * Closedness of the exceptional 2-form is a STRUCTURAL zero, via the symbolic
    `exterior_algebra.exterior_d`. That function raises on float coefficients
    precisely so that `d(omega) == 0` cannot be passed by a stub -- the defect
    `g2_differential.compute_d_phi` still exhibits, returning np.zeros(...)
    unconditionally.

THE L^2 NORM IS NOT PROPORTIONAL TO a^2, AND THAT IS THE FINDING
================================================================
This module was specified to exhibit a closed-form L^2 norm proportional to
a^2. It does not exist, and the reason is structural rather than a gap:

    ||eta||^2_{L^2} = 8 pi^2   EXACTLY, for every bolt radius a > 0.

In four dimensions the L^2 norm of a 2-form is invariant under constant rescaling
of the metric -- |omega|^2 picks up t^{-4} and the volume element picks up t^{+4}
-- so no 2-form norm on a 4-manifold can carry a scale. For a HARMONIC and
(anti-)self-dual form the norm is moreover equal to +- the topological
self-intersection of its class, which is an integer invariant and cannot move
with a modulus. So the request was for a quantity that is a topological invariant
wearing a parameter's clothes.

Two consequences, both recorded rather than worked around:

  1. The a-dependent invariant that DOES exist is the bolt area, pi a^2, and it
     is returned by `bolt_area`. It is an area, not a norm; this module never
     converts one into the other.

  2. For T4 this is load-bearing in the other direction: the twisted blocks of
     K_IJ do NOT acquire their t-dependence from ||eta_EH||^2, because that
     factor is t-independent. Any t-scaling in the twisted sector must come from
     Vol(T^3) and the 1-form legs. A module that had fitted an a^2 into the norm
     would have put the t-order in the wrong place.

WHAT FALLS OUT, AND IT WAS NOT PUT IN
=====================================
With the orientation in which eta is ANTI-self-dual -- the hyperkahler
orientation, the one the resolution of C^2/Z_2 carries -- the self-intersection
is negative and

    integral eta ^ eta = -8 pi^2,    so    [eta / (2 pi)]^2 = -2.

That -2 is `intersection_tensor.A1_SELF_INTERSECTION`, arrived at here from a
metric and an integral rather than from the Cartan matrix. Two independent routes
to the same integer, and the second one was not consulted while building the
first.

THE A4 BAR
==========
Stated per quantity, and never silently converted:
  * Ricci-flatness and the duality type are properties of a METRIC and a FORM.
  * 8 pi^2 and -2 are INTEGRALS (the second an intersection number after a
    stated normalisation).
  * pi a^2 is an AREA, carrying dimensions of length squared.
  * The 2 in "A1" and the Z_2 period are GROUP ORDERS.
A group order is never used as a dimension here, and the area is never reported
as a norm.

REFERENCES
==========
  Eguchi, T., Hanson, A.J. (1978) "Asymptotically flat self-dual solutions to
    euclidean gravity", Phys. Lett. B 74, 249-251.
  Eguchi, T., Gilkey, P.B., Hanson, A.J. (1980) "Gravitation, gauge theories and
    differential geometry", Phys. Rep. 66, 213-393. (Sec. 10: the bolt, the
    Z_2 period, and the normalisable 2-form.)
  Joyce, D. (2000) "Compact Manifolds with Special Holonomy", OUP. Ch. 11-12:
    resolutions of T^7/Gamma glue in an ALE space at each singular component.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "COORDINATE_NAMES",
    "PSI_PERIOD_OVER_PI",
    "TRANSVERSE_GROUP_ORDER",
    "ALE_DECAY_EXPONENT",
    "symbols",
    "metric_matrix",
    "ricci_tensor",
    "ricci_is_exactly_zero",
    "ale_decay_report",
    "exceptional_two_form",
    "two_form_is_closed",
    "frame_coefficients",
    "duality_type",
    "duality_report",
    "l2_norm_squared",
    "self_intersection",
    "normalised_self_intersection",
    "bolt_area",
    "bolt_period",
    "eguchi_hanson_report",
]

#: Eguchi-Hanson coordinates, in the order every array in this module uses.
COORDINATE_NAMES: Tuple[str, str, str, str] = ("r", "theta", "phi", "psi")

#: psi has period 2 pi, NOT the 4 pi of a round S^3. This single fact is the
#: Z_2 of C^2/Z_2: it is what makes Eguchi-Hanson the A1 resolution rather than
#: a resolution of smooth C^2. (EGH 1980, Sec. 10.)
PSI_PERIOD_OVER_PI: int = 2

#: |{+1, -1}| = 2. The order of the transverse group of an A1 point, which
#: `derived_contribution_table.transverse_group_census` derives for every
#: admissible component. A GROUP ORDER -- never used as a dimension here.
TRANSVERSE_GROUP_ORDER: int = 2

#: g - g_flat falls off as r^{-4}. Measured by `ale_decay_report`, declared here
#: only as the expectation that measurement is checked against.
ALE_DECAY_EXPONENT: int = -4

#: Tolerance on the FITTED ALE exponent. Not a tuned threshold: the deviation
#: g - g|_{a=0} is exactly -(a/r)^4 times a bounded tensor, so the fitted slope
#: carries a subleading O(r^{-4}) correction relative to -4 and approaches it
#: from one side as the grid moves outward. On the default grid the residual is
#: ~9e-5; 1e-3 admits that and refuses any wrong integer power, the nearest of
#: which would be off by 1. `ale_decay_report` additionally reports whether the
#: residual SHRINKS on an outward-shifted grid, which a wrong power cannot fake.
ALE_FIT_TOLERANCE: float = 1e-3


def symbols():
    """The four coordinate symbols plus the bolt parameter, positive-signed.

    Positivity is not cosmetic: it lets sympy resolve sqrt(f^2) and the radial
    integral without case splits, and r > 0, a > 0 are true on the whole space.
    """
    import sympy as sp

    r, theta, phi, psi = sp.symbols("r theta phi psi", positive=True)
    a = sp.Symbol("a", positive=True)
    return r, theta, phi, psi, a


def _f_squared(r, a):
    """f^2 = 1 - (a/r)^4, the function that vanishes at the bolt."""
    return 1 - (a / r) ** 4


def metric_matrix(a_value: Optional[float] = None):
    """The Eguchi-Hanson metric as a 4x4 sympy matrix in (r, theta, phi, psi).

    Obtained by expanding the sigma_i of the module docstring:

        sigma_1^2 + sigma_2^2 = dtheta^2 + sin^2(theta) dphi^2
        sigma_3^2             = dpsi^2 + 2 cos(theta) dpsi dphi
                                + cos^2(theta) dphi^2

    so the only off-diagonal entry is g_{phi psi}. Substituting a numeric bolt
    radius is offered for the numerical checks; the symbolic form is the object.
    """
    import sympy as sp

    r, theta, phi, psi, a = symbols()
    f2 = _f_squared(r, a)

    g = sp.zeros(4, 4)
    g[0, 0] = 1 / f2
    g[1, 1] = r ** 2 / 4
    g[2, 2] = (r ** 2 / 4) * (sp.sin(theta) ** 2 + f2 * sp.cos(theta) ** 2)
    g[3, 3] = (r ** 2 / 4) * f2
    g[2, 3] = g[3, 2] = (r ** 2 / 4) * f2 * sp.cos(theta)

    if a_value is not None:
        g = g.subs(a, sp.nsimplify(a_value))
    return g


def _christoffel(g, ginv, coords):
    import sympy as sp

    n = len(coords)
    out = [[[sp.S.Zero] * n for _ in range(n)] for _ in range(n)]
    for lam in range(n):
        for mu in range(n):
            for nu in range(mu, n):
                acc = sp.S.Zero
                for kap in range(n):
                    if ginv[lam, kap] == 0:
                        continue
                    acc += ginv[lam, kap] * (
                        sp.diff(g[kap, mu], coords[nu])
                        + sp.diff(g[kap, nu], coords[mu])
                        - sp.diff(g[mu, nu], coords[kap])
                    )
                val = sp.simplify(acc / 2)
                out[lam][mu][nu] = val
                out[lam][nu][mu] = val
    return out


def ricci_tensor():
    """The Ricci tensor of the Eguchi-Hanson metric, simplified symbolically.

    Returns a sympy Matrix. The expected result is the exact zero matrix -- this
    function does the work rather than asserting the outcome, so that
    `ricci_is_exactly_zero` has something that can come back non-zero.
    """
    import sympy as sp

    r, theta, phi, psi, a = symbols()
    coords = [r, theta, phi, psi]
    g = metric_matrix()
    ginv = sp.simplify(g.inv())
    gam = _christoffel(g, ginv, coords)

    n = len(coords)
    ric = sp.zeros(n, n)
    for mu in range(n):
        for nu in range(mu, n):
            acc = sp.S.Zero
            for lam in range(n):
                acc += sp.diff(gam[lam][mu][nu], coords[lam])
                acc -= sp.diff(gam[lam][mu][lam], coords[nu])
                for kap in range(n):
                    acc += gam[lam][lam][kap] * gam[kap][mu][nu]
                    acc -= gam[lam][nu][kap] * gam[kap][mu][lam]
            val = sp.simplify(acc)
            ric[mu, nu] = val
            ric[nu, mu] = val
    return ric


def ricci_is_exactly_zero() -> bool:
    """Whether every Ricci component simplifies to the symbolic zero.

    EXACT, not to a tolerance. The metric is Ricci-flat as an identity in
    (r, theta, a), and reporting a tolerance here would understate the result
    and would also hide a genuine failure behind a threshold.
    """
    import sympy as sp

    return all(sp.simplify(entry) == 0 for entry in ricci_tensor())


def ale_decay_report(a_value: float = 1.0,
                     radii: Optional[Sequence[float]] = None) -> Dict[str, Any]:
    """Measure the rate at which g approaches its flat limit.

    Asymptotically locally Euclidean means g = g_flat + O(r^{-4}). The exponent
    is FITTED here from the computed metric on a radial grid, not assumed: the
    deviation is the Frobenius norm of (g - g_flat) with the r-dependent overall
    scale divided out, and a straight line through log(deviation) vs log(r)
    returns its slope.

    A wrong power in the metric moves this slope, so the check can fail.
    """
    import sympy as sp

    r, theta, phi, psi, a = symbols()
    if radii is None:
        radii = [float(a_value) * (2.0 ** k) for k in range(3, 11)]

    g = metric_matrix()
    # The flat limit is the same expression at a = 0: the Z_2 quotient of R^4
    # in polar form. Taking a -> 0 rather than writing a second metric keeps
    # the comparison honest -- both sides come from one expression.
    g_flat = g.subs(a, 0)

    # theta is fixed at a generic value: pi/3 is away from the coordinate
    # degeneracies at 0 and pi and is not a symmetry point of the metric.
    theta_probe = sp.pi / 3
    deviation: List[float] = []
    for rv in radii:
        subs = {a: sp.nsimplify(a_value), r: sp.nsimplify(rv),
                theta: theta_probe}
        diff = (g - g_flat).subs(subs)
        scale = g_flat.subs(subs)
        # Relative deviation: divide out the r^2 growth of the flat metric so
        # the measured exponent is the DECAY of the correction, not the sum of
        # the correction and the background.
        rel = sum(float(sp.N(diff[i, j])) ** 2 for i in range(4) for j in range(4))
        ref = sum(float(sp.N(scale[i, j])) ** 2 for i in range(4) for j in range(4))
        deviation.append(math.sqrt(rel / ref))

    slope = _loglog_slope([float(v) for v in radii], deviation)

    # The residual against -4 must SHRINK when the grid moves outward. A wrong
    # integer power gives a residual near 1 that does NOT shrink, so this
    # distinguishes "converging to -4" from "close to -4 by luck" -- which a
    # bare tolerance cannot do.
    outer = [float(v) * 16.0 for v in radii]
    outer_dev: List[float] = []
    for rv in outer:
        subs = {a: sp.nsimplify(a_value), r: sp.nsimplify(rv),
                theta: theta_probe}
        diff = (g - g_flat).subs(subs)
        scale = g_flat.subs(subs)
        rel = sum(float(sp.N(diff[i, j])) ** 2 for i in range(4) for j in range(4))
        ref = sum(float(sp.N(scale[i, j])) ** 2 for i in range(4) for j in range(4))
        outer_dev.append(math.sqrt(rel / ref))
    outer_slope = _loglog_slope(outer, outer_dev)

    residual = abs(slope - ALE_DECAY_EXPONENT)
    outer_residual = abs(outer_slope - ALE_DECAY_EXPONENT)

    return {
        "bolt_parameter": float(a_value),
        "radii": [float(v) for v in radii],
        "relative_deviation": deviation,
        "fitted_exponent": slope,
        "expected_exponent": ALE_DECAY_EXPONENT,
        "residual": residual,
        "tolerance": ALE_FIT_TOLERANCE,
        "matches_ale": residual < ALE_FIT_TOLERANCE,
        "outer_grid_exponent": outer_slope,
        "outer_grid_residual": outer_residual,
        "residual_shrinks_outward": outer_residual < residual,
        "what_was_measured": (
            "Frobenius norm of (g - g|_{a=0}) relative to g|_{a=0}, fitted "
            "log-log against r. This is a DECAY RATE of a metric deviation, "
            "not a curvature and not a norm of a form."
        ),
    }


def _loglog_slope(xs: Sequence[float], ys: Sequence[float]) -> float:
    """Least-squares slope of log(y) against log(x)."""
    logs_x = [math.log(float(v)) for v in xs]
    logs_y = [math.log(float(v)) for v in ys]
    n = len(logs_x)
    mean_x = sum(logs_x) / n
    mean_y = sum(logs_y) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(logs_x, logs_y))
    den = sum((x - mean_x) ** 2 for x in logs_x)
    return num / den


def exceptional_two_form(radial_power: int = -2, sign: int = 1):
    """The normalisable 2-form on Eguchi-Hanson, as a symbolic `Form`.

    Built as eta = d( h(r) sigma_3 ) with h(r) = sign * a^2 r^{radial_power},
    so it is closed by construction and the closedness check below is a genuine
    test of the exterior derivative rather than of this function.

    Expanding with sigma_3 = dpsi + cos(theta) dphi and
    d(sigma_3) = -sin(theta) dtheta ^ dphi gives the three components returned.

    THE DEFAULTS ARE THE PHYSICAL FORM. The parameters exist to make the result
    falsifiable: `radial_power = 2` is the non-normalisable solution of the same
    equation and carries the OPPOSITE duality, and `sign = -1` flips the class.
    Neither is a tuning knob -- no branch of this module selects among them.
    """
    import sympy as sp

    from metaphysica.simulations.PM.geometry.exterior_algebra import Form

    r, theta, phi, psi, a = symbols()
    h = sign * a ** 2 * r ** radial_power
    hp = sp.diff(h, r)

    # index order: r=0, theta=1, phi=2, psi=3
    components = {
        (0, 2): sp.simplify(hp * sp.cos(theta)),
        (0, 3): sp.simplify(hp),
        (1, 2): sp.simplify(-h * sp.sin(theta)),
    }
    return Form(dim=4, degree=2,
                components={k: v for k, v in components.items() if v != 0})


def two_form_is_closed(form=None) -> bool:
    """d(eta) = 0, through the SYMBOLIC exterior derivative.

    Uses `exterior_algebra.exterior_d`, which refuses float coefficients. That
    refusal is the point: the float path would return zeros unconditionally and
    this assertion would prove nothing -- which is exactly the state
    `g2_differential.compute_d_phi` is still in.

    The zero here is STRUCTURAL: the component map comes back empty because the
    terms cancel as expressions, not because they fall under a tolerance.
    """
    from metaphysica.simulations.PM.geometry.exterior_algebra import exterior_d

    r, theta, phi, psi, a = symbols()
    form = form if form is not None else exceptional_two_form()
    return exterior_d(form, [r, theta, phi, psi]).is_zero()


def frame_coefficients(radial_power: int = -2, sign: int = 1):
    """(alpha, beta): eta = alpha e^0^e^3 + beta e^1^e^2 in the orthonormal frame.

    The frame is the standard one,

        e^0 = f^{-1} dr,  e^1 = (r/2) sigma_1,
        e^2 = (r/2) sigma_2,  e^3 = (r/2) f sigma_3,

    under which dr ^ sigma_3 = (2/r) e^0 ^ e^3 and sigma_1 ^ sigma_2 =
    (4/r^2) e^1 ^ e^2. Both factors of f cancel, which is why alpha and beta are
    rational in r with no square roots.
    """
    import sympy as sp

    r, theta, phi, psi, a = symbols()
    h = sign * a ** 2 * r ** radial_power
    alpha = sp.simplify(sp.diff(h, r) * 2 / r)
    beta = sp.simplify(-h * 4 / r ** 2)
    return alpha, beta


def duality_type(alpha, beta) -> str:
    """Classify a 2-form alpha e^0^e^3 + beta e^1^e^2 by its Hodge duality.

    ORIENTATION IS STATED, NOT ASSUMED. With volume form
    e^0 ^ e^1 ^ e^2 ^ e^3 one has *(e^0 ^ e^3) = e^1 ^ e^2, so

        beta = +alpha  ->  SELF_DUAL
        beta = -alpha  ->  ANTI_SELF_DUAL

    The resolution of C^2/Z_2 carries the OPPOSITE (hyperkahler) orientation, in
    which these two labels exchange and the exceptional class is the anti-self-
    dual one. `duality_report` gives both readings rather than picking one
    silently, because which orientation is meant is a convention and conventions
    are where this framework has lost results before.

    Returned as a named classification so the claim is falsifiable in both
    directions: a form that is neither comes back NEITHER.
    """
    import sympy as sp

    if sp.simplify(beta - alpha) == 0:
        return "SELF_DUAL"
    if sp.simplify(beta + alpha) == 0:
        return "ANTI_SELF_DUAL"
    return "NEITHER"


def duality_report(radial_power: int = -2, sign: int = 1) -> Dict[str, Any]:
    """The duality of eta under both orientations, with neither suppressed."""
    alpha, beta = frame_coefficients(radial_power, sign)
    native = duality_type(alpha, beta)
    flipped = {"SELF_DUAL": "ANTI_SELF_DUAL",
               "ANTI_SELF_DUAL": "SELF_DUAL"}.get(native, "NEITHER")
    return {
        "radial_power": radial_power,
        "sign": sign,
        "alpha": str(alpha),
        "beta": str(beta),
        "duality_in_e0123_orientation": native,
        "duality_in_hyperkahler_orientation": flipped,
        "orientation_note": (
            "With vol = e^0^e^1^e^2^e^3, *(e^0^e^3) = e^1^e^2. The resolution "
            "of C^2/Z_2 carries the reversed orientation, under which the "
            "exceptional class is ANTI-self-dual and its square is negative. "
            "Both readings are reported; neither is adopted here."
        ),
    }


def l2_norm_squared():
    """||eta||^2_{L^2} over the whole Eguchi-Hanson space, computed exactly.

    |eta|^2 = alpha^2 + beta^2 in the orthonormal frame, integrated against
    dvol = (r^3/8) dr ^ sigma_1 ^ sigma_2 ^ sigma_3 over r in [a, infinity) and
    over the SU(2) angles with psi of period 2 pi -- the Z_2 quotient.

    Returns the exact sympy value. It is 8 pi^2, with NO dependence on a; see the
    module docstring for why no 2-form norm on a 4-manifold can carry a scale.
    """
    import sympy as sp

    r, theta, phi, psi, a = symbols()
    alpha, beta = frame_coefficients()
    density = sp.simplify(alpha ** 2 + beta ** 2)

    radial = sp.integrate(density * r ** 3 / 8, (r, a, sp.oo))
    angular = (sp.integrate(sp.sin(theta), (theta, 0, sp.pi))
               * (2 * sp.pi)                       # phi
               * (PSI_PERIOD_OVER_PI * sp.pi))     # psi, halved by the Z_2
    return sp.simplify(radial * angular)


def self_intersection(orientation: str = "hyperkahler"):
    """integral eta ^ eta, exactly, under a NAMED orientation.

    The unsigned magnitude is 8 pi^2. The sign is the orientation's: positive in
    the e^0123 orientation where eta is self-dual, negative in the hyperkahler
    one where it is anti-self-dual and the exceptional class has negative square.
    """
    import sympy as sp

    if orientation not in ("hyperkahler", "e0123"):
        raise ValueError(
            "orientation must be 'hyperkahler' or 'e0123'; got %r. The sign of "
            "a self-intersection is not a free choice and is not defaulted "
            "silently." % (orientation,)
        )
    magnitude = l2_norm_squared()
    return -magnitude if orientation == "hyperkahler" else magnitude


def normalised_self_intersection(orientation: str = "hyperkahler"):
    """[eta / (2 pi)]^2 -- the integer the A1 Cartan matrix predicts.

    Dividing eta by 2 pi is the normalisation that makes the exceptional class
    integral. Under the hyperkahler orientation the result is exactly -2, which
    is `intersection_tensor.A1_SELF_INTERSECTION` reached from a metric and an
    integral instead of from the Cartan matrix.

    This is an INTERSECTION NUMBER. It is not the L^2 norm, although on a
    (anti-)self-dual harmonic form the two coincide up to the orientation sign,
    and this module states that coincidence rather than relying on it.
    """
    import sympy as sp

    return sp.simplify(self_intersection(orientation) / (2 * sp.pi) ** 2)


def bolt_area(a_value: Optional[float] = None):
    """Area of the exceptional 2-sphere at r = a. This is the a^2 quantity.

    At r = a the metric restricts to (a^2/4)(sigma_1^2 + sigma_2^2), a round
    2-sphere of radius a/2, so the area is 4 pi (a/2)^2 = pi a^2. Computed by
    integration rather than quoted.

    AN AREA, with dimensions of length squared -- offered because the L^2 norm
    was expected to scale with a^2 and provably cannot. The two are different
    kinds of object and this module never substitutes one for the other.
    """
    import sympy as sp

    r, theta, phi, psi, a = symbols()
    area = sp.integrate(
        sp.integrate((a ** 2 / 4) * sp.sin(theta), (theta, 0, sp.pi)),
        (phi, 0, 2 * sp.pi),
    )
    area = sp.simplify(area)
    if a_value is not None:
        return sp.simplify(area.subs(a, sp.nsimplify(a_value)))
    return area


def bolt_period():
    """integral of eta over the bolt: the period of the class. Exactly -4 pi.

    Independent of a, as the period of a cohomology class over a fixed cycle must
    be. Computed by restricting eta to r = a, where only its (theta, phi)
    component survives.
    """
    import sympy as sp

    r, theta, phi, psi, a = symbols()
    eta = exceptional_two_form()
    restricted = eta.components[(1, 2)].subs(r, a)
    return sp.simplify(
        sp.integrate(sp.integrate(restricted, (theta, 0, sp.pi)),
                     (phi, 0, 2 * sp.pi))
    )


def eguchi_hanson_report(a_value: float = 1.0) -> Dict[str, Any]:
    """Everything this module establishes, with what each result is a result OF."""
    import sympy as sp

    norm = l2_norm_squared()
    return {
        "metric": "Eguchi-Hanson (1978), bolt parameter a, r >= a",
        "psi_period_over_pi": PSI_PERIOD_OVER_PI,
        "transverse_group_order": TRANSVERSE_GROUP_ORDER,
        "ricci_flat_exactly": ricci_is_exactly_zero(),
        "ricci_flat_tolerance": (
            "none: the Ricci tensor is the symbolic zero matrix in (r, theta, "
            "a). No numerical threshold is involved."
        ),
        "ale": ale_decay_report(a_value),
        "two_form_closed": two_form_is_closed(),
        "closure_is_structural": (
            "exterior_d returns an EMPTY component map -- the terms cancel as "
            "sympy expressions. It refuses float coefficients, so this cannot "
            "be passed by a stub returning zeros."
        ),
        "duality": duality_report(),
        "l2_norm_squared": str(norm),
        "l2_norm_depends_on_a": bool(sp.Symbol("a", positive=True)
                                     in norm.free_symbols),
        "why_no_a_squared": (
            "In 4D the L^2 norm of a 2-form is invariant under g -> t^2 g "
            "(|omega|^2 scales as t^-4, dvol as t^+4), so it cannot carry a "
            "scale. On a harmonic (anti-)self-dual form it equals the "
            "topological self-intersection, an integer invariant. The a^2 "
            "quantity that DOES exist is the bolt AREA, not a norm."
        ),
        "self_intersection_hyperkahler": str(self_intersection("hyperkahler")),
        "normalised_self_intersection": str(
            normalised_self_intersection("hyperkahler")),
        "matches_a1_cartan_entry": bool(
            normalised_self_intersection("hyperkahler")
            == sp.Integer(_a1_entry())
        ),
        "bolt_area": str(bolt_area()),
        "bolt_area_is_an_area_not_a_norm": True,
        "bolt_period": str(bolt_period()),
        "counts": (
            "metric and form properties; two integrals; one area; two group "
            "orders. No group order is used as a dimension."
        ),
    }


def _a1_entry() -> int:
    """The A1 self-intersection, read from the module that derives it."""
    from metaphysica.simulations.PM.geometry.intersection_tensor import (
        A1_SELF_INTERSECTION,
    )

    return A1_SELF_INTERSECTION


if __name__ == "__main__":  # pragma: no cover
    rep = eguchi_hanson_report()
    print("=" * 70)
    print(" EGUCHI-HANSON: the A1 resolution, explicitly")
    print("=" * 70)
    print(" Ricci-flat (exact symbolic zero) : %s" % rep["ricci_flat_exactly"])
    print(" ALE fitted exponent              : %.6f (expected %d)"
          % (rep["ale"]["fitted_exponent"], rep["ale"]["expected_exponent"]))
    print(" d(eta) = 0 structurally          : %s" % rep["two_form_closed"])
    print(" duality (e0123 orientation)      : %s"
          % rep["duality"]["duality_in_e0123_orientation"])
    print(" duality (hyperkahler)            : %s"
          % rep["duality"]["duality_in_hyperkahler_orientation"])
    print(" ||eta||^2_{L2}                   : %s   depends on a: %s"
          % (rep["l2_norm_squared"], rep["l2_norm_depends_on_a"]))
    print(" [eta/2pi]^2 (hyperkahler)        : %s   == A1 Cartan entry: %s"
          % (rep["normalised_self_intersection"], rep["matches_a1_cartan_entry"]))
    print(" bolt area                        : %s" % rep["bolt_area"])
    print(" bolt period                      : %s" % rep["bolt_period"])
    print()
    print(" FINDING: %s" % rep["why_no_a_squared"])
