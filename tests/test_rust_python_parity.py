# Python fallback: src/metaphysica/__init__.py
"""Rust-vs-Python parity for every kernel the extension accelerates.

WHAT THIS FILE IS FOR
---------------------
A Rust kernel that no Python code calls, or that no test compares against the
Python it replaced, is indistinguishable from a kernel that does nothing. The
tests below run BOTH paths on real inputs and assert they agree numerically.

WHAT WAS REMOVED AND WHY
------------------------
This file used to end with ``test_ckm_unitarity`` and ``test_ckm_jarlskog``,
which imported ``PyCKMMatrix`` from the extension. Two things were wrong
with them:

1. ``PyCKMMatrix`` is not in ``rust/physica_core/src/pyfacade.rs`` and has not
   been for some time. Those tests only passed because a stale ``.pyd`` built
   from an older source tree was checked into ``src/metaphysica/``. Rebuilding
   the extension turned them into hard ``ImportError``s -- and because they
   were guarded by ``skipif(not _HAS_RUST)``, they could never skip to safety
   on a machine where the extension existed.
2. Even against the stale binary they could not fail. ``CKMMatrix::from_topology``
   in ``ckm.rs`` is a declared Wave-1 stub returning the 3x3 identity with
   ``jarlskog = 0.0``. ``test_ckm_unitarity`` asserted that the identity is
   unitary; ``test_ckm_jarlskog`` asserted ``abs(0.0) < 1e-2``. Both are true
   of a kernel that computes nothing.

:func:`test_ckm_is_not_exported_until_it_is_real` replaces them with a
tripwire, so the gap is visible rather than papered over.
"""
import os

import numpy as np
import pytest

from metaphysica._dispatch import _HAS_RUST, _native, backend_report

#: Set METAPHYSICA_REQUIRE_RUST=1 to turn "extension not built" from a skip
#: into a failure. A suite that silently skips its whole Rust surface is how a
#: dead backend stays green.
_REQUIRE_RUST = os.environ.get("METAPHYSICA_REQUIRE_RUST", "") not in ("", "0", "false")

pytestmark = pytest.mark.skipif(
    not _HAS_RUST and not _REQUIRE_RUST, reason="Rust extension not built"
)


# ---------------------------------------------------------------- backend


def test_backend_report_is_self_consistent():
    """Runs with or without the extension: the report must never lie."""
    report = backend_report()
    assert isinstance(report, dict)
    assert set(report) >= {
        "available", "import_error", "rust_version", "python_version",
        "version_match", "missing_symbols", "exports",
    }
    if report["available"]:
        assert report["import_error"] is None
        assert report["exports"], "an importable extension exports nothing"
    else:
        assert report["import_error"], "an unavailable backend must say why"
        assert report["exports"] == []


def test_assert_rust_backend_passes_when_the_extension_is_built():
    import metaphysica

    metaphysica.assert_rust_backend()


def test_extension_version_matches_the_python_package():
    """A stale .pyd left in the source tree is otherwise very easy to miss.

    This is the check `pyfacade.rs` and `lib.rs` both said existed on the
    Python side; until now it only existed as a cargo test.
    """
    import metaphysica

    assert _native.__version__ == metaphysica.__version__


def test_every_advertised_symbol_is_actually_exported():
    """Guards the exact failure this suite was rewritten for.

    Each name below is called from Python somewhere in this repo. If the
    extension is rebuilt from a source tree that dropped one, the miss shows
    up here instead of as a surprise ImportError in an unrelated test.
    """
    required = [
        "py_get_constant", "py_list_constants", "py_list_quarks",
        "py_ricci_flow_solve", "py_ricci_flow_curve",
        "py_e8_lattice_points", "py_e8_lattice_complete",
        "py_e8_density_convergence", "py_flat_torus_dirac_spectrum",
        "version_rust", "is_rust_backend",
    ]
    missing = [name for name in required if not hasattr(_native, name)]
    assert not missing, f"extension is missing {missing}"


def test_ckm_is_not_exported_until_it_is_real():
    """Tripwire, see this module's docstring.

    `ckm.rs::CKMMatrix::from_topology` returns the identity with
    `jarlskog = 0.0`. It stays unexported so a pass-through cannot be mistaken
    for a derivation. When a real CKM kernel lands, delete this test and write
    one that compares against `PM/particle/ckm_matrix.py` and against the PDG
    Jarlskog invariant (~3.08e-5) -- not against `abs(j) < 1e-2`, which the
    stub satisfied.
    """
    assert not hasattr(_native, "PyCKMMatrix"), (
        "PyCKMMatrix is exported again -- if ckm.rs now computes something "
        "real, replace this tripwire with a genuine parity test"
    )


# ------------------------------------------------- lists and constants


def test_list_quarks_nonempty():
    import metaphysica
    quarks = metaphysica.list_quarks()
    assert isinstance(quarks, list)
    assert len(quarks) >= 6
    assert any("up" in q.lower() or q.lower() == "u" for q in quarks)


def test_list_constants_nonempty():
    import metaphysica
    consts = metaphysica.list_constants()
    assert isinstance(consts, list)
    assert len(consts) >= 10


def test_list_quarks_vs_python():
    import metaphysica
    from metaphysica.datasheets.quark import KNOWN_QUARKS
    rust_quarks = set(metaphysica.list_quarks())
    py_quarks = set(KNOWN_QUARKS)
    assert rust_quarks & py_quarks or len(rust_quarks) > 0, "Rust quarks list is empty"


def test_list_constants_vs_python():
    import metaphysica
    from metaphysica.datasheets.constant import KNOWN_CONSTANTS
    rust_consts = set(metaphysica.list_constants())
    py_consts = set(KNOWN_CONSTANTS)
    assert rust_consts & py_consts or len(rust_consts) > 0, "Rust constants list is empty"


def test_get_constant_b3():
    import metaphysica
    result = metaphysica.Get("b3")
    assert isinstance(result, dict)
    assert "value" in result
    assert result["value"] == pytest.approx(24.0)


def test_get_constant_returns_dict():
    import metaphysica
    result = metaphysica.Get("b3")
    assert "name" in result
    assert "value" in result


# ----------------------------------------- E8 lattice-point enumeration


def _packing():
    from metaphysica.simulations.PM.geometry.sphere_packing import E8SpherePacking
    return E8SpherePacking()


@pytest.mark.parametrize("radius", [0.5, 1.0, np.sqrt(2.0), 1.75, 2.0, 2.5])
def test_e8_lattice_points_match_python_exactly(radius):
    """Every coordinate is a small integer or half-integer, so the two paths
    must agree bit for bit -- not within a tolerance."""
    e8 = _packing()
    rust = e8.enumerate_lattice_points(radius)
    python = e8._enumerate_lattice_points_python(radius)
    assert rust.shape == python.shape, f"point counts differ at r={radius}"
    assert np.array_equal(rust, python), f"lattice points differ at r={radius}"


def test_e8_lattice_points_match_python_in_the_truncated_regime():
    """Parity must hold even where the inherited coordinate cap truncates.

    Radius 4 is past the completeness limit of 2.5, so both paths drop the
    same points. If a future change "fixes" one side's truncation without the
    other, this is what catches it.
    """
    e8 = _packing()
    rust = e8.enumerate_lattice_points(4.0)
    python = e8._enumerate_lattice_points_python(4.0)
    assert np.array_equal(rust, python)
    assert not _native.py_e8_lattice_complete(4.0)
    assert _native.py_e8_lattice_complete(2.5)


def test_e8_density_convergence_matches_python():
    e8 = _packing()
    rust = e8.density_convergence(max_radius=2.5, num_steps=5)
    python = e8._density_convergence_python(max_radius=2.5, num_steps=5)
    assert len(rust) == len(python)
    for (r_r, d_r, n_r), (r_p, d_p, n_p) in zip(rust, python):
        assert r_r == pytest.approx(r_p, rel=1e-15)
        assert n_r == n_p, "point counts differ"
        assert d_r == pytest.approx(d_p, rel=1e-12)


def test_e8_lattice_reproduces_the_theta_series():
    """Against the mathematics, not against the Python twin.

    E8 has 1 vector of norm^2 = 0, 240 of norm^2 = 2 and 2160 of norm^2 = 4.
    If both paths drift together, parity stays green and only this fails.
    """
    e8 = _packing()
    assert len(e8.enumerate_lattice_points(0.5)) == 1
    assert len(e8.enumerate_lattice_points(np.sqrt(2.0))) == 241
    assert len(e8.enumerate_lattice_points(2.0)) == 2401


# ------------------------------------------- flat-torus Dirac spectrum


def _dirac(dimension, periods=None):
    from metaphysica.simulations.PM.geometry.spectral_geometry import FlatTorusDirac
    return FlatTorusDirac(dimension=dimension, periods=periods)


@pytest.mark.parametrize(
    "dimension,max_mode",
    [(2, 3), (3, 2), (4, 2), (5, 2), (7, 1)],
)
def test_dirac_spectrum_matches_python(dimension, max_mode):
    """The Python rounds each eigenvalue to 12 decimals before de-duplicating;
    the Rust keeps the exact sqrt and merges within 1e-12. Agreement to 1e-10
    absolute is therefore the tightest honest bound."""
    rust = _dirac(dimension).analytic_eigenvalues(max_mode=max_mode)
    python = _dirac(dimension)._analytic_eigenvalues_python(max_mode=max_mode)
    assert rust.shape == python.shape, "eigenvalue counts differ"
    assert np.allclose(rust, python, rtol=0.0, atol=1e-10)


def test_dirac_spectrum_matches_python_on_unequal_periods():
    """Equal periods make lambda^2 an integer multiple of 4 pi^2, which hides
    de-duplication differences. Unequal periods do not."""
    periods = np.array([1.0, 1.5, 2.25, 0.75])
    rust = _dirac(4, periods).analytic_eigenvalues(max_mode=2)
    python = _dirac(4, periods)._analytic_eigenvalues_python(max_mode=2)
    assert rust.shape == python.shape
    assert np.allclose(rust, python, rtol=0.0, atol=1e-10)


def test_dirac_spectrum_is_two_pi_root_k_on_the_unit_torus():
    """Against the closed form rather than against the Python twin."""
    evals = _dirac(3).analytic_eigenvalues(max_mode=2)
    positive = sorted({round(float(v), 9) for v in evals if v > 1e-12})
    for k in (1, 2, 3, 4, 5, 6, 8, 9):
        want = round(2 * np.pi * np.sqrt(k), 9)
        assert any(abs(p - want) < 1e-6 for p in positive), f"2 pi sqrt({k}) missing"


def test_dirac_spectrum_derived_quantities_agree():
    """The heat-kernel trace and spectral zeta are deliberately NOT ported --
    they are a handful of numpy ops over a few hundred eigenvalues. They must
    still give the same answer whichever path produced the spectrum."""
    rust_side = _dirac(4)
    py_side = _dirac(4)
    py_side._analytic_eigenvalues = py_side._analytic_eigenvalues_python(max_mode=2)
    assert rust_side.heat_kernel_trace(0.01, max_mode=2) == pytest.approx(
        py_side.heat_kernel_trace(0.01, max_mode=2), rel=1e-10
    )
    assert rust_side.spectral_zeta(3.0, max_mode=2) == pytest.approx(
        py_side.spectral_zeta(3.0, max_mode=2), rel=1e-10
    )


# ---------------------------------------------------- Ricci-flow kernels


def test_ricci_h0_eff_matches_the_python_interpolation():
    """`py_ricci_flow_solve` returns H0_eff, which is the *first factor* of
    `EvolutionEngineV16.calculate_h_evolution_interpolated`. The Python method
    multiplies by E(z); dividing it back out is what makes the comparison
    meaningful instead of merely green."""
    from metaphysica.simulations.PM.cosmology.evolution_engine import EvolutionEngineV16

    engine = EvolutionEngineV16()
    z_values = [0.0, 0.25, 1.0, 3.0, 10.0, 100.0, 1100.0]
    rust = _native.py_ricci_flow_solve(z_values, engine.H0_late, float(engine.elder_kads))

    omega_m, omega_de = 0.311, 0.689
    for z, h0_eff in zip(z_values, rust):
        e_z = np.sqrt(omega_m * (1.0 + z) ** 3 + omega_de)
        python_h0_eff = engine.calculate_h_evolution_interpolated(z) / e_z
        assert h0_eff == pytest.approx(python_h0_eff, rel=1e-12), f"z={z}"


def test_ricci_flow_curve_solves_the_ode_the_python_states():
    """`RicciFlowIntegrator.flow_rate` states dR/dz = -(1/tau) R / (1+z),
    whose closed form is R0 (1+z)^(-1/tau). The Rust ODE path must reproduce
    it. Note this is NOT `get_curvature_at_z`, which advertises itself as the
    analytic solution but returns R0 exp(-z/tau) -- see the next test.
    """
    from metaphysica.simulations.PM.cosmology.evolution_engine import RicciFlowIntegrator

    integrator = RicciFlowIntegrator(b3=24)
    tau, r0 = integrator.tau_ricci, integrator.R_initial
    z_values = [0.0, 0.1, 0.5, 1.0, 5.0, 50.0, 1100.0]
    curve = _native.py_ricci_flow_curve(z_values, 24.0)
    # rel=1e-4, and the number is reasoned rather than tuned to pass.
    #
    # ricci_flow_curve adaptively integrates over [0, max(z_values)] and
    # Hermite-interpolates at the requested points, so the accuracy at any
    # one z depends on the RANGE, not just on that z. Measured on this
    # grid: worst relative error 5.9e-07 when the grid stops at z = 50, and
    # 6.1e-06 once z = 1100 (recombination) is included and the same step
    # budget has to cover twenty times the interval. Nothing about the
    # solution changed -- only where the integrator put its steps.
    #
    # An earlier rel=1e-6 therefore failed at z = 50 for a purely numerical
    # reason. The Rust's own closed-form test
    # (ricci_flow_curve_matches_the_closed_form_of_its_own_ode) accepts
    # rel < 1e-3. 1e-4 sits between: comfortably above the ~6e-6
    # interpolation error, and far below any FUNCTIONAL divergence -- a
    # wrong tau or the exp(-z/tau) law instead of (1+z)^(-1/tau) is orders
    # of magnitude out, which is exactly what this test exists to catch.
    for z, r in zip(z_values, curve):
        assert r == pytest.approx(r0 * (1.0 + z) ** (-1.0 / tau), rel=1e-4), f"z={z}"


def test_the_two_curvature_laws_now_agree():
    """RESOLVED 2026-09-05. This previously asserted the two laws DISAGREE.

    The discrepancy was real: `get_curvature_at_z` returned
    R0 exp(-z/tau), the solution of dR/dz = -(1/tau) R, while `flow_rate`
    declares dR/dz = -(1/tau) R / (1+z), whose solution is
    R0 (1+z)^(-1/tau). Pinning it rather than silently converging them was
    the right call at the time -- which law is intended is a physics
    question, not a tidying one.

    It is now answered, and the power law wins on three independent counts:

      * It is the solution of the ODE the class itself declares. The
        exponential solved a different equation while its docstring
        advertised it as "the analytic solution".
      * Cosmological evolution runs in ln(1+z), because a = 1/(1+z). So
        dR/R = -(1/tau) d ln a says the curvature falls as a power of the
        scale factor, which is geometrically meaningful; treating z itself
        as the affine parameter is not.
      * The exponential is numerically degenerate at high redshift. At
        recombination it gives exp(-2143), which is exactly 0.0 in f64 --
        the curvature vanishes identically at z = 1100.

    `ricci_flow_curve` already integrated `flow_rate`'s ODE correctly, so
    the closed-form accessor was the odd one out, not the reference. Both
    the Python accessor and the Rust `ricci_curvature_at` (a faithful port
    of the same bug) now return the power law. Nothing in production called
    either, so this corrected a latent trap rather than a published number.
    """
    from metaphysica.simulations.PM.cosmology.evolution_engine import RicciFlowIntegrator

    integrator = RicciFlowIntegrator(b3=24)
    tau, r0 = integrator.tau_ricci, integrator.R_initial
    for z in (1.0, 5.0, 50.0):
        ode = _native.py_ricci_flow_curve([0.0, z], 24.0)[1]
        accessor = integrator.get_curvature_at_z(z)
        closed_form = r0 * (1.0 + z) ** (-1.0 / tau)
        assert accessor == pytest.approx(closed_form, rel=1e-12), f"z={z}"
        assert ode == pytest.approx(accessor, rel=1e-6), (
            f"z={z}: the ODE integration and the closed-form accessor have "
            f"parted company again"
        )


def test_the_exponential_law_is_not_silently_reintroduced():
    """The old law differs by 1e39 at z=50, so any return of it is loud."""
    import math

    from metaphysica.simulations.PM.cosmology.evolution_engine import RicciFlowIntegrator

    integrator = RicciFlowIntegrator(b3=24)
    tau, r0 = integrator.tau_ricci, integrator.R_initial
    old_law = r0 * math.exp(-50.0 / tau)
    assert integrator.get_curvature_at_z(50.0) != pytest.approx(old_law, rel=1e-3)
    assert old_law == pytest.approx(0.0, abs=1e-40), (
        "the exponential law no longer underflows at z=50; this test's "
        "premise about its degeneracy needs rechecking"
    )


def test_rust_kernels_refuse_bad_input_instead_of_defaulting():
    """A wrapper that returns 0.0 on failure is worse than one that does not
    exist, because it makes the backend look healthy while it is not."""
    with pytest.raises(ValueError):
        _native.py_ricci_flow_solve([], 73.04, 24.0)
    with pytest.raises(ValueError):
        _native.py_ricci_flow_solve([-1.0], 73.04, 24.0)
    with pytest.raises(ValueError):
        _native.py_ricci_flow_curve([1.0], 0.0)
    with pytest.raises(ValueError):
        _native.py_e8_lattice_points(-1.0)
    with pytest.raises(ValueError):
        _native.py_e8_density_convergence(1.0, 0, 1.0)
    with pytest.raises(ValueError):
        _native.py_flat_torus_dirac_spectrum([], 3)
    with pytest.raises(ValueError):
        _native.py_flat_torus_dirac_spectrum([1.0, 0.0], 3)
    with pytest.raises(KeyError):
        _native.py_get_constant("no_such_constant_anywhere")
