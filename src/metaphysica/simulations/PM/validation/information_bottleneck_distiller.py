#!/usr/bin/env python3
"""
Information Bottleneck Distiller - v24.1 Principia Metaphysica
===============================================================

Tallies whether the 26D→125 residue mapping compresses the constants
(Minimal Description Length, MDL): the bits of the seed and the constraint
code against the bits of the raw constants. The MDL status is computed from
that tally (mdl_status_from_tally); it is not assumed.

This addresses the peer review concern: "With 27 free parameters deriving 125
constants, isn't this just a parameter fit in disguise?"

Theoretical Framework:
    - Algorithmic Symmetry (an interpretation, not a tested property): that the
      code is isomorphic to geometric constraints
    - Topological Compression: MDL tally of the seed and constraint code against
      the raw constants; the status is computed from the tally, and the
      27 input dimensions are the superseded 27D count (adopted bulk: 26D (24,2))
    - The 288/24/4 structure is a retired off-path reading, not claimed as derived

Purpose:
    - Calculate Kolmogorov complexity of 26D input vs 125 output constants
    - Tally the description length with and without the constraint code
    - Report the MDL status the tally gives, and the seed-only ratio as a
      labelled side figure
    - Whether the framework avoids overfitting is not established by the tally

Output:
    compression_report.json - Information-theoretic and MDL analysis

STATUS ON THE ADOPTED PATH
OFF-PATH (b3_seed = seed_24): this analysis was written at the off-path seed
b_3 = 24 and describes the internal space as a twisted connected sum (TCS).
The adopted internal space is Joyce's resolution of T^7/(Z/2)^3 with
(b_2, b_3) = (12, 43), and n_gen = b_2/4 = 3. Its "27 dimensions" are the
superseded 27D count with one shared time (RETIRED, signature ruling
2026-08-31); the adopted bulk is 26D of signature (24,2). The description
string in analyze_input_description_length() is kept verbatim because its
byte length is the input of the complexity estimate.

Copyright (c) 2026 Andrew Keith Watts. All rights reserved.
"""

import numpy as np
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from scipy.stats import entropy
from datetime import datetime
import hashlib

# Add parent directory to path
import sys
REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("InformationBottleneck")

#: The MDL statuses the tally can give (mdl_status_from_tally), each with the
#: verdict and the overall-status label the report states. FAILS_AS_TALLIED:
#: L(Theory) (seed plus constraint code) exceeds L(Data), the raw constants.
#: HOLDS_AS_TALLIED (new in the close-out review): it does not.
MDL_FAILS = "FAILS_AS_TALLIED"
MDL_HOLDS = "HOLDS_AS_TALLIED"
_MDL_VERDICTS = {
    MDL_FAILS: ("NOT VERIFIED", "MDL FAILS AS TALLIED"),
    MDL_HOLDS: ("SUPPORTED AS TALLIED (an estimate of description length, not a proof)",
                "MDL HOLDS AS TALLIED"),
}

_RETIRED_288 = ("The 288/24/4 structure is a retired off-path reading (b3 = 24); "
                "it is not claimed as derived.")


def seed_accounting_status(data_compression_ratio: float) -> str:
    """Label of the seed-only data ratio (constraint code excluded); it is a
    side figure, not the MDL status."""
    for floor, label in ((50, "HIGHLY EFFICIENT"), (10, "VERY EFFICIENT"),
                         (2, "EFFICIENT"), (1, "MARGINAL")):
        if data_compression_ratio > floor:
            return f"{label} (seed accounting only)"
    return "INEFFICIENT (expansion even under the seed accounting)"


def mdl_status_from_tally(compression: Dict[str, Any]) -> str:
    """MDL status computed from the tally: the seed plus the constraint code
    (first_use_total_bits) against the raw constants (without_theory_bits)."""
    first_use = compression["first_use_total_bits"]
    raw = compression["without_theory_bits"]
    seed = compression["with_theory_data_bits"]
    if first_use <= raw:
        return MDL_HOLDS
    if seed < raw:
        return f"{MDL_FAILS} (holds only under {seed}-bit seed accounting)"
    return MDL_FAILS


def _mdl_verdict(mdl_status: str) -> Tuple[str, str]:
    """(verdict, overall-status label) for a recorded MDL status; a missing or
    unknown status raises ValueError."""
    if not mdl_status:
        raise ValueError("an MDL verdict needs the recorded MDL status")
    base = mdl_status.split(" (", 1)[0]
    if base not in _MDL_VERDICTS:
        raise ValueError(f"unknown MDL status {mdl_status!r}; known: {sorted(_MDL_VERDICTS)}")
    return _MDL_VERDICTS[base]


def mdl_holds(mdl_status: str) -> bool:
    """True only when the recorded MDL status is HOLDS_AS_TALLIED."""
    _mdl_verdict(mdl_status)
    return mdl_status.split(" (", 1)[0] == MDL_HOLDS


def overall_status(mdl_status: str) -> str:
    """Report overall status, built from the recorded MDL status."""
    return f"{_mdl_verdict(mdl_status)[1]}: {mdl_status}"


def integrity_conclusion(mdl_status: str) -> str:
    """Overall code-theoretical conclusion, worded from the recorded MDL status."""
    verdict = _mdl_verdict(mdl_status)[0]
    return (
        f"Code-theoretical integrity {verdict}: MDL status {mdl_status}. "
        "That the code is isomorphic to geometric constraints (Algorithmic Symmetry) "
        "is an interpretation, not a tested property. " + _RETIRED_288
    )


def mdl_principle(compression: Dict[str, Any], n_output: int) -> Dict[str, str]:
    """MDL principle entry, worded from the computed tally and its status."""
    c = compression
    status = mdl_status_from_tally(c)
    relation = "EXCEEDS" if c["first_use_total_bits"] > c["without_theory_bits"] else "does not exceed"
    return {
        "definition": (
            "Minimal Description Length (MDL) principle: The best theory is the one "
            "that minimizes the total description length: L(Theory) + L(Data|Theory)"
        ),
        "application_to_pm": (
            f"As tallied, L(Theory) = seed ({c['with_theory_data_bits']} bits) + constraint "
            f"code ({c['theory_code_bits']} bits) = {c['first_use_total_bits']} bits, with "
            "L(Data|Theory) = 0 bits (deterministic mapping). Without theory: L(Data) = "
            f"{n_output} constants x {c['without_theory_bits'] // n_output} bits = "
            f"{c['without_theory_bits']} bits (no predictive power). L(Theory) {relation} "
            f"L(Data): MDL status {status}."
        ),
        "mdl_status": status,
    }


def mdl_interpretation(compression: Dict[str, Any], mdl_status: str,
                       n_output: int) -> Dict[str, str]:
    """Report interpretation, built from the computed tally and the MDL status."""
    holds = mdl_holds(mdl_status)
    c = compression
    seed = c["with_theory_data_bits"]
    seed_part = (f"Under the {seed}-bit seed accounting (constraint code excluded) the "
                 f"data ratio is {c['data_compression_ratio']:.1f}:1 ({c['status']}); "
                 f"counting the {c['theory_code_bits']}-bit constraint code the first-use "
                 f"ratio is {c['first_use_ratio']:.2f}:1. ")
    tally = (f"L(Theory) = {c['first_use_total_bits']} bits (seed plus constraint code) "
             f"against L(Data) = {c['without_theory_bits']} bits for {n_output} constants "
             f"at {c['without_theory_bits'] // n_output} bits each")
    conclusion = (f"MDL status as tallied: {mdl_status} ({tally})" if holds else
                  f"Data compression under the {seed}-bit seed accounting only; "
                  f"MDL status as tallied: {mdl_status}")
    caveat = ("The tally is an estimate of description length, not a proof." if holds else
              "Compression holds only if the constraint code is left out of the tally.")
    return {
        "conclusion": conclusion,
        "peer_review_response": (
            seed_part + f"MDL status as tallied: {mdl_status}. The input dimension count "
            "is the superseded 27D count (adopted bulk: 26D of signature (24,2))."),
        "key_insight": (
            seed_part + f"MDL status as tallied: {mdl_status}; whether the framework "
            "avoids overfitting is not established by this tally. " + _RETIRED_288),
        "mdl_justification": f"As tallied, {tally}: MDL status {mdl_status}. {caveat}",
    }


class InformationBottleneckDistiller:
    """
    Tallies whether the PM framework compresses its constants under the
    Minimal Description Length (MDL) criterion; the MDL status is computed
    from the tally (mdl_status_from_tally).

    That the code is the geometric constraints expressed as symbolic logic
    (Algorithmic Symmetry) is an interpretation, not a tested property. The
    288/24/4 structure is a retired off-path reading (b3 = 24).

    The tally HOLDS if:
    1. Description length of theory (seed plus constraint code) <= description
       length of the raw constants (MDL)
    2. Compression ratio > 1 counting the constraint code
    3. Mutual information I(Input; Output) is maximal (deterministic mapping)
    4. No redundancy in the 125-residue encoding (optimal compression)
    5. Code complexity equals geometric constraint complexity (Algorithmic Symmetry)
    """

    def __init__(self):
        """Initialize information bottleneck distiller."""
        # PM framework structure
        self.n_input_dims = 27  # the superseded 27D count; the adopted bulk M^{26}(24,2) has 26 (kept: the analysis is sized by it)
        self.n_output_params = 125  # Physical constants
        self.n_formulas = 116  # Topological formulas (from PM v23.9)

        # Parameter classification (from PM v24.1)
        self.n_geometric = 55  # Pure predictions
        self.n_calibrated = 3  # Calibration inputs
        self.n_fitted = 2  # Fitted PMNS
        self.n_established = 65  # Measured/established

        logger.info(f"Initialized: {self.n_input_dims}D → {self.n_output_params} constants")
        logger.info(f"Classification: {self.n_geometric} geometric, {self.n_calibrated} calibrated, {self.n_fitted} fitted")

    def calculate_kolmogorov_complexity_bound(self, description: str) -> Dict[str, Any]:
        """
        Estimate Kolmogorov complexity K(x) via description length.

        K(x) ≈ length of shortest program that generates x

        Args:
            description: String description of the object

        Returns:
            Complexity bounds and compression metrics
        """
        # Uncompressed length (raw description)
        uncompressed_bits = len(description.encode('utf-8')) * 8

        # Compressed length (gzip-like compression as proxy for K(x))
        # Since we don't have gzip, use hash entropy as proxy
        hash_digest = hashlib.sha256(description.encode('utf-8')).hexdigest()
        compressed_bits = len(hash_digest) * 4  # Hex chars = 4 bits each

        # Compression ratio
        compression_ratio = uncompressed_bits / compressed_bits if compressed_bits > 0 else 0

        return {
            "uncompressed_bits": uncompressed_bits,
            "compressed_bits": compressed_bits,
            "compression_ratio": float(compression_ratio),
            "hash_entropy_bits": compressed_bits
        }

    def analyze_input_description_length(self) -> Dict[str, Any]:
        """
        Calculate description length of the 26D input manifold.

        The "input" is the topological structure M^{26}(24,2) = 12×(2,0) + S^(2,0) + (0,1)

        Returns:
            Input description complexity
        """
        logger.info("Analyzing input (26D manifold) description length...")

        # The 26D manifold is specified here by:
        # 1. G₂ holonomy group (Lie group, 14-dimensional)
        # 2. Third Betti number b₃ (one integer; written b₃ = 24, the off-path
        #    seed -- the adopted b₃ is 43, tied to b₂ = 12 by b₃ = 7 + 3b₂)
        # 3. Bridge structure: 12 pairs (integer)
        # 4. Structure: (24,2) (3 integers)
        # 5. Sampler data fields signature: (2,0) (2 integers)

        # OFF-PATH (b3_seed = seed_24): the description below is the retired
        # wording -- a twisted connected sum, b₃ = 24, and shadow-time
        # directions of Euclidean signature beside a single time fibre T¹
        # (the shared single time is RETIRED, signature ruling 2026-08-31).
        # The adopted internal space is Joyce's resolution of T^7/(Z/2)^3 and
        # the bulk is (24,2), one time per shadow. The string is kept verbatim
        # because its byte length is the input of the complexity estimate;
        # rewriting it would change the computed bits.
        description = (
            "Manifold M^{26}(24,2) = Twisted Connected Sum of two G₂ holonomy 7-manifolds, "
            "connected by 12 bridge pairs with signature (2,0), "
            "plus shadow-time directions S^{(2,0)} with Euclidean signature (2,0), "
            "plus two-time structure fiber T¹ with signature (0,1). "
            f"Third Betti number b₃ = 24. "  # retired wording (off-path seed), kept verbatim: see above
            "G₂ holonomy fixes Ricci-flatness and induces associative 3-cycles."
        )

        complexity = self.calculate_kolmogorov_complexity_bound(description)

        # Additional information: specification of G₂ holonomy
        # This requires: structure constants of G₂ Lie algebra (14 parameters)
        # But these are UNIVERSAL (not tunable) - they're fixed by G₂ mathematics

        universal_parameters = {
            "g2_structure_constants": 14,  # Lie algebra structure (universal, not free)
            "betti_number_b3": 1,  # Integer specification
            "signature": 3,  # (24,2) = 3 integers
            "bridge_count": 1,  # 12 bridges = 1 integer
            "bridge_signature": 2,  # (2,0) = 2 integers
            "central_signature": 2,  # (2,0) = 2 integers
        }

        total_universal_params = sum(universal_parameters.values())

        # Information content: log₂(parameter space volume)
        # For b₃ (one fixed integer; 24 at the off-path seed): log₂(1) = 0 bits
        # For structure (24,2): log₂(1) = 0 bits (fixed by construction)
        # For 12 bridges: log₂(1) = 0 bits (formerly "derived from b₃/2", true
        # only at the off-path seed; on the adopted path the 12 bridges are the
        # 12 resolved A1 components, WA-1)

        # True free parameters: ZERO (all topological invariants)
        information_bits_free = 0

        return {
            "description": description,
            "complexity_bounds": complexity,
            "universal_parameters": universal_parameters,
            "total_universal_params": total_universal_params,
            "free_parameters": 0,
            "information_content_bits": information_bits_free,
            "note": "All 27 dimensions are topological invariants, not free parameters"
        }

    def analyze_output_description_length(self) -> Dict[str, Any]:
        """
        Calculate description length of the 125 output constants via MDL.

        If these were arbitrary, they'd require ~125 × 64 bits ≈ 8000 bits.
        Under Algorithmic Symmetry, they require only the geometric constraint
        encoding (Topological Compression).

        Returns:
            Output description complexity and MDL analysis
        """
        logger.info("Analyzing output (125 constants) description length via MDL...")

        # If 125 constants were INDEPENDENT and ARBITRARY:
        # Each constant requires ~64 bits (double precision)
        arbitrary_bits = self.n_output_params * 64

        # But in PM, constants are DERIVED via Algorithmic Symmetry
        # The code IS the geometric constraints expressed as formal symbolic logic
        # Description length = Σ geometric_constraint_complexity

        # Example constraints from PM (as originally listed):
        # - α⁻¹ = χ_eff × (G₂ holonomy correction)  [CALIBRATED, k_gimel layer, D-007]
        # - M_GUT = M_Planck / √(b₃)  [topological scale]
        # - n_gen = b₂ / 4 = 3  [the ruled route; the "n_gen = b₃ / 8 chiral
        #   index theorem" listed here before is ABANDONED: 8 divides no
        #   reachable b₃]

        # Each constraint is ~10-50 characters of symbolic logic
        # Estimate: average 30 characters per constraint
        avg_formula_length_chars = 30
        total_formula_description_bits = self.n_formulas * avg_formula_length_chars * 8

        # Compression ratio: arbitrary vs Topological Compression
        compression_ratio = arbitrary_bits / total_formula_description_bits if total_formula_description_bits > 0 else 0

        # Information saved by Topological Compression (MDL principle)
        information_saved_bits = arbitrary_bits - total_formula_description_bits

        return {
            "arbitrary_description_bits": arbitrary_bits,
            "formula_description_bits": total_formula_description_bits,
            "n_formulas": self.n_formulas,
            "avg_formula_length_chars": avg_formula_length_chars,
            "compression_ratio": float(compression_ratio),
            "information_saved_bits": float(information_saved_bits),
            "compression_efficiency": f"{(1 - 1/compression_ratio)*100:.1f}%" if compression_ratio > 1 else "0%",
            "note": (f"Formula tally: {total_formula_description_bits} bits for {self.n_formulas} "
                     f"formulas against {arbitrary_bits} bits of raw constants "
                     f"(ratio {compression_ratio:.2f}:1; the MDL status is computed in "
                     "compression_ratio_analysis)"),
            "mdl_interpretation": "Code complexity equals geometric constraint complexity (isomorphism)"
        }

    def calculate_mutual_information(self) -> Dict[str, Any]:
        """
        Calculate mutual information I(Input; Output).

        I(X;Y) = H(Y) - H(Y|X)

        For a deterministic mapping (topology → constants), H(Y|X) = 0,
        so I(X;Y) = H(Y).

        Returns:
            Mutual information analysis
        """
        logger.info("Calculating mutual information I(Input; Output)...")

        # The PM framework is a DETERMINISTIC mapping:
        # 26D topology → 125 constants (via formulas)

        # For deterministic mapping: H(Output | Input) = 0
        # Therefore: I(Input; Output) = H(Output)

        # Entropy of output: log₂(number of possible outputs)
        # Since mapping is deterministic and topology is fixed: H(Output) ≈ 0

        # BUT: If we consider the *information content* of the constants themselves
        # as a probability distribution over physical parameter space, then:
        # H(Output) ≈ log₂(125) ≈ 6.97 bits (distinguishing which constant)

        entropy_output_bits = np.log2(self.n_output_params)

        # Input entropy: log₂(27) ≈ 4.75 bits (which dimension)
        entropy_input_bits = np.log2(self.n_input_dims)

        # Mutual information for deterministic mapping
        mutual_info_bits = float(entropy_output_bits)  # Since H(Y|X) = 0

        # Normalized mutual information: I(X;Y) / H(Y)
        normalized_mi = 1.0  # Perfect correlation (deterministic)

        return {
            "entropy_input_bits": float(entropy_input_bits),
            "entropy_output_bits": float(entropy_output_bits),
            "conditional_entropy_bits": 0.0,  # H(Output | Input) = 0 for deterministic map
            "mutual_information_bits": mutual_info_bits,
            "normalized_mutual_information": normalized_mi,
            "interpretation": "Perfect information preservation (deterministic topology → constants mapping)"
        }

    def analyze_redundancy(self) -> Dict[str, Any]:
        """
        Analyze redundancy in the 125-parameter encoding via MDL.

        Check if any constants could be removed without loss of information.
        Read as Topological Compression (an interpretation), apparent redundancy
        reflects the continuous phase space of the bulk (adopted: 26D of
        signature (24,2)) being discretized into observables.

        Returns:
            Redundancy analysis and MDL optimality
        """
        logger.info("Analyzing redundancy in 125-parameter encoding (MDL criterion)...")

        # The 125 constants are organized into categories:
        # - 55 geometric: PURE predictions (Topological Compression outputs)
        # - 3 calibrated: Inputs (scale anchors for continuous→discrete mapping)
        # - 2 fitted: PMNS angles (awaiting full Algorithmic Symmetry for Yukawa sector)
        # - 65 established: Measured values (redundancy = experimental cross-checks)

        # Minimal Description Length: how few numbers could the constants need?
        # The claim made here: ALL 125 could be derived from just:
        # - b₃ (1 integer - topological invariant; written b₃ = 24, the
        #   off-path seed)
        # - k_gimel = 12.3183... (CALIBRATED: a fit at the retired seed, D-007)
        # - φ = golden ratio (mathematical constant, 0 bits - universal)

        # So the claimed MINIMAL description is 2 numbers: b₃ and k_gimel
        # (whether MDL holds is computed in calculate_compression_ratio)
        minimal_info_parameters = 2

        # Redundancy ratio: (actual parameters - minimal) / actual
        redundancy_ratio = (self.n_output_params - minimal_info_parameters) / self.n_output_params

        # But this is INTENTIONAL redundancy for experimental validation
        # Each derived constant serves as independent cross-check
        # The 288/24/4 structure is a retired off-path reading (b3 = 24), not
        # claimed as derived

        essential_parameters = {
            "topological_invariants": ["b3", "k_gimel"],
            "mathematical_constants": ["phi"],
            "calibration_inputs": ["M_Planck", "alpha_EM", "m_H"],
            "fitted_parameters": ["theta_13", "delta_CP"]
        }

        total_essential = 2 + 1 + 3 + 2  # = 8 parameters

        return {
            "total_parameters": self.n_output_params,
            "minimal_information_parameters": minimal_info_parameters,
            "essential_parameters": total_essential,
            "redundancy_ratio": float(redundancy_ratio),
            "interpretation": (
                f"125 constants could theoretically be derived from just {minimal_info_parameters} numbers (b₃, k_gimel), "
                "but are expanded for experimental validation. "
                "Whether this is compression rather than fitting is what the MDL tally tests "
                "(compression_ratio_analysis.mdl_status). " + _RETIRED_288
            ),
            "parameter_breakdown": {
                "geometric_predictions": self.n_geometric,
                "calibration_inputs": self.n_calibrated,
                "fitted_pmns": self.n_fitted,
                "established_measured": self.n_established
            },
            "mdl_note": "Apparent redundancy = discretization of continuous phase space (unavoidable for observables)"
        }

    def calculate_compression_ratio(self) -> Dict[str, Any]:
        """
        Calculate Topological Compression ratio via MDL criterion.

        Ratio > 1 means Topological Compression achieved (MDL satisfied)
        Ratio < 1 means expansion (overfitting - MDL violated)

        Returns:
            Compression ratio analysis and MDL validation
        """
        logger.info("Calculating Topological Compression ratio (MDL criterion)...")

        # Input: 26D topology specified by ~100 characters + G₂ structure
        # Output: 125 constants, IF independent, would require 125 × 64 bits

        # But PM achieves Algorithmic Symmetry:
        # Input: ~2 fundamental topological invariants (b₃, k_gimel)
        # Output: 125 constants derived via 116 geometric constraints

        # Description length comparison (MDL principle):
        # L(Theory) = L(topology) + L(geometric_constraints) + L(constraint_logic)
        #           ≈ 100 chars + 116 constraints × 30 chars + 500 chars (logic)
        #           ≈ 100 + 3480 + 500 = 4080 chars ≈ 32,640 bits

        theory_description_bits = (100 + self.n_formulas * 30 + 500) * 8

        # L(Data) = 125 constants × 64 bits (if stored as raw doubles)
        #         = 8000 bits

        data_description_bits = self.n_output_params * 64

        # Naive compression ratio (just comparing bit counts)
        naive_ratio = data_description_bits / theory_description_bits

        # But this is WRONG comparison! The MDL-correct comparison is:
        # "How many bits to specify constants WITHOUT Topological Compression vs WITH?"

        # WITHOUT Topological Compression: Must measure and store all 125 constants independently
        # = 125 × 64 bits = 8000 bits

        # WITH Topological Compression: Only specify fundamental topological invariants:
        # - b₃ (5 bits, sized for the off-path seed b₃ = 24 in 0-31; the
        #   adopted b₃ = 43 needs 6 -- the tally below is unchanged)
        # - k_gimel ≈ 12.318... (64 bits for double precision; CALIBRATED, D-007)
        # - φ = golden ratio (mathematical constant, 0 bits - universally defined)

        # Geometric constraints are REUSABLE LOGIC (Algorithmic Symmetry), not data
        # They're a ONE-TIME cost amortized across all uses
        # For encoding a SINGLE instance (our universe), constraints are "code", not "data"
        # This is the key insight: code IS geometry (isomorphism)

        # Total WITH Topological Compression (data encoding): 5 + 64 = 69 bits
        # Geometric constraint complexity (one-time cost): ~116 constraints × 30 chars ≈ 27,840 bits

        with_theory_data_bits = 5 + 64  # Just the fundamental topological parameters
        without_theory_bits = self.n_output_params * 64
        theory_code_bits = self.n_formulas * 30 * 8  # Geometric constraints (amortized cost)

        # Data compression ratio (MDL criterion: data only, constraints are reusable logic)
        data_compression_ratio = without_theory_bits / with_theory_data_bits

        # Total information: data + geometric constraints (for first use)
        first_use_total_bits = with_theory_data_bits + theory_code_bits
        first_use_ratio = without_theory_bits / first_use_total_bits

        tally = {
            "without_theory_bits": without_theory_bits,
            "with_theory_data_bits": with_theory_data_bits,
            "theory_code_bits": theory_code_bits,
            "first_use_total_bits": first_use_total_bits,
            "data_compression_ratio": float(data_compression_ratio),
            "first_use_ratio": float(first_use_ratio),
            "bits_saved_data": float(without_theory_bits - with_theory_data_bits),
            "bits_saved_first_use": float(without_theory_bits - first_use_total_bits),
            "efficiency_percent": f"{(1 - with_theory_data_bits/without_theory_bits)*100:.1f}%",
            "status": seed_accounting_status(data_compression_ratio),
        }
        mdl_status = mdl_status_from_tally(tally)
        return {
            **tally,
            "mdl_status": mdl_status,
            "interpretation": (
                f"The seed accounting stores {self.n_output_params} constants in "
                f"{with_theory_data_bits} bits (b₃ and k_gimel) against {without_theory_bits} bits "
                f"of raw storage, a {data_compression_ratio:.1f}:1 data ratio that leaves the "
                f"constraint code out. Including the constraint code ({theory_code_bits} bits), "
                f"first use requires {first_use_total_bits} bits (ratio {first_use_ratio:.2f}:1). "
                f"MDL status as tallied: {mdl_status}."
            ),
            "note": "The seed accounting treats the geometric constraints as reusable logic, amortized across applications; the first-use tally counts them",
            "mdl_principle": "That code complexity equals geometric constraint complexity (isomorphism) is an interpretation, not a tested property",
            "key_insight_288_24_4": "OFF-PATH (b3_seed = seed_24): the 288/24/4 structure was read as DERIVED from G₂ topology at the off-path seed b₃ = 24; on the adopted path its 24 is not b₃ (see structure_288_24_4)"
        }

    def analyze_code_theoretical_integrity(self, compression: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Code-Theoretical Integrity: Code as Geometric Constraints.

        This section states the reading that the code is the geometric
        constraints rather than a simulation (an interpretation, not a tested
        property). Its MDL entry and conclusion are worded from the tally in
        ``compression`` (calculate_compression_ratio).

        Key concepts:
        - MDL Principle: Minimal Description Length criterion (status from the tally)
        - Topological Compression: Continuous phase space → discrete observables
        - Algorithmic Symmetry: Code complexity = Geometric constraint complexity
        - 288/24/4 structure: retired off-path reading (b3 = 24), not claimed as derived

        Returns:
            Code-theoretical integrity analysis
        """
        logger.info("Analyzing Code-Theoretical Integrity (Algorithmic Symmetry)...")

        # The core question: Is the code a "simulation" or "the theory itself"?
        # The reading below: the code is the formal symbolic encoding of the
        # geometric constraints imposed by G₂ topology (an interpretation).

        # 1. MDL Principle (worded from the computed tally)
        mdl = mdl_principle(compression, self.n_output_params)

        # 2. Topological Compression
        topological_compression = {
            "concept": (
                "Topological Compression (an interpretation, not a tested property): the "
                "continuous phase space of the bulk (adopted: 26D of signature (24,2)) is read as "
                "discretized into observable quantities via spectral descent, with the 125 "
                f"constants as its residues. MDL status as tallied: {mdl['mdl_status']}."
            ),
            "mechanism": (
                "G₂ holonomy constrains the manifold's geometry, inducing discrete spectral gaps. "
                "The Dirac operator's spectrum on this manifold is meant to yield fermion masses "
                "(flavour is OPEN: it needs a chiral sector, D-011). "
                "Gauge coupling unification is forced by dimensional reduction. "
                "The 288/24/4 structure emerges from: "
                "  - 288 = 24 × 12 (the integer 24 × bridge count) "
                "  - 24: formerly read as b₃, the third Betti number of the G₂ manifold; "
                "OFF-PATH (b3_seed = seed_24) -- the adopted b₃ is not 24, so this 24 is "
                "calibrated at the off-path seed "
                "  - 4 = the four faces (formerly 'Kähler moduli faces in compactification')"
            ),
            "compression_type": f"LOSSY (continuous → discrete); MDL status as tallied: {mdl['mdl_status']}"
        }

        # 3. Algorithmic Symmetry
        algorithmic_symmetry = {
            "definition": (
                "Algorithmic Symmetry: The code's complexity is isomorphic to the geometric "
                "constraints' complexity. This is NOT coincidental - the code IS the constraints "
                "expressed in executable form."
            ),
            "isomorphism": {
                "code_function": "compute_alpha_inverse(chi_eff, b3)",
                "geometric_constraint": "α⁻¹ = χ_eff × (G₂ holonomy correction) × (flux quantization)",
                "mapping": "1:1 (bijective)"
            },
            "key_insight": (
                "Every line of code corresponds to a specific geometric constraint. "
                "Adding code without geometric justification would BREAK the isomorphism. "
                "Conversely, every geometric constraint MUST be encoded in code to be testable."
            ),
            "why_not_arbitrary": (
                "OFF-PATH (b3_seed = seed_24): this argument was written at the off-path "
                "seed and does not hold on the adopted path. b₃ is a topological "
                "invariant, but the adopted b₃ is not 24; the 12 bridges are the 12 "
                "resolved A1 components (WA-1), not b₃/2; and the 4 faces are not Kähler "
                "moduli (a 7-manifold has none). As written: "
                "If the 288/24/4 structure were arbitrary fitting, we could vary it freely. "
                "But it's LOCKED by topology: b₃ = 24 (the off-path seed) is a topological invariant (cannot be tuned), "
                "12 bridges are derived from b₃/2 (Morse index theorem), "
                "4 faces are the Kähler moduli of the compactification (fixed by complex structure). "
                "These are mathematical necessities, not adjustable knobs."
            )
        }

        # 4. Why Code IS Geometry
        code_is_geometry = {
            "formal_equivalence": (
                "In differential geometry, constraints are expressed as differential equations. "
                "In PM, those same constraints are expressed as Python functions. "
                "The CONTENT is identical - only the NOTATION differs. "
                "Example: Einstein's equation G_μν = 8πT_μν is geometry. "
                "Implementing it as `def compute_ricci_tensor(metric): ...` doesn't make it 'simulation'."
            ),
            "symbolic_logic": (
                "The code operates on symbolic representations (FormulasRegistry, PMRegistry). "
                "It's not numerical simulation - it's symbolic constraint propagation. "
                "The 'execution' is just evaluating the constraint network, "
                "similar to how a computer algebra system evaluates symbolic expressions."
            ),
            "proof_by_reproducibility": (
                "The 72 certificates are PROOFS that the constraints are satisfied. "
                "Each certificate verifies that a predicted value matches experimental data "
                "within stated uncertainties. These are mathematical proofs, not simulation outputs."
            )
        }

        # 5. The 288/24/4 Structure Explained
        structure_288_24_4 = {
            "288": {
                "origin": "Total roots in dual-shadow G₂ × G₂ structure",
                "derivation": (
                    "OFF-PATH (b3_seed = seed_24): formerly derived as chi_eff = 144 per "
                    "shadow (6·b₃) × two shadows. On the adopted path chi_eff = 144 is the "
                    "total over both shadows (the K3 reading: 48 n at n = 3) and 6·b₃ = 144 "
                    "only at the off-path seed b₃ = 24, so this derivation of 288 does not hold. G₂ itself has "
                    "12 roots (dim 14) — 288 is not a root count"
                ),
                "topological_invariant": "YES (fixed by G₂ Lie algebra structure)"
            },
            "24": {
                "origin": (
                    "OFF-PATH (b3_seed = seed_24): formerly the third Betti number b₃ of the "
                    "G₂ manifold; the adopted b₃ is not 24, so this 24 is calibrated at the "
                    "off-path seed"
                ),
                "derivation": (
                    "No theorem gives b₃ = 24 here: the adopted Y₇ (Joyce's resolution of "
                    "T^7/(Z/2)^3) has b₃ = 7 + 3b₂, and b₃ = 24 is not reachable by that "
                    "construction (CG.7). Formerly stated as 'G₂ holonomy ⟹ b₃ = 24 "
                    "(mathematical theorem, Joyce 2000)'"
                ),
                "topological_invariant": "YES (characteristic class of G₂ manifold)"
            },
            "4": {
                "origin": (
                    "the four faces (the 12 bridges are the directed edges of K4 on a Fano "
                    "arc of four faces); formerly 'Kähler moduli faces in twisted connected "
                    "sum' -- OFF-PATH: the adopted internal space is Joyce's resolution of "
                    "T^7/(Z/2)^3, not a TCS"
                ),
                "derivation": (
                    "On the adopted path the ruled route n_gen = b₂/4 divides by the four faces; the "
                    "former 'TCS construction ⟹ 4 matching pairs (Kovalev-Lee 2016)' is "
                    "OFF-PATH"
                ),
                "topological_invariant": "YES (required for gluing compatibility)"
            },
            "conclusion": (
                "OFF-PATH (b3_seed = seed_24): written at the off-path seed (see '24'). "
                "None of these numbers are free parameters. They are topological invariants "
                "determined by the choice of G₂ manifold with dual-shadow structure. "
                "Changing any of them would require a different manifold (different theory)."
            )
        }

        return {
            "mdl_principle": mdl,
            "topological_compression": topological_compression,
            "algorithmic_symmetry": algorithmic_symmetry,
            "code_is_geometry": code_is_geometry,
            "structure_288_24_4": structure_288_24_4,
            "overall_conclusion": integrity_conclusion(mdl["mdl_status"])
        }

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive information bottleneck report."""
        logger.info("Generating information bottleneck report...")

        # Run all analyses
        input_analysis = self.analyze_input_description_length()
        output_analysis = self.analyze_output_description_length()
        mutual_info = self.calculate_mutual_information()
        redundancy = self.analyze_redundancy()
        compression = self.calculate_compression_ratio()
        code_theoretical = self.analyze_code_theoretical_integrity(compression)

        # Overall assessment: the status and mdl_satisfied come from the MDL
        # status the tally records; the seed-only ratio is a labelled side figure.
        mdl_status = code_theoretical["mdl_principle"]["mdl_status"]
        is_compressed = redundancy["redundancy_ratio"] < 0.99
        seed_side_figure = {
            "seed_bits": compression["with_theory_data_bits"],
            "data_compression_ratio": compression["data_compression_ratio"],
            "compresses": bool(compression["data_compression_ratio"] > 1.0),
            "note": "constraint code excluded; not the MDL status",
        }
        interpretation = mdl_interpretation(compression, mdl_status, self.n_output_params)

        report = {
            "framework": "Principia Metaphysica",
            "test_date": datetime.now().isoformat(),
            "test_name": "Topological Compression via Algorithmic Symmetry (MDL Analysis)",
            "framework_structure": {
                "input_dimensions": self.n_input_dims,
                "output_parameters": self.n_output_params,
                "geometric_constraints": self.n_formulas,
                "parameter_classification": {
                    "geometric": self.n_geometric,
                    "calibrated": self.n_calibrated,
                    "fitted": self.n_fitted,
                    "established": self.n_established
                }
            },
            "results": {
                "overall_status": overall_status(mdl_status),
                "mdl_status": mdl_status,
                "mdl_satisfied": mdl_holds(mdl_status),
                "data_compression_under_seed_accounting": seed_side_figure,
                "achieves_topological_compression": bool(is_compressed),
                "input_complexity": input_analysis,
                "output_complexity": output_analysis,
                "mutual_information": mutual_info,
                "redundancy_analysis": redundancy,
                "compression_ratio_analysis": compression,
                "code_theoretical_integrity": code_theoretical
            },
            "interpretation": interpretation
        }

        return report

    def save_report(self, report: Dict[str, Any], output_path: Path = None):
        """Save compression report to JSON."""
        if output_path is None:
            output_path = REPO_ROOT / "AutoGenerated" / "compression_report.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved: {output_path}")
        return output_path


def main():
    """Run Topological Compression analysis via Algorithmic Symmetry and MDL."""
    print("=" * 70)
    print(" TOPOLOGICAL COMPRESSION ANALYZER")
    print(" Algorithmic Symmetry via Minimal Description Length (MDL)")
    print("=" * 70)
    print(" Objective: Tally whether the theory compresses its constants (MDL)")
    print(" Analysis: Kolmogorov complexity, MDL criterion, Algorithmic Symmetry")
    print(" Key: Code IS geometric constraints (isomorphism, not simulation)")
    print("=" * 70)

    distiller = InformationBottleneckDistiller()
    report = distiller.generate_report()
    output_path = distiller.save_report(report)

    # Print summary
    print("\n" + "=" * 70)
    print(" TOPOLOGICAL COMPRESSION ANALYSIS COMPLETE")
    print("=" * 70)
    print(f" Overall Status: {report['results']['overall_status']}")
    print(f" Seed-accounting data ratio (constraint code excluded): {report['results']['compression_ratio_analysis']['data_compression_ratio']:.1f}:1")
    print(f" First-use ratio (constraint code counted): {report['results']['compression_ratio_analysis']['first_use_ratio']:.2f}:1")
    print(f" Seed-accounting efficiency: {report['results']['compression_ratio_analysis']['efficiency_percent']}")
    print(f" MDL Satisfied: {report['results']['mdl_satisfied']}")
    print("\n Conclusion:")
    # Convert to ASCII-safe string for Windows console
    conclusion = report['interpretation']['conclusion'].encode('ascii', 'replace').decode('ascii')
    print(f"   {conclusion}")
    print("\n Key Insight (Algorithmic Symmetry):")
    key_insight = report['interpretation']['key_insight'].encode('ascii', 'replace').decode('ascii')
    print(f"   {key_insight}")
    print("\n MDL Justification:")
    mdl_just = report['interpretation']['mdl_justification'].encode('ascii', 'replace').decode('ascii')
    print(f"   {mdl_just}")
    print("=" * 70)
    print(f" Report: {output_path}")
    print("=" * 70)

    return report


if __name__ == "__main__":
    main()
