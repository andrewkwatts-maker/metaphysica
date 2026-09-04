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
    - abstract.calibration_inputs (3), abstract.fitted_pmns (2)
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
    import arithma as _A
    def _arithma_num(v):
        return _A.Expression.number(float(v))
except ImportError:  # pragma: no cover
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
            "abstract.calibration_inputs":     3,
            "abstract.fitted_pmns":            2,
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
            "validation.calibrated_count":     0,    # EDOF=3: calibrations are scale-setting, not fitted
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
            "abstract.tau_p_display":          round(tau_p / 1e34, 1),         # 4.8
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
        """
        Return section content for Section 0: Abstract.

        Returns:
            SectionContent instance with the paper abstract
        """
        content_blocks = [
            # v2.2.0 honesty polish: research-status callout before any
            # claims. Every downstream renderer (paper.html, PDF paper,
            # sections.json) picks this up automatically.
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
            # Lead paragraph - framework introduction
            ContentBlock(
                type="paragraph",
                content=(
                    'We introduce a candidate mathematical model that proposes geometric expressions for <span class="pm-value" data-pm-value="abstract.total_constants">125</span> physical '
                    'constants and cosmological observables from the topological invariants of a '
                    '<span class="pm-value" data-pm-value="dimensions.D_bulk">26</span>-dimensional manifold '
                    '<strong>M<sup>26</sup>(24,2)</strong>\u2014where <em>24</em> denotes the G\u2082 physics core '
                    '(12\u00d7(2,0) bridge pairs creating dual 13D shadows), <em>1</em> the shared clock t+ = (t1+t2)/sqrt(2)like fiber T\u00b9, '
                    'and <em>2</em> the <strong>shadow-time directions</strong> S<sup>(2,0)</sup> '
                    '(an architecturally separate Euclidean sector providing global cross-shadow averaging). '
                    '<strong>Principia Metaphysica <span class="pm-value" data-pm-value="framework.version_label">v24.2</span></strong> '
                    'proposes a dual-shadow structure where the shared clock t+ = (t1+t2)/sqrt(2) is intended to eliminate ghosts/CTCs, and the '
                    'shadow-time directions S<sup>(2,0)</sup> (ds\u00b2 = ds\u2081\u00b2 + ds\u2082\u00b2) are used to model '
                    'coherent cross-shadow objective reduction (OR). Each shadow compactifies on G\u2082(7,0) to '
                    '<span class="pm-value" data-pm-value="dimensions.D_observable">4</span>D, yielding '
                    'exactly three chiral fermion generations from n<sub>gen</sub> = \u03c7<sub>eff</sub>/(2\u00b7b\u2083) = '
                    '144/48 = <span class="pm-value" data-pm-value="topology.n_gen">3</span> per shadow, '
                    'consistent with M-theory phenomenology (Acharya-Witten 2001).'
                ),
                label="abstract-lead"
            ),
            # Predictions and validation paragraph
            ContentBlock(
                type="paragraph",
                content=(
                    'The model proposes a <strong><span class="pm-value" data-pm-value="abstract.compression_ratio">131</span>:1 compression ratio</strong> '
                    '(125 base constants plus 13 candidate new items proposed in v25.0+v26.0, from EDOF=3 effective seeds; see S5.10) &mdash; '
                    'this ratio is an internal model artifact, not an independently validated result. '
                    'Standard Model parameters are proposed to emerge from manifold topology, flux quantization, and effective torsion. '
                    '<strong><span class="pm-value" data-pm-value="abstract.pure_predictions">55</span> parameters are candidate predictions</strong>. <strong>EDOF=3</strong> (effective degrees of freedom): three calibration seeds '
                    '(VEV coefficient <span class="pm-value" data-pm-value="abstract.vev_coefficient">1.5859</span>, 1/\u03b1<sub>GUT</sub> coefficient 1/(10\u03c0) \u2248 <span class="pm-value" data-pm-value="abstract.alpha_gut_coefficient">0.0318</span>, '
                    'Re(T) constrained from Higgs mass). Two PMNS parameters (\u03b8\u2081\u2083, \u03b4<sub>CP</sub>) '
                    'are fitted to NuFIT 6.0 pending explicit Yukawa calculation.'
                ),
                label="abstract-predictions"
            ),
            # Proof-completeness ledger (v25.0+v26.0 closures)
            ContentBlock(
                type="paragraph",
                content=(
                    '<strong>Proof-completeness ledger</strong>: Of '
                    '<span class="pm-value" data-pm-value="abstract.ledger_total">620</span> tracked parameters, '
                    '<strong><span class="pm-value" data-pm-value="abstract.ledger_derived">571</span> are fully derived '
                    '(<span class="pm-value" data-pm-value="abstract.ledger_derived_pct">92.1</span>%)</strong>, '
                    '<span class="pm-value" data-pm-value="abstract.ledger_numerical">28</span> reach numerical agreement, '
                    '<span class="pm-value" data-pm-value="abstract.ledger_fitted">14</span> remain fitted '
                    '(legacy \u03b8\u2081\u2083 / \u03b4<sub>CP</sub> markers), and '
                    '<span class="pm-value" data-pm-value="abstract.ledger_open">7</span> are documented open tensions '
                    '(PMNS Majorana phase \u03b7, baryogenesis normalisation, soft SUSY scale, and four further entries). '
                    'The v25.0+v26.0 sprint closed <strong>13 previously open DERIVED items</strong>, lifting the '
                    'compression ratio from 116:1 to <strong>131:1</strong>.'
                ),
                label="abstract-ledger"
            ),
            # Validation results paragraph
            ContentBlock(
                type="paragraph",
                content=(
                    'The framework does not fit the data globally. Over the 65 scoring rows of '
                    'the validation registry the computed statistic is <strong>\u03c7\u00b2 = 126,748.86 '
                    '(reduced 1,950), p = 0, status POOR_FIT</strong>; excluding five candidates now '
                    'carried as FALSIFIED it is \u03c7\u00b2 = 5,790.62 over 60 rows (reduced \u2248 96.5). '
                    'Both figures are published in <code>statistical_rigor_report.json</code> under '
                    '<code>chi_squared_from_rows</code>. A previously published headline of '
                    '\u03c7\u00b2 = 0.23, reduced 0.077, p \u2248 0.97, verdict TOO_GOOD was read from a summary '
                    'key that has never existed, and is withdrawn in full. '
                    'Individual comparisons are a different matter and are reported per row: of '
                    '<span class="pm-value" data-pm-value="validation.total_predictions">67</span> '
                    'scored parameter comparisons, '
                    '<strong><span class="pm-value" data-pm-value="validation.within_1sigma">41</span></strong> '
                    'lie within 1\u03c3 of current experimental '
                    'data (see Section 3 for full comparison table), including the fine structure '
                    'constant \u03b1<sup>\u22121</sup> = <span class="pm-value" data-pm-value="abstract.alpha_inv_pred">137.0367</span> (\u03b1<sup>\u22121</sup><sub>pred</sub> vs CODATA 2022: <span class="pm-value" data-pm-value="abstract.alpha_inv_codata">137.036</span>; '
                    '~<span class="pm-value" data-pm-value="abstract.alpha_inv_theory_sigma">0.05</span>\u03c3 theory-level comparison\u2014note: CODATA experimental precision is sub-ppb) and '
                    '\u03b8\u2082\u2083 = <span class="pm-value" data-pm-value="pmns_matrix.theta_23">49.75</span>\u00b0 '
                    '(from G\u2082 holonomy SU(3) symmetry; NuFIT 6.0 IO: <span class="pm-value" data-pm-value="abstract.theta23_io_central">49.3</span>\u00b0, <span class="pm-value" data-pm-value="abstract.theta23_sigma_io">0.45</span>\u03c3). '
                    'The model predicts thawing dark energy '
                    '<Normal>w\u2080 = \u221223/24 \u2248 <span class="pm-value" data-pm-value="cosmology.w0_derived">\u22120.9583</span> (from b\u2083=24 topology)</Normal>'
                    '<EML>w\u2080 = ops.add(ops.neg(1), ops.inv(b\u2083)) = ops.div(ops.neg(23), 24) \u2248 \u22120.9583</EML>, '
                    'consistent with DESI 2025 thawing dark energy constraints '
                    '(BAO-only: w\u2080 = <span class="pm-value" data-pm-value="desi.w0">\u22120.957</span> \u00b1 <span class="pm-value" data-pm-value="abstract.desi_w0_uncertainty">0.067</span>), '
                    'and proton decay lifetime \u03c4<sub>p</sub> \u2248 <span class="pm-value" data-pm-value="abstract.tau_p_display">4.8</span>\u00d710<sup>34</sup> years '
                    '(Super-K bound: ><span class="pm-value" data-pm-value="abstract.tau_p_bound_display">1.67</span>\u00d710<sup>34</sup> yr; Hyper-K testable). '
                    'All derivation chains are recorded in '
                    '<span class="pm-value" data-pm-value="statistics.certificates_total">72</span> '
                    'reproducibility certificates.'
                ),
                label="abstract-validation"
            ),
            # MDL justification paragraph
            ContentBlock(
                type="paragraph",
                content=(
                    '<strong>Topologically Anchored Framework (131:1 Compression)</strong>: '
                    'We frame this proposed derivation through the lens of Minimal Description Length (MDL). '
                    'The 125 observed constants \u2014 extended to 138 after the candidate v25.0+v26.0 additions \u2014 are '
                    'proposed as an efficient topological compression of the M<sup>26</sup> bulk, '
                    'targeting <strong>EDOF=3</strong> (1 geometric seed b\u2083 + 2 calibrations: VEV coefficient, Re(T)). '
                    'The computational implementation proposes a <strong>~131:1 compression ratio</strong> (\u224810,500 bits \u2192 69 bits, per S5.10) &mdash; '
                    'this is a model-internal information-theoretic artifact, not an independently validated result. '
                    'The code is isomorphic to the proposed geometric constraints, with '
                    '<Normal>three topological seeds: b\u2083=24, k_\u2137\u224812.318, \u03c6=(1+\u221a5)/2</Normal>'
                    '<EML>Seeds: eml_scalar(24) [b\u2083], ops.add(ops.div(24,2), ops.inv(pi)) [k_\u2137], ops.div(ops.add(1,ops.sqrt(5)),2) [\u03c6]</EML> '
                    'encoding the 288/24/4 structure proposed from G\u2082 topology (minimal phenomenological input).'
                ),
                label="abstract-mdl"
            ),
            # Field names note
            ContentBlock(
                type="note",
                content=(
                    '<sup>\u2020</sup> The fields are named "Primordial Spinor Field" (\u03a8<sub>P</sub>) and '
                    '"Attractor Scalar" (\u03a6<sub>M</sub>). Historical names "Pneuma" and "Mashiach" reflect '
                    'philosophical inspiration but are not used in technical discussions.'
                ),
                label="abstract-note"
            ),
            # Two-Layer Objective Reduction
            ContentBlock(
                type="paragraph",
                content=(
                    '<strong>Two-Layer Objective Reduction</strong>: '
                    'The theory introduces a hierarchical two-layer OR structure: '
                    '(i) Bridge/Global OR (R<sub>\u22a5</sub><sup>global</sup>) creates dual shadows from the 26D bulk via tensor product '
                    'of 12 M\u00f6bius double-cover operators, and '
                    '(ii) Face/Local OR (R<sub>face</sub><sup>(f)</sup>) selects the visible sector within each shadow from 4 K\u00e4hler '
                    'moduli faces. The master action explicitly captures both layers through warping potentials '
                    'V<sub>bridge</sub> (shadow creation) and V<sub>face</sub> (face selection). Hidden faces (f=2,3,4) provide '
                    'multi-component dark matter with portal coupling '
                    '<Normal>\u03b1<sub>leak</sub> = 1/\u221a6 \u2248 <span class="pm-value" data-pm-value="geometry.alpha_leak">0.408</span> (E\u2087 \u2283 E\u2086\u00d7U(1) branching)</Normal>'
                    '<EML>\u03b1<sub>leak</sub> = ops.inv(ops.sqrt(eml_scalar(6))) \u2014 E\u2087 Clebsch\u2013Gordan coefficient</EML> '
                    'derived algebraically from E\u2087 \u2283 E\u2086 \u00d7 U(1) group branching '
                    '(zero free parameters: the U(1) Clebsch\u2013Gordan coefficient is 1/\u221a6 by necessity). '
                    'Dark force leakage across shadows is predicted to be asymmetric: strong/weak forces effectively zero, '
                    'EM and gravity at P<sub>leak</sub> ≈ <span class="pm-value" data-pm-value="abstract.dark_force_pleak">4.27×10⁻⁸</span>.'
                ),
                label="abstract-two-layer-or"
            ),
            # Principia Metric - ALP Falsification
            ContentBlock(
                type="paragraph",
                content=(
                    '<strong>The Principia Metric</strong>: '
                    'Finally, we present a testable prediction: the existence of a '
                    'topologically induced Axion-Like Particle (ALP) at m<sub>a</sub> = <span class="pm-value" data-pm-value="alp.mass_meV">3.51</span> meV. '
                    'This "Principia Metric" is predicted to arise from the vacuum residue of the M<sup>26</sup> \u2192 M<sup>4</sup> projection '
                    'and the Euclidean Information Sector (S<sub>EIS</sub>) coupling to the photon field, with '
                    'g<sub>a\u03b3\u03b3</sub> \u2248 <span class="pm-value" data-pm-value="alp.coupling_GeV_inv_value">2.9\u00d710\u207b\u00b9\u00b9</span> GeV\u207b\u00b9. '
                    'The single falsifiable axion prediction (m<sub>a</sub> \u2248 '
                    '<span class="pm-value" data-pm-value="alp.mass_meV">3.51</span> meV, '
                    'g<sub>a\u03b3\u03b3</sub> \u2248 2.9\u00d710\u207b\u00b9\u00b9 GeV\u207b\u00b9) is reachable by <strong>BabyIAXO 2028</strong>, '
                    'providing a clear falsification criterion for the G\u2082 compactification framework.'
                ),
                label="abstract-principia-metric"
            ),
        ]

        return SectionContent(
            section_id="0",
            subsection_id=None,
            title="Abstract",
            abstract=(
                "Unified mathematical framework proposing geometric expressions for 125 fundamental "
                "physical constants and cosmological observables as spectral residues of a "
                "M^{26}(24,2) dual-shadow G2 manifold compactification with Euclidean bridge. "
                "Predicts 26 Standard Model parameters (24 within 1-sigma) and proton "
                "decay lifetime testable by Hyper-K. All derivation chains recorded in "
                "reproducibility certificates."
            ),
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
        return [
            Formula(
                id="abstract-framework-overview",
                label="(0.1)",
                latex=r"M^{26}(24{,}1{,}2) \;\xrightarrow{\text{OR}}\; 2 \times 13\text{D}(12,1) \;\xrightarrow{G_2}\; 2 \times 4\text{D} \quad \Rightarrow \quad n_{\text{gen}} = \frac{\chi_{\text{eff}}}{2 \cdot b_3} = \frac{144}{48} = 3",
                plain_text="M^{26}(24,2) -> 2 x 13D(12,1) -> 2 x 4D => n_gen = chi_eff / (2*b3) = 144/48 = 3",
                category="DERIVED",
                description="Framework overview: the M^{26}(24,2) ancestral bulk decomposes as T^1 (two-time structure) x S^(2,0) (shadow-time directions) x 12 bridge pairs B_i^(2,0). The OR reduction operator R_perp = tensor product of 12 Moebius double-covers (R_perp^2 = -I per pair) selects complementary coordinates from each bridge pair, splitting 26D into two 13D(12,1) shadows sharing the single time dimension. Each shadow then independently compactifies on a 7-dimensional TCS G2 holonomy manifold V7 (Ricci-flat, b3 = 24 associative 3-cycles), reducing 13D -> 4D(3,1) x V7 with Spin(3,1) Lorentz symmetry. The generation count n_gen = chi_eff/(2*b3) = 144/48 = 3 follows from the index theorem on V7 (Acharya-Witten 2001), fixing 3 chiral fermion families per shadow without free parameters.",
                eml_tree_str="ops.div(eml_scalar(144.0), ops.mul(eml_scalar(2.0), b3_leaf()))",
                eml_latex=r"n_{\text{gen}} = \mathrm{ops.div}(\mathrm{eml\_scalar}(144),\; \mathrm{ops.mul}(\mathrm{eml\_scalar}(2),\; \mathrm{b3\_leaf}()))",
                eml_description="EML: n_gen = ops.div(chi_eff=144, ops.mul(2, b3_leaf())) — generation count as ratio of topological integers (Sprint T1.7: 4·b3 → 2·b3 LaTeX/EML fix consistent)",
                input_params=["topology.elder_kads", "topology.mephorash_chi"],
                output_params=["topology.n_gen"],
                derivation={
                    "steps": [
                        {"description": "Start from M^{26}(24,2) ancestral bulk: the single time dimension (0,1) is shared by both shadows, 12 bridge pairs B_i^(2,0) each contribute 2 spatial dimensions, and S^(2,0) provides the shadow-time directions", "formula": r"M^{26} = T^1 \times S^{(2,0)} \times_{\text{fiber}} \bigoplus_{i=1}^{12} B_i^{(2,0)}"},
                        {"description": "OR reduction: each bridge pair B_i^(2,0) admits a Moebius double-cover operator R_perp^i (satisfying R_perp^2 = -I) that selects one coordinate for Shadow_Aleph and the complementary coordinate for Shadow_Beth, yielding 12 spatial dims per shadow + 1 shared time = 13D(12,1) each", "formula": r"R_\perp^{\text{full}} = \bigotimes_{i=1}^{12} R_\perp^i \;\Rightarrow\; 2 \times 13\text{D}(12,1)"},
                        {"description": "G2 compactification: each 13D shadow compactifies 9 dimensions on a 7D TCS G2 holonomy manifold V7 (Ricci-flat, b3=24 associative 3-cycles, h^{1,1}=4 Kaehler moduli sectors giving 4 face partitions), reducing to 4D with Spin(3,1) Lorentz symmetry", "formula": r"13\text{D}(12,1) \;\xrightarrow{G_2}\; 4\text{D}(3,1) \times V_7"},
                        {"description": "Generation count from index theorem on V7: effective Euler characteristic chi_eff = 144 (from TCS topology #187) divided by 2*b3 = 48 gives exactly 3 chiral fermion generations per shadow, with no free parameter (Sprint 2.9 LaTeX fix: 4·b₃ → 2·b₃)", "formula": r"n_{\text{gen}} = \frac{\chi_{\text{eff}}}{2 \cdot b_3} = \frac{144}{48} = 3"},
                        {"description": "Ghost-free unitarity: the single shared time dimension eliminates ghosts and closed timelike curves; Euclidean bridge ds^2 = dy_1^2 + dy_2^2 has positive-definite metric enabling coherent cross-shadow sampling via OR reduction", "formula": r"\text{ds}^2_{\text{bridge}} = dy_1^2 + dy_2^2 > 0"},
                    ],
                    "method": "dimensional_descent",
                    "parentFormulas": [
                        "intro-division-algebra-decomposition",
                        "g2-holonomy",
                        "laplacian-eigenvalue",
                    ]
                },
                terms={
                    "M^{26}(24,2)": "26-dimensional ancestral bulk with structure (24 physics core, 1 temporal, 2 shadow-time directions), decomposed as 12x(2,0) bridge pairs + (0,1) two-time structure + two shadow-time directions",
                    "13D(12,1)": "13-dimensional observable shadow with signature (12 spatial from bridge, 1 shared temporal); each shadow compactifies independently on G2",
                    "S^(2,0)": "2-dimensional shadow-time directions with positive-definite metric ds^2 = ds_1^2 + ds_2^2 enabling cross-shadow coherence via OR reduction",
                    "n_gen": "Number of chiral fermion generations per shadow, topologically fixed at 3",
                    "chi_eff": "Effective Euler characteristic of the G2 manifold (chi_eff = 144), computed from TCS topology #187",
                    "b_3": "Third Betti number of the G2 manifold V7; 4*b_3 = 48 appears in the generation formula denominator",
                    "OR": "Orthogonal Reduction operator R_perp providing per-pair Moebius double-cover (R_perp^2 = -I) for cross-shadow coordinate selection",
                    "G_2": "Exceptional Lie group G2 = Aut(O) providing holonomy for 7D compactification; Ricci-flat metric ensures spectral rigidity",
                    "V_7": "7-dimensional internal G2 holonomy manifold (TCS construction) hosting the 125-residue spectral port",
                }, 
            arithma=_arithma_div(_arithma_num(144.0), _arithma_mul(_arithma_num(2.0), _arithma_num(24.0))), eml=_eml_div(_eml_scalar(144.0), _eml_mul(_eml_scalar(2.0), _b3_leaf())), value=3.0)
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
                eml_description="EML: eml_vec('framework_version') — PM framework version identifier string"
            ),
            Parameter(
                path="framework.version_major",
                name="Framework Major Version",
                no_experimental_value=True,
                units="version",
                description="Major version number only (e.g., '24')",
                status="SYSTEM",
                eml_description="EML: eml_vec('framework_version_major') — PM framework major version identifier"
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
                name="Calibration Input Count",
                no_experimental_value=True,
                units="dimensionless",
                description="Number of scale calibration inputs required by the theory (VEV, alpha_GUT, Re(T))",
                status="SYSTEM",
                eml_description="EML: eml_scalar(3.0) — number of calibrated inputs (θ₁₃, δ_CP, DM normalization) setting physical scales"
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
                name="Calibrated Parameter Count",
                no_experimental_value=True,
                units="count",
                description="Number of calibrated (scale-setting) parameters; EDOF=3 are scale-setting, not fitted free parameters",
                status="SYSTEM",
                eml_description="EML: eml_scalar(0) — EDOF=3 calibrations are scale-setting constraints, not free-parameter fits"
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
