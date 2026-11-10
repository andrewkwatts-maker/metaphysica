"""Class attributes read from the path in force at access.

A parameter class whose metaclass is `PathValued` answers ``B3``, ``B2``,
``CHI_EFF`` and ``N_GENERATIONS`` from `active_path.topology()` each time
they are read, so they follow `variants.selection.forced(...)`, and
``N_FLUX`` = chi_eff / 6 with them. A class may also declare
``_PATH_DERIVED`` (name -> function of the class) for values built from
those names, such as racetrack coefficients; they are computed at access
too. Nothing is typed here and nothing falls back: the readers behind
`topology()` raise on an unknown path, fork or option.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

from typing import Any, Callable, Dict

__all__ = ["PathValued", "PATH_NAMES"]

#: Attribute name -> reader of the topology of the path in force.
PATH_NAMES: Dict[str, Callable[[Any], int]] = {
    "B3": lambda t: t.b3,
    "B2": lambda t: t.b2,
    "CHI_EFF": lambda t: t.chi_eff,
    "N_GENERATIONS": lambda t: t.n_gen,
    "N_FLUX": lambda t: t.chi_eff / 6,
}


def _derived(cls: type, name: str) -> Any:
    """The class's own `_PATH_DERIVED` reader for *name*, or None."""
    for klass in cls.__mro__:
        table = vars(klass).get("_PATH_DERIVED")
        if table is not None and name in table:
            return table[name]
    return None


class PathValued(type):
    """Metaclass: PATH_NAMES and `_PATH_DERIVED` are computed at access."""

    def __getattr__(cls, name: str) -> Any:
        if name in PATH_NAMES:
            from metaphysica.simulations.core.active_path import topology

            return PATH_NAMES[name](topology())
        reader = _derived(cls, name)
        if reader is not None:
            return reader(cls)
        raise AttributeError("%s has no attribute %r" % (cls.__name__, name))
