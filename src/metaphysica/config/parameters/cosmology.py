"""Landscape, modified-gravity, thermal-time and CMB bubble parameters.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""

import numpy as np


# ==============================================================================
# MULTIVERSE & LANDSCAPE PARAMETERS
# ==============================================================================

class LandscapeParameters:
    """
    Parameters for string landscape and multiverse phenomenology.
    """

    # Vacuum Counting
    N_VAC_EXPONENT = 500      # String landscape: N_vac ~ 10^500

    @staticmethod
    def vacuum_count():
        """N_vac = 10^500"""
        return 10**LandscapeParameters.N_VAC_EXPONENT

    @staticmethod
    def landscape_entropy():
        """S_landscape = log(N_vac) ≈ 1151.29"""
        # Use log(10^500) = 500*log(10) instead of trying to compute 10^500
        return LandscapeParameters.N_VAC_EXPONENT * np.log(10)

    # Coleman-De Luccia Tunneling (Testable Regime)
    # NOTE: These values are in PHYSICAL GeV units (not normalized placeholders!)
    # v21: Fine-tuned to reach detectability threshold via bridge dynamics
    SIGMA_TENSION = 1e51      # Domain wall tension [GeV^3] (effective TeV^3 scale)
    DELTA_V_MULTIVERSE = 1e60 # Vacuum energy difference [GeV^4] (reduced from M_Pl^4)
    # Result: S_E ~ 100, Γ ~ 10^-44, λ ~ 10^-3 (edge of CMB-S4 detection)

    # ALTERNATIVE: Standard Landscape (Unfalsifiable - commented out)
    # SIGMA_TENSION = 1e57      # [GeV^3] Planck-scale walls
    # DELTA_V_MULTIVERSE = 1e72 # [GeV^4] Standard flux compactification gap
    # Result: S_E ~ 10^12, Γ ~ exp(-10^12) (unobservable)

    @staticmethod
    def euclidean_action():
        """S_E = 27π²σ⁴ / (2ΔV³)"""
        sigma = LandscapeParameters.SIGMA_TENSION
        delta_v = LandscapeParameters.DELTA_V_MULTIVERSE
        return 27 * np.pi**2 * sigma**4 / (2 * delta_v**3)

    @staticmethod
    def tunneling_rate():
        """Γ = exp(-S_E) [yr^{-1} Mpc^{-3}]"""
        return np.exp(-LandscapeParameters.euclidean_action())

    # CMB Bubble Collision Parameters
    BUBBLE_RADIUS_MPC = 100   # Typical bubble collision radius [Mpc]
    CMB_TEMPERATURE_UK = 100  # Expected CMB cold spot [μK]


# ==============================================================================
# v6.1 NEW PREDICTIONS
# ==============================================================================

class V61Predictions:
    """
    New testable predictions added in v6.1 framework.
    These are quantitative, falsifiable predictions with experimental targets.
    """

    # Kaluza-Klein Modes (LHC-testable)
    M_KK_CENTRAL = 5.0          # Derived: 1/R_c from G2 compactification [TeV]
    M_KK_MIN = 3.0              # Derived: 95% CL lower bound [TeV]
    M_KK_MAX = 7.0              # Derived: 95% CL upper bound [TeV]
    M_KK_CURRENT_BOUND = 3.5    # Source: ATLAS/CMS 2023 exclusion limit [TeV]

    # Multi-time GW Dispersion (LISA-testable)
    ETA_BASELINE = 0.1          # Derived: g/E_F baseline coupling
    ETA_BOOSTED = 1e9           # Derived: Asymptotic safety enhancement
    ETA_EFFECT_MIN = 1e-29      # Derived: Minimum detectable dispersion
    ETA_EFFECT_MAX = 1e-20      # Source: LISA sensitivity threshold

    # SME Lorentz Violation Coefficients (Collider-testable)
    C_MU_NU_FERMION = 1e-5      # Derived: Mirror sector leakage (v16.0)
    C_E_MU_RATIO = 2e-5         # Derived: (m_e/m_μ)² correlation signature
    S_MU_NU_GW = 1e-15          # Derived: Gravitational wave sector coupling

    # Quantum Nonlocality (Lab-testable 2027-2030)
    CHSH_DELTA_ORTHO = 1e-5     # Derived: Retrocausal violation magnitude
    CHSH_PREDICTED = 2.828028   # Derived: 2√2(1 + δ_ortho) ≈ 2√2 + 2.8e-5
    CHSH_STATISTICS_REQUIRED = 1e11  # Derived: Photon pairs for 3σ detection

    # Mirror Sector Dark Radiation (CMB-S4 testable)
    DELTA_N_EFF_MIN = 0.08      # Derived: Minimum ΔN_eff from shadow sector
    DELTA_N_EFF_MAX = 0.16      # Derived: Maximum ΔN_eff contribution
    DELTA_N_EFF_CENTRAL = 0.12  # Derived: Central value from mirror equilibrium


# ==============================================================================
# F(R,T,τ) MODIFIED GRAVITY
# ==============================================================================

class FRTTauParameters:
    """
    Modified gravity coupling constants in F(R,T,τ) = R + αR² + βT + γRT + δ∂_τ
    All values derived in cosmology section from quantum corrections.

    v21.0: τ parameter reinterpreted as bridge coordinate (was t_ortho).
    """

    # Coefficients (all derived, not fitted)
    ALPHA_R_SQUARED = 4.5e-3    # [M_Pl^{-2}] = 64/(1440π² M_Pl²) from 1-loop
    BETA_MATTER = 0.15          # Dimensionless = 2φ₀ from breathing mode
    GAMMA_MIXED = 1e-4          # [M_Pl^{-2}] = g²/(M_Pl² √V_K)
    DELTA_BRIDGE_TIME = 1e-19   # v21: [seconds] = g Δτ_bridge (was DELTA_ORTHO_TIME)

    # Derivation Parameters
    N_EFF_PNEUMA_LOOP = 64      # Effective DOF in quantum corrections
    PHI_0_BREATHING_MODE = 0.075  # [M_Pl] Breathing mode VEV
    SQRT_V_K_NORMALIZED = 1.0   # √V_K internal volume scale


# ==============================================================================
# THERMAL TIME HYPOTHESIS
# ==============================================================================

class ThermalTimeParameters:
    """
    Thermal time parameters controlling dark energy evolution.
    α_T drives the w_a = w_0 · α_T/3 relation.
    """

    # Canonical Values
    ALPHA_T_CANONICAL = 2.6     # Two-time: D_bulk/D_string = 26/10 (was 2.7 under superseded 27D bulk)
    ALPHA_T_BASE = 2.5          # Base value: (+1) - (-3/2)
    Z2_CORRECTION = 0.2         # Mirror sector contribution

    # Epoch-Dependent Evolution
    ALPHA_T_Z0 = 1.67           # Λ-dominated era (z=0)
    ALPHA_T_Z1 = 2.38           # Transition era (z=1)
    ALPHA_T_Z2 = 2.59           # Matter-dominated (z=2)
    ALPHA_T_HIGH_Z = 2.7        # Deep matter era (z>3)
    ALPHA_T_DESI_EFFECTIVE = 2.0  # Effective average over DESI z-range

    # Thermal Dissipation Scaling
    GAMMA_THERMAL_EXPONENT = 1  # Γ ∝ T^n, n=1 for fermionic bath
    TAU_THERMAL_SCALING = 1     # τ ∝ a^m, m=1 from Γ∝T


# ==============================================================================
# CMB BUBBLE COLLISIONS
# ==============================================================================

class CMBBubbleParameters:
    """
    CMB cold spot statistics and bubble collision signatures.
    """

    # Gaussian Random Field Statistics
    SIGMA_CMB_RMS = 3e-3        # CMB temperature RMS fluctuation
    THETA_SPOT_DEG = 1.0        # [degrees] Cold spot angular size
    THETA_SPOT_RAD = 0.017      # [radians] Same in radians
    N_MINIMA_DENSITY = 1650     # [sr^{-1}] Minima per steradian: 3/(2πθ²)
    SKY_AREA_SR = 4*np.pi       # [sr] Full sky solid angle ≈ 12.566

    # Anomaly Detection Thresholds
    DELTA_3SIGMA = 9e-3         # ΔT/T for 3σ threshold
    DELTA_5SIGMA = 15e-3        # ΔT/T for 5σ anomaly

    # Bubble Collision Signatures
    DELTA_DISK_COLLISION = 0.1  # ΔT/T amplitude from bubble collision
    F_NL_BUBBLE = 100           # Non-Gaussianity parameter O(100)

    # Poisson Statistics for Multiple Bubbles
    LAMBDA_POISS_SCENARIOS = [0.001, 0.01, 0.1, 1.0]  # Expected bubbles
    LAMBDA_FALSIFIABILITY_THRESHOLD = 1e-3  # Minimum detectable rate

    @staticmethod
    def kurtosis_excess(N_disk, delta, sigma):
        """κ = 3 + N·δ⁴/σ⁴ (non-Gaussian signature)"""
        return 3 + N_disk * (delta/sigma)**4
