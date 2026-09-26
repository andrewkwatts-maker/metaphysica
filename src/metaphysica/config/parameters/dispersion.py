"""Lattice configuration and subleading dispersion parameters.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""

import numpy as np


# ==============================================================================
# LATTICE CONFIGURATION DISPERSION PARAMETERS (v16.0)
# ==============================================================================

class LatticeDispersionParameters:
    """
    Lattice Configuration Dispersion (δ_lat) - Embedding Modulation Factor.

    Physical Interpretation:
    The geometric coupling g_geom from PM theory is the "ideal" coupling assuming
    a perfect embedding of geometry in matter. Real physical systems may deviate
    due to lattice-level variations in how the G₂ holonomy is realized in actual
    microtubule lattices. δ_lat modulates this:

        g_eff = g_geom × δ_lat

    Range and Meaning:
    - δ_lat = 1.0: Perfect geometric embedding (baseline/protozoa)
    - δ_lat < 1.0: Suppressed coupling (degraded lattice coherence)
    - δ_lat > 1.0: Enhanced coupling (optimized lattice configuration)
    - Valid range: [0.7, 1.5] (physically motivated bounds)

    Biological Interpretation (Appendix/Speculative):
    - Protozoa (primitive): δ_lat ≈ 1.0 (baseline geometry)
    - Insects: δ_lat ≈ 1.15 (basic neural enhancement)
    - Mammals: δ_lat ≈ 1.30 (complex neural networks)
    - Humans: δ_lat ≈ 1.45 (tubulin isoform diversity optimizes coherence)

    Relation to Tubulin Diversity:
    The δ_lat factor may correlate with tubulin isoform diversity (α/β-tubulin
    variants), which varies across species and could modulate the effective
    geometric realization of G₂ structure in microtubule lattices.

    Main Paper Status:
    Introduced as a neutral structural parameter that acknowledges the potential
    for lattice-level modulation of geometric coupling, WITHOUT making claims
    about consciousness or evolutionary optimization.

    References:
    - Hameroff & Penrose (2014): Orch OR framework
    - Joyce (2007): G₂ holonomy geometry
    - PM v15.2: Microtubule-PM coupling
    """

    # === BASELINE PARAMETERS ===
    DELTA_LAT_BASELINE = 1.0      # Baseline: perfect geometric embedding
    DELTA_LAT_MIN = 0.7           # Lower bound: degraded coherence
    DELTA_LAT_MAX = 1.5           # Upper bound: optimized configuration

    # === GEOMETRIC COUPLING (from PneumaVielbeinParameters) ===
    # Base coupling strength from vielbein emergence
    G_GEOM_BASE = 0.1             # Dimensionless coupling from PM framework

    # === CROSS-SPECIES PREDICTIONS (SPECULATIVE/APPENDIX) ===
    # These are exploratory and require biological validation
    DELTA_LAT_PROTOZOA = 1.0      # Baseline single-cell
    DELTA_LAT_CNIDARIA = 1.05     # Simple neural nets (jellyfish)
    DELTA_LAT_INSECT = 1.15       # Basic insect nervous system
    DELTA_LAT_FISH = 1.20         # Fish neural complexity
    DELTA_LAT_REPTILE = 1.25      # Reptilian brain
    DELTA_LAT_MAMMAL = 1.30       # Mammalian neural networks
    DELTA_LAT_PRIMATE = 1.38      # Primate complexity
    DELTA_LAT_HUMAN = 1.45        # Human tubulin isoform diversity

    # === EVOLUTIONARY ORCHESTRATION FACTOR ===
    # α_evo = (δ_lat - 1.0) / 0.45 ∈ [0, 1] for evolutionary range
    # Measures degree of enhancement from baseline

    @staticmethod
    def effective_coupling(delta_lat: float = None) -> float:
        """
        Compute effective coupling modulated by lattice dispersion.

        g_eff = g_geom × δ_lat

        Args:
            delta_lat: Lattice dispersion factor (default: baseline 1.0)

        Returns:
            Effective coupling strength
        """
        if delta_lat is None:
            delta_lat = LatticeDispersionParameters.DELTA_LAT_BASELINE
        # Clamp to valid range
        delta_lat = np.clip(delta_lat,
                            LatticeDispersionParameters.DELTA_LAT_MIN,
                            LatticeDispersionParameters.DELTA_LAT_MAX)
        return LatticeDispersionParameters.G_GEOM_BASE * delta_lat

    @staticmethod
    def evolutionary_factor(delta_lat: float) -> float:
        """
        Compute evolutionary orchestration factor α_evo.

        α_evo = (δ_lat - 1.0) / (δ_lat_max - 1.0) ∈ [0, 1]

        This quantifies how far along the evolutionary optimization
        spectrum a given δ_lat value lies.

        Args:
            delta_lat: Lattice dispersion factor

        Returns:
            Evolutionary factor (0 = baseline, 1 = maximum enhancement)
        """
        delta_lat = np.clip(delta_lat,
                            LatticeDispersionParameters.DELTA_LAT_MIN,
                            LatticeDispersionParameters.DELTA_LAT_MAX)
        return (delta_lat - LatticeDispersionParameters.DELTA_LAT_BASELINE) / \
               (LatticeDispersionParameters.DELTA_LAT_MAX - LatticeDispersionParameters.DELTA_LAT_BASELINE)

    @staticmethod
    def get_species_predictions() -> dict:
        """Return cross-species δ_lat predictions."""
        params = LatticeDispersionParameters
        species = [
            ('Protozoa', params.DELTA_LAT_PROTOZOA),
            ('Cnidaria', params.DELTA_LAT_CNIDARIA),
            ('Insect', params.DELTA_LAT_INSECT),
            ('Fish', params.DELTA_LAT_FISH),
            ('Reptile', params.DELTA_LAT_REPTILE),
            ('Mammal', params.DELTA_LAT_MAMMAL),
            ('Primate', params.DELTA_LAT_PRIMATE),
            ('Human', params.DELTA_LAT_HUMAN),
        ]
        return {
            name: {
                'delta_lat': delta,
                'g_eff': params.effective_coupling(delta),
                'alpha_evo': params.evolutionary_factor(delta)
            }
            for name, delta in species
        }

    @staticmethod
    def export_data() -> dict:
        """Export data for theory_output.json"""
        params = LatticeDispersionParameters
        return {
            'parameter_name': 'Lattice Configuration Dispersion',
            'symbol': 'δ_lat',
            'baseline': params.DELTA_LAT_BASELINE,
            'valid_range': [params.DELTA_LAT_MIN, params.DELTA_LAT_MAX],
            'g_geom_base': params.G_GEOM_BASE,
            'formula': 'g_eff = g_geom × δ_lat',
            'evolutionary_formula': 'α_evo = (δ_lat - 1) / (δ_lat_max - 1)',
            'species_predictions': params.get_species_predictions(),
            'physical_interpretation': (
                'Modulates geometric coupling strength based on lattice-level '
                'realization of G₂ holonomy in physical systems'
            ),
            'main_paper_status': 'Neutral structural parameter',
            'appendix_status': 'Speculative evolutionary implications',
            'references': [
                'Hameroff & Penrose (2014): Orch OR',
                'Joyce (2007): G₂ holonomy',
                'PM v15.2: Microtubule coupling'
            ],
            'version': 'v23.0'
        }


# ==============================================================================
# SUBLEADING DISPERSION PARAMETERS (v23.0)
# ==============================================================================

class SubleadingDispersionParameters:
    """
    Subleading corrections and theoretical uncertainties for fragile predictions.

    Several leading-order relations emerge exactly from the geometric symmetries
    and flux stabilization of TCS manifold #187. Subleading effects—such as flux
    perturbations on associative cycles or higher-order instantons—are expected
    to introduce small dispersions.

    These parameters default to 0, corresponding to leading-order exactitude.
    Non-zero values represent subleading geometric corrections that may be
    constrained by future precision data (DUNE, Hyper-K, next-gen cosmology).

    Key Parameters:
    - ε_atm: Atmospheric mixing deviation (θ₂₃ = 45° × (1 + ε_atm))
    - φ_CP: CP phase dispersion (discrete set from Z_n automorphisms)
    - δ_race: Racetrack secondary coefficient offset (N_second = 25 + δ_race)
    - Δγ: Ghost correction factor uncertainty (γ = 0.5 ± Δγ)

    Current experimental agreement favors values near zero, consistent with
    suppressed subleading contributions. Future precision data may constrain
    or require non-zero values, providing tests of geometric rigidity.

    References:
    - NuFIT 6.0 (2024): Global neutrino oscillation analysis
    - DESI DR2 (2024): Dark energy constraints
    - PM v16.0: Lattice dispersion framework
    """

    # === ATMOSPHERIC MIXING (θ₂₃) ===
    # Leading order: exactly 45° from shadow_kuf = shadow_chet symmetry
    # Subleading: flux perturbation or Ricci-flow asymmetry
    EPSILON_ATM_DEFAULT = 0.0       # Default: exact maximality
    EPSILON_ATM_MIN = -0.05         # Allows down to ~42.75°
    EPSILON_ATM_MAX = 0.05          # Allows up to ~47.25°
    THETA_23_LEADING = 45.0         # degrees

    # === CP VIOLATING PHASE (δ_CP) ===
    # Leading order: 235° from specific G₂ cycle phase combination
    # Subleading: Z_n automorphisms allow discrete set
    DELTA_CP_CENTRAL = 235.0        # degrees (geometric prediction)
    DELTA_CP_DISCRETE_SET = [194.0, 235.0, 286.0]  # From Z₄ cycle automorphisms
    PHI_CP_OFFSET_DEFAULT = 0.0     # Default: central value
    PHI_CP_OFFSET_MIN = -41.0       # Allows down to 194°
    PHI_CP_OFFSET_MAX = 51.0        # Allows up to 286°

    # === RACETRACK SECONDARY COEFFICIENT ===
    # Leading order: N_second = N_flux + 1 = 25
    # Subleading: landscape statistics allow N_flux ± {0,1}
    N_FLUX_PRIMARY = 24  # Derived: chi_eff/6 = 144/6 = 24 (flux quantization)
    DELTA_RACE_DEFAULT = 0          # Default: N_second = 25
    DELTA_RACE_MIN = -1             # Allows N_second = 24
    DELTA_RACE_MAX = 1              # Allows N_second = 26

    # === GHOST CORRECTION FACTOR (γ for d_eff) ===
    # Leading order: γ = 0.5 from loop corrections
    # Subleading: quantum volume corrections
    GAMMA_GHOST_DEFAULT = 0.5  # Derived: Loop correction from ghost sector (1-loop)
    DELTA_GAMMA_DEFAULT = 0.0       # Default: exact γ = 0.5
    DELTA_GAMMA_MIN = -0.1          # Allows γ down to 0.4
    DELTA_GAMMA_MAX = 0.1           # Allows γ up to 0.6

    # === ALPHA_GUT THRESHOLD CORRECTIONS ===
    # Leading order: α_GUT⁻¹ = 23.54 from b₃ flux
    # Subleading: threshold corrections ~5-10%
    ALPHA_GUT_INV_CENTRAL = 23.54  # Derived: b₃/(1 + loop) = 24/1.02 flux quantization
    ALPHA_GUT_UNCERTAINTY = 1.5     # ±1.5 from subleading effects

    @staticmethod
    def theta_23(epsilon_atm: float = None) -> float:
        """
        Compute atmospheric mixing angle with subleading correction.

        θ₂₃ = 45° × (1 + ε_atm)

        Args:
            epsilon_atm: Deviation from maximal (default 0)

        Returns:
            Atmospheric mixing angle in degrees
        """
        if epsilon_atm is None:
            epsilon_atm = SubleadingDispersionParameters.EPSILON_ATM_DEFAULT
        epsilon_atm = np.clip(epsilon_atm,
                              SubleadingDispersionParameters.EPSILON_ATM_MIN,
                              SubleadingDispersionParameters.EPSILON_ATM_MAX)
        return SubleadingDispersionParameters.THETA_23_LEADING * (1.0 + epsilon_atm)

    @staticmethod
    def delta_cp(phi_offset: float = None, discrete_choice: str = None) -> float:
        """
        Compute CP phase with subleading dispersion.

        δ_CP = 235° + φ_offset (continuous)
        OR
        δ_CP ∈ {194°, 235°, 286°} (discrete from Z_n automorphisms)

        Args:
            phi_offset: Continuous offset from central value (default 0)
            discrete_choice: "low", "central", or "high" for discrete set

        Returns:
            CP violating phase in degrees
        """
        if discrete_choice is not None:
            choices = {
                "low": 194.0,
                "central": 235.0,
                "high": 286.0
            }
            return choices.get(discrete_choice.lower(), 235.0)

        if phi_offset is None:
            phi_offset = SubleadingDispersionParameters.PHI_CP_OFFSET_DEFAULT
        phi_offset = np.clip(phi_offset,
                             SubleadingDispersionParameters.PHI_CP_OFFSET_MIN,
                             SubleadingDispersionParameters.PHI_CP_OFFSET_MAX)
        return SubleadingDispersionParameters.DELTA_CP_CENTRAL + phi_offset

    @staticmethod
    def racetrack_b(delta_race: int = None) -> float:
        """
        Compute racetrack secondary coefficient with offset.

        b = 2π / (25 + δ_race)

        Args:
            delta_race: Integer offset {-1, 0, +1} (default 0)

        Returns:
            Secondary racetrack coefficient
        """
        if delta_race is None:
            delta_race = SubleadingDispersionParameters.DELTA_RACE_DEFAULT
        delta_race = int(np.clip(delta_race,
                                 SubleadingDispersionParameters.DELTA_RACE_MIN,
                                 SubleadingDispersionParameters.DELTA_RACE_MAX))
        n_second = 25 + delta_race
        return 2 * np.pi / n_second

    @staticmethod
    def d_eff_with_uncertainty(delta_gamma: float = None) -> tuple:
        """
        Compute effective dimension with ghost correction uncertainty.

        d_eff = 12 + γ × correction_terms

        Args:
            delta_gamma: Uncertainty in γ (default 0)

        Returns:
            (d_eff_central, d_eff_min, d_eff_max)
        """
        if delta_gamma is None:
            delta_gamma = SubleadingDispersionParameters.DELTA_GAMMA_DEFAULT
        delta_gamma = np.clip(delta_gamma,
                              SubleadingDispersionParameters.DELTA_GAMMA_MIN,
                              SubleadingDispersionParameters.DELTA_GAMMA_MAX)

        gamma_central = SubleadingDispersionParameters.GAMMA_GHOST_DEFAULT
        gamma_min = gamma_central - abs(delta_gamma)
        gamma_max = gamma_central + abs(delta_gamma)

        # d_eff = 12 + γ × (shadow_kuf + shadow_chet) with typical correction ~1.15
        correction_factor = 1.152  # From shadow sector contributions
        d_eff_central = 12 + gamma_central * correction_factor
        d_eff_min = 12 + gamma_min * correction_factor
        d_eff_max = 12 + gamma_max * correction_factor

        return (d_eff_central, d_eff_min, d_eff_max)

    @staticmethod
    def w0_band(delta_gamma: float = None) -> tuple:
        """
        Compute w₀ band from d_eff uncertainty.

        w₀ = -(d_eff - 1)/(d_eff + 1)

        Args:
            delta_gamma: Ghost correction uncertainty (default 0)

        Returns:
            (w0_central, w0_min, w0_max) - note: more negative is "min"
        """
        d_central, d_min, d_max = SubleadingDispersionParameters.d_eff_with_uncertainty(delta_gamma)

        def w0_from_deff(d):
            return -(d - 1) / (d + 1)

        w0_central = w0_from_deff(d_central)
        w0_low = w0_from_deff(d_max)   # Higher d_eff → more negative w₀
        w0_high = w0_from_deff(d_min)  # Lower d_eff → less negative w₀

        return (w0_central, w0_low, w0_high)

    @staticmethod
    def get_dispersion_summary() -> dict:
        """Return summary of all dispersion parameters and their defaults."""
        return {
            'epsilon_atm': {
                'default': SubleadingDispersionParameters.EPSILON_ATM_DEFAULT,
                'range': [SubleadingDispersionParameters.EPSILON_ATM_MIN,
                          SubleadingDispersionParameters.EPSILON_ATM_MAX],
                'effect': 'θ₂₃ = 45° × (1 + ε_atm)',
                'theta_23_range': [
                    SubleadingDispersionParameters.theta_23(SubleadingDispersionParameters.EPSILON_ATM_MIN),
                    SubleadingDispersionParameters.theta_23(SubleadingDispersionParameters.EPSILON_ATM_MAX)
                ]
            },
            'phi_cp_offset': {
                'default': SubleadingDispersionParameters.PHI_CP_OFFSET_DEFAULT,
                'discrete_set': SubleadingDispersionParameters.DELTA_CP_DISCRETE_SET,
                'effect': 'δ_CP = 235° + φ_offset OR discrete {194°, 235°, 286°}'
            },
            'delta_race': {
                'default': SubleadingDispersionParameters.DELTA_RACE_DEFAULT,
                'range': [SubleadingDispersionParameters.DELTA_RACE_MIN,
                          SubleadingDispersionParameters.DELTA_RACE_MAX],
                'effect': 'N_second = 25 + δ_race'
            },
            'delta_gamma': {
                'default': SubleadingDispersionParameters.DELTA_GAMMA_DEFAULT,
                'range': [SubleadingDispersionParameters.DELTA_GAMMA_MIN,
                          SubleadingDispersionParameters.DELTA_GAMMA_MAX],
                'effect': 'γ = 0.5 ± Δγ → w₀ band'
            }
        }

    @staticmethod
    def export_data() -> dict:
        """Export data for theory_output.json"""
        w0_band = SubleadingDispersionParameters.w0_band(0.1)  # With max uncertainty
        return {
            'parameter_name': 'Subleading Dispersion Corrections',
            'version': 'v23.0',
            'theta_23': {
                'leading_order': SubleadingDispersionParameters.THETA_23_LEADING,
                'with_uncertainty': f"{SubleadingDispersionParameters.THETA_23_LEADING}° ± 2.25°",
                'epsilon_atm_range': [
                    SubleadingDispersionParameters.EPSILON_ATM_MIN,
                    SubleadingDispersionParameters.EPSILON_ATM_MAX
                ],
                'justification': 'Subleading flux-induced symmetry breaking'
            },
            'delta_cp': {
                'central': SubleadingDispersionParameters.DELTA_CP_CENTRAL,
                'discrete_set': SubleadingDispersionParameters.DELTA_CP_DISCRETE_SET,
                'justification': 'Z_n automorphisms of G₂ cycle graph'
            },
            'racetrack': {
                'n_second_default': 25,
                'n_second_range': [24, 25, 26],
                'justification': 'Landscape statistics for nearby integer fluxes'
            },
            'w0_band': {
                'central': w0_band[0],
                'range': [w0_band[1], w0_band[2]],
                'justification': 'Loop corrections to ghost factor γ'
            },
            'framing': 'Leading-order predictions with stated theoretical uncertainties',
            'status': 'DEFAULTS AT ZERO - Future data may constrain non-zero values'
        }
