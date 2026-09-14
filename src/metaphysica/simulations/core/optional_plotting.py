"""Import matplotlib where it is USED, not where a simulation is defined.

WHY
===
Three simulation modules under ``PM/consciousness`` imported matplotlib at
module top level::

    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyBboxPatch

matplotlib lives in the ``[plots]`` extra. CI installs ``.[dev,sims]``. So on
every CI run those three imports raised ImportError, ``run_all_simulations``
swallowed it, and the three simulations were silently absent -- taking four
formulas with them:

    four-dice-branch-count          four_dice_sampling
    gnosis-coherence-enhancement    gnosis_unlocking
    gnosis-unlocking-probability    gnosis_unlocking
    pair-shielding-enhancement      orch_or_pair_shielding

That is the difference between the 569 formulas the author's build produces
and the 565 CI produces, which is why ``test_arithma_b3_coverage_never_regresses``
asserted ``565 >= 569`` and failed. The formulas were never lost; a plotting
dependency was deciding whether a physics simulation ran.

This is the same defect the repository has already caught twice -- nine
simulations that "had never run" because their import sat under an
``except ImportError``, and a stub arithma that imported and could not compute.
An optional dependency must gate the optional FEATURE, never the module that
happens to contain it.

WHAT THIS DOES
==============
``pyplot()`` and friends import matplotlib at CALL time and raise a message
naming the extra if it is missing. A module that only defines simulations
imports nothing; a module that draws a figure pays for matplotlib at the
moment it draws.

Signatures annotated ``-> plt.Figure`` need ``from __future__ import
annotations`` in the consuming module so the annotation is never evaluated.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Tuple

__all__ = ["available", "pyplot", "patches", "collections", "colors", "require"]

_HINT = (
    "matplotlib is not installed. It belongs to the [plots] extra: "
    "pip install metaphysica[plots] (or .[full] for every extra). "
    "The simulation itself does not need it -- only this figure does."
)


def available() -> bool:
    """True when matplotlib can actually be imported."""
    try:
        import matplotlib  # noqa: F401
    except Exception:                          # noqa: BLE001 - absent is absent
        return False
    return True


def require() -> None:
    """Raise with the install hint if matplotlib is absent."""
    if not available():
        raise ImportError(_HINT)


def pyplot() -> Any:
    """``matplotlib.pyplot``, imported now rather than at module load."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:                 # pragma: no cover - env-specific
        raise ImportError(_HINT) from exc
    return plt


def patches() -> Any:
    try:
        import matplotlib.patches as mpatches
    except ImportError as exc:                 # pragma: no cover - env-specific
        raise ImportError(_HINT) from exc
    return mpatches


def collections() -> Any:
    try:
        import matplotlib.collections as mcollections
    except ImportError as exc:                 # pragma: no cover - env-specific
        raise ImportError(_HINT) from exc
    return mcollections


def colors() -> Any:
    try:
        import matplotlib.colors as mcolors
    except ImportError as exc:                 # pragma: no cover - env-specific
        raise ImportError(_HINT) from exc
    return mcolors


def pyplot_and_patches() -> Tuple[Any, Any]:
    """The pair most drawing code needs, in one call."""
    return pyplot(), patches()
