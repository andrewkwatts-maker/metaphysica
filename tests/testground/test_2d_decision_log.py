"""Lane 2D: parsing a decision log (synthetic and the real site log, read-only).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from metaphysica.testground.decisions.log import (ACCEPT, ADDENDUM, ENTRY,
                                                  RESULT, VERIFICATION,
                                                  DecisionLog, exists,
                                                  is_decision_id, load_log,
                                                  next_id, parse_heading,
                                                  parse_log)
from tests.testground.test_2d_support import SAMPLE_LOG

REAL_LOG = Path("H:/Github/PrincipiaMetaphysica/docs/DECISION_LOG.md")


@pytest.mark.parametrize("heading, expected", [
    ("D-001 · 2026-09-30 · G0 · PRE-REGISTERED",
     dict(ids=("D-001",), date="2026-09-30", kind=ENTRY, gate="G0",
          status="PRE-REGISTERED", title="")),
    ("D-001 · RESULT · 2026-09-30 · CONFIRMED (lead run)",
     dict(kind=RESULT, label="RESULT", status="CONFIRMED (lead run)")),
    ("D-001 / D-002 · INDEPENDENT VERIFICATION · 2026-09-30",
     dict(ids=("D-001", "D-002"), kind=VERIFICATION,
          status="INDEPENDENT VERIFICATION")),
    ("D-003 · ADDENDUM · the split form does not support the resolution",
     dict(date=None, kind=ADDENDUM, status="ADDENDUM",
          title="the split form does not support the resolution")),
    ("D-003 · ADDENDUM 2 · 2026-10-02 · the glued form",
     dict(kind=ADDENDUM, label="ADDENDUM 2", title="the glued form")),
    ("D-015 · 2026-10-01 · RULINGS — the author's, on the four held decisions",
     dict(status="RULINGS", title="the author's, on the four held decisions")),
    ("D-008 · BLIND VERIFICATION · 2026-10-01 — H1, H2, H4 confirmed",
     dict(kind=VERIFICATION, date="2026-10-01", title="H1, H2, H4 confirmed")),
    ("D-010 · 2026-09-30 · open problems C2 + C3 · PRE-REGISTERED",
     dict(gate="open problems C2 + C3", status="PRE-REGISTERED")),
    ("D-021 · 2026-10-02 · PATH ACCEPT · toy-closure",
     dict(kind=ACCEPT, status="ACCEPTED", title="toy-closure")),
])
def test_heading_shapes(heading, expected):
    parts = parse_heading(heading)
    for key, value in expected.items():
        assert parts[key] == value, (key, parts)


def test_non_decision_headings_are_ignored():
    assert parse_heading("How decisions are made (author's delegation)") is None
    assert parse_heading("D-01 · short id") is None


def test_sample_log_entries_bodies_and_fences():
    entries = parse_log(SAMPLE_LOG)
    assert [e.ids for e in entries] == [("D-001",), ("D-001",), ("D-002",),
                                        ("D-001", "D-002"), ("D-002",)]
    first = entries[0]
    assert first.line == 11
    assert first.summary == "**Question.** Does the seed close? It is asked first."
    assert not first.body.endswith("---")
    assert "D-999" in entries[2].body          # fenced heading stays in the body


def test_decision_merge_and_lookups():
    log = DecisionLog.parse(SAMPLE_LOG)
    assert log.ids() == ["D-001", "D-002"]
    assert log.exists("D-002") and not log.exists("D-003")
    assert log.next_id() == "D-003"
    d1 = log.decision("D-001")
    assert d1.date == "2026-09-30"
    assert d1.title == "Does the seed close?"          # derived: no heading title
    assert d1.status == "INDEPENDENT VERIFICATION"     # latest entry
    d2 = log.decision("D-002")
    assert d2.title == "the author's, on the seed"
    assert d2.status == "ADDENDUM" and d2.date == "2026-10-01"
    assert d2.as_dict()["entries"][0]["kind"] == ENTRY
    assert log.decision("D-404") is None
    assert [d.id for d in log.decisions()] == ["D-001", "D-002"]
    assert len(log.of_kind(RESULT)) == 1


def test_module_helpers_and_missing_files(tmp_path):
    path = tmp_path / "log.md"
    assert next_id(path) == "D-001" and not exists(path, "D-001")
    path.write_text(SAMPLE_LOG, encoding="utf-8")
    assert next_id(path) == "D-003" and exists(str(path), "D-001")
    assert load_log(path).path == path
    assert is_decision_id("D-019") and not is_decision_id("D-19")


def test_long_derived_titles_are_cut():
    text = "## D-001 · 2026-01-01 · G0 · OPEN\n\n" + "word " * 60 + "end.\n"
    title = DecisionLog.parse(text).decision("D-001").title
    assert len(title) == 120 and title.endswith("…")


def test_accept_entries_expose_their_target():
    text = ("## D-021 · 2026-10-02 · PATH ACCEPT · toy-closure\n\n"
            "**Target.** Configuration `toy-closure`, digest "
            "`0123456789abcdef`, of theory `toy`.\n")
    entry = parse_log(text)[0]
    assert entry.target_name == "toy-closure"
    assert entry.target_digest == "0123456789abcdef"
    assert parse_log(SAMPLE_LOG)[0].target_digest is None


@pytest.mark.skipif(not REAL_LOG.is_file(), reason="site repo absent")
def test_the_real_decision_log_parses_read_only():
    before = hashlib.sha256(REAL_LOG.read_bytes()).hexdigest()
    log = load_log(REAL_LOG)
    raw = REAL_LOG.read_text(encoding="utf-8")
    headings = [l for l in raw.splitlines() if re.match(r"^## D-\d{3}", l)]
    assert len(log.entries) == len(headings)
    numbers = sorted(int(i[2:]) for i in log.ids())
    assert numbers == list(range(1, numbers[-1] + 1))   # no gaps
    assert log.next_id() == "D-%03d" % (numbers[-1] + 1)
    assert len(log.entries_for("D-008")) >= 2
    assert any(e.ids == ("D-001", "D-002") for e in log.entries)
    assert log.decision("D-015").title.startswith("the author's")
    d19 = log.entries_for("D-019")[0]
    assert d19.gate == "PATH ASSESSMENT" and d19.status.startswith(
        "PRE-REGISTERED")
    assert all(e.date for e in log.entries
               if e.kind not in (ADDENDUM,)), "every non-addendum is dated"
    assert hashlib.sha256(REAL_LOG.read_bytes()).hexdigest() == before
