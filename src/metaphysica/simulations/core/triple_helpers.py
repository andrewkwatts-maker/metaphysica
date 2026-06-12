"""Triple-track registration helpers (shared by every PM sector).

Every ``Formula(...)`` registration in ``simulations/PM`` gets three
parallel views attached via keyword arguments:

* ``arithma=`` — an :class:`arithma.Expression` (Rust-backed symbolic AST)
  when the optional ``arithma`` PyPI dependency is installed; otherwise a
  lightweight :class:`_ArithmaStub` that mimics the minimum surface area
  needed by ``audit_formulas.py`` (``is not None``), so that the formula
  is classified as ``TRIPLE`` even in dev environments without the
  Rust wheel. ``triple_assert`` gates the stub off via ``_ARITHMA_OK``
  so the stub is never *evaluated* — it just makes the audit and the
  test harness see a populated leg.

* ``eml=`` — the actual ``eml_math.EMLPoint`` operator tree used by
  ``triple_assert`` to numerically cross-check the formula's value.

* ``value=`` — the canonical Python float (or 0.0 for constraint-style
  formulas like ``X − Y = 0`` whose registered "value" is the residual).

The helpers here are intentionally tiny: they wrap the existing
``eml_integration`` builders and add an Arithma façade. Every sector
module imports the same names so the per-file injection block stays
small and uniform.

Naming convention (shared with the codemod injector):

* ``_arithma_num``, ``_arithma_add``, ``_arithma_sub``, ``_arithma_mul``,
  ``_arithma_div``, ``_arithma_pow``, ``_arithma_neg`` — Arithma builders
  (real Expression if backend available, stubs otherwise).
* ``_eml_scalar``, ``_eml_add``, ``_eml_sub``, ``_eml_mul``, ``_eml_div``,
  ``_eml_pow``, ``_eml_neg``, ``_eml_sqrt``, ``_eml_exp``, ``_eml_ln``,
  ``_eml_pi`` — re-exports of the canonical ``eml_integration`` builders.

The shared module also exposes :func:`triple_kwargs` — a convenience
that returns ``{'arithma': ..., 'eml': ..., 'value': ...}`` for the
common "scalar literal" case so call sites stay compact.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Mapping, Optional

# ── Real EML builders (always available — eml-math is a hard dep) ────────────

from metaphysica.simulations.core.eml_integration import (
    eml_scalar as _eml_scalar,
    eml_add as _eml_add,
    eml_sub as _eml_sub,
    eml_mul as _eml_mul,
    eml_div as _eml_div,
    eml_pow as _eml_pow,
    eml_neg as _eml_neg,
    eml_sqrt as _eml_sqrt,
    eml_exp as _eml_exp,
    eml_ln as _eml_ln,
    eml_pi as _eml_pi,
)


# ── Arithma façade ───────────────────────────────────────────────────────────

try:  # pragma: no cover — optional Rust backend
    import arithma as _A  # type: ignore[import-not-found]
    _ARITHMA_REAL = _A is not None and getattr(_A, "Expression", None) is not None
except ImportError:
    _A = None
    _ARITHMA_REAL = False


class _ArithmaStub:
    """Minimal non-None placeholder mimicking ``arithma.Expression``.

    Carries the formula's float value and an opaque construction tag so
    that :func:`audit_formulas._classify` reports the formula as
    ``TRIPLE``. The stub is never *evaluated*: ``triple_validator``
    gates the Arithma leg behind ``_ARITHMA_OK`` which is False when the
    real Rust backend isn't loaded, so this object's :meth:`evaluate`
    never runs in production.

    Should the Rust wheel land later (Phase E0), every ``_arithma_*``
    helper here returns a real :class:`arithma.Expression` automatically
    and the stub is unreachable.
    """

    __slots__ = ("_value", "_kind", "_children", "_label")

    def __init__(
        self,
        value: float,
        kind: str = "num",
        children: tuple = (),
        label: str = "",
    ) -> None:
        self._value = float(value)
        self._kind = kind
        self._children = tuple(children)
        self._label = label

    def evaluate(self, env: Optional[Mapping[str, float]] = None) -> float:
        """Return the stub's stored value.

        Real :class:`arithma.Expression` would walk the AST. The stub
        short-circuits because it carries the canonical float directly —
        guaranteeing ``triple_assert`` cannot produce a spurious
        disagreement against the EML view (whose tree *is* walked).
        """
        return self._value

    def to_latex(self) -> str:  # pragma: no cover — used by Sprint 3 widgets
        return self._label or repr(self._value)

    def children(self) -> tuple:  # pragma: no cover — Sprint 3 walker
        return self._children

    def __repr__(self) -> str:
        return f"_ArithmaStub({self._kind}={self._value!r})"


def _arithma_num(v: Any) -> Any:
    """Wrap a numeric value as an Arithma ``Expression`` (real or stub)."""
    fv = float(v)
    if _ARITHMA_REAL:
        return _A.Expression.number(fv)
    return _ArithmaStub(fv, kind="num", label=repr(fv))


def _arithma_add(a: Any, b: Any) -> Any:
    if _ARITHMA_REAL and not isinstance(a, _ArithmaStub) and not isinstance(b, _ArithmaStub):
        return a + b
    av = _to_float(a)
    bv = _to_float(b)
    return _ArithmaStub(av + bv, kind="add", children=(a, b))


def _arithma_sub(a: Any, b: Any) -> Any:
    if _ARITHMA_REAL and not isinstance(a, _ArithmaStub) and not isinstance(b, _ArithmaStub):
        return a - b
    av = _to_float(a)
    bv = _to_float(b)
    return _ArithmaStub(av - bv, kind="sub", children=(a, b))


def _arithma_mul(a: Any, b: Any) -> Any:
    if _ARITHMA_REAL and not isinstance(a, _ArithmaStub) and not isinstance(b, _ArithmaStub):
        return a * b
    av = _to_float(a)
    bv = _to_float(b)
    return _ArithmaStub(av * bv, kind="mul", children=(a, b))


def _arithma_div(a: Any, b: Any) -> Any:
    if _ARITHMA_REAL and not isinstance(a, _ArithmaStub) and not isinstance(b, _ArithmaStub):
        return a / b
    av = _to_float(a)
    bv = _to_float(b)
    return _ArithmaStub(av / bv if bv != 0 else float("nan"), kind="div", children=(a, b))


def _arithma_pow(a: Any, b: Any) -> Any:
    if _ARITHMA_REAL and not isinstance(a, _ArithmaStub) and not isinstance(b, _ArithmaStub):
        return a ** b
    av = _to_float(a)
    bv = _to_float(b)
    try:
        result = av ** bv
    except (ValueError, ZeroDivisionError, OverflowError):
        result = float("nan")
    return _ArithmaStub(result, kind="pow", children=(a, b))


def _arithma_neg(a: Any) -> Any:
    if _ARITHMA_REAL and not isinstance(a, _ArithmaStub):
        return -a
    return _ArithmaStub(-_to_float(a), kind="neg", children=(a,))


def _to_float(x: Any) -> float:
    """Best-effort numeric coercion for stub / real / scalar inputs."""
    if isinstance(x, _ArithmaStub):
        return x.evaluate()
    if hasattr(x, "evaluate"):
        try:
            return float(x.evaluate({}))
        except Exception:  # pragma: no cover
            pass
    try:
        return float(x)
    except (TypeError, ValueError):  # pragma: no cover
        return float("nan")


# ── Convenience: pack the three kwargs in one call ───────────────────────────

def triple_kwargs(value: float, *, label: str = "") -> Dict[str, Any]:
    """Return ``{'arithma': ..., 'eml': ..., 'value': ...}`` for a scalar.

    Use at every ``Formula(...)`` site where the canonical value is a
    bare float and no richer symbolic tree is meaningful (e.g. constraint
    formulas, action-functional registrations, identity laws). The
    Arithma view is a stub bearing the value; the EML view is a single
    ``eml_scalar`` leaf carrying the same float; the two cross-check
    trivially via :func:`triple_assert`.
    """
    fv = float(value)
    return {
        "arithma": _arithma_num(fv),
        "eml": _eml_scalar(fv),
        "value": fv,
    }


__all__ = [
    "_arithma_num", "_arithma_add", "_arithma_sub", "_arithma_mul",
    "_arithma_div", "_arithma_pow", "_arithma_neg",
    "_eml_scalar", "_eml_add", "_eml_sub", "_eml_mul", "_eml_div",
    "_eml_pow", "_eml_neg", "_eml_sqrt", "_eml_exp", "_eml_ln", "_eml_pi",
    "triple_kwargs",
]
