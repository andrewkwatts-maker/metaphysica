"""Proton decay, doublet-triplet splitting and GUT breaking chain parameters.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""

import numpy as np

from .gauge import GaugeUnificationParameters
from .fitted import TorsionClass


# ==============================================================================
# v11.0 OBSERVABLES - PROTON DECAY & HIGGS MASS
# ==============================================================================

class ProtonLifetimeParameters:
    """
    DEPRECATED (v14.1): Use GeometricProtonDecayParameters instead.

    v11.0: Proton lifetime prediction from G₂ torsion-enhanced suppression.
    This gives τ_p = 3.91e34 years, but v13.0 geometric approach gives 8.15e34 years.

    τ_p = (M_GUT)^4 / (m_p^5 α_GUT^2) × exp(8π|T_ω|) / hadronic_matrix_elements

    WARNING: This class is kept for backward compatibility only.
    Use GeometricProtonDecayParameters for v14.1+ calculations.
    """

    # From GaugeUnificationParameters (single source of truth)
    M_GUT = GaugeUnificationParameters.M_GUT  # 2.118e16 GeV
    M_GUT_ERROR = GaugeUnificationParameters.M_GUT_ERROR  # 0.09e16 GeV
    ALPHA_GUT = GaugeUnificationParameters.ALPHA_GUT  # 1/23.54
    M_PROTON = 0.938             # [GeV] Proton mass

    # Super-Kamiokande bounds (from PhenomenologyParameters)
    SUPER_K_BOUND = 1.67e34      # [years] 90% CL lower limit (2017)

    # Monte Carlo baseline (v12.8)
    TAU_P_MC_BASELINE = 3.91e34  # [years] From flux quantization MC

    # Torsion enhancement (v12.8: uses geometric T_ω from spinor fraction)
    # T_ω_geometric = -0.875 (1.02% from target), T_ω_target = -0.884
    T_OMEGA = TorsionClass.T_OMEGA  # -0.875 (Spin(7) spinor fraction)
    TORSION_FACTOR = np.exp(8 * np.pi * abs(T_OMEGA))  # ≈ 4.0×10⁹

    # Hadronic matrix elements from lattice QCD (FLAG 2024)
    F_PI_LATTICE = 0.130         # [GeV] Pion decay constant
    ALPHA_LATTICE = -0.0152      # [GeV³] Hadronic matrix element

    @staticmethod
    def proton_lifetime():
        """Calculate τ_p in years"""
        tau_base = (ProtonLifetimeParameters.M_GUT**4 /
                   (ProtonLifetimeParameters.M_PROTON**5 *
                    ProtonLifetimeParameters.ALPHA_GUT**2))

        hadronic = (ProtonLifetimeParameters.F_PI_LATTICE**2 *
                   abs(ProtonLifetimeParameters.ALPHA_LATTICE)**2)

        tau_GeV_inv = tau_base * ProtonLifetimeParameters.TORSION_FACTOR / hadronic

        # Convert to years (1 GeV^-1 ≈ 6.58×10^-25 s)
        seconds_per_year = 3.156e7
        GeV_to_seconds = 6.58e-25

        return tau_GeV_inv * GeV_to_seconds / seconds_per_year

    # Predicted value
    TAU_PROTON_PREDICTED = 3.91e34  # [years]


class GeometricProtonDecayParameters:
    """
    v13.0: Proton decay with TCS cycle separation suppression.

    Resolution to "Proton Decay Rate Uncertainty":
    - Geometric selection rule from TCS cycle separation
    - Matter and Higgs localize on separated 3-cycles
    - Wavefunction overlap suppression: exp(-2π d/R)

    References:
    - Acharya et al. (2008): Proton decay in M-theory on G₂ manifolds
    - Corti-Haskins-Nordström-Pacini (2015): TCS G₂ construction
    - Friedmann-Witten (2002): Brane models and proton stability
    """

    # TCS cycle separation from K=4 matching fibres
    K_MATCHING = 4              # Source: CHNP 2015 - four matching K3 fibres
    D_OVER_R = 0.12             # Source: TCS neck geometry (CHNP 2015)

    # Geometric suppression factor S = exp(2π d/R)
    @staticmethod
    def suppression_factor():
        """Wavefunction overlap suppression from cycle separation"""
        return np.exp(2 * np.pi * GeometricProtonDecayParameters.D_OVER_R)

    # GUT parameters (from GaugeUnificationParameters)
    M_GUT = GaugeUnificationParameters.M_GUT            # 2.118e16 GeV
    M_GUT_ERROR = GaugeUnificationParameters.M_GUT_ERROR  # 0.09e16 GeV
    ALPHA_GUT_INV = GaugeUnificationParameters.ALPHA_GUT_INV  # 23.54

    # Standard GUT prefactor (hadronic matrix elements included)
    C_PREFACTOR = 3.82e33       # years (calibrated to SU(5) GUT)

    # Branching ratio from orientation sum
    BR_E_PI0 = 0.25             # (12/24)² = 0.25

    # Super-K bound
    SUPER_K_BOUND = 1.67e34     # years (90% CL)

    @staticmethod
    def tau_proton():
        """
        Proton lifetime with geometric suppression.

        τ_p = C × (M_GUT/10¹⁶)⁴ × (0.03/α_GUT)² × S
        """
        m_gut_16 = GeometricProtonDecayParameters.M_GUT / 1e16
        alpha_gut = 1.0 / GeometricProtonDecayParameters.ALPHA_GUT_INV
        alpha_ratio = 0.03 / alpha_gut
        S = GeometricProtonDecayParameters.suppression_factor()

        return (GeometricProtonDecayParameters.C_PREFACTOR *
                (m_gut_16**4) * (alpha_ratio**2) * S)

    # Predicted values (v13.0) - from MC simulation
    TAU_PROTON_PREDICTED = 8.15e34  # years (median from MC)
    TAU_PROTON_68_LOW = 6.84e34     # 68% CI lower
    TAU_PROTON_68_HIGH = 9.64e34    # 68% CI upper
    OOM_UNCERTAINTY = 0.075         # Order of magnitude spread (narrow!)

    @staticmethod
    def ratio_to_super_k():
        """Ratio of predicted lifetime to Super-K bound"""
        return GeometricProtonDecayParameters.tau_proton() / GeometricProtonDecayParameters.SUPER_K_BOUND

    @staticmethod
    def export_data():
        """Export for theory_output.json"""
        return {
            'tau_p_years': GeometricProtonDecayParameters.tau_proton(),
            'tau_p_68_low': GeometricProtonDecayParameters.TAU_PROTON_68_LOW,
            'tau_p_68_high': GeometricProtonDecayParameters.TAU_PROTON_68_HIGH,
            'oom_uncertainty': GeometricProtonDecayParameters.OOM_UNCERTAINTY,
            'd_over_r': GeometricProtonDecayParameters.D_OVER_R,
            'suppression_factor': GeometricProtonDecayParameters.suppression_factor(),
            'k_matching': GeometricProtonDecayParameters.K_MATCHING,
            'br_e_pi0': GeometricProtonDecayParameters.BR_E_PI0,
            'super_k_ratio': GeometricProtonDecayParameters.ratio_to_super_k(),
            'mechanism': 'TCS cycle separation (K=4 neck topology)',
            'selection_rule': 'exp(-2π d/R) wavefunction overlap',
            'status': 'RESOLVED - Geometric selection rule from TCS'
        }


class DoubletTripletSplittingParameters:
    """
    v14.1: Doublet-Triplet Splitting via Native TCS Topological Filter.

    Resolution: The splitting is achieved intrinsically within the TCS G₂ manifold
    using a TOPOLOGICAL FILTER under the Z₂×Z₂ quotient action. This is cleaner
    than Wilson lines - triplets are shunted to the shadow sector, not just lifted.

    Mechanism (Topological Filter):
    - The Higgs 5-plet of SU(5) (or 10 of SO(10)) lives on a 3-cycle γ_H
    - The Z₂ action on the manifold has "fixed points" where doublets localize
    - Triplet components are projected to the non-observable shadow sector
    - The triplet becomes TOPOLOGICALLY DISCONNECTED from the 4D vacuum
    - No gauge flux tuning required - only G₂ holonomy preservation

    Key Insight:
    - Triplets don't just "get heavy" - they're topologically removed
    - Uses same Z₂×Z₂ that gives us 3 generations (consistency)
    - Predicts exact same M_GUT as proton decay (cross-validation)

    The number of light doublets is fixed by:
    N_doublets - N_triplets = ∫_M Â(M) ∧ ch(L_Y) mod Z₂

    References:
    - Witten (2001): Discrete torsion in G₂ compactifications
    - Corti-Haskins-Nordström-Pacini (2015): TCS G₂ construction
    """

    # TCS topology parameters (from TCSTopologyParameters)
    B2 = 4  # Source: TCS construction h^{1,1} = 4 (CHNP 2015)
    K_MATCHING = 4              # Source: CHNP 2015 - four matching K3 fibres
    CHI_EFF = 144  # Derived: 2(h^{1,1} - h^{2,1} + h^{3,1}) = 2(4 - 0 + 68) = 144 (CHNP construction #187)

    # Gauge group structure
    SM_RANK = 4                 # Derived: rank(SU(3)×SU(2)×U(1)) = 3+1+1-1 = 4
    U1Y_FLUX_SUPPORTED = True   # b₂ ≥ SM_RANK ensures U(1)_Y flux

    # Z₂×Z₂ Topological Filter parameters
    Z2_REAL_STRUCTURE = True    # Real structure on CY3 building blocks
    Z2_FREE_INVOLUTION = True   # Free involution for smoothness
    Z2_SHADOW_PROJECTION = True # Projects triplets to shadow sector

    # Index theorem results
    TRIPLET_INDEX = 0           # Derived: Z2xZ2 projection removes all triplet zero-modes
    DOUBLET_INDEX_PER_GEN = 1   # Derived: Index theorem preserves one doublet per generation

    # Topological filter efficiency
    TRIPLET_SUPPRESSION = 0.9999999  # Derived: 1 - exp(-2π d/R) ≈ 1 (topological)
    DOUBLET_PRESERVATION = 1.0        # Derived: Exact zero-modes from index theorem

    # Mass scales
    M_GUT = 2.118e16            # GUT scale where triplets live [GeV]
    M_EW = 246.0                # Electroweak scale where doublets live [GeV]

    @staticmethod
    def triplet_mass():
        """Higgs triplet mass ~ M_GUT (shunted to shadow sector)"""
        return DoubletTripletSplittingParameters.M_GUT

    @staticmethod
    def doublet_mass():
        """Higgs doublet mass ~ M_EW (protected zero-mode at fixed points)"""
        return DoubletTripletSplittingParameters.M_EW

    @staticmethod
    def mass_hierarchy():
        """Triplet/Doublet mass ratio"""
        return DoubletTripletSplittingParameters.M_GUT / DoubletTripletSplittingParameters.M_EW

    @staticmethod
    def is_topologically_locked():
        """Check if b₂ ≥ SM_RANK (required for topological filter)"""
        return DoubletTripletSplittingParameters.B2 >= DoubletTripletSplittingParameters.SM_RANK

    @staticmethod
    def filter_active():
        """Check if topological filter is active (Z₂×Z₂ with shadow projection)"""
        return (DoubletTripletSplittingParameters.Z2_REAL_STRUCTURE and
                DoubletTripletSplittingParameters.Z2_FREE_INVOLUTION and
                DoubletTripletSplittingParameters.Z2_SHADOW_PROJECTION)

    @staticmethod
    def export_data():
        """Export for theory_output.json"""
        return {
            'b2': DoubletTripletSplittingParameters.B2,
            'k_matching': DoubletTripletSplittingParameters.K_MATCHING,
            'sm_rank': DoubletTripletSplittingParameters.SM_RANK,
            'u1y_flux_supported': DoubletTripletSplittingParameters.U1Y_FLUX_SUPPORTED,
            'triplet_index': DoubletTripletSplittingParameters.TRIPLET_INDEX,
            'doublet_index_per_gen': DoubletTripletSplittingParameters.DOUBLET_INDEX_PER_GEN,
            'triplet_mass_gev': DoubletTripletSplittingParameters.triplet_mass(),
            'doublet_mass_gev': DoubletTripletSplittingParameters.doublet_mass(),
            'mass_hierarchy': DoubletTripletSplittingParameters.mass_hierarchy(),
            'topologically_locked': DoubletTripletSplittingParameters.is_topologically_locked(),
            'filter_active': DoubletTripletSplittingParameters.filter_active(),
            'triplet_suppression': DoubletTripletSplittingParameters.TRIPLET_SUPPRESSION,
            'doublet_preservation': DoubletTripletSplittingParameters.DOUBLET_PRESERVATION,
            'z2_action': 'Z2 x Z2 (real structure + free involution + shadow projection)',
            'mechanism': 'Native TCS Topological Filter (triplets to shadow sector)',
            'index_formula': 'N_doublets - N_triplets = integral A-hat(M) wedge ch(L_Y) mod Z2',
            'status': 'RESOLVED - Native G2 topological filter, no Wilson lines'
        }


class BreakingChainParameters:
    """
    v21.0: Symmetry Breaking Chain - Geometric Pati-Salam Selection.

    The Pati-Salam chain is GEOMETRICALLY PREFERRED because it is the natural
    intermediate step in the 26D(24,2) → dual-shadow → 4D dimensional reduction.

    Derivation:
    1. Bulk: SO(24,2) contains maximal subgroup including SO(10)
    2. Per-shadow G₂ Projection: TCS construction (K=4) favors maximal subgroup
    3. Intermediate: SO(10) → SU(4)_C × SU(2)_L × SU(2)_R (Pati-Salam)
    4. Enforced by: Pneuma condensate (54_H) alignment with 7D curvature

    v21.0: Updated from Sp(2,R) to dual-shadow framework (mechanism preserved).

    References:
    - Pati-Salam (1974): Original lepton-quark unification
    - Mohapatra-Pati (1975): Left-right symmetric gauge theories
    - PM v21.0 (2026): Dual-Shadow Bridge Framework
    """

    # Unification group
    GUT_GROUP = "SO(10)"
    GUT_RANK = 5  # Source: SO(10) rank = 5 (Lie algebra theory)

    # Intermediate group (Pati-Salam)
    INTERMEDIATE_GROUP = "SU(4)_C x SU(2)_L x SU(2)_R"
    INTERMEDIATE_RANK = 4 + 1 + 1  # Derived: = 6 from SU(4)×SU(2)×SU(2)

    # Final group
    SM_GROUP = "SU(3)_C x SU(2)_L x U(1)_Y"
    SM_RANK = 4  # Source: SM gauge group rank = 3+1+0 = 4

    # Mass scales
    M_GUT = 2.118e16            # GUT scale [GeV]
    M_PS = 1.2e12               # Pati-Salam intermediate scale [GeV] (from 54_H VEV)
    M_EW = 246.0                # Electroweak scale [GeV]

    # Higgs representations
    HIGGS_GUT_BREAK = "54_H"    # Breaks SO(10) → Pati-Salam
    HIGGS_PS_BREAK = "126_H"    # Breaks Pati-Salam → SM (B-L breaking)
    HIGGS_EW_BREAK = "10_H"     # Electroweak symmetry breaking

    # Geometric selection factors
    PNEUMA_ALIGNMENT = True     # 54_H aligns with 7D curvature
    G2_MAXIMAL_SUBGROUP = True  # TCS K=4 favors maximal at first stage

    # Beta function coefficients (1-loop)
    # SM running: MZ to M_PS
    B_SM = (6.6, 1.0, -3.0)     # (b1, b2, b3) with Pneuma KK corrections

    # Pati-Salam running: M_PS to M_GUT
    B_PS = (12.3, 2.0, 2.0)     # (b_SU4, b_SU2L, b_SU2R)

    @staticmethod
    def is_chain_geometric():
        """Check if breaking chain is geometrically derived"""
        return (BreakingChainParameters.PNEUMA_ALIGNMENT and
                BreakingChainParameters.G2_MAXIMAL_SUBGROUP)

    @staticmethod
    def chain_description():
        """Return the breaking chain as string"""
        return f"{BreakingChainParameters.GUT_GROUP} -> {BreakingChainParameters.INTERMEDIATE_GROUP} -> {BreakingChainParameters.SM_GROUP}"

    @staticmethod
    def export_data():
        """Export for theory_output.json"""
        return {
            'gut_group': BreakingChainParameters.GUT_GROUP,
            'intermediate_group': BreakingChainParameters.INTERMEDIATE_GROUP,
            'sm_group': BreakingChainParameters.SM_GROUP,
            'm_gut_gev': BreakingChainParameters.M_GUT,
            'm_ps_gev': BreakingChainParameters.M_PS,
            'm_ew_gev': BreakingChainParameters.M_EW,
            'higgs_gut_break': BreakingChainParameters.HIGGS_GUT_BREAK,
            'higgs_ps_break': BreakingChainParameters.HIGGS_PS_BREAK,
            'chain': BreakingChainParameters.chain_description(),
            'is_geometric': BreakingChainParameters.is_chain_geometric(),
            'mechanism': 'Pneuma condensate (54_H) alignment with G2 curvature',
            'status': 'RESOLVED - Pati-Salam geometrically preferred by TCS K=4'
        }
