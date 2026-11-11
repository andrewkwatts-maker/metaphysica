"""XV-16: the DE plane gate scores the registered (w0, wa), not -(b3-1)/b3.

w0 is registered by the dark_energy_betti fork (-(n-1)/n); the gate used to
recompute it as -(B3-1)/B3 at the live b3, which on seed_43_joyce gave -42/43
while the register holds -(n-1)/n at the fork's n. Expected values below come
from the fork readers and the seed reader, never typed.
"""
from __future__ import annotations

import math

import pytest

from metaphysica.simulations.core.variants import selection
from metaphysica.simulations.PM.cosmology.late_time_routes import (
    de_betti_n,
    resolve_de_betti,
)
from metaphysica.simulations.PM.geometry.b3_path import resolve_path, seed_values
from metaphysica.simulations.PM.validation.de_plane_gate import framework_point


def _registered_point() -> dict:
    n = de_betti_n(resolve_de_betti())
    b3 = seed_values(resolve_path())[0]
    return {"w0": -(n - 1) / n, "wa": -1.0 / math.sqrt(b3)}


def test_point_is_the_registered_point_on_the_active_path():
    expected = _registered_point()
    p = framework_point()
    assert p["w0"] == pytest.approx(expected["w0"], abs=1e-12)
    assert p["wa"] == pytest.approx(expected["wa"], abs=1e-12)


def test_w0_follows_the_dark_energy_betti_fork_not_b3():
    """Under a frozen fork option w0 is -(n-1)/n at that n, whatever b3 is."""
    b3 = seed_values(resolve_path())[0]
    for option in ("b3_24", "bridges_12"):
        n = de_betti_n(option)
        with selection.forced({"dark_energy_betti": option}):
            w0 = framework_point()["w0"]
        assert w0 == pytest.approx(-(n - 1) / n, abs=1e-12)
        if n != b3:
            assert w0 != pytest.approx(-(b3 - 1) / b3, abs=1e-9)


def test_b3_live_option_uses_the_live_b3():
    with selection.forced({"dark_energy_betti": "b3_live"}):
        b3 = seed_values(resolve_path())[0]
        w0 = framework_point()["w0"]
    assert w0 == pytest.approx(-(b3 - 1) / b3, abs=1e-12)
