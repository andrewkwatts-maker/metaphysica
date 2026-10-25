"""Late-time routes behind the ``h0_route`` and ``dark_energy_mechanism`` forks (D-022).

Consumers: ``FormulasRegistry.calculate_h0_local`` (cosmology.H0_local),
``FormulasRegistry.calculate_w0`` (w0_dark_energy) and
``DarkEnergy._derive_dark_energy_eos`` (cosmology.w0_derived).

Provenance (``theories/pm/lineage/branches.yaml``):
  * h0_route ``odowd_composite`` -- ADOPTED: the registry's own O'Dowd formula
    H0 = 288/4 - 163/144 + eta_S = 71.55 (canonical_values CANON['H0_km_s_Mpc']).
  * h0_route ``ricci_flow`` -- H0 = H0_planck (1 + sin^2(theta)/2), theta = 31 deg
    (ricci_flow_h0.THETA_MIXING_13D_26D_DEG), H0_planck = registry h0_early.
  * h0_route ``kk_bridge`` -- H0 from the KK/KNP early-dark-energy sound-horizon
    shift, exactly the steps of hubble_tension.HubbleTensionEDE.run (REFUTED).
  * dark_energy_mechanism ``thawing_quintessence`` -- ADOPTED: w0 = -1 + 1/b3.
  * dark_energy_mechanism ``mep_11_13`` -- w0 = -(D-1)/(D+1) with D = 12, the
    pre-v16.2 D_eff formula quoted in dark_energy.py (D_eff = 12 + alpha_shadow;
    the catalogue's d = 12 drops the legacy alpha_shadow).
"""

from __future__ import annotations

import math

ADOPTED_H0_ROUTE: str = "odowd_composite"
ADOPTED_DE_MECHANISM: str = "thawing_quintessence"

#: Dimension of the catalogue's MEP argument ("d=12").
MEP_D: int = 12


def resolve_h0_route() -> str:
    from metaphysica.simulations.core.variants import resolve

    return resolve("h0_route")


def resolve_de_mechanism() -> str:
    from metaphysica.simulations.core.variants import resolve

    return resolve("dark_energy_mechanism")


def _ricci_flow_h0(h0_planck: float) -> float:
    from metaphysica.simulations.PM.cosmology.ricci_flow_h0 import (
        THETA_MIXING_13D_26D_DEG,
    )

    theta = THETA_MIXING_13D_26D_DEG * math.pi / 180.0
    return h0_planck * (1.0 + math.sin(theta) ** 2 / 2.0)


def _kk_bridge_h0(b3: float) -> float:
    """H0_ede, the same steps as HubbleTensionEDE.run (no registry needed)."""
    from metaphysica.simulations.PM.cosmology import hubble_tension as ht

    knp = ht.compute_knp_parameters(b3=int(b3))
    rho_ede = ht.compute_ede_energy_density(knp["m_required_eV"], knp["f_eff_eV"])
    z_peak = 3500.0
    rho_crit = ht.compute_critical_density_eV4(z_peak, ht.H0_PLANCK * ht.H0_EV_FACTOR)
    f_ede = rho_ede / rho_crit
    r_lcdm = ht.compute_sound_horizon(
        ht.H0_PLANCK, ht.OMEGA_M, ht.OMEGA_R, ht.OMEGA_B, ht.Z_DEC, f_ede_peak=0.0)
    r_ede = ht.compute_sound_horizon(
        ht.H0_PLANCK, ht.OMEGA_M, ht.OMEGA_R, ht.OMEGA_B, ht.Z_DEC,
        f_ede_peak=f_ede, z_peak=z_peak)
    return ht.H0_PLANCK * (1.0 - (r_ede - r_lcdm) / r_lcdm)


def h0_local_for_route(route: str, *, odowd: float, h0_planck: float, b3: float) -> float:
    """H0 under *route*; ``odowd`` is the registry's own composite."""
    if route == "odowd_composite":
        return odowd
    if route == "ricci_flow":
        return _ricci_flow_h0(h0_planck)
    if route == "kk_bridge":
        return _kk_bridge_h0(b3)
    raise ValueError("unknown h0_route %r" % route)


def w0_for_mechanism(mechanism: str, *, thawing: float) -> float:
    """w0 under *mechanism*; ``thawing`` is the consumer's own -1 + 1/b3 / -sigma_T."""
    if mechanism == "thawing_quintessence":
        return thawing
    if mechanism == "mep_11_13":
        return -(MEP_D - 1.0) / (MEP_D + 1.0)
    raise ValueError("unknown dark_energy_mechanism %r" % mechanism)
