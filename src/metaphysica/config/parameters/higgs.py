"""Higgs mass parameters (phenomenological input constraining Re(T)).

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""

import numpy as np


class HiggsMassParameters:
    """
    v24.2: Higgs mass — THREE COMPETING Re(T) VALUES (OPEN PROBLEM)

    The Higgs mass formula m_h² = 8π² v² (λ₀ - κ Re(T) y_t²) connects
    the Higgs mass to the Kähler modulus Re(T). Three values exist:

    1. RE_T_ATTRACTOR = 1.833  (GEOMETRIC — from TCS #187 attractor mechanism)
       → Gives m_h ≈ 414 GeV (FAILS experiment)
    2. RE_T_PHENOMENOLOGICAL = 9.865  (CONSTRAINED — inverted from m_h = 125.10 GeV)
       → Circular: m_h is INPUT, Re(T) is OUTPUT
    3. Re(T) = 7.086  (CALIBRATED — used in baryon asymmetry for BBN match)
       → Gives exp(-7.086) ≈ 8.4e-4 damping, η_b ≈ 6.1e-10

    The tension: values (2) and (3) disagree. This is an OPEN PROBLEM.
    The geometric prediction (1) fails for the Higgs mass entirely.
    We must be honest about what is geometric vs. phenomenological.

    Formula: m_h² = 8π² v² (λ₀ - κ Re(T) y_t²)
    Where:
    - v = 174 GeV (Yukawa coupling scale, from HiggsVEVs.V_YUKAWA)
    - λ₀ = 0.129 (tree-level quartic from SO(10) → MSSM matching)
    - κ = 1/(8π²) (1-loop coefficient)
    - y_t = 0.99 (top Yukawa from geometry)
    - Re(T) = ??? (complex structure modulus - the problem!)
    """

    # Yukawa coupling scale (v/√2, NOT the electroweak VEV!)
    # See HiggsVEVs class for correct VEV definitions
    V_YUKAWA = 174.0             # [GeV] = v_EW/√2 ≈ 246/√2 (for Yukawa couplings)

    # SO(10) → MSSM matching - NOTE: This is actually calibrated, not purely geometric!
    # The value λ₀ = 0.129 is chosen to match the Higgs mass when Re(T) = 1.833
    # True geometric calculation gives λ₀ ≈ 0.0945 (see comment below)
    G_GUT = np.sqrt(4*np.pi/24.3)
    COS2_THETA_W = 0.77
    LAMBDA_0_GEOMETRIC = (G_GUT**2 / 8) * (3/5 * COS2_THETA_W + 1)  # = 0.0945 (pure geometry)
    LAMBDA_0 = 0.129             # [CALIBRATED] Tree-level quartic used in v11.0-v12.4

    # G₂ complex structure modulus - TWO VALUES (GEOMETRIC vs PHENOMENOLOGICAL)
    #
    # GEOMETRIC VALUE (from TCS attractor mechanism):
    RE_T_ATTRACTOR = 1.833       # [GEOMETRIC] From flux + membrane instantons on TCS #187
    #                              Formula: Re(T) = √(χ_eff/b₃) × f(T_ω)
    #                                      = √(144/24) × 0.748 = 1.833
    #                              This is the TRUE geometric prediction.
    #                              Result: m_h ≈ 414 GeV (FAILS to match experiment!)
    #
    # PHENOMENOLOGICAL VALUE (inverted from Higgs mass):
    RE_T_PHENOMENOLOGICAL = 9.865  # [CONSTRAINED] Inverted from m_h = 125.10 GeV
    #                                Formula: Re(T) = (λ₀ - λ_eff) / (κ y_t²)
    #                                where λ_eff = m_h²/(8π²v²) = 125.1²/(8π² × 174²) = 0.00655
    #                                Re(T) = (0.129 - 0.00655) / (κ × 0.99²) = 9.865
    #                                This is NOT a prediction - it's circular!
    #
    # NOTE: Re(T) = 7.086 is used in baryon_asymmetry.py (CALIBRATED for BBN).
    # It is NOT the Higgs-derived value (9.865) — this tension is an open problem.

    # For backward compatibility, keep old names but mark them clearly
    RE_T_MODULUS = RE_T_PHENOMENOLOGICAL  # [CIRCULAR] Uses experimental m_h as input

    # 1-loop correction coefficient
    KAPPA = 1/(8*np.pi**2)  # Derived: 1/(8π²) from 1-loop beta function

    # Top Yukawa (from geometry)
    Y_TOP = 0.99  # Source: PDG 2024 top Yukawa ≈ mt/v ≈ 173/175 ≈ 0.99

    @staticmethod
    def higgs_mass_constrained():
        """
        Calculate m_h using PHENOMENOLOGICAL Re(T) = 9.865

        WARNING: This is CIRCULAR! The value Re(T) = 9.865 was obtained
        by inverting this very formula with m_h = 125.10 GeV as input.
        This is NOT a prediction - it's a consistency check.

        Returns:
            m_h in GeV (should give 125.10 GeV by construction)
        """
        m_h_squared = (8*np.pi**2 * HiggsMassParameters.V_YUKAWA**2 *
                      (HiggsMassParameters.LAMBDA_0 -
                       HiggsMassParameters.KAPPA *
                       HiggsMassParameters.RE_T_PHENOMENOLOGICAL *
                       HiggsMassParameters.Y_TOP**2))
        return np.sqrt(m_h_squared)

    @staticmethod
    def higgs_mass_predicted():
        """
        Calculate m_h using GEOMETRIC Re(T) = 1.833

        This is the TRUE prediction from TCS G₂ attractor mechanism.
        Result: m_h ≈ 414 GeV (FAILS to match experiment!)

        Returns:
            m_h in GeV (predicted from geometry)
        """
        m_h_squared = (8*np.pi**2 * HiggsMassParameters.V_YUKAWA**2 *
                      (HiggsMassParameters.LAMBDA_0 -
                       HiggsMassParameters.KAPPA *
                       HiggsMassParameters.RE_T_ATTRACTOR *
                       HiggsMassParameters.Y_TOP**2))
        return np.sqrt(m_h_squared)

    # Experimental value (PDG 2024) - THIS IS INPUT, NOT OUTPUT!
    M_HIGGS_EXPERIMENTAL = 125.10   # Source: PDG 2024 m_H = 125.10 ± 0.14 GeV (ATLAS+CMS)
    M_HIGGS_EXPERIMENTAL_ERROR = 0.14  # [GeV] Experimental uncertainty

    # For backward compatibility
    M_HIGGS_PREDICTED = M_HIGGS_EXPERIMENTAL  # [MISLEADING NAME] Actually experimental input!
