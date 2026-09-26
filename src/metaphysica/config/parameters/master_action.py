"""v21 master action and Pneuma field parameters.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""


# ==============================================================================
# v21 MASTER ACTION AND PNEUMA FIELD PARAMETERS
# ==============================================================================

class MasterActionParameters:
    """
    v21.0/v22.0: Master Action parameters for the 26D(24,2) theory.
    (Legacy variable names use "25D" for backward compatibility)

    S_26D = ∫d²⁶X √G [M²⁵R + Ψ̄_P(iΓ·D - m)Ψ_P + L_bridge]

    Two-time: The Pneuma field Ψ_P is a 26D Weyl spinor of Cl(24,2) (4096 = 2^13/2).
    Note: 4096 components (was 8192 from Cl(24,2) in v16-v20).
    """

    # Bulk Planck mass power
    BULK_PLANCK_POWER = 23  # Derived: D_BULK - 2 = 25 - 2 = 23 (graviton dim reduction)

    # v21/v22 Pneuma spinor dimension chain (26D → 12D per shadow → 4D)
    PNEUMA_25D = 4096       # Legacy name - 26D: Weyl 2^13/2 = 4096 of Cl(24,2)
    PNEUMA_SHADOW_FULL = 64 # v22: 2^[13/2] = 2^6 = 64 from Spin(12,1)
    PNEUMA_SHADOW_CHIRAL = 32  # Derived: Weyl projection 64/2 = 32
    PNEUMA_4D = 4           # Derived: 4D Weyl spinor from dim reduction

    # v21/v22 Reduction factors
    BRIDGE_REDUCTION = 64   # v21/v22: PNEUMA_26D / PNEUMA_SHADOW = 4096/64 = 64 (legacy var name)
    G2_REDUCTION = 8        # Derived: Per-shadow G₂ reduction factor
    Z2_REDUCTION = 2        # Derived: Chirality projection factor

    # Pneuma condensate parameters
    CONDENSATE_SCALE = 1.0  # TeV (condensation scale)
    CONDENSATE_GAP = 0.5    # Mass gap from symmetry breaking

    @staticmethod
    def reduction_chain():
        """v22: Returns the full spinor reduction chain"""
        return {
            '26D_Cl(24,2)': 4096,     # Two-time bulk (legacy keys '25D_Cl(24,1)', '26D_Cl(26,1)')
            '13D_Spin(12,1)': 64,     # v22: Per-shadow (12 space + 1 time (its own))
            '13D_chiral': 32,
            '4D_Weyl': 4,
            'total_factor': 4096 / 4  # v22: = 1024
        }


class HiddenVariableParameters:
    """
    v12.8: Hidden variable structure from 4-brane geometry.

    Observable states arise from partial tracing over shadow branes:
    ρ_Σ₁ = Tr_{Σ₂,Σ₃,Σ₄}[|Ψ⟩_bulk ⟨Ψ|]
    """

    # Brane structure (same as FundamentalConstants but explicit)
    N_OBSERVABLE = 1        # Derived: Our brane Σ₁ (singular observable)
    N_SHADOW = 3            # Derived: Shadow branes Σ₂, Σ₃, Σ₄ (from N_BRANES-1)
    TOTAL_BRANES = 4  # Derived: 1 observable + 3 shadow = 4 branes

    # Inter-brane correlation via Pneuma field
    BULK_CORRELATION = 0.8  # Entanglement strength
    DECOHERENCE_TIME = 1e-18  # seconds (Planck scale)

    # Bell test parameters
    BELL_CONSTRAINT = 'local'  # Bell constrains LOCAL hidden variables
    PM_STRUCTURE = 'bulk_nonlocal'  # PM variables are non-local in 3D
    COMPATIBLE = True  # Bell's theorem does not constrain PM

    # Randomness interpretation
    RANDOMNESS_TYPE = 'epistemic'  # Not fundamental indeterminacy
    RANDOMNESS_SOURCE = 'shadow_brane_ignorance'
    BULK_DETERMINISM = True  # 26D dynamics are deterministic
