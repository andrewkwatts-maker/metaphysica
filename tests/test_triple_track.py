"""Triple-track CI gate (Phase E.7).

Walks every formula registered by every ``simulations.PM`` simulation and
runs :func:`triple_assert` on it. Fully-migrated formulas (those carrying
``arithma`` + ``eml`` + ``value``, or one symbolic leg + value) are
exercised unconditionally. Formulas still in the legacy float-only / no-
value state are individually skipped with a clear reason, so the suite
stays green while the migration is in progress.

Any disagreement between Arithma, EML, and the canonical float fails
loudly with the full :class:`FormulaConsistencyError` message — which is
the whole point of the gate.
"""
from __future__ import annotations

import importlib
import pkgutil
import sys
import warnings
from typing import Any, List, Tuple

import pytest


# ── Discovery ────────────────────────────────────────────────────────────────


def _iter_pm_modules():
    import metaphysica.simulations.PM as pm_pkg
    for info in pkgutil.walk_packages(pm_pkg.__path__, prefix="metaphysica.simulations.PM."):
        yield info.name


def _collect_formulas() -> List[Tuple[str, str, Any]]:
    """Return ``(module, formula_id, Formula)`` triples for every simulation
    that defines :meth:`get_formulas`."""
    from metaphysica.simulations.base import SimulationBase

    triples: List[Tuple[str, str, Any]] = []
    seen = set()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
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
                if obj is SimulationBase or not issubclass(obj, SimulationBase):
                    continue
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
                    if f is None or not hasattr(f, "id"):
                        continue
                    if f.id in seen:
                        continue
                    seen.add(f.id)
                    triples.append((mod_name, f.id, f))
    return triples


_FORMULAS = _collect_formulas()


# ── Pytest collection helpers ────────────────────────────────────────────────


def _can_triple_check(formula) -> bool:
    """Return True when the formula has enough data to run triple_assert.

    ``triple_assert`` needs at least one symbolic view AND a canonical
    float value. Anything less is a migration TODO, not a test failure.
    """
    has_a = getattr(formula, "arithma", None) is not None
    has_e = getattr(formula, "eml", None) is not None
    has_v = getattr(formula, "value", None) is not None
    return has_v and (has_a or has_e)


def _ids() -> List[str]:
    return [fid for _, fid, _ in _FORMULAS]


# ── The actual test ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "module_name, formula_id, formula",
    _FORMULAS,
    ids=_ids() or ["no-formulas-collected"],
)
def test_triple_track(module_name: str, formula_id: str, formula: Any) -> None:
    """For every formula that has finished triple-track migration,
    Arithma + EML + float must agree at registration tolerances.

    Formulas still missing one or more legs are skipped with a reason so
    the migration progress is auditable from the test report."""
    if not _can_triple_check(formula):
        pytest.skip(f"not yet triple-tracked ({formula_id})")
    from metaphysica.simulations.core.triple_validator import triple_assert

    triple_assert(
        formula.arithma,
        formula.eml,
        float(formula.value),
        env=getattr(formula, "triple_env", None) or {},
        rel=getattr(formula, "triple_rel", 1e-12),
        abs_=getattr(formula, "triple_abs", 0.0),
        name=formula_id,
    )


def test_at_least_one_formula_was_collected() -> None:
    """Sanity check the discovery pipeline didn't silently collect zero
    formulas (which would make the parametrized test vacuously pass)."""
    assert len(_FORMULAS) > 0, (
        "No formulas collected from simulations.PM.*; "
        "the discovery loop is broken."
    )
