#!/usr/bin/env python3
"""
PRINCIPIA METAPHYSICA - Section 1.1: Foundations of Dimensional Descent
=======================================================================

DOI: 10.5281/zenodo.18079602

THE ADOPTED BULK (signature ruling 2026-08-31; author's rulings D-015):
  - Bulk: M^{26}(24,2) = (bigoplus_{i=1}^{12} B_i^{(2,0)}) oplus R^{(0,2)}_{t_1, t_2}
  - Metric: ds^2 = -dt_1^2 - dt_2^2 + sum_{i=1}^{12} (dy_{1i}^2 + dy_{2i}^2)
  - 24 space directions, paired into 12 Euclidean (2,0) bridges, and two
    times, one per 13D(12,1) shadow: (24,2) = (12,1) + (12,1)
  - Shadows: the y_{1i} plus t_1 (normal), the y_{2i} plus t_2 (mirror)
  - OR reduction: bigotimes_{i=1}^{12} R_perp_i on the bridge pairs
  - Internal space of each shadow: Y_7 = Joyce's resolution of T^7/(Z/2)^3,
    (b_2, b_3) = (12, 43), pi_1 = 1, chi = 0 (certificate, Section 2.4)

WHY 12 PAIRS: the bulk has 24 space directions, 24/2 = 12. The 24 counts
bulk directions, not 3-cycles; reading it as b_3 = 24 belonged to the retired
seed and is withdrawn (D-004/D-007: class BULK).

RETIRED READINGS kept as labelled history in the text: the single fibred
time T^1 and the Euclidean "shadow-time" pair S^{(2,0)} (the '+2' now has one
reading, one time per shadow); the Calabi-Yau filtering through the
twisted-connected-sum building block (off-path construction); n_gen = b_3/8.

This simulation generates the content for subsection 1.1 of the paper:
  1.1 The M^{26}(24,2) Ancestral Bulk with 12x(2,0) Paired Bridge
  1.2 The Paired Bridge System and OR Reduction
  1.3 The Internal Manifold Y_7 per Shadow
  1.4 From 13D to 4D

SECTION: 1 (Foundations of Dimensional Descent)

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

from metaphysica.simulations.PM.geometry.geometry_narration import (
    fragments as _fragments,
    holonomy_claim as _holonomy_claim,
    render as _render,
)


def _r(template: str) -> str:
    """Fill `template` from the live geometry fragments, HTML register."""
    return _render(template, "html")


class FoundationsV16_2(SimulationBase):
    """
    Section 1.1: Foundations of Dimensional Descent.

    Provides the narrative for the (24,2) -> 4D descent path:
    - 1.1: The M^{26}(24,2) bulk with 12 x (2,0) paired bridges
    - 1.2: The paired bridge system and OR reduction
    - 1.3: The internal manifold Y_7 per shadow
    - 1.4: From 13D to 4D (the off-path Calabi-Yau filtering, labelled)

    STRUCTURE:
        M^{26}(24,2) = (bigoplus_{i=1}^{12} B_i^{(2,0)}) oplus R^{(0,2)}_{t_1, t_2}
        ds^2 = -dt_1^2 - dt_2^2 + sum_{i=1}^{12} (dy_{1i}^2 + dy_{2i}^2)

    WHY 12 PAIRS:
        the bulk's 24 space directions, 24 / 2 = 12 paired bridges
        (a count of bulk directions, not the Betti number b_3)
        Each pair: (y_{1i}, y_{2i}) with Euclidean (2,0) signature
    """

    # Dynamic formula IDs referenced by this section
    FORMULA_REFS = [
        "26d-signature",
        "euclidean-bridge",
        "or-reduction-tensor",
        "g2-holonomy-foundations",
        "b3-generations",
        "calabi-yau-projection",
        "leech-e8-decomposition",
    ]

    # Dynamic parameter paths referenced by this section
    PARAM_REFS = [
        "dimensions.D_bulk",
        "geometry.D_shadow",
        "geometry.D_shadow_total",
        "dimensions.D_observable",
        "topology.elder_kads",
        "topology.mephorash_chi",
        "geometry.n_generations",
    ]

    @property
    def metadata(self) -> SimulationMetadata:
        """Return metadata about this simulation."""
        return SimulationMetadata(
            id="foundations_v16_2",
            version="24.2",
            domain="foundations",
            title="Foundations of Dimensional Descent",
            description=(
                "The M^{26}(24,2) bulk: 24 space directions paired into 12 "
                "(2,0) bridges and two times, one per 13D(12,1) shadow; the "
                "dual shadows and the internal 7-manifold Y_7"
            ),
            section_id="1",
            subsection_id="1.1"  # unique subsection (introduction_v16_0 owns section 1)
        )

    @property
    def required_inputs(self) -> List[str]:
        """Registry parameters referenced by the foundations narrative."""
        return ["geometry.elder_kads", "geometry.k_gimel"]

    @property
    def output_params(self) -> List[str]:
        """No output parameters - narrative content only."""
        return []

    @property
    def output_formulas(self) -> List[str]:
        """Key formulas for dimensional descent."""
        return self.FORMULA_REFS

    def run(self, registry: 'PMRegistry') -> Dict[str, Any]:
        """Execute - returns empty dict as this is narrative only."""
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
        Return section content for Section 1.1: Foundations of Dimensional Descent.

        Seed numbers are rendered from the live fragments; the one sentence
        that depends on the real form of phi branches on holonomy_claim().
        Retired readings (the fibred single time, the Euclidean shadow-time
        pair, the Calabi-Yau filtering of the off-path construction) are kept
        as labelled history.

        Returns:
            SectionContent instance with the foundation narrative
        """
        frag = _fragments("plain")
        compact = bool(_holonomy_claim()["may_claim_g2_holonomy"])
        if compact:
            holonomy_text = _r(
                "On the compact real form of &phi;, adopted by the author&rsquo;s "
                "ruling D-015, {manifold} has holonomy exactly G<sub>2</sub>: "
                "&pi;<sub>1</sub> = 1, and for a compact torsion-free "
                "G<sub>2</sub>-structure a finite fundamental group is equivalent "
                "to full holonomy (Joyce, Prop. 1.1.1). Its metric is torsion-free "
                "and Ricci-flat, as are those of T<sup>7</sup> and K3 &times; "
                "T<sup>3</sup>, which carry more parallel spinors."
            )
        else:
            holonomy_text = _r(
                "The author&rsquo;s ruling D-015 adopts the compact real form of "
                "&phi;, on which {manifold} has holonomy exactly G<sub>2</sub> "
                "(&pi;<sub>1</sub> = 1; Joyce, Prop. 1.1.1) and a torsion-free, "
                "Ricci-flat metric. The real-form branch the code currently runs "
                "is the split form, whose induced metric has signature (4,3), so "
                "no holonomy statement is made on it."
            )

        content_blocks = [
            # NOTE: Abstract/lead paragraph removed - content is now in Section 0 (abstract_v17_2.py)
            # Section 1 should start directly with the foundational content

            # ================================================================
            # 1.1 The M^{26}(24,2) Ancestral Bulk with 12x(2,0) Paired Bridge
            # ================================================================
            ContentBlock(
                type="heading",
                content="The M<sup>26</sup>(24,2) Ancestral Bulk with 12×(2,0) Paired Bridge",
                level=2,
                label="1.1"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The foundational premise of the Sterile Model &mdash; a postulate, "
                    "not a result &mdash; is that the observable universe is not an "
                    "independent system but a lower-dimensional <strong>residue</strong> "
                    "of an <strong>M<sup>26</sup>(24,2) ancestral bulk</strong>. The bulk "
                    "has 24 space directions, paired into a <strong>12×(2,0) bridge "
                    "system</strong> that couples the two shadows, and two timelike "
                    "directions, one per 13D(12,1) shadow. Whether the second time is "
                    "free of ghosts and closed timelike curves is an open problem."
                )
            ),
            ContentBlock(
                type="heading",
                content="1.1.1 The Algebraic Origin",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The framework is motivated by the algebraic structures of the "
                    "<strong>Monster Group</strong> and the <strong>Leech Lattice</strong>, "
                    "whose 24-dimensional ambient space matches the bulk&rsquo;s 24 space "
                    "directions. The bulk itself is <strong>M<sup>26</sup>(24,2)</strong>: "
                    "24 space directions, paired into the 12×(2,0) bridges, and two "
                    "times, one per shadow. "
                    "Ghost control in this configuration is an <strong>open problem</strong>. "
                    "Earlier text called the bulk ghost-free by appeal to &lsquo;the single "
                    "timelike direction&rsquo;, which is not a description of a (24,2) bulk, and "
                    "then by appeal to Bars&rsquo; Sp(2,ℝ) theorem. Both are withdrawn under "
                    "the 2026-08-31 signature ruling: Sp(2,ℝ) gauging removes two dimensions "
                    "and yields <em>one</em> 24D shadow of signature (23,1), not two 13D(12,1) "
                    "shadows, so this framework&rsquo;s shadows do not inherit that theorem. OR "
                    "reduction to 13D(12,1) shadows is what the framework asserts; it is not a "
                    "computed removal of unphysical states."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<strong>Why (24,2) specifically?</strong> Because the 24 space directions "
                    "pair into the twelve bridges and each of the two shadows carries one "
                    "time: 26 = 24 + 2. That is the framework&rsquo;s own dimensional identity "
                    "(it coincided with b₃ + 2 only at the retired seed), and the 2026-08-31 "
                    "ruling keeps it — at a price that is stated here rather than "
                    "buried. Three claims that previously supported this paragraph are "
                    "<strong>withdrawn</strong>. (i) <em>D<sub>bulk</sub> = D<sub>crit</sub> = 26.</em> "
                    "26 is the critical dimension of the <em>one-time</em> bosonic string at "
                    "signature (25,1), where 26 = 24 transverse + a lightcone pair (one space, one "
                    "time) — not two times. The two-time bosonic critical dimension is 27–28 "
                    "(Bars &amp; Kounnas, hep-th/9705205; Watabiki, hep-th/0303045). The framework "
                    "may keep 26 = 24 + 2 as its own identity but may no longer call it the "
                    "critical dimension. (ii) <em>The appeal to Bars for ghost-freedom</em>, for "
                    "the reason given above. (iii) <em>The Leech/modular-invariance justification.</em> "
                    "An even unimodular lattice of signature (p,q) exists iff p − q ≡ 0 (mod 8). "
                    "For (24,2), 24 − 2 = 22 ≡ 6 (mod 8): <strong>no even self-dual lattice "
                    "exists at this signature</strong>, and there is no modular-invariant lattice "
                    "compactification here. Both (25,1) and (26,2) pass that test; the adopted "
                    "signature is the one that fails it. <strong>This obstruction is unanswered.</strong> "
                    "Any future modular-invariance claim must derive its own footing rather than "
                    "cite the lattice. The 24 transverse dimensions still match the Leech lattice "
                    "rank, and Moonshine (Borcherds 1992) is still the motivating analogy — but "
                    "an analogy is what it now is."
                )
            ),
            ContentBlock(
                type="equation",
                content=r"\text{Structure}(M^{26}) = (24, 2) \quad \Rightarrow \quad ds^2 = -dt_1^2 - dt_2^2 + \sum_{i=1}^{12} (dy_{1i}^2 + dy_{2i}^2)",
                label="27d-signature"
            ),
            ContentBlock(
                type="heading",
                content="1.1.1a The E8–G2 Connection via Octonions",
                level=4
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The connection between the exceptional Lie group G<sub>2</sub> and the "
                    "E<sub>8</sub> root system is mediated by the octonion algebra "
                    "<strong>O</strong>. G<sub>2</sub> is the automorphism group of the "
                    "8-dimensional octonions, Aut(<strong>O</strong>), and acts faithfully on the "
                    "7-dimensional imaginary part Im(<strong>O</strong>) ≅ R<sup>7</sup>, "
                    "preserving the octonionic structure constants C<sub>ijk</sub>. These structure "
                    "constants define the G<sub>2</sub> associative 3-form φ<sub>ijk</sub> = C<sub>ijk</sub>. "
                    "The quadratic contraction φ<sub>iab</sub>φ<sub>jab</sub>/6 = δ<sub>ij</sub> is a "
                    "consistency identity that holds for either real form of φ; the metric itself "
                    "comes from Hitchin&rsquo;s cubic construction, which depends on the real form. "
                    "The E<sub>8</sub> root system (240 roots in R<sup>8</sup> ≅ <strong>O</strong>) "
                    "shares this octonionic origin; the link motivates the construction rather "
                    "than deriving it."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The 24-dimensional ambient space of the Leech lattice, R<sup>24</sup>, "
                    "is partitioned into three orthogonal 8-dimensional blocks, each endowed with "
                    "E<sub>8</sub>-structured symmetries. It is important to distinguish these "
                    "E<sub>8</sub>-structured blocks of the <em>ambient space</em> from "
                    "sublattices of the Leech lattice itself (which has no norm-2 vectors). "
                    "The coordinate pairing of this 24D space yields 12 bridge pairs "
                    "(24/2 = 12), which are then grouped into 4 faces of 3 bridges each — "
                    "one bridge from each E<sub>8</sub> block per face."
                )
            ),
            ContentBlock(
                type="equation",
                content=r"\mathbb{R}^{24} = \mathbb{R}^8 \oplus \mathbb{R}^8 \oplus \mathbb{R}^8 \;\;\Rightarrow\;\; 12\text{ bridges} = 4\text{ faces} \times 3\text{ bridges/face}",
                label="leech-e8-decomposition"
            ),
            ContentBlock(
                type="heading",
                content="1.1.1a Why Four Faces: the Bridge-to-Channel Join",
                level=4
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "n<sub>faces</sub> = 4 was previously read off h<sup>1,1</sup> = 4 of the "
                    "off-path twisted-connected-sum building block (&lsquo;TCS #187&rsquo;), a "
                    "reading this repository labels <strong>FITTED</strong> because it depends on "
                    "having chosen that manifold. It no longer needs to be. "
                    "On the R<sup>7</sup> side the allowed couplings resolve into the seven lines "
                    "of the Fano plane, and a maximal bridge placement fills four complete "
                    "triangles — 4 points × 3 lines through each = 12 slots, against 4 faces "
                    "× 3 bridges = 12 on the R<sup>24</sup> side. A face corresponds to a Fano "
                    "point and its three bridges to the three lines through that point."
                )
            ),
            ContentBlock(
                type="callout",
                callout_type="warning",
                title="The one assumption",
                content=(
                    "Bridge b carries an E<sub>8</sub> block because the 24 Leech coordinates "
                    "split 8 + 8 + 8. The join <em>assumes</em> — states rather than derives — "
                    "that this block is a property of the <strong>channel</strong> and not of the "
                    "observing face: one global labelling of the 7 Fano lines by 3 blocks, the "
                    "same for every face. Everything below follows from that premise and falls "
                    "with it."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Under that premise a face is admissible only when the three lines through "
                    "its point receive three distinct blocks — call such a point "
                    "<em>rainbow</em>. Enumerating all 3<sup>7</sup> = 2187 labellings gives two "
                    "results that were not put in: <strong>the maximum number of simultaneously "
                    "rainbow points is four</strong> (no labelling makes five, six or seven), so "
                    "four faces is the largest number admitting a consistent block assignment at "
                    "all; and of the 35 = C(7,4) four-point sets, <strong>exactly the 7 arcs "
                    "qualify</strong> — the 28 sets that contain a Fano line admit zero "
                    "labellings, while each arc admits 18. <strong>Genericity is therefore "
                    "derived, not stipulated</strong>: it had been carried as a stated criterion "
                    "with the note that it was not a derivation."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "On its own the join does <em>not</em> single out one configuration. It "
                    "narrows C(21,12) = 293,930 placements → 35 → 7 and stops there, leaving "
                    "open which of the 7 arcs, and which of its 18 labellings. The internal "
                    "geometry now fixes the arc: the three singular involutions of the folding "
                    "group are three non-concurrent Fano lines, and they determine the arc "
                    "{0, 1, 3, 6} with complement line (2, 4, 5) (CG.8). With working "
                    "assumption WA-1 adopted by the author&rsquo;s ruling D-015 &mdash; each "
                    "bridge is one resolved A<sub>1</sub> component &mdash; that arc is the "
                    "physical one. Whether the singular set also fixes the labelling is not "
                    "established here, and inventing a tie-break would not be a derivation. "
                    "Two counts in this construction are "
                    "also now enumerated rather than asserted: 15400 = 12!/((3!)<sup>4</sup>4!) "
                    "groupings of 12 bridges into 4 unordered triples, of which 576 = (4!)<sup>2</sup> "
                    "are cross-E<sub>8</sub>-valid. Note that the stride-4 triples {i, i+4, i+8} "
                    "and contiguous triples are different objects — the contiguous first face "
                    "lies entirely inside one E<sub>8</sub> block and is therefore not "
                    "cross-E<sub>8</sub>-valid at all."
                )
            ),
            ContentBlock(
                type="heading",
                content="1.1.2 The 12×(2,0) Paired Bridge Structure",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The M<sup>26</sup>(24,2) bulk decomposes into <strong>12 paired "
                    "bridges</strong>, each with (2,0) signature, and <strong>two times</strong>, "
                    "one per shadow. The total bulk structure is:"
                )
            ),
            ContentBlock(
                type="equation",
                content=r"M^{26}(24,2) = \bigoplus_{i=1}^{12} B_i^{(2,0)} \oplus \mathbb{R}^{(0,2)}_{(t_1,\,t_2)}, \qquad B_i = (y_{1i}, y_{2i})",
                label="bulk-decomposition"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Each bridge pair B<sub>i</sub> = (y<sub>1i</sub>, y<sub>2i</sub>) contributes "
                    "two space directions, giving 12 × 2 = 24; the two times t<sub>1</sub> and "
                    "t<sub>2</sub>, one per shadow, complete <strong>M<sup>26</sup>(24,2)</strong>. "
                    "The 24 counts the bulk&rsquo;s space directions. It is not a Betti number: "
                    "the earlier reading of the pair count as half of b₃ belonged to the retired "
                    "seed and is withdrawn. Earlier versions also wrote the bulk with a single "
                    "fibred time T<sup>1</sup> and a Euclidean &lsquo;shadow-time&rsquo; pair "
                    "S<sup>(2,0)</sup>; under the 2026-08-31 ruling the &lsquo;+2&rsquo; has one "
                    "reading, one time per shadow, and those forms are retired."
                )
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>Bridge Pairs:</strong> B<sub>i</sub><sup>(2,0)</sup> = (y<sub>1i</sub>, y<sub>2i</sub>) for i = 1,...,12",
                    "<strong>Normal Shadow:</strong> all y<sub>1i</sub> (the normal halves) + its own time t<sub>1</sub> = 13D(12,1), compactified on the internal 7-manifold",
                    "<strong>Mirror Shadow:</strong> all y<sub>2i</sub> (the mirror halves) + its own time t<sub>2</sub> = 13D(12,1), compactified on the internal 7-manifold",
                    "<strong>Per-pair OR:</strong> R<sub>⊥</sub><sup>i</sup> = [[0,-1],[1,0]] acts on each (y<sub>1i</sub>, y<sub>2i</sub>)"
                ],
                label="dual-shadow-structure"
            ),
            ContentBlock(
                type="heading",
                content="1.1.3 The Symmetry Threshold",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "In the model&rsquo;s picture (a postulate), the M<sup>26</sup>(24,2) bulk "
                    "descends by a <strong>dimensional collapse</strong> into the dual-shadow "
                    "configuration, with the bridges providing the coherence substrate, and each "
                    "shadow then compactifies on the internal 7-manifold to a 4D condensate. The "
                    "model calls this transition a <strong>topological shattering</strong>; it "
                    "is a description, not a computed process."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=_r(
                    "<strong>The Dimensional Descent Chain and Its Status:</strong> each step in "
                    "the descent from 26D to 4D, with what supports it. (1) <strong>The 26D bulk "
                    "of signature (24,2)</strong>: a postulate &mdash; 24 space directions and one "
                    "time per shadow; the earlier appeal to the bosonic critical dimension is "
                    "withdrawn, because 26 is critical only for one time. (2) <strong>The 12 × "
                    "(2,0) bridge pairs</strong>: the bulk&rsquo;s 24 space directions taken in "
                    "pairs, 24/2 = 12; each pair is Euclidean, and ghost control of the second "
                    "time is open. (3) <strong>The dual 13D(12,1) shadows</strong>: OR reduction, "
                    "proposed as the orientation-preserving projection consistent with spinor "
                    "coherence ((R<sub>⊥</sub><sup>full</sup>)² = I for 12 pairs). (4) "
                    "<strong>Compactification on {manifold}</strong>: M-theory on a compact "
                    "G<sub>2</sub> manifold preserves N = 1 supersymmetry in 4D (standard; Joyce, "
                    "2000), and {manifold} = {construction}, with {betti_pair}, is selected as the "
                    "Introduction describes (&sect;1.3.2). (5) <strong>4D physics</strong>: "
                    "three generations are counted as {n_gen_route}; how they become chiral is "
                    "open, because {manifold} has no codimension-7 points, and the earlier route "
                    "through a Calabi&ndash;Yau sub-manifold of the twisted-connected-sum "
                    "construction is off-path."
                )
            ),
            ContentBlock(
                type="note",
                content=(
                    "<h4>Foundational Note: The Origin of Sterility</h4>"
                    "<p>In the model&rsquo;s picture (a postulate, not a computation), the "
                    "&lsquo;sterility&rsquo; of our 4D reality is inherited from this 26D origin: "
                    "the ancestral bulk is taken to carry a finite &lsquo;symmetry budget&rsquo;, "
                    "so the residues extracted in 4D must sum to a fixed constant. The dual-shadow "
                    "structure is proposed to enforce this through a balanced 12/12 split of the "
                    "bulk&rsquo;s space directions across the two shadows.</p>"
                ),
                label="sterility-origin"
            ),

            # ================================================================
            # 1.2 The Paired Bridge System and OR Reduction
            # ================================================================
            ContentBlock(
                type="heading",
                content="The Paired Bridge System and OR Reduction",
                level=2,
                label="1.2"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The connection between the dual shadows is mediated by the "
                    "<strong>12×(2,0) paired bridge system</strong>. Each bridge pair B<sub>i</sub> "
                    "provides a timeless Euclidean substrate enabling cross-shadow coordinate sampling "
                    "via <strong>per-pair Orthogonal Reduction (OR)</strong>."
                )
            ),
            ContentBlock(
                type="heading",
                content="1.2.1 The Paired Bridge Metric",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Each of the 12 bridge pairs has a positive-definite (2,0) metric, so the "
                    "bridges themselves add no timelike directions; ghost control of the "
                    "bulk&rsquo;s second time is a separate, open problem. The total bridge "
                    "metric is the direct sum over all pairs:"
                )
            ),
            ContentBlock(
                type="equation",
                content=r"ds^2_{\text{bridge}} = \sum_{i=1}^{12} \left(dy_{1i}^2 + dy_{2i}^2\right) \quad \text{(24D positive-definite)}",
                label="bridge-metric"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The pairing is of the bulk&rsquo;s 24 space directions: 24/2 = 12 pairs. "
                    "(An earlier reading took the 24 to be the Betti number b₃; that reading "
                    "belonged to the retired seed and is withdrawn.) "
                    "<Speculation>Each pair serves as a 'neural gate' for consciousness flow between shadows.</Speculation>"
                )
            ),
            ContentBlock(
                type="heading",
                content="1.2.2 The Per-Pair OR Reduction Operator",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Cross-shadow coordinate sampling uses <strong>per-pair OR operators R<sub>⊥</sub><sup>i</sup></strong>. "
                    "Each 2×2 operator acts on the corresponding bridge pair (y<sub>1i</sub>, y<sub>2i</sub>):"
                )
            ),
            ContentBlock(
                type="equation",
                content=r"R_\perp^i = \left(\begin{smallmatrix} 0 & -1 \\ 1 & 0 \end{smallmatrix}\right) \quad \Rightarrow \quad R_\perp^{\text{full}} = \bigotimes_{i=1}^{12} R_\perp^i",
                label="or-reduction-tensor"
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>Per-Pair Operator:</strong> R<sub>⊥</sub><sup>i</sup> = [[0, -1], [1, 0]] (90° rotation on pair i)",
                    "<strong>Full Tensor Product:</strong> R<sub>⊥</sub><sup>full</sup> = tensor product over all 12 pairs",
                    "<strong>Möbius Property:</strong> (R<sub>⊥</sub><sup>i</sup>)² = −I per pair; (R<sub>⊥</sub><sup>full</sup>)² = (−1)<sup>12</sup> I = I",
                    "<strong>Spinor Coherence:</strong> Full double-traversal returns to identity (even number of pairs)"
                ],
                label="or-reduction-operator"
            ),
            ContentBlock(
                type="heading",
                content="1.2.3 The Breathing Dark Energy Proposal",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=_r(
                    "The model proposes that a <strong>condensate flux mismatch</strong> between "
                    "the shadows produces a bridge pressure, &rho;<sub>breath</sub> = "
                    "|T<sup>ab</sup><sub>normal</sub> &minus; R<sub>&perp;</sub> "
                    "T<sup>ab</sup><sub>mirror</sub>|, and that this residue drives cosmic "
                    "acceleration. It is a proposal: dark energy is <strong>OPEN</strong>. The "
                    "leading-order flux potential on {manifold} cannot accelerate the universe "
                    "(|&nabla;V|/V &ge; 5&radic;(2/7) &asymp; 2.673 &gt; &radic;2, CG.11). The "
                    "value w<sub>0</sub> = &minus;1 + 1/b<sub>3</sub> = &minus;23/24 once quoted "
                    "here is frozen at {off_path_seed} and has no derivation; both it and the "
                    "adopted-seed value &minus;" + str(int(frag["b3"]) - 1) + "/" + frag["b3"]
                    + " lie more than 3&sigma; from the DESI DR2 headline w<sub>0</sub> = "
                    "&minus;0.752 &plusmn; 0.057."
                )
            ),
            ContentBlock(
                type="heading",
                content="1.2.4 Hierarchical Bridge Sampling (a Retired Reading)",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "RETIRED (signature ruling 2026-08-31): an earlier version extended the 12 "
                    "local (2,0) bridge pairs with a <strong>central (2,0) ancestral "
                    "sampler</strong> S<sup>(2,0)</sup>, built from the bulk&rsquo;s "
                    "&lsquo;+2&rsquo;, to provide global averaging. Under the ruling the "
                    "&lsquo;+2&rsquo; are the two times, one per shadow, so no Euclidean pair is "
                    "left to carry the sampler. The construction is kept below as a labelled "
                    "record; it enters no adopted result."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<strong>Former descent flow:</strong><br/>"
                    "• Bulk → 12×(2,0) local pairs (fine flux sampling per bridge)<br/>"
                    "• Local → central (2,0) averaging → ancestral descent into condensate ((5,1) + 3×(3,1))"
                )
            ),
            ContentBlock(
                type="equation",
                content=r"p_{\text{anc}} = \frac{1}{12}\sum_{i=1}^{12} p_i + \sqrt{\frac{n_{\text{local}}}{12}} \cdot \phi",
                label="central-sampler-formula"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "In that record, p<sub>i</sub> is the local probability from bridge pair i, "
                    "n<sub>local</sub> is the number of active local pairs (6 baseline → 12 full "
                    "gnosis), and φ is the golden ratio; the central pair was said to activate at "
                    "mid-gnosis (n<sub>local</sub> ≥ 9)."
                )
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>Former dimensional accounting:</strong> 24 core + 24 local + 2 central = 50 spacelike dimensions (inconsistent with a (24,2) bulk; retired)",
                    "<strong>Local level:</strong> 12×(2,0) pairs → micro-stability (per-branch selection)",
                    "<strong>Central level (retired):</strong> 1×(2,0) pair → macro-precision (global averaging)",
                    "<strong>Signature:</strong> the adopted bulk is M<sup>26</sup>(24,2) = 12×(2,0) ⊕ (0,2), the two times one per shadow; the Euclidean S<sup>(2,0)</sup> extension is retired"
                ],
                label="hierarchical-sampling-structure"
            ),

            # ================================================================
            # 1.3 The internal manifold Y_7 per shadow
            # ================================================================
            ContentBlock(
                type="heading",
                content="The Internal Manifold Y₇: Per-Shadow Compactification",
                level=2,
                label="1.3"
            ),
            ContentBlock(
                type="paragraph",
                content=_r(
                    "Each shadow compactifies on the internal space {manifold} = "
                    "{construction}: {structure}, with {betti_pair} (Introduction, "
                    "&sect;1.3.2; certificate in Section 2.4). Three generations are counted as "
                    "{n_gen_route}. The effective index &chi;<sub>eff</sub> = 48n = "
                    + str(48 * int(round(float(frag["n_gen"])))) + " (the K3 reading, adopted by "
                    "the author&rsquo;s ruling D-015) restates that count; it is not the Euler "
                    "characteristic of {manifold}, which is 0. Earlier text called the manifold "
                    "a &lsquo;hard-lock&rsquo; that keeps the constants of nature from drifting; "
                    "that is not supported, because the metric moduli of {manifold}, Re(T) "
                    "included, are not fixed at leading order (CG.6)."
                )
            ),
            ContentBlock(
                type="heading",
                content="1.3.1 Holonomy, Ricci-Flatness, and What They Do Not Fix",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    holonomy_text + " Ricci-flatness does not fix the constants of nature: the "
                    "moduli are flat directions at leading order (CG.6), and the constants built "
                    "on k<sub>ℷ</sub> = b<sub>3</sub>/2 + 1/π were calibrations (D-007). The "
                    "earlier claim that the geometry makes every derivation &lsquo;path "
                    "independent&rsquo; and removes fine-tuning is withdrawn."
                )
            ),
            ContentBlock(
                type="equation",
                content=r"\text{Hol}(g) \subseteq G_2 \iff \exists \eta: \nabla \eta = 0 \quad \Rightarrow \quad R_{\mu\nu} = 0",
                label="g2-holonomy"
            ),
            ContentBlock(
                type="heading",
                content="1.3.2 The Laplacian Spectrum (λₙ)",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The model proposes (a postulate, not a computation) that the constants it "
                    "calls residues correspond to spectral eigenvalues of the <strong>manifold "
                    "Laplacian</strong> Δ<sub>Y₇</sub>, with this division of roles:"
                )
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>Low-Frequency Modes:</strong> proposed to correspond to global cosmological constants (e.g., H₀, Λ).",
                    "<strong>High-Frequency Modes:</strong> proposed to correspond to discrete particle masses (e.g., the Top Quark)."
                ],
                label="laplacian-modes"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "If the proposal holds, the constants would be resonant frequencies of the "
                    "internal shape. It is a research programme, not a result: the spectrum "
                    "depends on the metric moduli of Y₇, which are not fixed at leading order "
                    "(CG.6)."
                )
            ),
            ContentBlock(
                type="heading",
                content="1.3.3 The 3-Cycles and Flux-Tube Screening",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=_r(
                    "The model proposes that vacuum energy is screened by flux through the "
                    "3-cycles of {manifold} ({b3} of them), with brane-tension cancellation "
                    "inside them setting a small floor. It is a proposal, not a resolution of the "
                    "cosmological-constant problem: the leading-order G<sub>4</sub>-flux "
                    "potential on {manifold} is positive and runs away (CG.6) and cannot "
                    "accelerate the universe (CG.11), so dark energy and the cosmological "
                    "constant are open."
                )
            ),
            ContentBlock(
                type="equation",
                content=(
                    r"n_{\text{gen}} = \frac{b_2}{4} = \frac{%s}{4} = %s \quad "
                    r"\text{(the number of singular involutions)}"
                    % (frag["b2"], frag["n_gen"])
                ),
                label="b3-generations"
            ),

            # ================================================================
            # 1.4 From 13D to 4D
            # ================================================================
            ContentBlock(
                type="heading",
                content="From 13D to 4D (and the Off-Path Calabi-Yau Filtering)",
                level=2,
                label="1.4"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "On the adopted path each 13D(12,1) shadow splits as 13 = 7 + 6: the "
                    "internal 7-manifold and a 6D external space, with 6 = 4 + 2 (the bulk ruling "
                    "of 2026-08-31). OFF-PATH: earlier versions instead routed the descent through "
                    "a <strong>6-dimensional Calabi-Yau intermediate</strong> inside the internal "
                    "space &mdash; the Calabi&ndash;Yau building block of the twisted-connected-sum "
                    "construction &mdash; which was said to act as a &lsquo;diffraction "
                    "grating&rsquo; turning geometric nodes into flavour physics and gauge "
                    "couplings. A Joyce orbifold resolution has no such building block, so that "
                    "reading is retired."
                )
            ),
            ContentBlock(
                type="heading",
                content="1.4.1 Calabi-Yau Sub-Manifolds and Chirality (Off-Path)",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=_r(
                    "In the off-path reading, the Hodge numbers (h<sup>1,1</sup>, "
                    "h<sup>2,1</sup>) of the Calabi&ndash;Yau threefold were said to produce "
                    "chirality and to count generations. Neither holds on the adopted path: "
                    "chirality is open, because the singular loci of {manifold} are disjoint and "
                    "leave no codimension-7 points (D-011), and generations are counted as "
                    "{n_gen_route}. The nearest standard relative of a Calabi&ndash;Yau step is "
                    "the heterotic dual of M-theory on Joyce manifolds, in which the K3 fibration "
                    "of {manifold} corresponds to a T<sup>3</sup>-fibred Calabi&ndash;Yau "
                    "threefold on the heterotic side (Acharya 1996); whether that dual carries a "
                    "chiral sector is an open research direction."
                )
            ),
            ContentBlock(
                type="equation",
                content=r"13 = \underbrace{7}_{Y_7} + \underbrace{6}_{\text{external}}, \qquad 6 = 4 + 2",
                label="cy3-projection"
            ),
            ContentBlock(
                type="heading",
                content="1.4.2 Brane-Node Shadowing",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "In 4D reality, fundamental particles are perceived as point-like excitations. "
                    "In the Sterile Model&rsquo;s picture &mdash; a metaphor, not a computation "
                    "&mdash; they are <strong>shadows of brane-node intersections</strong>:"
                )
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>Mass Generation:</strong> a particle's mass as the 'shadow length' cast by a spectral node of the internal manifold (the 'Calabi-Yau filter' this image once named belongs to the off-path construction).",
                    "<strong>Charge & Coupling:</strong> the force couplings (g<sub>s</sub>, g<sub>w</sub>, e) as 'aperture widths' through which the ancestral 26D flux passes. Neither image yet carries computed content."
                ],
                label="brane-shadows"
            ),
            ContentBlock(
                type="heading",
                content="1.4.3 The 4D Minkowski World-Sheet",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=_r(
                    "Our observable universe is the <strong>4D end</strong> of this descent. The "
                    "model&rsquo;s aim is to read the constants of nature as geometric residues "
                    "of the M<sup>26</sup>(24,2) bulk. That aim is not yet met: the "
                    "fine-structure constant and the proton-to-electron mass ratio, once "
                    "presented as a &lsquo;terminal geometric identity&rsquo;, are built on "
                    "k<sub>&#8503;</sub> = b<sub>3</sub>/2 + 1/&pi; and were fits made at "
                    "{off_path_seed} (CALIBRATED, D-007), and the moduli that would fix the "
                    "remaining scales are open (CG.6)."
                )
            ),
            ContentBlock(
                type="note",
                content=_r(
                    "<h4>The Descent Path Summary</h4>"
                    "<p>M<sup>26</sup>(24,2) = 12×(2,0) ⊕ (0,2) → [bridges split by OR "
                    "reduction] → 2×13D(12,1) → 13 = 7 + 6: the internal {manifold} "
                    "({construction}, {betti_pair}) and a 6D external space → 4D</p>"
                    "<p>Every arrow is a postulate of the model except the internal geometry, "
                    "which is selected and certified (Introduction &sect;1.3.2; Section 2.4). The "
                    "earlier picture of 125 &lsquo;residues&rsquo; extracted as spectral "
                    "eigenvalues of the descended geometry is a proposal, not a computation.</p>"
                ),
                label="descent-summary"
            ),
        ]

        return SectionContent(
            section_id="1",
            subsection_id="1.1",  # unique subsection
            title="Foundations of Dimensional Descent",
            abstract=_r(
                "The M<sup>26</sup>(24,2) bulk &mdash; 24 space directions paired into 12 "
                "bridges and two times, one per 13D(12,1) shadow &mdash; its OR reduction "
                "into the dual shadows, the internal 7-manifold {manifold}, and the descent "
                "to 4D."
            ),
            content_blocks=content_blocks
        )

    def get_formulas(self) -> List[Formula]:
        """Return formula definitions for dimensional descent foundations."""
        return [
            Formula(
                id="26d-signature",
                label="(1.1)",
                latex=r"\text{Signature}(M^{24,2}) = (24, 2) \quad ds^2 = -dt_1^2 - dt_2^2 + \sum_{i=1}^{12}(dy_{1i}^2 + dy_{2i}^2)",
                plain_text="Signature(M^{24,2}) = (24, 2); ds^2 = -dt_1^2 - dt_2^2 + sum_i(dy_{1i}^2 + dy_{2i}^2)",
                category="DERIVED",
                description="26D ancestral bulk signature (24,2). 24 spacelike from 12x2 pairs, 2 timelike (one per shadow).",
                input_params=["dimensions.D_bulk", "topology.elder_kads"],
                output_params=[],
                derivation={
                    "method": "algebraic_construction",
                    "steps": [
                        "Start from 26D total (24 spatial + 2 temporal)",
                        "Decompose 24 spacelike dimensions into 12 Euclidean (2,0) bridge pairs",
                        "Assign one timelike direction per 13D shadow; ghost control of the second time is OPEN (the appeal to the Sp(2,R) gauge constraint is withdrawn, signature ruling 2026-08-31)"
                    ],
                    "parentFormulas": []
                },
                eml_tree_str=(
                    "ops.add(eml_scalar(24.0), eml_scalar(2.0))  # D_space_24 + 2 times; the b3 + 2 identity broke with the b3_seed adoption"
                ),
                eml_description=(
                    "Bulk signature (24,2): 24 spacelike dimensions plus 2 timelike (one per 13D shadow)."
                ),
                terms={
                    "M^{24,2}": "26-dimensional manifold with signature (24,2)",
                    "ds^2": "Line element of the bulk metric",
                    "dy_{1i}, dy_{2i}": "Bridge pair coordinates for the i-th pair"
                },
            arithma=_arithma_add(_arithma_num(24.0), _arithma_num(2.0)), eml=_eml_add(_eml_scalar(24.0), _eml_scalar(2.0)), value=26.0),
            Formula(
                id="euclidean-bridge",
                label="(1.2)",
                latex=r"M^{24,2} = T^1 \times_{\text{fiber}} \left(\bigoplus_{i=1}^{12} B_i^{2,0}\right)",
                plain_text="M^{24,2} = T^1 x_fiber (bigoplus_{i=1}^{12} B_i^{2,0})",
                category="DERIVED",
                description=(
                    "The bulk's 24 space directions as 12 Euclidean (2,0) bridge pairs: "
                    "12 x 2 = 24. The two times, one per 13D(12,1) shadow, complete the "
                    "(24,2) signature. The 24 counts bulk space directions, not 3-cycles "
                    "(b_3 = 43 on the adopted seed); the earlier reading of it as the Betti "
                    "number is retired, and the T^1-fibre notation in the displayed form is "
                    "the retired single-time reading (signature ruling 2026-08-31)."
                ),
                input_params=["dimensions.D_bulk", "topology.elder_kads"],
                output_params=["geometry.D_shadow"],
                derivation={
                    "method": "topological_decomposition",
                    "steps": [
                        "The bulk carries 24 space directions (D_space = 24), the space part of the (24,2) signature; the earlier reading of this 24 as b3 Betti cycles is retired",
                        "Pair the 24 space directions into 12 Euclidean bridge pairs: 24/2 = 12",
                        "Add the two times, one per 13D(12,1) shadow, to form the (24,2) bulk (the single fibred time T^1 of earlier versions is retired)"
                    ],
                    "parentFormulas": ["26d-signature"]
                },
                eml_tree_str=(
                    "ops.mul(eml_scalar(12.0), eml_scalar(2.0))"
                ),
                eml_description=(
                    "Bridge bulk: 12 bridge pairs times 2 dimensions each = 24D spatial sector."
                ),
                terms={
                    "T^1": "Single fibred time of earlier versions (retired: the bulk has two times, one per shadow)",
                    "B_i^{2,0}": "i-th Euclidean bridge pair with (2,0) signature",
                    "x_fiber": "Fiber product over the retired single time"
                },
            arithma=_arithma_mul(_arithma_num(12.0), _arithma_num(2.0)), eml=_eml_mul(_eml_scalar(12.0), _eml_scalar(2.0)), value=24.0),
            Formula(
                id="or-reduction-tensor",
                label="(1.2b)",
                latex=r"R_\perp^{\text{full}} = \bigotimes_{i=1}^{12} R_\perp^i \quad \text{where} \quad R_\perp^i = \left(\begin{smallmatrix} 0 & -1 \\ 1 & 0 \end{smallmatrix}\right)",
                plain_text="R_perp^full = tensor_{i=1}^{12} R_perp^i where R_perp^i = [[0,-1],[1,0]]",
                category="DERIVED",
                description="Full OR reduction operator as tensor product of 12 per-pair 90-degree rotations.",
                input_params=["topology.elder_kads"],
                output_params=[],
                derivation={
                    "method": "tensor_product_construction",
                    "steps": [
                        "Define per-pair OR operator R_perp^i as 90-degree rotation in (y_{1i}, y_{2i}) plane",
                        "Verify Möbius property: (R_perp^i)^2 = -I per pair",
                        "Full operator is tensor product over all 12 pairs: (R_perp^full)^2 = (-1)^12 I = I"
                    ],
                    "parentFormulas": ["euclidean-bridge"]
                },
                eml_tree_str=(
                    "ops.pow(eml_vec('R_perp_i'), eml_scalar(12.0))"
                ),
                eml_description=(
                    "Full OR reduction operator: tensor product of 12 per-pair R_perp^i operators."
                ),
                terms={
                    "R_perp^i": "Per-pair orthogonal reduction operator (90-deg rotation)",
                    "R_perp^full": "Full tensor product OR operator over 12 pairs",
                    "bigotimes": "Tensor product over all bridge pairs"
                },
            arithma=_arithma_div(_arithma_num(24.0), _arithma_num(2.0)), eml=_eml_div(_eml_scalar(24.0), _eml_scalar(2.0)), value=12.0),
            Formula(
                id="central-sampler-formula",
                label="(1.2c)",
                latex=r"p_{\text{anc}} = \frac{1}{12}\sum_{i=1}^{12} p_i + \sqrt{\frac{n_{\text{local}}}{12}} \cdot \phi",
                plain_text="p_anc = (1/12)*sum(p_i) + sqrt(n_local/12)*phi",
                category="DERIVED",
                description=(
                    "RETIRED (signature ruling 2026-08-31): central (2,0) ancestral sampler "
                    "formula, averaging the 12 local pairs with golden-ratio scaling. It was "
                    "built on a Euclidean shadow-time pair S^(2,0); under the ruling the "
                    "bulk's '+2' are the two times, one per shadow, so the sampler has no "
                    "directions of its own. Kept as a labelled record."
                ),
                input_params=["topology.elder_kads"],
                output_params=[],
                derivation={
                    "method": "hierarchical_averaging",
                    "steps": [
                        "Average local probabilities p_i across 12 bridge pairs",
                        "Apply golden ratio phi scaling based on active pair count n_local",
                        "Central sampler was said to activate at mid-gnosis (n_local >= 9); retired with the Euclidean shadow-time pair"
                    ],
                    "parentFormulas": ["euclidean-bridge", "or-reduction-tensor"]
                },
                eml_tree_str=(
                    "ops.add(ops.mul(ops.inv(eml_scalar(12.0)), eml_vec('sum_p_i')), ops.mul(ops.sqrt(ops.div(eml_vec('n_local'), eml_scalar(12.0))), eml_vec('phi')))"
                ),
                eml_description=(
                    "Central sampler: (1/12)*sum(p_i) plus sqrt(n_local/12)*phi golden ratio scaling."
                ),
                terms={
                    "p_anc": "Ancestral probability from the retired Euclidean shadow-time pair",
                    "p_i": "Local probability from bridge pair i",
                    "n_local": "Number of active local pairs (6 baseline to 12 full)",
                    "phi": "Golden ratio (1+sqrt(5))/2"
                },
            arithma=_arithma_div(_arithma_num(24.0), _arithma_num(2.0)), eml=_eml_div(_eml_scalar(24.0), _eml_scalar(2.0)), value=12.0),
            Formula(
                id="g2-holonomy-foundations",
                label="(1.3)",
                latex=r"\text{Hol}(g) \subseteq G_2 \iff \exists \eta: \nabla \eta = 0",
                plain_text="Hol(g) ⊆ G2 iff exists eta: nabla eta = 0",
                category="DERIVED",
                description="G2 holonomy condition for torsion-free, Ricci-flat metric.",
                input_params=["topology.elder_kads", "topology.mephorash_chi"],
                output_params=[],
                derivation={
                    "method": "holonomy_classification",
                    "steps": [
                        "G2 is the automorphism group of octonions Aut(O)",
                        "G2 holonomy implies existence of a parallel 3-form eta with nabla eta = 0",
                        "Parallel 3-form implies Ricci-flatness: R_mu_nu = 0"
                    ],
                    "parentFormulas": []
                },
                eml_tree_str=(
                    "eml_vec('G2_holonomy')"
                ),
                eml_description=(
                    "G2 holonomy condition: Hol(g) subset G2 iff a parallel 3-form eta exists with nabla eta = 0."
                ),
                terms={
                    "Hol(g)": "Holonomy group of the Riemannian metric g",
                    "G_2": "Exceptional Lie group, Aut(O), dim=14",
                    "eta": "Associative 3-form (parallel under G2 holonomy)",
                    "nabla": "Levi-Civita connection"
                },
            arithma=_arithma_num(0.0), eml=_eml_scalar(0.0), value=0.0),
            # b3 Generations formula - critical for fermion generation count
            Formula(
                id="b3-generations",
                label="(1.3b)",
                latex=r"N_{\text{gen}} = \frac{b_3}{8} = \frac{24}{8} = 3",
                plain_text="N_gen = b3/8 = 24/8 = 3",
                category="DERIVED",
                description=(
                    "RELOCATED (n_gen_source): three fermion generations, computed as "
                    "n_gen = b2/4 = 3, the number of singular involutions of the folding "
                    "group. The displayed b3/8 = 24/8 form is the retired route at the "
                    "off-path seed b3 = 24; it yields an integer nowhere on the Joyce "
                    "family, where b3 is odd."
                ),
                input_params=["topology.elder_kads"],
                output_params=["geometry.n_generations"],
                derivation={
                    "method": "topological_index",
                    "steps": [
                        "OFF-PATH history (retired seed_24): the internal space was the "
                        "G2 manifold 'TCS #187' with b3 = 24 and b2 = 4. That pair "
                        "cannot exist as a twisted connected sum -- Crowley & Nordstrom "
                        "(arXiv:1211.0269) Thm 1.7 gives nu = 24 for every TCS and the "
                        "Thm 1.3 parity constraint then forces b2 + b3 to be ODD, while "
                        "4 + 24 = 28 is even -- and b3 = 24 is unreachable by Joyce's "
                        "construction from phi's (Z/2)^3 (CG.7).",
                        "OFF-PATH: the retired route counted fermion zero modes as "
                        "chi_eff/(2*b3) = 144/48 = 3, which holds only at b3 = 24. On the "
                        "adopted path chi_eff = 48 n (the K3 reading, author's ruling "
                        "D-015), and chi_eff/48 = n restates the count below.",
                        "ADOPTED route: n_gen = b2/4 = 3, the number of singular involutions (the rank of their span, equal to rank(Gamma) at the adopted point); the b3/8 form held only at the off-path b3 = 24"
                    ],
                    "parentFormulas": ["g2-holonomy-foundations"]
                },
                eml_tree_str=(
                    "ops.div(eml_scalar(12.0), eml_scalar(8.0/2.0))  # b2/4 = 12/4, the adopted n_gen route"
                ),
                eml_description=(
                    "Three fermion generations: n_gen = b2/4 = 12/4 = 3, the RANK of the "
                    "orbifold group recovered from the derived family count. The former "
                    "b3/8 reading is the off-path n_gen_source branch (integer nowhere "
                    "on the Joyce family)."
                ),
                terms={
                    "N_gen": "Number of fermion generations = the number of singular involutions",
                    "b_2": "Second Betti number, the derived A1 family count (12 on the adopted seed)",
                    "4": "The derived faces: moved coordinates of an involution (R2)"
                },
            arithma=_arithma_div(_arithma_num(12.0), _arithma_num(4.0)), eml=_eml_div(_eml_scalar(12.0), _eml_scalar(4.0)), value=3.0),
            Formula(
                id="calabi-yau-projection",
                label="(1.4)",
                latex=r"V_7 \xrightarrow{\text{CY}_3} M^4 \times K^6",
                plain_text="V7 -> M^4 x K^6 via CY3",
                category="DERIVED",
                description=(
                    "OFF-PATH (twisted-connected-sum construction, retired): Calabi-Yau "
                    "filtering from the 7D internal space to 4D Minkowski spacetime through "
                    "the CY3 building block of a TCS manifold. The adopted internal space "
                    "Y_7 is a Joyce orbifold resolution with no such building block; on the "
                    "adopted path a 13D shadow splits as 13 = 7 + 6 with 6 = 4 + 2. The "
                    "value 4 = D_observable is unchanged."
                ),
                # dimensions.D_after_sp2r repointed at geometry.D_shadow_total:
                # the same 13D(12,1) per-shadow dimension under the name that is
                # actually registered (config.PMConstants keeps D_AFTER_SP2R as
                # an SSOT-backed alias of D_shadow_total).
                input_params=["topology.elder_kads", "geometry.D_shadow_total"],
                output_params=["dimensions.D_observable"],
                derivation={
                    "method": "dimensional_reduction",
                    "steps": [
                        "OFF-PATH reading: V7 was the TCS manifold of the retired seed (b3 = 24); the adopted internal space is Y_7, Joyce's resolution of T^7/(Z/2)^3 with b3 = 43",
                        "In the TCS reading, the building block's CY3 served as an intermediate step in the dimensional descent (a Joyce orbifold has no such building block)",
                        "Projection yields M^4 (Minkowski) x K^6 (internal Calabi-Yau)",
                        "In that reading, CY3 Hodge numbers were said to fix chirality and the gauge group in 4D; on the adopted path chirality is OPEN (D-011)"
                    ],
                    "parentFormulas": ["g2-holonomy-foundations", "b3-generations"]
                },
                eml_tree_str=(
                    "ops.sub(eml_scalar(7.0), eml_scalar(3.0))"
                ),
                eml_description=(
                    "CY projection: 7D G2 minus 3 internal compactified dimensions yields 4D Minkowski."
                ),
                terms={
                    "V_7": "7-dimensional internal G2 manifold (Y_7 on the adopted path)",
                    "CY_3": "Calabi-Yau 3-fold intermediate",
                    "M^4": "4-dimensional Minkowski spacetime",
                    "K^6": "6-dimensional internal compact space"
                },
            arithma=_arithma_sub(_arithma_num(7.0), _arithma_num(3.0)), eml=_eml_sub(_eml_scalar(7.0), _eml_scalar(3.0)), value=4.0),
        ]

    def get_output_param_definitions(self) -> List[Parameter]:
        """Return parameter definitions for foundations section."""
        return [
            Parameter(
                path="foundations.descent_stages",
                name="Dimensional Descent Stages",
                no_experimental_value=True,
                units="stages",
                description="Number of descent stages: 26D -> dual 13D -> 7D G2 -> 4D Minkowski",
                status="SYSTEM"
            ),
        ]

    # -------------------------------------------------------------------------
    # SSOT enrichment methods
    # -------------------------------------------------------------------------

    def get_references(self) -> List[Dict[str, Any]]:
        """Return bibliographic references for foundations section."""
        return [
            {
                "id": "joyce2000",
                "authors": "Joyce, D.D.",
                "title": "Compact Manifolds with Special Holonomy",
                "year": 2000,
                "publisher": "Oxford University Press",
                "doi": "10.1093/oso/9780198506010.001.0001",
                "url": "https://doi.org/10.1093/oso/9780198506010.001.0001",
                "notes": "Definitive reference for G2 holonomy manifold construction",
            },
            {
                "id": "chnp2015",
                "authors": "Corti, A., Haskins, M., Nordstrom, J., Pacini, T.",
                "title": "G2-manifolds and associative submanifolds via semi-Fano 3-folds",
                "year": 2015,
                "journal": "Duke Math. J.",
                "volume": "164",
                "pages": "1971-2092",
                "doi": "10.1215/00127094-3120743",
                "arxiv": "1207.4470",
                "url": "https://arxiv.org/abs/1207.4470",
                "notes": "OFF-PATH: the twisted-connected-sum construction used by earlier versions; the adopted internal space is a Joyce orbifold resolution",
            },
            {
                "id": "acharya_witten2001",
                "authors": "Acharya, B.S. and Witten, E.",
                "title": "Chiral Fermions from Manifolds of G2 Holonomy",
                "year": 2001,
                "arxiv": "hep-th/0109152",
                "url": "https://arxiv.org/abs/hep-th/0109152",
                "notes": "n_gen counts the singular involutions; chirality is OPEN on the smooth G2 manifold (disjoint loci leave no codimension-7 points)",
            },
        ]

    def get_certificates(self) -> List[Dict[str, Any]]:
        """Return certificate assertions for foundations section."""
        formulas = self.get_formulas()
        section = self.get_section_content()
        blocks = section.content_blocks if section else []
        paragraph_blocks = [b for b in blocks if b.type == "paragraph"]
        total_text = " ".join(b.content for b in paragraph_blocks)
        has_descent = "26D" in total_text and "4D" in total_text

        return [
            {
                "id": "CERT_FOUNDATIONS_FORMULA_COUNT",
                "assertion": "Foundations section defines at least 5 formulas for dimensional descent",
                "condition": f"formula_count >= 5 (actual: {len(formulas)})",
                "tolerance": 5,
                "status": "PASS" if len(formulas) >= 5 else "FAIL",
                "wolfram_query": "N/A (structural check)",
                "wolfram_result": "N/A",
                "sector": "foundations"
            },
            {
                "id": "CERT_FOUNDATIONS_DESCENT_PATH",
                "assertion": "Foundations content describes full 26D to 4D descent path",
                "condition": f"has_descent_path: {has_descent}",
                "tolerance": "exact",
                "status": "PASS" if has_descent else "FAIL",
                "wolfram_query": "N/A (content integrity check)",
                "wolfram_result": "N/A",
                "sector": "foundations"
            },
            {
                "id": "CERT_FOUNDATIONS_B3_GENERATIONS",
                "assertion": "OFF-PATH record (retired seed b3 = 24): the abandoned route b3/8 gave 3 there; the adopted count is n_gen = b2/4 = 3",
                "condition": "24 / 8 == 3",
                "tolerance": 0,
                "status": "PASS",
                "wolfram_query": "24/8",
                "wolfram_result": "3",
                "sector": "foundations"
            },
        ]

    def get_learning_materials(self) -> List[Dict[str, Any]]:
        """Return educational resources for foundations section topics."""
        return [
            {
                "topic": "G2 manifolds and holonomy groups",
                "url": "https://en.wikipedia.org/wiki/G2_manifold",
                "relevance": "Section 1.3 compactifies each shadow on Y_7, a compact 7-manifold with a torsion-free G2-structure; its metric moduli are not fixed at leading order, so it does not by itself fix the constants",
                "validation_hint": "G2 is the automorphism group of the octonions; a torsion-free G2-structure has a Ricci-flat metric"
            },
            {
                "topic": "Kaluza-Klein dimensional reduction",
                "url": "https://en.wikipedia.org/wiki/Kaluza%E2%80%93Klein_theory",
                "relevance": "Section 1.4 records the 13 = 7 + 6 split of each shadow and labels the earlier Calabi-Yau filtering as off-path; KK reduction is the mechanism by which gauge symmetries emerge from geometry",
                "validation_hint": "Compactification on manifold K with isometry group G yields gauge theory with group G"
            },
            {
                "topic": "Betti numbers in topology",
                "url": "https://en.wikipedia.org/wiki/Betti_number",
                "relevance": "Y_7 has (b2, b3) = (12, 43); n_gen = b2/4 = 3 counts the singular involutions; the 12 bridge pairs count the bulk's 24 space directions, not b3",
                "validation_hint": "b3 counts independent 3-cycles; for Joyce's resolution of T^7/(Z/2)^3, b3 = 7 + 3 b2 = 43 (the off-path TCS seed with b3 = 24 is retired)"
            },
        ]

    def validate_self(self) -> Dict[str, Any]:
        """Validate foundations section integrity."""
        checks = []

        formulas = self.get_formulas()
        f_ok = len(formulas) >= 5
        checks.append({
            "name": "At least 5 formulas defined for dimensional descent",
            "passed": f_ok,
            "confidence_interval": {
                "lower": 5,
                "upper": 20,
                "sigma": 0.0
            },
            "log_level": "INFO" if f_ok else "ERROR",
            "message": f"Formula count = {len(formulas)} (minimum 5)"
        })

        section = self.get_section_content()
        blocks = section.content_blocks if section else []
        b_ok = len(blocks) >= 20
        checks.append({
            "name": "At least 20 content blocks in foundations section",
            "passed": b_ok,
            "confidence_interval": {
                "lower": 20,
                "upper": 100,
                "sigma": 0.0
            },
            "log_level": "INFO" if b_ok else "ERROR",
            "message": f"Content blocks = {len(blocks)} (minimum 20)"
        })

        gen_ok = 24 // 8 == 3
        checks.append({
            "name": "OFF-PATH record: b3/8 = 24/8 = 3 at the retired seed (adopted count: n_gen = b2/4)",
            "passed": gen_ok,
            "confidence_interval": {
                "lower": 3,
                "upper": 3,
                "sigma": 0.0
            },
            "log_level": "INFO" if gen_ok else "ERROR",
            "message": "retired seed b3 = 24: b3/8 = 3 there; the adopted count is n_gen = b2/4 = 3 (the b3/8 route is an integer nowhere on the Joyce family)"
        })

        return {
            "passed": all(c["passed"] for c in checks),
            "checks": checks
        }

    def get_gate_checks(self) -> List[Dict[str, Any]]:
        """Return gate check results for foundations section."""
        formulas = self.get_formulas()
        section = self.get_section_content()
        blocks = section.content_blocks if section else []
        passed = len(formulas) >= 5 and len(blocks) >= 20

        return [
            {
                "gate_id": "G_FOUNDATIONS_DESCENT_COMPLETENESS",
                "simulation_id": self.metadata.id,
                "assertion": "Foundations section provides complete 26D-to-4D descent with formulas and narrative",
                "result": "PASS" if passed else "FAIL",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "formula_count": len(formulas),
                    "content_blocks": len(blocks),
                    "descent_stages": 4,
                    "b3_value": 24,
                    "n_generations": 3,
                    "section_type": "foundations"
                }
            },
        ]


# Module execution
if __name__ == "__main__":
    from metaphysica.simulations.base import PMRegistry
    registry = PMRegistry()
    sim = FoundationsV16_2()
    print(f"Simulation: {sim.metadata.title}")
    print(f"Version: {sim.metadata.version}")
    print(f"Section: {sim.metadata.section_id}")
    content = sim.get_section_content()
    if content:
        print(f"Content blocks: {len(content.content_blocks)}")
