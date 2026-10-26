"""Lane 2D: decision entry templates and the append-only writer.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from metaphysica.testground.decisions.log import (ACCEPT, REINSTATE, RETIRE,
                                                  parse_log)
from metaphysica.testground.decisions.write import (AcceptEntry,
                                                    ReinstateEntry,
                                                    RetireEntry, append_entry,
                                                    render_accept,
                                                    render_reinstate,
                                                    render_retire)
from tests.testground.test_2d_support import SAMPLE_LOG

DIGEST = "0123456789abcdef"


def _accept(**kw):
    base = dict(decision_id="D-021", date="2026-10-02", theory="toy",
                name="toy-closure", digest=DIGEST, previous_name="toy-active",
                previous_digest="fedcba9876543210",
                kept_as="previous-active-2026-10-02",
                diff={"seed": ("a", "b")})
    base.update(kw)
    return AcceptEntry(**base)


def test_accept_entry_has_heading_target_diff_and_rule():
    text = render_accept(_accept(reason="the closure margin"))
    entry = parse_log(text)[0]
    assert entry.kind == ACCEPT and entry.target_name == "toy-closure"
    assert entry.target_digest == DIGEST and entry.date == "2026-10-02"
    assert "| `seed` | `a` | `b` |" in text
    assert "previous-active-2026-10-02" in text and "D-019" in text
    assert "None supplied" in text and "**Reason.** the closure margin" in text
    assert "Data tie-break" not in text and text.endswith("\n")


def test_accept_entry_with_scores_tiebreak_override_and_notes():
    text = render_accept(_accept(
        assessment_verdict="DATA_TIEBREAK_SUGGESTS", target_verdict="ADOPTABLE",
        deciding_criterion="data",
        scores=[("validity", "(0)", "(0)"), ("data", "(1, 0)", "(0, 0)")],
        data_tiebreak=True, trials_factor=4, override_reason="author said so",
        stale_reasons=["engine changed"], notes=["a note"], diff={}))
    assert "deciding criterion `data`" in text
    assert "| data | (1, 0) | (0, 0) |" in text
    assert "trials factor k = 4" in text and "fitted degree of freedom" in text
    assert "**Override.** author said so" in text
    assert "- overridden: engine changed" in text and "- a note" in text
    assert "selection is identical" in text
    unknown_k = render_accept(_accept(data_tiebreak=True))
    assert "k = unknown" in unknown_k


def test_retire_and_reinstate_entries_parse_back():
    retire = render_retire(RetireEntry(
        "D-022", "2026-10-02", "toy", "seed", "c", "certain", "refuted",
        "considered", evidence="the run", kill_condition="fit < x"))
    entry = parse_log(retire)[0]
    assert entry.kind == RETIRE and entry.target_name == "seed.c"
    assert "archaeology" in retire and "**Evidence.** the run" in retire
    assert "**Kill condition.** fit < x" in retire
    soft = render_retire(RetireEntry("D-022", "2026-10-02", "toy", "seed", "c",
                                     "reassessable", "maybe", "considered"))
    assert "reassess" in soft and "Evidence" not in soft
    back = render_reinstate(ReinstateEntry("D-023", "2026-10-02", "toy",
                                           "seed", "d", "new evidence"))
    entry = parse_log(back)[0]
    assert entry.kind == REINSTATE and entry.status == "REINSTATED"
    assert "certainty `reassessable`" in back


def test_append_keeps_existing_bytes_and_adds_one_separator(tmp_path):
    path = tmp_path / "log.md"
    path.write_bytes(SAMPLE_LOG.encode("utf-8"))
    before = path.read_bytes()
    text = append_entry(path, render_accept(_accept()))
    after = path.read_bytes()
    assert after.startswith(before) and after.decode("utf-8") == text
    assert after[len(before):].startswith(b"\n---\n\n## D-021")
    assert after.endswith(b"\n") and b"\r\n" not in after
    assert [e.id for e in parse_log(text)][-1] == "D-021"


def test_append_after_a_trailing_separator_and_to_new_files(tmp_path):
    path = tmp_path / "log.md"
    # newline="\n": on Windows write_text made this a CRLF log, which
    # append_entry rightly preserves, so the LF assertion failed there.
    path.write_text("## D-001 · 2026-01-01 · G0 · OPEN\n\nx\n\n---", "utf-8", newline="\n")
    text = append_entry(path, "## D-002 · 2026-01-02 · G0 · OPEN\n")
    assert text.count("---") == 1 and text.endswith("OPEN\n")
    fresh = tmp_path / "new.md"
    assert append_entry(fresh, "## D-001 · 2026-01-01 · G0 · OPEN") == \
        "## D-001 · 2026-01-01 · G0 · OPEN\n"


def test_append_preserves_crlf_logs_and_continues_without_separator(tmp_path):
    path = tmp_path / "log.md"
    path.write_bytes(b"## D-001 \xc2\xb7 2026-01-01 \xc2\xb7 G0 \xc2\xb7 OPEN"
                     b"\r\n\r\nbody\r\n")
    append_entry(path, "**Store write failed.** x", separate=False)
    raw = path.read_bytes()
    assert raw.endswith(b"body\r\n\r\n**Store write failed.** x\r\n")
    assert b"---" not in raw
    empty = tmp_path / "empty.md"
    assert append_entry(empty, "note", separate=False) == "note\n"
