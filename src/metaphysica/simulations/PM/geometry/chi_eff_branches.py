"""Both chi_eff branches, executable, with their costs across the pipeline.

WHAT THIS IS FOR
================
chi_eff is an OPEN AUTHOR RULING and it blocks the EML track. This module does
not rule it. It makes both branches RUNNABLE and measures what each one costs
under each seed, so the choice can be made with numbers in hand instead of a
preference.

    branch A   CONSTANT        chi_eff is independent of the seed
    branch B   SEED_DEPENDENT  chi_eff = f(b_3), with the two claimed f's

`chi_eff_claim()` in `geometry_narration` keeps returning the dichotomy, and
the `chi_eff_route` fork defaults to UNRULED. Nothing here selects.

THE TWO FINDINGS, AND THEY ARE NEW COSTS THE DICHOTOMY DID NOT NAME
===================================================================

**1. Route C plus n_gen = chi_eff/48 IS the b_3/8 route, identically.**

    n_gen = chi_eff / 48 = 6 b_3 / 48 = b_3 / 8

exactly, for every b_3. So "chi_eff = 6 b_3" combined with the standard n_gen
formula is not an independent route to the generation count -- it is
`n_gen_source = b3_over_dim_O` wearing different notation. The register already
settled that one: b_3 is ODD at every Joyce-reachable profile (b_3 = 7 + 3 n_T3
with n_T3 even), and 8 divides no odd number, so b_3/8 is an integer NOWHERE on
the family. Route C therefore inherits that refutation wholesale.

**2. On the Joyce family, n_gen = chi_eff/48 fails on BOTH branches, differently.**

  * branch B gives a NON-INTEGER n_gen at every reachable profile:

        n_T3   b_3    b_3^2/4 -> n_gen     6 b_3 -> n_gen
           0     7      12.25 -> 0.2552       42 -> 0.875
           4    19      90.25 -> 1.8802      114 -> 2.375
           8    31     240.25 -> 5.0052      186 -> 3.875
          12    43     462.25 -> 9.6302      258 -> 5.375

    A generation count is a number of things. None of these is one, and the
    b_3 = 31 entry (5.00521) is close enough to 5 to be dangerous if anyone
    rounds it.

  * branch A gives n_gen = 3 at EVERY profile -- including n_T3 = 0, where the
    manifold carries no A_1 families at all and the generation count should be
    0. So the constant branch is not merely "carrying no topological content"
    as a matter of interpretation: it is DEMONSTRABLY wrong at a profile the
    construction reaches, and the demonstration is one line of arithmetic.

**So n_gen = chi_eff/48 does not survive the 43 path on either branch.** That
is a coupled cost: ruling chi_eff also rules on `n_gen_source`, and the two
forks are not independent. Which way to go remains the author's.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

__all__ = [
    "BRANCHES",
    "N_GEN_DIVISOR",
    "chi_eff_on_branch",
    "downstream_values",
    "branch_cost_table",
    "consumers",
    "route_c_is_the_b3_over_8_route",
    "branches_report",
]

#: n_gen = chi_eff / 48, the formula every branch is being costed against.
#: Named rather than inlined so the identity in `route_c_is_the_b3_over_8_route`
#: is checked against the same number the cost table uses.
N_GEN_DIVISOR: int = 48

#: The executable branches. Each is a function of b_3 alone, because that is
#: what "seed-dependent" means; branch A ignores its argument by construction
#: and that is the whole content of the branch.
BRANCHES: Dict[str, Dict[str, Any]] = {
    "constant_144": {
        "branch": "A",
        "kind": "CONSTANT",
        "expression": "144",
        "fn": lambda b3: 144.0,
        "consequence": (
            "chi_eff carries no topological content: n_gen = chi_eff/48 = 3 at "
            "every profile, including n_T3 = 0 where there are no A_1 families "
            "and the count should be 0"
        ),
    },
    "b3_squared_over_4": {
        "branch": "B",
        "kind": "SEED_DEPENDENT",
        "expression": "b_3^2 / 4",
        "fn": lambda b3: b3 ** 2 / 4.0,
        "consequence": (
            "chi_eff = 462.25 at b_3 = 43 -- not an integer, and neither is "
            "n_gen. Every consumer of the literal 144 moves."
        ),
    },
    "six_b3": {
        "branch": "B",
        "kind": "SEED_DEPENDENT",
        "expression": "6 b_3",
        "fn": lambda b3: 6.0 * b3,
        "consequence": (
            "chi_eff = 258 at b_3 = 43. Combined with n_gen = chi_eff/48 this "
            "is IDENTICALLY the b_3/8 route, which the register refuted across "
            "the whole family."
        ),
    },
}


def chi_eff_on_branch(branch_id: str, b3: int) -> float:
    """chi_eff under one branch at one seed. No branch is defaulted."""
    if branch_id not in BRANCHES:
        raise ValueError(
            "unknown chi_eff branch %r; declared: %s"
            % (branch_id, sorted(BRANCHES)))
    return float(BRANCHES[branch_id]["fn"](b3))


def downstream_values(branch_id: str, b3: int) -> Dict[str, Any]:
    """Every quantity that moves when chi_eff moves, at one (branch, seed).

    The three consumers are the ones the register names as load-bearing:
    n_gen = chi_eff/48, alpha_leak = 1/sqrt(chi_eff/b_3), and
    reid_invariant = 1/chi_eff.
    """
    import math

    chi = chi_eff_on_branch(branch_id, b3)
    n_gen = chi / N_GEN_DIVISOR
    ratio = chi / b3 if b3 else float("nan")

    return {
        "branch": branch_id,
        "b3": b3,
        "chi_eff": chi,
        "chi_eff_is_integer": abs(chi - round(chi)) < 1e-12,
        "n_gen": n_gen,
        "n_gen_is_integer": abs(n_gen - round(n_gen)) < 1e-12,
        "n_gen_equals_three": abs(n_gen - 3.0) < 1e-12,
        "alpha_leak": 1.0 / math.sqrt(ratio) if ratio > 0 else None,
        "reid_invariant": 1.0 / chi if chi else None,
        "counts_what": ("chi_eff is claimed as an EULER CHARACTERISTIC; n_gen "
                        "is a COUNT OF GENERATIONS and must be a non-negative "
                        "integer"),
    }


def _reachable_profiles() -> List[Dict[str, int]]:
    from metaphysica.simulations.PM.geometry.chi_eff_routes import (
        reachable_family,
    )

    return reachable_family()


def branch_cost_table(include_adopted_seed: bool = True) -> List[Dict[str, Any]]:
    """Every branch at every reachable profile, plus the adopted off-family seed.

    The adopted (b_2, b_3) = (4, 24) is included and LABELLED off-family: it is
    where all three routes agree, and leaving it out would hide the only point
    at which the dichotomy looks harmless.
    """
    points = [{"n_T3": f["n_T3"], "b3": f["b3"], "b2": f["b2"],
               "on_joyce_family": True} for f in _reachable_profiles()]
    if include_adopted_seed:
        points.insert(0, {"n_T3": None, "b3": 24, "b2": 4,
                          "on_joyce_family": False})

    rows = []
    for point in points:
        for branch_id in BRANCHES:
            rows.append({**point, **downstream_values(branch_id, point["b3"]),
                         "branch_kind": BRANCHES[branch_id]["kind"],
                         "expression": BRANCHES[branch_id]["expression"]})
    return rows


def route_c_is_the_b3_over_8_route() -> Dict[str, Any]:
    """6 b_3 / 48 = b_3 / 8, checked symbolically rather than at sample points.

    A sampled check could be a coincidence at the sampled b_3. This is an
    identity in the symbol, so it cannot be.
    """
    import sympy as sp

    b = sp.Symbol("b", positive=True)
    lhs = BRANCHES["six_b3"]["fn"](b) / N_GEN_DIVISOR
    rhs = b / 8
    difference = sp.simplify(lhs - rhs)

    return {
        "identity": "6 b_3 / 48 = b_3 / 8",
        "difference": str(difference),
        "holds_identically": difference == 0,
        "consequence": (
            "route C combined with n_gen = chi_eff/48 is not an independent "
            "route to the generation count: it IS n_gen_source = "
            "b3_over_dim_O. The register's refutation of that route -- b_3 is "
            "odd at every Joyce profile and 8 divides no odd number -- applies "
            "to route C unchanged."
        ),
        "a4_bar": ("both sides are COUNTS OF GENERATIONS; the 48 and the 8 are "
                   "divisors, not dimensions"),
    }


def consumers() -> Dict[str, Any]:
    """Modules that read chi_eff under any of its names, traced by source text.

    Named rather than reasoned about: the register's instruction for branch B
    is to name every downstream consumer, and a list produced from memory would
    be the defect this campaign keeps finding.
    """
    import pathlib
    import re

    root = pathlib.Path(__file__).resolve().parents[3]
    names = ("mephorash_chi", "qedem_chi_sum", "chi_eff_total", "chi_eff",
             "CHI_EFF", "reid_invariant", "alpha_leak")
    pattern = re.compile("|".join(re.escape(n) for n in names))

    # This module and the routes module discuss chi_eff rather than consuming
    # it; listing them would inflate the count with the instruments.
    exclude = {"simulations/PM/geometry/chi_eff_branches.py",
               "simulations/PM/geometry/chi_eff_routes.py",
               "simulations/PM/geometry/geometry_narration.py"}

    hits: Dict[str, int] = {}
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        if rel in exclude:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        n = len(pattern.findall(text))
        if n:
            hits[rel] = n

    return {
        "names_searched": list(names),
        "n_modules": len(hits),
        "n_mentions": sum(hits.values()),
        "by_module": dict(sorted(hits.items(), key=lambda kv: -kv[1])),
        "excluded_as_instruments": sorted(exclude),
        "what_moves_on_branch_B": (
            "every module above that uses a chi_eff VALUE rather than "
            "discussing it. The mention count is an upper bound on the work, "
            "not a count of breakages: some mentions are prose."
        ),
    }


def branches_report() -> Dict[str, Any]:
    """Both branches, both seeds, the whole cost. Adopts nothing."""
    table = branch_cost_table()
    identity = route_c_is_the_b3_over_8_route()

    on_family = [r for r in table if r["on_joyce_family"]]
    seed_dependent = [r for r in on_family if r["branch_kind"] == "SEED_DEPENDENT"]
    constant = [r for r in on_family if r["branch_kind"] == "CONSTANT"]

    non_integer = [r for r in seed_dependent if not r["n_gen_is_integer"]]
    empty_profile = [r for r in constant if r["n_T3"] == 0]

    return {
        "ruling": "OPEN -- this module adopts nothing",
        "branches": {k: {kk: vv for kk, vv in v.items() if kk != "fn"}
                     for k, v in BRANCHES.items()},
        "cost_table": table,
        "route_c_identity": identity,
        "consumers": consumers(),
        "branch_A_cost": (
            "n_gen = 3 at every reachable profile, including n_T3 = %s where "
            "the manifold carries no A_1 families and the count should be 0. "
            "chi_eff then carries no topological content, and this is "
            "demonstrated rather than interpreted."
            % ([r["n_T3"] for r in empty_profile] or "0")
        ),
        "branch_B_cost": (
            "n_gen is NON-INTEGER at %d of %d seed-dependent rows on the Joyce "
            "family, i.e. at every one. A generation count is a number of "
            "things. Additionally every consumer of the literal 144 moves: %d "
            "modules mention chi_eff under one of its names."
            % (len(non_integer), len(seed_dependent),
               consumers()["n_modules"])
        ),
        "the_coupled_cost": (
            "n_gen = chi_eff/48 does not survive the 43 path on EITHER branch: "
            "branch A makes it vacuous, branch B makes it non-integer. So "
            "ruling chi_eff also rules on n_gen_source -- the two forks are "
            "not independent, which the dichotomy as previously stated did not "
            "say."
        ),
        "still_the_authors": ["chi_eff", "n_gen_source", "b3_seed"],
    }
