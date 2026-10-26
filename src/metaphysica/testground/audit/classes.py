"""Output equivalence classes: runs whose rows all match are one class.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Mapping

from metaphysica.testground.audit.rows import Rows, changed

__all__ = ["RunClass", "equivalence_classes"]


@dataclass
class RunClass:
    representative: str
    members: List[str] = field(default_factory=list)


def equivalence_classes(runs: Mapping[str, Rows]) -> List[RunClass]:
    """Group runs; a run joins the first class whose representative it matches on every row.

    The tolerance is not transitive, so each run is compared with the representative only.
    """
    classes: List[RunClass] = []
    reps: List[Rows] = []
    for run_id, rows in runs.items():
        for cls, rep in zip(classes, reps):
            if not changed(rep, rows):
                cls.members.append(run_id)
                break
        else:
            classes.append(RunClass(run_id, [run_id]))
            reps.append(rows)
    return classes
