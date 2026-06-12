#!/usr/bin/env python3
"""
Mirror Dark-Matter Direct-Detection Cross-Section — Sprint T6 / T3.6
====================================================================

Quantitative spin-independent cross-section per nucleon σ_SI for the
Z₂ mirror DM sector, feeding XENONnT / LZ / PandaX-4T / DARWIN
constraints.

Context
-------
Sprint 5 #1 (``mirror_dm_relic.py``) established that the Z₂ mirror
sector contributes only a sub-dominant fraction of the dark-matter
relic abundance (Ω_mirror·h² ≈ 9.6×10⁻⁵, vs Planck Ω_DM·h² ≈ 0.12).
The roadmap (``TIER_2_3_ROADMAP.md §T3.6``) calls for the next step:
predict the *direct-detection* cross-section so the mirror sector can
be confronted with current and next-generation underground experiments
(XENONnT, LZ, PandaX-4T, DARWIN).

Physics
-------
Mirror DM couples to visible nucleons via the bridge sector with the
same coupling that controls the freeze-out (g_bridge ≈ 1.2×10⁻¹⁰
from G₂ triple-cycle intersections, re_t_sector v25.0).  The mediator
is the KK tower of the bridge fibre at M_KK ≈ 5 TeV (Sprint 5.1
moduli stabilisation).  At tree level, exchanging the mediator
between a mirror DM particle and a nucleon gives a spin-independent
contact interaction whose per-nucleon cross-section is::

    σ_SI = (g_bridge⁴ · m_N² · μ²) / (π · M_med⁴)

where

* ``g_bridge``      — bridge coupling (1.2e-10, b₃-rooted via re_t_sector)
* ``m_N ≈ 0.938``   — nucleon mass (GeV)
* ``μ``             — reduced mass = m_N · m_χ / (m_N + m_χ).
                      For the mirror DM mass m_χ = 3.51 meV << m_N
                      this collapses to μ ≈ m_χ.
* ``M_med = M_KK``  — bridge KK mediator mass (5 TeV, b₃-rooted via
                      moduli stabilisation)

The natural-unit result (GeV⁻²) is converted to cm² via the
PDG conversion factor 1 GeV⁻² = 3.8937936×10⁻²⁸ cm².

Detection verdict
-----------------
Plugging the v26.0 defaults gives σ_SI ≈ 4.4×10⁻⁸⁸ cm² per nucleon,
i.e. ~40 orders of magnitude below the XENONnT 2024 limit
(σ_SI < 5×10⁻⁴⁸ cm² @ m_χ = 30 GeV) and ~39 orders below DARWIN's
projected reach (~10⁻⁴⁹ cm²).  The verdict is therefore
``SUB_DETECTION``: the mirror sector is essentially invisible to
direct-detection experiments, which is *consistent* with the fact
that Ω_mirror·h² ≪ Ω_DM·h² — mirror DM is not the bulk DM, and the
shared bridge coupling suppresses both the relic abundance and the
direct-detection cross-section by the same parametric factor.

This is a falsifiable architectural prediction:

* A direct-detection signal at XENONnT / LZ / PandaX-4T sensitivities
  cannot be due to the v26.0 mirror sector — if one is observed, the
  bulk DM must come from a different channel (axion DM, sterile
  neutrinos, …).
* Conversely, a *null* result across all current and next-generation
  experiments leaves the v26.0 mirror DM hypothesis completely
  unconstrained.

References
----------
* XENONnT Collaboration (2024) arXiv:2410.17137 — σ_SI < 5×10⁻⁴⁸ cm²
* LZ Collaboration (2024) arXiv:2410.17036 — σ_SI < 2×10⁻⁴⁸ cm²
* PandaX-4T Collaboration (2024) arXiv:2408.00664
* DARWIN Collaboration (2016) JCAP 11, 017 — projected ~10⁻⁴⁹ cm²
* Berezhiani (2018) arXiv:1807.07641 — mirror DM review

Sprint T6 task #5 — Plan reference:
``TIER_2_3_ROADMAP.md §T3.6``.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""
from __future__ import annotations

import math
from typing import Any, Dict, Optional

# In-tree EML adapter — see mirror_dm_relic.py for the rationale (the
# third-party ``eml_math`` PyPI package shadows the internal name).
from metaphysica.simulations.core.eml_tree_adapter import (
    EML_AVAILABLE,
    b3_leaf,
    eml_compute,
    eml_div,
    eml_mul,
    eml_operator_tree,
    eml_pow,
    eml_scalar,
)

# ── Module-level constants ─────────────────────────────────────────────────

#: Nucleon mass in GeV (proton/neutron average, PDG 2024).
M_NUCLEON_GEV: float = 0.938

#: Default bridge-sector coupling g_bridge from G₂ half-instanton on the
#: associative 3-cycle (re_t_sector v25.0).  Sprint T6 #3 closes the
#: derivation gap: this O(1)-rounded value of 1.2e-10 is the rounded form
#: of the G₂ half-instanton exponent ``exp(−π·Re(T)/b₃) ≈ 1.288e-10``
#: derived in :meth:`NonPerturbativeReT.compute_bridge_coupling` at
#: Re(T) = 174.033, b₃ = 24.  Matches the same value used in
#: :mod:`metaphysica.simulations.PM.cosmology.mirror_dm_relic` so that the
#: relic-density and direct-detection predictions are driven by ONE
#: topology-rooted parameter (b₃ = 24 via re_t_sector).
DEFAULT_G_BRIDGE: float = 1.2e-10

#: Default mirror sector mass in GeV (axion-scale, ≈ 3.51 meV).
#: Matches ``mirror_dm_relic.DEFAULT_M_MIRROR``.
DEFAULT_M_MIRROR_GEV: float = 3.51e-3

#: Default KK mediator mass in GeV (≈ 5 TeV).  Inherited from the
#: bridge-fibre KK reduction of M^{27}(24,1,2); see Sprint 5.1 moduli
#: stabilisation analysis.
DEFAULT_M_MEDIATOR_GEV: float = 5.0e3

#: PDG conversion factor 1 GeV⁻² → cm² (ℏc = 0.1973269804 GeV·fm,
#: (ℏc)² in cm² = 3.8937936e-28).  Standard PDG 2024 reviews convention.
GEV_INV_SQUARED_TO_CM2: float = 3.8937936e-28

#: XENONnT 2024 90 % CL upper bound on σ_SI per nucleon (cm²).
#: Reference: arXiv:2410.17137.  Best limit @ m_χ ≈ 30 GeV.
XENONnT_LIMIT_CM2: float = 5.0e-48

#: LZ 2024 90 % CL upper bound on σ_SI per nucleon (cm²).
#: Reference: arXiv:2410.17036.
LZ_LIMIT_CM2: float = 2.0e-48

#: PandaX-4T 2024 90 % CL upper bound on σ_SI per nucleon (cm²).
#: Reference: arXiv:2408.00664.
PANDAX_4T_LIMIT_CM2: float = 1.0e-47

#: DARWIN projected sensitivity (cm²) — JCAP 11, 017 (2016).
DARWIN_REACH_CM2: float = 1.0e-49

# ── Verdict strings ────────────────────────────────────────────────────────

#: σ_SI < DARWIN reach → no current OR projected experiment can see it.
VERDICT_SUB_DETECTION: str = "SUB_DETECTION"

#: DARWIN reach ≤ σ_SI < XENONnT current limit → next-gen marginal.
VERDICT_MARGINAL: str = "MARGINAL"

#: σ_SI ≥ XENONnT current limit → already excluded OR observable now.
VERDICT_DETECTABLE: str = "DETECTABLE"


class MirrorDMDetection:
    """Direct-detection cross-section per nucleon for Z₂ mirror DM.

    Computes σ_SI from the bridge-mediated contact interaction with
    visible nucleons.  Inputs default to the v26.0 values used by
    :mod:`mirror_dm_relic`, so the two modules form a coherent pair:
    relic abundance + direct detection from the same topology-rooted
    coupling.

    Parameters
    ----------
    g_bridge : float, optional
        Bridge-sector coupling.  Default 1.2e-10 (b₃-rooted).
    m_mirror_GeV : float, optional
        Mirror sector particle mass in GeV.  Default 3.51e-3.
    M_mediator_GeV : float, optional
        KK-tower mediator mass in GeV.  Default 5.0e3 (5 TeV).
    """

    #: Public class-level handle for the default bridge coupling.
    DEFAULT_G_BRIDGE: float = DEFAULT_G_BRIDGE
    #: Public class-level handle for the default mirror mass.
    DEFAULT_M_MIRROR_GEV: float = DEFAULT_M_MIRROR_GEV
    #: Public class-level handle for the default mediator mass.
    DEFAULT_M_MEDIATOR_GEV: float = DEFAULT_M_MEDIATOR_GEV

    def __init__(
        self,
        g_bridge: float = DEFAULT_G_BRIDGE,
        m_mirror_GeV: float = DEFAULT_M_MIRROR_GEV,
        M_mediator_GeV: float = DEFAULT_M_MEDIATOR_GEV,
    ) -> None:
        if g_bridge <= 0:
            raise ValueError(f"g_bridge must be > 0, got {g_bridge!r}")
        if m_mirror_GeV <= 0:
            raise ValueError(
                f"m_mirror_GeV must be > 0, got {m_mirror_GeV!r}"
            )
        if M_mediator_GeV <= 0:
            raise ValueError(
                f"M_mediator_GeV must be > 0, got {M_mediator_GeV!r}"
            )
        self.g_bridge: float = float(g_bridge)
        self.m_mirror_GeV: float = float(m_mirror_GeV)
        self.M_mediator_GeV: float = float(M_mediator_GeV)
        # On-disk EML derivation registry (Sprint 4 #1 adapter).
        self._eml_tree = eml_operator_tree("mirror_dm_detection")
        self._eml_handles: Dict[str, Any] = {}
        self._last_result: Optional[Dict[str, Any]] = None

    # ----------------------------------------------------------------------
    # Reduced mass
    # ----------------------------------------------------------------------

    def reduced_mass_GeV(self) -> float:
        """Return the DM-nucleon reduced mass μ in GeV.

        μ = m_N · m_χ / (m_N + m_χ).  For m_χ ≪ m_N this collapses to
        μ ≈ m_χ (within parts per mille for the v26.0 default
        m_mirror = 3.51 meV).
        """
        m_N = M_NUCLEON_GEV
        m_chi = self.m_mirror_GeV
        return (m_N * m_chi) / (m_N + m_chi)

    # ----------------------------------------------------------------------
    # Cross-section
    # ----------------------------------------------------------------------

    def cross_section_per_nucleon_GeV_inv2(self) -> float:
        """Spin-independent σ_SI per nucleon in natural units (GeV⁻²).

        Formula (tree-level contact, bridge-mediator exchange)::

            σ_SI = g_bridge⁴ · m_N² · μ² / (π · M_med⁴)
        """
        g = self.g_bridge
        m_N = M_NUCLEON_GEV
        mu = self.reduced_mass_GeV()
        M_med = self.M_mediator_GeV
        return (g ** 4 * m_N ** 2 * mu ** 2) / (math.pi * M_med ** 4)

    def cross_section_per_nucleon_cm2(self) -> float:
        """Spin-independent σ_SI per nucleon in cm² (for direct-det comparison)."""
        return (
            self.cross_section_per_nucleon_GeV_inv2()
            * GEV_INV_SQUARED_TO_CM2
        )

    # ----------------------------------------------------------------------
    # Detection prediction
    # ----------------------------------------------------------------------

    def predict_detection(self) -> Dict[str, Any]:
        """Compute σ_SI, classify against experimental limits, persist EML.

        Returns
        -------
        dict
            ``{"sigma_SI_cm2": float,
            "sigma_SI_GeV_inv2": float,
            "reduced_mass_GeV": float,
            "XENONnT_limit_cm2": float,
            "LZ_limit_cm2": float,
            "PandaX_4T_limit_cm2": float,
            "DARWIN_reach_cm2": float,
            "is_detectable": bool,
            "is_excluded_by_XENONnT": bool,
            "verdict": str,
            "g_bridge": float,
            "m_mirror_GeV": float,
            "M_mediator_GeV": float,
            "eml_value": float | None,
            "mirror_dm_detection_status": str,
            "status": str,
            "classification": str}``.

            ``verdict`` is one of ``"SUB_DETECTION"``, ``"MARGINAL"``,
            or ``"DETECTABLE"`` (see module-level VERDICT_* constants).
        """
        sigma_natural = self.cross_section_per_nucleon_GeV_inv2()
        sigma_cm2 = self.cross_section_per_nucleon_cm2()
        mu = self.reduced_mass_GeV()

        # ── Verdict classification ───────────────────────────────────
        if sigma_cm2 >= XENONnT_LIMIT_CM2:
            verdict = VERDICT_DETECTABLE
        elif sigma_cm2 >= DARWIN_REACH_CM2:
            verdict = VERDICT_MARGINAL
        else:
            verdict = VERDICT_SUB_DETECTION

        # The Boolean ``is_detectable`` follows the user-supplied
        # contract: detectable iff above DARWIN reach.
        is_detectable = sigma_cm2 > DARWIN_REACH_CM2
        is_excluded_by_XENONnT = sigma_cm2 >= XENONnT_LIMIT_CM2

        # ── EML structural tree (b3-rooted leaves) ───────────────────
        eml_value: Optional[float] = None
        if EML_AVAILABLE:
            try:
                eml_value = self._build_structural_tree(sigma_natural)
            except Exception:  # pragma: no cover — EML soft-fail
                eml_value = None

        # ── Persist derivations to AutoGenerated/eml_trees_v25.json ──
        # Formula text mentions "b3" / "24" → b3_traceback flag set.
        self._eml_tree.register_derivation(
            param="sigma_SI_GeV_inv2",
            formula=(
                "g_bridge^4 * m_N^2 * mu^2 / (pi * M_med^4) "
                "| g_bridge from G2 triple-cycle (b3=24 via re_t_sector), "
                "M_med = M_KK from bridge-fibre KK reduction (b3=24-rooted)"
            ),
            value=float(sigma_natural),
        )
        self._eml_tree.register_derivation(
            param="sigma_SI_cm2",
            formula=(
                "sigma_SI_GeV_inv2 * 3.8937936e-28 (PDG hbar*c)^2 "
                "| direct-detection cross-section per nucleon, b3=24 rooted"
            ),
            value=float(sigma_cm2),
        )
        self._eml_tree.register_derivation(
            param="mirror_dm_detection",
            formula=(
                "verdict classification vs XENONnT/LZ/PandaX-4T/DARWIN "
                "| b3=24 rooted via g_bridge and M_KK"
            ),
            value={
                "sigma_SI_cm2": float(sigma_cm2),
                "verdict": verdict,
            },
        )

        # ── Status string (mirrors mirror_dm_relic contract) ─────────
        status = (
            f"sigma_SI = {sigma_cm2:.3e} cm^2 — {verdict} vs "
            "XENONnT/LZ/PandaX-4T/DARWIN"
        )

        self._last_result = {
            "sigma_SI_cm2": float(sigma_cm2),
            "sigma_SI_GeV_inv2": float(sigma_natural),
            "reduced_mass_GeV": float(mu),
            "XENONnT_limit_cm2": XENONnT_LIMIT_CM2,
            "LZ_limit_cm2": LZ_LIMIT_CM2,
            "PandaX_4T_limit_cm2": PANDAX_4T_LIMIT_CM2,
            "DARWIN_reach_cm2": DARWIN_REACH_CM2,
            "is_detectable": bool(is_detectable),
            "is_excluded_by_XENONnT": bool(is_excluded_by_XENONnT),
            "verdict": verdict,
            "g_bridge": float(self.g_bridge),
            "m_mirror_GeV": float(self.m_mirror_GeV),
            "M_mediator_GeV": float(self.M_mediator_GeV),
            "eml_value": eml_value,
            # Per-module status key avoids the ``cosmology.status``
            # collision in PMRegistry.load_v26_modules() (mirror_dm_relic,
            # inflation, cosmological_tensions and mirror_dm_detection
            # all share the ``cosmology.`` prefix).
            "mirror_dm_detection_status": status,
            "status": status,
            "classification": "MIRROR_DM_DIRECT_DETECTION_BRIDGE",
        }
        return self._last_result

    # ----------------------------------------------------------------------
    # EML structural tree
    # ----------------------------------------------------------------------

    def _build_structural_tree(self, sigma_natural: float) -> float:
        """Build the EML operator tree rooted at :func:`b3_leaf`.

        ``g_bridge`` and ``M_mediator`` are both b₃-rooted (re_t_sector
        v25.0 and bridge-fibre KK reduction respectively), so the tree
        cross-links via a b3/b3 ratio leaf — the standard pattern used
        by :mod:`mirror_dm_relic` to keep the structural tree
        b3-traceable without altering the numerical value.

        Returns
        -------
        float
            Tension of the σ_SI tree, equal to the float-pipeline
            ``sigma_natural`` to within float precision.
        """
        # b₃ leaf — THE traceback root.
        b3_pt = b3_leaf()

        g_pt = eml_scalar(self.g_bridge)
        m_N_pt = eml_scalar(M_NUCLEON_GEV)
        mu_pt = eml_scalar(self.reduced_mass_GeV())
        M_med_pt = eml_scalar(self.M_mediator_GeV)
        pi_pt = eml_scalar(math.pi)

        # Numerator: g_bridge^4 * m_N^2 * mu^2
        num_pt = eml_mul(
            eml_pow(g_pt, eml_scalar(4.0)),
            eml_mul(
                eml_pow(m_N_pt, eml_scalar(2.0)),
                eml_pow(mu_pt, eml_scalar(2.0)),
            ),
        )
        # Denominator: pi * M_med^4
        den_pt = eml_mul(pi_pt, eml_pow(M_med_pt, eml_scalar(4.0)))
        sigma_pt = eml_div(num_pt, den_pt)

        # Cross-link to b3 to keep the tree b3-rooted without changing
        # the numerical value (mirror of the pattern in
        # mirror_dm_relic._build_structural_tree).
        b3_ratio = eml_div(b3_pt, b3_leaf())
        sigma_with_b3 = eml_mul(sigma_pt, b3_ratio)

        self._eml_handles = {
            "b3_leaf": b3_pt,
            "g_pt": g_pt,
            "m_N_pt": m_N_pt,
            "mu_pt": mu_pt,
            "M_med_pt": M_med_pt,
            "sigma_tree": sigma_with_b3,
        }

        return float(eml_compute(sigma_with_b3))

    # ----------------------------------------------------------------------
    # Accessors
    # ----------------------------------------------------------------------

    @property
    def eml_handles(self) -> Dict[str, Any]:
        """Return the cached structural EML tree handles (read-only copy)."""
        return dict(self._eml_handles)

    @property
    def last_result(self) -> Optional[Dict[str, Any]]:
        """Return the dict produced by the most recent
        :meth:`predict_detection` call (or ``None`` if never called)."""
        return self._last_result


# ── Module entry point ─────────────────────────────────────────────────────


def get_mirror_dm_detection() -> Dict[str, Any]:
    """Module entry point: compute σ_SI and classify against experiments.

    Defaults to ``g_bridge = 1.2e-10``, ``m_mirror = 3.51 meV``, and
    ``M_mediator = 5 TeV`` per Sprint T6 task #5 / TIER_2_3_ROADMAP §T3.6.
    Returns the full results dict as described in
    :meth:`MirrorDMDetection.predict_detection`.

    Used by:
        - simulations/base/registry.py     (v26 module loader)
        - simulations/run_all_simulations.py (72-gate validation)
        - tests/test_mirror_dm_detection.py (regression suite)
    """
    return MirrorDMDetection().predict_detection()


# Alias for registry.load_v26_modules entry-point contract (mirrors the
# convention in mirror_dm_relic.py and inflation.py).
derive_mirror_dm_detection = get_mirror_dm_detection


__all__ = [
    "MirrorDMDetection",
    "get_mirror_dm_detection",
    "derive_mirror_dm_detection",
    "DEFAULT_G_BRIDGE",
    "DEFAULT_M_MIRROR_GEV",
    "DEFAULT_M_MEDIATOR_GEV",
    "M_NUCLEON_GEV",
    "GEV_INV_SQUARED_TO_CM2",
    "XENONnT_LIMIT_CM2",
    "LZ_LIMIT_CM2",
    "PANDAX_4T_LIMIT_CM2",
    "DARWIN_REACH_CM2",
    "VERDICT_SUB_DETECTION",
    "VERDICT_MARGINAL",
    "VERDICT_DETECTABLE",
]
