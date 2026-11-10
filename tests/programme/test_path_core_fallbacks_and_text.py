"""Round 4 of path-core: fallbacks raise or report, text follows the path in force.

core-paths-20, 21, 22, 24, 25, 33, 35, 36, 38, 39, 41 and the config Hodge
literals (core-paths-11 remainder). core-paths-22/23 also edit
tests/testground/test_2c_screen.py.
"""
import inspect
import types

import pytest

from metaphysica.simulations.core import switch_search as ss
from metaphysica.simulations.core.active_path import topology
from metaphysica.simulations.core.variants import selection


def test_errored_combination_is_apart_from_inconsistent():
    err = {"name": "a", "kind": "ERROR", "ok": False}
    bad = {"name": "b", "kind": "CONTRADICTION", "ok": False}
    assert ss.combination_state([]) == "CONSISTENT"
    assert ss.combination_state([err]) == "ERRORED"
    assert ss.combination_state([err, bad]) == "INCONSISTENT"


def test_free_set_failure_is_an_unmeasured_record(monkeypatch):
    from metaphysica.simulations.core import free_set

    def boom():
        raise RuntimeError("no ledger")

    monkeypatch.setattr(free_set, "build_free_set", boom)
    size, status = ss._free_set_load_bearing()
    assert size is None and status == "UNMEASURED: RuntimeError: no ledger"


def test_a_fork_with_no_default_raises(monkeypatch):
    def no_default():
        raise ValueError("no default")

    fork = types.SimpleNamespace(default=no_default, options=(),
                                 sweepable_ids=lambda: ())
    monkeypatch.setattr(ss, "_variants",
                        lambda: types.SimpleNamespace(FORKS={"f": fork}))
    with pytest.raises(ValueError, match="no default"):
        ss._option_lists(["f"], False)


def test_re_t_check_reads_the_live_action_selection(monkeypatch):
    from metaphysica.simulations.core.variants import adopted

    monkeypatch.setattr(adopted, "_action_bulk_sectors_adopted", lambda: "other")
    row = ss._re_t_check(7.0, lambda n: [])
    assert row["mode"] == "labelled_calibrated_d015"


def test_ranking_header_lists_rows_not_evaluated():
    from metaphysica.testground.rank import SCHEMA, validate_ranking

    doc = {"schema": SCHEMA, "rule": "r", "reasonable_rule": "r",
           "selected": "a", "verdict": "v", "searched": 1, "unranked": [],
           "rows": [{"path_id": "a", "missing": ["consistency"]}]}
    assert any("not_evaluated" in p for p in validate_ranking(doc))


def test_run_log_without_reason_or_wall_time_raises():
    from metaphysica.testground.runner.worker import RunResult

    data = {"theory": "t", "digest": "d", "root": "r", "status": "COMPLETED",
            "stages": []}
    with pytest.raises(KeyError):
        RunResult.from_dict(data)


def test_preferred_path_does_not_count_forks_in_prose():
    from metaphysica.simulations.core import preferred_path

    assert "twelve" not in preferred_path.__doc__


def test_eml_chi_eff_is_the_k3_reading_of_the_path():
    from metaphysica.simulations.core import eml_integration as eml

    n_gen = topology().n_gen
    assert eml.eml_g2_chi_eff() == pytest.approx(48 * n_gen)
    assert eml.eml_n_gen(48.0 * n_gen) == pytest.approx(n_gen)
    assert "b3" not in inspect.signature(eml.eml_n_gen).parameters


def test_resolver_seeds_are_read_from_the_registry():
    from metaphysica.simulations.core.dependency_resolver import build_seed_values
    from metaphysica.simulations.core.FormulasRegistry import get_registry

    seeds, reg = build_seed_values(), get_registry()
    assert seeds["seeds.logic_closure"] == reg.roots_total
    assert seeds["seeds.bulk_pressure"] == reg.sterile_sector
    src = inspect.getsource(build_seed_values)
    assert "288" not in src and "163" not in src


def test_integer_closure_is_retired_and_labels_are_computed():
    from metaphysica.simulations.core import demon_lock_guard as dlg

    assert "verify_integer_closure" in dlg.RETIRED_FROM_PAPER
    guard = dlg.DemonLockGuard.__new__(dlg.DemonLockGuard)
    guard.registry = dlg.get_registry()
    labels = " ".join(name for name, _ in guard.preflight_checks())
    assert "H0=%.2f" % guard.registry.h0_local in labels
    assert "by construction" in labels


def test_free_variable_ledger_names_the_anchor_it_reads():
    from metaphysica.simulations.core import free_variable_ledger as fvl

    src = inspect.getsource(fvl._derived_from_free_variables)
    assert "GeometricAnchors(24)" not in src and "b3 = 24" not in src
    assert "ANCHOR_FIT" in src


def test_bridge_states_the_two_13d_shadow_reading():
    from metaphysica.config.parameters.bridge import V21BridgeParameters as V

    assert V.SHADOW_SIGNATURE == (12, 1)
    assert not hasattr(V, "SHADOW_SIGNATURE_SPATIAL")
    assert V.RETIRED_SHADOW_SIGNATURE_SPATIAL == (12, 0)
    assert V.verify_signature()


@pytest.mark.parametrize("seed", [None, "seed_24"])
def test_fundamental_constants_follow_the_path(seed):
    from metaphysica.config import FundamentalConstants as F

    with selection.forced({"b3_seed": seed} if seed else {}):
        topo = topology()
        assert (F.B3, F.B2, F.CHI_EFF) == (topo.b3, topo.b2, topo.chi_eff)
        assert F.fermion_generations() == topo.n_gen
        assert F.euler_characteristic() == topo.chi_eff
    assert not hasattr(F, "HODGE_H11") and F.RETIRED_TCS187_HODGE_H31 == 68
