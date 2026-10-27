"""
QED sector triple-track helpers (Sprint 2).
============================================

The nine QED kernels (Avogadro, Compton, Faraday, Hartree, magnetic flux,
molar gas, Stefan-Boltzmann, von Klitzing, weak mixing) all share the same
Decad-Cubic Projection structure:

    manifest = bulk * (1 + epsilon)^n
    manifest = bulk / (1 + epsilon)^n     (inverse cubic, "Torsion Gate")
    manifest = bulk * (1+epsilon) * (1-epsilon)^2  (Bohr / Hartree gate)

with epsilon = 1 / (_roots_total * DECAD^2) = 1 / 28800 from the SSoT.

This module centralises the Arithma + EML tree builders so each kernel only
has to call one helper per formula. Sprint 3's b3-traceback walker chains
through *_roots_total* (=288 = 12 * b3) naturally; for now we expose epsilon
as a SSoT-sourced numeric leaf — the walker will still see ``roots_total``
in the per-formula derivation metadata.

Arithma falls through to ``None`` when the wheel isn't built (e.g. dev
machines); the triple-track validator skips a leg cleanly in that case.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from typing import Any, Optional

from metaphysica.simulations.core.FormulasRegistry import get_registry
from metaphysica.simulations.core.eml_integration import (
    eml_scalar,
    eml_add,
    eml_sub,
    eml_mul,
    eml_div,
    eml_pow,
    eml_sqr,
)


# ── Optional Arithma backend ─────────────────────────────────────────────────

try:  # pragma: no cover - exercised only when the Rust wheel is installed
    import arithma as _A  # type: ignore[import-not-found]
    _ARITHMA_OK = True
except ImportError:  # pragma: no cover
    _A = None  # type: ignore[assignment]
    _ARITHMA_OK = False


def arithma_num(v: float) -> Optional[Any]:
    """Wrap a Python float as an Arithma Expression.number, or None if unavailable."""
    if not _ARITHMA_OK:
        return None
    return _A.Expression.number(float(v))


def arithma_add(a: Optional[Any], b: Optional[Any]) -> Optional[Any]:
    if a is None or b is None:
        return None
    return a + b


def arithma_sub(a: Optional[Any], b: Optional[Any]) -> Optional[Any]:
    if a is None or b is None:
        return None
    return a - b


def arithma_mul(a: Optional[Any], b: Optional[Any]) -> Optional[Any]:
    if a is None or b is None:
        return None
    return a * b


def arithma_div(a: Optional[Any], b: Optional[Any]) -> Optional[Any]:
    if a is None or b is None:
        return None
    return a / b


def arithma_pow(a: Optional[Any], b: Optional[Any]) -> Optional[Any]:
    if a is None or b is None:
        return None
    return a ** b


# ── SSoT-sourced QED epsilon ─────────────────────────────────────────────────

def qed_epsilon() -> float:
    """Return the Decad-Cubic projection parameter epsilon = 1/(_roots_total*DECAD^2)."""
    reg = get_registry()
    return 1.0 / (reg._roots_total * (reg.DECAD ** 2))


# ── Arithma builders for the recurring QED gates ─────────────────────────────

def arithma_inverse_cubic(bulk: float, epsilon: float) -> Optional[Any]:
    """Arithma tree for: bulk / (1 + epsilon)."""
    if not _ARITHMA_OK:
        return None
    one_plus = arithma_add(arithma_num(1.0), arithma_num(epsilon))
    return arithma_div(arithma_num(bulk), one_plus)


def arithma_direct_expansion(bulk: float, epsilon: float) -> Optional[Any]:
    """Arithma tree for: bulk * (1 + epsilon)."""
    if not _ARITHMA_OK:
        return None
    one_plus = arithma_add(arithma_num(1.0), arithma_num(epsilon))
    return arithma_mul(arithma_num(bulk), one_plus)


def arithma_quad_gate(bulk: float, epsilon: float) -> Optional[Any]:
    """Arithma tree for: bulk * (1 + epsilon)^4 (Stefan-Boltzmann)."""
    if not _ARITHMA_OK:
        return None
    one_plus = arithma_add(arithma_num(1.0), arithma_num(epsilon))
    return arithma_mul(arithma_num(bulk), arithma_pow(one_plus, arithma_num(4.0)))


def arithma_double_gate(bulk: float, epsilon: float) -> Optional[Any]:
    """Arithma tree for: bulk * (1 + epsilon) * (1 - epsilon)^2 (Hartree energy)."""
    if not _ARITHMA_OK:
        return None
    one_plus = arithma_add(arithma_num(1.0), arithma_num(epsilon))
    one_minus = arithma_sub(arithma_num(1.0), arithma_num(epsilon))
    return arithma_mul(
        arithma_mul(arithma_num(bulk), one_plus),
        arithma_pow(one_minus, arithma_num(2.0)),
    )


def arithma_inverse_double_gate(codata: float, epsilon: float) -> Optional[Any]:
    """Arithma tree for: codata / [(1+ε)(1-ε)²] (Hartree bulk derivation)."""
    if not _ARITHMA_OK:
        return None
    one_plus = arithma_add(arithma_num(1.0), arithma_num(epsilon))
    one_minus = arithma_sub(arithma_num(1.0), arithma_num(epsilon))
    denom = arithma_mul(one_plus, arithma_pow(one_minus, arithma_num(2.0)))
    return arithma_div(arithma_num(codata), denom)


def arithma_neutral_bridge(na_bulk: float, kb_bulk: float, epsilon: float) -> Optional[Any]:
    """Arithma tree for molar gas: (na_bulk/(1+eps)) * (kb_bulk*(1+eps)).

    The two ε factors cancel exactly — R is the Pleromic invariant — but we
    keep the symbolic form to honour the gate structure.
    """
    if not _ARITHMA_OK:
        return None
    one_plus = arithma_add(arithma_num(1.0), arithma_num(epsilon))
    return arithma_mul(
        arithma_div(arithma_num(na_bulk), one_plus),
        arithma_mul(arithma_num(kb_bulk), one_plus),
    )


# ── EML builders for the recurring QED gates ─────────────────────────────────

def eml_inverse_cubic(bulk: float, epsilon: float):
    """EML tree for: bulk / (1 + epsilon)."""
    one_plus = eml_add(eml_scalar(1.0), eml_scalar(epsilon))
    return eml_div(eml_scalar(bulk), one_plus)


def eml_direct_expansion(bulk: float, epsilon: float):
    """EML tree for: bulk * (1 + epsilon)."""
    one_plus = eml_add(eml_scalar(1.0), eml_scalar(epsilon))
    return eml_mul(eml_scalar(bulk), one_plus)


def eml_quad_gate(bulk: float, epsilon: float):
    """EML tree for: bulk * (1 + epsilon)^4 (Stefan-Boltzmann)."""
    one_plus = eml_add(eml_scalar(1.0), eml_scalar(epsilon))
    return eml_mul(eml_scalar(bulk), eml_pow(one_plus, eml_scalar(4.0)))


def eml_double_gate(bulk: float, epsilon: float):
    """EML tree for: bulk * (1 + epsilon) * (1 - epsilon)^2 (Hartree energy)."""
    one_plus = eml_add(eml_scalar(1.0), eml_scalar(epsilon))
    one_minus = eml_sub(eml_scalar(1.0), eml_scalar(epsilon))
    return eml_mul(eml_mul(eml_scalar(bulk), one_plus), eml_sqr(one_minus))


def eml_inverse_double_gate(codata: float, epsilon: float):
    """EML tree for: codata / [(1+ε)(1-ε)²] (Hartree bulk derivation)."""
    one_plus = eml_add(eml_scalar(1.0), eml_scalar(epsilon))
    one_minus = eml_sub(eml_scalar(1.0), eml_scalar(epsilon))
    denom = eml_mul(one_plus, eml_sqr(one_minus))
    return eml_div(eml_scalar(codata), denom)


def eml_neutral_bridge(na_bulk: float, kb_bulk: float, epsilon: float):
    """EML tree for molar gas: (na_bulk/(1+eps)) * (kb_bulk*(1+eps))."""
    one_plus = eml_add(eml_scalar(1.0), eml_scalar(epsilon))
    return eml_mul(
        eml_div(eml_scalar(na_bulk), one_plus),
        eml_mul(eml_scalar(kb_bulk), one_plus),
    )


# Re-export the low-level helpers callers may need.
__all__ = [
    "arithma_num",
    "arithma_add",
    "arithma_sub",
    "arithma_mul",
    "arithma_div",
    "arithma_pow",
    "arithma_inverse_cubic",
    "arithma_direct_expansion",
    "arithma_quad_gate",
    "arithma_double_gate",
    "arithma_inverse_double_gate",
    "arithma_neutral_bridge",
    "eml_inverse_cubic",
    "eml_direct_expansion",
    "eml_quad_gate",
    "eml_double_gate",
    "eml_inverse_double_gate",
    "eml_neutral_bridge",
    "qed_epsilon",
    "qed_gate_kwargs",
]


# ── Checked values: float + Arithma tree + EML tree per gate ─────────────────
#
# Each gate formula is X_bulk * (1+eps)^n (or its inverse) with CODATA inputs.
# The float is plain Python; the two trees come from one closed_form spec, with
# eps = 1/(288 * 10^2) = 1/28800 (roots_total * DECAD^2). The 288 is a literal,
# not 12*b3: the live registry b3 is 43 (elder_kads), which would give 1/51600.

_EPS_PY = 1.0 / 28800.0
_EPS = ("div", 1, ("mul", 288, ("pow", 10, 2)))
_UP = ("add", 1, _EPS)
_DN = ("sub", 1, _EPS)
_DOUBLE = ("mul", _UP, ("pow", _DN, 2))
_CODATA_NA = 6.02214076e23
_CODATA_KB = 1.380649e-23


def _gate_table():
    e = _EPS_PY
    dbl = (1 + e) * (1 - e) ** 2
    return {
        "avogadro-inverse-cubic": (_CODATA_NA, ("div", "x", _UP), {"x": _CODATA_NA * (1 + e)}),
        "compton-bulk-derivation": (2.42631023867e-12 * (1 + e), ("mul", "x", _UP), {"x": 2.42631023867e-12}),
        "compton-inverse-cubic-projection": (2.42631023867e-12, ("div", "x", _UP), {"x": 2.42631023867e-12 * (1 + e)}),
        "faraday-inverse-cubic": (96485.33212, ("div", "x", _UP), {"x": 96485.33212 * (1 + e)}),
        "hartree-bulk-derivation": (4.3597447222071e-18 / dbl, ("div", "x", _DOUBLE), {"x": 4.3597447222071e-18}),
        "hartree-inverse-double-gate": (4.3597447222071e-18, ("mul", "x", _DOUBLE), {"x": 4.3597447222071e-18 / dbl}),
        "flux-direct-expansion": (2.067833848e-15, ("mul", "x", _UP), {"x": 2.067833848e-15 / (1 + e)}),
        "rk-direct-expansion": (25812.80745, ("mul", "x", _UP), {"x": 25812.80745 / (1 + e)}),
        "stefan-quad-gate": (5.670374419e-8, ("mul", "x", ("pow", _UP, 4)), {"x": 5.670374419e-8 / (1 + e) ** 4}),
        "weak-mixing-torsion": (0.23122, ("div", "x", _UP), {"x": 0.23122 * (1 + e)}),
        # R = N_A * k_B from the exact SI values (N_A contracts, k_B expands).
        "molar-gas-neutral": (
            _CODATA_NA * _CODATA_KB,
            ("mul", ("div", "na", _UP), ("mul", "kb", _UP)),
            {"na": _CODATA_NA * (1 + e), "kb": _CODATA_KB / (1 + e)},
        ),
    }


def qed_gate_kwargs(formula_id: str) -> dict:
    """Return ``value``, ``arithma``, ``eml`` and ``triple_env`` for a QED gate."""
    from metaphysica.simulations.core.triple_helpers import closed_form
    table = _gate_table()
    if formula_id not in table:
        raise KeyError("qed_gate_kwargs: unknown gate %r" % formula_id)
    value, spec, env = table[formula_id]
    return {"value": float(value), **closed_form(spec, env)}
