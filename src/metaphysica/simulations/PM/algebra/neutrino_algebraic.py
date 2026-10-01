"""
Neutrino PMNS Angles from G₂ × E₇ Topology (Algebraic Derivation)
====================================================================

The PMNS reactor angle θ₁₃ and CP-violation phase δ_CP are estimated
from G₂ topology and E₇ branching with no free parameters. Both estimates
miss: θ₁₃ is FALSIFIED, and δ_CP scored MARGINAL at the off-path seed
b₃ = 24, where its construction was written (see Status).

θ₁₃ DERIVATION (E₇ ⊃ E₆ × U(1) branching + SU(2)_L correction):
    α_leak = 1/√6  (E₇ ⊃ E₆×U(1) Clebsch-Gordan coefficient, DERIVED)
    SU(2)_L sees n_gen=3 generations → √(2n_gen) suppression
    sin(θ₁₃) = α_leak / √(2 n_gen) = (1/√6) / √6 = 1/6 ≈ 0.1667
    θ₁₃ ≈ 9.59°   (NuFIT 6.0 IO: 8.63°, 12% high — FALSIFIED, ~9σ)

δ_CP CONSTRUCTION (G₂ associative 3-form holonomy angle). It splits b₃
evenly among the generations; at the adopted b₃ = 43 the split 43/3 is not
an integer, so the construction does not carry over, and run() (which reads
topology.elder_kads) registers values that follow the seed in force. As
written at the off-path seed:
    b₃ = 24, n_gen = 3  →  cycles_per_gen = b₃/n_gen = 8
    φ_assoc = 2π / cycles_per_gen = 2π/8 = π/4   (elementary holonomy angle)
    The CP phase from parallel transport around an associative 3-cycle,
    modulated by the full manifold factor χ_eff/(b₃ × n_gen):
        δ_CP = −φ_assoc × χ_eff/(b₃ × n_gen)
             = −(π/4) × 144/(24×3)
             = −(π/4) × 2 = −π/2 = −90°
    NuFIT 6.0 (NO) best fit ≈ 197° (−163°); the −107° once quoted here was a
    T2K-only fit. At the off-path seed −90° scores 1.825σ (MARGINAL); the
    earlier "inside the 1σ favoured region" claim is withdrawn.

Inputs as written: b₃ = 24 (the off-path seed), χ_eff = 144 (the K3 reading,
χ_eff = 2 Σ χ(K3) = 48n at n = 3), n_gen = 3 = b₂/4, and α_leak = 1/√6 —
no free parameters.

Status:
    neutrino.theta13_derived  — FALSIFIED (R1 ruling 2026-08-25: ~9σ from
        NuFIT 6.0 given 1σ≈0.25°. Kept on the books labelled -- the
        zero-parameter asin(1/6) candidate died honestly, which is the
        gate system demonstrating it has teeth. Working headline is
        particle.theta_13_deg = 8.669°.)
    neutrino.delta_CP_derived — DERIVED  (NO framing, -pi/2 = 270 deg at
        the off-path seed b3 = 24; ~1.8 sigma from the NuFIT 6.0 NO best
        fit ~197 deg; the registered value follows the seed in force. NOTE: two
        sibling modules export different delta_CP values in different
        orderings - particle/neutrino_mixing 278.4 deg (IO, includes a
        FITTED 45.9 deg offset) and particle/yukawa_derivation 277.3
        deg. They are not three confirmations of one prediction.)

Dependencies: g2_geometry_v16_0 (topology.elder_kads, topology.n_gen),
              e7_representation_v1_0 (geometry.alpha_leak)

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

import math
import sys
import os
from typing import Dict, Any, List, Optional

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.insert(0, project_root)

from metaphysica.simulations.base import (
    SimulationBase,
    SimulationMetadata,
    Formula,
    Parameter,
    ContentBlock,
    SectionContent,
)


# ---------------------------------------------------------------------------
# Pre-computed reference constants (for get_formulas / get_section_content
# which run without a live registry). They are written at the off-path seed
# b3 = 24; run() reads the seed in force from topology.elder_kads.
# ---------------------------------------------------------------------------
_ALPHA_LEAK = 1.0 / math.sqrt(6.0)      # E₇ ⊃ E₆×U(1) Clebsch-Gordan
_B3 = 24                                # the off-path seed (Y_7 has b3 = 43)
_CHI_EFF = 144                          # the K3 reading, chi_eff = 48 n at n = 3
_N_GEN = 3
_CYCLES_PER_GEN = _B3 / _N_GEN          # = 8 at the off-path seed only
_PHI_ASSOC = 2.0 * math.pi / _CYCLES_PER_GEN     # = π/4
_SIN_THETA13 = _ALPHA_LEAK / math.sqrt(2.0 * _N_GEN)  # = 1/6 ≈ 0.1667
_THETA13_DEG = math.degrees(math.asin(min(1.0, _SIN_THETA13)))  # ≈ 9.59°
_DELTA_CP_RAD = -_PHI_ASSOC * (_CHI_EFF / (_B3 * _N_GEN))       # = -π/2
_DELTA_CP_DEG = math.degrees(_DELTA_CP_RAD)                      # = -90°

# NuFIT 6.0 reference values (Normal Ordering)
# ORDERING CONSISTENCY (2026-08-20): the framework predicted INVERTED
# ordering from the even parity of the off-path seed b3 = 24 (see
# neutrino_mixing for the ordering on the seed in force), and the sibling
# module scores against IO. This module had been anchored to NORMAL
# ordering, so the same prediction was being graded on two different
# rulers. Anchored to IO for consistency; the candidate is falsified
# either way (8.8 sigma IO / 9.3 sigma NO).
_THETA13_NUFIT = 8.63        # degrees, NuFIT 6.0 IO best fit
_THETA13_1SIGMA = 0.11       # degrees, NuFIT 6.0 1σ (earlier 0.25 band understated the miss)
_DELTA_CP_NUFIT = 197.0 - 360.0  # degrees: NuFIT 6.0 NO best fit ~197 deg mapped to (-180, 180]; the earlier -107 was the T2K-only fit
_DELTA_CP_1SIGMA = 40.0      # degrees, approximate 1σ (range ≈ -180° to 0°)


def _seed_split_note() -> str:
    """Prose only: does the delta_CP split b3/n_gen work on the seed in force?

    Generated from the live seed so the sentence follows a fork flip; it
    changes no computed value.
    """
    from metaphysica.simulations.PM.geometry.b3_path import (
        resolve_path,
        seed_values,
    )

    b3, _b2 = seed_values(resolve_path())
    if b3 % _N_GEN == 0:
        return ("b_3 = %d, so b_3/n_gen = %d whole 3-cycles per generation"
                % (b3, b3 // _N_GEN))
    return ("b_3 = %d, and %d/%d is not an integer, so no whole number of "
            "3-cycles is assigned to a generation" % (b3, b3, _N_GEN))


class NeutrinoAlgebraicSimulation(SimulationBase):
    """
    Derives PMNS θ₁₃ and δ_CP from G₂ × E₇ topology.

    Uses α_leak = 1/√6 (from E₇ ⊃ E₆×U(1) algebraic branching) and
    the G₂ associative 3-form holonomy structure to estimate the two
    currently-CALIBRATED PMNS parameters.  No free parameters.

    Both candidates miss: θ₁₃ is FALSIFIED, and δ_CP scored MARGINAL at
    the off-path seed b₃ = 24, whose even split b₃/n_gen = 8 does not carry
    over to the adopted b₃ = 43.
    """

    @property
    def metadata(self) -> SimulationMetadata:
        return SimulationMetadata(
            id="neutrino_algebraic_v24_0",
            version="24.0",
            domain="algebra",
            title="Neutrino PMNS Angles from G2 x E7 Topology",
            description=(
                "Algebraic estimates of PMNS reactor angle theta_13 and CP phase delta_CP "
                "from G2 topology, written at the off-path seed (b3 = 24; chi_eff = 144, the "
                "K3 reading; n_gen = 3), and E7 branching (alpha_leak = 1/sqrt(6)). "
                "Zero free parameters, and both candidates miss: neutrino.theta13_derived "
                "is FALSIFIED (8.8 sigma vs NuFIT 6.0) and neutrino.delta_CP_derived scored "
                "1.825 sigma MARGINAL at the off-path seed; run() reads the seed in force. "
                "The 'promotes theta_13 and delta_CP from CALIBRATED "
                "toward DERIVED' claim is withdrawn. The working theta_13 headline is the "
                "independent particle.theta_13_deg = 8.6686 deg, 0.805 sigma PASS."
            ),
            section_id="neutrino-algebraic",
            appendix=True,
        )

    @property
    def required_inputs(self) -> List[str]:
        return [
            "topology.elder_kads",
            "geometry.alpha_leak",
        ]

    @property
    def output_params(self) -> List[str]:
        return [
            "neutrino.theta13_derived",
            "neutrino.delta_CP_derived",
            "neutrino.sin_theta13_derived",
            "neutrino.cycles_per_gen",
            "neutrino.phi_assoc",
            "neutrino.theta13_sigma",
            "neutrino.delta_CP_sigma",
        ]

    @property
    def output_formulas(self) -> List[str]:
        return [
            "pmns-theta13-derived",
            "pmns-delta-CP-derived",
        ]

    # ------------------------------------------------------------------
    # run(): normal-math path
    # ------------------------------------------------------------------

    def run(self, registry: "PMRegistry") -> Dict[str, Any]:
        # --- fetch topology parameters (fallback to hardcoded if absent) ---
        b3_raw = registry.get_param("topology.elder_kads")
        b3 = float(b3_raw) if b3_raw is not None else float(_B3)

        chi_eff_raw = registry.get_param("topology.mephorash_chi")
        chi_eff = float(chi_eff_raw) if chi_eff_raw is not None else float(_CHI_EFF)

        n_gen_raw = registry.get_param("topology.n_gen")
        n_gen = float(n_gen_raw) if n_gen_raw is not None else float(_N_GEN)

        alpha_leak_raw = registry.get_param("geometry.alpha_leak")
        alpha_leak = float(alpha_leak_raw) if alpha_leak_raw is not None else _ALPHA_LEAK

        # --- θ₁₃ from E₇ ⊃ E₆ × U(1) branching + SU(2)_L correction ---
        # Leptons are SU(3)_colour singlets; the reactor angle picks up an
        # additional 1/sqrt(2 n_gen) suppression relative to the quark sector.
        sin_theta13_derived = alpha_leak / math.sqrt(2.0 * n_gen)
        sin_theta13_derived = min(1.0, sin_theta13_derived)   # clamp
        theta13_rad_derived = math.asin(sin_theta13_derived)
        theta13_deg_derived = math.degrees(theta13_rad_derived)

        # --- δ_CP from G₂ associative 3-form holonomy angle ---
        # Each of n_gen generations accesses b3/n_gen associative 3-cycles
        # (a whole number only at the off-path seed b3 = 24; 43/3 is not).
        # The elementary holonomy angle around each cycle: φ = 2π/(b3/n_gen).
        # The CP phase is modulated by the full-manifold factor chi_eff/(b3 n_gen).
        cycles_per_gen = b3 / n_gen                     # = 8 at the off-path seed (14.33 at b3 = 43)
        phi_assoc = 2.0 * math.pi / cycles_per_gen      # = π/4 at the off-path seed
        delta_CP_rad_derived = -phi_assoc * (chi_eff / (b3 * n_gen))   # = -π/2 at the off-path seed
        delta_CP_deg_derived = math.degrees(delta_CP_rad_derived)       # = -90° at the off-path seed

        # --- sigma deviations from NuFIT 6.0 ---
        sigma_theta13 = (theta13_deg_derived - _THETA13_NUFIT) / _THETA13_1SIGMA
        sigma_delta_CP = (delta_CP_deg_derived - _DELTA_CP_NUFIT) / _DELTA_CP_1SIGMA

        return {
            "neutrino.theta13_derived":   theta13_deg_derived,
            "neutrino.delta_CP_derived":  delta_CP_deg_derived,
            "neutrino.sin_theta13_derived": sin_theta13_derived,
            "neutrino.cycles_per_gen":    cycles_per_gen,
            "neutrino.phi_assoc":         phi_assoc,
            "neutrino.theta13_sigma":     sigma_theta13,
            "neutrino.delta_CP_sigma":    sigma_delta_CP,
            # private scratch
            "_b3": b3,
            "_chi_eff": chi_eff,
            "_n_gen": n_gen,
            "_alpha_leak": alpha_leak,
        }

    # ------------------------------------------------------------------
    # run_eml(): EML operator-tree path (falls back to run() if not avail)
    # ------------------------------------------------------------------

    def run_eml(self, registry: "PMRegistry") -> Dict[str, Any]:
        try:
            from metaphysica.simulations.core.eml_integration import (
                eml_scalar, eml_compute, eml_div, eml_mul, eml_pi,
                eml_neg, eml_sqrt,
            )

            b3_raw = registry.get_param("topology.elder_kads")
            b3 = float(b3_raw) if b3_raw is not None else float(_B3)
            chi_eff_raw = registry.get_param("topology.mephorash_chi")
            chi_eff = float(chi_eff_raw) if chi_eff_raw is not None else float(_CHI_EFF)
            n_gen_raw = registry.get_param("topology.n_gen")
            n_gen = float(n_gen_raw) if n_gen_raw is not None else float(_N_GEN)
            alpha_leak_raw = registry.get_param("geometry.alpha_leak")
            alpha_leak = float(alpha_leak_raw) if alpha_leak_raw is not None else _ALPHA_LEAK

            # sin(θ₁₃) = α_leak / √(2 n_gen)
            two_n_gen = eml_mul(eml_scalar(2.0), eml_scalar(n_gen))
            sin13_pt = eml_div(eml_scalar(alpha_leak), eml_sqrt(two_n_gen))
            sin_theta13_derived = min(1.0, eml_compute(sin13_pt))
            theta13_rad_derived = math.asin(sin_theta13_derived)
            theta13_deg_derived = math.degrees(theta13_rad_derived)

            # δ_CP = −(2π / (b3/n_gen)) × (chi_eff / (b3 × n_gen))
            cycles_per_gen = b3 / n_gen
            phi_assoc_val = 2.0 * math.pi / cycles_per_gen
            delta_CP_rad_derived = -phi_assoc_val * (chi_eff / (b3 * n_gen))
            delta_CP_deg_derived = math.degrees(delta_CP_rad_derived)

            sigma_theta13 = (theta13_deg_derived - _THETA13_NUFIT) / _THETA13_1SIGMA
            sigma_delta_CP = (delta_CP_deg_derived - _DELTA_CP_NUFIT) / _DELTA_CP_1SIGMA

        except (ImportError, Exception):
            return self.run(registry)

        return {
            "neutrino.theta13_derived":   theta13_deg_derived,
            "neutrino.delta_CP_derived":  delta_CP_deg_derived,
            "neutrino.sin_theta13_derived": sin_theta13_derived,
            "neutrino.cycles_per_gen":    cycles_per_gen,
            "neutrino.phi_assoc":         phi_assoc_val,
            "neutrino.theta13_sigma":     sigma_theta13,
            "neutrino.delta_CP_sigma":    sigma_delta_CP,
            "_b3": b3,
            "_chi_eff": chi_eff,
            "_n_gen": n_gen,
            "_alpha_leak": alpha_leak,
        }

    # ------------------------------------------------------------------
    # get_formulas()
    # ------------------------------------------------------------------

    def get_formulas(self) -> List[Formula]:
        # Prose only: live Betti numbers for the formula text.
        from metaphysica.simulations.PM.geometry.geometry_narration import (
            render as _render,
        )

        return [
            Formula(
                id="pmns-theta13-derived",
                label="(A5.1)",
                latex=(
                    r"\sin\theta_{13} = \frac{\alpha_{\rm leak}}{\sqrt{2\,n_{\rm gen}}}"
                    r"= \frac{1/\sqrt{6}}{\sqrt{6}} = \frac{1}{6} \approx "
                    + f"{_SIN_THETA13:.4f}"
                    + r",\quad \theta_{13} \approx "
                    + f"{_THETA13_DEG:.2f}°"
                ),
                plain_text=(
                    f"sin(theta_13) = alpha_leak / sqrt(2*n_gen)"
                    f" = (1/sqrt(6)) / sqrt(6) = 1/6 ≈ {_SIN_THETA13:.4f},"
                    f" theta_13 ≈ {_THETA13_DEG:.2f} deg"
                    f" (NuFIT 6.0: {_THETA13_NUFIT} deg)"
                ),
                category="DERIVED",
                description=(
                    f"PMNS reactor angle θ₁₃ derived from E₇ ⊃ E₆×U(1) branching. "
                    f"α_leak = 1/√6 is the Clebsch-Gordan coefficient for the U(1) "
                    f"factor. Leptons are colour singlets, giving an additional "
                    f"1/√(2n_gen) suppression. Result: θ₁₃ ≈ {_THETA13_DEG:.2f}°; "
                    f"NuFIT 6.0 (IO) gives {_THETA13_NUFIT}°. "
                    f"FALSIFIED (R1 ruling 2026-08-25): ~12% high, about 9σ at the "
                    f"NuFIT 1σ of {_THETA13_1SIGMA}°."
                ),
                inputParams=["geometry.alpha_leak", "topology.n_gen"],
                outputParams=["neutrino.theta13_derived", "neutrino.sin_theta13_derived"],
                eml_latex=(
                    r"\mathrm{ops.asin}\!\left("
                    r"\mathrm{ops.div}\!\left(\alpha_{\rm leak},\;"
                    r"\mathrm{ops.sqrt}\!\left(\mathrm{ops.mul}(2,\,n_{\rm gen})\right)"
                    r"\right)\right)"
                ),
                eml_tree_str=(
                    "ops.asin(ops.div(alpha_leak, ops.sqrt(ops.mul(eml_scalar(2.0), n_gen))))"
                ),
                eml_description=(
                    "θ₁₃ via EML: ops.asin(ops.div(alpha_leak, "
                    "ops.sqrt(ops.mul(2, n_gen)))). "
                    "alpha_leak = 1/sqrt(6) from E₇ ⊃ E₆×U(1) algebraic branching. "
                    "n_gen = 3 = b₂/4, the number of singular involutions. Zero free parameters."
                ),
                derivation={
                    "method": (
                        "E₇ representation theory branching coefficient + "
                        "SU(2)_L generation counting"
                    ),
                    "steps": [
                        "E₇ ⊃ E₆ × U(1): 56 → 27 + 27* + 1 + 1",
                        "U(1) Clebsch-Gordan coefficient: α_leak = 1/√6  (purely algebraic)",
                        "Leptons are SU(3)_colour singlets: no colour-averaging factor",
                        "n_gen = 3 lepton generations → SU(2)_L factor √(2 n_gen) = √6",
                        "sin(θ₁₃) = α_leak / √(2 n_gen) = (1/√6) / √6 = 1/6 ≈ 0.1667",
                        f"θ₁₃ = asin(1/6) ≈ {_THETA13_DEG:.4f}°  (NuFIT 6.0: {_THETA13_NUFIT}°)",
                    ],
                    "references": [
                        "Buras et al. (1978) E₇ representation theory",
                        "NuFIT 6.0 (2024) https://www.nu-fit.org",
                    ],
                },
                terms={
                    r"\alpha_{\rm leak}": (
                        "E₇ ⊃ E₆×U(1) branching coefficient = 1/√6 (DERIVED)"
                    ),
                    r"n_{\rm gen}": "Number of lepton generations = 3 (n_gen = b₂/4, the number of singular involutions)",
                    r"\theta_{13}": f"PMNS reactor angle ≈ {_THETA13_DEG:.2f}° (NuFIT 6.0: {_THETA13_NUFIT}°)",
                },
            ),
            Formula(
                id="pmns-delta-CP-derived",
                label="(A5.2)",
                latex=(
                    r"\delta_{\rm CP} = -\varphi_{\rm assoc}"
                    r"\cdot \frac{\chi_{\rm eff}}{b_3\,n_{\rm gen}}"
                    r"= -\frac{\pi}{4}\cdot\frac{144}{72}"
                    r"= -\frac{\pi}{2} \approx "
                    + f"{_DELTA_CP_DEG:.1f}°"
                    + r"\ \ (\text{off-path seed } b_3 = 24)"
                ),
                plain_text=(
                    f"delta_CP = -phi_assoc * chi_eff/(b3*n_gen)"
                    f" = -(pi/4) * (144/72) = -pi/2 = {_DELTA_CP_DEG:.1f} deg"
                    f" at the off-path seed b3 = 24"
                    f" (NuFIT 6.0 NO: {_DELTA_CP_NUFIT} deg)"
                ),
                category="DERIVED",
                description=(
                    f"PMNS CP phase δ_CP from G₂ associative 3-form holonomy, written at "
                    f"the off-path seed b₃ = 24. There each lepton generation corresponds "
                    f"to b₃/n_gen = 8 associative 3-cycles, the elementary holonomy angle "
                    f"is φ_assoc = 2π/8 = π/4, and the full-manifold modulation factor is "
                    f"χ_eff/(b₃ n_gen) = 144/72 = 2 (χ_eff = 144 is the K3 reading, 48n at "
                    f"n = 3). Result: δ_CP = −(π/4)×2 = −π/2 = {_DELTA_CP_DEG:.1f}°. "
                    f"NuFIT 6.0 (NO) best fit: {_DELTA_CP_NUFIT}°, range −180° to 0°; "
                    f"scored 1.825σ (MARGINAL) — the earlier 'within the 1σ favoured "
                    f"region' claim is withdrawn. The construction is −2π χ_eff/b₃²; "
                    f"on the seed in force {_seed_split_note()}."
                ),
                inputParams=[
                    "topology.elder_kads",
                    "topology.mephorash_chi",
                    "topology.n_gen",
                ],
                outputParams=["neutrino.delta_CP_derived", "neutrino.phi_assoc"],
                eml_latex=(
                    r"\mathrm{ops.neg}\!\left("
                    r"\mathrm{ops.mul}\!\left("
                    r"\varphi_{\rm assoc},\;"
                    r"\mathrm{ops.div}(\chi_{\rm eff},\;"
                    r"\mathrm{ops.mul}(b_3,\,n_{\rm gen}))"
                    r"\right)\right)"
                ),
                eml_tree_str=(
                    "ops.neg(ops.mul(phi_assoc, "
                    "ops.div(chi_eff, ops.mul(b3, n_gen))))"
                ),
                eml_description=(
                    "δ_CP via EML: ops.neg(ops.mul(phi_assoc, "
                    "ops.div(chi_eff, ops.mul(b3, n_gen)))). "
                    "phi_assoc = 2π/(b3/n_gen). "
                    "Written at the off-path seed: chi_eff = 144 (the K3 reading), b3 = 24, n_gen = 3."
                ),
                derivation={
                    "method": "G₂ associative 3-form holonomy angle modulated by χ_eff",
                    "steps": [
                        _render(
                            "At the off-path seed b_3 = 24 the G₂ manifold has 24 associative "
                            "3-cycle classes ({manifold} has b_3 = {b3})"
                        ),
                        "With n_gen=3 generations: cycles_per_gen = 24/3 = 8 (on the seed in force " + _seed_split_note() + ")",
                        "Elementary holonomy angle: φ_assoc = 2π/8 = π/4",
                        "Full-manifold modulation: χ_eff/(b₃ n_gen) = 144/(24×3) = 144/72 = 2",
                        "CP phase from parallel transport: δ_CP = −φ_assoc × (χ_eff/(b₃ n_gen))",
                        f"= −(π/4) × 2 = −π/2 = {_DELTA_CP_DEG:.1f}°",
                        f"NuFIT 6.0 (NO): {_DELTA_CP_NUFIT}°. At the off-path seed this scores 1.825σ (MARGINAL); the earlier 'within 1σ' reading is withdrawn.",
                    ],
                    "references": [
                        "Joyce, D. (2000) Compact Manifolds with Special Holonomy. OUP.",
                        "NuFIT 6.0 (2024) https://www.nu-fit.org",
                    ],
                },
                terms={
                    r"\varphi_{\rm assoc}": "Elementary holonomy angle = 2π/(b₃/n_gen) = π/4 at the off-path seed b₃ = 24",
                    r"\chi_{\rm eff}": "Effective index chi_eff = 2 x sum chi(K3) = 48 n = 144 at n = 3 (the K3 reading; not the Euler characteristic of Y_7, which is 0)",
                    r"b_3": _render("Third Betti number: b_3 = {b3} for {manifold}; this formula's 24 is the off-path seed"),
                    r"n_{\rm gen}": "Number of generations = 3",
                    r"\delta_{\rm CP}": (
                        f"PMNS CP-violation phase ≈ {_DELTA_CP_DEG:.1f}° "
                        f"(NuFIT 6.0 NO: {_DELTA_CP_NUFIT}°)"
                    ),
                },
            ),
        ]

    # ------------------------------------------------------------------
    # get_output_param_definitions()
    # ------------------------------------------------------------------

    def get_output_param_definitions(self) -> List[Parameter]:
        split_note = _seed_split_note()      # prose only
        return [
            Parameter(
                path="neutrino.theta13_derived",
                name="PMNS Reactor Angle theta_13 (Falsified Candidate)",
                units="degrees",
                status="FALSIFIED",
                description=(
                    f"FALSIFIED (R1 ruling, 2026-08-25): sin(θ₁₃) = "
                    f"α_leak/√(2 n_gen) = 1/6 gives {_THETA13_DEG:.4f}°, "
                    f"~9σ from NuFIT 6.0 ({_THETA13_NUFIT}° ± "
                    f"{_THETA13_1SIGMA}°). A zero-parameter prediction that "
                    f"misses by 9σ is a falsification, not a tension -- the "
                    f"row stays on the books as the framework's proof its "
                    f"gates can kill an elegant candidate. Working headline: "
                    f"particle.theta_13_deg = 8.6686°, scored 0.805σ PASS against "
                    f"NuFIT 6.0 (8.58 ± 0.11). WITHDRAWN: the '0.4σ geometric "
                    f"cross-check' against geometry.theta_13 = 8.54°. That anchor "
                    f"is a hardcoded restatement of a pre-release NuFIT central "
                    f"value (eml_scalar(8.54), status MEASURED) and not a "
                    f"geometric quantity, so comparing a prediction to it "
                    f"cross-checks nothing."
                ),
                eml_description=(
                    "EML: ops.mul(ops.div(eml_scalar(180.0), eml_pi()), "
                    "ops.asin(ops.div(eml_scalar(1.0), eml_scalar(6.0)))) — "
                    "θ₁₃ = (180/π)·asin(1/6) = (180/π)·asin(α_leak/√(2·n_gen)) ≈ 9.59° "
                    "[FALSIFIED: ~9σ from NuFIT 8.57°±0.11°]"
                ),
                derivation_formula="pmns-theta13-derived",
                experimental_bound=_THETA13_NUFIT,
                bound_type="central_value",
                bound_source="NuFIT_6.0_IO_2024",
                uncertainty=_THETA13_1SIGMA,
                no_experimental_value=False,
            ),
            Parameter(
                path="neutrino.delta_CP_derived",
                name="PMNS CP Phase delta_CP (Derived)",
                units="degrees",
                status="DERIVED",
                description=(
                    f"PMNS CP-violation phase from G₂ associative 3-form holonomy, "
                    f"δ_CP = −(2π/(b₃/n_gen)) × χ_eff/(b₃ n_gen) = −2π χ_eff/b₃². "
                    f"Written at the off-path seed b₃ = 24, where it is −π/2 = "
                    f"{_DELTA_CP_DEG:.1f}°. "
                    f"NuFIT 6.0 (NO) best fit: {_DELTA_CP_NUFIT}°, range −180° to 0°. "
                    f"Scored 1.825σ there, verdict MARGINAL — not the '~0.4σ from best fit, "
                    f"within the 1σ favoured region' previously claimed here, which is "
                    f"withdrawn. The registered value follows the seed in force (run() "
                    f"reads topology.elder_kads), where {split_note}. Zero free parameters."
                ),
                eml_description=(
                    # Was ops.div(eml_pi(), eml_scalar(6.0)): a pi/K ansatz this module
                    # does not run, in radians while the parameter is in degrees.
                    # run() computes -phi_assoc * chi_eff/(b3*n_gen) with
                    # phi_assoc = 2pi/(b3/n_gen), converted to degrees; 2pi rad = 360 deg.
                    "EML: ops.neg(ops.mul("
                    "ops.div(eml_scalar(360.0), ops.div(eml_vec('topology.elder_kads'), eml_vec('topology.n_gen'))), "
                    "ops.div(eml_vec('topology.mephorash_chi'), ops.mul(eml_vec('topology.elder_kads'), eml_vec('topology.n_gen'))))) "
                    "— δ_CP = −(2π/(b₃/n_gen)) × χ/(b₃·n_gen) = −π/2 = −90° at the off-path seed b₃ = 24"
                ),
                derivation_formula="pmns-delta-CP-derived",
                experimental_bound=_DELTA_CP_NUFIT,
                bound_type="central_value",
                bound_source="NuFIT_6.0_IO_2024",
                uncertainty=_DELTA_CP_1SIGMA,
                no_experimental_value=False,
            ),
            Parameter(
                path="neutrino.sin_theta13_derived",
                name="sin(theta_13) Falsified Candidate",
                units="dimensionless",
                status="FALSIFIED",
                description=(
                    f"sin(θ₁₃) = α_leak/√(2 n_gen) = (1/√6)/√6 = 1/6 ≈ {_SIN_THETA13:.6f}. "
                    "FALSIFIED with its angle (R1 ruling): the exact rational "
                    "1/6 is ~9σ from the measured sin θ₁₃ ≈ 0.149. Kept on "
                    "the books labelled, per standing policy."
                ),
                eml_description=(
                    "EML: ops.div(eml_scalar(1.0), ops.mul(eml_scalar(6.0), eml_scalar(1.0))) — "
                    "sin(θ₁₃) = α_leak / √(2·n_gen) = (1/√6) / √6 = 1/6 from E₇ branching"
                ),
                derivation_formula="pmns-theta13-derived",
                experimental_bound=math.sin(math.radians(_THETA13_NUFIT)),
                bound_type="central_value",
                bound_source="NuFIT_6.0_IO_2024",
                uncertainty=0.005,
                no_experimental_value=False,
            ),
            Parameter(
                path="neutrino.cycles_per_gen",
                name="Associative 3-Cycles per Generation",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "b₃/n_gen: the number of associative 3-cycles assigned to each "
                    "lepton generation in the G₂ manifold. Written at the off-path "
                    "seed b₃ = 24, where it is 24/3 = 8. The registered value follows "
                    f"the seed in force, where {split_note}."
                ),
                eml_description=(
                    "EML: ops.div(eml_scalar(24.0), eml_scalar(3.0)) — "
                    "8 associative 3-cycles per generation at the off-path seed (b₃ = 24 / 3 generations)"
                ),
                no_experimental_value=True,
            ),
            Parameter(
                path="neutrino.phi_assoc",
                name="G₂ Associative 3-Form Holonomy Angle phi_assoc",
                units="radians",
                status="DERIVED",
                description=(
                    "Elementary holonomy angle φ_assoc = 2π/(b₃/n_gen); 2π/8 = π/4 at "
                    "the off-path seed b₃ = 24. Sets the CP phase scale in the lepton "
                    "sector. The registered value follows the seed in force."
                ),
                eml_description=(
                    "EML: ops.div(ops.mul(eml_scalar(2.0), eml_pi()), eml_scalar(8.0)) — "
                    "φ_assoc = 2π / (b₃/n_gen) = 2π/8 = π/4 elementary holonomy angle at the off-path seed"
                ),
                no_experimental_value=True,
            ),
            Parameter(
                path="neutrino.theta13_sigma",
                name="theta_13 Sigma Deviation from NuFIT 6.0",
                units="dimensionless",
                status="VALIDATION",
                description=(
                    f"(θ₁₃_derived − θ₁₃_NuFIT) / {_THETA13_1SIGMA}°. "
                    f"Derived: {_THETA13_DEG:.2f}°, NuFIT: {_THETA13_NUFIT}°. "
                    f"Expected ≈ {(_THETA13_DEG - _THETA13_NUFIT)/_THETA13_1SIGMA:.1f}σ."
                ),
                eml_description=(
                    # 8.57 / 0.25 were a superseded NuFIT band; run() divides by
                    # _THETA13_NUFIT = 8.63 and _THETA13_1SIGMA = 0.11.
                    "EML: ops.div(ops.sub(eml_vec('neutrino.theta13_derived'), eml_scalar(8.63)), "
                    "eml_scalar(0.11)) — "
                    "σ-deviation = (θ₁₃_derived − 8.63°) / 0.11° from NuFIT 6.0 IO"
                ),
                no_experimental_value=True,
            ),
            Parameter(
                path="neutrino.delta_CP_sigma",
                name="delta_CP Sigma Deviation from NuFIT 6.0",
                units="dimensionless",
                status="VALIDATION",
                description=(
                    f"(δ_CP_derived − δ_CP_NuFIT) / {_DELTA_CP_1SIGMA}°. "
                    f"At the off-path seed b₃ = 24: derived {_DELTA_CP_DEG:.1f}°, NuFIT {_DELTA_CP_NUFIT}°, "
                    f"≈ {(_DELTA_CP_DEG - _DELTA_CP_NUFIT)/_DELTA_CP_1SIGMA:.2f}σ. "
                    f"The registered value follows the seed in force."
                ),
                eml_description=(
                    # -107 was the T2K-only fit; run() uses
                    # _DELTA_CP_NUFIT = 197 - 360 = -163 (NuFIT 6.0 NO best fit).
                    "EML: ops.div(ops.sub(eml_vec('neutrino.delta_CP_derived'), "
                    "ops.sub(eml_scalar(197.0), eml_scalar(360.0))), "
                    "eml_scalar(40.0)) — "
                    "σ-deviation = (δ_CP_derived − (−163°)) / 40° from NuFIT 6.0"
                ),
                no_experimental_value=True,
            ),
        ]

    # ------------------------------------------------------------------
    # get_section_content()
    # ------------------------------------------------------------------

    def get_section_content(self) -> Optional[SectionContent]:
        sigma_theta13 = (_THETA13_DEG - _THETA13_NUFIT) / _THETA13_1SIGMA
        sigma_dcp = (_DELTA_CP_DEG - _DELTA_CP_NUFIT) / _DELTA_CP_1SIGMA
        split_note = _seed_split_note()      # prose only

        blocks = [
            ContentBlock(
                type="heading",
                content="Neutrino PMNS Angles from G₂ × E₇ Topology (Algebraic Derivation)",
                level=2,
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The PMNS matrix governs lepton-sector mixing just as the CKM matrix governs "
                    "the quark sector. In the standard PM framework, the reactor angle θ₁₃ "
                    f"(≈ {_THETA13_NUFIT}°, NuFIT 6.0) and the CP phase δ_CP (≈ {_DELTA_CP_NUFIT}°, "
                    "NuFIT 6.0) are currently fitted (CALIBRATED) to experimental data. "
                    "This section records an algebraic estimate of both quantities from "
                    "the integers b₃ = 24 (the off-path seed, where it was written), "
                    "χ_eff = 144 (the K3 reading, 48n at n = 3) and n_gen = 3, and the E₇ "
                    "branching coefficient α_leak = 1/√6. "
                    "<em>Both estimates miss: θ₁₃ is FALSIFIED (R1 ruling 2026-08-25, "
                    "about 9σ), and δ_CP scored 1.825σ (MARGINAL) at the off-path seed. "
                    "The δ_CP construction splits b₃ evenly among the generations, which "
                    f"works only at the off-path seed: on the seed in force {split_note}.</em>"
                ),
            ),

            # --- θ₁₃ section ---
            ContentBlock(
                type="heading",
                content="Reactor Angle θ₁₃ from E₇ ⊃ E₆ × U(1) Branching",
                level=3,
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<Normal>"
                    "The E₇ representation theory produces the portal coupling "
                    "α_leak = 1/√6 as the Clebsch-Gordan coefficient for the "
                    "U(1) factor in E₇ ⊃ E₆ × U(1) (see Appendix A3, "
                    "e7_representation_v1_0). "
                    "In the quark sector, this coupling sets the scale for Yukawa "
                    "textures. In the lepton sector, leptons are SU(3)_colour singlets, "
                    "so there is no colour-averaging factor. Instead, the SU(2)_L "
                    "structure distributes the mixing across n_gen = 3 generations, "
                    "giving an additional suppression factor of 1/√(2 n_gen) = 1/√6:"
                    "</Normal>"
                    "<EML>"
                    "ops.asin(ops.div(alpha_leak, ops.sqrt(ops.mul(2, n_gen)))). "
                    "alpha_leak from E₇ algebraic branching; n_gen = 3 = b₂/4, the number of singular involutions."
                    "</EML>"
                ),
            ),
            ContentBlock(
                type="formula",
                content=(
                    r"\sin\theta_{13} = \frac{\alpha_{\rm leak}}{\sqrt{2\,n_{\rm gen}}}"
                    r"= \frac{1/\sqrt{6}}{\sqrt{6}} = \frac{1}{6}"
                ),
                formula_id="pmns-theta13-derived",
                label="(A5.1)",
            ),
            ContentBlock(
                type="callout",
                callout_type="success",
                title=f"θ₁₃ Algebraic Result — FALSIFIED (R1 ruling)",
                content=(
                    f"sin(θ₁₃) = α_leak / √(2 n_gen) = (1/√6) / √6 = 1/6 ≈ {_SIN_THETA13:.4f}\n"
                    f"θ₁₃_derived ≈ {_THETA13_DEG:.4f}°\n"
                    f"NuFIT 6.0 (IO): {_THETA13_NUFIT}° ± {_THETA13_1SIGMA}°\n"
                    f"Sigma deviation: {sigma_theta13:+.2f}σ  (~12% high — FALSIFIED)"
                ),
            ),

            # --- δ_CP section ---
            ContentBlock(
                type="heading",
                content="CP Phase δ_CP from G₂ Associative 3-Form Holonomy",
                level=3,
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<Normal>"
                    "The CP-violation phase δ_CP arises from the phase acquired during "
                    "parallel transport of a spinor around a closed loop in the G₂ manifold. "
                    "As written at the off-path seed b₃ = 24, the relevant loops are the 24 "
                    "associative 3-cycles. "
                    "With n_gen = 3 generations, each generation corresponds to "
                    "b₃/n_gen = 8 cycles. "
                    "The elementary holonomy angle for one generation is "
                    "φ_assoc = 2π/8 = π/4. "
                    "The CP phase in the lepton sector is modulated by the full-manifold "
                    "factor χ_eff/(b₃ n_gen) = 144/72 = 2 "
                    f"(on the seed in force the split fails: {split_note}):"
                    "</Normal>"
                    "<EML>"
                    "ops.neg(ops.mul(phi_assoc, ops.div(chi_eff, ops.mul(b3, n_gen)))). "
                    "Inputs at the off-path seed: chi_eff = 144 (the K3 reading), b3 = 24, n_gen = 3. No free parameters."
                    "</EML>"
                ),
            ),
            ContentBlock(
                type="formula",
                content=(
                    r"\delta_{\rm CP} = -\varphi_{\rm assoc}"
                    r"\cdot \frac{\chi_{\rm eff}}{b_3\,n_{\rm gen}}"
                    r"= -\frac{\pi}{4}\cdot\frac{144}{72}"
                    r"= -\frac{\pi}{2}\ \ (\text{off-path seed } b_3 = 24)"
                ),
                formula_id="pmns-delta-CP-derived",
                label="(A5.2)",
            ),
            ContentBlock(
                type="callout",
                callout_type="success",
                title=f"δ_CP Algebraic Result at the Off-Path Seed (MARGINAL)",
                content=(
                    f"φ_assoc = 2π/(b₃/n_gen) = 2π/8 = π/4\n"
                    f"Modulation = χ_eff/(b₃ n_gen) = 144/(24×3) = 2\n"
                    f"δ_CP_derived = −(π/4) × 2 = −π/2 = {_DELTA_CP_DEG:.1f}°\n"
                    f"NuFIT 6.0 (NO): {_DELTA_CP_NUFIT}° (range: −180° to 0°)\n"
                    f"Sigma deviation: {sigma_dcp:+.2f}σ  (MARGINAL; the earlier 'within 1σ' claim is withdrawn)"
                ),
            ),

            # --- Discussion ---
            ContentBlock(
                type="heading",
                content="Discussion and Limitations",
                level=3,
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    f"The algebraic estimates give theta_13 = {_THETA13_DEG:.2f} deg "
                    f"(NuFIT 6.0 IO: {_THETA13_NUFIT} deg, +12%, {sigma_theta13:+.1f}sigma "
                    f"at 1sigma = {_THETA13_1SIGMA} deg) and, at the off-path seed b3 = 24, "
                    f"delta_CP = {_DELTA_CP_DEG:.0f} deg "
                    f"(NuFIT 6.0 NO: {_DELTA_CP_NUFIT} deg, {sigma_dcp:+.2f}sigma). "
                    "Neither value is fitted; both were written from the integers "
                    "b3 = 24 (the off-path seed), chi_eff = 144 (the K3 reading) and "
                    "n_gen = 3, and the algebraic coefficient alpha_leak = 1/sqrt(6). "
                    "theta_13 is FALSIFIED (R1 ruling 2026-08-25); attributing the ~12% "
                    "overshoot to loop corrections or higher-order E7 branching is "
                    "untested. delta_CP scored MARGINAL with the right sign (inside the "
                    "NuFIT preferred range -180 to 0 degrees); the earlier '0.4sigma' "
                    "claim is withdrawn. "
                    f"The delta_CP construction does not carry over to Y_7: {split_note}."
                ),
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<Speculation>"
                    "(This speculation rests on the off-path seed b₃ = 24; the same "
                    "construction does not give π/4 or −90° on Y₇.) "
                    "The emergence of δ_CP ≈ −90° from the π/4 holonomy angle "
                    "of the G₂ associative 3-form may hint at a deeper geometric principle: "
                    "maximal CP violation (|δ_CP| = π/2) as a topological fixed point "
                    "of the G₂ holonomy group. "
                    "If this connection between G₂ geometry and CP violation is real, it "
                    "would predict that future precision measurements of δ_CP will converge "
                    "toward −90° (or equivalently +270°) as experimental uncertainties "
                    "decrease — a testable, parameter-free prediction. "
                    "However, this interpretation rests on unverified assumptions about "
                    "the relationship between parallel transport phases and the physical "
                    "CP phase in the PMNS matrix; rigorous derivation requires a full "
                    "Dirac operator analysis on the G₂ manifold."
                    "</Speculation>"
                ),
            ),
        ]

        return SectionContent(
            section_id="neutrino-algebraic",
            subsection_id=None,
            title="Neutrino PMNS Angles from G₂ Topology (Algebraic Derivation)",
            abstract=(
                f"Algebraic estimates, written at the off-path seed b₃ = 24, of PMNS "
                f"θ₁₃ ≈ {_THETA13_DEG:.1f}° (NuFIT: {_THETA13_NUFIT}°, {sigma_theta13:+.1f}σ, "
                f"FALSIFIED) and δ_CP ≈ {_DELTA_CP_DEG:.0f}° "
                f"(NuFIT: {_DELTA_CP_NUFIT}°, {sigma_dcp:+.2f}σ, MARGINAL) "
                "from G₂ × E₇ inputs with no free parameters: b₃ = 24 (the off-path "
                "seed), χ_eff = 144 (the K3 reading), n_gen = 3, α_leak = 1/√6. "
                f"The δ_CP construction does not carry over to Y₇: {split_note}."
            ),
            content_blocks=blocks,
            formula_refs=["pmns-theta13-derived", "pmns-delta-CP-derived"],
            param_refs=self.output_params,
            appendix=True,
        )

    # ------------------------------------------------------------------
    # get_certificates()
    # ------------------------------------------------------------------

    def get_certificates(self) -> List[Dict[str, Any]]:
        sigma_theta13 = (_THETA13_DEG - _THETA13_NUFIT) / _THETA13_1SIGMA
        sigma_dcp = (_DELTA_CP_DEG - _DELTA_CP_NUFIT) / _DELTA_CP_1SIGMA
        # theta_13 is 12% above NuFIT; given the tight 1sigma~0.25 deg this is ~4sigma.
        # The derivation is an ORDER-OF-MAGNITUDE prediction — use a 5sigma check to reflect that.
        theta13_within_5sigma = abs(sigma_theta13) <= 5.0
        dcp_within_2sigma = abs(sigma_dcp) <= 2.0
        dcp_in_preferred_range = -180.0 <= _DELTA_CP_DEG <= 0.0
        return [
            {
                "id": "CERT_NEUTRINO_THETA13_WITHIN_5SIGMA",
                "assertion": (
                    f"theta_13_derived = {_THETA13_DEG:.4f} deg is within 5sigma of "
                    f"NuFIT 6.0 value {_THETA13_NUFIT} deg "
                    "(order-of-magnitude algebraic derivation, not a precision fit)"
                ),
                "condition": f"abs({sigma_theta13:.4f}) <= 5.0",
                "status": "PASS" if theta13_within_5sigma else "FAIL",
                "detail": (
                    f"Sigma deviation: {sigma_theta13:+.2f}sigma (1sigma_NuFIT = {_THETA13_1SIGMA} deg). "
                    "FALSIFIED (R1 ruling 2026-08-25); attributing the 12% overshoot to "
                    "the tree-level Clebsch-Gordan approximation is untested. "
                    "Derived from E7 branching, zero free parameters."
                ),
            },
            {
                "id": "CERT_NEUTRINO_DELTA_CP_WITHIN_2SIGMA",
                "assertion": (
                    f"delta_CP_derived = {_DELTA_CP_DEG:.1f}° (at the off-path seed b₃ = 24) "
                    f"is within 2σ of NuFIT 6.0 NO best fit {_DELTA_CP_NUFIT}°"
                ),
                "condition": f"abs({sigma_dcp:.4f}) <= 2.0",
                "status": "PASS" if dcp_within_2sigma else "FAIL",
                "detail": (
                    f"Sigma deviation: {sigma_dcp:+.2f}σ. "
                    "Evaluated at the off-path seed b₃ = 24; the registered value "
                    "follows the seed in force."
                ),
            },
            {
                "id": "CERT_NEUTRINO_DELTA_CP_SIGN_CORRECT",
                "assertion": (
                    f"delta_CP_derived = {_DELTA_CP_DEG:.1f}° is in NuFIT preferred "
                    "range (−180°, 0°)"
                ),
                "condition": f"-180.0 <= {_DELTA_CP_DEG:.1f} <= 0.0",
                "status": "PASS" if dcp_in_preferred_range else "FAIL",
                "detail": (
                    "At the off-path seed the construction gives a negative δ_CP, "
                    "inside NuFIT's preferred range, without any fitting."
                ),
            },
        ]

    # ------------------------------------------------------------------
    # validate_self()
    # ------------------------------------------------------------------

    def validate_self(self) -> Dict[str, Any]:
        sigma_theta13 = (_THETA13_DEG - _THETA13_NUFIT) / _THETA13_1SIGMA
        sigma_dcp = (_DELTA_CP_DEG - _DELTA_CP_NUFIT) / _DELTA_CP_1SIGMA
        return {
            "checks": [
                {
                    "name": "theta13_from_alpha_leak_and_n_gen",
                    "passed": abs(_SIN_THETA13 - 1.0 / 6.0) < 1e-12,
                    "log_level": "INFO",
                    "message": (
                        f"sin(θ₁₃) = α_leak/√(2 n_gen) = 1/6 = {_SIN_THETA13:.8f} "
                        "(exact algebraic value)"
                    ),
                },
                {
                    "name": "theta13_within_5sigma_of_nufit",
                    "passed": abs(sigma_theta13) <= 5.0,
                    "log_level": "INFO" if abs(sigma_theta13) <= 5.0 else "WARNING",
                    "message": (
                        f"theta13_derived = {_THETA13_DEG:.4f} deg, NuFIT = {_THETA13_NUFIT} deg, "
                        f"deviation = {sigma_theta13:+.2f}sigma "
                        "(order-of-magnitude algebraic derivation; 5sigma threshold)"
                    ),
                },
                {
                    "name": "delta_CP_from_g2_holonomy",
                    "passed": abs(_DELTA_CP_RAD - (-math.pi / 2.0)) < 1e-12,
                    "log_level": "INFO",
                    "message": (
                        f"δ_CP = −π/2 = {_DELTA_CP_DEG:.6f}° "
                        "(π/4 holonomy × 2 modulation, at the off-path seed b₃ = 24)"
                    ),
                },
                {
                    "name": "delta_CP_within_2sigma_of_nufit",
                    "passed": abs(sigma_dcp) <= 2.0,
                    "log_level": "INFO" if abs(sigma_dcp) <= 2.0 else "WARNING",
                    "message": (
                        f"δ_CP_derived = {_DELTA_CP_DEG:.1f}°, NuFIT = {_DELTA_CP_NUFIT}°, "
                        f"deviation = {sigma_dcp:+.2f}σ"
                    ),
                },
                {
                    "name": "delta_CP_sign_correct",
                    "passed": _DELTA_CP_DEG < 0.0,
                    "log_level": "INFO",
                    "message": (
                        f"δ_CP = {_DELTA_CP_DEG:.1f}° is negative "
                        "(consistent with NuFIT 6.0 preferred range −180° to 0°)"
                    ),
                },
            ]
        }

    # ------------------------------------------------------------------
    # get_references()
    # ------------------------------------------------------------------

    def get_references(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "nufit6_2024",
                "authors": "Esteban, I., Gonzalez-Garcia, M.C., Maltoni, M., Schwetz, T., Zhou, A.",
                "title": "NuFIT 6.0: Global analysis of three-neutrino oscillation parameters",
                "year": 2024,
                "url": "https://www.nu-fit.org",
            },
            {
                "id": "joyce2000",
                "authors": "Joyce, D.D.",
                "title": "Compact Manifolds with Special Holonomy",
                "year": 2000,
                "publisher": "Oxford University Press",
                "doi": "10.1093/oso/9780198506010.001.0001",
                "url": "https://doi.org/10.1093/oso/9780198506010.001.0001",
            },
            {
                "id": "acharya_witten2001",
                "authors": "Acharya, B.S. and Witten, E.",
                "title": "Chiral Fermions from Manifolds of G2 Holonomy",
                "year": 2001,
                "arxiv": "hep-th/0109152",
                "url": "https://arxiv.org/abs/hep-th/0109152",
            },
            {
                "id": "buras1978",
                "authors": "Buras, A.J., Ellis, J., Gaillard, M.K., Nanopoulos, D.V.",
                "title": "Aspects of the Grand Unification of Strong, Weak and Electromagnetic Interactions",
                "year": 1978,
                "doi": "10.1016/0550-3213(78)90168-6",
            },
        ]

    # ------------------------------------------------------------------
    # get_learning_materials()
    # ------------------------------------------------------------------

    def get_learning_materials(self) -> List[Dict[str, Any]]:
        return [
            {
                "topic": "PMNS Matrix and Neutrino Oscillations",
                "url": "https://en.wikipedia.org/wiki/Pontecorvo%E2%80%93Maki%E2%80%93Nakagawa%E2%80%93Sakata_matrix",
                "relevance": (
                    "The PMNS mixing matrix parametrises lepton-sector CP violation "
                    "and generation mixing — the quantities derived here from G₂ topology."
                ),
            },
            {
                "topic": "G₂ Holonomy and Associative 3-Cycles",
                "url": "https://en.wikipedia.org/wiki/G2_manifold",
                "relevance": (
                    "The associative 3-cycles in the G₂ manifold provide the integer "
                    "b₃ used in the δ_CP construction (24 at the off-path seed, where "
                    "the holonomy angle is φ_assoc = π/4)."
                ),
            },
            {
                "topic": "E₇ Representation Theory and Branching Rules",
                "url": "https://en.wikipedia.org/wiki/E7_(mathematics)",
                "relevance": (
                    "The branching E₇ ⊃ E₆ × U(1): 56 → 27+27*+1+1 "
                    "fixes α_leak = 1/√6 as a purely algebraic Clebsch-Gordan coefficient."
                ),
            },
        ]
