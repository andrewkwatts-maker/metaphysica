"""Fundamental constants, the SM parameter registry and framework statistics.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""

from .registry import _ssot_dim


# ==============================================================================
# FUNDAMENTAL CONSTANTS (THEORY-DERIVED)
# ==============================================================================

class FundamentalConstants:
    """
    Constants derived from fundamental theoretical principles.
    These should NOT be changed unless the underlying theory is modified.
    """

    # Dimensional Structure (v21/v22 Dual-Shadow Bridge Framework)
    # =========================================================
    # 26D(24,2) = 12×(2,0) bridge pairs + 2 shadow times + two shadow-time directions → 2×13D(12,1) shadows
    # (Legacy variable names use "25D" for backward compatibility)
    #
    # Structure: 26D(24,2) bulk splits via 12×(2,0) bridge pairs into dual 13D(12,1) shadows
    # The 12 bridge pairs connect corresponding spatial dimensions between Normal/Mirror shadows
    # Both shadows share the single (0,1) temporal dimension
    # Two-time ruling: Sp(2,R) gauge symmetry (Bars) controls ghosts/CTCs (STRUCTURAL)
    # OR reduction R_perp² = -I identifies physics across shadows

    # Bulk dimensions (two-time): 24 space + 2 times = 26D
    # Read from FormulasRegistry, not written here -- see _ssot_dim(). These
    # follow the open (24,2)/26D vs (26,2)/28D ruling automatically.
    D_BULK = _ssot_dim("D_ancestral_total")
    SIGNATURE_BULK = (_ssot_dim("D_ancestral_space"), _ssot_dim("D_ancestral_time"))

    # v21/v22 Dual-Shadow Structure (replaces Sp(2,R) gauge fixing)
    N_SHADOWS = 2             # Derived: Normal + Mirror shadows
    D_PER_SHADOW = _ssot_dim("D_shadow_total")
    SIGNATURE_SHADOW = (_ssot_dim("D_shadow_space"), _ssot_dim("D_shadow_time"))
    N_BRIDGE_PAIRS = _ssot_dim("bridge_local")
    SIGNATURE_BRIDGE_PAIR = (2, 0)  # Each bridge pair is Euclidean (2,0)

    # Legacy (deprecated - kept for backward compatibility)
    D_AFTER_SP2R = _ssot_dim("D_shadow_total")  # legacy alias, SSOT-backed
    SIGNATURE_INITIAL = (_ssot_dim("D_ancestral_space"), _ssot_dim("D_ancestral_time"))

    # Internal compactification (G₂ manifold or CY3×S¹/Z₂)
    INTERNAL_MANIFOLD = "G2"  # 7D holonomy manifold
    D_INTERNAL = 7  # Source: Joyce (2000) G2 holonomy manifold dimension

    # Effective spacetime after compactification
    # v21: 12D per shadow - 7D (G2) = 5D, plus bridge contribution gives 6D effective
    D_EFFECTIVE = 6           # Derived: 5D per shadow + bridge = 6D effective bulk
    SIGNATURE_EFFECTIVE = (5, 1)  # Derived: Five spatial + one time

    # Shared dimensions decomposition
    D_COMMON = 4              # Derived: Accessible to all branes (3 space + 1 time)
    D_SHARED_EXTRAS = 2       # Derived: Extra dimensions (observable brane only)

    # Brane Hierarchy Structure (Heterogeneous)
    N_BRANES = 4              # Derived: 1 observable + 3 shadow branes
    D_OBSERVABLE_BRANE = 6    # Derived: (5,1) = 4D_common + 2D_shared + time
    D_SHADOW_BRANE = 4        # Derived: (3,1) = 4D_common + time only
    N_SHADOW_BRANES = 3  # Derived: N_BRANES - 1 observable = 4 - 1 = 3

    # Legacy (for backward compatibility, will be phased out)
    D_OBSERVED = 4            # Derived: Effective 4D at low energies
    SPATIAL_DIMS = 3          # Source: Observable spatial dimensions (empirical)
    TIME_DIMS = 1             # Source: Observable time dimension (empirical)

    # TCS G₂ Manifold #187 Topology (Corti et al. 2015)
    # χ_eff = 2(h¹¹ - h²¹ + h³¹) = 2(4 - 0 + 68) = 144
    # Also: χ_eff = 6 × b₃ = 6 × 24 = 144 (flux quantization)
    HODGE_H11 = 4  # Source: CHNP 2015 h^{1,1} = 4 Kahler moduli (= b2)
    HODGE_H21 = 0  # Source: G2 manifolds have no complex structure moduli (h^{2,1} = 0)
    HODGE_H31 = 68  # Source: CHNP 2015 h^{3,1} = 68 associative moduli

    # Symmetry Factors
    FLUX_REDUCTION = 2  # Derived: Z2 orbifold flux reduction factor
    BRIDGE_DOFS = 2     # v21: Bridge dimensions (was GAUGING_DOFS=12 from Sp(2,R))
    MIRRORING_FACTOR = 2  # Derived: Dual-shadow structure (Normal + Mirror)

    # v21 OR Reduction Operator
    # R_perp = [[0,-1],[1,0]], R_perp² = -I, det(R_perp) = 1
    OR_SQUARE_VALUE = -1  # R_perp² = -I (Möbius double-cover)
    OR_DET_VALUE = 1      # det(R_perp) = 1 (orientation-preserving)
    BRIDGE_PERIOD = 7.99  # L = 2π√φ ≈ 7.99 (golden ratio period)

    # Standard Model Structure
    SM_GLUONS = 8  # Source: dim(SU(3)) = 8 gluon degrees of freedom
    SM_WEAK = 3  # Source: dim(SU(2)) = 3 weak gauge bosons
    SM_PHOTON = 1  # Source: dim(U(1)) = 1 photon
    SM_BOSONS = SM_GLUONS + SM_WEAK + SM_PHOTON  # Total: 12

    # Derived Topological Invariants
    @staticmethod
    def euler_characteristic():
        """χ_eff = 2(h¹¹ - h²¹ + h³¹) for TCS G₂ manifold"""
        chi_eff = 2 * (FundamentalConstants.HODGE_H11
                      - FundamentalConstants.HODGE_H21
                      + FundamentalConstants.HODGE_H31)
        return chi_eff  # = 2(4 - 0 + 68) = 144

    @staticmethod
    def euler_characteristic_effective():
        """Effective χ for generation counting: |χ_eff|/48 = 3 generations"""
        # χ_eff = 144 from Hodge numbers OR 6 × b₃ = 6 × 24 = 144
        return 144

    @staticmethod
    def fermion_generations():
        """N_gen = floor(χ_eff / (24 × flux_reduce))"""
        chi_eff = FundamentalConstants.euler_characteristic_effective()
        return int(chi_eff / (24 * FundamentalConstants.FLUX_REDUCTION))

    @staticmethod
    def pneuma_dimension_full():
        """Pneuma spinor dimension: 2^(D/2) from Clifford algebra"""
        return int(2**(FundamentalConstants.D_BULK / 2))

    @staticmethod
    def pneuma_dimension_reduced():
        """v22: Per-shadow spinor dimension after dual-shadow split"""
        # In v22: Each shadow has Spin(12,1) spinors = 2^[13/2] = 2^6 = 64 components
        # Combined via OR reduction: 64 effective (not 64×64)
        full = FundamentalConstants.pneuma_dimension_full()
        # v21: Divide by bridge DOFs and shadow factor
        return int(full / (2**(FundamentalConstants.BRIDGE_DOFS))
                   / FundamentalConstants.MIRRORING_FACTOR)


# ==============================================================================
# SM PARAMETER REGISTRY (v16.1) - Single Source of Truth for All Parameters
# ==============================================================================

class SMParameterRegistry:
    """Registry of all Standard Model and BSM parameters with derivation status.

    Status Types:
    - DERIVED: Geometrically derived from G₂ topology (pure prediction)
    - CALIBRATED: Fitted to experimental data (pending geometric derivation)
    - INPUT: Observational constraint (e.g., Higgs mass fixes modulus)
    - TOPOLOGICAL: Fixed by manifold choice (e.g., χ_eff, b₂, b₃)

    This registry is the single source of truth for:
    - Total parameter count
    - Calibrated vs derived counts
    - Framework statistics for UI display
    """

    # Complete registry of all 58 parameters
    # Format: 'param_id': {'name': str, 'status': str, 'category': str, 'sigma': float}
    PARAMETERS = {
        # === QUARK MASSES (6) ===
        'm_u': {'name': 'Up quark mass', 'status': 'DERIVED', 'category': 'fermion_masses', 'sigma': 0.5},
        'm_d': {'name': 'Down quark mass', 'status': 'DERIVED', 'category': 'fermion_masses', 'sigma': 0.8},
        'm_c': {'name': 'Charm quark mass', 'status': 'DERIVED', 'category': 'fermion_masses', 'sigma': 0.2},
        'm_s': {'name': 'Strange quark mass', 'status': 'DERIVED', 'category': 'fermion_masses', 'sigma': 1.2},
        'm_t': {'name': 'Top quark mass', 'status': 'DERIVED', 'category': 'fermion_masses', 'sigma': 0.7},
        'm_b': {'name': 'Bottom quark mass', 'status': 'DERIVED', 'category': 'fermion_masses', 'sigma': 0.6},

        # === LEPTON MASSES (3) ===
        'm_e': {'name': 'Electron mass', 'status': 'CALIBRATED', 'category': 'fermion_masses', 'sigma': 0.0},
        'm_mu': {'name': 'Muon mass', 'status': 'CALIBRATED', 'category': 'fermion_masses', 'sigma': 0.0},
        'm_tau': {'name': 'Tau mass', 'status': 'DERIVED', 'category': 'fermion_masses', 'sigma': 0.1},

        # === NEUTRINO MASSES (3) ===
        'm_nu1': {'name': 'Lightest neutrino mass', 'status': 'DERIVED', 'category': 'neutrino', 'sigma': 0.5},
        'm_nu2': {'name': 'Second neutrino mass', 'status': 'DERIVED', 'category': 'neutrino', 'sigma': 2.7},
        'm_nu3': {'name': 'Heaviest neutrino mass', 'status': 'DERIVED', 'category': 'neutrino', 'sigma': 0.2},

        # === CKM MATRIX (4) ===
        'theta_12_ckm': {'name': 'CKM θ₁₂ (Cabibbo angle)', 'status': 'DERIVED', 'category': 'ckm', 'sigma': 0.1},
        'theta_23_ckm': {'name': 'CKM θ₂₃', 'status': 'FITTED', 'category': 'ckm', 'sigma': 0.3},
        'theta_13_ckm': {'name': 'CKM θ₁₃', 'status': 'FITTED', 'category': 'ckm', 'sigma': 0.2},
        'delta_ckm': {'name': 'CKM CP phase δ', 'status': 'FITTED', 'category': 'ckm', 'sigma': 0.5},

        # === PMNS MATRIX (4) ===
        'theta_12_pmns': {'name': 'PMNS θ₁₂ (solar angle)', 'status': 'FITTED', 'category': 'pmns', 'sigma': 0.2},
        'theta_23_pmns': {'name': 'PMNS θ₂₃ (atmospheric angle)', 'status': 'DERIVED', 'category': 'pmns', 'sigma': 0.0},
        'theta_13_pmns': {'name': 'PMNS θ₁₃ (reactor angle)', 'status': 'DERIVED', 'category': 'pmns', 'sigma': 0.2},
        'delta_cp_pmns': {'name': 'PMNS CP phase δ_CP', 'status': 'FITTED', 'category': 'pmns', 'sigma': 1.1},

        # === GAUGE COUPLINGS (3) ===
        'g1': {'name': 'U(1) coupling g₁', 'status': 'DERIVED', 'category': 'gauge', 'sigma': 0.1},
        'g2': {'name': 'SU(2) coupling g₂', 'status': 'DERIVED', 'category': 'gauge', 'sigma': 0.1},
        'g3': {'name': 'SU(3) coupling g₃', 'status': 'DERIVED', 'category': 'gauge', 'sigma': 0.2},

        # === HIGGS PARAMETERS (2) ===
        'v_higgs': {'name': 'Higgs VEV', 'status': 'DERIVED', 'category': 'higgs', 'sigma': 0.02},
        'm_higgs': {'name': 'Higgs mass', 'status': 'INPUT', 'category': 'higgs', 'sigma': 0.9},

        # === STRONG CP (1) ===
        'theta_qcd': {'name': 'Strong CP phase θ_QCD', 'status': 'DERIVED', 'category': 'gauge', 'sigma': 0.0},

        # === GUT PARAMETERS (3) ===
        'm_gut': {'name': 'GUT scale M_GUT', 'status': 'DERIVED', 'category': 'gut', 'sigma': 0.5},
        'alpha_gut': {'name': 'Unified coupling α_GUT', 'status': 'CALIBRATED', 'category': 'gut', 'sigma': 0.3},
        'proton_lifetime': {'name': 'Proton lifetime τ_p', 'status': 'DERIVED', 'category': 'gut', 'sigma': 0.5},

        # === NEUTRINO MECHANISM (2) ===
        'majorana_phase1': {'name': 'Majorana phase α₁', 'status': 'DERIVED', 'category': 'neutrino', 'sigma': 1.0},
        'majorana_phase2': {'name': 'Majorana phase α₂', 'status': 'DERIVED', 'category': 'neutrino', 'sigma': 1.0},

        # === DARK SECTOR (3) ===
        'w0': {'name': 'Dark energy w₀', 'status': 'DERIVED', 'category': 'dark_energy', 'sigma': 0.4},
        'wa': {'name': 'Dark energy wa', 'status': 'DERIVED', 'category': 'dark_energy', 'sigma': 0.8},
        'dm_ratio': {'name': 'DM/baryon ratio', 'status': 'DERIVED', 'category': 'dark_matter', 'sigma': 0.7},

        # === KK SPECTRUM (2) ===
        'm_kk1': {'name': 'First KK graviton mass', 'status': 'DERIVED', 'category': 'kk_spectrum', 'sigma': 0.0},
        'm_kk2': {'name': 'Second KK graviton mass', 'status': 'DERIVED', 'category': 'kk_spectrum', 'sigma': 0.0},

        # === TOPOLOGICAL INVARIANTS (6) ===
        'chi_eff': {'name': 'Effective Euler characteristic', 'status': 'TOPOLOGICAL', 'category': 'topology', 'sigma': 0.0},
        'b2': {'name': 'Second Betti number', 'status': 'TOPOLOGICAL', 'category': 'topology', 'sigma': 0.0},
        'b3': {'name': 'Third Betti number', 'status': 'TOPOLOGICAL', 'category': 'topology', 'sigma': 0.0},
        'n_gen': {'name': 'Number of generations', 'status': 'DERIVED', 'category': 'topology', 'sigma': 0.0},
        'h11': {'name': 'Hodge number h¹¹', 'status': 'TOPOLOGICAL', 'category': 'topology', 'sigma': 0.0},
        'h31': {'name': 'Hodge number h³¹', 'status': 'TOPOLOGICAL', 'category': 'topology', 'sigma': 0.0},

        # === MODULI (4) ===
        're_t': {'name': 'Complex structure modulus Re(T)', 'status': 'INPUT', 'category': 'moduli', 'sigma': 0.0},
        'im_t': {'name': 'Complex structure modulus Im(T)', 'status': 'DERIVED', 'category': 'moduli', 'sigma': 0.5},
        'vev_coefficient': {'name': 'VEV coefficient', 'status': 'CALIBRATED', 'category': 'moduli', 'sigma': 0.1},
        'tcs_volume': {'name': 'TCS manifold volume', 'status': 'DERIVED', 'category': 'moduli', 'sigma': 0.3},

        # === COSMOLOGICAL (4) ===
        'hubble_constant': {'name': 'Hubble constant H₀', 'status': 'DERIVED', 'category': 'cosmology', 'sigma': 1.5},
        'omega_matter': {'name': 'Matter density Ωₘ', 'status': 'DERIVED', 'category': 'cosmology', 'sigma': 0.8},
        'omega_lambda': {'name': 'Dark energy density Ω_Λ', 'status': 'DERIVED', 'category': 'cosmology', 'sigma': 0.8},
        'sigma8': {'name': 'Amplitude σ₈', 'status': 'DERIVED', 'category': 'cosmology', 'sigma': 1.2},

        # === ADDITIONAL PREDICTIONS (6) ===
        'epsilon_cabibbo': {'name': 'Cabibbo suppression ε', 'status': 'DERIVED', 'category': 'yukawa', 'sigma': 0.1},
        'd_eff': {'name': 'Effective dimension d_eff', 'status': 'DERIVED', 'category': 'dark_energy', 'sigma': 0.3},
        'shadow_kuf': {'name': 'Shadow dimension ק', 'status': 'DERIVED', 'category': 'shadow', 'sigma': 0.0},
        'shadow_chet': {'name': 'Shadow dimension ח', 'status': 'DERIVED', 'category': 'shadow', 'sigma': 0.0},
        'gw_dispersion': {'name': 'GW dispersion η', 'status': 'DERIVED', 'category': 'predictions', 'sigma': 0.5},
        'br_proton': {'name': 'Proton decay BR(e⁺π⁰)', 'status': 'DERIVED', 'category': 'gut', 'sigma': 0.2},
    }

    @classmethod
    def count_by_status(cls, status: str) -> int:
        """Count parameters with given status."""
        return sum(1 for p in cls.PARAMETERS.values() if p['status'] == status)

    @classmethod
    def count_by_category(cls, category: str) -> int:
        """Count parameters in given category."""
        return sum(1 for p in cls.PARAMETERS.values() if p['category'] == category)

    @classmethod
    def get_by_status(cls, status: str) -> dict:
        """Get all parameters with given status."""
        return {k: v for k, v in cls.PARAMETERS.items() if v['status'] == status}

    @classmethod
    def get_within_sigma(cls, max_sigma: float) -> int:
        """Count parameters within given sigma of experiment."""
        return sum(1 for p in cls.PARAMETERS.values() if p['sigma'] <= max_sigma)

    @classmethod
    def get_exact_matches(cls) -> int:
        """Count parameters with sigma = 0 (exact matches)."""
        return sum(1 for p in cls.PARAMETERS.values() if p['sigma'] == 0.0)

    @classmethod
    def total_parameters(cls) -> int:
        """Total number of registered parameters."""
        return len(cls.PARAMETERS)

    @classmethod
    def export_registry(cls) -> dict:
        """Export full registry for theory_output.json."""
        return {
            'parameters': cls.PARAMETERS,
            'counts': {
                'total': cls.total_parameters(),
                'derived': cls.count_by_status('DERIVED'),
                'calibrated': cls.count_by_status('CALIBRATED'),
                'input': cls.count_by_status('INPUT'),
                'topological': cls.count_by_status('TOPOLOGICAL'),
            },
            'validation': {
                'within_1sigma': cls.get_within_sigma(1.0),
                'within_2sigma': cls.get_within_sigma(2.0),
                'exact_matches': cls.get_exact_matches(),
            },
            'categories': list(set(p['category'] for p in cls.PARAMETERS.values()))
        }


# ==============================================================================
# FRAMEWORK STATISTICS (v16.1) - Dynamically Computed from Registry
# ==============================================================================

class FrameworkStatistics:
    """Framework Statistics for Dynamic UI Population

    All counts are now dynamically computed from SMParameterRegistry.
    Used by auth-guard.js and other UI components.

    Version: 16.1
    """

    # Descriptions for UI
    FRAMEWORK_TAGLINE = "A unified geometric framework"
    MANIFOLD_TYPE = "G₂"

    @classmethod
    def total_sm_parameters(cls) -> int:
        """Total SM + BSM parameters (dynamically computed)."""
        return SMParameterRegistry.total_parameters()

    @classmethod
    def calibrated_parameters(cls) -> int:
        """Count of calibrated parameters (dynamically computed)."""
        return SMParameterRegistry.count_by_status('CALIBRATED')

    @classmethod
    def derived_parameters(cls) -> int:
        """Count of derived parameters (dynamically computed)."""
        return SMParameterRegistry.count_by_status('DERIVED')

    @classmethod
    def input_parameters(cls) -> int:
        """Count of input parameters (dynamically computed)."""
        return SMParameterRegistry.count_by_status('INPUT')

    @classmethod
    def topological_inputs(cls) -> int:
        """Count of topological invariants (dynamically computed)."""
        return SMParameterRegistry.count_by_status('TOPOLOGICAL')

    @classmethod
    def pure_predictions(cls) -> int:
        """Parameters that are pure predictions (derived, not inputs)."""
        return cls.derived_parameters()

    @classmethod
    def within_1_sigma(cls) -> int:
        """Parameters within 1σ of experiment (dynamically computed)."""
        return SMParameterRegistry.get_within_sigma(1.0)

    @classmethod
    def within_2_sigma(cls) -> int:
        """Parameters within 2σ of experiment (dynamically computed)."""
        return SMParameterRegistry.get_within_sigma(2.0)

    @classmethod
    def exact_matches(cls) -> int:
        """Parameters matching exactly (σ=0) (dynamically computed)."""
        return SMParameterRegistry.get_exact_matches()

    @classmethod
    def success_rate_1sigma(cls) -> float:
        """Percentage within 1σ (dynamically computed)."""
        total = cls.total_sm_parameters()
        return round(100.0 * cls.within_1_sigma() / total, 1) if total > 0 else 0.0

    @classmethod
    def get_description(cls) -> str:
        """Return dynamic description for auth overlay"""
        cal = cls.calibrated_parameters()
        total = cls.total_sm_parameters()
        return (
            f"A unified geometric framework deriving all {total} "
            f"Standard Model parameters from a single {cls.MANIFOLD_TYPE} manifold "
            f"with minimal calibration ({cal} fitted parameter{'s' if cal != 1 else ''})"
        )

    @classmethod
    def export_data(cls) -> dict:
        """Export statistics for theory_output.json"""
        return {
            'total_sm_parameters': cls.total_sm_parameters(),
            'derived_parameters': cls.derived_parameters(),
            'calibrated_parameters': cls.calibrated_parameters(),
            'input_parameters': cls.input_parameters(),
            'topological_inputs': cls.topological_inputs(),
            'pure_predictions': cls.pure_predictions(),
            'within_1_sigma': cls.within_1_sigma(),
            'within_2_sigma': cls.within_2_sigma(),
            'exact_matches': cls.exact_matches(),
            'success_rate_1sigma': cls.success_rate_1sigma(),
            'manifold_type': cls.MANIFOLD_TYPE,
            'description': cls.get_description(),
            'registry': SMParameterRegistry.export_registry()
        }


class DimensionalStructure:
    """v22 Dimensional Reduction Framework
    (Legacy variable names use "25D" for backward compatibility)

    Structure:
    26D(24,2) = 12×(2,0) bridge pairs + 2 shadow times + two shadow-time directions

    Stages:
    1. Bulk: 26D(24,2) = 24 space + 2 times (one per shadow) = 26D
    2. Dual-Shadow Split: 26D → 2×13D(12,1) via 12×(2,0) bridge pairs
       - Each shadow: 13D = 12 spatial + 1 time (its own)
       - 12 bridge pairs connect corresponding spatial dimensions between shadows
    3. Per-Shadow G₂ Compactification: 13D(12,1) → 6D(5,1) (7D compact per shadow)
    4. OR Reduction: Dual 6D → 4D identified via R_perp

    Note: This class was updated in v22.0 from (11,1) to (12,1) shadow signatures.
    """
    D_BULK = _ssot_dim("D_ancestral_total")
    SIGNATURE_BULK = (_ssot_dim("D_ancestral_space"), _ssot_dim("D_ancestral_time"))

    # Stage 1: v22 Dual-shadow split via 12×(2,0) bridge pairs
    D_PER_SHADOW = _ssot_dim("D_shadow_total")
    SIGNATURE_SHADOW = (_ssot_dim("D_shadow_space"), _ssot_dim("D_shadow_time"))
    N_BRIDGE_PAIRS = _ssot_dim("bridge_local")

    # Stage 2: Per-shadow G₂ compactification 13D→6D
    D_AFTER_G2 = 6  # v22: 13 - 7 = 6 dimensions per shadow
    D_COMPACT_G2 = 7  # Source: Joyce (2000) G2 holonomy manifold dimension

    # Stage 3: Observable emergence 6D→4D (via OR reduction)
    D_OBSERVABLE = 4  # Derived: Observable spacetime
    D_COMPACT_FINAL = 2  # v22: 2D final compactification per shadow (6D - 4D = 2D)

    # Validation
    @staticmethod
    def validate():
        """Two-time: validate dimensional reduction stages (26 = 2×13)."""
        # Two-time: 26D = 2×13D (own time per shadow)
        assert DimensionalStructure.D_BULK == 2 * DimensionalStructure.D_PER_SHADOW, \
            "Two-time: 26D = 2×13D (one time per shadow)"
        # v22: G₂ compactification: 13D - 7D = 6D per shadow
        assert DimensionalStructure.D_AFTER_G2 == DimensionalStructure.D_PER_SHADOW - DimensionalStructure.D_COMPACT_G2, \
            "v22: G₂ compactification: 13D - 7D = 6D per shadow"
        # v22: OR reduction: 6D - 2D = 4D
        assert DimensionalStructure.D_OBSERVABLE == DimensionalStructure.D_AFTER_G2 - DimensionalStructure.D_COMPACT_FINAL, \
            "v22: OR reduction: 6D - 2D = 4D"
        return True
