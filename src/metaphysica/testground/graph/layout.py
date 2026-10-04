"""Layout: deterministic layered positions for the path graph, in integers.

Computed here, once, so the website and the app draw identical positions (and
visual-regression captures cannot drift). No randomness, no floating point:

- the theory node sits at the left, level with the active row;
- one column per fork, ordered by constraint depth (a fork that requires
  another sits to its right), then kind (physics < policy < narrative), then
  declaration order;
- inside a column: the fork header, then its options -- the one on the active
  path first, then the CONSIDERED ones by priority, then the DISABLED ones,
  each group in declaration order;
- narrative nodes in a band across the top; decisions in a band at the
  bottom, each centred on the mean x of the nodes it is linked to, ties
  broken by id, pushed right just enough not to overlap.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import (Any, Dict, Iterable, List, Mapping, Optional, Sequence,
                    Set, Tuple)

from metaphysica.testground.constraints import Requires

__all__ = [
    "LAYOUT_VERSION",
    "KIND_ORDER",
    "constraint_depths",
    "column_key",
    "option_row_key",
    "layout_graph",
]

LAYOUT_VERSION = 1
KIND_ORDER = {"physics": 0, "policy": 1, "narrative": 2}

MARGIN = 24
THEORY_W, THEORY_H = 180, 64
COLUMN_W, COLUMN_GAP = 220, 56
FORK_H, OPTION_H, ROW_GAP = 48, 36, 10
BAND_GAP = 64
DECISION_W, DECISION_H, DECISION_GAP = 120, 40, 12
NARRATIVE_W, NARRATIVE_H = 200, 44

Box = List[int]


def _reaches(graph: Mapping[str, Set[str]], start: str, goal: str) -> bool:
    stack, seen = [start], {start}
    while stack:
        node = stack.pop()
        if node == goal:
            return True
        for nxt in sorted(graph.get(node, ())):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return False


def _requirement_edges(fork_ids: Sequence[str],
                       constraints: Iterable[Any]) -> List[Tuple[str, str]]:
    """(prerequisite fork, dependent fork) pairs, cycle-free, deterministic.

    Only `Requires` orders columns (Excludes is symmetric). Edges are taken in
    declaration order of the dependent fork, and one that would close a cycle
    is skipped.
    """
    index = {f: i for i, f in enumerate(fork_ids)}
    wanted = sorted({(c.needs_fork, c.fork) for c in constraints
                     if isinstance(c, Requires) and c.fork in index
                     and c.needs_fork in index and c.fork != c.needs_fork},
                    key=lambda e: (index[e[1]], index[e[0]]))
    graph: Dict[str, Set[str]] = {}
    kept: List[Tuple[str, str]] = []
    for before, after in wanted:
        if _reaches(graph, after, before):
            continue
        graph.setdefault(before, set()).add(after)
        kept.append((before, after))
    return kept


def constraint_depths(fork_ids: Sequence[str],
                      constraints: Iterable[Any]) -> Dict[str, int]:
    """fork -> length of the longest chain of requirements leading to it."""
    depth = {f: 0 for f in fork_ids}
    edges = _requirement_edges(fork_ids, constraints)
    for _ in range(len(fork_ids)):
        changed = False
        for before, after in edges:
            if depth[after] < depth[before] + 1:
                depth[after] = depth[before] + 1
                changed = True
        if not changed:
            break
    return depth


def column_key(depth: int, kind: str, order: int) -> Tuple[int, int, int]:
    """Sort key of a fork column: depth, then kind, then declaration order."""
    return (depth, KIND_ORDER.get(kind, len(KIND_ORDER)), order)


def option_row_key(node: Mapping[str, Any]) -> Tuple[int, int, int]:
    """Sort key of an option row: active path, CONSIDERED by priority, DISABLED."""
    attrs = node.get("attrs", {})
    if attrs.get("on_active_path"):
        group, priority = 0, 0
    elif node.get("status") == "disabled":
        group, priority = 2, 0
    else:
        group, priority = 1, int(attrs.get("priority") or 0)
    return (group, priority, int(attrs.get("order", 0)))


def _by_type(graph: Mapping[str, Any]) -> Dict[str, List[Mapping[str, Any]]]:
    out: Dict[str, List[Mapping[str, Any]]] = {
        "theory": [], "fork": [], "option": [], "decision": [], "narrative": []}
    for node in graph.get("nodes", ()):
        if node["type"] not in out:
            raise ValueError("node %r has unknown type %r"
                             % (node["id"], node["type"]))
        out[node["type"]].append(node)
    return out


def _ordered_forks(forks: Sequence[Mapping[str, Any]]
                   ) -> List[Mapping[str, Any]]:
    def key(node: Mapping[str, Any]) -> Tuple[int, int, int]:
        attrs = node.get("attrs", {})
        return column_key(int(attrs.get("depth", 0)),
                          str(attrs.get("kind", "physics")),
                          int(attrs.get("order", 0)))
    return sorted(forks, key=key)


def _place_columns(forks: Sequence[Mapping[str, Any]],
                   options: Sequence[Mapping[str, Any]], top: int,
                   positions: Dict[str, Box]) -> Tuple[List[Dict[str, Any]], int]:
    """Fork headers and option rows; returns (columns, lowest y used)."""
    by_fork: Dict[str, List[Mapping[str, Any]]] = {}
    for node in options:
        by_fork.setdefault(str(node.get("attrs", {}).get("fork")), []).append(node)
    columns: List[Dict[str, Any]] = []
    bottom = top + FORK_H
    x0 = MARGIN + THEORY_W + COLUMN_GAP
    for i, fork in enumerate(_ordered_forks(forks)):
        x = x0 + i * (COLUMN_W + COLUMN_GAP)
        positions[fork["id"]] = [x, top, COLUMN_W, FORK_H]
        y = top + FORK_H + ROW_GAP
        attrs = fork.get("attrs", {})
        fork_id = str(attrs.get("fork", fork.get("label")))
        for node in sorted(by_fork.pop(fork_id, []), key=option_row_key):
            positions[node["id"]] = [x, y, COLUMN_W, OPTION_H]
            y += OPTION_H + ROW_GAP
        bottom = max(bottom, y - ROW_GAP)
        columns.append({"fork": fork_id, "node": fork["id"], "index": i,
                        "x": x, "w": COLUMN_W,
                        "depth": int(attrs.get("depth", 0)),
                        "kind": attrs.get("kind", "physics")})
    if by_fork:
        raise ValueError("options without a fork column: %s"
                         % sorted(n["id"] for v in by_fork.values() for n in v))
    return columns, bottom


def _linked_centres(graph: Mapping[str, Any],
                    positions: Mapping[str, Box]) -> Dict[str, List[int]]:
    """decision node id -> x centres of the positioned nodes linked to it."""
    out: Dict[str, List[int]] = {}
    for edge in graph.get("edges", ()):
        box = positions.get(edge["source"])
        if box is not None and edge["target"].startswith("decision:"):
            out.setdefault(edge["target"], []).append(box[0] + box[2] // 2)
    return out


def _place_decisions(decisions: Sequence[Mapping[str, Any]],
                     centres: Mapping[str, List[int]], y: int,
                     positions: Dict[str, Box]) -> None:
    def desired(node: Mapping[str, Any]) -> Optional[int]:
        xs = centres.get(node["id"])
        if not xs:
            return None
        return (sum(xs) + len(xs) // 2) // len(xs) - DECISION_W // 2
    wanted = [(desired(n), n["id"]) for n in decisions]
    cursor = MARGIN
    for want, node_id in sorted(wanted, key=lambda w: (w[0] is None,
                                                       w[0] or 0, w[1])):
        x = cursor if want is None else max(want, cursor)
        positions[node_id] = [x, y, DECISION_W, DECISION_H]
        cursor = x + DECISION_W + DECISION_GAP


def _place_narrative(narrative: Sequence[Mapping[str, Any]],
                     positions: Dict[str, Box]) -> None:
    x = MARGIN + THEORY_W + COLUMN_GAP
    for node in narrative:
        positions[node["id"]] = [x, MARGIN, NARRATIVE_W, NARRATIVE_H]
        x += NARRATIVE_W + DECISION_GAP


def _bbox(positions: Mapping[str, Box]) -> List[int]:
    right = max((b[0] + b[2] for b in positions.values()), default=0)
    bottom = max((b[1] + b[3] for b in positions.values()), default=0)
    return [0, 0, right + MARGIN, bottom + MARGIN]


def layout_graph(graph: Mapping[str, Any]) -> Dict[str, Any]:
    """``{version, bbox, positions{id: [x, y, w, h]}, columns, bands}``."""
    nodes = _by_type(graph)
    positions: Dict[str, Box] = {}
    _place_narrative(nodes["narrative"], positions)
    top = MARGIN + (NARRATIVE_H + BAND_GAP if nodes["narrative"] else 0)
    columns, bottom = _place_columns(nodes["fork"], nodes["option"], top,
                                     positions)
    first_row = top + FORK_H + ROW_GAP
    for node in nodes["theory"]:
        positions[node["id"]] = [MARGIN, first_row - (THEORY_H - OPTION_H) // 2,
                                 THEORY_W, THEORY_H]
        bottom = max(bottom, positions[node["id"]][1] + THEORY_H)
    band = bottom + BAND_GAP
    _place_decisions(nodes["decision"], _linked_centres(graph, positions),
                     band, positions)
    return {
        "version": LAYOUT_VERSION,
        "bbox": _bbox(positions),
        "positions": positions,
        "columns": columns,
        "bands": {"narrative": MARGIN if nodes["narrative"] else None,
                  "decisions": band},
    }
