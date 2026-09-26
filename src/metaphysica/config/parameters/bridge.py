"""Unified time / bridge physics parameters (v21).

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""

import numpy as np

from ..registry import _ssot_dim


# ==============================================================================
# UNIFIED TIME / BRIDGE PHYSICS PARAMETERS (v21)
# ==============================================================================

class BridgePhysicsParameters:
    """
    Parameters for v21 two-time framework with Euclidean bridge.

    v21.0: Replaces two-time physics with dual-shadow bridge structure.
    The 2D Euclidean bridge connects Normal and Mirror shadows, with
    physics identified via the OR reduction operator R_perp.

    Historical note: This class was formerly MultiTimeParameters for
    the (24,2) two-time framework (v16-v20). The v21 framework uses
    two-time signature (24,2) with an Euclidean bridge instead.
    """

    # Coupling Constants
    G_COUPLING = 0.1         # Multi-time coupling strength g
    # Derived from RG: β(g) = g³/(16π²) at TeV scale

    E_FERMI = 1.0            # Fermi energy scale [TeV] (condensate formation)

    # Gravitational Wave Dispersion (v6.1)
    XI_QUADRATIC = 1e10      # Quadratic GW coefficient ξ (1-loop estimate)

    @staticmethod
    def eta_linear():
        """Linear GW coefficient: η = g/E_F"""
        return MultiTimeParameters.G_COUPLING / MultiTimeParameters.E_FERMI

    # Orthogonal Time Parameters
    DELTA_T_ORTHO = 1e-18    # Orthogonal time delay [seconds]
    # Estimate: R_ortho/c ~ TeV^{-1} ~ 10^{-18} s

    R_ORTHO = 1.0            # Orthogonal compactification radius [normalized units]

    # LISA Gravitational Wave Band
    K_LISA_MIN = 1e-4        # LISA minimum frequency [Hz]
    K_LISA_TYPICAL = 1e-3    # LISA peak sensitivity [Hz]
    K_LISA_MAX = 1e-1        # LISA maximum frequency [Hz]
    K_LISA_DEFAULT = 1e-10   # Conservative estimate for calculations [Hz]

    # Thermal Time Hypothesis
    ALPHA_TTH = 1.0          # TTH normalization (Tomita-Takesaki)
    BETA_INVERSE_TEMP = 1.0  # Inverse temperature (KMS condition)

    # Mirror Sector Mixing
    THETA_MIRROR_DEFAULT = 0.0      # Mirror mixing angle [radians] (no mixing)
    THETA_EXAMPLE_45DEG = np.pi/4   # Example 45° mixing for proton decay

    @staticmethod
    def beta_mixing(theta):
        """Mirror sector mixing: β = cos(θ)"""
        return np.cos(theta)


# Legacy alias for backward compatibility
MultiTimeParameters = BridgePhysicsParameters  # DEPRECATED: Use BridgePhysicsParameters


# ==============================================================================
# v21 DUAL-SHADOW BRIDGE PARAMETERS (replaces Sp(2,R) Gauge Fixing)
# ==============================================================================

class V21BridgeParameters:
    """
    Parameters for v21 Euclidean Bridge mechanism.

    v21.0: The dual-shadow bridge framework replaces Sp(2,R) gauge fixing.
    Two-time signature (24,2): the Sp(2,R) gauge constraint (Bars,
    STRUCTURAL) eliminates ghosts and CTCs.

    v22.0 FIBERED TIME STRUCTURE (12×(2,0) Bridge Architecture):
    -----------------------------------------------------------
    Two-time ruling: each shadow carries its OWN timelike direction.
    The 12×(2,0) bridge pairs connect corresponding spatial dimensions.

        M^26 = (12,1)_normal + (12,1)_mirror

    - (12,1)_normal: Normal shadow, 12 spatial + its own time
    - (12,1)_mirror: Mirror shadow, 12 spatial + its own time
    - 12×(2,0): Bridge pairs connecting corresponding spatial dimensions
    - Shared clock: the Sp(2,R)-invariant t+ = (t1+t2)/sqrt(2)

    Dimensional check: 13 + 13 = 26 ✓
    Signature check: (12,1) + (12,1) = (24,2) ✓

    Each shadow sees: 12 spatial + 1 time (its own) = 13D(12,1)

    Key features:
    - Two-time (24,2): Sp(2,R) gauge removes negative-norm states (STRUCTURAL)
    - Dual shadows: 2×13D(12,1) each with its own time
    - 12×(2,0) bridge pairs: Connect corresponding spatial dimension pairs
    - OR reduction: R_perp² = -I implements Möbius topology

    Decomposition: 26D(24,2) = 12×(2,0) bridge pairs + 2 shadow times + two shadow-time directions
                 = 24D space + 2D time = 26D ✓
    Per shadow: 12 spatial + 1 time (its own) = 13D(12,1)

    References:
    - PM v21.0 (2026): Dual-Shadow Bridge Framework
    - PM v21.1 (2026): Fibered Time Resolution
    - Appendix G: Euclidean Bridge Derivation
    """

    # Bulk spacetime (v21/v22: two-time structure)
    D_BULK = _ssot_dim("D_ancestral_total")
    BULK_SIGNATURE = (_ssot_dim("D_ancestral_space"), _ssot_dim("D_ancestral_time"))

    # Dual-shadow structure (replaces Sp(2,R) constraints)
    N_SHADOWS = 2             # Normal + Mirror shadows
    D_PER_SHADOW = _ssot_dim("D_shadow_total")
    SHADOW_SIGNATURE_SPATIAL = (12, 0)  # v22: Shadows are SPATIAL only (12,0)

    # v21.1 Fibered Time Structure (Issue 4 Resolution)
    TIME_STRUCTURE = "per-shadow"   # Two-time: each shadow carries its own time
    TIME_FIBER_SIGNATURE = (0, 2)   # T^2: two times, one per shadow
    TIME_SHARED = False             # Two-time ruling: each shadow evolves in its own time

    # Legacy (for backward compatibility - use SHADOW_SIGNATURE_SPATIAL instead)
    SHADOW_SIGNATURE = (_ssot_dim("D_shadow_space"), _ssot_dim("D_shadow_time"))

    # Euclidean bridge
    D_BRIDGE = 2              # Bridge dimensions
    BRIDGE_SIGNATURE = (2, 0)   # Positive-definite: ds² = dy₁² + dy₂²
    BRIDGE_PERIOD = 7.99      # L = 2π√φ (golden ratio period)
    GOLDEN_RATIO = 1.618034   # φ = (1 + √5)/2

    # OR Reduction Operator
    #
    # IDENTIFICATION (2026-08-20 literature review): this matrix is the
    # modular S element of SL(2,Z), and it is EXACTLY the gluing map of a
    # twisted connected sum G2 manifold. Kovalev's TCS construction glues
    # two asymptotically-cylindrical halves across a neck that is
    # asymptotically K3 x T^2 x R; the matching map exchanges the two
    # circle factors of that T^2. Globally the TCS G2 manifold is a
    # coassociative K3 fibration over an S^3 assembled from two solid tori
    # glued along their common T^2 - the genus-1 Heegaard splitting of
    # S^3 - and the gluing element of that splitting is S = [[0,-1],[1,0]].
    # S^2 = -I is precisely the kernel of the double cover
    # SL(2,Z) -> PSL(2,Z), which makes the framework's "Mobius double
    # cover" language rigorous rather than analogical.
    #
    # So R_perp is not merely LIKE the TCS gluing; it IS the TCS gluing
    # element. This was written down independently in this framework before
    # the identification was noticed.
    # Refs: Kovalev math/0012189; Corti-Haskins-Nordstrom-Pacini 1207.4470;
    #       Kovalev math/0511150 (coassociative K3 fibration over S^3);
    #       Braun & Schafer-Nameki 1708.07215.
    OR_MATRIX = [[0, -1], [1, 0]]  # R_perp = modular S element of SL(2,Z)
    # ------------------------------------------------------------------
    # OR-MODULAR CONJECTURE (2026-08-20). Recorded as a CONJECTURE with a
    # falsifiable gate, not as a result.
    #
    # Bisognano-Wichmann factorises the modular conjugation of a wedge
    # algebra as J_W = Theta . U(R_W(pi)): an antiunitary PCT factor times
    # the UNITARY rotation by pi that carries one wedge onto the other.
    # In Spin(2) the lift of a pi-rotation is exp((pi/2) e1 e2) = e1 e2,
    # whose 2x2 realisation is exactly [[0,-1],[1,0]] = R_perp. So
    #
    #     R_perp = U(R_W(pi))  -- the GEOMETRIC HALF of J, not J itself.
    #
    # The square is then not a mismatch but the required value:
    # R_perp^2 = U(R(2pi)) = (-1)^F, the spinor double cover. J^2 = +1
    # holds only because Theta^2 = (-1)^F cancels it. Independently,
    # Cl(12,1) is quaternionic ((s-t) = 3 mod 8; equivalently D = 13 = 5
    # mod 8, symplectic Majorana), so any antilinear conjugation on a
    # single shadow's spinors MUST square to -1 - forced, not chosen.
    #
    # CONJECTURE: there exists an antiunitary Theta reversing both shadow
    # times, with Theta^2 = (-1)^F, such that J = Theta . R_perp. Theta is
    # the object the framework does not yet have; R_perp supplies the
    # geometry and none of the conjugation.
    #
    # 'The central OR balances the shadows' then has a precise form:
    #     (K_normal - K_mirror) Omega = 0
    # i.e. the shared state is annihilated by the difference of the two
    # shadows' modular Hamiltonians - the same statement as
    # (H_R - H_L)|TFD> = 0 for a thermofield double - together with Haag
    # duality M_mirror = (M_normal)' (twisted, Z^2 = (-1)^F, for fermions).
    #
    # FALSIFIABLE GATE (the highest-value test available): REFLECTION
    # POSITIVITY. Exhibit an isometric involution theta exchanging the two
    # shadows and prove <theta F, F> >= 0 for F supported on one shadow.
    # Reflection positivity is exactly what FAILS for ghost, higher-
    # derivative and generically two-time theories, so this is a real
    # test that could close the modular route cleanly and early.
    # Template for spinors: Jaffe & Ritter arXiv:hep-th/0609003; the
    # RP -> modular objects step: Neeb & Olafsson arXiv:1611.00080.
    #
    # TWO HAZARDS.
    # (a) EQUIVOCATION. 'Modular' in Tomita-Takesaki (from the modulus /
    #     Radon-Nikodym derivative) and 'modular' in SL(2,Z) (from moduli
    #     of elliptic curves) are UNRELATED. The established result that
    #     R_perp is the S element of SL(2,Z) therefore gives ZERO support
    #     for the modular-conjugation reading. Any argument passing
    #     through the shared word is void; the two must be kept apart.
    # (b) TYPE. Modular theory is non-trivial only for type III_1 factors.
    #     Compact internal manifolds give discrete KK towers whose algebras
    #     are type I with a trace, where J is just a transpose. See the
    #     open tension noted on foundations/tomita-takesaki.html.
    # ------------------------------------------------------------------

    OR_SQUARE = -1                 # R_perp² = -I (Möbius double-cover)
    OR_DET = 1                     # det(R_perp) = 1 (orientation-preserving)

    # Physics validation flags
    GHOST_FREE = True         # Sp(2,R) gauge removes negative-norm states in (24,2) (STRUCTURAL)
    CTC_FREE = True           # Sp(2,R) gauging forbids closed timelike curves in (24,2) (STRUCTURAL)
    MOBIUS_VERIFIED = True    # Spinor double-cover topology confirmed

    @staticmethod
    def verify_decomposition():
        """Verify: 26D = 2×13D (own time per shadow)"""
        # Two-time: 2 shadows × 13D each (own time) = 26D bulk
        return V21BridgeParameters.D_BULK == (
            V21BridgeParameters.N_SHADOWS * V21BridgeParameters.D_PER_SHADOW
        )  # Two-time: 26 = 2 x 13, no shared time to subtract

    @staticmethod
    def verify_signature():
        """
        Verify: (24,2) signature from fibered time + spatial shadows.

        v22.0 FIBERED TIME STRUCTURE (12×(2,0) Bridge Architecture):
        ------------------------------------------------------------
        M^25 = T^1 ×_fiber (S_normal^12 ⊕ S_mirror^12)

        The key insight is that time is NOT duplicated across shadows.
        Time T^1 is the shared fiber base with signature (0,1).
        Shadows are SPATIAL manifolds with signature (12,0) each.
        12×(2,0) bridge pairs connect corresponding spatial dimensions.

        Correct arithmetic:
        - Time fiber T^1:        (0,1)   -> 0 spatial, 1 temporal
        - Normal shadow S^12:    (12,0)  -> 12 spatial, 0 temporal
        - Mirror shadow S^12:    (12,0)  -> 12 spatial, 0 temporal
        -------------------------------------------------------
        Total:                   (24,2)  -> 24 spatial, 2 temporal ✓

        Note: The 12×(2,0) bridge pairs connect dimensions between shadows,
        not adding new dimensions (they pair up existing ones).
        """
        # Spatial: 2×12 (shadow spatial) = 24 ✓
        spatial = (V21BridgeParameters.N_SHADOWS *
                   V21BridgeParameters.SHADOW_SIGNATURE_SPATIAL[0])
        # Temporal: 2 (one timelike direction per shadow) ✓
        temporal = V21BridgeParameters.TIME_FIBER_SIGNATURE[1]  # = 2
        return (spatial, temporal) == V21BridgeParameters.BULK_SIGNATURE

    @staticmethod
    def export_data():
        """Export data for theory_output.json"""
        return {
            'D_bulk': V21BridgeParameters.D_BULK,
            'bulk_signature': V21BridgeParameters.BULK_SIGNATURE,
            'n_shadows': V21BridgeParameters.N_SHADOWS,
            'D_per_shadow': V21BridgeParameters.D_PER_SHADOW,
            'shadow_signature': V21BridgeParameters.SHADOW_SIGNATURE,
            'D_bridge': V21BridgeParameters.D_BRIDGE,
            'bridge_signature': V21BridgeParameters.BRIDGE_SIGNATURE,
            'bridge_period': V21BridgeParameters.BRIDGE_PERIOD,
            'or_operator': 'R_perp = [[0,-1],[1,0]]',
            'or_square': 'R_perp² = -I (Möbius)',
            'or_det': V21BridgeParameters.OR_DET,
            'ghost_free': V21BridgeParameters.GHOST_FREE,
            'ctc_free': V21BridgeParameters.CTC_FREE,
            'decomposition_valid': V21BridgeParameters.verify_decomposition(),
            'status': 'v21.0 DUAL-SHADOW BRIDGE - Replaces Sp(2,R) gauge fixing'
        }


# Legacy alias for backward compatibility
Sp2RGaugeFixingParameters = V21BridgeParameters  # DEPRECATED: Use V21BridgeParameters


# ==============================================================================
# PNEUMA VIELBEIN EMERGENCE PARAMETERS (v13.0 - Open Question 2)
# ==============================================================================

class PneumaVielbeinParameters:
    """
    Parameters for Pneuma vielbein emergence validation.

    The frame field (vielbein) emerges from Pneuma spinor bilinears:
    e_M^a ∝ Re⟨Ψ̄_P Γ^a D_M Ψ_P⟩

    Einstein-Hilbert gravity is induced via Sakharov mechanism.

    v21.0: Updated for dual-shadow bridge framework with two times (one per shadow).

    References:
    - Akama, K. (1978): Pregeometry
    - Wetterich, C. (2004): Phys. Rev. D 70, 105004
    - Sakharov, A.D. (1967): Induced gravity
    - PM v21.0 (2026): Dual-Shadow Bridge Framework
    """

    # Bulk spacetime (v22 two-time structure)
    D_BULK = _ssot_dim("D_ancestral_total")
    BULK_SIGNATURE = (_ssot_dim("D_ancestral_space"), _ssot_dim("D_ancestral_time"))

    # Per-shadow spacetime (v22 dual-shadow structure)
    D_PER_SHADOW = _ssot_dim("D_shadow_total")
    SHADOW_SIGNATURE = (_ssot_dim("D_shadow_space"), _ssot_dim("D_shadow_time"))

    # Internal manifold (per shadow)
    D_INTERNAL = 7  # Source: Joyce (2000) G2 holonomy manifold dimension

    # Clifford algebra (two-time signature (24,2))
    CLIFFORD_DIM = 4096  # Weyl spinor of Cl(24,2): 2^13/2 = 4096

    # Vielbein construction
    VIELBEIN_FORMULA = "e_M^a = (1/M*^13) Re⟨Ψ̄_P Γ^a D_M Ψ_P⟩"
    METRIC_FORMULA = "G_MN = e_M^a e_N^b η_ab"

    # Induced gravity
    INDUCED_ACTION = "S_induced = (M_Pl²/16π) ∫ d⁴x √g R"

    @staticmethod
    def export_data():
        """Export data for theory_output.json"""
        return {
            'D_bulk': PneumaVielbeinParameters.D_BULK,
            'bulk_signature': PneumaVielbeinParameters.BULK_SIGNATURE,
            'D_per_shadow': PneumaVielbeinParameters.D_PER_SHADOW,
            'shadow_signature': PneumaVielbeinParameters.SHADOW_SIGNATURE,
            'D_internal': PneumaVielbeinParameters.D_INTERNAL,
            'clifford_dim': PneumaVielbeinParameters.CLIFFORD_DIM,
            'vielbein_formula': PneumaVielbeinParameters.VIELBEIN_FORMULA,
            'metric_formula': PneumaVielbeinParameters.METRIC_FORMULA,
            'induced_action': PneumaVielbeinParameters.INDUCED_ACTION,
            'machian_principle': 'Pneuma IS the fabric that curves',
            'references': [
                'Akama (1978): Pregeometry',
                'Wetterich (2004): Spinor gravity',
                'Sakharov (1967): Induced gravity',
                'PM v21.0 (2026): Dual-Shadow Bridge'
            ],
            'status': 'v21.0 - Geometry emerges from Pneuma via induced gravity'
        }


# ==============================================================================
# v21 UNIFIED TIME PHYSICS PARAMETERS (replaces 2T-Physics)
# ==============================================================================

class V21UnifiedTimePhysics:
    """
    SUPERSEDED (2026-08-19 two-time ruling): v21.0/v22.0 Unified Time
    Physics Framework. This class encoded the one-time (24,2) formulation
    that briefly replaced TwoTimePhysics (v6.4-v20); the author's ruling
    restored the two-time structure, so the CURRENT geometry is signature
    (24,2) = (12,1) + (12,1), one time per 13D shadow, with the Sp(2,R)
    gauge constraint (Bars) controlling ghosts (STRUCTURAL). The block
    below is retained for historical provenance only - see
    canonical_values.py for the ruling.

    The 12 bridge pairs connect 12 corresponding spatial dimension pairs between
    Normal and Mirror shadows. Both shadows share the single temporal dimension.

    Historical reference (deprecated):
    - Bars, I. (2000). "Survey of two-time physics" - Inspired approach
    - PM v21.0 (2026): Dual-Shadow Bridge Framework
    """

    # === v21/v22 DIMENSIONAL STRUCTURE ===
    D_SHADOW_NORMAL = _ssot_dim("D_shadow_total")
    D_SHADOW_MIRROR = _ssot_dim("D_shadow_total")
    N_BRIDGE_PAIRS = _ssot_dim("bridge_local")

    # Verification: 12 (Normal spatial) + 12 (Mirror spatial) + 1 (shared time) = 25 ✓
    # Each shadow sees: 12 spatial + 1 time = 13D(12,1)
    SPATIAL_NORMAL = 12      # Derived: D_SHADOW - 1 = 12 spacelike
    SPATIAL_MIRROR = 12      # Derived: D_SHADOW - 1 = 12 spacelike
    TEMPORAL_UNIFIED = 1     # v21/v22: Two-time structure (no ghosts, no CTCs)
    
    # === CFT ANOMALY CANCELLATION ===
    C_MATTER = 25            # Matter: 24 spatial + 1 temporal (v21 two-time structure)
    C_GHOST = -25            # Virasoro ghost (b-c system) - matches C_MATTER for cancellation
    DELTA_C_BRIDGE = 0       # v21: Bridge contributes no central charge anomaly
    C_MATTER_EFFECTIVE = 24  # v21: C_MATTER - TEMPORAL_UNIFIED = 25 - 1 = 24
    C_TOTAL = 0              # v21: Anomaly cancellation preserved

    # Critical dimensions
    D_CRITICAL_V21 = 25      # v21/v22: Two-time structure critical dimension (24+1)

    # === v21 OR REDUCTION ===
    OR_COUPLING = 0.1        # v21: OR reduction coupling
    OR_CONSTRAINTS = 1       # v21: Single Möbius constraint R_perp² = -I

    # === BRST QUANTIZATION ===
    BRST_GHOST_NUMBER = 1    # Source: BRST cohomology - ghost number for physical states
    BRST_ANOMALY = 0.0       # Derived: Q^2 = 0 (nilpotency verified)

    # === v21 DUAL-SHADOW CONFIGURATION ===
    SHADOW_NORMAL_PRE_G2 = (12, 1)   # v22: Before G₂ compactification = 13D(12,1)
    SHADOW_MIRROR_PRE_G2 = (12, 1)   # v22: Before G₂ compactification = 13D(12,1)
    SHADOW_NORMAL_POST_G2 = (5, 1)   # v22: After G₂ compactification = 6D(5,1)
    SHADOW_MIRROR_POST_G2 = (5, 1)   # v22: After G₂ compactification = 6D(5,1)
    # Before G2: (12,1) per shadow = 13D
    # After G2: (5,1) per shadow = 6D (13D - 7D G2 = 6D)

    # === BPS STABILITY ===
    # C_2 = p(p + 22)/4 for SO(24,2)
    CASIMIR_NORMAL = 33.75   # 5 * (5 + 22) / 4 (preserved from v20)
    CASIMIR_MIRROR = 33.75   # Same for mirror shadow

    # === v21 STABILITY FLAGS ===
    GHOST_FREE = True        # v21: Two-time structure eliminates ghosts
    CTC_FREE = True          # v21: No closed timelike curves
    TACHYON_PROJECTED = True
    ANOMALY_FREE = True
    UNITARITY_PRESERVED = True


# Legacy alias for backward compatibility
TwoTimePhysics = V21UnifiedTimePhysics  # DEPRECATED: Use V21UnifiedTimePhysics
