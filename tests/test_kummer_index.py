"""The K3 reading of chi_eff: 2 x (one Kummer K3 per singular involution)
= 48 n, so n_gen = chi_eff/48 counts singular involutions (D-009).

Pre-registered 2026-09-30 in the site repo's docs/DECISION_LOG.md after the
consumer inventory and before this computation. MEASURED the same day: at the
adopted point each singular involution fixes 16 transverse points (counted,
not assumed) and its resolution has chi = 24 both from the quotient and from
Betti numbers (b_2 = 22); chi_eff = 144, n_gen = 3. Over all 15,963
pairwise-disjoint classes of the first generating triple the reading equals n
every time, while b_2/4 = n holds for only 15,963 of the 26,155 reachable
(class, pair) combinations.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from metaphysica.simulations.PM.geometry.intersection_tensor import (
    canonical_point,
)
from metaphysica.simulations.PM.geometry.kummer_index import (
    family_sweep,
    k3_reading,
    kummer_betti,
    kummer_euler,
)


def test_a_kummer_surface_has_euler_characteristic_24_two_ways():
    assert kummer_euler(16) == 24
    betti = kummer_betti(16)
    assert betti[2] == 22
    assert sum((-1) ** k * b for k, b in betti.items()) == 24


def test_the_count_can_fail():
    """A quotient with a different fixed-point count is not a Kummer K3."""
    assert kummer_euler(8) != 24


def test_the_adopted_point_gives_144_and_three():
    r = k3_reading(canonical_point())
    assert [row["fixed_points"] for row in r["kummer"]] == [16, 16, 16]
    assert r["per_shadow"] == 72 and r["chi_eff"] == 144
    assert r["n_gen"] == Fraction(3) and r["consistent"]


@pytest.fixture(scope="module")
def sweep():
    return family_sweep()


def test_the_k3_reading_equals_n_on_every_class(sweep):
    assert sweep["holds"], sweep["k3_failures"]
    assert sweep["classes"] == sweep["k3_reading_equals_n"] == 15963


def test_b2_over_4_counts_involutions_only_on_some_pairs(sweep):
    assert sweep["reachable_pairs_checked"] == 26155
    assert sweep["b2_over_4_equals_n"] == 15963
