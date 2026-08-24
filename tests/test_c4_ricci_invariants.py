"""Physics-invariant gate for the C4 Ricci-flow cosmology kernel.

WHY THIS EXISTS
---------------
tests/test_rust_python_parity.py proves the Rust kernels agree with the
Python fallbacks — but parity only proves Rust matches Python's step logic.
If both drift the same way, parity stays green. An ODE solver needs at least
one check against PHYSICS rather than against its own twin.

WHAT THE KERNEL ACTUALLY RETURNS (learned the hard way)
-------------------------------------------------------
The first draft of this file asserted H(z) grows with redshift — true of the
expansion RATE, and the gate promptly failed on 20 of 20 steps. That failure
was the gate working: py_ricci_flow_solve does not return H(z). It returns
the framework's EFFECTIVE H0 as a function of the probe's redshift — the
Ricci-flow "unwinding" that is this model's entire Hubble-tension mechanism:

    H0_eff(0)     = 73.04    (late-time / SH0ES-like boundary)
    H0_eff(10)    = 67.61
    H0_eff(100)   = 67.40
    H0_eff(1100)  = 67.4000  (recombination -> the Planck value, exactly)

So the honest invariants are: monotone DECREASE with z, the given late-time
boundary at z = 0, and a floor that lands on the early-universe anchor at
recombination. The 67.4 below is desi.H0 / Planck 2018 — an anchor already
in the registry, not an invented threshold.

Skips when the Rust extension is absent; the parity suite covers the
Rust-vs-Python relationship separately.
"""
from __future__ import annotations

import pytest

try:
    from metaphysica._dispatch import _HAS_RUST
except ImportError:  # pragma: no cover
    _HAS_RUST = False

pytestmark = pytest.mark.skipif(not _HAS_RUST, reason="Rust extension not built")

#: Late-time boundary handed to the solver (SH0ES-like, registry anchor).
_H0_LATE = 73.04
#: Early-universe H0 — Planck 2018 / desi.H0 registry anchor.
_H0_EARLY = 67.4


def _solve(z_values, b3: float = 24.0, h0_late: float = _H0_LATE):
    from metaphysica._physica_core import py_ricci_flow_solve

    return py_ricci_flow_solve(list(z_values), h0_late, b3)


def test_solution_is_finite():
    h = _solve([i / 10.0 for i in range(0, 21)])
    assert all(v == v and abs(v) != float("inf") for v in h), (
        "NaN/inf in the Ricci-flow solution — step control failed silently"
    )


def test_late_time_boundary_is_honoured():
    h = _solve([0.0])
    assert h[0] == pytest.approx(_H0_LATE, rel=1e-3)


def test_unwinding_is_monotone_decreasing():
    """Effective H0 must fall from the late value toward the early one.

    An increase anywhere means the unwinding mechanism ran backwards —
    which would invert the framework's own explanation of the tension.
    """
    z = [i / 4.0 for i in range(0, 41)]  # 0 .. 10
    h = _solve(z)
    rises = [(a, b) for a, b in zip(h, h[1:]) if b > a + 1e-12]
    assert not rises, f"H0_eff increases with z at {len(rises)} step(s)"


def test_recombination_lands_on_the_planck_anchor():
    """The mechanism's whole point: early probes must infer ~67.4.

    If this drifts, the framework no longer reconciles the tension it
    claims to reconcile — regardless of what the parity suite says.
    """
    h = _solve([0.0, 1100.0])
    assert h[1] == pytest.approx(_H0_EARLY, abs=0.01)


def test_solution_stays_inside_the_physical_band():
    """No value may overshoot the boundary or undershoot the floor."""
    h = _solve([i / 2.0 for i in range(0, 41)])  # 0 .. 20
    assert all(_H0_EARLY - 0.01 <= v <= _H0_LATE + 0.01 for v in h)


def test_solution_depends_on_b3():
    """Mutation-style: changing the topological seed must change the curve.

    Guards the fake-gate failure mode — a function that ignores its physics
    input passes every smooth-curve check while computing nothing.
    """
    z = [i / 2.0 for i in range(0, 9)]
    h24 = _solve(z, b3=24.0)
    h12 = _solve(z, b3=12.0)
    assert max(abs(a - b) for a, b in zip(h24, h12)) > 1e-6, (
        "identical curves for b3 = 24 and b3 = 12 — the kernel is not "
        "consuming its topological input"
    )


def test_boundary_condition_can_fail():
    """The gate itself must be falsifiable: a different late-time boundary
    must move the curve."""
    h_a = _solve([0.0], h0_late=73.04)
    h_b = _solve([0.0], h0_late=67.4)
    assert h_a[0] != pytest.approx(h_b[0], rel=1e-4)
