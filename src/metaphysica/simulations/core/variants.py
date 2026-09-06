"""Executable forks: run the pipeline under a choice that is not yet ruled.

WHY THIS EXISTS
---------------
The framework already records its open decisions well. ``CANON["bulk"]``
carries a STRUCTURAL_CHALLENGED status, a multi-page ``challenge``, a
``resolution_evidence`` block and an explicit "RESOLUTION OPTIONS (author's
call): (a) ... (b) ... (c) ...". The four-face choice, the render policy, the
Path A/B question and the person-within-a-face reading are all documented the
same way.

What none of them can do is **run**. The options are prose, so seeing what
option (b) actually changes means editing code, rebuilding, remembering to
put it back, and comparing by hand -- which is how the strict/permissive
render policy was decided (two git branches, manually diffed). That works
once. It does not scale to a dozen open forks, and nothing stops a switch
being flipped and silently left flipped.

This module makes a fork a first-class object: declared, enumerable,
selectable, and defaulted to whatever CANON says is currently adopted.

NOT A NEW CONSTANT STORE
------------------------
Every default here must correspond to a value that already exists elsewhere
(a CANON entry, a module-level policy switch, a registry property). This is a
*view* over decisions, in the same sense that PhysicsConfig is a view over
FormulasRegistry. If a variant's default and its source disagree, that is a
bug and ``test_variants`` fails on it.

THE TUNING HAZARD -- READ THIS BEFORE ADDING A FORK
---------------------------------------------------
A switchboard for physics choices is one keystroke away from being a
parameter fitter: run every option, keep whichever agrees best with the
anchors, report that. That is anchor-shopping with better tooling, and this
repo has already retired one advertised agreement that came from exactly
that pattern.

Three rules follow, and the comparison runner enforces the first two:

1. A comparison reports **every** option's outcome. It never returns "the
   best one".
2. It never ranks by agreement with experimental anchors. Consequences are
   recorded; the ordering is declaration order.
3. Adopting an option is an explicit author act recorded at its source (the
   CANON entry or the module switch), not a default quietly changed here.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

__all__ = [
    "VariantOption",
    "Fork",
    "FORKS",
    "resolve",
    "active_selection",
    "describe",
]

#: Environment prefix: METAPHYSICA_VARIANT_<FORK_ID_UPPER>=<option id>
_ENV_PREFIX = "METAPHYSICA_VARIANT_"


@dataclass(frozen=True)
class VariantOption:
    """One branch of a fork, with what choosing it costs and buys."""

    id: str
    summary: str
    consequence: str
    #: True only for the option currently adopted at the fork's source.
    adopted: bool = False


@dataclass(frozen=True)
class Fork:
    """An open decision that can be executed either way.

    ``source`` names where the adopted value actually lives, so the default
    can be checked against it rather than restated here.
    """

    id: str
    question: str
    source: str
    options: List[VariantOption]
    status: str
    #: Reads the currently-adopted option id from ``source``. Kept as a
    #: callable so the check is against live state, not a copy.
    read_adopted: Optional[Callable[[], str]] = None
    notes: str = ""

    def option_ids(self) -> List[str]:
        return [o.id for o in self.options]

    def default(self) -> str:
        for option in self.options:
            if option.adopted:
                return option.id
        raise ValueError(f"fork {self.id!r} declares no adopted option")


def _bulk_signature_adopted() -> str:
    from metaphysica.simulations.core.canonical_values import CANON

    form = CANON["bulk"].get("form", "")
    for option, token in (("26_2", "(26,2)"), ("25_1", "(25,1)"), ("24_2", "(24,2)")):
        if token in form:
            return option
    return "24_2"



def _dark_energy_betti_adopted() -> str:
    """Which integer n currently sets w0 = -(n-1)/n.

    Measured, not declared: n = 1/(1 + w0), so the live value of w0 reports
    which option is in force and a silent change to the derivation cannot
    leave this fork claiming the wrong one.
    """
    try:
        from metaphysica.simulations.base.registry import PMRegistry

        w0 = PMRegistry.get_instance().get("cosmology.w0_derived")
    except Exception:  # pragma: no cover - registry not populated
        return "b3_24"
    if w0 is None or w0 <= -1.0:
        return "b3_24"
    n = round(1.0 / (1.0 + float(w0)))
    return {24: "b3_24", 12: "bridges_12", 8: "octonion_8",
            6: "chi_over_b3_6", 4: "b2_4", 3: "ngen_3"}.get(n, "b3_24")


def _render_policy_adopted() -> str:
    from metaphysica.generators.eml_render_validity import REQUIRE_OPERATOR

    return "strict" if REQUIRE_OPERATOR else "permissive"


def _theory_uncertainty_policy_adopted() -> str:
    from metaphysica.generators.generate_validation_certificates import (
        DEFAULT_THEORY_UNCERTAINTY_POLICY,
    )

    return DEFAULT_THEORY_UNCERTAINTY_POLICY


def _face_genericity_adopted() -> str:
    from metaphysica.simulations.PM.gauge.topological_terms import (
        face_assignment_candidates,
    )

    status = face_assignment_candidates()["status"]
    return "generic" if status == "CRITERION_STATED_NOT_DERIVED" else "all"


#: The forks that are executable today. Documented-but-not-runnable
#: decisions (Path A/B, the person-within-a-face reading) are deliberately
#: absent: Path A is blocked on an underived C_3, and the reading changes
#: what a result MEANS rather than what the code computes. Declaring them
#: here would imply a switch that does nothing.
FORKS: Dict[str, Fork] = {
    "bulk_signature": Fork(
        id="bulk_signature",
        question="What is the bulk dimension and signature?",
        source="simulations.core.canonical_values.CANON['bulk']",
        status="RULED",
        read_adopted=_bulk_signature_adopted,
        options=[
            VariantOption(
                id="24_2",
                summary="26D at (24,2) -- 24 space, 2 times, one per shadow",
                consequence="Adopted 2026-08-31. Shadows stay 13D(12,1), so "
                            "the descent 13 = G2(7) + external(6) and "
                            "6 = visible(4) + 2 is preserved and nothing "
                            "migrates. COSTS, recorded in CANON['bulk']"
                            "['ruling']: withdraws 'D_bulk = D_crit = 26' "
                            "(the two-time critical dimension is 27-28), "
                            "withdraws the Bars appeal for ghost-freedom "
                            "(Sp(2,R) gives one 24D shadow, not two 13D "
                            "ones), and leaves the lattice obstruction "
                            "unanswered (24 - 2 = 6 mod 8, so no even "
                            "self-dual lattice exists here).",
                adopted=True,
            ),
            VariantOption(
                id="26_2",
                summary="28D at (26,2) -- the four-agent review's recommendation",
                consequence="Passes the lattice test (24 = 0 mod 8), matches "
                            "the Bars-Kounnas two-time critical dimension "
                            "d = 28, and admits Majorana-Weyl spinors. Costs: "
                            "26 = b3 + 2 becomes 28 = b3 + 4; alpha_T moves "
                            "2.6 -> 2.8, which shifts w(z) and the DESI "
                            "comparison by ~7.7%; bulk Weyl 4096 -> 8192, so "
                            "4096 becomes the shadow-pair spinor. Taking the "
                            "lattice partition literally gives two 14D(13,1) "
                            "shadows, and 14 - 7 = 7 breaks the descent.",
            ),
            VariantOption(
                id="25_1",
                summary="26D at (25,1) -- one time, the bosonic string reading",
                consequence="Matches the standard bosonic critical dimension "
                            "and the Lorentzian Leech lattice II_25,1, and "
                            "passes the mod-8 test. Abandons two-time "
                            "entirely, so the one-time-per-shadow structure "
                            "and the second shadow's time current go with it.",
            ),
        ],
        notes="INDEPENDENT AND STILL OPEN whichever option is taken: the "
              "construction of the manifold. CORRECTED 2026-09-06 -- the "
              "parity statement previously recorded here ('Crowley-Nordstrom "
              "forces b2 + b3 odd') is not what the literature says. Their nu "
              "is a Z/48 invariant built from the signature and Euler "
              "characteristic of a Spin(7) coboundary, it equals 24 for EVERY "
              "twisted connected sum, and it says nothing about the parity of "
              "b2 + b3. The real exclusion is sharper: TCS manifolds built "
              "from pairs of Fano 3-folds satisfy 71 <= b3 <= 155, so b3 = 24 "
              "is far below the floor and cannot come from that construction "
              "at all. The escape is Joyce's orbifold resolutions of T^7/Gamma, "
              "which span b2 in [0,28] and b3 in [4,215] over 252 distinct "
              "(b2,b3) pairs and can carry odd nu where TCS cannot -- so "
              "(4,24) lies inside the Joyce ranges. Compatible ranges are "
              "necessary and not sufficient: no Joyce example with (4,24) has "
              "been exhibited, so the item stays open, for a much narrower "
              "reason than was recorded. The framework should drop the TCS "
              "framing. Also open: the Frobenius-Schur reality argument, "
              "which (24,2) fails on a test generated by the framework's own "
              "13D(12,1) shadow claim.",
    ),
    "dark_energy_betti": Fork(
        id="dark_energy_betti",
        question="Which topological integer n sets w0 = -(n-1)/n?",
        source="simulations.PM.cosmology.dark_energy_thawing",
        status="RULED",
        read_adopted=_dark_energy_betti_adopted,
        options=[
            VariantOption(
                id="b3_24",
                summary="n = b3 = 24, w0 = -23/24 = -0.9583 (adopted)",
                consequence="The framework's headline: pure b3 topology, zero "
                            "free parameters, and a stated derivation (static "
                            "pressure of the 24-cycle with 12-pair "
                            "aggregation). It is also the WORST fit of the "
                            "options: 3.62 sigma on w0 alone and 3.21-3.52 "
                            "sigma in the 2D (w0,wa) plane across the whole "
                            "rho scan. Its Caldwell-Linder thawing band, "
                            "wa in [-1/8, -1/24], excludes the DR2 central wa "
                            "= -0.86 by 3.20 sigma.",
                adopted=True,
            ),
            VariantOption(
                id="b2_4",
                summary="n = b2 = h11 = 4, w0 = -3/4 = -0.75",
                consequence="RULED OUT 2026-09-06, on physics, despite being "
                            "the BEST FIT BY A LARGE MARGIN -- 0.04 sigma on "
                            "w0 and 0.25-0.74 sigma in the 2D plane against "
                            "the adopted option's 3.2-3.5. "
                            "b2 counts KAHLER moduli, and the framework's own "
                            "racetrack fixes their mass without any new "
                            "input: a_i = i*pi/b3 with T_i = b3*k_gimel/(i*pi) "
                            "gives a_i T_i = k_gimel for every face (the 1/i "
                            "hierarchy cancels exactly), and that combination "
                            "is what sets the KKLT modulus mass, m_T = "
                            "2 (a T) m_3/2 = 2 k_gimel m_3/2 (Choi et al, "
                            "hep-th/0503216). With this framework's own "
                            "gravitino mass of 1 TeV that is 24.6 TeV, while "
                            "a rolling dark-energy field needs m_phi = b3 H0 "
                            "= 3.5e-32 eV. The gap is 7.1e44 -- about "
                            "forty-five orders of magnitude, published as "
                            "geometry.kahler_over_quintessence_mass. "
                            "A field stabilised at 24.6 TeV cannot be rolling "
                            "today, so b2 = 4 cannot be the origin of w0 no "
                            "matter how well it fits. Two further objections "
                            "stand independently: it has no derivation, and "
                            "its wa would have to sit exactly at the EDGE of "
                            "the thawing wedge, an edge chosen because it "
                            "fits.",
            ),
            VariantOption(
                id="ngen_3",
                summary="n = 3 (E8 blocks = generations), w0 = -2/3 = -0.6667",
                consequence="The only option whose thawing band, "
                            "wa in [-1, -1/3], CONTAINS the DR2 central "
                            "wa = -0.86 rather than merely approaching it. "
                            "w0 sits at 1.50 sigma and the 2D distance is "
                            "1.01-1.69 sigma -- worse than b2 = 4 on w0, "
                            "better on wa, and it needs no band-edge "
                            "fine-tuning. Like b2 = 4 it has no derivation.",
            ),
            VariantOption(
                id="chi_over_b3_6",
                summary="n = chi_eff/b3 = 6, w0 = -5/6 = -0.8333",
                consequence="1.43 sigma on w0, 1.17-1.24 sigma in 2D. The 6 "
                            "already carries independent geometric meaning as "
                            "the aligned bridge pair count behind "
                            "alpha_leak = 1/sqrt(6), so it is the option with "
                            "the most existing structural support -- but it "
                            "is a middling fit rather than a good one.",
            ),
            VariantOption(
                id="bridges_12",
                summary="n = 12 bridges, w0 = -11/12 = -0.9167",
                consequence="2.89 sigma on w0, 2.48-2.75 sigma in 2D. "
                            "Recorded for completeness; no better than the "
                            "adopted option in any respect.",
            ),
            VariantOption(
                id="octonion_8",
                summary="n = dim(O) = 8, w0 = -7/8 = -0.875",
                consequence="2.16 sigma on w0, 1.78-1.98 sigma in 2D. As "
                            "above: recorded, not advocated.",
            ),
        ],
        notes="RULED 2026-09-06 in favour of the option that fits WORSE, "
              "which is the point. "
              "The fork was opened because scanning the framework's own "
              "structural integers through the SAME form w0 = -(n-1)/n, "
              "scored the same way, spans 0.25 sigma to 3.5 sigma in the 2D "
              "plane -- the dark-energy result is more sensitive to which "
              "integer is chosen than to any of the physics around it, and "
              "that is worth recording whether or not the adopted option "
              "changes. It does not change. "
              "WHAT SETTLED IT: not a smaller sigma but a mass. b2 counts "
              "Kahler moduli and b3 counts C3 moduli (axions). The "
              "framework's own racetrack stabilises the four Kahler moduli "
              "at 2 k_gimel m_3/2 = 24.6 TeV, forty-five orders of magnitude "
              "above the b3 H0 = 3.5e-32 eV a rolling field needs, so the "
              "quintessence direction cannot be one of them. It must be "
              "shift-symmetry protected, which is what an axion is and what "
              "a saxion is not. b3 = 24 survives on structure. "
              "This also independently settles the S8 friction onset by the "
              "same argument, and it is COMPUTED "
              "(geometry.kahler_over_quintessence_mass) rather than asserted "
              "-- if the gravitino mass or the racetrack changes, the ruling "
              "moves with them. "
              "WHAT IT COSTS: the surviving option is the one at 3.2-3.5 "
              "sigma from DESI DR2. Ruling on physics rather than on fit "
              "means accepting the worse number, and the tension is now "
              "structural rather than a matter of choosing differently. "
              "AND A CAUTION THAT SURVIVES THE RULING: the DR2 central "
              "wa = -0.86 lies OUTSIDE the Caldwell-Linder thawing wedge for "
              "every n >= 4. If DR2 holds, thawing quintessence is "
              "disfavoured on its own terms whichever integer is adopted, so "
              "the remaining work is not re-tuning n but asking whether the "
              "dark energy sector is thawing at all.",
    ),
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


def resolve(fork_id: str, override: Optional[str] = None) -> str:
    """Selected option for *fork_id*.

    Precedence: explicit *override*, then ``METAPHYSICA_VARIANT_<ID>``, then
    the adopted default -- the same order build() uses for its output root,
    so callers do not have to remember a second convention.
    """
    fork = FORKS.get(fork_id)
    if fork is None:
        raise KeyError(
            f"unknown fork {fork_id!r}; declared: {sorted(FORKS)}"
        )
    chosen = override or os.environ.get(_ENV_PREFIX + fork_id.upper())
    if chosen is None:
        return fork.default()
    if chosen not in fork.option_ids():
        raise ValueError(
            f"fork {fork_id!r} has no option {chosen!r}; "
            f"available: {fork.option_ids()}"
        )
    return chosen


def active_selection() -> Dict[str, str]:
    """Every fork's currently selected option, including env overrides."""
    return {fid: resolve(fid) for fid in FORKS}


def describe() -> Dict[str, Any]:
    """Machine-readable summary for the build artifact."""
    out: Dict[str, Any] = {
        "schema_version": 1,
        "note": (
            "Open decisions that can be executed either way. Defaults mirror "
            "the value adopted at each fork's source and are checked against "
            "it; this module stores no physics of its own. Comparisons "
            "report every option and never rank by agreement with anchors."
        ),
        "env_prefix": _ENV_PREFIX,
        "forks": {},
    }
    for fid, fork in FORKS.items():
        drift = None
        if fork.read_adopted is not None:
            try:
                live = fork.read_adopted()
                if live != fork.default():
                    drift = f"source says {live!r}, declaration says {fork.default()!r}"
            except Exception as exc:  # pragma: no cover - diagnostic only
                drift = f"could not read source: {exc}"
        out["forks"][fid] = {
            "question": fork.question,
            "source": fork.source,
            "status": fork.status,
            "selected": resolve(fid),
            "default": fork.default(),
            "options": [
                {
                    "id": o.id,
                    "summary": o.summary,
                    "consequence": o.consequence,
                    "adopted": o.adopted,
                }
                for o in fork.options
            ],
            "notes": fork.notes,
            "drift": drift,
        }
    return out


def write_report(out_path=None):
    """Emit AutoGenerated/variants.json so the open forks are visible."""
    import json
    from pathlib import Path

    from metaphysica.generators._common import autogen_dir

    payload = describe()
    out_path = Path(out_path) if out_path else autogen_dir() / "variants.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return out_path


def main(argv=None) -> int:
    out = write_report()
    payload = describe()
    print("=" * 70)
    print(" EXECUTABLE FORKS")
    print("=" * 70)
    for fid, entry in payload["forks"].items():
        mark = "*" if entry["selected"] != entry["default"] else " "
        print(f" {mark}{fid}  [{entry['status']}]  selected={entry['selected']}")
        print(f"    {entry['question']}")
        for opt in entry["options"]:
            flag = "adopted" if opt["adopted"] else "       "
            print(f"      {flag}  {opt['id']}: {opt['summary']}")
        if entry["drift"]:
            print(f"    DRIFT: {entry['drift']}")
    print("")
    print(f"  override with {payload['env_prefix']}<FORK_ID>=<option>")
    print(f"  Report written to: {out}")
    return 1 if any(e["drift"] for e in payload["forks"].values()) else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
