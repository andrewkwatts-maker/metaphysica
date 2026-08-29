"""Ordering of the EML cross-check disagreement diagnostics.

WHY THIS EXISTS
---------------
``_classify`` labelled a disagreement by the first pattern that matched,
and the unresolved-reference check ran LAST. So a row evaluated with 0.0
substituted for a missing name was diagnosed by whatever shape its
meaningless number happened to take.

The case that exposed it: ``gauge.qcd_canonical`` computes
``ops.inv(eml_vec('alpha_s_inv'))``. ``alpha_s_inv`` is in no registry, so
it resolved to 0.0, ``inv(0)`` overflowed to 1e300, and the ratio to the
registered 1 is exactly 10^300 -- filed as "off by 10^300", a unit error.
The real fault is that the name does not exist. Diagnosing the artifact
sends the reader looking for a scale factor that was never there.
"""
from __future__ import annotations

import pytest

from metaphysica.generators.eml_param_crosscheck import _classify


TOL, LOOSE = 0.001, 0.01


def test_unresolved_reference_outranks_a_scale_pattern():
    """The regression: 1e300 vs 1 is a clean power of ten AND a missing ref."""
    status, diag = _classify(1e300, 1.0, TOL, LOOSE, ["alpha_s_inv"])
    assert status == "DISAGREE_MISSING_CTX"
    assert "alpha_s_inv" in diag


def test_unresolved_reference_outranks_a_sign_flip():
    status, _ = _classify(-5.0, 5.0, TOL, LOOSE, ["some_name"])
    assert status == "DISAGREE_MISSING_CTX"


def test_scale_is_still_diagnosed_when_nothing_is_missing():
    """The reordering must not blind the scale check on clean rows."""
    status, diag = _classify(1000.0, 1.0, TOL, LOOSE, [])
    assert status == "DISAGREE_SCALE"
    assert "10^3" in diag


def test_sign_flip_is_still_diagnosed_when_nothing_is_missing():
    status, _ = _classify(-5.0, 5.0, TOL, LOOSE, [])
    assert status == "DISAGREE_SIGN"


def test_agreement_is_not_downgraded_by_a_missing_reference():
    """Deliberate: a row that agrees despite a missing ref stays AGREE.

    Reclassifying it would change the headline agreement rate, which is an
    author decision. The build reports these separately instead, so the
    coincidence is visible without being silently re-scored.
    """
    status, _ = _classify(1.0, 1.0, TOL, LOOSE, ["something"])
    assert status == "AGREE"


def test_non_finite_still_wins_over_everything():
    status, _ = _classify(float("nan"), 1.0, TOL, LOOSE, ["x"])
    assert status == "DISAGREE_NONFINITE"


def test_plain_disagreement_reports_relative_error():
    status, diag = _classify(2.0, 1.0, TOL, LOOSE, [])
    assert status == "DISAGREE"
    assert "rel_err" in diag
