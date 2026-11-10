"""The b3 in force for section text, certificates and self-checks (no literal).

Text built outside run() has no registry in hand, so it reads the same fork
the geometry tree reads: ``seed_values(resolve_path())``. A missing path or key
raises; there is no default.
"""
from __future__ import annotations

from metaphysica.simulations.PM.geometry.b3_path import resolve_path, seed_values


def active_b3() -> int:
    """b3 of the active path (43 on the adopted Joyce resolution)."""
    return seed_values(resolve_path())[0]
