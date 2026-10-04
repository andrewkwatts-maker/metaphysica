"""Lane 2C: the run plan orders, de-duplicates and groups configurations.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.runner.plan import (build_plan, group_key,
                                                import_time_forks)
from metaphysica.testground.signals.model import FULL, SCREEN
from tests.testground import test_2c_support as tiny


def test_import_time_forks_are_found_by_binding():
    theory = tiny.make_theory()
    assert import_time_forks(theory) == ("seed",)
    unknown = tiny.make_theory(fork_map=tiny.forks(mode_binding="unknown"))
    assert import_time_forks(unknown) == ("seed",)
    assert import_time_forks(unknown, unknown_as_import_time=True) == (
        "mode", "seed")


def test_plan_keeps_order_drops_duplicates_and_groups_by_import_time_options():
    theory = tiny.make_theory()
    cfgs = [tiny.cfg("b", "high"), tiny.cfg("a", "low"), tiny.cfg("b", "high"),
            tiny.cfg("c", "low"), tiny.cfg("a", "high")]
    plan = build_plan(theory, cfgs, FULL)
    assert plan.stage == FULL
    assert plan.digests() == [c.digest for c in
                              (cfgs[0], cfgs[1], cfgs[3], cfgs[4])]
    assert len(plan) == 4
    assert [g.key for g in plan.groups] == [(("seed", "high"),),
                                            (("seed", "low"),)]
    assert plan.groups[0].digests() == [cfgs[0].digest, cfgs[4].digest]
    assert [e.group for e in plan] == [0, 1, 1, 0]
    assert plan.configurations[0] == cfgs[0]
    assert plan.groups[0].env(theory) == {tiny.SEED_VAR: "high"}


def test_call_time_only_theory_is_one_group():
    theory = tiny.make_theory(fork_map=tiny.forks(seed_binding="call_time"))
    plan = build_plan(theory, tiny.all_cfgs())
    assert plan.stage == SCREEN
    assert plan.import_time_forks == ()
    assert len(plan.groups) == 1 and plan.groups[0].key == ()
    assert len(plan.groups[0].configurations) == 6


def test_plan_refuses_an_unknown_stage_and_a_foreign_configuration():
    theory = tiny.make_theory()
    with pytest.raises(ValueError, match="stage"):
        build_plan(theory, [tiny.cfg()], "warp")
    foreign = Configuration.of("other", {"mode": "a", "seed": "low"})
    with pytest.raises(ValueError, match="do not belong"):
        build_plan(theory, [foreign])


def test_group_key_skips_forks_absent_from_the_selection():
    cfg = Configuration.of(tiny.THEORY_ID, {"mode": "a"})
    assert group_key(cfg, ["seed", "mode"]) == (("mode", "a"),)


def test_plan_serialises():
    plan = build_plan(tiny.make_theory(), [tiny.cfg(), tiny.cfg("a", "high")])
    data = plan.to_dict()
    assert data["theory"] == tiny.THEORY_ID
    assert data["import_time_forks"] == ["seed"]
    assert [g["key"] for g in data["groups"]] == [{"seed": "low"},
                                                  {"seed": "high"}]
    assert [e["group"] for e in data["entries"]] == [0, 1]
