"""Fermion chirality, EFT validity, G2 spinor geometry and TCS (retired reading) topology parameters.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.

2026-11-11: FermionChiralityParameters.CHI_EFF and N_GENERATIONS are read
from the path in force (``path_valued.PathValued``); the TCS #187 numbers
they were typed from are kept as RETIRED_TCS187_* rows.
"""

from .path_valued import PathValued


# ==============================================================================
# FERMION CHIRALITY & GENERATION COUNT (v13.0)
# ==============================================================================

class FermionChiralityParameters(metaclass=PathValued):
    """
    Fermion chirality and generation count from G₂ topology via Pneuma mechanism.

    Generation count derivation (parameter-free):
    - N_flux = χ_eff/6 = 24 (standard flux quantization)
    - Spinor DOF in 7D = 8 (Spin(7) representation)
    - n_gen = N_flux / spinor_DOF = 24/8 = 3

    Pneuma Chiral Filter Mechanism:
    - Modified Dirac operator: D_eff = γ^μ(∂_μ + igA_μ + γ^5 T_μ)
    - Axial torsion: T_μ ~ ∇_μ⟨Ψ_P⟩ (from Pneuma gradient)
    - Left-handed modes localize on brane
    - Right-handed modes delocalize to UV bulk

    Comparison to Standard Approaches:
    - Intersecting Branes: Singular/Discrete geometry
    - Flux Compactification: Global/Topological G4 flux
    - Pneuma Mechanism: Dynamical/Smooth torsion coupling (our approach)

    References:
    - Kaplan (1992): Domain wall fermions
    - Acharya-Witten (2001): Chiral fermions from G2
    - Joyce (2000): Spinor structures on G2 manifolds
    """

    # CHI_EFF and N_GENERATIONS are read from the path in force at access
    # (metaclass PathValued: chi_eff_route fork and n_gen_source fork).
    # RETIRED reading (TCS G2 manifold #187, CHNP 2015), kept as a record:
    RETIRED_TCS187_CHI_EFF = 144  # 2(h^{1,1} - h^{2,1} + h^{3,1}) = 2(4 - 0 + 68)
    RETIRED_TCS187_N_FLUX = RETIRED_TCS187_CHI_EFF / 6  # chi_eff/6 at TCS #187

    # Spinor structure from Spin(7)
    SPIN7_TOTAL = 8  # Source: dim(8_s) = 8 real spinor components in Spin(7)
    SPIN7_STABILIZED = 7  # Derived: 8 - 1 = 7 components after G2 stabilization
    SPINOR_DOF = SPIN7_TOTAL  # Derived: dim(8_s) = 8

    # RETIRED route: n_gen = N_flux / spinor_DOF at TCS #187 (the b3/dim route)
    RETIRED_TCS187_N_GENERATIONS = int(RETIRED_TCS187_N_FLUX / SPINOR_DOF)

    # Chiral filter strength from spinor stabilization
    CHIRAL_FILTER_STRENGTH = SPIN7_STABILIZED / SPIN7_TOTAL  # Derived: 7/8 = 0.875

    # Modified Dirac operator components
    DIRAC_MODIFICATION = "gamma^5 T_mu (axial torsion coupling)"
    TORSION_SOURCE = "T_mu ~ nabla_mu ⟨Psi_P⟩ (Pneuma gradient)"

    @staticmethod
    def get_fermion_chirality():
        """Return all fermion chirality parameters as dictionary.

        chi_eff and n_generations are those of the path in force; the
        retired TCS #187 route (chi_eff/6/8) is reported under 'retired'.
        """
        from metaphysica.simulations.core.active_path import topology

        topo = topology()
        cls = FermionChiralityParameters
        return {
            'chi_eff': topo.chi_eff,
            'n_flux': topo.chi_eff / 6,
            'spinor_dof': cls.SPINOR_DOF,
            'n_generations': topo.n_gen,
            'n_generations_derived': True,
            'path': topo.path,
            'spin7_total': FermionChiralityParameters.SPIN7_TOTAL,
            'spin7_stabilized': FermionChiralityParameters.SPIN7_STABILIZED,
            'chiral_filter_strength': FermionChiralityParameters.CHIRAL_FILTER_STRENGTH,
            'dirac_modification': FermionChiralityParameters.DIRAC_MODIFICATION,
            'torsion_source': FermionChiralityParameters.TORSION_SOURCE,
            'formula': ('n_gen = b2/4 = %d/4 = %d on path %s; chi_eff = 48 n_gen = %d'
                        % (topo.b2, topo.n_gen, topo.path, topo.chi_eff)),
            'retired': {
                'chi_eff': cls.RETIRED_TCS187_CHI_EFF,
                'n_generations': cls.RETIRED_TCS187_N_GENERATIONS,
                'route': 'TCS #187: n_gen = (chi_eff/6) / 8 (retired)',
            },
            'modified_dirac': 'D_eff = gamma^mu (d_mu + igA_mu + gamma^5 T_mu)',
            'mechanism': 'Pneuma torsion filter (axial coupling)',
            'comparison': {
                'intersecting_branes': 'Singular/Discrete geometry',
                'flux_compactification': 'Global/Topological G4 flux',
                'pneuma_mechanism': 'Dynamical/Smooth torsion coupling'
            },
            'status': 'n_gen from the n_gen_source fork, chi_eff from the chi_eff_route fork'
        }


# ==============================================================================
# EFT VALIDITY & UV COMPLETION (v13.0)
# ==============================================================================

class EFTValidityParameters(metaclass=PathValued):
    """
    EFT validity regime with geometric protection.

    The effective field theory remains valid up to the unification scale due to:
    1. Asymptotic Safety: UV fixed point prevents coupling divergence (Section 3.4.5)
    2. Geometric Suppression: Higher-dimensional operators suppressed by 1/b₃ per level

    Key Result:
    - Standard EFT correction at GUT scale: (E/M_GUT)² ~ O(1)
    - PM geometric correction: (E/M_GUT)² / b₃ ~ 3-4%

    This ensures precision predictions (m_t, m_b, mixing angles) remain valid.

    References:
    - Weinberg (1979): Asymptotic safety proposal
    - Reuter (1998): Non-perturbative fixed point
    - Acharya et al. (2010): G₂ compactification EFT
    """

    # Energy scales
    M_GUT = 2.118e16  # GeV (from GaugeUnificationParameters)
    M_PLANCK = 1.221e19  # GeV (FULL Planck mass; reduced is 2.435e18)

    # Geometric suppression factor from G₂ topology
    # B3 is that of the path in force, read at access (PathValued).
    RETIRED_TCS187_B3 = 24  # b3 = b2(X1) + b2(X2) + K + 1 at TCS #187 (CHNP 2015)

    # Asymptotic Safety parameters
    G_FIXED_POINT = 0.27  # Source: Reuter-Saueressig (2012) asymptotic safety fixed point
    LAMBDA_FIXED_POINT = 0.19  # Dimensionless cosmological constant at fixed point

    @staticmethod
    def standard_eft_correction(E_scale):
        """Standard EFT correction: (E/M_GUT)^(d-4) for dim-6 operator"""
        return (E_scale / EFTValidityParameters.M_GUT)**2

    @staticmethod
    def geometric_correction_dim6(E_scale):
        """Dim-6 correction with geometric suppression: (E/M_GUT)² / b₃"""
        epsilon_sq = (E_scale / EFTValidityParameters.M_GUT)**2
        return epsilon_sq / EFTValidityParameters.B3

    @staticmethod
    def geometric_correction_dim8(E_scale):
        """Dim-8 correction: (E/M_GUT)⁴ / b₃²"""
        epsilon_4 = (E_scale / EFTValidityParameters.M_GUT)**4
        return epsilon_4 / (EFTValidityParameters.B3**2)

    @staticmethod
    def total_uncertainty(E_scale):
        """Total EFT uncertainty envelope at given scale"""
        dim6 = EFTValidityParameters.geometric_correction_dim6(E_scale)
        dim8 = EFTValidityParameters.geometric_correction_dim8(E_scale)
        return dim6 + dim8

    @staticmethod
    def max_uncertainty_at_gut():
        """Maximum correction at unification scale"""
        return EFTValidityParameters.total_uncertainty(EFTValidityParameters.M_GUT)

    @staticmethod
    def is_valid(E_scale, threshold=0.1):
        """Check if EFT is valid (corrections < threshold)"""
        return EFTValidityParameters.total_uncertainty(E_scale) < threshold

    @staticmethod
    def get_eft_validity():
        """Return EFT validity parameters as dictionary"""
        M_GUT = EFTValidityParameters.M_GUT
        return {
            'M_GUT': M_GUT,
            'b3': EFTValidityParameters.B3,
            'dim6_at_gut': EFTValidityParameters.geometric_correction_dim6(M_GUT),
            'dim8_at_gut': EFTValidityParameters.geometric_correction_dim8(M_GUT),
            'total_at_gut': EFTValidityParameters.total_uncertainty(M_GUT),
            'total_percent': EFTValidityParameters.total_uncertainty(M_GUT) * 100,
            'g_fixed_point': EFTValidityParameters.G_FIXED_POINT,
            'as_uv_completion': True,
            'geometric_suppression': f'1/b₃ = 1/{EFTValidityParameters.B3}',
            'status': 'VALID - Precision protected by AS + geometric suppression'
        }


# ==============================================================================
# G2 SPINOR GEOMETRY PARAMETERS (v13.0)
# ==============================================================================

class G2SpinorGeometryParameters(metaclass=PathValued):
    """
    Parameters for G2 spinor geometry validation.

    The Pneuma condensate provides the invariant spinor eta that defines
    G2 holonomy. The associative 3-form phi is constructed via canonical
    spinor-to-form mappings: phi_{mnp} ~ eta_bar Gamma_{mnp} eta.

    References:
    - Joyce (2000): Compact Manifolds with Special Holonomy
    - Acharya & Witten (2001): G2 moduli and spinor bundles
    """

    # Topological parameters (from TopologicalDerivations)
    # CHI_EFF and B3 are those of the path in force, read at access.
    RETIRED_TCS187_CHI_EFF = 144  # 2(h^{1,1} - h^{2,1} + h^{3,1}) = 2(4 - 0 + 68)
    RETIRED_TCS187_B3 = 24  # b3 = b2(X1) + b2(X2) + K + 1 (CHNP 2015)

    # Spinor representation theory
    SPINOR_DOF_7D = 8  # Source: dim(8_s) = 8 real spinor components (Spin(7) -> G2)
    INVARIANT_SPINORS = 1  # Source: Joyce (2000) G2 holonomy fixes exactly one covariantly constant spinor

    # Derived quantities
    @staticmethod
    def active_components():
        """Components that source geometry/torsion = 7"""
        return G2SpinorGeometryParameters.SPINOR_DOF_7D - G2SpinorGeometryParameters.INVARIANT_SPINORS

    @staticmethod
    def spinor_fraction():
        """7/8 = 0.875 - the fraction sourcing torsion"""
        return G2SpinorGeometryParameters.active_components() / G2SpinorGeometryParameters.SPINOR_DOF_7D

    @staticmethod
    def n_flux():
        """N_flux = chi_eff / 6 of the path in force"""
        return G2SpinorGeometryParameters.CHI_EFF / 6.0

    @staticmethod
    def T_topological():
        """TCS #187 only: -b3/N_flux = -24/(144/6) = -1.0 at the retired reading.

        Not re-derived on any other path: -b3/N_flux at the live b3 (e.g.
        -43/24) is a number nobody derived, so the retired records are used.
        Agrees with TorsionClass.T_TOPOLOGICAL.
        """
        cls = G2SpinorGeometryParameters
        return -cls.RETIRED_TCS187_B3 / (cls.RETIRED_TCS187_CHI_EFF / 6.0)

    @staticmethod
    def T_omega_spinor():
        """TCS #187 only: T_topological x 7/8 = -0.875 (TorsionClass.T_OMEGA)."""
        return G2SpinorGeometryParameters.T_topological() * G2SpinorGeometryParameters.spinor_fraction()

    @staticmethod
    def vielbein_dof():
        """Frame field DOF constrained by G2 = 14 (dim G2)"""
        return 14  # G2 Lie algebra dimension

    @staticmethod
    def export_data():
        """Export data for theory_output.json"""
        return {
            'chi_eff': G2SpinorGeometryParameters.CHI_EFF,
            'b3': G2SpinorGeometryParameters.B3,
            'spinor_dof_7d': G2SpinorGeometryParameters.SPINOR_DOF_7D,
            'invariant_spinors': G2SpinorGeometryParameters.INVARIANT_SPINORS,
            'active_components': G2SpinorGeometryParameters.active_components(),
            'spinor_fraction': G2SpinorGeometryParameters.spinor_fraction(),
            'spinor_fraction_formula': '7/8 (active/total spinor DOF)',
            'n_flux': G2SpinorGeometryParameters.n_flux(),
            'T_topological_tcs187': G2SpinorGeometryParameters.T_topological(),
            'T_omega_tcs187': G2SpinorGeometryParameters.T_omega_spinor(),
            'torsion_status': ('RETIRED - T_topological and T_omega are the '
                               'TCS #187 reading (b3 = 24, N_flux = 24); not '
                               're-derived on the path in force'),
            'vielbein_dof': G2SpinorGeometryParameters.vielbein_dof(),
            'geometry_mechanism': 'phi_{mnp} ~ eta_bar Gamma_{mnp} eta (Joyce 2000)',
            'pneuma_role': 'Provides invariant spinor eta after dimensional reduction',
            'signature_protection': 'Sp(2,R) gauge fixing',
            'status': 'ANSATZ - geometry from canonical G2 spinor bilinears (mechanism stated, torsion not derived on the path)'
        }


# ==============================================================================
# TCS (retired reading) G₂ MANIFOLD TOPOLOGY PARAMETERS (v13.0)
# ==============================================================================

class TCSTopologyParameters(metaclass=PathValued):
    """
    TCS G₂ Manifold #187 Topology (Corti-Haskins-Nordström-Pacini 2015)

    The Twisted Connected Sum construction yields a compact G₂ manifold
    with explicit Betti numbers from the gluing of two K3-fibred CY3s.

    Gluing formula: b₃ = b₂(X₁) + b₂(X₂) + K + 1

    References:
    - Corti, Haskins, Nordström, Pacini (2015): "G2-manifolds and associative
      submanifolds via semi-Fano 3-folds", Duke Math. J. 164(10)
    - CHNP (2018): "Asymptotically cylindrical Calabi-Yau 3-folds from weak
      Fano 3-folds", Geom. Topol. 17(4)
    """

    # Primary topology: CHI_EFF, B2 and B3 are those of the path in force,
    # read at access (PathValued). RETIRED record of manifold #187:
    RETIRED_TCS187_CHI_EFF = 144  # 2(h^{1,1} - h^{2,1} + h^{3,1}) = 2(4 - 0 + 68)
    RETIRED_TCS187_B2 = 4  # h^{1,1} = 4 (CHNP 2015)
    RETIRED_TCS187_B3 = 24  # b3 = b2(X1) + b2(X2) + K + 1 (CHNP 2015)
    K_MATCHING = 4  # Source: CHNP 2015 - four matching K3 fibres (calibrated at the retired TCS seed; not re-derived on Y7)

    # Hodge numbers of the retired manifold #187
    RETIRED_TCS187_HODGE_H11 = 4  # CHNP 2015 h^{1,1} = 4 Kahler moduli
    RETIRED_TCS187_HODGE_H21 = 0  # G2 manifolds have no complex structure moduli
    RETIRED_TCS187_HODGE_H31 = 68  # CHNP 2015 h^{3,1} = 68 associative 3-cycle moduli

    # Derived quantities
    @staticmethod
    def n_flux():
        """N_flux = chi_eff / 6 of the path in force"""
        return TCSTopologyParameters.CHI_EFF / 6

    @staticmethod
    def export_data():
        """Export data for theory_output.json"""
        return {
            'chi_eff': TCSTopologyParameters.CHI_EFF,
            'b2': TCSTopologyParameters.B2,
            'b3': TCSTopologyParameters.B3,
            'k_matching': TCSTopologyParameters.K_MATCHING,
            'n_flux': TCSTopologyParameters.n_flux(),
            'retired_tcs187': {
                'chi_eff': TCSTopologyParameters.RETIRED_TCS187_CHI_EFF,
                'b2': TCSTopologyParameters.RETIRED_TCS187_B2,
                'b3': TCSTopologyParameters.RETIRED_TCS187_B3,
                'hodge_h11': TCSTopologyParameters.RETIRED_TCS187_HODGE_H11,
                'hodge_h21': TCSTopologyParameters.RETIRED_TCS187_HODGE_H21,
                'hodge_h31': TCSTopologyParameters.RETIRED_TCS187_HODGE_H31,
                'gluing_formula': ('b₃ = b₂(X₁) + b₂(X₂) + K + 1 = %d (retired)'
                                   % TCSTopologyParameters.RETIRED_TCS187_B3),
            },
            'manifold_id': '#187 (CHNP 2015)',
            'construction': 'Twisted Connected Sum of K3-fibred CY3s',
            'literature': 'Corti-Haskins-Nordström-Pacini, Duke Math. J. 164(10) 2015',
            'status': 'EXPLICIT - Complete topological data from TCS (retired reading) construction'
        }
