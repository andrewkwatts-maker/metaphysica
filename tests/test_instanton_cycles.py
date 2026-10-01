"""PR-1 (D-017): no Harvey-Moore instanton cycle among the flat associatives of
Y_7's orbifold.

Pre-registered 2026-10-01 in the site repo's docs/DECISION_LOG.md before any
computation. MEASURED the same day: dim (R^7)^S = 8/|S| - 1 on all 16
subgroups; over the canonical point and all 9,667 n >= 1 pairwise-disjoint
classes of the first generating triple (17,323,264 rows) no row is b_1 = 0,
rigid and free. Rigid b_1 = 0 rows occur (S = Gamma, 16 rows in each of 245
classes) and none is free. The canonical point has no S = Gamma row at all.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from metaphysica.simulations.PM.geometry.half_shift_enumeration import (
    _compose,
)
from metaphysica.simulations.PM.geometry.instanton_cycles import (
    flat_associative_census,
    instanton_cycle_sweep,
    subgroup_identity,
)
from metaphysica.simulations.PM.geometry.intersection_tensor import (
    canonical_point,
)

FANO = {(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6),
        (2, 4, 5)}
_QUARTERS = tuple(Fraction(q, 4) for q in range(4))


def test_the_subgroup_identity_holds_on_all_16_subgroups():
    r = subgroup_identity()
    assert r["holds"]
    assert r["by_order"] == {1: 1, 2: 7, 4: 7, 8: 1}
    assert r["invariant_dim_by_order"] == {1: [7], 2: [3], 4: [1], 8: [0]}


@pytest.fixture(scope="module")
def canonical():
    return flat_associative_census(canonical_point())


def test_the_census_on_the_canonical_point(canonical):
    assert canonical["n_rows"] == 7 * 256
    assert {r["line"] for r in canonical["rows"]} == FANO
    assert canonical["by_order"] == {1: 656, 2: 944, 4: 192}
    assert (canonical["b1_zero"], canonical["rigid"],
            canonical["free"]) == (128, 112, 768)
    assert canonical["rigid_and_b1_zero"] == 0
    assert canonical["qualifying"] == 0 and canonical["qualifying_rows"] == []
    assert canonical["identity_holds_on_every_row"]
    assert canonical["every_quotient_orientable"]


def _brute_row(elems, line, offset):
    """The row from the definitions, in exact arithmetic: S by mapping the
    torus, fixed points searched on the quarter lattice of each coordinate
    (the action is diagonal, so the torus has one iff every coordinate does)."""
    transverse = [a for a in range(7) if a not in line]
    stab = [(eps, s) for eps, s in elems
            if all((eps[a] * c + Fraction(s[a], 2) - c) % 1 == 0
                   for a, c in zip(transverse, offset))]

    def fixes_a_point(eps, s):
        return all(any((eps[b] * x + Fraction(s[b], 2) - x) % 1 == 0
                       for x in _QUARTERS) for b in line)

    moving = [(eps, s) for eps, s in stab
              if any(e < 0 for e in eps) or any(s)]
    return (len(stab),
            sum(1 for b in line if all(eps[b] > 0 for eps, _ in stab)),
            not any(all(eps[a] > 0 for eps, _ in stab) for a in transverse),
            not any(fixes_a_point(eps, s) for eps, s in moving))


def test_the_census_agrees_with_the_definitions(canonical):
    elems = list(canonical_point()["elements"].values())
    for row in canonical["rows"]:
        assert (row["order"], row["b1"], row["rigid"], row["free"]) == \
            _brute_row(elems, row["line"], row["offset"]), row


@pytest.fixture(scope="module")
def sweep():
    return instanton_cycle_sweep()


def test_no_class_carries_an_instanton_cycle(sweep):
    assert sweep["qualifying"] == 0
    assert sweep["prediction_holds"] and not sweep["kill_fired"]
    assert sweep["subgroup_identity_holds"]
    assert sweep["classes"] == 9667 and sweep["rows"] == 9667 * 1792
    assert {n: a["classes"] for n, a in sweep["by_n"].items()} == \
        {1: 6783, 2: 2520, 3: 364}
    assert sweep["per_class_qualifying"] == {0: 9667}
    assert all(a["identity_held"] and a["orientable"]
               for a in sweep["by_n"].values())
    assert sweep["canonical_in_sweep"]


def test_rigid_rational_homology_tori_exist_and_are_never_free(sweep):
    """The hypothesis is not vacuous: S = Gamma rows occur, and fail on
    freeness alone, as the lemma says."""
    assert {n: a["rigid_and_b1_zero"] for n, a in sweep["by_n"].items()} == \
        {1: 784, 2: 1344, 3: 1792}
    assert sum(c["rigid_and_b1_zero"] > 0 for c in sweep["per_class"]) == 245


def _hantzsche_wendt(shift_on_0=1):
    """By hand, outside Gamma: (Z/2)^2 acting on T_{012} as the
    Hantzsche-Wendt group (free, b_1 = 0) and flipping every transverse
    coordinate, so (R^7)^S = 0 and the line-012 tori through c = 0 are rigid."""
    ident = ((1,) * 7, (0,) * 7)
    alpha = ((1, -1, -1, -1, -1, 1, 1), (shift_on_0, 1, 0, 0, 0, 0, 0))
    beta = ((-1, 1, -1, 1, 1, -1, -1), (0, 1, 1, 0, 0, 0, 0))
    return {"elements": {(0, 0): ident, (1, 0): alpha, (0, 1): beta,
                         (1, 1): _compose(*alpha, *beta)}}


def _row(census, line, offset):
    return next(r for r in census["rows"]
                if r["line"] == line and r["offset"] == offset)


def test_the_detector_fires_on_a_hand_built_instanton_cycle():
    census = flat_associative_census(_hantzsche_wendt())
    row = _row(census, (0, 1, 2), (Fraction(0),) * 4)
    assert row["order"] == 4 and row["b1"] == 0 and row["rigid"]
    assert row["free"] and row["qualifies"]
    assert census["qualifying"] > 0
    # It escapes only because it breaks the identity (|S| = 4, invariant 0).
    assert not census["identity_holds_on_every_row"]


def test_a_fixed_point_switches_the_detector_off():
    census = flat_associative_census(_hantzsche_wendt(shift_on_0=0))
    row = _row(census, (0, 1, 2), (Fraction(0),) * 4)
    assert row["b1"] == 0 and row["rigid"] and not row["free"]
    assert not row["qualifies"]
