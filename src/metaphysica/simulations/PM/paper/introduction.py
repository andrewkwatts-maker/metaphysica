#!/usr/bin/env python3
"""
PRINCIPIA METAPHYSICA - Introduction
====================================

DOI: 10.5281/zenodo.18079602

Licensed under the MIT License. See LICENSE file for details.

Provides section content for the Introduction (Section 1).

This simulation does not compute physics parameters. It generates the
narrative of the paper's introduction: the history of unification, then the
model told TOP DOWN, in the order the provenance registry
(`PM/geometry/closed_geometry/provenance.py`) and the certificate of Section
2.4 use:

    1.3.1  the standard physics the model uses, cited
    1.3.2  how the internal geometry is selected, and why
    1.3.3  the model's postulates
    1.3.4  what its computations establish (CG.1-CG.11)
    1.3.5  what was corrected
    1.3.6  what is open

HOW THE TEXT STAYS TRUE
=======================
* Numbers that follow the seed ((b_2, b_3), n_gen, the Betti sequence) are
  rendered by `geometry_narration.render`, never typed, so flipping the seed
  rewrites the sentences instead of leaving them contradicting the values.
* The six lists (standard, postulate, ruling, finding, correction, open) are
  generated from `PROVENANCE`, the registry Section 2.4 renders in full, so
  the introduction summarises that table without duplicating or drifting
  from it.
* Sentences that depend on the real form of phi branch on
  `geometry_narration.holonomy_claim()`.

The adopted model (author's rulings through D-015, 2026-10-01): bulk 26D of
signature (24,2), one time per 13D(12,1) shadow, 12 bridge pairs; internal
space Y_7 = Joyce's resolution of T^7/(Z/2)^3 with (b_2, b_3) = (12, 43),
pi_1 = 1, chi = 0; n_gen = b_2/4 = 3; chi_eff = 48 n (the K3 reading);
chirality, moduli (Re(T) included), dark energy and flavour OPEN.

SECTION: 1 (Introduction)

OUTPUTS:
    - None (narrative content only)

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
import html as _html_lib
import re as _re

from metaphysica.simulations.PM.geometry.geometry_narration import (
    fragments as _fragments,
    holonomy_claim as _holonomy_claim,
    render as _render,
)
from metaphysica.simulations.PM.geometry.closed_geometry.provenance import (
    PROVENANCE,
    by_kind,
)
from metaphysica.simulations.PM.geometry.closed_geometry.references import (
    REFERENCES as _REFERENCES,
)


# ---------------------------------------------------------------------------
# Wording helpers. Seed numbers come from `render`, lists from `PROVENANCE`,
# holonomy from `holonomy_claim()`; nothing the registry already states is
# typed a second time here.
# ---------------------------------------------------------------------------

def _r(template: str) -> str:
    """Fill `template` from the live geometry fragments, HTML register."""
    return _render(template, "html")


#: Typesetting for the registry's ASCII technical register. Applied in order
#: after HTML-escaping. Replacements are Unicode characters, never named
#: entities, so a later ASCII pattern (``\bpi\b``) cannot match inside an
#: earlier replacement. A pattern that matches nothing changes nothing, so a
#: new registry row is shown as written rather than mangled.
_TYPESET = (
    (r"\(Z/2\)\^3", "(ℤ/2)<sup>3</sup>"),
    (r"\bT\^7/Gamma\b", "T<sup>7</sup>/Γ"),
    (r"\bT\^(\d)", r"T<sup>\1</sup>"),
    (r"\bpi_1\b", "π<sub>1</sub>"),
    (r"\b([bh])_(\d)\b", r"\1<sub>\2</sub>"),
    (r"\bY_7\b", "Y<sub>7</sub>"),
    (r"\bchi_eff\b", "χ<sub>eff</sub>"),
    (r"\bk_gimel\b", "k<sub>ℷ</sub>"),
    (r"\bn_gen\b", "n<sub>gen</sub>"),
    (r"\bchi(?=\(| =)", "χ"),
    (r"\bG4\b", "G₄"),
    (r"\bG2\b", "G₂"),
    (r"\bE8\b", "E₈"),
    (r"\bK4\b", "K₄"),
    (r"\bA1\b", "A₁"),
    (r"\bphi\b", "φ"),
    (r"\bGamma\b", "Γ"),
    (r"\bSp\(2,R\)", "Sp(2,ℝ)"),
    (r"\bsqrt\(", "√("),
    (r"\bpi\b", "π"),
)


def _typeset(text: str) -> str:
    """A provenance row's technical text, typeset as HTML."""
    out = text.replace(">=", "≥").replace("<=", "≤")
    out = _html_lib.escape(out, quote=False)
    for pattern, repl in _TYPESET:
        out = _re.sub(pattern, repl, out)
    return out


def _short_cite(key: str) -> str:
    """'Surname(s) year, arXiv-or-venue' for a verified registry reference."""
    ref = _REFERENCES[key]
    parts = [s.strip() for s in ref["authors"].split(",")]
    names = [s for s in parts if s and "." not in s]
    if len(names) > 2:
        who = ", ".join(names[:-1]) + " &amp; " + names[-1]
    else:
        who = " &amp; ".join(names)
    text = "%s %s" % (who, ref["year"])
    if ref.get("arxiv"):
        text += ", " + ref["arxiv"]
    elif ref.get("journal"):
        venue = " ".join(p for p in (ref["journal"], ref.get("volume")) if p)
        text += ", " + venue
        if ref.get("pages"):
            text += ", " + ref["pages"]
    elif ref.get("publisher"):
        text += ", " + ref["publisher"]
    return text


def _provenance_items(kind: str) -> List[str]:
    """One HTML list item per provenance row of `kind`.

    STANDARD rows carry their verified sources (an unverified row says so,
    as the full table in Section 2.4 does); FINDING, CORRECTION, OPEN and
    RULING rows carry their evidence (a certificate id, a test or a decision
    entry); POSTULATE rows are assumptions and carry nothing.
    """
    items = []
    for p in by_kind(kind):
        text = _typeset(p.technical)
        if kind == "STANDARD":
            if not p.verified:
                source = "source to be verified"
            elif p.references:
                source = "; ".join(_short_cite(k) for k in p.references)
            else:
                source = ""
        elif kind == "POSTULATE":
            source = ""
        else:
            source = _html_lib.escape(p.evidence, quote=False)
        items.append("%s <em>[%s]</em>" % (text, source) if source else text)
    return items


def _n_singular() -> int:
    """The number of singular involutions on the live seed (= b_2/4)."""
    return int(round(float(_fragments("plain")["n_gen"])))


def _w0_live() -> str:
    """-(b_3 - 1)/b_3 on the live seed: what w_0 = -1 + 1/b_3 gives there."""
    from metaphysica.simulations.PM.geometry.b3_path import seed_values

    b3, _b2 = seed_values()
    return "&minus;%d/%d" % (b3 - 1, b3)


class IntroductionV16(SimulationBase):
    """
    Introduction section generator.

    Provides the narrative of Section 1: the history of unification, then the
    model told top down -- standard physics, the selection of the internal
    geometry, postulates, findings, corrections and open problems -- with
    seed numbers rendered live and the six lists generated from the
    provenance registry.
    """

    @property
    def metadata(self) -> SimulationMetadata:
        """Return metadata about this simulation."""
        return SimulationMetadata(
            id="introduction_v16_0",
            version="24.2",
            domain="introduction",
            title="Introduction to Principia Metaphysica",
            description=(
                "Narrative introduction: the history of unification, then the "
                "model top down -- standard physics, how the internal geometry "
                "is selected, postulates, findings, corrections and open "
                "problems"
            ),
            section_id="1",
            subsection_id=None
        )

    @property
    def required_inputs(self) -> List[str]:
        """Registry parameters referenced by the introduction narrative."""
        return ["topology.elder_kads"]

    @property
    def output_params(self) -> List[str]:
        """No output parameters - narrative content only."""
        return []

    @property
    def output_formulas(self) -> List[str]:
        """No formulas - introduction is narrative."""
        return []

    def run(self, registry: 'PMRegistry') -> Dict[str, Any]:
        """
        Execute the introduction generation.

        Args:
            registry: PMRegistry instance (not used)

        Returns:
            Empty dictionary (no computed parameters)
        """
        # Introduction section provides narrative content only
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

    def get_beginner_explanation(self) -> Dict[str, Any]:
        """
        Return a beginner-friendly explanation of Principia Metaphysica.

        Returns:
            Dictionary with title and explanation suitable for non-experts
        """
        frag = _fragments("plain")
        return {
            "title": "What is Principia Metaphysica?",
            "summary": (
                "Principia Metaphysica is a speculative model of fundamental "
                "physics. It starts from established physics -- M-theory, "
                "with seven extra dimensions curled into a special shape -- "
                "and adds assumptions of its own about a larger space with "
                "two time directions."
            ),
            "explanation": (
                "The model tells its story from the top down. Established "
                "physics comes first: seven extra dimensions curled into a "
                "special shape leave a four-dimensional world whose forces "
                "and fields are counted by the shape's holes. Next comes how "
                "the shape is chosen. A symmetry of the model's basic 3-form "
                "fixes how a seven-dimensional doughnut is folded, and "
                "Joyce's recipe for smoothing the folds gives a family of "
                "possible shapes. Only some of them have no loops that cannot "
                "be shrunk away, and among those only one lets the model's "
                "twelve links match the twelve smoothed creases one to one "
                "(the model identifies each link with one crease, an "
                "assumption it states openly). That shape has %s "
                "two-dimensional holes and %s three-dimensional holes, and "
                "counting the folds that leave creases gives %s generations "
                "of particles. The model's own assumptions -- "
                "a 26-dimensional space with two time directions, split into "
                "two mirror halves joined by twelve links -- are labelled as "
                "assumptions. Four problems remain open: why matter tells "
                "left from right, what fixes the size of the extra "
                "dimensions, what drives dark energy, and why particles have "
                "the masses they do."
                % (frag["b2"], frag["b3"], frag["n_gen"])
            ),
            "key_concepts": [
                {
                    "name": "Extra Dimensions",
                    "explanation": (
                        "Just as a 3D object casts a 2D shadow, our 4D spacetime "
                        "(3 space + 1 time) might be a 'shadow' of a higher-dimensional reality. "
                        "PM proposes 26 dimensions -- 24 of space and 2 of time, one time for "
                        "each of two 13-dimensional 'shadows' -- that reduce down to the 4 we "
                        "observe. This is the model's assumption, not established physics."
                    )
                },
                {
                    "name": "Two Shadows Joined by Bridges",
                    "explanation": (
                        "The two shadows are mirror halves of the 26-dimensional space, joined "
                        "by twelve bridges; each shadow has its own time direction. Whether a "
                        "second time direction is harmless -- free of the unphysical 'ghost' "
                        "states it could bring -- has not been shown and is an open problem. "
                        "The model does not yet explain dark energy."
                    )
                },
                {
                    "name": "Geometry to Physics",
                    "explanation": (
                        "Instead of putting particles and forces into spacetime by hand, PM "
                        "proposes that geometry comes from a fundamental field (the 'Pneuma') "
                        "and that the shape of the seven hidden dimensions sets the particle "
                        "content. The shape it uses is built by Joyce's method: a "
                        "seven-dimensional doughnut folded by three mirror symmetries, with "
                        "the creases smoothed out. Its hole counts are %s, and the number of "
                        "folds that leave creases gives %s generations."
                        % (frag["betti_pair"], frag["n_gen"])
                    )
                },
                {
                    "name": "Testable Predictions",
                    "explanation": (
                        "Some numbers are genuine tests and some are not. Several headline "
                        "constants were tuned to data rather than predicted, and are labelled "
                        "as calibrations. The dark-energy value w0 = -23/24 was fixed with an "
                        "older, retired version of the shape, and it sits more than three "
                        "standard deviations from the latest DESI result (w0 = -0.752 +/- "
                        "0.057). Section 6 lists every comparison with its status; the "
                        "predictions that remain genuinely untested, such as the proton decay "
                        "rate and new particles at colliders, are listed there with their "
                        "caveats."
                    )
                }
            ],
            "why_it_matters": (
                "The aim is to replace arbitrary input parameters with geometry. The "
                "internal shape is now fixed by stated rules rather than by fitting, and "
                "every claim is labelled -- established physics, the model's own "
                "assumption, a computed finding, a correction, or an open problem -- so a "
                "reader can see what is claimed and what is not."
            )
        }

    def get_foundations(self) -> Dict[str, str]:
        """
        Return the foundational principles of Principia Metaphysica.

        Returns:
            Dictionary mapping principle names to descriptions
        """
        n = _n_singular()
        foundations = {
            "metric_emergence": (
                "POSTULATE: spacetime geometry is proposed to emerge from spinor "
                "bilinears of a fundamental fermionic field, the Pneuma. The "
                "Pneuma&ndash;vielbein construction is meant to give a Lorentzian "
                "(&minus;,+,+,+) metric in 4D without assuming a background metric, "
                "which would remove the usual circular dependence on a pre-existing "
                "one. It is the model's assumption, not a result of standard physics."
            ),
            "dimensional_hierarchy": _r(
                "POSTULATE: the bulk is 26-dimensional with signature (24,2) = "
                "(12,1) + (12,1) &mdash; 24 space directions and two times, one per "
                "13D(12,1) shadow. The space directions pair into 12 bridges, and "
                "each shadow takes one direction from every bridge plus its own "
                "time. Each shadow reduces to 4D on the internal space {manifold}, "
                "{structure} built as {construction}, with {betti_pair}. Ghost "
                "control of the second time is an open problem."
            ),
            "moduli_stabilization": _r(
                "OPEN: the moduli of {manifold}, Re(T) included, are not fixed at "
                "leading order. The G<sub>4</sub>-flux potential is positive and runs "
                "away (CG.6); the singular loci carry N = 4 super Yang&ndash;Mills, "
                "so there is no gaugino condensate and no racetrack on {manifold} "
                "(CG.5), and no member of the n = 3 line has a confining sector "
                "(CG.10). Re(T) is an open modulus (author's ruling D-015). The "
                "racetrack values used by earlier versions (&epsilon; &asymp; 0.2257, "
                "Re(T) = 7.086) are {calibrated_at_24}."
            ),
            "thermal_time": (
                "POSTULATE (the thermal-time hypothesis of Connes and Rovelli): "
                "physical time is identified with the modular flow of the KMS "
                "(Kubo&ndash;Martin&ndash;Schwinger) equilibrium state of the Pneuma "
                "field. The model adopts this as its answer to the 'frozen "
                "formalism' problem of canonical quantum gravity, where time is "
                "absent at the fundamental level, and as a link between quantum "
                "gravity and the arrow of time. It is a hypothesis about what time "
                "is, not a derivation."
            ),
            "gauge_unification": _r(
                "SU(3) &times; SU(2) &times; U(1) couplings are run with the standard "
                "renormalisation group toward a unification scale of order "
                "10<sup>16</sup> GeV, where that running gives "
                "&alpha;<sub>GUT</sub><sup>&minus;1</sup> &asymp; 42.7. This is standard "
                "physics with a calibrated &alpha;<sub>GUT</sub> coefficient; it is "
                "not an output of the topology of {manifold}."
            ),
            "topological_generations": _r(
                "Three generations: {n_gen_route} of the folding group "
                "&Gamma; = (&#8484;/2)<sup>3</sup> (the ruled route), with no free "
                "parameter. The effective index is the K3 reading, "
                "&chi;<sub>eff</sub> = 2 &Sigma; &chi;(K3) = 48n, one Kummer K3 per "
                "singular involution counted once per shadow, so "
                "&chi;<sub>eff</sub> = " + str(48 * n) + " at n = " + str(n)
                + " (author's ruling D-015). It is not the Euler characteristic of "
                "{manifold} ({chi_y7}), and n<sub>gen</sub> = &chi;<sub>eff</sub>/48 = n "
                "restates b<sub>2</sub>/4 rather than deriving it again. How the "
                "generations become chiral is an open problem."
            ),
            "yukawa_hierarchy": _r(
                "OPEN: flavour needs a chiral sector, which {manifold} does not "
                "provide &mdash; its singular loci are disjoint, so it has no "
                "codimension-7 points. The model's Yukawa textures (exponential "
                "wavefunction-overlap suppression, with &epsilon; = e<sup>&minus;&lambda;</sup> "
                "and &lambda; = 1.5 an ansatz following Froggatt&ndash;Nielsen) are "
                "model constructs or fits, not derivations of the fermion mass "
                "hierarchy."
            ),
            "cosmological_framework": _r(
                "OPEN: dark energy is not explained. The leading-order flux "
                "potential cannot accelerate the universe, since "
                "|&nabla;V|/V &ge; 5&radic;(2/7) &asymp; 2.673 &gt; &radic;2 (CG.11). "
                "The value w<sub>0</sub> = &minus;23/24 is frozen at {off_path_seed}, "
                "and w<sub>0</sub> = &minus;1 + 1/b<sub>3</sub> has no derivation; both "
                "&minus;23/24 and the adopted-seed value "
            ) + _w0_live() + _r(
                " lie more than 3&sigma; from the DESI DR2 headline "
                "w<sub>0</sub> = &minus;0.752 &plusmn; 0.057. The mirror-sector ratio "
                "&Omega;<sub>DM</sub>/&Omega;<sub>b</sub> &asymp; 5.4 rests on a mirror "
                "temperature ratio calibrated to the Planck abundance, so it is a "
                "calibration, not a prediction."
            ),
        }

        assert all(v.strip() for v in foundations.values()), "All foundations must be non-empty"
        assert len(foundations) >= 6, "Must have at least 6 foundational principles"

        return foundations

    def get_section_content(self) -> Optional[SectionContent]:
        """
        Return section content for Section 1: Introduction.

        The history of unification (1.1, 1.2), then the model top down
        (1.3.1-1.3.6, in the provenance registry's order), then the two
        postulates that need room (1.4, 1.5), then related work and the
        outline (1.6). Seed numbers are rendered live; the six lists are
        generated from PROVENANCE; holonomy sentences follow the real-form
        fork.

        Returns:
            SectionContent instance with introduction narrative
        """
        # Validate that helper methods return non-empty content
        beginner_exp = self.get_beginner_explanation()
        assert beginner_exp, "get_beginner_explanation() returned empty content"

        foundations = self.get_foundations()
        assert foundations, "get_foundations() returned empty content"
        assert len(foundations) >= 6, "get_foundations() must return at least 6 principles"

        n = _n_singular()
        chi_eff_total = 48 * n
        compact = bool(_holonomy_claim()["may_claim_g2_holonomy"])

        if compact:
            holonomy_reading = (
                "For a compact torsion-free G₂-structure, a finite "
                "fundamental group is equivalent to holonomy exactly G₂ "
                "(Joyce, Prop. 1.1.1). With the compact real form of &phi; in "
                "force, the n = 3 line is therefore the top of the holonomy "
                "ladder &mdash; restricted holonomy trivial, SU(2), SU(3) and "
                "G₂ for n = 0, 1, 2, 3 &mdash; and its members are the only "
                "ones in the family with holonomy exactly G₂."
            )
        else:
            holonomy_reading = (
                "For a compact torsion-free G₂-structure, a finite "
                "fundamental group is equivalent to holonomy exactly G₂ "
                "(Joyce, Prop. 1.1.1), which makes the n = 3 line the top of "
                "the holonomy ladder on the compact real form. The real-form "
                "branch the code currently runs is the split form G₂*, "
                "whose induced metric has signature (4,3) and supports no "
                "holonomy statement; until the compact form is switched in, "
                "only the topological half &mdash; &pi;<sub>1</sub> finite "
                "exactly at n = 3 &mdash; is claimed here, and the selection "
                "below uses only that half."
            )

        content_blocks = [
            # ================================================================
            # Lead paragraph
            # ================================================================
            ContentBlock(
                type="paragraph",
                content=_r(
                    "This paper presents <strong>Principia Metaphysica</strong>, a "
                    "speculative model built on established physics &mdash; "
                    "M-theory compactified on a compact seven-dimensional internal "
                    "space &mdash; together with postulates of its own: a "
                    "26-dimensional bulk of signature (24,2), whose 24 space "
                    "directions pair into twelve bridges and whose two times belong "
                    "one to each of two 13-dimensional shadows of signature (12,1). "
                    "The internal space is {manifold}, {construction}: {structure}. "
                    "Its Betti numbers are {betti_pair}; its fundamental group is "
                    "trivial and {chi_y7}. It is selected, not fitted. The "
                    "model&rsquo;s 3-form &phi; fixes the folding group &Gamma; = "
                    "(&#8484;/2)<sup>3</sup>; Joyce&rsquo;s construction from &Gamma; "
                    "reaches a family of 28 Betti pairs; a finite fundamental group "
                    "occurs only on the line where all three folds are singular; and "
                    "on that line the match between the 12 bridges and the {b2} "
                    "resolved singular components picks out {manifold} without "
                    "reference to data "
                    "(&sect;1.3.2). Three generations then follow as {n_gen_route} "
                    "&mdash; a count that the observed three generations test rather "
                    "than choose. The introduction tells this story top down: the "
                    "standard physics the model uses, how the geometry is selected, "
                    "the model&rsquo;s postulates, what its computations establish "
                    "(the certificate CG.1&ndash;CG.11 of Section 2.4), what has been "
                    "corrected, and what remains open. Four physics problems are "
                    "open, and the geometry avoids none of them: chirality, moduli "
                    "stabilisation (Re(T) included), dark energy and flavour. The "
                    "model does <strong>not</strong> fit the data globally: the "
                    "validation registry&rsquo;s computed verdict is "
                    "<strong>POOR_FIT</strong>, earlier global-alignment headlines "
                    "are withdrawn, and each comparison with experiment is reported "
                    "in its own row."
                ),
                label="lead"
            ),

            # Status & Caveats note
            ContentBlock(
                type="note",
                content=_r(
                    "<h4>Status &amp; Caveats</h4>"
                    "<p>Principia Metaphysica is a <strong>speculative theoretical "
                    "framework</strong> in early development. Its claims carry "
                    "labels, and the labels matter:</p>"
                    "<ul>"
                    "<li><strong>No peer review:</strong> this work has not been "
                    "reviewed by the broader physics community.</li>"
                    "<li><strong>Standard physics versus the model:</strong> results "
                    "labelled STANDARD are established physics with cited sources; "
                    "POSTULATES are the model&rsquo;s own assumptions; FINDINGS are "
                    "the model&rsquo;s computations, each with a test (Section "
                    "2.4).</li>"
                    "<li><strong>Calibrations:</strong> the constants built on "
                    "k<sub>&#8503;</sub> = b<sub>3</sub>/2 + 1/&pi; (&alpha;<sup>&minus;1</sup>, "
                    "the Higgs vev, sin<sup>2</sup>&theta;<sub>W</sub>, "
                    "T<sub>CMB</sub>, &mu;) are fits made at {off_path_seed}; they are "
                    "labelled CALIBRATED and their values are unchanged. The "
                    "racetrack values (&epsilon; &asymp; 0.2257, Re(T) = 7.086) are "
                    "{calibrated_at_24}; no racetrack exists on {manifold}. The VEV "
                    "and &alpha;<sub>GUT</sub> coefficients are calibration inputs, "
                    "and two PMNS parameters (&theta;<sub>13</sub>, "
                    "&delta;<sub>CP</sub>) are fitted to NuFIT 6.0 pending an explicit "
                    "Yukawa calculation.</li>"
                    "<li><strong>Predictions versus postdictions:</strong> most "
                    "comparisons are with values measured before the formula was "
                    "written. Genuine predictions (proton decay rate, KK graviton "
                    "mass, axion properties) remain untested.</li>"
                    "<li><strong>Consciousness appendix:</strong> the "
                    "Orch-OR/consciousness appendix is an interpretive speculation, "
                    "not a core claim of the framework.</li>"
                    "</ul>"
                ),
                label="status-caveats"
            ),

            # ================================================================
            # 1.1 The Quest for Unification
            # ================================================================
            ContentBlock(
                type="heading",
                content="The Quest for Unification",
                level=2,
                label="1.1"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The history of physics is, in large part, a history of unification. "
                    "James Clerk Maxwell's synthesis of electricity and magnetism in 1865 "
                    "revealed that apparently distinct phenomena were manifestations of a "
                    "single electromagnetic field. This triumph established a paradigm: what "
                    "appears as separate forces at low energies may be unified at higher "
                    "energy scales."
                )
            ),
            ContentBlock(
                type="note",
                content=(
                    "<h4>Maxwell's Legacy</h4>"
                    "<p>Maxwell's equations demonstrated that electric and magnetic fields are "
                    "two aspects of a single entity, the electromagnetic field tensor F<sub>μν</sub>. "
                    "The symmetry underlying this unification is the U(1) gauge symmetry of "
                    "electrodynamics.</p>"
                ),
                label="maxwell-legacy"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The 20th century witnessed further dramatic unifications. The "
                    "Glashow-Weinberg-Salam electroweak theory (1967-1968) demonstrated that "
                    "electromagnetism and the weak nuclear force are unified into a single "
                    "SU(2)<sub>L</sub> × U(1)<sub>Y</sub> gauge theory, spontaneously broken "
                    "at the electroweak scale (~246 GeV) to yield the observed low-energy "
                    "phenomenology."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The Standard Model of particle physics incorporates the electroweak theory "
                    "with quantum chromodynamics (QCD), the SU(3)<sub>C</sub> gauge theory of the "
                    "strong nuclear force. While phenomenologically successful, the Standard Model's "
                    "gauge group G<sub>SM</sub> = SU(3)<sub>C</sub> × SU(2)<sub>L</sub> × U(1)<sub>Y</sub> "
                    "appears somewhat arbitrary, motivating the search for a larger unifying structure."
                )
            ),
            ContentBlock(
                type="equation",
                content="G<sub>SM</sub> = SU(3)<sub>C</sub> × SU(2)<sub>L</sub> × U(1)<sub>Y</sub> ⊂ G<sub>GUT</sub>",
                label="sm-gut-embedding"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Grand Unified Theories (GUTs), pioneered by Georgi, Glashow, Pati, and Salam "
                    "in the 1970s, embed the Standard Model into a larger simple gauge group. The "
                    "minimal SU(5) model of Georgi-Glashow (1974) provided the first concrete "
                    "realization, though it is now disfavored by proton decay constraints. The SO(10) "
                    "model, proposed independently by Fritzsch and Minkowski (1975) and by Georgi "
                    "(1975), remains a compelling candidate due to its natural accommodation of a "
                    "right-handed neutrino and elegant family structure."
                )
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>SU(5):</strong> Minimal GUT; predicts proton decay at rates now excluded",
                    "<strong>SO(10):</strong> Natural right-handed neutrino; all fermions in 16-dim spinor",
                    "<strong>E<sub>6</sub>:</strong> Emerges naturally from heterotic string compactifications",
                    "<strong>Flipped SU(5):</strong> SU(5) × U(1)<sub>X</sub> with different hypercharge embedding"
                ],
                label="gut-models"
            ),

            # ================================================================
            # 1.2 Geometrization of Forces
            # ================================================================
            ContentBlock(
                type="heading",
                content="Geometrization of Forces",
                level=2,
                label="1.2"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "A parallel thread in the unification program concerns the geometrization of "
                    "gauge forces. Einstein's general relativity demonstrated that gravity is not "
                    "a force in the Newtonian sense but rather the manifestation of spacetime curvature. "
                    "The natural question arises: can other forces be similarly geometrized?"
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The Kaluza-Klein (KK) proposal (Kaluza 1921, Klein 1926) provided an affirmative "
                    "answer for electromagnetism. By extending spacetime from 4 to 5 dimensions and "
                    "compactifying the extra dimension on a circle S¹, the gravitational field in 5D "
                    "yields both 4D gravity and a U(1) gauge field upon dimensional reduction."
                )
            ),
            ContentBlock(
                type="equation",
                content="M<sup>5</sup> = M<sup>4</sup> × S<sup>1</sup> → g<sub>MN</sub><sup>(5)</sup> → {g<sub>μν</sub><sup>(4)</sup>, A<sub>μ</sub>, φ}",
                label="kk-decomposition"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The gauge symmetry arises geometrically: the U(1) corresponds to isometries of "
                    "the internal S¹. More generally, compactification on a manifold K with isometry "
                    "group G yields a gauge theory with gauge group G in the lower-dimensional "
                    "effective theory."
                )
            ),
            ContentBlock(
                type="note",
                content=(
                    "<h4>Gauge from Geometry</h4>"
                    "<p>For a general internal manifold K<sup>d</sup>, the isometry group Isom(K) "
                    "becomes the gauge group of the dimensionally reduced theory. The gauge bosons "
                    "correspond to Killing vectors on the internal space. This geometric origin "
                    "provides a natural explanation for the gauge principle.</p>"
                ),
                label="gauge-from-geometry"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "To accommodate the full Standard Model gauge group, one requires an internal "
                    "manifold K whose isometry group contains G<sub>SM</sub>. For SO(10) unification, "
                    "the internal space must possess SO(10) isometries. This constraint severely "
                    "restricts the geometry of K and motivates the search for specific compactification "
                    "manifolds."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Modern realizations of this program include supergravity compactifications, "
                    "heterotic string theory on Calabi-Yau manifolds, and M-theory on G₂ "
                    "manifolds. Each approach provides a rich structure connecting extra-dimensional "
                    "geometry to four-dimensional particle physics. In M-theory on a compact G₂ "
                    "manifold the mechanism differs from the classical one: a compact Ricci-flat "
                    "manifold whose holonomy is all of G₂ has no continuous isometries, so the "
                    "abelian gauge fields come from its harmonic 2-forms (b<sub>2</sub> of them) "
                    "and non-abelian ones from its singularities. That is the setting this model "
                    "starts from."
                )
            ),

            # ================================================================
            # 1.3 The Model, Top Down
            # ================================================================
            ContentBlock(
                type="heading",
                content="The Model, Top Down",
                level=2,
                label="1.3"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "This section is the paper&rsquo;s map. It tells the model&rsquo;s story "
                    "from the top down and labels every claim by its kind: "
                    "<strong>STANDARD</strong> (established physics, cited to its source), "
                    "<strong>POSTULATE</strong> (an assumption the model makes), "
                    "<strong>FINDING</strong> (a result of the model&rsquo;s own computation, "
                    "with its test), <strong>CORRECTION</strong> (an earlier claim that was "
                    "wrong, and what replaced it), <strong>OPEN</strong> (a problem not yet "
                    "solved) and <strong>RULING</strong> (a decision that is the "
                    "author&rsquo;s). The lists below are generated from the same provenance "
                    "registry that Section 2.4 renders in full, with every source and test, so "
                    "the two cannot drift apart."
                ),
                label="top-down-map"
            ),

            # 1.3.1 Standard physics
            ContentBlock(
                type="heading",
                content="1.3.1 Standard Physics the Model Uses",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The internal geometry rests on established mathematics and physics, which "
                    "the model uses without modification. None of the following is a claim of "
                    "the model:"
                )
            ),
            ContentBlock(
                type="list",
                items=_provenance_items("STANDARD"),
                label="provenance-standard"
            ),

            # 1.3.2 Selection
            ContentBlock(
                type="heading",
                content="1.3.2 How the Geometry Is Selected, and Why",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=_r(
                    "The selection runs downward from the model&rsquo;s 3-form, and each "
                    "step names its evidence in Section 2.4. The 3-form &phi; on "
                    "&#8477;<sup>7</sup> is read from the octonion product, and the "
                    "diagonal sign changes that preserve it &mdash; the same on either "
                    "real form of &phi; &mdash; form the group &Gamma; = "
                    "(&#8484;/2)<sup>3</sup>, generated by three involutions. Joyce&rsquo;s "
                    "construction divides the flat torus T<sup>7</sup> by &Gamma; and "
                    "replaces each singular three-torus with an Eguchi&ndash;Hanson space. "
                    "With pairwise-disjoint singular sets, resolved in every admissible "
                    "way, it reaches 28 literature-checked Betti pairs "
                    "(b<sub>2</sub>, b<sub>3</sub>), on the lines b<sub>2</sub> + "
                    "b<sub>3</sub> = 7 + 16n, where n = 0, 1, 2, 3 counts the singular "
                    "involutions (CG.7). Earlier versions of the model used "
                    "{off_path_seed}; it is not among them, so Joyce&rsquo;s construction "
                    "from &Gamma; cannot produce it."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The fundamental group then divides the family. By Armstrong&rsquo;s "
                    "theorem, &pi;<sub>1</sub> of the quotient is the orbifold group modulo "
                    "the subgroup generated by elements with fixed points. It is finite "
                    "exactly when all three generating involutions are singular &mdash; the "
                    "n = 3 line b<sub>2</sub> + b<sub>3</sub> = 55 &mdash; and trivial there "
                    "(CG.4). " + holonomy_reading
                )
            ),
            ContentBlock(
                type="paragraph",
                content=_r(
                    "On that line the model&rsquo;s own structure singles out one member. "
                    "Its twelve bridges are the directed edges of K<sub>4</sub> on a Fano "
                    "arc of four faces, grouped into three E<sub>8</sub> blocks. The three "
                    "singular involutions fix such an arc, and each E<sub>8</sub> block "
                    "contains exactly one side of their triangle, so blocks and involutions "
                    "match one to one, and the twelve bridges match the twelve resolved "
                    "components as a single 3 &times; 4 structure. That structure exists "
                    "only on the all-plain members of the family, and on the n = 3 line the "
                    "all-plain member is (b<sub>2</sub>, b<sub>3</sub>) = (12, 43) (CG.8). "
                    "Working assumption WA-1 identifies each bridge with one resolved "
                    "A<sub>1</sub> component, carrying one U(1); the author adopted it "
                    "(ruling D-015), so the correspondence selects the member without "
                    "data. Its consequence to test: the {b2} U(1) gauge couplings come in "
                    "three quartets, one per E<sub>8</sub> block."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=_r(
                    "The internal space is that member: {manifold} = {construction}, "
                    "{structure}, with {betti_pair}, Betti sequence {betti_sequence} and "
                    "{b3_split}, &pi;<sub>1</sub> = 1 and {chi_y7} (CG.1&ndash;CG.4). Its "
                    "singular set is {b2} disjoint flat three-tori, each with "
                    "b<sub>1</sub> = 3; on the smooth manifold they carry "
                    "U(1)<sup>{b2}</sup> (SU(2)<sup>{b2}</sup> at the orbifold point), with "
                    "the local content of N = 4 super Yang&ndash;Mills (CG.3, CG.5). Three "
                    "generations follow from the selection rather than choosing it: "
                    "{n_gen_route}. Each singular involution fixes one &Gamma;-orbit of "
                    "four three-tori, so b<sub>2</sub>/4 counts the singular involutions "
                    "(CG.3). Earlier versions picked the seed by requiring three "
                    "generations, which is selection by data; with WA-1 adopted, the seed "
                    "is selected without data and three generations become an output "
                    "tested against the three observed."
                )
            ),
            ContentBlock(
                type="equation",
                content=_r(
                    "&phi; &rarr; &Gamma; = (&#8484;/2)<sup>3</sup> &rarr; Joyce&rsquo;s "
                    "family (28 pairs) &rarr; n = 3: b<sub>2</sub> + b<sub>3</sub> = 55 "
                    "(&pi;<sub>1</sub> finite) &rarr; WA-1: {betti_pair} &rarr; "
                    "n<sub>gen</sub> = b<sub>2</sub>/4 = {n_gen}"
                ),
                label="selection-chain"
            ),
            ContentBlock(
                type="note",
                content=(
                    "<h4>The author&rsquo;s rulings behind the selection</h4>"
                    "<p>The author&rsquo;s rulings of 2026-10-01 (D-015) settle the choices "
                    "the selection depends on. &phi; takes the compact real form, the one "
                    "the framework&rsquo;s own octonion product gives; the split form stays a "
                    "switchable path, and no published number depends on the choice (D-003). "
                    "WA-1 is adopted. &chi;<sub>eff</sub> is the K3 reading, and Re(T) is an "
                    "open modulus. Rulings recorded in the provenance registry:</p>"
                    "<ul>"
                    + "".join("<li>%s</li>" % item for item in _provenance_items("RULING"))
                    + "</ul>"
                ),
                label="selection-rulings"
            ),

            # 1.3.3 Postulates
            ContentBlock(
                type="heading",
                content="1.3.3 The Model's Postulates",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Beyond standard physics, the model assumes the following. Each is "
                    "labelled a postulate wherever it is stated:"
                )
            ),
            ContentBlock(
                type="list",
                items=_provenance_items("POSTULATE"),
                label="provenance-postulates"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Two further proposals are developed in &sect;1.4 and &sect;1.5 and "
                    "labelled there: that geometry emerges from a fundamental spinor field, "
                    "the Pneuma, and that the normed division algebras motivate thirteen "
                    "dimensions per shadow. Whether the second time direction is free of "
                    "ghosts is an open problem (&sect;1.3.6); the appeals to Bars&rsquo; "
                    "Sp(2,&#8477;) theorem and to 26 as the bosonic critical dimension were "
                    "withdrawn in the signature ruling of 2026-08-31."
                )
            ),

            # 1.3.4 Findings
            ContentBlock(
                type="heading",
                content="1.3.4 What the Model's Computations Establish",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=_r(
                    "Section 2.4 publishes the closed geometry as a certificate of theorems "
                    "CG.1&ndash;CG.11, each rendered from a live computation and paired with "
                    "the test that fails if it is false and the observation that would "
                    "refute it. In order: the Betti sequence {betti_sequence} of {manifold} "
                    "(CG.1); {chi_y7} (CG.2); a singular set of {b2} disjoint flat "
                    "three-tori, each with b<sub>1</sub> = 3 (CG.3); &pi;<sub>1</sub> = 1, "
                    "with &pi;<sub>1</sub> finite only when all three generating involutions "
                    "are singular (CG.4); the gauge content &mdash; U(1)<sup>{b2}</sup> on "
                    "the resolved manifold and local N = 4 super Yang&ndash;Mills at the "
                    "orbifold point, which neither confines nor forms a gaugino condensate "
                    "(CG.5); a leading-order G<sub>4</sub>-flux potential that runs away and "
                    "fixes no modulus (CG.6); the reachable set of Joyce&rsquo;s construction "
                    "(CG.7); the bridge&ndash;component correspondence (CG.8); one Kummer K3 "
                    "surface per singular involution (CG.9); the absence of any confining "
                    "sector on the n = 3 line (CG.10); and a flux potential too steep to "
                    "accelerate the universe (CG.11). The registry records the findings as "
                    "follows:"
                )
            ),
            ContentBlock(
                type="list",
                items=_provenance_items("FINDING"),
                label="provenance-findings"
            ),
            ContentBlock(
                type="paragraph",
                content=_r(
                    "Read through CG.9, the effective index is the K3 reading, adopted by "
                    "the author&rsquo;s ruling D-015: &chi;<sub>eff</sub> = 2 &Sigma; "
                    "&chi;(K3) = 48n, the Kummer K3 surfaces transverse to the n singular "
                    "involutions, counted once per shadow, so &chi;<sub>eff</sub> = "
                    + str(chi_eff_total) + " at n = " + str(n) + ". It is not the Euler "
                    "characteristic of {manifold}, which is 0. And n<sub>gen</sub> = "
                    "&chi;<sub>eff</sub>/48 = n restates b<sub>2</sub>/4: it is neither a "
                    "second derivation of the generation count nor an index theorem for "
                    "chirality."
                )
            ),

            # 1.3.5 Corrections
            ContentBlock(
                type="heading",
                content="1.3.5 What Was Corrected",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Several earlier claims of the model were wrong. Each is corrected "
                    "below; the earlier wording survives only as labelled history, and the "
                    "dead ends stay runnable as switchable paths:"
                )
            ),
            ContentBlock(
                type="list",
                items=_provenance_items("CORRECTION"),
                label="provenance-corrections"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The real-form correction is adopted by the author&rsquo;s ruling of "
                    "2026-10-01 (D-015), with the split form kept as a switchable path. The "
                    "combinatorial results of &sect;1.3.2 &mdash; &Gamma;, the family, the "
                    "Betti numbers, &pi;<sub>1</sub> and &chi; &mdash; come out the same on "
                    "both forms. What the compact form supplies is the geometry behind "
                    "them: the Eguchi&ndash;Hanson resolution that realises the Betti "
                    "numbers needs a Riemannian transverse space, and holonomy and "
                    "Joyce&rsquo;s existence theorem are statements about the compact form "
                    "(D-003)."
                )
            ),

            # 1.3.6 Open problems
            ContentBlock(
                type="heading",
                content="1.3.6 What Is Open",
                level=3
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The geometry avoids none of the four physics problems &mdash; "
                    "chirality, moduli, dark energy and flavour (D-011) &mdash; and two of "
                    "them are now no-go statements inside the construction. Each open "
                    "problem is stated with its status:"
                )
            ),
            ContentBlock(
                type="list",
                items=_provenance_items("OPEN"),
                label="provenance-open"
            ),
            ContentBlock(
                type="paragraph",
                content=_r(
                    "What earlier versions presented as solutions is labelled accordingly. "
                    "No racetrack exists on {manifold}: its singular loci carry N = 4 super "
                    "Yang&ndash;Mills, and no member of the n = 3 line has a confining "
                    "sector (CG.5, CG.10). The racetrack values &epsilon; &asymp; 0.2257 "
                    "and Re(T) = 7.086 are {calibrated_at_24}, values computed with the "
                    "calibrated Re(T) are CALIBRATED, and Re(T) itself is an open modulus "
                    "(D-015). The leading-order flux potential has |&nabla;V|/V &ge; "
                    "5&radic;(2/7) &asymp; 2.673 &gt; &radic;2, so it cannot drive "
                    "accelerated expansion (CG.11). The dark-energy value w<sub>0</sub> = "
                    "&minus;23/24 is frozen at {off_path_seed}, and w<sub>0</sub> = "
                    "&minus;1 + 1/b<sub>3</sub> has no derivation; both &minus;23/24 and "
                    "the adopted-seed value "
                ) + _w0_live() + (
                    " lie more than 3&sigma; from the DESI DR2 headline w<sub>0</sub> = "
                    "&minus;0.752 &plusmn; 0.057 (arXiv:2503.14738)."
                ),
                label="open-status"
            ),

            # ================================================================
            # 1.4 The Pneuma Field and the Two Shadows (postulates)
            # ================================================================
            ContentBlock(
                type="heading",
                content="The Pneuma Field and the Two Shadows",
                level=2,
                label="1.4"
            ),
            ContentBlock(
                type="note",
                content=(
                    "<h4>Why Go Beyond Standard Kaluza-Klein?</h4>"
                    "<p>The Kaluza-Klein framework described in Section 1.2 is elegant but incomplete. "
                    "While it proposes derivations of gauge symmetries from extra-dimensional geometry, "
                    "it faces three well-known obstacles that limit standard-KK unification:</p>"
                    "<ul class=\"concept-list\">"
                    "<li><strong>The Chirality Problem:</strong> Standard KK reduction produces vector-like "
                    "(non-chiral) fermions, but the Standard Model requires chiral fermions where left "
                    "and right components transform differently under the gauge group.</li>"
                    "<li><strong>The Moduli Problem:</strong> The size and shape of the internal manifold "
                    "K appear as massless scalar fields (moduli) that would mediate unobserved long-range "
                    "forces unless stabilized by an additional mechanism.</li>"
                    "<li><strong>The Origin Problem:</strong> Why should the internal manifold K exist "
                    "at all? What physical principle selects its topology and geometry?</li>"
                    "</ul>"
                    "<p>The <strong>Pneuma postulate</strong> is the model&rsquo;s proposed answer to "
                    "the third: the internal geometry is meant to emerge from condensates of a "
                    "fundamental fermionic field rather than sit as a fixed background. That emergence "
                    "is assumed, not computed; the internal space actually used is the one selected in "
                    "&sect;1.3.2. The first two obstacles are open problems of the adopted geometry "
                    "(&sect;1.3.6).</p>"
                ),
                label="why-pneuma"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The model postulates that the internal geometry is not a fundamental given "
                    "but emerges from the dynamics of a fundamental fermionic field, the "
                    "<strong>Pneuma field</strong> Ψ<sub>P</sub>."
                )
            ),
            ContentBlock(
                type="note",
                content=_r(
                    "<h4>The Pneuma Postulate</h4>"
                    "<p>In the 26D bulk of signature (24,2) = (12,1) + (12,1) &mdash; 24 "
                    "space directions and two times, one per shadow &mdash; the Pneuma field "
                    "&Psi;<sub>P</sub> is a <strong>4096-component Weyl spinor</strong> of "
                    "Cl(24,2). The 24 space directions pair into twelve bridges, and each "
                    "<strong>13D(12,1) shadow</strong> takes one direction from every bridge "
                    "plus its own time (12 space + 1 time), carrying an effective "
                    "64-component spinor. The internal space of each shadow is {manifold}, "
                    "{construction}; that it is formed from Pneuma condensates is the "
                    "postulate. Earlier versions described a twisted-connected-sum manifold "
                    "with four K&auml;hler-moduli sectors and a racetrack that fixed "
                    "&epsilon; &asymp; 0.2257; that construction is off-path, no racetrack "
                    "exists on {manifold}, and the racetrack values are "
                    "{calibrated_at_24}.</p>"
                ),
                label="pneuma-postulate"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The Pneuma field Ψ<sub>P</sub> transforms under Spin(24,2). On each of the "
                    "twelve bridge pairs the OR reduction operator R<sub>⊥</sub> acts as a "
                    "Möbius double cover (R<sub>⊥</sub>² = −I), and each shadow has Spin(12,1) "
                    "symmetry with a 64-component spinor representation. Bilinear condensates of "
                    "the field are proposed to generate the geometric tensors that define the "
                    "internal manifold. Whether the second time direction is free of ghost modes "
                    "and closed timelike curves has not been shown; it is an open problem "
                    "(&sect;1.3.6)."
                )
            ),
            ContentBlock(
                type="equation",
                content=(
                    "Ψ<sub>P</sub> ∈ <strong>4096</strong><sub>Spin(24,2)</sub><br/>"
                    "&nbsp;&nbsp;&nbsp;&nbsp;→ 2 × <strong>64</strong><sub>Spin(12,1)</sub><br/>"
                    "&nbsp;&nbsp;&nbsp;&nbsp;→ ⟨Ψ<sub>P</sub>Γ<sub>A...B</sub>Ψ<sub>P</sub>⟩ defines geometry"
                ),
                label="pneuma-condensate"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Any higher-dimensional theory must also face the <strong>chirality "
                    "problem</strong>. In standard Kaluza-Klein compactifications, fermions in "
                    "higher dimensions are necessarily non-chiral (vector-like), yet the "
                    "Standard Model fermions are manifestly chiral."
                )
            ),
            ContentBlock(
                type="note",
                content=(
                    "<h4>What is Chirality and Why Does It Matter?</h4>"
                    "<p><strong>Chirality</strong> refers to the distinction between left-handed and "
                    "right-handed fermions. Mathematically, a Dirac spinor ψ can be decomposed into "
                    "two Weyl spinors: ψ = ψ<sub>L</sub> + ψ<sub>R</sub>, where "
                    "ψ<sub>L,R</sub> = (1/2)(1 ∓ γ⁵)ψ.</p>"
                    "<p>The Standard Model is <em>maximally chiral</em>: the weak force (SU(2)<sub>L</sub>) "
                    "couples <strong>only to left-handed fermions</strong>. This is not a small effect—it "
                    "is the very structure of the weak interaction. For example:</p>"
                    "<ul>"
                    "<li>Left-handed electrons (e<sub>L</sub>) form doublets with neutrinos and couple to W bosons</li>"
                    "<li>Right-handed electrons (e<sub>R</sub>) are singlets and do <em>not</em> couple to W bosons</li>"
                    "<li>This asymmetry is why parity is violated in weak interactions (Wu experiment, 1956)</li>"
                    "</ul>"
                    "<p><strong>The problem:</strong> In higher dimensions (D > 4), fermions generically "
                    "come in <em>vector-like pairs</em>—for every left-handed mode, there is a right-handed "
                    "partner with identical quantum numbers. When you dimensionally reduce, you get equal "
                    "numbers of each chirality. But the Standard Model requires n<sub>L</sub> ≠ n<sub>R</sub> "
                    "for the weak sector!</p>"
                ),
                label="chirality-explanation"
            ),
            ContentBlock(
                type="list",
                items=[
                    "<strong>Orbifold projections:</strong> Discrete identifications removing half the degrees of freedom",
                    "<strong>Magnetic flux backgrounds:</strong> Index theorems yield chiral zero modes",
                    "<strong>Domain wall localization:</strong> Chiral modes bound to topological defects",
                    "<strong>Wilson line breaking:</strong> Gauge holonomy generates chiral spectrum",
                    "<strong>Conical singularities:</strong> In M-theory on G₂ manifolds, chiral fermions "
                    "live at codimension-7 conical points (Acharya and Witten, 2001)"
                ],
                label="chirality-mechanisms"
            ),
            ContentBlock(
                type="paragraph",
                content=_r(
                    "The Pneuma proposal is that &Psi;<sub>P</sub> is non-chiral in 13D but "
                    "that its condensate selects an orientation in the internal space, giving "
                    "effective chirality in the 4D reduction. That is a proposal, not a "
                    "result. {manifold} has no chiral matter of its own: its singular loci are "
                    "disjoint three-tori, so it has none of the codimension-7 points where "
                    "chiral fermions would live, and &pi;<sub>1</sub> = 1 leaves no Wilson "
                    "lines (D-011). The representation theory involved is that of Spin(12,1) "
                    "decomposed under the 4D Lorentz group times the internal symmetry group."
                )
            ),
            ContentBlock(
                type="equation",
                content=(
                    "Spin(12,1) ⊃ Spin(3,1) × Spin(8) → <strong>64</strong><br/>"
                    "&nbsp;&nbsp;&nbsp;&nbsp;= (<strong>2</strong>,<strong>8</strong><sub>s</sub>) ⊕ "
                    "(<strong>2</strong>,<strong>8</strong><sub>c</sub>) ⊕ "
                    "(<strong>2̄</strong>,<strong>8</strong><sub>v</sub>) ⊕ "
                    "(<strong>2̄</strong>,<strong>8</strong><sub>s</sub>)"
                ),
                label="spinor-decomposition"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "If such a mechanism exists, different condensate patterns would give "
                    "different 4D effective theories, and no computation yet selects one. Two "
                    "routes to chiral matter outside the internal space are recorded as "
                    "research directions (D-011), each to be pre-registered with a kill "
                    "condition before it is computed: a heterotic dual through the Kummer K3 "
                    "fibrations, and the two shadows acting as boundary walls that carry "
                    "chiral multiplets."
                )
            ),
            ContentBlock(
                type="note",
                content=(
                    "<h4>Dual-Shadow Chirality (a proposal)</h4>"
                    "<p>The dual 13D(12,1) shadows are formed from the twelve bridge pairs, and "
                    "the per-pair OR reduction operator R<sub>⊥</sub> gives a spinor double "
                    "cover, R<sub>⊥</sub>² = &minus;I per pair. The proposal is that the mirror "
                    "shadow carries fermions with opposite chirality assignments, keeping CPT "
                    "overall while each 13D(12,1) shadow violates parity maximally. It is not "
                    "derived: whether the shadow structure can host chiral matter at all is "
                    "open (&sect;1.3.6).</p>"
                ),
                label="dual-shadow-chirality"
            ),

            # ================================================================
            # 1.5 The Division-Algebra Motivation for D = 13 per Shadow
            # ================================================================
            ContentBlock(
                type="heading",
                content="The Division-Algebra Motivation for D = 13 per Shadow",
                level=2,
                label="1.5"
            ),
            ContentBlock(
                type="note",
                content=(
                    "<h4>Framework: 26D → Dual 13D(12,1) Shadows</h4>"
                    "<p>The model&rsquo;s bulk is 26-dimensional with signature (24,2) = "
                    "(12,1) + (12,1). Twelve bridge pairs supply the 24 space directions, and "
                    "each 13D(12,1) shadow takes one direction from every pair plus its own "
                    "time. Each shadow compactifies on the internal 7-manifold, with the OR "
                    "reduction operator R<sub>⊥</sub> providing cross-shadow coherence. This "
                    "subsection explains why D = 13 = 1 + 4 + 8 is the division-algebra "
                    "choice for each shadow under the assumptions stated below. It is a "
                    "motivation, not a derivation.</p>"
                ),
                label="framework-26d-dual-shadows"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "A central question for any higher-dimensional theory is: why this particular dimension? "
                    "For string theory, D = 10 emerges from worldsheet conformal anomaly cancellation. For "
                    "M-theory, D = 11 is the maximum dimension admitting supergravity. Principia "
                    "Metaphysica takes <strong>D = 26 = 24 + 2</strong> &mdash; the bulk&rsquo;s 24 "
                    "space directions and one time per shadow &mdash; as its own dimensional identity. "
                    "It is <strong>not</strong> the bosonic-string critical dimension: that claim was "
                    "withdrawn in the 2026-08-31 signature ruling, because 26 is the one-time critical "
                    "dimension and the two-time critical dimension is 27&ndash;28. The "
                    "<strong>observable shadow dimension D = 13</strong> is motivated by the mathematics "
                    "of normed division algebras."
                )
            ),
            ContentBlock(
                type="note",
                content=(
                    "<h4>The Hurwitz Theorem (1898)</h4>"
                    "<p>There exist exactly <strong>four</strong> normed division algebras over the real numbers:</p>"
                    "<ul class=\"concept-list\">"
                    "<li><strong>R</strong> (Real numbers): dimension 1 — associative, commutative, ordered</li>"
                    "<li><strong>C</strong> (Complex numbers): dimension 2 — associative, commutative</li>"
                    "<li><strong>H</strong> (Quaternions): dimension 4 — associative, non-commutative</li>"
                    "<li><strong>O</strong> (Octonions): dimension 8 — non-associative, alternative</li>"
                    "</ul>"
                    "<p style=\"margin-top: 1rem; font-style: italic;\">No other dimensions admit such "
                    "algebraic structure. The dimensions 1, 2, 4, 8 are mathematically privileged.</p>"
                ),
                label="hurwitz-theorem"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The total dimension D = 13 admits a <em>unique</em> decomposition into division "
                    "algebra dimensions that satisfies the physical requirements this model imposes:"
                )
            ),
            ContentBlock(
                type="equation",
                content=(
                    "D = 13 = 1 + 4 + 8 = dim(<strong>R</strong>) + dim(<strong>H</strong>) + "
                    "dim(<strong>O</strong>)"
                ),
                label="division-algebra-decomposition"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The model gives each component a physical interpretation: <strong>R</strong> "
                    "(dimension 1) corresponds to emergent thermal time, <strong>H</strong> "
                    "(dimension 4) to Lorentzian spacetime with Spin(3,1) ≅ SL(2,C), and "
                    "<strong>O</strong> (dimension 8) to the internal geometry: G₂ = Aut(O) acts on "
                    "the imaginary octonions Im(O) ≅ R<sup>7</sup>, the model space for the "
                    "tangent spaces of the internal 7-manifold. This is an interpretation that "
                    "motivates D = 13, not a derivation of it."
                )
            ),
            ContentBlock(
                type="note",
                content=(
                    "<h4>The Hurwitz Constraint</h4>"
                    "<p><strong>Neither 3 nor 9 is a division algebra dimension.</strong> The Hurwitz "
                    "theorem establishes that no normed division algebra exists in dimension 3 or 9 (or "
                    "any dimension other than 1, 2, 4, 8). Any decomposition using non-division-algebra "
                    "dimensions lacks the algebraic structure necessary for consistent spinor physics and "
                    "gauge theory.</p>"
                ),
                label="hurwitz-constraint"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The major candidates for fundamental theory—string theory (D = 10), M-theory (D = 11), "
                    "and now Principia Metaphysica (D = 26 full / D = 13 per shadow)—have division algebra "
                    "interpretations with crucial differences. D = 10 = 2 + 8 = <strong>C</strong> + "
                    "<strong>O</strong> (worldsheet coordinates + transverse directions, requires "
                    "supersymmetry). D = 11 = 1 + 2 + 8 = <strong>R</strong> + <strong>C</strong> + "
                    "<strong>O</strong> (mixed structure, requires supersymmetry, compactified on 7D G₂ "
                    "manifolds). D = 13 = 1 + 4 + 8 = <strong>R</strong> + <strong>H</strong> + "
                    "<strong>O</strong> (emergent thermal time, quaternionic spacetime, octonionic "
                    "internal structure, <strong>no supersymmetry assumed</strong>). D = 26 with "
                    "(24,2) = (12,1) + (12,1): twelve bridge pairs split the bulk into two 13D(12,1) "
                    "shadows, each with its own time."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "A key distinction is that D = 13 = <strong>R</strong> + <strong>H</strong> + "
                    "<strong>O</strong> excludes the complex numbers <strong>C</strong>, whereas D = 10 "
                    "and D = 11 include it. The model reads this exclusion physically: (1) No "
                    "worldsheet—the complex structure <strong>C</strong> in string theory represents the "
                    "2D worldsheet, but Principia Metaphysica has no fundamental strings. (2) Emergent "
                    "time—time is taken to emerge thermodynamically from <strong>R</strong> (real-valued "
                    "entropy), not geometrically from <strong>C</strong>. (3) Quaternionic spacetime—the "
                    "4D spacetime structure is read from <strong>H</strong>, matching the quaternionic "
                    "structure of the Lorentz group. (4) Octonionic internal structure—G₂ = Aut(O) is "
                    "the structure group of the internal 3-form on the 7-manifold."
                )
            ),
            ContentBlock(
                type="note",
                content=(
                    "<h4>Theorem (D = 13 Uniqueness)</h4>"
                    "<p>Let D be a spacetime dimension satisfying:</p>"
                    "<ol>"
                    "<li>D can be expressed as a sum of normed division algebra dimensions</li>"
                    "<li>The decomposition includes exactly one factor of dimension 1 (emergent time)</li>"
                    "<li>The decomposition includes exactly one factor of dimension 4 (Lorentz spacetime)</li>"
                    "<li>The decomposition includes exactly one factor of dimension 8 (maximal internal structure)</li>"
                    "<li>Complex structure (dimension 2) is excluded (no worldsheet)</li>"
                    "</ol>"
                    "<p>Then <strong>D = 13 = 1 + 4 + 8</strong> is the <em>unique</em> solution.</p>"
                ),
                label="uniqueness-theorem"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "This follows from the Hurwitz theorem: given the normed division algebra constraint, the only possible sum is "
                    "D = dim(<strong>R</strong>) + dim(<strong>H</strong>) + dim(<strong>O</strong>) = "
                    "1 + 4 + 8 = 13. The Hurwitz theorem limits the available normed division algebras, "
                    "and the physical requirements of this construction favour D = 13."
                )
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The number 13 also appears in exceptional mathematics: dim(F₄) = 52 = 4 × 13 "
                    "(automorphisms of J₃(O)), dim(E₆) = 78 = 6 × 13 (collineations of OP²), and "
                    "dim(J₃(O)) - dim(G₂) = 27 - 14 = 13 (Jordan algebra mod automorphisms). These "
                    "coincidences motivate the choice; they do not derive it."
                )
            ),

            # ================================================================
            # 1.6 Related Work and Outline of the Paper
            # ================================================================
            ContentBlock(
                type="heading",
                content="Related Work and Outline of the Paper",
                level=2,
                label="1.6"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "Principia Metaphysica relates observable 4D physics to the geometry of a compact "
                    "internal space and to its own postulated bulk. This projection-based approach, "
                    "where effective low-energy physics is read from geometric features of a compact "
                    "internal space, builds upon several foundational programs in theoretical physics."
                )
            ),
            ContentBlock(
                type="note",
                content=_r(
                    "<h4>Kaluza-Klein Theory (1920s)</h4>"
                    "<p>The original insight that extra compact dimensions can yield gauge "
                    "interactions from pure geometry remains the conceptual ancestor of all "
                    "modern unification programs. PM inherits this philosophy while extending "
                    "to 26D with signature (24,2) &mdash; one timelike direction per 13D(12,1) "
                    "shadow &mdash; and compactifying each shadow on the internal 7-manifold "
                    "{manifold}. Unlike classical Kaluza-Klein reduction, an M-theory "
                    "compactification on a G₂ manifold draws its gauge fields from "
                    "harmonic 2-forms and singularities rather than from isometries.</p>"
                ),
                label="kk-context"
            ),
            ContentBlock(
                type="note",
                content=_r(
                    "<h4>M-Theory on G₂ Manifolds (Acharya, Witten, et al. ~2000s&ndash;present)</h4>"
                    "<p>M-theory on a compact G₂ manifold gives four-dimensional N = 1 "
                    "physics; non-abelian gauge fields live on codimension-4 singularities and "
                    "chiral fermions at codimension-7 conical points (<strong>Acharya &amp; "
                    "Witten 2001</strong>). PM draws on this literature &mdash; Joyce&rsquo;s "
                    "construction of compact G₂ manifolds, Acharya&rsquo;s local super "
                    "Yang&ndash;Mills on Joyce orbifolds (1999), the Lukas&ndash;Morris moduli "
                    "K&auml;hler potential (2004) and the flux analysis of Acharya, Denef and "
                    "Valandro (2005) &mdash; and on <strong>Halverson &amp; Morrison "
                    "(2020)</strong> for the wider G₂ landscape. Earlier versions also used "
                    "the twisted-connected-sum construction of "
                    "<strong>Corti-Haskins-Nordstr&ouml;m-Pacini (2015)</strong> and a KKLT-style "
                    "racetrack (KKLT 2003, Blanco-Pillado et al. 2004). Both are off-path: "
                    "{manifold} is a Joyce orbifold resolution, b<sub>3</sub> = {b3} lies "
                    "outside every published TCS range, and no racetrack exists on it "
                    "(&sect;1.3.5).</p>"
                ),
                label="g2-context"
            ),
            ContentBlock(
                type="note",
                content=(
                    "<h4>Two-Time Physics (Bars 1998–2010; Pettini 2026)</h4>"
                    "<p>Itzhak Bars' program demonstrated that a physical theory in signature (d,2) with an "
                    "Sp(2,ℝ) gauge symmetry reproduces families of ordinary one-time systems as different "
                    "gauge fixings, with the gauge constraint removing ghost states. PM borrows the "
                    "<em>shape</em> of this structure: the bulk carries signature (24,2), and each "
                    "13D(12,1) shadow is treated as a one-time slice carrying its own timelike "
                    "direction — (12,1) + (12,1) = (24,2) exactly. <strong>PM does not inherit "
                    "Bars&rsquo; ghost-freedom theorem, and the appeal to it is withdrawn</strong> "
                    "(2026-08-31 signature ruling): Sp(2,ℝ) gauging removes two dimensions and "
                    "yields ONE 24D shadow of signature (23,1), not two 13D(12,1) shadows, and "
                    "Bars&rsquo; shadows are alternative gauge-fixings of the same bulk rather than "
                    "a partition of it into halves. Ghost control of the second time is an OPEN "
                    "problem here with no computed backing. The Sp(2,ℝ) constraint, where the "
                    "framework invokes it, is a STRUCTURAL assumption, not a derivation. "
                    "Recent work by <strong>Pettini (2026, arXiv:2606.12457)</strong> argues that an extra "
                    "<em>timelike</em> dimension lets spatially separated branes correlate causally through the "
                    "second time — where an extra spacelike dimension would instead permit superluminal "
                    "shortcuts — which is the mechanism PM invokes for inter-shadow correlation. This yields a "
                    "falsifiable signature: Bell-type correlations between cross-shadow pairs (SPECULATIVE; "
                    "see the falsification program). An earlier version also argued that the "
                    "Sp(2,ℝ)-invariant combination t₊ = (t₁+t₂)/√2 acts as a common clock while the "
                    "relative time t₋ = (t₁−t₂)/√2 is pure gauge; that argument needs the Sp(2,ℝ) "
                    "gauging the model does not inherit, and it is withdrawn: each shadow keeps its own "
                    "time. A literal third timelike direction would give D = 27, an odd dimension, "
                    "whose Clifford algebra admits no chiral (Weyl) spinors. The argument against it is "
                    "chirality, not criticality: the claim "
                    "&lsquo;D = 27 ≠ D<sub>crit</sub> = 26&rsquo; is <strong>withdrawn</strong>, "
                    "because 26 is the ONE-time critical dimension at (25,1) and the two-time "
                    "bosonic critical dimension is 27–28 (Bars &amp; Kounnas hep-th/9705205). "
                    "26 = 24 + 2 &mdash; the bulk&rsquo;s 24 space directions and one time per "
                    "shadow &mdash; is retained as the framework&rsquo;s own dimensional identity "
                    "and not as a criticality result.</p>"
                ),
                label="historical-two-time-context"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "The general strategy of projecting or embedding 4D observer physics within a larger "
                    "geometric structure also shares broad conceptual parallels with other speculative "
                    "unification frameworks: String Theory Landscape &amp; Flux Compactifications "
                    "(discretuum of vacua), F-Theory GUTs (Vafa et al., elliptically fibered geometries "
                    "yielding grand unification with geometric origins for Yukawas), Braneworld Scenarios "
                    "(Randall-Sundrum warped extra dimensions), and Geometric Unity (Weinstein 2021, "
                    "observerse construction with 14D manifold)."
                )
            ),
            ContentBlock(
                type="note",
                content=_r(
                    "<h4>PM&rsquo;s Own Contributions</h4>"
                    "<p>Beside these debts, the model&rsquo;s own results are computations with "
                    "tests, and its own assumptions are labelled as such:</p>"
                    "<ul>"
                    "<li><strong>The closed-geometry certificate</strong> CG.1&ndash;CG.11 "
                    "(Section 2.4): the topology and gauge content of {manifold} and two "
                    "leading-order no-go results, for moduli and for dark energy</li>"
                    "<li><strong>The reachable set</strong> of Joyce&rsquo;s construction from "
                    "&phi;&rsquo;s (&#8484;/2)<sup>3</sup>, and the ladder of fundamental groups "
                    "across the family</li>"
                    "<li><strong>The bridge&ndash;component correspondence</strong> that, with "
                    "WA-1, selects {betti_pair} without data</li>"
                    "<li><strong>The K3 reading</strong> of &chi;<sub>eff</sub> (48n)</li>"
                    "<li><strong>Thermal time</strong>: the thermal-time hypothesis applied to the "
                    "Pneuma field (a postulate)</li>"
                    "<li><Speculation><strong>Pneuma-microtubule coupling</strong> inspired by "
                    "Orch-OR quantum biology (speculative appendix)</Speculation></li>"
                    "</ul>"
                    "<p>Flavour textures, mixing angles and cosmological ratios computed elsewhere "
                    "in the paper are model constructs or fits until a chiral sector exists; each "
                    "is labelled where it appears.</p>"
                ),
                label="pm-contributions"
            ),
            ContentBlock(
                type="paragraph",
                content=(
                    "<strong>Outline.</strong> The subsection that follows, "
                    "<em>Foundations of Dimensional Descent</em>, sets out the bulk, the "
                    "bridges and the shadows. "
                    "<strong>Section 2 (Geometric Framework)</strong> develops the master action and "
                    "the spectral decomposition, publishes the closed-geometry certificate in "
                    "&sect;2.4 together with the full table of standard results, postulates, "
                    "findings, corrections and open problems, and states the methodology in "
                    "&sect;2.6. <strong>Section 3</strong> treats the gauge sector and the "
                    "cosmological comparisons (&sect;3.7). <strong>Section 4</strong> covers "
                    "chirality, generations, flavour and the Higgs sector &mdash; where chirality "
                    "and flavour are open and many values are fits &mdash; and the integrity checks "
                    "of the validation layer. <strong>Section 5</strong> treats cosmology and dark "
                    "energy, which is open. <strong>Section 6</strong> lists the falsifiable "
                    "predictions with their status, and <strong>Section 7</strong> discusses the "
                    "results. The appendices provide the spectral registry, the algebraic "
                    "foundations, the statistical logs and the validation certificates."
                ),
                label="outline"
            ),
            ContentBlock(
                type="table",
                content=_r(
                    "<h4>Inputs and Their Status</h4>"
                    "<table style='width:100%; border-collapse:collapse; margin:1rem 0;'>"
                    "<tr style='border-bottom:2px solid #555;'>"
                    "<th style='text-align:left; padding:0.5rem;'>Input</th>"
                    "<th style='text-align:left; padding:0.5rem;'>Value</th>"
                    "<th style='text-align:left; padding:0.5rem;'>Status</th>"
                    "<th style='text-align:left; padding:0.5rem;'>Role</th></tr>"
                    "<tr style='border-bottom:1px solid #333;'>"
                    "<td style='padding:0.5rem;'>(b<sub>2</sub>, b<sub>3</sub>)</td>"
                    "<td style='padding:0.5rem;'>({b2}, {b3})</td>"
                    "<td style='padding:0.5rem;'><strong>DERIVED</strong></td>"
                    "<td style='padding:0.5rem;'>Betti numbers of {manifold} from Joyce&rsquo;s "
                    "construction (CG.1); the member selected by &pi;<sub>1</sub> and WA-1 "
                    "(&sect;1.3.2)</td></tr>"
                    "<tr style='border-bottom:1px solid #333;'>"
                    "<td style='padding:0.5rem;'>n<sub>gen</sub></td>"
                    "<td style='padding:0.5rem;'>{n_gen}</td>"
                    "<td style='padding:0.5rem;'><strong>DERIVED</strong></td>"
                    "<td style='padding:0.5rem;'>b<sub>2</sub>/4, the number of singular "
                    "involutions; tested against the observed generations</td></tr>"
                    "<tr style='border-bottom:1px solid #333;'>"
                    "<td style='padding:0.5rem;'>&chi;<sub>eff</sub></td>"
                    "<td style='padding:0.5rem;'>" + str(chi_eff_total) + "</td>"
                    "<td style='padding:0.5rem;'><strong>DERIVED</strong> (K3 reading, D-015)</td>"
                    "<td style='padding:0.5rem;'>48n, an effective index; not &chi;(Y<sub>7</sub>) "
                    "= 0</td></tr>"
                    "<tr style='border-bottom:1px solid #333;'>"
                    "<td style='padding:0.5rem;'>VEV coefficient</td>"
                    "<td style='padding:0.5rem;'><span class=\"pm-value\" "
                    "data-pm-value=\"abstract.vev_coefficient\">1.5859</span></td>"
                    "<td style='padding:0.5rem;'>CALIBRATED</td>"
                    "<td style='padding:0.5rem;'>Electroweak scale anchor</td></tr>"
                    "<tr style='border-bottom:1px solid #333;'>"
                    "<td style='padding:0.5rem;'>&alpha;<sub>GUT</sub> coefficient</td>"
                    "<td style='padding:0.5rem;'><span class=\"pm-value\" "
                    "data-pm-value=\"abstract.alpha_gut_coefficient\">0.031831</span></td>"
                    "<td style='padding:0.5rem;'>CALIBRATED</td>"
                    "<td style='padding:0.5rem;'>Unification scale anchor</td></tr>"
                    "<tr style='border-bottom:1px solid #333;'>"
                    "<td style='padding:0.5rem;'>Re(T)</td>"
                    "<td style='padding:0.5rem;'>not fixed</td>"
                    "<td style='padding:0.5rem;'><strong>OPEN</strong> (D-015)</td>"
                    "<td style='padding:0.5rem;'>K&auml;hler modulus; no leading-order mechanism on "
                    "{manifold} fixes it (CG.6). The values used elsewhere &mdash; "
                    "<span class=\"pm-value\" data-pm-value=\"moduli.re_t_phenomenological\">9.865</span> "
                    "from the Higgs-mass inversion and "
                    "<span class=\"pm-value\" data-pm-value=\"cosmology.racetrack_Re_T\">7.086</span>, "
                    "{calibrated_at_24} &mdash; are calibrations, and results computed with them "
                    "are CALIBRATED</td></tr>"
                    "</table>"
                    "<p>The compression ratios quoted by earlier versions counted fitted constants "
                    "as derived and are not used here.</p>"
                ),
                label="seed-hierarchy-table"
            ),
        ]

        return SectionContent(
            section_id="1",
            subsection_id=None,
            title="Introduction",
            abstract=_r(
                "The pursuit of a unified description of the fundamental forces runs from "
                "Maxwell&rsquo;s unification of electricity and magnetism through grand "
                "unification to Kaluza-Klein theory and M-theory on G₂ manifolds. This "
                "section follows that arc and then tells the model&rsquo;s own story top down: "
                "the standard physics it uses; how its internal space {manifold} &mdash; "
                "{construction}, with {betti_pair} &mdash; is selected without fitting; its "
                "postulates (a 26D bulk of signature (24,2) with one time per 13D(12,1) shadow, "
                "and twelve bridges); what its computations establish (CG.1&ndash;CG.11); what "
                "was corrected; and what remains open &mdash; chirality, moduli stabilisation, "
                "dark energy and flavour."
            ),
            content_blocks=content_blocks,
            formula_refs=[],
            param_refs=[
                "D_bulk",
                "D_shadow",
                "D_bridge",
                "D_observable",
                "D_G2",
                "D_spin8",
                "wa_PM_effective",
                "w0_PM",
                "alpha_GUT_inv",
                "higgs_mass.m_h_GeV",
                "proton_lifetime.tau_p_years",
                "vev_pneuma.v_EW",
            ]
        )

    def get_formulas(self) -> List[Formula]:
        """Return key framework formula for the introduction."""
        return [
            Formula(
                id="intro-division-algebra-decomposition",
                label="(1.4)",
                latex=r"D = 13 = 1 + 4 + 8 = \dim(\mathbb{R}) + \dim(\mathbb{H}) + \dim(\mathbb{O})",
                plain_text="D = 13 = 1 + 4 + 8 = dim(R) + dim(H) + dim(O)",
                category="DERIVED",
                description=(
                    "The shadow dimension D=13 admits a unique decomposition into normed division "
                    "algebra components, as classified by the Hurwitz theorem (1898), once the model's "
                    "physical roles are assigned: real R (dim 1, read as emergent thermal time from KMS "
                    "modular flow), quaternionic H (dim 4, read as Lorentz spacetime with Spin(3,1) "
                    "isomorphic to SL(2,C)), and octonionic O (dim 8, read as the internal structure: "
                    "Aut(O) = G2 acts on Im(O) = R^7, the model space of the internal 7-manifold). The "
                    "decomposition 13 = 1 + 4 + 8 is the unique partition of 13 into Hurwitz dimensions "
                    "that assigns exactly one factor to each of these roles, with the exclusion of dim 2 "
                    "(complex numbers) reflecting the absence of a fundamental worldsheet degree of "
                    "freedom in the observable sector. The roles are the model's postulates; the "
                    "arithmetic is the theorem."
                ),
                eml_tree_str="ops.add(eml_scalar(1.0), ops.add(eml_scalar(4.0), eml_scalar(8.0)))",
                eml_latex=r"D = \mathrm{ops.add}(\mathrm{eml\_scalar}(1),\; \mathrm{ops.add}(\mathrm{eml\_scalar}(4),\; \mathrm{eml\_scalar}(8)))",
                eml_description="EML: D = ops.add(dim_R=1, ops.add(dim_H=4, dim_O=8)) — Hurwitz decomposition of shadow dimension into division algebra factors",
                input_params=[
                    "dimensions.D_bulk",
                    "topology.elder_kads",
                ],
                output_params=[
                    "geometry.D_shadow",
                ],
                derivation={
                    "steps": [
                        {"description": "Hurwitz theorem: only 4 normed division algebras exist over R with dimensions 1, 2, 4, 8", "formula": r"\mathbb{R}(1),\; \mathbb{C}(2),\; \mathbb{H}(4),\; \mathbb{O}(8)"},
                        {"description": "Physical constraints: exactly one factor each of dim 1 (time), dim 4 (spacetime), dim 8 (internal); exclude dim 2 (no worldsheet)", "formula": r"D = \dim(\mathbb{R}) + \dim(\mathbb{H}) + \dim(\mathbb{O})"},
                        {"description": "Unique solution yields D=13 per shadow, with Aut(O) = G2 governing internal geometry", "formula": r"D = 1 + 4 + 8 = 13, \quad \text{Aut}(\mathbb{O}) = G_2"},
                    ],
                    "method": "hurwitz_classification",
                    "parentFormulas": []
                },
                terms={
                    "D": "Total dimension of each observable shadow sector (13)",
                    "R": "Real numbers, dimension 1 (emergent thermal time)",
                    "H": "Quaternions, dimension 4 (Lorentzian spacetime with Spin(3,1))",
                    "O": "Octonions, dimension 8 (internal manifold with Aut(O) = G2)",
                    "Aut(O)": "Automorphism group of octonions, isomorphic to G2",
                }, 
            arithma=_arithma_add(_arithma_num(1.0), _arithma_add(_arithma_num(4.0), _arithma_num(8.0))), eml=_eml_add(_eml_scalar(1.0), _eml_add(_eml_scalar(4.0), _eml_scalar(8.0))), value=13.0)
        ]

    def get_output_param_definitions(self) -> List[Parameter]:
        """No output parameters in introduction section — narrative section."""
        return [
            Parameter(
                path="introduction.subsection_count",
                name="Introduction Subsection Count",
                no_experimental_value=True,
                units="sections",
                description="Number of subsections in the introduction (1.1 through 1.6)",
                status="SYSTEM",
                eml_description="EML: eml_scalar(6) — count of introduction subsections (1.1 through 1.6)"
            )
        ]

    def get_references(self) -> List[Dict[str, str]]:
        """Return historical references for introduction."""
        return [
            {
                "id": "maxwell_1865",
                "authors": "Maxwell, J. C.",
                "title": "A Dynamical Theory of the Electromagnetic Field",
                "journal": "Phil. Trans. R. Soc. Lond.",
                "volume": "155",
                "year": "1865",
                "url": "https://doi.org/10.1098/rstl.1865.0008"
            },
            {
                "id": "glashow_1961",
                "authors": "Glashow, S. L.",
                "title": "Partial Symmetries of Weak Interactions",
                "journal": "Nucl. Phys.",
                "volume": "22",
                "year": "1961",
                "url": "https://doi.org/10.1016/0029-5582(61)90469-2"
            },
            {
                "id": "weinberg1967",
                "authors": "Weinberg, S.",
                "title": "A Model of Leptons",
                "year": 1967,
                "journal": "Phys. Rev. Lett.",
                "volume": "19",
                "pages": "1264-1266",
                "doi": "10.1103/PhysRevLett.19.1264",
                "url": "https://doi.org/10.1103/PhysRevLett.19.1264",
            },
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
        ]


    # -------------------------------------------------------------------------
    # SSOT enrichment methods
    # -------------------------------------------------------------------------

    def get_certificates(self) -> List[Dict[str, Any]]:
        """Return certificate assertions verifying introduction section integrity."""
        section = self.get_section_content()
        blocks = section.content_blocks if section else []
        paragraph_blocks = [b for b in blocks if b.type == "paragraph"]
        total_text = " ".join(b.content for b in paragraph_blocks)
        word_count = len(total_text.split())
        heading_blocks = [b for b in blocks if b.type == "heading"]
        has_key_concepts = all(
            term in total_text
            for term in ["Maxwell", "Kaluza-Klein", "Pneuma", "division algebra", "G\u2082"]
        )

        return [
            {
                "id": "CERT_INTRO_WORD_COUNT",
                "assertion": "Introduction contains at least 500 words of substantive content",
                "condition": f"word_count >= 500 (actual: {word_count})",
                "tolerance": 500,
                "status": "PASS" if word_count >= 500 else "FAIL",
                "wolfram_query": "N/A (content integrity check)",
                "wolfram_result": "N/A",
                "sector": "paper"
            },
            {
                "id": "CERT_INTRO_KEY_CONCEPTS",
                "assertion": "Introduction covers Maxwell, Kaluza-Klein, Pneuma, division algebras, and G2",
                "condition": f"all key concepts present: {has_key_concepts}",
                "tolerance": "exact",
                "status": "PASS" if has_key_concepts else "FAIL",
                "wolfram_query": "N/A (content integrity check)",
                "wolfram_result": "N/A",
                "sector": "paper"
            },
            {
                "id": "CERT_INTRO_SUBSECTIONS",
                "assertion": "Introduction has at least 5 subsection headings",
                "condition": f"heading_count >= 5 (actual: {len(heading_blocks)})",
                "tolerance": 5,
                "status": "PASS" if len(heading_blocks) >= 5 else "FAIL",
                "wolfram_query": "N/A (structural check)",
                "wolfram_result": "N/A",
                "sector": "paper"
            },
        ]

    def get_learning_materials(self) -> List[Dict[str, Any]]:
        """Return educational resources about concepts introduced in the introduction."""
        return [
            {
                "topic": "Electroweak unification",
                "url": "https://en.wikipedia.org/wiki/Electroweak_interaction",
                "relevance": "Section 1.1 traces unification history from Maxwell through Glashow-Weinberg-Salam electroweak theory",
                "validation_hint": "Electroweak theory unifies EM and weak force at ~246 GeV (SU(2)_L x U(1)_Y)"
            },
            {
                "topic": "Kaluza-Klein theory",
                "url": "https://en.wikipedia.org/wiki/Kaluza%E2%80%93Klein_theory",
                "relevance": "Section 1.2 describes geometrization of forces via extra dimensions; PM extends this to a 26D bulk whose two 13D shadows each compactify on a 7-manifold",
                "validation_hint": "5D KK yields gravity + U(1); in M-theory on a compact G2 manifold the abelian gauge fields come from harmonic 2-forms rather than isometries"
            },
            {
                "topic": "Normed division algebras and the Hurwitz theorem",
                "url": "https://en.wikipedia.org/wiki/Hurwitz%27s_theorem_(composition_algebras)",
                "relevance": "Section 1.5 motivates D=13 per shadow from division algebra dimensions 1+4+8 (R+H+O), unique under the roles the model assigns",
                "validation_hint": "Only 4 normed division algebras exist: R(1), C(2), H(4), O(8) by Hurwitz 1898"
            },
            {
                "topic": "G2 manifolds and M-theory compactification",
                "url": "https://en.wikipedia.org/wiki/G2_manifold",
                "relevance": "Section 1.3 starts from M-theory on a compact 7-manifold with a torsion-free G2-structure; the internal space Y_7 is Joyce's resolution of T^7/(Z/2)^3",
                "validation_hint": "A smooth G2 compactification gives 4D N=1 with b_2 vector and b_3 chiral multiplets; chiral fermions need codimension-7 conical points, which Y_7 lacks (chirality is open)"
            },
        ]

    def validate_self(self) -> Dict[str, Any]:
        """Validate introduction section integrity."""
        checks = []
        section = self.get_section_content()
        blocks = section.content_blocks if section else []
        paragraph_blocks = [b for b in blocks if b.type == "paragraph"]
        total_text = " ".join(b.content for b in paragraph_blocks)
        word_count = len(total_text.split())

        wc_ok = word_count >= 500
        checks.append({
            "name": "Introduction word count meets minimum (>=500)",
            "passed": wc_ok,
            "confidence_interval": {
                "lower": 500,
                "upper": 10000,
                "sigma": 0.0
            },
            "log_level": "INFO" if wc_ok else "ERROR",
            "message": f"Word count = {word_count} (minimum 500)"
        })

        foundations = self.get_foundations()
        f_ok = len(foundations) >= 6
        checks.append({
            "name": "At least 6 foundational principles defined",
            "passed": f_ok,
            "confidence_interval": {
                "lower": 6,
                "upper": 20,
                "sigma": 0.0
            },
            "log_level": "INFO" if f_ok else "ERROR",
            "message": f"Foundation principles = {len(foundations)} (minimum 6)"
        })

        refs = self.get_references()
        r_ok = len(refs) >= 3
        checks.append({
            "name": "At least 3 references provided",
            "passed": r_ok,
            "confidence_interval": {
                "lower": 3,
                "upper": 50,
                "sigma": 0.0
            },
            "log_level": "INFO" if r_ok else "ERROR",
            "message": f"References = {len(refs)} (minimum 3)"
        })

        return {
            "passed": all(c["passed"] for c in checks),
            "checks": checks
        }

    def get_gate_checks(self) -> List[Dict[str, Any]]:
        """Return gate check results for introduction section."""
        section = self.get_section_content()
        blocks = section.content_blocks if section else []
        paragraph_blocks = [b for b in blocks if b.type == "paragraph"]
        total_text = " ".join(b.content for b in paragraph_blocks)
        word_count = len(total_text.split())
        passed = word_count >= 500

        return [
            {
                "gate_id": "G_INTRO_CONTENT_INTEGRITY",
                "simulation_id": self.metadata.id,
                "assertion": "Introduction section provides comprehensive framework overview with historical context (>=500 words)",
                "result": "PASS" if passed else "FAIL",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "word_count": word_count,
                    "content_blocks": len(blocks),
                    "foundations_count": len(self.get_foundations()),
                    "references_count": len(self.get_references()),
                    "section_type": "narrative_introduction"
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
    sim = IntroductionV16()

    print("=" * 70)
    print(f" {sim.metadata.title}")
    print("=" * 70)
    print()

    # Generate section content
    section_content = sim.get_section_content()

    print(f"Section: {section_content.section_id}")
    print(f"Title: {section_content.title}")
    print(f"Abstract: {section_content.abstract[:100]}...")
    print(f"Content blocks: {len(section_content.content_blocks)}")
    print()


if __name__ == "__main__":
    main()
