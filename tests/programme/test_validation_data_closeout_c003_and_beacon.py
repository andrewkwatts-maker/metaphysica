"""Validation-data close-out XV-14: C003 over forced b2 paths; the two-time beacon on inputs that can fail."""

import inspect

import pytest

from metaphysica.actions.spinors import dirac_dim
from metaphysica.simulations.PM.geometry import b3_path
from metaphysica.simulations.PM.geometry.chi_eff_branches import N_GEN_DIVISOR
from metaphysica.simulations.PM.validation import consistency_beacons as cb
from metaphysica.simulations.PM.validation.CERTIFICATES import PrincipiaValidator
from metaphysica.simulations.core.FormulasRegistry import get_registry
from metaphysica.simulations.core.variants.selection import forced

JOYCE = sorted(k for k, v in b3_path.PATHS.items() if v.get("reachable_by_joyce"))


def _c003(chi):
    v = PrincipiaValidator.__new__(PrincipiaValidator)
    v.reg, v.results = {"topology.mephorash_chi": {"value": chi}}, {}
    v.cert_c003_chi_effective()
    return v.results["C003-CHI"]


def _registry_signatures():
    reg = get_registry()
    return ((reg.D_ancestral_space, reg.D_ancestral_time),
            (reg.D_shadow_space, reg.D_shadow_time))


@pytest.mark.parametrize("path", JOYCE)
def test_c003_expected_tracks_forced_b2(path):
    with forced({"b3_seed": path}):
        b3, b2 = b3_path.seed_values(b3_path.resolve_path())
        n_gen = b3_path.n_gen_report()["n_gen"]
        row = _c003(N_GEN_DIVISOR * n_gen)
        assert b2 == b3_path.PATHS[path]["b2"]
        assert row["expected"] == N_GEN_DIVISOR * n_gen
        assert row["status"] == "LOCKED"
        assert _c003(6 * b3)["status"] == "FAILED"


def test_c003_expected_differs_across_b2():
    expected = set()
    for path in JOYCE:
        with forced({"b3_seed": path}):
            expected.add(_c003(None)["expected"])
    assert len(expected) == len({b3_path.PATHS[p]["b2"] for p in JOYCE})


def test_c003_follows_the_forced_n_gen_source_not_b2():
    """Fails if C003 reverts to N_GEN_DIVISOR * (b2 // 4) and ignores the n_gen_source fork."""
    b3, b2 = b3_path.seed_values(b3_path.resolve_path())
    with forced({"n_gen_source": "b3_over_dim_O"}):
        report = b3_path.n_gen_report()
        row = _c003(N_GEN_DIVISOR * (b2 // 4))
        forced_row = _c003(N_GEN_DIVISOR * report["n_gen"])
    assert report["declared_source"] == "b3_over_dim_O" and report["n_gen"] == b3 / 8
    assert row["expected"] == N_GEN_DIVISOR * b3 / 8 != N_GEN_DIVISOR * (b2 // 4)
    assert row["status"] == "FAILED" and forced_row["status"] == "FAILED"


def _bulk_d():
    (space, time), _ = _registry_signatures()
    return space + time


def test_beacon_passes_on_registry_signatures():
    beacon = cb.beacon_two_time_bulk_accounting()
    assert beacon.status == "PASS" and beacon.value == 0.0
    explicit = cb.beacon_two_time_bulk_accounting(_registry_signatures())
    assert explicit.value == 0.0


def test_beacon_fails_on_a_bulk_that_is_not_two_shadows():
    (space, time), shadow = _registry_signatures()
    beacon = cb.beacon_two_time_bulk_accounting(((space + 2, time), shadow))
    assert beacon.status == "FAIL" and beacon.value > 0


def test_beacon_fails_when_shadow_times_do_not_add_up():
    (space, time), (s_space, s_time) = _registry_signatures()
    sig = ((space, time), (s_space - 1, s_time + 1))
    assert cb.beacon_two_time_bulk_accounting(sig).status == "FAIL"


def test_beacon_fails_on_a_wrong_declared_spinor():
    wrong = dirac_dim(_bulk_d())             # the Dirac count while Weyl is in force
    beacon = cb.beacon_two_time_bulk_accounting(spinor=wrong)
    assert beacon.status == "FAIL"
    assert str(wrong) in beacon.note


def test_forced_dirac_moves_the_expected_spinor():
    weyl = cb.beacon_two_time_bulk_accounting()
    with forced({"action_bulk_spinor": "dirac"}):
        dirac = cb.beacon_two_time_bulk_accounting()
        dirac_vs_weyl = cb.beacon_two_time_bulk_accounting(spinor=dirac_dim(_bulk_d()) // 2)
    assert "weyl = %d vs" % (dirac_dim(_bulk_d()) // 2) in weyl.name
    assert "dirac = %d vs" % dirac_dim(_bulk_d()) in dirac.name and dirac.status == "PASS"
    assert dirac_vs_weyl.status == "FAIL" and dirac_vs_weyl.value == dirac_dim(_bulk_d()) // 2


def test_time_term_checks_bulk_time_is_twice_shadow_time():
    """The docstring's claim: 2 t_shadow = t_bulk, not one time per shadow."""
    (space, time), (s_space, s_time) = _registry_signatures()
    sig = ((space - time, 2 * time), (s_space - s_time, 2 * s_time))
    assert cb.beacon_two_time_bulk_accounting(sig).value == 0.0


def test_no_typed_spinor_size_in_module():
    src = inspect.getsource(cb)
    assert "PNEUMA_WEYL_COMPONENTS" not in src and "4096" not in src


def test_beacon_text_built_from_inputs():
    (space, time), shadow = _registry_signatures()
    beacon = cb.beacon_two_time_bulk_accounting(((space + 2, time), shadow))
    assert "Cl(%d,%d)" % (space + 2, time) in beacon.name
    assert "Cl(%d,%d)" % (space + 2, time) in beacon.note


def test_beacon_refuses_non_positive_dimensions():
    (space, time), shadow = _registry_signatures()
    with pytest.raises(ValueError):
        cb.beacon_two_time_bulk_accounting(((space, 0), shadow))


def test_beacon_body_types_no_dimension():
    body = inspect.getsource(cb.beacon_two_time_bulk_accounting).split('"""')[2]
    for literal in ("24", "26", "13", "4096"):
        assert literal not in body
