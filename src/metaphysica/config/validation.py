"""Self-consistency validation functions.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""

from .constants import FundamentalConstants
from .parameters.moduli import ModuliParameters


# ==============================================================================
# VALIDATION FUNCTIONS
# ==============================================================================

def validate_swampland_constraint():
    """Verify a > √(2/3) for de Sitter compatibility"""
    a = ModuliParameters.a_swampland()
    bound = ModuliParameters.SWAMPLAND_BOUND
    return a > bound, a, bound


def validate_generation_count():
    """Verify we get exactly 3 generations"""
    n_gen = FundamentalConstants.fermion_generations()
    return n_gen == 3, n_gen


def validate_dimensional_consistency():
    """
    Verify dimensional structure is self-consistent.

    v22 Checks (legacy code uses 25D values for backward compatibility):
    1. Bulk starts at 26D(24,2) - signature (24,2)
    2. Dual-shadow bridge: 26D = 2×13D + 1 (with shared time structure)
    3. G₂ compactification: 13D - 7D = 6D per shadow → 4D visible
    4. Shared dimensions: 6D = 4D_common + 2D_shared
    5. Observable brane has full 6D access
    6. Shadow branes restricted to 4D_common

    Historical note: v16-v20 used 26D(24,2) bosonic string theory origin.
    """
    checks = []

    # Check 1: two-time bulk (24,2) = 26D
    checks.append(FundamentalConstants.D_BULK == 26)

    # Check 2: v22 dual-shadow structure (D_PER_SHADOW = 13)
    checks.append(FundamentalConstants.D_AFTER_SP2R == 13)

    # Check 3: G₂ compactification (v22: 13D - 7D = 6D per shadow)
    per_shadow_calc = FundamentalConstants.D_AFTER_SP2R - FundamentalConstants.D_INTERNAL  # 13 - 7 = 6
    checks.append(per_shadow_calc == FundamentalConstants.D_EFFECTIVE)
    checks.append(FundamentalConstants.D_EFFECTIVE == 6)

    # Check 4: Shared dimensions decomposition
    shared_sum = FundamentalConstants.D_COMMON + FundamentalConstants.D_SHARED_EXTRAS
    checks.append(shared_sum == FundamentalConstants.D_EFFECTIVE)
    checks.append(FundamentalConstants.D_COMMON == 4)
    checks.append(FundamentalConstants.D_SHARED_EXTRAS == 2)

    # Check 5: Observable brane dimensions
    checks.append(FundamentalConstants.D_OBSERVABLE_BRANE == 6)

    # Check 6: Shadow brane dimensions
    checks.append(FundamentalConstants.D_SHADOW_BRANE == 4)

    all_pass = all(checks)
    return all_pass, sum(checks), len(checks)


def validate_all():
    """Run all validation checks"""
    results = {
        'swampland': validate_swampland_constraint(),
        'generations': validate_generation_count(),
        'dimensions': validate_dimensional_consistency(),
    }

    all_passed = all(result[0] for result in results.values())
    return all_passed, results
