"""Formula, parameter and section metadata infrastructure.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


# ==============================================================================
# PARAMETER CATEGORIZATION FRAMEWORK
# ==============================================================================

# NOTE: ParameterCategory class is defined below at line ~295 with uppercase convention
# (e.g., "GEOMETRIC" not "geometric"). The uppercase version is used throughout the codebase.
# Removed duplicate lowercase definition to avoid override conflicts (v24.2 fix).

class FormulaCategory:
    """Categories for formula derivation chains."""
    ESTABLISHED = "ESTABLISHED"   # Foundational physics (Einstein, Yang-Mills, etc.)
    THEORY = "THEORY"             # PM foundational formulas (derive from ESTABLISHED)
    DERIVED = "DERIVED"           # Computed formulas (derive from THEORY)
    PREDICTIONS = "PREDICTIONS"   # Testable predictions (derive from DERIVED)
    SPECULATIVE = "SPECULATIVE"   # Superseded / alternative-story candidates (not operative)


@dataclass
class FormulaTerm:
    """A hoverable term within a formula (Level 2 display)."""
    name: str
    description: str
    link: Optional[str] = None
    symbol: Optional[str] = None      # Unicode symbol for display
    value: Optional[str] = None       # Numerical value if applicable
    # Enhanced fields for three-level display
    units: Optional[str] = None       # Physical units
    oom: Optional[float] = None       # Order of magnitude (log10)
    param_id: Optional[str] = None    # Link to parameter ID
    formula_id: Optional[str] = None  # Link to defining formula ID
    contribution: Optional[str] = None  # How this term contributes to the formula

    def to_dict(self) -> Dict[str, Any]:
        d = {"name": self.name, "description": self.description}
        if self.link:
            d["link"] = self.link
        if self.symbol:
            d["symbol"] = self.symbol
        if self.value:
            d["value"] = self.value
        if self.units:
            d["units"] = self.units
        if self.oom is not None:
            d["oom"] = self.oom
        if self.param_id:
            d["paramId"] = self.param_id
        if self.formula_id:
            d["formulaId"] = self.formula_id
        if self.contribution:
            d["contribution"] = self.contribution
        return d


@dataclass
class FormulaReference:
    """A reference/citation for a formula."""
    id: str              # e.g., "acharya2008"
    title: str           # Short title
    authors: str         # Author list
    year: int
    arxiv: Optional[str] = None
    doi: Optional[str] = None
    description: Optional[str] = None  # Why this reference is relevant

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year
        }
        if self.arxiv:
            d["arxiv"] = self.arxiv
        if self.doi:
            d["doi"] = self.doi
        if self.description:
            d["description"] = self.description
        return d


@dataclass
class LearningResource:
    """A learning resource (video, tutorial, etc.) for a formula."""
    title: str
    url: str
    type: str = "video"  # video, tutorial, article, interactive
    duration: Optional[str] = None  # e.g., "15 min"
    level: str = "intermediate"  # beginner, intermediate, advanced
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "title": self.title,
            "url": self.url,
            "type": self.type,
            "level": self.level
        }
        if self.duration:
            d["duration"] = self.duration
        if self.description:
            d["description"] = self.description
        return d


@dataclass
class FormulaDerivation:
    """Derivation chain for a formula (Level 3 display)."""
    parent_formulas: List[str] = field(default_factory=list)
    established_physics: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    verification_page: Optional[str] = None
    comments: Optional[str] = None
    # Enhanced fields for three-level display
    assumptions: List[str] = field(default_factory=list)
    approximations: List[str] = field(default_factory=list)
    difficulty: str = "intermediate"  # beginner, intermediate, advanced
    method: str = "algebraic"  # geometric, algebraic, numerical

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "parentFormulas": self.parent_formulas,
            "establishedPhysics": self.established_physics,
            "steps": self.steps,
            "method": self.method,
            "difficulty": self.difficulty,
        }
        if self.verification_page:
            d["verificationPage"] = self.verification_page
        if self.comments:
            d["comments"] = self.comments
        if self.assumptions:
            d["assumptions"] = self.assumptions
        if self.approximations:
            d["approximations"] = self.approximations
        return d


@dataclass
class FormulaInfoItem:
    """Info grid item for formula panel (displays key facts about the formula)."""
    title: str
    content: str
    link: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"title": self.title, "content": self.content}
        if self.link:
            d["link"] = self.link
        return d


@dataclass
class FormulaSubComponent:
    """Clickable sub-component in expandable formula section."""
    symbol: str                           # HTML/Unicode symbol
    name: str                            # Component name
    description: str                     # Brief description
    link: Optional[str] = None           # URL to learn more
    badge: Optional[str] = None          # Badge text (e.g., "Established", "Mathematics")
    badge_type: str = "established"      # established, theory, mathematics

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "symbol": self.symbol,
            "name": self.name,
            "description": self.description,
            "badgeType": self.badge_type,
        }
        if self.link:
            d["link"] = self.link
        if self.badge:
            d["badge"] = self.badge
        return d


@dataclass
class FormulaDerivationStep:
    """Single step in derivation chain (path to established physics)."""
    title: str                           # e.g., "Dirac Equation (1928)"
    link: Optional[str] = None           # URL to learn more
    badge: Optional[str] = None          # Badge text (e.g., "Established")
    badge_type: str = "established"      # established, theory, mathematics

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "title": self.title,
            "badgeType": self.badge_type,
        }
        if self.link:
            d["link"] = self.link
        if self.badge:
            d["badge"] = self.badge
        return d


# ==============================================================================
# PARAMETER METADATA TEMPLATE (v17.0+)
# Standardized three-level display for all parameters
# ==============================================================================

class ParameterCategory:
    """Categories for parameter provenance tracking."""
    GEOMETRIC = "GEOMETRIC"           # Pure topology (χ_eff, b2, b3, n_gen)
    DERIVED = "DERIVED"               # Computed from geometry (M_GUT, τ_p)
    CALIBRATED = "CALIBRATED"         # Fitted to data (θ₁₃, δ_CP)
    INPUT = "INPUT"                   # Phenomenological input (M_Planck, m_H)
    PREDICTED = "PREDICTED"           # Testable predictions (M_KK, GW)
    EXPERIMENTAL = "EXPERIMENTAL"     # Reference experimental values
    PHENOMENOLOGICAL = "PHENOMENOLOGICAL"  # Legacy: fitted/phenomenological params


@dataclass
class ParameterMetadata:
    """
    Complete metadata for any physical parameter.
    Supports three-level display: Display (L1), Hover (L2), Expandable (L3).
    """
    # === LEVEL 1: DISPLAY (Always shown) ===
    id: str                               # Unique kebab-case ID
    value: float                          # Numerical value
    units: str                            # Physical units
    symbol: str                           # LaTeX/Unicode symbol
    status: str = ParameterCategory.DERIVED  # Category

    # === LEVEL 2: HOVER (Tooltip content) ===
    title: str = ""                       # Human-readable name
    description: str = ""                 # One-line description
    oom: Optional[float] = None           # Order of magnitude
    uncertainty: Optional[float] = None   # Absolute uncertainty
    uncertainty_percent: Optional[float] = None

    # Experimental comparison
    experimental_value: Optional[float] = None
    experimental_error: Optional[float] = None
    experimental_source: str = ""
    sigma_deviation: Optional[float] = None

    # === LEVEL 3: EXPANDABLE ===
    long_description: str = ""
    derivation: str = ""
    derivation_formula_ids: List[str] = field(default_factory=list)
    simulation_file: str = ""

    # Bidirectional references
    used_in_formulas: List[str] = field(default_factory=list)
    depends_on_params: List[str] = field(default_factory=list)
    section_refs: List[str] = field(default_factory=list)

    # Documentation
    references: List[str] = field(default_factory=list)
    notes: str = ""
    website_only_notes: str = ""

    # Testability
    testable: bool = False
    testable_by: str = ""
    testable_year: Optional[int] = None

    # Metadata
    version_introduced: str = ""
    last_updated: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Export to JSON-serializable dict."""
        return {
            # Level 1
            "id": self.id,
            "value": self.value,
            "units": self.units,
            "symbol": self.symbol,
            "status": self.status,
            "displayValue": f"{self.value} {self.units}",
            # Level 2
            "title": self.title,
            "description": self.description,
            "oom": self.oom,
            "uncertainty": self.uncertainty,
            "uncertaintyPercent": self.uncertainty_percent,
            "experimentalValue": self.experimental_value,
            "experimentalError": self.experimental_error,
            "experimentalSource": self.experimental_source,
            "sigmaDeviation": self.sigma_deviation,
            # Level 3
            "longDescription": self.long_description,
            "derivation": self.derivation,
            "derivationFormulaIds": self.derivation_formula_ids,
            "simulationFile": self.simulation_file,
            "usedInFormulas": self.used_in_formulas,
            "dependsOnParams": self.depends_on_params,
            "sectionRefs": self.section_refs,
            "references": self.references,
            "notes": self.notes,
            "websiteOnlyNotes": self.website_only_notes,
            "testable": self.testable,
            "testableBy": self.testable_by,
            "testableYear": self.testable_year,
            "versionIntroduced": self.version_introduced,
            "lastUpdated": self.last_updated,
        }


# ==============================================================================
# SECTION/CONTENT METADATA TEMPLATE (v17.0+)
# Standardized structure for paper sections and website pages
# ==============================================================================

@dataclass
class ContentBlock:
    """
    Single block of content within a section.
    Can be text, formula reference, parameter reference, figure, table, or nested container.
    """
    type: str                             # text, formula, param, figure, table, callout, grid, panel
    # For type="text"
    text: str = ""                        # Markdown/HTML text
    # For type="formula"
    formula_id: str = ""
    show_derivation: bool = False
    show_terms: bool = True
    # For type="param"
    param_id: str = ""
    display_mode: str = "inline"          # inline, card, full
    # For type="figure"
    figure_id: str = ""
    caption: str = ""
    alt_text: str = ""
    # For type="table"
    table_id: str = ""
    columns: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)
    # For type="callout"
    callout_type: str = "info"            # info, warning, derivation, example
    title: str = ""
    # For nested types (grid, panel, callout)
    children: List['ContentBlock'] = field(default_factory=list)
    columns_count: int = 2                # For grid layout
    # Visibility flags
    paper_only: bool = False
    website_only: bool = False
    expandable: bool = False              # Wrapped in accordion on website

    def to_dict(self) -> Dict[str, Any]:
        d = {"type": self.type}
        if self.type == "text":
            d["text"] = self.text
        elif self.type == "formula":
            d["formulaId"] = self.formula_id
            d["showDerivation"] = self.show_derivation
            d["showTerms"] = self.show_terms
        elif self.type == "param":
            d["paramId"] = self.param_id
            d["displayMode"] = self.display_mode
        elif self.type == "figure":
            d["figureId"] = self.figure_id
            d["caption"] = self.caption
            d["altText"] = self.alt_text
        elif self.type == "table":
            d["tableId"] = self.table_id
            d["columns"] = self.columns
            d["rows"] = self.rows
        elif self.type == "callout":
            d["calloutType"] = self.callout_type
            d["title"] = self.title
            d["children"] = [c.to_dict() for c in self.children]
        elif self.type in ("grid", "panel"):
            d["columnsCount"] = self.columns_count
            d["children"] = [c.to_dict() for c in self.children]

        if self.paper_only:
            d["paperOnly"] = True
        if self.website_only:
            d["websiteOnly"] = True
        if self.expandable:
            d["expandable"] = True
        return d


@dataclass
class AppendixMetadata:
    """Appendix associated with a section."""
    id: str                               # Appendix letter (A, B, etc.)
    title: str
    content_blocks: List[ContentBlock] = field(default_factory=list)
    simulation_code: str = ""             # Python simulation code snippet
    simulation_file: str = ""             # File path
    parent_section: str = ""              # Section this appendix belongs to

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "contentBlocks": [b.to_dict() for b in self.content_blocks],
            "simulationCode": self.simulation_code,
            "simulationFile": self.simulation_file,
            "parentSection": self.parent_section,
        }


@dataclass
class SectionMetadata:
    """
    Complete metadata for paper/website sections.
    Enables dynamic rendering of both paper and website from single source.
    """
    # === IDENTIFICATION ===
    id: str                               # Section ID (1, 2, 2.1, A, etc.)
    title: str
    section_type: str = "section"         # section, subsection, appendix
    parent_id: str = ""                   # Parent section ID

    # === ABSTRACT ===
    abstract: str = ""                    # Section summary

    # === CONTENT ===
    content_blocks: List[ContentBlock] = field(default_factory=list)

    # === APPENDICES ===
    appendices: List[AppendixMetadata] = field(default_factory=list)

    # === REFERENCES ===
    formula_refs: List[str] = field(default_factory=list)
    param_refs: List[str] = field(default_factory=list)
    figure_refs: List[str] = field(default_factory=list)
    citation_refs: List[str] = field(default_factory=list)

    # === NAVIGATION ===
    prev_section: str = ""
    next_section: str = ""
    subsections: List[str] = field(default_factory=list)

    # === SOURCE MAPPING ===
    paper_line_start: int = 0
    paper_line_end: int = 0
    section_file: str = ""                # sections/*.html file

    # === WEBSITE ENHANCEMENTS ===
    beginner_summary: str = ""            # Simplified explanation
    key_takeaways: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    website_only_content: List[ContentBlock] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "sectionType": self.section_type,
            "parentId": self.parent_id,
            "abstract": self.abstract,
            "contentBlocks": [b.to_dict() for b in self.content_blocks],
            "appendices": [a.to_dict() for a in self.appendices],
            "formulaRefs": self.formula_refs,
            "paramRefs": self.param_refs,
            "figureRefs": self.figure_refs,
            "citationRefs": self.citation_refs,
            "prevSection": self.prev_section,
            "nextSection": self.next_section,
            "subsections": self.subsections,
            "paperLineStart": self.paper_line_start,
            "paperLineEnd": self.paper_line_end,
            "sectionFile": self.section_file,
            "beginnerSummary": self.beginner_summary,
            "keyTakeaways": self.key_takeaways,
            "learningObjectives": self.learning_objectives,
            "websiteOnlyContent": [b.to_dict() for b in self.website_only_content],
        }


@dataclass
class Formula:
    """
    Complete formula definition for PM framework.

    Matches the structure in js/formula-registry.js for seamless integration.
    Can be exported to JSON for use in theory_output.json.

    Supports multiple rendering modes:
    - Plain text (for paper with LaTeX)
    - HTML with subscripts/superscripts (website inline)
    - Hoverable terms with tooltips
    - Expandable derivation sections
    - Links to simulations, references, learning resources

    Example:
        generation_formula = Formula(
            id="generation-number",
        input_params=['topology.CHI_EFF'],
        output_params=['topology.n_gen'],
            label="(2.6) Three Generations",
            html="n<sub>gen</sub> = χ<sub>eff</sub>/48 = 144/48 = 3",
            latex="n_{gen} = \\\\frac{\\\\chi_{eff}}{48} = \\\\frac{144}{48} = 3",
            plain_text="n_gen = χ_eff/48 = 144/48 = 3",
            category=FormulaCategory.DERIVED,
            description="Number of fermion generations from G₂ topology",
            section="3.2",
            simulation_file="simulations/fermion_chirality_generations_v13_0.py",
            references=[FormulaReference("acharya2008", "G₂ Compactification", "Acharya et al.", 2008)],
        )
    """
    # === REQUIRED FIELDS ===
    id: str                 # Unique kebab-case identifier
    label: str              # Display label, e.g., "(2.6) Three Generations"
    html: str               # HTML with <sub>/<sup> for website
    latex: str              # LaTeX for paper/MathJax
    plain_text: str         # Plain Unicode text fallback
    category: str           # FormulaCategory constant
    description: str        # One-line description

    # === DISPLAY OPTIONS ===
    attribution: str = "Principia Metaphysica"
    status: Optional[str] = None  # e.g., "EXACT MATCH", "TESTABLE", "VERIFIED"
    section: Optional[str] = None  # Paper section, e.g., "3.2"
    paper_page: Optional[int] = None  # Page in paper

    # === TERMS (hoverable) ===
    terms: Dict[str, FormulaTerm] = field(default_factory=dict)

    # === DERIVATION ===
    derivation: Optional[FormulaDerivation] = None

    # === NUMERICAL VALUES ===
    computed_value: Optional[float] = None  # Computed result
    units: Optional[str] = None             # e.g., "GeV", "years"
    experimental_value: Optional[float] = None
    experimental_error: Optional[float] = None
    sigma_deviation: Optional[float] = None

    # === LINKS & RESOURCES ===
    simulation_file: Optional[str] = None   # Path to simulation file
    verification_simulation: Optional[str] = None  # Simulation that validates this
    references: List[FormulaReference] = field(default_factory=list)
    learning_resources: List[LearningResource] = field(default_factory=list)
    related_formulas: List[str] = field(default_factory=list)  # IDs of related formulas

    # === PARAMETER LINKAGE (for bi-directional refs) ===
    input_params: List[str] = field(default_factory=list)   # Parameter IDs this formula uses
    output_params: List[str] = field(default_factory=list)  # Parameter IDs this formula computes
    reference_ids: List[str] = field(default_factory=list)  # Reference IDs (for central lookup)

    # === COMMENTS ===
    notes: Optional[str] = None  # Additional notes/caveats
    testability: Optional[str] = None  # How/when this can be tested

    # === RICH UX RENDERING (for interactive formulas like index.html) ===
    # Interactive HTML display
    html_interactive: Optional[str] = None  # HTML with formula-var spans for hover tooltips

    # Info panel (formula meaning and context)
    info_title: Optional[str] = None        # e.g., "Unified 26-dimensional Action Principle"
    info_meaning: Optional[str] = None      # Long description of what the formula means
    info_grid: List[FormulaInfoItem] = field(default_factory=list)  # Key facts grid
    use_cases: List[str] = field(default_factory=list)  # What emerges from this formula

    # Expandable section
    expansion_title: Optional[str] = None   # Plain text LaTeX as section title
    sub_components: List[FormulaSubComponent] = field(default_factory=list)  # Clickable components
    derivation_chain: List[FormulaDerivationStep] = field(default_factory=list)  # Path to established physics

    # Discussion for paper rendering
    discussion: Optional[str] = None  # Detailed discussion for paper/website context

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary for theory_output.json."""
        d = {
            "id": self.id,
            "label": self.label,
            "html": self.html,
            "latex": self.latex,
            "plainText": self.plain_text,
            "category": self.category,
            "description": self.description,
            "attribution": self.attribution,
        }
        # Display options
        if self.status:
            d["status"] = self.status
        if self.section:
            d["section"] = self.section
        if self.paper_page:
            d["paperPage"] = self.paper_page

        # Terms (hoverable)
        if self.terms:
            d["terms"] = {k: v.to_dict() for k, v in self.terms.items()}

        # Derivation
        if self.derivation:
            d["derivation"] = self.derivation.to_dict()

        # Numerical values
        if self.computed_value is not None:
            d["computedValue"] = self.computed_value
        if self.units:
            d["units"] = self.units
        if self.experimental_value is not None:
            d["experimentalValue"] = self.experimental_value
        if self.experimental_error is not None:
            d["experimentalError"] = self.experimental_error
        if self.sigma_deviation is not None:
            d["sigmaDeviation"] = self.sigma_deviation

        # Links & Resources
        if self.simulation_file:
            d["simulationFile"] = self.simulation_file
        if self.verification_simulation:
            d["verificationSimulation"] = self.verification_simulation
        if self.references:
            d["references"] = [r.to_dict() for r in self.references]
        if self.learning_resources:
            d["learningResources"] = [r.to_dict() for r in self.learning_resources]
        if self.related_formulas:
            d["relatedFormulas"] = self.related_formulas

        # Parameter linkage
        if self.input_params:
            d["inputParams"] = self.input_params
        if self.output_params:
            d["outputParams"] = self.output_params
        if self.reference_ids:
            d["referenceIds"] = self.reference_ids

        # Comments
        if self.notes:
            d["notes"] = self.notes
        if self.testability:
            d["testability"] = self.testability

        # Rich UX rendering
        if self.html_interactive:
            d["htmlInteractive"] = self.html_interactive
        if self.info_title:
            d["infoTitle"] = self.info_title
        if self.info_meaning:
            d["infoMeaning"] = self.info_meaning
        if self.info_grid:
            d["infoGrid"] = [item.to_dict() for item in self.info_grid]
        if self.use_cases:
            d["useCases"] = self.use_cases
        if self.expansion_title:
            d["expansionTitle"] = self.expansion_title
        if self.sub_components:
            d["subComponents"] = [comp.to_dict() for comp in self.sub_components]
        if self.derivation_chain:
            d["derivationChain"] = [step.to_dict() for step in self.derivation_chain]
        if self.discussion:
            d["discussion"] = self.discussion

        return d
