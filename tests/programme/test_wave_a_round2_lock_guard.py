"""Wave A round 2 R2-24..R2-27: the demon-lock guard.

Each test fails on the code before the fix (8ccbfc3), except the one marked
as a control:
* R2-24 a violation recorded by an identity was moved to the warnings, so a
  drifted manifest JSON (christ_constant, roots, the parity pair) left the lock
  SECURE;
* R2-25 a scored check that raised was printed and added no violation, so
  run_preflight returned True;
* R2-26 verify_tzimtzum_fraction and verify_hubble_formula, true by
  construction on the registry side, were counted as scored;
* R2-27 verify_tzimtzum_fraction read the dark_energy_betti fork itself (a PM
  import inside core) instead of the registry's _tzimtzum_from_fork.
"""
import copy
import inspect

import pytest

from metaphysica.simulations.core import demon_lock_guard as dlg
from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry
from metaphysica.simulations.core.variants import selection
from metaphysica.simulations.PM.cosmology.late_time_routes import de_betti_n

IDENTITIES = {"verify_integer_closure", "verify_sterile_parity",
              "verify_tzimtzum_fraction", "verify_hubble_formula"}


def _guard(manifest=None):
    guard = dlg.DemonLockGuard(registry=FormulasRegistry())
    if manifest is not None:
        guard.data = copy.deepcopy(manifest)
    return guard


@pytest.fixture(scope="module")
def manifest():
    """The manifest the registry itself writes: the one with no drift."""
    return FormulasRegistry().generate_named_constants_json()


def _drifted(manifest, section, key, delta):
    data = copy.deepcopy(manifest)
    data[section][key]["value"] += delta
    return data


# (section, key, drift, violation prefix, identities broken, scored checks failed)
# The first three are the R2-24 cases: no scored check reads the value, so
# before the fix the lock stayed SECURE. The last two are the R2-26 checks:
# their drift blocked before as a scored failure and blocks now as an identity
# (the Hubble value is also read by the scored SSoT sync).
DRIFTS = [
    ("constants", "christ_constant", 1, "CLOSURE ERROR: Christ Constant", 1, 0),
    ("topological_invariants", "roots", 1, "CLOSURE ERROR: Total roots", 1, 0),
    ("constants", "sophian_drag", 0.01, "PARITY ERROR: JSON parity", 1, 0),
    ("constants", "tzimtzum_pressure", 0.01, "TZIMTZUM ERROR: JSON value", 2, 0),
    ("derived_values", "hubble_constant", 1.0, "H0 ERROR: JSON H0", 1, 1),
]


@pytest.mark.parametrize("section, key, delta, prefix, broken, scored_failed", DRIFTS)
def test_a_drifted_manifest_blocks_the_lock_without_being_scored(
        manifest, capsys, section, key, delta, prefix, broken, scored_failed):
    clean = _guard(manifest)
    assert clean.run_preflight() is True
    assert clean.violations == [] and clean.tally["identities_broken"] == 0
    capsys.readouterr()

    drifted = _guard(_drifted(manifest, section, key, delta))
    assert drifted.run_preflight() is False
    assert any(v.startswith(prefix) for v in drifted.violations), drifted.violations
    assert not any(prefix in w for w in drifted.warnings)
    assert drifted.tally["identities_broken"] == broken
    assert drifted.tally["scored_total"] == clean.tally["scored_total"]
    assert drifted.tally["scored_passed"] == clean.tally["scored_passed"] - scored_failed
    assert drifted.tally["identities_not_counted"] == len(IDENTITIES)
    out = capsys.readouterr().out
    assert "DEMON LOCK: COMPROMISED" in out and "BROKEN, blocks, not counted" in out


def test_a_scored_check_that_raises_blocks_the_lock(capsys):
    clean = _guard()
    assert clean.run_preflight() is True
    capsys.readouterr()

    guard = _guard()

    def verify_w0_seal():
        raise RuntimeError("the fork reader failed")

    guard.verify_w0_seal = verify_w0_seal
    assert guard.run_preflight() is False
    assert guard.violations == [
        "CHECK ERROR: W0 Seal (active mechanism) raised RuntimeError: "
        "the fork reader failed"]
    assert guard.tally["scored_total"] == clean.tally["scored_total"]
    assert guard.tally["scored_passed"] == clean.tally["scored_passed"] - 1
    out = capsys.readouterr().out
    assert "W0 Seal (active mechanism): [ERROR]" in out
    assert "DEMON LOCK: COMPROMISED" in out and "DEMON LOCK: SECURE" not in out


def test_checks_true_by_construction_are_identities_not_scored(capsys):
    guard = _guard()
    assert guard.run_preflight() is True
    names = [fn.__name__ for _, fn in guard.preflight_checks()]
    assert set(dlg.RETIRED_FROM_PAPER) == IDENTITIES
    assert IDENTITIES <= set(names)
    assert guard.tally["identities_not_counted"] == len(IDENTITIES)
    assert guard.tally["scored_total"] == len(names) - len(IDENTITIES)
    assert guard.tally["scored_passed"] == guard.tally["scored_total"]
    lines = capsys.readouterr().out.splitlines()
    for label in ("Tzimtzum Fraction", "Hubble Formula"):
        (line,) = [text for text in lines if label in text]
        assert line.endswith("[IDENTITY holds, not counted]")
    summary = "Scored checks: %d of %d passed; %d identities run, not counted" % (
        guard.tally["scored_passed"], guard.tally["scored_total"], len(IDENTITIES))
    assert any(summary in text for text in lines)


def test_tzimtzum_fraction_reads_the_fork_through_the_registry_helper():
    guard = _guard()
    guard.registry._tzimtzum_from_fork = lambda: 6.0 / 7.0
    guard.registry._tzimtzum_pressure = 6.0 / 7.0
    assert guard.verify_tzimtzum_fraction() is True
    assert guard.violations == []

    guard.registry._tzimtzum_pressure = 5.0 / 7.0
    assert guard.verify_tzimtzum_fraction() is False
    assert guard.violations == [
        "TZIMTZUM ERROR: Registry drift detected. Must be 6/7."]

    source = inspect.getsource(dlg.DemonLockGuard.verify_tzimtzum_fraction)
    assert "self.registry._tzimtzum_from_fork()" in source
    assert "late_time_routes" not in source and "de_betti_n" not in source


def test_a_fork_value_that_is_not_n_minus_1_over_n_raises():
    guard = _guard()
    guard.registry._tzimtzum_from_fork = lambda: 0.4
    with pytest.raises(ValueError, match=r"not of the form \(n-1\)/n"):
        guard.verify_tzimtzum_fraction()


@pytest.mark.parametrize("option", ["b3_live", "b2_4", "b3_24"])
def test_control_the_fraction_text_is_n_minus_1_over_n_on_every_option(option):
    """Control (holds before and after): the text built from the registry
    helper's value is the "(n-1)/n" the fork reader's n gives."""
    with selection.forced({"dark_energy_betti": option}):
        guard = _guard()
        n = de_betti_n(option)
        guard.registry._tzimtzum_pressure = 0.5 * (n - 1) / n
        assert guard.verify_tzimtzum_fraction() is False
    assert guard.violations == [
        "TZIMTZUM ERROR: Registry drift detected. Must be %d/%d." % (n - 1, n)]
