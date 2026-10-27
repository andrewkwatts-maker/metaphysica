"""The established-physics catalogue: every check and its failing controls.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import List

from metaphysica.actions import established_gauge, established_gravity, established_matter
from metaphysica.actions.established import EstablishedCheck


def action_checks() -> List[EstablishedCheck]:
    """Checks that take a single action (gravity, matter, gauge)."""
    return (established_gravity.checks() + established_matter.checks()
            + established_gauge.checks())


def action_controls() -> List[EstablishedCheck]:
    return (established_gravity.controls() + established_matter.controls()
            + established_gauge.controls())
