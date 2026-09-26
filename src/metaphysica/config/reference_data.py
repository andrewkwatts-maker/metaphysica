"""Experimental reference data used for validation.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""


# ==============================================================================
# REAL-WORLD DATA (FOR VALIDATION)
# ==============================================================================

class RealWorldData:
    """
    Experimental/observational values for comparison with theoretical predictions.
    Format: (value, error, source_link)
    """

    PLANCK_MASS = (
        1.2205e19,  # GeV
        0.0003e19,   # error
        'https://pdg.lbl.gov/2024/reviews/contents_sports.html'
    )

    GENERATIONS = (
        3,           # exact
        0,           # no error
        'https://pdg.lbl.gov/2024/tables/contents_tables.html'
    )

    W0_DARK_ENERGY = (
        -0.827,      # DESI 2024 + Planck
        0.063,       # 1σ error
        'https://arxiv.org/abs/2404.03002'
    )

    WA_EVOLUTION = (
        -0.75,       # CPL parametrization
        0.3,         # typical error
        'https://arxiv.org/abs/2404.03002'
    )

    PROTON_LIFETIME = (
        3.5e34,      # years (SO(10) central value)
        1.83e34,     # error (Super-K lower bound: 1.67e34)
        'https://arxiv.org/abs/1408.1195'
    )

    HUBBLE_CONSTANT = (
        67.4,        # km/s/Mpc (Planck 2018)
        0.5,         # error
        'https://arxiv.org/abs/1807.06209'
    )
