"""Lane 2D: rationale sections and decision references.

The round-trip test runs on every fork text of the real PM registry
(`simulations.core.variants.FORKS`, imported read-only by the TEST; the test
ground itself never imports simulations).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pytest

from metaphysica.testground.graph.rationale import (TEXT, decision_refs,
                                                    normalise_whitespace,
                                                    parse_rationale,
                                                    rationale_sections,
                                                    split_rationale)


def _real_fork_texts():
    variants = pytest.importorskip("metaphysica.simulations.core.variants")
    out = []
    for fork_id, fork in variants.FORKS.items():
        out.append(("%s.notes" % fork_id, fork.notes))
        out.append(("%s.question" % fork_id, fork.question))
        for opt in fork.options:
            out.append(("%s.%s.consequence" % (fork_id, opt.id),
                        opt.consequence))
            out.append(("%s.%s.summary" % (fork_id, opt.id), opt.summary))
    return out


def test_every_real_fork_text_rejoins_exactly_and_modulo_whitespace():
    texts = _real_fork_texts()
    assert len(texts) > 100
    for name, text in texts:
        sections = split_rationale(text)
        assert "".join(s.raw for s in sections) == text, name
        parts = parse_rationale(text)
        assert (normalise_whitespace(" ".join(parts.values()))
                == normalise_whitespace(text)), name


def test_real_fork_texts_split_on_their_headings():
    variants = pytest.importorskip("metaphysica.simulations.core.variants")
    forks = variants.FORKS
    calibrated = parse_rationale(forks["re_t_adoption"].option(
        "calibrated").consequence)
    assert list(calibrated) == ["buys", "costs"]
    demoted = parse_rationale(forks["re_t_adoption"].option(
        "computed_vacuum").consequence)
    assert list(demoted) == ["buys", "costs", "demoted"]
    assert demoted["demoted"].startswith("DEMOTED 2026-10-01 (D-015):")
    ruled = parse_rationale(forks["chi_eff_route"].notes)
    assert list(ruled)[0] == "ruled" and "D-015" in decision_refs(
        ruled["ruled"])
    # mid-paragraph heading after a sentence end
    assert list(parse_rationale(forks["bulk_signature"].option(
        "24_2").consequence)) == [TEXT, "costs"]
    # "STILL OPEN" inside a sentence is prose, not a heading
    assert "open" not in parse_rationale(forks["bulk_signature"].notes)


def test_headings_with_and_without_qualifiers():
    text = ("Intro line.\nBUYS: a thing.\nCOSTS, measured: a price. "
            "RULED OUT 2026-09-06, on physics. More text.\n"
            "NOT ADOPTED, and that is the point. Tail.\nRE-OPENS ROUTE 1. x")
    sections = split_rationale(text)
    assert [s.key for s in sections] == [TEXT, "buys", "costs", "ruled_out",
                                         "not_adopted", "re_opens"]
    assert sections[2].heading == "COSTS, measured:"
    assert sections[3].heading == "RULED OUT"
    assert sections[4].heading == "NOT ADOPTED"


def test_repeated_headings_get_numbered_keys_and_blank_parts_drop():
    text = "  \nBUYS: one.\nBUYS: two.\nBUYS: three."
    parts = parse_rationale(text)
    assert list(parts) == ["buys", "buys_2", "buys_3"]
    assert parse_rationale("") == {}
    assert parse_rationale("plain prose only") == {TEXT: "plain prose only"}


def test_custom_headings_extend_the_vocabulary():
    text = "WHAT SETTLED IT: a mass. BUYS: x."
    parts = parse_rationale(text, headings=[("WHAT SETTLED IT", "settled"),
                                            ("BUYS", "buys")])
    assert list(parts) == ["settled", "buys"]


def test_lower_case_and_embedded_words_are_not_headings():
    text = "Costs: lower case. OPENED today. The BUYS column. REOPENS no."
    assert list(parse_rationale(text)) == [TEXT]


def test_rationale_sections_carry_refs_in_order():
    text = "Lead D-003.\nDEMOTED 2026-10-01 (D-015): see D-015 and ruling:2026-09-22."
    sections = rationale_sections(text)
    assert [s["key"] for s in sections] == [TEXT, "demoted"]
    assert sections[1]["heading"] == "DEMOTED 2026-10-01 (D-015):"
    assert sections[1]["refs"] == ["D-015", "ruling:2026-09-22"]
    assert sections[1]["body"].startswith("see D-015")


def test_decision_refs_are_unique_and_ordered():
    text = "D-015, D-001 / D-002, D-015 again, ruling:2026-09-22, XD-0011, D-1234"
    assert decision_refs(text) == ("D-015", "D-001", "D-002",
                                   "ruling:2026-09-22")
    assert decision_refs("") == ()
