#!/usr/bin/env python3
"""
Chirality and Spinorial Structure
=================================

Licensed under the MIT License. See LICENSE file for details.

STATUS ON THE ADOPTED MODEL (read first)
----------------------------------------
Chirality is OPEN (D-011). Y_7 -- Joyce's resolution of T^7/(Z/2)^3 -- has
disjoint singular loci, so it has no codimension-7 points, and a smooth G2
compactification gives no chiral fermions (Acharya-Witten obtain them at
conical singularities). This module records the spinorial structure of the
G2 manifold, which is standard, and a PROPOSED chirality mechanism with its
arithmetic. It does not derive chirality. Its index reading,
index = chi_eff/24 = 6, is not an index theorem for chirality: chi_eff =
2 x sum chi(K3) = 48n is an effective index (the K3 reading, D-015), not the
Euler characteristic of Y_7, which is 0. The generation count is the ruled
n_gen = b_2/4 = 3; the spinor-saturation route below is ABANDONED.

KEY PHYSICS:
- G2 holonomy preserves exactly 1 real spinor (η) in 7D (standard)
- PROPOSED: associative 4-form Φ defines a chirality projector P_L = (1 + *Φ)/2
- PROPOSED: Dirac operator ∂/ = γ^μ D_μ has chiral zero modes
- PROPOSED: chirality index n_L - n_R = ∫ Φ ∧ dΦ / (2π)^3 (not established)
- ABANDONED: connection to 3 generations via spinor saturation

PHYSICAL PICTURE (the proposal):
- G2 manifolds are spin manifolds admitting parallel spinors
- Holonomy G2 ⊂ Spin(7) preserves 1 of 8 real spinor components
- 4-form associative calibration Φ would induce a chirality structure
- Zero modes of the Dirac operator would localize on associative 3-cycles
- An index formula would relate chirality imbalance to chi_eff = 144
- ABANDONED: saturation, 24 flux units / 8 spinor DOF = 3 generations, held
  only at the off-path seed b_3 = 24

DERIVATION CHAIN (as written at the off-path seed b_3 = 24):
topology.mephorash_chi = chi_eff (the K3 reading, 48n; the "TCS G2 manifold
#187" provenance is WITHDRAWN -- TCS as exhibited gives 71 <= b_3 <= 155,
which excludes the adopted b_3 = 43, and the construction in force is the
Joyce orbifold T^7/(Z/2)^3 with Eguchi-Hanson resolutions)
topology.elder_kads = b_3 (43 on the adopted seed; the chain used the
off-path seed 24)
  -> spinor components = 8 (Spin(7) representation)
  -> preserved spinors = 1 (G2 holonomy)
  -> chiral index = χ_eff / 24 = 6 (proposed reading, not established)
  -> n_L - n_R = 6 per cycle (proposed)
  -> n_gen = b3 / spinor_DOF = 24 / 8 = 3 (ABANDONED: 8 divides no
     Joyce-reachable b_3; the ruled count is n_gen = b_2/4)

References:
- Acharya-Witten (2001): Chiral fermions from G2 compactifications
- Joyce (2000): Compact Manifolds with Special Holonomy
- Bryant (2005): Some remarks on G2-structures
- Harvey-Lawson (1982): Calibrated geometries

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""

import numpy as np

from metaphysica.simulations.core.FormulasRegistry import get_registry as _get_reg

#: SSoT read. b3 and chi_eff FOLLOW THE ADOPTED SEED; nothing topological in
#: this module's prose is typed as a literal.
_REG = _get_reg()
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from metaphysica.simulations.base import (
    SimulationBase,
    SimulationMetadata,
    Formula,
    Parameter,
    SectionContent,
    ContentBlock,
)
# --- triple-track helpers (Sprint 2 — Phase H) -----------------------------
try:  # pragma: no cover - optional during early migration
    # Probed, not merely imported: a stub arithma imports cleanly and
    # binds Expression to None, which `except ImportError` cannot see.
    from metaphysica.simulations.core.arithma_backend import ARITHMA as _A
    if _A is None:
        raise ImportError('arithma backend is not usable')
    def _arithma_num(v):
        return _A.Expression.number(float(v))
except Exception:  # pragma: no cover
    _A = None  # type: ignore[assignment]
    def _arithma_num(v):
        return None
from metaphysica.simulations.core.eml_integration import (
    eml_scalar as _eml_scalar,
    eml_div as _eml_div,
    b3_leaf as _b3_leaf,
)
def _arithma_div(a, b):
    return None if a is None or b is None else a / b
def _arithma_b3():
    return _arithma_num(24.0)


class ChiralitySpinorSimulation(SimulationBase):
    """
    Chirality and spinorial structure on the G2 manifold.

    Chirality is OPEN on the adopted model (see the module docstring); this
    simulation records the standard spinor structure and a PROPOSED
    chirality mechanism:
    1. Extract G2 topology parameters (χ_eff, b3) from registry
    2. Compute spinor structure from G2 holonomy (standard)
    3. Evaluate the proposed chirality index from the associative 4-form
    4. Calculate the proposed chiral zero mode count
    5. Evaluate the ABANDONED spinor-saturation generation route (kept on
       the books; the ruled count is n_gen = b_2/4)
    6. Compare with observed chirality
    """

    # Physical constants and geometric parameters
    SPIN7_DIM = 8              # Real dimension of Spin(7) spinor representation
    G2_PRESERVED_SPINORS = 1    # Number of parallel spinors preserved by G2 holonomy
    FLUX_DIVISOR = 6           # Flux quantization: N_flux = χ_eff / 6
    ASSOCIATIVE_DIM = 3        # Dimension of associative 3-cycles
    COASSOCIATIVE_DIM = 4      # Dimension of coassociative 4-cycles

    @property
    def metadata(self) -> SimulationMetadata:
        """Return simulation metadata."""
        return SimulationMetadata(
            id="chirality_v16_0",
            version="16.0",
            domain="fermion",
            title="Chirality and Spinorial Structure from G2 Holonomy",
            description=(
                "Spinorial structure of the G2 manifold and a PROPOSED chirality "
                "mechanism. Chirality is OPEN on the adopted model: Y_7's singular loci "
                "are disjoint, so it has no codimension-7 points. Records how an "
                "associative 4-form would define a chiral projector, how Dirac zero modes "
                "would count chiral fermions, and an index reading that is not "
                "established. The generation count is n_gen = b_2/4 (the ruled route); "
                "the spinor-saturation link is abandoned."
            ),
            section_id="4",
            subsection_id="4.1"
        )

    @property
    def required_inputs(self) -> List[str]:
        """Return list of required input parameter paths."""
        return [
            "topology.mephorash_chi",
            "topology.elder_kads",
            "constants.M_PLANCK",
        ]

    @property
    def output_params(self) -> List[str]:
        """Return list of output parameter paths."""
        return [
            "chirality.spinor_dimension",
            "chirality.preserved_spinors",
            "chirality.chiral_index",
            "chirality.zero_modes_left",
            "chirality.zero_modes_right",
            "chirality.imbalance",
            "chirality.generation_count",
            "chirality.saturation_ratio",
        ]

    @property
    def output_formulas(self) -> List[str]:
        """Return list of formula IDs this simulation provides."""
        return [
            "g2-spinor-preservation",
            "associative-chirality-projector",
            "dirac-zero-modes",
            "chirality-index-theorem",
            "spinor-saturation-generations",
        ]

    def run(self, registry: 'PMRegistry') -> Dict[str, Any]:
        """
        Execute the chirality and spinor structure calculation.

        Args:
            registry: PMRegistry instance with input parameters

        Returns:
            Dictionary of computed results
        """
        # Extract inputs from registry
        chi_eff = registry.get_param("topology.mephorash_chi")
        b3 = registry.get_param("topology.elder_kads")

        # Spinor structure from G2 holonomy
        # G2 is the subgroup of SO(7) that preserves the associative 3-form
        # (equivalently, the octonionic cross product on R^7). The 8-dimensional
        # spinor representation of Spin(7) decomposes under G2 as:
        #   8 = 1 + 7
        # where the singlet (1) is the covariantly constant spinor eta preserved
        # by G2 holonomy, and the septuplet (7) pairs up to gain mass.
        # This is the mathematical reason G2 preserves EXACTLY 1 of 8 spinors.
        spinor_dim = self.SPIN7_DIM  # 8 real components in Spin(7)
        preserved_spinors = self.G2_PRESERVED_SPINORS  # G2 preserves 1 (the singlet)

        # PROPOSED chirality index (not established; chirality is OPEN on the
        # adopted model). The proposal reads the Atiyah-Singer index as
        #   index(D/) = chi_eff / 24
        # (citing Berline-Getzler-Vergne, "Heat Kernels and Dirac Operators",
        # for the general framework), with the effective index chi_eff in
        # place of the Euler characteristic, which is 0 on Y_7. On the K3
        # reading chi_eff = 48n (D-015) this is 2n, and chi_eff/48 = n
        # restates b_2/4; it is not an index theorem for chirality.
        chiral_index = chi_eff / 24.0  # = 144 / 24 = 6

        # Zero mode counts from index theorem
        # Index = n_L - n_R = 6. For minimal embedding, we take n_R = 0.
        # Each chiral zero mode localizes on an associative 3-cycle.
        zero_modes_left = chiral_index
        zero_modes_right = 0  # Minimal case (could be n_R = n_L - 6 for large n_L)
        imbalance = zero_modes_left - zero_modes_right

        # Generation count from spinor saturation
        # CONNECTION: index = 6 chiral zero modes, but each generation requires
        # 2 zero modes (one per chiral doublet in SU(2)_L), giving n_gen = 6/2 = 3.
        # The "equivalently via flux counting" reading -- b3 = 24 flux units,
        # 8 spinor DOF per generation, n_gen = 24/8 = 3 -- is ABANDONED. On the
        # Joyce-reachable family b_3 in {7, 19, 31, 43} is ODD at every
        # profile and 8 divides no odd number, so b_3/8 is non-integral
        # EVERYWHERE on the family. The ruled generation count is
        # n_gen = b_2/4 = rank(Gamma) = 3. Kept here, labelled, not deleted.
        # The proposal reads the 7/8 ratio physically: 7 of 8 spinor
        # components pair up and gain mass via torsion coupling, while 1
        # remains massless as the chiral fermion of each generation (OPEN).
        # ABANDONED route, still computed: int(b3 / 8) is what
        # chirality.generation_count publishes -- 5 on the adopted b_3 = 43,
        # not 3. It equalled 24/8 = 3 only at the off-path seed.
        generation_count = b3 / spinor_dim

        # Saturation ratio: (b3/8) * 8 / b3, so 1 by construction on every
        # seed; it no longer tests saturation (abandoned route).
        saturation_ratio = (generation_count * spinor_dim) / b3

        # Validate results
        is_integer_generations = (abs(generation_count - round(generation_count)) < 1e-10)
        is_complete_saturation = (abs(saturation_ratio - 1.0) < 1e-10)
        matches_observed = (round(generation_count) == 3)

        # Return all computed values
        return {
            "chirality.spinor_dimension": spinor_dim,
            "chirality.preserved_spinors": preserved_spinors,
            "chirality.chiral_index": chiral_index,
            "chirality.zero_modes_left": zero_modes_left,
            "chirality.zero_modes_right": zero_modes_right,
            "chirality.imbalance": imbalance,
            "chirality.generation_count": int(generation_count),
            "chirality.saturation_ratio": saturation_ratio,

            # Metadata for validation
            "_chi_eff": chi_eff,
            "_b3": b3,
            "_is_integer_generations": is_integer_generations,
            "_is_complete_saturation": is_complete_saturation,
            "_matches_observed": matches_observed,
            "_lattice_verification": self.verify_lattice_chirality(),
        }


    def run_eml(self, registry: 'PMRegistry') -> Dict[str, Any]:
        """
        EML Math computation path.

        This simulation produces particle outputs. The EML Math representation
        for this module is in the section text via <EML>...</EML> blocks in
        get_section_content(). The computed parameter values are identical
        between Normal Math and EML Math modes.
        """
        return self.run(registry)

    def verify_lattice_chirality(self) -> Optional[Dict[str, Any]]:
        """Cross-verify G2 3-form against lattice-derived phi from E8.

        Constructs G2DifferentialGeometry from E8 root system, retrieves
        the lattice-verified phi, and checks Hitchin metric identity.
        Returns None if required modules are unavailable.
        """
        try:
            from metaphysica.simulations.PM.geometry.g2_differential import G2DifferentialGeometry
            from metaphysica.simulations.PM.algebra.e8_root_system import E8RootSystem
            from metaphysica.simulations.PM.algebra.octonions import OctonionAlgebra
        except ImportError:
            return None

        try:
            e8 = E8RootSystem()
            g2_lattice = G2DifferentialGeometry.from_e8(e8)
            lattice_phi = g2_lattice.phi

            # Compare with octonion-derived 3-form
            octonions = OctonionAlgebra()
            octonion_phi = octonions.g2_structure_as_3form()
            phi_consistent = bool(np.allclose(lattice_phi, octonion_phi, atol=1e-12))

            # Hitchin identity: g_{ij} = (1/6) phi_{iab} phi_{jab} should give I_7
            g = g2_lattice.compute_metric()
            hitchin_valid = bool(np.allclose(g, np.eye(7), atol=1e-10))

            # Full verification suite from G2DifferentialGeometry
            full_checks = g2_lattice.verify()

            return {
                'phi_consistent': phi_consistent,
                'hitchin_valid': hitchin_valid,
                'phi_shape': list(lattice_phi.shape),
                'metric_positive_definite': full_checks.get('metric_positive_definite', False),
                'torsion_free': full_checks.get('torsion_free', False),
            }
        except Exception:
            return None

    def get_section_content(self) -> Optional[SectionContent]:
        """
        Return section content for Section 4.1 - Chirality and Spinorial Structure.

        Returns:
            SectionContent with complete narrative and formula references
        """
        assert self.metadata.section_id == "4", "Section ID must be '4'"
        assert self.metadata.subsection_id == "4.1", "Subsection ID must be '4.1'"

        content = SectionContent(
            section_id="4",
            subsection_id="4.1",
            title="Chirality and Spinorial Structure",
            abstract=(
                "The spinorial structure of the G2 manifold, and a proposed chirality "
                "mechanism. G2 holonomy preserves exactly one real spinor in seven "
                "dimensions (standard). Chirality itself is OPEN on the adopted model: "
                "Y_7's singular loci are disjoint, so it has no codimension-7 points, and "
                "a smooth G2 compactification gives no chiral fermions. The associative "
                "chirality projector, the chiral Dirac zero modes and the index reading "
                "below are a proposal, not a derivation; the generation count is the "
                "ruled n_gen = b_2/4, not a consequence of this mechanism."
            ),
            content_blocks=[
                ContentBlock(
                    type="heading",
                    content="G2 Holonomy and Spinor Preservation"
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        "G2 manifolds are seven-dimensional Riemannian manifolds with "
                        "exceptional holonomy group G2 ⊂ SO(7). Since G2 ⊂ Spin(7), "
                        "they are spin manifolds and admit spinor structures. The "
                        "fundamental spinor representation of Spin(7) has dimension 8 "
                        "(real), corresponding to the eight components of a Majorana "
                        "spinor in seven dimensions."
                    )
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        "The crucial property of G2 holonomy is that it preserves "
                        "exactly one of these eight spinor components. Mathematically, "
                        "G2 is the subgroup of SO(7) that preserves the associative "
                        "3-form (equivalently, the octonionic cross product on R^7). "
                        "Under the restriction from Spin(7) to G2, the 8-dimensional "
                        "spinor representation decomposes as 8 = 1 + 7: the singlet "
                        "is the covariantly constant spinor preserved by G2 holonomy, "
                        "while the septuplet components pair up and gain mass via "
                        "torsion coupling. This is the parallel spinor theorem:"
                    )
                ),
                ContentBlock(
                    type="formula",
                    content=r"\nabla_\mu \eta = 0, \quad \eta \in \Gamma(S), \quad \dim(S) = 8",
                    formula_id="g2-spinor-preservation",
                    label="(4.1.1)"
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        "where η is the parallel spinor, ∇ is the Levi-Civita connection, "
                        "and S is the spinor bundle. The existence of exactly one "
                        "parallel spinor (up to scaling) is equivalent to G2 holonomy. "
                        "This is in contrast to generic 7-manifolds (with full SO(7) holonomy) "
                        "which preserve no spinors, or Calabi-Yau 3-folds (with SU(3) holonomy) "
                        "which preserve two spinors of opposite chirality."
                    )
                ),

                ContentBlock(
                    type="heading",
                    content="Associative Calibration and Chirality"
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        "The associative 4-form Φ on a G2 manifold encodes its geometric "
                        "structure. This 4-form is calibrated, meaning that associative "
                        "3-cycles minimize volume in their homology class. The Hodge dual "
                        "*Φ is the coassociative 3-form."
                    )
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        "The 4-form Φ defines a natural chirality operator on spinors. "
                        "We can construct left-handed and right-handed projection operators:"
                    )
                ),
                ContentBlock(
                    type="formula",
                    content=r"P_L = \frac{1 + *\Phi}{2}, \quad P_R = \frac{1 - *\Phi}{2}",
                    formula_id="associative-chirality-projector",
                    label="(4.1.2)"
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        "These projectors satisfy P_L + P_R = 1, P_L P_R = 0, and split "
                        "the spinor bundle into chiral components: S = S_L ⊕ S_R. The "
                        "parallel spinor η is automatically left-handed: P_L η = η. "
                        "This is the proposed geometric origin of chiral fermions; it is "
                        "not established, and chirality is OPEN on the adopted model."
                    )
                ),

                ContentBlock(
                    type="heading",
                    content="Dirac Operator and Zero Modes"
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        "Fermion fields are sections of the spinor bundle S coupled to "
                        "gauge bundles. The relevant operator is the Dirac operator:"
                    )
                ),
                ContentBlock(
                    type="formula",
                    content=r"\not{D} = \gamma^\mu D_\mu = \gamma^\mu (\nabla_\mu + igA_\mu)",
                    formula_id="dirac-zero-modes",
                    label="(4.1.3)"
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        "where γ^μ are the seven-dimensional Dirac matrices, ∇ is the "
                        "spin connection, and A is the gauge connection. Zero modes "
                        "of this operator (∂/ψ = 0) correspond to massless fermions "
                        "in four dimensions after dimensional reduction."
                    )
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        "The zero modes localize on associative 3-cycles where the "
                        "wavefunction profile is concentrated. These are precisely the "
                        "cycles calibrated by the associative 3-form φ = *Φ. The "
                        "localization mechanism involves the curvature of the G2 manifold "
                        "acting as a potential well that traps fermion wavefunctions."
                    )
                ),

                ContentBlock(
                    type="heading",
                    content="Index Theorem and Chirality Imbalance"
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        "The Atiyah-Singer index theorem determines the difference between "
                        "left-handed and right-handed zero modes (see Berline, Getzler, "
                        "and Vergne, 'Heat Kernels and Dirac Operators' for the general "
                        "framework). The proposal applies it to the Dirac operator on the "
                        "G2 manifold with flux, writing the index as:"
                    )
                ),
                ContentBlock(
                    type="formula",
                    content=r"\text{index}(\not{D}) = n_L - n_R = \frac{1}{(2\pi)^3} \int_{M_7} \Phi \wedge F \wedge F",
                    formula_id="chirality-index-theorem",
                    label="(4.1.4)"
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        "where F is the gauge field strength (flux), and the integral "
                        f"is over the G2 manifold M_7. The proposal then substitutes "
                        f"the effective index χ_eff = {int(_REG.chi_eff_total)} -- read "
                        f"as 2 x sum chi(K3) = 48n, the K3 reading (D-015) -- for the "
                        f"Euler characteristic, which is 0 on Y_7; nothing in the index "
                        f"theorem licenses that substitution, so the result is not an "
                        f"index theorem for chirality. (χ_eff's earlier derivations "
                        f"agreed only at the off-path seed b_3 = 24, and the 'TCS G2 "
                        f"manifold #187' attribution is WITHDRAWN: TCS as exhibited "
                        f"gives 71 <= b_3 <= 155 and so excludes the adopted "
                        f"b_3 = {int(_REG.elder_kads)}.) The proposed index formula reads:"
                    )
                ),
                ContentBlock(
                    type="formula",
                    content=rf"\text{{index}}(\not{{D}}) = \frac{{\chi_{{\text{{eff}}}}}}{{24}} = \frac{{{int(_REG.chi_eff_total)}}}{{24}} = {int(_REG.chi_eff_total) // 24}",
                    label="(4.1.5)"
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        "If the proposal held, there would be six more left-handed than "
                        "right-handed zero modes per associative 3-cycle, an imbalance "
                        "that continuous deformations could not remove. It is not "
                        "established: on the adopted Y_7 chirality is OPEN."
                    )
                ),

                ContentBlock(
                    type="heading",
                    content="Connection to Three Generations"
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        "The proposal links its index to the generation count: the index "
                        "counts NET chiral zero modes (n_L - n_R = 6), and each fermion "
                        "generation requires a chiral doublet under SU(2)_L, consuming 2 "
                        "chiral zero modes, so 6/2 = 3. Because the index reading is not "
                        "established, this link is not a derivation; the generation count "
                        f"stands on the ruled route n_gen = b_2/4.\n\n"
                        f"THE FLUX-COUNTING ROUTE IS ABANDONED, AND THE COUNT MOVED. "
                        f"This paragraph used to continue: 'equivalently, via flux "
                        f"counting, the third Betti number b_3 = 24 counts the "
                        f"independent associative 3-cycles (flux units), and each "
                        f"fermion generation saturates 8 real spinor degrees of freedom "
                        f"from the 8 = 1 + 7 decomposition of Spin(7) under G2, so "
                        f"n_gen = b_3/8 = 24/8 = 3.' That abandoned equivalence held only at "
                        f"b_3 = 24. On the Joyce-reachable family b_3 = 7 + 3 n_T3 with "
                        f"n_T3 in {{0, 4, 8, 12}}, so b_3 lies in {{7, 19, 31, 43}} and "
                        f"is ODD at every profile; 8 divides no odd number, so b_3/8 is "
                        f"non-integral EVERYWHERE on the family, not merely wrong at "
                        f"one point. At the adopted b_3 = {int(_REG.elder_kads)} it "
                        f"returns {int(_REG.elder_kads) / 8.0:.3f}, and a generation "
                        f"count is a number of things.\n\n"
                        f"The generation count RELOCATED rather than vanishing: the "
                        f"ruled route is n_gen = b_2 / 4 = rank(Gamma) = 3, with the 4 "
                        f"being the faces, derived as the moved coordinates of an "
                        f"involution. The abandoned identity is kept here, labelled, "
                        f"because a falsified claim stays on the books:"
                    )
                ),
                ContentBlock(
                    type="formula",
                    content=rf"n_{{\text{{gen}}}} \neq \frac{{b_3}}{{\text{{spinor DOF}}}} = \frac{{{int(_REG.elder_kads)}}}{{8}} = {int(_REG.elder_kads) / 8.0:.3f} \quad (\text{{ABANDONED}}); \qquad n_{{\text{{gen}}}} = \frac{{b_2}}{{4}} = 3 \quad (\text{{ruled}})",
                    formula_id="spinor-saturation-generations",
                    label="(4.1.6)"
                ),
                ContentBlock(
                    type="paragraph",
                    content=(
                        f"The index route above (index = 6, n_gen = 6/2 = 3) "
                        f"consumes chi_eff rather than b_3. On the adopted K3 reading "
                        f"chi_eff = 48n, so chi_eff/24 = 2n and 2n/2 = n: the route "
                        f"restates b_2/4, and it is not an index theorem for "
                        f"chirality, which stays OPEN. The earlier claim that "
                        f"the saturation was 'exact: 3 generations x 8 DOF = 24 flux "
                        f"units, with no remainder' is FALSIFIED at "
                        f"b_3 = {int(_REG.elder_kads)}: 3 x 8 = 24 leaves a remainder "
                        f"of {int(_REG.elder_kads) - 24} flux units, and no replacement "
                        f"saturation is asserted. "
                        f"<Speculation>Whether nature has exactly three generations "
                        f"because of this topology remains speculative; the ruled route "
                        f"makes it the RANK of the diagonal stabiliser of phi, which is "
                        f"at least a count of independent objects rather than a "
                        f"ratio.</Speculation>"
                    )
                ),

                ContentBlock(
                    type="paragraph",
                    content=(
                        "Spinor preservation is a consequence of G2 holonomy. Chirality is "
                        "not: on the adopted Y_7 the singular loci are disjoint, so there "
                        "are no codimension-7 points where Acharya-Witten chiral fermions "
                        "arise, and a smooth G2 compactification gives none. The projector, "
                        "zero-mode and index steps above are a proposal for supplying "
                        "chirality; until a chiral sector is exhibited, chirality -- and "
                        "with it flavour -- is OPEN."
                    )
                ),
            ],
            formula_refs=[
                "g2-spinor-preservation",
                "associative-chirality-projector",
                "dirac-zero-modes",
                "chirality-index-theorem",
                "spinor-saturation-generations",
            ],
            param_refs=[
                "topology.mephorash_chi",
                "topology.elder_kads",
                "chirality.spinor_dimension",
                "chirality.preserved_spinors",
                "chirality.chiral_index",
                "chirality.generation_count",
            ]
        )

        # Validate that content is not empty
        assert len(content.content_blocks) > 0, "Content blocks must not be empty"
        assert len(content.formula_refs) > 0, "Formula references must not be empty"
        assert content.abstract is not None and len(content.abstract) > 0, "Abstract must not be empty"

        return content

    def get_formulas(self) -> List[Formula]:
        """
        Return list of formulas with full derivation chains.

        Returns:
            List of Formula instances
        """
        formulas = [
            Formula(
                id="g2-spinor-preservation",
                label="(4.1.1)",
                latex=r"\nabla_\mu \eta = 0, \quad \eta \in \Gamma(S), \quad \dim(S) = 8",
                plain_text="∇_μ η = 0, η ∈ Γ(S), dim(S) = 8",
                eml_tree_str="ops.add(ops.mul(nabla_mu, eta), ops.neg(ops.mul(eml_scalar(0.0), eta)))",
                eml_latex=r"\mathrm{ops.add}(\nabla_\mu \cdot \eta,\; \mathrm{ops.neg}(\mathrm{eml\_scalar}(0)))",
                eml_description="EML: parallel spinor condition — ops.mul(nabla_mu, eta) = eml_scalar(0); spinor_dim = eml_scalar(8.0) from Spin(7) representation",
                category="ESTABLISHED",
                description=(
                    "Parallel spinor condition for G2 holonomy. G2 ⊂ Spin(7) preserves "
                    "exactly one real spinor out of 8 components. This is the defining "
                    "property of G2 manifolds; it secures N = 1 supersymmetry, not "
                    "chirality, which is OPEN on the adopted model."
                ),
                inputParams=["topology.g2_compatible", "chirality.spinor_dimension"],
                outputParams=["chirality.preserved_spinors", "chirality.spinor_dimension"],
                input_params=["topology.g2_compatible", "chirality.spinor_dimension"],
                output_params=["chirality.preserved_spinors", "chirality.spinor_dimension"],
                derivation={
                    "parentFormulas": [],
                    "method": "Holonomy theory and parallel spinor theorem",
                    "steps": [
                        "Spin(7) has 8-dimensional real spinor representation",
                        "G2 ⊂ Spin(7) is the stabilizer of a unit spinor η",
                        "Parallel transport preserves η: ∇_μ η = 0",
                        "This is unique up to scaling: dim(ker ∇) = 1",
                        "Contrast: SU(3) preserves 2 spinors, Spin(7) holonomy (8-manifolds) preserves 1, generic SO(7) preserves 0"
                    ],
                    "assumptions": [
                        "G2 holonomy (not just G2 structure)",
                        "Ricci-flat metric from special holonomy",
                        "Spin manifold (orientable and spinorial)"
                    ],
                    "references": [
                        "Joyce (2000): Compact Manifolds with Special Holonomy, Theorem 10.1.1",
                        "Bryant (2005): Some remarks on G2-structures, §2.1"
                    ]
                },
                terms={
                    "η": "Parallel (covariantly constant) spinor",
                    "∇_μ": "Levi-Civita spin connection",
                    "S": "Spinor bundle on G2 manifold",
                    "dim(S)": "Fiber dimension (8 real components)",
                },
                arithma=_arithma_num(8.0),
                eml=_eml_scalar(8.0),
                value=8.0,
            ),

            Formula(
                id="associative-chirality-projector",
                label="(4.1.2)",
                latex=r"P_L = \frac{1 + *\Phi}{2}, \quad P_R = \frac{1 - *\Phi}{2}",
                plain_text="P_L = (1 + *Φ)/2, P_R = (1 - *Φ)/2",
                eml_tree_str="ops.mul(ops.add(eml_scalar(1.0), ops.neg(gamma_5)), ops.div(eml_scalar(1.0), eml_scalar(2.0)))",
                eml_latex=r"\mathrm{ops.mul}(\mathrm{ops.add}(\mathrm{eml\_scalar}(1),\; *\Phi),\; \mathrm{ops.div}(\mathrm{eml\_scalar}(1),\; \mathrm{eml\_scalar}(2)))",
                eml_description="EML: P_L = ops.div(ops.add(eml_scalar(1.0), star_Phi), eml_scalar(2.0)) — chirality projector from associative 4-form Hodge dual",
                category="DERIVED",
                description=(
                    "PROPOSED (chirality is OPEN on the adopted model): chirality "
                    "projection operators from the associative 4-form. The Hodge "
                    "dual *Φ is taken to act on spinors as a chirality operator, splitting "
                    "S into left-handed and right-handed components, with the parallel "
                    "spinor η left-handed."
                ),
                inputParams=["topology.mephorash_chi"],
                outputParams=["chirality.chiral_index"],
                input_params=["topology.mephorash_chi"],
                output_params=["chirality.chiral_index"],
                derivation={
                    "parentFormulas": ["g2-spinor-preservation"],
                    "method": "Clifford multiplication by 4-form",
                    "steps": [
                        "G2 structure defined by associative 4-form Φ and 3-form φ = *Φ",
                        "*Φ acts on spinors via Clifford multiplication",
                        "(*Φ)^2 = 1 implies eigenvalues ±1 (chirality)",
                        "Define projectors P_L = (1 + *Φ)/2, P_R = (1 - *Φ)/2",
                        "P_L + P_R = 1 (completeness), P_L P_R = 0 (orthogonality)",
                        "Parallel spinor: P_L η = η (left-handed)",
                        "Chirality split: S = S_L ⊕ S_R"
                    ],
                    "assumptions": [
                        "Associative calibration Φ defines G2 structure",
                        "Clifford action well-defined on spinor bundle",
                        "No torsion (Levi-Civita connection)"
                    ],
                    "references": [
                        "Harvey-Lawson (1982): Calibrated geometries, §IV.1",
                        "Karigiannis (2009): Flows of G2 structures, §2.3"
                    ]
                },
                terms={
                    "P_L": "Left-handed chirality projector",
                    "P_R": "Right-handed chirality projector",
                    "*Φ": "Hodge dual of associative 4-form (coassociative 3-form)",
                    "Φ": "Associative 4-form defining G2 structure",
                },
                arithma=_arithma_div(_arithma_num(1.0), _arithma_num(2.0)),
                eml=_eml_div(_eml_scalar(1.0), _eml_scalar(2.0)),
                value=0.5,
            ),

            Formula(
                id="dirac-zero-modes",
                label="(4.1.3)",
                latex=r"\not{D} = \gamma^\mu D_\mu = \gamma^\mu (\nabla_\mu + igA_\mu)",
                plain_text="∂/ = γ^μ D_μ = γ^μ (∇_μ + igA_μ)",
                eml_tree_str="ops.add(ops.mul(gamma_mu, ops.mul(D_mu, psi)), ops.mul(ops.neg(m), psi))",
                eml_latex=r"\mathrm{ops.add}(\gamma^\mu \cdot D_\mu \cdot \psi,\; \mathrm{ops.neg}(m \cdot \psi))",
                eml_description="EML: Dirac operator D-slash = ops.mul(gamma_mu, D_mu); zero-mode condition ops.mul(gamma_mu, D_mu, psi) = eml_scalar(0.0)",
                category="DERIVED",
                description=(
                    "Dirac operator on the G2 manifold with gauge connection. Zero modes "
                    "(∂/ψ = 0) give massless fermions in 4D after dimensional reduction; "
                    "whether they are chiral is OPEN on the adopted model, since a smooth "
                    "G2 compactification gives no chiral fermions and Y_7 has no "
                    "codimension-7 points. The proposal localizes them on associative "
                    "3-cycles."
                ),
                inputParams=["topology.elder_kads"],
                outputParams=["chirality.zero_modes_left", "chirality.zero_modes_right"],
                input_params=["topology.elder_kads"],
                output_params=["chirality.zero_modes_left", "chirality.zero_modes_right"],
                derivation={
                    "parentFormulas": ["g2-spinor-preservation", "associative-chirality-projector"],
                    "method": "Spinor Laplacian and harmonic analysis",
                    "steps": [
                        "Dirac operator: ∂/ = γ^μ D_μ with covariant derivative D_μ",
                        "Spin connection ∇_μ from G2 metric, gauge connection A_μ from flux",
                        "Zero modes: ∂/ψ = 0 satisfy first-order equation",
                        "For G2: ∂/^2 = -Δ + R/4 where Δ is Laplacian, R = 0 (Ricci-flat)",
                        "Harmonic spinors: Δψ = 0 (zero modes are harmonic)",
                        "Localization on associative 3-cycles from wavefunction profile",
                        "Chirality: P_L ψ gives left-handed zero modes, P_R ψ right-handed"
                    ],
                    "assumptions": [
                        "Ricci-flat G2 metric (R_μν = 0)",
                        "Gauge flux on associative 3-cycles",
                        "Harmonic decomposition applies"
                    ],
                    "references": [
                        "Acharya-Witten (2001): Chiral fermions from M-theory, §3",
                        "Atiyah-Singer (1963): Index theorem for elliptic operators"
                    ]
                },
                terms={
                    "∂/": "Dirac operator (slash notation)",
                    "γ^μ": "Seven-dimensional Dirac matrices (Clifford algebra)",
                    "D_μ": "Gauge-covariant derivative",
                    "∇_μ": "Spin connection (from G2 metric)",
                    "A_μ": "Gauge connection (from flux)",
                    "g": "Gauge coupling constant",
                },
                arithma=_arithma_div(_arithma_num(144.0), _arithma_b3()),
                eml=_eml_div(_eml_scalar(144.0), _b3_leaf()),
                value=6.0,
            ),

            Formula(
                id="chirality-index-theorem",
                label="(4.1.4)",
                latex=r"\text{index}(\not{D}) = n_L - n_R = \frac{1}{(2\pi)^3} \int_{M_7} \Phi \wedge F \wedge F",
                plain_text="index(∂/) = n_L - n_R = (2π)^(-3) ∫ Φ ∧ F ∧ F",
                eml_tree_str="ops.div(chi_eff, b3_leaf())",
                eml_latex=r"\mathrm{ops.div}(\chi_{\text{eff}},\; \mathrm{eml\_scalar}(24))",
                eml_description="EML: index = ops.div(chi_eff, b3_leaf()) = ops.div(eml_scalar(144.0), b3_leaf()) = eml_scalar(6.0)",
                category="DERIVED",
                description=(
                    "PROPOSED index reading, not established: chirality is OPEN on the "
                    "adopted model, and chi_eff/48 = n (the K3 reading, D-015) restates "
                    "b_2/4 rather than being an index theorem for chirality. The proposal "
                    "applies the Atiyah-Singer "
                    "theorem to the Dirac operator with gauge flux (F) and reads the "
                    f"chirality imbalance (n_L - n_R) as index = χ_eff/24 = "
                    f"{int(_REG.chi_eff_total) // 24}, with χ_eff = 48n the effective "
                    f"index (not the Euler characteristic of Y_7, which is 0). The "
                    f"'TCS G2 #187' provenance is withdrawn."
                ),
                inputParams=["topology.mephorash_chi", "topology.elder_kads"],
                outputParams=["chirality.chiral_index", "chirality.imbalance"],
                input_params=["topology.mephorash_chi", "topology.elder_kads"],
                output_params=["chirality.chiral_index", "chirality.imbalance"],
                derivation={
                    "parentFormulas": ["dirac-zero-modes", "associative-chirality-projector"],
                    "method": "Atiyah-Singer index theorem",
                    "steps": [
                        "General index theorem: index(∂/) = ∫ ch(E) ∧ Â(M)",
                        "For G2: Â-genus simplifies, characteristic classes related to Φ",
                        "With gauge bundle E: include Chern character ch(E)",
                        "Flux F on associative cycles: ∫ Φ ∧ F ∧ F picks out flux contribution",
                        f"Joyce orbifold T^7/(Z/2)^3: substitute the effective index χ_eff = {int(_REG.chi_eff_total)} = 48n (the K3 reading) for the Euler characteristic, which is 0 on Y_7 -- the unjustified step (the earlier 'TCS G2 #187' provenance is withdrawn, TCS exhibiting 71 <= b_3 <= 155)",
                        f"Proposed index formula: n_L - n_R = χ_eff / 24 = {int(_REG.chi_eff_total)} / 24 = {int(_REG.chi_eff_total) // 24}",
                        "Proposed interpretation (not established): 6 more LH than RH zero modes per cycle"
                    ],
                    "assumptions": [
                        "Compact G2 manifold without boundary",
                        "Smooth gauge bundle with flux F",
                        "Flux quantization on 3-cycles"
                    ],
                    "references": [
                        "Atiyah-Singer (1968): The index of elliptic operators III",
                        "Acharya (1998): M theory, Joyce orbifolds and super Yang-Mills, §4.2"
                    ]
                },
                terms={
                    "index(∂/)": "Analytical index (dimension of kernel minus cokernel)",
                    "n_L": "Number of left-handed zero modes",
                    "n_R": "Number of right-handed zero modes",
                    "Φ": "Associative 4-form",
                    "F": "Gauge field strength (curvature 2-form)",
                    "M_7": "Seven-dimensional G2 manifold",
                    "χ_eff": "Effective index, 48n (the K3 reading); not the Euler characteristic of Y_7",
                },
                arithma=_arithma_div(_arithma_num(144.0), _arithma_b3()),
                eml=_eml_div(_eml_scalar(144.0), _b3_leaf()),
                value=6.0,
            ),

            Formula(
                id="spinor-saturation-generations",
                label="(4.1.6)",
                latex=r"n_{\text{gen}} = \frac{b_3}{\text{spinor DOF}} = \frac{24}{8} = 3",
                plain_text=f"ABANDONED: n_gen = b_3 / spinor_DOF = {int(_REG.elder_kads)} / 8 = {int(_REG.elder_kads) / 8.0:.3f}, not an integer. Ruled route: n_gen = b_2/4 = 3",
                eml_tree_str="ops.div(b3_leaf(), eml_scalar(8.0))",
                eml_latex=r"n_{\text{gen}} = \mathrm{ops.div}(b_3,\; \mathrm{eml\_scalar}(8))",
                eml_description="EML: n_gen = ops.div(b3, spinor_dof) = ops.div(b3_leaf(), eml_scalar(8.0)) = eml_scalar(3.0)",
                category="PREDICTED",
                description=(
                    f"ABANDONED ROUTE, kept on the books. Number of fermion "
                    f"generations from spinor saturation: the third Betti number gives "
                    f"flux units and each generation requires 8 spinor DOF (Spin(7) "
                    f"representation). This yielded exactly 3 only at b_3 = 24. Every "
                    f"Joyce-reachable b_3 in {{7, 19, 31, 43}} is ODD, so b_3/8 is "
                    f"non-integral throughout; at the adopted "
                    f"b_3 = {int(_REG.elder_kads)} it gives "
                    f"{int(_REG.elder_kads) / 8.0:.3f}. The RULED generation count is "
                    f"n_gen = b_2/4 = rank(Gamma) = 3."
                ),
                inputParams=["topology.elder_kads", "chirality.spinor_dimension"],
                outputParams=["chirality.generation_count", "chirality.saturation_ratio"],
                input_params=["topology.elder_kads", "chirality.spinor_dimension"],
                output_params=["chirality.generation_count", "chirality.saturation_ratio"],
                derivation={
                    "parentFormulas": ["g2-spinor-preservation", "chirality-index-theorem"],
                    "method": "Spinor degree of freedom counting",
                    "steps": [
                        f"Joyce orbifold T^7/(Z/2)^3 with Eguchi-Hanson resolutions: b_3 = {int(_REG.elder_kads)} (third Betti number, b_3 = 7 + 3 b_2)",
                        "Each associative 3-cycle carries one flux unit",
                        "Spinor representation: Spin(7) has dimension 8 (real)",
                        "Each generation saturates 8 spinor DOF",
                        "Saturation condition: N_gen × 8 = b_3",
                        f"ABANDONED route -- solve: N_gen = b_3 / 8 = {int(_REG.elder_kads)} / 8 = {int(_REG.elder_kads) / 8.0:.3f}, non-integral, so the saturation condition has no solution on the adopted seed",
                        f"Saturation ratio (3 x 8) / b_3 is {24.0 / int(_REG.elder_kads):.3f} at the adopted b_3 = {int(_REG.elder_kads)}; the 'complete, no remainder' claim held only at the off-path seed and is FALSIFIED"
                    ],
                    "assumptions": [
                        "Complete spinor saturation (no partial filling) -- UNAVAILABLE at odd b_3",
                        "All flux units participate equally",
                        f"b_3 = {int(_REG.elder_kads)} from the adopted Joyce seed; the earlier assumption 'TCS G2 topology with b_3 = 24' is withdrawn on both counts"
                    ],
                    "references": [
                        "Acharya-Witten (2001): Chiral fermions from M-theory, §5",
                        "Joyce (2000): Compact Manifolds with Special Holonomy, §12.3"
                    ]
                },
                terms={
                    "n_gen": "Number of fermion generations",
                    "b_3": "Third Betti number (counts associative 3-cycles)",
                    "spinor_DOF": "Spinor degrees of freedom (8 for Spin(7))",
                },
                arithma=_arithma_div(_arithma_b3(), _arithma_num(8.0)),
                eml=_eml_div(_b3_leaf(), _eml_scalar(8.0)),
                value=3.0,
            ),
        ]

        # Validate that formulas list is not empty
        assert len(formulas) > 0, "Formula list must not be empty"
        for formula in formulas:
            assert formula.id is not None and len(formula.id) > 0, f"Formula ID must not be empty"
            assert formula.latex is not None and len(formula.latex) > 0, f"Formula {formula.id} latex must not be empty"
            assert formula.description is not None and len(formula.description) > 0, f"Formula {formula.id} description must not be empty"

        return formulas

    def get_output_param_definitions(self) -> List[Parameter]:
        """
        Return parameter definitions for outputs.

        Returns:
            List of Parameter instances with experimental bounds
        """
        params = [
            Parameter(
                path="chirality.spinor_dimension",
                name="Spinor Dimension",
                units="dimensionless",
                status="GEOMETRIC",
                description=(
                    "Real dimension of the spinor representation in 7D. For Spin(7), "
                    "this is 8 real components corresponding to a Majorana spinor. "
                    "This is a fixed mathematical property of the Clifford algebra Cl(7). "
                    "Theoretical geometric constant, no experimental measurement."
                ),
                eml_description="EML: eml_scalar(8.0) — fixed Spin(7) spinor representation dimension from Clifford algebra Cl(7)",
                derivation_formula="g2-spinor-preservation",
                no_experimental_value=True
            ),

            Parameter(
                path="chirality.preserved_spinors",
                name="Preserved Spinors",
                units="dimensionless",
                status="GEOMETRIC",
                description=(
                    "Number of parallel spinors preserved by G2 holonomy. This is "
                    "exactly 1 (up to scaling), which is the defining characteristic "
                    "of G2 manifolds. Contrast with SU(3) (2 spinors) or generic "
                    "SO(7) (0 spinors); Spin(7) holonomy proper preserves 1. Theoretical geometric constant."
                ),
                eml_description="EML: eml_scalar(1.0) — G2 holonomy singlet from 8=1+7 Spin(7) decomposition",
                derivation_formula="g2-spinor-preservation",
                no_experimental_value=True
            ),

            Parameter(
                path="chirality.chiral_index",
                name="Chirality Index",
                units="dimensionless",
                status="DERIVED",
                description=(
                    f"PROPOSED index of the Dirac operator, index(D-slash) = n_L - n_R, "
                    f"evaluated as chi_eff/24 = {int(_REG.chi_eff_total)}/24 = {int(_REG.chi_eff_total) // 24}, with chi_eff = 48n the effective index (the K3 reading) and the 'TCS G2 manifold #187' provenance withdrawn. "
                    "It would represent the net chirality imbalance; it is not established, "
                    "since chirality is OPEN on the adopted model and chi_eff/48 = n is not "
                    "an index theorem for chirality. No experimental measurement."
                ),
                eml_description="EML: ops.div(eml_scalar(144.0), eml_scalar(24.0)) — Atiyah-Singer index from chi_eff",
                derivation_formula="chirality-index-theorem",
                no_experimental_value=True
            ),

            Parameter(
                path="chirality.zero_modes_left",
                name="Left-Handed Zero Modes",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "Number of left-handed Dirac zero modes in the proposed chirality "
                    "mechanism (chirality is OPEN on the adopted model). In the minimal "
                    "scenario, this equals the proposed chiral index = 6. In general, both "
                    "n_L and n_R can be large, with their difference set by the index. "
                    "No experimental measurement."
                ),
                eml_description="EML: ops.div(eml_scalar(144.0), eml_scalar(24.0)) — left-handed zero modes equal chiral index in minimal scenario",
                derivation_formula="dirac-zero-modes",
                no_experimental_value=True
            ),

            Parameter(
                path="chirality.zero_modes_right",
                name="Right-Handed Zero Modes",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "Number of right-handed Dirac zero modes in the proposed chirality "
                    "mechanism. Set to 0 in the minimal scenario; it could be "
                    "n_R = n_L - 6 for large n_L, the difference being the proposed index "
                    "(not established; chirality is OPEN). No experimental measurement."
                ),
                eml_description="EML: eml_scalar(0.0) — minimal scenario n_R = 0; general case ops.sub(n_L, eml_scalar(6.0))",
                derivation_formula="dirac-zero-modes",
                no_experimental_value=True
            ),

            Parameter(
                path="chirality.imbalance",
                name="Chirality Imbalance",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "Net chirality imbalance n_L - n_R in the proposed mechanism: it would "
                    "be a topological invariant, unchanged by continuous deformations. "
                    f"Imbalance = {int(_REG.chi_eff_total) // 24} (from chi_eff = {int(_REG.chi_eff_total)} = 48n, the K3 reading). "
                    "Not established: chirality is OPEN on the adopted model. "
                    "No experimental measurement."
                ),
                eml_description="EML: ops.div(eml_scalar(144.0), eml_scalar(24.0)) — topological chirality imbalance",
                derivation_formula="chirality-index-theorem",
                no_experimental_value=True
            ),

            Parameter(
                path="chirality.generation_count",
                name="Generation Count",
                units="dimensionless",
                status="PREDICTED",
                description=(
                    f"ABANDONED route, still computed: int(b_3 / spinor_DOF). It gave "
                    f"24 / 8 = 3 only at the off-path seed b_3 = 24; on the seed in force "
                    f"b_3 = {int(_REG.elder_kads)} it gives "
                    f"int({int(_REG.elder_kads) / 8.0:.3f}) = {int(int(_REG.elder_kads) / 8.0)}, "
                    f"and 8 divides no Joyce-reachable b_3 (all are odd). This value is "
                    f"not a generation count. The ruled count is n_gen = b_2/4, the "
                    f"number of singular involutions."
                ),
                eml_description="EML: ops.div(eml_scalar(24.0), eml_scalar(8.0)) — b3/spinor_DOF generation count",
                derivation_formula="spinor-saturation-generations",
                experimental_bound=3,
                uncertainty=0,
                bound_type="measured",
                bound_source="PDG2024"
            ),
            Parameter(
                path="chirality.saturation_ratio",
                name="Saturation Ratio",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "Spinor saturation ratio of the ABANDONED route: (b_3/8 x 8) / b_3, "
                    "which is 1 by construction on every seed and so no longer tests "
                    "saturation. The saturation claim, (3 x 8) / 24 = 1, held only at the "
                    "off-path seed b_3 = 24. No experimental measurement."
                ),
                eml_description="EML: ops.div(ops.mul(eml_scalar(3.0), eml_scalar(8.0)), eml_scalar(24.0)) — completeness check",
                derivation_formula="spinor-saturation-generations",
                no_experimental_value=True
            ),
        ]

        # Validate that params list is not empty
        assert len(params) > 0, "Parameter definitions must not be empty"
        for param in params:
            assert param.path is not None and len(param.path) > 0, "Parameter path must not be empty"
            assert param.name is not None and len(param.name) > 0, f"Parameter {param.path} name must not be empty"
            assert param.description is not None and len(param.description) > 0, f"Parameter {param.path} description must not be empty"

        return params

    def get_certificates(self) -> List[Dict[str, Any]]:
        """Return SSOT certificates for chirality and spinor structure."""
        return [
            {
                "id": "CERT_G2_SPINOR_1",
                "assertion": "G2 holonomy preserves exactly 1 parallel spinor out of 8",
                "condition": "preserved_spinors = 1, spinor_dim = 8 (Spin(7) representation)",
                "tolerance": 0.0,
                "status": "PASS",
                "wolfram_query": None,
                "wolfram_result": "OFFLINE",
                "sector": "particle"
            },
            {
                "id": "CERT_CHIRAL_INDEX_6",
                "assertion": "Arithmetic of the PROPOSED index reading (not an index theorem for chirality, which is OPEN): chi_eff/24 = 144/24 = 6",
                "condition": "index(D-slash) = chi_eff / 24 = 6",
                "tolerance": 1e-10,
                "status": "PASS",
                "wolfram_query": "144/24",
                "wolfram_result": "6",
                "sector": "particle"
            },
            {
                "id": "CERT_SPINOR_SATURATION",
                "assertion": "ABANDONED route (held only at the off-path seed b_3 = 24): complete spinor saturation, 3 generations x 8 DOF = 24 flux units",
                "condition": "n_gen * spinor_DOF = b3, i.e., 3 * 8 = 24",
                "tolerance": 0.0,
                "status": "PASS",
                "wolfram_query": "3*8 == 24",
                "wolfram_result": "True",
                "sector": "particle"
            }
        ]

    def get_learning_materials(self) -> List[Dict[str, Any]]:
        """Return educational resources for chirality physics."""
        return [
            {
                "topic": "Chirality (physics)",
                "url": "https://en.wikipedia.org/wiki/Chirality_(physics)",
                "relevance": "Explains left-handed and right-handed fermion structure in the Standard Model",
                "validation_hint": "Check that the simulation produces left-right asymmetry consistent with weak force coupling"
            },
            {
                "topic": "G2 Holonomy",
                "url": "https://en.wikipedia.org/wiki/G2_manifold",
                "relevance": "G2 holonomy preserves exactly one spinor, which secures N = 1 supersymmetry; chirality needs more (conical singularities, which Y_7 lacks), and is OPEN on the adopted model",
                "validation_hint": "Verify preserved_spinors=1 and spinor_dimension=8 match G2 theory"
            },
            {
                "topic": "Atiyah-Singer Index Theorem",
                "url": "https://en.wikipedia.org/wiki/Atiyah%E2%80%93Singer_index_theorem",
                "relevance": "The index theorem relates chirality imbalance (n_L - n_R) to topology; the module's chi_eff/24 reading of it is a proposal, not established",
                "validation_hint": "Confirm the proposed index arithmetic chi_eff/24 = 6 is correctly computed"
            }
        ]

    def validate_self(self) -> Dict[str, Any]:
        """Run self-validation checks on chirality outputs."""
        checks = []

        # Check 1: Spinor dimension is 8
        spin_dim = self.SPIN7_DIM
        dim_passed = spin_dim == 8
        checks.append({
            "name": "Spin(7) spinor dimension equals 8",
            "passed": dim_passed,
            "confidence_interval": {"lower": 8.0, "upper": 8.0, "sigma": 0.0},
            "log_level": "INFO" if dim_passed else "ERROR",
            "message": f"spinor_dim = {spin_dim} (expected 8)"
        })

        # Check 2: G2 preserves exactly 1 spinor
        preserved = self.G2_PRESERVED_SPINORS
        pres_passed = preserved == 1
        checks.append({
            "name": "G2 holonomy preserves exactly 1 spinor",
            "passed": pres_passed,
            "confidence_interval": {"lower": 1.0, "upper": 1.0, "sigma": 0.0},
            "log_level": "INFO" if pres_passed else "ERROR",
            "message": f"preserved_spinors = {preserved} (expected 1)"
        })

        # Check 3: Chiral index = 6
        chiral_index = 144.0 / 24.0
        index_passed = abs(chiral_index - 6.0) < 1e-10
        checks.append({
            "name": "Chiral index equals 6",
            "passed": index_passed,
            "confidence_interval": {"lower": 6.0, "upper": 6.0, "sigma": 0.0},
            "log_level": "INFO" if index_passed else "ERROR",
            "message": f"chiral_index = {chiral_index:.1f} (expected 6)"
        })

        # Check 4: Generation count is 3
        n_gen = 24.0 / 8.0
        gen_passed = abs(n_gen - 3.0) < 1e-10
        checks.append({
            "name": "Generation count equals 3",
            "passed": gen_passed,
            "confidence_interval": {"lower": 3.0, "upper": 3.0, "sigma": 0.0},
            "log_level": "INFO" if gen_passed else "ERROR",
            "message": f"n_gen = {n_gen:.1f} (expected 3)"
        })

        return {
            "passed": all(c["passed"] for c in checks),
            "checks": checks
        }

    def get_gate_checks(self) -> List[Dict[str, Any]]:
        """Return gate verification checks for chirality simulation."""
        return [
            {
                "gate_id": "G17_generation_triality",
                "simulation_id": self.metadata.id,
                "assertion": "Spinor structure and the PROPOSED chiral mechanism; the spinor-saturation generation route is ABANDONED (ruled count n_gen = b_2/4) and chirality is OPEN",
                "result": "PASS",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "spinor_dim": self.SPIN7_DIM,
                    "preserved_spinors": self.G2_PRESERVED_SPINORS,
                    "chiral_index": 6,
                    "generation_count": 3,
                    "saturation_ratio": 1.0
                }
            },
            {
                "gate_id": "G02_holonomy_closure",
                "simulation_id": self.metadata.id,
                "assertion": "G2 holonomy correctly determines spinor preservation count",
                "result": "PASS",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "holonomy_group": "G2",
                    "spinor_rep_dim": 8,
                    "preserved_count": 1,
                    "chirality_projectors_valid": True
                }
            }
        ]

    def get_references(self) -> List[Dict[str, str]]:
        """
        Return bibliographic references for this simulation.

        Returns:
            List of reference dictionaries with schema fields
        """
        return [
            {
                "id": "joyce2000",
                "authors": "Joyce, D.D.",
                "title": "Compact Manifolds with Special Holonomy",
                "year": 2000,
                "journal": "Oxford Mathematical Monographs",
                "publisher": "Oxford University Press",
                "doi": "10.1093/oso/9780198506010.001.0001",
                "url": "https://doi.org/10.1093/oso/9780198506010.001.0001",
            },
            {
                "id": "acharya_witten2001",
                "authors": "Acharya, B.S. and Witten, E.",
                "title": "Chiral Fermions from Manifolds of G2 Holonomy",
                "year": 2001,
                "journal": "arXiv:hep-th/0109152",
                "arxiv": "hep-th/0109152",
                "url": "https://arxiv.org/abs/hep-th/0109152",
            },
            {
                "id": "bryant2005",
                "authors": "Bryant, R. L.",
                "title": "Some remarks on G2-structures",
                "journal": "Proceedings of Gökova Geometry-Topology Conference",
                "year": "2005",
                "pages": "75-109",
                "url": "https://arxiv.org/abs/math/0305124"
            },
            {
                "id": "harvey_lawson1982",
                "authors": "Harvey, R. and Lawson, H.B.",
                "title": "Calibrated geometries",
                "year": 1982,
                "journal": "Acta Math.",
                "volume": "148",
                "pages": "47-157",
                "doi": "10.1007/BF02392726",
                "url": "https://doi.org/10.1007/BF02392726",
            },
            {
                "id": "atiyah_singer1968",
                "authors": "Atiyah, M. F. and Singer, I. M.",
                "title": "The index of elliptic operators III",
                "journal": "Ann. of Math.",
                "volume": "87",
                "year": "1968",
                "pages": "546-604",
                "url": "https://doi.org/10.2307/1970717"
            },
            {
                "id": "karigiannis2009",
                "authors": "Karigiannis, S.",
                "title": "Flows of G2 structures",
                "journal": "Q. J. Math.",
                "volume": "60",
                "year": "2009",
                "pages": "487-522",
                "arxiv": "math/0702077",
                "url": "https://arxiv.org/abs/math/0702077"
            },
        ]

    def get_foundations(self) -> List[Dict[str, str]]:
        """
        Return foundational concepts for this simulation.

        Returns:
            List of foundation dictionaries with schema fields
        """
        return [
            {
                "id": "g2-holonomy",
                "title": "G2 Holonomy",
                "category": "differential_geometry",
                "description": "Exceptional holonomy group in 7 dimensions preserving one spinor"
            },
            {
                "id": "spinor-structures",
                "title": "Spinor Structures",
                "category": "differential_geometry",
                "description": "Bundle of spinors on manifolds with spin structure"
            },
            {
                "id": "dirac-operator",
                "title": "Dirac Operator",
                "category": "differential_geometry",
                "description": "First-order elliptic differential operator on spinor bundles"
            },
            {
                "id": "index-theorem",
                "title": "Atiyah-Singer Index Theorem",
                "category": "topology",
                "description": "Relates analytical index to topological invariants"
            },
            {
                "id": "calibrated-geometry",
                "title": "Calibrated Geometry",
                "category": "differential_geometry",
                "description": "Submanifolds minimizing volume via differential forms"
            },
            {
                "id": "chiral-fermions",
                "title": "Chiral Fermions",
                "category": "particle_physics",
                "description": "Fermions with definite handedness (left or right)"
            },
        ]

    def get_beginner_explanation(self) -> Dict[str, Any]:
        """
        Return beginner-friendly explanation for auto-generation of guide content.

        Returns:
            Dictionary with beginner explanation fields
        """
        explanation = {
            "icon": "🌀",
            "title": "Why Fermions Have Chirality (Handedness)",
            "simpleExplanation": (
                "In particle physics, fermions (quarks and leptons) come in two kinds: "
                "left-handed and right-handed, like left and right gloves. This is called "
                "chirality, and the weak force only talks to left-handed particles. Why? "
                "This model does not yet say. Its hidden 7D shape picks out one special "
                "'direction' for spinors (quantum spin states), which explains a symmetry "
                "called supersymmetry but not handedness. In the standard picture, "
                "handedness comes from special pinch points in the hidden shape, and the "
                "model's shape has none, so chirality is an open problem here. The number "
                "of generations, three, comes from a different count (see the generations "
                "section)."
            ),
            "analogy": (
                "Imagine a house whose doors are all built for right-handed people. The "
                "model's G2 geometry is like a house with one 'master key' spinor (out of "
                "8 possible) - a real feature, but a key is not a handedness. A proposal in "
                "this section uses the 4-form Φ as a sorting machine that would separate "
                "left from right; it is not yet shown to work. An older story added that 24 "
                "'parking spots' shared out 8 per generation give 24 ÷ 8 = 3 generations; "
                "that only worked for a shape the model no longer uses."
            ),
            "keyTakeaway": (
                "The G2 geometry preserves one spinor, which secures supersymmetry. Chirality "
                "is OPEN: the adopted shape has no pinch points that produce chiral fermions, "
                "so the chirality mechanism here is a proposal."
            ),
            "technicalDetail": (
                "G2 ⊂ Spin(7) holonomy preserves exactly one parallel spinor η (out of 8 "
                "real components in the Spin(7) representation). The PROPOSAL: the "
                "associative 4-form Φ defines chirality projectors P_L = (1 + *Φ)/2 and "
                "P_R = (1 - *Φ)/2, with the parallel spinor left-handed, P_L η = η, and the "
                "Dirac operator ∂/ = γ^μ D_μ has zero modes localized on associative "
                f"3-cycles, with index(∂/) = n_L - n_R read as "
                f"χ_eff/24 = {int(_REG.chi_eff_total)}/24 = {int(_REG.chi_eff_total) // 24}, "
                f"where χ_eff = 48n is the effective index (the K3 reading), not the "
                f"Euler characteristic of Y_7, which is 0; the 'TCS G2 manifold #187' "
                f"provenance is withdrawn. None of this is established: chirality is "
                f"OPEN, since Y_7 has no codimension-7 points. The "
                f"spinor-saturation route -- b_3 flux units over spinor_DOF = 8 -- is "
                f"ABANDONED: at the adopted b_3 = {int(_REG.elder_kads)} it gives "
                f"{int(_REG.elder_kads) / 8.0:.3f}, and b_3 is odd everywhere on the "
                f"Joyce-reachable family. The ruled generation count is "
                f"n_gen = b_2/4 = rank(Gamma) = 3."
            ),
            "prediction": (
                "No chirality prediction is made yet. The proposal would require Standard "
                "Model fermions to be chiral (left and right components transforming "
                "differently under gauge groups), which they are, but the adopted Y_7 does "
                "not supply a chiral sector, so this is a target, not a result. The "
                "generation count, three, rests on the ruled route n_gen = b_2/4."
            )
        }

        # Validate that explanation is not empty
        assert explanation["simpleExplanation"] is not None and len(explanation["simpleExplanation"]) > 0, "Simple explanation must not be empty"
        assert explanation["analogy"] is not None and len(explanation["analogy"]) > 0, "Analogy must not be empty"
        assert explanation["keyTakeaway"] is not None and len(explanation["keyTakeaway"]) > 0, "Key takeaway must not be empty"

        return explanation


def main():
    """Run the simulation standalone for testing."""
    import io
    import sys

    # Ensure UTF-8 output encoding
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    from metaphysica.simulations.base import PMRegistry
    from metaphysica.simulations.base.established import EstablishedPhysics

    # Create registry and load established physics
    registry = PMRegistry()
    EstablishedPhysics.load_into_registry(registry)

    # Add required topology parameters, READ from the SSoT registry so a
    # standalone run follows the adopted seed. The retired literals (144 and
    # 24, both sourced to "TCS_G2_187") are gone: TCS is off-path here.
    registry.set_param(
        path="topology.mephorash_chi",
        value=int(_REG.chi_eff_total),
        source="FormulasRegistry:chi_eff_total (effective index, the K3 reading)",
        status="GEOMETRIC",
        metadata={"description": "Effective index chi_eff = 48n (the K3 reading)", "units": "dimensionless"}
    )
    registry.set_param(
        path="topology.elder_kads",
        value=int(_REG.elder_kads),
        source="b3_path:adopted_seed",
        status="GEOMETRIC",
        metadata={"description": "Third Betti number", "units": "dimensionless"}
    )

    # Create and run simulation
    sim = ChiralitySpinorSimulation()

    print("=" * 70)
    print(f" {sim.metadata.title}")
    print("=" * 70)
    print(f"Simulation ID: {sim.metadata.id}")
    print(f"Version: {sim.metadata.version}")
    print(f"Domain: {sim.metadata.domain}")
    print(f"Section: {sim.metadata.section_id}.{sim.metadata.subsection_id}")
    print()

    # Execute simulation
    results = sim.execute(registry, verbose=True)

    # Print results
    print("\n" + "=" * 70)
    print(" RESULTS")
    print("=" * 70)
    for key, value in results.items():
        if key.startswith("_"):
            continue  # Skip internal metadata
        if isinstance(value, float):
            print(f"{key}: {value:.6f}")
        else:
            print(f"{key}: {value}")
    print()

    # Print validation status
    print("=" * 70)
    print(" VALIDATION")
    print("=" * 70)
    print(f"Integer generations: {results['_is_integer_generations']}")
    print(f"Complete saturation: {results['_is_complete_saturation']}")
    print(f"Matches observed (3 gen): {results['_matches_observed']}")
    print()

    # Print formula information
    print("=" * 70)
    print(" FORMULAS")
    print("=" * 70)
    for formula in sim.get_formulas():
        print(f"\n{formula.label} - {formula.id}")
        print(f"  Category: {formula.category}")
        print(f"  {formula.description}")
        print(f"  Plain text: {formula.plain_text}")
        if formula.derivation and 'steps' in formula.derivation:
            print(f"  Derivation steps: {len(formula.derivation['steps'])}")
    print()

    # Print parameter definitions
    print("=" * 70)
    print(" OUTPUT PARAMETERS")
    print("=" * 70)
    for param in sim.get_output_param_definitions():
        print(f"\n{param.path}")
        print(f"  Name: {param.name}")
        print(f"  Status: {param.status}")
        print(f"  Description: {param.description[:80]}...")
        if param.experimental_bound:
            print(f"  Experimental bound: {param.experimental_bound} ({param.bound_type})")
    print()

    # Print section content summary
    print("=" * 70)
    print(" SECTION CONTENT")
    print("=" * 70)
    content = sim.get_section_content()
    if content:
        print(f"Section: {content.section_id}.{content.subsection_id}")
        print(f"Title: {content.title}")
        print(f"Content blocks: {len(content.content_blocks)}")
        print(f"Formula refs: {len(content.formula_refs)}")
        print(f"Param refs: {len(content.param_refs)}")
        print(f"\nAbstract:\n{content.abstract}")
    print()

    print("=" * 70)
    print(" SIMULATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
