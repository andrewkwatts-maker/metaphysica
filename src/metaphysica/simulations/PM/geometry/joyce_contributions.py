"""The Joyce contribution table gate: absent by default, decisive when supplied.

WHAT IS MISSING AND WHY IT CANNOT BE INVENTED
=============================================
half_shift_enumeration computes, unconditionally, the singular locus of every
admissible (Z/2)^3 assignment on T^7: how many T^3 families, and each family's
stabiliser type. What it cannot do is turn those families into (b_2, b_3),
because that needs the per-type, per-resolution contribution table for
T^3 x C^2/{+-1} singularities and their quotients.

That table is a citation -- Joyce, *Compact Manifolds with Special Holonomy*,
ch. 12 -- and the standing rule forbids inventing physical inputs. A fabricated
table would produce Betti numbers that look like results, which is worse than
having none.

So this module is a GATE, controlled by the `joyce_contribution_table` fork:

  absent (adopted)   no table. Nothing Betti-valued is published. The
                     unconditional bound still applies.
  supplied           a table is present, each entry carrying its own citation.
                     The survey becomes a finite decision procedure.

HOW TO SUPPLY ONE
=================
Write a JSON file and point METAPHYSICA_JOYCE_TABLE at it, or place it at
data/joyce_contributions.json. Shape:

    {
      "source": "Joyce, Compact Manifolds with Special Holonomy, ch. 12",
      "entries": {
        "T3":            {"b2": <int>, "b3": <int>, "citation": "<page/thm>"},
        "T3_reflected":  [{"b2": <int>, "b3": <int>, "citation": "..."},
                          {"b2": <int>, "b3": <int>, "citation": "..."}]
      }
    }

A list means that family type admits SEVERAL topologically distinct
resolutions -- which is how one orbifold yields several (b_2, b_3) pairs in
Joyce's tables, and precisely the freedom whose neglect sank the withdrawn
parity theorem. Every entry must carry a non-empty `citation`; entries without
one are rejected rather than used.

WHAT BECOMES DECIDABLE
======================
With a validated table, reachable_betti() enumerates, over all admissible
assignments and all resolution choices per family, the set of (b_2, b_3) pairs
the construction can produce. Then:

  * whether b_3 = 24 is reachable at all -- settling the b3_origin fork's
    joyce branch;
  * whether (4, 24) and (7, 24) specifically occur -- settling two questions
    the register has carried open for months;

and all of it as a finite check rather than an argument.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

__all__ = [
    "table_is_supplied",
    "load_table",
    "validate_table",
    "reachable_betti",
    "gate_report",
]

#: The flat (untwisted) contribution, derived in joyce_orbifold R3.
FLAT_B3 = 7


def _fork_choice() -> str:
    try:
        from metaphysica.simulations.core.variants import resolve

        return resolve("joyce_contribution_table")
    except Exception:                          # pragma: no cover
        return "absent"


def _candidate_paths() -> List[Path]:
    paths = []
    env = os.environ.get("METAPHYSICA_JOYCE_TABLE")
    if env:
        paths.append(Path(env))
    paths.append(Path(__file__).resolve().parents[3] / "data"
                 / "joyce_contributions.json")
    return paths


def load_table() -> Optional[Dict[str, Any]]:
    """The supplied table, or None. Never fabricates one."""
    for path in _candidate_paths():
        try:
            if path.is_file():
                return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
    return None


def validate_table(table: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Reject a table that lacks citations, rather than trusting it.

    An entry without a non-empty citation is exactly the failure mode this
    gate exists to prevent, so validation is refusal, not repair.
    """
    if table is None:
        return {"valid": False, "reason": "no table supplied"}
    if not isinstance(table, dict) or "entries" not in table:
        return {"valid": False, "reason": "malformed: no 'entries' key"}
    if not str(table.get("source", "")).strip():
        return {"valid": False, "reason": "no top-level 'source' citation"}

    problems: List[str] = []
    for family_type, spec in table["entries"].items():
        options = spec if isinstance(spec, list) else [spec]
        if not options:
            problems.append("%s: no resolution options" % family_type)
        for opt in options:
            if not isinstance(opt, dict):
                problems.append("%s: option is not an object" % family_type)
                continue
            if not isinstance(opt.get("b2"), int) or not isinstance(opt.get("b3"), int):
                problems.append("%s: b2/b3 must be integers" % family_type)
            if not str(opt.get("citation", "")).strip():
                problems.append("%s: an option carries no citation" % family_type)
    return {
        "valid": not problems,
        "reason": "; ".join(problems) if problems else "validated",
        "source": table.get("source"),
        "family_types": sorted(table["entries"]),
    }


def table_is_supplied() -> bool:
    """True only when the fork says supplied AND a valid table is present."""
    if _fork_choice() != "supplied":
        return False
    return validate_table(load_table())["valid"]


def _profile_counts(profile: Iterable[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for t in profile:
        counts[t] = counts.get(t, 0) + 1
    return counts


def reachable_betti(max_profiles: Optional[int] = None) -> Dict[str, Any]:
    """The (b_2, b_3) pairs the construction can produce. Gated.

    Enumerates every admissible assignment's family-type profile from the
    corrected survey, then every combination of per-family resolution choices
    the table allows, summing contributions and adding the derived flat 7 to
    b_3.
    """
    if not table_is_supplied():
        return {
            "decided": False,
            "reason": ("the joyce_contribution_table fork is 'absent' or no "
                       "validated table is present; no Betti pair is "
                       "published"),
            "unconditional_bound": (
                "dim H^1(T^3) = 3 bounds any single A1 family's b_3 "
                "contribution, so twisted = 17 needs at least 6 families"
            ),
            "flat_b3": FLAT_B3,
        }

    table = load_table()
    entries = table["entries"]

    from metaphysica.simulations.PM.geometry.half_shift_enumeration import survey

    surveyed = survey(include_relative=True)
    profiles = list(surveyed["admissible_type_profiles"])
    if max_profiles is not None:
        profiles = profiles[:max_profiles]

    pairs: Dict[Tuple[int, int], int] = {}
    unknown_types: set = set()
    for profile_key in profiles:
        try:
            profile = eval(profile_key) if profile_key.startswith("(") else ()
        except Exception:                       # pragma: no cover
            continue
        counts = _profile_counts(profile)
        if any(t not in entries for t in counts):
            unknown_types.update(t for t in counts if t not in entries)
            continue
        per_type_options = []
        for family_type, n in counts.items():
            spec = entries[family_type]
            options = spec if isinstance(spec, list) else [spec]
            # each of the n families independently picks a resolution
            per_type_options.append([
                combo for combo in itertools.combinations_with_replacement(
                    range(len(options)), n)
            ])
        for selection in itertools.product(*per_type_options):
            b2 = 0
            b3 = FLAT_B3
            for (family_type, n), combo in zip(counts.items(), selection):
                spec = entries[family_type]
                options = spec if isinstance(spec, list) else [spec]
                for idx in combo:
                    b2 += options[idx]["b2"]
                    b3 += options[idx]["b3"]
            pairs[(b2, b3)] = pairs.get((b2, b3), 0) + 1

    b3_values = sorted({b3 for _b2, b3 in pairs})
    return {
        "decided": True,
        "source": table.get("source"),
        "n_pairs": len(pairs),
        "pairs": {str(k): v for k, v in sorted(pairs.items())},
        "b3_values": b3_values,
        "b3_24_reachable": any(b3 == 24 for _b2, b3 in pairs),
        "pair_4_24_reachable": (4, 24) in pairs,
        "pair_7_24_reachable": (7, 24) in pairs,
        "unknown_family_types": sorted(unknown_types),
        "flat_b3": FLAT_B3,
    }


def gate_report() -> Dict[str, Any]:
    """The gate's state, and what it would settle."""
    table = load_table()
    validation = validate_table(table)
    return {
        "fork_choice": _fork_choice(),
        "table_found": table is not None,
        "validation": validation,
        "active": table_is_supplied(),
        "searched": [str(p) for p in _candidate_paths()],
        "would_settle": [
            "whether b_3 = 24 is reachable by any admissible (Z/2)^3 "
            "assignment, settling the b3_origin joyce branch",
            "whether (4, 24) occurs -- the g2_construction question",
            "whether (7, 24) occurs -- the b_2 = 7 alternative",
        ],
        "refuses_to": (
            "invent contributions. An entry without a citation is rejected, "
            "because a fabricated table produces numbers that look like "
            "results."
        ),
    }
