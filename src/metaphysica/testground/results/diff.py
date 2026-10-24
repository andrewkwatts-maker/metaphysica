"""Structural JSON diff as RFC 6902 ops (add, remove, replace) and its inverse.

Pointers follow RFC 6901 (``~0`` for ``~``, ``~1`` for ``/``). Objects are diffed
per key. An array of a different length is replaced whole; one of the same length
is diffed per index. Equality is exact: no rounding, and ``1``, ``1.0`` and
``True`` are three different values.
"""
from __future__ import annotations

import copy
import math
from typing import Any, Dict, List

Op = Dict[str, Any]


def escape(key: str) -> str:
    """One pointer segment, escaped."""
    return key.replace("~", "~0").replace("/", "~1")


def unescape(seg: str) -> str:
    """Inverse of :func:`escape`."""
    return seg.replace("~1", "/").replace("~0", "~")


def split_pointer(ptr: str) -> List[str]:
    """The unescaped segments of a pointer (``""`` is the root)."""
    if ptr == "":
        return []
    if not ptr.startswith("/"):
        raise ValueError("bad JSON pointer: %r" % ptr)
    return [unescape(s) for s in ptr[1:].split("/")]


def _scalar_equal(a: Any, b: Any) -> bool:
    if type(a) is not type(b):
        return False
    if isinstance(a, float) and math.isnan(a) and math.isnan(b):
        return True
    return a == b


def diff(a: Any, b: Any, base: str = "") -> List[Op]:
    """Ops turning ``a`` into ``b``."""
    if isinstance(a, dict) and isinstance(b, dict):
        return _diff_dict(a, b, base)
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        out: List[Op] = []
        for i, (x, y) in enumerate(zip(a, b)):
            out.extend(diff(x, y, "%s/%d" % (base, i)))
        return out
    if type(a) is type(b) and not isinstance(a, (dict, list)):
        return [] if _scalar_equal(a, b) else [_replace(base, b)]
    return [_replace(base, b)]


def _replace(ptr: str, value: Any) -> Op:
    return {"op": "replace", "path": ptr, "value": value}


def _diff_dict(a: dict, b: dict, base: str) -> List[Op]:
    out: List[Op] = []
    for k in a:
        ptr = "%s/%s" % (base, escape(str(k)))
        if k not in b:
            out.append({"op": "remove", "path": ptr})
        else:
            out.extend(diff(a[k], b[k], ptr))
    for k in b:
        if k not in a:
            out.append({"op": "add", "path": "%s/%s" % (base, escape(str(k))),
                        "value": b[k]})
    return out


def resolve(doc: Any, ptr: str) -> Any:
    """The value at ``ptr``; ``KeyError`` when absent."""
    cur = doc
    for seg in split_pointer(ptr):
        try:
            cur = cur[int(seg)] if isinstance(cur, list) else cur[seg]
        except (KeyError, IndexError, ValueError, TypeError):
            raise KeyError(ptr) from None
    return cur


def _parent(doc: Any, ptr: str):
    cut = ptr.rfind("/")
    return resolve(doc, ptr[:cut]), unescape(ptr[cut + 1:])


def apply_patch(doc: Any, ops: List[Op]) -> Any:
    """A deep copy of ``doc`` with ``ops`` applied; ``KeyError`` on a bad op."""
    out = copy.deepcopy(doc)
    for op in ops:
        out = _apply_one(out, op)
    return out


def _apply_one(doc: Any, op: Op) -> Any:
    kind, ptr = op["op"], op["path"]
    if kind not in ("add", "remove", "replace"):
        raise KeyError("unsupported op %r" % kind)
    if ptr == "":
        if kind != "replace":
            raise KeyError("root supports replace only")
        return copy.deepcopy(op["value"])
    parent, last = _parent(doc, ptr)
    if isinstance(parent, list):
        idx = int(last)
        if kind != "replace" or not 0 <= idx < len(parent):
            raise KeyError(ptr)
        parent[idx] = copy.deepcopy(op["value"])
    elif isinstance(parent, dict):
        _apply_dict(parent, last, kind, op, ptr)
    else:
        raise KeyError(ptr)
    return doc


def _apply_dict(parent: dict, key: str, kind: str, op: Op, ptr: str) -> None:
    if kind == "add":
        if key in parent:
            raise KeyError(ptr)
        parent[key] = copy.deepcopy(op["value"])
    elif key not in parent:
        raise KeyError(ptr)
    elif kind == "remove":
        del parent[key]
    else:
        parent[key] = copy.deepcopy(op["value"])
