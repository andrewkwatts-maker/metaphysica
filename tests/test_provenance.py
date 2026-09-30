"""The provenance registry: every surface's top-down story comes from one list,
and every row carries the evidence its kind demands.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

from metaphysica.simulations.PM.geometry.closed_geometry.provenance import (
    KINDS,
    PROVENANCE,
    by_kind,
)
from metaphysica.simulations.PM.geometry.closed_geometry.references import (
    REFERENCES,
)

_REPO = Path(__file__).resolve().parents[1]


def test_ids_are_unique_and_kinds_known():
    ids = [p.id for p in PROVENANCE]
    assert len(ids) == len(set(ids))
    assert {p.kind for p in PROVENANCE} <= set(KINDS)


def test_every_reference_key_resolves():
    for p in PROVENANCE:
        for key in p.references:
            assert key in REFERENCES, (p.id, key)


def test_a_standard_row_is_cited_or_marked_unverified():
    """Standard physics is never stated without a source -- or, while its
    source is unchecked, it says so."""
    for p in by_kind("STANDARD"):
        assert p.references or not p.verified, p.id


def test_every_finding_names_its_test():
    for p in by_kind("FINDING"):
        target = p.evidence.split("::")[0]
        if target.startswith("tests/"):
            assert (_REPO / target).is_file(), (p.id, p.evidence)
        else:
            assert target.startswith("CG."), (p.id, p.evidence)


def test_both_registers_are_written():
    for p in PROVENANCE:
        assert p.technical.strip() and p.plain.strip(), p.id
        assert "..." not in p.plain, p.id


def test_the_story_has_every_part():
    for kind in ("STANDARD", "POSTULATE", "FINDING", "CORRECTION", "OPEN"):
        assert by_kind(kind), kind
