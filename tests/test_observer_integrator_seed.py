"""The observer and unitary reports are reproducible.

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


def _unitary(seed):
    from metaphysica.simulations.PM.validation.unitary_closure_checker import \
        UnitaryClosureChecker
    report = UnitaryClosureChecker(n_test_states=20, seed=seed).generate_report()
    return {k: v for k, v in report.items() if "date" not in k and "time" not in k}


def test_unitary_report_is_reproducible():
    """Unseeded, unitary_report.json changed on every build."""
    assert _unitary(0) == _unitary(0)
