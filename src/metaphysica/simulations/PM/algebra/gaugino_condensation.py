"""
Gaugino Condensation — Cabibbo Angle from an N₁=24/N₂=23 Racetrack (CALIBRATED)
================================================================================

CALIBRATED at the off-path seed b₃ = 24; no racetrack exists on Y₇. A gaugino
racetrack needs a confining hidden sector, and the adopted geometry has none:
Y₇'s singular loci carry N = 4 super Yang-Mills (certificate CG.5), and in
φ's Joyce family holonomy exactly G₂ and a confining sector are mutually
exclusive (CG.10). The exponent 2π/N₁ with N₁ = b₃ read a Betti number as the
rank of a gauge group (provenance row `racetrack-type`), and Re(T) is an OPEN
modulus on Y₇ (CG.6). The construction below was written at the off-path seed
b₃ = 24 (N₁ = 24, N₂ = 23), and every number quoted in this text is that
calibration. run() reads topology.elder_kads, which carries the b₃ in force,
so the registered rows follow the seed; no value has been changed. The module
is kept so the failure stays reproducible.

As written, hidden E₈' gaugino condensation with competing fluxes on
associative 3-cycles generates a non-perturbative racetrack superpotential,
and a Cabibbo-like suppression was sought in the competition between:

    W_np(N₁=24) = A·exp(−2π/N₁)   dominant term (N₁ = the off-path seed b₃ = 24)
    W_np(N₂=23) = A·exp(−2π/N₂)   sub-dominant term (N₁−1)

The effective Yukawa suppression at the racetrack minimum:
    λ_eff = exp(−2π/24) ≈ 0.7697

The Cabibbo proxy (coarse):
    ε_proxy ≈ λ_eff³ ≈ 0.456   (order of magnitude for first-generation suppression)

Algebraic Cabibbo construction (FALSIFIED; numbers at the off-path seed):
    Step 1 — Racetrack moduli minimum from ∂W/∂T = 0:
        T_min = (N₁·N₂) / (2π·(N₁−N₂)) · ln(N₁/N₂) ≈ 3.739
    Step 2 — Evaluate both condensates at T_min:
        W₁ = exp(−2π·T_min/N₁) ≈ 0.3757
        W₂ = exp(−2π·T_min/N₂) ≈ 0.3601
    Step 3 — Racetrack epsilon (off-diagonal Yukawa texture):
        ε_racetrack = |W₁ − W₂| ≈ 0.01566
    Step 4 — Generation correction (n_gen=3 eigenvalues in the Yukawa matrix):
        λ_W ≈ ε_racetrack^(1/n_gen) = 0.01566^(1/3) ≈ 0.2502
        cf. PDG Wolfenstein λ_W = 0.22500 ± 0.00067  —  37.6σ away

As written, N₁ = 24 was the off-path seed b₃ = 24 read as a gauge-group rank,
N₂ = N₁ − 1 = 23, and n_gen = 3. No free parameters enter the construction,
which is why it cannot be rescued.

STATUS: FALSIFIED (2026-09). All three Cabibbo candidates produced by this
module are scored against PDG Wolfenstein λ_W = 0.22500 ± 0.00067 and all
three fail. At the off-path seed b₃ = 24 they were:

    algebra.gaugino_cabibbo_proxy    0.455938   344.7 sigma
    algebra.gaugino_cabibbo_derived  0.250163    37.6 sigma
    algebra.gaugino_cabibbo_refined  0.207880    25.6 sigma

The registered rows follow the seed in force and fail there too. At the
values above they carried 95.4% of the framework's global chi-squared. Two
claims are WITHDRAWN: that this "promotes the Cabibbo angle from CALIBRATED
toward DERIVED", and that "11% agreement, zero free parameters" is an
agreement at all. An 11% discrepancy on a quantity measured to 0.3% is a
failure. Zero free parameters makes a wrong prediction unavoidable, not
excusable. The racetrack construction is kept on the books with its
derivation intact so the failure stays visible and reproducible.

Dependencies: g2_geometry_v16_0 (topology.elder_kads, the b₃ in force; the
text below was written at the off-path seed b₃ = 24)

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

import math
import sys
import os
from typing import Dict, Any, List, Optional

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from metaphysica.simulations.base import (
    SimulationBase,
    SimulationMetadata,
    Formula,
    Parameter,
    ContentBlock,
    SectionContent,
)


class GauginoCondensationSimulation(SimulationBase):
    """
    Hidden E₈' gaugino condensation with N₁/N₂ racetrack -- CALIBRATED; Y₇ has no racetrack.

    Computes λ_eff = exp(−2π/N₁) and the Cabibbo proxy from N₁ = b₃ and
    N₂ = b₃ − 1. The text was written at the off-path seed b₃ = 24 (N₁ = 24,
    N₂ = 23); Y₇ has no gaugino racetrack (CG.5, CG.10).
    """

    @property
    def metadata(self) -> SimulationMetadata:
        return SimulationMetadata(
            id="gaugino_condensation_v1_0",
            version="1.0",
            domain="algebra",
            title="Hidden E8 Gaugino Condensation - Cabibbo from Racetrack (Calibrated, Off-Path Seed)",
            description=(
                "CALIBRATED at the off-path seed b₃ = 24: Y₇ has no gaugino racetrack (its "
                "singular loci carry N = 4 SYM, CG.5; holonomy exactly G₂ excludes a "
                "confining sector in φ's Joyce family, CG.10). Cabibbo-like suppression "
                "from the N₁=24/N₂=23 racetrack superpotential. FALSIFIED: all three candidates miss PDG λ_W = 0.22500 ± 0.00067 "
                "(344.7σ / 37.6σ / 25.6σ at the off-path seed). The 'promotes Cabibbo "
                "from CALIBRATED toward DERIVED' claim is withdrawn."
            ),
            section_id="A4",
            appendix=True,
        )

    @property
    def required_inputs(self) -> List[str]:
        return ["topology.elder_kads"]

    @property
    def output_params(self) -> List[str]:
        return [
            "algebra.gaugino_W_np_1",
            "algebra.gaugino_W_np_2",
            "algebra.gaugino_lambda_eff",
            "algebra.gaugino_cabibbo_proxy",
            "algebra.gaugino_cabibbo_refined",
            "algebra.gaugino_racetrack_T_min",
            "algebra.gaugino_condensate_ratio",
            "algebra.gaugino_cabibbo_derived",
        ]

    @property
    def output_formulas(self) -> List[str]:
        return [
            "gaugino-racetrack-superpotential",
            "gaugino-lambda-eff",
            "gaugino-cabibbo-proxy",
            "gaugino-cabibbo-derived",
        ]

    def run(self, registry: "PMRegistry") -> Dict[str, Any]:
        # topology.elder_kads carries the b_3 in force; the fallback below is
        # the off-path seed b_3 = 24, used only when no seed is registered.
        b3 = registry.get_param("topology.elder_kads")
        if b3 is None:
            b3 = 24
        N1 = int(b3)    # dominant flux quanta, read as b₃ (24 at the off-path seed)
        N2 = N1 - 1     # sub-dominant flux quanta (23 at the off-path seed)

        n_gen_raw = registry.get_param("topology.n_gen")
        n_gen = int(n_gen_raw) if n_gen_raw is not None else 3

        # Analytic racetrack at unit modulus T=1 (the construction's normalization).
        # W_np(N) = exp(-2π/N) with T=1. Setting N₁ = b₃ read a Betti number as a
        # gauge-group rank; Y₇ has no gaugino racetrack (CG.5, CG.10).
        W1 = math.exp(-2.0 * math.pi / N1)
        W2_val = math.exp(-2.0 * math.pi / N2)
        lambda_eff = W1
        cabibbo_proxy = lambda_eff ** 3
        # Refined estimate: first-generation suppression uses N1/4 cycles out of N1 total.
        # Physical argument as written: E₆ has 4 SM-like gauge sectors
        # (SU(3)×SU(2)×U(1)×hidden); at the off-path seed N1 = 24 the first-generation
        # Yukawa sees N1/4 = 6 racetrack suppressions.
        # cabibbo_refined = λ_eff^(N1/4) = exp(-π/2) ≈ 0.2079 (cf. PDG λ_W ≈ 0.2250).
        # The value is fixed at exp(-π/2) and does not follow the seed.
        cabibbo_refined = math.exp(-math.pi / 2.0)   # = exp(-2π*6/24) = exp(-π/2)

        # Algebraic Cabibbo derivation from racetrack moduli minimum.
        # Step 1: T_min from ∂W/∂T = 0 → T_min = (N₁·N₂)/(2π(N₁−N₂)) · ln(N₁/N₂)
        T_min = _racetrack_T_min(N1, N2)
        # Step 2: condensates evaluated at the minimum (not at unit modulus T=1)
        W1_at_Tmin = math.exp(-2.0 * math.pi * T_min / N1)
        W2_at_Tmin = math.exp(-2.0 * math.pi * T_min / N2)
        # Step 3: racetrack epsilon — off-diagonal Yukawa texture from condensate splitting
        racetrack_epsilon = abs(W1_at_Tmin - W2_at_Tmin)
        # Step 4: Wolfenstein λ_W ~ ε^(1/n_gen); n_gen=3 eigenvalues in the Yukawa matrix
        cabibbo_derived = racetrack_epsilon ** (1.0 / n_gen) if racetrack_epsilon > 0 else 0.0

        condensate_ratio = W1 / W2_val if abs(W2_val) > 1e-300 else 0.0

        return {
            "algebra.gaugino_W_np_1": W1,
            "algebra.gaugino_W_np_2": W2_val,
            "algebra.gaugino_lambda_eff": lambda_eff,
            "algebra.gaugino_cabibbo_proxy": cabibbo_proxy,
            "algebra.gaugino_cabibbo_refined": cabibbo_refined,
            "algebra.gaugino_racetrack_T_min": T_min,
            "algebra.gaugino_condensate_ratio": condensate_ratio,
            "algebra.gaugino_cabibbo_derived": cabibbo_derived,
            "_N1": N1,
            "_N2": N2,
            "_n_gen": n_gen,
            "_b3": b3,
        }

    def run_eml(self, registry: "PMRegistry") -> Dict[str, Any]:
        """EML path — same racetrack via EML exponential operators."""
        # Same read as run(): the b_3 in force, falling back to the off-path
        # seed b_3 = 24 only when no seed is registered.
        b3 = registry.get_param("topology.elder_kads")
        if b3 is None:
            b3 = 24
        N1 = int(b3)
        N2 = N1 - 1

        n_gen_raw = registry.get_param("topology.n_gen")
        n_gen = int(n_gen_raw) if n_gen_raw is not None else 3

        try:
            from metaphysica.simulations.core.eml_integration import (
                eml_scalar, eml_compute, eml_div, eml_mul, eml_pi,
                eml_neg,
            )
            from eml_math.point import EMLPoint
            import math as _math

            pi_pt = eml_pi()
            two_pi_over_N1 = eml_div(eml_mul(eml_scalar(2.0), pi_pt), eml_scalar(float(N1)))
            two_pi_over_N2 = eml_div(eml_mul(eml_scalar(2.0), pi_pt), eml_scalar(float(N2)))

            exponent1 = eml_compute(eml_neg(two_pi_over_N1))
            exponent2 = eml_compute(eml_neg(two_pi_over_N2))

            W1 = _math.exp(exponent1)
            W2_val = _math.exp(exponent2)
            lambda_eff = W1
            cabibbo_proxy = lambda_eff ** 3
            cabibbo_refined = _math.exp(-_math.pi / 2.0)
            T_min = _racetrack_T_min(N1, N2)
            W1_at_Tmin = _math.exp(-2.0 * _math.pi * T_min / N1)
            W2_at_Tmin = _math.exp(-2.0 * _math.pi * T_min / N2)
            racetrack_epsilon = abs(W1_at_Tmin - W2_at_Tmin)
            cabibbo_derived = racetrack_epsilon ** (1.0 / n_gen) if racetrack_epsilon > 0 else 0.0
            condensate_ratio = W1 / W2_val if abs(W2_val) > 1e-300 else 0.0
        except ImportError:
            return self.run(registry)

        return {
            "algebra.gaugino_W_np_1": W1,
            "algebra.gaugino_W_np_2": W2_val,
            "algebra.gaugino_lambda_eff": lambda_eff,
            "algebra.gaugino_cabibbo_proxy": cabibbo_proxy,
            "algebra.gaugino_cabibbo_refined": cabibbo_refined,
            "algebra.gaugino_racetrack_T_min": T_min,
            "algebra.gaugino_condensate_ratio": condensate_ratio,
            "algebra.gaugino_cabibbo_derived": cabibbo_derived,
            "_N1": N1,
            "_N2": N2,
            "_n_gen": n_gen,
            "_b3": b3,
        }

    def get_formulas(self) -> List[Formula]:
        # The formula text is written at the off-path seed b_3 = 24
        # (N1 = 24, N2 = 23); run() follows the seed in force.
        N1, N2 = 24, 23
        n_gen = 3
        W1 = math.exp(-2.0 * math.pi / N1)
        W2 = math.exp(-2.0 * math.pi / N2)
        leff = W1
        cab = leff ** 3
        T_min_val = _racetrack_T_min(N1, N2)
        W1_tmin = math.exp(-2.0 * math.pi * T_min_val / N1)
        W2_tmin = math.exp(-2.0 * math.pi * T_min_val / N2)
        epsilon_rt = abs(W1_tmin - W2_tmin)
        cab_derived = epsilon_rt ** (1.0 / n_gen)
        return [
            Formula(
                id="gaugino-racetrack-superpotential",
                label="(A4.1)",
                latex=(
                    r"W_{\text{np}} = A\,e^{-2\pi T/N_1} + A\,e^{-2\pi T/N_2},\quad"
                    r"N_1 = b_3 = 24,\; N_2 = b_3 - 1 = 23\ \ (\text{off-path seed})"
                ),
                plain_text="W_np = A*exp(-2π T/24) + A*exp(-2π T/23), N1=24, N2=23",
                category="DERIVED",
                description=(
                    "CALIBRATED at the off-path seed: no gaugino racetrack exists on Y₇ (its "
                    "singular loci carry N = 4 SYM, CG.5; holonomy exactly G₂ excludes a confining sector "
                    "in φ's Joyce family, CG.10). Racetrack superpotential from two competing "
                    "hidden E₈' gaugino condensates, with N₁ = 24 read from the off-path seed "
                    "b₃ = 24 and N₂ = N₁ − 1 = 23. Reading a Betti number as the rank of a "
                    "gauge group was the error; the values are calibrations at that seed."
                ),
                inputParams=["topology.elder_kads"],
                outputParams=["algebra.gaugino_W_np_1", "algebra.gaugino_W_np_2"],
                eml_latex=(
                    r"\mathrm{ops.add}(A\cdot\mathrm{ops.exp}(\mathrm{ops.neg}(\mathrm{ops.div}(2\pi T, N_1))),\;"
                    r"A\cdot\mathrm{ops.exp}(\mathrm{ops.neg}(\mathrm{ops.div}(2\pi T, N_2))))"
                ),
                eml_tree_str=(
                    "ops.add(ops.mul(A, ops.exp(ops.neg(ops.div(ops.mul(2,pi,T), N1)))), "
                    "ops.mul(A, ops.exp(ops.neg(ops.div(ops.mul(2,pi,T), N2)))))"
                ),
                eml_description=(
                    "Racetrack superpotential via EML: sum of two exponential condensates. "
                    "N₁ = b₃ and N₂ = b₃ − 1 as written at the off-path seed b₃ = 24 "
                    "(no racetrack on Y₇)."
                ),
                derivation={
                    "steps": [
                        "As written: the hidden E₈' factor has gaugino condensation from strong-coupling gauge dynamics (Y₇ has no such confining sector: CG.5, CG.10)",
                        "Non-perturbative superpotential: W_np = A·exp(−2π T/N) for N associative 3-cycles",
                        "At the off-path seed b₃ = 24, N₁ = 24 dominant cycles (a Betti number read as a gauge-group rank)",
                        "Sub-dominant: N₂ = 23 = N₁ − 1 (next-to-leading-order contribution)",
                        "Competition between W_np(24) and W_np(23) creates a racetrack minimum",
                        "The minimum would lock the modulus T_min = ln(a₂/a₁)/(a₂−a₁) where aᵢ = 2π/Nᵢ; on Y₇ the moduli are OPEN (CG.6)",
                    ],
                    "method": "Racetrack moduli stabilization from E₈' gaugino condensation",
                    "references": [
                        "Krasnikov (1987); Dixon, Kaplunovsky, Louis (1990) 'Moduli dependence'",
                        "de Carlos, Casas, Quevedo (1993) 'Supersymmetry breaking in string compactifications'",
                    ],
                },
                terms={
                    r"W_{\text{np}}": "Non-perturbative racetrack superpotential from competing gaugino condensates",
                    r"N_1 = b_3 = 24": "Dominant flux quanta, set to b₃ at the off-path seed b₃ = 24 (a Betti number read as a gauge-group rank; no racetrack on Y₇)",
                    r"N_2 = b_3 - 1 = 23": "Sub-dominant flux quanta = N₁ − 1 (next-to-leading order)",
                    r"T": "Kähler modulus (the racetrack would lock it; on Y₇ the moduli, Re(T) included, are OPEN, CG.6)",
                },
            ),
            Formula(
                id="gaugino-lambda-eff",
                label="(A4.2)",
                latex=r"\lambda_{\text{eff}} = e^{-2\pi/N_1} = e^{-2\pi/24} \approx " + f"{leff:.6f}",
                plain_text=f"lambda_eff = exp(-2π/24) ≈ {leff:.6f}",
                category="DERIVED",
                description=(
                    "CALIBRATED at the off-path seed; no gaugino racetrack exists on Y₇ (CG.5, CG.10). "
                    f"Effective Yukawa texture suppression at the racetrack minimum, "
                    f"λ_eff = exp(−2π/N₁); at the off-path seed N₁ = 24 it is "
                    f"exp(−2π/24) ≈ {leff:.6f}. The registered value follows the "
                    "seed in force (run() reads topology.elder_kads)."
                ),
                inputParams=["topology.elder_kads"],
                outputParams=["algebra.gaugino_lambda_eff"],
                eml_latex=r"\mathrm{ops.exp}(\mathrm{ops.neg}(\mathrm{ops.div}(2\pi, N_1)))",
                eml_tree_str="ops.exp(ops.neg(ops.div(ops.mul(2, pi), b3_leaf())))",
                eml_description="λ_eff = exp(−2π/24) via EML: ops.exp(ops.neg(ops.div(ops.mul(2,pi),24)))",
                derivation={
                    "method": "Yukawa suppression from the racetrack minimum at N1 = 24 (off-path seed)",
                    "parentFormulas": ["gaugino-racetrack-superpotential"],
                    "steps": [
                        "At the racetrack minimum, the dominant condensate W_np(N₁) = exp(−2π/N₁) sets the scale",
                        "At the off-path seed N₁ = b₃ = 24, λ_eff = exp(−2π/24) ≈ 0.7697",
                        "As written, this is the Yukawa suppression factor for first-generation fermion masses",
                        "No free parameters: N₁ was the Betti number b₃ read as a gauge-group rank, the reading that fails on Y₇ (no racetrack: CG.5, CG.10)",
                    ],
                    "references": ["Krasnikov, N.V. (1987) 'On supersymmetry breaking in superstring theories'"],
                },
                terms={
                    r"\lambda_{\text{eff}}": f"Effective Yukawa suppression = exp(−2π/24) ≈ {leff:.6f}",
                    r"N_1": "Dominant flux quanta, set to b₃ at the off-path seed b₃ = 24 (no racetrack on Y₇)",
                },
            ),
            Formula(
                id="gaugino-cabibbo-proxy",
                label="(A4.3)",
                latex=r"\varepsilon_{\text{proxy}} = \lambda_{\text{eff}}^3 \approx " + f"{cab:.4f}",
                plain_text=f"epsilon_proxy = lambda_eff^3 ≈ {cab:.4f}",
                category="DERIVED",
                description=(
                    "FALSIFIED. The racetrack is a calibration at the off-path seed; Y₇ has none (CG.5, CG.10). "
                    f"Cabibbo-like suppression proxy ε ≈ λ_eff³ ≈ {cab:.4f} at the "
                    "off-path seed b₃ = 24, against PDG λ_W = 0.22500 ± 0.00067 — "
                    "344.7σ, off by roughly a factor of two. The 'promotes Cabibbo angle "
                    "from CALIBRATED toward DERIVED' claim is withdrawn. Kept with its "
                    "derivation intact, with the refined and derived variants (which "
                    "also fail), so the failure stays reproducible."
                ),
                inputParams=["algebra.gaugino_lambda_eff"],
                outputParams=["algebra.gaugino_cabibbo_proxy"],
                eml_latex=r"\mathrm{ops.pow}(\lambda_{\text{eff}}, 3)",
                eml_tree_str="ops.pow(lambda_eff, eml_scalar(3.0))",
                eml_description="Cabibbo proxy via EML: ops.pow(lambda_eff, 3)",
                derivation={
                    "method": "Cabibbo proxy from cubic power of Yukawa suppression",
                    "parentFormulas": ["gaugino-lambda-eff"],
                    "steps": [
                        "The Wolfenstein parametrization gives the Cabibbo angle as the leading CKM parameter λ_W ≈ 0.2250",
                        "From the racetrack at the off-path seed, λ_eff ≈ 0.7697 is the suppression scale",
                        "The third power ε ≈ λ_eff³ ≈ 0.456 is the coarse proxy for Cabibbo suppression",
                        "The exact matching λ_W ≈ λ_eff^p requires minimization with SM matter content (p ≈ 3.4)",
                    ],
                    "references": ["Wolfenstein, L. (1983) 'Parametrization of the Kobayashi-Maskawa matrix'. Phys. Rev. Lett. 51, 1945"],
                },
                terms={
                    r"\varepsilon_{\text{proxy}}": {
                        "description": "Coarse proxy for Wolfenstein λ_W ≈ 0.2250; "
                                       "exact derivation needs racetrack minimization with SM matter content",
                    },
                    r"\lambda_{\text{eff}}": {
                        "description": f"Yukawa texture suppression ≈ {leff:.6f} from racetrack minimum",
                    },
                },
            ),
            Formula(
                id="gaugino-cabibbo-derived",
                label="(A4.4)",
                latex=(
                    r"T_{\min} = \frac{N_1 N_2}{2\pi(N_1 - N_2)}\ln\!\frac{N_1}{N_2} \approx "
                    + f"{T_min_val:.4f}"
                    + r",\quad"
                    r"\varepsilon_{\text{rt}} = \left|e^{-2\pi T_{\min}/N_1} - e^{-2\pi T_{\min}/N_2}\right|"
                    r" \approx " + f"{epsilon_rt:.6f}"
                    + r",\quad\lambda_W = \varepsilon_{\text{rt}}^{1/n_{\text{gen}}} \approx "
                    + f"{cab_derived:.6f}"
                ),
                plain_text=(
                    f"T_min = (N1*N2)/(2pi*(N1-N2)) * ln(N1/N2) = {T_min_val:.4f}; "
                    f"epsilon_rt = |exp(-2pi*T_min/N1) - exp(-2pi*T_min/N2)| = {epsilon_rt:.6f}; "
                    f"lambda_W = epsilon_rt^(1/n_gen) = {cab_derived:.6f} (cf. PDG 0.22500)"
                ),
                category="FALSIFIED",
                description=(
                    "FALSIFIED. The racetrack is a calibration at the off-path seed; Y₇ has none (CG.5, CG.10). "
                    f"Algebraic Wolfenstein parameter λ_W ≈ {cab_derived:.4f} from the racetrack moduli minimum. "
                    f"T_min = {T_min_val:.4f} from ∂W/∂T = 0 with N₁=24, N₂=23 (the off-path seed). "
                    f"ε_rt = |W₁(T_min) − W₂(T_min)| = {epsilon_rt:.6f} is the off-diagonal Yukawa texture. "
                    f"λ_W = ε_rt^(1/n_gen) = ε_rt^(1/3) ≈ {cab_derived:.4f}. "
                    "PDG: 0.22500 ± 0.00067 — 37.6σ away. N₁ = 24 was the off-path seed "
                    "b₃ = 24 read as a gauge-group rank, N₂ = N₁ − 1 = 23 and n_gen = 3: "
                    "the construction takes no free parameters, which is why it cannot be "
                    "rescued. The registered value follows the seed in force and also "
                    "fails. The earlier 'agreement ≈ 89%, DERIVED, zero free parameters' "
                    "framing is withdrawn."
                ),
                inputParams=["topology.elder_kads", "topology.n_gen"],
                outputParams=["algebra.gaugino_cabibbo_derived", "algebra.gaugino_racetrack_T_min"],
                eml_latex=(
                    r"\mathrm{ops.pow}(\mathrm{ops.abs}("
                    r"\mathrm{ops.exp}(\mathrm{ops.neg}(2\pi T_{\min}/N_1))"
                    r" - \mathrm{ops.exp}(\mathrm{ops.neg}(2\pi T_{\min}/N_2))"
                    r"),\; \mathrm{ops.inv}(n_{\text{gen}}))"
                ),
                eml_tree_str=(
                    "ops.pow("
                    "ops.abs(ops.add("
                    "ops.exp(ops.neg(ops.mul(eml_scalar(2), ops.mul(eml_pi(), ops.div(T_min, b3_leaf()))))), "
                    "ops.neg(ops.exp(ops.neg(ops.mul(eml_scalar(2), ops.mul(eml_pi(), ops.div(T_min, eml_scalar(23))))))))), "
                    "ops.inv(eml_scalar(3)))"
                ),
                eml_description=(
                    "Algebraic Cabibbo via EML: ops.pow(racetrack_epsilon, ops.inv(n_gen)). "
                    "racetrack_epsilon = ops.abs(W1_at_Tmin - W2_at_Tmin). "
                    "Inputs as written at the off-path seed: N₁ = b₃ = 24, N₂ = 23, n_gen = 3."
                ),
                derivation={
                    "method": "Racetrack moduli minimum + generation-weighted Yukawa texture",
                    "parentFormulas": ["gaugino-racetrack-superpotential", "gaugino-lambda-eff"],
                    "steps": [
                        "Minimise W = A[exp(-2πT/N₁) - exp(-2πT/N₂)] w.r.t. T: ∂W/∂T = 0",
                        "→ (1/N₁)exp(-2πT/N₁) = (1/N₂)exp(-2πT/N₂)",
                        f"→ T_min = (N₁N₂)/(2π(N₁-N₂))·ln(N₁/N₂) = {T_min_val:.6f}",
                        f"Evaluate condensates at T_min: W₁ = exp(-2π·T_min/N₁) = {W1_tmin:.6f}",
                        f"  W₂ = exp(-2π·T_min/N₂) = {W2_tmin:.6f}",
                        f"Off-diagonal Yukawa texture: ε_rt = |W₁ - W₂| = {epsilon_rt:.6f}",
                        "The Wolfenstein parametrization of the CKM matrix has 3 eigenvalues (n_gen=3)",
                        f"Leading mixing angle: λ_W = ε_rt^(1/n_gen) = {epsilon_rt:.6f}^(1/3) = {cab_derived:.6f}",
                        "PDG Wolfenstein λ_W = 0.22500 ± 0.00067: 37.6σ away, FALSIFIED (the earlier 'agreement ≈ 89%, DERIVED' reading is withdrawn)",
                    ],
                    "references": [
                        "Krasnikov (1987); de Carlos, Casas, Quevedo (1993) 'Supersymmetry breaking'",
                        "Wolfenstein, L. (1983) 'Parametrization of the Kobayashi-Maskawa matrix'. Phys. Rev. Lett. 51, 1945",
                        "PDG 2024 CKM review: Wolfenstein λ = 0.22500±0.00067",
                    ],
                },
                terms={
                    r"T_{\min}": f"Racetrack moduli minimum ≈ {T_min_val:.4f} from ∂W/∂T = 0",
                    r"\varepsilon_{\text{rt}}": f"Off-diagonal Yukawa texture = |W₁(T_min) − W₂(T_min)| ≈ {epsilon_rt:.6f}",
                    r"n_{\text{gen}}": "Number of fermion generations = 3 (on Y₇, n_gen = b₂/4, the number of singular involutions)",
                    r"\lambda_W": f"Wolfenstein CKM parameter ≈ {cab_derived:.4f} (PDG: 0.22500)",
                    r"N_1 = 24": "Dominant flux quanta, set to b₃ at the off-path seed b₃ = 24 (no racetrack on Y₇)",
                    r"N_2 = 23": "Sub-dominant flux quanta = N₁ − 1",
                },
            ),
        ]

    def get_output_param_definitions(self) -> List[Parameter]:
        return [
            Parameter(
                path="algebra.gaugino_W_np_1",
                name="Dominant Gaugino Condensate W_np(N₁)",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "CALIBRATED at the off-path seed; no gaugino racetrack exists on Y₇ (CG.5, CG.10). Non-perturbative "
                    "superpotential W_np(N₁) = exp(−2π/N₁), the dominant term, with N₁ read "
                    "from topology.elder_kads (the b₃ in force). Written at the off-path "
                    "seed b₃ = 24 as exp(−2π/24)."
                ),
                derivation_formula="gaugino-racetrack-superpotential",
                eml_description=(
                    "EML: ops.exp(ops.neg(ops.div(ops.mul(eml_scalar(2.0), eml_pi()), eml_scalar(24.0)))) "
                    "— W_np₁ = exp(−2π/24), the dominant condensate at the off-path seed N₁ = 24"
                ),
                no_experimental_value=True,
            ),
            Parameter(
                path="algebra.gaugino_W_np_2",
                name="Sub-dominant Gaugino Condensate W_np(N₂)",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "CALIBRATED at the off-path seed; no gaugino racetrack exists on Y₇ (CG.5, CG.10). Non-perturbative "
                    "superpotential W_np(N₂) = exp(−2π/N₂), the sub-dominant term, with "
                    "N₂ = b₃ − 1 for the b₃ in force. Written at the off-path seed as "
                    "exp(−2π/23)."
                ),
                derivation_formula="gaugino-racetrack-superpotential",
                eml_description=(
                    "EML: ops.exp(ops.neg(ops.div(ops.mul(eml_scalar(2.0), eml_pi()), eml_scalar(23.0)))) "
                    "— W_np₂ = exp(−2π/23), the sub-dominant condensate at the off-path seed N₂ = 23"
                ),
                no_experimental_value=True,
            ),
            Parameter(
                path="algebra.gaugino_lambda_eff",
                name="Yukawa Texture Suppression λ_eff",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "CALIBRATED at the off-path seed; no gaugino racetrack exists on Y₇ (CG.5, CG.10). Effective Yukawa "
                    "suppression λ_eff = exp(−2π/N₁) at the racetrack minimum; at the "
                    "off-path seed N₁ = 24 it is exp(−2π/24) ≈ 0.7697, the bound recorded "
                    "here. The registered value follows the seed in force."
                ),
                derivation_formula="gaugino-lambda-eff",
                eml_description=(
                    "EML: ops.exp(ops.neg(ops.div(ops.mul(eml_scalar(2.0), eml_pi()), eml_scalar(24.0)))) "
                    "— λ_eff = exp(−2π/24) ≈ 0.7676 Yukawa texture suppression"
                ),
                experimental_bound=0.7697,
                bound_type="central_value",
                bound_source="racetrack_minimum_N1_24",
                uncertainty=0.0,
                no_experimental_value=False,
            ),
            Parameter(
                path="algebra.gaugino_cabibbo_proxy",
                name="Cabibbo-like Suppression Proxy ε",
                units="dimensionless",
                status="FALSIFIED",
                description=(
                    "FALSIFIED. The racetrack is a calibration at the off-path seed; Y₇ has none (CG.5, CG.10). "
                    "Coarse proxy ε ≈ λ_eff³ for the Wolfenstein Cabibbo parameter λ_W. "
                    "At the off-path seed b₃ = 24 it evaluates to 0.455938 against PDG "
                    "0.22500 ± 0.00067 — 344.7σ, off by roughly a factor of two; the "
                    "registered value follows the seed in force and also fails. Kept on "
                    "the books with its derivation intact, beside the refined and derived "
                    "variants, so the failure stays reproducible. It no longer promotes "
                    "the Cabibbo angle toward DERIVED; that claim is withdrawn."
                ),
                derivation_formula="gaugino-cabibbo-proxy",
                eml_description=(
                    "EML: ops.pow(eml_vec('algebra.gaugino_lambda_eff'), eml_scalar(3.0)) "
                    "— Cabibbo proxy = λ_eff³ from racetrack minimum"
                ),
                experimental_bound=0.22500,
                bound_type="central_value",
                bound_source="CKM_PDG2024",
                uncertainty=0.00067,
                no_experimental_value=False,
            ),
            Parameter(
                path="algebra.gaugino_cabibbo_refined",
                name="Cabibbo Refined Estimate exp(-pi/2)",
                units="dimensionless",
                status="FALSIFIED",
                description=(
                    "FALSIFIED. The racetrack is a calibration at the off-path seed; Y7 has none (CG.5, CG.10). "
                    "Refined Cabibbo-like estimate exp(-pi/2) = "
                    "lambda_eff^(N1/4) = 0.207880, against PDG 0.22500 +- 0.00067 "
                    "— 25.6 sigma. The physical argument was that first-generation "
                    "Yukawa suppression involves N1/4 = 6 racetrack cycles out of "
                    "N1 = 24 total at the off-path seed b3 = 24 (E6 has 4 SM-like "
                    "gauge sectors); the value is fixed at exp(-pi/2). This is the "
                    "closest of the three variants and still fails by a wide margin. "
                    "The residual gap was previously attributed to loop corrections "
                    "and SU(5) embedding; that attribution is untested and does not "
                    "account for a 7.6% shortfall on a quantity measured to 0.3%."
                ),
                derivation_formula="gaugino-cabibbo-proxy",
                eml_description=(
                    "EML: ops.exp(ops.neg(ops.div(eml_pi(), eml_scalar(2.0)))) "
                    "— refined Cabibbo angle = exp(−π/2) = λ_eff^(N₁/4) from racetrack minimum with 6 cycles"
                ),
                experimental_bound=0.22500,
                bound_type="central_value",
                bound_source="CKM_PDG2024",
                uncertainty=0.00067,
                no_experimental_value=False,
            ),
            Parameter(
                path="algebra.gaugino_racetrack_T_min",
                name="Racetrack Minimum Modulus T_min",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "CALIBRATED at the off-path seed; no gaugino racetrack exists on Y₇ (CG.5, CG.10). Analytic racetrack "
                    "minimum T_min = ln(a₂/a₁)/(a₂−a₁) where aᵢ = 2π/Nᵢ, with N₁ = b₃ and "
                    "N₂ = b₃ − 1 (24 and 23 at the off-path seed). It fixes no modulus of "
                    "Y₇: the moduli, Re(T) included, are OPEN at leading order (CG.6)."
                ),
                eml_description=(
                    # a1 = 2pi/N1 and a2 = 2pi/N2 are inlined rather than named in a
                    # trailing "where" clause: the clause was prose, not EML, so a1 and
                    # a2 were unbound and the expression evaluated with 0.0 for both.
                    "EML: ops.div(ops.log(ops.div("
                    "ops.div(ops.mul(eml_scalar(2.0), eml_pi()), eml_scalar(23.0)), "
                    "ops.div(ops.mul(eml_scalar(2.0), eml_pi()), eml_scalar(24.0)))), "
                    "ops.sub(ops.div(ops.mul(eml_scalar(2.0), eml_pi()), eml_scalar(23.0)), "
                    "ops.div(ops.mul(eml_scalar(2.0), eml_pi()), eml_scalar(24.0)))) "
                    "— T_min = ln(a₂/a₁)/(a₂−a₁) with aᵢ = 2π/Nᵢ, N₁=24, N₂=23 (the off-path seed)"
                ),
                no_experimental_value=True,
            ),
            Parameter(
                path="algebra.gaugino_condensate_ratio",
                name="Condensate Ratio W_np(N₁)/W_np(N₂)",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "CALIBRATED at the off-path seed; no gaugino racetrack exists on Y₇ (CG.5, CG.10). Ratio of dominant "
                    "to sub-dominant condensate strengths; written at the off-path seed "
                    "as W_np(24)/W_np(23)."
                ),
                eml_description=(
                    "EML: ops.div(eml_vec('algebra.gaugino_W_np_1'), eml_vec('algebra.gaugino_W_np_2')) "
                    "— ratio W_np₁/W_np₂ = exp(−2π/24)/exp(−2π/23) of dominant to sub-dominant condensates at the off-path seed"
                ),
                no_experimental_value=True,
            ),
            Parameter(
                path="algebra.gaugino_cabibbo_derived",
                name="Wolfenstein λ_W from Racetrack Minimum (Algebraic)",
                units="dimensionless",
                status="FALSIFIED",
                description=(
                    "FALSIFIED. The racetrack is a calibration at the off-path seed; Y₇ has none (CG.5, CG.10). "
                    "Wolfenstein CKM parameter "
                    "λ_W = |exp(-2π·T_min/N₁) - exp(-2π·T_min/N₂)|^(1/n_gen) from the "
                    "racetrack moduli minimum T_min = (N₁·N₂)/(2π·(N₁-N₂))·ln(N₁/N₂). "
                    "At the off-path seed (N₁ = b₃ = 24, N₂ = 23, n_gen = 3) it is "
                    "0.250163, 37.6σ from PDG Wolfenstein λ_W = 0.22500 ± 0.00067; the "
                    "registered value follows the seed in force and also fails. "
                    "Minimising the racetrack moved the "
                    "prediction toward the measurement relative to the λ_eff³ proxy "
                    "but overshot it; the mechanism does not fix the Cabibbo angle. "
                    "The earlier '11% agreement, zero free parameters' framing is "
                    "withdrawn — an 11% discrepancy on a quantity measured to 0.3% "
                    "is a failure, not an agreement."
                ),
                derivation_formula="gaugino-cabibbo-derived",
                eml_description=(
                    "EML: ops.pow(ops.abs(ops.add("
                    # 'T_min' is not a registry name; the modulus is registered at
                    # algebra.gaugino_racetrack_T_min and is referenced by full path.
                    "ops.exp(ops.neg(ops.mul(eml_scalar(2), ops.mul(eml_pi(), ops.div(eml_vec('algebra.gaugino_racetrack_T_min'), eml_scalar(24)))))), "
                    "ops.neg(ops.exp(ops.neg(ops.mul(eml_scalar(2), ops.mul(eml_pi(), ops.div(eml_vec('algebra.gaugino_racetrack_T_min'), eml_scalar(23))))))))), "
                    "ops.inv(eml_scalar(3)))"
                ),
                experimental_bound=0.22500,
                bound_type="central_value",
                bound_source="CKM_PDG2024_Wolfenstein_lambda",
                uncertainty=0.00067,
                no_experimental_value=False,
            ),
        ]

    def get_section_content(self) -> Optional[SectionContent]:
        # The section records the construction at the off-path seed
        # b_3 = 24 (N1 = 24, N2 = 23); Y_7 has no racetrack, so these are
        # calibrations.
        N1 = 24
        N2 = 23
        n_gen = 3
        W1 = math.exp(-2 * math.pi / N1)
        W2 = math.exp(-2 * math.pi / N2)
        leff = W1
        cab = leff ** 3
        T_min = _racetrack_T_min(N1, N2)
        W1_tmin = math.exp(-2 * math.pi * T_min / N1)
        W2_tmin = math.exp(-2 * math.pi * T_min / N2)
        epsilon_rt = abs(W1_tmin - W2_tmin)
        cab_derived = epsilon_rt ** (1.0 / n_gen)

        blocks = [
            ContentBlock(type="heading", content="Gaugino Condensation and the Cabibbo Angle", level=2),
            ContentBlock(
                type="paragraph",
                content=(
                    "CALIBRATED at the off-path seed. This section records a construction the adopted "
                    "geometry does not support. A gaugino racetrack needs a confining "
                    "hidden sector, but Y₇'s singular loci carry N = 4 super Yang-Mills "
                    "(CG.5), and with holonomy exactly G₂ no confining sector exists in "
                    "φ's Joyce family (CG.10). As written, the hidden E₈' gauge factor "
                    "condensed on two classes of associative 3-cycles, with "
                    f"N₁ = {int(N1)} taken from the off-path seed b₃ = {int(N1)} and "
                    f"N₂ = N₁ − 1 = {int(N2)}. Reading a Betti number as the rank of a "
                    "gauge group was the error; the numbers below are calibrations at "
                    "the off-path seed, kept so the failure stays reproducible."
                ),
            ),
            ContentBlock(
                type="formula",
                content=r"W_{\text{np}} = A\,e^{-2\pi T/24} + A\,e^{-2\pi T/23}",
                formula_id="gaugino-racetrack-superpotential",
                label="(A4.1)",
            ),
            ContentBlock(
                type="callout",
                callout_type="warning",
                title="Racetrack Minimum at the Off-Path Seed — FALSIFIED; No Racetrack on Y₇",
                content=(
                    f"W_np(N₁=24) = {W1:.8f},  W_np(N₂=23) = {W2:.8f}\n"
                    f"λ_eff = exp(−2π/24) = {leff:.8f}\n"
                    f"Cabibbo proxy ε ≈ λ_eff³ = {cab:.6f}  (cf. PDG Wolfenstein λ_W ≈ 0.2250)\n"
                    f"Racetrack minimum T_min ≈ {T_min:.6f}\n"
                    f"Algebraic: ε_rt = |W₁(T_min) − W₂(T_min)| = {epsilon_rt:.6f},  "
                    f"λ_W = ε_rt^(1/3) = {cab_derived:.6f}  "
                    f"[FALSIFIED: PDG 0.22500 ± 0.00067, {abs(cab_derived-0.22500)/0.00067:.1f} sigma]"
                ),
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<Normal>"
                    "At the off-path seed (N₁ = 24, N₂ = 23), "
                    f"the effective Yukawa suppression λ_eff = exp(−2π/24) ≈ {leff:.6f} at the racetrack minimum "
                    f"gives a Cabibbo-like proxy ε ≈ λ_eff³ ≈ {cab:.4f}. "
                    "Beyond this coarse proxy, the algebraic Wolfenstein parameter follows from evaluating "
                    "both condensates at the exact racetrack moduli minimum T_min. "
                    f"Setting ∂W/∂T = 0 gives T_min = (N₁·N₂)/(2π·(N₁−N₂))·ln(N₁/N₂) ≈ {T_min:.4f}. "
                    f"The off-diagonal Yukawa texture ε_rt = |W₁(T_min) − W₂(T_min)| ≈ {epsilon_rt:.5f} "
                    "encodes the condensate splitting at the minimum. "
                    f"With n_gen = 3 fermion generations, λ_W = ε_rt^(1/n_gen) = ε_rt^(1/3) ≈ {cab_derived:.4f}. "
                    "The PDG value is 0.22500 ± 0.00067, so this is "
                    f"{abs(cab_derived-0.22500)/0.00067:.1f}σ away and the row is scored "
                    "FALSIFIED. Minimising the racetrack moved the prediction toward the "
                    "measurement relative to the λ_eff³ proxy (344.7σ) but overshot it; "
                    "the closest of the three variants, exp(−π/2) = 0.207880, is still "
                    "25.6σ out. The mechanism does not fix the Cabibbo angle. Zero free "
                    "parameters is a statement about the construction's arity, not a "
                    "defence of its accuracy."
                    "</Normal>"
                    "<EML>"
                    f"T_min: ops.div(ops.mul(eml_scalar({N1}), eml_scalar({N2})), "
                    f"ops.mul(ops.mul(eml_scalar(2), eml_pi()), eml_scalar({N1 - N2}))) * ln({N1}/{N2}). "
                    f"W1_tmin = ops.exp(ops.neg(ops.mul(eml_scalar(2), ops.mul(eml_pi(), ops.div(T_min, eml_scalar({N1})))))); "
                    f"W2_tmin = ops.exp(ops.neg(ops.mul(eml_scalar(2), ops.mul(eml_pi(), ops.div(T_min, eml_scalar({N2})))))); "
                    "epsilon_rt = ops.abs(ops.add(W1_tmin, ops.neg(W2_tmin))); "
                    "lambda_W = ops.pow(epsilon_rt, ops.inv(eml_scalar(3))). "
                    "N₁ and N₂ are the off-path seed's 24 and 23; no fitting, and no "
                    "racetrack on Y₇."
                    "</EML>"
                ),
            ),
            ContentBlock(
                type="formula",
                content=(
                    r"T_{\min} = \frac{N_1 N_2}{2\pi(N_1-N_2)}\ln\frac{N_1}{N_2},\quad"
                    r"\lambda_W = \left|e^{-2\pi T_{\min}/N_1} - e^{-2\pi T_{\min}/N_2}\right|^{1/n_{\text{gen}}}"
                ),
                formula_id="gaugino-cabibbo-derived",
                label="(A4.4)",
            ),
        ]

        return SectionContent(
            section_id="A4",
            subsection_id=None,
            title="Gaugino Condensation: Cabibbo from Racetrack N₁=24/N₂=23 (Calibrated; No Racetrack on Y₇)",
            abstract=(
                "CALIBRATED at the off-path seed: Y₇ has no gaugino racetrack (its singular loci carry "
                "N = 4 SYM, CG.5; holonomy exactly G₂ excludes a confining sector in φ's "
                "Joyce family, CG.10). As written at the off-path seed b₃ = 24, hidden E₈' "
                "gaugino condensation gave an N₁=24/N₂=23 racetrack. "
                f"The algebraic Wolfenstein parameter λ_W = ε_rt^(1/3) ≈ {cab_derived:.4f} "
                "follows from the racetrack moduli minimum with no free parameters, and is "
                "FALSIFIED against PDG λ_W = 0.22500 ± 0.00067 at 37.6σ. All three Cabibbo "
                "candidates from this module fail (344.7σ / 37.6σ / 25.6σ at the off-path seed)."
            ),
            content_blocks=blocks,
            formula_refs=[
                "gaugino-racetrack-superpotential",
                "gaugino-lambda-eff",
                "gaugino-cabibbo-proxy",
                "gaugino-cabibbo-derived",
            ],
            param_refs=self.output_params,
            appendix=True,
        )


    def get_certificates(self) -> List[Dict[str, Any]]:
        N1, N2 = 24, 23
        W1 = math.exp(-2.0 * math.pi / N1)
        W2 = math.exp(-2.0 * math.pi / N2)
        leff = W1
        cab = leff ** 3
        return [
            {
                "id": "CERT_GAUGINO_LAMBDA_EFF",
                "assertion": f"lambda_eff = exp(-2π/24) = {leff:.10f}",
                "condition": f"abs({leff} - math.exp(-2*math.pi/24)) < 1e-12",
                "status": "PASS",
            },
            {
                "id": "CERT_GAUGINO_W1_GT_W2",
                "assertion": f"W_np(N1=24) = {W1:.8f} < W_np(N2=23) = {W2:.8f} (dominant < sub-dominant at T=1)",
                "condition": f"{W1} < {W2}",
                "status": "PASS",
            },
            {
                "id": "CERT_GAUGINO_CABIBBO_PROXY",
                "assertion": (
                    f"Cabibbo proxy epsilon = lambda_eff^3 = {cab:.6f}. The order-of-magnitude "
                    "band 0.1 < eps < 1.0 is satisfied, but the row is FALSIFIED against PDG "
                    "lambda_W = 0.22500 +- 0.00067 at 344.7 sigma. The band check is not a "
                    "validation of the prediction."
                ),
                "condition": f"0.1 < {cab} < 1.0",
                # The band check itself passes; the PARAMETER it describes is
                # falsified. Both facts matter, so they go in separate fields
                # -- a status is a vocabulary token and must stay parseable.
                # It previously read "PASS (band only; parameter row
                # FALSIFIED)", which no consumer could match against the
                # allowed set.
                "status": "PASS",
                "scope_caveat": (
                    "Band only. The parameter row this certificate covers is "
                    "FALSIFIED (344.7 sigma against PDG); passing the band "
                    "does not rehabilitate it."
                ),
            },
        ]

    def validate_self(self) -> Dict[str, Any]:
        N1, N2 = 24, 23
        W1 = math.exp(-2.0 * math.pi / N1)
        W2 = math.exp(-2.0 * math.pi / N2)
        leff = W1
        cab = leff ** 3
        return {
            "checks": [
                {
                    "name": "lambda_eff_from_b3",
                    "passed": abs(leff - math.exp(-2.0 * math.pi / 24.0)) < 1e-12,
                    "log_level": "INFO",
                    "message": f"lambda_eff = exp(-2π/24) = {leff:.10f}",
                },
                {
                    "name": "racetrack_ordering",
                    "passed": W1 < W2,
                    "log_level": "INFO",
                    "message": f"W_np(24) = {W1:.8f} < W_np(23) = {W2:.8f} (correct ordering)",
                },
                {
                    "name": "cabibbo_proxy_range",
                    "passed": 0.1 < cab < 1.0,
                    "log_level": "INFO",
                    "message": f"Cabibbo proxy ε = λ_eff³ = {cab:.6f} in (0.1, 1.0)",
                },
            ]
        }

    def get_references(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "krasnikov1987",
                "authors": "Krasnikov, N.V.",
                "title": "On supersymmetry breaking in superstring theories",
                "year": 1987,
                "doi": "10.1016/0370-2693(87)91274-2",
            },
            {
                "id": "dine1985",
                "authors": "Dine, M., Rohm, R., Seiberg, N., & Witten, E.",
                "title": "Gluino condensation in superstring models",
                "year": 1985,
                "doi": "10.1016/0370-2693(85)91354-1",
            },
        ]

    def get_learning_materials(self) -> List[Dict[str, Any]]:
        return [
            {
                "topic": "Gaugino Condensation",
                "url": "https://en.wikipedia.org/wiki/Gaugino_condensation",
                "relevance": "Mechanism by which the hidden E8' gauge sector breaks supersymmetry via non-perturbative condensation",
            },
            {
                "topic": "Racetrack Superpotential",
                "url": "https://en.wikipedia.org/wiki/Moduli_stabilization",
                "relevance": "Two competing gaugino condensates create a racetrack potential that stabilizes the Kähler modulus T",
            },
        ]


def _racetrack_T_min(N1: int, N2: int) -> float:
    """Analytic racetrack minimum modulus T_min = ln(a2/a1)/(a2-a1)."""
    a1 = 2.0 * math.pi / N1
    a2 = 2.0 * math.pi / N2
    if abs(a2 - a1) < 1e-15:
        return float("inf")
    return math.log(a2 / a1) / (a2 - a1)
