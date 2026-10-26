"""The observer report is reproducible.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from metaphysica.simulations.PM.validation.observer_integrator import \
    ObserverIntegrator


def _results(seed):
    return ObserverIntegrator(n_measurements=20, seed=seed).generate_report()["results"]


def test_same_seed_gives_the_same_results():
    """Unseeded, mass_variation changed every build and path runs counted it."""
    assert _results(0) == _results(0)


def test_the_seed_reaches_the_sampling():
    assert _results(0) != _results(1)
