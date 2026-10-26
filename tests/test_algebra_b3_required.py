"""Five algebra sims fell back to b3 = 24 when topology.elder_kads read None.
PMRegistry raises KeyError for a missing parameter, so the fallback only ran
under stub registries, where it computed silently at the off-path seed.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import importlib

import pytest

SIMS = [
    ("e7_representation", "E7RepresentationSimulation"),
    ("e8x8_splitting", "E8xE8SplittingSimulation"),
    ("freudenthal_triple", "FreudenthalTripleSimulation"),
    ("gaugino_condensation", "GauginoCondensationSimulation"),
    ("neutrino_algebraic", "NeutrinoAlgebraicSimulation"),
]


class _Unset:
    def get_param(self, path):
        return None

    def has_param(self, path):
        return False


@pytest.mark.parametrize("module, cls", SIMS)
@pytest.mark.parametrize("path", ["run", "run_eml"])
def test_unset_b3_fails_instead_of_using_24(module, cls, path):
    mod = importlib.import_module(f"metaphysica.simulations.PM.algebra.{module}")
    sim = getattr(mod, cls)()
    with pytest.raises(ValueError, match="elder_kads"):
        getattr(sim, path)(_Unset())
