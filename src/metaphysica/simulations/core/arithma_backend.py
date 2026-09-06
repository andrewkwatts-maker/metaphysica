"""One place that decides whether the arithma backend is actually usable.

WHY THIS EXISTS
---------------
Fifty-three modules guard their arithma import as::

    try:
        import arithma as _A
        def _arithma_num(v):
            return _A.Expression.number(float(v))
    except ImportError:
        _A = None
        def _arithma_num(v):
            return None

That guard catches a MISSING package. It cannot see a package that imports
successfully and does not work, and on 2026-09-06 CI hit exactly that: a
stub arithma installed, ``import arithma`` succeeded, and every module then
died at import time with

    AttributeError: 'NoneType' object has no attribute 'number'

because arithma's own fallback binds ``Expression`` to ``None`` when its
compiled extension fails to load. Four test modules failed collection and the
whole ``metaphysica.simulations`` package became unimportable -- a *degraded*
optional dependency turned into a hard failure.

The same blind spot had already shown up in the artifacts as
``arithma_available: false`` alongside 422 formulas none of which carried an
arithma tree: the import worked, every expression did not.

So the question this module answers is not "does it import" but "does it
compute". :data:`ARITHMA` is the module if a probe expression evaluates, and
``None`` otherwise. Callers keep their existing shape -- ``if ARITHMA is
None`` behaves exactly like the old ImportError branch -- and a stub is
treated as absent, which is what it is.
"""
from __future__ import annotations

from typing import Any, Optional

__all__ = ["ARITHMA", "ARITHMA_UNAVAILABLE_REASON", "is_usable"]


def _probe() -> tuple[Optional[Any], str]:
    """Import arithma and confirm it can build and evaluate an expression."""
    try:
        import arithma as module
    except Exception as exc:  # noqa: BLE001 - any failure means unusable
        return None, f"import failed: {type(exc).__name__}: {exc}"

    expression = getattr(module, "Expression", None)
    if expression is None:
        return None, (
            "arithma.Expression is None -- the compiled extension did not "
            "load, so the package is a stub"
        )

    # Build and evaluate. A stub can expose the names and still raise, and a
    # backend that cannot round-trip a literal is no use to the triple-track
    # comparison it exists to serve.
    try:
        number = expression.number(2.0)
        try:
            value = number.evaluate({})
        except TypeError:
            value = number.evaluate()
        if float(value) != 2.0:
            return None, f"probe expression evaluated to {value!r}, expected 2.0"
    except Exception as exc:  # noqa: BLE001
        return None, f"probe expression failed: {type(exc).__name__}: {exc}"

    return module, ""


ARITHMA, ARITHMA_UNAVAILABLE_REASON = _probe()


def is_usable() -> bool:
    """True when the arithma backend can actually compute."""
    return ARITHMA is not None
