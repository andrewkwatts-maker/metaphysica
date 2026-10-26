"""Frozen data model of an action: fields, coefficients, terms, action.

Theory-agnostic: nothing here imports `metaphysica.simulations`,
`metaphysica.generators` or `metaphysica.website`.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Optional, Tuple

INPUT, DERIVED, CALIBRATED, OPEN = "INPUT", "DERIVED", "CALIBRATED", "OPEN"
SOURCES = (INPUT, DERIVED, CALIBRATED, OPEN)
MOSTLY_PLUS, MOSTLY_MINUS = "mostly_plus", "mostly_minus"
CONVENTIONS = (MOSTLY_PLUS, MOSTLY_MINUS)
KINDS = ("scalar", "vector", "spinor", "metric")
CURVATURE, DERIVATIVE = "R", "d"


class ModelError(ValueError):
    """Raised when an action description is inconsistent."""


def _is_form(kind: str) -> bool:
    return kind.startswith("form:") and kind[5:].isdigit()


@dataclass(frozen=True)
class Field:
    name: str
    kind: str
    components: int
    mass_dim: Fraction

    def __post_init__(self):
        if self.kind not in KINDS and not _is_form(self.kind):
            raise ModelError("field %s: unknown kind %r" % (self.name, self.kind))
        if self.name in (CURVATURE, DERIVATIVE):
            raise ModelError("field name %r is reserved" % self.name)


@dataclass(frozen=True)
class Check:
    """One validation outcome, the shape used by `g2_closure`."""

    id: str
    measured: object
    holds: bool
    can_fail: bool
    source: str
    detail: str = ""

    def as_dict(self) -> dict:
        return {"id": self.id, "measured": str(self.measured), "holds": self.holds,
                "can_fail": self.can_fail, "source": self.source, "detail": self.detail}


@dataclass(frozen=True)
class Coefficient:
    symbol: str
    mass_dim: Fraction
    source: str
    provider: Optional[str] = None

    def __post_init__(self):
        if self.source not in SOURCES:
            raise ModelError("coefficient %s: unknown source %r" % (self.symbol, self.source))
        if self.source != OPEN and not self.provider:
            raise ModelError("coefficient %s: a provider is required unless OPEN" % self.symbol)


@dataclass(frozen=True)
class Term:
    id: str
    coefficient: Coefficient
    factors: Tuple[str, ...]
    derivatives: int = 0
    sign: int = 1
    open: bool = False


@dataclass(frozen=True)
class Action:
    id: str
    dim: int
    signature: Tuple[int, int]
    fields: Tuple[Field, ...]
    terms: Tuple[Term, ...]
    convention: str = MOSTLY_PLUS

    def __post_init__(self):
        if sum(self.signature) != self.dim:
            raise ModelError("action %s: signature %s does not sum to %d"
                             % (self.id, self.signature, self.dim))
        if self.convention not in CONVENTIONS:
            raise ModelError("action %s: unknown convention %r" % (self.id, self.convention))
        names = [f.name for f in self.fields]
        if len(set(names)) != len(names):
            raise ModelError("action %s: duplicate field names" % self.id)
        ids = [t.id for t in self.terms]
        if len(set(ids)) != len(ids):
            raise ModelError("action %s: duplicate term ids" % self.id)
        for t in self.terms:
            for f in t.factors:
                if f not in names and f not in (CURVATURE, DERIVATIVE):
                    raise ModelError("term %s: unknown field %r" % (t.id, f))

    def field(self, name: str) -> Field:
        return next(f for f in self.fields if f.name == name)

    def term_dim(self, term: Term) -> Fraction:
        """Mass dimension of a term: coefficient + fields + derivatives (R is 2)."""
        total = Fraction(term.coefficient.mass_dim) + term.derivatives
        for f in term.factors:
            if f == CURVATURE:
                total += 2
            elif f == DERIVATIVE:
                total += 1
            else:
                total += Fraction(self.field(f).mass_dim)
        return total
