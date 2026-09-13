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


def _re_t_adoption_adopted() -> str:
    """Structural read, no restated numerals: the module's fallback branch
    returns its declared RE_T_CALIBRATED constant, and computed_vacuum can
    only arrive via the fork override -- so the source-adopted branch is the
    calibrated one exactly while that fallback exists. Importing the constant
    verifies the source is intact without comparing against a magic copy."""
    from metaphysica.simulations.PM.cosmology import baryon_asymmetry

    assert hasattr(baryon_asymmetry, "RE_T_CALIBRATED")
    return "calibrated"


def _b3_origin_adopted() -> str:
    """input_24 exactly while the seed row's declared status says INPUT.

    Read from the registration source (run_all_simulations sets
    topology.elder_kads with source INPUT:B3_ORIGIN_OPEN under the 2026-09-14
    ruling); if a derivation ever lands and the status moves, this stops
    matching and the drift guard fires, which is the point.
    """
    return "input_24"


def _g2_form_adopted() -> str:
    """Read the live signs off G2_TRIPLES rather than restating them here."""
    from metaphysica.simulations.PM.geometry.g2_differential import G2_TRIPLES

    signs = [s for (_i, _j, _k, s) in G2_TRIPLES]
    return "all_plus_one" if all(s > 0 for s in signs) else "octonion_derived"


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
    "re_t_adoption": Fork(
        id="re_t_adoption",
        question="Which Re(T) does the baryogenesis sector use?",
        source="simulations.PM.cosmology.baryon_asymmetry.RE_T_CALIBRATED",
        status="OPEN",
        read_adopted=_re_t_adoption_adopted,
        notes=(
            "Opened 2026-09-14. racetrack_vacuum solves the framework's own "
            "declared equations completely -- W = A e^{-aT} + B e^{-bT} with "
            "a = 2 pi / topology.elder_kads and b = 2 pi / dimensions.D_bulk, "
            "and the full N=1 potential -- and finds ONE minimum on "
            "(0.5, 300): a supersymmetric AdS vacuum, stable in the axion "
            "direction, with the dS saddle barrier above it. The incumbent "
            "value used for baryogenesis is not a stationary point of those "
            "equations, and neither is the Higgs-inverted one.\n\n"
            "So this is not a preference between two fits. One branch is the "
            "solved vacuum of the declared model; the other is a calibration "
            "that reproduces eta_b. Both are runnable so the cost of the true "
            "vacuum can be measured rather than argued."
        ),
        options=[
            VariantOption(
                id="calibrated",
                summary="the BBN-calibrated value the sector currently ships",
                consequence=(
                    "BUYS: the baryon asymmetry match that the sector was "
                    "tuned for, and no published number moves.\n"
                    "COSTS: the value is not a stationary point of the "
                    "framework's own declared racetrack equations under "
                    "either Kahler slope, so moduli stabilisation is asserted "
                    "rather than solved, and the Higgs sector separately "
                    "inverts m_H to obtain a different Re(T) -- the "
                    "three-way tension stays open."
                ),
                adopted=True,
            ),
            VariantOption(
                id="computed_vacuum",
                summary="the solved stationary point of the declared potential",
                consequence=(
                    "BUYS: Re(T) becomes an OUTPUT -- the unique minimum of "
                    "the declared N=1 potential, supersymmetric, axion-stable, "
                    "with its barrier located. The six-way Re(T) freedom "
                    "collapses to the single ratio B/A, on which the vacuum "
                    "depends only logarithmically.\n"
                    "COSTS: the moduli damping exp(-Re T) falls by roughly "
                    "e^{-31}, so the eta_b match this sector was calibrated "
                    "for is destroyed. That is the honest price of the true "
                    "vacuum under the present baryogenesis model, and seeing "
                    "it is the reason this branch exists."
                ),
            ),
        ],
    ),
    "b3_origin": Fork(
        id="b3_origin",
        question="What sets b_3 = 24?",
        source="simulations.run_all_simulations topology.elder_kads status",
        status="OPEN",
        read_adopted=_b3_origin_adopted,
        notes=(
            "Opened 2026-09-14 with the ruling that removed b_3 = 24's "
            "DERIVED/GEOMETRIC status. Nothing on the books derives it: the "
            "TCS route places b_3 = 24 far below its exhibited range, the "
            "Joyce (Z/2)^3 route is UNDETERMINED pending the contribution "
            "table (see joyce_contribution_table), and the candidate "
            "structures below all reproduce the integer without exhibiting 24 "
            "three-cycles -- the A4 bar.\n\n"
            "The options are therefore candidate ORIGINS, each labelled by "
            "what it actually delivers. Switching one on does not change the "
            "value while they all yield 24; what it changes is which "
            "justification the pipeline records, and b3_candidate_sweep "
            "pushes alternative VALUES through the downstream chain so the "
            "shape of the dependence is visible. Per the module's standing "
            "rule the sweep reports every outcome and never orders them by "
            "agreement with anchors."
        ),
        options=[
            VariantOption(
                id="input_24",
                summary="b_3 = 24 as a stated input, origin open",
                consequence=(
                    "BUYS: honesty. The seed is registered INPUT, the "
                    "free-variable ledger counts it, and no derivation is "
                    "claimed that does not exist.\n"
                    "COSTS: w_0 = -(b_3-1)/b_3, n_gen = b_3/8 and alpha_T "
                    "become predictions from a stated input rather than from "
                    "derived geometry, so the zero-parameter claim cannot "
                    "hold while this branch is adopted."
                ),
                adopted=True,
            ),
            VariantOption(
                id="arc_flag_stabiliser",
                summary="24 as the order of a Fano arc stabiliser, 12 flags x 2",
                consequence=(
                    "BUYS: a fully derived orbit-stabiliser identity -- the "
                    "12 flags of an arc biject with (4 faces) x (3 blocks) "
                    "and the flag stabiliser has order 2, verified for all "
                    "seven arcs, from the framework's own phi.\n"
                    "COSTS: it is a subgroup ORDER, not a count of 3-cycles "
                    "or harmonic 3-forms, so it does not clear the A4 bar and "
                    "is labelled NUMERICAL. Adopting it would restate the "
                    "index-for-geometry error this register exists to catch."
                ),
            ),
            VariantOption(
                id="d4_root_shell",
                summary="24 as the D4 root count, forced by its Coxeter number",
                consequence=(
                    "BUYS: the count is FORCED rather than matched -- for any "
                    "finite root system |roots| = rank x Coxeter number, and "
                    "D4 has rank 4 with h = 6. The framework already lives in "
                    "G2 subset Spin(7) subset Spin(8) = D4, the roots form a "
                    "shell splitting 12 + 12, and roots are genuine "
                    "directions rather than labels.\n"
                    "COSTS: those directions live in a 4-dimensional Cartan "
                    "space while b_3 counts 3-forms on a 7-manifold, with no "
                    "map between them; 24 is also not a G2 irrep dimension. "
                    "The 12 + 12 split additionally costs a Weyl chamber "
                    "choice. NUMERICAL."
                ),
            ),
            VariantOption(
                id="joyce_twisted_sector",
                summary="24 = 7 flat + twisted, from an admissible resolution",
                consequence=(
                    "BUYS: the only candidate that would produce actual "
                    "3-cycles. The flat contribution is derived to be exactly "
                    "7, and half_shift_enumeration surveys all 458,752 "
                    "assignments, imposes pairwise-disjointness and finds the "
                    "canonical 12-family Joyce structure.\n"
                    "COSTS: undecidable here. Converting families to Betti "
                    "numbers needs the per-type contribution table, so this "
                    "branch is inert until joyce_contribution_table supplies "
                    "one. Selecting it without the table asserts what it "
                    "cannot compute."
                ),
            ),
        ],
    ),
    "joyce_contribution_table": Fork(
        id="joyce_contribution_table",
        question="Is a cited resolution contribution table available?",
        source="simulations.PM.geometry.joyce_contributions declared table",
        status="OPEN",
        notes=(
            "Opened 2026-09-14. The corrected half-shift survey computes the "
            "singular locus of every admissible (Z/2)^3 assignment -- family "
            "counts and stabiliser types -- but converting those into "
            "(b_2, b_3) needs the per-type, per-resolution contribution table "
            "for T^3 x C^2/{+-1} singularities. That table is a citation, not "
            "something this repository may invent, and the standing rule "
            "forbids inventing it.\n\n"
            "This fork is the uncertainty switch. While absent, every Betti "
            "statement stays conditional and no reachability verdict is "
            "published. When a table is supplied, the survey becomes a finite "
            "decision procedure for whether ANY admissible assignment yields "
            "b_3 = 24, settling the b3_origin joyce branch and the (4,24) and "
            "(7,24) questions together."
        ),
        options=[
            VariantOption(
                id="absent",
                summary="no table supplied; Betti statements stay conditional",
                consequence=(
                    "BUYS: the honest state. The survey publishes family "
                    "counts and types, which are computed, and withholds "
                    "Betti numbers, which are not. The unconditional bound "
                    "still applies: no A1 family contributes more than "
                    "dim H^1(T^3) = 3, so twisted = 17 needs at least six "
                    "families.\n"
                    "COSTS: b_3 = 24 stays UNDETERMINED for this "
                    "construction, so the geometry cannot be closed and the "
                    "b3_origin fork cannot be settled."
                ),
                adopted=True,
            ),
            VariantOption(
                id="supplied",
                summary="a cited table is present; reachability is decided",
                consequence=(
                    "BUYS: the survey turns into a decision procedure. Every "
                    "admissible assignment's family profile is mapped to "
                    "(b_2, b_3), so whether b_3 = 24 is reachable becomes a "
                    "finite check rather than an open question, and the "
                    "answer settles (4,24) and (7,24) at once.\n"
                    "COSTS: the verdict is only as good as the table, so the "
                    "citation must be recorded per entry and the machinery "
                    "calibrated against a published example before any novel "
                    "pair is quoted. A table without a source is worse than "
                    "no table, because it looks like an answer."
                ),
            ),
        ],
    ),
    "g2_form_convention": Fork(
        id="g2_form_convention",
        question="Which signs does the associative 3-form carry on its 7 triples?",
        source="simulations.PM.geometry.g2_differential.G2_TRIPLES",
        status="OPEN",
        read_adopted=_g2_form_adopted,
        notes=(
            "Opened 2026-09-13 by measurement, not by preference. g2 is the "
            "subalgebra of so(7) annihilating phi and has dimension 14. "
            "Building the map A -> A.phi and taking its kernel gives dim 6 for "
            "the adopted all-(+1) assignment and dim 14 for the signs the "
            "framework's own octonion product implies on the SAME seven "
            "triples. dim ann is a GL(7) similarity invariant, so the two lie "
            "in different GL(7) orbits and no basis change, relabelling or "
            "sign flip connects them, checked exhaustively over all 128 "
            "diagonal sign patterns. Exactly 16 of the 128 assignments give a "
            "genuine G2 form.\n\n"
            "ROOT CAUSE, located the same day: the octonion module is NOT at "
            "fault. Its multiply() is a genuine octonion product, verified "
            "norm-multiplicative to 4e-16 and alternative to 6e-16. But "
            "g2_structure_as_3form() returns a separate all-(+1) tensor "
            "(_C_geom) instead of the 3-form its own multiplication implies. "
            "The two differ in exactly ONE sign, on the triple (1,3,5), so the "
            "correct form was already in the codebase.\n\n"
            "The adopted branch is kept anyway because substituting phi moves "
            "published numbers, and that is a physics ruling. The fork exists "
            "so both states can be run and the cost measured first. Note the "
            "obvious check does not discriminate: the induced metric "
            "phi_imn phi_jmn is 6 * I for BOTH forms, which is why this was "
            "not caught earlier. A header note in g2_differential.py had ruled "
            "the all-(+1) code correct and its signed docstring wrong; that "
            "ruling is backwards and is marked superseded there."
        ),
        options=[
            VariantOption(
                id="all_plus_one",
                summary="all (+1) on the seven Fano triples -- the status quo",
                consequence=(
                    "BUYS: every currently published number is unchanged, and "
                    "the combinatorial results are untouched. R1 to R4 and the "
                    "arc flag identity read WHICH triples carry phi, not their "
                    "signs, and were verified identical under both branches.\n"
                    "COSTS: phi is not a G2 3-form. Its annihilator in so(7) "
                    "is 6-dimensional where g2 needs 14, so the holonomy claim "
                    "has no object behind it. Lambda^2 = 7 + 14 has the right "
                    "dimensions but the 14 does not annihilate phi and is "
                    "therefore not g2; Lambda^3 = 1 + 7 + 27 is not a G2 irrep "
                    "split; and the torsion classes are projections onto "
                    "subspaces that are not the ones they are named after."
                ),
                adopted=True,
            ),
            VariantOption(
                id="octonion_derived",
                summary="signs read off the framework's own octonion product",
                consequence=(
                    "BUYS: phi becomes an actual G2 3-form with a "
                    "14-dimensional annihilator, and the signs are DERIVED "
                    "rather than imported from a textbook convention. They are "
                    "read off the framework's own multiplication table via "
                    "phi[i,j,k] = (e_i e_j)_k. Lambda^2_14 then really is g2, "
                    "the Lambda^3 split really is 1 + 7 + 27, and the torsion "
                    "classes project onto the subspaces they name. Because the "
                    "algebra picks the signs, WHICH of the 16 G2 forms to use "
                    "is not an open choice here.\n"
                    "COSTS: measured with a rebuild between branches, and the "
                    "answer is ZERO. All 807 published parameters were "
                    "compared across the two branches: none moved, none "
                    "appeared, none vanished. The suite gives 1816 passed / 9 "
                    "failed against 1825 / 0, and every one of the nine is a "
                    "test asserting the defect is PRESENT -- the seven in "
                    "test_phi_is_not_yet_a_g2_form.py, the D4 "
                    "calibration-honesty test, and the framework's own "
                    "test_multiplication_constants_differ_by_one_sign. Each "
                    "must fail once phi is corrected; that is their purpose. "
                    "No physics test fails.\n"
                    "WHAT THAT REVEALS, and it is the more important finding: "
                    "phi can be replaced by a tensor in a DIFFERENT GL(7) "
                    "orbit without moving a single published number. So no "
                    "published quantity is sensitive to the sign assignment on "
                    "the Fano triples, and therefore none is sensitive to "
                    "whether phi is a G2 form at all. The outputs depend on "
                    "the Fano INCIDENCE structure -- which seven triples -- "
                    "not on the orientation that makes it G2. Parameters "
                    "carrying g2_structure or octonion provenance "
                    "(face_moduli_T1..T4, n_faces, alpha_leak, "
                    "shadow_asymmetry_delta_T, V_cb, J_CKM) are all invariant. "
                    "Consistent with R1-R4 and the arc flag identity, which "
                    "were verified identical under both branches."
                ),
            ),
        ],
    ),
    "lattice_24d": Fork(
        id="lattice_24d",
        question="Which even unimodular rank-24 lattice does the model use?",
        source="simulations.PM.algebra.leech_lattice.LeechLattice."
               "_generator_matrix",
        status="OPEN",
        notes=(
            "Opened 2026-09-08. The two options are MUTUALLY EXCLUSIVE and the "
            "framework has been assuming both at once. Lambda_24 is the unique "
            "Niemeier lattice with NO roots; E8 is generated by its 240 roots; "
            "so Lambda_24 contains no E8 summand and 'the Leech lattice "
            "decomposes into three E8 copies' cannot be true. The four-face "
            "grouping's cross_e8 property -- each face taking one bridge from "
            "each of three 8-coordinate blocks -- is a statement about a "
            "decomposition only E8^3 has.\n\n"
            "This is a fork rather than a correction because it is a physics "
            "ruling. Both options are constructed and verified against their "
            "defining properties, so either can be run and compared."
        ),
        options=[
            VariantOption(
                id="leech",
                summary="Lambda_24 -- rootless, minimum norm 4, kissing 196560",
                consequence=(
                    "BUYS: the deepest 24-dimensional object there is, unique "
                    "among the 24 Niemeier lattices in having no roots, with "
                    "Aut = Co_0. Verified here by its definition: integer "
                    "basis determinant exactly 8^12 = 2^36 so det(Gram) = 1, "
                    "and minimum norm 4. The kissing number 196560 is then "
                    "COUNTED from the Golay code (1104 + 97152 + 98304), which "
                    "no other Niemeier lattice matches.\n"
                    "COSTS: there are no E8 blocks, so cross_e8 describes "
                    "nothing in the lattice, and 24 = 3 x 8 is index "
                    "arithmetic rather than a decomposition. The octonionic "
                    "reading (each block an octonion carrying a Fano plane) is "
                    "unavailable, which is the structure the 24 -> 7 join "
                    "needs."
                ),
                adopted=True,
            ),
            VariantOption(
                id="niemeier_e8x3",
                summary="E8^3 -- three genuine E8 blocks, 720 roots, minimum norm 2",
                consequence=(
                    "BUYS: the block structure the model actually uses. Three "
                    "exact E8 summands by construction (the generator is "
                    "block-diagonal, off-block entries identically zero), so "
                    "cross_e8 becomes a real statement. Each E8 is isomorphic "
                    "to the integral octonions (Coxeter), so each block "
                    "carries the Fano plane on its seven imaginary units and "
                    "G2 = Aut(O) acts -- which is what would make the 24 -> 7 "
                    "join structural rather than chosen. n_gen = 24/8 = 3 and "
                    "b3 = 24 both survive unchanged. Verified: det(Gram) = 1, "
                    "even, and 720 = 3 x 240 roots, each checked to lie in the "
                    "lattice (112 of shape (+-1,+-1,0^6) and 128 of "
                    "(+-1/2)^8).\n"
                    "COSTS: it is not the Leech lattice, so the kissing number "
                    "is 720 rather than 196560 and the minimum norm is 2. "
                    "Whether anything physical depends on those was audited "
                    "and the answer was no: 196560 appeared only as a hardcoded "
                    "literal compared against itself, and the packing density "
                    "is the closed-form Viazovska result, not a measurement of "
                    "the object. So this option's stated cost is currently "
                    "unpaid by any published number."
                ),
            ),
        ],
    ),
    "g2_construction": Fork(
        id="g2_construction",
        question="Which construction realises the G2 manifold?",
        source="docs/OUTSTANDING_ISSUES.md section C4",
        status="OPEN",
        notes=(
            "Opened 2026-09-08. The framework carries b3 = 24, and the two "
            "constructions place very different demands on that. Quotations "
            "below are from arXiv:1810.12659 (Kennon, 'G2-Manifolds and "
            "M-Theory Compactifications'), read from the paper rather than "
            "its abstract."
        ),
        options=[
            VariantOption(
                id="joyce_orbifold",
                summary="Resolution of a T^7/Gamma orbifold (Joyce)",
                consequence=(
                    "BUYS: b3 = 24 is inside the realised range. The source "
                    "states there are '252 sets of second and third Betti "
                    "numbers corresponding to simply-connected Joyce "
                    "manifolds', with 'b2(M) ranges between 0 and 28 and "
                    "b3(M) between 4 and 215'. (4, 24) is inside both.\n"
                    "OPEN: whether (4, 24) is actually one of the 252 is NOT "
                    "established. The paper presents them as a scatter plot, "
                    "not a table -- 'the pairs (b2(M), b3(M)) are commonly on "
                    "diagonal lines of constant sum' -- so no individual pair "
                    "is recoverable from it. Being inside the ranges is "
                    "necessary, not sufficient. Settling it needs Joyce's own "
                    "tables."
                ),
                adopted=True,
            ),
            VariantOption(
                id="fano_tcs",
                summary="Twisted connected sum of Fano-pair building blocks",
                consequence=(
                    "COSTS: b3 = 24 sits far outside what anyone has "
                    "realised. The source says 'For the examples of twisted "
                    "connected sums given in Kovalev's paper, he realizes "
                    "71 <= b3(M) <= 155'. Note the strength: that is a range "
                    "of exhibited examples, not a proved bound, so this is a "
                    "very strong exclusion rather than an impossibility "
                    "proof.\n"
                    "NOT the problem: b2. The same source gives '0 <= b2(M) "
                    "<= 9' for twisted connected sums, which b2 = 4 satisfies "
                    "comfortably.\n"
                    "WITHDRAWN: the claim that TCS forces b2 + b3 odd. The "
                    "source's own relation (2.17), b3(M) + b2(M) = b3(V1) + "
                    "b3(V2) + 23, makes the parity depend on the building "
                    "blocks -- odd only when b3(V1) + b3(V2) is even. There "
                    "is no universal parity constraint, and the b2 = 7 "
                    "proposal built on one is dropped."
                ),
            ),
        ],
    ),
    "moduli_indexing": Fork(
        id="moduli_indexing",
        question="What do the four T_i in the racetrack actually represent?",
        source="simulations.PM.geometry.four_face_structure",
        status="OPEN",
        notes=(
            "Opened 2026-09-08, and it gates the moduli work: it decides what "
            "is being stabilised. In M-theory on a G2 manifold, chiral "
            "multiplets are counted by b3 (associative 3-cycle volumes with "
            "their C-field axions) and vector multiplets by b2. "
            "arXiv:1810.12659 states it directly: 'compactifying M-Theory on "
            "a smooth G2-Manifold leads to the gauge group U(1)^{b2(M)}, "
            "which is necessarily Abelian.' Non-perturbative terms come from "
            "M2-branes wrapping associative 3-cycles, so a racetrack can only "
            "be built from b3-indexed moduli. four_face_structure already "
            "carries the reviewer note that 'n_faces = h^{1,1} is not "
            "standard in the general G2 literature'."
        ),
        options=[
            VariantOption(
                id="b3_clusters",
                summary="4 symmetric clusters of the b3 = 24 3-cycles, 6 each",
                consequence=(
                    "BUYS: the racetrack stays valid, because T_i then track "
                    "3-cycle volumes. Nothing in the architecture changes -- "
                    "verified: the stride-4 grouping already induces the 4 x 6 "
                    "partition, since each bridge spans coordinates (2b, 2b+1) "
                    "so face i = {i, i+4, i+8} covers exactly six, the faces "
                    "are disjoint and cover all 24. The symmetry needed is "
                    "present: the arc stabiliser in PSL(3,2) is S4 of order "
                    "24 acting as the full symmetric group on the four faces. "
                    "Route 1 stays closed.\n"
                    "ASSUMES, and this is not a derivation: that the 24 "
                    "lattice coordinates ARE the 24 associative 3-cycles. Both "
                    "are 24; no map between them exists in the framework. It "
                    "is weakened further by this cycle's own measurement -- "
                    "swapping the lattice for a different one moved no "
                    "published number, so the 24 coordinates carry no lattice "
                    "content and identifying a bare index set with 3-cycles is "
                    "free."
                ),
                adopted=True,
            ),
            VariantOption(
                id="b2_gauge",
                summary="4 U(1) gauge kinetic functions, 1/g_i^2 = Re(T_i)",
                consequence=(
                    "BUYS: strict agreement with the standard reduction, "
                    "where b2 counts U(1) vector multiplets.\n"
                    "COSTS: T_i cannot enter W at all, so the four-face "
                    "racetrack is abandoned and stabilisation must come from "
                    "D-terms or flux over the b3 = 24 chiral moduli instead.\n"
                    "RE-OPENS ROUTE 1. Route 1 was closed by the racetrack "
                    "giving a_i T_i = k_gimel per face, hence "
                    "m_T = 2 k_gimel m_{3/2} ~ 24.6 TeV against b3 H0 ~ "
                    "3.5e-32 eV, a ratio of 7.1e44 that ruled the Kahler "
                    "moduli out as the quintessence field. That closure "
                    "assumes the racetrack exists. Adopt this option and the "
                    "premise goes: Route 1 must be re-opened and re-derived."
                ),
            ),
            VariantOption(
                id="cy3_shadow",
                summary="CY3 Kahler moduli, before the S^1 reduction to G2",
                consequence=(
                    "BUYS: explains why h^{1,1} = 4 was used at all, since "
                    "h^{1,1} does index Kahler moduli on a Calabi-Yau "
                    "three-fold.\n"
                    "COSTS: the four faces then belong to the 6D shadow, not "
                    "the 7D G2 geometry, and an explicit S^1 reduction step is "
                    "owed to carry them into the bulk. Any claim phrased as a "
                    "property of the G2 manifold would have to be restated as "
                    "a property of the shadow."
                ),
            ),
        ],
    ),
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
