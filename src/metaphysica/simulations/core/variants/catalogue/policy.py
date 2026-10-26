"""Catalogue: policy forks (render, uncertainty, face genericity).

Split out of the former single-file variants.py; text moved verbatim.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from typing import Dict

from ..model import Fork, VariantOption
from ..adopted import (
    _face_genericity_adopted,
    _render_policy_adopted,
    _theory_uncertainty_policy_adopted,
)

FORKS: Dict[str, Fork] = {
    "render_policy": Fork(
        id="render_policy",
        question="May a lone symbol be offered as a formula's EML diagram?",
        source="generators.eml_render_validity.REQUIRE_OPERATOR",
        status="RULED",
        read_adopted=_render_policy_adopted,
        options=[
            VariantOption(
                id="strict",
                summary="a render must depict at least one operator",
                consequence="Withholds every formula whose EML render is a "
                            "lone symbol, because such a render misrepresents "
                            "its own statement -- 'G2 = Aut(O)' would show as "
                            "the glyph '8'. Currently ten fewer formulas "
                            "offered than under 'permissive'.",
                adopted=True,
            ),
            VariantOption(
                id="permissive",
                summary="any clean render may be offered",
                consequence="Publishes those lone-symbol renders as if they "
                            "were the formulas. Offers ten more, every one of "
                            "them a truncation that misstates its formula.",
            ),
        ],
        notes="Decided by running both against the live formula set "
              "(two branches, manually diffed). This fork exists partly to "
              "validate the machinery against an answer already known.",
    ),
    "theory_uncertainty_policy": Fork(
        id="theory_uncertainty_policy",
        question="May an UNCITED theory uncertainty change a verdict?",
        source="generators.generate_validation_certificates"
               ".DEFAULT_THEORY_UNCERTAINTY_POLICY",
        status="OPEN",
        read_adopted=_theory_uncertainty_policy_adopted,
        options=[
            VariantOption(
                id="cited_only",
                summary="a theory uncertainty may only change a verdict if cited",
                consequence="Fifteen rows carry a theory uncertainty; for ten "
                            "it makes no difference to the verdict and is "
                            "unaffected. Five are load-bearing and none is "
                            "cited, so they revert to the experimental "
                            "verdict: G_F_matched 0.02->57.1 sigma, "
                            "m_higgs_pred 1.14->41.6, T_CMB 0.79->18.6, "
                            "sin2_theta_w_geometric 0.68->17.1 (all PASS or "
                            "MARGINAL -> FAIL) and eta_baryon 0.22->1.63 "
                            "(PASS -> MARGINAL). Reversible: supplying a "
                            "citation restores the folded verdict.",
                adopted=True,
            ),
            VariantOption(
                id="always",
                summary="fold theory uncertainty in regardless of provenance",
                consequence="The behaviour before this fork existed. Keeps "
                            "the four extreme deflations as PASS/MARGINAL, "
                            "including sin2_theta_w_geometric at 0.68 sigma "
                            "-- the same number G12 reports as COMPUTED_FAIL "
                            "at 17.1 sigma with no buffer. One prediction, "
                            "two published verdicts.",
            ),
            VariantOption(
                id="experimental_only",
                summary="verdict from experimental uncertainty alone, always",
                consequence="Ignores theory uncertainty entirely. Honest "
                            "about measurement, but overstates failure for a "
                            "genuinely tree-level prediction, which does not "
                            "claim the experiment's precision. Also demotes "
                            "the ten rows where the allowance is modest and "
                            "was doing no work.",
            ),
        ],
        notes="Generalises the R6 ruling (G12 converts with no invented "
              "theory buffer and fails honestly) from one gate to the whole "
              "validation layer. All three verdicts are exported per row in "
              "validation_report.json, so the comparison needs no rebuild.",
    ),
    "face_genericity": Fork(
        id="face_genericity",
        question="Must the four face labels avoid containing a Fano line?",
        source="PM.gauge.topological_terms.face_assignment_candidates",
        # Was OPEN with the note that adopting `generic` was "a stated
        # criterion, not a derivation". It is now a consequence. Requiring
        # the E8 block to be a property of the CHANNEL -- one global
        # labelling of the 7 Fano lines by 3 blocks, shared by every face --
        # means the 3 lines through each chosen point must carry 3 distinct
        # blocks. Enumerating all 3^7 labellings
        # (topological_terms.block_labelling_analysis) shows the 28
        # line-containing 4-point sets admit ZERO such labellings while each
        # of the 7 arcs admits 18. The same enumeration forces the number of
        # faces: no labelling makes 5 or more points rainbow, so 4 is the
        # maximum, which n_faces = 4 previously took from h^{1,1} of TCS #187
        # -- a value this repository labels FITTED.
        status="RULED",
        read_adopted=_face_genericity_adopted,
        options=[
            VariantOption(
                id="generic",
                summary="no three of the four labels collinear (arcs only)",
                consequence="35 -> 7 candidates, in bijection with the seven "
                            "lines; the three unchosen triangles are exactly "
                            "the omitted line. NOW DERIVED (2026-09-01), "
                            "having been carried as a stated criterion. "
                            "Requiring the E8 block to be a property of the "
                            "channel -- one global labelling of the 7 Fano "
                            "lines by 3 blocks, shared by every face -- "
                            "forces the 3 lines through each chosen point to "
                            "carry 3 distinct blocks. Enumerating all 3^7 "
                            "labellings shows the 28 line-containing "
                            "4-point sets admit ZERO, while each of the 7 "
                            "arcs admits 18. The same enumeration caps the "
                            "number of faces at 4: no labelling makes 5 or "
                            "more points rainbow. See "
                            "topological_terms.block_labelling_analysis. "
                            "The GLOBAL-LABELLING PREMISE is the input and "
                            "is stated, not derived.",
                adopted=True,
            ),
            VariantOption(
                id="all",
                summary="any 4-subset of the seven Fano points",
                consequence="all 35 candidates remain; the residual choice "
                            "is structural rather than a labelling.",
            ),
        ],
        notes="See docs/BRIDGE_CHANNEL_ASSIGNMENT.md. Adopting 'generic' is "
              "a criterion, not a result; the orbit split 28/7 is the fact.",
    ),
}
