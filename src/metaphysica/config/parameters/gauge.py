"""Gauge unification and heavy X,Y gauge boson parameters.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""

import numpy as np


# ==============================================================================
# GAUGE UNIFICATION
# ==============================================================================

class GaugeUnificationParameters:
    """
    Grand Unification parameters for SO(10) GUT.
    """

    # GUT Scale (Geometric Derivation from TCS G2)
    M_GUT = 2.118e16            # [GeV] Geometric derivation (was 1.8e16)
    M_GUT_ERROR = 0.09e16       # [GeV] From b3 flux variations (5%)
    ALPHA_GUT = 1/23.54         # Derived: 1/α_GUT from 3-loop RG + threshold corrections
    ALPHA_GUT_INV = 23.54       # Source: Georgi-Quinn-Weinberg 1974 + 3-loop precision

    # SO(10) Group Theory
    C_A_SO10_ADJOINT = 9        # Quadratic Casimir for adjoint (45)
    DIM_ADJOINT = 45            # Dimension of SO(10) adjoint representation
    DIM_SPINOR = 16             # Dimension of SO(10) spinor representation
    BETA_PREFACTOR = 1/(16*np.pi**2)  # RG beta function normalization

    # Yukawa Couplings (order of magnitude)
    F_IJ_MIN = 0.01             # Minimum Yukawa matrix element
    F_IJ_MAX = 1.0              # Maximum Yukawa matrix element

    # Seesaw Scale
    M_RH_NEUTRINO_SCALE = 1e14  # [GeV] Right-handed Majorana mass from ⟨126_H⟩


# ==============================================================================
# X,Y HEAVY GAUGE BOSONS (SO(10))
# ==============================================================================

class XYGaugeBosonParameters:
    """
    SO(10) heavy gauge bosons (X and Y particles).
    These mediate proton decay and are predicted but not yet observed.

    GEOMETRICALLY CONSTRAINED:
    - Masses from M_GUT (TCS torsion logarithms)
    - Coupling from alpha_GUT (3-loop RG)
    - Charges from SO(10) representation theory

    THEORETICAL ESTIMATES:
    - Lifetimes from decay width calculations
    - Branching ratios require full Yukawa matrix
    """

    # Masses (Geometrically Derived from M_GUT)
    M_X = GaugeUnificationParameters.M_GUT      # [GeV] X boson mass = M_GUT
    M_Y = GaugeUnificationParameters.M_GUT      # [GeV] Y boson mass = M_GUT (assume degeneracy)
    M_X_ERROR = GaugeUnificationParameters.M_GUT_ERROR  # [GeV] From TCS flux variations
    M_Y_ERROR = GaugeUnificationParameters.M_GUT_ERROR  # [GeV] Same uncertainty

    # Couplings (from Gauge Unification)
    ALPHA_GUT = GaugeUnificationParameters.ALPHA_GUT    # Fine structure at M_GUT
    ALPHA_GUT_INV = GaugeUnificationParameters.ALPHA_GUT_INV  # 23.54

    # Electric Charges (SO(10) Representation Theory - FIXED)
    CHARGE_X = 4/3  # e (X boson charge)
    CHARGE_Y = 1/3  # e (Y boson charge)

    # Quantum Numbers (SO(10) Group Structure - FIXED)
    SPIN = 1                # Vector boson
    B_VIOLATING = True      # Violates baryon number
    L_VIOLATING = True      # Violates lepton number

    # SO(10) Gauge Boson Counting (Group Theory - FIXED)
    N_TOTAL_BOSONS = 45     # Total SO(10) adjoint representation
    N_SM_BOSONS = 12        # Standard Model: 8 gluons + 3 W + 1 photon
    N_X_BOSONS = 12         # X-type bosons (charge ±4/3)
    N_Y_BOSONS = 12         # Y-type bosons (charge ±1/3)
    N_NEUTRAL_HEAVY = 9     # Heavy neutral bosons (Z', W'' cousins)

    # Lifetimes (Theoretical Estimate)
    @staticmethod
    def lifetime_estimate():
        """
        τ ~ ℏ/Γ ~ ℏ/M_GUT (order of magnitude)
        Returns: lifetime in seconds
        """
        import scipy.constants as const
        hbar_GeV_s = const.hbar / const.e / 1e9  # Convert J·s to GeV·s
        return hbar_GeV_s / XYGaugeBosonParameters.M_X  # ~10^-41 seconds

    # Branching Ratios (Currently Unknown - Need Full Yukawa Calculation)
    # These would come from wavefunction overlaps on G₂ associative cycles
    BR_UNKNOWN = True       # Flag indicating BRs not yet calculated

    # Decay Channels (Qualitative)
    # X bosons: u + ū, u + e⁺, d + νₑ
    # Y bosons: d + d̄, d + νₑ, u + e⁻
    # Exact branching ratios require Yukawa matrix diagonalization
