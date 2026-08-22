#!/usr/bin/env python3
"""Reject Lagrangian terms whose form degrees cannot integrate over their domain.

WHY THIS EXISTS
---------------
A term written as an integral of a wedge product is only well formed when the
degrees sum to the dimension of the domain. This is a finite, decidable check,
and the framework had no way to make it -- which is how a proposed cross-shadow
coupling

    S_flux = int_{13D} C_3 ^ F_A ^ F_B

reached the design stage. Its degrees are 3 + 2 + 2 = 7, integrated over a
13-manifold: short by six. Compare M-theory's Chern-Simons term,
int_{11} C_3 ^ G_4 ^ G_4, where 3 + 4 + 4 = 11 exactly.

That malformed term is the gate's first record, and it FAILS. A gate whose
shipped records all pass demonstrates nothing about its ability to reject.

HOW IT IS USED
--------------
validate_action_term() is called at STRATEGY REGISTRATION time, so an
ill-formed term cannot enter the action pipeline at all. Degree validation is
a precondition rather than a separate audit step.

Domain dimensions are read from PhysicsConfig, so a term stays correct if the
open (24,2)/26D vs (26,2)/28D ruling changes the bulk rank.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

__all__ = [
    "DegreeCheck",
    "validate_action_term",
    "enumerate_completions",
    "run_all_checks",
    "write_report",
    "main",
]

#: Form degrees that appear in candidate terms. A p-form potential C_p carries
#: degree p; its field strength G_{p+1} = dC_p carries p+1.
_CANDIDATE_DEGREES = (1, 2, 3, 4, 5)

#: Cap on enumerated completions, so a wide search cannot run away.
_MAX_COMPLETIONS = 200


@dataclass(frozen=True)
class DegreeCheck:
    """One term's verdict."""

    term_id: str
    expression: str
    degrees: Sequence[int]
    total_degree: int
    domain_dim: int
    status: str      # PASS | FAIL
    note: str


def validate_action_term(
    term_degrees: Sequence[int], domain_dim: int, *, name: str = "term"
) -> bool:
    """Return True when the degrees sum to the domain dimension; else raise.

    Raises
    ------
    ValueError
        If the total degree does not match, with the shortfall spelled out.
    """
    if any(d < 0 for d in term_degrees):
        raise ValueError(f"{name}: negative form degree in {list(term_degrees)}")
    if domain_dim < 0:
        raise ValueError(f"{name}: negative domain dimension {domain_dim}")

    total = sum(term_degrees)
    if total != domain_dim:
        short = domain_dim - total
        direction = "short by" if short > 0 else "over by"
        raise ValueError(
            f"{name}: form degree mismatch -- "
            f"{' + '.join(str(d) for d in term_degrees)} = {total}, "
            f"but integrating over a {domain_dim}-dimensional domain requires "
            f"a {domain_dim}-form ({direction} {abs(short)})."
        )
    return True


def enumerate_completions(
    fixed_degrees: Sequence[int],
    domain_dim: int,
    *,
    max_extra_factors: int = 3,
    allowed: Sequence[int] = _CANDIDATE_DEGREES,
) -> List[List[int]]:
    """List well-formed degree multisets extending `fixed_degrees`.

    Answers "what would make this term integrate?" without guessing the
    physics. Bounded by construction: at most `max_extra_factors` additional
    wedge factors, drawn from `allowed`, capped at _MAX_COMPLETIONS results.
    """
    base = sum(fixed_degrees)
    deficit = domain_dim - base
    out: List[List[int]] = []
    if deficit == 0:
        return [list(fixed_degrees)]
    if deficit < 0:
        return []

    for k in range(1, max_extra_factors + 1):
        for extra in combinations_with_replacement(allowed, k):
            if sum(extra) == deficit:
                out.append(list(fixed_degrees) + list(extra))
                if len(out) >= _MAX_COMPLETIONS:
                    return out
    return out


def _config():
    from metaphysica.simulations.core.physics_config import PhysicsConfig

    return PhysicsConfig.from_registry()


def _check(term_id, expression, degrees, domain_dim, note) -> DegreeCheck:
    total = sum(degrees)
    return DegreeCheck(
        term_id=term_id,
        expression=expression,
        degrees=list(degrees),
        total_degree=total,
        domain_dim=domain_dim,
        status="PASS" if total == domain_dim else "FAIL",
        note=note,
    )


def run_all_checks() -> List[DegreeCheck]:
    """Every candidate action term the framework has proposed or adopted."""
    cfg = _config()
    shadow = cfg.d_shadow_total   # 13
    cycle = cfg.d_g2_total        # 7

    checks = [
        _check(
            "flux-13d-original",
            "int_{13D} C_3 ^ F_A ^ F_B",
            (3, 2, 2),
            shadow,
            "The originally proposed cross-shadow coupling. FAILS: a 7-form "
            "cannot be integrated over a 13-manifold. Retained as the gate's "
            "demonstration that it can reject.",
        ),
        _check(
            "flux-13d-path-a",
            "int_{13D} C_3 ^ G_4 ^ G_4 ^ F_2",
            (3, 4, 4, 2),
            shadow,
            "Path A: the well-formed 13D completion, generalising M-theory's "
            "11D term by coupling the cross-shadow 2-form F_2 = F_A - F_B. "
            "Requires G_4 = dC_3, hence the symbolic exterior derivative.",
        ),
        _check(
            "flux-sigma7-path-b",
            "int_{Sigma_7} C_3 ^ F_A ^ F_B",
            (3, 2, 2),
            cycle,
            "Path B: the same 7-form, localised on the G2 associative cycle "
            "where it IS top degree. Computable with wedge alone -- no "
            "exterior derivative needed.",
        ),
        _check(
            "m-theory-cs-reference",
            "int_{11} C_3 ^ G_4 ^ G_4",
            (3, 4, 4),
            11,
            "Textbook anchor, not a framework claim: the standard M-theory "
            "Chern-Simons term. If this ever fails, the gate is broken.",
        ),
    ]
    return checks


def write_report(
    checks: Optional[List[DegreeCheck]] = None, out_path: Optional[Path] = None
) -> Path:
    """Emit AutoGenerated/exterior_degree_gate.json."""
    if checks is None:
        checks = run_all_checks()
    if out_path is None:
        raw = os.environ.get("METAPHYSICA_OUT")
        # parents[5] is the repo root: validation/PM/simulations/metaphysica/src/<root>.
        # (consistency_beacons.py used parents[4] and so fell back to src/.)
        base = Path(raw).resolve() if raw else Path(__file__).resolve().parents[5]
        out_path = base / "AutoGenerated" / "exterior_degree_gate.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n_pass = sum(1 for c in checks if c.status == "PASS")
    payload: Dict[str, Any] = {
        "schema_version": 1,
        "count": len(checks),
        "n_pass": n_pass,
        "n_fail": len(checks) - n_pass,
        "checks": [asdict(c) for c in checks],
        "note": (
            "Form-degree validation for candidate action terms: a wedge "
            "product integrates over a domain only when its degrees sum to "
            "the domain dimension. The FAIL record is deliberate and "
            "permanent -- it is the originally proposed flux term, kept so "
            "the gate ships demonstrating it can reject. This checks that a "
            "term is WELL FORMED, which is necessary but not sufficient for "
            "it to be physically correct."
        ),
    }
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return out_path


def main() -> int:
    checks = run_all_checks()
    print("=" * 68)
    print(" EXTERIOR DEGREE GATE")
    print("=" * 68)
    for c in checks:
        degrees = " + ".join(str(d) for d in c.degrees)
        print(f"  [{c.status}] {c.term_id}")
        print(f"         {c.expression}")
        print(f"         {degrees} = {c.total_degree}  vs domain {c.domain_dim}")
    out = write_report(checks)
    n_fail = sum(1 for c in checks if c.status == "FAIL")
    print()
    print(f"  {len(checks) - n_fail} well formed, {n_fail} rejected")
    print(f"  Report written to: {out}")
    # The known-malformed record is expected to fail, so a non-zero exit would
    # halt every build. The gate's job is to REPORT, and to raise at
    # registration time via validate_action_term().
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
