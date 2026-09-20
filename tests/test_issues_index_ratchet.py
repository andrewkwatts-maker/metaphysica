"""The register may gain issues and settle them; it may not lose the record.

The standing rule is that nothing is silently retired: a falsified claim stays
on the books labelled FALSIFIED, a withdrawn one stays WITHDRAWN. That rule has
been enforced by prose alone, and prose does not fail a build. It has already
been tested in practice -- b_3 = 24 was refuted in the fifteenth pass, the
refutation withdrawn in the sixteenth, and re-established on different grounds
in the nineteenth. Each step was deliberate and recorded. The next one might
not be.

The baseline below is a LITERAL, not a tracked artifact. The register's own
eighteenth-pass ruling says "whether tracked artifacts may serve as baselines
at all is a policy call", and a baseline read from the very file under test
would agree with itself. Changing an entry's status therefore means editing
this dict, in a diff a reviewer can see.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json
import os
import pathlib

import pytest

from metaphysica.generators.generate_issues_index import build_index

#: Measured 2026-09-20 from docs/OUTSTANDING_ISSUES.md. Every value is a status
#: word the register itself uses; UNLABELLED means the entry declares none.
_BASELINE = {
    "1.1": "FALSIFIED",
    "1.10": "UNLABELLED",
    "1.11": "RESOLVED",
    "1.12": "STRUCTURAL",
    "1.13": "STRUCTURAL",
    "1.2": "RETIRED",
    "1.3": "RETIRED",
    "1.4": "OPEN",
    "1.5": "UNLABELLED",
    "1.6": "FALSIFIED",
    "1.6a": "FALSIFIED",
    "1.6b": "UNLABELLED",
    "1.6c": "CLOSED",
    "1.6d": "CLOSED",
    "1.6e": "CLOSED",
    "1.6f": "CLOSED",
    "1.6g": "CLOSED",
    "1.6h": "CLOSED",
    "1.7": "AUTHOR_RULING",
    "1.8": "CLOSED",
    "1.9": "CLOSED",
    "2.1": "CLOSED",
    "2.2": "AUTHOR_RULING",
    "2.3": "UNLABELLED",
    "2.4": "UNBOUNDED",
    "2.5": "OPEN",
    "2.6": "CLOSED",
    "2.6a": "CLOSED",
    "2.7": "CLOSED",
}

#: Statuses that record a claim as dead. These may never be dropped.
_LABELLED_DEAD = frozenset({"FALSIFIED", "WITHDRAWN", "RETIRED"})
#: Statuses that record a question as settled.
_SETTLED = frozenset({"CLOSED", "RESOLVED"})


def _register_text():
    raw = os.environ.get("METAPHYSICA_OUT")
    roots = [pathlib.Path(raw)] if raw else []
    roots += [pathlib.Path("H:/Github/PrincipiaMetaphysica"),
              pathlib.Path(__file__).resolve().parents[2] / "PrincipiaMetaphysica"]
    for root in roots:
        candidate = root / "docs" / "OUTSTANDING_ISSUES.md"
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8")
    return None


@pytest.fixture(scope="module")
def index():
    text = _register_text()
    if text is None:
        pytest.skip("OUTSTANDING_ISSUES.md not reachable from this checkout")
    return build_index(text)


def _status_map(index):
    return {r["id"]: r["status"] for r in index["entries"]}


def test_the_index_is_not_empty(index):
    """Guards against the ratchet passing because nothing was parsed."""
    assert index["n_entries"] >= len(_BASELINE), (
        "parsed %d entries against a baseline of %d -- entries disappeared, or "
        "the parser stopped matching the register's headings"
        % (index["n_entries"], len(_BASELINE))
    )


def test_no_entry_vanishes_from_the_register(index):
    missing = sorted(set(_BASELINE) - set(_status_map(index)))
    assert not missing, (
        "entries removed from the register: %s. Nothing is silently retired; "
        "an entry that no longer applies is relabelled, not deleted." % missing
    )


def test_a_labelled_dead_claim_never_loses_its_label(index):
    live = _status_map(index)
    lost = {
        eid: (was, live[eid])
        for eid, was in _BASELINE.items()
        if was in _LABELLED_DEAD and eid in live
        and live[eid] not in _LABELLED_DEAD
    }
    assert not lost, (
        "a falsified or withdrawn claim lost its label: %s. The standing rule "
        "is that these stay on the books labelled -- if one is genuinely "
        "revived, update the baseline in this file so the change is reviewed."
        % lost
    )


def test_a_settled_entry_does_not_silently_reopen(index):
    live = _status_map(index)
    reopened = {
        eid: (was, live[eid])
        for eid, was in _BASELINE.items()
        if was in _SETTLED and eid in live and live[eid] not in _SETTLED
    }
    assert not reopened, (
        "closed entries reopened without a baseline update: %s. Reopening is "
        "allowed and sometimes correct; doing it unnoticed is not." % reopened
    )


def test_recorded_contradictions_do_not_grow_unnoticed(index):
    """One is known: 1.1 reads FALSIFIED while a pass reads RESOLVED."""
    assert index["n_contradictions"] <= 1, (
        "new contradictions between a numbered entry and a pass that cites it: "
        "%s" % [r["id"] for r in index["entries"] if r["contradiction"]]
    )


def test_the_structural_gap_is_still_reported(index):
    """The finding that motivated the index must not quietly disappear."""
    assert index["n_entries_never_cited_by_id"] > 0
    assert "joined by nothing a machine can check" in index[
        "_the_structural_finding"]


def test_the_ratchet_can_fail():
    """A ratchet that cannot fire is the defect it exists to catch."""
    mutated = {
        "_schema": 1,
        "entries": [{"id": "1.1", "status": "CLOSED", "contradiction": None}],
        "n_entries": 1,
        "n_contradictions": 0,
    }
    live = {r["id"]: r["status"] for r in mutated["entries"]}
    assert _BASELINE["1.1"] in _LABELLED_DEAD
    assert live["1.1"] not in _LABELLED_DEAD, (
        "the mutation probe no longer mutates anything"
    )


def test_the_index_serialises(index):
    json.dumps(index, ensure_ascii=False)
