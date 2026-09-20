"""Superseded documents stay on the books, and stay out of the pipeline.

The standing rule is that nothing is silently retired, so a withdrawn document
is preserved rather than deleted. The risk that creates is the opposite one: a
preserved document being read as current. `docs/history/` is the quarantine,
and these tests keep it sealed.

RULINGS_ASSESSMENT_2026-08-25.md is the first occupant. It scores theory
branches on an "Accuracy vs data" axis and recommends winners, which is exactly
what `switch_search`'s permanent NO_SELECTION_MADE verdict and the
`tests/test_variants.py` word ban exist to prevent. Preserving it is correct;
letting anything import it would not be.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pathlib

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_HISTORY = _ROOT / "docs" / "history"
_SRC = _ROOT / "src" / "metaphysica"


def _history_docs():
    return sorted(_HISTORY.glob("*.md")) if _HISTORY.is_dir() else []


def test_the_history_directory_exists_and_is_populated():
    """If this fails the quarantine was emptied, which is a silent retirement."""
    assert _history_docs(), "docs/history/ is empty; superseded docs must be kept"


@pytest.mark.parametrize("doc", _history_docs(), ids=lambda p: p.name)
def test_every_superseded_doc_says_so_in_its_first_lines(doc):
    head = "\n".join(doc.read_text(encoding="utf-8").splitlines()[:3]).upper()
    assert "SUPERSEDED" in head, (
        "%s must declare itself superseded in its opening lines, or a reader "
        "arriving mid-file cannot tell it is not current" % doc.name
    )


@pytest.mark.parametrize("doc", _history_docs(), ids=lambda p: p.name)
def test_no_production_module_reads_a_superseded_doc(doc):
    """A quarantined document must not be reachable from the pipeline."""
    stem = doc.stem
    offenders = []
    for py in _SRC.rglob("*.py"):
        text = py.read_text(encoding="utf-8", errors="replace")
        if stem in text or doc.name in text:
            offenders.append(str(py.relative_to(_ROOT)))
    assert not offenders, (
        "%s is referenced by production code: %s. A superseded document may be "
        "cited in prose, never read by the pipeline." % (doc.name, offenders)
    )


def test_the_rulings_assessment_carries_its_three_reasons():
    """The specific reasons must survive; 'superseded' alone loses the lesson."""
    doc = _HISTORY / "RULINGS_ASSESSMENT_2026-08-25.md"
    if not doc.is_file():
        pytest.skip("rulings assessment not present")
    text = doc.read_text(encoding="utf-8")
    for marker in ("anti-tuning guard", "NO_SELECTION_MADE", "b_3 = 24",
                   "The questions survive"):
        assert marker in text, "the stated reason %r went missing" % marker
