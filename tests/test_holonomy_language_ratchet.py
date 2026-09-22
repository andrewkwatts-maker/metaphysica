"""The corpus claims G2 holonomy in files where, on the adopted branch, it is false.

This is a RATCHET, not a repair. The count is measured and pinned; it may fall
and may not rise. Fixing 80-odd files by hand would be a find-and-replace on a
PATH-DEPENDENT claim -- true on `octonion_derived`, false on the adopted
`all_plus_one` -- and that is how the corpus acquired the debt in the first
place. The route out is `geometry_narration`, which generates the sentence from
the live fork.

WHY THE COUNT IS NOT ZERO AND IS NOT BEING DRIVEN TO ZERO TODAY
===============================================================
Most hits are prose describing the INTENDED construction, which is a legitimate
thing to describe. What is not legitimate is asserting the framework HAS G2
holonomy while the adopted phi is the split real form. Separating those two
readings per file is a reading task, not a grep, and doing it badly would
either delete accurate history or leave the false claims in place.

So: the total is pinned as a ceiling, the modules that now KNOW better are
required to be clean, and the narration module is the supported way to say any
of it going forward.

WHAT THIS FILE'S NUMBER COUNTS, AND WHAT IT DOES NOT
====================================================
`_CEILING` counts **source FILES** containing at least one of the four phrases
in `_CLAIM_PHRASES`. It is not a count of occurrences, and it is not a count of
anything a reader of the published site can see. A file with 43 mentions
contributes 1.

Per the author's directive the meaningful measure is **published on-path
strings**, and that one lives in `test_published_holonomy_ratchet.py`:
PUBLISHED STRING OCCURRENCES in the built JSON artifacts, pinned separately and
measured against a fresh build. Both are kept because they move independently:

    this file   rises when a NEW file starts making the claim, even if no
                published text changed.
    that file   rises when existing wording is duplicated into more output,
                which leaves this file's count flat.

The two ceilings differ (92 here, 93 there) because the phrase SETS differ --
this file scans 4 phrases, that one scans the 9 that
`holonomy_wording_audit.phrases()` generates from
`geometry_narration.forbidden_phrases()` plus typographic variants. Neither
number is stale and they are not in conflict; each states its own phrase set.

For the record, measured 2026-09-22 on the adopted branch over the 9-phrase
set: 93 source files, 538 source occurrences, 742 published occurrences. Of the
source occurrences a line-local classifier reads 459 as bare ASSERTION, 43 as
ATTRIBUTED to the literature or a named construction, 14 as CONDITIONAL and 22
as DENIAL -- so the reading task this docstring describes is ~459 sites, not 93
files, and that is why it is not being done with a regex.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import pathlib

import pytest

_SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "metaphysica"

#: MEASURED 2026-09-22 on the adopted branch, across all four phrases in
#: `_CLAIM_PHRASES`. Counts source FILES. A ceiling, not a target. It was first
#: set to 90 from an earlier single-phrase grep and the ratchet immediately
#: failed at 92 -- which is the ratchet working: a number typed from memory is
#: not a measurement. Re-measured 2026-09-22 and it is still exactly 92.
_CEILING = 92

#: Modules that carry the new findings. These must not assert what they refute.
_MUST_BE_CLEAN = (
    "simulations/PM/geometry/geometry_narration.py",
    "simulations/PM/geometry/chi_eff_routes.py",
    "simulations/PM/geometry/generation_selection.py",
    "simulations/PM/geometry/multilinear_degree_audit.py",
    "simulations/PM/geometry/intersection_tensor.py",
    "simulations/PM/geometry/holonomy_wording_audit.py",
    "simulations/PM/geometry/glued_orbit_scan.py",
)

_CLAIM_PHRASES = ("G2 holonomy", "G2-holonomy", "G₂ holonomy",
                  "holonomy group G2")


def _files_asserting_holonomy():
    hits = []
    for path in sorted(_SRC.rglob("*.py")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(phrase in text for phrase in _CLAIM_PHRASES):
            hits.append(path.relative_to(_SRC).as_posix())
    return hits


def test_the_scan_finds_something():
    """A ratchet over an empty scan would pass forever and mean nothing."""
    assert _files_asserting_holonomy(), (
        "no file mentions G2 holonomy, which means the scan is broken rather "
        "than the corpus being clean"
    )


def test_the_holonomy_claim_count_does_not_rise():
    hits = _files_asserting_holonomy()
    assert len(hits) <= _CEILING, (
        "files asserting G2 holonomy rose to %d, above the pinned ceiling of "
        "%d. On the adopted branch phi is the SPLIT real form and no "
        "Riemannian G2 holonomy exists; new claims must go through "
        "geometry_narration. Newest offenders are likely among: %s"
        % (len(hits), _CEILING, hits[-5:])
    )


@pytest.mark.parametrize("relpath", _MUST_BE_CLEAN)
def test_the_modules_that_know_better_do_not_assert_it(relpath):
    """These modules computed the refutation; they may not contradict it."""
    path = _SRC / relpath
    if not path.is_file():
        pytest.skip("%s not present" % relpath)
    text = path.read_text(encoding="utf-8", errors="replace")
    for phrase in _CLAIM_PHRASES:
        if phrase not in text:
            continue
        # Mentioning it to DENY it is fine; asserting it is not.
        for line in text.splitlines():
            if phrase in line:
                lowered = line.lower()
                assert any(marker in lowered for marker in
                           ("no ", "not ", "cannot", "false", "refut",
                            "may_claim", "forbidden", "-holonomy manifold",
                            "corpus", "files.", "files ", "phrase")), (
                    "%s asserts %r without qualification: %s"
                    % (relpath, phrase, line.strip())
                )


def test_the_narration_is_the_supported_route():
    """If this module vanished, the ratchet would have nothing to point at."""
    from metaphysica.simulations.PM.geometry.geometry_narration import (
        forbidden_phrases,
        narrate,
    )

    assert narrate()["claims"]["holonomy"]["sentence"]
    assert "G2 holonomy" in forbidden_phrases(), (
        "on the adopted branch the phrase must be listed as forbidden, with a "
        "reason, or the ratchet has no authority to cite"
    )
