"""Retire-from-paper support for figure modules (Rule 5: keep the module, drop it from the paper).

A figure module that sets ``RETIRED_FROM_PAPER = True`` keeps its code and its
output, but the output goes to a ``retired`` subfolder, never into the folder
the paper, the site and the plot manifest read, and ``paper_figures`` removes
it from any list of figure modules a builder iterates.
"""
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Iterable, List

RETIRED_SUBDIR = "retired"


def is_retired(module) -> bool:
    """True when the module carries RETIRED_FROM_PAPER = True (absent means live)."""
    return getattr(module, "RETIRED_FROM_PAPER", False) is True


def output_dir_for(module, base: Path) -> Path:
    """`base` for a live figure, `base/retired` for a retired one."""
    return Path(base) / RETIRED_SUBDIR if is_retired(module) else Path(base)


def paper_figures(dotted_names: Iterable[str]) -> List[str]:
    """The figure modules that may appear in the paper: retired ones are dropped."""
    return [n for n in dotted_names if not is_retired(importlib.import_module(n))]
