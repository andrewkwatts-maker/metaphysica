"""metaphysica — G2-manifold-derived theoretical physics framework.

The package bundles three things:

* the simulation engine (under :mod:`metaphysica.simulations`) — derives
  125 physical constants from G2 topology + a small number of seeds;
* the generators (under :mod:`metaphysica.generators`) that turn those
  simulation outputs into JSON, JS, HTML and plot artefacts;
* the website templates (under :mod:`metaphysica.website`) — the static
  HTML / CSS / JS files that render the theory in a browser.

The :func:`build` entry point composes all three: it runs the sims,
runs every generator, and copies the bundled website assets into a
user-supplied output directory.

Public datasheet API
--------------------
:func:`Get` is the EML-stack-uniform name for "give me the datasheet for
this thing". It dispatches by name kind — quark vs physics constant —
and returns a JSON-serialisable dict (or string with ``as_json=True``).

>>> import metaphysica
>>> metaphysica.Get('Up')['Mass_MeVc2']           # 2.16
>>> metaphysica.Get('Top')['pm_prediction']['phi_scaling_N']   # 0
>>> metaphysica.Get('m_planck')['value']          # 2.435e18

Available namespaces:

* ``metaphysica.list_quarks()``     — 12 names (6 SM + 6 anti)
* ``metaphysica.list_constants()``  — ~35 curated physics constants
                                       (any flat parameters.json key works too)

Quick start (build pipeline)
----------------------------
>>> from metaphysica import build
>>> from pathlib import Path
>>> build(out_dir=Path("./site"))   # populates ./site/ with a full website

Or from the shell::

    metaphysica-build --out ./site
"""
from __future__ import annotations

from typing import Any, Dict, Union

__version__ = "2.0.3"
__author__ = "Andrew Keith Watts"

# Companion-app launcher — `metaphysica.Launch()` finds/clones metaphysica-app and runs it.
from metaphysica._launcher import launch as Launch


# ── Optional Rust acceleration ───────────────────────────────────────────────
# The Rust core (``metaphysica._physica_core``, built from
# ``rust/physica_core/`` via maturin) is strictly opt-in — see the
# README's "Optional Rust acceleration" section for build instructions.
# When the extension is missing (the default slim install) we transparently
# fall back to the pure-Python implementation, so importing this module is
# always safe.
# Rust dispatch is wired via _dispatch.py. _HAS_RUST re-exported for inspection.
from metaphysica._dispatch import _HAS_RUST, _native  # noqa: F401


# ── Build pipeline ───────────────────────────────────────────────────────────
# Heavy import deferred to first call so `import metaphysica` stays cheap.

def build(out_dir=None, *, fast: bool = False, skip_sims: bool = False, only=None) -> int:
    """Run the full simulation + generation pipeline into *out_dir*.

    Returns 0 on success, non-zero on any step's failure (matching the
    failing step's exit code).
    """
    from metaphysica.build import build as _build
    return _build(out_dir=out_dir, fast=fast, skip_sims=skip_sims, only=only)


# ── Datasheet API (Get + listings) ───────────────────────────────────────────

def Get(name: str, *, as_json: bool = False) -> Union[Dict[str, Any], str]:
    """Return a JSON datasheet for the named quark or physics constant.

    Dispatch order:

    1. If *name* matches a known quark (case-insensitive: ``"Up"``,
       ``"up"``, ``"u"``, ``"Up Quark"`` all map to up), return the quark
       datasheet (periodica-compatible schema + ``pm_prediction`` block).
    2. Otherwise treat *name* as a physics-constant lookup — Rust backend
       when available, pure-Python fallback otherwise.

    Parameters
    ----------
    name : str
        The quark or constant name to look up.
    as_json : bool, default False
        Return a JSON-encoded string instead of a dict (convenience for
        shell users).

    Raises
    ------
    KeyError
        If *name* matches neither a quark nor a known constant.
    """
    from metaphysica.datasheets.quark import (
        canonical_quark_name, build_quark_datasheet,
    )
    from metaphysica.datasheets.constant import build_constant_datasheet

    # 1. Try quark dispatch first (cheap; in-memory table).
    try:
        canonical_quark_name(name)
        result = build_quark_datasheet(name)
    except KeyError:
        # 2. Fall through to constant — Rust fast path for known registry names.
        if _HAS_RUST and _native is not None:
            fn = getattr(_native, "py_get_constant", None)
            if fn is not None:
                try:
                    result = fn(name)
                    if as_json:
                        import json
                        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
                    return result
                except (KeyError, Exception):
                    pass  # Fall through to Python.
        result = build_constant_datasheet(name)

    if as_json:
        import json
        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
    return result


def list_quarks() -> list:
    """Return all canonical quark names recognised by :func:`Get`."""
    if _HAS_RUST and _native is not None:
        fn = getattr(_native, "py_list_quarks", None)
        if fn is not None:
            try:
                return fn()
            except Exception:
                pass
    from metaphysica.datasheets.quark import KNOWN_QUARKS
    return list(KNOWN_QUARKS)


def list_constants() -> list:
    """Return curated physics-constant names recognised by :func:`Get`.

    Note: this is not exhaustive — any flat key from
    ``AutoGenerated/parameters.json`` (e.g. ``"constants.M_PLANCK"``,
    ``"geometry.higgs_vev"``) is also accepted by :func:`Get`.
    """
    if _HAS_RUST and _native is not None:
        fn = getattr(_native, "py_list_constants", None)
        if fn is not None:
            try:
                return fn()
            except Exception:
                pass
    from metaphysica.datasheets.constant import KNOWN_CONSTANTS
    return list(KNOWN_CONSTANTS)


__all__ = [
    "__version__",
    "build",
    "Get",
    "list_quarks",
    "list_constants",
    "Launch",
]
