"""Computational settings for the framework.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""

import numpy as np


# ==============================================================================
# COMPUTATIONAL SETTINGS
# ==============================================================================

class ComputationalSettings:
    """
    Numerical parameters for simulations and calculations.
    """

    # QuTiP Quantum Simulations
    N_QUTIP_HILBERT = 4       # Hilbert space dimension (toy model)
    N_QUTIP_PRODUCTION = 10   # Production-level dimension (if needed)

    TIME_START = 0            # Evolution start time
    TIME_END = 10             # Evolution end time
    TIME_STEPS = 100          # Number of time steps

    # Numerical Tolerances
    TOLERANCE_UNITARITY = 1e-10   # Unitary evolution check
    TOLERANCE_CONVERGENCE = 1e-8  # Convergence criterion

    # G₂ Ricci Flow Tolerances (v16.0)
    TORSION_TOLERANCE = 1e-15     # Geometric torsion threshold (dφ=0, d(*φ)=0)
    RICCI_TOLERANCE = 1e-12       # Ricci-flatness check (Ric=0)
    INTEGRATION_RTOL = 1e-10      # Relative tolerance for ODE solver
    INTEGRATION_ATOL = 1e-12      # Absolute tolerance for ODE solver
    AUTO_TORSION_SURGERY = True   # Enable automatic torsion surgery

    # Asymptotic Limits
    A_LIMIT_EXPONENT = 10     # Late-time scale factor: a → exp(10) ≈ 22026
    # For w(a→∞) limit evaluation

    # SymPy Precision
    SYMPY_PRECISION_DIGITS = 10   # Number of significant digits

    # Export Settings
    CSV_DELIMITER = ','
    EXCEL_ENGINE = 'openpyxl'

    @staticmethod
    def time_array():
        """Generate time array for evolution"""
        return np.linspace(ComputationalSettings.TIME_START,
                          ComputationalSettings.TIME_END,
                          ComputationalSettings.TIME_STEPS)
