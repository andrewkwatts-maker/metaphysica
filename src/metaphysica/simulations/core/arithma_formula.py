"""Declare a formula once; get an Arithma tree, LaTeX, and a drift check.

WHY
===
Arithma is the third track. A quantity is computed in plain Python, described
in EML, and -- where it exists -- built as an Arithma expression, so three
independent statements of the same formula can be compared. When they disagree,
something has drifted.

Coverage was 51 of 121 simulation modules, because adding the third track meant
hand-writing the same scaffolding every time: the stub guard, expression
construction, an evaluation environment, and a comparison against the Python
value. Fifty-three modules had already copied that guard, and the copies were
what let a *degraded* arithma turn into a hard failure in CI.

This module is that scaffolding, once. A simulation declares:

    FORMULA = ArithmaFormula(
        name="w0_from_b3",
        latex_hint="-(b_3 - 1)/b_3",
        build=lambda E, v: E.div(E.neg(E.sub(v("b3"), E.number(1.0))), v("b3")),
        inputs={"b3": "topology.elder_kads"},
        python=lambda b3: -(b3 - 1) / b3,
    )

and gets `.latex()`, `.compact()`, `.evaluate()`, `.derivative(var)` and
`.check()` -- the last comparing the Arithma tree against the Python callable
on registry values, which is the part that catches drift rather than merely
asserting agreement.

NO MAGIC NUMBERS
================
`inputs` maps a symbol to a REGISTRY PATH. Values are fetched at evaluate time,
so a formula never carries a numeral, and `provenance()` reports where each came
from. A symbol with no registry path must be supplied explicitly by the caller,
and `check()` records that it was.

STUB SAFETY
===========
Every entry point degrades to None / "unavailable" when the backend is a stub,
using arithma_backend's probe rather than a bare ImportError guard -- a package
that imports and does not compute is treated as absent, because that is what it
is.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple

__all__ = ["ArithmaFormula", "registry_value", "available"]

_PARAMS_CACHE: Optional[Dict[str, Any]] = None


def available() -> bool:
    """True only when the backend can actually build and evaluate."""
    from metaphysica.simulations.core.arithma_backend import ARITHMA

    return ARITHMA is not None


def _expression():
    from metaphysica.simulations.core.arithma_backend import ARITHMA

    return None if ARITHMA is None else ARITHMA.Expression


_DEFAULTS_READY = False


def arithma_constant(name: str) -> Optional[float]:
    """A MATHEMATICAL constant from Arithma's own table.

    pi and e are not physics parameters and do not belong in the parameter
    registry, but they must not be literals here either. Arithma ships a
    constant table; initialize_defaults() populates it, and lookup_value reads
    it. That makes Arithma the declared source, on the same footing as the
    registry for physical quantities.
    """
    global _DEFAULTS_READY
    from metaphysica.simulations.core.arithma_backend import ARITHMA

    if ARITHMA is None:
        return None
    if not _DEFAULTS_READY:
        try:
            ARITHMA.initialize_defaults()
        except Exception:
            pass
        _DEFAULTS_READY = True
    try:
        value = ARITHMA.lookup_value(name)
    except Exception:
        return None
    return float(value) if isinstance(value, (int, float)) else None


def registry_value(path: str) -> Optional[float]:
    """A registered value, or None. The only source of numbers here."""
    global _PARAMS_CACHE
    if _PARAMS_CACHE is None:
        # Delegated to `core.parameter_artifact`, which exists to be the ONE
        # place that knows where parameters.json lives. This function carried
        # a fourth private copy of the search, and it was wrong in the two
        # ways that module's docstring already names: `parents[3]` resolves to
        # `src/`, which the build never writes to, and METAPHYSICA_OUT was not
        # consulted at all -- so it read the repo-local tree or nothing.
        # When the repo-local scratch tree was absent it returned an empty
        # dict, and every caller then saw `None` for rows that exist, which
        # reads as "the registry lost this parameter" rather than "the lookup
        # never found the file".
        from metaphysica.simulations.core.parameter_artifact import (
            load_parameters,
        )

        _PARAMS_CACHE = load_parameters()
    row = _PARAMS_CACHE.get(path)
    value = row.get("value") if isinstance(row, dict) else None
    return float(value) if isinstance(value, (int, float)) else None


def reset_cache() -> None:
    """Drop the parameter cache, so a rebuild or a fork flip is picked up."""
    global _PARAMS_CACHE
    _PARAMS_CACHE = None


@dataclass(frozen=True)
class ArithmaFormula:
    """One formula, stated once, available on all three tracks."""

    name: str
    #: How the formula reads, for humans and for the export's sanity.
    latex_hint: str
    #: (Expression, var) -> Expression. `var(symbol)` yields a variable node.
    build: Callable[[Any, Callable[[str], Any]], Any]
    #: symbol -> registry path. Values are fetched at evaluate time.
    inputs: Dict[str, str] = field(default_factory=dict)
    #: symbol -> Arithma constant name, for mathematical constants like pi.
    constants: Dict[str, str] = field(default_factory=dict)
    #: The plain-Python statement of the same formula, for the drift check.
    python: Optional[Callable[..., float]] = None
    notes: str = ""

    # ---------------------------------------------------------------- build

    def expression(self):
        """The Arithma tree, or None when the backend is unusable."""
        expression_cls = _expression()
        if expression_cls is None:
            return None
        cache: Dict[str, Any] = {}

        def var(symbol: str):
            if symbol not in cache:
                cache[symbol] = expression_cls.variable(symbol)
            return cache[symbol]

        try:
            return self.build(expression_cls, var)
        except Exception:                      # a broken spec is data, not a crash
            return None

    # --------------------------------------------------------------- export

    def latex(self) -> Optional[str]:
        tree = self.expression()
        return None if tree is None else tree.to_latex()

    def compact(self):
        tree = self.expression()
        return None if tree is None else tree.to_compact()

    def roundtrips(self) -> bool:
        """Compact -> tree -> value must reproduce the direct evaluation."""
        tree = self.expression()
        if tree is None:
            return False
        env = self.environment()
        if env is None:
            return False
        try:
            expression_cls = _expression()
            back = expression_cls.from_compact(tree.to_compact())
            return abs(back.evaluate(env) - tree.evaluate(env)) < 1e-12
        except Exception:
            return False

    # ------------------------------------------------------------ evaluate

    def environment(self, extra: Optional[Dict[str, float]] = None
                    ) -> Optional[Dict[str, float]]:
        """Symbol -> value, fetched from the registry. None if any is missing."""
        env: Dict[str, float] = {}
        for symbol, path in self.inputs.items():
            value = registry_value(path)
            if value is None:
                return None
            env[symbol] = value
        for symbol, constant_name in self.constants.items():
            value = arithma_constant(constant_name)
            if value is None:
                return None
            env[symbol] = value
        if extra:
            env.update(extra)
        return env

    def evaluate(self, extra: Optional[Dict[str, float]] = None
                 ) -> Optional[float]:
        tree = self.expression()
        env = self.environment(extra)
        if tree is None or env is None:
            return None
        try:
            return float(tree.evaluate(env))
        except Exception:
            return None

    def derivative(self, symbol: str,
                   extra: Optional[Dict[str, float]] = None
                   ) -> Optional[float]:
        """Exact symbolic derivative, evaluated. Not a finite difference."""
        tree = self.expression()
        env = self.environment(extra)
        if tree is None or env is None:
            return None
        from metaphysica.simulations.core.arithma_backend import ARITHMA

        try:
            return float(ARITHMA.differentiate(tree, symbol).evaluate(env))
        except Exception:
            return None

    # --------------------------------------------------------------- verify

    def provenance(self) -> Dict[str, str]:
        out = dict(self.inputs)
        out.update({s: "arithma constant table: %s" % n
                    for s, n in self.constants.items()})
        return out

    def check(self, extra: Optional[Dict[str, float]] = None,
              rel_tol: float = 1e-9) -> Dict[str, Any]:
        """Compare the Arithma tree against the Python statement. The point.

        A formula that agrees is a formula stated consistently on two tracks.
        A formula that disagrees has drifted, and this reports which side moved
        rather than hiding it behind a tolerance.
        """
        if not available():
            return {"name": self.name, "status": "BACKEND_UNAVAILABLE",
                    "agrees": None}
        env = self.environment(extra)
        if env is None:
            missing = [s for s, p in self.inputs.items()
                       if registry_value(p) is None]
            missing += [s for s, n in self.constants.items()
                        if arithma_constant(n) is None]
            return {"name": self.name, "status": "INPUTS_MISSING",
                    "missing": missing, "agrees": None}

        tree_value = self.evaluate(extra)
        if tree_value is None:
            return {"name": self.name, "status": "TREE_FAILED", "agrees": None}
        if self.python is None:
            return {"name": self.name, "status": "NO_PYTHON_REFERENCE",
                    "arithma": tree_value, "agrees": None}
        try:
            python_value = float(self.python(**env))
        except Exception as exc:
            return {"name": self.name, "status": "PYTHON_FAILED",
                    "error": type(exc).__name__, "agrees": None}

        denominator = max(abs(python_value), 1e-300)
        rel = abs(tree_value - python_value) / denominator
        return {
            "name": self.name,
            "status": "OK" if rel < rel_tol else "DISAGREES",
            "arithma": tree_value,
            "python": python_value,
            "rel_error": rel,
            "agrees": rel < rel_tol,
            "environment": env,
            "provenance": self.provenance(),
        }

    def export(self) -> Dict[str, Any]:
        """Everything a formula registry or a paper generator needs."""
        return {
            "name": self.name,
            "latex_hint": self.latex_hint,
            "latex": self.latex(),
            "compact": self.compact(),
            "roundtrips": self.roundtrips(),
            "value": self.evaluate(),
            "provenance": self.provenance(),
            "check": self.check(),
            "notes": self.notes,
            "backend_available": available(),
        }
