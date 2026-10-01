"""Does Y_7 carry a Harvey-Moore instanton cycle? (C2, PR-1)

Pre-registered as PR-1 in D-017 (site repo docs/DECISION_LOG.md, 2026-10-01)
before this was run; D-016 records why it was needed.

THE QUESTION
============
Harvey-Moore M2 instantons need an associative 3-cycle that is RIGID and a
RATIONAL HOMOLOGY SPHERE. The candidates counted here are the totally geodesic
associatives of the flat orbifold T^7/Gamma that avoid its singular set:

    N = (T_L + c) / S,      S = { g in Gamma : g(T_L + c) = T_L + c }

with L a Fano line (the associative coordinate 3-planes of the flat phi are
exactly its seven lines) and c a transverse offset. One row per (L, c):

  * b_1(N) = the L-coordinates on which every element of S acts by +1
    (translations act trivially on constant forms);
  * rigid  = no transverse coordinate on which every element of S acts by +1.
    The McLean operator of a flat T^3 is constant-coefficient and elliptic, so
    its kernel is the constant normal fields; N keeps the S-invariant ones,
    (V^perp)^S;
  * free   = no non-identity element of S fixes a point of T_L + c. An element
    outside S carries T_L + c to a disjoint parallel torus, so free is the same
    as avoiding the singular set.

Every element of Gamma flips 0 or 2 coordinates of every line (checked per
census), so N is orientable and b_1 = 0 makes it a rational homology sphere.

THE LEMMA THE COUNT TESTS
=========================
The seven coordinates carry the seven non-trivial characters of Gamma, one
each, so dim (R^7)^S = 8/|S| - 1 on every subgroup S (7, 3, 1, 0 for
|S| = 1, 2, 4, 8). Since (R^7)^S = V^S + (V^perp)^S, "rigid and b_1 = 0"
forces S = Gamma, and then a singular involution (n >= 1) lies in S with zero
shift on its fixed coordinates, so it fixes points of T_L + c.
Prediction: no row qualifies.

THE OFFSETS
===========
The quarter lattice, 4^4 = 256 offsets per line, in quarter units. An element
that flips a transverse coordinate a preserves c_a only on the quarter lattice,
so an offset off it in some a has every element of S fixing a: not rigid. The
quarter lattice therefore holds every row that could qualify, and a qualifying
row needs S = Gamma, whose invariant 3-planes are coordinate ones -- so the
seven Fano lines are all the planes that could qualify too.

SCOPE
=====
Compact form only: T^7/Gamma for the canonical point and the pairwise-disjoint
classes of the first generating triple. Totally geodesic associatives away from
the singular set only. Non-flat associatives are NOT covered; the known ones of
this resolution are S^1 x S^2 with b_1 = 1 (Dwivedi-Platt-Walpuski, CMP 401
(2023), Ex. 4.9).

A4: b_1 counts cohomology classes, |S| counts group elements, rows count
(line, offset) pairs. None is converted into another.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import functools
import itertools
from collections import Counter
from fractions import Fraction
from typing import Any, Dict, List, Tuple

__all__ = [
    "subgroup_identity",
    "flat_associative_census",
    "instanton_cycle_sweep",
]

_N = 7
_OFFSETS = tuple(itertools.product(range(4), repeat=4))   # quarter units


@functools.lru_cache(maxsize=None)
def _fano_lines() -> Tuple[Tuple[int, ...], ...]:
    from metaphysica.simulations.PM.geometry.arc_flag_structure import (
        fano_lines,
    )

    return tuple(sorted(tuple(sorted(line)) for line in fano_lines()))


def subgroup_identity() -> Dict[str, Any]:
    """dim (R^7)^S = |Gamma|/|S| - 1 on every subgroup S of Gamma."""
    from metaphysica.simulations.PM.geometry.joyce_orbifold import (
        diagonal_stabiliser,
    )

    group = [tuple(g) for g in diagonal_stabiliser()]
    ident = tuple([1] * _N)
    others = [g for g in group if g != ident]
    rows = []
    for k in range(len(others) + 1):
        for subset in itertools.combinations(others, k):
            members = {ident, *subset}
            if any(tuple(x * y for x, y in zip(a, b)) not in members
                   for a in members for b in members):
                continue
            rows.append({
                "order": len(members),
                "invariant_dim": sum(1 for a in range(_N)
                                     if all(g[a] > 0 for g in members)),
                "predicted": len(group) // len(members) - 1,
            })
    orders = Counter(r["order"] for r in rows)
    return {
        "subgroups": len(rows),
        "by_order": dict(sorted(orders.items())),
        "invariant_dim_by_order": {
            o: sorted({r["invariant_dim"] for r in rows if r["order"] == o})
            for o in sorted(orders)},
        "holds": len(rows) == 16 and all(
            r["invariant_dim"] == r["predicted"] for r in rows),
    }


def _line_tables(elems, line):
    """Bitmasks over the element list for one line: which elements keep each
    transverse coordinate at each quarter value, which flip each coordinate,
    and which non-identity elements fix a point of T_L + c once they map it to
    itself (zero shift on every L-coordinate they fix)."""
    transverse = tuple(a for a in range(_N) if a not in line)
    keeps = [[0] * 4 for _ in transverse]
    flips = [0] * _N
    fixes = 0
    for i, (eps, s) in enumerate(elems):
        bit = 1 << i
        for k, a in enumerate(transverse):
            for q in range(4):
                # x_a = q/4 goes to eps q/4 + s/2 (shifts in half units)
                if (eps[a] * q + 2 * s[a] - q) % 4 == 0:
                    keeps[k][q] |= bit
        for a in range(_N):
            if eps[a] < 0:
                flips[a] |= bit
        moves = any(e < 0 for e in eps) or any(s)
        if moves and all(s[b] == 0 for b in line if eps[b] > 0):
            fixes |= bit
    return transverse, keeps, flips, fixes


def _verdict(stab, line, transverse, flips, fixes) -> Dict[str, Any]:
    normal = sum(1 for a in transverse if not stab & flips[a])
    return {
        "order": bin(stab).count("1"),
        "b1": sum(1 for b in line if not stab & flips[b]),
        "normal_invariant": normal,
        "rigid": normal == 0,
        "free": not stab & fixes,
    }


def flat_associative_census(point: Dict[str, Any],
                            keep_rows: bool = True) -> Dict[str, Any]:
    """One row per Fano line and quarter-lattice offset: |S|, b_1, rigid,
    free. A row QUALIFIES when b_1 = 0, rigid and free."""
    elems = list(point["elements"].values())
    lines = _fano_lines()
    keys = ("rows", "b1_zero", "rigid", "free", "rigid_and_b1_zero",
            "rigid_and_free", "b1_zero_and_free", "qualifying")
    tally = dict.fromkeys(keys, 0)
    by_order: Counter = Counter()
    qualifying_orders = set()
    identity_ok = True
    rows: List[Dict[str, Any]] = []
    for line in lines:
        transverse, keeps, flips, fixes = _line_tables(elems, line)
        k0, k1, k2, k3 = keeps
        stabs = [k0[q0] & k1[q1] & k2[q2] & k3[q3]
                 for q0, q1, q2, q3 in _OFFSETS]
        verdicts = {}
        for stab, mult in Counter(stabs).items():
            v = verdicts[stab] = _verdict(stab, line, transverse, flips, fixes)
            identity_ok &= (v["b1"] + v["normal_invariant"]
                            == len(elems) // v["order"] - 1)
            b1_zero = v["b1"] == 0
            by_order[v["order"]] += mult
            for key, hit in (("rows", True), ("b1_zero", b1_zero),
                             ("rigid", v["rigid"]), ("free", v["free"]),
                             ("rigid_and_b1_zero", v["rigid"] and b1_zero),
                             ("rigid_and_free", v["rigid"] and v["free"]),
                             ("b1_zero_and_free", b1_zero and v["free"]),
                             ("qualifying",
                              b1_zero and v["rigid"] and v["free"])):
                tally[key] += mult * hit
            if v["rigid"] and b1_zero:
                qualifying_orders.add(v["order"])
        if keep_rows:
            for c, stab in zip(_OFFSETS, stabs):
                v = verdicts[stab]
                rows.append({
                    "line": line,
                    "offset": tuple(Fraction(q, 4) for q in c),
                    "order": v["order"],
                    "b1": v["b1"],
                    "rigid": v["rigid"],
                    "free": v["free"],
                    "qualifies": v["b1"] == 0 and v["rigid"] and v["free"],
                })
    out: Dict[str, Any] = {
        "n_rows": tally["rows"],
        "by_order": dict(sorted(by_order.items())),
        **{k: tally[k] for k in keys[1:]},
        "orders_of_rigid_b1_zero_rows": sorted(qualifying_orders),
        "identity_holds_on_every_row": identity_ok,
        "every_quotient_orientable": all(
            sum(1 for b in line if eps[b] < 0) % 2 == 0
            for eps, _s in elems for line in lines),
        "counts": "rows: (Fano line, offset) pairs; order: group elements",
    }
    if keep_rows:
        out["rows"] = rows
        out["qualifying_rows"] = [r for r in rows if r["qualifies"]]
    return out


def instanton_cycle_sweep() -> Dict[str, Any]:
    """The census on the canonical point and on every n >= 1 pairwise-disjoint
    class of the first generating triple (the class loop of
    gauge_sectors.confinement_sweep)."""
    from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
        _group,
        _non_identity,
        assignments,
        elements,
        fixed_sets_disjoint,
        generating_triples,
        is_singular,
    )
    from metaphysica.simulations.PM.geometry.intersection_tensor import (
        canonical_point,
    )

    group = _group()
    nz = _non_identity(group)
    triple = generating_triples(group)[0]
    gens = [nz[i] for i in triple]
    per_class: List[Dict[str, Any]] = []
    by_n: Dict[int, Dict[str, Any]] = {}
    summed = ("n_rows", "qualifying", "rigid_and_b1_zero", "rigid_and_free",
              "b1_zero_and_free")
    for svecs in assignments(triple, group, include_relative=True):
        els = elements(gens, svecs)
        singular = [(b, e) for b, e in els.items()
                    if b != (0, 0, 0) and is_singular(e)]
        if not singular or not all(
                fixed_sets_disjoint(a[1], b[1])
                for a, b in itertools.combinations(singular, 2)):
            continue
        census = flat_associative_census({"elements": els}, keep_rows=False)
        n = len(singular)
        per_class.append({"shifts": svecs, "n": n,
                          "qualifying": census["qualifying"],
                          "rigid_and_b1_zero": census["rigid_and_b1_zero"]})
        agg = by_n.setdefault(n, {"classes": 0, **dict.fromkeys(summed, 0),
                                  "identity_held": True,
                                  "orientable": True})
        agg["classes"] += 1
        for key in summed:
            agg[key] += census[key]
        agg["identity_held"] &= census["identity_holds_on_every_row"]
        agg["orientable"] &= census["every_quotient_orientable"]

    canon = canonical_point()
    canon_census = flat_associative_census(canon, keep_rows=False)
    canon_in_sweep = (tuple(canon["triple"]) == tuple(triple) and any(
        c["shifts"] == tuple(canon["shifts"]) for c in per_class))
    qualifying = sum(c["qualifying"] for c in per_class)
    if not canon_in_sweep:
        qualifying += canon_census["qualifying"]
    identity = subgroup_identity()
    return {
        "classes": len(per_class),
        "rows": sum(a["n_rows"] for a in by_n.values()),
        "by_n": {n: by_n[n] for n in sorted(by_n)},
        "per_class": per_class,
        "per_class_qualifying": dict(sorted(
            Counter(c["qualifying"] for c in per_class).items())),
        "canonical": {k: v for k, v in canon_census.items()},
        "canonical_in_sweep": canon_in_sweep,
        "qualifying": qualifying,
        "subgroup_identity_holds": identity["holds"],
        "prediction_holds": qualifying == 0,
        "kill_fired": qualifying > 0 or not identity["holds"],
    }
