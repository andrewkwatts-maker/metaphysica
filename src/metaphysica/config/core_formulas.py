"""CoreFormulas - the foundational Principia Metaphysica equations.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""

from typing import Dict, List, Any

from .version import VERSION
from .formula import Formula, FormulaCategory, FormulaDerivation, FormulaDerivationStep, FormulaInfoItem, FormulaReference, FormulaSubComponent, FormulaTerm, LearningResource


# ==============================================================================
# CORE FORMULAS - Foundational PM equations
# ==============================================================================

class CoreFormulas:
    """
    Central repository of key PM formulas for export to theory_output.json.
    These are the most important formulas that should be tracked and validated.
    """

    GENERATION_NUMBER = Formula(
        id="generation-number",
        input_params=['topology.CHI_EFF'],
        output_params=['topology.n_gen'],
        label="(4.2) Three Generations",
        html="n<sub>gen</sub> = χ<sub>eff</sub>/48 = 144/48 = 3",
        latex="n_{gen} = \\frac{\\chi_{eff}}{48} = \\frac{144}{48} = 3",
        plain_text="n_gen = χ_eff/48 = 144/48 = 3",
        category=FormulaCategory.DERIVED,
        description="Number of fermion generations from G₂ topology",
        section="4",
        status="EXACT MATCH",
        terms={
            "n_gen": FormulaTerm(
                name="Number of Generations",
                description="The number of fermion families in the Standard Model",
                link="sections/fermion-sector.html",
                symbol="n_gen",
                units="dimensionless",
                contribution="The count we aim to derive from topology"
            ),
            "χ_eff": FormulaTerm(
                name="Effective Euler Characteristic",
                description="Topological invariant from TCS G₂ manifold construction",
                symbol="χ_eff",
                value="144",
                units="dimensionless",
                contribution="Geometric input from TCS construction",
                link="foundations/g2-manifold.html"
            ),
            "48": FormulaTerm(
                name="G₂ Index Divisor",
                description="From G₂ index theorem (twice F-theory's divisor of 24)",
                symbol="48",
                value="48",
                units="dimensionless",
                contribution="Topological constraint from G₂ holonomy",
                link="foundations/f-theory.html"
            ),
        },
        info_title="Three Generations from Topology",
        info_meaning="This formula demonstrates that the number of fermion generations emerges directly from the topology of the G₂ manifold. Using the effective Euler characteristic χ_eff = 144 from the TCS construction, the G₂ index theorem yields exactly three generations—matching the observed particle spectrum without any free parameters.",
        info_grid=[
            FormulaInfoItem(
                title="Topology Source",
                content="TCS G₂ Manifold #187",
                link="foundations/g2-manifold.html"
            ),
            FormulaInfoItem(
                title="χ_eff Value",
                content="144 (from Hodge numbers)",
                link="sections/topology.html"
            ),
            FormulaInfoItem(
                title="Index Divisor",
                content="48 (from G₂ theorem)",
                link="foundations/f-theory.html"
            ),
            FormulaInfoItem(
                title="Result",
                content="n_gen = 3 exactly",
                link="sections/fermion-sector.html"
            ),
        ],
        expansion_title="n_{gen} = \\frac{\\chi_{eff}}{48} = \\frac{144}{48} = 3",
        sub_components=[
            FormulaSubComponent(
                symbol="χ_eff",
                name="Effective Euler Characteristic",
                description="From TCS G₂ manifold construction",
                badge="DERIVED",
                badge_type="theory"
            ),
            FormulaSubComponent(
                symbol="48",
                name="Index Divisor",
                description="From G₂ index theorem",
                badge="ESTABLISHED",
                badge_type="established"
            ),
            FormulaSubComponent(
                symbol="144",
                name="Topological Invariant",
                description="2(h¹¹ - h²¹ + h³¹) = 2(4 - 0 + 68)",
                badge="GEOMETRIC",
                badge_type="mathematics"
            ),
        ],
        derivation_chain=[
            FormulaDerivationStep(
                title="TCS G₂ Manifold Construction",
                link="foundations/tcs.html",
                badge="MATHEMATICS",
                badge_type="mathematics"
            ),
            FormulaDerivationStep(
                title="F-theory Index Theorem",
                link="foundations/f-theory.html",
                badge="ESTABLISHED",
                badge_type="established"
            ),
            FormulaDerivationStep(
                title="G₂ Index Theorem",
                link="foundations/g2-manifold.html",
                badge="ESTABLISHED",
                badge_type="established"
            ),
        ],
        discussion="The generation number emerges directly from the topology of the G₂ manifold. Using the effective Euler characteristic χ_eff = 144 from the TCS construction (Corti et al. 2015), the G₂ index theorem—which generalizes the F-theory result n_gen = χ/24—yields exactly three generations via the divisor 48. This is a parameter-free geometric prediction that matches observation exactly.",
        derivation=FormulaDerivation(
            parent_formulas=["tcs-euler-characteristic"],
            established_physics=["f-theory-index"],
            steps=[
                "Start with G₂ manifold effective Euler characteristic χ_eff = 144",
                "Apply G₂ index theorem: n_gen = χ_eff/48 (twice F-theory divisor)",
                "Result: n_gen = 144/48 = 3 exactly"
            ],
            verification_page="sections/fermion-sector.html"
        ),
        simulation_file="simulations/fermion_chirality_generations_v13_0.py",
        computed_value=3,
        units="dimensionless",
        experimental_value=3,  # Source: PDG 2024 - three generations confirmed
        sigma_deviation=0.0,
        related_formulas=["tcs-topology", "effective-euler", "flux-quantization"],
        learning_resources=[
            LearningResource(
                title="G₂ Manifold - Wikipedia",
                url="https://en.wikipedia.org/wiki/G2_manifold",
                type="article",
                level="beginner",
                description="Overview of exceptional holonomy and basic properties of G₂ manifolds"
            ),
            LearningResource(
                title="Introduction to G₂ Geometry - Spiro Karigiannis",
                url="https://arxiv.org/abs/0807.3858",
                type="article",
                level="intermediate",
                duration="~2 hours reading",
                description="Comprehensive introduction to G₂ manifolds and their topology including Euler characteristics"
            ),
            LearningResource(
                title="Riemannian Holonomy Groups and Calibrated Geometry - Dominic Joyce",
                url="https://www.cambridge.org/core/books/riemannian-holonomy-groups-and-calibrated-geometry/",
                type="textbook",
                level="advanced",
                description="Definitive reference on G₂ manifolds, index theorems, and topological invariants (Chapters 10-13)"
            ),
        ],
        references=[
            FormulaReference(
                id="vafa1996",
                title="Evidence for F-Theory",
                authors="Vafa, C.",
                year=1996,
                arxiv="hep-th/9602022",
                description="F-theory index theorem: n_gen = χ/24 for D3-branes on CY4"
            ),
            FormulaReference(
                id="acharya2001_chiral",
                title="Chiral Fermions from Manifolds of G₂ Holonomy",
                authors="Acharya, B.S., Witten, E.",
                year=2001,
                arxiv="hep-th/0109152",
                description="Chiral fermions from M-theory on G₂ manifolds"
            ),
            FormulaReference(
                id="corti2015",
                title="G₂-manifolds and associative submanifolds via semi-Fano 3-folds",
                authors="Corti, A., Haskins, M., Nordström, J., Pacini, T.",
                year=2015,
                description="TCS construction: b₂=4, b₃=24, χ_eff=144"
            )
        ]
    )

    GUT_SCALE = Formula(
        id="gut-scale",
        input_params=['dimensions.D_EFFECTIVE'],
        output_params=['gauge.M_GUT'],
        label="(5.3) GUT Scale",
        html="M<sub>GUT</sub> = M<sub>Pl</sub> · V<sub>G₂</sub><sup>-1/7</sup> = 2.118 × 10<sup>16</sup> GeV",
        latex="M_{GUT} = M_{Pl} \\cdot V_{G_2}^{-1/7} = 2.118 \\times 10^{16}\\,\\text{GeV}",
        plain_text="M_GUT = M_Pl · V_G2^(-1/7) = 2.118 × 10^16 GeV",
        category=FormulaCategory.DERIVED,
        description="Grand unification scale from G₂ compactification volume",
        section="5",
        status="GEOMETRIC",
        terms={
            "M_GUT": FormulaTerm(
                name="GUT Scale",
                description="Grand unification mass scale where gauge couplings unify",
                symbol="M_GUT",
                value="2.118 × 10¹⁶ GeV",
                units="GeV",
                oom=16.33,
                contribution="The derived unification scale",
                link="sections.html#gauge-unification"
            ),
            "M_Pl": FormulaTerm(
                name="Planck Mass",
                description="Reduced Planck mass (fundamental quantum gravity scale)",
                symbol="M_Pl",
                value="2.435 × 10¹⁸ GeV",
                units="GeV",
                oom=18.39,
                contribution="Fundamental input scale",
                link="foundations/planck-scale.html"
            ),
            "V_G2": FormulaTerm(
                name="G₂ Volume",
                description="Compactification volume of G₂ manifold in Planck units",
                symbol="V_G₂",
                units="dimensionless",
                contribution="Geometric modulus from TCS topology",
                link="foundations/g2-manifold.html"
            ),
        },
        info_title="GUT Scale from G₂ Compactification",
        info_meaning="The grand unification scale emerges from dimensional reduction on the G₂ manifold. The compactification volume V_G₂ sets the ratio between the 26D Planck scale M* and the effective 4D GUT scale via M_GUT = M_Pl · V_G₂^(-1/7). This geometric origin naturally yields M_GUT ≈ 2.1×10¹⁶ GeV, precisely in the range needed for gauge coupling unification.",
        info_grid=[
            FormulaInfoItem(
                title="Planck Scale",
                content="M_Pl = 2.435 × 10¹⁸ GeV",
                link="foundations/planck-scale.html"
            ),
            FormulaInfoItem(
                title="Volume Power",
                content="-1/7 (from 7D compactification)",
                link="foundations/kaluza-klein.html"
            ),
            FormulaInfoItem(
                title="Computed Value",
                content="2.118 × 10¹⁶ GeV",
                link="sections.html#gauge-unification"
            ),
            FormulaInfoItem(
                title="Comparison",
                content="Standard GUT scale: 2 × 10¹⁶ GeV",
                link="foundations/grand-unification.html"
            ),
        ],
        expansion_title="M_{GUT} = M_{Pl} \\cdot V_{G_2}^{-1/7} = 2.118 \\times 10^{16}\\,\\text{GeV}",
        sub_components=[
            FormulaSubComponent(
                symbol="M_Pl",
                name="Planck Mass",
                description="Fundamental gravity scale: 2.435 × 10¹⁸ GeV",
                badge="ESTABLISHED",
                badge_type="established"
            ),
            FormulaSubComponent(
                symbol="V_G₂",
                name="G₂ Volume",
                description="From moduli stabilization via racetrack potential",
                badge="DERIVED",
                badge_type="theory"
            ),
            FormulaSubComponent(
                symbol="-1/7",
                name="Dimensional Reduction",
                description="Power from 7D compactification (Kaluza-Klein)",
                badge="ESTABLISHED",
                badge_type="established"
            ),
        ],
        derivation_chain=[
            FormulaDerivationStep(
                title="Kaluza-Klein Compactification",
                link="foundations/kaluza-klein.html",
                badge="ESTABLISHED",
                badge_type="established"
            ),
            FormulaDerivationStep(
                title="G₂ Manifold Geometry",
                link="foundations/g2-manifold.html",
                badge="MATHEMATICS",
                badge_type="mathematics"
            ),
            FormulaDerivationStep(
                title="Moduli Stabilization",
                link="sections/moduli-stabilization.html",
                badge="THEORY",
                badge_type="theory"
            ),
        ],
        discussion="The GUT scale emerges from the geometry of the G₂ compactification. Via dimensional reduction, the effective 4D Planck scale is related to the 26D fundamental scale by M_GUT = M_Pl · V_G₂^(-1/7), where the -1/7 power comes from compactifying 7 dimensions. The TCS topology and moduli stabilization fix V_G₂, yielding M_GUT = 2.118×10¹⁶ GeV—remarkably close to the phenomenologically required unification scale of ~2×10¹⁶ GeV.",
        derivation=FormulaDerivation(
            parent_formulas=["g2-compactification"],
            established_physics=["kaluza-klein"],
            steps=[
                "G₂ manifold volume V_G2 determines effective 4D Planck scale",
                "Dimensional reduction: M_GUT = M_Pl · V_G2^(-1/7)",
                "From TCS topology: V_G2 yields M_GUT = 2.118×10¹⁶ GeV"
            ],
            verification_page="sections.html#gauge-unification"
        ),
        simulation_file="simulations/gauge_unification_precision_v12_4.py",
        computed_value=2.118e16,
        units="GeV",
        related_formulas=["tcs-topology", "gut-coupling", "planck-mass-derivation", "kappa-gut-coefficient"],
        learning_resources=[
            LearningResource(
                title="Grand Unified Theory - Wikipedia",
                url="https://en.wikipedia.org/wiki/Grand_Unified_Theory",
                type="article",
                level="beginner",
                description="Overview of GUT models and experimental tests including gauge coupling unification"
            ),
            LearningResource(
                title="Grand Unification - Paul Langacker",
                url="https://arxiv.org/abs/0901.0241",
                type="article",
                level="intermediate",
                duration="~3 hours reading",
                description="Review of GUT models including SO(10) and gauge coupling unification scale"
            ),
            LearningResource(
                title="Gauge Theories in Particle Physics - Aitchison & Hey",
                url="https://www.taylorfrancis.com/books/mono/10.1201/b14664/gauge-theories-particle-physics-ian-aitchison-anthony-hey",
                type="textbook",
                level="advanced",
                description="Standard textbook for gauge theory and unification (Chapters 15-17 on GUT theories, SO(10), symmetry breaking)"
            ),
        ],
        references=[
            FormulaReference(
                id="acharya1998",
                title="M Theory, Joyce Orbifolds and Super Yang-Mills",
                authors="Acharya, B.S.",
                year=1998,
                description="M-theory on G₂: ADE singularities yield SO(10)"
            ),
            FormulaReference(
                id="acharya2003_freund",
                title="Freund-Rubin Revisited",
                authors="Acharya, B.S., Denef, F., Hofman, C., Lambert, N.",
                year=2003,
                arxiv="hep-th/0211051",
                description="Moduli stabilization and scale hierarchies in M-theory on G₂"
            )
        ]
    )

    DARK_ENERGY_W0 = Formula(
        id="dark-energy-w0",
        input_params=['topology.elder_kads'],
        output_params=['dark_energy.w0'],
        label="(7.1) Dark Energy EoS",
        html="w₀ = -(b₃ - 1)/b₃ = -23/24 = -0.9583",
        latex="w_0 = -\\frac{b_3 - 1}{b_3} = -\\frac{23}{24} = -0.9583",
        plain_text="w₀ = -(b₃ - 1)/b₃ = -23/24 = -0.9583",
        category=FormulaCategory.PREDICTIONS,
        description="Dark energy equation of state from pure G2 topology (v16.2 STERILE)",
        section="7",
        status="ANCHOR-DEPENDENT: 0.027σ vs adopted thawing anchor; 3.6σ vs DESI DR2 w0waCDM headline",
        terms={
            "w₀": FormulaTerm(
                name="Dark Energy Equation of State",
                description="Ratio of pressure to energy density at present epoch (z=0)",
                symbol="w₀",
                value="-0.9583",
                units="dimensionless",
                contribution="The predicted present-day dark energy parameter from pure geometry"
            ),
            "b₃": FormulaTerm(
                name="Third Betti Number",
                description="G₂ manifold topological invariant counting associative 3-cycles",
                symbol="b₃",
                value="24",
                units="dimensionless",
                contribution="Fixed by G₂ holonomy - TCS manifold with 24 associative cycles"
            ),
        },
        info_title="Dark Energy from G₂ Topology (STERILE)",
        info_meaning="v16.2 STERILE: Dark energy's equation of state emerges directly from the G₂ manifold's third Betti number b₃ = 24. The formula w₀ = -(b₃-1)/b₃ = -23/24 = -0.9583 is pure topology with zero free parameters. Against the framework-adopted thawing anchor (w₀ = -0.957 ± 0.05; attribution unverified) this is 0.027σ; against the DESI DR2 w0waCDM headline (w₀ = -0.752 ± 0.057) it is 3.6σ. The comparison is anchor/model dependent.",
        info_grid=[
            FormulaInfoItem(title="Predicted Value", content="w₀ = -23/24 = -0.9583"),
            FormulaInfoItem(title="DESI 2025", content="-0.957 ± 0.05"),
            FormulaInfoItem(title="Agreement", content="0.027σ (adopted anchor) / 3.6σ (DESI DR2 w0waCDM headline)"),
            FormulaInfoItem(title="Mechanism", content="Pure G₂ topology"),
        ],
        expansion_title="w_0 = -\\frac{b_3 - 1}{b_3} = -\\frac{24 - 1}{24} = -\\frac{23}{24} = -0.9583",
        sub_components=[
            FormulaSubComponent(symbol="-1", name="Cosmological Constant", description="Pure vacuum energy contribution", badge="ESTABLISHED", badge_type="established"),
            FormulaSubComponent(symbol="b₃", name="Third Betti Number", description="G₂ manifold associative 3-cycle count: b₃ = 24", badge="TOPOLOGY", badge_type="theory"),
            FormulaSubComponent(symbol="1/b₃", name="Breathing-Mode Correction", description="Deviation from ΛCDM: w₀ = -1 + 1/b₃", badge="RETRODICTED", badge_type="theory"),
        ],
        derivation_chain=[
            FormulaDerivationStep(title="G₂ Manifold Topology (b₃ = 24)", badge="GEOMETRY", badge_type="mathematics"),
            FormulaDerivationStep(title="Breathing-Mode Vacuum Relaxation", badge="THEORY", badge_type="theory"),
            FormulaDerivationStep(title="w₀ = -(b₃-1)/b₃ Retrodiction vs DESI", badge="RETRODICTED", badge_type="theory"),
        ],
        discussion="The dark energy equation of state parameter w₀ = -(b₃-1)/b₃ = -23/24 ≈ -0.9583 follows from the breathing-mode relaxation of the G₂ vacuum with b₃ = 24 associative cycles. Compared against the DESI thawing-quintessence anchor w₀ = -0.957 ± 0.067 the agreement is 0.02σ. Honesty note: the b₃-based form replaced an earlier thermal-time candidate (w₀ = -1 + 2/(3α_T) = -0.8528) after DESI data arrived, so this is a retrodiction, not an a-priori prediction — see the dark_energy module's assessment header.",
        derivation=FormulaDerivation(
            parent_formulas=["betti-numbers", "breathing-mode"],
            established_physics=["desi-2024-baO", "friedmann-equations"],
            steps=[
                "G₂ compactification fixes b₃ = 24 associative 3-cycles",
                "Vacuum breathing mode relaxes w by one part in b₃",
                "Result: w₀ = -1 + 1/b₃ = -23/24 ≈ -0.9583"
            ],
            verification_page="sections/cosmology.html"
        ),
        simulation_file="simulations/wz_evolution_desi_dr2.py",
        computed_value=-0.9583,
        units="dimensionless",
        experimental_value=-0.957,  # DESI thawing-quintessence anchor w_0 = -0.957 ± 0.067
        sigma_deviation=0.027,
        related_formulas=["dark-energy-wa", "thermal-time", "kms-condition", "effective-dimension"],
        learning_resources=[
            LearningResource(
                title="Dark Energy Explained - PBS Space Time",
                url="https://www.youtube.com/c/pbsspacetime",
                type="video",
                level="beginner",
                duration="15-20 min",
                description="Introduction to dark energy and cosmic acceleration (search 'dark energy')"
            ),
            LearningResource(
                title="Dark Energy - Edmund Copeland, M. Sami, Shinji Tsujikawa",
                url="https://arxiv.org/abs/hep-th/0603057",
                type="article",
                level="intermediate",
                duration="~4 hours reading",
                description="Comprehensive review of dark energy models and equation of state w(z)"
            ),
            LearningResource(
                title="Modern Cosmology - Scott Dodelson & Fabian Schmidt",
                url="https://www.sciencedirect.com/book/9780128159484/modern-cosmology",
                type="textbook",
                level="advanced",
                description="Standard modern cosmology textbook (Chapters 6-8 on dark energy, equation of state, observational tests)"
            ),
        ],
        references=[
            FormulaReference(
                id="connes1994",
                title="Von Neumann Algebra Automorphisms and Time-Thermodynamics Relation",
                authors="Connes, A., Rovelli, C.",
                year=1994,
                arxiv="gr-qc/9406019",
                description="Thermal time hypothesis: time emerges from statistical flow"
            ),
            FormulaReference(
                id="desi2024",
                title="DESI 2024 VI: Cosmological Constraints from BAO",
                authors="DESI Collaboration",
                year=2024,
                arxiv="2404.03002",
                description="Experimental validation: w₀ = -0.827 ± 0.063"
            )
        ],
    )

    PROTON_LIFETIME = Formula(
        id="proton-lifetime",
        input_params=['gauge.M_GUT', 'gauge.ALPHA_GUT'],
        output_params=['proton_decay.tau_p_years'],
        label="(5.10) Proton Lifetime",
        html="τ<sub>p</sub> = M<sub>GUT</sub>⁴/(α<sub>GUT</sub>² m<sub>p</sub>⁵) × S² = 8.15 × 10<sup>34</sup> years",
        latex="\\tau_p = \\frac{M_{GUT}^4}{\\alpha_{GUT}^2 m_p^5} \\times S^2 = 8.15 \\times 10^{34}\\,\\text{years}",
        plain_text="τ_p = M_GUT⁴/(α_GUT² m_p⁵) × S² = 8.15 × 10³⁴ years",
        category=FormulaCategory.PREDICTIONS,
        description="Proton lifetime from GUT scale with TCS suppression",
        section="5",
        status="TESTABLE (Hyper-K ~2030s)",
        terms={
            "τ_p": FormulaTerm(
                name="Proton Lifetime",
                description="Characteristic timescale for proton decay via p → e⁺π⁰ channel",
                symbol="τ_p",
                value="8.15 × 10³⁴ years",
                units="years",
                oom=34.91,
                contribution="The predicted proton decay lifetime",
                link="sections/proton-decay.html"
            ),
            "M_GUT": FormulaTerm(
                name="GUT Scale",
                description="Grand unification mass scale from G₂ compactification",
                symbol="M_GUT",
                value="2.118 × 10¹⁶ GeV",
                units="GeV",
                oom=16.33,
                contribution="Sets the suppression scale for decay operators",
                link="sections.html#gauge-unification"
            ),
            "α_GUT": FormulaTerm(
                name="GUT Coupling",
                description="Unified gauge coupling constant at M_GUT",
                symbol="α_GUT",
                value="1/23.54 ≈ 0.0425",
                units="dimensionless",
                contribution="Strength of dimension-6 operators",
                link="sections.html#gauge-unification"
            ),
            "S": FormulaTerm(
                name="Geometric Suppression Factor",
                description="Additional suppression from TCS cycle separation",
                symbol="S",
                value="~2.1",
                units="dimensionless",
                contribution="Enhances lifetime by S² ≈ 4.4",
                link="foundations/tcs.html"
            ),
        },
        info_title="Proton Decay from GUT Scale",
        info_meaning="Proton decay is a key prediction of grand unified theories. The lifetime scales as τ_p ∝ M_GUT⁴/(α_GUT² m_p⁵) from dimension-6 baryon-number-violating operators. The TCS geometry provides an additional suppression factor S² ≈ 4.4 from cycle separation, pushing the predicted lifetime to 8.15×10³⁴ years—just above the Super-Kamiokande bound and within reach of Hyper-Kamiokande.",
        info_grid=[
            FormulaInfoItem(
                title="GUT Scale",
                content="M_GUT = 2.118 × 10¹⁶ GeV",
                link="sections.html#gauge-unification"
            ),
            FormulaInfoItem(
                title="GUT Coupling",
                content="α_GUT = 1/23.54",
                link="sections.html#gauge-unification"
            ),
            FormulaInfoItem(
                title="TCS Suppression",
                content="S² ≈ 4.4",
                link="foundations/tcs.html"
            ),
            FormulaInfoItem(
                title="Predicted Lifetime",
                content="8.15 × 10³⁴ years",
                link="sections/proton-decay.html"
            ),
        ],
        expansion_title="\\tau_p = \\frac{M_{GUT}^4}{\\alpha_{GUT}^2 m_p^5} \\times S^2 = 8.15 \\times 10^{34}\\,\\text{years}",
        sub_components=[
            FormulaSubComponent(
                symbol="M_GUT⁴",
                name="GUT Scale Suppression",
                description="Fourth power from dimension-6 operator",
                badge="DERIVED",
                badge_type="theory"
            ),
            FormulaSubComponent(
                symbol="α_GUT²",
                name="Coupling Strength",
                description="Squared unified coupling constant",
                badge="DERIVED",
                badge_type="theory"
            ),
            FormulaSubComponent(
                symbol="m_p⁵",
                name="Proton Mass Factor",
                description="Phase space suppression (dimensional analysis)",
                badge="ESTABLISHED",
                badge_type="established"
            ),
            FormulaSubComponent(
                symbol="S²",
                name="TCS Geometric Factor",
                description="Cycle separation enhancement ≈ 4.4",
                badge="GEOMETRIC",
                badge_type="mathematics"
            ),
        ],
        derivation_chain=[
            FormulaDerivationStep(
                title="Dimension-6 Operators (GUT)",
                link="foundations/grand-unification.html",
                badge="ESTABLISHED",
                badge_type="established"
            ),
            FormulaDerivationStep(
                title="GUT Scale from G₂",
                link="sections.html#gauge-unification",
                badge="DERIVED",
                badge_type="theory"
            ),
            FormulaDerivationStep(
                title="TCS Geometric Suppression",
                link="foundations/tcs.html",
                badge="MATHEMATICS",
                badge_type="mathematics"
            ),
        ],
        discussion="The proton lifetime is calculated from the standard GUT formula τ_p ∝ M_GUT⁴/(α_GUT² m_p⁵), using the geometrically determined values M_GUT = 2.118×10¹⁶ GeV and α_GUT = 1/23.54. The TCS manifold geometry provides an additional suppression factor S ≈ 2.1 from the separation between associative 3-cycles, enhancing the lifetime by S² ≈ 4.4. This yields τ_p = 8.15×10³⁴ years, safely above the Super-Kamiokande bound of 2.4×10³⁴ years and testable at Hyper-Kamiokande in the 2030s.",
        derivation=FormulaDerivation(
            parent_formulas=["gut-scale", "tcs-suppression"],
            established_physics=["yang-mills"],
            steps=[
                "Standard dimension-6 decay: τ_p ∝ M_GUT⁴/(α_GUT² m_p⁵)",
                "TCS geometry provides additional suppression S = 2.1 from cycle separation",
                "Result: τ_p = 8.15×10³⁴ years (4.9× Super-K bound)"
            ],
            verification_page="sections.html#gauge-unification"
        ),
        simulation_file="simulations/proton_decay_geometric_v13_0.py",
        # Canonical ruling: registry proton_decay chain value (the old
        # 8.15e34 literal was a stale config-only number).
        computed_value=4.757e34,
        units="years",
        related_formulas=["gut-scale", "gut-coupling", "proton-branching", "doublet-triplet"],
        learning_resources=[
            LearningResource(
                title="Proton Decay - Wikipedia",
                url="https://en.wikipedia.org/wiki/Proton_decay",
                type="article",
                level="beginner",
                description="Phenomenon, experimental bounds, and theoretical predictions from GUT theories"
            ),
            LearningResource(
                title="Proton Decay in GUT Theories - Review",
                url="https://arxiv.org/abs/hep-ph/0001293",
                type="article",
                level="intermediate",
                duration="~2 hours reading",
                description="Theoretical framework for proton decay in grand unified theories"
            ),
            LearningResource(
                title="The Standard Model and Beyond - Paul Langacker",
                url="https://www.routledge.com/The-Standard-Model-and-Beyond/Langacker/p/book/9781420079067",
                type="textbook",
                level="advanced",
                description="Comprehensive treatment of proton decay in GUTs (Chapters 12-13 on proton decay, dimension-6 operators)"
            ),
        ],
        references=[
            FormulaReference(
                id="georgi1974",
                title="Unity of All Elementary-Particle Forces",
                authors="Georgi, H., Glashow, S.L.",
                year=1974,
                description="Original SU(5) GUT with proton decay"
            ),
            FormulaReference(
                id="langacker1981",
                title="Grand Unified Theories and Proton Decay",
                authors="Langacker, P.",
                year=1981,
                description="Comprehensive review of GUT proton decay mechanisms"
            ),
            FormulaReference(
                id="sk2017",
                title="Search for proton decay via p → e⁺π⁰",
                authors="Super-Kamiokande Collaboration",
                year=2017,
                description="Experimental bound: τ(p → e⁺π⁰) > 2.4 × 10³⁴ years"
            )
        ],
    )

    THETA23_MAXIMAL = Formula(
        id="theta23-maximal",
        output_params=['neutrino.theta_23_pred', 'pmns.theta_23'],
        label="(6.1) Atmospheric Mixing",
        html="θ<sub>23</sub> = π/4 = 45° (G₂ holonomy symmetry)",
        latex="\\theta_{23} = \\frac{\\pi}{4} = 45^\\circ",
        plain_text="θ_23 = π/4 = 45° (G₂ holonomy symmetry)",
        category=FormulaCategory.SPECULATIVE,
        description=(
            "FALSIFIED elegant candidate (2026-08 ruling): maximal mixing "
            "θ_23 = π/4 = 45° from G₂ Z₂ symmetry is the zero-spare-variable "
            "form, but NuFIT places θ_23 in the upper octant (IO 49.3° ± 1.0 "
            "→ 4.3σ; NO 42.2° → 2.8σ). Retained on the books as falsified; "
            "the operative registry value is neutrino.theta_23_pred = 49.75°."
        ),
        section="6",
        status="FALSIFIED candidate (4.3σ vs NuFIT IO); registry uses 49.75°",
        terms={
            "θ_23": FormulaTerm("Atmospheric Angle", "PMNS mixing angle"),
            "G₂": FormulaTerm("G₂ Holonomy", "7D exceptional holonomy group"),
        },
        derivation=FormulaDerivation(
            parent_formulas=["g2-holonomy"],
            established_physics=[],
            steps=[
                "G₂ holonomy provides Z₂ symmetry between 2nd and 3rd generation",
                "This discrete symmetry would enforce θ_23 = π/4 exactly",
                "NuFIT upper-octant data falsify exact maximality (4.3σ IO)"
            ],
            verification_page="sections/fermion-sector.html"
        ),
        simulation_file="simulations/derive_theta23_g2_v12_8.py",
        computed_value=45.0,
        units="degrees",
        experimental_value=49.3,  # NuFIT IO best fit θ_23 = 49.3° ± 1.0°
        sigma_deviation=4.3,
        related_formulas=["neutrino-mass-21", "neutrino-mass-31", "tcs-topology", "cp-phase-geometric", "ckm-elements"],
        learning_resources=[
            LearningResource(
                title="Neutrino Oscillations Explained - Fermilab",
                url="https://www.youtube.com/user/fermilab",
                type="video",
                level="beginner",
                duration="10-15 min",
                description="Introduction to neutrino masses and mixing including atmospheric angle"
            ),
            LearningResource(
                title="TASI Lectures on Neutrino Physics - André de Gouvêa",
                url="https://arxiv.org/abs/hep-ph/0411274",
                type="article",
                level="intermediate",
                duration="~4 hours reading",
                description="Comprehensive lecture notes on neutrino masses and mixing including PMNS matrix"
            ),
            LearningResource(
                title="Fundamentals of Neutrino Physics and Astrophysics - Giunti & Kim",
                url="https://global.oup.com/academic/product/fundamentals-of-neutrino-physics-and-astrophysics-9780198508717",
                type="textbook",
                level="advanced",
                description="Standard reference for neutrino physics (Chapters 6-8 on PMNS matrix, mass hierarchy, oscillations)"
            ),
        ],
        references=[
            FormulaReference(
                id="joyce2000",
                title="Compact Manifolds with Special Holonomy",
                authors="Joyce, D.D.",
                year=2000,
                description="Definitive text on G₂ geometry and holonomy groups"
            ),
            FormulaReference(
                id="bryant-1987",
                title="Metrics with exceptional holonomy",
                authors="Bryant, R.L.",
                year=1987,
                description="First construction of complete metrics with G₂ holonomy"
            ),
            FormulaReference(
                id="nufit2025",
                title="NuFIT 6.0",
                authors="Esteban, I., Gonzalez-Garcia, M.C., Maltoni, M., Schwetz, T., Zhou, A.",
                year=2025,
                description="Experimental data: θ₂₃ = 45.2° ± 1.3°"
            )
        ],
    )

    KK_GRAVITON = Formula(
        id="kk-graviton-mass",
        # Deliberate orphan: registry geometry.m_KK is the ratio-form
        # quantity (~3.4e15 GeV, mislabelled per the canonical ruling) —
        # binding it here would compare two different quantities. The
        # canonical 4.5 TeV comes from the warped/exponential form.
        label="(8.1) KK Graviton Mass",
        html="m<sub>KK,1</sub> = 1/R<sub>c</sub> = 5.0 TeV",
        latex="m_{KK,1} = \\frac{1}{R_c} = 5.0\\,\\text{TeV}",
        plain_text="m_KK,1 = 1/R_c = 5.0 TeV",
        category=FormulaCategory.PREDICTIONS,
        description="First KK graviton mode mass from compactification radius",
        section="8",
        status="HL-LHC TESTABLE",
        terms={
            "m_KK,1": FormulaTerm("First KK Mode", "Lowest graviton excitation mass"),
            "R_c": FormulaTerm("Compactification Radius", "G₂ manifold characteristic size"),
        },
        derivation=FormulaDerivation(
            parent_formulas=["g2-compactification"],
            established_physics=["kaluza-klein"],
            steps=[
                "KK tower masses: m_n = n/R_c",
                "R_c determined by M_GUT and volume: R_c = 1/(5.0 TeV)",
                "First mode at 5.0 TeV, accessible at HL-LHC"
            ],
            verification_page="sections.html#predictions"
        ),
        simulation_file="simulations/kk_spectrum_full.py",
        # Canonical ruling: 4.5 TeV warped/exponential form (registry
        # geometry.m_KK is the mislabelled ratio-form quantity — deliberate
        # non-binding; see canonical_values MKK entry).
        computed_value=4.5,
        units="TeV",
        related_formulas=["gut-scale", "tcs-topology", "planck-mass-derivation"],
        learning_resources=[
            LearningResource(
                title="Extra Dimensions Explained - PBS Space Time",
                url="https://www.youtube.com/c/pbsspacetime",
                type="video",
                level="beginner",
                duration="15-20 min",
                description="Introduction to compactified dimensions and Kaluza-Klein theory"
            ),
            LearningResource(
                title="Extra Dimensions in Particle Physics - Review",
                url="https://arxiv.org/abs/hep-ph/0404175",
                type="article",
                level="intermediate",
                duration="~3 hours reading",
                description="Phenomenology of extra dimensions and KK graviton signals"
            ),
            LearningResource(
                title="Gravity and Strings - Tomás Ortín",
                url="https://www.cambridge.org/core/books/gravity-and-strings/",
                type="textbook",
                level="advanced",
                description="Modern treatment of dimensional reduction (Chapters 8-9 on Kaluza-Klein reduction, compactification)"
            ),
        ],
        references=[
            FormulaReference(
                id="kaluza1921",
                title="Zum Unitätsproblem der Physik",
                authors="Kaluza, T.",
                year=1921,
                description="Original Kaluza-Klein theory"
            ),
            FormulaReference(
                id="arkani1998",
                title="The hierarchy problem and new dimensions at a millimeter",
                authors="Arkani-Hamed, N., Dimopoulos, S., Dvali, G.",
                year=1998,
                arxiv="hep-ph/9803315",
                description="Large extra dimensions and TeV-scale KK modes"
            )
        ],
    )

    # =========================================================================
    # SECTION 2: THE 27-DIMENSIONAL BULK (24,2) UNIFIED TIME
    # (Legacy variable names use "25D" for backward compatibility)
    # =========================================================================

    MASTER_ACTION_26D = Formula(
        id="master-action-27d",  # Updated ID for v23.1
        output_params=['dimensions.D_BULK'],
        label="(2.1) Master Action",
        html="S<sub>26</sub> = ∫ d<sup>26</sup>x √|G| [M<sub>*</sub><sup>24</sup>R<sub>26</sub> + Ψ̄<sub>P</sub>(iΓ<sup>M</sup>D<sub>M</sub> - m)Ψ<sub>P</sub> + ℒ<sub>bridge</sub>]",
        latex="S_{26} = \\int d^{26}x \\sqrt{|G_{(24,2)}|} \\left[ M_*^{25} R_{26} + \\bar{\\Psi}_P \\left( i\\Gamma^M D_M - m \\right) \\Psi_P + \\mathcal{L}_{\\text{bridge}} \\right]",
        plain_text="S_26 = ∫ d²⁶X √|G| [M*²⁴R₂₆ + Ψ̄_P(iΓᴹD_M - m)Ψ_P + ℒ_bridge]",
        category=FormulaCategory.THEORY,
        description="v23.1 Master action for 26D(24,2) bulk with Pneuma field and shadow-time directions sector",
        section="2",
        status="FOUNDATIONAL",
        terms={
            "S_26": FormulaTerm("26D Action", "Full action in the 26D(24,2) two-time bulk", "sections.html#2"),
            "M_*": FormulaTerm("Fundamental Scale", "26D Planck scale ~10¹⁶ GeV"),
            "R_26": FormulaTerm("Ricci Scalar", "26D curvature scalar"),
            "Ψ_P": FormulaTerm("Pneuma Field", "4096-component Weyl spinor of Cl(24,2)"),
            "ℒ_bridge": FormulaTerm("Bridge Lagrangian", "v23.1: 12×(2,0) bridge pairs + two shadow-time directions"),
        },
        derivation=FormulaDerivation(
            parent_formulas=[],
            established_physics=["virasoro-anomaly", "string-theory"],
            steps=[
                "Start with 26D(24,2) = 24 space + 2 times (one per shadow)",
                "Include Pneuma spinor field for fermionic DOF (4096 Weyl components of Cl(24,2))",
                "v23.1: Add shadow-time directions sector for dual-shadow structure"
            ],
            verification_page="sections.html#2"
        ),
        simulation_file="simulations/v21/bridge/bridge_pressure.py",
        units="dimensionless",
        related_formulas=["virasoro-anomaly", "v21-or-reduction"],
        learning_resources=[
            LearningResource(
                title="String Theory Explained - PBS Space Time",
                url="https://www.youtube.com/c/pbsspacetime",
                type="video",
                level="beginner",
                duration="15-20 min",
                description="Accessible introduction to string theory basics, critical dimension, and extra dimensions (search 'String Theory')"
            ),
            LearningResource(
                title="Lectures on String Theory - David Tong",
                url="http://www.damtp.cam.ac.uk/user/tong/string.html",
                type="article",
                level="intermediate",
                duration="~10 hours reading",
                description="Excellent freely available lecture notes with clear explanations of 26D bosonic string"
            ),
            LearningResource(
                title="String Theory Vol. 1 - Polchinski",
                url="https://doi.org/10.1017/CBO9780511816079",
                type="textbook",
                level="advanced",
                description="Standard graduate-level reference for string theory (Chapters 2-3 on Virasoro algebra, BRST quantization)"
            ),
        ],
        references=[
            FormulaReference(
                id="lovelace1971",
                title="Pomeron Form Factors and Dual Regge Cuts",
                authors="Lovelace, C.",
                year=1971,
                description="First derivation of D=26 critical dimension from Virasoro anomaly cancellation"
            ),
            FormulaReference(
                id="polchinski1998_vol1",
                title="String Theory Volume I: An Introduction to the Bosonic String",
                authors="Polchinski, J.",
                year=1998,
                description="Standard reference for bosonic string theory and D=26 requirement"
            ),
            FormulaReference(
                id="veneziano1968",
                title="Construction of a crossing-symmetric, Regge-behaved amplitude for linearly rising trajectories",
                authors="Veneziano, G.",
                year=1968,
                description="Original dual resonance model leading to string theory"
            )
        ]
    )

    VIRASORO_ANOMALY = Formula(
        id="virasoro-anomaly",
        input_params=['dimensions.D_BULK'],
        label="(2.2) Virasoro Anomaly Cancellation",
        html="c<sub>total</sub> = c<sub>matter</sub> + c<sub>ghost</sub> = D + (-26) = 0 ⟹ D = 26",
        latex="c_{\\text{total}} = c_{\\text{matter}} + c_{\\text{ghost}} = D + (-26) = 0 \\quad \\Rightarrow \\quad D = 26",
        plain_text="c_total = c_matter + c_ghost = D + (-26) = 0 ⟹ D = 26",
        category=FormulaCategory.DERIVED,
        description="Virasoro anomaly cancellation fixes critical dimension to 26",
        section="2",
        status="EXACT MATCH",
        terms={
            "c_total": FormulaTerm("Total Central Charge", "Must vanish for consistent string"),
            "c_matter": FormulaTerm("Matter Central Charge", "= D (spacetime dimension)"),
            "c_ghost": FormulaTerm("Ghost Central Charge", "= -26 (from reparametrization ghosts)"),
        },
        simulation_file="simulations/virasoro_anomaly_v12_8.py",
        computed_value=26,
        units="dimensionless",
        related_formulas=["master-action-26d"],
        learning_resources=[
            LearningResource(
                title="Virasoro Algebra - Wikipedia",
                url="https://en.wikipedia.org/wiki/Virasoro_algebra",
                type="article",
                level="beginner",
                description="Overview of central extension and highest-weight representations"
            ),
            LearningResource(
                title="Introduction to Conformal Field Theory - Joshua Qualls",
                url="https://arxiv.org/abs/1511.04074",
                type="article",
                level="intermediate",
                duration="~3 hours reading",
                description="Modern lecture notes on CFT with emphasis on Virasoro algebra and central charge"
            ),
            LearningResource(
                title="Conformal Field Theory - Di Francesco, Mathieu, Sénéchal",
                url="https://link.springer.com/book/10.1007/978-1-4612-2256-9",
                type="textbook",
                level="advanced",
                description="Comprehensive reference for conformal field theory and Virasoro algebra (Chapters 5-7 on central charge, representations)"
            ),
        ],
        references=[
            FormulaReference(
                id="lovelace1971_virasoro",
                title="Pomeron Form Factors and Dual Regge Cuts",
                authors="Lovelace, C.",
                year=1971,
                description="First derivation of c_ghost = -26"
            ),
            FormulaReference(
                id="polyakov1981",
                title="Quantum Geometry of Bosonic Strings",
                authors="Polyakov, A.M.",
                year=1981,
                description="Path integral formulation showing ghost contribution"
            ),
            FormulaReference(
                id="polchinski1998_virasoro",
                title="String Theory Volume I",
                authors="Polchinski, J.",
                year=1998,
                description="Comprehensive treatment of Virasoro algebra and anomaly cancellation"
            )
        ],
    )

    # v23.1: OR Reduction Operator (replaces Sp(2,R) constraints)
    V21_OR_REDUCTION = Formula(
        id="v21-or-reduction",
        input_params=['dimensions.D_BULK'],
        output_params=['dimensions.D_EFFECTIVE'],
        label="(2.3) v23.1 OR Reduction Operator",
        html="R<sub>⊥</sub> = [[0,-1],[1,0]], R<sub>⊥</sub>² = -I, det(R<sub>⊥</sub>) = 1",
        latex="R_\\perp = \\begin{pmatrix} 0 & -1 \\\\ 1 & 0 \\end{pmatrix}, \\quad R_\\perp^2 = -I, \\quad \\det(R_\\perp) = 1",
        plain_text="R_perp = [[0,-1],[1,0]], R_perp² = -I, det(R_perp) = 1",
        category=FormulaCategory.THEORY,
        description="v23.1 OR reduction operator for dual-shadow coordinate mapping with Möbius topology",
        section="2",
        status="v23.1 FOUNDATIONAL",
        terms={
            "R_⊥": FormulaTerm("OR Operator", "Maps between Normal and Mirror shadow coordinates"),
            "R_⊥²=-I": FormulaTerm("Möbius Property", "Spinor double-cover: ψ→-ψ after single traversal"),
            "det=1": FormulaTerm("Orientation", "Preserves orientation across shadows"),
        },
        derivation=FormulaDerivation(
            parent_formulas=[],
            established_physics=["clifford-algebra", "spinor-geometry"],
            steps=[
                "v23.1: 26D(24,2) = 24 space + 2 times (one per shadow); the Sp(2,R) gauge constraint controls ghosts",
                "Dual shadows 2×13D(12,1) connected via 12×(2,0) bridge pairs + two shadow-time directions",
                "OR reduction R_perp identifies physics across shadows",
                "R_perp² = -I gives Möbius double-cover for spinor topology"
            ]
        ),
        simulation_file="simulations/v21/sampling/or_reduction_v21.py",
        related_formulas=["master-action-26d", "reduction-cascade"],
        learning_resources=[
            LearningResource(
                title="Möbius Strip Topology - Wikipedia",
                url="https://en.wikipedia.org/wiki/M%C3%B6bius_strip",
                type="article",
                level="beginner",
                description="Introduction to Möbius topology and double-covers"
            ),
            LearningResource(
                title="Spinor Representations - Wikipedia",
                url="https://en.wikipedia.org/wiki/Spinor",
                type="article",
                level="intermediate",
                description="How spinors transform under 2π rotations (sign flip)"
            ),
            LearningResource(
                title="Clifford Algebras and Spin Groups",
                url="https://arxiv.org/abs/math-ph/0105040",
                type="article",
                level="advanced",
                description="Mathematical foundations of spinor representations"
            ),
        ],
        references=[
            FormulaReference(
                id="pm_v21_2026",
                title="Principia Metaphysica v21.0: Dual-Shadow Bridge Framework",
                authors="Watts, A.K.",
                year=2026,
                description="Introduction of OR reduction operator and two-time signature (24,2)"
            ),
            FormulaReference(
                id="joyce2000",
                title="Compact Manifolds with Special Holonomy",
                authors="Joyce, D.D.",
                year=2000,
                description="G2 holonomy manifolds for per-shadow compactification"
            ),
        ],
    )

    # Legacy alias for backward compatibility
    SP2R_CONSTRAINTS = V21_OR_REDUCTION  # DEPRECATED: Use V21_OR_REDUCTION

    RACETRACK_SUPERPOTENTIAL = Formula(
        id="racetrack-superpotential",
        input_params=['gauge.M_GUT'],
        output_params=['pneuma.VEV'],
        label="(2.6) Racetrack Superpotential",
        html="W(Ψ<sub>P</sub>) = A·e<sup>-aΨ<sub>P</sub></sup> - B·e<sup>-bΨ<sub>P</sub></sup>",
        latex="W(\\Psi_P) = A \\cdot e^{-a\\Psi_P} - B \\cdot e^{-b\\Psi_P}",
        plain_text="W(Ψ_P) = A·exp(-a·Ψ_P) - B·exp(-b·Ψ_P)",
        category=FormulaCategory.THEORY,
        description="Racetrack superpotential for Pneuma vacuum stabilization",
        section="2",
        terms={
            "W": FormulaTerm("Superpotential", "Generates F-term scalar potential"),
            "A,B": FormulaTerm("Amplitudes", "Order unity from instanton prefactors"),
            "a,b": FormulaTerm("Exponents", "a=2π/N_flux, b=2π/(N_flux+1) from topology"),
            "Ψ_P": FormulaTerm("Pneuma Modulus", "Scalar component of Pneuma field"),
        },
        derivation=FormulaDerivation(
            parent_formulas=["tcs-topology"],
            established_physics=["kklt-stabilization"],
            steps=[
                "Two hidden gauge sectors with different ranks give competing condensates",
                "Topological coefficients: a = 2π/24, b = 2π/25",
                "Minimum at ⟨Ψ_P⟩ = ln(Aa/Bb)/(a-b) ≈ 1.076"
            ]
        ),
        simulation_file="simulations/pneuma_full_potential_v14_1.py",
        related_formulas=["pneuma-vev", "scalar-potential"],
        references=[
            FormulaReference(
                id="kachru2003",
                title="de Sitter vacua in string theory",
                authors="Kachru, S., Kallosh, R., Linde, A., Trivedi, S.P.",
                year=2003,
                arxiv="hep-th/0301240",
                description="KKLT mechanism for stabilizing moduli via racetrack superpotential"
            ),
            FormulaReference(
                id="blanco2004",
                title="Racetrack Inflation",
                authors="Blanco-Pillado, J.J., Burgess, C.P., Cline, J.M., et al.",
                year=2004,
                arxiv="hep-th/0406230",
                description="Racetrack potential from competing non-perturbative effects"
            ),
            FormulaReference(
                id="burgess2003",
                title="de Sitter String Vacua from Supersymmetric D-terms",
                authors="Burgess, C.P., Kallosh, R., Quevedo, F.",
                year=2003,
                arxiv="hep-th/0309187",
                description="Alternative stabilization mechanisms"
            )
        ]
    )

    PNEUMA_VEV = Formula(
        id="pneuma-vev",
        output_params=['pneuma.VEV'],
        label="(2.9) Pneuma Field VEV",
        html="⟨Ψ<sub>P</sub>⟩ = ln(Aa/Bb)/(a - b) ≈ 1.076",
        latex="\\langle\\Psi_P\\rangle = \\frac{\\ln(Aa/Bb)}{a - b} \\approx 1.076",
        plain_text="⟨Ψ_P⟩ = ln(Aa/Bb)/(a - b) ≈ 1.076",
        category=FormulaCategory.DERIVED,
        description="Pneuma field VEV from racetrack minimum (dynamically selected)",
        section="2",
        status="DYNAMICALLY SELECTED",
        terms={
            "⟨Ψ_P⟩": FormulaTerm("Pneuma VEV", "Vacuum expectation value"),
            "a,b": FormulaTerm("Racetrack Exponents", "From topological flux quantization"),
        },
        simulation_file="simulations/pneuma_full_potential_v14_1.py",
        computed_value=1.076,
        units="dimensionless",
        related_formulas=["racetrack-superpotential"],
        references=[
            FormulaReference(
                id="kachru2003_vev",
                title="de Sitter vacua in string theory",
                authors="Kachru, S., Kallosh, R., Linde, A., Trivedi, S.P.",
                year=2003,
                arxiv="hep-th/0301240",
                description="F-term potential minimization from superpotential"
            ),
            FormulaReference(
                id="blanco2004_racetrack",
                title="Racetrack Inflation",
                authors="Blanco-Pillado, J.J., et al.",
                year=2004,
                arxiv="hep-th/0406230",
                description="Derivation of racetrack minimum"
            ),
            FormulaReference(
                id="giddings2002",
                title="Hierarchies from fluxes in string compactifications",
                authors="Giddings, S.B., Kachru, S., Polchinski, J.",
                year=2002,
                arxiv="hep-th/0105097",
                description="Flux stabilization mechanisms"
            )
        ]
    )

    # =========================================================================
    # SECTION 3: REDUCTION TO 13D SHADOW
    # =========================================================================

    REDUCTION_CASCADE = Formula(
        id="reduction-cascade",
        input_params=['dimensions.D_BULK'],
        output_params=['dimensions.D_EFFECTIVE'],
        label="(1.1) v23.1 Dimensional Cascade",
        html="26D<sub>(24,2)</sub> →<sup>12×(2,0) + S<sup>(2,0)</sup></sup> 2×13D<sub>(12,1)</sub> →<sup>per-shadow G₂</sup> 2×4D<sub>(3,1)</sub> →<sup>R<sub>⊥</sub></sup> 4D<sub>(3,1)</sub>",
        latex="\\text{26D}_{(24,2)} \\xrightarrow{12\\times(2,0)+S^{(2,0)}} 2\\times\\text{13D}_{(12,1)} \\xrightarrow{G_2} 2\\times\\text{4D}_{(3,1)} \\xrightarrow{R_\\perp} \\text{4D}_{(3,1)}",
        plain_text="26D_(24,2) → [12×(2,0) + S^(2,0)] → 2×13D_(12,1) → [per-shadow G₂] → 2×4D_(3,1) → [R_perp] → 4D_(3,1)",
        category=FormulaCategory.THEORY,
        description="v23.1 Dimensional cascade from 26D(24,2) bulk via dual shadows to 4D observable",
        section="1",
        status="v23.1 FOUNDATIONAL",
        terms={
            "26D_(24,2)": FormulaTerm("Bulk", "v23.1: 24 space + 2 times (one per shadow)"),
            "2×13D_(12,1)": FormulaTerm("Dual Shadows", "v23.1: Normal + Mirror shadows, each 12 space + 1 time (its own)"),
            "12×(2,0)": FormulaTerm("Bridge Pairs", "v23.1: 12 Euclidean bridge pairs connecting shadow dimensions"),
            "S^(2,0)": FormulaTerm("Sampler Data Fields", "v23.1: 2D Euclidean shadow-time directions (averaging sector)"),
            "per-shadow G₂": FormulaTerm("Compactification", "G₂ on (7,0) per shadow"),
            "R_⊥": FormulaTerm("OR Reduction", "Identifies physics across shadows"),
            "4D_(3,1)": FormulaTerm("Observable", "Our spacetime"),
        },
        units="dimensionless",
        related_formulas=["v21-or-reduction", "g2-compactification"],
        simulation_file="simulations/v21/descent/merged_descent_v21.py",
        references=[
            FormulaReference(
                id="pm_v21_cascade",
                title="Principia Metaphysica v21.0: Dual-Shadow Bridge Framework",
                authors="Watts, A.K.",
                year=2026,
                description="v21 dimensional cascade with two times (one per shadow) and dual shadows"
            ),
            FormulaReference(
                id="acharya1998_m_theory",
                title="M Theory, Joyce Orbifolds and Super Yang-Mills",
                authors="Acharya, B.S.",
                year=1998,
                description="M-theory on G₂ manifolds: 11D → 4D"
            ),
            FormulaReference(
                id="atiyah2001",
                title="M-Theory Dynamics On A Manifold Of G₂ Holonomy",
                authors="Atiyah, M.F., Witten, E.",
                year=2001,
                arxiv="hep-th/0107177",
                description="Comprehensive study of dimensional reduction via G₂ compactification"
            )
        ]
    )

    PRIMORDIAL_SPINOR_13D = Formula(
        id="primordial-spinor-13d",
        output_params=['geometry.spinor_13d'],
        input_params=['dimensions.D_EFFECTIVE'],
        label="(3.2) v21 Per-Shadow Spinor",
        html="Ψ<sub>64</sub> ∈ Spin(12,1), dim(Ψ) = 2<sup>[13/2]</sup> = 64 per shadow",
        latex="\\Psi_{64} \\in \\text{Spin}(12,1), \\quad \\dim(\\Psi) = 2^{[13/2]} = 64 \\text{ per shadow}",
        plain_text="Ψ_64 ∈ Spin(12,1), dim(Ψ) = 2^[13/2] = 64 per shadow",
        category=FormulaCategory.DERIVED,
        description="v21/v22: Per-shadow spinor in 13D(12,1) dual-shadow structure",
        section="3",
        status="v21.0 EXACT MATCH",
        terms={
            "Ψ_64": FormulaTerm("64-Component Spinor", "v21/v22: Per-shadow spinor from Spin(12,1) in 13D"),
            "Spin(12,1)": FormulaTerm("Spin Group", "v21/v22: Per-shadow 13D Lorentz spinor representation"),
        },
        computed_value=64,
        units="dimensionless",
        related_formulas=["reduction-cascade"],
        simulation_file="simulations/g2_spinor_geometry_validation_v13_0.py",
        references=[
            FormulaReference(
                id="dirac1928",
                title="The Quantum Theory of the Electron",
                authors="Dirac, P.A.M.",
                year=1928,
                description="Original spinor formulation"
            ),
            FormulaReference(
                id="cartan1913",
                title="Les groupes projectifs qui ne laissent invariante aucune multiplicité plane",
                authors="Cartan, É.",
                year=1913,
                description="Classification of spinor representations"
            ),
            FormulaReference(
                id="lawson1989",
                title="Spin Geometry",
                authors="Lawson, H.B., Michelsohn, M.-L.",
                year=1989,
                description="Standard reference for spinor representations: dim = 2^[D/2]"
            )
        ]
    )

    # =========================================================================
    # SECTION 2.2: INTERMEDIATE LAGRANGIANS (26D → 13D → 6D → 4D)
    # =========================================================================

    LAGRANGIAN_13D_EFFECTIVE = Formula(
        id="lagrangian-13d-effective",
        input_params=['constants.M_STAR', 'topology.elder_kads'],
        output_params=['derivations.L_13D_form'],
        label="(2.2.2) v21 Per-Shadow Effective Lagrangian",
        html="ℒ<sub>shadow</sub> = M<sub>*</sub><sup>10</sup>R<sub>12</sub> + Ψ̄<sub>64</sub>(iγ<sup>μ</sup>∇<sub>μ</sub> - m<sub>eff</sub>)Ψ<sub>64</sub> + ℒ<sub>flux</sub>",
        latex="\\mathcal{L}_{\\text{shadow}} = M_*^{10}R_{12} + \\bar{\\Psi}_{64}(i\\gamma^\\mu\\nabla_\\mu - m_{\\text{eff}})\\Psi_{64} + \\mathcal{L}_{\\text{flux}}",
        plain_text="L_shadow = M*^10 R_12 + Psi_64(i*gamma*nabla - m_eff)Psi_64 + L_flux",
        category=FormulaCategory.DERIVED,
        description="v21/v22: Per-shadow effective Lagrangian in 13D(12,1) dual-shadow structure",
        section="2.2",
        status="v21.0 DERIVED FROM DUAL-SHADOW",
        terms={
            "M_*": FormulaTerm("Fundamental Scale", "26D Planck scale"),
            "R_12": FormulaTerm("13D Ricci Scalar", "v21/v22: Per-shadow spacetime curvature"),
            "Psi_64": FormulaTerm("64-Component Spinor", "v21/v22: Per-shadow from Spin(12,1)"),
            "m_eff": FormulaTerm("Effective Mass", "Generated by bridge mechanism"),
            "L_flux": FormulaTerm("Flux Lagrangian", "G-form field strength contributions"),
        },
        simulation_file="simulations/derivations/dimensional_reduction_derivations.py",
        related_formulas=["v21-or-reduction", "reduction-cascade", "lagrangian-6d-bulk"],
        references=[
            FormulaReference(
                id="pm_v21_lagrangian",
                title="Principia Metaphysica v21.0: Dual-Shadow Bridge Framework",
                authors="Watts, A.K.",
                year=2026,
                description="v21 per-shadow Lagrangian derivation"
            ),
            FormulaReference(
                id="acharya2002_mshadow",
                title="M theory, G2-manifolds and four-dimensional physics",
                authors="Acharya, B.S.",
                year=2002,
                arxiv="hep-th/0212294",
                description="G2 compactification framework"
            )
        ]
    )

    LAGRANGIAN_6D_BULK = Formula(
        id="lagrangian-6d-bulk",
        input_params=['derivations.M_6D_scale', 'derivations.warp_factor_scale'],
        output_params=['derivations.L_6D_form'],
        label="(2.2.4) 6D Bulk Lagrangian",
        html="ℒ<sub>6D</sub> = M<sub>6</sub><sup>4</sup>R<sub>6</sub> + e<sup>2A(y)</sup>[ℒ<sub>SM</sub> + ℒ<sub>KK</sub>]",
        latex="\\mathcal{L}_{6D} = M_6^4 R_6 + e^{2A(y)}\\left[\\mathcal{L}_{SM} + \\mathcal{L}_{KK}\\right]",
        plain_text="L_6D = M_6^4 R_6 + e^(2A(y))[L_SM + L_KK]",
        category=FormulaCategory.DERIVED,
        description="6D bulk Lagrangian with warped Standard Model and KK tower before final compactification",
        section="2.2",
        status="DERIVED FROM G2",
        terms={
            "M_6": FormulaTerm("6D Mass Scale", "Effective 6D Planck mass"),
            "R_6": FormulaTerm("6D Ricci Scalar", "Bulk curvature"),
            "A(y)": FormulaTerm("Warp Factor", "Creates TeV-Planck hierarchy"),
            "L_SM": FormulaTerm("Standard Model", "4D SM Lagrangian"),
            "L_KK": FormulaTerm("KK Tower", "Kaluza-Klein excitations"),
        },
        simulation_file="simulations/derivations/dimensional_reduction_derivations.py",
        related_formulas=["lagrangian-13d-effective", "g2-holonomy-constraint", "warp-factor-ansatz"],
        references=[
            FormulaReference(
                id="randall1999",
                title="Large Mass Hierarchy from a Small Extra Dimension",
                authors="Randall, L., Sundrum, R.",
                year=1999,
                arxiv="hep-ph/9905221",
                description="Warped extra dimensions and hierarchy"
            ),
            FormulaReference(
                id="acharya2002_bulk",
                title="M theory, G2-manifolds and four-dimensional physics",
                authors="Acharya, B.S.",
                year=2002,
                arxiv="hep-th/0212294",
                description="G2 compactification to lower dimensions"
            )
        ]
    )

    # v21: Euclidean Bridge Action (replaces Sp(2,R) gauge-fixing)
    V21_BRIDGE_ACTION = Formula(
        id="v21-bridge-action",
        input_params=['dimensions.D_BULK'],
        output_params=['dimensions.D_EFFECTIVE', 'derivations.shadow_signature'],
        label="(2.2.3) v21 Euclidean Bridge Action",
        html="S<sub>bridge</sub> = ∫ d²y √g<sub>E</sub> [κR<sub>bridge</sub> + |D<sub>a</sub>φ|² + V(φ)]",
        latex="S_{\\text{bridge}} = \\int d^2y \\sqrt{g_E} \\left[ \\kappa R_{\\text{bridge}} + |D_a\\phi|^2 + V(\\phi) \\right]",
        plain_text="S_bridge = integral d^2y sqrt(g_E) [kappa R_bridge + |D_a phi|^2 + V(phi)]",
        category=FormulaCategory.THEORY,
        description="v21: Euclidean bridge action connecting dual shadows with positive-definite metric",
        section="2.2",
        status="v21.0 FOUNDATIONAL",
        terms={
            "g_E": FormulaTerm("Bridge Metric", "v21: Positive-definite ds² = dy₁² + dy₂²"),
            "R_bridge": FormulaTerm("Bridge Curvature", "2D Euclidean Ricci scalar"),
            "phi": FormulaTerm("Bridge Modulus", "Scalar field on bridge"),
            "V(phi)": FormulaTerm("Bridge Potential", "Stabilizes bridge geometry"),
            "kappa": FormulaTerm("Bridge Coupling", "Curvature coupling constant"),
        },
        simulation_file="simulations/v21/bridge/bridge_pressure.py",
        related_formulas=["v21-or-reduction", "lagrangian-13d-effective"],
        references=[
            FormulaReference(
                id="pm_v21_bridge",
                title="Principia Metaphysica v21.0: Euclidean Bridge Mechanism",
                authors="Watts, A.K.",
                year=2026,
                description="v21 Euclidean bridge replacing Sp(2,R) gauge fixing"
            )
        ]
    )

    # Legacy alias for backward compatibility
    SP2R_GAUGE_FIXING_ACTION = V21_BRIDGE_ACTION  # DEPRECATED: Use V21_BRIDGE_ACTION

    G2_HOLONOMY_CONSTRAINT = Formula(
        id="g2-holonomy-constraint",
        input_params=['topology.elder_kads'],
        output_params=['derivations.n_generations'],
        label="(2.2.5) G2 Holonomy Constraint",
        html="Hol(g<sub>X</sub>) = G<sub>2</sub> ⟹ b<sub>3</sub>(X) = 24, n<sub>gen</sub> = b<sub>3</sub>/8 = 3",
        latex="\\text{Hol}(g_X) = G_2 \\implies b_3(X) = 24, \\quad n_{\\text{gen}} = \\frac{b_3}{8} = 3",
        plain_text="Hol(g_X) = G2 implies b3(X) = 24, n_gen = b3/8 = 3",
        category=FormulaCategory.THEORY,
        description="G2 holonomy constraint that freezes b3=24, producing exactly 3 fermion generations",
        section="2.2",
        status="EXACT MATCH",
        terms={
            "Hol(g)": FormulaTerm("Holonomy Group", "G2 subset of SO(7)"),
            "b_3": FormulaTerm("Third Betti Number", "= 24 for TCS manifold"),
            "n_gen": FormulaTerm("Generation Count", "= b3/8 = 3 exactly"),
        },
        computed_value=3,
        units="generations",
        experimental_value=3,  # Source: PDG 2024 - three generations confirmed
        sigma_deviation=0.0,
        simulation_file="simulations/derivations/dimensional_reduction_derivations.py",
        related_formulas=["tcs-topology", "generation-number", "lagrangian-6d-bulk"],
        references=[
            FormulaReference(
                id="joyce2000_g2",
                title="Compact Manifolds with Special Holonomy",
                authors="Joyce, D.D.",
                year=2000,
                description="Definitive text on G2 holonomy manifolds"
            ),
            FormulaReference(
                id="acharya_witten2001",
                title="Chiral Fermions from Manifolds of G2 Holonomy",
                authors="Acharya, B.S., Witten, E.",
                year=2001,
                arxiv="hep-th/0109152",
                description="Generation count from G2 index theorem"
            )
        ]
    )

    # =========================================================================
    # SECTION 4: TCS G₂ COMPACTIFICATION
    # =========================================================================

    TCS_TOPOLOGY = Formula(
        id="tcs-topology",
        output_params=['topology.B2', 'topology.B3'],
        label="(4.1) TCS #187 Topology",
        html="b<sub>2</sub> = 4, b<sub>3</sub> = 24, χ<sub>eff</sub> = 144, ν = 24",
        latex="b_2 = 4, \\quad b_3 = 24, \\quad \\chi_{\\text{eff}} = 144, \\quad \\nu = 24",
        plain_text="b₂ = 4, b₃ = 24, χ_eff = 144, ν = 24",
        category=FormulaCategory.THEORY,
        description="TCS G₂ manifold #187 topological parameters",
        section="4",
        status="GEOMETRIC INPUT",
        terms={
            "b_2": FormulaTerm("Second Betti", "= h¹¹ = 4 (Kähler moduli)"),
            "b_3": FormulaTerm("Third Betti", "= 24 (associative 3-cycles)"),
            "χ_eff": FormulaTerm("Effective Euler", "= 2(h¹¹ - h²¹ + h³¹) = 144"),
            "ν": FormulaTerm("Flux Quantum", "= χ_eff/6 = 24"),
        },
        simulation_file="simulations/g2_landscape_scanner_v14_1.py",
        notes="49 valid topologies found with identical predictions",
        related_formulas=["generation-number", "flux-quantization"],
        references=[
            FormulaReference(
                id="corti2015_tcs",
                title="G₂-manifolds and associative submanifolds via semi-Fano 3-folds",
                authors="Corti, A., Haskins, M., Nordström, J., Pacini, T.",
                year=2015,
                description="Systematic TCS construction of compact G₂ manifolds with b₂=4, b₃=24"
            ),
            FormulaReference(
                id="joyce2000",
                title="Compact Manifolds with Special Holonomy",
                authors="Joyce, D.D.",
                year=2000,
                description="Foundation for G₂ topology and Hodge numbers"
            ),
            FormulaReference(
                id="halverson2020",
                title="The Landscape of M-theory Compactifications on Seven-Manifolds with G₂ Holonomy",
                authors="Halverson, J., Morrison, D.R.",
                year=2020,
                arxiv="1905.03729",
                description="Systematic study of G₂ landscape"
            )
        ]
    )

    EFFECTIVE_EULER = Formula(
        id="effective-euler",
        input_params=['topology.B2', 'topology.B3'],
        output_params=['geometry.chi_eff_total', 'topology.CHI_EFF'],
        label="(4.1a) Effective Euler Characteristic",
        html="χ<sub>eff</sub> = 2(h<sup>1,1</sup> - h<sup>2,1</sup> + h<sup>3,1</sup>) = 2(4 - 0 + 68) = 144",
        latex="\\chi_{\\text{eff}} = 2(h^{1,1} - h^{2,1} + h^{3,1}) = 2(4 - 0 + 68) = 144",
        plain_text="χ_eff = 2(h^{1,1} - h^{2,1} + h^{3,1}) = 2(4 - 0 + 68) = 144",
        category=FormulaCategory.DERIVED,
        description="Effective Euler characteristic from Hodge numbers",
        section="4",
        status="EXACT MATCH",
        terms={
            "h^{1,1}": FormulaTerm("Kähler Moduli", "= 4"),
            "h^{2,1}": FormulaTerm("Complex Structure", "= 0 (G₂ has none)"),
            "h^{3,1}": FormulaTerm("Associative Moduli", "= 68"),
        },
        computed_value=144,  # Derived: 2(h^{1,1} - h^{2,1} + h^{3,1}) = 2(4 - 0 + 68) = 144
        units="dimensionless",
        related_formulas=["tcs-topology", "generation-number"],
        simulation_file="simulations/g2_landscape_scanner_v14_1.py",
        references=[
            FormulaReference(
                id="joyce2000_euler",
                title="Compact Manifolds with Special Holonomy",
                authors="Joyce, D.D.",
                year=2000,
                description="Definitive treatment of G₂ cohomology and Hodge numbers"
            ),
            FormulaReference(
                id="corti2015_hodge",
                title="G₂-manifolds and associative submanifolds via semi-Fano 3-folds",
                authors="Corti, A., et al.",
                year=2015,
                description="Explicit computation of Hodge numbers for TCS manifolds"
            ),
            FormulaReference(
                id="atiyah1963",
                title="The Index of Elliptic Operators on Compact Manifolds",
                authors="Atiyah, M.F., Singer, I.M.",
                year=1963,
                description="Index theorem relating topology to analysis"
            )
        ]
    )

    FLUX_QUANTIZATION = Formula(
        id="flux-quantization",
        input_params=['topology.CHI_EFF'],
        output_params=['fermion.n_flux', 'topology.n_flux'],
        label="(4.3) Flux Quantization",
        html="N<sub>flux</sub> = χ<sub>eff</sub>/6 = 144/6 = 24",
        latex="N_{\\text{flux}} = \\frac{\\chi_{\\text{eff}}}{6} = \\frac{144}{6} = 24",
        plain_text="N_flux = χ_eff/6 = 144/6 = 24",
        category=FormulaCategory.DERIVED,
        description="Flux quantization from effective Euler characteristic",
        section="4",
        status="EXACT MATCH",
        terms={
            "N_flux": FormulaTerm("Flux Quantum", "Quantized G-flux units"),
            "χ_eff": FormulaTerm("Effective Euler", "= 144"),
        },
        computed_value=24,
        units="dimensionless",
        related_formulas=["tcs-topology", "effective-torsion"],
        references=[
            FormulaReference("acharya2002", "M theory, Joyce Orbifolds and Super Yang-Mills", "Acharya, B.S.", 2002, arxiv="hep-th/9812205"),
            FormulaReference("acharya2001", "Chiral Fermions from Manifolds of G₂ Holonomy", "Acharya, B.S. & Witten, E.", 2001, arxiv="hep-th/0109152"),
            FormulaReference("gukov2000", "CFT's from Calabi-Yau four-folds", "Gukov, S., Vafa, C., & Witten, E.", 2000, arxiv="hep-th/9906070"),
        ],
        simulation_file="simulations/flux_stabilization_full_v12_7.py"
    )

    EFFECTIVE_TORSION = Formula(
        id="effective-torsion",
        # No registry path: topology.shadow_torsion_total (=24) is a DIFFERENT
        # quantity than this normalized torsion class (-1.0) — deliberate orphan
        # until the registry exports T_omega_eff itself.
        input_params=['topology.CHI_EFF'],
        label="(4.3b) Effective Torsion",
        html="T<sub>ω,eff</sub> = -b<sub>3</sub>/N<sub>flux</sub> = -24/24 = -1.0",
        latex="T_{\\omega,\\text{eff}} = -\\frac{b_3}{N_{\\text{flux}}} = -\\frac{24}{24} = -1.0",
        plain_text="T_ω,eff = -b₃/N_flux = -24/24 = -1.0",
        category=FormulaCategory.DERIVED,
        description="Effective torsion from topology",
        section="4",
        status="EXACT MATCH",
        terms={
            "T_ω,eff": FormulaTerm("Effective Torsion", "Normalized torsion class"),
            "b₃": FormulaTerm("Third Betti Number", "= 24 for TCS"),
            "N_flux": FormulaTerm("Flux Quantum", "= 24"),
        },
        computed_value=-1.0,
        units="dimensionless",
        related_formulas=["flux-quantization", "tcs-topology"],
        references=[
            FormulaReference("fernandez1982", "Riemannian manifolds with structure group G₂", "Fernández, M. & Gray, A.", 1982, doi="10.1007/BF01760975"),
            FormulaReference("karigiannis2009", "Flows of G₂-structures, I", "Karigiannis, S.", 2009, arxiv="math/0702077"),
            FormulaReference("acharya2004", "Freund-Rubin Revisited", "Acharya, B.S. et al.", 2004, arxiv="hep-th/0308046"),
        ],
        simulation_file="simulations/torsion_effective_v12_8.py"
    )

    MIRROR_DM_RATIO = Formula(
        id="mirror-dm-ratio",
        output_params=['mirror_sector.dm_baryon_ratio'],
        label="(4.5) Dark Matter Ratio",
        html="Ω<sub>DM</sub>/Ω<sub>b</sub> = (T/T')³ = (1/0.57)³ ≈ 5.8",
        latex="\\frac{\\Omega_{\\text{DM}}}{\\Omega_b} = \\left(\\frac{T}{T'}\\right)^3 = \\left(\\frac{1}{0.57}\\right)^3 \\approx 5.8",
        plain_text="Ω_DM/Ω_b = (T/T')³ = (1/0.57)³ ≈ 5.8",
        category=FormulaCategory.PREDICTIONS,
        description="Dark matter to baryon ratio from mirror sector",
        section="4",
        status="CONSISTENT WITH Ω_DM/Ω_b ≈ 5.4",
        computed_value=5.8,
        experimental_value=5.4,  # Source: Planck 2020 Ω_DM/Ω_b = 5.4 ± 0.3
        sigma_deviation=0.7,
        related_formulas=["mirror-temp-ratio"],
        references=[
            FormulaReference("foot1991", "A model with fundamental improper spacetime symmetries", "Foot, R., Lew, H., & Volkas, R.R.", 1991, doi="10.1016/0370-2693(91)91013-L"),
            FormulaReference("foot2004", "Experimental implications of mirror matter-type dark matter", "Foot, R.", 2004, arxiv="astro-ph/0309330"),
            FormulaReference("planck2020", "Planck 2018 results. VI. Cosmological parameters", "Planck Collaboration", 2020, arxiv="1807.06209"),
        ],
        simulation_file="simulations/mirror_dark_matter_abundance_v15_3.py"
    )

    # =========================================================================
    # SECTION 5: GAUGE UNIFICATION
    # =========================================================================

    SO10_BREAKING = Formula(
        id="so10-breaking",
        input_params=['gauge.M_GUT'],
        label="(5.1) SO(10) Breaking Chain",
        html="SO(10) ⊃ SU(3)<sub>C</sub> × SU(2)<sub>L</sub> × U(1)<sub>Y</sub>",
        latex="\\text{SO}(10) \\supset \\text{SU}(3)_C \\times \\text{SU}(2)_L \\times \\text{U}(1)_Y",
        plain_text="SO(10) ⊃ SU(3)_C × SU(2)_L × U(1)_Y",
        category=FormulaCategory.THEORY,
        description="SO(10) GUT gauge symmetry breaking to Standard Model",
        section="5",
        related_formulas=["gut-scale", "gut-coupling"],
        references=[
            FormulaReference("fritzsch1975", "Unified Interactions of Leptons and Hadrons", "Fritzsch, H. & Minkowski, P.", 1975, doi="10.1016/0003-4916(75)90211-0"),
            FormulaReference("mohapatra1980", "Neutrino Mass and Spontaneous Parity Nonconservation", "Mohapatra, R.N. & Senjanović, G.", 1980, doi="10.1103/PhysRevLett.44.912"),
            FormulaReference("langacker1981", "Grand Unified Theories and Proton Decay", "Langacker, P.", 1981, doi="10.1016/0370-1573(81)90059-4"),
        ],
        simulation_file="simulations/breaking_chain_geometric_v14_1.py"
    )

    GUT_COUPLING = Formula(
        id="gut-coupling",
        label="(5.2) GUT Coupling",
        html="1/α<sub>GUT</sub> = 10π · Vol(Σ<sub>sing</sub>)/Vol(G₂) · e<sup>|T_ω|/h¹¹</sup> = 23.54",
        latex="\\frac{1}{\\alpha_{\\text{GUT}}} = 10\\pi \\times \\frac{\\text{Vol}(\\Sigma_{\\text{sing}})}{\\text{Vol}(G_2)} \\times e^{|T_\\omega|/h^{1,1}} = 23.54",
        plain_text="1/α_GUT = 10π · Vol(Σ_sing)/Vol(G₂) · exp(|T_ω|/h¹¹) = 23.54",
        category=FormulaCategory.DERIVED,
        description="Unified gauge coupling from G₂ geometry",
        section="5",
        status="GEOMETRIC",
        terms={
            "α_GUT": FormulaTerm("GUT Coupling", "≈ 1/23.54 ≈ 0.0425"),
            "Vol": FormulaTerm("Volumes", "G₂ and singularity locus"),
            "T_ω": FormulaTerm("Effective Torsion", "= -1.0"),
            "h¹¹": FormulaTerm("Kähler Moduli", "= 4"),
        },
        computed_value=23.54,
        simulation_file="simulations/gauge_unification_precision_v12_4.py",
        related_formulas=["gut-scale", "tcs-topology"],
        references=[
            FormulaReference("georgi1974", "Hierarchy of Interactions in Unified Gauge Theories", "Georgi, H., Quinn, H.R., & Weinberg, S.", 1974, doi="10.1103/PhysRevLett.33.451"),
            FormulaReference("dimopoulos1981", "Supersymmetry and the Scale of Unification", "Dimopoulos, S., Raby, S., & Wilczek, F.", 1981, doi="10.1103/PhysRevD.24.1681"),
            FormulaReference("amaldi1991", "Comparison of grand unified theories with electroweak and strong coupling constants", "Amaldi, U., de Boer, W., & Fürstenau, H.", 1991, doi="10.1016/0370-2693(91)91641-8"),
        ]
    )

    WEAK_MIXING_ANGLE = Formula(
        id="weak-mixing-angle",
        output_params=['gauge.sin2_theta_w'],
        label="(5.5) Weak Mixing Angle",
        html="sin²θ<sub>W</sub>(M<sub>Z</sub>) = 0.23122",
        latex="\\sin^2\\theta_W(M_Z) = 0.23122",
        plain_text="sin²θ_W(M_Z) = 0.23122",
        category=FormulaCategory.PREDICTIONS,
        description="Weak mixing angle at Z pole (NOTE: displayed value is the PDG anchor; the registry's geometric prediction is 0.23190 — 0.68σ with 0.001 theory uncertainty. See drift audit.)",
        section="5",
        status="ESTABLISHED input (scheme ruling); geometric candidate 0.23190 at gauge.sin2_theta_w_geometric",
        computed_value=0.23122,   # gauge.sin2_theta_w now carries the PDG MS-bar input (2026-08 scheme ruling)
        experimental_value=0.23122,  # Source: PDG 2024 sin²θ_W(M_Z) = 0.23122 ± 0.00003
        experimental_error=0.00003,
        sigma_deviation=0.0,
        simulation_file="simulations/gauge_unification_precision_v12_4.py",
        related_formulas=["gut-coupling", "gut-scale"],
        references=[
            FormulaReference("weinberg1967", "A Model of Leptons", "Weinberg, S.", 1967, doi="10.1103/PhysRevLett.19.1264"),
            FormulaReference("pdg2024", "Review of Particle Physics", "Particle Data Group", 2024, doi="10.1103/PhysRevD.110.030001"),
            FormulaReference("erler2005", "Weak mixing angle at low energies", "Erler, J. & Ramsey-Musolf, M.J.", 2005, arxiv="hep-ph/0409169"),
        ]
    )

    HIGGS_VEV = Formula(
        id="higgs-vev",
        output_params=['higgs.vev'],
        input_params=['pneuma.VEV'],
        label="(5.6) Electroweak VEV",
        html="v<sub>EW</sub> = √2 · M<sub>Pl</sub> · e<sup>-h²¹/b₃</sup> · e<sup>|T_ω|</sup> = 246.03 GeV (v/√2 = 173.97)",
        latex="v_{\\text{EW}} = \\sqrt{2}\\, M_{\\text{Pl}} \\times e^{-h^{2,1}/b_3} \\times e^{|T_\\omega|} = 246.03\\,\\text{GeV}",
        plain_text="v_EW = √2 · M_Pl · exp(-h²¹/b₃) · exp(|T_ω|) = 246.03 GeV (v/√2 = 173.97)",
        category=FormulaCategory.DERIVED,
        description="Electroweak VEV in the conventional normalization (machine value = v_EW so the registry binding compares like-for-like; the Yukawa-normalization v/√2 = 173.97 GeV is shown alongside)",
        section="5",
        terms={
            "v_EW/√2": FormulaTerm("Higgs VEV (Yukawa norm)", "v/√2 ≈ 174 GeV; conventional v_EW = 246.22 GeV"),
            "M_Pl": FormulaTerm("Planck Mass (reduced)", "2.435×10¹⁸ GeV"),
        },
        computed_value=246.03,   # v_EW conventional normalization (= 173.97 × √2)
        units="GeV",
        related_formulas=["top-quark-mass"],
        references=[
            FormulaReference("higgs1964", "Broken Symmetries and the Masses of Gauge Bosons", "Higgs, P.W.", 1964, doi="10.1103/PhysRevLett.13.508"),
            FormulaReference("atlas_cms2015", "Combined Measurement of the Higgs Boson Mass", "ATLAS & CMS Collaborations", 2015, arxiv="1503.07589"),
        ],
        simulation_file="simulations/derive_vev_pneuma.py"
    )

    # =========================================================================
    # SECTION 6: FERMION SECTOR
    # =========================================================================

    TOP_QUARK_MASS = Formula(
        id="top-quark-mass",
        output_params=['pdg.m_top'],
        input_params=['pneuma.VEV'],
        label="(6.4) Top Quark Mass",
        html="m<sub>t</sub> = y<sub>t</sub> · v<sub>EW</sub>/√2 = 172.7 GeV",
        latex="m_t = y_t \\times \\frac{v_{\\text{EW}}}{\\sqrt{2}} = 172.7\\,\\text{GeV}",
        plain_text="m_t = y_t · v_EW/√2 = 172.7 GeV",
        category=FormulaCategory.PREDICTIONS,
        description="Top quark mass from Yukawa coupling",
        section="6",
        status="0.06σ",
        computed_value=172.7,
        units="GeV",
        experimental_value=172.69,  # Source: PDG 2024 m_t = 172.69 ± 0.30 GeV
        experimental_error=0.30,
        sigma_deviation=0.06,
        related_formulas=["higgs-vev"],
        references=[
            FormulaReference("cdf_d0_2014", "Combination of CDF and D0 results on the mass of the top quark", "CDF & D0 Collaborations", 2014, arxiv="1407.2682"),
            FormulaReference("pdg2024_top", "Review of Particle Physics (top quark)", "Particle Data Group", 2024, doi="10.1103/PhysRevD.110.030001"),
            FormulaReference("froggatt1979", "Hierarchy of Quark Masses, Cabibbo Angles and CP Violation", "Froggatt, C.D. & Nielsen, H.B.", 1979, doi="10.1016/0550-3213(79)90316-X"),
        ],
        simulation_file="simulations/higgs_yukawa_rg_v12_4.py"
    )

    STRONG_COUPLING = Formula(
        id="strong-coupling",
        output_params=['constants.alpha_s_pred'],
        label="(6.7) Strong Coupling",
        html="α<sub>s</sub>(M<sub>Z</sub>) = 0.1179",
        latex="\\alpha_s(M_Z) = 0.1179",
        plain_text="α_s(M_Z) = 0.1179",
        category=FormulaCategory.PREDICTIONS,
        description="Strong coupling constant at Z pole",
        section="6",
        status="0.1σ FROM PDG",
        computed_value=0.1179,
        experimental_value=0.1180,  # Source: PDG 2024 α_s(M_Z) = 0.1180 ± 0.0009
        experimental_error=0.0009,
        sigma_deviation=0.11,  # |0.1179 - 0.1180| / 0.0009
        simulation_file="simulations/gauge_unification_precision_v12_4.py",
        related_formulas=["gut-coupling"],
        references=[
            FormulaReference("gross1973", "Ultraviolet Behavior of Non-Abelian Gauge Theories", "Gross, D.J. & Wilczek, F.", 1973, doi="10.1103/PhysRevLett.30.1343"),
            FormulaReference("politzer1973", "Reliable Perturbative Results for Strong Interactions?", "Politzer, H.D.", 1973, doi="10.1103/PhysRevLett.30.1346"),
            FormulaReference("pdg2024_alpha_s", "Review of Particle Physics (QCD)", "Particle Data Group", 2024, doi="10.1103/PhysRevD.110.030001"),
        ]
    )

    NEUTRINO_MASS_21 = Formula(
        id="neutrino-mass-21",
        input_params=['neutrino.seesaw'],
        output_params=['neutrino.dm2_21', 'neutrino.mass_splittings'],
        label="(6.2) Solar Mass Splitting",
        html="Δm²<sub>21</sub> = 7.97 × 10<sup>-5</sup> eV²",
        latex="\\Delta m^2_{21} = 7.97 \\times 10^{-5}\\,\\text{eV}^2",
        plain_text="Δm²_21 = 7.97 × 10⁻⁵ eV²",
        category=FormulaCategory.PREDICTIONS,
        description="Solar neutrino mass splitting",
        section="6",
        status="7.4% (2.6σ) from NuFIT",
        computed_value=7.97e-5,
        units="eV²",
        experimental_value=7.42e-5,  # Source: NuFIT 6.0 (2024) Δm²_21 = 7.42 × 10⁻⁵ eV²
        sigma_deviation=2.62,  # |7.97-7.42|/0.21 vs NuFIT uncertainty (7.4% relative error)
        simulation_file="simulations/pmns_full_matrix.py",
        related_formulas=["neutrino-mass-31", "theta23-maximal"],
        references=[
            FormulaReference("fukuda1998_sk", "Evidence for oscillation of atmospheric neutrinos", "Fukuda, Y., et al. (Super-Kamiokande)", 1998, arxiv="hep-ex/9807003"),
            FormulaReference("ahmad2002_sno", "Direct Evidence for Neutrino Flavor Transformation", "Ahmad, Q.R., et al. (SNO)", 2002, arxiv="nucl-ex/0204008"),
            FormulaReference("nufit2024", "NuFIT 6.0 (2024)", "Esteban, I., et al.", 2024),
        ]
    )

    NEUTRINO_MASS_31 = Formula(
        id="neutrino-mass-31",
        input_params=['neutrino.seesaw'],
        # NOTE: registry publishes the IO splitting dm2_32 (negative); this
        # formula displays the NO-convention |Δm²_31| — the drift auditor
        # flags the sign/story mismatch until the two are reconciled.
        output_params=['neutrino.dm2_32', 'neutrino.mass_splittings'],
        label="(6.3) Atmospheric Mass Splitting",
        html="Δm²<sub>31</sub> = 2.525 × 10<sup>-3</sup> eV²",
        latex="\\Delta m^2_{31} = 2.525 \\times 10^{-3}\\,\\text{eV}^2",
        plain_text="Δm²_31 = 2.525 × 10⁻³ eV²",
        category=FormulaCategory.PREDICTIONS,
        description="Atmospheric neutrino mass splitting",
        section="6",
        status="0.4σ",
        computed_value=2.525e-3,
        units="eV²",
        experimental_value=2.515e-3,  # Source: NuFIT 6.0 (2024) Δm²_31 = 2.515 × 10⁻³ eV²
        sigma_deviation=0.4,
        simulation_file="simulations/pmns_full_matrix.py",
        related_formulas=["neutrino-mass-21", "theta23-maximal"],
        references=[
            FormulaReference("fukuda1998_atm", "Evidence for oscillation of atmospheric neutrinos", "Fukuda, Y., et al. (Super-Kamiokande)", 1998, arxiv="hep-ex/9807003"),
            FormulaReference("t2k2020", "Constraint on the matter-antimatter symmetry-violating phase", "Abe, K., et al. (T2K)", 2020, arxiv="1910.03887"),
            FormulaReference("nufit2024_dm31", "NuFIT 6.0 (2024) - global fit", "Esteban, I., et al.", 2024),
        ]
    )

    CP_PHASE_GEOMETRIC = Formula(
        id="cp-phase-geometric",
        output_params=['neutrino.delta_CP_pred'],
        label="(6.8) CP Phase",
        html="δ<sub>CP</sub> = π · Σorient<sub>i</sub>/b₃ = π · 12/24 = π/2",
        latex="\\delta_{\\text{CP}} = \\pi \\frac{\\sum_i \\text{orientation}_i}{b_3} = \\pi \\frac{12}{24} = \\frac{\\pi}{2}",
        plain_text="δ_CP = π · Σorient_i/b₃ = π · 12/24 = π/2",
        category=FormulaCategory.SPECULATIVE,
        description="SUPERSEDED speculative candidate: the operative registry value is the FITTED δ_CP = 278.4° (neutrino_mixing, parity_offset = 45.9° fitted). This 90° cycle-orientation form is retained as an alternative story only.",
        section="6",
        terms={
            "δ_CP": FormulaTerm(
                name="CP Violation Phase",
                description="Dirac CP-violating phase in the PMNS matrix (neutrino mixing)",
                symbol="δ_CP",
                value="π/2 = 90°",
                units="degrees",
                contribution="Geometric prediction from cycle orientations"
            ),
            "orient_i": FormulaTerm(
                name="Cycle Orientations",
                description="Orientation signs (±1) of associative 3-cycles in G₂ manifold",
                symbol="Σorient_i",
                value="12 (out of 24)",
                units="dimensionless",
                contribution="Net signed sum from TCS geometry"
            ),
            "b₃": FormulaTerm(
                name="Third Betti Number",
                description="Number of independent 3-cycles in G₂ manifold",
                symbol="b₃",
                value="24",
                units="dimensionless",
                contribution="Topological invariant from TCS construction"
            ),
        },
        info_title="CP Phase from G₂ Topology",
        info_meaning="The CP-violating phase δ_CP in neutrino oscillations emerges from the geometry of associative 3-cycles in the G₂ manifold. The signed sum of cycle orientations (12 out of 24) yields δ_CP = π·(12/24) = π/2 = 90°, predicting maximal CP violation in the neutrino sector.",
        info_grid=[
            FormulaInfoItem(title="Predicted Value", content="δ_CP = 90° (π/2)"),
            FormulaInfoItem(title="Cycle Sum", content="Σorient_i = 12"),
            FormulaInfoItem(title="Total Cycles", content="b₃ = 24"),
            FormulaInfoItem(title="Current Data", content="Favors maximal ~90°"),
        ],
        expansion_title="\\delta_{\\text{CP}} = \\pi \\frac{\\sum_i \\text{orientation}_i}{b_3} = \\pi \\frac{12}{24} = \\frac{\\pi}{2} = 90^\\circ",
        sub_components=[
            FormulaSubComponent(symbol="Σorient_i", name="Orientation Sum", description="Net signed sum: 12 positive minus negatives", badge="GEOMETRIC", badge_type="mathematics"),
            FormulaSubComponent(symbol="b₃", name="Third Betti Number", description="Total 3-cycles: b₃ = 24", badge="TOPOLOGY", badge_type="mathematics"),
            FormulaSubComponent(symbol="π/2", name="Maximal Phase", description="90° = maximal CP violation", badge="PREDICTION", badge_type="theory"),
        ],
        derivation_chain=[
            FormulaDerivationStep(title="TCS G₂ Topology", badge="MATHEMATICS", badge_type="mathematics"),
            FormulaDerivationStep(title="Associative 3-Cycles", badge="GEOMETRIC", badge_type="mathematics"),
            FormulaDerivationStep(title="Orientation Counting", badge="TOPOLOGY", badge_type="mathematics"),
        ],
        discussion="The CP-violating phase arises from the topology of the G₂ manifold. Associative 3-cycles carry orientation signs (±1), and their signed sum Σorient_i = 12 (out of b₃ = 24 total) determines δ_CP = π·(12/24) = π/2. This predicts maximal CP violation (90°) in neutrino oscillations, consistent with current T2K and NOvA data that favor δ_CP near ±90°. This also constrains the reactor angle θ_13 ≈ 8.5°, matching observations.",
        computed_value=90.0,  # degrees (π/2)
        units="degrees",
        simulation_file="simulations/pmns_theta13_delta_geometric_v14_1.py",
        related_formulas=["tcs-topology"],
        references=[
            FormulaReference("kobayashi1973", "CP-Violation in the Renormalizable Theory of Weak Interaction", "Kobayashi, M. & Maskawa, T.", 1973, doi="10.1143/PTP.49.652"),
            FormulaReference("t2k2020_cp", "Constraint on the matter-antimatter symmetry-violating phase", "Abe, K., et al. (T2K)", 2020, arxiv="1910.03887"),
            FormulaReference("nufit2024_cp", "NuFIT 6.0 (2024) - CP phase", "Esteban, I., et al.", 2024),
        ]
    )

    # =========================================================================
    # SECTION 7: COSMOLOGY
    # =========================================================================

    EFFECTIVE_DIMENSION = Formula(
        id="effective-dimension",
        output_params=['cosmology.D_eff'],
        label="(7.1) Effective Dimension",
        html="d<sub>eff</sub> = 12 + γ(Shadow<sub>ק</sub> + Shadow<sub>ח</sub>) = 12 + 0.5(1.152) = 12.576",
        latex="d_{\\text{eff}} = 12 + \\gamma(\\text{Shadow}_ק + \\text{Shadow}_ח) = 12 + 0.5(1.152) = 12.576",
        plain_text="d_eff = 12 + γ(Shadow_ק + Shadow_ח) = 12 + 0.5(1.152) = 12.576",
        category=FormulaCategory.DERIVED,
        description="Effective dimension with ghost correction",
        section="7",
        status="EXACT MATCH",
        terms={
            "d_eff": FormulaTerm("Effective Dimension", "Governs dark energy EoS"),
            "γ": FormulaTerm("Ghost Coefficient", "= 0.5 from Virasoro"),
            "Shadow": FormulaTerm("Shadow Contributions", "= 0.576 each"),
        },
        computed_value=12.576,
        units="dimensionless",
        related_formulas=["dark-energy-w0"],
        references=[
            FormulaReference("virasoro1970", "Subsidiary Conditions and Ghosts in Dual-Resonance Models", "Virasoro, M.A.", 1970, doi="10.1103/PhysRevD.1.2933"),
            FormulaReference("goddard1973", "Quantum dynamics of a massless relativistic string", "Goddard, P., et al.", 1973, doi="10.1016/0550-3213(73)90223-X"),
            FormulaReference("polchinski1998", "String Theory, Vol. 1: An Introduction to the Bosonic String", "Polchinski, J.", 1998),
        ],
        simulation_file="simulations/derive_d_eff_v12_8.py"
    )

    DARK_ENERGY_WA = Formula(
        id="dark-energy-wa",
        input_params=['dark_energy.w0'],
        output_params=['dark_energy.wa'],
        label="(7.4) Dark Energy Evolution",
        html="w<sub>a</sub> = -1/√b₃ = -1/√24 = -0.204",
        latex="w_a = -\\frac{1}{\\sqrt{b_3}} = -\\frac{1}{\\sqrt{24}} = -0.204",
        plain_text="w_a = -1/√b₃ = -1/√24 = -0.204",
        category=FormulaCategory.PREDICTIONS,
        description=(
            "Dark energy evolution slope — CANONICAL pure form (zero spare "
            "variables; 2026-08 ruling). The ×4 co-associative projection "
            "(-0.816, 0.23σ) was a post-DESI graft and is retained only as "
            "the RETRODICTED variant cosmology.wa_projection_x4."
        ),
        section="7",
        status="PREDICTED (1.88σ vs DESI DR1 w_a = -0.75 ± 0.29 — honest tension)",
        terms={
            "w_a": FormulaTerm("Evolution Parameter", "CPL parametrization slope"),
            "b₃": FormulaTerm("Third Betti Number", "= 24"),
        },
        computed_value=-0.2041,
        units="dimensionless",
        experimental_value=-0.75,  # Source: DESI 2024 DR1 w_a = -0.75 ± 0.29
        experimental_error=0.29,
        sigma_deviation=1.88,
        simulation_file="simulations/thermal_time_v12_8.py",
        related_formulas=["dark-energy-w0", "effective-dimension"],
        references=[
            FormulaReference("chevallier2001", "Accelerating Universes with Scaling Dark Matter", "Chevallier, M. & Polarski, D.", 2001, arxiv="gr-qc/0009008"),
            FormulaReference("linder2003", "Exploring the Expansion History of the Universe", "Linder, E.V.", 2003, arxiv="astro-ph/0208512"),
            FormulaReference("desi2024", "DESI 2024 VI: Cosmological Constraints from BAO", "DESI Collaboration", 2024, arxiv="2404.03002"),
        ]
    )

    THERMAL_TIME = Formula(
        id="thermal-time",
        label="(7.8) Thermal Time",
        html="t<sub>therm</sub> = α<sub>T</sub> · S<sub>Pneuma</sub> = α<sub>T</sub> · Tr(ρ log ρ)",
        latex="t_{\\text{therm}} = \\alpha_T \\cdot S_{\\text{Pneuma}} = \\alpha_T \\cdot \\text{Tr}(\\rho \\log \\rho)",
        plain_text="t_therm = α_T · S_Pneuma = α_T · Tr(ρ log ρ)",
        category=FormulaCategory.THEORY,
        description="Thermal time from Pneuma entropy via Tomita-Takesaki",
        section="7",
        terms={
            "t_therm": FormulaTerm("Thermal Time", "Emergent time parameter"),
            "α_T": FormulaTerm("Thermal Exponent", "Normalization from KMS"),
            "S_Pneuma": FormulaTerm("Pneuma Entropy", "Von Neumann entropy of Pneuma"),
            "ρ": FormulaTerm("Density Matrix", "Pneuma state"),
        },
        simulation_file="simulations/thermal_time_v12_8.py",
        related_formulas=["dark-energy-wa", "kms-condition"]
    )

    # =========================================================================
    # SECTION 8: PREDICTIONS (Additional)
    # =========================================================================

    GW_DISPERSION = Formula(
        id="gw-dispersion",
        input_params=['kk_spectrum.m1_TeV'],
        label="(I.1) GW Dispersion",
        html="ω² = k²c² + η · k⁴/M<sub>GW</sub>²",
        latex="\\omega^2 = k^2 c^2 + \\eta \\cdot k^4 / M_{\\text{GW}}^2",
        plain_text="ω² = k²c² + η · k⁴/M_GW²",
        category=FormulaCategory.PREDICTIONS,
        description="Gravitational wave dispersion from extra dimensions",
        section="Appendix I",
        terms={
            "ω": FormulaTerm("Frequency", "GW angular frequency"),
            "k": FormulaTerm("Wavenumber", "Spatial wavenumber"),
            "η": FormulaTerm("Dispersion Coefficient", "= exp(|T_ω|)/b₃ ≈ 0.113"),
            "M_GW": FormulaTerm("GW Scale", "Characteristic dispersion mass"),
        },
        testability="LISA 2030s",
        simulation_file="simulations/gw_dispersion_v12_8.py",
        related_formulas=["effective-torsion", "tcs-topology"]
    )

    GW_DISPERSION_COEFF = Formula(
        id="gw-dispersion-coeff",
        label="(I.2) GW Dispersion Coefficient",
        html="η = e<sup>|T_ω|</sup>/b₃ = e/24 ≈ 0.113",
        latex="\\eta = \\frac{e^{|T_\\omega|}}{b_3} = \\frac{e}{24} \\approx 0.113",
        plain_text="η = exp(|T_ω|)/b₃ = e/24 ≈ 0.113",
        category=FormulaCategory.PREDICTIONS,
        description="GW dispersion coefficient from topology",
        section="Appendix I",
        computed_value=0.113,
        related_formulas=["gw-dispersion", "effective-torsion"],
        simulation_file="simulations/gw_dispersion_v12_8.py"
    )

    PROTON_BRANCHING = Formula(
        id="proton-branching",
        label="(H.1) Proton Decay Branching",
        html="BR(p → e⁺π⁰) = (N<sub>orient</sub>/b₃)² = (12/24)² = 0.25",
        latex="\\text{BR}(p \\to e^+\\pi^0) = \\left(\\frac{N_{\\text{orient}}}{b_3}\\right)^2 = \\left(\\frac{12}{24}\\right)^2 = 0.25",
        plain_text="BR(p → e⁺π⁰) = (N_orient/b₃)² = (12/24)² = 0.25",
        category=FormulaCategory.PREDICTIONS,
        description="Proton decay branching ratio to e⁺π⁰",
        section="Appendix H",
        computed_value=0.25,
        testability="Hyper-K 2030s",
        simulation_file="simulations/proton_decay_geometric_v13_0.py",
        related_formulas=["proton-lifetime", "tcs-topology"]
    )

    # =========================================================================
    # ADDITIONAL THEORETICAL FORMULAS (Non-simulation)
    # =========================================================================

    PNEUMA_STRESS_ENERGY = Formula(
        id="pneuma-stress-energy",
        label="(2.4) Pneuma Stress-Energy Tensor",
        html="T<sub>MN</sub><sup>(Pneuma)</sup> = (i/4)[Ψ̄<sub>P</sub>Γ<sub>(M</sub>D<sub>N)</sub>Ψ<sub>P</sub> - D<sub>(M</sub>Ψ̄<sub>P</sub>Γ<sub>N)</sub>Ψ<sub>P</sub>] - g<sub>MN</sub>ℒ<sub>Ψ</sub>",
        latex="T_{MN}^{(\\text{Pneuma})} = \\frac{i}{4}\\left[\\bar{\\Psi}_P\\Gamma_{(M}D_{N)}\\Psi_P - D_{(M}\\bar{\\Psi}_P\\Gamma_{N)}\\Psi_P\\right] - g_{MN}\\mathcal{L}_{\\Psi}",
        plain_text="T_MN^(Pneuma) = (i/4)[Ψ̄_P Γ_(M D_N) Ψ_P - D_(M Ψ̄_P Γ_N) Ψ_P] - g_MN ℒ_Ψ",
        category=FormulaCategory.DERIVED,
        description="Pneuma field stress-energy tensor sourcing 26D geometry (Mach's principle)",
        section="2.5",
        status="THEORETICAL",
        terms={
            "T_MN": FormulaTerm("Stress-Energy Tensor", "Energy-momentum tensor of Pneuma field"),
            "Ψ_P": FormulaTerm("Pneuma Field", "4096-component primordial Weyl spinor of Cl(24,2)"),
            "Γ_(M": FormulaTerm("Symmetrized Gamma", "Clifford gamma matrices with symmetrized indices"),
            "D_M": FormulaTerm("Covariant Derivative", "Gauge and spin covariant derivative"),
            "g_MN": FormulaTerm("26D Metric", "v22: Metric tensor in signature (24,2)"),
            "ℒ_Ψ": FormulaTerm("Pneuma Lagrangian", "Lagrangian density = Ψ̄(iΓD - m)Ψ"),
        },
        derivation=FormulaDerivation(
            parent_formulas=["master-action-26d"],
            established_physics=["noether-theorem", "einstein-equations"],
            steps=[
                "Start with Pneuma Lagrangian from master action",
                "Apply Noether: T_MN = (2/√|g|) δS/δg^MN",
                "Couple to Einstein equations: R_MN - (1/2)g_MN R = (1/M*^24) T_MN",
                "Vacuum condensate ⟨Ψ̄Ψ⟩ = v_P³ generates curvature",
                "Result: Geometry emerges from Pneuma (Mach's principle)"
            ]
        ),
        notes="Pneuma condensate is the SOURCE of spacetime geometry - Mach's principle realized",
        related_formulas=["master-action-26d", "pneuma-vev", "bekenstein-hawking"]
    )

    BEKENSTEIN_HAWKING = Formula(
        id="bekenstein-hawking",
        label="(2.5) Bekenstein-Hawking Entropy",
        html="S<sub>BH</sub> = A/(4l<sub>P</sub>²) = N<sub>Pneuma</sub>/4 · log(2)",
        latex="S_{\\text{BH}} = \\frac{A}{4l_P^2} = \\frac{N_{\\text{Pneuma}}}{4} \\cdot \\log(2)",
        plain_text="S_BH = A/(4l_P²) = N_Pneuma/4 · log(2)",
        category=FormulaCategory.DERIVED,
        description="Black hole entropy from Pneuma spinor counting",
        section="2",
        status="THEORETICAL DERIVATION",
        terms={
            "S_BH": FormulaTerm("BH Entropy", "Bekenstein-Hawking entropy"),
            "A": FormulaTerm("Horizon Area", "Black hole event horizon area"),
            "l_P": FormulaTerm("Planck Length", "√(ℏG/c³) ≈ 1.6×10⁻³⁵ m"),
            "N_Pneuma": FormulaTerm("Pneuma Count", "Spinor degrees of freedom on horizon"),
        },
        units="dimensionless",
        notes="Provides microscopic interpretation of black hole entropy",
        related_formulas=["master-action-26d"]
    )

    SCALAR_POTENTIAL = Formula(
        id="scalar-potential",
        label="(2.7) Scalar Potential",
        html="V(Ψ<sub>P</sub>) = |∂W/∂Ψ<sub>P</sub>|² = |-Aa·e<sup>-aΨ</sup> + Bb·e<sup>-bΨ</sup>|²",
        latex="V(\\Psi_P) = \\left| \\frac{\\partial W}{\\partial \\Psi_P} \\right|^2 = \\left| -Aa \\, e^{-a\\Psi_P} + Bb \\, e^{-b\\Psi_P} \\right|^2",
        plain_text="V(Ψ_P) = |∂W/∂Ψ_P|² = |-Aa·exp(-aΨ) + Bb·exp(-bΨ)|²",
        category=FormulaCategory.DERIVED,
        description="F-term scalar potential from racetrack superpotential",
        section="2",
        status="DYNAMICALLY SELECTED",
        terms={
            "V": FormulaTerm("Scalar Potential", "Determines vacuum structure"),
            "W": FormulaTerm("Superpotential", "Holomorphic function of moduli"),
        },
        simulation_file="simulations/pneuma_full_potential_v14_1.py",
        units="GeV^4",
        related_formulas=["racetrack-superpotential", "pneuma-vev"],
        learning_resources=[
            LearningResource(
                title="Perimeter Scholars - Introduction to Supergravity",
                url="https://www.youtube.com/results?search_query=Perimeter+supergravity+moduli+stabilization",
                type="video",
                duration="3 hours",
                level="advanced",
                description="Topics: SUSY breaking, moduli, KKLT"
            ),
            LearningResource(
                title="KKLT After 20 Years - Quevedo & Valenzuela",
                url="https://arxiv.org/abs/2212.06886",
                type="article",
                level="advanced",
                description="Modern perspective on moduli stabilization"
            ),
            LearningResource(
                title="Racetrack Superpotentials - Burgess, Quevedo, et al.",
                url="https://arxiv.org/abs/hep-th/0209104",
                type="article",
                level="advanced",
                description="Detailed analysis with examples"
            )
        ]
    )

    HIDDEN_VARIABLES = Formula(
        id="hidden-variables",
        input_params=['dimensions.D_SHARED_EXTRAS'],
        label="(3.3) Hidden Variables Density Matrix",
        html="ρ<sub>Σ₁</sub> = Tr<sub>Σ₂,Σ₃,Σ₄</sub>[|Ψ⟩<sub>bulk</sub>⟨Ψ|]",
        latex="\\rho_{\\Sigma_1} = \\text{Tr}_{\\Sigma_2,\\Sigma_3,\\Sigma_4} \\left[|\\Psi\\rangle_{\\text{bulk}} \\langle\\Psi|\\right]",
        plain_text="ρ_Σ₁ = Tr_{Σ₂,Σ₃,Σ₄}[|Ψ⟩_bulk⟨Ψ|]",
        category=FormulaCategory.THEORY,
        description="Observable sector density matrix from tracing out shadow branes",
        section="3",
        terms={
            "ρ_Σ₁": FormulaTerm("Observable Density", "Reduced density matrix on our brane"),
            "Σ₂,Σ₃,Σ₄": FormulaTerm("Shadow Branes", "Hidden sector branes traced out"),
            "|Ψ⟩_bulk": FormulaTerm("Bulk State", "Full 26D quantum state"),
        },
        notes="Provides geometric origin for quantum hidden variables",
        related_formulas=["reduction-cascade"],
        learning_resources=[
            LearningResource(
                title="Operator Algebras and Quantum Statistical Mechanics - Bratteli & Robinson",
                url="https://www.springer.com/gp/book/9783540170938",
                type="article",
                level="advanced",
                description="Volume 2, Chapter 5: Tomita-Takesaki theory and modular flow"
            ),
            LearningResource(
                title="Modular Theory in Quantum Field Theory",
                url="https://arxiv.org/abs/1902.05442",
                type="article",
                level="advanced",
                description="Modern pedagogical review of modular theory applications"
            )
        ]
    )

    HIERARCHY_RATIO = Formula(
        id="hierarchy-ratio",
        label="(4.4d) Hierarchy Ratio",
        html="M<sub>Pl</sub>/v<sub>EW</sub> ~ 1/√h¹¹ × M<sub>Pl,bulk</sub>/v<sub>EW,0</sub> = 2 × 10<sup>16</sup>",
        latex="\\frac{M_{\\text{Pl}}}{v_{\\text{EW}}} \\sim \\frac{1}{\\sqrt{h^{1,1}}} \\times \\frac{M_{\\text{Pl,bulk}}}{v_{\\text{EW,0}}} = 2 \\times 10^{16}",
        plain_text="M_Pl/v_EW ~ 1/√h¹¹ × M_Pl,bulk/v_EW,0 = 2 × 10¹⁶",
        category=FormulaCategory.DERIVED,
        description="Hierarchy problem solution from multi-sector sampling",
        section="4",
        terms={
            "M_Pl": FormulaTerm("Planck Mass", "4D effective Planck mass"),
            "v_EW": FormulaTerm("Electroweak VEV", "Higgs vacuum expectation value"),
            "h¹¹": FormulaTerm("Kähler Moduli", "= 4 sectors"),
        },
        notes="Natural explanation for 10¹⁶ hierarchy without fine-tuning",
        related_formulas=["higgs-vev", "tcs-topology"],
        references=[
            FormulaReference("arkani-hamed1998", "The Hierarchy problem and new dimensions at a millimeter", "Arkani-Hamed, N., Dimopoulos, S., & Dvali, G.", 1998, arxiv="hep-ph/9803315"),
            FormulaReference("randall1999", "A Large Mass Hierarchy from a Small Extra Dimension", "Randall, L. & Sundrum, R.", 1999, arxiv="hep-ph/9905221"),
            FormulaReference("kklt2003", "de Sitter Vacua in String Theory", "Kachru, S., Kallosh, R., Linde, A., & Trivedi, S.P.", 2003, arxiv="hep-th/0301240"),
        ],
        learning_resources=[
            LearningResource(
                title="The Standard Model in a Nutshell - Dave Goldberg",
                url="https://press.princeton.edu/books/hardcover/9780691167596/the-standard-model-in-a-nutshell",
                type="article",
                level="intermediate",
                description="Chapter 7: The Higgs Mechanism and hierarchy problem"
            ),
            LearningResource(
                title="Perimeter PSI - Extra Dimensions",
                url="https://www.youtube.com/results?search_query=Perimeter+PSI+Extra+Dimensions+hierarchy",
                type="video",
                duration="2 hours",
                level="advanced",
                description="Topics: KK reduction, warped geometries, hierarchy solutions"
            )
        ]
    )

    DIVISION_ALGEBRA = Formula(
        id="division-algebra",
        label="(3.4) Division Algebra Decomposition",
        html="D = 13 = 1(ℝ) + 4(ℍ) + 8(𝕆)",
        latex="D = 13 = 1(\\mathbb{R}) + 4(\\mathbb{H}) + 8(\\mathbb{O})",
        plain_text="D = 13 = 1(R) + 4(H) + 8(O)",
        category=FormulaCategory.THEORY,
        description="13D as unique combination of division algebra dimensions",
        section="3",
        terms={
            "ℝ": FormulaTerm("Reals", "1D: Thermal time (emergent)"),
            "ℍ": FormulaTerm("Quaternions", "4D: Spacetime (Lorentz)"),
            "𝕆": FormulaTerm("Octonions", "8D: Internal (Pneuma gauge)"),
        },
        notes="Explains why D=13 is special: Ω₁₃^String = 0 (cobordism)",
        related_formulas=["reduction-cascade"],
        learning_resources=[
            LearningResource(
                title="Itzhak Bars - Two-Time Physics",
                url="https://arxiv.org/abs/hep-th/0604051",
                type="article",
                level="advanced",
                description="Complete introduction to 2T-physics framework and Sp(2,R) gauge theory"
            ),
            LearningResource(
                title="3Blue1Brown - Quaternions and 3D Rotation",
                url="https://www.youtube.com/watch?v=d4EgbgTm0Bg",
                type="video",
                duration="20 min",
                level="intermediate",
                description="Visual understanding of quaternion algebra"
            ),
            LearningResource(
                title="Division Algebras and Supersymmetry - John Baez",
                url="https://arxiv.org/abs/hep-th/0105212",
                type="article",
                level="advanced",
                description="Connections between R, C, H, O and physics"
            )
        ]
    )

    SEESAW_MECHANISM = Formula(
        id="seesaw-mechanism",
        input_params=['gauge.M_GUT'],
        output_params=['neutrino.mass_spectrum'],
        label="(6.10) Type-I Seesaw",
        html="m<sub>ν</sub> = -Y<sub>D</sub><sup>T</sup> M<sub>R</sub><sup>-1</sup> Y<sub>D</sub> · v<sub>EW</sub>²",
        latex="m_\\nu = -Y_D^T M_R^{-1} Y_D \\cdot v_{\\text{EW}}^2",
        plain_text="m_ν = -Y_D^T M_R^{-1} Y_D · v_EW²",
        category=FormulaCategory.THEORY,
        description="Light neutrino masses from heavy right-handed neutrinos",
        section="6",
        terms={
            "m_ν": FormulaTerm("Light Neutrino Mass", "Sub-eV scale masses"),
            "Y_D": FormulaTerm("Dirac Yukawa", "Neutrino Yukawa coupling matrix"),
            "M_R": FormulaTerm("Majorana Mass", "Heavy right-handed neutrino mass"),
            "v_EW": FormulaTerm("Electroweak VEV", "= 246 GeV"),
        },
        related_formulas=["neutrino-mass-21", "neutrino-mass-31"],
        references=[
            FormulaReference("minkowski1977", "μ → eγ at a Rate of One Out of 10⁹ Muon Decays?", "Minkowski, P.", 1977, doi="10.1016/0370-2693(77)90435-X"),
            FormulaReference("gell-mann1979", "Complex Spinors and Unified Theories", "Gell-Mann, M., Ramond, P., & Slansky, R.", 1979, arxiv="1306.4669"),
            FormulaReference("mohapatra1980_seesaw", "Neutrino Mass and Spontaneous Parity Nonconservation", "Mohapatra, R.N. & Senjanović, G.", 1980, doi="10.1103/PhysRevLett.44.912"),
        ],
        learning_resources=[
            LearningResource(
                title="Fundamentals of Neutrino Physics - Giunti & Kim",
                url="https://www.oxfordscholarship.com/view/10.1093/acprof:oso/9780198508717.001.0001/acprof-9780198508717",
                type="article",
                level="advanced",
                description="Chapters 3-5: Mixing, oscillations, mass models including seesaw mechanism"
            ),
            LearningResource(
                title="Neutrino Mass Models - de Gouvêa",
                url="https://arxiv.org/abs/1411.0308",
                type="article",
                level="advanced",
                description="Comprehensive review of neutrino mass generation mechanisms"
            ),
            LearningResource(
                title="Wikipedia - Seesaw Mechanism",
                url="https://en.wikipedia.org/wiki/Seesaw_mechanism",
                type="article",
                level="intermediate",
                description="Accessible introduction to Type-I seesaw"
            )
        ],
        simulation_file="simulations/neutrino_mass_matrix_final_v12_7.py"
    )

    CKM_ELEMENTS = Formula(
        id="ckm-elements",
        label="(6.10) CKM Matrix Elements",
        html="|V<sub>ud</sub>| = 0.974, |V<sub>us</sub>| = 0.225, |V<sub>cb</sub>| = 0.041, |V<sub>ub</sub>| = 0.0036",
        latex="|V_{ud}| = 0.974, \\quad |V_{us}| = 0.225, \\quad |V_{cb}| = 0.041, \\quad |V_{ub}| = 0.0036",
        plain_text="|V_ud| = 0.974, |V_us| = 0.225, |V_cb| = 0.041, |V_ub| = 0.0036",
        category=FormulaCategory.PREDICTIONS,
        description="CKM quark mixing matrix elements from geometry",
        section="6",
        status="Within 2σ of PDG",
        notes="Derived from G₂ wavefunction overlaps",
        related_formulas=["theta23-maximal"],
        references=[
            FormulaReference("cabibbo1963", "Unitary Symmetry and Leptonic Decays", "Cabibbo, N.", 1963, doi="10.1103/PhysRevLett.10.531"),
            FormulaReference("kobayashi1973_ckm", "CP-Violation in the Renormalizable Theory of Weak Interaction", "Kobayashi, M. & Maskawa, T.", 1973, doi="10.1143/PTP.49.652"),
            FormulaReference("pdg2024_ckm", "Review of Particle Physics (CKM matrix)", "Particle Data Group", 2024, doi="10.1103/PhysRevD.110.030001"),
        ],
        learning_resources=[
            LearningResource(
                title="CERN Summer Student Lectures - Flavor Physics",
                url="https://indico.cern.ch/category/345/",
                type="video",
                duration="90 min",
                level="advanced",
                description="Topics: CKM matrix, CP violation, B-physics"
            ),
            LearningResource(
                title="CKMfitter Group - Global Fits",
                url="http://ckmfitter.in2p3.fr/",
                type="interactive",
                level="intermediate",
                description="Interactive plots and global fits to CKM parameters"
            ),
            LearningResource(
                title="Particle Data Group - CKM Matrix",
                url="https://pdg.lbl.gov/",
                type="article",
                level="intermediate",
                description="Section on 'The CKM Quark-Mixing Matrix' with latest data"
            )
        ],
        simulation_file="simulations/ckm_cp_rigor.py"
    )

    YUKAWA_INSTANTON = Formula(
        id="yukawa-instanton",
        input_params=['gauge.M_GUT'],
        label="(6.11) Yukawa Instanton Suppression",
        html="Y<sub>ij</sub> = Y<sub>ij</sub><sup>(0)</sup> · e<sup>-S<sub>inst</sub></sup> = Y<sup>(0)</sup> · e<sup>-Vol(Σ<sub>ij</sub>)/l<sub>s</sub>³</sup>",
        latex="Y_{ij} = Y_{ij}^{(0)} \\cdot e^{-S_{\\text{inst}}} = Y_{ij}^{(0)} \\cdot e^{-\\text{Vol}(\\Sigma_{ij})/l_s^3}",
        plain_text="Y_ij = Y_ij^(0) · exp(-S_inst) = Y^(0) · exp(-Vol(Σ_ij)/l_s³)",
        category=FormulaCategory.DERIVED,
        description="Yukawa coupling suppression from worldsheet instantons",
        section="6",
        terms={
            "Y_ij": FormulaTerm("Yukawa Coupling", "Generation-dependent couplings"),
            "S_inst": FormulaTerm("Instanton Action", "Worldsheet area/string scale"),
            "Σ_ij": FormulaTerm("Instanton Surface", "Minimal area connecting generations"),
        },
        notes="Explains fermion mass hierarchies geometrically",
        related_formulas=["top-quark-mass"],
        references=[
            FormulaReference("witten1996", "Strong Coupling Expansion Of Calabi-Yau Compactification", "Witten, E.", 1996, arxiv="hep-th/9602070"),
            FormulaReference("blumenhagen2005", "Toward realistic intersecting D-brane models", "Blumenhagen, R., Cvetic, M., Langacker, P., & Shiu, G.", 2005, arxiv="hep-th/0502005"),
            FormulaReference("donagi2008", "Model Building with F-Theory", "Donagi, R. & Wijnholt, M.", 2008, arxiv="0802.2969"),
        ],
        learning_resources=[
            LearningResource(
                title="Understanding Fermion Masses - Antusch & King",
                url="https://arxiv.org/abs/hep-ph/0402121",
                type="article",
                level="advanced",
                description="Reviews Froggatt-Nielsen mechanism, flavor symmetries"
            ),
            LearningResource(
                title="Yukawa Textures from String Theory",
                url="https://arxiv.org/abs/1105.3424",
                type="article",
                level="advanced",
                description="Geometric origin of mass hierarchies from instantons"
            )
        ],
        simulation_file="simulations/g2_yukawa_overlap_integrals_v15_0.py"
    )

    ATTRACTOR_POTENTIAL = Formula(
        id="attractor-potential",
        input_params=['pneuma.VEV'],
        label="(7.6) Attractor Potential",
        html="V(φ<sub>M</sub>) = V<sub>flux</sub>e<sup>-aφ</sup> + V<sub>inst</sub>e<sup>-b/φ</sup> + V<sub>axion</sub>cos(φ/f)",
        latex="V(\\phi_M) = V_{\\text{flux}} e^{-a\\phi_M} + V_{\\text{inst}} e^{-b/\\phi_M} + V_{\\text{axion}} \\cos\\left(\\frac{\\phi_M}{f}\\right)",
        plain_text="V(φ_M) = V_flux·exp(-a·φ) + V_inst·exp(-b/φ) + V_axion·cos(φ/f)",
        category=FormulaCategory.THEORY,
        description="Complete attractor scalar potential for late-time cosmology",
        section="7",
        terms={
            "φ_M": FormulaTerm("Mashiach Modulus", "log(Vol_7) = cosmological scalar"),
            "V_flux": FormulaTerm("Flux Potential", "From G-flux on G₂"),
            "V_inst": FormulaTerm("Instanton Uplift", "Non-perturbative correction"),
            "V_axion": FormulaTerm("Axion Modulation", "Periodic axionic component"),
        },
        simulation_file="simulations/attractor_scalar_v12_8.py",
        related_formulas=["dark-energy-w0", "dark-energy-wa"],
        learning_resources=[
            LearningResource(
                title="Modern Cosmology - Scott Dodelson",
                url="https://www.sciencedirect.com/book/9780122191411/modern-cosmology",
                type="article",
                level="advanced",
                description="Chapter 9: Dark Energy and attractor dynamics"
            ),
            LearningResource(
                title="Sean Carroll - The Big Picture: Dark Energy",
                url="https://www.youtube.com/results?search_query=Sean+Carroll+dark+energy+cosmology",
                type="video",
                duration="60 min",
                level="intermediate",
                description="Topics: Cosmological constant, equation of state, acceleration"
            )
        ]
    )

    FRIEDMANN_CONSTRAINT = Formula(
        id="friedmann-constraint",
        input_params=['dark_energy.w0', 'dark_energy.wa'],
        label="(7.9) Friedmann Constraint",
        html="H² = (2κ/3)[ρ + ρ<sub>DE</sub>(t)]",
        latex="H^2 = \\frac{2\\kappa}{3}[\\rho + \\rho_{\\text{DE}}(t)]",
        plain_text="H² = (2κ/3)[ρ + ρ_DE(t)]",
        category=FormulaCategory.ESTABLISHED,
        description="Friedmann constraint with dynamical dark energy",
        section="7",
        attribution="[Friedmann 1922]",
        terms={
            "H": FormulaTerm("Hubble Parameter", "Expansion rate a'/a"),
            "κ": FormulaTerm("Gravitational Constant", "8πG"),
            "ρ": FormulaTerm("Matter Density", "Total matter energy density"),
            "ρ_DE": FormulaTerm("Dark Energy Density", "Time-dependent from PM"),
        },
        related_formulas=["dark-energy-w0", "dark-energy-wa"],
        learning_resources=[
            LearningResource(
                title="Introduction to Cosmology - Barbara Ryden",
                url="https://www.cambridge.org/core/books/introduction-to-cosmology/7B4C3E6F3E5C0E9F5F5A5F5F5F5F5F5F",
                type="article",
                level="intermediate",
                description="Chapter 7: Dark Energy and the Accelerating Universe"
            ),
            LearningResource(
                title="Spacetime and Geometry - Sean Carroll",
                url="https://arxiv.org/abs/gr-qc/9712019",
                type="article",
                level="advanced",
                description="Chapters on Friedmann equations and cosmology"
            )
        ],
        simulation_file="simulations/wz_evolution_desi_dr2.py"
    )

    DE_SITTER_ATTRACTOR = Formula(
        id="de-sitter-attractor",
        input_params=['pneuma.VEV'],
        label="(7.10) de Sitter Attractor",
        html="H → H<sub>∞</sub> (constant), w → -1 as t → ∞",
        latex="H \\to H_\\infty \\, (\\text{constant}), \\quad w \\to -1 \\, \\text{as} \\, t \\to \\infty",
        plain_text="H → H_∞ (constant), w → -1 as t → ∞",
        category=FormulaCategory.DERIVED,
        description="Late-time de Sitter attractor from thermal time",
        section="7",
        notes="Ensures cosmic acceleration approaches de Sitter exponentially",
        related_formulas=["attractor-potential", "dark-energy-wa"],
        learning_resources=[
            LearningResource(
                title="Modern Cosmology - Scott Dodelson",
                url="https://www.sciencedirect.com/book/9780122191411/modern-cosmology",
                type="article",
                level="advanced",
                description="Chapter 3: Dynamics of the Universe, de Sitter solutions"
            ),
            LearningResource(
                title="DESI Collaboration - Dark Energy Results",
                url="https://data.desi.lbl.gov/",
                type="article",
                level="intermediate",
                description="2024 results on dark energy evolution and w(z) measurements"
            )
        ],
        simulation_file="simulations/attractor_scalar_v12_8.py"
    )

    TOMITA_TAKESAKI = Formula(
        id="tomita-takesaki",
        label="(7.7) Tomita-Takesaki Theorem",
        html="Δ<sup>it</sup>𝒜Δ<sup>-it</sup> = 𝒜, S = JΔ<sup>1/2</sup>",
        latex="\\Delta^{it} \\mathcal{A} \\Delta^{-it} = \\mathcal{A}, \\quad S = J\\Delta^{1/2}",
        plain_text="Δ^it 𝒜 Δ^{-it} = 𝒜, S = JΔ^{1/2}",
        category=FormulaCategory.ESTABLISHED,
        description="Modular automorphism theorem for von Neumann algebras",
        section="7",
        attribution="[Tomita 1967, Takesaki 1970]",
        terms={
            "Δ": FormulaTerm("Modular Operator", "Positive self-adjoint operator"),
            "𝒜": FormulaTerm("Observable Algebra", "von Neumann algebra"),
            "J": FormulaTerm("Modular Conjugation", "Anti-unitary involution"),
            "S": FormulaTerm("Tomita Operator", "S = JΔ^{1/2}"),
        },
        notes="Foundation for thermal time hypothesis",
        related_formulas=["thermal-time"],
        learning_resources=[
            LearningResource(
                title="Operator Algebras and Quantum Statistical Mechanics - Bratteli & Robinson",
                url="https://www.springer.com/gp/book/9783540170938",
                type="article",
                level="advanced",
                description="Volume 2, Chapter 5: Tomita-Takesaki theory"
            ),
            LearningResource(
                title="Thermal Time and Tolman-Ehrenfest Effect - Connes & Rovelli",
                url="https://doi.org/10.1088/0264-9381/11/12/007",
                type="article",
                level="advanced",
                description="Original thermal time hypothesis, Class. Quantum Grav. 11 (1994) 2899"
            ),
            LearningResource(
                title="Wikipedia - Tomita-Takesaki Theory",
                url="https://en.wikipedia.org/wiki/Tomita%E2%80%93Takesaki_theory",
                type="article",
                level="intermediate",
                description="Introduction to modular theory for von Neumann algebras"
            )
        ]
    )

    KMS_CONDITION = Formula(
        id="kms-condition",
        label="(7.8) KMS Condition",
        html="⟨A(t + iβ)B⟩ = ⟨BA(t)⟩ with β = 1/(k<sub>B</sub>T)",
        latex="\\langle A(t + i\\beta)B \\rangle = \\langle BA(t) \\rangle \\, \\text{with} \\, \\beta = \\frac{1}{k_B T}",
        plain_text="⟨A(t + iβ)B⟩ = ⟨BA(t)⟩ with β = 1/(k_B T)",
        category=FormulaCategory.ESTABLISHED,
        description="Kubo-Martin-Schwinger condition for thermal equilibrium",
        section="7",
        attribution="[Kubo 1957, Martin-Schwinger 1959]",
        terms={
            "A,B": FormulaTerm("Observables", "Operators in the algebra"),
            "β": FormulaTerm("Inverse Temperature", "= 1/(k_B T)"),
            "t + iβ": FormulaTerm("Complex Time", "Analytic continuation"),
        },
        notes="Characterizes thermal states in QFT",
        related_formulas=["thermal-time", "tomita-takesaki"],
        learning_resources=[
            LearningResource(
                title="Thermal Time and Tolman-Ehrenfest Effect - Connes & Rovelli",
                url="https://doi.org/10.1088/0264-9381/11/12/007",
                type="article",
                level="advanced",
                description="KMS condition in context of thermal time, Class. Quantum Grav. 11 (1994)"
            ),
            LearningResource(
                title="Modular Theory in Quantum Field Theory",
                url="https://arxiv.org/abs/1902.05442",
                type="article",
                level="advanced",
                description="Modern review including KMS states"
            )
        ]
    )

    PLANCK_MASS_DERIVATION = Formula(
        id="planck-mass-derivation",
        label="(4.5) Planck Mass from Volume",
        html="M<sub>Pl</sub>² = M<sub>*</sub><sup>11</sup> × V<sub>9</sub> / 16πG<sub>N</sub>",
        latex="M_{Pl}^2 = M_*^{11} \\times V_9 / 16\\pi G_N",
        plain_text="M_Pl² = M_*^11 × V_9 / 16πG_N",
        category=FormulaCategory.DERIVED,
        description="4D Planck mass from 13D fundamental scale and internal volume",
        section="4",
        terms={
            "M_Pl": FormulaTerm("4D Planck Mass", "2.435×10¹⁸ GeV"),
            "M_*": FormulaTerm("13D Fundamental Scale", "~7.5×10¹⁵ GeV"),
            "V_9": FormulaTerm("Internal Volume", "G₂ × T² volume"),
        },
        related_formulas=["gut-scale", "tcs-topology"],
        references=[
            FormulaReference("kaluza1921", "Zum Unitätsproblem der Physik", "Kaluza, T.", 1921),
            FormulaReference("klein1926", "Quantentheorie und fünfdimensionale Relativitätstheorie", "Klein, O.", 1926, doi="10.1007/BF01397481"),
            FormulaReference("witten1981", "Search for a Realistic Kaluza-Klein Theory", "Witten, E.", 1981, doi="10.1016/0550-3213(81)90021-3"),
        ],
        learning_resources=[
            LearningResource(
                title="TASI Lectures on Extra Dimensions - Csaba Csaki",
                url="https://arxiv.org/abs/hep-ph/0404096",
                type="article",
                level="advanced",
                description="Comprehensive introduction to Kaluza-Klein theory and volume-mass relations"
            ),
            LearningResource(
                title="Quantum Field Theory in a Nutshell - A. Zee",
                url="https://press.princeton.edu/books/hardcover/9780691140346/quantum-field-theory-in-a-nutshell",
                type="article",
                level="advanced",
                description="Chapter VIII.2: Kaluza-Klein and higher dimensions"
            )
        ]
    )

    DOUBLET_TRIPLET = Formula(
        id="doublet-triplet",
        input_params=['gauge.M_GUT', 'pneuma.VEV'],
        label="(5.4c) Doublet-Triplet Splitting",
        html="N<sub>doublets</sub> - N<sub>triplets</sub> = ∫<sub>M</sub> Â(M) ∧ ch(L<sub>Y</sub>) mod ℤ₂",
        latex="N_{\\text{doublets}} - N_{\\text{triplets}} = \\int_M \\hat{A}(M) \\wedge \\text{ch}(L_Y) \\mod \\mathbb{Z}_2",
        plain_text="N_doublets - N_triplets = ∫_M Â(M) ∧ ch(L_Y) mod Z₂",
        category=FormulaCategory.DERIVED,
        description="Index theorem for doublet-triplet splitting in Higgs sector",
        section="5",
        terms={
            "Â(M)": FormulaTerm("A-roof Genus", "Characteristic class of manifold"),
            "ch(L_Y)": FormulaTerm("Chern Character", "Of hypercharge line bundle"),
            "ℤ₂": FormulaTerm("Z₂ Quotient", "From orbifold projection"),
        },
        notes="Topological protection against proton decay from Higgs",
        related_formulas=["proton-lifetime", "so10-breaking"],
        references=[
            FormulaReference("atiyah1963", "The Index of Elliptic Operators on Compact Manifolds", "Atiyah, M.F. & Singer, I.M.", 1963, doi="10.1090/S0002-9904-1963-10957-X"),
            FormulaReference("witten1985", "Symmetry Breaking Patterns in Superstring Models", "Witten, E.", 1985, doi="10.1016/0550-3213(85)90603-0"),
            FormulaReference("kawamura2001", "Triplet-doublet splitting, proton stability and extra dimension", "Kawamura, Y.", 2001, arxiv="hep-ph/0012125"),
        ],
        learning_resources=[
            LearningResource(
                title="Doublet-Triplet Splitting in GUTs - Dermisek",
                url="https://arxiv.org/abs/hep-ph/0507133",
                type="article",
                level="advanced",
                description="Reviews solutions to the DT splitting problem in GUT theories"
            ),
            LearningResource(
                title="Modern Particle Physics - Mark Thomson",
                url="https://www.cambridge.org/core/books/modern-particle-physics/",
                type="article",
                level="intermediate",
                description="Chapter 17: Grand Unification and Higgs sector"
            )
        ]
    )

    DIRAC_PNEUMA = Formula(
        id="dirac-pneuma",
        input_params=['pneuma.VEV'],
        label="(3.1) Pneuma Dirac Equation",
        html="(iΓ<sup>M</sup>D<sub>M</sub> - m)Ψ<sub>P</sub> = 0",
        latex="(i\\Gamma^M D_M - m)\\Psi_P = 0",
        plain_text="(iΓᴹD_M - m)Ψ_P = 0",
        category=FormulaCategory.THEORY,
        description="Dirac equation for Pneuma spinor field",
        section="3",
        terms={
            "Γ^M": FormulaTerm("Gamma Matrices", "13D Clifford algebra generators"),
            "D_M": FormulaTerm("Covariant Derivative", "Includes spin connection"),
            "m": FormulaTerm("Pneuma Mass", "Fundamental mass parameter"),
            "Ψ_P": FormulaTerm("Pneuma Spinor", "64 components per shadow (v21 dual structure)"),
        },
        simulation_file="simulations/g2_spinor_geometry_validation_v13_0.py",
        related_formulas=["master-action-26d", "primordial-spinor-13d"]
    )

    # =========================================================================
    # SUPPLEMENTARY APPENDIX FORMULAS (Agent-recommended additions)
    # =========================================================================

    GHOST_COEFFICIENT = Formula(
        id="ghost-coefficient",
        label="(D.1) Ghost Coefficient",
        html="γ = |c<sub>ghost</sub>|/(2c<sub>matter</sub>) = 26/(2×26) = 0.5",
        latex="\\gamma = \\frac{|c_{\\text{ghost}}|}{2 c_{\\text{matter}}} = \\frac{26}{2 \\times 26} = 0.5",
        plain_text="γ = |c_ghost|/(2c_matter) = 26/(2×26) = 0.5",
        category=FormulaCategory.DERIVED,
        description="Ghost coefficient from Virasoro anomaly structure",
        section="Appendix D",
        terms={
            "γ": FormulaTerm("Ghost Coefficient", "Contribution factor to effective dimension"),
            "c_ghost": FormulaTerm("Ghost Central Charge", "= -26 from reparametrization ghosts"),
            "c_matter": FormulaTerm("Matter Central Charge", "= 26 from spacetime dimensions"),
        },
        computed_value=0.5,
        related_formulas=["virasoro-anomaly", "effective-dimension"],
        simulation_file="simulations/virasoro_anomaly_v12_8.py"
    )

    KAPPA_GUT_COEFFICIENT = Formula(
        id="kappa-gut-coefficient",
        label="(E.4) GUT Scale Coefficient",
        html="κ = 10π/V<sub>5</sub><sup>1/5</sup> = 10π/21.6 = 1.46",
        latex="\\kappa = \\frac{10\\pi}{V_5^{1/5}} = \\frac{10\\pi}{21.6} = 1.46",
        plain_text="κ = 10π/V_5^(1/5) = 10π/21.6 = 1.46",
        category=FormulaCategory.DERIVED,
        description="GUT scale coefficient from G₂ 5-cycle volume",
        section="Appendix E",
        terms={
            "κ": FormulaTerm("GUT Coefficient", "Gauge kinetic function normalization"),
            "V_5": FormulaTerm("5-Cycle Volume", "= (b₂·b₃/4π)^(5/3) = 21.6"),
        },
        computed_value=1.46,
        related_formulas=["gut-scale", "tcs-topology"],
        simulation_file="simulations/gauge_unification_precision_v12_4.py"
    )

    EFFECTIVE_TORSION_SPINOR = Formula(
        id="effective-torsion-spinor",
        label="(G.3) Torsion Spinor Correction",
        html="T<sub>ω</sub> = -1.000 × (7/8) = -0.875",
        latex="T_\\omega = -1.000 \\times \\frac{7}{8} = -0.875",
        plain_text="T_ω = -1.000 × (7/8) = -0.875",
        category=FormulaCategory.DERIVED,
        description="Effective torsion with Spin(7) spinor fraction correction",
        section="Appendix G",
        terms={
            "T_ω": FormulaTerm("Effective Torsion", "With spinor stabilization"),
            "7/8": FormulaTerm("Spinor Fraction", "G₄ flux stabilizes 7 of 8 components"),
        },
        computed_value=-0.875,
        experimental_value=-0.884,  # Source: PM phenomenological fit
        sigma_deviation=1.02,
        notes="1.02% agreement with phenomenological value",
        related_formulas=["effective-torsion", "flux-quantization"],
        simulation_file="simulations/torsion_spinor_fraction_v12_8.py"
    )

    GW_DISPERSION_ALT = Formula(
        id="gw-dispersion-alt",
        label="(I.4) GW Dispersion (Alternative)",
        html="η<sup>alt</sup> = e<sup>0.882</sup>/24 ≈ 0.101",
        latex="\\eta^{\\text{alt}} = \\frac{e^{0.882}}{24} \\approx 0.101",
        plain_text="η_alt = exp(0.882)/24 ≈ 0.101",
        category=FormulaCategory.PREDICTIONS,
        description="Alternative GW dispersion with phenomenological normalization",
        section="Appendix I",
        terms={
            "η_alt": FormulaTerm("Alternative Dispersion", "Using C = 27.2 normalization"),
            "T_ω^alt": FormulaTerm("Alternative Torsion", "= -b₃/27.2 = -0.882"),
        },
        computed_value=0.101,
        notes="0.2% agreement with phenomenological torsion T_ω = -0.884",
        related_formulas=["gw-dispersion-coeff", "effective-torsion"],
        simulation_file="simulations/gw_dispersion_v12_8.py"
    )

    # =========================================================================
    # SECTION 2-3 SUPPLEMENTARY FORMULAS (From gap analysis)
    # =========================================================================

    VACUUM_MINIMIZATION = Formula(
        id="vacuum-minimization",
        input_params=['pneuma.VEV', 'gauge.M_GUT'],
        label="(2.8) Vacuum Minimization Condition",
        html="∂V/∂Ψ<sub>P</sub> = 0 ⟹ Aa·e<sup>-a⟨Ψ<sub>P</sub>⟩</sup> = Bb·e<sup>-b⟨Ψ<sub>P</sub>⟩</sup>",
        latex="\\frac{\\partial V}{\\partial \\Psi_P} = 0 \\quad \\Rightarrow \\quad Aa \\, e^{-a\\langle\\Psi_P\\rangle} = Bb \\, e^{-b\\langle\\Psi_P\\rangle}",
        plain_text="∂V/∂Ψ_P = 0 ⟹ Aa·exp(-a⟨Ψ_P⟩) = Bb·exp(-b⟨Ψ_P⟩)",
        category=FormulaCategory.DERIVED,
        description="Vacuum stability condition for racetrack potential minimum",
        section="2",
        terms={
            "V": FormulaTerm("Scalar Potential", "F-term potential from superpotential"),
            "⟨Ψ_P⟩": FormulaTerm("Vacuum VEV", "Pneuma field vacuum expectation value ≈ 1.076"),
            "a, b": FormulaTerm("Racetrack Exponents", "a = 2π/24, b = 2π/25 from N_flux"),
            "A, B": FormulaTerm("Instanton Amplitudes", "Non-perturbative prefactors ~ O(1)"),
        },
        derivation=FormulaDerivation(
            parent_formulas=["scalar-potential", "racetrack-superpotential"],
            established_physics=["f-term-stabilization"],
            steps=[
                "Take derivative of V = |∂W/∂Ψ|² w.r.t. Ψ_P",
                "Set to zero for stable vacuum",
                "Solve transcendentally for ⟨Ψ_P⟩ ≈ 1.076"
            ]
        ),
        simulation_file="simulations/pneuma_full_potential_v14_1.py",
        related_formulas=["scalar-potential", "pneuma-vev", "racetrack-superpotential"]
    )

    MIRROR_TEMP_RATIO = Formula(
        id="mirror-temp-ratio",
        output_params=['cosmology.T_mirror_ratio'],
        label="(4.5a) Mirror Sector Temperature",
        html="T'/T = 0.57 = (b<sub>2</sub>/b<sub>3</sub>)<sup>1/4</sup>",
        latex="\\frac{T'}{T} = 0.57 = \\left(\\frac{b_2}{b_3}\\right)^{1/4}",
        plain_text="T'/T = 0.57 = (b₂/b₃)^{1/4}",
        category=FormulaCategory.DERIVED,
        description="Mirror sector temperature ratio from G₂ topology",
        section="4",
        status="GEOMETRIC",
        terms={
            "T'": FormulaTerm("Mirror Temperature", "Shadow sector thermal bath temperature"),
            "T": FormulaTerm("Observable Temperature", "Standard Model thermal bath"),
            "b₂": FormulaTerm("Second Betti", "= 4 (Kähler moduli count)"),
            "b₃": FormulaTerm("Third Betti", "= 24 (associative 3-cycles)"),
        },
        derivation=FormulaDerivation(
            parent_formulas=["tcs-topology"],
            established_physics=["thermal-field-theory"],
            steps=[
                "Mirror sector couples through gravitational portal only",
                "Temperature ratio from cycle volume ratio: T'/T = (Vol₂/Vol₃)^{1/4}",
                "Use Betti numbers as proxy: T'/T = (b₂/b₃)^{1/4} = (4/24)^{1/4} = 0.57"
            ]
        ),
        simulation_file="simulations/mirror_dark_matter_abundance_v15_3.py",
        computed_value=0.57,
        related_formulas=["mirror-dm-ratio", "tcs-topology"]
    )

    # =========================================================================
    # SECTION 5 SUPPLEMENTARY FORMULAS (Gauge Unification)
    # =========================================================================

    PATI_SALAM_CHAIN = Formula(
        id="pati-salam-chain",
        input_params=['gauge.M_GUT'],
        label="(5.1a) Pati-Salam Breaking Chain",
        html="SO(10) → SU(4)<sub>C</sub> × SU(2)<sub>L</sub> × SU(2)<sub>R</sub> → SU(3)<sub>C</sub> × SU(2)<sub>L</sub> × U(1)<sub>Y</sub>",
        latex="\\text{SO}(10) \\to \\text{SU}(4)_C \\times \\text{SU}(2)_L \\times \\text{SU}(2)_R \\to \\text{SU}(3)_C \\times \\text{SU}(2)_L \\times \\text{U}(1)_Y",
        plain_text="SO(10) → SU(4)_C × SU(2)_L × SU(2)_R → SU(3)_C × SU(2)_L × U(1)_Y",
        category=FormulaCategory.THEORY,
        description="Intermediate Pati-Salam symmetry breaking chain (geometrically preferred)",
        section="5",
        terms={
            "SU(4)_C": FormulaTerm("Extended Color", "Unifies quarks and leptons"),
            "SU(2)_R": FormulaTerm("Right-Handed Weak", "Parity restoration at GUT scale"),
        },
        derivation=FormulaDerivation(
            parent_formulas=["so10-breaking"],
            established_physics=["pati-salam-gut"],
            steps=[
                "First breaking: SO(10) → SU(4)_C × SU(2)_L × SU(2)_R at M_GUT",
                "Second breaking: SU(4)_C → SU(3)_C × U(1)_{B-L} at intermediate scale",
                "Final: SU(2)_R × U(1)_{B-L} → U(1)_Y at M_PS ~ 10^12 GeV"
            ]
        ),
        simulation_file="simulations/breaking_chain_geometric_v14_1.py",
        notes="Provides right-handed neutrinos for seesaw mechanism",
        related_formulas=["so10-breaking", "seesaw-mechanism"]
    )

    HIGGS_POTENTIAL = Formula(
        id="higgs-potential",
        input_params=['pneuma.VEV'],
        label="(5.6a) Higgs Scalar Potential",
        html="V(H) = -μ²|H|² + λ|H|⁴",
        latex="V(H) = -\\mu^2 |H|^2 + \\lambda |H|^4",
        plain_text="V(H) = -μ²|H|² + λ|H|⁴",
        category=FormulaCategory.ESTABLISHED,
        description="Standard Model Higgs potential from EWSB",
        section="5",
        attribution="Weinberg-Salam",
        terms={
            "μ²": FormulaTerm("Higgs Mass Parameter", "< 0 for EWSB, |μ| ≈ 88 GeV"),
            "λ": FormulaTerm("Higgs Quartic", "≈ 0.13 at M_Z, fixed by m_h"),
            "H": FormulaTerm("Higgs Doublet", "SU(2)_L doublet scalar field"),
        },
        derivation=FormulaDerivation(
            parent_formulas=["higgs-vev"],
            established_physics=["electroweak-theory"],
            steps=[
                "SU(2)_L × U(1)_Y gauge theory requires scalar doublet H",
                "Most general renormalizable potential: V = -μ²|H|² + λ|H|⁴",
                "Minimum at ⟨H⟩ = v_EW/√2 with v_EW² = μ²/λ"
            ]
        ),
        simulation_file="simulations/pneuma_full_potential_v14_1.py",
        notes="Minimization gives v_EW = 246 GeV and m_h = √(2λ)v_EW = 125 GeV",
        related_formulas=["higgs-vev"]
    )

    HIGGS_QUARTIC = Formula(
        id="higgs-quartic",
        output_params=['higgs.lambda_0'],
        label="(5.6b) Higgs Quartic Coupling",
        html="λ(M<sub>Z</sub>) = m<sub>h</sub>²/(2v<sub>EW</sub>²) = 0.1296",
        latex="\\lambda(M_Z) = \\frac{m_h^2}{2v_{\\text{EW}}^2} = 0.1296",
        plain_text="λ(M_Z) = m_h²/(2v_EW²) = 0.1296",
        category=FormulaCategory.DERIVED,
        description="Higgs self-coupling from observed Higgs mass",
        section="5",
        terms={
            "λ": FormulaTerm("Quartic Coupling", "Higgs self-interaction strength"),
            "m_h": FormulaTerm("Higgs Mass", "125.20 GeV (PDG 2024)"),
            "v_EW": FormulaTerm("EW VEV", "246 GeV"),
        },
        computed_value=0.1296,
        experimental_value=0.1296,  # Source: Derived from PDG 2024 m_h and v_EW
        sigma_deviation=0.0,
        related_formulas=["higgs-potential", "higgs-vev"],
        simulation_file="simulations/higgs_yukawa_rg_v12_4.py"
    )

    RG_RUNNING_COUPLINGS = Formula(
        id="rg-running-couplings",
        input_params=['gauge.ALPHA_GUT', 'gauge.M_GUT'],
        label="(5.5c) RG Running of Gauge Couplings",
        html="dα<sub>i</sub><sup>-1</sup>/d ln(μ) = -b<sub>i</sub>/(2π), b = (41/10, -19/6, -7)",
        latex="\\frac{d\\alpha_i^{-1}}{d\\ln(\\mu)} = -\\frac{b_i}{2\\pi}, \\quad b = \\left(\\frac{41}{10}, -\\frac{19}{6}, -7\\right)",
        plain_text="dα_i^{-1}/d ln(μ) = -b_i/(2π), b = (41/10, -19/6, -7)",
        category=FormulaCategory.ESTABLISHED,
        description="One-loop RG evolution equations for SM gauge couplings",
        section="5",
        attribution="Georgi-Quinn-Weinberg 1974",
        terms={
            "α_i": FormulaTerm("Gauge Couplings", "i = 1(U(1)_Y), 2(SU(2)_L), 3(SU(3)_C)"),
            "b_i": FormulaTerm("Beta Coefficients", "1-loop beta function coefficients"),
            "μ": FormulaTerm("Renormalization Scale", "Energy scale for running"),
        },
        notes="Evolves from α_GUT = 1/23.54 at M_GUT to SM values at M_Z",
        simulation_file="simulations/gauge_unification_precision_v12_4.py",
        related_formulas=["gut-coupling", "weak-mixing-angle", "strong-coupling"]
    )

    # =========================================================================
    # SECTION 6 SUPPLEMENTARY FORMULAS (Fermion Masses)
    # =========================================================================

    BOTTOM_QUARK_MASS = Formula(
        id="bottom-quark-mass",
        output_params=['pdg.m_bottom'],
        label="(6.5) Bottom Quark Mass",
        html="m<sub>b</sub> = y<sub>b</sub> · v<sub>EW</sub>/√2 = 4.18 GeV",
        latex="m_b = y_b \\times \\frac{v_{\\text{EW}}}{\\sqrt{2}} = 4.18\\,\\text{GeV}",
        plain_text="m_b = y_b · v_EW/√2 = 4.18 GeV",
        category=FormulaCategory.PREDICTIONS,
        description="Bottom quark mass from geometric Yukawa coupling",
        section="6",
        status="EXACT MATCH",
        terms={
            "m_b": FormulaTerm("Bottom Mass", "Running mass at m_b scale"),
            "y_b": FormulaTerm("Bottom Yukawa", "≈ 0.024 from Froggatt-Nielsen"),
            "v_EW": FormulaTerm("EW VEV", "= 246 GeV"),
        },
        computed_value=4.18,
        units="GeV",
        experimental_value=4.18,  # Source: PDG 2024 m_b(m_b) = 4.18 ± 0.03 GeV
        experimental_error=0.03,
        sigma_deviation=0.0,
        related_formulas=["higgs-vev", "top-quark-mass", "yukawa-instanton"],
        simulation_file="simulations/higgs_yukawa_rg_v12_4.py"
    )

    TAU_LEPTON_MASS = Formula(
        id="tau-lepton-mass",
        output_params=['pdg.m_tau'],
        label="(6.6) Tau Lepton Mass",
        html="m<sub>τ</sub> = y<sub>τ</sub> · v<sub>EW</sub>/√2 = 1.777 GeV",
        latex="m_\\tau = y_\\tau \\times \\frac{v_{\\text{EW}}}{\\sqrt{2}} = 1.777\\,\\text{GeV}",
        plain_text="m_τ = y_τ · v_EW/√2 = 1.777 GeV",
        category=FormulaCategory.PREDICTIONS,
        description="Tau lepton mass from geometric Yukawa coupling",
        section="6",
        status="0.01% AGREEMENT",
        terms={
            "m_τ": FormulaTerm("Tau Mass", "Pole mass from geometric derivation"),
            "y_τ": FormulaTerm("Tau Yukawa", "≈ 0.0102 from cycle overlaps"),
            "v_EW": FormulaTerm("EW VEV", "= 246 GeV"),
        },
        computed_value=1.777,
        units="GeV",
        experimental_value=1.77686,  # Source: PDG 2024 m_τ = 1.77686 ± 0.00012 GeV
        experimental_error=0.00012,
        sigma_deviation=0.01,
        related_formulas=["higgs-vev", "top-quark-mass", "bottom-quark-mass"],
        simulation_file="simulations/higgs_yukawa_rg_v12_4.py"
    )

    HIGGS_MASS = Formula(
        id="higgs-mass",
        output_params=['pdg.m_higgs'],
        input_params=['pneuma.VEV'],
        label="(5.7) Higgs Boson Mass",
        html="m<sub>h</sub> = 125.20 GeV (constrains Re(T) ≈ 9.865 via inversion)",
        latex="m_h = 125.20\\,\\text{GeV}",
        plain_text="m_h = 125.20 GeV",
        category=FormulaCategory.ESTABLISHED,  # Experimental input, not derived
        description="Higgs mass is phenomenological INPUT that constrains Re(T) modulus",
        section="5",
        status="PHENOMENOLOGICAL INPUT",
        terms={
            "m_h": FormulaTerm(
                name="Higgs Boson Mass",
                description="Mass of the Standard Model Higgs boson measured at LHC",
                symbol="m_h",
                value="125.20 GeV",
                units="GeV",
                contribution="Experimental input that constrains moduli"
            ),
            "Re(T)": FormulaTerm(
                name="Volume Modulus",
                description="Real part of Kähler modulus T controlling G₂ volume",
                symbol="Re(T)",
                value="9.865 (Higgs inversion) / 7.086 (baryon asymmetry)",
                units="dimensionless",
                contribution="CONSTRAINED from m_h; baryon asymmetry uses calibrated 7.086"
            ),
        },
        info_title="Higgs Mass Constrains Moduli",
        info_meaning="The Higgs mass is NOT a prediction—it is an experimental INPUT. Inverting the formula yields Re(T) = 9.865. Note: the baryon asymmetry calculation uses a calibrated Re(T) = 7.086 (this tension is an open problem).",
        info_grid=[
            FormulaInfoItem(title="LHC Measurement", content="125.20 ± 0.11 GeV (PDG 2024)"),
            FormulaInfoItem(title="Role", content="INPUT (not prediction)"),
            FormulaInfoItem(title="Constrains", content="Re(T) = 9.865 (Higgs) / 7.086 (BBN)"),
        ],
        expansion_title="m_h = 125.10\\,\\text{GeV} \\Rightarrow \\text{Re}(T) = 9.865",
        sub_components=[
            FormulaSubComponent(symbol="m_h", name="Higgs Mass", description="Measured at LHC", badge="ESTABLISHED", badge_type="established"),
            FormulaSubComponent(symbol="Re(T)", name="Volume Modulus", description="From scalar potential minimum", badge="CONSTRAINED", badge_type="theory"),
        ],
        derivation_chain=[
            FormulaDerivationStep(title="LHC Discovery (2012)", badge="EXPERIMENTAL", badge_type="established"),
            FormulaDerivationStep(title="Modulus Constraint", badge="DERIVED", badge_type="theory"),
        ],
        discussion="The Higgs mass m_h = 125.10 GeV is experimental INPUT. Inverting the scalar potential yields Re(T) = 9.865. The baryon asymmetry uses a different calibrated value Re(T) = 7.086 — this tension is an open problem.",
        computed_value=125.10,  # PDG 2024: m_H = 125.20 +/- 0.11 GeV (INPUT, not prediction)
        units="GeV",
        experimental_value=125.20,  # Source: PDG 2024 m_H = 125.20 ± 0.11 GeV
        experimental_error=0.11,
        sigma_deviation=0.91,  # input 125.10 (2022 ATLAS+CMS vintage) vs PDG 2024 125.20 ± 0.11
        notes="NOT a prediction — m_h is INPUT. Higgs inversion gives Re(T) = 9.865; baryon asymmetry uses calibrated 7.086.",
        related_formulas=["higgs-vev", "higgs-potential"],
        simulation_file="simulations/higgs_mass_v12_4_moduli_stabilization.py"
    )

    @classmethod
    def get_all_formulas(cls) -> List[Formula]:
        """Get all core formulas as a list."""
        return [
            # Original 6 (simulation-validated)
            cls.GENERATION_NUMBER,
            cls.GUT_SCALE,
            cls.DARK_ENERGY_W0,
            cls.PROTON_LIFETIME,
            cls.THETA23_MAXIMAL,
            cls.KK_GRAVITON,
            # Section 2: 26D Bulk (legacy names use "25D")
            cls.MASTER_ACTION_26D,
            cls.VIRASORO_ANOMALY,
            cls.SP2R_CONSTRAINTS,
            cls.RACETRACK_SUPERPOTENTIAL,
            cls.PNEUMA_VEV,
            cls.BEKENSTEIN_HAWKING,
            cls.SCALAR_POTENTIAL,
            # Section 3: Reduction
            cls.REDUCTION_CASCADE,
            cls.PRIMORDIAL_SPINOR_13D,
            cls.HIDDEN_VARIABLES,
            cls.DIVISION_ALGEBRA,
            cls.DIRAC_PNEUMA,
            # Section 4: Topology
            cls.TCS_TOPOLOGY,
            cls.EFFECTIVE_EULER,
            cls.FLUX_QUANTIZATION,
            cls.EFFECTIVE_TORSION,
            cls.MIRROR_DM_RATIO,
            cls.HIERARCHY_RATIO,
            cls.PLANCK_MASS_DERIVATION,
            # Section 5: Gauge
            cls.SO10_BREAKING,
            cls.GUT_COUPLING,
            cls.WEAK_MIXING_ANGLE,
            cls.HIGGS_VEV,
            cls.DOUBLET_TRIPLET,
            # Section 6: Fermion
            cls.TOP_QUARK_MASS,
            cls.STRONG_COUPLING,
            cls.NEUTRINO_MASS_21,
            cls.NEUTRINO_MASS_31,
            cls.CP_PHASE_GEOMETRIC,
            cls.SEESAW_MECHANISM,
            cls.CKM_ELEMENTS,
            cls.YUKAWA_INSTANTON,
            # Section 7: Cosmology
            cls.EFFECTIVE_DIMENSION,
            cls.DARK_ENERGY_WA,
            cls.THERMAL_TIME,
            cls.ATTRACTOR_POTENTIAL,
            cls.FRIEDMANN_CONSTRAINT,
            cls.DE_SITTER_ATTRACTOR,
            cls.TOMITA_TAKESAKI,
            cls.KMS_CONDITION,
            # Section 8: Predictions
            cls.GW_DISPERSION,
            cls.GW_DISPERSION_COEFF,
            cls.PROTON_BRANCHING,
            # Appendix supplementary formulas
            cls.GHOST_COEFFICIENT,
            cls.KAPPA_GUT_COEFFICIENT,
            cls.EFFECTIVE_TORSION_SPINOR,
            cls.GW_DISPERSION_ALT,
            # NEW: Section 2-3 Supplementary (from gap analysis)
            cls.VACUUM_MINIMIZATION,
            cls.MIRROR_TEMP_RATIO,
            # NEW: Section 5 Supplementary (Gauge Unification)
            cls.PATI_SALAM_CHAIN,
            cls.HIGGS_POTENTIAL,
            cls.HIGGS_QUARTIC,
            cls.RG_RUNNING_COUPLINGS,
            # NEW: Section 6 Supplementary (Fermion Masses)
            cls.BOTTOM_QUARK_MASS,
            cls.TAU_LEPTON_MASS,
            cls.HIGGS_MASS,
        ]

    @classmethod
    def export_formulas(cls) -> Dict[str, Any]:
        """Export all formulas as JSON-serializable dict."""
        formulas = {}
        for formula in cls.get_all_formulas():
            formulas[formula.id] = formula.to_dict()
        return {
            "version": VERSION,
            "count": len(formulas),
            "formulas": formulas
        }
