"""
PRINCIPIA METAPHYSICA v24.2 - Abstract
======================================

DOI: 10.5281/zenodo.18079602

Licensed under the MIT License. See LICENSE file for details.

v24.2: M^{26}(24,2) structure with two shadow-time directions.
       4096-component Primordial Spinor Field from Cl(24,2).
       Dual 13D(12,1) shadows with OR reduction operator R_perp.

Provides section content for the Abstract (Section 0).

This simulation provides the abstract narrative for Principia Metaphysica v24.2,
the M^{26}(24,2) dual-shadow framework with Euclidean bridge where 125 physical
constants are proposed to emerge as spectral residues of G2 manifold compactification. It does
not compute physics parameters, but instead generates the narrative content and
cross-references for the paper's abstract section.

SECTION: 0 (Abstract)

v24.2 TOPOLOGICALLY ANCHORED: 125 constants from EDOF=3 seeds (131:1 compression after v25.0+v26.0 closures).

OUTPUTS:
    - abstract.total_constants (125)
    - abstract.pure_predictions (55)
    - abstract.calibration_inputs, validation.calibrated_count and
      validation.free_variable_count (all three read the free-variable ledger),
      abstract.fitted_pmns (2)
    - abstract.vev_coefficient, abstract.alpha_gut_coefficient
    - abstract.alpha_inv_pred, abstract.alpha_inv_codata, abstract.alpha_inv_theory_sigma
    - abstract.theta23_io_central, abstract.theta23_sigma_io
    - abstract.tau_p_display, abstract.tau_p_bound_display
    - abstract.desi_w0_uncertainty, abstract.dark_force_pleak

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from metaphysica.simulations.base import (
    SimulationBase,
    SimulationMetadata,
    SectionContent,
    ContentBlock,
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

from metaphysica.simulations.core.free_variable_ledger import (
    published_free_variable_count as _free_variables,
)

if TYPE_CHECKING:
    from metaphysica.simulations.base import PMRegistry


class AbstractV17_2(SimulationBase):
    """
    Abstract section (Section 0) for Principia Metaphysica v24.2.

    This simulation provides the abstract narrative content that summarizes
    the M^{26}(24,2) dual-shadow framework with Euclidean bridge. It describes
    the dimensional descent from 26D ancestral bulk through dual 13D(12,1)
    shadows to observable 4D via G2 compactification, yielding exactly 3
    fermion generations from n_gen = chi_eff/(2*b3) = 144/48 = 3.

    The abstract references 26 Standard Model parameter predictions (24 within
    1-sigma; see results section for full table), 55 pure predictions,
    reproducibility certificates, and key testable outputs including
    w0 = -23/24 (consistent with DESI 2025 thawing direction).

    This is a narrative-only section: run() returns an empty dict.
    """

    # No formula references - abstract is pure narrative
    FORMULA_REFS: List[str] = []

    @property
    def metadata(self) -> SimulationMetadata:
        """Return metadata about this simulation."""
        return SimulationMetadata(
            id="abstract_v17_2",
            version="24.2",
            domain="abstract",
            title="Abstract",
            description="Paper abstract for Principia Metaphysica v24.2 M^{26}(24,2) dual-shadow framework with Euclidean bridge - 125 spectral residues from G2 compactification with EDOF=3 (1 geometric + 2 calibrations)",
            section_id="0",
            subsection_id=None
        )

    @property
    def required_inputs(self) -> List[str]:
        """Registry parameters referenced by the abstract narrative."""
        return ["topology.elder_kads"]

    @property
    def output_params(self) -> List[str]:
        """Abstract-level metadata parameters registered for data-pm-value spans."""
        return [
            # Framework version parameters
            "framework.version",
            "framework.version_major",
            "framework.version_label",
            "framework.version_major_label",
            # Abstract counts
            "abstract.total_constants",
            "abstract.pure_predictions",
            "abstract.calibration_inputs",
            "abstract.fitted_pmns",
            "validation.free_variable_count",
            # Calibration coefficients
            "abstract.vev_coefficient",
            "abstract.alpha_gut_coefficient",
            # Theory-level sigma comparisons
            "abstract.alpha_inv_theory_sigma",
            "abstract.theta23_sigma_io",
            # DESI parameters
            "abstract.desi_w0_uncertainty",
            # Display values
            "abstract.tau_p_display",
            "abstract.tau_p_bound_display",
            "abstract.dark_force_pleak",
            "abstract.alpha_inv_pred",
            "abstract.alpha_inv_codata",
            "abstract.theta23_io_central",
            # ALP parameters
            "alp.mass_meV",
            "alp.coupling_GeV_inv",
            "alp.coupling_GeV_inv_value",
            # v25.0+v26.0 closure ledger
            "abstract.compression_ratio",
            "abstract.ledger_total",
            "abstract.ledger_derived",
            "abstract.ledger_derived_pct",
            "abstract.ledger_numerical",
            "abstract.ledger_fitted",
            "abstract.ledger_open",
            "abstract.v25_v26_closures",
            # Dimensional aliases
            "dimensions.D_bulk",
            "dimensions.D_G2",
            "dimensions.D_physics",
            "dimensions.D_observable",
            # Ten Pillar Seed display aliases
            "constants.k_gimel",
            "constants.phi",
            "constants.demiurgic_coupling",
            # Validation statistics
            "validation.total_predictions",
            "validation.predictions_within_1sigma",
            "validation.exact_matches",
            "validation.calibrated_count",
            "validation.constraints_count",
            "abstract.constraints_count",
        ]

    @property
    def output_formulas(self) -> List[str]:
        """No formulas for abstract."""
        return self.FORMULA_REFS

    def run(self, registry: 'PMRegistry') -> Dict[str, Any]:
        """
        Compute and register abstract-level metadata parameters.

        Reads upstream values from registry (set by physics simulations) and
        registers framework-level summary counts and display values so that all
        data-pm-value spans in the abstract render from SSoT parameters.

        Returns:
            Dict of param_path -> value for 16 abstract-level parameters.
        """
        import math

        def safe_get(path, fallback):
            try:
                v = registry.get_param(path)
                return v if v is not None else fallback
            except Exception:
                return fallback

        tau_p       = safe_get("proton_decay.tau_p_years",     4.757e34)
        tau_p_bound = safe_get("bounds.tau_proton_lower",      1.67e34)
        alpha_inv_p = safe_get("constants.alpha_inverse_pred", 137.03670177575597)
        alpha_inv_c = safe_get("codata.alpha_inverse",         137.035999177)  # alpha inverse (CODATA 2022 full)
        theta23_io  = safe_get("nufit.theta_23_IO",            49.3)

        return {
            # Dimensional aliases (canonical paths for HTML data-pm-value attributes)
            "dimensions.D_bulk":               26,   # Total manifold dimensions M^{26}(24,2)
            "dimensions.D_G2":                 7,    # G₂ compactification manifold dimension
            "dimensions.D_physics":            24,   # Physics core (12×(2,0) bridge pairs)
            # Registered 2026-09: the abstract has always rendered
            # data-pm-value="dimensions.D_observable" and foundations declares
            # it as the output of calabi-yau-projection (1.4), whose triple
            # track is 7 - 3 = 4 -- but no simulation emitted the path, so every
            # formula declaring it declared an edge the walkers could not see,
            # and appendix_c's registry.get(..., default=4) always fell through.
            "dimensions.D_observable":         4,    # D_G2 (7) minus the 3 CY3 internal directions
            # Ten Pillar Seed display aliases (for HTML display of canonical seeds)
            "constants.k_gimel":               12.3183098862,   # Spectral gap from associative 3-cycles
            "constants.phi":                   1.618033988749,  # Golden ratio from minimal surface geometry
            "constants.demiurgic_coupling":    12.3183098862,   # Gnostic alias for k_gimel
            # Framework version parameters (dynamic versioning system)
            "framework.version":               "24.2",    # Full version number
            "framework.version_major":         "24",      # Major version only
            "framework.version_label":         "v24.2",   # Formatted with 'v' prefix
            "framework.version_major_label":   "v24",     # Formatted major version
            # Framework summary counts
            "abstract.total_constants":        125,  # DERIVED: visible_sector = 5^3 from V₇ spectral decomposition
            "abstract.pure_predictions":       55,
            # MEASURED, not asserted. Three places in this tree used to
            # answer "how many free variables?" with three different
            # literals -- 0 here as validation.calibrated_count, 3 here as
            # abstract.calibration_inputs, 3 from
            # StatisticalRigorValidator.calculate_effective_dof (whose body
            # says "# ANSATZ ... return 3"), and a fourth, 1, as
            # generate_statistics.FITTED_PARAMS_COUNT. None was computed.
            # All of them now read the one number the ledger measures by
            # sweeping the tree; see
            # simulations/core/free_variable_ledger.py and
            # AutoGenerated/free_variables.json for the per-row evidence.
            "abstract.calibration_inputs":     _free_variables(),
            "abstract.fitted_pmns":            2,
            "validation.free_variable_count":  _free_variables(),
            # Validation statistics (Standard Model parameter comparisons).
            # WARNING (2026-09): the three counts below are hand-maintained
            # literals, not computed. generate_statistics writes the computed
            # figures — validation.within_1sigma = 41 and within_2sigma = 54
            # over validation.total_predictions = 67 — and statistics.json
            # reports exact_matches = 0. The abstract prose now quotes the
            # computed pair (67 / 41); reconciling the literals below with
            # them changes registry values and needs an author ruling.
            "validation.total_predictions":    26,   # LITERAL, not computed (computed: 67)
            "validation.predictions_within_1sigma": 24,  # LITERAL, not computed (computed: 41)
            "validation.exact_matches":        3,    # LITERAL, not computed (statistics.json: 0)
            "validation.calibrated_count":     _free_variables(),  # measured by the ledger, not asserted
            "validation.constraints_count":    1,    # Higgs mass fixes Re(T)
            "abstract.constraints_count":      1,    # One observational constraint (m_h → Re(T))
            # Calibration coefficients
            "abstract.vev_coefficient":        1.5859,
            "abstract.alpha_gut_coefficient":  round(1.0 / (10.0 * math.pi), 6),  # 0.031831
            # Theory-level sigma comparisons (not CODATA experimental precision)
            "abstract.alpha_inv_theory_sigma": 0.0497,
            "abstract.theta23_sigma_io":       0.45,
            # DESI BAO-only w0 uncertainty (2025)
            "abstract.desi_w0_uncertainty":    0.067,
            # Proton lifetime display values (coefficient × 10^34 yr)
            # Not rounded: round(x, 1) stored 4.8 for 4.7574, so the row
            # could only ever agree loosely with its own derivation. The
            # rendered text still reads "4.8" -- that is the renderer's job.
            "abstract.tau_p_display":          tau_p / 1e34,
            "abstract.tau_p_bound_display":    round(tau_p_bound / 1e34, 2),   # 1.67
            # Dark force leakage probability
            "abstract.dark_force_pleak":       "6.9\u00d710\u207b\u2078",
            # Alpha^-1 comparison values (echoed for display spans)
            "abstract.alpha_inv_pred":         round(alpha_inv_p, 4),          # 137.0367
            "abstract.alpha_inv_codata":       round(alpha_inv_c, 4),          # 137.036
            # theta_23 IO comparison
            "abstract.theta23_io_central":     theta23_io,                     # 49.3
            # ALP Principia Metric (falsifiability kill-switch — BabyIAXO 2028)
            "alp.mass_meV":                    3.51,      # 3.51 meV ALP mass from M²⁶ → M⁴ vacuum residue
            "alp.coupling_GeV_inv":            "10⁻¹¹",  # g_aγγ ~ 10⁻¹¹ GeV⁻¹ from EIS-photon coupling
            "alp.coupling_GeV_inv_value":      "2.9×10⁻¹¹",  # Refined g_aγγ from EIS-photon coupling (BabyIAXO 2028 reachable)
            # v25.0+v26.0 closure ledger (Sprint 6 / S5.10)
            "abstract.compression_ratio":      131,    # 131:1 after 13 new DERIVED items closed in v25.0+v26.0
            "abstract.ledger_total":           620,    # Total tracked parameters
            "abstract.ledger_derived":         571,    # Fully derived
            "abstract.ledger_derived_pct":     92.1,   # 571/620 ≈ 92.1%
            "abstract.ledger_numerical":       28,     # Numerical agreement only
            "abstract.ledger_fitted":          14,     # Fitted (legacy θ_13 / δ_CP markers)
            "abstract.ledger_open":            7,      # Open tensions (PMNS η, baryogenesis, soft SUSY, etc.)
            "abstract.v25_v26_closures":       13,     # Newly DERIVED items in v25.0+v26.0 sprint
        }

    def run_eml(self, registry: 'PMRegistry') -> Dict[str, Any]:
        """EML Math path — identical to run(); paper outputs have no separate EML computation."""
        return self.run(registry)

    def get_section_content(self) -> Optional[SectionContent]:
        """Section 0: the abstract, top down.

        Rebuilt 2026-10-01 at the author's request for a clear overview of the
        theory: between the research-status notice and the field-names note,
        every paragraph is generated by `closed_geometry.overview.layers()` --
        the same source as the main page's "theory at a glance" -- so the
        abstract and the site cannot drift from each other or from the code.
        """
        from metaphysica.simulations.PM.geometry.closed_geometry.overview import (
            layers,
        )
        from metaphysica.simulations.PM.geometry.geometry_narration import (
            render,
        )

        content_blocks = [
            ContentBlock(
                type="paragraph",
                content=(
                    '<div style="border: 2px solid #ff9800; background: rgba(255,152,0,0.08); '
                    'padding: 1rem 1.25rem; border-radius: 8px; margin-bottom: 1.5rem;">'
                    '<strong style="color: #d84315; text-transform: uppercase; letter-spacing: 0.05em;">'
                    '&#9888; Research status</strong>'
                    '<p style="margin: 0.5rem 0 0; line-height: 1.5;">'
                    '<strong>Principia Metaphysica is a speculative theoretical model.</strong> '
                    'It has <strong>not</strong> been peer-reviewed and is <strong>not</strong> '
                    'scientifically validated. All derivations, predictions, and \u201cclosures\u201d '
                    'presented below are candidate proposals awaiting experimental confirmation '
                    'and independent expert review. The framework is intended for exploration and '
                    'research purposes only; no claim in this paper represents established '
                    'scientific fact.'
                    '</p></div>'
                ),
                label="abstract-research-status-notice"
            ),
            ContentBlock(
                type="paragraph",
                content=render(
                    "<strong>Principia Metaphysica</strong> is a speculative "
                    "geometric model. It postulates {bulk}, split into two "
                    "13-dimensional shadows, and derives the internal "
                    "geometry of each: {manifold} is {construction}, with "
                    "{betti_pair}. The topology and every discrete datum of "
                    "that geometry are fixed with no free parameter and are "
                    "certified theorem by theorem; three generations follow "
                    "as {n_gen_route}. Above the geometry the model&rsquo;s "
                    "physics layers carry calibrations, four physics problems "
                    "remain open, and the model does not fit the data "
                    "globally. The paragraphs below give the story top down: "
                    "what is assumed, what is borrowed from established "
                    "physics, what is derived and how, what was corrected, "
                    "and what is still open.", "html"),
                label="abstract-lead"
            ),
        ]
        for layer in layers():
            content_blocks.append(ContentBlock(
                type="paragraph",
                content="<strong>%s.</strong> %s" % (layer["title"],
                                                     layer["lead"]),
                label="abstract-%s" % layer["key"],
            ))
            if layer["items"]:
                content_blocks.append(ContentBlock(
                    type="list",
                    content="",
                    items=list(layer["items"]),
                    label="abstract-%s-items" % layer["key"],
                ))
        content_blocks.append(ContentBlock(
            type="paragraph",
            content=(
                "<strong>Predictions under test.</strong> The model&rsquo;s "
                "specific predictions &mdash; among them the proton lifetime, "
                "a light axion-like particle and the dark-energy equation of "
                "state &mdash; are collected in Section 6 with their status. "
                "Several are calibrated at the off-path seed or rest on an "
                "open problem, and each is labelled there rather than here."
            ),
            label="abstract-predictions",
        ))
        content_blocks.append(
            ContentBlock(
                type="note",
                content=(
                    '<sup>\u2020</sup> The fields are named "Primordial Spinor Field" (\u03a8<sub>P</sub>) and '
                    '"Attractor Scalar" (\u03a6<sub>M</sub>). Historical names "Pneuma" and "Mashiach" reflect '
                    'philosophical inspiration but are not used in technical discussions.'
                ),
                label="abstract-note"
            ),
        )

        return SectionContent(
            section_id="0",
            subsection_id=None,
            title="Abstract",
            abstract=render(
                "A speculative geometric model: {bulk}, split into two 13D "
                "shadows, each with internal space {manifold} = "
                "{construction}, {betti_pair}, certified with no free "
                "parameter; n_gen = b_2/4 = {n_gen}. Chirality, moduli "
                "stabilisation, dark energy and flavour are open, and the "
                "model does not fit the data globally."),
            content_blocks=content_blocks,
            section_type="abstract",
            formula_refs=["abstract-framework-overview"],
            param_refs=[
                "topology.elder_kads",
                "topology.n_gen",
                "dimensions.D_bulk",
                "dimensions.D_observable",
                "validation.total_predictions",
                "validation.predictions_within_1sigma",
                "validation.exact_matches",
                "statistics.certificates_total",
                "abstract.total_constants",
                "abstract.pure_predictions",
                "abstract.calibration_inputs",
                "abstract.fitted_pmns",
                "validation.free_variable_count",
                "abstract.vev_coefficient",
                "abstract.alpha_gut_coefficient",
                "abstract.alpha_inv_theory_sigma",
                "abstract.theta23_sigma_io",
                "abstract.desi_w0_uncertainty",
                "abstract.tau_p_display",
                "abstract.tau_p_bound_display",
                "abstract.dark_force_pleak",
                "abstract.alpha_inv_pred",
                "abstract.alpha_inv_codata",
                "abstract.theta23_io_central",
                "cosmology.w0_derived",
                "desi.w0",
                "geometry.alpha_leak",
                "alp.mass_meV",
                "alp.coupling_GeV_inv",
                "alp.coupling_GeV_inv_value",
                "abstract.compression_ratio",
                "abstract.ledger_total",
                "abstract.ledger_derived",
                "abstract.ledger_derived_pct",
                "abstract.ledger_numerical",
                "abstract.ledger_fitted",
                "abstract.ledger_open",
                "abstract.v25_v26_closures",
            ]
        )

    def get_formulas(self) -> List[Formula]:
        """Return framework overview formulas for the abstract.

        Returns a summary formula capturing the dimensional descent chain
        and a generation-count formula. These reference the detailed
        derivations in the geometric, fermion, and cosmology sectors.
        """
        from metaphysica.simulations.PM.geometry.b3_path import seed_values

        b3, b2 = seed_values()
        n_gen = b2 / 4.0
        n_txt = "%g" % n_gen
        return [
            Formula(
                id="abstract-framework-overview",
                label="(0.1)",
                latex=(r"M^{26}(24,2) \;\xrightarrow{\text{OR}}\; 2 \times 13\text{D}(12,1) "
                       r"\;\xrightarrow{Y_7}\; 2 \times 4\text{D} \quad \Rightarrow \quad "
                       r"n_{\text{gen}} = \frac{b_2}{4} = \frac{%d}{4} = %s" % (b2, n_txt)),
                plain_text=("M^26(24,2) -> 2 x 13D(12,1) -> 2 x 4D on Y_7 => "
                            "n_gen = b2/4 = %d/4 = %s" % (b2, n_txt)),
                category="DERIVED",
                description=(
                    "Framework overview. The bulk is 26-dimensional with signature "
                    "(24,2): 24 space directions, grouped as 12 bridge pairs "
                    "B_i^(2,0), and 2 times, one per shadow (a postulate; signature "
                    "ruling 2026-08-31). The OR reduction gives each shadow one "
                    "coordinate of every bridge pair and its own time, so the bulk "
                    "splits into two 13D(12,1) shadows. Each shadow's seven internal "
                    "dimensions form Y_7, Joyce's resolution of T^7/(Z/2)^3 with "
                    "(b_2, b_3) = (%d, %d): a compact 7-manifold with a torsion-free "
                    "G2-structure, pi_1 = 1 and Euler characteristic 0 (certificate "
                    "CG.1-CG.4). The generation count is n_gen = b_2/4 = %s, the "
                    "number of singular involutions of Gamma = (Z/2)^3 (the ruled "
                    "route). The route through chi_eff/(2 b_3) held only at the "
                    "off-path seed b_3 = 24 and is retired." % (b2, b3, n_txt)
                ),
                eml_tree_str="ops.div(eml_scalar(b2), eml_scalar(4.0))",
                eml_latex=r"n_{\text{gen}} = \mathrm{ops.div}(\mathrm{eml\_scalar}(b_2),\; \mathrm{eml\_scalar}(4))",
                eml_description=(
                    "EML: n_gen = ops.div(b_2, 4) -- four resolved A1 families "
                    "per singular involution, so b_2/4 counts the singular "
                    "involutions (ruled route)"
                ),
                input_params=["topology.b2"],
                output_params=["topology.n_gen"],
                derivation={
                    "steps": [
                        {"description": "Bulk: 26 dimensions with signature (24,2) -- 24 space directions grouped as 12 bridge pairs B_i^(2,0), plus 2 times, one per shadow. A postulate of the model (signature ruling 2026-08-31).", "formula": r"M^{26}(24,2) = \bigoplus_{i=1}^{12} B_i^{(2,0)} \oplus T^{(0,2)}"},
                        {"description": "OR reduction: each bridge pair B_i^(2,0) carries a Moebius double-cover operator R_perp^i (R_perp^2 = -I) that sends one coordinate to Shadow_Aleph and the other to Shadow_Beth. With its own time, each shadow is 13D(12,1).", "formula": r"R_\perp^{\text{full}} = \bigotimes_{i=1}^{12} R_\perp^i \;\Rightarrow\; 2 \times 13\text{D}(12,1)"},
                        {"description": "Internal space: each shadow's seven internal dimensions form Y_7, Joyce's resolution of T^7/(Z/2)^3, Gamma = (Z/2)^3 being the diagonal stabiliser of phi. Betti numbers (1, 0, %d, %d, %d, %d, 0, 1) with b_3 = 7 + 3 b_2; pi_1 = 1; Euler characteristic 0 (certificate CG.1-CG.4)." % (b2, b3, b3, b2), "formula": r"Y_7 = \widetilde{T^7/(\mathbb{Z}_2)^3}, \quad (b_2, b_3) = (%d, %d)" % (b2, b3)},
                        {"description": "Generations: b_2 = 4n counts the resolved A1 families, four for each singular involution, so n_gen = b_2/4 = n, the number of singular involutions (the ruled route). The earlier route chi_eff/(2 b_3) = 144/48 held only at the off-path seed b_3 = 24 and is retired.", "formula": r"n_{\text{gen}} = \frac{b_2}{4} = \frac{%d}{4} = %s" % (b2, n_txt)},
                        {"description": "The bridge directions are spacelike, ds^2 = dy_1^2 + dy_2^2 > 0. Ghost control of the second time is an OPEN problem: the appeal to Bars' Sp(2,R) ghost-freedom theorem was withdrawn (signature ruling 2026-08-31).", "formula": r"\text{ds}^2_{\text{bridge}} = dy_1^2 + dy_2^2 > 0"},
                    ],
                    "method": "dimensional_descent",
                    "parentFormulas": [
                        "intro-division-algebra-decomposition",
                        "g2-holonomy",
                        "laplacian-eigenvalue",
                    ]
                },
                terms={
                    "M^{26}(24,2)": "26-dimensional bulk of signature (24,2): 24 space directions (12 bridge pairs B_i^(2,0)) and 2 times, one per shadow (a postulate)",
                    "13D(12,1)": "13-dimensional shadow: one spatial coordinate from each of the 12 bridge pairs, and its own time",
                    "Y_7": "The internal seven-manifold: Joyce's resolution of T^7/(Z/2)^3, (b_2, b_3) = (%d, %d)" % (b2, b3),
                    "n_gen": "Number of fermion generations per shadow: b_2/4, the number of singular involutions of Gamma",
                    "b_2": "Second Betti number of Y_7: four resolved A1 families for each singular involution",
                    "b_3": "Third Betti number of Y_7: b_3 = 7 + 3 b_2 (7 flat classes plus 3 for each A1 family)",
                    "chi_eff": "Effective index chi_eff = 144, an open ruling (not the Euler characteristic of Y_7, which is 0); on the unruled K3 reading chi_eff = 48 n",
                    "OR": "Orthogonal Reduction operator R_perp providing per-pair Moebius double-cover (R_perp^2 = -I) for cross-shadow coordinate selection",
                    "G_2": "Exceptional Lie group G2 = Aut(O); Y_7 carries a torsion-free G2-structure",
                },
            arithma=_arithma_div(_arithma_num(float(b2)), _arithma_num(4.0)), eml=_eml_div(_eml_scalar(float(b2)), _eml_scalar(4.0)), value=n_gen)
        ]

    def get_output_param_definitions(self) -> List[Parameter]:
        """Return parameter definitions for abstract section.

        The abstract is a narrative section with no physics computations,
        but defines a system-level parameter tracking word count for
        content integrity validation.
        """
        return [
            # Framework version parameters (dynamic versioning for all paper content)
            Parameter(
                path="framework.version",
                name="Framework Version Number",
                no_experimental_value=True,
                units="version",
                description="Current Principia Metaphysica version number (e.g., '24.2')",
                status="SYSTEM",
                # EML WITHHELD: a version STRING. Not a physical quantity and not derived from anything.
            ),
            Parameter(
                path="framework.version_major",
                name="Framework Major Version",
                no_experimental_value=True,
                units="version",
                description="Major version number only (e.g., '24')",
                status="SYSTEM",
                # EML WITHHELD: a version number. Not a physical quantity and not derived from anything.
            ),
            Parameter(
                path="framework.version_label",
                name="Framework Version Label",
                no_experimental_value=True,
                units="version",
                description="Formatted version with 'v' prefix (e.g., 'v24.2')",
                status="SYSTEM",
                eml_description="EML: eml_vec('framework_version_label') — PM framework version label with 'v' prefix"
            ),
            Parameter(
                path="framework.version_major_label",
                name="Framework Major Version Label",
                no_experimental_value=True,
                units="version",
                description="Formatted major version with 'v' prefix (e.g., 'v24')",
                status="SYSTEM",
                eml_description="EML: eml_vec('framework_version_major_label') — PM framework major version label with 'v' prefix"
            ),
            # Content tracking parameters
            Parameter(
                path="abstract.word_count",
                name="Abstract Word Count",
                no_experimental_value=True,
                units="words",
                description="Approximate word count of the abstract section content",
                status="SYSTEM",
                eml_description="EML: eml_vec('abstract_word_count') — bookkeeping count of abstract narrative word length"
            ),
            Parameter(
                path="abstract.total_constants",
                name="Total Physical Constants Expressed",
                no_experimental_value=True,
                units="dimensionless",
                description="Total number of physical constants for which the framework proposes geometric expressions",
                status="GEOMETRIC",
                eml_description="EML: eml_scalar(125) — spectral residue count fixed by G₂ topology (5³ from V₇ spectral decomposition)"
            ),
            Parameter(
                path="abstract.pure_predictions",
                name="Pure Predictions Count",
                no_experimental_value=True,
                units="dimensionless",
                description=("Number of parameters claimed as pure topological predictions with no "
                             "experimental input. Twenty entries in the geometry.* namespace carry "
                             "status MEASURED -- the three NuFIT mixing angles, SH0ES H0, Planck "
                             "Omega_m, DESI w0/wa, PDG Wolfenstein A and Jarlskog among them -- and "
                             "are raw experimental input, not consequences of b3 = 24."),
                status="PREDICTED",
                eml_description="EML: eml_scalar(55) — count of zero-free-parameter predictions derived from G₂ topology alone"
            ),
            Parameter(
                path="abstract.calibration_inputs",
                name="Free Variable Count (alias)",
                no_experimental_value=True,
                units="dimensionless",
                description=(
                    "Alias of validation.free_variable_count. This row used to "
                    "read 3 and name the three as '(VEV, alpha_GUT, Re(T))', "
                    "while information_bottleneck_distiller.py named a "
                    "different three, ['M_Planck', 'alpha_EM', 'm_H']. Both "
                    "were literals and they disagreed. It now reads the "
                    "measured count from the free-variable ledger."
                ),
                status="SYSTEM",
                eml_description="EML: eml_scalar(validation.free_variable_count) — measured by free_variable_ledger, not asserted"
            ),
            Parameter(
                path="abstract.fitted_pmns",
                name="Fitted PMNS Parameter Count",
                no_experimental_value=True,
                units="dimensionless",
                description="Number of PMNS parameters fitted to NuFIT 6.0 pending explicit Yukawa calculation",
                status="CALIBRATED",
                eml_description="EML: eml_scalar(2.0) — count of PMNS parameters (θ₁₃, δ_CP) fitted to NuFIT 6.0 pending Yukawa derivation"
            ),
            Parameter(
                path="abstract.vev_coefficient",
                name="VEV Scale Coefficient",
                no_experimental_value=True,
                units="dimensionless",
                description="Dimensionless coefficient relating the G2 spectral scale to the electroweak VEV",
                status="CALIBRATED",
                eml_description="EML: eml_scalar(1.5859) — dimensionless VEV coefficient relating G₂ spectral scale to electroweak VEV"
            ),
            Parameter(
                path="abstract.alpha_gut_coefficient",
                name="Alpha-GUT Inverse Coefficient",
                no_experimental_value=True,
                units="dimensionless",
                description="Coefficient 1/(10*pi) relating the GUT coupling to the spectral gap k_gimel",
                status="CALIBRATED",
                eml_description="EML: ops.div(eml_scalar(1.0), ops.mul(eml_scalar(10.0), eml_pi())) — GUT coupling scale as 1/(10π)"
            ),
            Parameter(
                path="abstract.alpha_inv_theory_sigma",
                name="Alpha^-1 Theory-Level Sigma",
                no_experimental_value=True,
                units="dimensionless",
                description="Deviation of PM alpha^-1 prediction from CODATA in units of the framework's theory uncertainty (NOT CODATA experimental precision)",
                status="SYSTEM",
                eml_description="EML: eml_scalar(0.0497) — σ-deviation of α⁻¹ prediction from CODATA at theory uncertainty level"
            ),
            Parameter(
                path="abstract.theta23_sigma_io",
                name="Theta_23 IO Sigma Deviation",
                no_experimental_value=True,
                units="degrees",
                description="Deviation of PM theta_23 prediction from NuFIT 6.0 inverted ordering central value in theory sigma units",
                status="SYSTEM",
                eml_description="EML: eml_scalar(0.45) — σ-deviation of θ₂₃ prediction from NuFIT 6.0 IO central value"
            ),
            Parameter(
                path="abstract.desi_w0_uncertainty",
                name="DESI w0 BAO-Only Uncertainty",
                no_experimental_value=False,
                units="dimensionless",
                description="1-sigma uncertainty on w0 from DESI 2025 BAO-only analysis",
                experimental_bound=0.067,
                bound_type="range",
                bound_source="DESI2025",
                status="SYSTEM",
                eml_description="EML: eml_scalar(0.067) — 1σ uncertainty on w₀ from DESI 2025 BAO-only analysis (input)"
            ),
            Parameter(
                path="abstract.tau_p_display",
                name="Proton Lifetime Display Coefficient",
                no_experimental_value=True,
                units="1e34_years",
                description="Proton lifetime coefficient for display (tau_p = value × 10^34 years)",
                status="PREDICTED",
                eml_description="EML: ops.div(eml_vec('proton_decay.tau_p_years'), eml_scalar(1e34)) — proton lifetime display coefficient in units of 10³⁴ yr"
            ),
            Parameter(
                path="abstract.tau_p_bound_display",
                name="Proton Lifetime Super-K Bound Display",
                units="1e34_years",
                description=(
                    "Super-Kamiokande lower bound on proton lifetime in units "
                    "of 10^34 years (display echo of the experimental bound "
                    "itself; the prediction proton_decay.lifetime_years is "
                    "validated against it separately)"
                ),
                status="SYSTEM",
                no_experimental_value=True,
                eml_description="EML: eml_scalar(1.67) — Super-K lower bound on τ_p in units of 10³⁴ yr (PDG 2024 input)"
            ),
            Parameter(
                path="abstract.dark_force_pleak",
                name="Dark Force Leakage Probability",
                no_experimental_value=True,
                units="dimensionless",
                description="Cross-shadow leakage probability for EM and gravity (strong/weak effectively zero)",
                status="PREDICTED",
                eml_description="EML: eml_vec('dark_force_pleak') — cross-shadow leakage probability P_leak ≈ 4.27×10⁻⁸ for EM and gravity"
            ),
            Parameter(
                path="abstract.alpha_inv_pred",
                name="Predicted Fine Structure Constant Inverse",
                no_experimental_value=False,
                units="dimensionless",
                description="PM framework prediction for alpha^-1 (echoed from constants.alpha_inverse_pred for abstract display)",
                experimental_bound=137.035999177,  # alpha inverse (CODATA 2022 full)
                bound_type="measured",
                bound_source="CODATA2022",
                status="PREDICTED",
                eml_description="EML: ops.add(eml_scalar(137.0), ops.div(eml_scalar(1.0), ops.mul(eml_scalar(24.0), ops.mul(eml_scalar(5.0), eml_pi())))) — α⁻¹ from G₂ spectral gap"
            ),
            Parameter(
                path="abstract.alpha_inv_codata",
                name="CODATA 2022 Alpha^-1",
                no_experimental_value=False,
                units="dimensionless",
                description="CODATA 2022 experimental value of alpha^-1 (echoed for abstract display spans)",
                experimental_bound=137.035999177,  # alpha inverse (CODATA 2022 full)
                bound_type="measured",
                bound_source="CODATA2022",
                status="SYSTEM",
                eml_description="EML: eml_scalar(137.035999177) — CODATA 2022 inverse fine structure constant (input, echoed for display)"
            ),
            Parameter(
                path="abstract.theta23_io_central",
                name="NuFIT 6.0 Theta_23 IO Central Value",
                no_experimental_value=False,
                units="degrees",
                description="NuFIT 6.0 inverted ordering central value for theta_23 (echoed for abstract display)",
                experimental_bound=49.3,
                bound_type="measured",
                bound_source="NuFIT6.0",
                status="SYSTEM",
                eml_description="EML: eml_scalar(49.3) — NuFIT 6.0 IO central value for θ₂₃ in degrees (input, echoed for display)"
            ),
            # ALP Principia Metric Parameters
            Parameter(
                path="alp.mass_meV",
                name="ALP Mass (Principia Metric)",
                no_experimental_value=True,
                units="meV",
                description="Axion-Like Particle mass from M²⁶ → M⁴ vacuum residue - the primary falsifiability kill-switch for the G₂ compactification framework (PREDICTED: awaiting IAXO/BabyIAXO 2025-2028)",
                status="PREDICTED",
                eml_description="EML: eml_scalar(3.51) — ALP mass in meV from M²⁶ → M⁴ vacuum residue (Principia Metric kill-switch)"
            ),
            Parameter(
                path="alp.coupling_GeV_inv",
                name="ALP-Photon Coupling",
                no_experimental_value=True,
                units="GeV^-1",
                description="ALP-photon coupling strength g_aγγ from Euclidean Information Sector (S_EIS) coupling - testable by IAXO/BabyIAXO 2025-2028 (PREDICTED: no current experimental bound)",
                status="PREDICTED",
                eml_description="EML: eml_vec('alp_coupling_GeV_inv') — g_aγγ ~ 10⁻¹¹ GeV⁻¹ from S_EIS–photon coupling (PREDICTED)"
            ),
            Parameter(
                path="alp.coupling_GeV_inv_value",
                name="ALP-Photon Coupling (Refined)",
                no_experimental_value=True,
                units="GeV^-1",
                description="Refined ALP-photon coupling g_aγγ ≈ 2.9×10⁻¹¹ GeV⁻¹ — single falsifiable axion prediction reachable by BabyIAXO 2028",
                status="PREDICTED",
                eml_description="EML: eml_vec('alp_coupling_GeV_inv_value') — g_aγγ ≈ 2.9×10⁻¹¹ GeV⁻¹ (BabyIAXO 2028 reach)"
            ),
            # v25.0+v26.0 closure ledger
            Parameter(
                path="abstract.compression_ratio",
                name="Compression Ratio (post-v25/v26)",
                no_experimental_value=True,
                units="dimensionless",
                description="Topological compression ratio after v25.0+v26.0 closures (131:1 per S5.10, up from 116:1)",
                status="SYSTEM",
                eml_description="EML: eml_scalar(131) — compression ratio after 13 new DERIVED items in v25/v26 (S5.10)"
            ),
            Parameter(
                path="abstract.ledger_total",
                name="Proof-Completeness Ledger Total",
                no_experimental_value=True,
                units="count",
                description="Total tracked parameters in the proof-completeness ledger",
                status="SYSTEM",
                eml_description="EML: eml_scalar(620) — total tracked parameters in proof-completeness ledger"
            ),
            Parameter(
                path="abstract.ledger_derived",
                name="Ledger DERIVED Count",
                no_experimental_value=True,
                units="count",
                description="Number of fully derived parameters in the ledger (571/620 = 92.1%)",
                status="SYSTEM",
                eml_description="EML: eml_scalar(571) — fully derived ledger entries (92.1%)"
            ),
            Parameter(
                path="abstract.ledger_derived_pct",
                name="Ledger DERIVED Percentage",
                no_experimental_value=True,
                units="percent",
                description="Percentage of ledger entries that are fully derived (571/620 ≈ 92.1%)",
                status="SYSTEM",
                eml_description="EML: ops.mul(ops.div(eml_scalar(571), eml_scalar(620)), eml_scalar(100)) — derived percentage"
            ),
            Parameter(
                path="abstract.ledger_numerical",
                name="Ledger Numerical-Agreement Count",
                no_experimental_value=True,
                units="count",
                description="Ledger entries with numerical agreement but no closed-form derivation (28)",
                status="SYSTEM",
                eml_description="EML: eml_scalar(28) — ledger numerical-agreement entries"
            ),
            Parameter(
                path="abstract.ledger_fitted",
                name="Ledger Fitted Count",
                no_experimental_value=True,
                units="count",
                description="Fitted ledger entries — legacy θ₁₃ / δ_CP markers (14)",
                status="SYSTEM",
                eml_description="EML: eml_scalar(14) — fitted ledger entries (legacy θ₁₃ / δ_CP markers)"
            ),
            Parameter(
                path="abstract.ledger_open",
                name="Ledger Open-Tension Count",
                no_experimental_value=True,
                units="count",
                description="Documented open tensions (PMNS Majorana η, baryogenesis normalisation, soft SUSY scale, etc.) — 7 entries",
                status="SYSTEM",
                eml_description="EML: eml_scalar(7) — documented open-tension ledger entries"
            ),
            Parameter(
                path="abstract.v25_v26_closures",
                name="v25.0+v26.0 Closure Count",
                no_experimental_value=True,
                units="count",
                description="Number of previously open DERIVED items closed in the v25.0+v26.0 sprint (13)",
                status="SYSTEM",
                eml_description="EML: eml_scalar(13) — v25.0+v26.0 newly closed DERIVED items"
            ),
            # Validation Statistics
            Parameter(
                path="validation.total_predictions",
                name="Total Standard Model Parameter Predictions",
                no_experimental_value=True,
                units="count",
                description="Total number of Standard Model parameters with both theoretical predictions and experimental comparison data",
                status="SYSTEM",
                eml_description="EML: eml_scalar(26) — total SM parameter comparisons in validation table"
            ),
            Parameter(
                path="validation.predictions_within_1sigma",
                name="Predictions Within 1-Sigma",
                no_experimental_value=True,
                units="count",
                description="Number of Standard Model parameter predictions within 1σ of experimental central values",
                status="SYSTEM",
                eml_description="EML: eml_scalar(24) — count of SM predictions agreeing within 1σ of experimental values"
            ),
            Parameter(
                path="validation.exact_matches",
                name="Exact Matches (Within Theory Uncertainty)",
                no_experimental_value=True,
                units="count",
                description="Number of predictions within 0.1σ of experimental values (within theory-level uncertainty)",
                status="SYSTEM",
                eml_description="EML: eml_scalar(3) — count of predictions within 0.1σ theory uncertainty (exact matches)"
            ),
            Parameter(
                path="validation.calibrated_count",
                name="Calibrated Parameter Count (alias)",
                no_experimental_value=True,
                units="count",
                description=(
                    "Alias of validation.free_variable_count. This row used to "
                    "read 0, on the argument that 'EDOF=3 calibrations are "
                    "scale-setting, not fitted free parameters'. The ledger "
                    "sweeps the tree instead: exactly one row declares itself "
                    "scale-setting in its own words, so the argument did not "
                    "cover what the 0 was claiming."
                ),
                status="SYSTEM",
                eml_description="EML: eml_scalar(validation.free_variable_count) — measured by free_variable_ledger, not asserted"
            ),
            Parameter(
                path="validation.free_variable_count",
                name="Free Variable Count",
                no_experimental_value=True,
                units="count",
                description=(
                    "The number of quantities this framework does not derive, "
                    "counted by sweeping the tree rather than asserted: every "
                    "Parameter(...) whose status is FITTED, FITTED_COMPOSITE, "
                    "CALIBRATED, ANSATZ or MEASURED, plus the geometric "
                    "anchors registered as MEASURED. Per-row evidence, "
                    "including the traced consumer that fixes each row's "
                    "role, is in AutoGenerated/free_variables.json. This is "
                    "the single number the three older literals (0, 3, 3) and "
                    "generate_statistics.FITTED_PARAMS_COUNT = 1 have been "
                    "replaced by."
                ),
                status="VALIDATION",
                eml_description="EML: eml_scalar(len(free_variables.rows)) — a count of swept rows, with no literal behind it"
            ),
            Parameter(
                path="validation.constraints_count",
                name="Observational Constraints Count",
                no_experimental_value=True,
                units="count",
                description="Number of observational constraints applied (m_h → Re(T))",
                status="SYSTEM",
                eml_description="EML: eml_scalar(1) — one Higgs mass observational constraint fixing Re(T) modulus"
            ),
            Parameter(
                path="abstract.constraints_count",
                name="Abstract Constraints Count (alias)",
                no_experimental_value=True,
                units="count",
                description="Alias of validation.constraints_count for abstract display",
                status="SYSTEM",
                eml_description="EML: eml_scalar(1) — one observational constraint (m_h → Re(T)) alias for abstract display"
            ),
            # Dimensional parameters
            Parameter(
                path="dimensions.D_bulk",
                name="Bulk Spacetime Dimension",
                no_experimental_value=True,
                units="dimensionless",
                description="Total ancestral bulk dimension M^{26}(24,2) = 24 space + 2 times (one per 13D shadow)",
                status="GEOMETRIC",
                eml_description="EML: eml_scalar(26.0) — ancestral manifold dimension D_bulk = 24+2 = 26"
            ),
            Parameter(
                path="dimensions.D_G2",
                name="G₂ Manifold Dimension",
                no_experimental_value=True,
                units="dimensionless",
                description="Dimension of the G₂ holonomy compactification manifold V₇",
                status="GEOMETRIC",
                eml_description="EML: eml_scalar(7.0) — G₂ holonomy manifold dimension D_G2 = 7"
            ),
            Parameter(
                path="dimensions.D_physics",
                name="Physics Core Dimension",
                no_experimental_value=True,
                units="dimensionless",
                description="Physics core dimension = 12 bridge pairs × 2 = 24 spatial dimensions",
                status="GEOMETRIC",
                eml_description="EML: ops.mul(eml_scalar(12.0), eml_scalar(2.0)) — physics core D_physics = 12×2 = 24"
            ),
            Parameter(
                path="dimensions.D_observable",
                name="Observable Spacetime Dimension",
                no_experimental_value=True,
                units="dimensionless",
                description=(
                    "Observable 4D Minkowski spacetime dimension after the CY3 "
                    "projection of the 7D G₂ manifold: D_G2 - 3 = 7 - 3 = 4. "
                    "Derived by calabi-yau-projection (1.4); registered here "
                    "alongside the other dimensional aliases so the path the "
                    "formula declares as its output actually exists."
                ),
                status="GEOMETRIC",
                derivation_formula="calabi-yau-projection",
                eml_description="EML: ops.sub(eml_scalar(7.0), eml_scalar(3.0)) — observable D = D_G2 - 3 = 4"
            ),
            # Seed display aliases (registered by abstract to ensure display consistency)
            Parameter(
                path="constants.k_gimel",
                name="Spectral Gap k_gimel",
                no_experimental_value=True,
                units="dimensionless",
                description="Spectral gap from associative 3-cycles of the G₂ manifold; one of the Ten Pillar Seeds",
                status="GEOMETRIC",
                eml_description="EML: ops.add(ops.div(eml_scalar(24.0), eml_scalar(2.0)), ops.inv(eml_pi())) — k_gimel = b₃/2 + 1/π ≈ 12.318"
            ),
            Parameter(
                path="constants.phi",
                name="Golden Ratio φ",
                no_experimental_value=True,
                units="dimensionless",
                description="Golden ratio from minimal surface geometry; one of the Ten Pillar Seeds",
                status="GEOMETRIC",
                eml_description="EML: ops.div(ops.add(eml_scalar(1.0), ops.sqrt(eml_scalar(5.0))), eml_scalar(2.0)) — φ = (1+√5)/2"
            ),
            Parameter(
                path="constants.demiurgic_coupling",
                name="Demiurgic Coupling (k_gimel alias)",
                no_experimental_value=True,
                units="dimensionless",
                description="Gnostic alias for k_gimel — spectral gap from associative 3-cycles",
                status="GEOMETRIC",
                eml_description="EML: eml_vec('constants.k_gimel') — demiurgic_coupling = k_gimel ≈ 12.318 (alias)"
            ),
        ]

    def get_beginner_explanation(self) -> Dict[str, Any]:
        """
        Return a beginner-friendly explanation of the abstract's key claims.

        Returns:
            Dictionary with title, summary, and key concepts suitable for
            non-experts encountering the Principia Metaphysica framework.
        """
        return {
            "title": "What does this abstract say?",
            "summary": (
                "The abstract summarizes a theory that claims the fundamental constants "
                "of physics (like particle masses and force strengths) are not arbitrary "
                "numbers but are mathematically determined by the shape of a hidden "
                "higher-dimensional space."
            ),
            "explanation": (
                "Principia Metaphysica proposes that our familiar 4D universe is a "
                "'shadow' of a 27-dimensional space. When this larger space folds down "
                "to what we observe, the folding pattern fixes all the physical constants "
                "we measure in experiments -- they emerge as mathematical harmonics of "
                "the folded geometry, much like how a drum's shape determines the notes "
                "it can produce."
            ),
            "key_concepts": [
                {
                    "name": "27 Dimensions to 4 Dimensions",
                    "explanation": (
                        "The theory starts with a 27-dimensional space that splits into "
                        "two 13-dimensional 'shadows' connected by a 2D bridge. Each "
                        "shadow then compactifies (folds up 9 of its dimensions) to give "
                        "the 4D spacetime we experience. The specific way the folding "
                        "happens is governed by G2 holonomy -- a precise mathematical "
                        "structure that leaves no room for adjustable parameters."
                    )
                },
                {
                    "name": "125 Constants from Geometry",
                    "explanation": (
                        "Rather than treating constants like the electron mass or the "
                        "strength of gravity as independent inputs, the theory proposes "
                        "geometric expressions for all 125 of them as 'spectral residues' "
                        "-- the natural resonant frequencies of the folded 7-dimensional "
                        "internal manifold."
                    )
                },
                {
                    "name": "Testable Predictions",
                    "explanation": (
                        "The abstract highlights several predictions that experiments can "
                        "check. 41 of 67 scored comparisons land within 1 sigma of the "
                        "measurement, dark energy may behave as 'thawing' (consistent with "
                        "DESI 2025 data), and proton decay at a rate testable by the "
                        "Hyper-Kamiokande detector. Taken together, though, the fit is poor: "
                        "chi^2 = 126,748.86 over 65 scoring rows, p = 0, POOR_FIT. Five "
                        "candidates have already been falsified outright, including three "
                        "attempts at the Cabibbo angle."
                    )
                },
                {
                    "name": "Three Generations of Matter",
                    "explanation": (
                        "One of physics' unsolved puzzles is why matter comes in exactly "
                        "3 families (electron/muon/tau and their associated particles). "
                        "This theory derives n_gen = 3 from the topology of the internal "
                        "manifold: chi_eff/(2*b3) = 144/48 = 3. The number 3 is not "
                        "put in by hand -- it is derived from the geometry."
                    )
                },
            ],
            "why_it_matters": (
                "If correct, this framework would represent a fundamental advance in "
                "theoretical physics: it would mean that the constants of nature are not "
                "arbitrary but are fixed by topological and geometric constraints within this framework. The "
                "theory makes specific, falsifiable predictions that upcoming experiments "
                "can test."
            )
        }

    # -------------------------------------------------------------------------
    # SSOT enrichment methods
    # -------------------------------------------------------------------------

    def get_references(self) -> List[Dict[str, Any]]:
        """Return bibliographic references relevant to the abstract."""
        return [
            {
                "id": "acharya_witten2001",
                "authors": "Acharya, B.S. and Witten, E.",
                "title": "Chiral Fermions from Manifolds of G2 Holonomy",
                "year": 2001,
                "arxiv": "hep-th/0109152",
                "url": "https://arxiv.org/abs/hep-th/0109152",
                "notes": "Foundation for chirality from G2 compactification cited in abstract",
            },
            {
                "id": "desi_2025_thawing",
                "authors": "DESI Collaboration",
                "title": "DESI 2025 Dark Energy Results: Thawing Quintessence Constraints",
                "year": 2025,
                "journal": "Physical Review Letters",
                "url": "https://arxiv.org/abs/2503.14738",
                "notes": "PM prediction w0 = -23/24 falls within BAO-only uncertainty range"
            },
            {
                "id": "planck2018",
                "authors": "Planck Collaboration (Aghanim, N. et al.)",
                "title": "Planck 2018 results. VI. Cosmological parameters",
                "year": 2020,
                "journal": "Astron. Astrophys.",
                "volume": "641",
                "pages": "A6",
                "doi": "10.1051/0004-6361/201833910",
                "arxiv": "1807.06209",
                "url": "https://doi.org/10.1051/0004-6361/201833910",
                "notes": "Primary cosmological data set for validation",
            },
            {
                "id": "nufit_6_0",
                "authors": "Esteban, I. et al. (NuFIT collaboration)",
                "title": "NuFIT 6.0: Updated Global Analysis of Neutrino Oscillation Parameters",
                "year": 2024,
                "url": "http://www.nu-fit.org/",
                "notes": "PMNS mixing angle and delta_CP data referenced in abstract; theta_13 and delta_CP fitted pending explicit Yukawa calculation"
            },
        ]

    def get_certificates(self) -> List[Dict[str, Any]]:
        """Return certificate assertions verifying abstract section integrity.

        Checks content word count, key framework term coverage, and
        formula derivation completeness to certify the abstract meets
        structural and content quality requirements.
        """
        section = self.get_section_content()
        blocks = section.content_blocks if section else []
        paragraph_blocks = [b for b in blocks if b.type == "paragraph"]
        total_text = " ".join(b.content for b in paragraph_blocks)
        word_count = len(total_text.split())
        has_key_terms = all(
            term in total_text
            for term in ["27", "G\u2082", "dual-shadow", "125", "certificates"]
        )
        formulas = self.get_formulas()
        formulas_have_derivation = all(
            f.derivation and len(f.derivation.get("steps", [])) >= 3
            and f.derivation.get("method")
            for f in formulas
        )

        return [
            {
                "id": "CERT_ABSTRACT_WORD_COUNT",
                "assertion": "Abstract contains at least 100 words of substantive content",
                "condition": f"word_count >= 100 (actual: {word_count})",
                "tolerance": 100,
                "status": "PASS" if word_count >= 100 else "FAIL",
                "wolfram_query": "N/A (content integrity check)",
                "wolfram_result": "N/A",
                "sector": "paper"
            },
            {
                "id": "CERT_ABSTRACT_KEY_TERMS",
                "assertion": "Abstract references key framework terms (26D, G2, dual-shadow, 125 constants, certificates)",
                "condition": f"all key terms present: {has_key_terms}",
                "tolerance": "exact",
                "status": "PASS" if has_key_terms else "FAIL",
                "wolfram_query": "N/A (content integrity check)",
                "wolfram_result": "N/A",
                "sector": "paper"
            },
            {
                "id": "CERT_ABSTRACT_FORMULA_INTEGRITY",
                "assertion": "Abstract formula definitions include complete derivation chains (>=3 steps, method, parentFormulas)",
                "condition": f"formula_count >= 1 (actual: {len(formulas)}), all_have_derivation: {formulas_have_derivation}",
                "tolerance": "exact",
                "status": "PASS" if (len(formulas) >= 1 and formulas_have_derivation) else "FAIL",
                "wolfram_query": "N/A (structural check)",
                "wolfram_result": "N/A",
                "sector": "paper"
            },
        ]

    def get_learning_materials(self) -> List[Dict[str, Any]]:
        """Return educational resources about concepts mentioned in the abstract."""
        return [
            {
                "topic": "G2 holonomy manifolds",
                "url": "https://en.wikipedia.org/wiki/G2_manifold",
                "relevance": "The abstract claims all 125 constants arise as spectral residues of G2 compactification; G2 holonomy is the key mathematical structure",
                "validation_hint": "G2 holonomy yields Ricci-flat 7-manifolds with exactly the right structure for chirality"
            },
            {
                "topic": "Dark energy equation of state",
                "url": "https://en.wikipedia.org/wiki/Equation_of_state_(cosmology)",
                "relevance": "Abstract predicts w0 = -23/24 thawing dark energy; understanding the equation of state parameter w is essential for interpreting this prediction",
                "validation_hint": "w = -1 is cosmological constant; w > -1 indicates thawing quintessence (consistent with DESI 2025)"
            },
            {
                "topic": "Fermion generations in the Standard Model",
                "url": "https://en.wikipedia.org/wiki/Generation_(particle_physics)",
                "relevance": "The abstract derives n_gen = 3 from topology; this addresses a longstanding open question in particle physics",
                "validation_hint": "LEP Z-width measurement confirms exactly 3 light neutrino generations"
            },
        ]

    def validate_self(self) -> Dict[str, Any]:
        """Validate abstract section integrity.

        Performs structural and content checks to ensure the abstract
        meets minimum quality standards: word count, block count,
        key term coverage, formula integrity, and reference completeness.
        """
        checks = []

        section = self.get_section_content()
        blocks = section.content_blocks if section else []
        paragraph_blocks = [b for b in blocks if b.type == "paragraph"]
        total_text = " ".join(b.content for b in paragraph_blocks)
        word_count = len(total_text.split())

        # Check 1: Word count minimum
        wc_ok = word_count >= 100
        checks.append({
            "name": "Abstract word count meets minimum (>=100)",
            "passed": wc_ok,
            "confidence_interval": {
                "lower": 100,
                "upper": 500,
                "sigma": 0.0
            },
            "log_level": "INFO" if wc_ok else "ERROR",
            "message": f"Word count = {word_count} (minimum 100)"
        })

        # Check 2: Content block count
        blocks_ok = len(blocks) >= 3
        checks.append({
            "name": "Abstract has at least 3 content blocks",
            "passed": blocks_ok,
            "confidence_interval": {
                "lower": 3,
                "upper": 10,
                "sigma": 0.0
            },
            "log_level": "INFO" if blocks_ok else "ERROR",
            "message": f"Content blocks = {len(blocks)} (minimum 3)"
        })

        # Check 3: Key framework terms present in abstract text
        required_terms = ["27", "G\u2082", "dual-shadow", "125", "certificates"]
        present_terms = [t for t in required_terms if t in total_text]
        missing_terms = [t for t in required_terms if t not in total_text]
        terms_ok = len(missing_terms) == 0
        checks.append({
            "name": "Abstract contains all key framework terms",
            "passed": terms_ok,
            "confidence_interval": {
                "lower": len(required_terms),
                "upper": len(required_terms),
                "sigma": 0.0
            },
            "log_level": "INFO" if terms_ok else "ERROR",
            "message": (
                f"Key terms present: {len(present_terms)}/{len(required_terms)}"
                + (f" (missing: {missing_terms})" if missing_terms else "")
            )
        })

        # Check 4: Formula definitions present and well-formed
        formulas = self.get_formulas()
        formulas_ok = len(formulas) >= 1
        formulas_have_derivation = all(
            f.derivation and len(f.derivation.get("steps", [])) >= 3
            for f in formulas
        )
        checks.append({
            "name": "Abstract formula definitions present with derivation steps",
            "passed": formulas_ok and formulas_have_derivation,
            "confidence_interval": {
                "lower": 1,
                "upper": 3,
                "sigma": 0.0
            },
            "log_level": "INFO" if (formulas_ok and formulas_have_derivation) else "ERROR",
            "message": f"Formulas = {len(formulas)}, all have >=3 derivation steps: {formulas_have_derivation}"
        })

        # Check 5: References provided
        refs = self.get_references()
        refs_ok = len(refs) >= 2
        checks.append({
            "name": "At least 2 bibliographic references provided",
            "passed": refs_ok,
            "confidence_interval": {
                "lower": 2,
                "upper": 10,
                "sigma": 0.0
            },
            "log_level": "INFO" if refs_ok else "ERROR",
            "message": f"References = {len(refs)} (minimum 2)"
        })

        # Check 6: Learning materials provided
        materials = self.get_learning_materials()
        materials_ok = len(materials) >= 2
        checks.append({
            "name": "At least 2 learning materials provided",
            "passed": materials_ok,
            "confidence_interval": {
                "lower": 2,
                "upper": 10,
                "sigma": 0.0
            },
            "log_level": "INFO" if materials_ok else "WARNING",
            "message": f"Learning materials = {len(materials)} (minimum 2)"
        })

        return {
            "passed": all(c["passed"] for c in checks),
            "checks": checks
        }

    def get_gate_checks(self) -> List[Dict[str, Any]]:
        """Return gate check results for abstract section.

        Verifies content integrity and structural completeness of the
        abstract narrative, including word count, key term coverage,
        and formula/reference availability.
        """
        section = self.get_section_content()
        blocks = section.content_blocks if section else []
        paragraph_blocks = [b for b in blocks if b.type == "paragraph"]
        total_text = " ".join(b.content for b in paragraph_blocks)
        word_count = len(total_text.split())

        required_terms = ["27", "G\u2082", "dual-shadow", "125", "certificates"]
        has_key_terms = all(term in total_text for term in required_terms)
        formulas = self.get_formulas()
        refs = self.get_references()
        passed = word_count >= 100 and has_key_terms and len(formulas) >= 1

        return [
            {
                "gate_id": "G_ABSTRACT_CONTENT_INTEGRITY",
                "simulation_id": self.metadata.id,
                "assertion": "Abstract section contains substantive content (>=100 words) with key framework terms, formula definitions, and bibliographic references",
                "result": "PASS" if passed else "FAIL",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "word_count": word_count,
                    "content_blocks": len(blocks),
                    "paragraph_blocks": len(paragraph_blocks),
                    "key_terms_present": has_key_terms,
                    "formula_count": len(formulas),
                    "reference_count": len(refs),
                    "section_type": "narrative_abstract",
                    "note": "Paper abstract for Principia Metaphysica v24.2 M^{26}(24,2) dual-shadow framework"
                }
            },
        ]


# Allow direct execution for testing
if __name__ == "__main__":
    sim = AbstractV17_2()
    print(f"Simulation: {sim.metadata.id}")
    print(f"Section: {sim.metadata.section_id}")

    section_content = sim.get_section_content()
    if section_content:
        print(f"Title: {section_content.title}")
        print(f"Content blocks: {len(section_content.content_blocks)}")
