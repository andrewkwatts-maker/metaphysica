"""A ladder: ordered steps, each validated, reduced and cross-checked.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from metaphysica.actions.correspondence import Correspondence
from metaphysica.actions.dimensions import check_action
from metaphysica.actions.model import Action
from metaphysica.actions.reduction import Reduction, check_reduction

VALIDATED = "VALIDATED"


@dataclass(frozen=True)
class Step:
    """`reduction` (optional) is the map from the previous step action to this one."""

    id: str
    action: Action
    reduction: Optional[Reduction] = None
    correspondences: Tuple[Correspondence, ...] = ()


@dataclass(frozen=True)
class Ladder:
    steps: Tuple[Step, ...]

    def report(self) -> Dict:
        steps, verdict = [], VALIDATED
        for s in self.steps:
            checks = list(check_action(s.action))
            if s.reduction is not None:
                checks += check_reduction(s.reduction)
            checks += [c.run() for c in s.correspondences]
            steps.append({"step": s.id, "checks": [c.as_dict() for c in checks]})
            if verdict == VALIDATED:
                bad = next((c.id for c in checks if not c.holds), None)
                verdict = bad or VALIDATED
        return {"steps": steps, "verdict": verdict}
