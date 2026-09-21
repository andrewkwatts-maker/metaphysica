"""The 43 three-forms, as REPRESENTATIVES rather than as a count.

WHAT WAS MISSING
================
`derived_contribution_table` settles b_3 = 7 + 3 n_T3 with n_T3 in {0, 4, 8, 12},
and `b3_path` carries (b_3, b_2) = (43, 12) on the Joyce branch. Every one of
those is a COUNT. Nothing in the tree exhibited a single one of the 43 classes,
so "b_3 = 43" was a number with no objects under it, and the twisted 36 in
particular had never been written down.

This module writes them down. Each basis element is a labelled 3-form with a
POSITION -- the chart it lives in and the family whose neck supports it -- so the
43 becomes a list of things rather than an integer.

THE CONSTRUCTION, AND WHERE EACH PIECE COMES FROM
=================================================
  FLAT (7).  The Gamma-invariant coordinate 3-forms, read from
  `joyce_orbifold.invariant_three_forms` (R3/R5). These are exactly phi's own
  triples, which is R5's content: the 7 coordinate characters realise the 7
  non-trivial characters of (Z/2)^3 bijectively, so the invariant 3-forms are
  the lines of the Fano plane on the coordinate index set. They live on the
  torus chart and have constant coefficients.

  TWISTED (3 per family).  Joyce's resolution replaces a neighbourhood of each
  singular component by T^3 x (resolved C^2/Z_2) = T^3 x EH. On that piece a
  3-form is built by wedging one of the THREE 1-forms of the T^3 against the
  EH exceptional 2-form:

      omega_{f,i} = dx^i ^ eta_EH,    i ranging over family f's T^3 directions.

  The T^3 directions are not chosen here: family f's `fixed_line` is the set of
  coordinates its involution FIXES, which R2 establishes is a Fano line -- three
  coordinates, hence three legs, hence the 3 in 7 + 3 n_T3. The 12 families are
  read live from `intersection_tensor.sector_families()` and are never
  tabulated: change phi or the admissibility conditions and this list moves.

THE NECK CHART, STATED EXPLICITLY
=================================
A family's involution fixes 3 coordinates and moves 4. In the neck chart the 3
fixed coordinates stay torus coordinates, and the 4 MOVED ones are the transverse
C^2/Z_2, replaced after resolution by the four Eguchi-Hanson coordinates
(r, theta, phi, psi) in the order of the sorted moved set. So a twisted
representative is a genuine 7-dimensional 3-form; it is simply written in a
different chart from the flat ones, which is what "position-dependent
representative" means and why the two families are labelled rather than merged.

WHAT IS AND IS NOT CLAIMED
==========================
CLAIMED: these 43 forms are closed, they are distinct, they carry the labels
that assign each to a family and a chart, and their count is 7 + 3 n_T3 for
every admissible profile.

NOT CLAIMED: that they are L^2-orthonormal harmonic representatives of the
resolved metric, or that they are independent in cohomology. Joyce's gluing
corrects each by an exact form of size O(t); these are the LEADING-ORDER
representatives and every consumer must carry that order. `metric_pairing`
(M4) labels its blocks accordingly and this module never drops the label.

THE A4 BAR
==========
This produces OBJECTS -- differential forms of degree 3 -- and counts them. The
43 is a DIMENSION of a span of representatives, the 12 is a count of FAMILIES,
the 3 is a count of COORDINATE DIRECTIONS in a fixed line, and the 4 is a count
of families per sector. No count here is converted into a different kind.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "N_COORDS",
    "LEGS_PER_FAMILY",
    "ADMISSIBLE_N_T3",
    "basis_dimension",
    "neck_chart",
    "flat_representatives",
    "twisted_representatives",
    "build_basis",
    "basis_is_closed",
    "basis_report",
]

#: The torus is T^7. A DIMENSION.
N_COORDS: int = 7

#: Each family contributes one twisted 3-form per T^3 direction, and its T^3 is
#: the involution's fixed line -- three coordinates (R2). A count of COORDINATE
#: DIRECTIONS, and the 3 in b_3 = 7 + 3 n_T3.
LEGS_PER_FAMILY: int = 3

#: n_T3 values a Joyce (Z/2)^3 resolution can reach, from
#: derived_contribution_table. Four singular involutions' worth of families each.
ADMISSIBLE_N_T3: Tuple[int, ...] = (0, 4, 8, 12)


def basis_dimension(n_t3: int, n_flat: Optional[int] = None) -> int:
    """b_3 = n_flat + 3 n_T3, with n_flat read from the orbifold, not assumed.

    Kept as a function of n_T3 so the parametric check over profiles has
    something to compare against that is not the construction itself.
    """
    if n_flat is None:
        from metaphysica.simulations.PM.geometry.joyce_orbifold import (
            invariant_three_forms,
        )

        n_flat = len(invariant_three_forms())
    return n_flat + LEGS_PER_FAMILY * n_t3


def neck_chart(fixed_line: Sequence[int], moved_arc: Sequence[int]):
    """The 7 coordinate symbols of one family's neck chart.

    The 3 fixed coordinates keep torus symbols x_i; the 4 moved coordinates
    become the Eguchi-Hanson symbols (r, theta, phi, psi), in the order of the
    sorted moved set. Returns (symbols, eh_slots), where `eh_slots` maps each EH
    axis 0..3 to the coordinate index it occupies.
    """
    import sympy as sp

    from metaphysica.simulations.PM.geometry.eguchi_hanson import symbols as eh_symbols

    r, theta, phi, psi, _a = eh_symbols()
    eh_axis = [r, theta, phi, psi]

    coords: List[Any] = [None] * N_COORDS
    for i in fixed_line:
        coords[i] = sp.Symbol("x%d" % i, real=True)
    eh_slots: Dict[int, int] = {}
    for axis, i in enumerate(sorted(moved_arc)):
        coords[i] = eh_axis[axis]
        eh_slots[axis] = i

    missing = [i for i, c in enumerate(coords) if c is None]
    if missing:
        raise RuntimeError(
            "coordinates %s are in neither the fixed line %s nor the moved arc "
            "%s; the involution no longer partitions the seven coordinates and "
            "R2 has broken" % (missing, tuple(fixed_line), tuple(moved_arc))
        )
    return coords, eh_slots


def flat_representatives() -> List[Dict[str, Any]]:
    """The 7 flat 3-forms: phi's triples, on the torus chart.

    Coefficients are sympy Integers rather than floats so that the closedness
    check runs through the symbolic exterior derivative, which refuses floats.
    """
    import sympy as sp

    from metaphysica.simulations.PM.geometry.exterior_algebra import Form
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        invariant_three_forms,
    )

    out: List[Dict[str, Any]] = []
    for triple in invariant_three_forms():
        key = tuple(sorted(triple))
        out.append({
            "kind": "flat",
            "index": len(out),
            "triple": key,
            "chart": "torus",
            "family": None,
            "sector": None,
            "leg": None,
            "form": Form(dim=N_COORDS, degree=3,
                         components={key: sp.Integer(1)}),
            "coords": [sp.Symbol("x%d" % i, real=True)
                       for i in range(N_COORDS)],
        })
    return out


def twisted_representatives(families: Optional[Sequence[Dict[str, Any]]] = None
                            ) -> List[Dict[str, Any]]:
    """Three 3-forms per family: dx^i ^ eta_EH, i over the family's T^3.

    The families are read from the live enumeration. The EH 2-form is the one
    `eguchi_hanson.exceptional_two_form` builds -- closed, normalisable, and
    anti-self-dual in the hyperkahler orientation -- re-indexed from its own
    4D chart into the four moved slots of the 7D neck chart.
    """
    from metaphysica.simulations.PM.geometry.eguchi_hanson import (
        exceptional_two_form,
    )
    from metaphysica.simulations.PM.geometry.exterior_algebra import Form, wedge
    from metaphysica.simulations.PM.geometry.intersection_tensor import (
        sector_families,
    )
    import sympy as sp

    families = families if families is not None else sector_families()
    eta4 = exceptional_two_form()

    out: List[Dict[str, Any]] = []
    for fam in families:
        fixed = tuple(fam["fixed_line"])
        moved = tuple(fam["moved_arc"])
        coords, eh_slots = neck_chart(fixed, moved)

        # Lift eta from its 4D chart into the 7D neck chart.
        lifted = Form.from_terms(
            N_COORDS, 2,
            [(tuple(eh_slots[axis] for axis in key), val)
             for key, val in eta4.components.items()],
        )

        for leg_position, i in enumerate(fixed):
            leg = Form(dim=N_COORDS, degree=1,
                       components={(i,): sp.Integer(1)})
            out.append({
                "kind": "twisted",
                "index": len(out),
                "family": fam["family"],
                "sector": fam["sector"],
                "leg": i,
                "leg_position": leg_position,
                "fixed_line": fixed,
                "moved_arc": moved,
                "chart": "neck(family=%d)" % fam["family"],
                "form": wedge(leg, lifted),
                "coords": coords,
            })
    return out


def build_basis(n_sectors: Optional[int] = None) -> Dict[str, Any]:
    """The full basis, optionally restricted to the first `n_sectors` sectors.

    Restricting by SECTOR rather than by family is what makes the profile sweep
    meaningful: each singular involution carries a whole block of families, so
    the admissible n_T3 values are exactly 4 x (number of singular involutions).
    Passing n_sectors = 2 therefore models the n_T3 = 8 profile and must give
    7 + 12 + 12.
    """
    from metaphysica.simulations.PM.geometry.intersection_tensor import (
        sector_families,
    )

    families = sector_families()
    sectors = sorted({f["sector"] for f in families})
    if n_sectors is not None:
        if not 0 <= n_sectors <= len(sectors):
            raise ValueError(
                "n_sectors must lie in 0..%d for the live enumeration; got %r"
                % (len(sectors), n_sectors)
            )
        keep = set(sectors[:n_sectors])
        families = [f for f in families if f["sector"] in keep]

    flat = flat_representatives()
    twisted = twisted_representatives(families)

    per_sector: Dict[int, int] = {}
    for rep in twisted:
        per_sector[rep["sector"]] = per_sector.get(rep["sector"], 0) + 1

    n_t3 = len(families)
    return {
        "n_sectors": len(({f["sector"] for f in families})),
        "n_families": n_t3,
        "n_t3": n_t3,
        "flat": flat,
        "twisted": twisted,
        "n_flat": len(flat),
        "n_twisted": len(twisted),
        "dimension": len(flat) + len(twisted),
        "expected_dimension": basis_dimension(n_t3, len(flat)),
        "twisted_per_sector": per_sector,
        "blocks": [len(flat)] + [per_sector[s] for s in sorted(per_sector)],
    }


def basis_is_closed(basis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Every representative must satisfy d(omega) = 0, symbolically.

    Runs the real exterior derivative on each of the 43, in that element's own
    chart. The flat ones close because their coefficients are constant; the
    twisted ones close because eta_EH is closed and the leg is a constant
    1-form. Both are STRUCTURAL zeros -- empty component maps.
    """
    from metaphysica.simulations.PM.geometry.exterior_algebra import exterior_d

    basis = basis or build_basis()
    failures: List[Dict[str, Any]] = []
    for rep in list(basis["flat"]) + list(basis["twisted"]):
        d = exterior_d(rep["form"], rep["coords"])
        if not d.is_zero():
            failures.append({"kind": rep["kind"], "index": rep["index"],
                             "residual": {str(k): str(v)
                                          for k, v in d.components.items()}})
    return {
        "n_checked": basis["dimension"],
        "all_closed": not failures,
        "failures": failures,
        "closure_is_structural": (
            "exterior_d returns empty component maps; it refuses float "
            "coefficients, so no stub can pass this."
        ),
    }


def basis_report() -> Dict[str, Any]:
    """The basis at every admissible profile, with what each number counts."""
    from metaphysica.simulations.PM.geometry.intersection_tensor import (
        sector_families,
    )

    live_sectors = len({f["sector"] for f in sector_families()})
    profiles = []
    for k in range(live_sectors + 1):
        b = build_basis(n_sectors=k)
        profiles.append({
            "n_sectors": k,
            "n_t3": b["n_t3"],
            "dimension": b["dimension"],
            "expected_dimension": b["expected_dimension"],
            "blocks": b["blocks"],
            "agrees": b["dimension"] == b["expected_dimension"],
        })

    full = build_basis()
    closure = basis_is_closed(full)
    return {
        "live_sectors": live_sectors,
        "profiles": profiles,
        "full_dimension": full["dimension"],
        "full_blocks": full["blocks"],
        "all_closed": closure["all_closed"],
        "admissible_n_t3": ADMISSIBLE_N_T3,
        "order_in_t": (
            "LEADING ORDER. These are the model representatives on the glued "
            "pieces; Joyce's construction corrects each by an exact form of "
            "size O(t). Nothing here is exact in t and no consumer may treat "
            "it as such."
        ),
        "counts": (
            "43 is a DIMENSION of a span of representatives; 12 counts "
            "FAMILIES; 3 counts COORDINATE DIRECTIONS in a fixed line; 4 "
            "counts families per sector. None is converted into another."
        ),
    }


if __name__ == "__main__":  # pragma: no cover
    rep = basis_report()
    print("=" * 70)
    print(" THE 43 THREE-FORMS, as representatives")
    print("=" * 70)
    for p in rep["profiles"]:
        print("  sectors=%d  n_T3=%2d  dim=%2d  blocks=%-18s agrees=%s"
              % (p["n_sectors"], p["n_t3"], p["dimension"],
                 str(p["blocks"]), p["agrees"]))
    print()
    print("  full dimension : %d   blocks %s"
          % (rep["full_dimension"], rep["full_blocks"]))
    print("  all closed     : %s" % rep["all_closed"])
    print()
    print("  ORDER: %s" % rep["order_in_t"])
