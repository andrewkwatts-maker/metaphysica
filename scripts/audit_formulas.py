"""Audit the formula registry's triple-track coverage and dry-run consistency.

Walks every simulation module under ``simulations.PM.*``, collects the
``Formula`` records they emit via ``get_formulas()``, and reports:

* how many are fully triple-tracked (arithma + eml + value),
* how many are missing only one symbolic leg,
* how many are float-only or missing values entirely,
* any formula where ``triple_assert`` currently DISAGREES (dry-run).

Writes a JSON report to ``scripts/_audit_formulas.json`` and a human
summary table to stdout. Exit code:

* ``0`` — no disagreements (legs may still be missing; that's a warning).
* ``1`` — at least one formula fails the triple cross-check.

Usage:
    python scripts/audit_formulas.py
"""
from __future__ import annotations

import importlib
import json
import pkgutil
import sys
import traceback
import warnings
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

OUTPUT_JSON = REPO_ROOT / "scripts" / "_audit_formulas.json"


def _iter_pm_modules():
    """Yield every importable module name under metaphysica.simulations.PM."""
    import metaphysica.simulations.PM as pm_pkg
    for info in pkgutil.walk_packages(pm_pkg.__path__, prefix="metaphysica.simulations.PM."):
        yield info.name


def _collect_formulas() -> List[Tuple[str, Any]]:
    """Instantiate each simulation and harvest its formulas. Returns
    a list of ``(module_name, Formula)`` tuples."""
    from metaphysica.simulations.base import SimulationBase

    formulas: List[Tuple[str, Any]] = []
    for mod_name in _iter_pm_modules():
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        for attr in dir(mod):
            try:
                obj = getattr(mod, attr)
            except Exception:
                continue
            if not isinstance(obj, type):
                continue
            if obj is SimulationBase:
                continue
            if not issubclass(obj, SimulationBase):
                continue
            # Skip abstract intermediate classes — only count concrete sims.
            try:
                sim = obj()
            except Exception:
                continue
            getter = getattr(sim, "get_formulas", None)
            if not callable(getter):
                continue
            try:
                fs = getter() or []
            except Exception:
                continue
            for f in fs:
                if f is not None and hasattr(f, "id"):
                    formulas.append((mod_name, f))
    return formulas


def _classify(formula) -> str:
    has_a = getattr(formula, "arithma", None) is not None
    has_e = getattr(formula, "eml", None) is not None
    has_v = getattr(formula, "value", None) is not None
    if has_a and has_e and has_v:
        return "TRIPLE"
    if has_a and has_v:
        return "ARITHMA_ONLY"
    if has_e and has_v:
        return "EML_ONLY"
    if has_v:
        return "FLOAT_ONLY"
    if has_a or has_e:
        return "SYMBOLIC_NO_VALUE"
    return "MISSING_ALL"


def _dry_run_assert(formula) -> Optional[str]:
    """Return None on agreement, or an error message on disagreement.

    Skips when the formula has no value or no symbolic view (those are
    captured by the coverage counts, not by failures).
    """
    has_a = getattr(formula, "arithma", None) is not None
    has_e = getattr(formula, "eml", None) is not None
    has_v = getattr(formula, "value", None) is not None
    if not has_v or not (has_a or has_e):
        return None
    try:
        from metaphysica.simulations.core.triple_validator import (
            triple_assert,
            FormulaConsistencyError,
        )
    except ImportError as exc:
        return f"triple_validator import failed: {exc}"
    try:
        triple_assert(
            formula.arithma,
            formula.eml,
            float(formula.value),
            env=formula.triple_env or {},
            rel=getattr(formula, "triple_rel", 1e-12),
            abs_=getattr(formula, "triple_abs", 0.0),
            name=formula.id,
        )
        return None
    except FormulaConsistencyError as exc:
        return str(exc)
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"


def main(argv: Optional[List[str]] = None) -> int:
    warnings.simplefilter("ignore")

    print("Collecting formulas from simulations.PM.* ...")
    formulas = _collect_formulas()
    print(f"  {len(formulas)} formula objects discovered")

    counts = Counter()
    failures: List[Dict[str, str]] = []
    per_formula: Dict[str, Dict[str, Any]] = {}

    for mod_name, f in formulas:
        klass = _classify(f)
        counts[klass] += 1
        err = _dry_run_assert(f)
        per_formula[f.id] = {
            "module": mod_name,
            "classification": klass,
            "triple_status": getattr(f, "triple_status", ""),
            "dry_run_error": err,
        }
        if err is not None:
            failures.append({"id": f.id, "module": mod_name, "error": err})

    # ── Summary table ───────────────────────────────────────────────────
    print()
    print("=== Triple-track audit summary ===")
    rows = [
        ("Total formulas",            len(formulas)),
        ("Triple-tracked",            counts["TRIPLE"]),
        ("Arithma + value only",      counts["ARITHMA_ONLY"]),
        ("EML + value only",          counts["EML_ONLY"]),
        ("Float only (legacy)",       counts["FLOAT_ONLY"]),
        ("Symbolic but no value",     counts["SYMBOLIC_NO_VALUE"]),
        ("Missing arithma+eml+value", counts["MISSING_ALL"]),
        ("Dry-run failures",          len(failures)),
    ]
    width = max(len(label) for label, _ in rows)
    for label, n in rows:
        print(f"  {label:<{width}}  {n}")

    if failures:
        print()
        print(f"=== {len(failures)} dry-run cross-check failures ===")
        for fail in failures[:25]:
            print(f"  - {fail['id']} ({fail['module']}): {fail['error'][:140]}")
        if len(failures) > 25:
            print(f"  ... and {len(failures) - 25} more (see {OUTPUT_JSON})")

    report = {
        "totals": dict(counts),
        "n_formulas": len(formulas),
        "failures": failures,
        "per_formula": per_formula,
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2, default=str)
    print(f"\nFull report written to {OUTPUT_JSON.relative_to(REPO_ROOT)}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
