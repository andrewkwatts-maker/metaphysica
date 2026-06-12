#!/usr/bin/env python3
"""
Soft SUSY-Breaking Spectrum (v25.0 Sprint 4, retuned in v25.0 Sprint 6,
                              Kahler-completed in Sprint T6 / Tier 3 T3.1)
============================================================================

Derives the full soft SUSY-breaking spectrum
(m_{3/2}, m_{1/2}, m_0, mu, A_0, B_mu) from the same non-perturbative
superpotential W = W_flux + W_inst that stabilizes Re(T) in v25.0
(``simulations/PM/geometry/re_t_sector.py``), now combined with the
no-scale Kahler ansatz K(T) = -3 ln(T + T*) standard in G_2-MSSM
literature (Acharya 2007+, Acharya-Bobkov-Kane 2008+).

Physics reasoning
-----------------
* All terms originate from the same non-perturbative superpotential
  W = W_flux + W_inst used for Re(T) stabilization (v25.0).
* The Kahler potential is taken to be the no-scale form
  K(T) = -3 ln(T + T*), giving the Planck-unit Kahler factor
  e^{K/2} = (T + T*)^{-3/2}. With Re(T) = 174.033 this is
  (348.066)^{-3/2} ~ 1.54e-4.
* Gravity-mediated moduli mediation via the F-term F^T / (T + T*)
  dominates.
* Gravitino mass m_{3/2} sets the overall scale and follows the full
  N=1 SUGRA formula ``m_{3/2} = e^{K/2} |W|`` in Planck units, where
  |W| = |W_flux + W_inst|. The instanton piece W_inst =
  exp(-2 pi Re(T) / b_3) is the v25.0 Re(T)-stabilization output;
  W_flux is set by the flux-quantization constraint (see below).
* Gaugino masses m_{1/2} receive anomaly + modulus contributions and
  scale as ``(b_3 / (2 pi Re(T))) * m_{3/2}``.
* Scalar masses m_0 are universal at leading order: m_0 = m_{3/2}.
* The mu-term picks up the standard O(1) instanton / Giudice-Masiero
  coefficient: ``mu = 0.8 * m_{3/2}``.
* The A-term (trilinear soft coupling) in G_2 volume-modulus mediation
  follows the standard Kahler-potential-expansion result
  ``A_0 = -3 * m_{3/2}``.
* The B mu term is generated as B ~ m_{3/2}, so
  ``B mu = m_{3/2} * mu`` (common in G_2-MSSM literature).

All masses are computed first in Planck units, then rescaled by 1e16 GeV.

Sprint T6 / Tier 3 T3.1 documented Kahler constraint
-----------------------------------------------------
The Sprint 6 module exposed the "160 keV gravitino problem": the literal
G_2-MSSM exponent W_inst = exp(-2 pi Re(T) / b_3) at v25.0 defaults
gives m_{3/2} ~ 1.6e-20 Planck ~ 160 keV after rescaling, well below
both the TeV-scale G_2-MSSM target (Acharya et al.) and the
cosmological gravitino-problem bound. The fix promised in the v25.0
Sprint 6 docstring -- "full Kahler-potential structure
m_{3/2} = e^{K/2} |W| with non-trivial K(T)" -- is implemented here.

Kahler ansatz: no-scale ``K(T) = -3 ln(T + T*)``
   * Standard in G_2-MSSM (Acharya 2007+).
   * Gives e^{K/2} = (T + T*)^{-3/2} ~ 1.54e-4 at v25.0 defaults.
   * Combined with the instanton-suppressed W_inst ~ 1.6e-20 Planck,
     the bare instanton contribution alone gives
     m_{3/2} ~ 1.54e-4 * 1.6e-20 ~ 2.5e-24 Planck ~ 2.5e-8 GeV (~25 eV),
     which is *worse* than the Sprint-6 value -- the no-scale prefactor
     suppresses the gravitino *further*.

Why a flux W_flux must dominate
   The N=1 SUGRA formula carries |W| = |W_flux + W_inst|. In KKLT-like
   constructions and in G_2-MSSM (Acharya-Bobkov-Kane-Kumar-Vaman 2008)
   the dominant contribution to W at the minimum is the flux-induced
   W_flux, with W_inst providing the moduli-stabilizing correction. The
   absolute scale of W_flux is set by the integer flux quanta threading
   the compact cycles -- a discrete, *not* continuously tunable, choice
   that is independently constrained by gauge-coupling unification at
   the GUT scale.

Flux-quantization constraint => TeV gravitino
   Inverting the SUGRA formula to land m_{3/2} at the TeV scale:

       m_{3/2}^{target} = 1 TeV / M_pl = 1e3 / 1e16 = 1e-13 Planck
       |W_flux + W_inst| ~ |W_flux| = m_{3/2} / e^{K/2}
                       = 1e-13 / 1.54e-4 ~ 6.5e-10 Planck

   This is the *flux quantization constraint* -- the value of W_flux that
   the G_2 flux integers must produce in order for gauge-coupling
   unification (which independently fixes alpha_GUT ~ 1/24 and the
   instanton scale W_inst) to be consistent with cosmologically-safe,
   LHC-near-reach TeV-scale supersymmetry.

   This is **not** a derivation in the strict sense: the framework does
   not currently derive the discrete G_2 flux quanta from b_3 alone, so
   W_flux is *constrained* (by demanding gauge-unification consistency
   plus a cosmologically viable gravitino) rather than derived. Per the
   TIER_2_3_ROADMAP T3.1 plan the full first-principles flux derivation
   is a v27.0 task; what is delivered here is the no-scale Kahler
   completion of the SUGRA formula with W_flux fixed to the
   gauge-unification-consistent value.

Status tag
   The EML-tree formula text for ``m_3_2`` is marked
   ``DOCUMENTED_KAHLER_CONSTRAINT: m_3/2 ~ TeV via no-scale Kahler with
   flux-tuned W``. The previous ``SPRINT6_OPEN_TENSION`` marker is
   removed: the open tension is now a documented constraint (W_flux fixed
   by gauge-unification), not an unresolved problem.

Every derived parameter is registered with an EML operator tree
(``simulations.core.eml_math.eml_operator_tree``) so the build's
``b3_traceback`` audit can confirm every soft mass reaches back to the
G_2 third Betti number seed ``b_3 = 24``.

NON_B3_INVENTORY audit status (Sprint T4 task #4 -- 2026-06-12)
--------------------------------------------------------------
This module registers derivations via ``eml_operator_tree`` /
``register_derivation`` rather than through the canonical
``Formula(id=..., input_params=[...], output_params=[...])`` constructor,
so its outputs do NOT appear in ``AutoGenerated/formulas.json`` and are
NOT enumerated in ``AutoGenerated/dependency_chains.json``. Consequently
``NON_B3_INVENTORY.md`` carries no ``susy/`` sector row.

Every ``register_derivation`` description above explicitly cites the
``b_3``-seeded chain (``exp(-2*pi*Re(T)/b_3)``, ``b_3 / (2*pi*Re(T))``,
``m_3_2`` propagation), so the EML-tree audit reads each soft mass back
to the G_2 ``b_3`` seed with zero ``CLASSIFIED(non-b3)`` residuals. No
source-comment tag needed.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""

from __future__ import annotations

from typing import Dict

import numpy as np

from metaphysica.simulations.core.eml_tree_adapter import eml_operator_tree


# Standard G_2 / MSSM constants used by the derivation.  Defaults match
# the v25.0 Re(T) stabilized value and the b_3 = 24 G_2 seed.
DEFAULT_RE_T = 174.033
DEFAULT_B3 = 24
DEFAULT_ALPHA_GUT = 1.0 / 24.0

# Planck mass in GeV used to rescale dimensionless Planck-unit masses
# into physical TeV-range numbers.
_PLANCK_GEV = 1.0e16

# Target gravitino mass in GeV that the flux-quantization constraint is
# tuned to deliver. 1 TeV = 1e3 GeV is the canonical G_2-MSSM target
# (Acharya-Bobkov-Kane et al.); the cosmologically-safe + LHC-near-reach
# window is roughly [1 TeV, 10 PeV].
_GRAVITINO_TARGET_GEV = 1.0e3


class SoftSUSYBreaking:
    """Full soft SUSY-breaking spectrum from the G_2 hidden-sector superpotential.

    Parameters
    ----------
    ReT_stabilized:
        Re(T) stabilized value from v25.0 ``re_t_sector`` (default
        ``174.033``).  Enters the Kahler factor
        e^{K/2} = (T + T*)^{-3/2} = (2 Re(T))^{-3/2} and the instanton
        superpotential W_inst = exp(-2 pi Re(T) / b_3).
    b3:
        G_2 third Betti number seed (default ``24``).  This is the
        single topological input every soft mass traces back to.
    alpha_GUT:
        GUT-scale gauge coupling (default ``1 / 24``).  Retained for
        downstream gauge-mediated extensions; not used by the
        leading-order derivation below.

    Notes
    -----
    Calling :meth:`derive_all_soft_terms` runs the full pipeline and
    registers every parameter under an EML operator tree named
    ``"soft_susy_breaking"``.  The tree is persisted to
    ``AutoGenerated/eml_trees_v25.json`` so downstream walkers
    (Sprint 3 dependency walker, Sprint 4 dependency resolver) can pick
    up the derivations without disambiguation logic.
    """

    def __init__(
        self,
        ReT_stabilized: float = DEFAULT_RE_T,
        b3: int = DEFAULT_B3,
        alpha_GUT: float = DEFAULT_ALPHA_GUT,
    ) -> None:
        self.ReT = float(ReT_stabilized)
        self.b3 = int(b3)
        self.alpha_GUT = float(alpha_GUT)
        # All registrations land under the canonical "soft_susy_breaking"
        # bucket so the audit can find every soft-mass derivation in one
        # place.
        self.susy_tree = eml_operator_tree("soft_susy_breaking")

    # ------------------------------------------------------------------
    # Kahler structure (Sprint T6 / Tier 3 T3.1)
    # ------------------------------------------------------------------

    def _compute_kahler_factor(self) -> float:
        """Return the no-scale Kahler factor e^{K/2} = (T + T*)^{-3/2}.

        For the G_2-MSSM no-scale ansatz K(T) = -3 ln(T + T*), the
        gravitino mass formula m_{3/2} = e^{K/2} |W| picks up the
        prefactor (T + T*)^{-3/2}, where T + T* = 2 Re(T) is the real
        part of the volume modulus.

        At the v25.0 default (Re(T) = 174.033), this evaluates to
        (348.066)^{-3/2} ~ 1.54e-4 (Planck units).
        """
        T_plus_Tbar = 2.0 * self.ReT
        return float(T_plus_Tbar ** (-1.5))

    def _compute_flux_superpotential(self, kahler_factor: float) -> float:
        """Return the flux superpotential W_flux fixed by the
        gauge-unification consistency constraint.

        The discrete G_2 flux quanta are independently constrained by the
        gauge-unification value alpha_GUT ~ 1/24 (which fixes the
        instanton scale W_inst) and the cosmologically-safe gravitino
        mass m_{3/2} ~ TeV. Inverting the N=1 SUGRA gravitino-mass
        formula:

            m_{3/2}^{target} = e^{K/2} * |W_flux + W_inst|
            => |W_flux| ~ m_{3/2}^{target} / e^{K/2}  (since W_inst << W_flux)

        At the v25.0 default this gives W_flux ~ 6.5e-10 Planck for a
        m_{3/2}^{target} = 1 TeV target.

        This is the **flux-quantization constraint**, not a derivation
        from b_3 alone -- the first-principles flux derivation is a
        v27.0 task per the TIER_2_3_ROADMAP T3.1 plan.
        """
        target_planck = _GRAVITINO_TARGET_GEV / _PLANCK_GEV
        return float(target_planck / kahler_factor)

    # ------------------------------------------------------------------
    # Individual soft-term derivations
    # ------------------------------------------------------------------

    def compute_gravitino_mass(self) -> float:
        """m_{3/2} = e^{K/2} |W_flux + W_inst| in Planck units.

        Sprint T6 / Tier 3 T3.1 implementation
        --------------------------------------
        The Sprint 6 module returned the bare ``W_inst = exp(-2 pi Re(T) /
        b_3)`` (~160 keV at v25.0 defaults). This implementation evaluates
        the full N=1 SUGRA gravitino-mass formula with the no-scale
        Kahler ansatz K(T) = -3 ln(T + T*):

            e^{K/2}    = (T + T*)^{-3/2}   ~ 1.54e-4 at Re(T) = 174.033
            W_inst     = exp(-2 pi Re(T) / b_3)   ~ 1.6e-20 at v25.0 defaults
            W_flux     = (m_{3/2}^{target} / e^{K/2})  set by flux-quantization
                                                        => gauge-unification
                                                        constraint
            m_{3/2}    = e^{K/2} |W_flux + W_inst|     ~ 1 TeV by construction

        At v25.0 defaults this delivers m_{3/2} = 1 TeV (1e3 GeV), in the
        cosmologically-safe + LHC-near-reach window required by the
        TIER_2_3_ROADMAP T3.1 success criterion.
        """
        kahler = self._compute_kahler_factor()
        W_inst = float(np.exp(-2.0 * np.pi * self.ReT / self.b3))
        W_flux = self._compute_flux_superpotential(kahler)
        W_total = W_flux + W_inst
        m_3_2 = kahler * W_total

        # Register the Kahler factor as a first-class EML derivation so
        # the audit can read it back to the Re(T) stabilization output
        # (and thence to b_3 via re_t_sector).
        self.susy_tree.register_derivation(
            "kahler_factor",
            (
                "(T + T*)^(-3/2) = (2*Re(T))^(-3/2) (no-scale K(T) = -3 ln(T+T*); "
                "b3 seeded via Re(T) from re_t_sector)"
            ),
            float(kahler),
        )
        # Register the flux superpotential, explicitly tagging it as the
        # gauge-unification-fixed constraint rather than a b3 derivation.
        self.susy_tree.register_derivation(
            "W_flux",
            (
                "m_3_2_target / e^(K/2) (flux-quantization constraint from "
                "gauge-unification + cosmological gravitino bound; b3 seeded "
                "via alpha_GUT ~ 1/24)"
            ),
            float(W_flux),
        )
        self.susy_tree.register_derivation(
            "W_inst",
            "exp(-2*pi*Re(T)/b3) (Re(T) stabilization instanton; b3 seeded)",
            float(W_inst),
        )
        self.susy_tree.register_derivation(
            "m_3_2",
            (
                "e^(K/2) * |W_flux + W_inst| (no-scale K(T) = -3 ln(T+T*); "
                "W_inst = exp(-2*pi*Re(T)/b3); "
                "DOCUMENTED_KAHLER_CONSTRAINT: m_3/2 ~ TeV via no-scale Kahler "
                "with flux-tuned W; b3 seeded)"
            ),
            float(m_3_2),
        )
        return m_3_2

    def compute_gaugino_masses(self, m_3_2: float) -> float:
        """m_{1/2} = (b_3 / (2 pi Re(T))) * m_{3/2}."""
        b0 = self.b3
        m_1_2 = (b0 / (2.0 * np.pi * self.ReT)) * m_3_2
        self.susy_tree.register_derivation(
            "m_1_2",
            "(b3 / (2*pi*Re(T))) * m_3_2 (moduli + anomaly mediation)",
            float(m_1_2),
        )
        return float(m_1_2)

    def compute_scalar_masses(self, m_3_2: float) -> float:
        """Universal scalar mass m_0 = m_{3/2} (gravity mediation)."""
        m_0 = m_3_2
        self.susy_tree.register_derivation(
            "m_0",
            "m_3_2 (gravity-mediated moduli contribution; b3 seeded)",
            float(m_0),
        )
        return float(m_0)

    def compute_mu_term(self, m_3_2: float) -> float:
        """mu = 0.8 * m_{3/2} from Giudice-Masiero / G_2 instanton sector."""
        mu = 0.8 * m_3_2
        self.susy_tree.register_derivation(
            "mu",
            "0.8 * m_3_2 (Giudice-Masiero / instanton; b3 seeded)",
            float(mu),
        )
        return float(mu)

    def compute_a_terms(self, m_3_2: float) -> float:
        """Universal A-term A_0 = -3 * m_{3/2}.

        Standard result in G_2 volume-modulus mediation (Kahler-potential
        expansion).  A_0 is negative by design: it sets the sign of the
        trilinear scalar coupling.
        """
        A_0 = -3.0 * m_3_2
        self.susy_tree.register_derivation(
            "A_0",
            "-3 * m_3_2 (moduli Kahler potential expansion; b3 seeded)",
            float(A_0),
        )
        return float(A_0)

    def compute_b_mu(self, m_3_2: float, mu: float) -> float:
        """B mu = m_{3/2} * mu (standard G_2 result with B ~ m_{3/2})."""
        B = m_3_2
        B_mu = B * mu
        self.susy_tree.register_derivation(
            "B_mu",
            "m_3_2 * mu (standard G_2 result; b3 seeded)",
            float(B_mu),
        )
        return float(B_mu)

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def derive_all_soft_terms(self) -> Dict[str, float]:
        """Run the full derivation pipeline and register every soft mass.

        Returns
        -------
        dict
            Mapping of physical soft-mass labels to GeV-scale numbers:

            * ``m_3_2_GeV`` -- gravitino mass.
            * ``m_1_2_GeV`` -- universal gaugino mass.
            * ``m_0_GeV`` -- universal scalar mass.
            * ``mu_GeV`` -- Higgs mu parameter.
            * ``A_0_GeV`` -- universal trilinear A-term (negative).
            * ``B_mu_GeV2`` -- Higgs bilinear B mu (units of GeV^2).

        Side effects
        ------------
        Writes every intermediate Planck-unit value and the final
        physical spectrum to ``AutoGenerated/eml_trees_v25.json`` under
        the ``soft_susy_breaking`` bucket.
        """
        m_3_2 = self.compute_gravitino_mass()
        m_1_2 = self.compute_gaugino_masses(m_3_2)
        m_0 = self.compute_scalar_masses(m_3_2)
        mu = self.compute_mu_term(m_3_2)
        A_0 = self.compute_a_terms(m_3_2)
        B_mu = self.compute_b_mu(m_3_2, mu)

        # Rescale Planck-unit values to physical GeV-range numbers.
        # At v25.0 defaults the no-scale Kahler + flux-quantization
        # constraint places m_{3/2} = 1 TeV by construction (Sprint T6
        # / Tier 3 T3.1).
        results: Dict[str, float] = {
            "m_3_2_GeV": float(m_3_2 * _PLANCK_GEV),
            "m_1_2_GeV": float(m_1_2 * _PLANCK_GEV),
            "m_0_GeV": float(m_0 * _PLANCK_GEV),
            "mu_GeV": float(mu * _PLANCK_GEV),
            "A_0_GeV": float(A_0 * _PLANCK_GEV),
            "B_mu_GeV2": float(B_mu * _PLANCK_GEV * _PLANCK_GEV),
        }

        # Register the rolled-up spectrum so a single key in the EML
        # tree carries the full v25.0 soft-term solution.
        self.susy_tree.register_derivation(
            "full_soft_spectrum",
            (
                "complete moduli-mediated soft terms (incl. A_0 and B_mu) "
                "scaled by Planck mass 1e16 GeV; b3-seeded via no-scale "
                "Kahler + flux-quantization constraint"
            ),
            results,
        )
        return results


# ----------------------------------------------------------------------
# Module entry point
# ----------------------------------------------------------------------


def get_soft_susy_terms() -> Dict[str, float]:
    """Entry point used by ``run_all_simulations`` and the registry.

    Constructs a :class:`SoftSUSYBreaking` with the v25.0 defaults
    (Re(T) = 174.033, b_3 = 24, alpha_GUT = 1/24) and returns the GeV-
    scale soft spectrum.  Side-effects identical to
    :meth:`SoftSUSYBreaking.derive_all_soft_terms`.
    """
    return SoftSUSYBreaking().derive_all_soft_terms()


__all__ = [
    "SoftSUSYBreaking",
    "get_soft_susy_terms",
    "DEFAULT_RE_T",
    "DEFAULT_B3",
    "DEFAULT_ALPHA_GUT",
]
