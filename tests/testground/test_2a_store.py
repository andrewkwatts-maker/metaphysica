"""Lane 2A: the YAML selection store -- verified loads, atomic writes, history.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import os

import pytest
import yaml

from metaphysica.testground.configurations import store as store_mod
from metaphysica.testground.configurations.enumerate import (
    count_configurations,
    enumerate_configurations,
)
from metaphysica.testground.configurations.model import (
    ACTIVE,
    Configuration,
    digest_of,
)
from metaphysica.testground.configurations.store import (
    DigestMismatchError,
    StoreError,
    YamlSelectionStore,
    atomic_write_text,
)
from metaphysica.testground.switches.resolve import CONFIG_ENV, resolve
from metaphysica.testground.theory import SelectionStore
from tests.testground.test_2a_support import (
    ACTIVE_SELECTION,
    make_theory,
    tiny_forks,
    write_active_yaml,
)


def _sel(**changes):
    return dict(ACTIVE_SELECTION, **changes)


@pytest.fixture
def paths(tmp_path):
    return tmp_path / "active.yaml", tmp_path / "configurations.yaml"


@pytest.fixture
def store(paths):
    write_active_yaml(paths[0], ACTIVE_SELECTION,
                      decided_by={"seed": ["D-015"]})
    return YamlSelectionStore(paths[0], paths[1], forks=tiny_forks(),
                              theory_id="tiny")


def _write_named(path, configurations, theory="tiny"):
    path.write_text(yaml.safe_dump({"theory": theory,
                                    "configurations": configurations}),
                    encoding="utf-8")


# ---------------------------------------------------------------- loading


def test_the_store_is_a_selection_store(store):
    assert isinstance(store, SelectionStore)


def test_the_active_loads_as_an_active_configuration(store):
    cfg = store.active()
    assert cfg.mapping == ACTIVE_SELECTION and cfg.lifecycle == ACTIVE
    assert cfg.name == "adopted" and cfg.theory == "tiny"
    assert cfg.decided_by == (("seed", ("D-015",)),)
    assert store.data_tiebreak_dof() == 0 and store.previous() == []
    assert store.document()["digest"] == digest_of(ACTIVE_SELECTION)


def test_a_digest_mismatch_is_a_load_error(paths):
    write_active_yaml(paths[0], ACTIVE_SELECTION, digest="0" * 16)
    with pytest.raises(DigestMismatchError, match="recorded digest"):
        YamlSelectionStore(paths[0]).active()


def test_a_missing_digest_is_a_load_error(paths):
    paths[0].write_text(yaml.safe_dump({"theory": "tiny",
                                        "selection": ACTIVE_SELECTION}),
                        encoding="utf-8")
    with pytest.raises(DigestMismatchError):
        YamlSelectionStore(paths[0]).active()


def test_a_disabled_active_option_is_an_error_only_with_forks(paths):
    write_active_yaml(paths[0], _sel(seed="dr"))
    assert YamlSelectionStore(paths[0]).active().mapping["seed"] == "dr"
    with pytest.raises(StoreError, match="DISABLED option seed=dr"):
        YamlSelectionStore(paths[0], forks=tiny_forks()).active()


def test_forks_may_be_supplied_lazily(paths):
    write_active_yaml(paths[0], _sel(seed="dc"))
    with pytest.raises(StoreError, match="DISABLED"):
        YamlSelectionStore(paths[0], forks=tiny_forks).active()


@pytest.mark.parametrize("selection, match", [
    (_sel(ghost="x"), "undeclared fork 'ghost'"),
    (_sel(seed="zzz"), "has no option 'zzz'"),
])
def test_undeclared_forks_and_options_are_load_errors(paths, selection,
                                                      match):
    write_active_yaml(paths[0], selection)
    with pytest.raises(StoreError, match=match):
        YamlSelectionStore(paths[0], forks=tiny_forks()).active()


def test_a_fork_the_active_predates_takes_its_legacy_option(paths):
    partial = {k: v for k, v in ACTIVE_SELECTION.items() if k != "seed"}
    write_active_yaml(paths[0], partial)
    cfg = YamlSelectionStore(paths[0], forks=tiny_forks()).active()
    assert cfg.mapping == ACTIVE_SELECTION
    assert cfg.reasons == ("seed absent from %s; extended with its legacy "
                           "option a" % paths[0],)


def test_a_fork_without_a_legacy_option_must_be_in_the_active(paths):
    partial = {k: v for k, v in ACTIVE_SELECTION.items() if k != "shape"}
    write_active_yaml(paths[0], partial)
    with pytest.raises(StoreError, match="no legacy_option"):
        YamlSelectionStore(paths[0], forks=tiny_forks()).active()


@pytest.mark.parametrize("doc, match", [
    ("- just\n- a list\n", "must be a mapping"),
    ("theory: ''\n", "non-empty string"),
    ("theory: tiny\nname: 3\n", "'name' must be a string"),
    ("theory: tiny\n", "no 'selection'"),
    ("theory: tiny\nselection: [a]\n", "must be a mapping"),
    ("theory: tiny\nselection: {seed: yes}\n", "quote ids"),
    ("theory: [unclosed\n", "not readable YAML"),
])
def test_malformed_active_files_are_load_errors(paths, doc, match):
    paths[0].write_text(doc, encoding="utf-8")
    with pytest.raises(StoreError, match=match):
        YamlSelectionStore(paths[0]).active()


@pytest.mark.parametrize("extra, match", [
    ({"decided_by": {"ghost": ["D-1"]}}, "names forks"),
    ({"decided_by": {"seed": "D-1"}}, "list of decision ids"),
    ({"decided_by": ["D-1"]}, "decided_by must be a mapping"),
    ({"data_tiebreak_dof": -1}, "non-negative"),
    ({"data_tiebreak_dof": True}, "non-negative"),
    ({"previous": {"a": 1}}, "'previous' must be a list"),
])
def test_malformed_optional_fields_are_load_errors(paths, extra, match):
    write_active_yaml(paths[0], ACTIVE_SELECTION, **extra)
    with pytest.raises(StoreError, match=match):
        YamlSelectionStore(paths[0]).active()


def test_a_missing_file_and_a_foreign_theory_are_load_errors(paths):
    with pytest.raises(StoreError, match="no selection store file"):
        YamlSelectionStore(paths[0]).active()
    write_active_yaml(paths[0], ACTIVE_SELECTION, theory="other")
    with pytest.raises(StoreError, match="belongs to theory 'other'"):
        YamlSelectionStore(paths[0], theory_id="tiny").active()


def test_an_edited_file_is_re_read(store, paths):
    assert store.active().mapping["seed"] == "a"
    write_active_yaml(paths[0], _sel(seed="p0"))
    assert store.active().mapping["seed"] == "p0"


# --------------------------------------------------------------- writing


def test_write_active_round_trips_and_keeps_history(store, paths):
    new = Configuration.of("tiny", _sel(seed="p0", shape="flat"))
    store.write_active(new, "D-021", "adopt the p0 seed", name="p0-path")
    cfg = store.active()
    assert cfg.mapping == new.mapping and cfg.name == "p0-path"
    assert dict(cfg.decided_by) == {"seed": ("D-021",), "shape": ("D-021",)}
    doc = store.document()
    assert doc["decision"] == "D-021" and doc["note"] == "adopt the p0 seed"
    (old,) = store.previous()
    assert old["selection"] == ACTIVE_SELECTION
    assert old["digest"] == digest_of(ACTIVE_SELECTION)
    assert old["decided_by"] == {"seed": ["D-015"]}
    assert old["superseded_by"] == "D-021" and old["superseded_on"]


def test_unchanged_forks_keep_their_decisions(store):
    store.write_active(Configuration.of("tiny", _sel(shape="flat")), "D-021")
    assert dict(store.active().decided_by) == {"seed": ("D-015",),
                                               "shape": ("D-021",)}
    again = Configuration.of("tiny", _sel(shape="flat"),
                             decided_by=(("render", ("D-019",)),))
    store.write_active(again, "D-022", data_tiebreak_dof=1)
    assert dict(store.active().decided_by) == {
        "seed": ("D-015",), "shape": ("D-021",), "render": ("D-019",)}
    assert store.data_tiebreak_dof() == 1
    assert len(store.previous()) == 2
    store.write_active(again, "D-023")
    assert store.data_tiebreak_dof() == 1          # kept when not given


def test_the_first_write_creates_the_file(paths):
    fresh = YamlSelectionStore(paths[0], forks=tiny_forks())
    fresh.write_active(Configuration.of("tiny", ACTIVE_SELECTION), "D-001")
    cfg = fresh.active()
    assert cfg.mapping == ACTIVE_SELECTION and fresh.previous() == []
    assert cfg.name.startswith("active-")
    assert set(dict(cfg.decided_by)) == set(ACTIVE_SELECTION)


@pytest.mark.parametrize("cfg, decision, match", [
    (Configuration.of("tiny", _sel(seed="dr")), "D-1", "DISABLED"),
    (Configuration.of("tiny", {"seed": "a"}), "D-1", "names no option"),
    (Configuration.of("tiny", ACTIVE_SELECTION), "", "decision id"),
    (Configuration.of("other", ACTIVE_SELECTION), "D-1", "theory 'other'"),
])
def test_write_active_refuses_what_it_could_not_load(store, paths, cfg,
                                                     decision, match):
    before = paths[0].read_bytes()
    with pytest.raises(StoreError, match=match):
        store.write_active(cfg, decision)
    assert paths[0].read_bytes() == before


def test_write_active_refuses_to_overwrite_a_corrupt_file(paths):
    paths[0].write_text("theory: [unclosed\n", encoding="utf-8")
    with pytest.raises(StoreError):
        YamlSelectionStore(paths[0]).write_active(
            Configuration.of("tiny", ACTIVE_SELECTION), "D-1")
    assert paths[0].read_text(encoding="utf-8") == "theory: [unclosed\n"


def test_write_active_refuses_a_theory_change_without_a_theory_id(paths):
    write_active_yaml(paths[0], ACTIVE_SELECTION)
    with pytest.raises(StoreError, match="holds theory 'tiny'"):
        YamlSelectionStore(paths[0]).write_active(
            Configuration.of("other", ACTIVE_SELECTION), "D-1")


@pytest.mark.parametrize("failing", ["replace", "fsync"])
def test_a_failed_write_leaves_the_old_file_and_no_debris(store, paths,
                                                          monkeypatch,
                                                          failing):
    before = paths[0].read_bytes()

    def boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(store_mod.os, failing, boom)
    with pytest.raises(OSError, match="disk full"):
        store.write_active(Configuration.of("tiny", _sel(seed="p0")), "D-1")
    assert paths[0].read_bytes() == before
    assert sorted(p.name for p in paths[0].parent.iterdir()) == [
        "active.yaml"]


def test_atomic_write_creates_parent_directories(tmp_path):
    target = tmp_path / "a" / "b" / "file.yaml"
    atomic_write_text(target, "x: 1\n")
    assert target.read_text(encoding="utf-8") == "x: 1\n"


# ----------------------------------------------------- named configurations


def test_named_configurations_resolve_to_full_configurations(store, paths):
    _write_named(paths[1], {
        "fixed": {"selection": _sel(seed="dc"),
                  "digest": digest_of(_sel(seed="dc")),
                  "decided_by": {"seed": ["D-003"]}},
        "relative": {"overrides": {"shape": "flat"}, "note": "probe"},
        "chained": {"base": "relative", "overrides": {"seed": "p0"}},
    })
    named = store.named()
    assert named["fixed"].mapping == _sel(seed="dc")         # DISABLED ok
    assert named["fixed"].decided_by == (("seed", ("D-003",)),)
    assert named["relative"].mapping == _sel(shape="flat")
    assert named["chained"].mapping == _sel(shape="flat", seed="p0")
    assert all(cfg.name == name for name, cfg in named.items())
    assert store.named_document()["relative"]["note"] == "probe"


def test_a_fixed_named_selection_is_extended_for_newer_forks(store, paths):
    partial = {k: v for k, v in _sel(origin="input").items()
               if k not in ("seed", "shape")}
    _write_named(paths[1], {"old": {"selection": partial}})
    cfg = store.named()["old"]
    assert cfg.mapping == _sel(origin="input")
    assert cfg.not_runnable
    assert len(cfg.reasons) == 2 and "legacy option a" in cfg.reasons[0]
    assert "active option round" in cfg.reasons[1]


@pytest.mark.parametrize("configurations, match", [
    ({"x": {"base": "x"}}, "base cycle"),
    ({"x": {"base": "nowhere"}}, "does not exist"),
    ({"x": {"base": "active", "selection": ACTIVE_SELECTION}},
     "both 'selection' and 'base'"),
    ({"x": {"overrides": {"seed": "p0"}, "digest": "f" * 16}},
     "recorded digest"),
    ({"active": {"overrides": {}}}, "reserved"),
    ({"x": {"overrides": {"seed": "zzz"}}}, "no option 'zzz'"),
])
def test_malformed_named_configurations_are_errors(store, paths,
                                                   configurations, match):
    _write_named(paths[1], configurations)
    with pytest.raises(StoreError, match=match):
        store.named()


@pytest.mark.parametrize("doc, match", [
    ("- a list\n", "must be a mapping"),
    ("theory: other\n", "belongs to theory 'other'"),
    ("configurations: [a]\n", "'configurations' must be a mapping"),
])
def test_malformed_named_files_are_errors(store, paths, doc, match):
    paths[1].write_text(doc, encoding="utf-8")
    with pytest.raises(StoreError, match=match):
        store.named()


def test_no_named_file_means_no_named_configurations(paths):
    write_active_yaml(paths[0], ACTIVE_SELECTION)
    assert YamlSelectionStore(paths[0]).named() == {}
    assert YamlSelectionStore(paths[0], paths[1]).named() == {}
    paths[1].write_text("", encoding="utf-8")
    assert YamlSelectionStore(paths[0], paths[1]).named() == {}


def test_write_named_adds_without_deleting(store, paths):
    old = Configuration.of("tiny", ACTIVE_SELECTION,
                           decided_by=(("seed", ("D-015",)),))
    store.write_named("previous-active-2026-10-02", old, "kept on accept")
    store.write_named("probe", Configuration.of("tiny", _sel(seed="dr")))
    named = store.named()
    assert sorted(named) == ["previous-active-2026-10-02", "probe"]
    assert named["previous-active-2026-10-02"].decided_by == \
        (("seed", ("D-015",)),)
    raw = store.named_document()
    assert raw["previous-active-2026-10-02"]["note"] == "kept on accept"
    assert raw["probe"]["digest"] == digest_of(_sel(seed="dr"))
    with pytest.raises(StoreError, match="already exists"):
        store.write_named("probe", Configuration.of("tiny", ACTIVE_SELECTION))
    store.write_named("probe", Configuration.of("tiny", ACTIVE_SELECTION),
                      replace=True)
    assert store.named()["probe"].mapping == ACTIVE_SELECTION


@pytest.mark.parametrize("name", ["", "active"])
def test_write_named_refuses_reserved_and_empty_names(store, name):
    with pytest.raises(StoreError, match="invalid configuration name"):
        store.write_named(name, Configuration.of("tiny", ACTIVE_SELECTION))


def test_write_named_needs_a_named_file(paths):
    write_active_yaml(paths[0], ACTIVE_SELECTION)
    with pytest.raises(StoreError, match="no named-configurations file"):
        YamlSelectionStore(paths[0]).write_named(
            "x", Configuration.of("tiny", ACTIVE_SELECTION))


def test_write_named_refuses_a_corrupt_or_foreign_file(store, paths):
    paths[1].write_text("- a list\n", encoding="utf-8")
    with pytest.raises(StoreError):
        store.write_named("x", Configuration.of("tiny", ACTIVE_SELECTION))
    assert paths[1].read_text(encoding="utf-8") == "- a list\n"
    _write_named(paths[1], {}, theory="other")
    with pytest.raises(StoreError, match="theory"):
        store.write_named("x", Configuration.of("tiny", ACTIVE_SELECTION))


def test_write_named_tolerates_a_file_without_a_theory(store, paths):
    paths[1].write_text("configurations: {}\n", encoding="utf-8")
    store.write_named("x", Configuration.of("tiny", _sel(seed="p0")))
    assert store.named()["x"].mapping["seed"] == "p0"


# ---------------------------------------------------------- integration


def test_resolve_and_enumerate_through_the_yaml_store(store, paths,
                                                      monkeypatch):
    _write_named(paths[1], {"alt": {"overrides": {"seed": "p0"}}})
    theory = make_theory(store=store)
    assert resolve(theory, "seed", environ={CONFIG_ENV: "alt"}) == "p0"
    names = {c.name for c in enumerate_configurations(theory, "assess")}
    assert {"adopted", "alt"} <= names


def test_reading_and_enumerating_never_touch_the_store_files(store, paths):
    _write_named(paths[1], {"alt": {"overrides": {"seed": "p0"}}})
    before = (paths[0].read_bytes(), paths[1].read_bytes(),
              os.stat(paths[0]).st_mtime_ns)
    theory = make_theory(store=store)
    for mode in ("assess", "reassess", "archaeology", "probe-constraint",
                 "single"):
        list(enumerate_configurations(theory, mode))
        count_configurations(theory, mode)
    resolve(theory, "seed", environ={CONFIG_ENV: "alt"})
    after = (paths[0].read_bytes(), paths[1].read_bytes(),
             os.stat(paths[0]).st_mtime_ns)
    assert after == before


def test_write_named_refuses_a_configuration_of_another_theory(store, paths):
    store.write_named("x", Configuration.of("tiny", ACTIVE_SELECTION))
    with pytest.raises(StoreError, match="holds theory 'tiny'"):
        store.write_named("y", Configuration.of("other", ACTIVE_SELECTION))
    paths[1].unlink()
    with pytest.raises(StoreError, match="belongs to theory 'other'"):
        store.write_named("y", Configuration.of("other", ACTIVE_SELECTION))
    assert not paths[1].exists()


def test_a_failed_replace_tolerates_a_vanished_temp_file(tmp_path,
                                                         monkeypatch):
    target = tmp_path / "file.yaml"
    target.write_text("old\n", encoding="utf-8")

    def vanish_then_fail(src, dst):
        os.unlink(src)
        raise OSError("gone")

    monkeypatch.setattr(store_mod.os, "replace", vanish_then_fail)
    with pytest.raises(OSError, match="gone"):
        atomic_write_text(target, "new\n")
    assert target.read_text(encoding="utf-8") == "old\n"
    assert [p.name for p in tmp_path.iterdir()] == ["file.yaml"]
