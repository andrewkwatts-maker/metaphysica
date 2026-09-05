"""Arithma must cover the dynamic range this framework's physics spans.

WHY THIS EXISTS
---------------
On 2026-09-06 the build went from green to nine failing simulations with no
change to any physics file. The cause was the ``arithma`` dependency, which is
UNPINNED in ``pyproject.toml``: an installed 2.0.4 replaced the published
2.0.2, and 2.0.4 is a FIXED-POINT rewrite. Measured behaviour of 2.0.4:

    usable range        [1e-15, 9.223372e18]     (i64: 2**63 = 9.223372e18)
    below  1e-15        flushed to 0.0
    above  9.223e18     saturated at 9.223372e18

The framework needs roughly 1.9e-93 (``portal-dm-cross-section-v23``) through
4.8e34 (``proton-lifetime``) -- about 128 decades against arithma 2.0.4's 33.
So the portal cross-section evaluated to exactly 0.0 and the proton lifetime
to a saturated value, on the arithma track only.

Two things are worth recording about how this surfaced.

* **The triple-track guard did its job.** Nothing was silently wrong: nine
  simulations failed loudly, naming the expected value and the arithma value
  side by side. That is what a redundant-computation guard is for, and it is
  why the guard must NOT be relaxed to make this pass. The fix is the
  dependency, not the check.

* **The failure mode was silent by nature.** A number library that returns 0.0
  instead of 1.9e-93 does not raise; without a second track to compare
  against, every affected value would have been published as zero.

This test states the requirement as a property of the LIBRARY, so a future
swap fails here with a diagnosis instead of showing up as scattered
simulation failures whose common cause has to be rediscovered.
"""
from __future__ import annotations

import pytest

#: Smallest and largest magnitudes that appear on the arithma track today,
#: taken from the failing formulas rather than chosen: the v23 portal
#: cross-section and the v17.2 proton lifetime.
SMALLEST_REQUIRED = 1.9038579508229144e-93
LARGEST_REQUIRED = 4.757399129595567e34


def _number(value):
    from arithma import Expression

    expr = Expression.number(value)
    try:
        return expr.evaluate({})
    except TypeError:
        # Older arithma took no environment argument.
        return expr.evaluate()


def test_arithma_is_importable():
    pytest.importorskip("arithma")


def test_arithma_represents_the_smallest_value_the_physics_uses():
    """A library that flushes to zero publishes zeros as predictions."""
    pytest.importorskip("arithma")
    got = _number(SMALLEST_REQUIRED)
    assert got != 0.0, (
        f"arithma flushed {SMALLEST_REQUIRED:.3e} to exactly 0.0. This is the "
        f"fixed-point regression seen in the unreleased arithma 2.0.4, whose "
        f"usable range is about [1e-15, 9.2e18]; the published version is "
        f"2.0.2. Do not relax the triple-track tolerances to accommodate it "
        f"-- the affected values would then be published as zero."
    )
    assert got == pytest.approx(SMALLEST_REQUIRED, rel=1e-9)


def test_arithma_represents_the_largest_value_the_physics_uses():
    """Saturation is the same failure with the opposite sign."""
    pytest.importorskip("arithma")
    got = _number(LARGEST_REQUIRED)
    assert got == pytest.approx(LARGEST_REQUIRED, rel=1e-9), (
        f"arithma returned {got!r} for {LARGEST_REQUIRED:.3e}. A saturating "
        f"backend caps the proton lifetime at its own integer limit."
    )


def test_arithma_covers_the_whole_span_in_one_expression():
    """The range matters end to end, not one endpoint at a time."""
    pytest.importorskip("arithma")
    from arithma import Expression

    small = Expression.number(SMALLEST_REQUIRED)
    large = Expression.number(LARGEST_REQUIRED)
    product = small.mul(large)
    try:
        got = product.evaluate({})
    except TypeError:
        got = product.evaluate()
    assert got == pytest.approx(SMALLEST_REQUIRED * LARGEST_REQUIRED, rel=1e-9)


def test_pyproject_pins_arithma():
    """An unpinned numeric backend is how this arrived without warning."""
    import re
    from pathlib import Path

    text = (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(
        encoding="utf-8")
    assert re.search(r'"arithma[=<>~]', text), (
        "arithma is not pinned in pyproject.toml. It is the numeric backend "
        "for one of the three tracks, and an unannounced change to it "
        "rewrites physics values rather than breaking an import."
    )
