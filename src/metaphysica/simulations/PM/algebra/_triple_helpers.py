"""Triple-track helper facade for the ``PM.algebra`` sector.

Centralises the optional-Arithma wrappers and re-exports the EML helpers
used by every triple-tracked formula in this sector. Each formula passes
``arithma=`` and ``eml=`` trees built from these helpers so that the
SSoT registry's ``triple_assert`` can cross-check Arithma + EML + float.

The Arithma leg degrades to ``None`` when the Rust-backed package is not
installed; the validator skips it silently and uses the EML leg + float.

Arithma operators used (Wave-3 facade): number, neg, sqrt, exp, ln, sin,
cos, pow_, and the operator overloads ``+ - * /``.

Limitations
-----------
Arithma's current integer backend saturates around ``9.2e9``. Formulas
that include large literal scales (M_Planck ≈ 1.22e19, etc.) leave the
``arithma=`` leg as ``None`` until Sprint 6 swaps in a high-precision
representation.
"""
from __future__ import annotations

import math
from typing import Any, Optional

# ── Arithma facade ──────────────────────────────────────────────────────────

try:  # pragma: no cover - optional during early migration
    import arithma as _A  # type: ignore[import-not-found]
    _ARITHMA_AVAILABLE = True
except ImportError:  # pragma: no cover
    _A = None  # type: ignore[assignment]
    _ARITHMA_AVAILABLE = False


def arithma_num(v: float) -> Optional[Any]:
    """Arithma number literal (Expression). Returns None when arithma absent."""
    if not _ARITHMA_AVAILABLE:
        return None
    return _A.Expression.number(float(v))


def arithma_neg(a: Optional[Any]) -> Optional[Any]:
    return None if a is None or not _ARITHMA_AVAILABLE else _A.Expression.neg(a)


def arithma_sqrt(a: Optional[Any]) -> Optional[Any]:
    return None if a is None or not _ARITHMA_AVAILABLE else _A.Expression.sqrt(a)


def arithma_exp(a: Optional[Any]) -> Optional[Any]:
    return None if a is None or not _ARITHMA_AVAILABLE else _A.Expression.exp(a)


def arithma_ln(a: Optional[Any]) -> Optional[Any]:
    return None if a is None or not _ARITHMA_AVAILABLE else _A.Expression.ln(a)


def arithma_sin(a: Optional[Any]) -> Optional[Any]:
    return None if a is None or not _ARITHMA_AVAILABLE else _A.Expression.sin(a)


def arithma_cos(a: Optional[Any]) -> Optional[Any]:
    return None if a is None or not _ARITHMA_AVAILABLE else _A.Expression.cos(a)


def arithma_pow(a: Optional[Any], b: Optional[Any]) -> Optional[Any]:
    if a is None or b is None or not _ARITHMA_AVAILABLE:
        return None
    return _A.Expression.pow_(a, b)


def arithma_pi() -> Optional[Any]:
    """Concrete π literal — Arithma's symbolic constant requires a cache that
    isn't populated in this build, so we substitute math.pi directly."""
    return arithma_num(math.pi)


def arithma_div(a: Optional[Any], b: Optional[Any]) -> Optional[Any]:
    return None if a is None or b is None else a / b


def arithma_mul(a: Optional[Any], b: Optional[Any]) -> Optional[Any]:
    return None if a is None or b is None else a * b


def arithma_add(a: Optional[Any], b: Optional[Any]) -> Optional[Any]:
    return None if a is None or b is None else a + b


def arithma_sub(a: Optional[Any], b: Optional[Any]) -> Optional[Any]:
    return None if a is None or b is None else a - b


def arithma_abs(a: Optional[Any]) -> Optional[Any]:
    """|a| via sqrt(a^2) — Arithma has no direct abs operator."""
    if a is None or not _ARITHMA_AVAILABLE:
        return None
    return _A.Expression.sqrt(_A.Expression.pow_(a, _A.Expression.number(2.0)))


def arithma_b3_leaf() -> Optional[Any]:
    """b₃ = 24 as an Arithma number, paralleling
    :func:`eml_integration.b3_leaf`. Sprint 3's walker uses call-site
    provenance (this function) to tag the leaf as b₃-derived rather than a
    bare literal 24."""
    return arithma_num(24.0)


# ── EML facade (re-export under shorter aliases) ────────────────────────────

from metaphysica.simulations.core.eml_integration import (  # noqa: E402
    eml_scalar,
    eml_div,
    eml_mul,
    eml_add,
    eml_sub,
    eml_neg,
    eml_sqrt,
    eml_pow,
    eml_exp,
    eml_ln,
    eml_sin,
    eml_cos,
    eml_pi,
    b3_leaf,
)


__all__ = [
    # Arithma helpers
    "arithma_num",
    "arithma_neg",
    "arithma_sqrt",
    "arithma_exp",
    "arithma_ln",
    "arithma_sin",
    "arithma_cos",
    "arithma_pow",
    "arithma_pi",
    "arithma_div",
    "arithma_mul",
    "arithma_add",
    "arithma_sub",
    "arithma_abs",
    "arithma_b3_leaf",
    # EML re-exports
    "eml_scalar",
    "eml_div",
    "eml_mul",
    "eml_add",
    "eml_sub",
    "eml_neg",
    "eml_sqrt",
    "eml_pow",
    "eml_exp",
    "eml_ln",
    "eml_sin",
    "eml_cos",
    "eml_pi",
    "b3_leaf",
]
