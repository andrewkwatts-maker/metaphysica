"""The toy theory's physics: one seed, one coupling, one light mass.

A deliberately tiny, FICTITIOUS model that exercises every part of the test
ground in microseconds. Nothing here is physical data or a physical claim.

The model has one integer seed (``SEED = 7``). Each option of a physics fork
contributes a FORMULA, written as a Python expression and evaluated here; the
same expressions are walked (with ``ast``) to count what the elegance and
closure criteria count, so no score is typed by hand:

* a formula that never mentions ``SEED`` is not rooted in the seed;
* a non-integer literal in a formula is a raw literal leaf;
* a formula that reads ``ALPHA_FIT`` uses a fitted input.

Observables (two data rows): the low-energy coupling ``alpha_low`` and the
light mass ``m_light``. Checks: a tachyon check (validity), a target fact
``n_light_states = 3`` (validity), a Ward identity, a Lorentz identity and a
strong-CP-like phase (consistency; the last fails on every path -- a standing
failure the assessment must exclude and disclose).

The full-run pipeline calls :func:`main` in a fresh process; it reads the
selection from the environment (``TOY_VARIANT_<FORK>``) and writes
``toy_output.json`` into the working directory, so the screen (in-process)
and the full run (subprocess) compute from one source.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import ast
import json
import math
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

__all__ = [
    "SEED",
    "ENV_PREFIX",
    "ARTIFACT",
    "TOY_DATA",
    "FORMULAS",
    "Prediction",
    "predict",
    "clear_cache",
    "selection_from_env",
    "write_artifact",
    "main",
]

SEED = 7                                  # the toy's single integer input
ENV_PREFIX = "TOY_VARIANT_"
ARTIFACT = "toy_output.json"
SUMMARY = "toy_summary.txt"
TOLERANCE = 1e-12

#: Invented "measurements" (value, sigma) -- NOT physical data.
TOY_DATA: Dict[str, Tuple[float, float]] = {
    "alpha_low": (0.0700, 0.0013),
    "m_light": (6.6e-4, 0.3e-4),
}
ALPHA_FIT = TOY_DATA["alpha_low"][0]      # the value a fitted route adopts
LATTICE_CUTOFF = 10.0                     # finite regulator of the lattice

#: (fork, option) -> the formula that option contributes. Options absent here
#: change no formula (the cutoff drops out of low-energy observables after
#: renormalisation; the singlet's charge is a discrete input, not a formula).
FORMULAS: Dict[Tuple[str, str], str] = {
    ("coupling_route", "geometric"): "1 / (2 * SEED + 1)",
    ("coupling_route", "fitted"): "ALPHA_FIT",
    ("coupling_route", "numerology"): "0.0729",
    ("mass_rule", "seesaw"): "(G0 ** 2 / SEED) ** 2",
    ("mass_rule", "dirac_only"): "G0 ** 2 - G0 / SEED",
    ("matching", "one_loop"): "G0 / (SEED + 1)",
    ("matching", "tree"): "0",
}
FITTED_SYMBOLS = frozenset({"ALPHA_FIT"})
UNIMPLEMENTED = frozenset({("mass_rule", "radiative")})


class Prediction(dict):
    """The model's output for one selection (a plain JSON-able mapping)."""


def _evaluate(expr: str, scope: Mapping[str, float]) -> float:
    tree = ast.parse(expr, mode="eval")
    return float(eval(compile(tree, "<toy>", "eval"), {"__builtins__": {}},
                      dict(scope)))


def formula_stats(expr: str) -> Dict[str, int]:
    """Counts read off a formula's syntax tree, never typed by hand."""
    nodes = list(ast.walk(ast.parse(expr, mode="eval")))
    names = {n.id for n in nodes if isinstance(n, ast.Name)}
    literals = [n for n in nodes if isinstance(n, ast.Constant)
                and isinstance(n.value, float)]
    rooted = "SEED" in names or "G0" in names
    trivial = all(isinstance(n, (ast.Expression, ast.Constant)) for n in nodes) \
        and not literals
    return {"literal_leaves": len(literals),
            "unrooted": int(not rooted and not trivial),
            "fitted_inputs": len(names & FITTED_SYMBOLS)}


def _formula(selection: Mapping[str, str], fork: str) -> str:
    option = selection[fork]
    if (fork, option) in UNIMPLEMENTED:
        raise NotImplementedError("%s=%s has no implementation" % (fork, option))
    return FORMULAS[(fork, option)]


def _verdict(pull: float) -> str:
    size = abs(pull)
    return "PASS" if size < 2 else "TENSION" if size < 3 else "FAIL"


def _rows(values: Mapping[str, Optional[float]]) -> List[Dict[str, Any]]:
    rows = []
    for key, (measured, sigma) in TOY_DATA.items():
        value = values.get(key)
        if value is None:
            rows.append({"id": key, "verdict": "UNEVALUABLE", "sigma": None})
            continue
        pull = (value - measured) / sigma
        rows.append({"id": key, "verdict": _verdict(pull),
                     "sigma": round(pull, 6), "predicted": value,
                     "measured": measured})
    return rows


def _identities(selection: Mapping[str, str], g0: float,
                threshold: float) -> Dict[str, float]:
    """Residuals of the identities the consistency criterion counts."""
    g_heavy = g0 * SEED / (SEED + 1)
    ward = abs(g_heavy + threshold - g0)
    lattice = selection.get("cutoff") == "lattice"
    lorentz = (1.0 / LATTICE_CUTOFF) ** 2 / 12.0 if lattice else 0.0
    return {"ward_identity": ward, "lorentz_identity": lorentz,
            "strong_cp_phase": 1.0}     # no mechanism on any path: standing


@lru_cache(maxsize=256)
def _predict(selection: Tuple[Tuple[str, str], ...]) -> Prediction:
    sel = dict(selection)
    scope: Dict[str, float] = {"SEED": SEED, "ALPHA_FIT": ALPHA_FIT}
    used = [_formula(sel, f) for f in ("coupling_route", "mass_rule",
                                       "matching")]
    g0 = _evaluate(used[0], scope)
    scope["G0"] = g0
    m2 = _evaluate(used[1], scope)
    threshold = _evaluate(used[2], scope)
    m_light = math.sqrt(m2) if m2 >= 0 else None
    stats = [formula_stats(e) for e in used]
    return Prediction(
        selection=sel,
        observables={"alpha_low": g0, "m_light": m_light, "m2": m2},
        n_light_states=SEED - 4,
        identities=_identities(sel, g0, threshold),
        formulas=used,
        literal_leaves=sum(s["literal_leaves"] for s in stats),
        unrooted_formulas=sum(s["unrooted"] for s in stats),
        fitted_inputs=sum(s["fitted_inputs"] for s in stats),
        rows=_rows({"alpha_low": g0, "m_light": m_light}),
    )


def predict(selection: Mapping[str, str]) -> Prediction:
    """The model's output for ``selection`` (cached by selection)."""
    return _predict(tuple(sorted(dict(selection).items())))


def clear_cache() -> None:
    """Forget cached predictions (the theory's ``invalidate_caches``)."""
    _predict.cache_clear()


def selection_from_env(defaults: Mapping[str, str],
                       env: Optional[Mapping[str, str]] = None) -> Dict[str, str]:
    """The selection a fresh process runs: env override, else the default."""
    env = os.environ if env is None else env
    return {fork: env.get(ENV_PREFIX + fork.upper(), option)
            for fork, option in defaults.items()}


def write_artifact(out_dir: Path, selection: Mapping[str, str]) -> Path:
    """Stage `compute`: write the prediction for ``selection``."""
    path = Path(out_dir) / ARTIFACT
    payload = dict(predict(selection))
    path.write_text(json.dumps(payload, indent=1, sort_keys=True),
                    encoding="utf-8")
    return path


def write_summary(out_dir: Path) -> Path:
    """Stage `generate`: render the artifact as one human-readable line."""
    data = json.loads((Path(out_dir) / ARTIFACT).read_text(encoding="utf-8"))
    verdicts = ", ".join("%s %s" % (r["id"], r["verdict"]) for r in data["rows"])
    path = Path(out_dir) / SUMMARY
    path.write_text("toy: %s\n" % verdicts, encoding="utf-8")
    return path


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point of the full-run stages (`compute` or `generate`)."""
    from metaphysica.theories.toy.forks import defaults
    args = list(sys.argv[1:] if argv is None else argv)
    stage = args[0] if args else "compute"
    if stage == "compute":
        write_artifact(Path.cwd(), selection_from_env(defaults()))
    elif stage == "generate":
        write_summary(Path.cwd())
    else:
        print("unknown stage %r" % stage, file=sys.stderr)
        return 2
    return 0
