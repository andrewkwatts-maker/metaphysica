"""Triple-track formula validator: Arithma + EML-Math + float.

Every formula registered in the framework carries three coherent views:

* an :class:`arithma.Expression` — symbolic AST, Rust-backed.
* an :class:`eml_math.EMLPoint` — universal real-valued primitive tree.
* a Python ``float`` — the canonical numeric value.

:func:`triple_assert` evaluates the symbolic views under a shared variable
environment and asserts both agree with the expected float within a stated
tolerance. Disagreement raises :class:`FormulaConsistencyError` which halts
the build — there is no silent fall-through.

The validator degrades gracefully when one of the symbolic backends isn't
installed (e.g. Arithma's wheel not built in a dev environment): the
missing leg is skipped and noted on the :class:`TripleResult`. At least
one symbolic view + the float is always required; a formula registered
with neither symbolic view fails the audit.

Typical usage from a simulation::

    from metaphysica.simulations.core.triple_validator import triple_assert
    from metaphysica.simulations.core.eml_integration import (
        eml_pi, eml_compute, eml_mul, eml_scalar,
    )
    import arithma as A

    expected = 6.283185307179586
    eml_tree = eml_mul(eml_scalar(2.0), eml_pi())
    arithma_expr = A.Expression.number(2.0) * A.Expression.variable("pi")

    triple_assert(arithma_expr, eml_tree, expected, name="two_pi")
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Optional


# ── Optional backends ────────────────────────────────────────────────────────

try:
    # Probed, not merely imported. Checking `Expression is not None` catches
    # one shape of stub; it does not catch a backend that exposes the names
    # and then raises, or one that cannot round-trip a literal.
    from metaphysica.simulations.core.arithma_backend import ARITHMA as _arithma
    _ARITHMA_OK = _arithma is not None
except Exception:
    _arithma = None
    _ARITHMA_OK = False

try:
    from metaphysica.simulations.core.eml_integration import (
        EML_AVAILABLE as _EML_OK,
        eml_compute as _eml_compute,
    )
except ImportError:
    _EML_OK = False
    _eml_compute = None  # type: ignore[assignment]


# ── Public API ───────────────────────────────────────────────────────────────


class FormulaConsistencyError(AssertionError):
    """Raised when a formula's Arithma / EML / float views disagree.

    The exception carries the three values plus the per-pair deltas so a
    failing build report can surface the precise disagreement.
    """

    def __init__(
        self,
        name: str,
        *,
        expected: float,
        arithma_value: Optional[float],
        eml_value: Optional[float],
        rel: float,
        abs_: float,
    ) -> None:
        self.name = name
        self.expected = expected
        self.arithma_value = arithma_value
        self.eml_value = eml_value
        self.rel = rel
        self.abs_ = abs_

        parts = [f"formula {name!r}: expected={expected!r}"]
        if arithma_value is not None:
            d = arithma_value - expected
            parts.append(f"arithma={arithma_value!r} (delta={d:+.3e})")
        if eml_value is not None:
            d = eml_value - expected
            parts.append(f"eml={eml_value!r} (delta={d:+.3e})")
        parts.append(f"tolerance rel={rel}, abs={abs_}")
        super().__init__("; ".join(parts))


@dataclass(frozen=True)
class TripleResult:
    """Outcome of one :func:`triple_assert` call."""
    name: str
    expected: float
    arithma_value: Optional[float]
    eml_value: Optional[float]
    arithma_used: bool
    eml_used: bool

    @property
    def value(self) -> float:
        return self.expected



def _default_symbol_env() -> dict:
    """Symbols the arithma track needs bound in order to evaluate at all.

    The two tracks must be given the SAME symbolic footing or the comparison
    is not like-for-like. The EML track already resolves b3 through
    ``b3_leaf()``, which reads the SSoT ``FormulasRegistry``; the arithma
    track builds ``Expression.variable("b3")`` and so needs the same value in
    its environment.

    This binds nothing new and invents nothing: b3 comes from the same single
    source of truth the EML leaf uses, and pi is math.pi. Without it every
    formula written in terms of b3 raised ``unbound variable 'b3'``, which
    ``triple_assert`` reported as ``arithma_value=None`` -- so the message
    named the formula and hid the cause.

    Previously these resolved because ``Expression.constant(name)`` consulted
    a global constants table. It no longer does: a constant now carries its
    own cached value and does not look at the environment, which is why the
    symbols became variables and the environment became necessary.
    """
    env: dict = {"pi": math.pi}
    try:
        from metaphysica.simulations.core.FormulasRegistry import get_registry

        env["b3"] = float(get_registry().elder_kads)
    except Exception:  # pragma: no cover - registry optional at import time
        pass
    return env


def triple_assert(
    arithma_expr: Any,
    eml_tree: Any,
    expected_float: float,
    *,
    env: Optional[Mapping[str, float]] = None,
    rel: float = 1e-12,
    abs_: float = 0.0,
    name: str = "<unnamed>",
) -> TripleResult:
    """Evaluate the symbolic views and assert agreement with *expected_float*.

    Parameters
    ----------
    arithma_expr
        An :class:`arithma.Expression` instance, or ``None`` to skip the
        Arithma leg.
    eml_tree
        An :class:`eml_math.EMLPoint` tree, or ``None`` to skip the EML leg.
    expected_float
        The canonical numeric value the formula should produce.
    env
        Variable bindings used when evaluating the symbolic views. Default
        empty (formula must be closed-form / fully bound).
    rel, abs_
        Tolerance bounds passed through to :func:`math.isclose`. The default
        ``rel=1e-12`` matches the precision of double-precision IEEE 754
        identities; relax for ODE-driven formulas.
    name
        Human-readable identifier used in error messages.

    Returns
    -------
    TripleResult
        Records which legs ran and the values they produced.

    Raises
    ------
    FormulaConsistencyError
        If either symbolic value disagrees with *expected_float* beyond the
        tolerance.
    ValueError
        If both symbolic views are ``None`` (a formula must offer at least
        one symbolic check; pure-float entries should not call this).
    """
    # Start from the shared symbol environment so the arithma track can
    # evaluate the same symbols the EML track resolves internally; an
    # explicit env still wins.
    env_dict = _default_symbol_env()
    env_dict.update(dict(env or {}))

    arithma_used = arithma_expr is not None and _ARITHMA_OK
    eml_used = eml_tree is not None and _EML_OK

    if not arithma_used and not eml_used:
        raise ValueError(
            f"triple_assert({name!r}): no symbolic view available — "
            "supply arithma_expr or eml_tree (and ensure the backing "
            "package is installed)."
        )

    arithma_value: Optional[float] = None
    eml_value: Optional[float] = None

    if arithma_used:
        try:
            arithma_value = float(arithma_expr.evaluate(env_dict))
        except Exception as exc:
            raise FormulaConsistencyError(
                name, expected=expected_float,
                arithma_value=None, eml_value=None,
                rel=rel, abs_=abs_,
            ) from exc

    if eml_used:
        try:
            assert _eml_compute is not None  # for type checker; gated by _EML_OK
            eml_value = float(_eml_compute(eml_tree))
        except Exception as exc:
            raise FormulaConsistencyError(
                name, expected=expected_float,
                arithma_value=arithma_value, eml_value=None,
                rel=rel, abs_=abs_,
            ) from exc

    # Compare each available view to the expected float.
    def _agrees(actual: float) -> bool:
        if math.isnan(expected_float) or math.isnan(actual):
            return math.isnan(expected_float) and math.isnan(actual)
        return math.isclose(actual, expected_float, rel_tol=rel, abs_tol=abs_)

    bad = False
    if arithma_value is not None and not _agrees(arithma_value):
        bad = True
    if eml_value is not None and not _agrees(eml_value):
        bad = True
    if bad:
        raise FormulaConsistencyError(
            name, expected=expected_float,
            arithma_value=arithma_value, eml_value=eml_value,
            rel=rel, abs_=abs_,
        )

    return TripleResult(
        name=name,
        expected=expected_float,
        arithma_value=arithma_value,
        eml_value=eml_value,
        arithma_used=arithma_used,
        eml_used=eml_used,
    )


def backends_available() -> tuple[bool, bool]:
    """Return ``(arithma_loaded, eml_loaded)`` for diagnostics."""
    return _ARITHMA_OK, _EML_OK


__all__ = [
    "FormulaConsistencyError",
    "TripleResult",
    "triple_assert",
    "backends_available",
]
