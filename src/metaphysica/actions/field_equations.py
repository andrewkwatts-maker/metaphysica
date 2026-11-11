"""Field equations of a free action, per field as LaTeX, and checks that a vacuum solves them.

Generic and theory-agnostic. Covered terms: the Einstein-Hilbert term c R, and one kinetic
term per matter field (two copies of the field plus derivatives). Varying
Int sqrt|G| [c R + L_m] gives 2c (R_MN - (1/2) G_MN R) = T_MN; a scalar gives Box phi = 0, a
p-form potential d*F = 0 with F = dA, a spinor Gamma^M D_M Psi = 0 (the hermitian and the
holomorphic kinetic forms give the same equation, C being invertible). Any other term (mass,
potential, interaction) raises: these equations are not derived for it. A Weyl kinetic term
that vanishes identically in the action's signature (`spinor_bilinears`) also raises.

The vacuum Psi = 0 (every matter field zero) has T_MN = 0 from the kinetic terms, so it solves
the equations iff the metric is Ricci-flat and no potential term (scalar factors only, no
derivative) spoils it. A closed potential term spoils it iff it has 0 or 1 scalar factors: a
constant gives T_MN proportional to G_MN, not zero, so the Ricci-flat metric fails the Einstein
equation (phi = 0 still solves Box phi = 0); a linear term gives V'(0) != 0, so phi = 0 fails
the scalar equation; a term with 2 or more factors (m^2 phi^2, phi^4) vanishes at phi = 0 with
its first derivative. An open term (`Term.open`) has no fixed form, whatever factors it lists:
it is reported as not evaluable, apart from the closed terms, and the check does not hold.
`vacuum_checks` checks a product vacuum factor by factor: an explicit metric through
`curvature.ricci_tensor`, otherwise a named certificate (a `Check` computed elsewhere, e.g. G2
holonomy implies Ricci-flat).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import sympy as sp

from metaphysica.actions.curvature import ricci_tensor
from metaphysica.actions.model import (CURVATURE, DERIVATIVE, HERMITIAN, Action, Check,
                                       ModelError, Term)
from metaphysica.actions.spinor_bilinears import NONZERO, weyl_bilinears

REF = "variation of Int sqrt|G| [c R + L_kin]; Wald, General Relativity (1984), App. E"


def _symbol(name: str) -> str:
    return sp.latex(sp.Symbol(name))


def _kinetic_field(term: Term) -> Optional[str]:
    """The field of a kinetic bilinear (two copies of one field, a derivative), else None."""
    fields = [f for f in term.factors if f not in (CURVATURE, DERIVATIVE)]
    deriv = term.derivatives > 0 or DERIVATIVE in term.factors
    if CURVATURE in term.factors or not deriv or len(fields) != 2 or len(set(fields)) != 1:
        return None
    return fields[0]


def _classify(action: Action) -> Tuple[List[Term], Dict[str, Term]]:
    gravity, kinetic = [], {}
    for t in action.terms:
        f = _kinetic_field(t)
        if t.factors == (CURVATURE,):
            gravity.append(t)
        elif f is not None and f not in kinetic:
            kinetic[f] = t
        else:
            raise ValueError("field_equations: term %s of %s is not a gravity or a single "
                             "kinetic term; its equation is not derived here" % (t.id, action.id))
    if len(gravity) > 1:
        raise ValueError("field_equations: %s has %d R terms" % (action.id, len(gravity)))
    return gravity, kinetic


def _matter_equation(action: Action, name: str, term: Term) -> str:
    f = action.field(name)
    sym = _symbol(name)
    if f.kind == "spinor":
        if f.chirality == "weyl":
            s, t = action.signature
            form = term.bilinear or HERMITIAN
            part = weyl_bilinears(s, t)[form]["kinetic"]
            if part != NONZERO:
                raise ValueError("term %s: the %s Weyl kinetic term is %s in signature (%d, %d); "
                                 "it gives no field equation" % (term.id, form, part, s, t))
        return r"\Gamma^{M} D_{M} %s = 0" % sym
    if f.kind == "scalar":
        return r"\Box %s = 0" % sym
    if f.kind == "vector":
        return r"\nabla_{M} F^{MN} = 0,\quad F = d%s" % sym
    if f.kind.startswith("form:"):
        return r"d{\star}F_{(%d)} = 0,\quad F = d%s" % (int(f.kind[5:]) + 1, sym)
    raise ValueError("field %s of kind %s has a kinetic term but no rule" % (name, f.kind))


def field_equations(action: Action) -> Dict[str, str]:
    """{field name: LaTeX equation} for a free action; raises for a term it does not cover."""
    gravity, kinetic = _classify(action)
    out: Dict[str, str] = {}
    for f in action.fields:
        if f.kind == "metric":
            if not gravity:
                raise ValueError("metric %s of %s has no R term" % (f.name, action.id))
            g = gravity[0]
            src = r"T_{MN}[%s]" % ", ".join(_symbol(n) for n in kinetic) if kinetic else "0"
            sign = "-" if g.sign < 0 else ""
            out[f.name] = (r"%s2\,\mathrm{%s}\left(R_{MN} - \tfrac{1}{2} G_{MN} R\right) = %s"
                           % (sign, g.coefficient.symbol.replace("_", r"\_"), src))
        elif f.name in kinetic:
            out[f.name] = _matter_equation(action, f.name, kinetic[f.name])
        else:
            raise ValueError("field %s of %s has no kinetic term" % (f.name, action.id))
    return out


@dataclass(frozen=True)
class Factor:
    """One factor of a product vacuum: an explicit metric, or a named Ricci-flat certificate."""

    name: str
    dim: int
    metric: Optional[sp.Matrix] = None
    coords: Tuple = ()
    certificate: Optional[Check] = None

    def __post_init__(self):
        if (self.metric is None) == (self.certificate is None):
            raise ModelError("factor %s: give exactly one of metric and certificate" % self.name)
        if self.metric is not None and (self.metric.shape != (self.dim, self.dim)
                                        or len(self.coords) != self.dim):
            raise ModelError("factor %s: metric or coordinates do not match dim %d"
                             % (self.name, self.dim))


def _ricci_flat(action: Action, fac: Factor) -> Check:
    cid = "vacuum_ricci_flat:%s:%s" % (action.id, fac.name)
    if fac.certificate is not None:
        c = fac.certificate
        return Check(cid, c.measured, c.holds, True, c.source, "certificate %s" % c.id)
    ric = ricci_tensor(fac.metric, list(fac.coords), simp=sp.simplify)
    inv = fac.metric.inv()
    scalar = sp.simplify(sum(inv[a, b] * ric[a, b] for a in range(fac.dim)
                             for b in range(fac.dim)))
    flat = all(sp.simplify(e) == 0 for e in ric)
    return Check(cid, str(scalar), flat, True, REF, "R_MN of the explicit metric; R = %s" % scalar)


POTENTIAL_RULES = (
    ("constant", "T_MN proportional to G_MN, not zero: the Ricci-flat metric fails the Einstein "
                 "equation"),
    ("linear", "V'(0) != 0: phi = 0 fails the scalar equation"),
    ("open", "no fixed form: not evaluable"),
)


def _spoils_vacuum(term: Term, action: Action) -> bool:
    """A closed potential term with 0 or 1 scalar factors: constant or linear in phi.

    An open term is never read as a potential: its listed factors are not its form.
    """
    if term.open or CURVATURE in term.factors or DERIVATIVE in term.factors or term.derivatives:
        return False
    scalar_only = all(action.field(f).kind == "scalar" for f in term.factors)
    return scalar_only and len(term.factors) <= 1


def _potential_check(action: Action) -> Check:
    """Holds iff no closed constant or linear potential term and no open term is present.

    `measured` names the closed terms, then the open ones under "not evaluable (open)".
    """
    spoil = [t for t in action.terms if _spoils_vacuum(t, action)]
    found = {"constant": [t.id for t in spoil if not t.factors],
             "linear": [t.id for t in spoil if t.factors],
             "open": [t.id for t in action.terms if t.open]}
    parts = [",".join(t.id for t in spoil)] if spoil else []
    if found["open"]:
        parts.append("not evaluable (open): " + ",".join(found["open"]))
    detail = "; ".join("%s term (%s): %s" % (kind, why, ",".join(found[kind]) or "none")
                       for kind, why in POTENTIAL_RULES)
    return Check("vacuum_potential:%s" % action.id, "; ".join(parts) or "none", not parts, True,
                 REF, detail + "; none may be present")


def vacuum_checks(action: Action, factors: Sequence[Factor],
                  background: Optional[Mapping[str, object]] = None) -> List[Check]:
    """Every factor Ricci-flat, every matter field zero, no constant, linear or open term.

    Each check can fail. A closed potential term of degree 2 or more (m^2 phi^2) passes: it
    vanishes with its first derivative at phi = 0. An open term never passes: it is not
    evaluable.
    """
    if sum(f.dim for f in factors) != action.dim:
        raise ModelError("vacuum of %s: factor dimensions sum to %d, not %d"
                         % (action.id, sum(f.dim for f in factors), action.dim))
    bg = dict(background or {})
    unknown = set(bg) - {f.name for f in action.fields}
    if unknown:
        raise ModelError("vacuum of %s: background for unknown fields %s" % (action.id, unknown))
    out = [_ricci_flat(action, fac) for fac in factors]
    for f in action.fields:
        if f.kind == "metric":
            continue
        v = bg.get(f.name, 0)
        out.append(Check("vacuum_matter:%s:%s" % (action.id, f.name), str(v), v == 0, True, REF,
                         "T_MN = 0 needs %s = 0 on this vacuum" % f.name))
    out.append(_potential_check(action))
    return out
