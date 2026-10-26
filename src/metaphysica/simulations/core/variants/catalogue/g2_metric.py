"""Catalogue: G2 geometry forks: metric construction, chi_eff, twisted norm.

Split out of the former single-file variants.py; text moved verbatim.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from typing import Dict

from ..model import DISABLED, Fork, VariantOption
from ..adopted import (
    _chi_eff_route_adopted,
    _metric_construction_adopted,
    _twisted_norm_convention_adopted,
)

FORKS: Dict[str, Fork] = {
    "metric_construction": Fork(
        id="metric_construction",
        question="Which construction turns phi into a metric?",
        source=("simulations.PM.geometry.g2_differential."
                "G2DifferentialGeometry.metric_by_convention"),
        status="OPEN",
        read_adopted=_metric_construction_adopted,
        notes=(
            "Opened 2026-09-21. compute_metric() is the QUADRATIC contraction "
            "phi_iab phi_jab / 6, and its docstring called that Hitchin's "
            "formula. It is not: Hitchin's construction is CUBIC in phi, "
            "B_ij = eps^{a1..a7} phi_{i a1 a2} phi_{j a3 a4} phi_{a5 a6 a7} "
            "with g = B / |det B|^(1/9), and cubic is the lowest degree that "
            "can see the difference. Measured: the quadratic returns exactly "
            "1.0 * I_7 for BOTH the all-(+1) phi and the octonion-derived one, "
            "so every claim of 'the unique compatible Riemannian metric' made "
            "through it was unfalsifiable -- which is why g2_form_convention "
            "went unnoticed as long as it did.\n\n"
            "WHAT THE CUBIC FORM REVEALS, refining the earlier finding rather "
            "than confirming it: Lambda^3(R^7) has exactly TWO open GL(7,R) "
            "orbits and BOTH have 14-dimensional stabilisers, so 'dim 14 vs 6' "
            "is not the invariant it was read as. The one that discriminates is "
            "the unordered signature of B -- (7,0) for octonion_derived, (4,3) "
            "for all_plus_one. So the adopted phi IS a G2-structure, for the "
            "SPLIT real form g2*, whose maximal compact SU(2)xSU(2) has "
            "dimension 6: exactly the 6 measured in so(7). What it is not is "
            "RIEMANNIAN, and Joyce's construction needs the compact form.\n\n"
            "This also settles the Lambda decomposition question. The "
            "dimensions 1 + 7 + 27 and 7 + 14 are correct on BOTH branches, as "
            "a shared complexification requires; only the IDENTIFICATION of the "
            "14 with compact g2 breaks, not any dimension.\n\n"
            "NOT AFFECTED, verified: the diagonal (Z/2)^3 stabiliser depends "
            "only on phi's SUPPORT, which both branches share exactly, so R1 "
            "to R4, the half-shift enumeration, the A1 census and "
            "b_3 = 7 + 3 n_T3 are fork-independent either way. The closure "
            "rides on Fano incidence, not on the real form.\n\n"
            "INERT ON THE ADOPTED PATH, BY DESIGN (D-023, 2026-10-25): on the "
            "compact octonion_derived form both constructions return a "
            "constant multiple of I_7 (measured: 1.0 and 3.017), so switching "
            "changes no output there. The fork is a consistency check, not a "
            "rival: it discriminates only on the split form, where the cubic "
            "exhibits (4,3)."
        ),
        options=[
            VariantOption(
                id="quadratic_contraction",
                summary="phi_iab phi_jab / 6 -- the status quo",
                consequence=(
                    "BUYS: nothing published moves. Every metric-dependent "
                    "quantity in the framework already rides on this, and it "
                    "is a genuine identity for a genuine G2 form.\n"
                    "COSTS: it is blind to the real form, returning 1.0 * I_7 "
                    "for compact and split alike, so it cannot certify any "
                    "orientation as Riemannian and cannot detect an unstable "
                    "phi at all. It is a consistency check wearing a metric "
                    "derivation's clothes."
                ),
                adopted=True,
            ),
            VariantOption(
                id="hitchin_cubic",
                summary="Hitchin's cubic construction on the 3-form",
                consequence=(
                    "BUYS: a metric that actually depends on the GL(7) orbit. "
                    "It gives a flat positive-definite metric on the compact "
                    "branch, exhibits signature (4,3) on the adopted split "
                    "branch, is stable under rotation, general GL(7) and "
                    "reflection, and RAISES on an unstable phi instead of "
                    "returning a matrix for a 3-form that induces no metric.\n"
                    "COSTS: on the adopted all-(+1) phi it is INDEFINITE, so "
                    "anything downstream expecting a Riemannian metric would be "
                    "consuming a signature-(4,3) object. That is not a defect "
                    "in the construction but an honest report of what the "
                    "adopted phi induces -- and it means this branch and "
                    "g2_form_convention = octonion_derived belong together if a "
                    "Riemannian metric is wanted.\n"
                    "ALSO LIMITED, measured: g_phi is not covariant under the "
                    "obvious pushforward, because B contracts with epsilon, "
                    "which transforms as a density rather than a fixed array. "
                    "g(h*phi) is not proportional to h^T g(phi) h. The "
                    "signature is still frame-robust up to overall sign, which "
                    "is what the classification uses."
                ),
            ),
        ],
    ),
    "chi_eff_route": Fork(
        id="chi_eff_route",
        question=(
            "Is chi_eff a CONSTANT independent of the seed, or SEED-DEPENDENT? "
            "The framework currently wants both."
        ),
        source="simulations.PM.geometry.geometry_narration.CHI_EFF_READING",
        status="RULED",
        read_adopted=_chi_eff_route_adopted,
        notes=(
            "RULED 2026-10-01 by the author (D-015): the K3 reading of D-009 "
            "is adopted. chi_eff = 2 x sum over the singular involutions of "
            "chi(K3) = 48 n -- the Kummer K3 surfaces transverse to the "
            "singular loci, once per shadow -- which is 144 at n = 3, tracks "
            "n on all 15,963 classes of phi's Joyce family, and keeps chi_eff "
            "an Euler characteristic of real objects. n_gen = chi_eff/48 = n "
            "then restates the ruled route b_2/4. The other routes stay "
            "switchable; seed_dependent is demoted (D-009 refuted both of its "
            "sub-routes on the family).\n\n"
            "Opened 2026-09-22 so the two branches can be RUN rather than "
            "argued. chi_eff = 144 is load-bearing -- n_gen is taken as "
            "chi_eff/48, alpha_leak as 1/sqrt(chi_eff/b_3), reid_invariant as "
            "1/chi_eff -- and 112 modules mention it under one of its names "
            "(measured). Three derivations are claimed and all three return 144 "
            "at b_3 = 24, which is precisely where the two b_3-dependent ones "
            "CROSS, uniquely.\n\n"
            "The default is `unruled` because adopting either branch is an "
            "author act and neither has been made. `unruled` is not a "
            "placeholder: it is what the code does today, and chi_eff_claim() "
            "returns the dichotomy rather than a value.\n\n"
            "TWO COSTS MEASURED 2026-09-22, both new, and they COUPLE this "
            "fork to n_gen_source. First, 6 b_3 / 48 = b_3 / 8 IDENTICALLY, so "
            "`seed_dependent` via route C is not an independent route to the "
            "generation count -- it IS n_gen_source = b3_over_dim_O, and "
            "inherits that route's refutation across the whole Joyce family. "
            "Second, n_gen = chi_eff/48 fails on BOTH branches on that family: "
            "seed-dependent gives a non-integer at every reachable profile "
            "(0.2552, 1.8802, 5.0052, 9.6302 via b_3^2/4), while the constant "
            "branch gives n_gen = 3 even at n_T3 = 0, where the manifold "
            "carries no A_1 families and the count should be 0.\n\n"
            "See PM.geometry.chi_eff_branches for the executable branches and "
            "the full cost table. Nothing there selects either."
        ),
        options=[
            VariantOption(
                id="k3_reading",
                summary=("chi_eff = 2 x sum chi(K3) over the singular "
                         "involutions = 48 n (D-009)"),
                consequence=(
                    "BUYS: chi_eff is an Euler characteristic of real objects "
                    "on Y_7 -- one Kummer K3 per singular involution, with "
                    "16 fixed points resolved to chi = 24 -- doubled for the "
                    "two shadows. It follows the geometry (48 n tracks n on "
                    "every class of phi's Joyce family) and equals 144 on the "
                    "adopted point, so the consumers of 144 keep their value "
                    "with a derivation behind it.\n"
                    "COSTS: n_gen = chi_eff/48 is then the SAME statement as "
                    "n_gen = n (= b_2/4 on the all-plain members), not an "
                    "independent route, and it says nothing about chirality, "
                    "which stays open."
                ),
                adopted=True,
            ),
            VariantOption(
                id="unruled",
                summary="no route adopted; chi_eff_claim returns the dichotomy",
                consequence=(
                    "BUYS: the framework does not assert a derivation it "
                    "cannot defend, and both branches stay runnable and "
                    "costed. This is the honest state and it is what the code "
                    "actually does.\n"
                    "COSTS: the EML track stays blocked -- the triple-track "
                    "mismatch at FormulasRegistry.py:653 is waiting on exactly "
                    "this ruling -- and every downstream consumer keeps reading "
                    "a literal 144 whose provenance is open."
                ),
            ),
            VariantOption(
                id="constant_144",
                summary="chi_eff is a constant, independent of the seed",
                consequence=(
                    "BUYS: every consumer of the literal 144 keeps working "
                    "unchanged, at either seed, and nothing downstream moves.\n"
                    "COSTS: chi_eff carries NO topological content, and this is "
                    "demonstrated rather than interpreted -- n_gen = "
                    "chi_eff/48 = 3 at every reachable profile INCLUDING "
                    "n_T3 = 0, where there are no A_1 families and the "
                    "generation count should be 0. Routes B and C are then "
                    "both wrong, and the three-derivation agreement at 144 was "
                    "never evidence."
                ),
            ),
            VariantOption(
                id="seed_dependent",
                summary="chi_eff = f(b_3), so it is not 144 off b_3 = 24",
                consequence=(
                    "BUYS: chi_eff becomes a genuine function of the topology "
                    "rather than a constant, so it can carry topological "
                    "content at all.\n"
                    "COSTS: it is not 144 on the 43 path -- 462.25 via b_3^2/4 "
                    "or 258 via 6 b_3 -- so every consumer of the literal "
                    "moves, across 112 modules that mention it. Worse, n_gen = "
                    "chi_eff/48 is then NON-INTEGER at every Joyce-reachable "
                    "profile on both sub-routes, so adopting this also forces "
                    "a ruling on n_gen_source. The two b_3-dependent routes "
                    "also disagree with each other everywhere except b_3 = 24, "
                    "so this branch is not one option but two."
                ),
                status=DISABLED,
            ),
        ],
    ),
    "twisted_norm_convention": Fork(
        id="twisted_norm_convention",
        question=(
            "Is a family's twisted representative the SUM over its orbit of "
            "T^3 components, or the average?"
        ),
        source=("simulations.PM.geometry.metric_pairing."
                "_resolve_orbit_convention"),
        status="OPEN",
        read_adopted=_twisted_norm_convention_adopted,
        notes=(
            "Opened 2026-09-21 while computing K_IJ. Each of the 12 A1 "
            "families is an ORBIT of T^3 components -- orbit_size is read live "
            "from intersection_tensor.sector_families() and is 4 at the "
            "canonical point -- and the class that survives the quotient is "
            "built from the whole orbit. Whether the representative is the sum "
            "over the orbit or its average is a NORMALISATION the framework "
            "has never fixed, and it multiplies every twisted diagonal entry "
            "of K_IJ by the orbit size.\n\n"
            "This is a fork rather than a choice because writing either factor "
            "into metric_pairing would have been an invented constant. It is "
            "wired: metric_pairing._resolve_orbit_convention consults it and "
            "twisted_block_entry consumes the result, so flipping it moves "
            "every twisted entry of the 43 x 43 matrix.\n\n"
            "NEITHER BRANCH CHANGES THE ISOTROPY VERDICT, measured: the flat "
            "entries go as L^7 and the twisted ones as L^3 under both, so K is "
            "not proportional to the identity either way. What moves is the "
            "RATIO between the blocks, which is what any downstream "
            "normalisation of the twisted sector would consume."
        ),
        options=[
            VariantOption(
                id="orbit_sum",
                summary="representative is the sum over the family's orbit",
                consequence=(
                    "BUYS: the representative is the honest push-forward of a "
                    "single component's form to the quotient, which is what "
                    "'the class of the exceptional divisor' normally means, "
                    "and it keeps the twisted entries integral multiples of "
                    "8 pi^2 L^3.\n"
                    "COSTS: the twisted entries carry a factor equal to the "
                    "orbit size, so they are not comparable across families "
                    "with different orbit sizes without dividing it back out. "
                    "At the canonical point every orbit has size 4, so this "
                    "cost is invisible there and would only appear at a point "
                    "with mixed orbit sizes -- which is exactly the kind of "
                    "hidden dependence a fork is for."
                ),
                adopted=True,
            ),
            VariantOption(
                id="orbit_average",
                summary="representative is normalised per component",
                consequence=(
                    "BUYS: twisted entries that are directly comparable across "
                    "families whatever their orbit sizes, and a K_IJ whose "
                    "twisted block is Vol(T^3) * 8 pi^2 with no group order in "
                    "it at all.\n"
                    "COSTS: the representative is no longer the push-forward "
                    "of a component's form, so its periods are divided by the "
                    "orbit size and it is not an integral class. Any later "
                    "comparison against an intersection number -- including "
                    "the -2 that eguchi_hanson reproduces -- would have to "
                    "restore the factor."
                ),
            ),
        ],
    ),
}
