"""Catalogue: seed and b3 forks (b3 seed, generation count, b3 origin, seed selection).

Split out of the former single-file variants.py; text moved verbatim.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from typing import Dict

from ..model import DISABLED, Fork, VariantOption
from ..adopted import (
    _b3_origin_adopted,
    _b3_seed_adopted,
    _seed_selection_adopted,
)

FORKS: Dict[str, Fork] = {
    "b3_seed": Fork(
        id="b3_seed",
        question="Which (b_3, b_2) does the model take, and is the seed derived?",
        source="simulations.PM.geometry.b3_path.PATHS adopted entry",
        status="RULED",
        read_adopted=_b3_seed_adopted,
        notes=(
            "Opened 2026-09-15 by a computation, not a preference. "
            "derived_contribution_table settled the reachable Betti numbers of "
            "a Joyce (Z/2)^3 resolution of T^7/Gamma with Gamma the diagonal "
            "stabiliser of the framework's own phi: b_3 = 7 + 3 n_T3 with "
            "n_T3 in {0, 4, 8, 12}, so b_3 in {7, 19, 31, 43} and b_3 = 7 "
            "(mod 12). 24 = 0 (mod 12), so b_3 = 24 is NOT REACHABLE by this "
            "construction, and fano_tcs had already placed it far below its "
            "exhibited 71-155 range.\n\n"
            "So b_3 = 24 has no geometric home left among the declared "
            "options, while (12, 43) is reachable AND is the Betti pair of "
            "Joyce's canonical published example -- reproduced by machinery "
            "that was never told it, which discharges the calibration gate by "
            "computation rather than by citation.\n\n"
            "The decisive discriminator is structural, not statistical: a "
            "generation count must be an integer. At b_3 = 43, b_3/8 fails, "
            "but b_2 = 12 arrives derived from the same family count and "
            "n_gen = b_2/4 = 3 exactly, with 4 the derived faces. So the three "
            "generations survive the move -- they relocate. See the "
            "n_gen_source fork."
        ),
        options=[
            VariantOption(
                id="seed_24",
                priority=0,
                summary="b_3 = 24, b_2 = 4 -- the status quo, seed as an input",
                consequence=(
                    "BUYS: every published number unchanged, and w_0 = "
                    "-23/24 at 0.017 sigma against the DESI anchor -- the "
                    "closest agreement any candidate reaches.\n"
                    "COSTS: b_3 = 24 is an INPUT with no geometric home left. "
                    "It is unreachable by the Joyce construction and far below "
                    "the TCS range, so nothing declared derives it, and b_2 = "
                    "4 traces to a previously FITTED h^{1,1}. The "
                    "free-variable count cannot reach zero while this holds."
                ),
            ),
            VariantOption(
                id="seed_7_joyce",
                status=DISABLED,
                summary="b_3 = 7, b_2 = 0 -- the unresolved orbifold limit",
                consequence=(
                    "BUYS: reachable and fully derived, so it belongs in "
                    "the family the selection argument ranges over.\n"
                    "COSTS: n_gen = b_2/4 = 0. No generations at all -- a "
                    "STRUCTURAL refutation, not a disagreement with data."
                ),
            ),
            VariantOption(
                id="seed_19_joyce",
                status=DISABLED,
                summary="b_3 = 19, b_2 = 4 -- four A1 families",
                consequence=(
                    "BUYS: reachable and derived; the b_2 = 4 that seed_24 "
                    "carries as a FITTED h^{1,1} arrives here derived.\n"
                    "COSTS: n_gen = b_2/4 = 1. One generation, refuted "
                    "structurally."
                ),
            ),
            VariantOption(
                id="seed_31_joyce",
                status=DISABLED,
                summary="b_3 = 31, b_2 = 8 -- eight A1 families",
                consequence=(
                    "BUYS: reachable and derived.\n"
                    "COSTS: n_gen = b_2/4 = 2. Two generations, refuted "
                    "structurally."
                ),
            ),
            VariantOption(
                id="seed_43_joyce",
                summary="b_3 = 43, b_2 = 12 -- both derived from the A1 family count",
                consequence=(
                    "BUYS: the seed stops being an input. b_3 = 7 + 3 x 12 "
                    "where the 7 is the derived flat contribution and the 12 "
                    "is the derived count of A1 T^3 families; b_2 = 12 is "
                    "derived from the same count, one exceptional 2-class per "
                    "family. The pair (12, 43) is Joyce's canonical published "
                    "example. The generation count survives as n_gen = b_2/4 = "
                    "3, relocated but still exactly three and still derived on "
                    "both sides.\n"
                    "COSTS: w_0 moves to -42/43, about 0.94 sigma against the "
                    "DESI anchor -- worse agreement, in exchange for a derived "
                    "seed, which is the same trade the dark_energy_betti "
                    "ruling already took deliberately. The '+2' identity "
                    "D_bulk - b_3 = 2 BREAKS, giving -17, so either D_bulk is "
                    "not 26 on this path or that identity was never "
                    "structural. Every b_3-consuming relation shifts: the "
                    "racetrack exponent, k_bary = b_3 - 14, chi/b_3, alpha_T."
                ),
                adopted=True,
            ),
        ],
    ),
    "n_gen_source": Fork(
        id="n_gen_source",
        question="Which geometric quantity supplies the generation count?",
        source="simulations.PM.geometry.b3_path n_gen_source per path",
        status="RULED",
        notes=(
            "Opened 2026-09-15 alongside b3_seed, because the two are coupled "
            "and pretending otherwise would hide the coupling. n_gen must be a "
            "positive integer -- a generation count is a number of things -- "
            "and that is a structural constraint referencing no measurement, "
            "which makes it the decisive discriminator where w_0 is not (w_0 "
            "moves only 0.0017 per unit b_3).\n\n"
            "b_3/8 gives 3 at b_3 = 24 and 5.375 at b_3 = 43, so it fails on "
            "the derived-seed path. b_2/4 gives 3 at b_2 = 12 and 1 at "
            "b_2 = 4, so it fails on the status-quo path. Exactly one works per "
            "seed, which is why this fork is not independent of b3_seed and "
            "says so."
        ),
        options=[
            VariantOption(
                id="b3_over_dim_O",
                summary="n_gen = b_3 / 8, the 8 being dim O",
                consequence=(
                    "BUYS: the current derivation, giving exactly 3 at "
                    "b_3 = 24, with the 8 carrying octonionic meaning.\n"
                    "COSTS: it requires 8 to divide b_3, so it is incompatible "
                    "with every Joyce-reachable value -- 7, 19, 31 and 43 are "
                    "all odd. Adopting the derived seed forces this to be "
                    "abandoned."
                ),
                # variants.py:936-939 (this consequence): "incompatible with
                # every Joyce-reachable value -- 7, 19, 31 and 43"; notes above
                # (b_3/8 "fails on the derived-seed path").
                excludes=(("b3_seed", "seed_7_joyce"), ("b3_seed", "seed_19_joyce"),
                      ("b3_seed", "seed_31_joyce"), ("b3_seed", "seed_43_joyce")),
            ),
            VariantOption(
                id="b2_over_faces",
                summary="n_gen = b_2 / 4, the 4 being the derived faces",
                # D-006 (2026-09-30): b_2 / 4 counts the singular
                # involutions only on the all-plain subfamily; on Joyce's
                # full family the invariant count is n, the rank of the
                # singular span. Scope recorded in generation_selection.
                consequence=(
                    "BUYS: exactly 3 at b_2 = 12, with both sides derived -- "
                    "b_2 from the A1 family count and 4 from the moved "
                    "coordinates of an involution (R2). It is the only "
                    "generation source compatible with a derived seed.\n"
                    "COSTS: gives 1 at the off-path b_2 = 4, so it is wrong on "
                    "the seed_24 branch. It also relocates the generation "
                    "count away from the octonions, which is a change in the "
                    "theory's story about why there are three -- and the "
                    "measured chain behind it is n_gen = rank(Gamma) = 3, of "
                    "which b_2/4 is the RECOVERY (n_families = 4 x n_singular "
                    "at every admissible assignment)."
                ),
                # variants.py:951-953 (this consequence): "gives 1 at the
                # off-path b_2 = 4, so it is wrong on the seed_24 branch";
                # notes above ("b_2/4 ... 1 at b_2 = 4, so it fails on the
                # status-quo path").
                # P5a2: n_gen = b_2/4 is 0, 1, 2 at seed_7/19/31 (b_2 = 0, 4, 8),
                # computed by b3_path._n_gen_value; only b_2 = 12 (seed_43)
                # gives 3, so build-time require_three_generations refuses them.
                excludes=(("b3_seed", "seed_24"), ("b3_seed", "seed_7_joyce"),
                          ("b3_seed", "seed_19_joyce"), ("b3_seed", "seed_31_joyce")),
                adopted=True,
            ),
            VariantOption(
                id="chi_over_24",
                summary="n_gen = chi_eff/24 (the per-sector chi_eff, 72/24 = 3)",
                consequence=(
                    "WIRED D-022: FormulasRegistry.n_gen reads chi_eff_sector/24. "
                    "Catalogue: corrected from chi/2 to chi/24 for 8D manifolds on "
                    "2025-11-22 (source 48ec267c); kept as the sector-level formula in "
                    "v20.1 (FormulasRegistry v20.1 'Formula A'). restored_from: none "
                    "(current source). Expected: 3, the same as the adopted route, "
                    "because the source supplies chi_eff_sector = 72."
                ),
                status="disabled",
            ),
            VariantOption(
                id="chi_eff_over_48",
                summary="n_gen = chi_eff_total/48 (144/48 = 3), generations from the effective Euler characteristic",
                consequence=(
                    "WIRED D-022: FormulasRegistry.n_gen reads chi_eff_total/48. "
                    "Catalogue (3ba5848): fails on the whole Joyce family on both "
                    "chi_eff branches; 6 b3/48 = b3/8 identically, so not independent. "
                    "Under D-009 it survives as n_gen = chi_eff/48 = n with the K3 "
                    "reading. restored_from: main:src/metaphysica/simulations/PM/"
                    "geometry/chi_eff_branches.py; source "
                    "metaphysica/docs/DISCARDED_PATH_COVERAGE.md rows 22, 23. "
                    "Expected: 3 on the registry's own chi_eff_total = 144."
                ),
            ),
        ],
    ),
    "b3_origin": Fork(
        id="b3_origin",
        question="What sets b_3? (asked of whichever seed is live; the options below were written when it was 24)",
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
            "agreement with anchors.\n\n"
            "INAPPLICABLE ON THE ADOPTED SEED (D-023, 2026-10-25): input_24, "
            "arc_flag_stabiliser, d4_root_shell and joyce_twisted_sector were "
            "written for b_3 = 24. On seed_43_joyce the origin is answered by "
            "derived_joyce_a1, and joyce_twisted_sector is what it became once "
            "the contribution table existed. Selecting the others there changes "
            "no output; input_24 is contract-bound to seed_24, and the other two "
            "already fail b3_origin_clears_the_a4_bar."
        ),
        options=[
            VariantOption(
                id="derived_joyce_a1",
                summary="the seed is DERIVED: b_2 = A1 family count, b_3 = 7 + 3 b_2",
                consequence=(
                    "BUYS: the origin question is ANSWERED on the reachable "
                    "family -- n_gen = rank(Gamma) = 3 selects (12, 43) out "
                    "of the four profiles, the flat 7 is derived (R5), and "
                    "the family count comes from the enumeration.\n"
                    "COSTS: applies only on a Joyce-reachable seed; on "
                    "seed_24 the candidate origins below stay exactly as "
                    "open as they were."
                ),
                adopted=True,
            ),
            VariantOption(
                id="input_24",
                summary="b_3 = 24 as a stated input, origin open (off-family)",
                consequence=(
                    "BUYS: honesty. The seed is registered INPUT, the "
                    "free-variable ledger counts it, and no derivation is "
                    "claimed that does not exist.\n"
                    "COSTS: w_0 = -(b_3-1)/b_3, n_gen = b_3/8 and alpha_T "
                    "become predictions from a stated input rather than from "
                    "derived geometry, so the zero-parameter claim cannot "
                    "hold while this branch is taken."
                ),
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
    "seed_selection": Fork(
        id="seed_selection",
        question=("What selects (b_2, b_3) = (12, 43) on the n = 3 line of "
                  "phi's Joyce family?"),
        source="simulations.PM.geometry.closed_geometry.selection."
               "SELECTION_ROUTE",
        status="RULED",
        read_adopted=_seed_selection_adopted,
        notes=(
            "RULED 2026-10-01 by the author (D-015): adopt WA-1. pi_1 is "
            "finite exactly on the n = 3 line (CG.4; holonomy exactly G2 "
            "there on the compact form), and on that line the 12 bridges "
            "match the 12 resolved A1 components as one 3 x 4 structure only "
            "on the all-plain classes (CG.8: 280 yes, 84 Example-4 no). "
            "Reading one bridge as one component turns that match into the "
            "selection. Consumer: certificate theorem CG.12 (y7-selection) "
            "and the overview's selection layer. WA-1's own test, stated "
            "when it was proposed: the 12 U(1) gauge-kinetic functions come "
            "in 3 quartets (Lukas-Morris eq. 1.3); a class breaking that "
            "would kill it."
        ),
        options=[
            VariantOption(
                id="wa1_correspondence",
                summary=("WA-1: one bridge = one resolved A1 component; the "
                         "3 x 4 match selects (12, 43)"),
                consequence=(
                    "BUYS: (12, 43) is selected by geometry with no data and "
                    "no free choice: the reachable family, pi_1 on the n = 3 "
                    "line, and the bridge <-> component match compose into "
                    "one chain (CG.12).\n"
                    "COSTS: WA-1 is an identification, not a theorem -- the "
                    "combinatorics are proved, the physical reading is "
                    "assumed. Its kill condition is the quartet structure of "
                    "the U(1) couplings."
                ),
                adopted=True,
            ),
            VariantOption(
                id="ruling_only",
                summary=("(12, 43) by the 2026-09-22 ruling; the bridge match "
                         "is a finding, not a selection"),
                consequence=(
                    "BUYS: no identification of bridges with components is "
                    "assumed.\n"
                    "COSTS: the n = 3 line has 9 Joyce-reachable pairs and "
                    "nothing in the geometry picks (12, 43) among them -- "
                    "the choice is an input."
                ),
                priority=0,
            ),
        ],
    ),
}
