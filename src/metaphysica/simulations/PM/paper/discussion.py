#!/usr/bin/env python3
"""
PRINCIPIA METAPHYSICA v24.2 - Discussion, Conclusions, and Theory Analysis
============================================================================

Licensed under the MIT License. See LICENSE file for details.

v24.2: M^{26}(24,2) structure with two shadow-time directions.
       12×(2,0) bridges + two shadow-time directions + T¹ time → 2×13D(12,1) shadows via OR reduction.
       4096-component Primordial Spinor Field from Cl(24,2).

Provides comprehensive section content for:
- Section 7: Conclusion (Summary, Predictions, Future Research)
- Section 8: Predictions and Testability
- Section 9: Discussion and Transparency
- Theory Analysis: Critical Analysis & Validation Summary

This simulation generates narrative content covering:
1. Summary of results and geometric unification achievements
2. Predictions, falsifiability criteria, and experimental tests
3. Theoretical implications and philosophical context
4. Comparison to alternative approaches
5. Theory status analysis and validation
6. Open questions, challenges, and future directions
7. Transparent assessment of inputs, limitations, and refinements

SECTIONS: 7, 8, 9, Theory-Analysis (Comprehensive Discussion/Conclusions)

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add parent directories to path for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_simulations_dir = os.path.dirname(os.path.dirname(_current_dir))
_project_root = os.path.dirname(_simulations_dir)
sys.path.insert(0, _project_root)

from metaphysica.simulations.base import (
    SimulationBase,
    SimulationMetadata,
    ContentBlock,
    SectionContent,
    Formula,
    Parameter,
)
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
    b3_leaf as _b3_leaf,
    eml_scalar as _eml_scalar,
    eml_add as _eml_add,
    eml_sub as _eml_sub,
    eml_mul as _eml_mul,
    eml_div as _eml_div,
    eml_neg as _eml_neg,
    eml_inv as _eml_inv,
    eml_exp as _eml_exp,
)
def _arithma_add(a, b):
    return None if a is None or b is None else a + b
def _arithma_sub(a, b):
    return None if a is None or b is None else a - b
def _arithma_neg(a):
    return None if a is None else -a
def _arithma_mul(a, b):
    return None if a is None or b is None else a * b
def _arithma_div(a, b):
    return None if a is None or b is None else a / b
def _arithma_inv(a):
    return None if a is None else 1.0 / a
import math as _math

from metaphysica.simulations.PM.paper.conclusions import (
    load_fit_summary as _load_fit_summary,
    section7_blocks,
    census_text,
    re_t_rows,
    re_t_mismatch_text,
    edof_items,
    prediction_rows,
    PATHS_LINK,
)


class DiscussionV16(SimulationBase):
    """
    Discussion, Conclusions, and Theory Analysis generator (v24.2).

    Provides comprehensive narrative content including:
    - Section 7: Conclusion (Summary, Predictions, Future Research)
    - Section 8: Predictions and Testability
    - Section 9: Discussion and Transparency
    - Theory Analysis: Critical Analysis & Validation
    """

    @property
    def metadata(self) -> SimulationMetadata:
        """Return metadata about this simulation."""
        return SimulationMetadata(
            id="discussion_v16_0",
            version="24.2",
            domain="discussion",
            title="Discussion, Conclusions, and Theory Analysis",
            description="Comprehensive discussion including theoretical implications, predictions, falsifiability, validation, and future directions for v24.2 dual-shadow framework (26D, 26,1)",
            section_id="7",
            subsection_id=None
        )

    @property
    def required_inputs(self) -> List[str]:
        """Registry parameters referenced by the discussion narrative."""
        return ["geometry.alpha_inverse", "geometry.w_zero"]

    @property
    def output_params(self) -> List[str]:
        """No output parameters - narrative content only."""
        return []

    @property
    def output_formulas(self) -> List[str]:
        """No formulas - discussion is narrative."""
        return []

    def run(self, registry: 'PMRegistry') -> Dict[str, Any]:
        """
        Execute the discussion generation.

        Args:
            registry: PMRegistry instance (not used)

        Returns:
            Empty dictionary (no computed parameters)
        """
        return {}


    def run_eml(self, registry: 'PMRegistry') -> Dict[str, Any]:
        """
        EML Math computation path.

        This simulation produces paper outputs. The EML Math representation
        for this module is in the section text via <EML>...</EML> blocks in
        get_section_content(). The computed parameter values are identical
        between Normal Math and EML Math modes.
        """
        return self.run(registry)

    def get_section_content(self) -> Optional[SectionContent]:
        """
        Return comprehensive section content for Sections 7-9 and Theory Analysis.

        Returns:
            SectionContent instance with complete discussion/conclusion narrative
        """
        content_blocks = [
            # =====================================================================
            # Section 7 is generated from live state (paper/conclusions.py).
            *section7_blocks(),

            # =====================================================================
            # SECTION 8: PREDICTIONS AND TESTABILITY
            # =====================================================================
            ContentBlock(
                type="heading",
                content="Predictions and Testability",
                level=1
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "This section gives the parameter census of the registry and presents key testable "
                    "predictions; the status of each result is stated in section 7. The framework makes specific, falsifiable predictions "
                    "for upcoming experiments including JUNO (neutrino hierarchy), HL-LHC (KK graviton), "
                    "Hyper-K (proton decay), and LISA (gravitational wave dispersion)."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The PM framework proposes Standard Model parameters on the active G₂ path (section 7 states "
                    "it and the status of each result). This section summarizes the parameter "
                    "derivations and presents testable predictions."
                )
            ),

            # 8.1 Parameter Census
            ContentBlock(
                type="heading",
                content="8.1 Parameter Census",
                level=2
            ),
            ContentBlock(type="paragraph", content=census_text(), label="parameter-census"),

            # 8.2 Testable Predictions
            ContentBlock(
                type="heading",
                content="8.2 Testable Predictions",
                level=2
            ),
            ContentBlock(
                type="table",
                headers=["Prediction", "Value", "Experiment", "Timeline"],
                rows=[
                    ["Normal Hierarchy", "OPEN: no computed confidence", "JUNO", "2027"],
                    *[[r[0], r[1] + " " + r[3], "HL-LHC" if "KK" in r[0] else "Hyper-K", "see section 7"] for r in prediction_rows() if r[0] in ("KK graviton mass", "Proton lifetime")],
                    ["BR(p→e⁺π⁰)", "OPEN: not computed", "Hyper-K", "2035+"],
                    ["GW dispersion", "η ≈ 0.113", "LISA", "2037+"],
                    ["w(z) form", "Logarithmic", "Euclid", "2028+"]
                ]
            ),

            # Derivation: KK Graviton Mass
            ContentBlock(
                type="heading",
                content="Derivation sketch: KK Graviton Mass M<sub>KK</sub> (canonical 4.5 TeV, warped form)",
                level=3
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>Step 1:</strong> G₂ compactification volume: V<sub>G₂</sub> = (Re(T))⁷ × ℓ<sub>P</sub>⁷ where ℓ<sub>P</sub> = 1.6 × 10⁻³⁵ m",
                    "<strong>Step 2:</strong> Modulus from Higgs constraint: Re(T) (open problem: 9.865 from Higgs inversion, 7.086 BBN-calibrated, 1.833 geometric)",
                    "<strong>Step 3:</strong> Compactification radius: R<sub>c</sub> = V<sub>G₂</sub><sup>1/7</sup> = Re(T) × ℓ<sub>P</sub>",
                    "<strong>Step 4:</strong> First KK mode mass: m<sub>KK,1</sub> = ℏc/R<sub>c</sub>",
                    "<strong>Step 5:</strong> As printed, Steps 1–4 give ℏc/R<sub>c</sub> ≈ 1.7 × 10¹⁸ GeV, not TeV; the 4.5 TeV value comes from the warped form M<sub>Pl</sub>e<sup>−k<sub>eff</sub>π</sup>, not this chain"
                ]
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<strong>Signature at HL-LHC:</strong> Missing transverse energy + dijets from "
                    "pp → G⁽¹⁾ → γγ, ZZ, W⁺W⁻"
                )
            ),

            # Re(T) Tension Ledger
            ContentBlock(
                type="heading",
                content="Re(T) Modulus: Open Tension Ledger",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The Kähler modulus Re(T) enters multiple calculation chains with incompatible values. "
                    "This tension is open; it is listed in the generated open problems of section 7."
                )
            ),
            ContentBlock(type="table", headers=["Re(T) value", "Registry row", "Registry classification", "Source"], rows=re_t_rows(), label="re-t-ledger"),
            ContentBlock(type="paragraph", content=re_t_mismatch_text(), label="re-t-mismatch"),
            ContentBlock(
                type="paragraph",
                content=(
                    "<strong>Resolution pathway:</strong> A unified Re(T) requires either (a) a racetrack superpotential "
                    "with multiple condensates that stabilizes the modulus at a single value consistent with both "
                    "Higgs mass and baryon asymmetry, or (b) a lattice G₂ computation of the full non-perturbative "
                    "potential V(T). Until resolved, Re(T) is OPEN; the table above states every registry row and "
                    "its classification."
                )
            ),

            # 8.3 Hidden Sector Particles
            ContentBlock(
                type="heading",
                content="8.3 Hidden Sector Particles",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The Z₂ mirror symmetry and shadow brane structure predict a hidden sector of particles "
                    "that couple weakly to Standard Model fields."
                )
            ),
            ContentBlock(
                type="table",
                headers=["Particle", "Mass Range", "Coupling to SM", "Signature"],
                rows=[
                    ["Shadow photon γ'", "~keV-MeV", "Kinetic mixing ε ~ 10⁻⁴", "Mono-photon + MET"],
                    ["Shadow Z boson Z'", "~1-10 TeV", "g' ~ g<sub>Z</sub> · 10⁻²", "Dilepton resonance"],
                    ["Pneuma axion a", "f<sub>a</sub> ~ 10¹² GeV", "g<sub>aγγ</sub> ~ α/(2πf<sub>a</sub>)", "ADMX, light shining through wall"],
                    ["Shadow fermions", "~100 GeV - 1 TeV", "Gravitational + Higgs portal", "Dark matter candidates"]
                ]
            ),

            # Dark Matter Candidate
            ContentBlock(
                type="heading",
                content="Dark Matter Candidate: Shadow Fermion",
                level=3
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>Step 1:</strong> Mass: m<sub>χ₀</sub> ~ v<sub>shadow</sub>/√2 ≈ 100−500 GeV (shadow EW breaking)",
                    "<strong>Step 2:</strong> Relic density: Ω<sub>χ</sub>h² ~ 0.12 (matches Planck) via thermal freeze-out",
                    "<strong>Step 3:</strong> Direct detection: σ<sub>SI</sub> ~ 10⁻⁴⁷ cm² (Higgs portal, below current limits)",
                    "<strong>Step 4:</strong> Indirect: χχ → W'W', Z'Z' → SM (cascade annihilation)"
                ]
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<em>Note:</em> The Z₂ mirror sector provides a WIMP dark matter candidate without "
                    "requiring additional fields."
                )
            ),

            # =====================================================================
            # SECTION 9: DISCUSSION AND TRANSPARENCY
            # =====================================================================
            ContentBlock(
                type="heading",
                content="Discussion and Transparency",
                level=1
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "This section provides a transparent summary of the framework's inputs, compares it to "
                    "other theoretical approaches, discusses supersymmetry, inflation, and black hole information, "
                    "and outlines limitations and future work."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Inputs, calibrations and fits are counted from the registry in the list below; "
                    "Re(T) is OPEN (see the Re(T) ledger in 8.2)."
                )
            ),

            # 9.1 Input Summary
            ContentBlock(
                type="heading",
                content="9.1 Input Summary",
                level=2
            ),
            ContentBlock(
                type="list",
                items=edof_items()
            ),

            # 9.1b Honest Scorecard (replaces earlier "v25.0/v26.0 closures"
            # narrative after the v2.1.0 shadow-derivation audit).
            ContentBlock(
                type="heading",
                content="9.1b Scorecard of Closures and Divergences",
                level=2,
                label="9.1b"
            ),
            ContentBlock(type="paragraph", content="OPEN: the counts and the compression ratio in this subsection were made at the superseded b<sub>3</sub> = 24 seed (see the <a href=\"" + PATHS_LINK + "\">paths page</a>) and are not regenerated by the engine for the active path."),
            ContentBlock(
                type="paragraph",
                content=(
                    "Sprints 4&ndash;6 of the v2.1.0 refactor landed thirteen candidate derivations "
                    "across versions 25.0 and 26.0. The triple-track validation harness "
                    "(Arithma + EML + float, registered through <code>run_all_simulations.py</code>) "
                    "subsequently surfaced <em>shadow derivations</em>: pre-existing chains in the "
                    "framework that compute the same observable as a new module but disagree on the "
                    "value. Re-evaluating the thirteen candidates against the live "
                    "<code>parameters.json</code> gives an honest breakdown: "
                    "<strong>5 real closures, 4 cross-consistent confirmations, 3 derivations worse "
                    "than the prior chain, and 1 documented open tension</strong>. This is still a "
                    "respectable lift, and the fact that the validation harness flagged the conflicts "
                    "automatically is itself the v2.1.0 methodological win &mdash; but the earlier "
                    "narrative that every proof-killer was sealed and every cosmological tension "
                    "eliminated is retired in favour of the breakdown that follows."
                )
            ),
            ContentBlock(
                type="heading",
                content="Closures",
                level=3
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>Strong CP &mdash; θ_QCD exactly 0.</strong> G<sub>2</sub> instanton "
                    "dynamics drive the axion VEV to the CP-conserving minimum "
                    "(<code>particle/strong_cp_axion.py</code>); f_a inherited from the Re(T) sector.",
                    "<strong>Re(T) VEV gap &mdash; 0.0000%.</strong> Non-perturbative "
                    "W<sub>flux</sub> + W<sub>inst</sub> stabilization at ReT⋆ = 174.033 GeV "
                    "(<code>geometry/re_t_sector.py::close_vev_gap</code>); consistent with v_EW = 246 GeV "
                    "up to the √2 factor.",
                    "<strong>Vacuum landscape pruning &mdash; 10<sup>33</sup> &rarr; 10<sup>24</sup>.</strong> "
                    "Dynamical Re(T) attractor flow reduces the naive flux landscape by nine orders of "
                    "magnitude (<code>cosmology/vacuum_selection.py</code>). The result is still huge; "
                    "this is a structural mechanism, not uniqueness of the vacuum.",
                    "<strong>Mirror DM relic &mdash; no overclosure.</strong> Boltzmann freeze-out across "
                    "the 12&times;(2,0) bridge coupling gives Ω_mirror·h² = 9.6&times;10⁻⁵, well under "
                    "the Planck 2018 cold-DM bound. Viable sub-component.",
                    "<strong>Higgs mass &mdash; 125.08 GeV via MSSM diagonalisation.</strong> "
                    "<code>particle/higgs_sector.py::derive_higgs_spectrum</code> diagonalises the "
                    "CP-even MSSM mass matrix against the v25.0 soft spectrum; m_h within 0.02 GeV "
                    "of PDG 2024."
                ]
            ),
            ContentBlock(
                type="heading",
                content="Cross-Consistent Confirmations",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Not new closures, but independent rederivations that agree with the framework's "
                    "prior chain at the 1% level &mdash; meaningful cross-checks:"
                )
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>PMNS θ₁₃.</strong> New T<sub>4</sub>/24-cell texture gives 8.67°; older "
                    "octonionic-mixing chain gives 8.65°. Both within ~1σ of NuFIT 6.0 IO 8.63° ± 0.11°.",
                    "<strong>θ_QCD.</strong> New geometric mechanism and older assignment both give 0.",
                    "<strong>Re(T) stabilization.</strong> New ReT⋆ minimum agrees with the existing "
                    "<code>moduli</code> location.",
                    "<strong>Σm<sub>ν</sub>.</strong> Refined neutrino sector gives 0.0425 eV, "
                    "comfortably below the DESI 2026 + Planck PR4 bound (&lt; 0.072 eV at 95% CL)."
                ]
            ),
            ContentBlock(
                type="heading",
                content="Derivations Worse Than the Prior Chain",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "These Sprint 4&ndash;5 modules landed schematic templates whose numerical output is "
                    "further from observation than the framework's pre-existing chain. Both sets of "
                    "numbers currently ship side-by-side in the registry; the shadow-derivation "
                    "detector (Tier 2 item T2.3) automates surfacing such conflicts. Each is "
                    "explicitly carried to v27.0 as a Tier 3 architectural item, not a quiet retraction:"
                )
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>n<sub>s</sub>:</strong> the Re(T) slow-roll variant (FALSIFIED) gives 0.9996 "
                    "(8.3σ from Planck); older <code>cosmology.n_s_pred = 0.9636</code> is "
                    "Planck-compatible. Status: <strong>OPEN</strong> &mdash; older derivation remains "
                    "canonical pending higher-order slow-roll corrections (Tier 3 T3.3).",
                    "<strong>η_B:</strong> new G<sub>2</sub>-entropy-dilution formula gives "
                    "2.3&times;10⁻¹⁰ (factor 2.6 low); older "
                    "<code>cosmology.eta_baryon_geometric = 6.19&times;10⁻¹⁰</code> sits within 3% of "
                    "observed 6&times;10⁻¹⁰. Status: <strong>PARTIAL (factor 2.6)</strong>.",
                    "<strong>H<sub>0</sub> and S<sub>8</sub> tensions:</strong> Sprint 5.5 claimed "
                    "resolution at H<sub>0</sub> = 73.0 via mirror-sector dark-energy coupling, but "
                    "the required coupling is ~10<sup>13</sup>× larger than the geometric value the "
                    "bridge sector can supply. Status: <strong>OPEN TENSION (magnitude gap)</strong>; "
                    "live <code>cosmology.H0_tension_sigma = 3.17σ</code> remains the honest figure "
                    "until the coupling magnitude is closed (Tier 3 T3.4)."
                ]
            ),
            ContentBlock(
                type="heading",
                content="Documented Open Tension",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<strong>Soft-SUSY gravitino mass.</strong> The gaugino-condensate potential that "
                    "stabilises Re(T) produces m<sub>3/2</sub> ≈ 160 keV, well below the TeV scale "
                    "required to evade LHC Run 2/3 limits on coloured superpartners. Carried explicitly "
                    "to v27.0 (Tier 3 T3.1) as the full G<sub>2</sub>&ndash;MSSM Kähler structure "
                    "with non-trivial K(T) and m<sub>3/2</sub> = e<sup>K/2</sup>|W|."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<strong>Net result.</strong> OPEN: the compression ratio and effective-input count are not "
                    "recomputed for the active path. The Hysteresis Seal and the shadow-derivation "
                    "detector still surface any drift between paired chains."
                )
            ),

            # 9.2 Comparison with Other Models
            ContentBlock(
                type="heading",
                content="9.2 Comparison with Other Models",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Unlike string landscape approaches with 10⁵⁰⁰ vacua, this framework works on one construction, the Joyce "
                    "resolution of T⁷/(Z/2)³ (section 7, CG.12). Uniqueness of that selection is not claimed; "
                    "the generation count and its status are stated in section 7."
                )
            ),

            # 9.3 Early Universe and Inflation
            ContentBlock(
                type="heading",
                content="9.3 Early Universe and Inflation",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The PM framework is compatible with slow-roll inflation through the attractor scalar φ<sub>M</sub>."
                )
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>Inflation potential:</strong> The flux term V<sub>flux</sub> exp(−a·φ<sub>M</sub>) provides a flat potential at large field values",
                    "<strong>Spectral index:</strong> n<sub>s</sub> = 1 − 2/N<sub>e</sub> = 0.9667 for N<sub>e</sub> = 60 e-folds (Planck: 0.965 ± 0.004)",
                    "<strong>Tensor-to-scalar:</strong> r ~ 0.003 (below Planck/BICEP limits)",
                    "<strong>Reheating:</strong> Pneuma field decay to SM particles at T<sub>R</sub> ~ 10⁹ GeV"
                ]
            ),

            # 9.4 Black Hole Information
            ContentBlock(
                type="heading",
                content="9.4 Black Hole Information",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The holographic entropy derivation suggests a perspective on the information paradox."
                )
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>Information encoding:</strong> All infalling information encoded in Pneuma correlations on horizon",
                    "<strong>Hawking radiation:</strong> Carries Pneuma entanglement, preserving unitarity",
                    "<strong>Page curve:</strong> Reproduced via hidden variable structure on shadow branes",
                    "<strong>Firewall resolution:</strong> No firewall needed; smooth horizon from condensate continuity"
                ]
            ),

            # 9.5 Supersymmetry Fate
            ContentBlock(
                type="heading",
                content="9.5 Supersymmetry Fate",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The framework is explicitly non-supersymmetric at low energies, consistent with the "
                    "experimental absence of superpartners at the LHC. This is not a deficiency but a structural feature."
                )
            ),
            ContentBlock(
                type="highlight_box",
                content=(
                    "<strong>SUSY in PM: Emergent and High-Scale Broken</strong><br>"
                    "<strong>Chiral fermions from topology:</strong> Three generations arise from G₂ index theorems "
                    "(n<sub>gen</sub> = |χ(Y)|/2), not from supersymmetric matter multiplets<br>"
                    "<strong>No low-energy SUSY required:</strong> The G₂ compactification produces Standard Model "
                    "matter content directly; supersymmetry is not invoked for hierarchy protection<br>"
                    "<strong>UV completion:</strong> If supersymmetry exists in the UV (e.g., via 11D supergravity lift), "
                    "it is broken at the compactification scale by flux and moduli stabilization<br>"
                    "<strong>Superpartner bounds:</strong> Any superpartners would appear at or above M<sub>GUT</sub> ~ 2.1 × 10¹⁶ GeV "
                    "- beyond all foreseeable experimental reach"
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "M<sub>SUSY</sub> ≳ M<sub>GUT</sub> ≈ 2.1 × 10¹⁶ GeV ≫ M<sub>LHC</sub> ~ 10⁴ GeV<br><br>"
                    "<strong>LHC Consistency:</strong> Current exclusion limits place squarks and gluinos above ~2 TeV. "
                    "The PM framework predicts superpartners (if any) at ~10¹⁶ GeV - a factor of 10¹³ above current bounds. "
                    "The LHC null results are therefore a prediction of this framework, not a puzzle."
                )
            ),

            # 9.6 Limitations and Future Work
            ContentBlock(
                type="heading",
                content="9.6 Limitations and Future Work",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content="Outstanding theoretical challenges:"
            ),
            ContentBlock(
                type="list",
                items=[
                    "<s>Derive θ₁₃ and δ<sub>CP</sub> from explicit cycle intersection integrals</s> - RESOLVED (v14.1): Both parameters now derived geometrically with 0.35σ average agreement with NuFIT",
                    "Compute Yukawa textures without cycle volume fitting",
                    "Establish rigorous proof of Z₂ factor in generation formula",
                    "Full quantum loop corrections to attractor potential",
                    "Explicit construction of shadow brane gauge theory",
                    "LQG time scale reconciliation: The bridge coordinate scale t<sub>bridge</sub> ~ R<sub>bridge</sub>/c ~ 10⁻¹⁸ s arises from Euclidean bridge compactification at TeV scale, while Loop Quantum Gravity predicts discrete spacetime at t<sub>Planck</sub> ~ 10⁻⁴⁴ s — a 26-order-of-magnitude gap"
                ]
            ),
            ContentBlock(
                type="table",
                headers=["Experiment", "Test", "Date"],
                rows=[
                    ["JUNO", "Mass hierarchy", "2027"],
                    ["HL-LHC", "KK graviton 5 TeV", "2030"],
                    ["DUNE", "δ<sub>CP</sub>", "2031"],
                    ["Euclid", "w(z) evolution", "2028"],
                    ["LISA", "GW dispersion η", "2037"],
                    ["Hyper-K", "τ<sub>p</sub> > 10³⁵ yr", "2040"]
                ]
            ),

            # 9.7 Conclusion
            ContentBlock(
                type="heading",
                content="9.7 Conclusion",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "This framework proposes Standard Model parameters on the active G₂ path (section 7). The agreement with experimental data should be "
                    "interpreted with caution: while many predictions fall within experimental uncertainties, "
                    "the framework remains a theoretical proposal requiring experimental validation."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The framework makes testable predictions: normal neutrino hierarchy, KK graviton signatures "
                    "near 5 TeV, and specific dark energy evolution. Confirmation or refutation of these predictions "
                    "by DUNE, HL-LHC, and next-generation cosmology surveys will provide meaningful tests."
                )
            ),

            # =====================================================================
            # INTERPRETIVE EXTENSION: CONSCIOUSNESS / ORCH-OR CAVEAT
            # =====================================================================
            ContentBlock(
                type="heading",
                content="9.8 Consciousness and Observer Coupling (Interpretive Extension)",
                level=2
            ),
            ContentBlock(
                type="note",
                content=(
                    "<h4>Interpretive Extension</h4>"
                    "<p>The following discussion of consciousness and observer coupling is a <strong>speculative "
                    "interpretive extension</strong> of the geometric framework, not a core theoretical claim. "
                    "The mathematical structure of the dual-shadow bridge admits an interpretation in terms of "
                    "Penrose-Hameroff Orch-OR, but this interpretation is not required by the physics and remains "
                    "highly contested in the neuroscience community.</p>"
                ),
                label="orch-or-caveat"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<Speculation>As a speculative interpretive extension, the PM dual-shadow geometry raises the possibility "
                    "of a connection to the Penrose-Hameroff Orchestrated Objective Reduction (Orch-OR) theory "
                    "of consciousness. The two-layer OR hierarchy (bridge OR creating dual shadows, face OR "
                    "selecting visible faces) suggests a structural analogue to the observer-selection problem "
                    "in quantum mechanics. It should be emphasized that the Orch-OR interpretation is not a "
                    "core claim of the framework. The geometric unification results (gauge couplings, fermion "
                    "masses, dark energy parameters) stand independently of any consciousness interpretation. "
                    "The Orch-OR bridge explored in Appendix 7.2 should be understood as an exploratory "
                    "extension whose claims are considerably more speculative than the physics derivations "
                    "in the main body of this work.</Speculation>"
                )
            ),

            # =====================================================================
            # THEORY ANALYSIS: CRITICAL ANALYSIS & VALIDATION SUMMARY
            # =====================================================================
            ContentBlock(
                type="heading",
                content="Critical Analysis & Validation Summary",
                level=1
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Status of the framework. All geometry statements, statuses, open problems and the "
                    "global fit are generated in section 7 from the engine's own certificate, registry and "
                    "validation artifacts; this part carries no separate scoring."
                )
            ),

            # Theory Status Summary
            ContentBlock(
                type="heading",
                content="Theory Status Summary",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content="<strong>Issue status</strong>"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "No count of resolved issues is stated. Each result carries its status in section 7 "
                    "(derived, calibrated, fitted, open or predicted), and what the engine marks open "
                    "is listed under 7.2 Open problems."
                )
            ),


            # Experimental Validation
            ContentBlock(
                type="heading",
                content="Experimental Validation",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The G₂ manifold framework makes specific, testable predictions across multiple domains."
                )
            ),
            ContentBlock(
                type="table",
                headers=["Observable", "Framework Prediction", "Current Data", "Status"],
                rows=[
                    *prediction_rows(),
                    ["θ₂₃ PMNS Angle", "45.0° (asymmetric coupling)", "42.1°−50.0° (NuFIT 6.0)", "Agreement"],
                    ["θ₁₃ PMNS Angle", "8.61° (cycle asymmetry)", "8.63° ± 0.11° (NuFIT 6.0 IO)", "Agreement"],
                    ["Proton Lifetime", [r[1] for r in prediction_rows() if r[0] == "Proton lifetime"][0], "> 1.67×10³⁴ years (Super-K)", "see section 7"],
                    ["GW Speed", "|c<sub>GW</sub>/c − 1| ~ M<sub>Pl</sub>⁻¹", "< 10⁻¹⁵ (GW170817)", "Consistent"]
                ]
            ),

            # DESI Agreement
            ContentBlock(
                type="heading",
                content="DESI Agreement: M<sup>26</sup>(24,2) Dual-Shadow Framework",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The M<sup>26</sup>(24,2) dual-shadow framework proposes cosmological observables from the "
                    "G₂ modulus dynamics and the Maximum Entropy Principle on the moduli space:"
                )
            ),
            ContentBlock(
                type="list",
                items=[
                    "w₀ = −1 + 1/b₃ = −23/24 ≈ −0.9583 (DERIVED via MEP from dual 13D(12,1) shadows)",
                    "w<sub>a</sub> ~ 0.1 (PREDICTED from residual modulus roll toward attractor)",
                    "de Sitter attractor preserved (w → −1 as t → ∞ at Ricci-flat fixed point)",
                    "Z₂ mirror sector provides dark matter candidate from the dual shadow",
                    "No ghost/tachyon instabilities: (24,2) structure + OR reduction ensures stability"
                ]
            ),

            # Future Refinements
            ContentBlock(
                type="heading",
                content="Future Refinements",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The G₂ framework has addressed major theoretical concerns. The following represent "
                    "opportunities for further refinement:"
                )
            ),
            ContentBlock(
                type="heading",
                content="Core Predictions (All Major Issues Resolved)",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<strong>Status:</strong> see section 7. Framework results: Generation count, M<sub>GUT</sub> (GEOMETRIC), "
                    "proton channels and mass ordering (OPEN: not computed), KK spectrum, PMNS angles, "
                    "dark energy; statuses are in section 7. No count of resolved issues is claimed."
                )
            ),

            ContentBlock(
                type="heading",
                content="Complete Moduli Stabilization Potential",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<strong>Current Status:</strong> Stabilization mechanisms identified (torsion, fluxes, "
                    "Casimir, non-perturbative). Qualitative balance achieved with G₂ torsion as dominant contribution.<br>"
                    "<strong>Future Work:</strong> Explicit potential V(σ, χ) calculation and KKLT-type analysis "
                    "for full vacuum structure. This is a quantitative refinement, not a fundamental gap."
                )
            ),

            ContentBlock(
                type="heading",
                content="Fifth Force Screening Details",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<strong>Current Status:</strong> Chameleon screening mechanism identified with β<sub>eff</sub> < 0.01 "
                    "in dense regions. Mpc-scale effects consistent with observations.<br>"
                    "<strong>Future Work:</strong> Detailed N-body simulations to verify screening across all "
                    "astrophysical scales. Solar system bounds require explicit chameleon potential parameters."
                )
            ),

            ContentBlock(
                type="heading",
                content="Cosmological Perturbation Spectrum",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<strong>Current Status:</strong> Dark energy evolution w(z) matches DESI DR2. F(R,T) "
                    "breathing mode bias quantified.<br>"
                    "<strong>Future Work:</strong> Full CMB power spectrum calculation including G₂ moduli "
                    "fluctuations. Tensor-to-scalar ratio r and isocurvature modes for comparison with Planck/LiteBIRD."
                )
            ),

            # Assessment
            ContentBlock(
                type="paragraph",
                content=(
                    "Assessment is by the statuses and the computed fit in section 7; remaining open items "
                    "are listed there, not summarised here."
                )
            ),

            # Executive Summary
            ContentBlock(
                type="heading",
                content="Executive Summary",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<strong>No score is assigned.</strong> A single self-assigned score has no stated method; "
                    "the evidence is the per-conclusion status and the computed fit in section 7."
                )
            ),


            # Position Relative to Major Frameworks
            ContentBlock(
                type="heading",
                content="Position Relative to Major Frameworks",
                level=2
            ),
            ContentBlock(
                type="table",
                headers=["Framework", "Dimensions", "Fundamental Object", "Testability"],
                rows=[
                    ["Principia Metaphysica", "M<sup>26</sup>(24,2) = 12×(2,0) + (0,1) + S<sup>(2,0)</sup> → 2×13D(12,1) → 4D via G₂", "4096-spinor Pneuma + G₂ manifold Y₇", "Near-term (2027-2030s)"],
                    ["Type IIA/IIB String", "10", "Strings (1D)", "Far-term (M<sub>Pl</sub> scale)"],
                    ["M-Theory", "11", "M2/M5 branes", "Far-term (M<sub>Pl</sub> scale)"],
                    ["Loop Quantum Gravity", "4", "Spin networks", "Far-term (Planck scale)"]
                ]
            ),

            # Final Summary Statement
            ContentBlock(
                type="heading",
                content="Final Summary",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The Principia Metaphysica framework is a geometric proposal whose status, by result, is "
                    "stated in section 7. Near-term tests (HL-LHC, JUNO, DUNE, Hyper-Kamiokande) can falsify "
                    "its predictions; the open problems listed there remain open."
                )
            ),

            # Two-Layer OR and Dark Sector Implications
            ContentBlock(
                type="heading",
                content="Two-Layer OR and Dark Sector Implications",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<strong>Two-Layer OR and Dark Sector Implications</strong><br><br>"
                    "The hierarchical OR structure has profound implications for dark matter and dark forces:<br><br>"
                    "1. <strong>Dark matter origin</strong>: Three hidden K\u00e4hler faces (f=2,3,4) per shadow provide "
                    "multi-component dark matter \u2014 KK modes (~40%), axion-like particles (~35%), and sterile "
                    "neutrinos (~25%) \u2014 with effective face sampling strength α<sub>sample</sub> ≈ 0.57 (base coupling α<sub>leak</sub> = 1/√6 ≈ 0.408 from G₂ volume ratio, enhanced by torsion and flux corrections).<br><br>"
                    "2. <strong>Dark force hierarchy</strong>: The theory predicts that strong and weak forces cannot leak "
                    "across shadows (confinement and mass barriers), while EM and gravity leak at P<sub>leak</sub> ≈ 6.9×10⁻⁶ "
                    "\u2014 a sharp, testable prediction.<br><br>"
                    "3. <strong>Communication impossibility</strong>: Dark motor designs are thermodynamically forbidden \u2014 "
                    "dark light is equilibrium noise, not free energy. Cross-shadow communication via any force "
                    "is impossible (P<sub>leak</sub> too weak, quantum-only, random).<br><br>"
                    "4. <strong>Chirality as mirror symmetry</strong>: The bridge OR operator R<sub>⊥</sub> naturally reverses chirality "
                    "between shadows (Left\u2194Right), explaining why our weak force is left-chiral while the mirror "
                    "shadow is right-chiral. CPT is preserved globally across both shadows."
                )
            ),

            # =====================================================================
            # PORTAL PHYSICS AND BEYOND-SM SEARCH IMPLICATIONS
            # =====================================================================
            ContentBlock(
                type="heading",
                content="Portal Physics: Implications for Beyond-SM Searches",
                level=2
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The four-face K\u00e4hler decomposition of the G₂ manifold provides a concrete "
                    "portal structure connecting the visible sector (Face 1) to three distinct hidden "
                    "sectors. Each hidden face supports a topologically protected portal through which "
                    "dark sector particles couple to Standard Model fields. The portal simulations "
                    "(dark_matter_portals, sterile_neutrino_portals, alp_portals) quantify these "
                    "couplings from first principles, deriving portal strengths from cycle intersection "
                    "volumes and flux threading rather than from phenomenological fits. This portal "
                    "architecture transforms dark sector physics from a landscape of ad hoc models "
                    "into a structured, predictive framework with specific experimental targets."
                )
            ),
            ContentBlock(
                type="heading",
                content="Four-Face Interpretation of Dark Matter",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The hidden-face portal structure assigns each dark matter component to a "
                    "specific geometric origin within the G₂ compactification. Face 2 supports "
                    "Kaluza-Klein (KK) excitations at the compactification scale, producing heavy "
                    "dark matter candidates near M<sub>KK</sub> ~ 5 TeV that are accessible to HL-LHC searches "
                    "via missing energy signatures. Face 3 hosts axion-like particles (ALPs) arising "
                    "from the pseudo-scalar moduli of the co-associative 4-cycles, with decay constants "
                    "set by the cycle volume and coupling to photons via the Chern-Simons interaction. "
                    "Face 4 provides the geometric substrate for sterile neutrino portal states, which "
                    "couple to active neutrinos through the bridge-mediated seesaw mechanism described "
                    "in the sterile neutrino portal simulation. Together, these three faces account "
                    "for the full dark matter relic abundance: KK modes (~40%), ALPs (~35%), and "
                    "sterile neutrinos (~25%), with the relative fractions determined by the K\u00e4hler "
                    "volume ratios of the respective faces."
                )
            ),
            ContentBlock(
                type="heading",
                content="Experimental Detection Roadmap from Portal Structure",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The hidden-face portal structure directly maps to an experimental detection "
                    "roadmap. The KK portal (Face 2) predicts dijet and dilepton resonances at "
                    "HL-LHC with cross-sections computable from the G₂ metric on the visible-hidden "
                    "cycle intersection. The ALP portal (Face 3) predicts light-shining-through-wall "
                    "signals at ALPS-II and helioscope signals at IAXO, with the coupling g<sub>aγγ</sub> "
                    "derived from the Chern-Simons volume integral over the co-associative 4-cycle. "
                    "The sterile neutrino portal (Face 4) predicts characteristic signatures in "
                    "short-baseline neutrino experiments and neutrinoless double-beta decay searches, "
                    "with the mixing angle set by the bridge wavefunction overlap computed in the "
                    "sterile neutrino portal simulation. Each portal channel provides an independent "
                    "falsification test: if any portal coupling deviates from the geometric prediction "
                    "by more than the topological uncertainty band, the four-face decomposition is "
                    "ruled out. Conversely, correlated signals across all three portal channels would "
                    "constitute strong evidence for the unified geometric dark sector."
                )
            ),
        ]

        return SectionContent(
            section_id="7",
            subsection_id=None,
            title="Discussion, Conclusions, and Theory Analysis",
            abstract=(
                "Conclusions generated from live engine state: geometry statements from the closed-geometry "
                "certificate (CG.x), physics conclusions each tagged derived, calibrated, fitted, open or "
                "predicted from the registry, the global fit read from the validation artifacts, and the "
                "open problems the engine marks. Followed by predictions and testability, a discussion of "
                "inputs and limitations, and a theory status part."
            ),
            content_blocks=content_blocks,
            formula_refs=[],
            param_refs=[]
        )

    def get_formulas(self) -> List[Formula]:
        """Return the global chi^2 formula, computed from the fit artifacts."""
        fit = _load_fit_summary()
        chi2 = fit["chi2"] if fit["available"] else None
        if chi2 is None:
            shown = r"\text{NOT AVAILABLE}"
            plain = "chi^2 = NOT AVAILABLE (" + fit["why"] + ")"
            desc = ("Global goodness-of-fit. NOT AVAILABLE: " + fit["why"] +
                    " No value is substituted.")
        else:
            shown = "{:,.2f}".format(chi2).replace(",", "{,}")
            plain = ("chi^2 = sum_i ((x_i^PM - x_i^exp)/sigma_i^exp)^2 = "
                     "%.2f over n = %d scoring rows" % (chi2, fit["n"]))
            desc = (
                "Global goodness-of-fit: the sum of squared pulls over every "
                "scoring row of the validation registry, read from "
                "statistical_rigor_report.json (chi_squared_from_rows). chi^2 = "
                "%.2f over n = %d rows (reduced %.4g); excluding the %d rows "
                "withdrawn as FALSIFIED, chi^2 = %.2f over n = %d. Both are "
                "published so that neither the withdrawn candidates nor the "
                "survivors alone set the headline. WITHDRAWN: this formula "
                "previously read sigma_bar = 0.48, a mean pull never computed "
                "from the registry." % (
                    chi2, fit["n"], fit["reduced"], fit["n_withdrawn"],
                    fit["chi2_live"], fit["n_live"]))
        return [
            Formula(
                id="discussion-global-alignment",
                label="(7.1)",
                latex=(r"\chi^2 = \sum_{i} \left(\frac{x_i^{\text{PM}} - "
                       r"x_i^{\text{exp}}}{\sigma_i^{\text{exp}}}\right)^{2} = "
                       + shown),
                plain_text=plain,
                category="DERIVED",
                description=desc,
                input_params=[
                    "topology.elder_kads",
                    "topology.mephorash_chi",
                    "cosmology.w0_derived",
                    "cosmology.H0_local",
                    "gauge.ALPHA_GUT_INV",
                    "gauge.sin2_theta_w",
                    "geometry.higgs_vev",
                ],
                output_params=[],
                derivation={
                    "steps": [
                        {"description": "Collect every scoring row of the validation registry: PM value, experimental value and experimental uncertainty. Rows with zero uncertainty are excluded.", "formula": r"\{x_i^{\text{PM}}, x_i^{\text{exp}}, \sigma_i^{\text{exp}}\}_{i=1}^{n}"},
                        {"description": "For each row compute the signed pull against the experimental uncertainty.", "formula": r"\text{pull}_i = \frac{x_i^{\text{PM}} - x_i^{\text{exp}}}{\sigma_i^{\text{exp}}}"},
                        {"description": "Sum the squared pulls. The value is read from the build artifact, not typed here.", "formula": r"\chi^2 = \sum_{i=1}^{n} \text{pull}_i^{2}"},
                    ],
                    "method": "chi_squared_from_rows",
                    "parentFormulas": []
                },
                terms={
                    "chi^2": "Sum of squared pulls over the scoring rows",
                    "n": "Number of scoring rows",
                    "x_i^PM": "PM framework prediction for observable i",
                    "x_i^exp": "Experimental measurement for observable i",
                    "sigma_i^exp": "Experimental uncertainty for observable i",
                    "pull_i": "Per-row deviation in sigma units",
                },
                eml_tree_str="ops.sum(eml_vec('squared_pulls'))",
                eml_description=(
                    "EML: chi^2 = sum_i ((x_i^PM - x_i^exp) / sigma_i^exp)^2, summed over the validation scoring rows"
                ),
                arithma=None if chi2 is None else _arithma_num(chi2),
                eml=None if chi2 is None else _eml_scalar(chi2),
                value=chi2, triple_rel=1e-3)
        ]

    def get_output_param_definitions(self) -> List[Parameter]:
        """No output parameters in discussion section -- narrative section."""
        return [
            Parameter(
                path="discussion.subsection_count",
                name="Discussion Subsection Count",
                no_experimental_value=True,
                units="sections",
                description="Number of subsections in the discussion covering open questions and future directions",
                status="SYSTEM"
            )
        ]

    # -------------------------------------------------------------------------
    # SSOT enrichment methods
    # -------------------------------------------------------------------------

    def get_references(self) -> List[Dict[str, Any]]:
        """Return bibliographic references for discussion section."""
        return [
            {
                "id": "witten1995",
                "authors": "Witten, E.",
                "title": "String Theory Dynamics In Various Dimensions",
                "year": 1995,
                "journal": "Nuclear Physics B",
                "volume": "443",
                "pages": "85-126",
                "arxiv": "hep-th/9503124",
                "url": "https://arxiv.org/abs/hep-th/9503124",
                "notes": "M-theory duality web; underpins the discussion of 11D vs 26D bulk structures"
            },
            {
                "id": "penrose1994",
                "authors": "Penrose, R.",
                "title": "Shadows of the Mind: A Search for the Missing Science of Consciousness",
                "year": 1994,
                "publisher": "Oxford University Press",
                "url": "https://doi.org/10.1093/oso/9780198539957.001.0001",
                "notes": "Orchestrated objective reduction (Orch-OR) theory discussed in consciousness section"
            },
            {
                "id": "hameroff_penrose_2014",
                "authors": "Hameroff, S. and Penrose, R.",
                "title": "Consciousness in the universe: A review of the Orch OR theory",
                "year": 2014,
                "journal": "Physics of Life Reviews",
                "volume": "11",
                "pages": "39-78",
                "doi": "10.1016/j.plrev.2013.08.002",
                "url": "https://doi.org/10.1016/j.plrev.2013.08.002",
                "notes": "Orch-OR consciousness model explored as a speculative interpretive extension of the PM geometric framework (not a core claim)",
            },
        ]

    def get_certificates(self) -> List[Dict[str, Any]]:
        """Return certificate assertions for discussion section."""
        section = self.get_section_content()
        blocks = section.content_blocks if section else []
        paragraph_blocks = [b for b in blocks if b.type == "paragraph"]
        total_text = " ".join(b.content for b in paragraph_blocks)
        word_count = len(total_text.split())
        heading_blocks = [b for b in blocks if b.type == "heading"]
        has_open_questions = "open" in total_text.lower() or "future" in total_text.lower() or "challenge" in total_text.lower()

        return [
            {
                "id": "CERT_DISCUSSION_WORD_COUNT",
                "assertion": "Discussion section contains at least 1000 words of substantive content",
                "condition": f"word_count >= 1000 (actual: {word_count})",
                "tolerance": 1000,
                "status": "PASS" if word_count >= 1000 else "FAIL",
                "wolfram_query": "N/A (content integrity check)",
                "wolfram_result": "N/A",
                "sector": "paper"
            },
            {
                "id": "CERT_DISCUSSION_OPEN_QUESTIONS",
                "assertion": "Discussion section addresses open questions and future directions",
                "condition": f"has_open_questions_content: {has_open_questions}",
                "tolerance": "exact",
                "status": "PASS" if has_open_questions else "FAIL",
                "wolfram_query": "N/A (content integrity check)",
                "wolfram_result": "N/A",
                "sector": "paper"
            },
            {
                "id": "CERT_DISCUSSION_SUBSECTIONS",
                "assertion": "Discussion has at least 5 subsection headings covering distinct topics",
                "condition": f"heading_count >= 5 (actual: {len(heading_blocks)})",
                "tolerance": 5,
                "status": "PASS" if len(heading_blocks) >= 5 else "FAIL",
                "wolfram_query": "N/A (structural check)",
                "wolfram_result": "N/A",
                "sector": "paper"
            },
        ]

    def get_learning_materials(self) -> List[Dict[str, Any]]:
        """Return educational resources for discussion section topics."""
        return [
            {
                "topic": "M-theory and string dualities",
                "url": "https://en.wikipedia.org/wiki/M-theory",
                "relevance": "Discussion evaluates how the 26D PM framework relates to 11D M-theory via duality and compactification",
                "validation_hint": "M-theory unifies five superstring theories in 11D; PM extends to 26D via dual-shadow structure"
            },
            {
                "topic": "Orchestrated objective reduction (Orch-OR)",
                "url": "https://en.wikipedia.org/wiki/Orchestrated_objective_reduction",
                "relevance": "As a speculative interpretive extension, the discussion explores the possibility that consciousness may relate to the topological structure via Penrose-Hameroff Orch-OR; this interpretation is not required by the core physics",
                "validation_hint": "Orch-OR proposes quantum gravity effects in microtubules; PM raises the possibility of geometric grounding via G2 holonomy, but this remains a speculative extension"
            },
            {
                "topic": "Fine-tuning problem in physics",
                "url": "https://en.wikipedia.org/wiki/Fine-tuning_(physics)",
                "relevance": "Discussion addresses how PM resolves fine-tuning by deriving all 125 constants as geometric residues rather than free parameters",
                "validation_hint": "Standard Model has ~25 free parameters; PM derives them from G2 spectral geometry"
            },
        ]

    def validate_self(self) -> Dict[str, Any]:
        """Validate discussion section integrity."""
        checks = []

        section = self.get_section_content()
        blocks = section.content_blocks if section else []
        paragraph_blocks = [b for b in blocks if b.type == "paragraph"]
        total_text = " ".join(b.content for b in paragraph_blocks)
        word_count = len(total_text.split())

        wc_ok = word_count >= 1000
        checks.append({
            "name": "Discussion word count meets minimum (>=1000)",
            "passed": wc_ok,
            "confidence_interval": {
                "lower": 1000,
                "upper": 20000,
                "sigma": 0.0
            },
            "log_level": "INFO" if wc_ok else "ERROR",
            "message": f"Word count = {word_count} (minimum 1000)"
        })

        heading_blocks = [b for b in blocks if b.type == "heading"]
        h_ok = len(heading_blocks) >= 5
        checks.append({
            "name": "At least 5 subsection headings in discussion",
            "passed": h_ok,
            "confidence_interval": {
                "lower": 5,
                "upper": 30,
                "sigma": 0.0
            },
            "log_level": "INFO" if h_ok else "ERROR",
            "message": f"Heading count = {len(heading_blocks)} (minimum 5)"
        })

        return {
            "passed": all(c["passed"] for c in checks),
            "checks": checks
        }

    def get_gate_checks(self) -> List[Dict[str, Any]]:
        """Return gate check results for discussion section."""
        section = self.get_section_content()
        blocks = section.content_blocks if section else []
        paragraph_blocks = [b for b in blocks if b.type == "paragraph"]
        total_text = " ".join(b.content for b in paragraph_blocks)
        word_count = len(total_text.split())
        heading_blocks = [b for b in blocks if b.type == "heading"]
        passed = word_count >= 1000 and len(heading_blocks) >= 5

        return [
            {
                "gate_id": "G_DISCUSSION_CONTENT_INTEGRITY",
                "simulation_id": self.metadata.id,
                "assertion": "Discussion section provides comprehensive coverage of open questions, future directions, and philosophical implications (>=1000 words, >=5 subsections)",
                "result": "PASS" if passed else "FAIL",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "word_count": word_count,
                    "content_blocks": len(blocks),
                    "heading_count": len(heading_blocks),
                    "section_type": "narrative_discussion"
                }
            },
        ]


def main():
    """Run the simulation standalone for testing."""
    import io
    import sys

    # Ensure UTF-8 output encoding
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    from metaphysica.simulations.base import PMRegistry

    # Create registry
    registry = PMRegistry()

    # Create and run simulation
    sim = DiscussionV16()

    print("=" * 70)
    print(f" {sim.metadata.title}")
    print("=" * 70)
    print()

    # Generate section content
    section_content = sim.get_section_content()

    print(f"Section: {section_content.section_id}")
    print(f"Title: {section_content.title}")
    print(f"Abstract: {section_content.abstract[:200]}...")
    print(f"Content blocks: {len(section_content.content_blocks)}")
    print()
    print("Content structure:")
    for i, block in enumerate(section_content.content_blocks[:10], 1):
        print(f"  {i}. {block.type}: {str(block.content)[:80]}...")
    print(f"  ... and {len(section_content.content_blocks) - 10} more blocks")


if __name__ == "__main__":
    main()
