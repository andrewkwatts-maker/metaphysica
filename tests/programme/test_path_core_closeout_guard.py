"""Close-out XP-01, XP-04, XP-07: the demon-lock guard.

Each test fails on the code before the close-out:
* XP-01 verify_tzimtzum_fraction compared sigma_T with a typed 23/24, so any
  dark_energy_betti option other than n = 24 was a violation;
* XP-04 two docstrings quoted the seed_24 H0 71.55;
* XP-07 the sterile parity identity was counted in the preflight and a broken
  identity blocked the lock.
"""
import inspect

import pytest

from metaphysica.simulations.core import demon_lock_guard as dlg
from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry
from metaphysica.simulations.core.variants import selection
from metaphysica.simulations.PM.cosmology.late_time_routes import de_betti_n


def _guard():
    return dlg.DemonLockGuard(registry=FormulasRegistry())


@pytest.mark.parametrize("option", ["b3_live", "b2_4", "b3_24"])
def test_tzimtzum_fraction_reads_the_dark_energy_fork(option):
    with selection.forced({"dark_energy_betti": option}):
        guard = _guard()
        n = de_betti_n(option)
        assert guard.registry.tzimtzum_pressure == pytest.approx((n - 1) / n)
        assert guard.verify_tzimtzum_fraction() is True
    assert guard.violations == []


def test_tzimtzum_fraction_flags_a_registry_off_the_fork():
    with selection.forced({"dark_energy_betti": "b2_4"}):
        guard = _guard()
        guard.registry._tzimtzum_pressure = 23.0 / 24.0
        assert guard.verify_tzimtzum_fraction() is False
    assert "3/4" in guard.violations[0]


def test_tzimtzum_formula_warning_names_the_fork_fraction():
    with selection.forced({"dark_energy_betti": "b2_4"}):
        guard = _guard()
        guard.data = {"constants": {"tzimtzum_pressure": {
            "value": 0.75, "formula": "sigma_T = (n-1)/n = 3/4"}}}
        assert guard.verify_tzimtzum_fraction() is True
    assert not [w for w in guard.warnings if "Tzimtzum" in w]


def test_docstrings_do_not_quote_the_seed_24_hubble_value():
    from metaphysica.simulations.base.registry import PMRegistry

    hubble = inspect.getdoc(dlg.DemonLockGuard.verify_hubble_formula)
    example = inspect.getdoc(PMRegistry.register_dependency)
    assert "71.55" not in hubble and "288/4" not in hubble
    assert "71.55" not in example


def test_parity_identity_is_not_counted_in_the_preflight(capsys):
    guard = _guard()
    assert "verify_sterile_parity" in dlg.RETIRED_FROM_PAPER
    guard.run_preflight()
    names = [fn.__name__ for _, fn in guard.preflight_checks()]
    identities = [n for n in names if n in dlg.RETIRED_FROM_PAPER]
    assert guard.tally["identities_not_counted"] == len(identities) == 2
    assert guard.tally["scored_total"] == len(names) - 2
    out = capsys.readouterr().out
    assert "Sterile Parity" in out and "not counted" in out


def test_a_broken_parity_identity_does_not_block_the_lock():
    guard = _guard()
    guard.run_preflight()
    baseline = (guard.tally["scored_passed"], list(guard.violations))
    broken = _guard()
    broken.verify_sterile_parity = _broken_identity(broken)
    broken.verify_sterile_parity.__name__ = "verify_sterile_parity"
    broken.run_preflight()
    assert (broken.tally["scored_passed"], broken.violations) == baseline
    assert any(w.startswith("IDENTITY (not scored): PARITY")
               for w in broken.warnings)


def _broken_identity(guard):
    def verify_sterile_parity():
        guard.violations.append("PARITY ERROR: forced")
        return False
    return verify_sterile_parity


def test_registry_main_tally_leaves_verify_parity_out():
    import importlib

    fr = importlib.import_module("metaphysica.simulations.core.FormulasRegistry")
    src = inspect.getsource(fr)
    block = src[src.index("all_verified = all(["):]
    block = block[:block.index("])")]
    assert "verify_parity()" not in block
    assert "verify_tzimtzum_fraction()" in block
