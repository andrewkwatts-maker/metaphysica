"""Dimensional reduction of an action over an internal space.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Dict, List, Mapping, Optional

import sympy as sp

from metaphysica.actions.model import Action, Check


@dataclass(frozen=True)
class InternalSpace:
    name: str
    dim: int
    ricci_flat: bool
    betti: Optional[Mapping[int, int]]
    volume_symbol: str


@dataclass(frozen=True)
class Reduction:
    """`coefficient_map`: child symbol -> sympy expression in parent symbols and Vol.

    `signature_change` declares an allowed change of the time count;
    `zero_mode_rule` maps betti -> {child field name: expected components}.
    """

    parent: Action
    child: Action
    internal: InternalSpace
    coefficient_map: Mapping[str, object]
    signature_change: bool = False
    zero_mode_rule: Optional[Callable[[Mapping[int, int]], Dict[str, int]]] = None


def _symbol_dims(red: Reduction) -> Dict[sp.Symbol, Fraction]:
    dims = {sp.Symbol(t.coefficient.symbol, positive=True): Fraction(t.coefficient.mass_dim)
            for t in red.parent.terms}
    dims[sp.Symbol(red.internal.volume_symbol, positive=True)] = Fraction(-red.internal.dim)
    return dims


def expression_dim(expr, dims: Mapping[sp.Symbol, Fraction]):
    """Mass dimension of expr under symbol scaling, or None if not homogeneous."""
    lam = sp.Symbol("lam", positive=True)
    scaled = expr.subs({s: s * lam ** sp.Rational(d.numerator, d.denominator)
                        for s, d in dims.items()}, simultaneous=True)
    ratio = sp.simplify(sp.powsimp(sp.expand(scaled / expr), force=True))
    if lam not in ratio.free_symbols:
        return Fraction(0)
    exponent = sp.simplify(sp.diff(sp.log(ratio), lam) * lam)
    if exponent.is_Rational:
        return Fraction(int(exponent.p), int(exponent.q))
    return None


def _map_checks(red: Reduction, src: str) -> List[Check]:
    dims = _symbol_dims(red)
    names = {s.name: s for s in dims}
    child_dims = {t.coefficient.symbol: Fraction(t.coefficient.mass_dim)
                  for t in red.child.terms}
    out = []
    for sym, expr in red.coefficient_map.items():
        got = expression_dim(sp.sympify(expr, locals=names), dims)
        want = child_dims.get(sym)
        out.append(Check("map:%s" % sym, got, got is not None and got == want, True, src,
                         "mapped dimension %s, child declares %s" % (got, want)))
    return out


def _zero_mode_checks(red: Reduction, src: str) -> List[Check]:
    if red.internal.betti is None or red.zero_mode_rule is None:
        return []
    expected = red.zero_mode_rule(red.internal.betti)
    have = {f.name: f.components for f in red.child.fields}
    return [Check("zero_modes:%s" % name, count, have.get(name) == count, True, src,
                  "expected %s components, child has %s" % (count, have.get(name)))
            for name, count in sorted(expected.items())]


def check_reduction(red: Reduction) -> List[Check]:
    src = "reduction:%s->%s" % (red.parent.id, red.child.id)
    p, c = red.parent, red.child
    out = [Check("reduction_dim:" + c.id, c.dim, c.dim == p.dim - red.internal.dim, True, src,
                 "child %d, parent %d minus internal %d" % (c.dim, p.dim, red.internal.dim))]
    same_t = c.signature[1] == p.signature[1]
    out.append(Check("reduction_time:" + c.id, c.signature[1],
                     same_t or red.signature_change, True, src,
                     "times %d -> %d" % (p.signature[1], c.signature[1])))
    return out + _map_checks(red, src) + _zero_mode_checks(red, src)
