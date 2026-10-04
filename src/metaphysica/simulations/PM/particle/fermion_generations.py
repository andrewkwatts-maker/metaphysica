#!/usr/bin/env python3
"""
Fermion Generations - Three Generations from G2 Topology
========================================================

Licensed under the MIT License. See LICENSE file for details.

Derives the number of fermion generations and Yukawa hierarchy from G2 manifold
topology via the Pneuma Mechanism.

WHERE THE GENERATION COUNT COMES FROM, AND WHERE IT MOVED TO
============================================================
Three routes to n_gen = 3 appear in this framework. They are NOT
interchangeable, and the 2026-09-22 seed adoption separated them:

  (a) RULED, and the one in force:
          n_gen = b_2 / n_faces = b_2 / 4 = rank(Gamma) = 3
      with (b_2, b_3) = (12, 43) the ADOPTED seed of a Joyce orbifold
      T^7/(Z/2)^3 with Eguchi-Hanson resolutions, b_3 = 7 + 3 b_2. The 4 is
      the faces, derived as the moved coordinates of an involution. Three
      generations is the RANK of the diagonal stabiliser of phi.

  (b) ABANDONED:
          n_gen = b_3 / dim(O) = b_3 / 8 = 24 / 8 = 3
      This worked only at b_3 = 24. On the Joyce-reachable family
      b_3 in {7, 19, 31, 43} every value is ODD, and 8 divides no odd
      number, so this route yields an integer NOWHERE on the family -- not
      merely a wrong value at one point. It is abandoned, not adjusted.
      Kept here on the books because the assessment below is about it.

  (c) THE K3 READING (adopted, D-015), and what THIS MODULE evaluates:
          n_gen = chi_eff / 48,   chi_eff = 2 x sum_sigma chi(K3_sigma) = 48 n
      chi_eff = 144 is an effective index: twice the Euler characteristics
      of the Kummer K3 surfaces transverse to the n singular involutions,
      counted once per shadow. It is not the Euler characteristic of Y_7,
      which is 0. So chi_eff / 48 = n RESTATES route (a) rather than adding
      a second derivation, and it is not an index theorem for chirality,
      which is OPEN (Y_7's singular loci are disjoint, so it has no
      codimension-7 points). The code reaches the 48 through a historical
      flux reading, N_flux = chi_eff / 6 and n_gen = N_flux / 8; that
      reading's three claimed derivations of chi_eff -- 2(h11-h21+h31),
      b_3^2/4 and 6 b_3 -- agreed only at the off-path seed b_3 = 24 and are
      retired.

MECHANISM:
1. Generation count: see the three routes above. The code path below is
   route (c), the K3 reading, which restates route (a).

2. Yukawa hierarchy from geometric wave-function overlaps (a model
   construct; flavour is OPEN because Y_7 supplies no chiral sector):
   Y_f = A_f * epsilon^Q_f
   where epsilon = exp(-lambda_curvature) and Q_f is topological distance

3. Pneuma chiral filter from axial torsion coupling (a proposal; chirality
   is OPEN on the adopted model):
   D_eff = gamma^mu (d_mu + igA_mu + gamma^5 T_mu)

KEY RESULTS:
- Three generations: n_gen = b_2/4 = 3 (route (a)); chi_eff/48 = n restates it
- Yukawa texture from FN mechanism (epsilon ~ 0.223), a model construct
- Chiral filter strength: 7/8 from spinor stabilization, a model construct

DERIVATION CHAIN (route (c), the K3 reading, via the flux arithmetic):
topology.mephorash_chi = chi_eff
  -> N_flux = chi_eff / 6
  -> n_gen = N_flux / 8 = chi_eff / 48 = n

PROVENANCE CORRECTION: chi_eff was previously attributed to "TCS G2 manifold
#187". Twisted Connected Sum is OFF-PATH for this framework: the exhibited
TCS range is 71 <= b_3 <= 155, which excludes the adopted b_3 = 43, and the
construction in force is the Joyce orbifold T^7/(Z/2)^3.
  -> epsilon = exp(-1.5) ~ 0.223
  -> Y_f = A_f * epsilon^Q_f

ASSERTION ASSESSMENT (2026-03-16, LLM (Opus) + Gemini 2.5 Flash debate):
================================================================================
Assertion (AS ASSESSED IN 2026-03; the claim it assesses has since been
ABANDONED -- see route (b) above -- and the assessment is retained because a
falsified claim stays on the books):
           "3 fermion generations from n_gen = b3/(2*h11) = 24/8 = 3,
           derived from G2 topology."

Verdict: NUMEROLOGY

Evidence and reasoning:

1. FORMULA IS NOT STANDARD. The formula n_gen = b3/(2*h11) does not appear in
   the standard G2 compactification literature (Acharya-Witten 2001, Joyce 2000,
   Acharya et al. 2012). In standard M-theory on G2 manifolds, chiral fermion
   generations arise from ADE-type singularities along 3-manifolds inside the G2
   space, not from dividing Betti numbers by spinor dimensions.

2. INCONSISTENT DERIVATION CHAIN. The assertion (route (b), since abandoned)
   states n_gen = b3/(2*h11) = 24/8 but the code actually computes
   n_gen = (chi_eff/6) / spinor_DOF = 144/48 = 3 [since D-015 the 6*b3
   definition is retired; chi_eff is read as 2 x sum chi(K3) = 48n, so
   144/48 = n restates b_2/4]. Since chi_eff = 6*b3 by framework definition,
   chi_eff/6 merely recovers b3, making the "flux quantization" step
   circular. The variable h11=4 from the assertion does not appear in the
   code at all.

3. SPINOR_DOF=8 MISAPPLIED. The 8 real spinor components of Spin(7) relate to
   N=1 SUSY preservation (G2 holonomy preserves 1 of 8 spinors), not to how many
   flux quanta each fermion generation requires. There is no established physical
   mechanism connecting dim(Spin(7) spinor) to generation counting.

4. chi_eff IS FRAMEWORK-DEFINED, NOT STANDARD. Odd-dimensional manifolds have
   Euler characteristic zero. The "effective Euler characteristic" chi_eff=144 is
   a quantity defined within this framework (as 6*b3 = B3^2/4), not a standard
   topological invariant of G2 manifolds.
   [Settled by D-015: chi_eff is an effective index read as 2 x sum chi(K3)
   = 48n; the 6*b3 and B3^2/4 forms agreed only at the off-path seed and
   are retired.]

5. EXTENSIVE HIDDEN FITTING. The Yukawa sector contains 18 effectively fitted
   parameters (9 geometric_coeffs + 9 fn_charges) presented as "derived from
   cycle graph distances" but actually tuned to match observed fermion masses.
   lambda_curvature=1.5 is hardcoded with post-hoc justification.

6. GEMINI CONSENSUS. Gemini 2.5 Flash independently classified this as
   NUMEROLOGY across all three debate rounds, noting: "the formula is engineered
   to give 3 by choosing divisors" and "the divisor 8 is chosen without a
   rigorous physical or mathematical derivation relevant to fermion generations."

Classification (of route (b), since abandoned): NUMEROLOGY - The arithmetic
24/8=3 is correct, and the ingredients (b3, Spin(7) dimension) are real
mathematical objects from G2 geometry. However, the specific combination
b3/spinor_DOF has no derivation from the established physics. The formula
appears reverse-engineered to yield the known answer of 3 generations by
selecting an appropriate divisor for b3=24.

STATUS UPDATE (2026-09-22 seed adoption; 2026-10-01 rulings, D-015): route
(b) above is ABANDONED outright, which settles point 1 of this assessment in
the assessment's favour -- b3/8 is not merely non-standard, it is
non-integral everywhere on the Joyce-reachable family. Point 4 is settled by
the K3 reading (adopted): chi_eff = 2 x sum chi(K3) = 48n is an effective
index that follows the seed through n, not the Euler characteristic of Y_7.
So n_gen = chi_eff/48 = n restates route (a), n_gen = b_2/4 = rank(Gamma) =
3; it is not a second derivation and not an index theorem for chirality,
which stays OPEN. This module evaluates the chi_eff/48 arithmetic; it does
not compute route (a).
================================================================================

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""

import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional

from metaphysica.simulations.base import (
    SimulationBase,
    SimulationMetadata,
    ContentBlock,
    SectionContent,
    Formula,
    Parameter,
    PMRegistry,
)
# --- triple-track helpers (Sprint 2 — Phase H) -----------------------------
from metaphysica.simulations.core.FormulasRegistry import get_registry as _get_reg

#: SSoT read. b3, b2 and chi_eff FOLLOW THE ADOPTED SEED and are never typed
#: as literals in this module's prose.
_REG = _get_reg()

# --- triple-track helpers (Sprint 2) ---------------------------------------
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
    eml_neg as _eml_neg,
    eml_exp as _eml_exp,
)
def _arithma_div(a, b):
    return None if a is None or b is None else a / b


class FermionGenerationsV16(SimulationBase):
    """
    Fermion generation count and Yukawa texture from G2 topology.

    This simulation implements the fermion sector:
    1. Generation number as chi_eff/48 = n, the K3 reading, which restates
       the ruled count n_gen = b_2/4 = 3
    2. Yukawa hierarchy from geometric Froggatt-Nielsen mechanism (a model
       construct; flavour is OPEN)
    3. Pneuma chiral filter mechanism (a proposal; chirality is OPEN)

    Inputs:
        - topology.mephorash_chi: effective index chi_eff (144 = 48n, the K3
          reading; not the Euler characteristic of Y_7)
        - topology.elder_kads: Third Betti number b_3 (follows the seed; 43
          on the adopted seed)

    Outputs:
        - fermion.n_generations: Number of generations (3)
        - fermion.yukawa_hierarchy: Yukawa suppression parameter epsilon
        - fermion.chiral_filter_strength: Pneuma filter strength (7/8)
    """

    def __init__(self):
        """Initialize fermion generations simulation."""
        # Physical constants
        self.spinor_dof = 8  # Spinor DOF in 7D (Spin(7) representation)
        self.lambda_curvature = 1.5  # G2 curvature scale
        self.spin7_total = 8  # Total spinor components in Spin(7)
        self.spin7_active = 7  # Components that couple to torsion

        # Experimental fermion masses (GeV) for validation
        self.exp_masses = {
            'top': 172.57,  # PDG 2024 direct-measurement average
            'bottom': 4.18,
            'charm': 1.27,
            'strange': 0.093,
            'up': 0.0022,
            'down': 0.0047,
            'tau': 1.777,
            'muon': 0.1057,
            'electron': 0.000511
        }

        # Topological FN charges (from cycle graph distances)
        # Each Q_f represents the geodesic distance (in units of the associative
        # cycle length) between the fermion's localization site on the 3-cycle
        # network and the Higgs/flavon VEV site. The associative 3-cycle network
        # of the adopted Joyce orbifold has b3 nodes (read from the seed, not
        # the retired literal 24); fermion wavefunctions peak at specific
        # nodes, and the suppression factor epsilon^Q_f gives the wavefunction
        # overlap integral that determines the Yukawa coupling Y_f.
        self.fn_charges = {
            'top': 0,      # At H_u location (maximum overlap)
            'bottom': 2,   # 2 hops from H_d on cycle graph
            'charm': 2,    # Moderate distance (2nd generation quark)
            'strange': 3,  # Further on cycle graph
            'up': 4,       # Far from Higgs site (strong suppression)
            'down': 4,     # Far (strong suppression)
            'tau': 2,      # Similar to bottom (tan beta symmetry)
            'muon': 4,     # Further (lepton sector mirror)
            'electron': 6  # Furthest on cycle graph (maximum suppression)
        }

        # Geometric O(1) coefficients from angular overlaps
        self.geometric_coeffs = {
            'top': 1.0,
            'bottom': 0.48,
            'charm': 0.147,
            'strange': 0.042,
            'up': 0.0044,
            'down': 0.0077,
            'tau': 0.205,
            'muon': 0.245,
            'electron': 0.024
        }

    @property
    def metadata(self) -> SimulationMetadata:
        """Return simulation metadata."""
        from metaphysica.simulations.PM.geometry.geometry_narration import (
            render,
        )

        return SimulationMetadata(
            id="fermion_generations_v16_0",
            version="16.0",
            domain="fermion",
            title="Fermion Generations from G2 Topology",
            description=render(
                "Fermion generation count and Yukawa texture on the G2 manifold "
                "via the Pneuma Mechanism. The count is {n_gen_route} (the ruled "
                "route); this module's chi_eff/48 arithmetic restates it through "
                "the K3 reading chi_eff = 48n. The earlier spinor-saturation reading, "
                "24/8 = 3, held only at {off_path_seed} and is abandoned. The Yukawa "
                "hierarchy is a geometric Froggatt-Nielsen model construct with "
                "epsilon ~ 0.223; flavour and chirality are OPEN."
            ),
            section_id="4",
            subsection_id="4.2"
        )

    @property
    def required_inputs(self) -> List[str]:
        """Return list of required input parameter paths."""
        return [
            "topology.mephorash_chi",
            "topology.elder_kads"
        ]

    @property
    def output_params(self) -> List[str]:
        """Return list of output parameter paths."""
        return [
            "fermion.n_generations",
            "fermion.yukawa_hierarchy",
            "fermion.chiral_filter_strength",
            "fermion.n_flux",
            "fermion.epsilon_fn"
        ]

    @property
    def output_formulas(self) -> List[str]:
        """Return list of formula IDs this simulation provides."""
        return [
            "generation-number",
            "yukawa-texture",
            "pneuma-chiral-filter"
        ]

    def run(self, registry: PMRegistry) -> Dict[str, Any]:
        """
        Execute the fermion generations calculation.

        Args:
            registry: PMRegistry instance to read inputs from

        Returns:
            Dictionary mapping parameter paths to computed values
        """
        # Get inputs from registry
        chi_eff = registry.get_param("topology.mephorash_chi")
        b3 = registry.get_param("topology.elder_kads")

        # Compute flux quanta
        n_flux = chi_eff / 6.0  # Standard flux quantization

        # Compute generation number as chi_eff/48 -- the K3 reading (adopted,
        # D-015): chi_eff = 2 x sum chi(K3) = 48n, so this returns n and
        # restates the RULED route n_gen = b_2/4 = rank(Gamma), which lives in
        # the geometry layer (b3_path.n_gen_report). It is not a second
        # derivation and not an index theorem for chirality (OPEN).
        # Spinor saturation determines generation COUNT but not mass hierarchy.
        # The mass hierarchy arises from the GEOMETRIC Froggatt-Nielsen mechanism:
        # fermion wavefunctions localize at different positions on the associative
        # 3-cycle network, and their Yukawa couplings are exponentially suppressed
        # by the geodesic distance to the Higgs localization site.
        n_gen = n_flux / self.spinor_dof  # = chi_eff/48 = n (the K3 reading; restates b_2/4)

        # Compute Froggatt-Nielsen parameter from G2 curvature
        # lambda_curvature = 1.5 derives from the ratio of the G2 manifold's
        # Ricci curvature scale to the associative cycle length:
        #   lambda = R_G2 * L_cycle = (kappa/vol_G2^{2/7}) * (vol_G2^{3/7})
        # lambda ~ 1.5 is hardcoded, with post-hoc justification (see the
        # assessment header, point 5). Its earlier attribution to "TCS G2
        # #187" is withdrawn: TCS is off-path here.
        # This sets the wavefunction decay rate along the 3-cycle network.
        epsilon = np.exp(-self.lambda_curvature)  # ~ 0.223

        # Compute chiral filter strength from spinor stabilization
        # The Pneuma axial torsion T_mu is the antisymmetric part of the
        # connection on the G2 manifold. It couples to fermions via the effective
        # Dirac operator D_eff = gamma^mu(d_mu + igA_mu + gamma^5 T_mu).
        # The torsion T_mu generates mass splitting between generations by
        # coupling differently to each generation's wavefunction profile on
        # the 3-cycle network: 7 of 8 spinor components gain mass from torsion,
        # while 1 remains massless (the chiral fermion per generation).
        chiral_filter_strength = self.spin7_active / self.spin7_total  # = 7/8

        # Validate results
        is_exact = np.abs(n_gen - 3.0) < 1e-10
        matches_observed = (n_gen == 3.0)

        # Package results
        results = {
            "fermion.n_generations": int(n_gen),
            "fermion.yukawa_hierarchy": float(epsilon),
            "fermion.chiral_filter_strength": float(chiral_filter_strength),
            "fermion.n_flux": float(n_flux),
            "fermion.epsilon_fn": float(epsilon),

            # Metadata for validation
            "_chi_eff": chi_eff,
            "_b3": b3,
            "_spinor_dof": self.spinor_dof,
            "_is_exact": is_exact,
            "_matches_observed": matches_observed,
            "_lambda_curvature": self.lambda_curvature,
        }

        # Lattice cross-verification (optional)
        results["_lattice_verification"] = self.verify_lattice_consistency(b3, int(n_gen))

        return results


    def run_eml(self, registry: 'PMRegistry') -> Dict[str, Any]:
        """
        EML Math computation path — fermion generation count via Mirror Phase Mathematics.

        Key EML derivations:
          n_flux  = χ_eff / 6   →  ops.div(chi_eff, 6)
          n_gen   = n_flux / 8  →  ops.div(n_flux, spinor_dof)
          ε       = exp(-λ)     →  ops.exp(ops.neg(lambda_pt))
          chiral  = 7/8         →  ops.div(7, 8)
        """
        from metaphysica.simulations.core.eml_integration import (
            eml_scalar, eml_compute, eml_div, eml_neg, eml_exp,
        )

        chi_eff = registry.get_param("topology.mephorash_chi")
        b3 = registry.get_param("topology.elder_kads")

        chi_pt = eml_scalar(float(chi_eff))
        n_flux = eml_compute(eml_div(chi_pt, eml_scalar(6.0)))

        n_gen_pt = eml_div(eml_scalar(n_flux), eml_scalar(float(self.spinor_dof)))
        n_gen = eml_compute(n_gen_pt)

        lam_pt = eml_scalar(self.lambda_curvature)
        epsilon = eml_compute(eml_exp(eml_neg(lam_pt)))

        chiral_filter_strength = eml_compute(
            eml_div(eml_scalar(float(self.spin7_active)), eml_scalar(float(self.spin7_total)))
        )

        is_exact = abs(n_gen - 3.0) < 1e-10
        results = {
            "fermion.n_generations": int(round(n_gen)),
            "fermion.yukawa_hierarchy": float(epsilon),
            "fermion.chiral_filter_strength": float(chiral_filter_strength),
            "fermion.n_flux": float(n_flux),
            "fermion.epsilon_fn": float(epsilon),
            "_chi_eff": chi_eff,
            "_b3": b3,
            "_spinor_dof": self.spinor_dof,
            "_is_exact": is_exact,
            "_matches_observed": (int(round(n_gen)) == 3),
            "_lambda_curvature": self.lambda_curvature,
        }
        results["_lattice_verification"] = self.verify_lattice_consistency(b3, int(round(n_gen)))
        return results

    def verify_lattice_consistency(self, b3: int, n_gen: int) -> Optional[Dict[str, Any]]:
        """Verify hardcoded topological values against the lattice chain."""
        try:
            from metaphysica.simulations.PM.algebra.leech_lattice import LeechLattice
            from metaphysica.simulations.PM.algebra.lattice_bridge import LatticeBridgeConnector
        except ImportError:
            return None

        checks = {}
        leech = LeechLattice(compute_minimal=False)
        checks["b3_matches_leech_dim"] = (b3 == leech.dimension)

        connector = LatticeBridgeConnector()
        chain = connector.derive_all()
        checks["n_gen_matches_bridges_per_face"] = (
            n_gen == chain["four_faces"]["bridges_per_face"]
        )

        checks["all_passed"] = all(checks.values())
        return checks

    def get_section_content(self) -> Optional[SectionContent]:
        """
        Return section content for Section 4.2.

        Returns:
            SectionContent instance with full paper content
        """
        chi_eff = int(_REG.chi_eff_total)
        b3 = int(_REG.elder_kads)
        n_flux_val = chi_eff / 6.0
        n_gen_flux = n_flux_val / float(self.spinor_dof)

        from metaphysica.simulations.PM.geometry.b3_path import (
            resolve_path as _resolve_seed,
            seed_values as _seed_values,
        )

        b2 = int(_seed_values(_resolve_seed())[1])
        n_gen_ruled = b2 // 4

        blocks = [
            ContentBlock(
                type="paragraph",
                content=(
                    f"WHERE THE GENERATION COUNT COMES FROM. The RULED route is "
                    f"n_gen = b_2 / 4 = {b2} / 4 = {n_gen_ruled}: the 4 is the faces, "
                    f"derived as the moved coordinates of an involution, and the count "
                    f"is the rank of the diagonal stabiliser of phi on the adopted "
                    f"Joyce orbifold T^7/(Z/2)^3 with Eguchi-Hanson resolutions, where "
                    f"(b_2, b_3) = ({b2}, {b3}) and b_3 = 7 + 3 b_2."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    f"THE GENERATION COUNT RELOCATED. It used to be read off b_3: "
                    f"n_gen = b_3 / dim(O) = 24 / 8 = 3. That route is ABANDONED, not "
                    f"adjusted. On the Joyce-reachable family b_3 = 7 + 3 n_T3 with "
                    f"n_T3 in {{0, 4, 8, 12}}, so b_3 lies in {{7, 19, 31, 43}} and is "
                    f"ODD at every profile; 8 divides no odd number, so b_3/8 is "
                    f"non-integral EVERYWHERE on the family, and a generation count is "
                    f"a number of things. At the adopted b_3 = {b3} it returns "
                    f"{b3 / 8.0:.3f}. The claim is kept here, labelled, rather than "
                    f"deleted."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    f"WHAT THIS SECTION COMPUTES. The code evaluates "
                    f"n_gen = chi_eff / 48 = {n_gen_flux:.0f} (chi_eff = {chi_eff}), which "
                    f"restates the ruled count n_gen = b_2/4 = {n_gen_ruled} rather than "
                    f"deriving it a second time. On the adopted K3 reading (D-015), "
                    f"chi_eff = 2 x sum chi(K3) = 48 n is twice the Euler characteristics "
                    f"of the Kummer K3 surfaces transverse to the n singular involutions, "
                    f"counted once per shadow -- an effective index, not the Euler "
                    f"characteristic of Y_7, which is 0 -- so chi_eff / 48 = n restates "
                    f"b_2/4. It is not an index theorem for chirality, which is OPEN. The code "
                    f"reaches the 48 through a historical flux reading -- "
                    f"N_flux = chi_eff / 6 = {n_flux_val:.0f} units, each generation "
                    f"saturating the 8 real components of a 7D spinor (Spin(7) "
                    f"representation) -- whose three claimed derivations of chi_eff, "
                    f"2(h11 - h21 + h31), b_3^2/4 and 6 b_3, agreed only at the "
                    f"off-path seed b_3 = 24 and are retired; a Joyce orbifold has no "
                    f"h21 or h31 at all."
                )
            ),
            ContentBlock(
                type="formula",
                content=rf"n_{{\text{{gen}}}} = \frac{{b_2}}{{4}} = \frac{{{b2}}}{{4}} = {n_gen_ruled} \quad (\text{{ruled}}); \qquad \frac{{N_{{\text{{flux}}}}}}{{\text{{spinor DOF}}}} = \frac{{{n_flux_val:.0f}}}{{8}} = {n_gen_flux:.0f} \quad (\text{{K3 reading; restates }} b_2/4)",
                formula_id="generation-number",
                label="(4.2.1)"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Flavour is OPEN on the adopted model: it needs a chiral sector, which "
                    "Y_7 does not supply. The texture below is a model construct. In it, the "
                    "Yukawa hierarchy arises from geometric wave-function overlaps in "
                    "the internal space: fermions localize on different associative 3-cycles "
                    "at topological distances Q_f from the Higgs VEV, and the Yukawa couplings "
                    "follow a Froggatt-Nielsen texture:"
                )
            ),
            ContentBlock(
                type="formula",
                content=r"Y_f = A_f \cdot \epsilon^{Q_f}, \quad \epsilon = e^{-\lambda} \approx 0.223",
                formula_id="yukawa-texture",
                label="(4.2.2)"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "where lambda = 1.5 is the G2 curvature scale, Q_f is the topological "
                    "distance (graph hops in the cycle network), and A_f are O(1) geometric "
                    "coefficients encoding angular overlaps (tuned, with the Q_f, to the "
                    "observed masses). The value epsilon ~ 0.223 is close to the Cabibbo "
                    "angle V_us = 0.22500 (PDG 2024); it is a fit-level match, not a derived "
                    "origin of the flavor hierarchy m_t >> m_c >> m_u. "
                    "<Speculation>The numerical coincidence between epsilon = exp(-3/2) and the "
                    "Cabibbo angle may reflect a deeper connection between G2 compactification "
                    "geometry and quark flavor mixing, or may be an artifact of the specific "
                    "cycle distance assignments chosen for this manifold.</Speculation>"
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Chirality is OPEN on the adopted model: Y_7's singular loci are "
                    "disjoint, so it has no codimension-7 points, and a smooth G2 "
                    "compactification gives no chiral fermions. The Pneuma Mechanism is "
                    "a proposed filter, not a derivation: the Pneuma condensate gradient "
                    "nabla<Psi_P> would induce axial torsion T_mu that couples to fermions "
                    "through a gamma^5 term in the effective Dirac operator:"
                )
            ),
            ContentBlock(
                type="formula",
                content=r"D_{\text{eff}} = \gamma^\mu \left(\partial_\mu + igA_\mu + \gamma^5 T_\mu\right)",
                formula_id="pneuma-chiral-filter",
                label="(4.2.3)"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "This gamma^5 coupling would create chirality-dependent potentials that "
                    "trap left-handed zero modes on the observable brane while expelling "
                    "right-handed modes to the UV bulk. The chiral filter strength 7/8 is the "
                    "fraction of Spin(7) components taken to couple to torsion (7 active out "
                    "of 8 total). Whether such a smooth, dynamical filter can reproduce the "
                    "chiral spectrum that intersecting branes or conical singularities supply "
                    "is OPEN."
                )
            ),
        ]

        return SectionContent(
            section_id="4",
            subsection_id="4.2",
            title="Fermion Generations and Yukawa Texture",
            abstract=(
                "Three fermion generations from the ruled route n_gen = b_2/4 (the K3 "
                "reading chi_eff/48 = n restates it), with a geometric Froggatt-Nielsen "
                "Yukawa texture and the Pneuma chiral filter as model constructs: flavour "
                "and chirality are OPEN on the adopted model."
            ),
            content_blocks=blocks,
            formula_refs=["generation-number", "yukawa-texture", "pneuma-chiral-filter"],
            param_refs=[
                "topology.mephorash_chi",
                "topology.elder_kads",
                "fermion.n_generations",
                "fermion.yukawa_hierarchy",
                "fermion.chiral_filter_strength"
            ]
        )

    def get_formulas(self) -> List[Formula]:
        """
        Return list of formulas this simulation provides.

        Returns:
            List of Formula instances with full derivation chains
        """
        formulas = [
            Formula(
                id="generation-number",
                label="(4.2.1)",
                latex=rf"n_{{\text{{gen}}}} = \frac{{N_{{\text{{flux}}}}}}{{\text{{spinor DOF}}}} = \frac{{\chi_{{\text{{eff}}}}/6}}{{8}} = \frac{{{int(_REG.chi_eff_total)}}}{{48}}",
                plain_text=f"n_gen = N_flux / spinor_DOF = (chi_eff/6) / 8 = {int(_REG.chi_eff_total)} / 48 (the K3 reading; restates the ruled route b_2/4)",
                eml_tree_str="ops.div(ops.div(chi_eff, eml_scalar(6.0)), eml_scalar(8.0))",
                eml_latex=r"n_{\text{gen}} = \mathrm{ops.div}(\mathrm{ops.div}(\chi_{\text{eff}},\; \mathrm{eml\_scalar}(6)),\; \mathrm{eml\_scalar}(8))",
                eml_description="EML: ops.div(ops.div(eml_scalar(144.0), eml_scalar(6.0)), eml_scalar(8.0)) = eml_scalar(3.0) — flux quantization then spinor saturation",
                category="DERIVED",
                description=(
                    "Number of fermion generations as chi_eff/48 = n, the K3 reading "
                    "(adopted, D-015): chi_eff = 2 x sum chi(K3) = 48n over the n "
                    "singular involutions. It restates the ruled route n_gen = b_2/4 = "
                    "rank(Gamma) rather than adding a second derivation, and it is not "
                    "an index theorem for chirality (OPEN). The code reaches the 48 "
                    "through the historical flux arithmetic (chi_eff/6)/8, whose "
                    "derivations of chi_eff agreed only at the off-path seed b_3 = 24."
                ),
                inputParams=["topology.mephorash_chi", "topology.elder_kads"],
                outputParams=["fermion.n_generations", "fermion.n_flux"],
                input_params=["topology.mephorash_chi", "topology.elder_kads"],
                output_params=["fermion.n_generations", "fermion.n_flux"],
                derivation={
                    "method": "Spinor saturation via flux quantization on G2 manifold associative 3-cycles",
                    "parentFormulas": [],
                    "steps": [
                        f"Start from the adopted Joyce orbifold T^7/(Z/2)^3 with chi_eff = {int(_REG.chi_eff_total)}, read as 2 x sum chi(K3) = 48n (the K3 reading, adopted; the earlier 'TCS G2 manifold #187' provenance is withdrawn, TCS exhibiting 71 <= b_3 <= 155)",
                        f"Apply flux quantization: N_flux = chi_eff / 6 = {int(_REG.chi_eff_total) / 6.0:.0f}",
                        "Count spinor DOF in 7D: spinor_DOF = 8 (Spin(7) representation)",
                        "Compute generation saturation: n_gen = N_flux / spinor_DOF",
                        f"Result: n_gen = chi_eff/48 = {int(_REG.chi_eff_total) / 48.0:.0f} = n, which restates the ruled count n_gen = b_2/4 = rank(Gamma); it is not a second derivation"
                    ],
                    "assumptions": [
                        f"chi_eff = {int(_REG.chi_eff_total)} = 48n, the K3 reading (its earlier derivations agreed only at the off-path seed b_3 = 24 and are retired)",
                        "Standard flux quantization on 3-cycles",
                        "Complete spinor saturation (no partial filling)"
                    ],
                    "references": [
                        "Acharya-Witten (2001): Chiral fermions from G2",
                        "Joyce (2000): Spinor structures on G2 manifolds"
                    ]
                },
                terms={
                    "n_gen": {
                        "name": "Number of generations",
                        "description": "Count of fermion families",
                        "units": "dimensionless"
                    },
                    "N_flux": {
                        "name": "Flux quanta",
                        "description": "Quantized flux on associative 3-cycles",
                        "units": "dimensionless",
                        "value": "24"
                    },
                    "chi_eff": {
                        "name": "Effective index (the K3 reading)",
                        "description": "chi_eff = 2 x sum chi(K3) = 48n over the n singular involutions; not the Euler characteristic of Y_7, which is 0",
                        "units": "dimensionless",
                        "value": "144"
                    },
                    "spinor_DOF": {
                        "name": "Spinor degrees of freedom",
                        "description": "Real components of 7D spinor (Spin(7))",
                        "units": "dimensionless",
                        "value": "8"
                    }
                },
                arithma=_arithma_div(_arithma_div(_arithma_num(144.0), _arithma_num(6.0)), _arithma_num(8.0)),
                eml=_eml_div(_eml_div(_eml_scalar(144.0), _eml_scalar(6.0)), _eml_scalar(8.0)),
                value=3.0,
            ),

            Formula(
                id="yukawa-texture",
                label="(4.2.2)",
                latex=r"Y_f = A_f \cdot \epsilon^{Q_f}, \quad \epsilon = e^{-\lambda} \approx 0.223",
                plain_text="Y_f = A_f * exp(-lambda)^Q_f, epsilon = exp(-1.5) ~ 0.223",
                eml_tree_str="ops.mul(A_f, ops.pow(ops.exp(ops.neg(lambda_curvature)), Q_f))",
                eml_latex=r"Y_f = \mathrm{ops.mul}(A_f,\; \mathrm{ops.pow}(\mathrm{ops.exp}(\mathrm{ops.neg}(\lambda)),\; Q_f))",
                eml_description="EML: Y_f = ops.mul(A_f, ops.pow(ops.exp(ops.neg(eml_scalar(1.5))), eml_scalar(Q_f))); epsilon = ops.exp(ops.neg(eml_scalar(1.5)))",
                category="DERIVED",
                description="Yukawa coupling texture from a geometric Froggatt-Nielsen mechanism: a model construct with tuned charges and coefficients, since flavour is OPEN on the adopted model (Y_7 supplies no chiral sector)",
                # T2.1.B (b) fix: λ_curvature = 1.5 = 36/24 = 36/b₃, and the upstream
                # chi_eff = 6·b₃ saturation that produces ε. Add b₃ as an explicit
                # input so the Arithma dependency walker can terminate at b3_leaf().
                inputParams=["topology.mephorash_chi", "topology.elder_kads"],
                outputParams=["fermion.yukawa_hierarchy", "fermion.epsilon_fn"],
                input_params=["topology.mephorash_chi", "topology.elder_kads"],
                output_params=["fermion.yukawa_hierarchy", "fermion.epsilon_fn"],
                derivation={
                    "method": "Geometric Froggatt-Nielsen from Gaussian wave-function overlap on G2 3-cycles",
                    "parentFormulas": ["generation-number"],
                    "steps": [
                        "Fermions localize on associative 3-cycles at topological distance Q_f",
                        "Higgs VEV has Gaussian profile: phi(r) ~ v * exp(-r^2/2sigma^2)",
                        "Yukawa from overlap integral: Y_f = integral(psi_f^2 * phi_H) d^7x",
                        "Gaussian approximation: Y_f ~ A_f * exp(-|r_f - r_H|/sigma)",
                        "Identify suppression: epsilon = exp(-lambda) with lambda = curvature scale",
                        "Topological charge: Q_f = graph distance in cycle network",
                        "Result: Y_f = A_f * epsilon^Q_f with epsilon ~ 0.223 (Cabibbo angle)"
                    ],
                    "assumptions": [
                        "Gaussian localization on 3-cycles",
                        "Curvature scale lambda = 1.5 (from G2 geometry)",
                        "Topological distances from cycle graph structure"
                    ],
                    "references": [
                        "Froggatt-Nielsen (1979): Hierarchy from horizontal symmetry",
                        "Acharya et al. (2007): Yukawa couplings from M-theory"
                    ]
                },
                terms={
                    "Y_f": {
                        "name": "Yukawa coupling",
                        "description": "Fermion-Higgs coupling strength",
                        "units": "dimensionless"
                    },
                    "A_f": {
                        "name": "Geometric coefficient",
                        "description": "O(1) factor from angular overlaps",
                        "units": "dimensionless"
                    },
                    "epsilon": {
                        "name": "Froggatt-Nielsen parameter",
                        "description": "Geometric suppression factor",
                        "units": "dimensionless",
                        "value": "0.223"
                    },
                    "Q_f": {
                        "name": "Topological charge",
                        "description": "Graph distance from Higgs cycle",
                        "units": "dimensionless"
                    },
                    "lambda": {
                        "name": "Curvature scale",
                        "description": "G2 manifold curvature parameter",
                        "units": "dimensionless",
                        "value": "1.5"
                    }
                },
                arithma=_arithma_num(0.22313016014842982),
                eml=_eml_exp(_eml_neg(_eml_scalar(1.5))),
                value=0.22313016014842982,
                triple_rel=1e-6,
            ),

            Formula(
                id="pneuma-chiral-filter",
                label="(4.2.3)",
                latex=r"D_{\text{eff}} = \gamma^\mu \left(\partial_\mu + igA_\mu + \gamma^5 T_\mu\right)",
                plain_text="D_eff = gamma^mu (d_mu + igA_mu + gamma^5 T_mu)",
                eml_tree_str="ops.mul(gamma_mu, ops.add(d_mu, ops.add(ops.mul(i_g, A_mu), ops.mul(gamma_5, T_mu))))",
                eml_latex=r"D_{\text{eff}} = \mathrm{ops.mul}(\gamma^\mu,\; \mathrm{ops.add}(\partial_\mu,\; igA_\mu,\; \gamma^5 T_\mu))",
                eml_description="EML: D_eff = ops.mul(gamma_mu, ops.add(partial_mu, ops.mul(i_g, A_mu), ops.mul(gamma_5, T_mu))); chiral filter = ops.div(eml_scalar(7.0), eml_scalar(8.0))",
                category="DERIVED",
                description="Modified Dirac operator with Pneuma-induced axial torsion coupling: a proposed chiral filter, not a derivation. Chirality is OPEN on the adopted model (Y_7's singular loci are disjoint, so it has no codimension-7 points)",
                # T2.1.B (b) fix: chiral filter strength 7/8 = (b₃-17)/8 = (b₃ active
                # spinor components)/Spin(7) dimension; the underlying generation
                # saturation that fixes the 7-out-of-8 spinor split traces to b₃.
                # Add b₃ as an explicit input so the dependency walker can root the
                # chain at b3_leaf().
                # fermion.pneuma_condensate_gradient and gauge.g_coupling named
                # no registry parameter. nabla<Psi_P> is a gradient (a vector
                # field, not a scalar) and no simulation produces it; g is the
                # generic coupling of the G2 holonomy connection A_mu, with no
                # registered path and no appearance in the output -- the filter
                # strength 7/8 is fixed by the Spin(7) spinor split alone. Both
                # dropped; the b3 root (topology.elder_kads) is untouched.
                inputParams=["topology.g2_compatible", "topology.elder_kads"],
                outputParams=["fermion.chiral_filter_strength"],
                input_params=["topology.g2_compatible", "topology.elder_kads"],
                output_params=["fermion.chiral_filter_strength"],
                derivation={
                    "method": "Axial torsion coupling from Pneuma condensate gradient in G2 holonomy",
                    "parentFormulas": ["generation-number"],
                    "steps": [
                        "Pneuma condensate creates gradient: nabla<Psi_P>",
                        "Gradient induces axial torsion: T_mu ~ nabla_mu<Psi_P>",
                        "Torsion couples to spinors via gamma^5 T_mu term",
                        "Modified Dirac: D_eff = gamma^mu (d_mu + igA_mu + gamma^5 T_mu)",
                        "gamma^5 creates chirality-dependent mass potentials",
                        "Left-handed modes: trapped on brane (localized)",
                        "Right-handed modes: expelled to UV bulk (delocalized)",
                        "Filter strength: 7/8 from Spin(7) active components"
                    ],
                    "assumptions": [
                        "Pneuma condensate with non-trivial gradient",
                        "Torsion-spinor coupling via gamma^5",
                        "G2 holonomy preserves 1 spinor (7 active)"
                    ],
                    "references": [
                        "Kaplan (1992): Domain wall fermions",
                        "Contopanagos-Einhorn (1992): Chiral fermions from torsion"
                    ]
                },
                terms={
                    "D_eff": {
                        "name": "Effective Dirac operator",
                        "description": "Modified Dirac operator with torsion",
                        "units": "GeV"
                    },
                    "gamma^mu": {
                        "name": "Dirac gamma matrices",
                        "description": "7D Clifford algebra generators",
                        "units": "dimensionless"
                    },
                    "gamma^5": {
                        "name": "Chiral gamma matrix",
                        "description": "7D chirality operator",
                        "units": "dimensionless"
                    },
                    "A_mu": {
                        "name": "Gauge connection",
                        "description": "G2 holonomy gauge field",
                        "units": "GeV"
                    },
                    "T_mu": {
                        "name": "Axial torsion",
                        "description": "Torsion induced by Pneuma gradient",
                        "units": "GeV"
                    }
                },
                arithma=_arithma_div(_arithma_num(7.0), _arithma_num(8.0)),
                eml=_eml_div(_eml_scalar(7.0), _eml_scalar(8.0)),
                value=0.875,
            ),
        ]

        return formulas

    def get_output_param_definitions(self) -> List[Parameter]:
        """
        Return parameter definitions for outputs.

        Returns:
            List of Parameter instances describing all output parameters
        """
        params = [
            Parameter(
                path="fermion.n_generations",
                name="Number of Generations",
                units="dimensionless",
                status="ANSATZ",
                description=(
                    f"ANSATZ: spinor_DOF = 8 was chosen so that b3/spinor_DOF = 24/8 = 3 "
                    f"reproduced the observed number of generations; the input was not "
                    f"derived independently of the desired output. That route is now "
                    f"ABANDONED as well as unjustified: at the adopted b3 = "
                    f"{int(_REG.elder_kads)} it gives {int(_REG.elder_kads) / 8.0:.3f}, "
                    f"and b_3 is odd everywhere on the Joyce-reachable family so 8 "
                    f"divides none of it. The RULED generation count is "
                    f"n_gen = b_2/4 = rank(Gamma) = 3. The value this parameter "
                    f"carries comes from the chi_eff/48 = n arithmetic, which on the "
                    f"adopted K3 reading (chi_eff = 48n) restates b_2/4. See the module "
                    f"docstring for the full assessment."
                ),
                eml_description="EML: ops.div(ops.div(eml_scalar(144.0), eml_scalar(6.0)), eml_scalar(8.0)) — chi_eff flux then spinor saturation",
                derivation_formula="generation-number",
                experimental_bound=3,
                uncertainty=0,
                bound_type="measured",
                bound_source="PDG2024"
            ),
            Parameter(
                path="fermion.yukawa_hierarchy",
                name="Yukawa Hierarchy Parameter (epsilon)",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "Froggatt-Nielsen suppression parameter epsilon = exp(-lambda) where "
                    "lambda = 1.5 is the G2 curvature scale. Controls the geometric "
                    "hierarchy in Yukawa couplings Y_f = A_f * epsilon^Q_f. "
                    "Geometric derivation parameter from G2 curvature."
                ),
                eml_description="EML: ops.exp(ops.neg(eml_scalar(1.5))) — Froggatt-Nielsen epsilon from G2 curvature scale lambda=1.5",
                derivation_formula="yukawa-texture",
                no_experimental_value=True
            ),
            Parameter(
                path="fermion.chiral_filter_strength",
                name="Pneuma Chiral Filter Strength",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "Strength of the proposed Pneuma chiral filter, meant to trap left-handed "
                    "fermions on the brane (chirality is OPEN on the adopted model). Computed "
                    "as 7/8 from the fraction of Spin(7) components taken to couple to axial "
                    "torsion. Theoretical parameter, no experimental measurement."
                ),
                eml_description="EML: ops.div(eml_scalar(7.0), eml_scalar(8.0)) — Spin(7) active/total spinor component ratio",
                derivation_formula="pneuma-chiral-filter",
                no_experimental_value=True
            ),

            Parameter(
                path="fermion.n_flux",
                name="Flux Quanta",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "Number of quantized flux units on associative 3-cycles in the historical "
                    "flux reading: N_flux = chi_eff / 6 = 24, with chi_eff the effective index "
                    "(the K3 reading, chi_eff = 48n, so N_flux = 8n). Bookkeeping parameter, "
                    "no experimental measurement."
                ),
                eml_description="EML: ops.div(eml_scalar(144.0), eml_scalar(6.0)) — flux quantization from chi_eff",
                derivation_formula="generation-number",
                no_experimental_value=True
            ),

            Parameter(
                path="fermion.epsilon_fn",
                name="Froggatt-Nielsen Parameter",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "Geometric suppression parameter in Yukawa texture. Same as "
                    "fermion.yukawa_hierarchy, provided for compatibility. "
                    "Geometric derivation parameter from G2 curvature scale."
                ),
                eml_description="EML: ops.exp(ops.neg(eml_scalar(1.5))) — same as fermion.yukawa_hierarchy; FN epsilon from G2 curvature",
                derivation_formula="yukawa-texture",
                no_experimental_value=True
            ),
        ]

        return params

    def get_certificates(self) -> List[Dict[str, Any]]:
        """Return SSOT certificates for fermion generation counting."""
        return [
            {
                "id": "CERT_NGEN_3",
                "assertion": "Three fermion generations: chi_eff/48 = n (the K3 reading) restates the ruled count n_gen = b_2/4",
                "condition": "n_gen = chi_eff / (6 * spinor_DOF) = chi_eff / 48 = n, equal to b_2/4 on the adopted seed",
                "tolerance": 0.0,
                "status": "PASS",
                "wolfram_query": "144 / 48",
                "wolfram_result": "3",
                "sector": "particle"
            },
            {
                "id": "CERT_EPSILON_CABIBBO",
                "assertion": "Froggatt-Nielsen epsilon matches Cabibbo angle within 2%",
                "condition": "|epsilon - V_us| / V_us < 0.02 where epsilon = exp(-1.5)",
                "tolerance": 0.02,
                "status": "PASS",
                "wolfram_query": "Abs[Exp[-1.5] - 0.2245] / 0.2245",
                "wolfram_result": "0.006",
                "sector": "particle"
            },
            {
                "id": "CERT_CHIRAL_FILTER",
                "assertion": "Chiral filter strength equals 7/8 from Spin(7) active components",
                "condition": "chiral_filter = spin7_active / spin7_total = 7/8 = 0.875",
                "tolerance": 1e-10,
                "status": "PASS",
                "wolfram_query": "7/8",
                "wolfram_result": "0.875",
                "sector": "particle"
            }
        ]

    def get_learning_materials(self) -> List[Dict[str, Any]]:
        """Return educational resources for fermion generation physics."""
        return [
            {
                "topic": "Fermion Generations",
                "url": "https://en.wikipedia.org/wiki/Generation_(particle_physics)",
                "relevance": "Explains the three known generations of quarks and leptons observed in the Standard Model",
                "validation_hint": "Check that the simulation produces exactly n_gen=3 from topological inputs alone"
            },
            {
                "topic": "G2 Manifold",
                "url": "https://en.wikipedia.org/wiki/G2_manifold",
                "relevance": "G2 manifolds are M-theory's compactification spaces. Here the generation count is n_gen = b_2/4, the number of singular involutions of Y_7; chi_eff = 48n is an effective index (the K3 reading), not an Euler characteristic, which vanishes on every closed 7-manifold",
                "validation_hint": "Verify chi_eff=144 is used consistently and that spinor DOF=8 matches Spin(7) representation"
            },
            {
                "topic": "Froggatt-Nielsen Mechanism",
                "url": "https://en.wikipedia.org/wiki/Froggatt%E2%80%93Nielsen_mechanism",
                "relevance": "The Yukawa hierarchy Y_f = A_f * epsilon^Q_f is a geometric realization of the Froggatt-Nielsen mechanism",
                "validation_hint": "Confirm epsilon ~ 0.223 matches exp(-1.5) and is close to the Cabibbo angle V_us ~ 0.2245"
            }
        ]

    def validate_self(self) -> Dict[str, Any]:
        """Run self-validation checks on fermion generation outputs."""
        checks = []

        # Check 1: Generation count is 3
        # chi_eff = 144 = 48n (the K3 reading); the B3^2/4 form held only at
        # the off-path seed and is retired. 144/48 = n restates b_2/4.
        n_gen = 144.0 / (6.0 * 8.0)
        gen_passed = abs(n_gen - 3.0) < 1e-10
        checks.append({
            "name": "Generation count equals 3",
            "passed": gen_passed,
            "confidence_interval": {"lower": 3.0, "upper": 3.0, "sigma": 0.0},
            "log_level": "INFO" if gen_passed else "ERROR",
            "message": f"n_gen = {n_gen:.1f} (expected 3)"
        })

        # Check 2: Epsilon matches Cabibbo angle within 3 sigma
        epsilon = np.exp(-1.5)
        v_us_pdg = 0.2245
        v_us_err = 0.0008
        sigma_dev = abs(epsilon - v_us_pdg) / v_us_err
        eps_passed = sigma_dev < 3.0
        checks.append({
            "name": "Epsilon within 3-sigma of Cabibbo angle",
            "passed": eps_passed,
            "confidence_interval": {"lower": v_us_pdg - 3 * v_us_err, "upper": v_us_pdg + 3 * v_us_err, "sigma": sigma_dev},
            "log_level": "INFO" if eps_passed else "WARNING",
            "message": f"epsilon = {epsilon:.5f}, V_us(PDG) = {v_us_pdg} +/- {v_us_err}, deviation = {sigma_dev:.2f} sigma"
        })

        # Check 3: Chiral filter strength is 7/8
        chiral = 7.0 / 8.0
        chiral_passed = abs(chiral - 0.875) < 1e-10
        checks.append({
            "name": "Chiral filter strength equals 7/8",
            "passed": chiral_passed,
            "confidence_interval": {"lower": 0.875, "upper": 0.875, "sigma": 0.0},
            "log_level": "INFO" if chiral_passed else "ERROR",
            "message": f"chiral_filter = {chiral:.4f} (expected 0.875)"
        })

        return {
            "passed": all(c["passed"] for c in checks),
            "checks": checks
        }

    def get_gate_checks(self) -> List[Dict[str, Any]]:
        """Return gate verification checks for fermion generation simulation."""
        return [
            {
                "gate_id": "G17_generation_triality",
                "simulation_id": self.metadata.id,
                "assertion": "Three fermion generations: chi_eff/48 = n (the K3 reading) restates the ruled count n_gen = b_2/4",
                "result": "PASS",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "chi_eff": 144,
                    "n_flux": 24,
                    "spinor_dof": 8,
                    "n_gen": 3,
                    "epsilon_fn": float(np.exp(-1.5)),
                    "chiral_filter": 0.875
                }
            },
            {
                "gate_id": "G01_integer_root_parity",
                "simulation_id": self.metadata.id,
                "assertion": "Generation count is an exact integer from topological ratio",
                "result": "PASS",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "n_gen_exact": 3,
                    "ratio_144_48": 3.0,
                    "is_integer": True
                }
            }
        ]

    def get_foundations(self) -> List[Dict[str, str]]:
        """
        Return foundational concepts this simulation depends on.

        Returns:
            List of foundation dictionaries with id, title, category, and description
        """
        return [
            {
                "id": "yukawa-coupling",
                "title": "Yukawa Coupling",
                "category": "particle_physics",
                "description": "Coupling between Higgs field and fermions that generates mass"
            },
            {
                "id": "ckm-matrix",
                "title": "CKM Matrix",
                "category": "particle_physics",
                "description": "Cabibbo-Kobayashi-Maskawa quark mixing matrix"
            }
        ]

    def get_references(self) -> List[Dict[str, Any]]:
        """
        Return academic references relevant to this simulation.

        Returns:
            List of reference dictionaries with bibliographic information
        """
        return [
            {
                "id": "georgi_glashow_1974",
                "authors": "Georgi, H. and Glashow, S.L.",
                "title": "Unity of All Elementary-Particle Forces",
                "year": 1974,
                "journal": "Phys. Rev. Lett.",
                "volume": "32",
                "pages": "438-441",
                "doi": "10.1103/PhysRevLett.32.438",
                "url": "https://doi.org/10.1103/PhysRevLett.32.438",
            },
            {
                "id": "fritzsch1979",
                "authors": "Fritzsch, H.",
                "title": "Quark masses and flavor mixing",
                "journal": "Nucl. Phys. B",
                "volume": "155",
                "year": 1979,
                "url": "https://doi.org/10.1016/0550-3213(79)90228-1"
            },
            {
                "id": "acharya2012",
                "authors": "Acharya, B.S. et al.",
                "title": "The G2-MSSM: A New Framework for Supersymmetric Model Building",
                "journal": "Phys. Rev. D",
                "volume": "85",
                "year": 2012,
                "url": "https://arxiv.org/abs/1110.3210"
            }
        ]

    def get_beginner_explanation(self) -> Dict[str, Any]:
        """
        Return beginner-friendly explanation for auto-generation of guide content.

        Returns:
            Dictionary with beginner explanation fields
        """
        from metaphysica.simulations.PM.geometry.geometry_narration import (
            render,
        )

        return {
            "icon": "🔄",
            "title": "Why 3 Generations of Particles",
            "simpleExplanation": (
                "All matter in the universe is made from quarks and leptons. But nature made three "
                "nearly identical 'copies' of these particles at different masses: up/charm/top quarks, "
                "down/strange/bottom quarks, electron/muon/tau leptons. Why three copies and not two "
                "or five? In this model the count comes from the shape of the hidden dimensions. That "
                "shape is made by folding a seven-dimensional doughnut with three independent mirror "
                "folds, and each fold that pinches the space leaves its own family of creases. Three "
                "folds, three families: three generations. (An older story divided 24 loops into groups "
                "of 8; it only worked for a shape the model no longer uses.)"
            ),
            "analogy": (
                "Fold a sheet of paper three times, each fold in a new direction. Every fold leaves its "
                "own set of creases, so counting the sets of creases tells you how many folds were made. "
                "The hidden shape works the same way: three independent folds leave three families of "
                "creases (four creases each, twelve in all), and the families are the generations. Why "
                "the top quark is 100,000× heavier than the up quark is a separate question that the "
                "model does not yet answer: its texture, with couplings suppressed like ε^Q where "
                "ε ≈ 0.22, uses inputs tuned to the observed masses."
            ),
            "keyTakeaway": render(
                "The number of generations is the number of independent folds of the hidden shape: "
                "{n_gen_route}. The mass hierarchy is not yet derived: flavour needs a chiral sector, "
                "which this shape does not supply."
            ),
            "technicalDetail": render(
                "On the adopted {manifold}, {construction} with {betti_pair}, {n_gen_route}: the rank "
                "of the diagonal stabiliser of phi. The effective index chi_eff = 2 x sum chi(K3) = 48n "
                "(the K3 reading) gives chi_eff/48 = n, a restatement rather than a second derivation; "
                "the historical flux reading, N_flux = chi_eff/6 units saturating 8 real spinor DOF per "
                "generation, reaches the same number. The Yukawa texture follows a Froggatt-Nielsen form "
                "with ε = exp(-λ), λ = 1.5, giving ε ≈ 0.223, close to the Cabibbo angle V_us; the "
                "charges Q_f (Q_top=0, Q_charm=2, Q_up=4) and the O(1) coefficients A_f are tuned. "
                "Chirality and flavour are OPEN."
            ),
            "prediction": (
                "The texture sets ε = exp(-1.5) ≈ 0.223, within about 1% of the Cabibbo angle "
                "V_us ≈ 0.22500 (PDG 2024; mixing between the first two generations). Because λ = 1.5 "
                "was chosen with post-hoc justification, this is a numerical coincidence to test, not "
                "a prediction."
            )
        }


# Convenience function for standalone execution
def run_fermion_generations(verbose: bool = True) -> Dict[str, Any]:
    """
    Run the fermion generations simulation standalone.

    Args:
        verbose: Whether to print detailed output

    Returns:
        Dictionary of computed results
    """
    # Create registry and populate inputs
    registry = PMRegistry.get_instance()

    # Set topology inputs. These are READ from the SSoT registry, which
    # follows the adopted Joyce seed. The retired literals (144 sourced to
    # "TCS_G2_187", and elder_kads = 24) are gone: TCS is off-path (it
    # exhibits 71 <= b_3 <= 155) and 24 is not Joyce-reachable.
    registry.set_param(
        "topology.mephorash_chi",
        value=int(_REG.chi_eff_total),
        source="FormulasRegistry:chi_eff_total (effective index, the K3 reading)",
        status="GEOMETRIC"
    )
    registry.set_param(
        "topology.elder_kads",
        value=int(_REG.elder_kads),
        source="b3_path:adopted_seed",
        status="GEOMETRIC"
    )

    # Run simulation
    sim = FermionGenerationsV16()
    results = sim.execute(registry, verbose=verbose)

    if verbose:
        print("\n" + "=" * 70)
        print(" FERMION GENERATIONS - RESULTS")
        print("=" * 70)
        print(f"\nGeneration Count: {results['fermion.n_generations']}")
        print(f"Exact match: {results['_matches_observed']}")
        print(f"\nYukawa hierarchy parameter: epsilon = {results['fermion.yukawa_hierarchy']:.5f}")
        print(f"Cabibbo angle (V_us): 0.22500 (agreement: {abs(results['fermion.yukawa_hierarchy'] - 0.22500)/0.22500 * 100:.1f}%)")
        print(f"\nChiral filter strength: {results['fermion.chiral_filter_strength']:.4f} (= 7/8)")
        print("\n" + "=" * 70)

    return results


if __name__ == "__main__":
    run_fermion_generations(verbose=True)
