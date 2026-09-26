"""Legacy flat configuration dictionary.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""

from .constants import FundamentalConstants
from .settings import ComputationalSettings
from .parameters.phenomenology import PhenomenologyParameters
from .parameters.bridge import BridgePhysicsParameters
from .parameters.moduli import ModuliParameters
from .parameters.cosmology import CMBBubbleParameters, FRTTauParameters, LandscapeParameters, ThermalTimeParameters, V61Predictions
from .parameters.gauge import GaugeUnificationParameters
from .parameters.neutrino import NeutrinoParameters


# ==============================================================================
# CONFIGURATION DICTIONARY (LEGACY COMPATIBILITY)
# ==============================================================================

def get_config_dict():
    """
    Returns a dictionary with all configuration values (EXTENDED v6.1).
    For backward compatibility with SimulateTheory.py

    Now includes 180+ parameters (up from original ~90)
    """
    return {
        # Dimensional structure
        'D_bulk': FundamentalConstants.D_BULK,
        'internal_dims': FundamentalConstants.D_INTERNAL,
        'branes': FundamentalConstants.N_BRANES,
        'spatial_dims': FundamentalConstants.SPATIAL_DIMS,
        'time_dims': FundamentalConstants.TIME_DIMS,

        # Topology
        'h_11': FundamentalConstants.HODGE_H11,
        'h_21': FundamentalConstants.HODGE_H21,
        'h_31': FundamentalConstants.HODGE_H31,
        'flux_reduce': FundamentalConstants.FLUX_REDUCTION,
        'bridge_dofs': FundamentalConstants.BRIDGE_DOFS,  # v21: was gauging_dofs
        'mirroring': FundamentalConstants.MIRRORING_FACTOR,

        # Fundamental scales
        'M_Pl': PhenomenologyParameters.M_PLANCK,
        'M_star': PhenomenologyParameters.M_STAR,
        'tau_p': PhenomenologyParameters.TAU_PROTON,

        # GW dispersion (v21: Bridge physics)
        'xi': BridgePhysicsParameters.XI_QUADRATIC,
        'g': BridgePhysicsParameters.G_COUPLING,
        'E_F': BridgePhysicsParameters.E_FERMI,
        'Delta_t_bridge': BridgePhysicsParameters.DELTA_T_ORTHO,  # v21: bridge parameter
        'k_LISA': BridgePhysicsParameters.K_LISA_DEFAULT,

        # Dark energy
        'w_0_num': PhenomenologyParameters.W0_NUMERATOR,
        'w_0_denom': PhenomenologyParameters.W0_DENOMINATOR,
        'w_a': PhenomenologyParameters.WA_EVOLUTION,

        # ==================== v6.1 NEW PARAMETERS ====================

        # v6.1 Predictions
        'm_KK': V61Predictions.M_KK_CENTRAL,
        'm_KK_min': V61Predictions.M_KK_MIN,
        'm_KK_max': V61Predictions.M_KK_MAX,
        'eta_boosted': V61Predictions.ETA_BOOSTED,
        'c_mu_nu': V61Predictions.C_MU_NU_FERMION,
        'delta_ortho': V61Predictions.CHSH_DELTA_ORTHO,
        'Delta_N_eff': V61Predictions.DELTA_N_EFF_CENTRAL,

        # F(R,T,τ) Coefficients
        'alpha_F': FRTTauParameters.ALPHA_R_SQUARED,
        'beta_F': FRTTauParameters.BETA_MATTER,
        'gamma_F': FRTTauParameters.GAMMA_MIXED,
        'delta_F': FRTTauParameters.DELTA_BRIDGE_TIME,  # v21: was DELTA_ORTHO_TIME

        # Thermal Time
        'alpha_T': ThermalTimeParameters.ALPHA_T_CANONICAL,
        'alpha_T_z0': ThermalTimeParameters.ALPHA_T_Z0,
        'alpha_T_high_z': ThermalTimeParameters.ALPHA_T_HIGH_Z,

        # Gauge Unification
        'M_GUT': GaugeUnificationParameters.M_GUT,
        'alpha_GUT': GaugeUnificationParameters.ALPHA_GUT,

        # Neutrino Sector
        'Hierarchy': NeutrinoParameters.HIERARCHY_PREDICTION,
        'Sum_m_nu': NeutrinoParameters.SUM_M_NU,

        # CMB Bubble Parameters
        'sigma_CMB': CMBBubbleParameters.SIGMA_CMB_RMS,
        'theta_spot': CMBBubbleParameters.THETA_SPOT_RAD,
        'f_NL': CMBBubbleParameters.F_NL_BUBBLE,

        # Moduli stabilization
        'lambda_coupling': ModuliParameters.LAMBDA_COUPLING,
        'F_term': ModuliParameters.F_TERM_NORMALIZED,
        'kappa': ModuliParameters.KAPPA_UPLIFT,
        's_instanton_norm': ModuliParameters.S_INSTANTON_NORM,
        'mu_periodic': ModuliParameters.MU_PERIODIC,
        'R_bridge': BridgePhysicsParameters.R_ORTHO,  # v21: bridge radius
        'phi_example': ModuliParameters.PHI_EXAMPLE,

        # Condensate
        'v_vev': ModuliParameters.V_VEV,
        'bridge_param_norm': ModuliParameters.BRIDGE_PARAM_NORMALIZED,  # v21
        'theta_mirror': BridgePhysicsParameters.THETA_MIRROR_DEFAULT,
        'theta_45': BridgePhysicsParameters.THETA_EXAMPLE_45DEG,

        # Landscape
        'N_vac_exp': LandscapeParameters.N_VAC_EXPONENT,
        'sigma_tension': LandscapeParameters.SIGMA_TENSION,
        'Delta_V_multiverse': LandscapeParameters.DELTA_V_MULTIVERSE,

        # Computational
        'N_qutip': ComputationalSettings.N_QUTIP_HILBERT,
        'time_start': ComputationalSettings.TIME_START,
        'time_end': ComputationalSettings.TIME_END,
        'tolerance': ComputationalSettings.TOLERANCE_UNITARITY,
        'a_limit_exp': ComputationalSettings.A_LIMIT_EXPONENT,
    }
