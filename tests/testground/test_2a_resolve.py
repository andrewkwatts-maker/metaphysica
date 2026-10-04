"""Lane 2A: resolve() -- override > per-fork env > METAPHYSICA_CONFIG > active.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.testground.configurations.model import digest_of
from metaphysica.testground.switches.resolve import (
    CONFIG_ENV,
    ResolutionError,
    active_selection,
    configuration_from_env,
    extend_selection,
    find_configuration,
    resolution,
    resolve,
    resolve_selection,
)
from tests.testground.test_2a_support import (
    ACTIVE_SELECTION,
    ENV_PREFIX,
    MemoryStore,
    make_theory,
    tiny_forks,
)

_NAMED = {"alt": dict(ACTIVE_SELECTION, seed="p0", shape="flat")}


def _theory(**kw):
    store = MemoryStore("tiny", kw.pop("selection", ACTIVE_SELECTION),
                        named=kw.pop("named", _NAMED))
    return make_theory(store=store)


def test_the_store_active_is_the_last_resort():
    theory = _theory()
    assert resolve(theory, "seed", environ={}) == "a"
    assert resolution(theory, "seed", environ={}).source == "active"


def test_a_named_configuration_beats_the_active():
    theory = _theory()
    env = {CONFIG_ENV: "alt"}
    assert resolve(theory, "seed", environ=env) == "p0"
    assert resolution(theory, "shape", environ=env).source == "config:alt"


def test_a_named_configuration_is_found_by_digest():
    theory = _theory()
    env = {CONFIG_ENV: digest_of(_NAMED["alt"])}
    assert resolve(theory, "shape", environ=env) == "flat"


@pytest.mark.parametrize("key", ["active", "adopted",
                                 digest_of(ACTIVE_SELECTION)])
def test_the_active_is_reachable_by_alias_name_and_digest(key):
    theory = _theory()
    cfg = find_configuration(theory, key)
    assert cfg.mapping == ACTIVE_SELECTION


def test_a_configuration_name_that_matches_nothing_is_an_error():
    theory = _theory()
    with pytest.raises(ResolutionError, match="matches no stored"):
        resolve(theory, "seed", environ={CONFIG_ENV: "nope"})


def test_the_per_fork_variable_beats_a_named_configuration():
    theory = _theory()
    env = {CONFIG_ENV: "alt", ENV_PREFIX + "SEED": "p1"}
    assert resolve(theory, "seed", environ=env) == "p1"
    assert resolution(theory, "seed", environ=env).source == \
        "env:" + ENV_PREFIX + "SEED"
    assert resolve(theory, "shape", environ=env) == "flat"


def test_an_explicit_override_beats_everything():
    theory = _theory()
    env = {CONFIG_ENV: "alt", ENV_PREFIX + "SEED": "p1"}
    assert resolve(theory, "seed", "dr", environ=env) == "dr"
    assert resolution(theory, "seed", "dr", environ=env).source == "override"


def test_empty_strings_count_as_unset():
    theory = _theory()
    env = {CONFIG_ENV: "", ENV_PREFIX + "SEED": ""}
    assert resolve(theory, "seed", "", environ=env) == "a"
    assert configuration_from_env(theory, env) is None


def test_the_process_environment_is_the_default(monkeypatch):
    theory = _theory()
    monkeypatch.setenv(ENV_PREFIX + "SHAPE", "flat")
    monkeypatch.delenv(CONFIG_ENV, raising=False)
    assert resolve(theory, "shape") == "flat"
    assert resolve_selection(theory)["shape"] == "flat"


def test_an_undeclared_option_is_refused_wherever_it_comes_from():
    theory = _theory()
    with pytest.raises(ResolutionError, match="no option 'zzz'"):
        resolve(theory, "seed", "zzz", environ={})
    with pytest.raises(ResolutionError, match="env:"):
        resolve(theory, "seed", environ={ENV_PREFIX + "SEED": "zzz"})
    bad = _theory(selection=dict(ACTIVE_SELECTION, seed="zzz"))
    with pytest.raises(ResolutionError, match="from active"):
        resolve(bad, "seed", environ={})


def test_a_disabled_option_resolves_like_any_other():
    theory = _theory()
    assert resolve(theory, "seed", "dc", environ={}) == "dc"


def test_an_unknown_fork_is_a_key_error():
    theory = _theory()
    with pytest.raises(KeyError):
        resolve(theory, "ghost", environ={})
    with pytest.raises(KeyError):
        resolve_selection(theory, {"ghost": "x"}, environ={})


def test_a_fork_the_active_predates_takes_its_legacy_option_or_default():
    partial = {k: v for k, v in ACTIVE_SELECTION.items()
               if k not in ("seed", "shape")}
    theory = _theory(selection=partial, named={})
    assert resolve(theory, "seed", environ={}) == "a"        # legacy_option
    assert resolve(theory, "shape", environ={}) == "round"   # default()
    assert active_selection(theory) == ACTIVE_SELECTION


def test_a_named_configuration_missing_a_fork_falls_through_to_active():
    partial = {"seed": "p0"}
    theory = _theory(named={"partial": partial})
    env = {CONFIG_ENV: "partial"}
    assert resolve(theory, "seed", environ=env) == "p0"
    assert resolution(theory, "shape", environ=env).source == "active"


def test_resolve_selection_reads_the_store_once_and_keeps_order():
    store = MemoryStore("tiny", ACTIVE_SELECTION, named=_NAMED)
    theory = make_theory(store=store)
    got = resolve_selection(theory, {"render": "fancy"},
                            environ={CONFIG_ENV: "alt"})
    assert list(got) == list(ACTIVE_SELECTION)
    assert got == dict(_NAMED["alt"], render="fancy")
    assert store.reads == 2          # one active() and one named()


def test_extend_selection_keeps_undeclared_entries_and_fills_the_rest():
    forks = tiny_forks()
    out = extend_selection(forks, {"ghost": "x", "seed": "p0"},
                           fallback=lambda fork: fork.option_ids()[-1])
    assert out["seed"] == "p0" and out["ghost"] == "x"
    assert out["shape"] == "flat"
