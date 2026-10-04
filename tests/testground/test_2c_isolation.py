"""Lane 2C: isolated, stamped roots that never leave the base directory.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metaphysica.testground.runner import isolation
from metaphysica.testground.runner.isolation import (
    STAMP_NAME, prepare_root, read_stamp, root_for, safe_segment,
    stamp_digest, stamp_fingerprint, stamped_context, write_json_atomic)
from tests.testground import test_2c_support as tiny

_SCHEMA = (Path(__file__).resolve().parents[2] / "src" / "metaphysica"
           / "testground" / "schemas" / "configuration.schema.json")
FP = "f00dfeedcafe0001"


def test_roots_differ_per_digest_and_follow_the_layout(tmp_path):
    theory = tiny.make_theory()
    a = prepare_root(tmp_path, theory, tiny.cfg("a"), FP)
    b = prepare_root(tmp_path, theory, tiny.cfg("b"), FP)
    assert a != b
    assert a == (tmp_path / "tiny" / FP / tiny.cfg("a").digest).resolve()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["tiny"]


def test_the_stamp_records_what_the_root_holds(tmp_path):
    theory = tiny.make_theory()
    cfg = tiny.cfg("b", "high", name="probe", decided_by=(("mode", ("D-019",)),))
    root = prepare_root(tmp_path, theory, cfg, FP)
    stamp = json.loads((root / STAMP_NAME).read_text(encoding="utf-8"))
    assert stamp["selection"] == {"mode": "b", "seed": "high"}
    assert stamp["digest"] == cfg.digest
    assert stamp["engine_fingerprint"] == FP
    assert stamp["env"] == {tiny.MODE_VAR: "b", tiny.SEED_VAR: "high"}
    assert stamp["decided_by"] == {"mode": ["D-019"]}
    assert stamp["created"].endswith("Z")
    assert stamp_digest(root) == cfg.digest
    assert stamp_fingerprint(root) == FP
    assert read_stamp(root)["name"] == "probe"


def test_the_stamp_validates_against_the_configuration_schema(tmp_path):
    jsonschema = pytest.importorskip("jsonschema")
    root = prepare_root(tmp_path, tiny.make_theory(), tiny.cfg(), FP)
    schema = json.loads(_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(read_stamp(root), schema)


def test_missing_or_corrupt_stamps_read_as_none(tmp_path):
    assert stamp_digest(tmp_path) is None
    assert stamp_fingerprint(tmp_path) is None
    (tmp_path / STAMP_NAME).write_text("{not json", encoding="utf-8")
    assert read_stamp(tmp_path) is None
    (tmp_path / STAMP_NAME).write_text("[1, 2]", encoding="utf-8")
    assert read_stamp(tmp_path) is None
    (tmp_path / STAMP_NAME).write_text('{"digest": 7}', encoding="utf-8")
    assert stamp_digest(tmp_path) is None


@pytest.mark.parametrize("bad", ["", "..", "../x", "a/b", "a\\b", ".hidden",
                                 "x..y", None])
def test_unsafe_path_components_are_refused(bad):
    with pytest.raises(ValueError):
        safe_segment(bad, "thing")


def test_nothing_escapes_the_base(tmp_path):
    base = tmp_path / "base"
    with pytest.raises(ValueError):
        root_for(base, "..", "0" * 16, FP)
    with pytest.raises(ValueError):
        root_for(base, "tiny", "../../evil", FP)
    with pytest.raises(ValueError):
        isolation._inside(base, tmp_path / "elsewhere")
    assert not base.exists()
    assert sorted(p.name for p in tmp_path.iterdir()) == []


def test_fresh_roots_are_emptied_and_reused_roots_kept(tmp_path):
    theory = tiny.make_theory()
    root = prepare_root(tmp_path, theory, tiny.cfg(), FP)
    (root / "stale.json").write_text("{}", encoding="utf-8")
    prepare_root(tmp_path, theory, tiny.cfg(), FP, fresh=False)
    assert (root / "stale.json").exists()
    prepare_root(tmp_path, theory, tiny.cfg(), FP)
    assert not (root / "stale.json").exists()
    assert stamp_digest(root) == tiny.cfg().digest


def test_a_configuration_of_another_theory_is_refused(tmp_path):
    from metaphysica.testground.configurations.model import Configuration
    other = Configuration.of("other", {"mode": "a", "seed": "low"})
    with pytest.raises(ValueError, match="belongs to theory"):
        prepare_root(tmp_path, tiny.make_theory(), other, FP)


def test_stamped_context(tmp_path):
    cfg = tiny.cfg()
    root = prepare_root(tmp_path, tiny.make_theory(), cfg, FP)
    assert stamped_context(cfg, root).stamped
    assert not stamped_context(tiny.cfg("b"), root).stamped
    unrooted = stamped_context(cfg)
    assert unrooted.root is None and not unrooted.stamped


def test_atomic_write_leaves_no_temp_file_on_failure(tmp_path, monkeypatch):
    def explode(*args, **kwargs):
        raise RuntimeError("disk full")

    monkeypatch.setattr(isolation.json, "dump", explode)
    with pytest.raises(RuntimeError):
        write_json_atomic(tmp_path / "x.json", {"a": 1})
    assert list(tmp_path.iterdir()) == []
