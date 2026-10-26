"""Generic LaTeX rendering of an `Action`: one summand per term, declared order.

Theory-agnostic: nothing here imports `metaphysica.simulations`,
`metaphysica.generators` or `metaphysica.website`.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from metaphysica.actions.model import Action, ModelError, Term


def measure_latex(action: Action) -> str:
    """The sqrt|g| measure with two times (det g > 0), sqrt(-g) with one."""
    times = action.signature[1]
    if times == 2:
        return r"\sqrt{|g|}"
    if times == 1:
        return r"\sqrt{-g}"
    raise ModelError("action %s: no measure for %d times" % (action.id, times))


def _escape(symbol: str) -> str:
    return symbol.replace("_", r"\_")


def summand_latex(action: Action, term: Term) -> str:
    """The term's display form; an OPEN term without one is shown by its symbol."""
    if term.latex:
        return term.latex
    if term.open:
        return r"\mathrm{%s}" % _escape(term.coefficient.symbol)
    raise ModelError("action %s: term %s has no latex and is not OPEN"
                     % (action.id, term.id))


def action_latex(action: Action) -> str:
    """S_D = int d^D x sqrt(|g|) [ ... ]: a signed summand per term, declared order."""
    if not action.terms:
        raise ModelError("action %s has no terms" % action.id)
    body = ""
    for i, term in enumerate(action.terms):
        if term.sign not in (1, -1):
            raise ModelError("term %s: sign must be +1 or -1" % term.id)
        text = summand_latex(action, term)
        if i == 0:
            body += ("- " if term.sign < 0 else "") + text
        else:
            body += (" - " if term.sign < 0 else " + ") + text
    return r"S_{%d} = \int d^{%d}x\,%s\,\left[ %s \right]" % (
        action.dim, action.dim, measure_latex(action), body)
