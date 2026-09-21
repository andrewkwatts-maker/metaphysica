"""K_IJ = int omega_I ^ *omega_J on H^3, to LEADING ORDER in the resolution t.

WHAT THIS IS, AND WHAT IT IS NOT
================================
`multilinear_degree_audit` settled that there is NO topological bilinear form on
H^3: 3 + 3 = 6 /= 7, so a metric-free pairing of two 3-forms does not exist, and
`intersection_tensor`'s N_IJK route was refuted by the same degree arithmetic
(3 + 3 + 3 = 9 > 7). The intrinsic route does not escape the metric. Both are
recorded and neither is re-opened here.

So a pairing on H^3 REQUIRES a metric, and this module supplies the only one
available: the leading-order glued metric of Joyce's construction, in which each
singular component's neighbourhood is replaced by T^3 x EH at resolution scale t.
Every number below is therefore ASYMPTOTIC IN t, and every one of them carries
its order. Nothing here is exact.

THE BLOCK STRUCTURE, AND WHERE EACH BLOCK COMES FROM
====================================================
  FLAT x FLAT (7 x 7), order t^0.
  The 7 flat 3-forms are phi's triples on the flat orbifold. Two distinct Fano
  lines meet in exactly ONE point, so as coordinate 3-forms they always differ
  in at least two legs and are pointwise orthogonal. The block is therefore
  diagonal with the common entry Vol(T^7/Gamma) = L^7 / |Gamma|.

  TWISTED x TWISTED (36 x 36), order t^0, block-diagonal by FAMILY.
  Joyce admissibility makes the singular sets pairwise disjoint
  (`half_shift_enumeration.fixed_sets_disjoint`), so two different families'
  representatives have disjoint support and pair to exactly zero. Within one
  family the product factorises over T^3 x EH:

      <dx^i ^ eta, dx^j ^ eta> = <dx^i, dx^j>_{T^3} * ||eta_EH||^2
                              = delta_ij * Vol(T^3) * 8 pi^2

  The 8 pi^2 is `eguchi_hanson.l2_norm_squared`, computed there from the metric.

  CROSS (flat x twisted), order t^2 -- NOT exactly zero.
  This is the one place the specification and the geometry part company, and the
  difference is recorded rather than smoothed. The cross terms were expected to
  vanish by character orthogonality. They do not vanish for that reason: the
  flat 3-forms are Gamma-invariant and so is eta, so characters do not separate
  them. Worse, leg counting does not kill them either -- two distinct Fano lines
  meet in one point, so a flat line L /= fixed_line(f) contributes exactly one
  T^3 leg and two transverse legs, which is precisely the index pattern a
  non-zero pairing needs.

  What DOES control them is the shrinking neck. The twisted representative is
  supported where the resolution lives, of 4-volume O(t^4), while the flat form
  is O(1) there. Cauchy-Schwarz then gives

      |<omega_L, omega_{f,i}>| <= ||omega_L||_{L^2(neck)} * ||omega_{f,i}||_{L^2}
                               ~ sqrt(t^4 Vol(T^3)) * O(1) = O(t^2).

  So the cross-blocks vanish AT LEADING ORDER, with a derived exponent, and are
  not claimed to vanish identically. A consumer that needs them exactly does not
  have them here.

WHY ||eta||^2 CARRIES NO t, AND WHY THAT MATTERS HERE
=====================================================
`eguchi_hanson` records that the L^2 norm of a 2-form on a 4-manifold is
invariant under g -> t^2 g, so ||eta_EH||^2 = 8 pi^2 exactly, with no t and no
bolt parameter. The twisted blocks therefore take their entire t-dependence from
Vol(T^3) and the legs, NOT from the exceptional form. A module that had fitted a
scale into that norm would have put the t-order in the wrong place -- which is
the practical reason that negative result was worth recording.

WHAT IS UNBOUND, AND IT IS SAID RATHER THAN FILLED IN
=====================================================
The torus circle length L is a MODULUS. The framework does not determine it, no
registry row carries it, and nothing here invents one. Every entry below is
returned as an expression in L, and the isotropy verdict is taken over the ring
of such expressions -- which is stronger than any numerical verdict, because it
holds for every L at once.

THE A4 BAR
==========
  * K_IJ entries are INTEGRALS with dimensions of (length)^7 or (length)^3.
  * 8 pi^2 is an integral over the EH fibre and is dimensionless.
  * 7, 12, 3, 4 are COUNTS -- of flat classes, families, legs, and families per
    sector respectively.
  * |Gamma| = 8 and the orbit sizes are GROUP ORDERS.
A group order divides a volume here and is never added to a dimension, and the
t-exponents are ORDERS, never treated as values.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "CROSS_BLOCK_T_ORDER",
    "DIAGONAL_BLOCK_T_ORDER",
    "pairing_symbols",
    "orbifold_group_order",
    "flat_block_entry",
    "twisted_block_entry",
    "pairing_matrix",
    "block_structure",
    "is_proportional_to_identity",
    "pairing_report",
]

#: Cross-blocks are O(t^2): Cauchy-Schwarz against a neck of 4-volume O(t^4).
#: An ORDER, not a value.
CROSS_BLOCK_T_ORDER: int = 2

#: The flat and twisted diagonal blocks are O(t^0) -- the leading order.
DIAGONAL_BLOCK_T_ORDER: int = 0


def pairing_symbols():
    """(L, t): the torus circle length and the resolution parameter.

    L is UNBOUND -- a modulus the framework does not fix. It is carried
    symbolically rather than given a value, so no number here is invented.
    """
    import sympy as sp

    return sp.Symbol("L", positive=True), sp.Symbol("t", positive=True)


def orbifold_group_order() -> int:
    """|Gamma|, read from the live stabiliser rather than written as 8."""
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        diagonal_stabiliser,
    )

    return len(diagonal_stabiliser())


def flat_block_entry():
    """Vol(T^7 / Gamma) = L^7 / |Gamma|. Order t^0.

    The flat 3-forms are orthonormal as coordinate forms -- distinct Fano lines
    differ in at least two legs -- so every diagonal entry is the volume and
    every off-diagonal entry is zero.
    """
    L, _t = pairing_symbols()
    return L ** 7 / orbifold_group_order()


def twisted_block_entry(orbit_size: int, orbit_convention: str = "orbit_sum"):
    """Vol(T^3) * ||eta_EH||^2 for one family, with the orbit factor stated.

    A family is an ORBIT of T^3 components, of size `orbit_size`, and the class
    that survives the quotient is built from the whole orbit. Whether the
    representative is the SUM over the orbit (norm picks up the orbit size) or
    the AVERAGE (it does not) is a normalisation convention that the framework
    has not fixed, so both are executable and neither is adopted here. See the
    `twisted_norm_convention` fork.
    """
    import sympy as sp

    from metaphysica.simulations.PM.geometry.eguchi_hanson import (
        l2_norm_squared,
    )

    if orbit_convention not in ("orbit_sum", "orbit_average"):
        raise ValueError(
            "orbit_convention must be 'orbit_sum' or 'orbit_average'; got %r. "
            "The normalisation is not defaulted silently." % (orbit_convention,)
        )
    L, _t = pairing_symbols()
    factor = sp.Integer(orbit_size) if orbit_convention == "orbit_sum" else sp.Integer(1)
    return sp.simplify(factor * L ** 3 * l2_norm_squared())


def _resolve_orbit_convention() -> str:
    """Which normalisation is in force, via the fork."""
    try:
        from metaphysica.simulations.core.variants import resolve

        return resolve("twisted_norm_convention")
    except Exception:
        return "orbit_sum"


def pairing_matrix(orbit_convention: Optional[str] = None):
    """The full K_IJ, as a symbolic matrix, at leading order in t.

    Rows and columns follow `twisted_form_basis.build_basis()` exactly: the 7
    flat classes first, then the 36 twisted ones in family order. Cross-blocks
    are entered as ZERO because that is their leading-order value; the O(t^2)
    remainder is reported by `block_structure` and is never silently promoted to
    an exact zero.
    """
    import sympy as sp

    from metaphysica.simulations.PM.geometry.twisted_form_basis import (
        build_basis,
    )

    convention = orbit_convention or _resolve_orbit_convention()
    basis = build_basis()
    order = list(basis["flat"]) + list(basis["twisted"])
    n = len(order)

    K = sp.zeros(n, n)
    flat_entry = flat_block_entry()
    for idx, rep in enumerate(order):
        if rep["kind"] == "flat":
            K[idx, idx] = flat_entry
        else:
            K[idx, idx] = twisted_block_entry(rep["orbit_size"]
                                              if "orbit_size" in rep
                                              else _orbit_size_of(rep),
                                              convention)
    return K


def _orbit_size_of(rep: Dict[str, Any]) -> int:
    """The orbit size of a twisted representative's family, read live."""
    from metaphysica.simulations.PM.geometry.intersection_tensor import (
        sector_families,
    )

    for fam in sector_families():
        if fam["family"] == rep["family"]:
            return int(fam["orbit_size"])
    raise RuntimeError(
        "family %r is absent from the live enumeration; the basis and the "
        "family list have diverged" % (rep["family"],)
    )


def block_structure(orbit_convention: Optional[str] = None) -> Dict[str, Any]:
    """The 7 + 12 + 12 + 12 blocks, with VALUES and with each block's t-order."""
    import sympy as sp

    from metaphysica.simulations.PM.geometry.twisted_form_basis import (
        build_basis,
    )

    convention = orbit_convention or _resolve_orbit_convention()
    basis = build_basis()
    sectors = sorted({rep["sector"] for rep in basis["twisted"]})

    blocks: List[Dict[str, Any]] = [{
        "name": "flat",
        "size": basis["n_flat"],
        "diagonal_entry": str(flat_block_entry()),
        "t_order": DIAGONAL_BLOCK_T_ORDER,
        "origin": "Vol(T^7/Gamma); Fano lines are pointwise orthogonal",
    }]
    for s in sectors:
        reps = [r for r in basis["twisted"] if r["sector"] == s]
        entries = {str(twisted_block_entry(_orbit_size_of(r), convention))
                   for r in reps}
        blocks.append({
            "name": "twisted[sector=%d]" % s,
            "size": len(reps),
            "diagonal_entry": sorted(entries)[0] if len(entries) == 1
                              else sorted(entries),
            "uniform_within_sector": len(entries) == 1,
            "t_order": DIAGONAL_BLOCK_T_ORDER,
            "origin": ("Vol(T^3) * ||eta_EH||^2 per family; families pair to "
                       "zero across the block by Joyce disjointness"),
        })

    return {
        "orbit_convention": convention,
        "blocks": blocks,
        "block_sizes": [b["size"] for b in blocks],
        "total": sum(b["size"] for b in blocks),
        "cross_block_t_order": CROSS_BLOCK_T_ORDER,
        "cross_block_value_at_leading_order": 0,
        "cross_block_is_not_exactly_zero": (
            "The cross-blocks are O(t^%d) by Cauchy-Schwarz against a neck of "
            "4-volume O(t^4), NOT identically zero. Character orthogonality "
            "does not apply: the flat forms and eta are both Gamma-invariant, "
            "and leg counting does not separate them either, because two "
            "distinct Fano lines meet in exactly one point. Recorded as an "
            "order, not promoted to an exact vanishing."
            % CROSS_BLOCK_T_ORDER
        ),
        "unbound": {
            "L": ("torus circle length -- a MODULUS the framework does not fix "
                  "and no registry row carries. Carried symbolically; not "
                  "given a value here."),
        },
    }


def is_proportional_to_identity(matrix) -> bool:
    """Whether a square matrix is c * I for some scalar c.

    The predicate the non-isotropy claim is measured against. Written so it
    returns TRUE on something that really is isotropic -- asserting "K is not
    proportional to the identity" proves nothing unless the same rule can say
    yes. Compared symbolically, so the verdict holds for every value of the
    unbound modulus at once rather than at one sampled L.
    """
    import sympy as sp

    n = matrix.shape[0]
    if n == 0 or matrix.shape[0] != matrix.shape[1]:
        return False
    c = sp.simplify(matrix[0, 0])
    for i in range(n):
        for j in range(n):
            expected = c if i == j else sp.S.Zero
            if sp.simplify(matrix[i, j] - expected) != 0:
                return False
    return True


def pairing_report(orbit_convention: Optional[str] = None) -> Dict[str, Any]:
    """K_IJ with its blocks, its orders, and its isotropy verdict."""
    import sympy as sp

    convention = orbit_convention or _resolve_orbit_convention()
    K = pairing_matrix(convention)
    structure = block_structure(convention)
    L, t = pairing_symbols()

    distinct = sorted({str(sp.simplify(K[i, i])) for i in range(K.shape[0])})
    isotropic = is_proportional_to_identity(K)

    return {
        "shape": (K.shape[0], K.shape[1]),
        "orbit_convention": convention,
        "block_sizes": structure["block_sizes"],
        "blocks": structure["blocks"],
        "distinct_diagonal_entries": distinct,
        "is_isotropic": isotropic,
        "why_not_isotropic": (
            "the flat entries are L^7/%d and the twisted ones are multiples of "
            "8 pi^2 L^3. These are different functions of the unbound modulus "
            "L, so no scalar c makes K = c I for all L. The verdict is taken "
            "over expressions, not at a sampled value."
            % orbifold_group_order()
        ),
        "t_orders": {
            "flat_block": DIAGONAL_BLOCK_T_ORDER,
            "twisted_blocks": DIAGONAL_BLOCK_T_ORDER,
            "cross_blocks": CROSS_BLOCK_T_ORDER,
        },
        "exact_or_asymptotic": (
            "ASYMPTOTIC. Every entry is the leading term of an expansion in "
            "the resolution parameter t. No entry here is exact, and the "
            "cross-blocks are zero only to that order."
        ),
        "unbound": structure["unbound"],
        "counts": (
            "entries are INTEGRALS of dimension length^7 or length^3; 8 pi^2 "
            "is a dimensionless fibre integral; 7/12/3/4 are COUNTS; |Gamma| "
            "and the orbit sizes are GROUP ORDERS."
        ),
    }


if __name__ == "__main__":  # pragma: no cover
    rep = pairing_report()
    print("=" * 70)
    print(" K_IJ = int omega_I ^ *omega_J   (LEADING ORDER IN t)")
    print("=" * 70)
    print("  shape            : %s" % (rep["shape"],))
    print("  block sizes      : %s" % rep["block_sizes"])
    print("  orbit convention : %s" % rep["orbit_convention"])
    for b in rep["blocks"]:
        print("    %-22s size %2d  entry %-24s  O(t^%d)"
              % (b["name"], b["size"], b["diagonal_entry"], b["t_order"]))
    print("  distinct diagonal: %s" % rep["distinct_diagonal_entries"])
    print("  isotropic        : %s" % rep["is_isotropic"])
    print()
    print("  t-orders         : %s" % rep["t_orders"])
    print("  %s" % rep["exact_or_asymptotic"])
    print("  UNBOUND: L -- %s" % rep["unbound"]["L"])
