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

__all__ = ["PathValued", "PATH_NAMES", "NotEvaluable", "TCS187_PATH", "tcs187_only"]

#: The retired seed whose (b3, b2) = (24, 4) the TCS #187 records were read at.
TCS187_PATH = "seed_24"


class NotEvaluable(LookupError):
    """A value that is defined only on another path than the one in force."""


def tcs187_only(cls: type, name: str) -> int:
    """The retired TCS #187 b3 of *cls* when seed_24 is in force; raises otherwise.

    For values counted on the TCS #187 manifold (an orientation sum, a
    torsion ratio) that no reader derives on any other path: dividing such a
    count by the live b3 gives a number nobody derived.
    """
    from metaphysica.simulations.core.active_path import topology

    topo = topology()
    if topo.path != TCS187_PATH:
        raise NotEvaluable(
            "%s.%s is the TCS #187 reading, defined only on path %s; path %r "
            "(b3 = %d) has no derivation of it"
            % (cls.__name__, name, TCS187_PATH, topo.path, topo.b3))
    return cls.RETIRED_TCS187_B3

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
