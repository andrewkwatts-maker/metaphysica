"""The transverse structure of each singular involution IS an orbifold-limit Kummer K3.

WHAT IS BEING CLAIMED, AND AT WHICH TYPE
========================================
Each singular involution of Gamma negates 4 of the 7 coordinates and fixes a
T^3. TRANSVERSE to that fixed T^3 the local model is T^4/Z_2 -- the orbifold
limit of the Kummer K3, whose minimal resolution carries exactly 16 A_1 points.

Measured at the canonical point, each singular involution carries **4 families
x orbit size 4 = 16 fixed tori on the COVER**, and the counts are 16 / 16 / 16
across the three singular involutions. That matches Kummer's 16 exactly.

THE A4 BAR, AND IT IS THE WHOLE POINT HERE
==========================================
Two different sixteens are being compared and they live on different spaces:

    16 fixed T^3 on the COVER        components of the fixed locus of the
                                     involution upstairs on T^7, counted as
                                     4 families x orbit size 4. These are
                                     SUBMANIFOLDS OF THE COVER.

    16 A_1 points on the QUOTIENT    the singular points of T^4/Z_2, one per
                                     2-torsion point of T^4. These are POINTS
                                     OF THE QUOTIENT.

The correspondence is **T^3 x (A_1 point)**, family by family: each fixed T^3
upstairs sits over one A_1 point of the transverse T^4/Z_2. They are equal in
number because they are the same index set seen on the two sides of the
quotient map, NOT because two independent counts happened to agree.

The 16 downstairs is derived here rather than cited: a Z_2 acting as -1 on
T^4 = R^4/Z^4 fixes exactly the half-lattice points, of which there are
2^4 = 16.

WHAT THIS IS NOT
================
NOT a global K3 fibration, and it does NOT license a TCS reading. The register
refuted that separately: TCS glues asymptotically cylindrical CY3 x S^1 pieces
along a K3 fibre with a Donaldson matching, and b_3 = 43 sits outside the TCS
range 71-155, which the register uses as an independent exclusion. This is the
LOCAL TRANSVERSE structure of Joyce's construction, now measured.

CHI(K3) = 24, AND WHAT IT IS ALLOWED TO DO
==========================================
The Euler characteristic is computed from the construction, not quoted:

    chi(K3) = (chi(T^4) - 16)/2 + 16 * chi(P^1) = (0 - 16)/2 + 16*2 = 24

That gives chi_eff a geometric entry point at 24. Whether any defect-count
expression through 24 reaches 144 is a question for `chi_eff_routes` to COST
under the trials-factor discipline -- an ENTRY in the enumeration, never a
derivation. **The ruling on chi_eff remains the author's** and nothing here
selects a branch.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

__all__ = [
    "TRANSVERSE_DIM",
    "KUMMER_A1_POINTS",
    "fixed_tori_per_involution",
    "kummer_fixed_points",
    "chi_k3_from_kummer",
    "transverse_report",
]

#: The involution negates 4 of 7 coordinates, so the transverse model is 4D.
TRANSVERSE_DIM: int = 4

#: 2^4 -- the 2-torsion points of T^4, DERIVED in `kummer_fixed_points`.
KUMMER_A1_POINTS: int = 2 ** TRANSVERSE_DIM


def kummer_fixed_points(dim: int = TRANSVERSE_DIM) -> Dict[str, Any]:
    """How many points -1 fixes on T^dim = R^dim/Z^dim, derived by enumeration.

    x is fixed iff -x = x mod Z^dim, i.e. 2x in Z^dim, i.e. every coordinate is
    0 or 1/2. Enumerated rather than asserted so the 2^dim is a count of things
    rather than a formula restated.
    """
    import itertools

    points = list(itertools.product((0.0, 0.5), repeat=dim))
    return {
        "dim": dim,
        "n_fixed_points": len(points),
        "matches_two_to_the_dim": len(points) == 2 ** dim,
        "points": points,
        "counts_what": ("POINTS of T^%d fixed by -1; after quotienting they "
                        "become A_1 singular points of T^%d/Z_2"
                        % (dim, dim)),
    }


def fixed_tori_per_involution(point: Optional[Dict[str, Any]] = None
                              ) -> List[Dict[str, Any]]:
    """Per singular involution: how many fixed T^3 it carries on the COVER.

    Read from the live enumeration through `sector_families`, so a change to
    phi or to admissibility moves this. The count is sum of ORBIT SIZES over
    the involution's families -- 4 families of orbit size 4 at the canonical
    point -- and not the family count, which is 4.
    """
    from metaphysica.simulations.PM.geometry.intersection_tensor import (
        sector_families,
    )

    by_sector: Dict[int, List[Dict[str, Any]]] = {}
    for fam in sector_families(point):
        by_sector.setdefault(fam["sector"], []).append(fam)

    out = []
    for sector, fams in sorted(by_sector.items()):
        n_tori = sum(f["orbit_size"] for f in fams)
        out.append({
            "sector": sector,
            "fixed_line": fams[0]["fixed_line"],
            "moved_arc": fams[0]["moved_arc"],
            "n_families": len(fams),
            "orbit_sizes": [f["orbit_size"] for f in fams],
            "n_fixed_tori_on_cover": n_tori,
            "matches_kummer_16": n_tori == KUMMER_A1_POINTS,
            "counts_what": ("n_fixed_tori_on_cover counts COMPONENTS OF THE "
                            "FIXED LOCUS upstairs on T^7; n_families counts "
                            "ORBITS of those components"),
        })
    return out


def chi_k3_from_kummer(dim: int = TRANSVERSE_DIM) -> Dict[str, Any]:
    """chi(K3) from the Kummer construction, computed rather than quoted.

        chi(T^4/Z_2 resolved) = (chi(T^4) - n)/2 + n * chi(P^1)

    with n the fixed-point count. chi(T^4) = 0, chi(P^1) = 2. Each A_1 point is
    replaced by an exceptional P^1, and the smooth part of T^4 double-covers
    the smooth part of the quotient, which is the /2.
    """
    n = kummer_fixed_points(dim)["n_fixed_points"]
    chi_torus = 0                      # chi(T^d) = 0 for every d >= 1
    chi_p1 = 2
    chi = (chi_torus - n) // 2 + n * chi_p1
    return {
        "chi_T4": chi_torus,
        "n_fixed_points": n,
        "chi_P1": chi_p1,
        "chi_K3": chi,
        "is_24": chi == 24,
        "derivation": ("(chi(T^4) - 16)/2 + 16 * chi(P^1) = (0 - 16)/2 + 32 "
                       "= 24"),
        "counts_what": ("an EULER CHARACTERISTIC of the resolved transverse "
                        "surface; not a count of defects and not a dimension"),
    }


def transverse_report(point: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The correspondence, with both sixteens named and kept apart."""
    per_involution = fixed_tori_per_involution(point)
    downstairs = kummer_fixed_points()
    chi = chi_k3_from_kummer()

    counts = [rec["n_fixed_tori_on_cover"] for rec in per_involution]
    all_match = all(rec["matches_kummer_16"] for rec in per_involution)

    return {
        "n_singular_involutions": len(per_involution),
        "fixed_tori_on_cover_per_involution": counts,
        "a1_points_on_quotient": downstairs["n_fixed_points"],
        "every_involution_matches_kummer": all_match,
        "per_involution": per_involution,
        "chi_k3": chi,
        "the_correspondence": (
            "T^3 x (A_1 point), family by family: each fixed T^3 upstairs sits "
            "over one A_1 point of the transverse T^4/Z_2. The two sixteens are "
            "the same index set seen on the two sides of the quotient map."
        ),
        "a4_bar": (
            "16 fixed T^3 counts COMPONENTS OF THE FIXED LOCUS ON THE COVER "
            "(4 orbits x orbit size 4); 16 A_1 counts POINTS OF THE QUOTIENT "
            "T^4/Z_2. Equal integers, different spaces, and the equality is a "
            "correspondence of index sets rather than two counts agreeing."
        ),
        "scope": (
            "LOCAL and TRANSVERSE. This is not a global K3 fibration and does "
            "not license a TCS reading, which the register excludes "
            "independently: b_3 = 43 lies outside the TCS range 71-155."
        ),
        "chi_eff": (
            "chi(K3) = 24 is now a geometric entry point for chi_eff. Whether "
            "any defect-count expression through it reaches 144 is for "
            "chi_eff_routes to COST under the trials-factor discipline. An "
            "entry in the enumeration, never a derivation; the ruling on "
            "chi_eff remains the author's."
        ),
    }
