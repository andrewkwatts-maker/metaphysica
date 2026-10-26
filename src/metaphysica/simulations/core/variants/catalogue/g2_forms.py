"""Catalogue: G2 geometry forks: forms, construction, moduli, bulk signature.

Split out of the former single-file variants.py; text moved verbatim.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from typing import Dict

from ..model import Fork, VariantOption
from ..adopted import (
    _bulk_signature_adopted,
    _g2_form_adopted,
)

FORKS: Dict[str, Fork] = {
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
        status="RULED",
        read_adopted=_g2_form_adopted,
        notes=(
            "RULED 2026-10-01 by the author (D-015): adopt the sensible path, "
            "keep the alternative switchable. The compact form "
            "(octonion_derived) is the active path -- it is a genuine G2 form "
            "and the only one on which Joyce's Eguchi-Hanson resolution, and "
            "so the derivation of (b_2, b_3) = (12, 43), applies (D-003 "
            "addendum: on the split form 6 of the 7 involutions have a "
            "neutral (2,2) transverse space). all_plus_one stays runnable "
            "for comparison.\n\n"
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
                summary=("all (+1) on the seven Fano triples -- the split "
                         "form G2*, kept switchable"),
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
                priority=0,
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
                adopted=True,
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
            "its abstract.\n\n"
            "SUPERSEDED READING (D-023, 2026-10-25): the adopted seed is now "
            "(b2, b3) = (12, 43), computed by joyce_resolution, and every "
            "hypothesis of Joyce 2000 Thm 11.6.1 is measured (g2_closure). "
            "fano_tcs is REFUSED by the engine "
            "(g2_closure.require_buildable_construction) with its reason."
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
                    "proposal built on one is dropped.\n"
                    "REFUSED (D-023): no cited building blocks are in the "
                    "engine, so selecting this builds nothing; exhibited "
                    "examples (71 <= b3 <= 155) also exclude b3 = 43."
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
}
