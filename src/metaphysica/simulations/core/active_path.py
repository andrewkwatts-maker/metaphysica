"""The topology of one geometric path, read from the readers that own it.

`topology(path)` is the one place outside the geometry tree that answers
"what are b3, b2, n_gen and chi_eff on this path". It writes no formula of
its own:

* b3 and b2 come from `b3_path.seed_values` (the seed table, fork b3_seed);
* n_gen comes from `b3_path.n_gen_report` (fork n_gen_source);
* chi_eff comes from `chi_eff_branches.registry_chi_eff_total` (fork
  chi_eff_route).

The seed table and both fork readers live under PM/geometry today; they are
imported inside the function so this module stays importable before the
geometry tree is (the move of the seed table into core is the geometry
lane's work). Nothing here falls back: an unknown path, fork or option
raises from the reader that owns it, and a non-integral generation count
raises here.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

__all__ = ["Topology", "topology"]


@dataclass(frozen=True)
class Topology:
    """b3, b2, n_gen and chi_eff (total over both shadows) of one path."""

    path: str
    b3: int
    b2: int
    n_gen: int
    chi_eff: int

    @property
    def chi_sector(self) -> int:
        """chi_eff per 13D shadow: the total is carried by two shadows."""
        if self.chi_eff % 2:
            raise ValueError(
                "chi_eff = %d on path %r is odd and does not split over two "
                "shadows" % (self.chi_eff, self.path))
        return self.chi_eff // 2


def topology(path: Optional[str] = None) -> Topology:
    """The topology of *path*, or of the path in force when *path* is None."""
    from metaphysica.simulations.PM.geometry.b3_path import (
        n_gen_report,
        resolve_path,
        seed_values,
    )
    from metaphysica.simulations.PM.geometry.chi_eff_branches import (
        registry_chi_eff_total,
    )
    from metaphysica.simulations.core.variants import resolve

    key = path or resolve_path()
    b3, b2 = seed_values(key)
    report = n_gen_report(key)
    if not report["is_integer"]:
        raise ValueError(
            "n_gen_source %r gives n_gen = %r on path %r, which is not a "
            "generation count" % (report["declared_source"], report["n_gen"],
                                  key))
    chi = registry_chi_eff_total(resolve("chi_eff_route"), b3)
    return Topology(path=key, b3=int(b3), b2=int(b2),
                    n_gen=int(round(report["n_gen"])), chi_eff=int(chi))
