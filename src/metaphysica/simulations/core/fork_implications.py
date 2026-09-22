"""What ONE fork deviation from the adopted state actually changes.

WHY THIS EXISTS
===============
Eighteen forks are declared and each is runnable, but "runnable" has been
cheaper than "costed": the campaign repeatedly discovered the consequences of
a fork only when something hard-failed under it. The b3_seed adoption moved
182 registered rows, broke twelve integer identities and deleted a vacuum, and
none of that was visible from the fork declaration -- it was found by running
the branch and reading the wreckage.

This module makes the wreckage a PUBLISHED TABLE. For every fork, for every
option that is not the adopted one, it evaluates the one-fork deviation from
the adopted state and reports three things:

  observables   which watched quantities move, with BOTH values
  identities    which claimed integer identities flip HOLDS <-> BROKEN
  gates         which gate verdicts change

The unit is deliberately ONE fork. A full combination sweep is
`core/switch_search`, which enumerates the product; this answers the narrower
and more useful question "what does this single choice buy or cost", which is
the question an author ruling actually faces.

THE ANTI-TUNING RULE, RESTATED
==============================
Rows are ordered by fork id then option id. Nothing here ranks options, counts
"improvements", or compares a moved observable to an experimental anchor. A
matrix that sorted deviations by how much they improved agreement would be a
parameter fitter with a JSON schema, and this repository has already retired
one advertised agreement that came from exactly that pattern. The `verdict`
field is a constant for the same reason it is a constant in switch_search.

WHAT THE ADOPTED COLUMN IS FOR
==============================
Each fork also gets a row for its ADOPTED option. Deviating to the option that
is already adopted is a no-op, so that row must be all-null. It is not padding:
it is the control. If the adopted row shows movement, the harness is measuring
noise -- a surviving module cache, a nondeterministic observable, an artifact
being rewritten mid-run -- and every other row in the matrix is then suspect.
A test asserts it.

WHAT IT CANNOT SEE, STATED SO NOBODY READS PAST IT
==================================================
Fork branches write to shared gitignored build artifacts. An observable or
gate that reads `parameters.json` reflects WHICHEVER SEED LAST BUILT, not the
deviated state, so it cannot move here however much it would move after a
rebuild. Those rows are labelled `artifact_bound` rather than reported as
"unchanged", because "did not move" and "could not move" are different facts
and conflating them is how a frozen value comes to wear a result.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional, Tuple

__all__ = [
    "one_fork_deviations",
    "implications_for",
    "build_matrix",
    "write_matrix",
]

#: Gate evaluators that read `parameters.json` rather than the live registry.
#: A build artifact does not follow an environment override, so these cannot
#: move in a one-fork deviation. Named rather than detected, so the list is
#: auditable and a gate cannot drift into it silently.
ARTIFACT_BOUND_GATES = (
    "gate_G01_integer_root_parity",
    "gate_G23_proton_stability_floor",
)


# ---------------------------------------------------------------------------
# The deviations
# ---------------------------------------------------------------------------


def one_fork_deviations() -> List[Tuple[str, str, bool]]:
    """(fork_id, option_id, is_adopted) for every option of every fork.

    Ordered by fork id then option id, so the emitted matrix is deterministic
    and its ordering carries no preference.
    """
    from metaphysica.simulations.core.preferred_path import preferred_selection
    from metaphysica.simulations.core.variants import FORKS

    adopted = preferred_selection()
    out: List[Tuple[str, str, bool]] = []
    for fork_id in sorted(FORKS):
        fork = FORKS[fork_id]
        for option in sorted(o.id for o in fork.options):
            out.append((fork_id, option, option == adopted.get(fork_id)))
    return out


# ---------------------------------------------------------------------------
# The three things measured per deviation
# ---------------------------------------------------------------------------


def _live_seed_values() -> Tuple[Optional[int], Optional[int]]:
    """(b_3, b_2) in whatever fork state is currently live."""
    try:
        from metaphysica.simulations.PM.geometry.b3_path import (
            resolve_path,
            seed_values,
        )

        return tuple(seed_values(resolve_path())[:2])   # type: ignore[return-value]
    except Exception:
        return (None, None)


def _live_chi_eff() -> Optional[float]:
    """chi_eff in the live state, or None while the route stays UNRULED.

    The chi_eff_route fork's adopted option is `unruled`, and a deviation to
    `constant_144` or `seed_dependent` is exactly the kind of consequence this
    matrix exists to show -- so the value is read from the fork rather than
    assumed.
    """
    try:
        from metaphysica.simulations.core.variants import resolve

        route = resolve("chi_eff_route")
    except Exception:
        return None
    if route == "constant_144":
        return 144.0
    if route == "seed_dependent":
        b3, _ = _live_seed_values()
        return None if b3 is None else 6.0 * b3
    return None


def _identity_statuses() -> Dict[str, str]:
    """identity id -> HOLDS / BROKEN / NOT_EVALUABLE in the live state."""
    from metaphysica.simulations.core.identity_ledger import evaluate_all

    b3, b2 = _live_seed_values()
    if b3 is None or b2 is None:
        return {}
    return {row["identity"]: row["status"]
            for row in evaluate_all(b3, b2, _live_chi_eff())}


def _gate_verdicts() -> Dict[str, str]:
    """gate evaluator name -> verdict in the live state."""
    from metaphysica.simulations.PM.validation.declarative_strategies import (
        strategy_a_semantic as sa,
    )

    out: Dict[str, str] = {}
    for name in sorted(sa.__all__):
        if not name.startswith("gate_"):
            continue
        try:
            out[name] = getattr(sa, name)().verdict
        except Exception as exc:              # a broken gate is data too
            out[name] = "ERROR: %s" % type(exc).__name__
    return out


def _observables() -> Dict[str, Any]:
    """The watched observables, evaluated in the live state."""
    from metaphysica.simulations.core.preferred_path import (
        _default_observables,
        _evaluate,
    )

    return _evaluate(_default_observables())


def _measure() -> Dict[str, Any]:
    """Everything this matrix watches, in whatever state is currently live."""
    return {
        "observables": _observables(),
        "identities": _identity_statuses(),
        "gates": _gate_verdicts(),
    }


def _run_under(selection: Dict[str, str]) -> Dict[str, Any]:
    """Measure with `selection` forced into the environment, then restore it."""
    from metaphysica.simulations.core.preferred_path import _invalidate_caches
    from metaphysica.simulations.core.variants import _ENV_PREFIX

    saved: Dict[str, Optional[str]] = {}
    try:
        for fork_id, option in selection.items():
            key = _ENV_PREFIX + fork_id.upper()
            saved[key] = os.environ.get(key)
            os.environ[key] = option
        _invalidate_caches()
        return _measure()
    finally:
        for key, old in saved.items():
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old
        _invalidate_caches()


def _diff(base: Dict[str, Any], dev: Dict[str, Any]) -> Dict[str, Any]:
    """The three change lists, each ordered by name."""
    moved = []
    for name in sorted(set(base["observables"]) | set(dev["observables"])):
        a, b = base["observables"].get(name), dev["observables"].get(name)
        if a != b:
            moved.append({"observable": name, "adopted": a, "deviated": b})

    flipped = []
    for name in sorted(set(base["identities"]) | set(dev["identities"])):
        a, b = base["identities"].get(name), dev["identities"].get(name)
        if a != b:
            flipped.append({"identity": name, "adopted": a, "deviated": b})

    regated = []
    for name in sorted(set(base["gates"]) | set(dev["gates"])):
        a, b = base["gates"].get(name), dev["gates"].get(name)
        if a != b:
            regated.append({
                "gate": name, "adopted": a, "deviated": b,
                "artifact_bound": name in ARTIFACT_BOUND_GATES,
            })

    return {
        "observables_moved": moved,
        "identities_flipped": flipped,
        "gates_changed": regated,
        "n_changes": len(moved) + len(flipped) + len(regated),
    }


def implications_for(fork_id: str, option: str,
                     base: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """One fork deviated from the adopted state; everything that changes."""
    from metaphysica.simulations.core.preferred_path import preferred_selection

    adopted = preferred_selection()
    base = base if base is not None else _run_under(adopted)
    deviated = dict(adopted)
    deviated[fork_id] = option
    return _diff(base, _run_under(deviated))


def build_matrix() -> Dict[str, Any]:
    """The full one-fork-deviation matrix, adopted state measured once."""
    from metaphysica.simulations.core.preferred_path import (
        digest_of,
        preferred_selection,
    )
    from metaphysica.simulations.core.variants import FORKS

    adopted = preferred_selection()
    base = _run_under(adopted)

    rows: List[Dict[str, Any]] = []
    for fork_id, option, is_adopted in one_fork_deviations():
        result = implications_for(fork_id, option, base=base)
        rows.append({
            "fork": fork_id,
            "option": option,
            "is_adopted_option": is_adopted,
            "fork_status": FORKS[fork_id].status,
            **result,
        })

    return {
        "generator": "fork_implications",
        "adopted_selection": adopted,
        "adopted_digest": digest_of(adopted),
        "n_forks": len(FORKS),
        "n_deviations": len(rows),
        "watched": {
            "observables": sorted(base["observables"]),
            "identities": sorted(base["identities"]),
            "gates": sorted(base["gates"]),
        },
        "artifact_bound_gates": list(ARTIFACT_BOUND_GATES),
        "rows": rows,
        "ordering": (
            "fork id, then option id; never by how much a deviation improves "
            "agreement with any anchor"
        ),
        "verdict": "NO_SELECTION_MADE",
        "note": (
            "A deviation row is a cost statement, not a recommendation. Rows "
            "whose only movement is in an artifact_bound gate are reporting "
            "the build artifact, not the deviation."
        ),
    }


def write_matrix(out_path=None) -> Dict[str, Any]:
    """Emit ``AutoGenerated/fork_implications.json`` and return the payload."""
    from metaphysica.generators._common import autogen_dir, write_json_stable

    payload = build_matrix()
    path = out_path or (autogen_dir() / "fork_implications.json")
    write_json_stable(path, payload)
    return payload


def main(argv=None) -> int:
    """CLI entry point: build the matrix and print a one-line-per-row summary."""
    payload = write_matrix()
    print("fork implications: %d forks, %d deviations"
          % (payload["n_forks"], payload["n_deviations"]))
    for row in payload["rows"]:
        mark = "  (adopted)" if row["is_adopted_option"] else ""
        print("  %-26s %-22s %2d changes  [%d obs / %d id / %d gate]%s"
              % (row["fork"], row["option"], row["n_changes"],
                 len(row["observables_moved"]), len(row["identities_flipped"]),
                 len(row["gates_changed"]), mark))
    return 0


if __name__ == "__main__":       # pragma: no cover - CLI
    raise SystemExit(main())
