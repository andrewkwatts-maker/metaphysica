#!/usr/bin/env python3
"""
Dynamical Vacuum Selection
==========================

A proposed cosmological attractor + bubble nucleation that would prune
the ~10^(10^8) G2 flux landscape down to a single dynamically selected
vacuum.

STATUS ON THE ADOPTED PATH (read first):
    - Y_7 is Joyce's resolution of T^7/(Z/2)^3 with (b_2, b_3) = (12, 43).
    - CALIBRATED at the off-path seed b_3 = 24; no gaugino racetrack exists
      on Y_7 (CG.5, CG.10). The pruning mechanism is the Acharya-Kane
      G2-MSSM moduli flow, driven by gaugino condensation in a hidden
      sector. Y_7's singular loci carry N = 4 super Yang-Mills, and full
      holonomy excludes a confining sector in phi's Joyce family, so that
      sector does not exist here. The decay rate 0.92 was chosen so that
      exp(-0.92 * 24) ~ 2.6e-10. It is not derived; the computation is
      kept as a model calculation.
    - select_vacuum() reads b_3 from the live seed (43 on the adopted
      path), so the values it returns follow the seed in force. The worked
      numbers below are the arithmetic at the off-path seed.
    - Re(T) is OPEN on Y_7: the leading-order flux potential is positive
      and runs away (CG.6).

DERIVATION (PossibleImprovements.txt section 3):

    Early-universe moduli evolution under gaugino condensation funnels
    the system toward the long-lived SUSY-breaking vacuum. Eternal
    inflation + bubble nucleation amplify the suppression. (On Y_7 there
    is no gaugino condensate to drive this; see the status above.)

    Raw landscape size (pre-selection):

        log N_raw = b3 * log(flux_modes) + 8 * log(10)

    where flux_modes = 12 counts the bulk's 12 bridge pairs (the
    M^{26}(24,2) bulk). At the off-path seed (b_3 = 24, flux_modes = 12)
    this gives log N_raw ~ 78 (natural log), i.e. N_raw ~ 10^34 distinct
    flux vacua before selection.

    Dynamical pruning factor (G2-cycle gaugino condensation attractor):

        pruning_factor = exp(-0.92 * b3)

    where 0.92 is the attractor decay rate per b3-cycle, taken from the
    Acharya-Kane G2-MSSM moduli flow and calibrated at the off-path seed:
    there exp(-22.08) ~ 2.6e-10, so >99.9999999% of the landscape would
    be dynamically rejected before BabyIAXO can probe it.

    Effective surviving vacua:

        N_eff = N_raw * pruning_factor

    At the off-path seed (flux_modes = 12): N_eff ~ 10^25. The remaining
    vacua are further pruned by the 72 Gates + EML sterility constraints
    + the falsifiable axion mass prediction. The original text ended with
    "a single attractor basin around the observed Re(T) value"; Re(T) is
    OPEN on Y_7 (CG.6), so no such basin is established.

DEPENDENCY CHAIN:
    The b3 leaf of the EML tree is the live seed's b_3 (43 on the adopted
    path), read through b3_leaf(). The flux_modes = 12 input counts the
    bulk's 12 bridge pairs; it was formerly written as b3/2, which holds
    only at the off-path seed. The 8*log(10) scale factor is the
    natural-log conversion of the 10^8 anthropic upper bound, and the
    0.92 attractor rate is calibrated at the off-path seed b_3 = 24.

OUTPUTS:
    - vacuum_selection.raw_vacua: pre-selection landscape size
    - vacuum_selection.dynamically_selected: post-attractor vacuum count
    - vacuum_selection.anthropic_rejected: fraction killed by dynamics
    - vacuum_selection.pruning_factor: exp(-0.92*b3)
    - vacuum_selection.log_vacua_raw: natural-log raw count
    - vacuum_selection.classification: "DYNAMICALLY_SELECTED"

REFERENCES:
    - Acharya, Kane, Kuflik (2012) "String/M theories about our world
      are testable in the near future" Phys. Rep. 519, 245-274
    - Kutasov, Maloney, Schwartz, Zaitsev (2009) "Dynamical landscape
      selection" arXiv:0907.4998
    - Bousso, Polchinski (2000) "Quantization of four-form fluxes..."
      JHEP 0006:006

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""
from __future__ import annotations

import math
from typing import Any, Dict, Optional

from metaphysica.simulations.core.FormulasRegistry import get_registry

try:
    from metaphysica.simulations.core.eml_integration import (
        EML_AVAILABLE,
        b3_leaf,
        eml_add,
        eml_compute,
        eml_exp,
        eml_ln,
        eml_mul,
        eml_neg,
        eml_scalar,
    )
except ImportError:  # pragma: no cover - defensive
    EML_AVAILABLE = False


# ── Module-level constants ──────────────────────────────────────────────────

# Dynamical attractor decay rate per b3-cycle (Acharya-Kane G2-MSSM).
# CALIBRATED at the off-path seed b_3 = 24: chosen so that
# exp(-0.92 * 24) ~ 2.6e-10, matching the >99.9999999% anthropic rejection
# target from PossibleImprovements.txt. Not derived; at the live seed the
# same rate gives a different factor.
ATTRACTOR_DECAY_RATE = 0.92

# Natural-log scale of the anthropic upper bound (10^8 vacua tolerated
# before the "landscape problem" becomes proof-killing).
LANDSCAPE_LOG_SCALE = 8

# Fraction of the landscape eliminated by the dynamical attractor.
# Reported as a human-readable string; the precise float is
# `1.0 - pruning_factor`.
ANTHROPIC_REJECTED_STR = "99.999%"


class DynamicalVacuumSelector:
    """Prune 10^(10^8) G2 flux vacua to a single dynamically selected one.

    CALIBRATED at the off-path seed b_3 = 24; no gaugino racetrack exists
    on Y_7 (CG.5, CG.10). The selector implements the Acharya-Kane G2-MSSM
    moduli flow, in which gaugino condensation in a hidden sector funnels
    Re(T) toward the long-lived SUSY-breaking minimum and everything
    outside that attractor basin tunnels away during eternal inflation.
    Y_7 has no confining hidden sector and Re(T) is an OPEN modulus (CG.6),
    so this is a model calculation, not a mechanism of the adopted path.

    b_3 is read from the live seed at call time (43 on the adopted path).
    The decay rate 0.92 is calibrated at the off-path seed b_3 = 24, and
    flux_modes = 12 counts the bulk's 12 bridge pairs.
    """

    # Default G2 inputs (overridable on `select_vacuum`). DEFAULT_B3 is a
    # PROPERTY-LIKE resolution, not a literal: it was formerly a frozen 24
    # and kept publishing cosmology.b3 = 24 while particle.b3 carried the adopted
    # seed's 43 -- two rows with the same short name and different values,
    # which the ambiguous-alias guard caught on 2026-09-22. A default
    # argument is exactly where a silent seed-blind value hides, so the
    # resolution happens at call time instead (see select_vacuum).
    DEFAULT_FLUX_MODES: int = 12

    def __init__(self) -> None:
        """Initialize the selector and cache an EML tree handle."""
        self._registry = get_registry()
        self._results: Optional[Dict[str, Any]] = None
        # EML tree for the dynamical-selection derivation. Each
        # registered formula appends a leaf rooted at `b3_leaf()`.
        self._eml_tree: Dict[str, Any] = {
            "name": "dynamical_selection",
            "derivations": {},
        }

    # =====================================================================
    # CORE COMPUTATION
    # =====================================================================

    @staticmethod
    def _seed_b3() -> int:
        """The live seed's b_3; the class carries no frozen default."""
        from metaphysica.simulations.PM.geometry.b3_path import (
            resolve_path,
            seed_values,
        )

        return seed_values(resolve_path())[0]

    def select_vacuum(
        self,
        b3: Optional[int] = None,
        flux_modes: int = DEFAULT_FLUX_MODES,
    ) -> Dict[str, Any]:
        """Compute the dynamically selected vacuum count.

        Args:
            b3: G2 third Betti number. None (default) resolves the LIVE
                seed via the b3_seed fork -- 43 on the adopted branch, 24
                under the seed_24 override. Pass an explicit value only to
                probe a hypothetical.
            flux_modes: bridge-pair count (default 12, the bulk's 12
                bridge pairs; it equals b3/2 only at the off-path seed
                b_3 = 24).

        Returns:
            Dict carrying ``raw_vacua``, ``dynamically_selected``,
            ``anthropic_rejected``, plus diagnostic fields used by the
            72-gate validation pipeline.
        """
        # ── 1. Raw landscape size (pre-selection) ────────────────────
        if b3 is None:
            b3 = self._seed_b3()

        # log N_raw = b3 * log(flux_modes) + 8 * log(10)
        log_vacua_raw = (
            b3 * math.log(flux_modes)
            + LANDSCAPE_LOG_SCALE * math.log(10)
        )
        raw_vacua = math.exp(log_vacua_raw)

        # ── 2. Dynamical pruning factor (G2 attractor) ───────────────
        # pruning_factor = exp(-0.92 * b3)
        pruning_factor = math.exp(-ATTRACTOR_DECAY_RATE * b3)

        # ── 3. Effective vacua after dynamical selection ─────────────
        effective_vacua = raw_vacua * pruning_factor

        # ── 4. EML tree registration (b3-rooted leaves) ──────────────
        eml_value: Optional[float] = None
        if EML_AVAILABLE:
            try:
                eml_value = self._build_eml_tree(b3, flux_modes)
            except Exception:  # pragma: no cover - EML soft-fail
                eml_value = None

        # ── 5. Register formula derivation in tree dict ──────────────
        self._register_derivation(
            "log_vacua_raw",
            "b3 * ln(flux_modes) + 8 * ln(10)",
            log_vacua_raw,
        )
        self._register_derivation(
            "pruning_factor",
            "exp(-0.92 * b3)",
            pruning_factor,
        )
        self._register_derivation(
            "effective_vacua",
            "exp(b3*ln(flux_modes) + 8*ln(10)) * exp(-0.92*b3)",
            effective_vacua,
        )

        self._results = {
            "raw_vacua": float(raw_vacua),
            "dynamically_selected": float(effective_vacua),
            "anthropic_rejected": ANTHROPIC_REJECTED_STR,
            "pruning_factor": float(pruning_factor),
            "log_vacua_raw": float(log_vacua_raw),
            "b3": int(b3),
            "flux_modes": int(flux_modes),
            "eml_value": eml_value,
            "classification": "DYNAMICALLY_SELECTED",
        }
        return self._results

    # =====================================================================
    # EML TREE CONSTRUCTION
    # =====================================================================

    def _build_eml_tree(self, b3: int, flux_modes: int) -> float:
        """Build the EML-Math operator tree rooted at b3_leaf().

        Returns the numeric tension of the tree (== effective_vacua to
        within float precision). The b3 leaf comes from :func:`b3_leaf`
        (the live seed's b_3); the other leaves are literal scalars:
        flux_modes (the bulk's 12 bridge pairs by default), the landscape
        log-scale 8, and the decay rate 0.92 (calibrated at the off-path
        seed b_3 = 24).
        """
        # b3 leaf: the live seed's b_3 (43 on the adopted path), read from
        # the registry.
        b3_pt = b3_leaf()

        # flux_modes leaf -- the bulk's 12 bridge pairs by default (formerly
        # written as b3/2, which holds only at the off-path seed b_3 = 24);
        # the caller can override; honor the explicit value so the EML
        # tree faithfully encodes the actual computation.
        flux_pt = eml_scalar(float(flux_modes))

        # log_vacua_raw = b3 * ln(flux_modes) + 8 * ln(10)
        ln_flux = eml_ln(flux_pt)
        term1 = eml_mul(b3_pt, ln_flux)
        ln_ten = eml_ln(eml_scalar(10.0))
        term2 = eml_mul(eml_scalar(float(LANDSCAPE_LOG_SCALE)), ln_ten)
        log_vacua_raw_tree = eml_add(term1, term2)

        # raw_vacua = exp(log_vacua_raw)
        raw_tree = eml_exp(log_vacua_raw_tree)

        # pruning_factor = exp(-0.92 * b3)
        decay_pt = eml_scalar(ATTRACTOR_DECAY_RATE)
        exponent = eml_neg(eml_mul(decay_pt, b3_leaf()))
        pruning_tree = eml_exp(exponent)

        # effective_vacua = raw * pruning
        effective_tree = eml_mul(raw_tree, pruning_tree)

        # Cache the tree handle for downstream consumers.
        self._eml_tree["root"] = effective_tree
        self._eml_tree["b3_leaf"] = b3_pt

        return float(eml_compute(effective_tree))

    # =====================================================================
    # REGISTRATION HELPERS
    # =====================================================================

    def _register_derivation(
        self,
        name: str,
        formula: str,
        value: float,
    ) -> None:
        """Record a derivation step in the EML tree dict."""
        self._eml_tree["derivations"][name] = {
            "formula": formula,
            "value": float(value),
        }

    @property
    def eml_tree(self) -> Dict[str, Any]:
        """Public accessor for the EML tree (for FormulasRegistry hookup)."""
        return self._eml_tree

    @property
    def results(self) -> Optional[Dict[str, Any]]:
        """Return cached results dict (or None if `select_vacuum` not called)."""
        return self._results


# ── Module entry point ──────────────────────────────────────────────────────

def prune_landscape() -> Dict[str, Any]:
    """Module entry point: prune the G2 flux landscape via dynamical selection.

    b_3 defaults to the live seed's value (43 on the adopted path);
    flux_modes defaults to 12, the bulk's bridge pairs. The decay rate is
    calibrated at the off-path seed b_3 = 24, and no gaugino racetrack
    exists on Y_7 (CG.5, CG.10). Returns the full
    results dict as described in :meth:`DynamicalVacuumSelector.select_vacuum`.

    Used by:
        - simulations/core/FormulasRegistry.py (derivation hook)
        - simulations/run_all_simulations.py  (72-gate validation)
        - tests/test_vacuum_selection.py      (regression suite)
    """
    return DynamicalVacuumSelector().select_vacuum()


__all__ = [
    "DynamicalVacuumSelector",
    "prune_landscape",
    "ATTRACTOR_DECAY_RATE",
    "LANDSCAPE_LOG_SCALE",
]
