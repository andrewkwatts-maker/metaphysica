"""What the model takes from standard physics, what it postulates, what it has
found, what it corrected, and what is open -- one list every surface renders.

WHY THIS EXISTS
===============
The author asked that paper, website and beginner guide all tell the same
top-down story: standard physics first (cited), then how the geometry is
selected and why, then the model's own postulates, findings, corrections and
open problems. Written separately, those surfaces drift; this registry is the
single place the story lives, in the same spirit as the certificate
(closed_geometry): a row names its kind, states itself in two registers
(technical and plain), and points at its evidence -- a verified reference for
STANDARD, a test for FINDING, a decision-log entry for everything the model
decided.

KINDS
=====
STANDARD    established physics or mathematics the model USES, cited to a
            verified source. Never a claim of the model.
POSTULATE   an assumption the model MAKES that standard physics does not
            (labelled as such wherever it is stated).
FINDING     a result the model's own computation establishes, with its test.
CORRECTION  an earlier claim of the model that was wrong, and what replaced it.
OPEN        a problem that is still open, with its honest status.
RULING      a decision that is the author's, with the lead's recommendation.

Reference keys point into references.REFERENCES (verified before use). A
STANDARD row whose source has not yet been verified carries
`verified=False` and must not be rendered as cited until it is.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from metaphysica.simulations.PM.geometry.closed_geometry.references import (
    REF_ACHARYA_1996,
    REF_ACHARYA_1999,
    REF_ADV_2005,
    REF_ARMSTRONG,
    REF_JOYCE_1996,
    REF_JOYCE_1996_II,
    REF_JOYCE_2000,
    REF_LUKAS_MORRIS,
)

__all__ = ["Provenance", "PROVENANCE", "by_kind", "KINDS"]

KINDS = ("STANDARD", "POSTULATE", "FINDING", "CORRECTION", "OPEN", "RULING")


@dataclass(frozen=True)
class Provenance:
    id: str
    kind: str
    technical: str
    plain: str
    references: Tuple[str, ...] = ()
    evidence: str = ""                # test id, module, or decision-log entry
    verified: bool = True             # False: a source still to be checked


PROVENANCE: Tuple[Provenance, ...] = (
    # ------------------------------------------------------------ STANDARD
    Provenance(
        "g2-compactification", "STANDARD",
        "M-theory on a compact 7-manifold with holonomy G2 gives 4D N = 1 "
        "supergravity with b_2 abelian vector multiplets and b_3 neutral "
        "chiral multiplets.",
        "Curling up seven extra dimensions into a special shape called a G2 "
        "manifold leaves a four-dimensional world with a fixed set of force "
        "carriers and shape parameters, counted by the shape's holes.",
        (REF_ACHARYA_1999, REF_LUKAS_MORRIS),
        "CG.5 y7-gauge-content"),
    Provenance(
        "joyce-construction", "STANDARD",
        "Compact 7-manifolds with a torsion-free G2-structure are obtained by resolving T^7/Gamma "
        "with Eguchi-Hanson spaces; the (Z/2)^3 example has b_2 = 12, "
        "b_3 = 43, and further examples include b_2 = 8 + l, b_3 = 47 - l.",
        "Joyce built the first such shapes by folding a seven-dimensional "
        "doughnut with mirror symmetries and smoothing out the creases.",
        (REF_JOYCE_1996, REF_JOYCE_1996_II, REF_JOYCE_2000),
        "tests/test_joyce_reachability.py"),
    Provenance(
        "holonomy-pi1", "STANDARD",
        "For a compact torsion-free G2-structure, Hol = G2 iff pi_1 is "
        "finite (Joyce, JDG II, Prop. 1.1.1).",
        "A shape has the full G2 character exactly when it has no loops that "
        "cannot be shrunk away.",
        (REF_JOYCE_1996_II,),
        "CG.4 y7-fundamental-group"),
    Provenance(
        "armstrong", "STANDARD",
        "pi_1 of a quotient space is the group modulo the subgroup generated "
        "by elements with fixed points.",
        "When folding a space, every fold that has a fixed crease lets loops "
        "through it be shrunk.",
        (REF_ARMSTRONG,),
        "CG.4 y7-fundamental-group"),
    Provenance(
        "local-sym", "STANDARD",
        "An A1 singularity fibred over a 3-manifold Q carries pure "
        "N = (1 + b_1(Q)) super Yang-Mills.",
        "The kind of force living on a crease is set by how many loops the "
        "crease itself has.",
        (REF_ACHARYA_1999,),
        "CG.5 y7-gauge-content"),
    Provenance(
        "flux-no-go", "STANDARD",
        "G4 flux on a smooth G2 manifold gives a positive runaway potential; "
        "a supersymmetric vacuum needs a non-real Chern-Simons invariant.",
        "Magnetic-like fluxes alone push the extra dimensions to grow for "
        "ever instead of settling.",
        (REF_ADV_2005, REF_LUKAS_MORRIS),
        "CG.6 y7-flux-potential-runaway"),
    Provenance(
        "heterotic-dual", "STANDARD",
        "M-theory on Joyce manifolds, as K3 fibrations, is dual to heterotic "
        "strings on T^3-fibred Calabi-Yau threefolds.",
        "The same physics can be described by a different kind of string "
        "theory, which may help with the open problems.",
        (REF_ACHARYA_1996,),
        "D-011"),
    Provenance(
        "two-time-physics", "STANDARD",
        "Two-time physics with an Sp(2,R) gauge symmetry removing the "
        "relative time (Bars). The model borrows its shape only; the "
        "ghost-freedom theorem is not inherited (signature ruling "
        "2026-08-31).",
        "A framework in which a second time direction is made harmless by a "
        "symmetry. The model borrows the idea but not the proof.",
        (), "canonical_values bulk entry", verified=False),
    # ------------------------------------------------------------ POSTULATE
    Provenance(
        "bulk-26d", "POSTULATE",
        "The bulk is 26-dimensional with signature (24,2), one time per 13D "
        "shadow of signature (12,1).",
        "The model starts from a 26-dimensional space with two time "
        "directions, split into two mirror halves.",
        (), "canonical_values bulk entry (rulings 2026-08-19, 2026-08-31)"),
    Provenance(
        "bridges", "POSTULATE",
        "Twelve bridges: the directed edges of K4 on a Fano arc of four faces, "
        "grouped into three E8 blocks.",
        "Twelve links connect the two halves, grouped in three sets of four.",
        (), "docs/BRIDGE_CHANNEL_ASSIGNMENT.md (site repo)"),
    Provenance(
        "wa1", "POSTULATE",
        "WA-1 (adopted 2026-10-01): one bridge per resolved A1 component "
        "(one U(1)). With the 3 x 4 bridge-component match it selects "
        "(b_2, b_3) = (12, 43) without data (CG.12).",
        "Each link is identified with one smoothed-out crease of the "
        "internal shape, and that identification picks out the shape.",
        (), "D-008; ruled D-015"),
    # ------------------------------------------------------------ FINDING
    Provenance(
        "reachable-set", "FINDING",
        "Joyce's construction from phi's diagonal (Z/2)^3 reaches 28 "
        "literature-checked (b_2, b_3); the off-path seed b_3 = 24 is not among them.",
        "Only certain hole-counts are possible; the old value 24 is not one.",
        (REF_JOYCE_1996_II,), "CG.7 joyce-reachable-set"),
    Provenance(
        "holonomy-ladder", "FINDING",
        "Across the family, restricted holonomy is trivial, SU(2), SU(3), G2 "
        "for n = 0..3 singular involutions; pi_1 is finite only at n = 3.",
        "As more creases appear, the shape climbs a ladder of richness; only "
        "the top rung is fully G2.",
        (REF_JOYCE_1996_II,), "tests/test_family_topology.py"),
    Provenance(
        "bridge-component-map", "FINDING",
        "The 12 bridges and the 12 A1 components form one 3 x 4 structure, "
        "existing exactly on the all-plain members; blocks match involutions "
        "canonically, while the matching inside a block is a free choice.",
        "The twelve links and the twelve creases match one-to-one, and only "
        "for the adopted shape.",
        (), "tests/test_bridge_component_map.py"),
    Provenance(
        "k3-reading", "FINDING",
        "chi_eff = 2 x sum over singular involutions of chi(Kummer K3) = 48n; "
        "n_gen = chi_eff/48 counts singular involutions (adopted "
        "2026-10-01).",
        "The number 144 counts hidden K3 surfaces: three in each mirror "
        "half, each contributing 24, taken once for each half.",
        (), "tests/test_kummer_index.py"),
    Provenance(
        "confinement-exclusion", "FINDING",
        "In phi's Joyce family, holonomy exactly G2 and a confining gauge "
        "sector are mutually exclusive.",
        "The shape that is fully G2 cannot also host the force usually used "
        "to pin its size.",
        (REF_ACHARYA_1999,), "tests/test_gauge_sectors.py"),
    # ------------------------------------------------------------ CORRECTION
    Provenance(
        "split-form", "CORRECTION",
        "The adopted 3-form was the split real form, one transcription sign "
        "away from the framework's own octonion product. The compact form is "
        "the active path since 2026-10-01; the split form stays switchable.",
        "A sign error made the internal shape the wrong kind; fixing it "
        "changes no number.",
        (), "D-003"),
    Provenance(
        "a1-filter", "CORRECTION",
        "The A1 filter tested the setwise stabiliser; the four-member family "
        "was the all-plain subfamily of Joyce's construction.",
        "An over-strict check had hidden most of the possible shapes.",
        (REF_JOYCE_1996_II,), "D-006"),
    Provenance(
        "k-gimel-layer", "CORRECTION",
        "Constants built on k_gimel = b_3/2 + 1/pi were fits made at the "
        "retired seed, not derivations.",
        "Several headline numbers were tuned, not predicted.",
        (), "D-007"),
    Provenance(
        "chi-eff-label", "CORRECTION",
        "chi_eff = 144 was called the Euler characteristic of the G2 "
        "manifold. Every closed odd-dimensional manifold has chi = 0, so "
        "chi_eff is an effective index, now defined by the K3 reading, "
        "48 n (adopted 2026-10-01).",
        "A number called the shape's Euler characteristic was not one: that "
        "value is zero, and what 144 counts is still being decided.",
        (), "D-009; CG.2"),
    Provenance(
        "tcs-construction", "CORRECTION",
        "The internal space was formerly described as a twisted connected "
        "sum ('TCS #187') with b_3 = 24. No published TCS enumeration has such "
        "an entry, and b_3 = 24 lies below the published TCS ranges. The "
        "construction is Joyce's orbifold resolution, which reaches "
        "b_3 = 43 and never 24.",
        "The internal shape was once said to be glued from two pieces, a "
        "construction that cannot give the old numbers. It is built by "
        "folding and smoothing instead.",
        (REF_JOYCE_1996_II,), "CG.7; canonical_values tcs_obstruction"),
    Provenance(
        "racetrack-type", "CORRECTION",
        "The racetrack exponent a = 2 pi / b_3 read a Betti number as the "
        "rank of a gauge group. Y_7's singular loci carry N = 4 super "
        "Yang-Mills, and with full holonomy no confining sector exists in "
        "phi's Joyce family, so Y_7 has no gaugino racetrack; its values "
        "were calibrations at the off-path seed.",
        "A mechanism once used to fix the size of the extra dimensions "
        "needs a kind of force this shape does not have.",
        (REF_ACHARYA_1999,), "D-005; CG.5; CG.10"),
    Provenance(
        "two-time-claims", "CORRECTION",
        "Two borrowed claims were withdrawn (signature ruling 2026-08-31): "
        "Bars' Sp(2,R) ghost-freedom theorem, because gauging (24,2) gives "
        "one (23,1) shadow rather than two (12,1) shadows; and "
        "'26 = the bosonic critical dimension', because with two times the "
        "critical dimension is 27-28.",
        "Two results borrowed from other theories turned out not to apply "
        "to this model's two time directions, and were withdrawn.",
        (), "canonical_values bulk entry (signature ruling 2026-08-31)"),
    # ------------------------------------------------------------ OPEN
    Provenance(
        "chirality", "OPEN",
        "No chiral matter inside Y_7: disjoint singular loci leave no "
        "codimension-7 points.",
        "The internal shape alone cannot yet make matter tell left from right.",
        (REF_ACHARYA_1996,), "D-011"),
    Provenance(
        "moduli", "OPEN",
        "The 43 moduli, Re(T) included, are unfixed at leading order; Re(T) "
        "is an open modulus, and values that need it use a labelled "
        "calibration.",
        "The size and shape of the extra dimensions are not yet pinned.",
        (REF_ADV_2005,), "D-005, D-010"),
    Provenance(
        "dark-energy", "OPEN",
        "The leading-order flux potential cannot accelerate the universe "
        "(slope >= 5 sqrt(2/7)).",
        "The model does not yet explain dark energy.",
        (), "D-010"),
    Provenance(
        "flavour", "OPEN",
        "Flavour structure awaits a chiral sector.",
        "Why particles come in different masses is not yet derived.",
        (), "D-011"),
    Provenance(
        "second-time", "OPEN",
        "Ghost control of the second time direction has no computed "
        "backing, and Nahm's bound on supersymmetric theories with one time "
        "(at most 11 dimensions) must be evaded by the 13D(12,1) shadows.",
        "Having two time directions raises consistency questions the model "
        "has not yet answered.",
        (), "canonical_values bulk entry (signature ruling 2026-08-31)"),
)


def by_kind(kind: str) -> List[Provenance]:
    return [p for p in PROVENANCE if p.kind == kind]
