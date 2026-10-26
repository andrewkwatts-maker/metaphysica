"""Footprints, interaction candidates and the additive prediction.

A single deviation changes a set of rows (its footprint). Two options of
different forks can only combine non-additively on rows both change.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, FrozenSet, Iterator, List, Mapping, Tuple

from metaphysica.testground.audit.rows import Option, Rows, Selection, changed, differs

__all__ = ["footprints", "interaction_sets", "predict", "non_additive"]

OptionSet = Tuple[Option, ...]


def footprints(base: Rows, singles: Mapping[Option, Rows]) -> Dict[Option, FrozenSet[str]]:
    """{option: rows its single deviation changes}."""
    return {opt: changed(base, rows) for opt, rows in singles.items()}


def _extend(sets: List[OptionSet], opts: List[Option],
            fp: Mapping[Option, FrozenSet[str]]) -> Iterator[OptionSet]:
    for cur in sets:
        for opt in opts:
            if opt <= cur[-1] or any(opt[0] == o[0] or not fp[opt] & fp[o] for o in cur):
                continue
            yield cur + (opt,)


def interaction_sets(fp: Mapping[Option, FrozenSet[str]], *, k_max: int = 3,
                     compatible: Callable[[Dict[str, str]], bool] = lambda sel: True,
                     limit: int = 10_000) -> List[OptionSet]:
    """Sets of 2..k_max options, distinct forks, pairwise sharing a row, compatible.

    Sorted tuples, ordered by size then lexicographically. Raises ValueError past *limit*.
    """
    if not 2 <= k_max <= 4:
        raise ValueError(f"k_max must be 2..4, got {k_max}")
    opts = sorted(fp)
    level: List[OptionSet] = [(o,) for o in opts]
    out: List[OptionSet] = []
    for _ in range(2, k_max + 1):
        level = sorted(_extend(level, opts, fp))
        out.extend(s for s in level if compatible(dict(s)))
        if len(out) > limit:
            raise ValueError(f"{len(out)} interaction sets so far exceed limit {limit}")
    return out


def _freeze(v: Any) -> Any:
    if isinstance(v, (list, tuple)):
        return tuple(_freeze(x) for x in v)
    if isinstance(v, dict):
        return tuple(sorted((k, _freeze(x)) for k, x in v.items()))
    return v


def _allowed(base: Rows, singles: Mapping[Option, Rows],
             selection: Selection) -> Dict[str, List[Any]]:
    chosen = [singles[o] for o in sorted(selection.items()) if o in singles]
    keys = set(base).union(*chosen) if chosen else set(base)
    out: Dict[str, List[Any]] = {}
    for k in keys:
        moved = [r.get(k) for r in chosen if differs(base.get(k), r.get(k))]
        out[k] = moved or [base.get(k)]
    return out


def predict(base: Rows, singles: Mapping[Option, Rows],
            selection: Selection) -> Dict[str, FrozenSet]:
    """Allowed values per row: baseline if no chosen option moved it, else the moved values.

    Chosen options without a single run are skipped. Unhashable values are frozen
    (lists to tuples, dicts to sorted item tuples).
    """
    return {k: frozenset(_freeze(v) for v in vs)
            for k, vs in _allowed(base, singles, selection).items()}


def non_additive(base: Rows, singles: Mapping[Option, Rows], selection: Selection,
                 joint_rows: Rows) -> List[str]:
    """Rows whose joint value is none of the allowed values (sorted)."""
    allowed = _allowed(base, singles, selection)
    keys = set(base) | set(joint_rows) | set(allowed)
    return sorted(k for k in keys
                  if all(differs(joint_rows.get(k), e)
                         for e in allowed.get(k, [base.get(k)])))
