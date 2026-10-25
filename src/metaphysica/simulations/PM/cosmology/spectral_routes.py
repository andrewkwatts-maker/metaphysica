"""Spectral-index routes behind the ``spectral_index_route`` fork.

Pure arithmetic, so both consumers (``inflation.G2Inflation`` and
``GeometricAnchors.n_s``) read the same formulas and neither imports the other.

Provenance (``theories/pm/lineage/branches.yaml``):
  * ``golden_modulated`` -- ADOPTED: n_s = 1 - 2 phi^2 / chi_eff (GeometricAnchors.n_s
    v18.0 and ``inflation._infrared_closure_n_s``; the source calls it the
    golden-modulated e-fold count N_eff = chi_eff / phi^2).
  * ``one_minus_2_over_b3`` -- n_s = 1 - 2 / b3 (GeometricAnchors.n_s docstring, v16.0,
    "0.9167, 11.48 sigma from Planck" at b3 = 24); replaced 2026-01-10 (0b984a37).
  * ``re_t_slow_roll`` -- n_s = 1 - 6 eps + 2 eta on V ~ Re(T), the value the
    inflation module already computes as ``n_s_slow_roll`` (8.263 sigma FAIL).
"""

from __future__ import annotations

from typing import Callable, Dict

#: The route the source takes today. variants._spectral_index_route_adopted
#: checks the fork's declared default against this constant.
ADOPTED_ROUTE: str = "golden_modulated"

ROUTES = ("golden_modulated", "one_minus_2_over_b3", "re_t_slow_roll")


def n_s_for_route(route: str, *, b3: float, chi_eff: float, phi: float,
                  n_s_slow_roll: Callable[[], float]) -> float:
    """n_s under *route*. ``n_s_slow_roll`` is lazy: only that route needs it."""
    if route == "golden_modulated":
        return 1.0 - 2.0 * (phi * phi) / float(chi_eff)
    if route == "one_minus_2_over_b3":
        return 1.0 - 2.0 / float(b3)
    if route == "re_t_slow_roll":
        return float(n_s_slow_roll())
    raise ValueError("unknown spectral_index_route %r; declared: %s"
                     % (route, list(ROUTES)))


def resolve_route() -> str:
    """The selected route (env override, else the fork default)."""
    from metaphysica.simulations.core.variants import resolve

    return resolve("spectral_index_route")
