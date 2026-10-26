"""A correspondence: established physics a step must reproduce, computed not asserted.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Tuple

from metaphysica.actions.model import Check


@dataclass(frozen=True)
class Correspondence:
    """`compute()` returns (measured, holds, detail); `reference` cites the textbook."""

    id: str
    step: str
    reference: str
    compute: Callable[[], Tuple[object, bool, str]]

    def run(self) -> Check:
        measured, holds, detail = self.compute()
        return Check(self.id, measured, bool(holds), True, self.reference, detail)
