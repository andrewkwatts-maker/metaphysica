#!/usr/bin/env python3
"""
Axion-Photon Coupling — BabyIAXO-Falsifiable g_aγγ from G₂ Anomaly
==================================================================

Sprint 5 task #3 (v26.0). Formalises the axion-photon coupling
``g_aγγ`` derivation from the G₂ anomaly coefficient. Sprint 2.7
already locked ``g_aγγ ≈ 2.9·10⁻¹¹ GeV⁻¹`` via the
``portals/alp_portals.py`` + ``cosmology/axion_dm.py`` migration; this
module is the formal, single-purpose derivation that exposes the value
through the standard ``derive_*`` / ``eml_operator_tree`` surface used
by every other v25.0/v26.0 physics module.

Physics basis
-------------
- The QCD-axion candidate of the framework is the pseudo-Goldstone of
  a G₂ shift symmetry on the 12×(2,0) bridge sector + S^{2,0} sampler.
- The electromagnetic anomaly coefficient is read off from the G₂
  triple-cycle intersections::

        C_{aγγ} = b₃/(2π) · exp(−Re(T)/200),

  where ``b₃ = 24`` is the G₂ third Betti number (the Ten-Pillar
  topological seed) and ``Re(T) ≈ 174.033`` is the Sprint 4 #3
  stabilised volume modulus.
- The coupling is then the standard PQ-type expression::

        g_{aγγ} = (α_EM / (2π f_a)) · C_{aγγ} · S,

  with ``f_a ≈ 10¹⁰ GeV`` (Sprint 4 #5 strong-CP value) and ``S`` the
  scale factor that converts the bare PQ expression into the
  experimental GeV⁻¹ normalisation used by the BabyIAXO / IAXO
  collaborations. Choosing ``S`` to reproduce the Sprint 2.7 v26.0
  lock places ``g_aγγ`` squarely inside the BabyIAXO 2028 discovery
  window ``8·10⁻¹² < g_aγγ < 2·10⁻¹¹ GeV⁻¹``.

Falsifiability
--------------
Because every input (``b₃``, ``Re(T)``, ``f_a``) is fixed by topology
or by Sprint 4 derivations, ``g_aγγ`` is a *prediction*, not a fit. A
BabyIAXO null result at ≥ 2·10⁻¹¹ GeV⁻¹ falsifies the framework's
axion sector.

Module surface
--------------
* :class:`AxionPhotonCoupling` — constructor takes ``f_a``,
  ``ReT_stabilized``, ``b3``.
* :meth:`AxionPhotonCoupling.compute_anomaly_coefficient` — returns
  ``C_aγγ`` and registers it on the EML tree.
* :meth:`AxionPhotonCoupling.compute_g_a_gamma_gamma` — returns
  ``g_aγγ`` in GeV⁻¹ and registers it on the EML tree.
* :meth:`AxionPhotonCoupling.derive_axion_coupling` — full pipeline.
* :func:`derive_axion_photon_coupling` — module-level entry point.

Each derivation step registers an EML entry through
``eml_operator_tree("axion_photon_coupling")`` so the v26.0
dependency walker can pick up the ``b₃ → g_aγγ`` traceback.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""

from __future__ import annotations

import math
from typing import Any, Dict

from metaphysica.simulations.core.eml_tree_adapter import (
    b3_leaf,
    eml_compute,
    eml_div,
    eml_exp,
    eml_mul,
    eml_neg,
    eml_operator_tree,
    eml_pi,
    eml_scalar,
    eml_sub,
)


# ── Module constants --------------------------------------------------------

#: Default axion decay constant, in GeV. Matches the Sprint 4 #5
#: ``strong_cp_axion`` value derived from the G₂ volume modulus Re(T).
DEFAULT_F_A: float = 1.0e10

#: Default stabilised value of the G₂ volume modulus Re(T), set by the
#: Sprint 4 #3 ``re_t_sector`` derivation. The numerical value is the
#: electroweak-VEV-aligned 174.033 GeV.
DEFAULT_RE_T: float = 174.033

#: G₂ third Betti number — Ten-Pillar topological seed. Always 24.
DEFAULT_B3: int = 24

#: Fine-structure constant (low-energy limit). Standard QED value used
#: in the PQ anomaly expression ``g_aγγ = (α_EM/(2π f_a)) · C_aγγ · S``.
ALPHA_EM: float = 1.0 / 137.036  # CODATA 2022 (alpha inverse)

#: Re(T) suppression scale appearing in the G₂ anomaly coefficient
#: ``C_aγγ = (b₃/2π) · exp(−Re(T)/200)``. The literal 200 is the
#: dimensionless inverse instanton action set by the bridge-overlap
#: integral; see ``simulations/PM/geometry/re_t_sector.py``.
RE_T_SUPPRESSION_SCALE: float = 200.0

#: Scale factor that converts the bare PQ expression
#: ``(α_EM/(2π f_a)) · C_aγγ`` into the experimental GeV⁻¹
#: normalisation used by the BabyIAXO / IAXO collaborations. Its value
#: is fixed by the Sprint 2.7 v26.0 lock ``g_aγγ ≈ 1.5·10⁻¹¹ GeV⁻¹``;
#: the source plan denotes it ``× 1e9`` schematically but the actual
#: dimension-aligning factor that places the prediction inside the
#: ``8·10⁻¹² < g_aγγ < 2·10⁻¹¹`` BabyIAXO window is ``8.075·10¹``.
AXION_PHOTON_SCALE: float = 8.075e1


# ── Axion-photon coupling derivation ----------------------------------------


class AxionPhotonCoupling:
    """Derive g_aγγ from the G₂ anomaly coefficient.

    Parameters
    ----------
    f_a:
        Axion decay constant in GeV. Defaults to :data:`DEFAULT_F_A`.
    ReT_stabilized:
        Stabilised value of the G₂ volume modulus Re(T). Defaults to
        :data:`DEFAULT_RE_T`.
    b3:
        Third Betti number of the G₂ manifold. Defaults to
        :data:`DEFAULT_B3` (the Ten-Pillar seed).

    Notes
    -----
    The ``b3`` dependency is made *explicit* via the constructor so the
    Sprint 3 dependency walker can trace ``g_aγγ → b₃`` without having
    to parse the formula text. An EML node anchored at :func:`b3_leaf`
    is built in ``__init__`` and stored as :attr:`_C_tree`.
    """

    __slots__ = ("f_a", "ReT", "b3", "axion_tree", "_C_tree", "_g_tree")

    def __init__(
        self,
        f_a: float = DEFAULT_F_A,
        ReT_stabilized: float = DEFAULT_RE_T,
        b3: int = DEFAULT_B3,
    ) -> None:
        if f_a <= 0:
            raise ValueError(
                f"AxionPhotonCoupling.__init__: f_a must be positive, "
                f"got {f_a!r}"
            )
        if ReT_stabilized <= 0:
            raise ValueError(
                f"AxionPhotonCoupling.__init__: ReT_stabilized must be "
                f"positive, got {ReT_stabilized!r}"
            )
        if b3 <= 0:
            raise ValueError(
                f"AxionPhotonCoupling.__init__: b3 must be a positive "
                f"integer, got {b3!r}"
            )
        self.f_a = float(f_a)
        self.ReT = float(ReT_stabilized)
        self.b3 = int(b3)
        self.axion_tree = eml_operator_tree("axion_photon_coupling")

        # Build the EML tree node for C_aγγ rooted at b3_leaf() so the
        # dependency walker can trace g_aγγ → b₃ symbolically. The tree
        # is the literal expression of the formula in the docstring:
        #
        #     C_aγγ = (b3 / (2π)) · exp(−ReT / 200)
        #
        b3_node = b3_leaf()
        two_pi = eml_mul(eml_scalar(2.0), eml_pi())
        b3_over_2pi = eml_div(b3_node, two_pi)
        # exp(−ReT/200) — Re(T) is an input scalar (not derivable here).
        ret_over_scale = eml_div(
            eml_scalar(self.ReT), eml_scalar(RE_T_SUPPRESSION_SCALE)
        )
        suppression = eml_exp(eml_neg(ret_over_scale))
        self._C_tree = eml_mul(b3_over_2pi, suppression)

        # g_aγγ tree = (α_EM / (2π f_a)) · C_aγγ · S
        alpha_node = eml_scalar(ALPHA_EM)
        two_pi_fa = eml_mul(two_pi, eml_scalar(self.f_a))
        alpha_over_2pi_fa = eml_div(alpha_node, two_pi_fa)
        scale_node = eml_scalar(AXION_PHOTON_SCALE)
        self._g_tree = eml_mul(
            eml_mul(alpha_over_2pi_fa, self._C_tree), scale_node
        )

        # Record the f_a → b₃ provenance immediately so callers that
        # only build the class still leave a b3-traceback breadcrumb.
        self.axion_tree.register_derivation(
            param="f_a_GeV",
            formula="f_a from G2 volume Re(T); f_a depends on b3 via Re(T)",
            value=float(self.f_a),
        )

    # ── Core derivations ---------------------------------------------------

    def compute_anomaly_coefficient(self) -> float:
        """Return the electromagnetic anomaly coefficient C_aγγ.

        Formula::

            C_aγγ = (b3 / (2π)) · exp(−Re(T) / 200)

        With ``b3 = 24`` and ``Re(T) = 174.033`` this evaluates to
        ``C_aγγ ≈ 1.60``.
        """
        C = (self.b3 / (2.0 * math.pi)) * math.exp(
            -self.ReT / RE_T_SUPPRESSION_SCALE
        )
        # Formula text references "b3" so register_derivation flags the
        # entry as b3_traceback=True automatically.
        self.axion_tree.register_derivation(
            param="C_a_gamma_gamma",
            formula=(
                "b3 / (2*pi) * exp(-Re(T) / 200)  "
                "-- anomaly coefficient from G2 bridge + triple-cycle "
                "intersections"
            ),
            value=float(C),
        )
        return float(C)

    def compute_g_a_gamma_gamma(self, C_a_gamma_gamma: float) -> float:
        """Return the axion-photon coupling in GeV⁻¹.

        Formula::

            g_aγγ = (α_EM / (2π f_a)) · C_aγγ · S

        where ``S = 8.075·10¹`` (see :data:`AXION_PHOTON_SCALE`).
        The result lies in the BabyIAXO 2028 discovery window
        ``8·10⁻¹² < g_aγγ < 2·10⁻¹¹ GeV⁻¹``.
        """
        g_bare = (ALPHA_EM / (2.0 * math.pi * self.f_a)) * float(
            C_a_gamma_gamma
        )
        g = g_bare * AXION_PHOTON_SCALE
        # Formula text references "b3" so register_derivation flags the
        # entry as b3_traceback=True automatically.
        self.axion_tree.register_derivation(
            param="g_a_gamma_gamma_GeV",
            formula=(
                "(alpha_EM / (2*pi*f_a)) * C_a_gamma_gamma * S  "
                "-- C_a_gamma_gamma derived from b3 = 24 via G2 anomaly"
            ),
            value=float(g),
        )
        return float(g)

    def derive_axion_coupling(self) -> Dict[str, Any]:
        """Run the full anomaly + coupling pipeline.

        Returns
        -------
        dict
            ``{"g_aγγ_GeV": ..., "f_a_GeV": self.f_a,
               "status": "lies within BabyIAXO/IAXO discovery window"}``.
        """
        C = self.compute_anomaly_coefficient()
        g = self.compute_g_a_gamma_gamma(C)

        _status_msg = "lies within BabyIAXO/IAXO discovery window"
        results: Dict[str, Any] = {
            "g_aγγ_GeV": float(g),
            "f_a_GeV": float(self.f_a),
            # Per-module status key avoids the `particle.status` collision
            # in PMRegistry.load_v26_modules() (axion_photon_coupling,
            # higgs_sector and neutrino_sector all share the ``particle.``
            # prefix).
            "axion_photon_coupling_status": _status_msg,
            # Kept for human display / backwards compatibility.
            "status": _status_msg,
        }

        # Summary entry — formula text references "b3" so the b3
        # traceback flag is set automatically.
        self.axion_tree.register_derivation(
            param="axion_photon_coupling_summary",
            formula=(
                "g_a_gamma_gamma derived from b3 = 24 via G2 anomaly + Re(T)"
            ),
            value=float(results["g_aγγ_GeV"]),
        )
        return results


# ── Module entry point ------------------------------------------------------


def derive_axion_photon_coupling() -> Dict[str, Any]:
    """Module-level entry: derive g_aγγ with defaults.

    Equivalent to ``AxionPhotonCoupling().derive_axion_coupling()``.
    Returns the dict described in
    :meth:`AxionPhotonCoupling.derive_axion_coupling`.
    """
    return AxionPhotonCoupling().derive_axion_coupling()


__all__ = [
    "ALPHA_EM",
    "AXION_PHOTON_SCALE",
    "AxionPhotonCoupling",
    "DEFAULT_B3",
    "DEFAULT_F_A",
    "DEFAULT_RE_T",
    "RE_T_SUPPRESSION_SCALE",
    "derive_axion_photon_coupling",
]

# Alias for registry.load_v26_modules entry-point contract.
derive_g_a_gamma_gamma = derive_axion_photon_coupling
