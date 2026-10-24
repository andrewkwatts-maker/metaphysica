"""Lineage layout: integer era columns and lanes, deterministic.

x comes from the era order (eras de-duplicated, sorted as text, so YYYY-MM
precedes a YYYY-MM-DD within it). Trunk and active versions take lane 0;
branches and dead ends take the lowest free lane below it. A version whose
preferred lane is taken in its era moves down, so no two boxes overlap and
the lane count is the minimum the eras allow.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

from metaphysica.testground.lineage.model import (ACTIVE, TRUNK, Lineage,
                                                  Version)

__all__ = ["BOX_W", "BOX_H", "era_order", "version_lanes", "layout_lineage"]

MARGIN = 24
BOX_W, BOX_H = 200, 64
COL_GAP, LANE_GAP = 56, 40
HEADER_H = 28


def era_order(lineage: Lineage) -> List[str]:
    """The distinct eras, oldest first."""
    return sorted({v.era for v in lineage.versions})


def version_lanes(lineage: Lineage) -> Dict[str, int]:
    """version id -> lane (0 = trunk and active)."""
    eras = era_order(lineage)
    taken: Set[Tuple[int, int]] = set()
    lanes: Dict[str, int] = {}
    ordered = sorted(enumerate(lineage.versions),
                     key=lambda p: (eras.index(p[1].era), p[0]))
    for _, v in ordered:
        col = eras.index(v.era)
        lane = 0 if v.status in (TRUNK, ACTIVE) else 1
        while (col, lane) in taken:
            lane += 1
        taken.add((col, lane))
        lanes[v.id] = lane
    return lanes


def _box(v: Version, eras: List[str], lane: int) -> List[int]:
    x = MARGIN + eras.index(v.era) * (BOX_W + COL_GAP)
    y = MARGIN + HEADER_H + lane * (BOX_H + LANE_GAP)
    return [x, y, BOX_W, BOX_H]


def layout_lineage(lineage: Lineage) -> Dict[str, Any]:
    """``{bbox, eras, lanes, positions}`` for ``layout.lineage``."""
    eras, lanes = era_order(lineage), version_lanes(lineage)
    positions = {"version:%s" % v.id: _box(v, eras, lanes[v.id])
                 for v in lineage.versions}
    n_lanes = max(lanes.values(), default=0) + 1
    right = max((b[0] + b[2] for b in positions.values()), default=0)
    bottom = max((b[1] + b[3] for b in positions.values()), default=0)
    return {
        "bbox": [0, 0, right + MARGIN, bottom + MARGIN],
        "eras": [{"label": e, "x": MARGIN + i * (BOX_W + COL_GAP)}
                 for i, e in enumerate(eras)],
        "lanes": [{"id": "lane%d" % n,
                   "label": "trunk" if n == 0 else "branches %d" % n,
                   "y": MARGIN + HEADER_H + n * (BOX_H + LANE_GAP)}
                  for n in range(n_lanes)],
        "positions": positions,
    }
