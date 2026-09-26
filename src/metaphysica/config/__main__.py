"""Command-line validation entry point: ``python -m metaphysica.config``.

The block below is the former in-module ``if __name__ == '__main__'`` section
of config.py, moved verbatim.
"""

from metaphysica.config import (
    FundamentalConstants,
    LandscapeParameters,
    ModuliParameters,
    MultiTimeParameters,
    PhenomenologyParameters,
    SharedDimensionsParameters,
    validate_all,
)


# ==============================================================================
# MAIN EXECUTION (FOR TESTING)
# ==============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("PRINCIPIA METAPHYSICA v6.2 - CONFIGURATION VALIDATION")
    print("=" * 80)

    # Test fundamental constants
    print("\nDIMENSIONAL STRUCTURE (Shared Extra Dimensions):")
    print(f"  Initial: {FundamentalConstants.D_BULK}D with signature {FundamentalConstants.SIGNATURE_INITIAL}")
    print(f"  After Sp(2,R): {FundamentalConstants.D_AFTER_SP2R}D with signature {FundamentalConstants.SIGNATURE_BULK}")
    print(f"  Internal manifold: {FundamentalConstants.INTERNAL_MANIFOLD} ({FundamentalConstants.D_INTERNAL}D)")
    print(f"  Effective bulk: {FundamentalConstants.D_EFFECTIVE}D with signature {FundamentalConstants.SIGNATURE_EFFECTIVE}")
    print(f"  Observable brane: {FundamentalConstants.D_OBSERVABLE_BRANE}D = {FundamentalConstants.D_COMMON}D_common + {FundamentalConstants.D_SHARED_EXTRAS}D_shared")
    print(f"  Shadow branes (×{FundamentalConstants.N_SHADOW_BRANES}): {FundamentalConstants.D_SHADOW_BRANE}D = {FundamentalConstants.D_COMMON}D_common only")

    print("\nTOPOLOGICAL INVARIANTS:")
    print(f"  Euler characteristic (eff) = {FundamentalConstants.euler_characteristic_effective()}")
    print(f"  Fermion generations = {FundamentalConstants.fermion_generations()}")
    print(f"  Pneuma (full 26D) = {FundamentalConstants.pneuma_dimension_full()} components")
    print(f"  Pneuma (reduced 13D) = {FundamentalConstants.pneuma_dimension_reduced()} components")

    # Test shared dimensions
    print("\nSHARED DIMENSIONS (KK SPECTRUM):")
    print(f"  R_shared_y = {SharedDimensionsParameters.R_SHARED_Y:.6e} GeV^-1")
    print(f"  R_shared_z = {SharedDimensionsParameters.R_SHARED_Z:.6e} GeV^-1")
    print(f"  M_KK (lightest) = {SharedDimensionsParameters.M_KK_CENTRAL} GeV")
    print(f"  Warp parameter k = {SharedDimensionsParameters.WARP_PARAMETER_K}")
    print(f"  Warp factor at IR: {SharedDimensionsParameters.warp_factor(1.0):.6e}")

    spectrum = SharedDimensionsParameters.kk_spectrum(n_max=3, m_max=3)
    print(f"\n  First 5 KK modes:")
    for i, (n, m, mass) in enumerate(spectrum[:5]):
        print(f"    ({n},{m}): {mass:.1f} GeV")

    # Test derived parameters
    print("\nDERIVED PARAMETERS:")
    print(f"  w_0 = {PhenomenologyParameters.w0_value():.6f}")
    print(f"  eta = g/E_F = {MultiTimeParameters.eta_linear():.3f}")
    print(f"  a_swampland = {ModuliParameters.a_swampland():.6f}")
    print(f"  Delta (gap) = {ModuliParameters.condensate_gap():.6f} TeV")
    print(f"  S_landscape = {LandscapeParameters.landscape_entropy():.2f}")
    print(f"  M_Pl (from 6D) = {SharedDimensionsParameters.effective_4d_planck_mass():.4e} GeV")

    # Run validation
    print("\nVALIDATION:")
    all_passed, results = validate_all()

    for name, (passed, *values) in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status} {values}")

    print(f"\n{'=' * 80}")
    print(f"Overall: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")
    print(f"{'=' * 80}")
