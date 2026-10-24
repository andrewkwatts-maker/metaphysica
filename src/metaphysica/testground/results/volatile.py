"""Volatile-key detection and masking.

A key is volatile when it differs between two builds of the same configuration
(timestamps, durations, run ids). Keys are recorded as pointer patterns in which
every array index is ``*``; masking removes dict keys and nulls array items that
match a pattern, so the rest of the document compares exactly.
"""
from __future__ import annotations

import copy
from typing import Any, Iterable, List, Set, Tuple

from .diff import escape, split_pointer

Pattern = Tuple[str, ...]


def detect(a: Any, b: Any) -> Set[str]:
    """Pointer patterns (with ``*``) of every place ``a`` and ``b`` differ."""
    out: Set[str] = set()
    _walk(a, b, (), out)
    return out


def _walk(a: Any, b: Any, path: Pattern, out: Set[str]) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            if k in a and k in b:
                _walk(a[k], b[k], path + (str(k),), out)
            else:
                out.add(_join(path + (str(k),)))
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for x, y in zip(a, b):
            _walk(x, y, path + ("*",), out)
    elif not _same_leaf(a, b):
        out.add(_join(path))


def _same_leaf(a: Any, b: Any) -> bool:
    if isinstance(a, (dict, list)) or isinstance(b, (dict, list)):
        return False
    if type(a) is not type(b):
        return False
    return a == b or (a != a and b != b)


def _join(path: Pattern) -> str:
    return "".join("/" + escape(s) if s != "*" else "/*" for s in path)


def _compile(patterns: Iterable[str]) -> List[Pattern]:
    return [tuple(split_pointer(p)) for p in patterns]


def mask(doc: Any, patterns: Iterable[str]) -> Any:
    """A deep copy of ``doc`` with every volatile place removed or nulled."""
    out = copy.deepcopy(doc)
    for pat in _compile(patterns):
        if pat:
            _mask_at(out, pat)
    return out


def _mask_at(node: Any, pat: Pattern) -> None:
    head, rest = pat[0], pat[1:]
    if isinstance(node, list) and head == "*":
        for i in range(len(node)):
            if rest:
                _mask_at(node[i], rest)
            else:
                node[i] = None
    elif isinstance(node, dict) and head in node and head != "*":
        if rest:
            _mask_at(node[head], rest)
        else:
            del node[head]
