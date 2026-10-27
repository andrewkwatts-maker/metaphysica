"""Established physics computed from an Action: generic check, roles and verdicts.

An `EstablishedCheck` names the roles it needs (a gravity R term, a spinor kinetic term, a
vector field strength, ...). `run(action, checks)` gives BLOCKED when a needed term is
missing or OPEN (naming the term and its audit reference), otherwise REPRODUCED or FAILS
with the computed residual. Nothing here imports `simulations`, `generators` or `website`.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from metaphysica.actions.model import CURVATURE, DERIVATIVE, Action, Term

REPRODUCED, FAILS, BLOCKED = "REPRODUCED", "FAILS", "BLOCKED"
NO_REF = "no audit reference supplied"


@dataclass(frozen=True)
class EstablishedCheck:
    """`compute(action)` returns (measured, holds, detail), as a Correspondence does."""

    id: str
    area: str
    ref: str
    needs: Tuple[str, ...]
    compute: Callable[[Action], Tuple[object, bool, str]]
    max_dim: Optional[int] = None  # skipped (not run) above this D: symbolic cost


@dataclass(frozen=True)
class Verdict:
    id: str
    area: str
    ref: str
    verdict: str
    measured: str
    detail: str
    blocked_on: Tuple[Tuple[str, str], ...] = ()  # (term key "<action>:<term>", audit ref)

    def as_dict(self) -> dict:
        return {"id": self.id, "area": self.area, "ref": self.ref, "verdict": self.verdict,
                "measured": self.measured, "detail": self.detail,
                "blocked_on": [list(b) for b in self.blocked_on]}


def _fields_of(action: Action, term: Term, kinds: Sequence[str]) -> List[str]:
    return [f for f in term.factors
            if f not in (CURVATURE, DERIVATIVE) and action.field(f).kind in kinds]


def _is_gravity(a: Action, t: Term) -> bool:
    return t.factors == (CURVATURE,)


def _is_spinor_kinetic(a: Action, t: Term) -> bool:
    return len(_fields_of(a, t, ("spinor",))) >= 2 and DERIVATIVE in t.factors


def _is_vector_kinetic(a: Action, t: Term) -> bool:
    return bool(_fields_of(a, t, ("vector", "form:1"))) and t.factors.count(DERIVATIVE) >= 2


def _is_gauge_sm(a: Action, t: Term) -> bool:
    return t.id.startswith("ym") or t.id == "L_SM"


def _is_potential(a: Action, t: Term) -> bool:
    return (len(_fields_of(a, t, ("scalar",))) >= 2 and DERIVATIVE not in t.factors
            and CURVATURE not in t.factors)


# role -> (predicate on a closed term, term ids that would supply it if they were not open)
ROLES: Dict[str, Tuple[Callable[[Action, Term], bool], Tuple[str, ...]]] = {
    "gravity": (_is_gravity, ("R",)),
    "spinor_kinetic": (_is_spinor_kinetic, ("psi_kin",)),
    "vector_kinetic": (_is_vector_kinetic, ("ym", "L_SM")),
    "gauge_sm": (_is_gauge_sm, ("ym", "L_SM")),
    "scalar_potential": (_is_potential, ("V", "L_SM")),
}


def _blockers(action: Action, role: str, refs: Mapping[str, str],
              role_open: Optional[Mapping[str, str]] = None) -> List[Tuple[str, str]]:
    """Empty when the role is supplied by a closed term; else the terms that block it."""
    pred, candidates = ROLES[role]
    if any(not t.open and pred(action, t) for t in action.terms):
        return []
    named = [("%s:%s" % (action.id, t.id), refs.get("%s:%s" % (action.id, t.id), NO_REF))
             for t in action.terms if t.id in candidates and t.open]
    if not named and role_open and role in role_open:  # supplied later on the ladder
        key = role_open[role]
        named = [(key, "%s; absent from %s" % (refs.get(key, NO_REF), action.id))]
    return named or [("%s:<no %s term>" % (action.id, role), "role %s absent" % role)]


def _verdict(check: EstablishedCheck, action: Action, refs: Mapping[str, str],
             role_open: Optional[Mapping[str, str]] = None) -> Verdict:
    blocked: List[Tuple[str, str]] = []
    for role in check.needs:
        blocked += [b for b in _blockers(action, role, refs, role_open) if b not in blocked]
    if blocked:
        detail = "needs " + ", ".join(check.needs) + "; blocked by " + "; ".join(
            "%s (%s)" % b for b in blocked)
        return Verdict(check.id, check.area, check.ref, BLOCKED, "-", detail, tuple(blocked))
    measured, holds, detail = check.compute(action)
    return Verdict(check.id, check.area, check.ref, REPRODUCED if holds else FAILS,
                   str(measured), detail)


def run(action: Action, checks: Sequence[EstablishedCheck],
        open_refs: Optional[Mapping[str, str]] = None,
        role_open: Optional[Mapping[str, str]] = None) -> List[Verdict]:
    """One verdict per check; `open_refs` maps "<action>:<term>" to its audit reference and
    `role_open` maps a role to the OPEN term that supplies it further down the ladder."""
    refs = open_refs or {}
    return [_verdict(c, action, refs, role_open) for c in checks
            if c.max_dim is None or action.dim <= c.max_dim]
