"""Regenerating an unchanged datasheet must produce no diff.

generated_at was restamped on every run, so regenerating rewrote 47 checked-in
datasource files with no semantic change. The cost is not cosmetic: a real edit
arrives invisible inside a wall of timestamp noise, and `git status` stops being
a signal anyone can read. The same class of noise is why a stray directory of
Windows icon-cache .db files sat committed at the repo root for two weeks.

The rule is that generated_at records when the CONTENT was generated, not when
the generator last ran -- so it holds still when nothing changed, and moves the
moment anything does. Both halves are asserted here; the second is what stops
the fix from degrading into "never update the timestamp".

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json

from metaphysica.generators.generate_datasheets import _write_json


def _payload(value, stamp):
    return {
        "name": "hbar",
        "value": value,
        "kind": "physics",
        "_provenance": {"metaphysica_version": "2.3.1",
                        "generated_at": stamp,
                        "sources": ["CODATA2022"]},
    }


def test_rewriting_identical_content_keeps_the_timestamp(tmp_path):
    path = tmp_path / "hbar.json"
    _write_json(path, _payload(6.582119569e-25, "2026-01-01T00:00:00+00:00"))
    first = path.read_text(encoding="utf-8")

    _write_json(path, _payload(6.582119569e-25, "2026-09-20T12:00:00+00:00"))
    assert path.read_text(encoding="utf-8") == first, (
        "an unchanged datasheet was rewritten; regeneration must be a no-op"
    )


def test_a_real_change_still_restamps(tmp_path):
    """The guard against the fix becoming 'freeze the timestamp forever'."""
    path = tmp_path / "hbar.json"
    _write_json(path, _payload(6.582119569e-25, "2026-01-01T00:00:00+00:00"))

    _write_json(path, _payload(1.2345e-99, "2026-09-20T12:00:00+00:00"))
    after = json.loads(path.read_text(encoding="utf-8"))
    assert after["value"] == 1.2345e-99
    assert after["_provenance"]["generated_at"] == "2026-09-20T12:00:00+00:00", (
        "content changed but the timestamp was carried forward; generated_at "
        "must move when the content it describes moves"
    )


def test_a_payload_without_provenance_is_written_unchanged(tmp_path):
    path = tmp_path / "bare.json"
    _write_json(path, {"name": "x", "value": 1})
    _write_json(path, {"name": "x", "value": 2})
    assert json.loads(path.read_text(encoding="utf-8"))["value"] == 2


def test_a_corrupt_existing_file_does_not_block_the_write(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    _write_json(path, _payload(1.0, "2026-09-20T12:00:00+00:00"))
    assert json.loads(path.read_text(encoding="utf-8"))["value"] == 1.0
