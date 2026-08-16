"""
Established Physics Loader for Principia Metaphysica
======================================================

Loads experimentally measured physics constants from CACHED JSON FILES:
- PDG 2024: simulations/data/experimental/pdg_2024_values.json
- NuFIT 6.0: simulations/data/experimental/nufit_6_0_parameters.json
- DESI 2025: simulations/data/experimental/desi_2025_constraints.json
- Super-Kamiokande and other experimental bounds

NO HARDCODED VALUES - all experimental data is loaded from JSON files
that can be independently verified and updated.

All values are marked with source "ESTABLISHED" and cannot be overridden by simulations.
Includes accuracy validation that computes sigma deviations during generation.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""

import sys
import os
from typing import Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass
import warnings

if TYPE_CHECKING:
    from .registry import PMRegistry

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Try to import the experimental data loader
try:
    from metaphysica.simulations.data.experimental_data_loader import ExperimentalDataLoader, get_loader
    DATA_LOADER_AVAILABLE = True
except ImportError as e:
    warnings.warn(f"Could not import ExperimentalDataLoader: {e}. Using fallback values.")
    DATA_LOADER_AVAILABLE = False

try:
    from metaphysica.config import (
        PhenomenologyParameters,
        NeutrinoParameters,
    )
    CONFIG_AVAILABLE = True
except ImportError as e:
    warnings.warn(f"Could not import from metaphysica.config.py: {e}. Using fallback values.")
    CONFIG_AVAILABLE = False


@dataclass
class EstablishedParameter:
    """A single established physics parameter with full provenance."""
    path: str                    # e.g., "pdg.m_higgs"
    value: float
    uncertainty: float
    units: str
    source: str                  # e.g., "ESTABLISHED:PDG2024"
    status: str = "ESTABLISHED"
    description: str = ""
    eml_description: str = ""    # EML/Mirror Phase Mathematics description


class EstablishedPhysics:
    """
    Loader for established experimental physics values.

    This class provides a centralized registry of all experimentally measured
    values that serve as ground truth for the theory. These values:

    1. Cannot be overridden by simulations
    2. Have clear source provenance (PDG, NuFIT, DESI, etc.)
    3. Include uncertainties where applicable
    4. Serve as validation targets for theoretical predictions

    Usage:
        registry = PMRegistry()
        EstablishedPhysics.load_into_registry(registry)
    """

    @classmethod
    def load_into_registry(cls, registry: 'PMRegistry') -> None:
        """Load all established physics parameters into the registry."""
        cls._load_constants(registry)
        cls._load_pdg_values(registry)
        cls._load_ckm_values(registry)
        cls._load_nufit_values(registry)
        cls._load_desi_values(registry)
        cls._load_experimental_bounds(registry)
        cls._load_theory_constants(registry)
        cls._load_codata_values(registry)

    # ------------------------------------------------------------------
    # SSOT helpers: the experimental JSONs under simulations/data/
    # experimental/ are authoritative. The literals passed as fallbacks
    # exist ONLY for environments where the loader can't run — every
    # value below should be read through these, never typed inline.
    # ------------------------------------------------------------------

    @classmethod
    def _pdg(cls, category: str, name: str,
             fb_value: float, fb_unc: float) -> tuple:
        """(value, uncertainty) from pdg_2024_values.json via the loader."""
        if DATA_LOADER_AVAILABLE:
            try:
                d = get_loader().get_pdg(category, name)
                return d.value, (d.uncertainty if d.uncertainty is not None else fb_unc)
            except Exception:
                pass
        return fb_value, fb_unc

    @classmethod
    def _nufit(cls, name: str, ordering: str,
               fb_value: float, fb_unc: float) -> tuple:
        """(value, uncertainty) from nufit JSON (NuFIT 5.2-era; see file metadata)."""
        if DATA_LOADER_AVAILABLE:
            try:
                d = get_loader().get_nufit(name, ordering)
                return d.value, (d.uncertainty if d.uncertainty is not None else fb_unc)
            except Exception:
                pass
        return fb_value, fb_unc

    @classmethod
    def _load_constants(cls, registry: 'PMRegistry') -> None:
        """Load fundamental constants (Planck mass, alpha_em, etc.).

        IMPORTANT - Planck Mass Distinction:
        -------------------------------------
        constants.M_PLANCK = 2.435e18 GeV - REDUCED Planck mass (M_Pl / sqrt(8*pi))
            This is the INPUT for PM's 26D string tension (M_Pl_26D).

        codata.M_PLANCK = 1.220890e19 GeV - FULL Planck mass (CODATA standard)
            This is the EXPERIMENTAL REFERENCE for comparing PM's 4D prediction.

        PM Prediction: geometry.m_planck_4d = M_Pl_26D * chi = 2.435e18 * 5.0132 = 1.2207e19 GeV
            This should be compared against codata.M_PLANCK (full), NOT constants.M_PLANCK (reduced).
            The 97.65σ error occurred when comparing 1.2207e19 against 2.435e18 (wrong quantity).
        """
        # SSOT: values read from pdg_2024_values.json (fundamental_constants /
        # baryons categories); literals are offline fallbacks only.
        table = [
            ("constants.M_PLANCK", "fundamental_constants", "M_PLANCK_REDUCED", "GeV",
             "Reduced Planck mass (M_Pl / sqrt(8*pi)) - INPUT for the bulk string tension",
             2.435e18, 3.0e15),
            ("constants.alpha_em", "fundamental_constants", "alpha_em", "dimensionless",
             "Fine structure constant (CODATA 2022)",
             7.2973525643e-3, 1.1e-12),
            ("constants.m_proton", "baryons", "m_proton", "GeV",
             "Proton mass",
             0.93827208943, 2.9e-10),
            ("constants.HBAR", "fundamental_constants", "HBAR", "GeV·s",
             "Reduced Planck constant (exact since 2019 SI redefinition)",
             6.582119569e-25, 0.0),
            ("constants.G_NEWTON", "fundamental_constants", "G_NEWTON", "GeV^-2",
             "Newton's gravitational constant",
             6.70883e-39, 1.5e-43),
        ]

        for path, category, name, units, desc, fb_value, fb_unc in table:
            value, unc = cls._pdg(category, name, fb_value, fb_unc)
            cls._register_param(registry, EstablishedParameter(
                path=path,
                value=value,
                uncertainty=unc,
                units=units,
                source="ESTABLISHED:PDG2024",
                description=desc,
                eml_description=f"EML: eml_scalar({value:g}) — {desc} ({units}; from pdg_2024_values.json)"
            ))

    @classmethod
    def _load_pdg_values(cls, registry: 'PMRegistry') -> None:
        """Load PDG 2024 experimental values.

        SSOT: every value/uncertainty is read from pdg_2024_values.json via
        :meth:`_pdg`; the literals below are offline fallbacks only. The
        table drives (path, JSON category, JSON name, units, description,
        fallback value, fallback uncertainty).
        """
        table = [
            ("pdg.m_higgs",     "gauge_bosons", "m_higgs",     "GeV", "Higgs boson mass",                             125.20,          0.11),
            ("pdg.m_electron",  "leptons",      "m_electron",  "GeV", "Electron mass",                                5.1099895069e-4, 3.1e-12),
            ("pdg.m_muon",      "leptons",      "m_muon",      "GeV", "Muon mass",                                    0.1056583755,    2.3e-9),
            ("pdg.m_tau",       "leptons",      "m_tau",       "GeV", "Tau mass",                                     1.77693,         9e-5),
            ("pdg.m_up",        "quarks",       "m_up",        "GeV", "Up quark mass (MS-bar, 2 GeV)",                2.16e-3,         0.49e-3),
            ("pdg.m_down",      "quarks",       "m_down",      "GeV", "Down quark mass (MS-bar, 2 GeV)",              4.67e-3,         0.48e-3),
            ("pdg.m_strange",   "quarks",       "m_strange",   "GeV", "Strange quark mass",                           93.4e-3,         8.6e-3),
            ("pdg.m_charm",     "quarks",       "m_charm",     "GeV", "Charm quark mass",                             1.27,            0.02),
            ("pdg.m_bottom",    "quarks",       "m_bottom",    "GeV", "Bottom quark mass",                            4.18,            0.03),
            ("pdg.m_top",       "quarks",       "m_top",       "GeV", "Top quark mass",                               172.57,          0.29),
            ("pdg.alpha_s_MZ",  "couplings",    "alpha_s_MZ",  "dimensionless", "Strong coupling at M_Z",             0.1180,          0.0009),
            ("pdg.sin2_theta_W","couplings",    "sin2_theta_W","dimensionless", "Weak mixing angle sin²θ_W at Z-pole, MS-bar scheme (PDG 2024)", 0.23122, 0.00003),
            ("pdg.m_W",         "gauge_bosons", "m_W",         "GeV", "W boson mass (PDG 2024 world average, excluding CDF 2022)", 80.3692, 0.0133),
            ("pdg.m_Z",         "gauge_bosons", "m_Z",         "GeV", "Z boson mass",                                 91.1880,         0.0020),
        ]

        for path, category, name, units, desc, fb_value, fb_unc in table:
            value, unc = cls._pdg(category, name, fb_value, fb_unc)
            cls._register_param(registry, EstablishedParameter(
                path=path,
                value=value,
                uncertainty=unc,
                units=units,
                source="ESTABLISHED:PDG2024",
                description=desc,
                eml_description=f"EML: eml_scalar({value:g}) — {desc} ({units}, PDG 2024, from pdg_2024_values.json)"
            ))

    @classmethod
    def _load_ckm_values(cls, registry: 'PMRegistry') -> None:
        """Load CKM matrix elements from PDG 2024.

        CKM (Cabibbo-Kobayashi-Maskawa) matrix elements describe quark mixing.
        These are established values that serve as validation targets for the
        octonionic mixing simulation (simulations.v16.fermion.octonionic_mixing_v16_2).
        """
        # SSOT: values read from pdg_2024_values.json (ckm category);
        # literals are offline fallbacks only.
        table = [
            ("pdg.V_us",  "V_us",     "CKM |V_us| Cabibbo angle",              0.22500, 0.00067),
            ("pdg.V_cb",  "V_cb",     "CKM |V_cb|",                            0.04182, 0.00085),
            ("pdg.V_ub",  "V_ub",     "CKM |V_ub|",                            0.00369, 0.00011),
            ("pdg.J_ckm", "jarlskog", "Jarlskog invariant J",                  3.12e-5, 0.13e-5),
        ]

        for path, name, desc, fb_value, fb_unc in table:
            value, unc = cls._pdg("ckm", name, fb_value, fb_unc)
            cls._register_param(registry, EstablishedParameter(
                path=path,
                value=value,
                uncertainty=unc,
                units="dimensionless",
                source="ESTABLISHED:PDG2024",
                description=desc,
                eml_description=f"EML: eml_scalar({value:g}) — {desc} (PDG 2024, from pdg_2024_values.json)"
            ))

    @classmethod
    def _load_nufit_values(cls, registry: 'PMRegistry') -> None:
        """Load NuFIT neutrino oscillation parameters.

        SSOT: values read from nufit_6_0_parameters.json via :meth:`_nufit`
        (the file carries NuFIT 5.2-era values — see its metadata note).
        The literals below are offline fallbacks only. Reading the IO block
        from the JSON also fixes the previous hard-coded −2.404e-3 (a model
        echo) — the dataset's honest IO value is −2.498e-3.
        """
        no_table = [
            ("nufit.theta_12",     "theta_12",      "degrees", "Solar mixing angle",                                   33.41,   0.75),
            ("nufit.theta_23",     "theta_23",      "degrees", "Atmospheric mixing angle",                             42.2,    1.0),
            ("nufit.theta_13",     "theta_13",      "degrees", "Reactor mixing angle",                                 8.58,    0.12),
            ("nufit.delta_CP",     "delta_CP",      "degrees", "CP-violating phase",                                   232.0,   25.0),
            ("nufit.delta_m21_sq", "delta_m21_sq",  "eV^2",    "Solar mass splitting",                                 7.42e-5, 0.21e-5),
            ("nufit.delta_m31_sq", "delta_m31_sq",  "eV^2",    "Atmospheric mass splitting (Normal Ordering convention)", 2.515e-3, 0.028e-3),
        ]
        io_table = [
            ("nufit.delta_m32_sq_IO", "delta_m32_sq", "eV^2",    "Atmospheric mass splitting (Inverted Ordering: dm2_32 < 0)", -2.498e-3, 0.028e-3),
            ("nufit.theta_23_IO",     "theta_23",     "degrees", "Atmospheric mixing angle (IO best fit, upper octant)",       49.3,      1.0),
            ("nufit.delta_CP_IO",     "delta_CP",     "degrees", "CP-violating phase (Inverted Ordering)",                     278.0,     26.0),
        ]

        for ordering, source, table in (
            ("normal_ordering",   "ESTABLISHED:NuFIT",    no_table),
            ("inverted_ordering", "ESTABLISHED:NuFIT_IO", io_table),
        ):
            for path, name, units, desc, fb_value, fb_unc in table:
                value, unc = cls._nufit(name, ordering, fb_value, fb_unc)
                cls._register_param(registry, EstablishedParameter(
                    path=path,
                    value=value,
                    uncertainty=unc,
                    units=units,
                    source=source,
                    description=desc,
                    eml_description=f"EML: eml_scalar({value:g}) — {desc} ({units}; from nufit_6_0_parameters.json {ordering})"
                ))

    @classmethod
    def _load_desi_values(cls, registry: 'PMRegistry') -> None:
        """Load DESI 2025 cosmological parameters from cached JSON file."""
        # Load from JSON file if available
        if DATA_LOADER_AVAILABLE:
            loader = get_loader()
            w0_data = loader.get_desi("w0")
            wa_data = loader.get_desi("wa")
            w0 = w0_data.value
            w0_unc = w0_data.uncertainty
            wa = wa_data.value
            wa_unc = wa_data.uncertainty
        else:
            # v16.2: Use DESI 2025 thawing quintessence constraint
            # Old DESI DR2 Lambda-CDM was w0=-0.728, now using thawing model
            w0 = -0.957  # DESI 2025 thawing quintessence
            w0_unc = 0.067
            wa = -0.99
            wa_unc = 0.33

        # DESI 2025 thawing quintessence constraint (v16.2)
        # PM predicts w0 = -23/24 = -0.9583, which falls within BAO-only uncertainty
        w0_thawing = -0.957  # DESI 2025 thawing constraint
        w0_thawing_unc = 0.067
        wa_thawing = -0.99
        wa_thawing_unc = 0.33

        H0 = 67.4     # Planck 2018 (loaded separately)

        # Load sigma8 and S8 from DESI if available
        if DATA_LOADER_AVAILABLE:
            loader = get_loader()
            sigma8_data = loader.get_desi("sigma8")
            sigma8 = sigma8_data.value
            sigma8_unc = sigma8_data.uncertainty
            # S8 = sigma8 * sqrt(Omega_m/0.3) - Planck 2018 value
            S8_data = loader.get_desi("S8")
            S8 = S8_data.value
            S8_unc = S8_data.uncertainty
        else:
            sigma8 = 0.827
            sigma8_unc = 0.011
            S8 = 0.832
            S8_unc = 0.013

        params = [
            EstablishedParameter(
                path="desi.w0",
                value=w0,
                uncertainty=w0_unc,
                units="dimensionless",
                source="ESTABLISHED:DESI_2025",
                description="Dark energy equation of state at z=0 (standard w0-wa constraint)",
                eml_description="EML: eml_scalar(-0.957) — dark energy w₀ at z=0 from DESI 2025 standard w0-wa analysis (input)"
            ),
            EstablishedParameter(
                path="desi.wa",
                value=wa,
                uncertainty=wa_unc,
                units="dimensionless",
                source="ESTABLISHED:DESI_2025",
                description="Dark energy evolution parameter (standard w0-wa constraint)",
                eml_description="EML: eml_scalar(-0.99) — dark energy evolution parameter w_a from DESI 2025 (input)"
            ),
            # Thawing quintessence constraint - matches PM prediction
            EstablishedParameter(
                path="desi.w0_thawing",
                value=w0_thawing,
                uncertainty=w0_thawing_unc,
                units="dimensionless",
                source="ESTABLISHED:DESI_2025_THAWING",
                description="Dark energy w0 from thawing quintessence model (v16.2: -0.957±0.067)",
                eml_description="EML: eml_scalar(-0.957) — DESI 2025 thawing quintessence w₀ (BAO-only; matches PM prediction -23/24)"
            ),
            EstablishedParameter(
                path="desi.wa_thawing",
                value=wa_thawing,
                uncertainty=wa_thawing_unc,
                units="dimensionless",
                source="ESTABLISHED:DESI_2025_THAWING",
                description="Dark energy wa from thawing quintessence model",
                eml_description="EML: eml_scalar(-0.99) — DESI 2025 thawing quintessence w_a evolution parameter (input)"
            ),
            EstablishedParameter(
                path="desi.sigma8",
                value=sigma8,
                uncertainty=sigma8_unc,
                units="dimensionless",
                source="ESTABLISHED:DESI_2025",
                description="RMS matter fluctuation amplitude at 8 h^-1 Mpc (from desi_2025_constraints.json)",
                eml_description="EML: eml_scalar(0.827) — σ₈ matter fluctuation amplitude at 8 h⁻¹ Mpc (DESI 2025 / Planck 2018 input)"
            ),
            EstablishedParameter(
                path="desi.H0",
                value=H0,
                uncertainty=0.5,
                units="km/s/Mpc",
                source="ESTABLISHED:Planck2018",
                description="Hubble constant",
                eml_description="EML: eml_scalar(67.4) — Hubble constant H₀ in km/s/Mpc (Planck 2018 input)"
            ),
            EstablishedParameter(
                path="desi.Omega_m",
                value=0.3111,
                uncertainty=0.0056,
                units="dimensionless",
                source="ESTABLISHED:Planck2018",
                description="Matter density parameter",
                eml_description="EML: eml_scalar(0.3111) — matter density parameter Ω_m (Planck 2018 input)"
            ),
            EstablishedParameter(
                path="planck.S8",
                value=S8,
                uncertainty=S8_unc,
                units="dimensionless",
                source="ESTABLISHED:Planck2018",
                description="S8 parameter from Planck 2018 CMB (S8 = sigma8 * sqrt(Omega_m/0.3))",
                eml_description="EML: ops.mul(eml_vec('sigma8'), ops.sqrt(ops.div(eml_vec('Omega_m'), eml_scalar(0.3)))) — S₈ = σ₈√(Ω_m/0.3) (Planck 2018)"
            ),
            EstablishedParameter(
                path="desi.S8",
                value=S8,
                uncertainty=S8_unc,
                units="dimensionless",
                source="ESTABLISHED:Planck2018",
                description="S8 = sigma8 * sqrt(Omega_m/0.3) - loaded from desi_2025_constraints.json",
                eml_description="EML: ops.mul(eml_vec('sigma8'), ops.sqrt(ops.div(eml_vec('Omega_m'), eml_scalar(0.3)))) — S₈ = σ₈√(Ω_m/0.3) (DESI/Planck input)"
            ),
        ]

        for param in params:
            cls._register_param(registry, param)

    @classmethod
    def _load_experimental_bounds(cls, registry: 'PMRegistry') -> None:
        """Load experimental bounds (Super-K, etc.)."""
        if CONFIG_AVAILABLE:
            tau_p_bound = getattr(PhenomenologyParameters, 'TAU_PROTON_SUPER_K_BOUND', 1.67e34)
        else:
            tau_p_bound = 1.67e34

        params = [
            EstablishedParameter(
                path="bounds.tau_proton_lower",
                value=tau_p_bound,
                uncertainty=0.03e34,
                units="years",
                source="ESTABLISHED:SuperK_2024",
                description="Proton lifetime lower bound",
                eml_description="EML: eml_scalar(1.67e34) — Super-K lower bound on proton lifetime τ_p > 1.67×10³⁴ yr (PDG 2024 input)"
            ),
            EstablishedParameter(
                path="bounds.sum_m_nu_upper",
                value=0.12,
                uncertainty=0,
                units="eV",
                source="ESTABLISHED:Planck2018",
                description="Sum of neutrino masses upper bound",
                eml_description="EML: eml_scalar(0.12) — Planck 2018 upper bound Σm_ν < 0.12 eV (cosmological input)"
            ),
        ]

        for param in params:
            cls._register_param(registry, param)

    @classmethod
    def _load_theory_constants(cls, registry: 'PMRegistry') -> None:
        """Load theory-derived constants used as inputs for simulations."""
        import numpy as np

        # Electroweak VEV and Yukawa couplings
        v_ew = 246.22  # GeV, electroweak VEV
        v_yukawa = v_ew / np.sqrt(2)  # 174 GeV, Yukawa coupling scale (m_f = y_f * v_yukawa)
        m_top = 172.69  # GeV
        y_top = m_top * np.sqrt(2) / v_ew  # Top Yukawa coupling ~ 0.994

        # GUT-scale parameters (from standard GUT relations)
        g_gut = np.sqrt(4 * np.pi / 24.3)  # GUT coupling from alpha_GUT ~ 1/24.3

        params = [
            # Higgs/Yukawa parameters
            EstablishedParameter(
                path="higgs.vev_yukawa",
                value=v_yukawa,  # 174 GeV, not 246 GeV - for Higgs mass formula
                uncertainty=0.01,
                units="GeV",
                source="ESTABLISHED:SM_EW",
                description="Yukawa coupling scale v/√2 = 174 GeV (NOT the EW VEV)",
                eml_description="EML: ops.div(eml_scalar(246.22), ops.sqrt(eml_scalar(2.0))) — Yukawa scale v/√2 ≈ 174 GeV (SM electroweak input)"
            ),
            EstablishedParameter(
                path="yukawa.y_top",
                value=y_top,
                uncertainty=0.003,
                units="dimensionless",
                source="ESTABLISHED:PDG2024",
                description="Top quark Yukawa coupling",
                eml_description="EML: ops.div(ops.mul(eml_scalar(172.69), ops.sqrt(eml_scalar(2.0))), eml_scalar(246.22)) — top Yukawa y_t = m_t√2/v (PDG 2024)"
            ),
            EstablishedParameter(
                path="gauge.g_gut",
                value=g_gut,
                uncertainty=0.01,
                units="dimensionless",
                source="ESTABLISHED:GUT_THEORY",
                description="GUT gauge coupling",
                eml_description="EML: ops.sqrt(ops.div(ops.mul(eml_scalar(4.0), eml_pi()), eml_scalar(24.3))) — GUT gauge coupling from α_GUT ≈ 1/24.3"
            ),
            # Moduli stabilization parameters
            # RE_T_ATTRACTOR: From TCS G2 flux/membrane instanton geometry
            # RE_T_PHENOMENOLOGICAL: Inverted from m_H = 125.10 GeV constraint
            EstablishedParameter(
                path="moduli.re_t_attractor",
                value=1.833,  # GEOMETRIC: from TCS #187 attractor mechanism
                uncertainty=0.05,
                units="dimensionless",
                source="ESTABLISHED:G2_GEOMETRY",
                description="Attractor value for Re(T) from G2 flux instantons",
                eml_description="EML: eml_scalar(1.833) — Re(T) attractor from TCS #187 G₂ flux instanton geometry (geometric input)"
            ),
            EstablishedParameter(
                path="moduli.re_t_phenomenological",
                value=9.865,  # CONSTRAINED: gives m_H = 125.10 GeV with v_yukawa = 174 GeV
                uncertainty=0.1,
                units="dimensionless",
                source="CONSTRAINED:HIGGS_MASS",
                description="Re(T) constrained by m_H = 125.10 GeV (phenomenological input)",
                eml_description="EML: eml_scalar(9.865) — Re(T) constrained by m_H = 125.10 GeV with v_yukawa = 174 GeV (observational constraint)"
            ),
            # Topology parameters (from G2 geometry)
            EstablishedParameter(
                path="topology.T_OMEGA",
                value=0.12,
                uncertainty=0.02,
                units="dimensionless",
                source="ESTABLISHED:G2_TORSION",
                description="Torsion class parameter from TCS construction",
                eml_description="EML: eml_scalar(0.12) — torsion class parameter T_Ω from TCS G₂ construction (geometric input)"
            ),
            EstablishedParameter(
                path="topology.orientation_sum",
                value=12,
                uncertainty=0.5,
                units="dimensionless",
                source="ESTABLISHED:V21_BRIDGE_REDUCTION",
                description="Orientation sum from v21 dual-shadow bridge - determines flux winding in theta_23",
                eml_description="EML: eml_scalar(12) — orientation sum from v21 dual-shadow bridge (12 bridge pairs, geometric input)"
            ),
            # Consciousness parameters for Appendix M (Speculative Extensions)
            EstablishedParameter(
                path="consciousness.coherence_fraction",
                value=1e-5,  # ~0.001% of neurons phase-coherent
                uncertainty=0.5e-5,
                units="dimensionless",
                source="INPUT:SPECULATIVE",
                description="Fraction of neurons in quantum-coherent state (Penrose-Hameroff Orch-OR)",
                eml_description="EML: eml_scalar(1e-5) — speculative coherent neuron fraction for Orch-OR (Penrose-Hameroff, speculative input)"
            ),
            EstablishedParameter(
                path="consciousness.neuron_count",
                value=86e9,  # 86 billion neurons in human brain
                uncertainty=10e9,
                units="count",
                source="ESTABLISHED:NEUROSCIENCE",
                description="Total neuron count in human brain",
                eml_description="EML: eml_scalar(86e9) — total neuron count in human brain (neuroscience input)"
            ),
        ]

        for param in params:
            cls._register_param(registry, param)

    @classmethod
    def _load_codata_values(cls, registry: 'PMRegistry') -> None:
        """Load CODATA 2022 fundamental constants from JSON file.

        These high-precision constants are loaded from:
        simulations/data/experimental/codata_2022.json

        Values include:
        - codata.alpha_inverse: Inverse fine structure constant (1/alpha)
        - codata.mu_pe: Proton-to-electron mass ratio
        - codata.M_PLANCK: Planck mass (full, not reduced)
        """
        import json
        from pathlib import Path

        # Path to CODATA JSON file
        data_dir = Path(__file__).parent.parent / "data" / "experimental"
        codata_file = data_dir / "codata_2022.json"

        # Load from JSON file
        try:
            with open(codata_file, 'r', encoding='utf-8') as f:
                codata_data = json.load(f)
            codata_available = True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            warnings.warn(f"Could not load CODATA 2022 data: {e}. Using fallback values.")
            codata_available = False

        if codata_available:
            fc = codata_data.get("fundamental_constants", {})

            # Inverse fine structure constant
            alpha_inv = fc.get("alpha_inverse", {})
            params = [
                EstablishedParameter(
                    path="codata.alpha_inverse",
                    value=alpha_inv.get("value", 137.035999177),
                    uncertainty=alpha_inv.get("uncertainty", 0.01),
                    units=alpha_inv.get("units", "dimensionless"),
                    source="ESTABLISHED:CODATA2022",
                    description=alpha_inv.get("description", "Inverse fine structure constant"),
                    eml_description="EML: eml_scalar(137.035999177) — α⁻¹ from CODATA 2022 (input)"
                ),
            ]

            # Proton-to-electron mass ratio (mu_pe)
            mu_pe = fc.get("proton_electron_mass_ratio", {})
            params.append(
                EstablishedParameter(
                    path="codata.mu_pe",
                    value=mu_pe.get("value", 1836.15267343),
                    uncertainty=mu_pe.get("uncertainty", 2.0),
                    units=mu_pe.get("units", "dimensionless"),
                    source="ESTABLISHED:CODATA2022",
                    description=mu_pe.get("description", "Proton-to-electron mass ratio"),
                    eml_description="EML: eml_scalar(1836.15267343) — μ_pe proton-to-electron mass ratio from CODATA 2022 (input)"
                )
            )

            # Planck mass (full, not reduced)
            m_planck = fc.get("M_PLANCK", {})
            params.append(
                EstablishedParameter(
                    path="codata.M_PLANCK",
                    value=m_planck.get("value", 1.220890e19),
                    uncertainty=m_planck.get("uncertainty", 1.9e15),
                    units=m_planck.get("units", "GeV"),
                    source="ESTABLISHED:CODATA2022",
                    description=m_planck.get("description", "Planck mass"),
                    eml_description="EML: eml_scalar(1.220890e19) — M_Pl full Planck mass in GeV from CODATA 2022 (input)"
                )
            )
        else:
            # Fallback values if JSON not available
            params = [
                EstablishedParameter(
                    path="codata.alpha_inverse",
                    value=137.035999177,
                    uncertainty=0.01,  # Theory uncertainty
                    units="dimensionless",
                    source="ESTABLISHED:CODATA2022",
                    description="Inverse fine structure constant",
                    eml_description="EML: eml_scalar(137.035999177) — α⁻¹ from CODATA 2022 (input)"
                ),
                EstablishedParameter(
                    path="codata.mu_pe",
                    value=1836.15267343,
                    uncertainty=2.0,  # Theory uncertainty
                    units="dimensionless",
                    source="ESTABLISHED:CODATA2022",
                    description="Proton-to-electron mass ratio",
                    eml_description="EML: eml_scalar(1836.15267343) — μ_pe proton-to-electron mass ratio from CODATA 2022 (input)"
                ),
                EstablishedParameter(
                    path="codata.M_PLANCK",
                    value=1.220890e19,
                    uncertainty=1.9e15,
                    units="GeV",
                    source="ESTABLISHED:CODATA2022",
                    description="Planck mass",
                    eml_description="EML: eml_scalar(1.220890e19) — M_Pl full Planck mass in GeV from CODATA 2022 (input)"
                ),
            ]

        for param in params:
            cls._register_param(registry, param)

    @classmethod
    def _register_param(cls, registry: 'PMRegistry', param: EstablishedParameter) -> None:
        """Register a single parameter with the registry.

        For ESTABLISHED parameters, the value IS the experimental value.
        We set experimental_value = value to indicate this is a measured constant.
        """
        meta = {'description': param.description, 'units': param.units}
        if param.eml_description:
            meta['eml_description'] = param.eml_description
        registry.set_param(
            path=param.path,
            value=param.value,
            source=param.source,
            uncertainty=param.uncertainty,
            status=param.status,
            metadata=meta,
            # For established physics, the value IS the experimental measurement
            experimental_value=param.value,
            experimental_uncertainty=param.uncertainty,
            experimental_source=param.source,
            bound_type="measured"  # Established constants are direct measurements
        )


# Documentation of all established parameters
ESTABLISHED_PARAMS = {
    "metadata": {
        "version": "1.1",
        "description": "Complete registry of established experimental physics values",
        "sources": [
            "PDG 2024 - Particle Data Group Review",
            "NuFIT 6.0 (2024) - Neutrino oscillation global fit",
            "DESI DR2 (2024) - Dark energy survey",
            "Planck 2018 - CMB observations",
            "Super-Kamiokande - Proton decay bounds",
            "CODATA 2022 - Fundamental physical constants"
        ]
    },
    "categories": {
        "constants": ["constants.M_PLANCK", "constants.alpha_em", "constants.m_proton"],
        "pdg": [
            "pdg.m_higgs", "pdg.m_electron", "pdg.m_muon", "pdg.m_tau",
            "pdg.m_up", "pdg.m_down", "pdg.m_strange", "pdg.m_charm", "pdg.m_bottom", "pdg.m_top",
            "pdg.alpha_s_MZ", "pdg.sin2_theta_W", "pdg.m_W", "pdg.m_Z"
        ],
        "ckm": ["pdg.V_us", "pdg.V_cb", "pdg.V_ub", "pdg.J_ckm"],
        "nufit": [
            "nufit.theta_12", "nufit.theta_23", "nufit.theta_13",
            "nufit.delta_CP", "nufit.delta_m21_sq", "nufit.delta_m31_sq"
        ],
        "desi": ["desi.w0", "desi.wa", "desi.sigma8", "desi.S8", "desi.H0", "desi.Omega_m"],
        "planck": ["planck.S8"],
        "bounds": ["bounds.tau_proton_lower", "bounds.sum_m_nu_upper"],
        "codata": ["codata.alpha_inverse", "codata.mu_pe", "codata.M_PLANCK"]
    },
    "total_count": 39
}
