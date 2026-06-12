#!/usr/bin/env python3
"""
LHC / HL-LHC SUSY Spectrum Predictions (Sprint T6 #4, T3.7)
============================================================

Takes the soft SUSY-breaking spectrum scale set by the gravitino mass
``m_{3/2}`` (Sprint T6 #1 / T3.1, the Kahler-lifted ``e^{K/2}|W|``
gravitino landing at the TeV scale after the v27.0 K(T) refinement) and
propagates it to the **direct-search observables** at the LHC:

* gluino mass ``m_{g~}``,
* universal stop / squark mass ``m_{t~}``,
* lightest neutralino (bino-like) mass ``m_{chi0}``,
* Higgsino mass ``m_{H~}``.

Mass relations
--------------
We assume the standard gravity-mediated, anomaly-free relation
``m_{1/2} = (1/2) m_{3/2}`` for the universal gaugino mass at the GUT
scale (mirror of the moduli-mediation result in
``simulations/PM/susy/soft_susy_breaking.py``, here recast for the
TeV-lifted Kahler-corrected gravitino).

Running the gaugino masses from the GUT scale to the SUSY (TeV) scale
amplifies the gluino mass by the well-known one-loop QCD factor
``g_3^2(M_S) / g_3^2(M_GUT) ~ 6.5`` (see e.g. Martin's SUSY primer,
arXiv:hep-ph/9709356, eq. 6.5.5).  Thus

    m_{g~}(M_S)  ~  6.5 * m_{1/2}.

For the lightest stop / first-generation squarks the running Higgs and
QCD contributions give the standard

    m_{q~}^2(M_S)  ~  m_0^2 + 5.5 * m_{1/2}^2

with ``m_0 = m_{3/2}`` from universal gravity mediation.

The lightest neutralino is bino-like with ``M_1 ~ m_{1/2}`` (after
running) and the lightest neutralino mass is

    m_{chi0}  ~  0.5 * m_{1/2}  =  0.25 * m_{3/2}.

The Higgsino mass is set by the mu-parameter from the
soft_susy_breaking pipeline, ``mu = 0.8 * m_{3/2}``, so

    m_{H~}  ~  0.8 * m_{3/2}.

LHC search reach (PDG 2024 + ATLAS/CMS Run 3 projections)
---------------------------------------------------------
* LHC Run 3 (~300 fb^-1 by 2026):    m_{g~} > ~2.2 TeV exclusion
* HL-LHC (3 ab^-1 by ~2040):         m_{g~} > ~3.0 TeV reach
* Beyond -- FCC-hh (100 TeV):        m_{g~} > ~10 TeV reach

Verdict
-------
The module returns a single string verdict for the predicted gluino mass:

* ``"EXCLUDED_BY_RUN3"``  if  m_{g~} <= LHC Run 3 reach
* ``"PROBE_AT_HL_LHC"``   if  LHC Run 3 reach < m_{g~} <= HL-LHC reach
* ``"WAITS_FOR_FCC"``     if  m_{g~} > HL-LHC reach

At the Sprint T6 default ``m_{3/2} = 1 TeV``, ``m_{1/2} = 500 GeV``,
``m_{g~} ~ 3.25 TeV`` -- just beyond the HL-LHC reach, sitting in the
``"WAITS_FOR_FCC"`` regime (a clean falsifiability statement against
imminent FCC-hh constraints).  Lifting ``m_{3/2}`` to ~0.9 TeV drops
``m_{g~}`` to ~2.93 TeV, putting it back inside the ``"PROBE_AT_HL_LHC"``
window -- so the module's verdict cleanly tracks the upstream gravitino
mass.

EML tree
--------
Every derived parameter is registered with an EML operator tree named
``"lhc_predictions"`` so the Sprint 3 ``arithma_dependency_walker`` and
the Sprint 4 dependency resolver can pick the derivation up and confirm
back-propagation to the ``m_{3/2}`` seed (which itself traces back to
the G_2 third Betti number seed ``b_3 = 24`` via
``soft_susy_breaking.py``).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""

from __future__ import annotations

from typing import Any, Dict

from metaphysica.simulations.core.eml_tree_adapter import eml_operator_tree


# Default inputs match the Sprint T6 #1 Kahler-lifted gravitino target
# (m_{3/2} ~ 1 TeV) and the canonical GUT scale used everywhere in PM.
DEFAULT_M_3_2_TEV = 1.0
DEFAULT_M_GUT_GEV = 2.1e16

# Gluino RGE running factor g_3^2(M_S) / g_3^2(M_GUT) ~ 6.5 (Martin
# SUSY primer, eq. 6.5.5).  Universal squark scalar coefficient 5.5
# from the leading one-loop RGE running of the soft scalar masses
# (Martin eq. 6.5.7).  Bino fraction 0.5 from M_1 ~ 0.5 * m_{1/2} after
# anomaly + modulus running.  Mu-coefficient 0.8 from
# soft_susy_breaking.compute_mu_term.
_GLUINO_RUN_FACTOR = 6.5
_SQUARK_M12_COEFF = 5.5
_BINO_FRACTION = 0.5
_MU_COEFF = 0.8
_GAUGINO_FRACTION = 0.5  # m_{1/2} = (1/2) * m_{3/2} (gravity-mediated, anomaly-free)

# LHC search reach numbers (ATLAS/CMS Run 3 + HL-LHC projections,
# CERN-LPCC-2024-01).  Kept as named module-level constants so the
# audit can trace the experimental inputs.
_LHC_RUN3_REACH_GLUINO_GEV = 2.2e3
_HL_LHC_REACH_GLUINO_GEV = 3.0e3


class LHCPredictions:
    """Direct-search SUSY spectrum at the LHC, derived from m_{3/2}.

    Parameters
    ----------
    m_3_2_TeV:
        Gravitino mass in TeV (default ``1.0``).  Matches the Sprint T6 #1
        Kahler-lifted ``e^{K/2}|W|`` target.
    M_GUT:
        GUT scale in GeV (default ``2.1e16``).  Carried through so the
        EML tree records the running scales but does not enter the
        leading-order mass formulae below (the RGE factors are
        pre-evaluated and absorbed into the module-level coefficients).

    Notes
    -----
    Calling :meth:`predictions` runs the full pipeline and registers
    every parameter under the ``"lhc_predictions"`` EML operator tree.
    """

    def __init__(
        self,
        m_3_2_TeV: float = DEFAULT_M_3_2_TEV,
        M_GUT: float = DEFAULT_M_GUT_GEV,
    ) -> None:
        # Convert TeV to GeV up-front so every downstream computation
        # works in GeV (matching the rest of the framework).
        self.m_3_2 = float(m_3_2_TeV) * 1.0e3  # GeV
        self.M_GUT = float(M_GUT)
        self.lhc_tree = eml_operator_tree("lhc_predictions")

    # ------------------------------------------------------------------
    # Individual mass derivations
    # ------------------------------------------------------------------

    def gluino_mass(self) -> float:
        """``m_{g~} ~ 6.5 * m_{1/2}`` at the SUSY scale.

        Gravity-mediated anomaly-free ``m_{1/2} = (1/2) m_{3/2}`` at the
        GUT scale; one-loop QCD running amplifies to the TeV scale by
        ``g_3^2(M_S) / g_3^2(M_GUT) ~ 6.5``.
        """
        m_1_2 = _GAUGINO_FRACTION * self.m_3_2
        m_gluino = _GLUINO_RUN_FACTOR * m_1_2
        self.lhc_tree.register_derivation(
            "m_gluino_GeV",
            (
                "6.5 * m_1_2 with m_1_2 = 0.5 * m_3_2 "
                "(one-loop QCD running from m_3_2; m_3_2 from soft_susy_breaking, "
                "ultimately b3-seeded via Re(T) stabilization)"
            ),
            float(m_gluino),
        )
        return float(m_gluino)

    def stop_mass(self) -> float:
        """``m_{t~}^2 ~ m_0^2 + 5.5 * m_{1/2}^2`` (one-loop RGE).

        With ``m_0 = m_{3/2}`` from universal gravity mediation.
        """
        m_0 = self.m_3_2
        m_1_2 = _GAUGINO_FRACTION * self.m_3_2
        m_stop_sq = m_0 ** 2 + _SQUARK_M12_COEFF * m_1_2 ** 2
        m_stop = m_stop_sq ** 0.5
        self.lhc_tree.register_derivation(
            "m_stop_GeV",
            (
                "sqrt(m_0^2 + 5.5 * m_1_2^2) with m_0 = m_3_2, m_1_2 = 0.5 m_3_2 "
                "(one-loop scalar RGE; b3-seeded via m_3_2)"
            ),
            float(m_stop),
        )
        return float(m_stop)

    def neutralino_mass(self) -> float:
        """Lightest bino-like neutralino: ``m_{chi0} ~ 0.5 * m_{1/2}``.

        With ``m_{1/2} = 0.5 * m_{3/2}``, ``m_{chi0} = 0.25 * m_{3/2}``.
        """
        m_1_2 = _GAUGINO_FRACTION * self.m_3_2
        m_chi0 = _BINO_FRACTION * m_1_2
        self.lhc_tree.register_derivation(
            "m_neutralino_GeV",
            (
                "0.5 * m_1_2 with m_1_2 = 0.5 m_3_2 (bino-like; b3-seeded "
                "via m_3_2)"
            ),
            float(m_chi0),
        )
        return float(m_chi0)

    def higgsino_mass(self) -> float:
        """``m_{H~} = mu = 0.8 * m_{3/2}`` (mu-term from soft_susy_breaking)."""
        m_higgsino = _MU_COEFF * self.m_3_2
        self.lhc_tree.register_derivation(
            "m_higgsino_GeV",
            (
                "0.8 * m_3_2 (mu-term from Giudice-Masiero / instanton; "
                "b3-seeded via m_3_2)"
            ),
            float(m_higgsino),
        )
        return float(m_higgsino)

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def predictions(self) -> Dict[str, Any]:
        """Run the full derivation pipeline and produce the LHC verdict.

        Returns
        -------
        dict
            Mapping of LHC observables to GeV-scale numbers plus
            qualitative reach metadata:

            * ``m_gluino_GeV``       -- gluino mass at SUSY scale.
            * ``m_stop_GeV``         -- universal stop / squark mass.
            * ``m_neutralino_GeV``   -- lightest bino neutralino mass.
            * ``m_higgsino_GeV``     -- Higgsino mass (mu-term).
            * ``lhc_run3_reach_gluino``  -- Run 3 exclusion reach (GeV).
            * ``hl_lhc_reach_gluino``    -- HL-LHC discovery reach (GeV).
            * ``verdict``  -- ``EXCLUDED_BY_RUN3`` / ``PROBE_AT_HL_LHC``
                              / ``WAITS_FOR_FCC``.
        """
        m_gluino = self.gluino_mass()
        m_stop = self.stop_mass()
        m_neutralino = self.neutralino_mass()
        m_higgsino = self.higgsino_mass()

        if m_gluino <= _LHC_RUN3_REACH_GLUINO_GEV:
            verdict = "EXCLUDED_BY_RUN3"
        elif m_gluino <= _HL_LHC_REACH_GLUINO_GEV:
            verdict = "PROBE_AT_HL_LHC"
        else:
            verdict = "WAITS_FOR_FCC"

        results: Dict[str, Any] = {
            "m_gluino_GeV": m_gluino,
            "m_stop_GeV": m_stop,
            "m_neutralino_GeV": m_neutralino,
            "m_higgsino_GeV": m_higgsino,
            "lhc_run3_reach_gluino": _LHC_RUN3_REACH_GLUINO_GEV,
            "hl_lhc_reach_gluino": _HL_LHC_REACH_GLUINO_GEV,
            "verdict": verdict,
        }

        self.lhc_tree.register_derivation(
            "full_lhc_spectrum",
            (
                "complete LHC SUSY spectrum (gluino, stop, neutralino, "
                "higgsino) with Run 3 / HL-LHC reach verdict; b3-seeded "
                "via m_3_2"
            ),
            {k: v for k, v in results.items() if isinstance(v, (int, float))},
        )
        self.lhc_tree.register_derivation(
            "verdict",
            "Run 3 / HL-LHC / FCC verdict from gluino mass vs experimental reach",
            verdict,
        )
        return results


# ----------------------------------------------------------------------
# Module entry point
# ----------------------------------------------------------------------


def get_lhc_predictions() -> Dict[str, Any]:
    """Entry point used by ``run_all_simulations`` and the registry.

    Constructs an :class:`LHCPredictions` with the Sprint T6 #4 defaults
    (``m_{3/2} = 1 TeV``, ``M_GUT = 2.1e16 GeV``) and returns the
    LHC observables and verdict.
    """
    return LHCPredictions().predictions()


__all__ = [
    "LHCPredictions",
    "get_lhc_predictions",
    "DEFAULT_M_3_2_TEV",
    "DEFAULT_M_GUT_GEV",
]
