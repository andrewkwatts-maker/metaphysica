"""The certificate: every theorem evaluated on the active seed, ending in the
selection theorem CG.12 (published since the 2026-10-01 rulings, D-015).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from metaphysica.simulations.PM.geometry.closed_geometry.findings import (
    FINDINGS_THEOREMS,
)
from metaphysica.simulations.PM.geometry.closed_geometry.physics import (
    PHYSICS_THEOREMS,
)
from metaphysica.simulations.PM.geometry.closed_geometry.selection import (
    SELECTION_THEOREMS,
)
from metaphysica.simulations.PM.geometry.closed_geometry.theorem import (
    Theorem,
)
from metaphysica.simulations.PM.geometry.closed_geometry.topology import (
    TOPOLOGY_THEOREMS,
)

THEOREMS: Tuple[Theorem, ...] = (TOPOLOGY_THEOREMS + PHYSICS_THEOREMS
                                 + FINDINGS_THEOREMS + SELECTION_THEOREMS)


def certificate() -> List[Dict[str, Any]]:
    """Every theorem evaluated on the active seed."""
    out = []
    for thm in THEOREMS:
        ev = thm.evidence()
        out.append({
            "id": thm.id,
            "label": thm.label,
            "title": thm.title,
            "statement": thm.statement(ev),
            "holds": bool(thm.holds(ev)),
            "derived": ev["derived"],
            "counts": thm.counts,
            "proof": thm.proof,
            "test": thm.test,
            "falsifier": thm.falsifier,
            "scope": thm.scope,
            "references": list(thm.references),
            "evidence": ev,
        })
    return out


def holonomy_selection_pending() -> Dict[str, Any]:
    """The D-002 holonomy reading -- no longer held back.

    It waited for the real-form ruling. RULED 2026-10-01 (D-015): the compact
    form is the active path, and the reading is published as part of the
    selection theorem CG.12 (`y7-selection`), whose statement follows the
    real-form switch. Kept so earlier callers get the record, not a KeyError.
    """
    from metaphysica.simulations.PM.geometry.family_topology import (
        holonomy_selection,
    )

    sel = holonomy_selection()
    sel["status"] = "PUBLISHED_IN_CG12"
    sel["published_as"] = "y7-selection"
    sel["ruling"] = "D-015 (2026-10-01): compact form active; WA-1 adopted"
    return sel
