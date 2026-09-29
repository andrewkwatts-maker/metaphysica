"""The certificate: every theorem evaluated on the active seed, and the
holonomy selection held back until the real-form ruling.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from metaphysica.simulations.PM.geometry.closed_geometry.physics import (
    PHYSICS_THEOREMS,
)
from metaphysica.simulations.PM.geometry.closed_geometry.theorem import (
    Theorem,
)
from metaphysica.simulations.PM.geometry.closed_geometry.topology import (
    TOPOLOGY_THEOREMS,
)

THEOREMS: Tuple[Theorem, ...] = TOPOLOGY_THEOREMS + PHYSICS_THEOREMS


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
    """The D-002 holonomy reading, held back from publication until G3."""
    from metaphysica.simulations.PM.geometry.family_topology import (
        holonomy_selection,
    )

    sel = holonomy_selection()
    sel["status"] = "PENDING_G3_REAL_FORM_RULING"
    sel["why_not_published"] = (
        "holonomy is Riemannian; the adopted form convention is the split "
        "form G2*, where only the topological half (pi_1 finite exactly at "
        "(12, 43)) is established -- and that half is published as "
        "y7-fundamental-group")
    return sel
