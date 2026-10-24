"""Per-file patches of a path build against the main build, and their checks."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .diff import Op, apply_patch, diff, escape, resolve, split_pointer
from .volatile import mask


def file_ops(main_raw: Any, path_raw: Any, patterns: Iterable[str],
             main_masked: Any = None) -> List[Op]:
    """Ops turning main into the path build, volatile places excluded.

    Values come from the unmasked path document, so a replaced array keeps
    every key it holds.
    """
    pats = list(patterns)
    base = main_masked if main_masked is not None else mask(main_raw, pats)
    ops = diff(base, mask(path_raw, pats))
    for op in ops:
        if "value" in op:
            op["value"] = resolve(path_raw, op["path"])
    return ops


def roundtrip_ok(main_raw: Any, path_raw: Any, ops: List[Op],
                 patterns: Iterable[str]) -> bool:
    """``apply(main, ops) == path`` with volatile places masked."""
    pats = list(patterns)
    try:
        got = apply_patch(main_raw, ops)
    except (KeyError, ValueError, TypeError):
        return False
    return diff(mask(got, pats), mask(path_raw, pats)) == []


def published_ok(pub_raw: Any, main_raw: Any, ops: List[Op],
                 patterns: Iterable[str]) -> bool:
    """Every op is valid against the published file, not just the main build."""
    pats = list(patterns)
    pub, main = mask(pub_raw, pats), mask(main_raw, pats)
    return all(_op_ok(pub, main, op) for op in ops)


def _op_ok(pub: Any, main: Any, op: Op) -> bool:
    ptr = op["path"]
    try:
        if op["op"] == "add":
            segs = split_pointer(ptr)
            parent_ptr = "".join("/" + escape(s) for s in segs[:-1])
            parent = resolve(pub, parent_ptr)
            return isinstance(parent, dict) and segs[-1] not in parent
        return diff(resolve(pub, ptr), resolve(main, ptr)) == []
    except (KeyError, IndexError):
        return False


def count_by_file(files: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
    """Ops per file, for the summary's ``changed.by_artifact``."""
    return {name: len(entry["ops"]) for name, entry in files.items()}
