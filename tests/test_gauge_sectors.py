"""Full holonomy and a confining sector are mutually exclusive in phi's Joyce
family (C2), and the flux potential is too steep to accelerate (C3). D-010.

Pre-registered 2026-09-30 in the site repo's docs/DECISION_LOG.md. MEASURED
the same day on the first generating triple: loci with b_1(Q) = 0 -- the only
ones carrying pure, confining N = 1 SYM -- occur only at n = 1 (7 classes);
every n = 3 class has smallest b_1 equal to 1 or 3. The canonical slope
|grad V|/V never fell below 5 sqrt(2/7) ~ 2.673 (minimum 2.72 over 60
samples), far above the acceleration threshold sqrt(2).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.simulations.PM.geometry.flux_vacuum import (
    acceleration_report,
)
from metaphysica.simulations.PM.geometry.gauge_sectors import (
    confinement_sweep,
)


@pytest.fixture(scope="module")
def sweep():
    return confinement_sweep()


def test_confining_loci_exist_only_without_full_holonomy(sweep):
    assert sweep["n_with_a_confining_locus"] == [1]
    assert not sweep["full_holonomy_can_confine"]
    assert sweep["min_b1_by_n"][3] == {1: 84, 3: 280}


def test_the_sweep_can_find_a_confining_locus(sweep):
    """The check has teeth: b_1 = 0 loci do exist, just not at n = 3."""
    assert sweep["min_b1_by_n"][1].get(0) == 7


def test_the_flux_potential_cannot_accelerate():
    rep = acceleration_report()
    assert rep["bound_respected"]
    assert not rep["can_accelerate"]
    assert rep["bound"] > rep["acceleration_threshold"]
