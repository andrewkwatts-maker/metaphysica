"""Phenomenological parameters fitted to data.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""


# ==============================================================================
# PHENOMENOLOGICAL PARAMETERS (FITTED TO DATA)
# ==============================================================================

class PhenomenologyParameters:
    """
    Parameters fitted to experimental/observational data.
    These values can be updated as new data becomes available.
    """

    # Energy Scales (v12.4 fix: standardized on reduced Planck mass)
    M_PLANCK_REDUCED = 2.435e18  # Source: CODATA 2022 reduced Planck mass [GeV]
    M_PLANCK_FULL = 1.221e19     # Source: CODATA 2022 full Planck mass [GeV]
    M_PLANCK = M_PLANCK_REDUCED  # Default: use reduced mass everywhere
    # v12.4 FIX: Derived from dimensional analysis M_* = (M_Pl^2 / V_9)^(1/11)
    M_STAR = 7.4604e+15  # 13D fundamental scale [GeV] (LOW string scale!)
    M_STAR_OLD = 1e19                # Old value (inconsistent with V_9, DO NOT USE)

    # Proton Decay (v14.1 Canonical - TCS Geometric Suppression)
    # NOTE: Uses GeometricProtonDecayParameters values (v13.0+)
    TAU_PROTON = 8.15e34  # Derived: TCS geometric suppression formula (v13.0)
    TAU_PROTON_LOWER_68 = 6.84e34  # Derived: 68% CI lower bound from Monte Carlo
    TAU_PROTON_UPPER_68 = 9.64e34  # Derived: 68% CI upper bound from Monte Carlo
    TAU_PROTON_UNCERTAINTY_OOM = 0.08  # Order of magnitude uncertainty
    TAU_PROTON_SUPER_K_BOUND = 1.67e34  # Source: Super-Kamiokande 2020 τ(p→e+π0) > 1.67×10^34 yr
    TAU_PROTON_SUPER_K_RATIO = 4.88   # Prediction / Super-K bound

    # Dark Energy (v16.2 STERILE - DESI 2025 Aligned)
    W0_NUMERATOR = -23       # Derived: -(b3 - 1) = -(24 - 1) = -23
    W0_DENOMINATOR = 24      # Derived: b3 = 24 (CHNP 2015 TCS construction)
    # w_0 = -23/24 = -0.958333... (pure geometry from G2 manifold)
    W0_GEOMETRIC = -23/24    # v16.2 STERILE: Pure geometric derivation
    W0_DESI_2025 = -0.957  # Framework-adopted thawing anchor (attribution unverified; DESI DR2 w0waCDM headline: -0.752 ± 0.057)
    W0_DESI_ERROR = 0.05  # Source: DESI 2025 DR2 1σ uncertainty
    W0_SIGMA_DEVIATION = 0.027  # vs adopted anchor; vs DESI DR2 w0waCDM headline (-0.752 ± 0.057) it is 3.6σ

    WA_EVOLUTION = 0.0       # v16.2 STERILE: No evolution (static dark energy)
    WA_ERROR = 0.15  # Source: DESI 2025 DR2 wa uncertainty
    WA_DESI_SIGNIFICANCE = 0.0  # No evolving DE in sterile model

    # Cosmological Parameters
    OMEGA_LAMBDA = 0.6889    # Source: Planck 2020 Ω_Λ = 0.6889 ± 0.0056
    OMEGA_MATTER = 0.3111    # Source: Planck 2020 Ω_m = 0.3111 ± 0.0056
    OMEGA_BARYON = 0.0486    # Source: Planck 2020 Ω_b = 0.0486 ± 0.0010
    H0 = 67.4                # Source: Planck 2020 H_0 = 67.4 ± 0.5 km/s/Mpc

    # Fine Structure Constant
    ALPHA_EM = 1/137.035999177  # Source: CODATA 2022 α = 1/137.035999177 (12-digit precision)

    @staticmethod
    def w0_value():
        """Dark energy equation of state at z=0"""
        return PhenomenologyParameters.W0_NUMERATOR / PhenomenologyParameters.W0_DENOMINATOR
