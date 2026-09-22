"""68 formulas exist in simulations and never reach the published artifact.

FOUND 2026-09-22, while auditing the ruled-divergence ledger for rows
pointing at formulas nobody publishes. Six such rows turned out to name
formulas that DO exist -- the triple-track collector sees them -- but that
`formulas.json` never carries. Widening the question: the collector walks
637 formulas; the artifact publishes 569. The 68-formula gap is spread
evenly over ~20 modules (4-6 each), which is the signature of whole
modules missing from the publishing path rather than individual formulas
being dropped.

This is NOT the same defect as the mid-registration truncation fixed the
same day (that one lost 61 formulas from simulations that DID publish, and
is closed: 569 published, 0 dangling derivation ids). This is a different
question -- whether every simulation that defines formulas is actually in
the published run -- and it needs a reading per module, not a sweep.

So: the gap is MEASURED and ratcheted here, and the triage is named as
outstanding. The count may fall, never rise. A test that merely asserted
"569 published" would have hidden the gap entirely, which is how it
survived this long.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import json

import pytest

from metaphysica.generators._common import autogen_dir

#: MEASURED 2026-09-22. A ceiling on the GAP, not on either total, so a
#: formula newly published lowers it and a formula newly hidden raises it.
_GAP_CEILING = 68


def _published_ids():
    path = autogen_dir() / "formulas.json"
    if not path.is_file():
        pytest.skip("formulas.json not built")
    payload = json.loads(path.read_text(encoding="utf-8"))
    formulas = payload.get("formulas", payload)
    return set(formulas) if isinstance(formulas, dict) else {
        f.get("id") for f in formulas}


def _collected():
    from tests.test_triple_track import _FORMULAS

    return _FORMULAS


def test_the_publishing_gap_does_not_grow():
    published = _published_ids()
    gap = sorted({fid for _m, fid, _f in _collected()} - published)
    assert len(gap) <= _GAP_CEILING, (
        "%d formulas are defined in simulations but never published, above "
        "the measured ceiling of %d. A formula the site cannot show is a "
        "formula nobody can check. Newest absentees: %s"
        % (len(gap), _GAP_CEILING, gap[-6:])
    )


def test_the_scan_sees_both_sides():
    """A gap ratchet over an empty collector would pass forever."""
    published = _published_ids()
    collected = _collected()
    assert len(collected) > 500, (
        "the collector found %d formulas; it is broken, not the corpus"
        % len(collected))
    assert len(published) > 500, (
        "the artifact carries %d formulas; rebuild before reading this"
        % len(published))


def test_every_ledger_row_names_a_formula_that_exists_somewhere():
    """A ruled-divergence row pointing at nothing is a stale excuse.

    The ledger may legitimately name a formula the artifact does not carry
    (that is the gap above), but never one that no simulation defines --
    that would be a row excusing a divergence that cannot occur.
    """
    from metaphysica.simulations.core.ruled_divergences import (
        RULED_DIVERGENCES,
    )

    known = {fid for _m, fid, _f in _collected()} | _published_ids()
    orphans = sorted(set(RULED_DIVERGENCES) - known)
    assert not orphans, (
        "these ruled-divergence rows name formulas no simulation defines "
        "and no artifact carries, so they excuse nothing and must be "
        "removed: %s" % orphans
    )
