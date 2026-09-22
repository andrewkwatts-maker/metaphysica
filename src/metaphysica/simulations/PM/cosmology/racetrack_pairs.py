"""Every racetrack exponent pair from the derived integer menu, COSTED.

WHY THIS EXISTS
===============
The b3_seed adoption deleted the racetrack vacuum. The mechanism IS the
exponent ordering a > b, with a = 2pi/b_3 and b = 2pi/D_bulk; on the adopted
seed a = 2pi/43 < b = 2pi/26, and the solver finds zero stationary points and
zero SUSY roots over its declared window. That leaves `re_t_adoption` OPEN and
REFRAMED: the racetrack supplies nothing, so Re(T) is unbound-by-racetrack.

One of the directions the register opened is this one: if the ordering is what
was lost, WHICH pairs of derived integers restore it, and what do they give?
This module answers that by running the existing solver over every ordered
pair from the derived menu and publishing the whole table.

WHAT THIS IS NOT, AND THE RULE IT OBEYS
=======================================
It is not a search for the pair that reproduces a favoured Re(T). Rows are
ordered BY PAIR, never by agreement with any anchor, and the verdict field is
a constant. **Nothing is adopted.**

The reason to state that so firmly is that this is exactly the shape of
computation that becomes a fitter if left unattended: 28 pairs, each yielding
a Re(T), against a quantity with six incumbent values in the codebase. Finding
a pair whose minimum lands near an incumbent would be unsurprising and would
mean nothing, which is why the TRIALS FACTOR is published as a first-class
field rather than a footnote. A match at 1-in-28 is not evidence.

THE MENU, AND WHY EACH INTEGER IS ON IT
=======================================
Only integers the framework DERIVES somewhere, so the enumeration cannot be
widened after the fact to capture a result:

    3   generations, n_gen = b_2/4 = rank(Gamma)   (RULED n_gen_source)
    4   faces of K_4, the moved coordinates of an involution
    7   the flat b_3 contribution of the Joyce orbifold (R3)
    12  b_2 on the adopted profile; also the K_4 directed-edge count
    24  the BULK's spacelike core dimensions at signature (24,2)
    26  D_bulk
    36  3 x 12, the hidden-sector rank the register names as a candidate
    43  b_3 on the adopted profile

Widening this menu is a decision, not a tweak: each addition multiplies the
trials factor, and the factor is what makes a hit interpretable.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import itertools
import math
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "DERIVED_INTEGER_MENU",
    "ordered_pairs",
    "solve_pair",
    "enumerate_pairs",
    "write_report",
]

#: (integer, what it counts). The second element is mandatory: an integer on
#: this menu without a stated referent is exactly the unearned coincidence the
#: identity ledger exists to catch.
DERIVED_INTEGER_MENU: Tuple[Tuple[int, str], ...] = (
    (3, "generations; n_gen = b_2/4 = rank(Gamma), the RULED n_gen_source"),
    (4, "faces of K_4, derived as the moved coordinates of an involution"),
    (7, "flat b_3 contribution of the Joyce orbifold (R3)"),
    (12, "b_2 on the adopted profile; also the K_4 directed-edge count"),
    (24, "the BULK's spacelike core dimensions at signature (24,2)"),
    (26, "D_bulk, the bulk dimension at signature (24,2) = 24 + 2"),
    (36, "3 x 12; a hidden-sector rank the register names as a candidate"),
    (43, "b_3 on the adopted profile"),
)

#: Kahler slopes the solver already runs: n = 3 (CY form), n = 7 (G2 7/3).
KAHLER_SLOPES: Tuple[int, ...] = (3, 7)

#: Prefactors. Held FIXED at the declaring module's values across every pair,
#: because the point is to vary the exponents alone. B/A is the one continuous
#: knob in this potential and letting it float per pair would turn a costed
#: enumeration into a two-parameter fit.
PREFACTOR_A: float = 1.0
PREFACTOR_B: float = -0.5

#: Solver window and sampling, DECLARED rather than tuned per row. The same
#: numbers are used for every pair so no row gets a finer search than another;
#: `samples` is below `stationary_points`' own default because this runs it
#: 56 times, and the reduction is stated here rather than hidden in a call.
WINDOW_LO: float = 0.5
WINDOW_HI: float = 300.0
SAMPLES: int = 60000


def ordered_pairs() -> List[Tuple[int, int]]:
    """(N1, N2) with N1 < N2, so a = 2pi/N1 > b = 2pi/N2 by construction.

    N1 < N2 IS the restored ordering: the racetrack needs the first exponent
    larger, and 2pi/N is decreasing in N. Ordered by (N1, N2) so the emitted
    table is deterministic and its ordering carries no preference.
    """
    menu = sorted(n for n, _why in DERIVED_INTEGER_MENU)
    return [(a, b) for a, b in itertools.combinations(menu, 2)]


def _referent(n: int) -> str:
    for value, why in DERIVED_INTEGER_MENU:
        if value == n:
            return why
    return "not on the derived menu"


def solve_pair(n1: int, n2: int, slope: int) -> Dict[str, Any]:
    """Run the EXISTING solver on one (N1, N2) pair at one Kahler slope.

    Deliberately calls `racetrack_vacuum`'s own `stationary_points` and
    `susy_condition_roots` with substituted coefficients rather than
    re-deriving the potential here. A second implementation would make every
    row a claim about this module instead of about the declared equations.
    """
    from metaphysica.simulations.PM.cosmology.racetrack_vacuum import (
        stationary_points,
        susy_condition_roots,
    )

    a = 2.0 * math.pi / n1
    b = 2.0 * math.pi / n2
    coeffs = (PREFACTOR_A, PREFACTOR_B, a, b)

    points = stationary_points(slope, coeffs=coeffs,
                               lo=WINDOW_LO, hi=WINDOW_HI, samples=SAMPLES)
    roots = susy_condition_roots(slope, coeffs=coeffs,
                                 lo=max(1.0, WINDOW_LO), hi=WINDOW_HI)

    minima = [p for p in points if p["kind"] == "minimum"]
    saddles = [p for p in points if p["kind"] == "saddle"]

    return {
        "kahler_slope": slope,
        "a": a,
        "b": b,
        "ordering_restored": a > b,
        "n_stationary_points": len(points),
        "n_minima": len(minima),
        "n_saddles": len(saddles),
        "n_susy_roots": len(roots),
        "re_t_minimum": minima[0]["re_t"] if minima else None,
        "V_at_minimum": minima[0]["V"] if minima else None,
        "vacuum_energy_sign": (minima[0]["vacuum_energy_sign"]
                               if minima else None),
        "re_t_saddle": saddles[0]["re_t"] if saddles else None,
        "susy_roots": [round(r, 6) for r in roots[:4]],
        "structure": _structure(minima, saddles, roots),
    }


def _structure(minima: List[Dict[str, Any]], saddles: List[Dict[str, Any]],
               roots: List[float]) -> str:
    """A one-line reading of what the solve found. Descriptive, never ranked."""
    if not minima and not saddles:
        return "NO STATIONARY POINT -- bare runaway over the declared window"
    if not minima:
        return "SADDLE(S) ONLY -- no minimum over the declared window"
    sign = minima[0]["vacuum_energy_sign"]
    has_barrier = bool(saddles and saddles[0]["re_t"] > minima[0]["re_t"])
    susy = "SUSY" if roots else "non-SUSY"
    return "%s %s minimum%s" % (
        susy, sign, " with a barrier above it" if has_barrier else
        " with no barrier above it in the window")


def enumerate_pairs(slopes: Optional[Tuple[int, ...]] = None) -> Dict[str, Any]:
    """Every pair, every slope. A COSTED enumeration: the trials factor leads."""
    slopes = slopes or KAHLER_SLOPES
    pairs = ordered_pairs()

    rows: List[Dict[str, Any]] = []
    for n1, n2 in pairs:
        per_slope = {}
        for slope in slopes:
            try:
                per_slope["n_%d" % slope] = solve_pair(n1, n2, slope)
            except Exception as exc:          # a failed solve is data too
                per_slope["n_%d" % slope] = {
                    "error": "%s: %s" % (type(exc).__name__, exc)}
        rows.append({
            "pair": "%d_%d" % (n1, n2),
            "N1": n1,
            "N2": n2,
            "N1_counts": _referent(n1),
            "N2_counts": _referent(n2),
            "is_the_adopted_pair": (n1, n2) == (26, 43) or (n1, n2) == (43, 26),
            "by_slope": per_slope,
        })

    n_trials = len(pairs) * len(slopes)
    return {
        "generator": "racetrack_pairs",
        "menu": [{"n": n, "counts": why} for n, why in DERIVED_INTEGER_MENU],
        "n_pairs": len(pairs),
        "kahler_slopes": list(slopes),
        "trials_factor": n_trials,
        "trials_note": (
            "%d solves were run. Any agreement between a row's Re(T) and an "
            "incumbent value must be read against that factor: at 1-in-%d a "
            "near-hit is expected and means nothing. The factor is published "
            "as a field, not a footnote, because an enumeration whose cost is "
            "not stated is a fit wearing a table."
            % (n_trials, n_trials)
        ),
        "held_fixed": {
            "A": PREFACTOR_A, "B": PREFACTOR_B,
            "why": (
                "B/A is the one continuous knob in this potential. Letting it "
                "float per pair would make this a two-parameter fit rather "
                "than an enumeration of exponent choices."
            ),
        },
        "window": {"lo": WINDOW_LO, "hi": WINDOW_HI, "samples": SAMPLES},
        "rows": rows,
        "ordering": "pair name (N1, N2); never by agreement with any anchor",
        "verdict": "NO_SELECTION_MADE",
        "adopted": None,
        "note": (
            "Feeds the OPEN re_t_adoption ruling an option table. The adopted "
            "path's own exponents (b_3 = 43 against D_bulk = 26) give a > b "
            "FALSE and are not in this list, which enumerates ordered pairs "
            "N1 < N2 -- i.e. every way the lost ordering COULD be restored, "
            "not a claim that any of them should be."
        ),
    }


def write_report(out_path=None) -> Dict[str, Any]:
    """Emit ``AutoGenerated/racetrack_pairs.json`` and return the payload."""
    from metaphysica.generators._common import autogen_dir, write_json_stable

    payload = enumerate_pairs()
    path = out_path or (autogen_dir() / "racetrack_pairs.json")
    write_json_stable(path, payload)
    return payload


def main(argv=None) -> int:
    """CLI: run the enumeration, WRITE the artifact, and print the table.

    `write_report`, not `enumerate_pairs`. Wired into the build as a
    generator, this printed all 56 rows, reported OK in 31.2s, and produced
    no file -- a step that looks like it worked because the evidence of its
    working is on stdout rather than on disk. Caught by looking for the
    artifact instead of reading the build summary.
    """
    payload = write_report()
    print("racetrack pairs: %d pairs x %d slopes = %d solves (trials factor)"
          % (payload["n_pairs"], len(payload["kahler_slopes"]),
             payload["trials_factor"]))
    print("ADOPTED: nothing. Ordered by pair name.")
    for row in payload["rows"]:
        for key in sorted(row["by_slope"]):
            r = row["by_slope"][key]
            if "error" in r:
                print("  %-8s %-4s ERROR %s" % (row["pair"], key, r["error"]))
                continue
            re_t = r["re_t_minimum"]
            print("  %-8s %-4s %-52s Re(T)=%s"
                  % (row["pair"], key, r["structure"],
                     "none" if re_t is None else "%.4f" % re_t))
    return 0


if __name__ == "__main__":       # pragma: no cover - CLI
    raise SystemExit(main())
