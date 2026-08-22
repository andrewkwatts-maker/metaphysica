#!/usr/bin/env python3
"""Typed, immutable view of the framework's dimensional structure.

WHY THIS EXISTS
---------------
Action terms need to know their own rank -- how many dimensions to integrate
over, what degree a top form has, how big a spinor is. Reading those through
`registry.get_param("topology.elder_kads")` is stringly-typed and silently
returns nothing useful when a path is misspelled. This gives callers a typed,
autocompleting object to inject instead.

WHAT THIS IS NOT
----------------
It is NOT a store. Every field is populated by reading a FormulasRegistry
property; none has a literal default. The repo already carries the same
dimensional integers in FormulasRegistry, config.FundamentalConstants,
PMRegistry, the dependency resolver and canonical_values -- a sixth independent
copy is exactly the ORPHAN class that generate_config_drift_audit.py exists to
catch. `FormulasRegistry` remains the sole Level-0/1 source; this is a view of
it, constructed fresh from the singleton.

WHY IT READS THE BULK RANK DYNAMICALLY
--------------------------------------
CANON["D_bulk"] is STRUCTURAL_CHALLENGED: the (24,2)/26D vs (26,2)/28D ruling is
open. Code that hardcodes a bulk rank freezes a value the framework has
explicitly flagged as under review. Anything built on this config follows the
ruling automatically whenever it lands.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:  # pragma: no cover - typing only
    from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry

__all__ = ["PhysicsConfig"]

#: Bott periodicity of the real Clifford algebras. This is a THEOREM, not a
#: framework input -- Cl(s,t) depends on (s - t) mod 8 -- so it is named here
#: rather than sourced from the registry, which holds only framework values.
_CLIFFORD_PERIOD: int = 8


@dataclass(frozen=True)
class PhysicsConfig:
    """Immutable dimensional view. Build it with :meth:`from_registry`."""

    # Ancestral (bulk) signature
    d_ancestral_total: int
    d_ancestral_space: int
    d_ancestral_time: int

    # Shadow signature -- one time direction per shadow
    d_shadow_total: int
    d_shadow_space: int
    d_shadow_time: int

    # Compactification cycle and the observed slice
    d_g2_total: int
    d_visible_total: int
    d_visible_space: int
    d_visible_time: int

    # Topology and bridge structure
    elder_kads: int
    bridge_local: int
    bridge_effective: int

    @classmethod
    def from_registry(
        cls, registry: Optional["FormulasRegistry"] = None
    ) -> "PhysicsConfig":
        """Read every field from FormulasRegistry -- the only constructor.

        Passing an explicit registry supports dependency injection in tests;
        omitting it uses the process singleton.
        """
        if registry is None:
            from metaphysica.simulations.core.FormulasRegistry import get_registry

            registry = get_registry()
        return cls(
            d_ancestral_total=registry.D_ancestral_total,
            d_ancestral_space=registry.D_ancestral_space,
            d_ancestral_time=registry.D_ancestral_time,
            d_shadow_total=registry.D_shadow_total,
            d_shadow_space=registry.D_shadow_space,
            d_shadow_time=registry.D_shadow_time,
            d_g2_total=registry.D_G2_total,
            d_visible_total=registry.D_visible_total,
            d_visible_space=registry.D_visible_space,
            d_visible_time=registry.D_visible_time,
            elder_kads=registry.elder_kads,
            bridge_local=registry.bridge_local,
            bridge_effective=registry.bridge_effective,
        )

    def __post_init__(self) -> None:
        """Signature identities -- total = space + time at every level.

        These hold under ANY signature ruling, so they stay valid if the bulk
        moves from (24,2) to (26,2). Deliberately absent: any assertion tying
        the bulk rank to twice the shadow rank, which holds at 26D but not at
        28D and would hard-fail the open ruling.
        """
        for name, total, space, time in (
            ("ancestral", self.d_ancestral_total, self.d_ancestral_space,
             self.d_ancestral_time),
            ("shadow", self.d_shadow_total, self.d_shadow_space,
             self.d_shadow_time),
            ("visible", self.d_visible_total, self.d_visible_space,
             self.d_visible_time),
        ):
            if total != space + time:
                raise ValueError(
                    f"{name} signature inconsistent: total={total} but "
                    f"space+time={space + time}"
                )

    # -- derived quantities, all expressed through the fields above ----------

    @property
    def orthogonal_bound(self) -> float:
        """Maximum bridge angle admitted by reflection positivity.

        RP requires the Gaussian cross block to be PSD, which forces
        theta <= 90 degrees. See PM/validation/reflection_positivity_gate.py.
        """
        return math.pi / 2

    @property
    def shadow_spinor_dim(self) -> int:
        """Spinor dimension of one shadow: 2 ** (d_shadow_space // 2)."""
        return 2 ** (self.d_shadow_space // 2)

    @property
    def shadow_pair_spinor(self) -> int:
        """Spinor dimension of the shadow pair."""
        return self.shadow_spinor_dim * self.shadow_spinor_dim

    @property
    def signature_invariant(self) -> int:
        """(s - t) mod 8 for one shadow -- fixes the Clifford reality type."""
        return (self.d_shadow_space - self.d_shadow_time) % _CLIFFORD_PERIOD
