"""metaphysica.theories -- the registry of theories the test ground can assess.

A theory is a :class:`metaphysica.testground.theory.Theory` bundle. It is found
by name, in this order:

1. a factory registered at run time with :func:`register`;
2. a built-in: ``toy`` (``metaphysica.theories.toy``) and ``pm``
   (``metaphysica.theories.pm``, available once that package exists --
   Phase 3 adds it and nothing here changes);
3. an installed entry point in the group ``metaphysica.theories``;
4. an explicit ``package.module:ATTRIBUTE`` reference.

The default theory is ``$METAPHYSICA_THEORY`` if set, else ``pm`` when it is
available, else ``toy``.

Theories depend on the test ground, never the reverse: the test ground looks a
theory up by NAME through this registry and imports no theory code itself.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import importlib
import importlib.util
import os
from importlib import metadata
from typing import Any, Callable, Dict, List, Optional

__all__ = [
    "ENTRY_POINT_GROUP",
    "DEFAULT_ENV",
    "BUILTINS",
    "UnknownTheory",
    "register",
    "unregister",
    "available_theories",
    "default_theory_name",
    "theory_ref",
    "get_theory",
]

ENTRY_POINT_GROUP = "metaphysica.theories"
DEFAULT_ENV = "METAPHYSICA_THEORY"
#: name -> "module:ATTRIBUTE" of a built-in theory.
BUILTINS: Dict[str, str] = {
    "toy": "metaphysica.theories.toy:THEORY",
    "pm": "metaphysica.theories.pm:THEORY",
}

_REGISTERED: Dict[str, Callable[[], Any]] = {}


class UnknownTheory(LookupError):
    """No theory of that name is registered, built in or installed."""


def register(name: str, factory: Callable[[], Any]) -> None:
    """Make ``factory()`` the theory called ``name`` (overrides a built-in)."""
    _REGISTERED[name] = factory


def unregister(name: str) -> None:
    _REGISTERED.pop(name, None)


def _module_exists(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError):
        return False


def _entry_points() -> Dict[str, Any]:
    try:
        return {ep.name: ep for ep in metadata.entry_points(
            group=ENTRY_POINT_GROUP)}
    except Exception:          # a broken distribution must not hide built-ins
        return {}


def available_theories() -> List[str]:
    """Names :func:`get_theory` can resolve, sorted."""
    names = set(_REGISTERED) | set(_entry_points())
    names |= {n for n, ref in BUILTINS.items()
              if _module_exists(ref.split(":")[0])}
    return sorted(names)


def default_theory_name() -> str:
    env = os.environ.get(DEFAULT_ENV, "").strip()
    if env:
        return env
    return "pm" if "pm" in available_theories() else "toy"


def _load_ref(ref: str) -> Any:
    module, _, attr = ref.partition(":")
    obj = importlib.import_module(module)
    for part in (attr or "THEORY").split("."):
        obj = getattr(obj, part)
    return obj


def _as_theory(obj: Any) -> Any:
    """A Theory instance, calling a factory if one was given."""
    if hasattr(obj, "switches") and hasattr(obj, "selections"):
        return obj
    if callable(obj):
        return obj()
    raise UnknownTheory("%r is neither a Theory nor a factory of one" % (obj,))


def theory_ref(name: Optional[str] = None) -> Optional[str]:
    """``"module:attribute"`` a fresh process can import ``name`` from, or
    None for a theory registered only at run time."""
    name = name or default_theory_name()
    if name in _REGISTERED:
        return None
    if name in BUILTINS and _module_exists(BUILTINS[name].split(":")[0]):
        return BUILTINS[name]
    eps = _entry_points()
    if name in eps:
        return eps[name].value
    return name if ":" in name else None


def get_theory(name: Optional[str] = None) -> Any:
    """The theory called ``name`` (default: :func:`default_theory_name`)."""
    name = name or default_theory_name()
    if name in _REGISTERED:
        return _as_theory(_REGISTERED[name]())
    if name in BUILTINS and _module_exists(BUILTINS[name].split(":")[0]):
        return _as_theory(_load_ref(BUILTINS[name]))
    eps = _entry_points()
    if name in eps:
        return _as_theory(eps[name].load())
    if ":" in name:
        return _as_theory(_load_ref(name))
    raise UnknownTheory("unknown theory %r; available: %s"
                        % (name, ", ".join(available_theories()) or "none"))
