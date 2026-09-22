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


def _usable_backend():
    """The arithma module only if it can actually build and evaluate.

    2026-09-14. These tests guarded with ``pytest.importorskip("arithma")``
    and then called ``Expression.number``. That guard asks whether the package
    IMPORTS -- the precise distinction arithma_backend.py was written to make
    -- and every published arithma passes it while failing the next line:
    2.0.1 and 2.0.2 both ship

        Expression = None   # "Wave 3 -- not yet exposed via PyO3"

    so the three range tests died with ``'NoneType' object has no attribute
    'number'`` on every CI run rather than skipping, and CI read red for six
    days over a missing optional dependency.

    A correction to this file's own diagnosis while we are here: the WHY
    section above attributes the failure to arithma 2.0.4's fixed-point range,
    and the commit that left these failing said the pinned 2.0.2 "cannot
    represent the span the physics uses". That is not what the pinned version
    does. It cannot represent ANY value, because it has no Expression class at
    all. The dynamic-range requirement below is unchanged and still the right
    requirement; it simply cannot be evaluated against a backend that does not
    compute, so it skips instead of failing.
    """
    from metaphysica.simulations.core.arithma_backend import (
        ARITHMA,
        ARITHMA_UNAVAILABLE_REASON,
    )

    if ARITHMA is None:
        pytest.skip("arithma backend unusable: %s" % ARITHMA_UNAVAILABLE_REASON)
    return ARITHMA


def _number(value):
    Expression = _usable_backend().Expression

    expr = Expression.number(value)
    try:
        return expr.evaluate({})
    except TypeError:
        # Older arithma took no environment argument.
        return expr.evaluate()


def test_arithma_is_importable():
    pytest.importorskip("arithma")


def test_the_backend_probe_distinguishes_importable_from_usable():
    """Load-bearing: the skip above must be able to NOT fire.

    If the probe reported every arithma usable, the three range requirements
    would skip forever and this file would assert nothing. So check the probe
    against the thing it claims to measure rather than trusting its verdict.

    THREE states, not two. This used to `import arithma` bare, so in an
    environment where the package is simply ABSENT the test ERRORED with
    ModuleNotFoundError while its four siblings skipped cleanly -- an optional
    dependency reported as a broken test, which is the same shape as a build
    halting for want of an extra. Absence is not an excuse to assert nothing,
    though: the probe still makes a checkable promise there, namely that it
    reports the backend unusable. That is now asserted instead of skipped.
    """
    from metaphysica.simulations.core.arithma_backend import ARITHMA

    try:
        import arithma
    except ImportError:
        assert ARITHMA is None, (
            "arithma is not importable at all and the probe still reports a "
            "usable backend -- the probe is not probing"
        )
        return

    if getattr(arithma, "Expression", None) is None:
        assert ARITHMA is None, (
            "arithma.Expression is None and the probe still reports the "
            "backend usable -- the stub guard is not guarding"
        )
    else:
        # The probe promises more than "the class exists": it promises the
        # class evaluates. Hold it to exactly that, so a backend that builds
        # and returns nonsense is reported unusable.
        expr = arithma.Expression.number(2.0)
        try:
            value = expr.evaluate({})
        except TypeError:
            value = expr.evaluate()
        assert (ARITHMA is not None) == (float(value) == 2.0), (
            "the probe's verdict disagrees with whether arithma can evaluate "
            "a literal"
        )


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
    Expression = _usable_backend().Expression

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
