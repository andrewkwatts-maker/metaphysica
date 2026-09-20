"""A no-op build must not rewrite the artifact tree.

A timestamp records when the CONTENT was generated, not when the generator last
ran. Restamping unconditionally meant a build with no semantic change rewrote
everything, so a real edit arrived invisible inside a wall of churn and
`git status` stopped being a signal anyone could read. That is not cosmetic: it
is how three Windows icon-cache files sat committed at a repo root for two weeks,
and it is why a changed parameter cannot be told apart from a rebuild.

MEASURED, on the build tree of 299 JSON artifacts:

    before   164 files rewritten by a no-op build
    after     22 files rewritten

The 22 that remain are top-level reports whose writers have not yet been moved
onto this helper -- parameters.json, formulas.json, GATES_72.json,
observer_report.json and the rest. They are recorded rather than quietly
tolerated, and `_common.write_json_stable` is the single place to fix them.

Both halves of the rule are tested here. "Never update the timestamp" would be
the same defect facing the other way, so a real content change must still
restamp.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json

import pytest

from metaphysica.generators._common import (
    TIMESTAMP_KEYS,
    write_json_stable,
)


def _cert(value, stamp):
    return {
        "proof_id": "G01_integer_root_parity",
        "timestamp": stamp,
        "evaluation": {"measured": value, "verdict": "PASS"},
        "references": ["acharya_witten2001"],
    }


# --------------------------------------------------------- the stable half

def test_rewriting_identical_content_leaves_the_file_byte_identical(tmp_path):
    path = tmp_path / "G01.json"
    changed = write_json_stable(path, _cert(288, "2026-01-01T00:00:00Z"))
    assert changed is True, "the first write is a change"
    first = path.read_bytes()

    changed = write_json_stable(path, _cert(288, "2026-09-21T12:00:00Z"))
    assert changed is False, "an unchanged payload must report no change"
    assert path.read_bytes() == first, (
        "a no-op write rewrote the file; the churn defect is back"
    )


def test_nested_timestamps_are_carried_too(tmp_path):
    """The datasheets keep theirs under _provenance, not at top level."""
    path = tmp_path / "hbar.json"
    make = lambda stamp: {
        "name": "hbar",
        "value": 6.582119569e-25,
        "_provenance": {"metaphysica_version": "2.3.1",
                        "generated_at": stamp,
                        "sources": ["CODATA2022"]},
    }
    write_json_stable(path, make("2026-01-01T00:00:00Z"))
    first = path.read_bytes()
    assert write_json_stable(path, make("2026-09-21T12:00:00Z")) is False
    assert path.read_bytes() == first


def test_timestamps_inside_lists_are_carried(tmp_path):
    path = tmp_path / "many.json"
    make = lambda stamp: {"certificates": [
        {"id": 1, "timestamp": stamp}, {"id": 2, "timestamp": stamp}]}
    write_json_stable(path, make("2026-01-01T00:00:00Z"))
    first = path.read_bytes()
    assert write_json_stable(path, make("2026-09-21T12:00:00Z")) is False
    assert path.read_bytes() == first


# --------------------------------------------------------- the moving half

def test_a_real_change_still_restamps(tmp_path):
    """The guard against the fix degrading into 'freeze time forever'."""
    path = tmp_path / "G01.json"
    write_json_stable(path, _cert(288, "2026-01-01T00:00:00Z"))

    changed = write_json_stable(path, _cert(290, "2026-09-21T12:00:00Z"))
    assert changed is True, "a changed payload must report a change"
    after = json.loads(path.read_text(encoding="utf-8"))
    assert after["evaluation"]["measured"] == 290
    assert after["timestamp"] == "2026-09-21T12:00:00Z", (
        "content moved but the timestamp was carried forward; a timestamp must "
        "move when the content it describes moves"
    )


def test_a_change_buried_deep_still_counts(tmp_path):
    path = tmp_path / "G01.json"
    write_json_stable(path, _cert(288, "2026-01-01T00:00:00Z"))
    payload = _cert(288, "2026-09-21T12:00:00Z")
    payload["evaluation"]["verdict"] = "FAIL"
    assert write_json_stable(path, payload) is True
    assert json.loads(path.read_text(encoding="utf-8"))["timestamp"] == \
        "2026-09-21T12:00:00Z"


# --------------------------------------------------------- robustness

def test_a_corrupt_existing_file_does_not_block_the_write(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    assert write_json_stable(path, _cert(1, "2026-09-21T12:00:00Z")) is True
    assert json.loads(path.read_text(encoding="utf-8"))["evaluation"]["measured"] == 1


def test_a_payload_with_no_timestamp_is_written_unchanged(tmp_path):
    path = tmp_path / "bare.json"
    write_json_stable(path, {"a": 1})
    assert write_json_stable(path, {"a": 2}) is True
    assert json.loads(path.read_text(encoding="utf-8"))["a"] == 2


def test_missing_parent_directories_are_created(tmp_path):
    path = tmp_path / "deep" / "nested" / "x.json"
    write_json_stable(path, {"a": 1})
    assert path.is_file()


def test_the_timestamp_key_set_is_declared_and_non_empty():
    """If this were empty the helper would be a plain writer wearing a name."""
    assert "timestamp" in TIMESTAMP_KEYS
    assert "generated_at" in TIMESTAMP_KEYS
    assert len(TIMESTAMP_KEYS) >= 2


def test_the_certificate_generator_uses_the_helper():
    """Traced, so the 164-file fix cannot be silently reverted."""
    import inspect

    from metaphysica.generators import generate_72_certificates as gen

    source = inspect.getsource(gen)
    assert "write_json_stable" in source, (
        "the certificate generator stopped using the stable writer; a no-op "
        "build will rewrite 164 files again"
    )
    assert source.count("json.dump(cert") == 0, (
        "a raw json.dump of a certificate is back"
    )
